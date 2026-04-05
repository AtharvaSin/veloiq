from datetime import date

from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.customer import Customer


def test_certificate_links_to_customer(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-9001", company_name="TestCo", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-44210",
        customer_id=customer.id,
        product_description="Industrial Control Panel",
        status="active",
        issue_date=date(2024, 3, 15),
        expiry_date=date(2027, 3, 14),
    )
    db_session.add(cert)
    db_session.flush()

    assert cert.id is not None
    assert cert.customer_id == customer.id
    assert cert.status == "active"


def test_certificate_status_check_constraint(db_session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    customer = Customer(
        customer_number="CUST-9002", company_name="TestCo2", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    db_session.add(Certificate(
        certificate_number="TC-BAD",
        customer_id=customer.id,
        product_description="Test",
        status="invalid_status",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    ))
    with pytest.raises(IntegrityError):
        db_session.flush()
