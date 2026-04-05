from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard


def _build_escalation(db: Session, **overrides) -> SalesEscalation:
    customer = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="Esc Test", country="DE",
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
        certificate_id=cert.id, standard_ref="raw", normalized_ref="norm",
        base_number="9001", linked_at=datetime.now(UTC),
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
        reason_code="Admin", decision="approved",
        decided_at=datetime.now(UTC), signature_hash="hash",
    )
    db.add(assessment)
    db.flush()

    notif = Notification(
        assessment_id=assessment.id, customer_id=customer.id,
        template_language="DE", subject="S", body_html="<p/>",
        status="breached",
        sla_deadline=datetime.now(UTC) - timedelta(days=1),
    )
    db.add(notif)
    db.flush()

    defaults = dict(
        notification_id=notif.id, customer_id=customer.id,
        escalation_reason="sla_breached",
        opportunity_value=Decimal("50000.00"), assigned_to=None,
        status="open", created_at=datetime.now(UTC),
    )
    defaults.update(overrides)
    esc = SalesEscalation(**defaults)
    db.add(esc)
    db.flush()
    return esc


def test_list_escalations_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_escalation(db_session)
    _build_escalation(db_session)
    db_session.commit()

    response = client.get("/api/v1/escalations")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 2


def test_list_escalations_filters_by_status(
    client: TestClient, db_session: Session
) -> None:
    _build_escalation(db_session, status="open")
    _build_escalation(db_session, status="resolved")
    db_session.commit()

    response = client.get("/api/v1/escalations?status=resolved")

    assert response.status_code == 200
    assert all(item["status"] == "resolved" for item in response.json()["data"])


def test_get_escalation_returns_record(client: TestClient, db_session: Session) -> None:
    esc = _build_escalation(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/escalations/{esc.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(esc.id)


def test_get_escalation_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/escalations/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["entity"] == "sales_escalation"


def test_patch_escalation_updates_status(
    client: TestClient, db_session: Session, actor: str
) -> None:
    esc = _build_escalation(db_session, status="open")
    db_session.commit()

    response = client.patch(
        f"/api/v1/escalations/{esc.id}",
        json={"status": "contacted", "assigned_to": "sales-rep-7"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "contacted"
    assert body["assigned_to"] == "sales-rep-7"


def test_patch_escalation_nonexistent_returns_404(
    client: TestClient, actor: str
) -> None:
    response = client.patch(
        f"/api/v1/escalations/{uuid4()}",
        json={"status": "resolved"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 404


def test_post_escalations_returns_405(client: TestClient, actor: str) -> None:
    # No POST endpoint exists.
    response = client.post(
        "/api/v1/escalations",
        json={},
        headers={"X-User-Id": actor},
    )
    assert response.status_code == 405
