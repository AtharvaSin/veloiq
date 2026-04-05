from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.standard import Standard


def _setup_parents(db_session: Session) -> tuple[Standard, CertStandardLink]:
    customer = Customer(
        customer_number="CUST-M1", company_name="MatchTest", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-M1", customer_id=customer.id,
        product_description="Test", status="active",
        issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db_session.add(cert)
    db_session.flush()

    standard = Standard(
        ac_code="ISO 14001:2015", title="EMS", status="60",
        normalized_code="iso 14001:2015", base_number="14001",
        source_payload={}, ingested_at=datetime.now(UTC),
    )
    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 14001:2015-11",
        normalized_ref="14001:2015",
        base_number="14001",
        linked_at=datetime.now(UTC),
    )
    db_session.add_all([standard, link])
    db_session.flush()
    return standard, link


def test_match_result_can_be_created(db_session: Session) -> None:
    standard, link = _setup_parents(db_session)
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

    assert mr.id is not None
    assert mr.similarity_score == Decimal("0.840")
    assert mr.confidence_tier == "expert_review"


def test_match_result_confidence_tier_constraint(db_session: Session) -> None:
    standard, link = _setup_parents(db_session)
    db_session.add(MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.5"), confidence_tier="invalid",
        status="pending", matched_at=datetime.now(UTC),
    ))
    with pytest.raises(IntegrityError):
        db_session.flush()
