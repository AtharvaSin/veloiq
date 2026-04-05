"""Certificates mutation service. Every mutation writes an audit_log entry."""
from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateUpdate
from app.services.audit import write_audit_entry


def _serialize(value: object) -> object:
    """Coerce non-JSON-native values (UUID, date) to strings for audit details."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def create_certificate(
    db: Session,
    payload: CertificateCreate,
    actor: str,
) -> Certificate:
    """Create a Certificate and write a paired audit_log entry."""
    cert = Certificate(
        id=uuid4(),
        certificate_number=payload.certificate_number,
        customer_id=payload.customer_id,
        product_description=payload.product_description,
        status=payload.status,
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
    )
    db.add(cert)
    db.flush()

    write_audit_entry(
        db,
        entity_type="certificate",
        entity_id=cert.id,
        action="created",
        actor=actor,
        details={
            "certificate_number": cert.certificate_number,
            "customer_id": str(cert.customer_id),
            "status": cert.status,
            "issue_date": cert.issue_date.isoformat(),
            "expiry_date": cert.expiry_date.isoformat(),
        },
    )

    db.commit()
    db.refresh(cert)
    return cert


def update_certificate(
    db: Session,
    certificate_id: UUID,
    payload: CertificateUpdate,
    actor: str,
) -> Certificate:
    """Update a Certificate and write a paired audit_log entry capturing diffs."""
    cert = db.get(Certificate, certificate_id)
    if cert is None:
        raise NotFoundError(entity="certificate", entity_id=certificate_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(cert, field)
        if old_value != new_value:
            changed_fields[field] = {
                "old": _serialize(old_value),
                "new": _serialize(new_value),
            }
            setattr(cert, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="certificate",
        entity_id=cert.id,
        action="updated",
        actor=actor,
        details={
            "certificate_number": cert.certificate_number,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(cert)
    return cert
