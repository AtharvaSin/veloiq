from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard
from app.schemas.notification import NotificationRead
from app.schemas.sales_escalation import SalesEscalationRead, SalesEscalationUpdate


def _build_notification(db_session: Session) -> tuple[Notification, Customer]:
    customer = Customer(
        customer_number="CUST-NOTIF-1",
        company_name="NotifCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-NOTIF-1",
        customer_id=customer.id,
        product_description="T",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    standard = Standard(
        ac_code="ISO 9001:2015",
        title="QMS",
        status="60",
        normalized_code="iso 9001:2015",
        base_number="9001",
        source_payload={},
        ingested_at=datetime.now(UTC),
    )
    db_session.add_all([cert, standard])
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 9001:2015",
        normalized_ref="9001:2015",
        base_number="9001",
        linked_at=datetime.now(UTC),
    )
    db_session.add(link)
    db_session.flush()

    mr = MatchResult(
        natos_standard_id=standard.id,
        cert_link_id=link.id,
        similarity_score=Decimal("0.95"),
        confidence_tier="auto_match",
        status="reviewed",
        matched_at=datetime.now(UTC),
    )
    db_session.add(mr)
    db_session.flush()

    assessment = Assessment(
        match_result_id=mr.id,
        assessor_id="Dr. M. Weber",
        impact_classification="minor_technical",
        action_required="reconfirm",
        reason_code="Administrative amendment",
        decision="approved",
        decided_at=datetime.now(UTC),
        signature_hash="hash1",
    )
    db_session.add(assessment)
    db_session.flush()

    notif = Notification(
        assessment_id=assessment.id,
        customer_id=customer.id,
        template_language="DE",
        subject="Standard update notification",
        body_html="<html><body>Test</body></html>",
        status="delivered",
        sent_at=datetime.now(UTC),
        delivered_at=datetime.now(UTC),
        sla_deadline=datetime.now(UTC) + timedelta(days=14),
    )
    db_session.add(notif)
    db_session.flush()
    return notif, customer


def test_notification_read_from_orm_model(db_session: Session) -> None:
    notif, _ = _build_notification(db_session)

    read = NotificationRead.model_validate(notif)
    assert read.id == notif.id
    assert read.template_language == "DE"
    assert read.status == "delivered"
    assert read.subject == "Standard update notification"
    assert read.sent_at is not None
    assert read.delivered_at is not None
    assert read.opened_at is None
    assert read.clicked_at is None
    assert read.sla_deadline is not None


def test_sales_escalation_read_from_orm_model(db_session: Session) -> None:
    notif, customer = _build_notification(db_session)

    escalation = SalesEscalation(
        notification_id=notif.id,
        customer_id=customer.id,
        escalation_reason="sla_breached",
        opportunity_value=Decimal("125000.00"),
        assigned_to="sales.rep@tuv.example.com",
        status="open",
        created_at=datetime.now(UTC),
    )
    db_session.add(escalation)
    db_session.flush()

    read = SalesEscalationRead.model_validate(escalation)
    assert read.id == escalation.id
    assert read.notification_id == notif.id
    assert read.opportunity_value == Decimal("125000.00")
    assert read.status == "open"
    assert read.assigned_to == "sales.rep@tuv.example.com"
    assert read.resolved_at is None


def test_sales_escalation_update_allows_status_only_patch() -> None:
    patch = SalesEscalationUpdate(status="contacted")
    assert patch.status == "contacted"
    assert patch.assigned_to is None


def test_sales_escalation_update_allows_assigned_to_only_patch() -> None:
    patch = SalesEscalationUpdate(assigned_to="new.rep@tuv.example.com")
    assert patch.assigned_to == "new.rep@tuv.example.com"
    assert patch.status is None


def test_sales_escalation_update_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        SalesEscalationUpdate(opportunity_value=Decimal("999"))  # type: ignore[call-arg]
