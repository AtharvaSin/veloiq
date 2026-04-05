from sqlalchemy.orm import Session

from app.models.customer import Customer


def test_customer_can_be_created_with_required_fields(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-0001",
        company_name="Huawei Technologies Co., Ltd.",
        country="CN",
        sales_area="Greater China",
        language="ZH",
        contact_email="li.wei@huawei.example.com",
    )
    db_session.add(customer)
    db_session.flush()

    assert customer.id is not None
    assert customer.customer_number == "CUST-0001"
    assert customer.country == "CN"
    assert customer.created_at is not None


def test_customer_number_must_be_unique(db_session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    db_session.add(Customer(
        customer_number="CUST-DUP", company_name="A", country="DE",
        sales_area="EMEA", language="DE",
    ))
    db_session.flush()

    db_session.add(Customer(
        customer_number="CUST-DUP", company_name="B", country="DE",
        sales_area="EMEA", language="DE",
    ))
    with pytest.raises(IntegrityError):
        db_session.flush()
