"""End-to-end smoke tests for the VeloIQ API.

These tests exercise the full HTTP stack: request -> router -> service -> DB ->
audit log -> response. They are the definition-of-done proof for Phase A and
the last line of defence before Phase B begins.
"""
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """GET /health returns 200 OK with a status payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_standards_creates_record_and_writes_audit_entry(
    client: TestClient, db_session: Session
) -> None:
    """POST /api/v1/standards creates a standard AND writes an audit_log row.

    This is the core Phase A guarantee: every mutation through the API
    produces an audit entry in the same transaction.
    """
    payload = {
        "ac_code": "ISO 9001:2015",
        "title": "Quality management systems — Requirements",
        "status": "60",
        "source_payload": {"raw": "smoke-test"},
    }
    response = client.post(
        "/api/v1/standards",
        json=payload,
        headers={"X-User-Id": "smoke-test-actor"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ac_code"] == "ISO 9001:2015"
    assert body["status"] == "60"
    assert "id" in body

    # Verify audit log entry was written in the same transaction
    audit_entries = (
        db_session.query(AuditLog)
        .filter_by(entity_type="standard", entity_id=body["id"])
        .all()
    )
    assert len(audit_entries) == 1
    assert audit_entries[0].action == "created"
    assert audit_entries[0].actor == "smoke-test-actor"
    assert audit_entries[0].details["ac_code"] == "ISO 9001:2015"


def test_get_standards_returns_paginated_list(client: TestClient) -> None:
    """GET /api/v1/standards returns a paginated envelope with data + pagination."""
    # Seed 3 records via the API so we have something to list
    for i in range(3):
        client.post(
            "/api/v1/standards",
            json={
                "ac_code": f"ISO {9000 + i}:2015",
                "title": f"Standard {i}",
                "status": "60",
                "source_payload": {"i": i},
            },
            headers={"X-User-Id": "smoke-test-actor"},
        )

    response = client.get("/api/v1/standards?page=1&limit=50")
    assert response.status_code == 200
    body = response.json()

    assert "data" in body
    assert "pagination" in body
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 3

    pagination = body["pagination"]
    assert pagination["page"] == 1
    assert pagination["limit"] == 50
    assert pagination["total"] >= 3
    assert pagination["total_pages"] >= 1


def test_get_standard_by_id_returns_single_record(client: TestClient) -> None:
    """GET /api/v1/standards/{id} returns the matching standard."""
    create_resp = client.post(
        "/api/v1/standards",
        json={
            "ac_code": "ISO 14001:2015",
            "title": "Environmental management systems",
            "status": "60",
            "source_payload": {"raw": "env"},
        },
        headers={"X-User-Id": "smoke-test-actor"},
    )
    assert create_resp.status_code == 201
    standard_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/standards/{standard_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == standard_id
    assert body["ac_code"] == "ISO 14001:2015"


def test_get_nonexistent_standard_returns_404(client: TestClient) -> None:
    """GET /api/v1/standards/{unknown-uuid} returns 404 with structured error body."""
    unknown_id = uuid4()
    response = client.get(f"/api/v1/standards/{unknown_id}")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NOT_FOUND"
    assert body["entity"] == "standard"
    assert body["id"] == str(unknown_id)
    assert "error" in body
