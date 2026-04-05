from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.standard import Standard


def _make_standard(db: Session, **overrides) -> Standard:
    defaults = dict(
        ac_code=f"ISO {uuid4().hex[:6]}:2015",
        title="Quality management systems",
        status="60",
        normalized_code="iso 9001:2015",
        base_number="9001",
        source_payload={},
        ingested_at=datetime.now(UTC),
    )
    defaults.update(overrides)
    std = Standard(**defaults)
    db.add(std)
    db.flush()
    return std


def test_list_standards_returns_paginated_envelope(client: TestClient, db_session: Session) -> None:
    for _ in range(3):
        _make_standard(db_session)
    db_session.commit()

    response = client.get("/api/v1/standards")

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["limit"] == 50
    assert body["pagination"]["total"] >= 3
    assert len(body["data"]) >= 3


def test_list_standards_filters_by_status(client: TestClient, db_session: Session) -> None:
    _make_standard(db_session, status="60")
    _make_standard(db_session, status="90")
    db_session.commit()

    response = client.get("/api/v1/standards?status=90")

    assert response.status_code == 200
    body = response.json()
    assert all(item["status"] == "90" for item in body["data"])


def test_get_standard_by_id_returns_record(client: TestClient, db_session: Session) -> None:
    std = _make_standard(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/standards/{std.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(std.id)


def test_get_standard_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/standards/{uuid4()}")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NOT_FOUND"
    assert body["entity"] == "standard"


def test_create_standard_returns_201(client: TestClient, actor: str) -> None:
    payload = {
        "ac_code": "ISO 14001:2015",
        "title": "Environmental management systems",
        "status": "60",
        "source_payload": {"raw": "test"},
    }

    response = client.post(
        "/api/v1/standards",
        json=payload,
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["ac_code"] == "ISO 14001:2015"
    assert data["status"] == "60"
    assert "id" in data


def test_patch_standard_updates_fields(client: TestClient, db_session: Session, actor: str) -> None:
    std = _make_standard(db_session, status="60")
    db_session.commit()

    response = client.patch(
        f"/api/v1/standards/{std.id}",
        json={"status": "95"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "95"


def test_patch_standard_nonexistent_returns_404(client: TestClient, actor: str) -> None:
    response = client.patch(
        f"/api/v1/standards/{uuid4()}",
        json={"status": "95"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 404
