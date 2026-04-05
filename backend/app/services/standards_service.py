"""Standards mutation service. Every mutation writes an audit_log entry."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.standard import Standard
from app.schemas.standard import StandardCreate, StandardUpdate
from app.services.audit import write_audit_entry


def create_standard(
    db: Session,
    payload: StandardCreate,
    actor: str,
) -> Standard:
    """Create a Standard and write a paired audit_log entry."""
    now = datetime.now(UTC)
    # Phase A placeholder normalization — Phase B replaces with real engine
    normalized = payload.ac_code.lower().strip()

    standard = Standard(
        id=uuid4(),
        ac_code=payload.ac_code,
        title=payload.title,
        status=payload.status,
        replaced_by=payload.replaced_by,
        committee=payload.committee,
        ics_code=payload.ics_code,
        normalized_code=normalized,
        base_number=normalized,
        source_payload=payload.source_payload,
        ingested_at=now,
    )
    db.add(standard)
    db.flush()

    write_audit_entry(
        db,
        entity_type="standard",
        entity_id=standard.id,
        action="created",
        actor=actor,
        details={
            "ac_code": standard.ac_code,
            "status": standard.status,
            "title": standard.title,
        },
    )

    db.commit()
    db.refresh(standard)
    return standard


def update_standard(
    db: Session,
    standard_id: UUID,
    payload: StandardUpdate,
    actor: str,
) -> Standard:
    """Update a Standard and write a paired audit_log entry capturing diffs."""
    standard = db.get(Standard, standard_id)
    if standard is None:
        raise NotFoundError(entity="standard", entity_id=standard_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(standard, field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
            setattr(standard, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="standard",
        entity_id=standard.id,
        action="updated",
        actor=actor,
        details={
            "ac_code": standard.ac_code,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(standard)
    return standard
