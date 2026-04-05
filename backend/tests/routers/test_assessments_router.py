from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.standard import Standard


def _build_assessment(db: Session, **overrides) -> Assessment:
    customer = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="AS Test", country="DE",
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

    defaults = dict(
        match_result_id=match.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Admin amendment", decision="approved",
        decided_at=datetime.now(UTC), signature_hash="hash-xyz",
    )
    defaults.update(overrides)
    a = Assessment(**defaults)
    db.add(a)
    db.flush()
    return a


def test_list_assessments_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_assessment(db_session)
    _build_assessment(db_session)
    db_session.commit()

    response = client.get("/api/v1/assessments")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 2


def test_list_assessments_filters_by_assessor_id(
    client: TestClient, db_session: Session
) -> None:
    _build_assessment(db_session, assessor_id="Dr. M. Weber")
    _build_assessment(db_session, assessor_id="A. Schmidt")
    db_session.commit()

    response = client.get("/api/v1/assessments?assessor_id=A.%20Schmidt")

    assert response.status_code == 200
    assert all(
        item["assessor_id"] == "A. Schmidt" for item in response.json()["data"]
    )


def test_list_assessments_filters_by_decision(
    client: TestClient, db_session: Session
) -> None:
    _build_assessment(db_session, decision="approved")
    _build_assessment(db_session, decision="rejected")
    db_session.commit()

    response = client.get("/api/v1/assessments?decision=rejected")

    assert response.status_code == 200
    assert all(item["decision"] == "rejected" for item in response.json()["data"])


def test_get_assessment_returns_record(client: TestClient, db_session: Session) -> None:
    a = _build_assessment(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/assessments/{a.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(a.id)


def test_get_assessment_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/assessments/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["entity"] == "assessment"


def test_post_assessments_returns_405(client: TestClient, actor: str) -> None:
    # Phase A: POST not supported yet (Phase C feature).
    response = client.post(
        "/api/v1/assessments",
        json={},
        headers={"X-User-Id": actor},
    )
    assert response.status_code == 405
