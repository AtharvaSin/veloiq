"""Customers mutation service. Every mutation writes an audit_log entry."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit import write_audit_entry


def create_customer(
    db: Session,
    payload: CustomerCreate,
    actor: str,
) -> Customer:
    """Create a Customer and write a paired audit_log entry."""
    customer = Customer(
        id=uuid4(),
        customer_number=payload.customer_number,
        company_name=payload.company_name,
        country=payload.country,
        sales_area=payload.sales_area,
        language=payload.language,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
    )
    db.add(customer)
    db.flush()

    write_audit_entry(
        db,
        entity_type="customer",
        entity_id=customer.id,
        action="created",
        actor=actor,
        details={
            "customer_number": customer.customer_number,
            "company_name": customer.company_name,
            "country": customer.country,
        },
    )

    db.commit()
    db.refresh(customer)
    return customer


def update_customer(
    db: Session,
    customer_id: UUID,
    payload: CustomerUpdate,
    actor: str,
) -> Customer:
    """Update a Customer and write a paired audit_log entry capturing diffs."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError(entity="customer", entity_id=customer_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(customer, field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
            setattr(customer, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="customer",
        entity_id=customer.id,
        action="updated",
        actor=actor,
        details={
            "customer_number": customer.customer_number,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(customer)
    return customer
