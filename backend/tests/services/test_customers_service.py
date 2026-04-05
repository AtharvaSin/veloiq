from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customers_service import create_customer, update_customer


def test_create_customer_returns_entity(db_session: Session) -> None:
    payload = CustomerCreate(
        customer_number="CUST-0042",
        company_name="Siemens AG",
        country="DE",
        sales_area="EMEA",
        language="DE",
        contact_name="Ingrid Müller",
        contact_email="ingrid.mueller@siemens.example.com",
    )
    customer = create_customer(db_session, payload, actor="sales-ops")

    assert customer.id is not None
    assert customer.customer_number == "CUST-0042"
    assert customer.country == "DE"
    assert customer.contact_email == "ingrid.mueller@siemens.example.com"


def test_create_customer_writes_audit_entry(db_session: Session) -> None:
    payload = CustomerCreate(
        customer_number="CUST-0099",
        company_name="Huawei Technologies",
        country="CN",
        sales_area="Greater China",
        language="ZH",
    )
    customer = create_customer(db_session, payload, actor="sales-ops")

    entries = db_session.query(AuditLog).filter_by(
        entity_type="customer", entity_id=customer.id
    ).all()

    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].actor == "sales-ops"
    assert entries[0].details["customer_number"] == "CUST-0099"
    assert entries[0].details["country"] == "CN"


def test_update_customer_modifies_entity_and_audits(db_session: Session) -> None:
    created = create_customer(
        db_session,
        CustomerCreate(
            customer_number="CUST-0500",
            company_name="Tata Steel",
            country="IN",
            sales_area="South Asia",
            language="EN",
        ),
        actor="seeder",
    )

    updated = update_customer(
        db_session,
        created.id,
        CustomerUpdate(
            contact_name="Priya Sharma",
            contact_email="priya.sharma@tatasteel.example.com",
        ),
        actor="sales-ops",
    )

    assert updated.id == created.id
    assert updated.contact_name == "Priya Sharma"
    assert updated.contact_email == "priya.sharma@tatasteel.example.com"
    assert updated.company_name == "Tata Steel"  # unchanged

    entries = db_session.query(AuditLog).filter_by(
        entity_type="customer", entity_id=created.id
    ).order_by(AuditLog.created_at).all()

    assert len(entries) == 2
    assert entries[0].action == "created"
    assert entries[1].action == "updated"
    assert entries[1].actor == "sales-ops"
    assert "contact_name" in entries[1].details["changed_fields"]
    assert entries[1].details["changed_fields"]["contact_name"]["new"] == "Priya Sharma"


def test_update_customer_raises_not_found_for_missing_id(db_session: Session) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        update_customer(
            db_session,
            uuid4(),
            CustomerUpdate(contact_name="Ghost"),
            actor="sales-ops",
        )

    assert excinfo.value.entity == "customer"
