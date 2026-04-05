from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer


def test_link_captures_messy_sap_format(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-L1", company_name="LinkTest", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-LINK-1", customer_id=customer.id,
        product_description="Test", status="active",
        issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db_session.add(cert)
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

    assert link.id is not None
    assert link.standard_ref == "DIN EN ISO 14001:2015-11"
    assert link.base_number == "14001"
