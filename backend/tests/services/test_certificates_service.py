from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.schemas.certificate import CertificateCreate, CertificateUpdate
from app.services.certificates_service import create_certificate, update_certificate


def _make_customer(db_session: Session, number: str = "CUST-CERT-1") -> Customer:
    customer = Customer(
        customer_number=number,
        company_name="CertTestCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()
    return customer


def test_create_certificate_returns_entity(db_session: Session) -> None:
    customer = _make_customer(db_session)
    payload = CertificateCreate(
        certificate_number="TC-55100",
        customer_id=customer.id,
        product_description="Medical Imaging Device",
        status="active",
        issue_date=date(2025, 1, 15),
        expiry_date=date(2028, 1, 14),
    )
    cert = create_certificate(db_session, payload, actor="certifier-01")

    assert cert.id is not None
    assert cert.certificate_number == "TC-55100"
    assert cert.customer_id == customer.id
    assert cert.status == "active"


def test_create_certificate_writes_audit_entry(db_session: Session) -> None:
    customer = _make_customer(db_session, number="CUST-CERT-2")
    payload = CertificateCreate(
        certificate_number="TC-55200",
        customer_id=customer.id,
        product_description="Industrial Robot Arm",
        status="active",
        issue_date=date(2025, 3, 1),
        expiry_date=date(2028, 2, 28),
    )
    cert = create_certificate(db_session, payload, actor="certifier-01")

    entries = db_session.query(AuditLog).filter_by(
        entity_type="certificate", entity_id=cert.id
    ).all()

    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].actor == "certifier-01"
    assert entries[0].details["certificate_number"] == "TC-55200"
    assert entries[0].details["status"] == "active"
    assert entries[0].details["customer_id"] == str(customer.id)


def test_update_certificate_modifies_entity_and_audits(db_session: Session) -> None:
    customer = _make_customer(db_session, number="CUST-CERT-3")
    created = create_certificate(
        db_session,
        CertificateCreate(
            certificate_number="TC-55300",
            customer_id=customer.id,
            product_description="Lab Analyzer",
            status="active",
            issue_date=date(2024, 6, 1),
            expiry_date=date(2027, 5, 31),
        ),
        actor="seeder",
    )

    updated = update_certificate(
        db_session,
        created.id,
        CertificateUpdate(status="suspended"),
        actor="compliance-officer",
    )

    assert updated.id == created.id
    assert updated.status == "suspended"
    assert updated.product_description == "Lab Analyzer"  # unchanged

    entries = db_session.query(AuditLog).filter_by(
        entity_type="certificate", entity_id=created.id
    ).order_by(AuditLog.created_at).all()

    assert len(entries) == 2
    assert entries[0].action == "created"
    assert entries[1].action == "updated"
    assert entries[1].actor == "compliance-officer"
    assert entries[1].details["changed_fields"]["status"] == {
        "old": "active",
        "new": "suspended",
    }


def test_update_certificate_raises_not_found_for_missing_id(db_session: Session) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        update_certificate(
            db_session,
            uuid4(),
            CertificateUpdate(status="expired"),
            actor="compliance-officer",
        )

    assert excinfo.value.entity == "certificate"
