from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.standard import Standard


def _build_full_chain(db: Session) -> dict:
    """Helper: create one full row-chain across all entities."""
    customer = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="RO Test", country="DE",
        sales_area="EMEA", language="DE",
    )
    db.add(customer)
    db.flush()

    standard = Standard(
        ac_code=f"ISO {uuid4().hex[:4]}:2015", title="QMS", status="60",
        normalized_code="iso 9001:2015", base_number="9001",
        source_payload={}, ingested_at=datetime.now(UTC),
    )
    cert = Certificate(
        certificate_number=f"TC-{uuid4().hex[:8]}",
        customer_id=customer.id, product_description="Test",
        status="active", issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db.add_all([standard, cert])
    db.flush()

    link = CertStandardLink(
        certificate_id=cert.id, standard_ref="DIN EN ISO 9001:2015",
        normalized_ref="9001:2015", base_number="9001",
        linked_at=datetime.now(UTC),
    )
    db.add(link)
    db.flush()

    match = MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.95"), confidence_tier="auto_match",
        status="reviewed", matched_at=datetime.now(UTC),
    )
    db.add(match)
    db.flush()

    assessment = Assessment(
        match_result_id=match.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Administrative amendment", decision="approved",
        decided_at=datetime.now(UTC), signature_hash="abc123",
    )
    db.add(assessment)
    db.flush()

    notif = Notification(
        assessment_id=assessment.id, customer_id=customer.id,
        template_language="DE", subject="Update", body_html="<p/>",
        status="delivered",
        sla_deadline=datetime.now(UTC) + timedelta(days=14),
    )
    db.add(notif)
    db.flush()

    audit = AuditLog(
        entity_type="standard", entity_id=standard.id,
        action="created", actor="Dr. M. Weber",
        details={"ac_code": standard.ac_code},
    )
    db.add(audit)
    db.flush()

    return {
        "customer": customer, "standard": standard, "cert": cert, "link": link,
        "match": match, "assessment": assessment, "notif": notif, "audit": audit,
    }


def test_list_matches_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/matches")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 1
    assert len(body["data"]) >= 1


def test_list_matches_filters_by_confidence_tier(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/matches?confidence_tier=auto_match")

    assert response.status_code == 200
    assert all(
        item["confidence_tier"] == "auto_match" for item in response.json()["data"]
    )


def test_get_match_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/matches/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["entity"] == "match_result"


def test_list_notifications_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/notifications")

    assert response.status_code == 200
    assert response.json()["pagination"]["total"] >= 1


def test_list_notifications_filters_by_status(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/notifications?status=delivered")

    assert response.status_code == 200
    assert all(item["status"] == "delivered" for item in response.json()["data"])


def test_get_notification_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/notifications/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["entity"] == "notification"


def test_list_audit_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/audit")

    assert response.status_code == 200
    assert response.json()["pagination"]["total"] >= 1


def test_list_audit_filters_by_entity_type_and_actor(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get(
        "/api/v1/audit?entity_type=standard&actor=Dr.%20M.%20Weber"
    )

    assert response.status_code == 200
    body = response.json()
    assert all(item["entity_type"] == "standard" for item in body["data"])
    assert all(item["actor"] == "Dr. M. Weber" for item in body["data"])


def test_get_audit_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/audit/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["entity"] == "audit_log"
