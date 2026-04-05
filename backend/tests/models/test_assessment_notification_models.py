from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.standard import Standard


def test_assessment_and_notification_can_be_created(db_session: Session) -> None:
    # Build the full chain
    customer = Customer(
        customer_number="CUST-A1", company_name="AssessTest", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-A1", customer_id=customer.id,
        product_description="Test", status="active",
        issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    standard = Standard(
        ac_code="ISO 9001:2015", title="QMS", status="60",
        normalized_code="iso 9001:2015", base_number="9001",
        source_payload={}, ingested_at=datetime.now(UTC),
    )
    db_session.add_all([cert, standard])
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id, standard_ref="DIN EN ISO 9001:2015",
        normalized_ref="9001:2015", base_number="9001",
        linked_at=datetime.now(UTC),
    )
    db_session.add(link)
    db_session.flush()

    mr = MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.95"), confidence_tier="auto_match",
        status="reviewed", matched_at=datetime.now(UTC),
    )
    db_session.add(mr)
    db_session.flush()

    assessment = Assessment(
        match_result_id=mr.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Administrative amendment only", decision="approved",
        decided_at=datetime.now(UTC), signature_hash="abc123",
    )
    db_session.add(assessment)
    db_session.flush()

    notif = Notification(
        assessment_id=assessment.id, customer_id=customer.id,
        template_language="DE", subject="Standard update notification",
        body_html="<html></html>", status="delivered",
        sla_deadline=datetime.now(UTC) + timedelta(days=14),
    )
    db_session.add(notif)
    db_session.flush()

    assert assessment.id is not None
    assert notif.id is not None
    assert notif.assessment_id == assessment.id
