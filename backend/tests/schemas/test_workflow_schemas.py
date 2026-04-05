from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.standard import Standard
from app.schemas.assessment import AssessmentRead
from app.schemas.match_result import MatchResultRead


def _build_match_result(db_session: Session) -> MatchResult:
    customer = Customer(
        customer_number="CUST-WF-1",
        company_name="WorkflowCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-WF-1",
        customer_id=customer.id,
        product_description="T",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    standard = Standard(
        ac_code="ISO 14001:2015",
        title="EMS",
        status="60",
        normalized_code="iso 14001:2015",
        base_number="14001",
        source_payload={},
        ingested_at=datetime.now(UTC),
    )
    db_session.add_all([cert, standard])
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 14001:2015-11",
        normalized_ref="14001:2015",
        base_number="14001",
        linked_at=datetime.now(UTC),
    )
    db_session.add(link)
    db_session.flush()

    mr = MatchResult(
        natos_standard_id=standard.id,
        cert_link_id=link.id,
        similarity_score=Decimal("0.840"),
        levenshtein_score=Decimal("0.820"),
        jaro_winkler_score=Decimal("0.890"),
        token_set_score=Decimal("0.910"),
        confidence_tier="expert_review",
        status="pending",
        matched_at=datetime.now(UTC),
    )
    db_session.add(mr)
    db_session.flush()
    return mr


def test_match_result_read_from_orm_model(db_session: Session) -> None:
    mr = _build_match_result(db_session)

    read = MatchResultRead.model_validate(mr)
    assert read.id == mr.id
    assert read.natos_standard_id == mr.natos_standard_id
    assert read.similarity_score == Decimal("0.840")
    assert read.confidence_tier == "expert_review"
    assert read.status == "pending"
    assert read.reviewed_at is None


def test_match_result_read_preserves_optional_sub_scores(db_session: Session) -> None:
    mr = _build_match_result(db_session)
    read = MatchResultRead.model_validate(mr)
    assert read.levenshtein_score == Decimal("0.820")
    assert read.jaro_winkler_score == Decimal("0.890")
    assert read.token_set_score == Decimal("0.910")


def test_assessment_read_from_orm_model(db_session: Session) -> None:
    mr = _build_match_result(db_session)
    assessment = Assessment(
        match_result_id=mr.id,
        assessor_id="Dr. M. Weber",
        impact_classification="minor_technical",
        action_required="reconfirm",
        reason_code="Administrative amendment only",
        notes="No structural changes; section renumbering only.",
        decision="approved",
        decided_at=datetime.now(UTC),
        signature_hash="abc123def456",
    )
    db_session.add(assessment)
    db_session.flush()

    read = AssessmentRead.model_validate(assessment)
    assert read.id == assessment.id
    assert read.assessor_id == "Dr. M. Weber"
    assert read.impact_classification == "minor_technical"
    assert read.action_required == "reconfirm"
    assert read.decision == "approved"
    assert read.signature_hash == "abc123def456"
    assert read.notes is not None
