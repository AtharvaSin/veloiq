"""SalesEscalation mutation service. PATCH-only — escalations are system-generated."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.sales_escalation import SalesEscalation
from app.schemas.sales_escalation import SalesEscalationUpdate
from app.services.audit import write_audit_entry


def update_escalation(
    db: Session,
    escalation_id: UUID,
    payload: SalesEscalationUpdate,
    actor: str,
) -> SalesEscalation:
    """Update a SalesEscalation status/assigned_to and write a paired audit entry."""
    esc = db.get(SalesEscalation, escalation_id)
    if esc is None:
        raise NotFoundError(entity="sales_escalation", entity_id=escalation_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(esc, field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
            setattr(esc, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="sales_escalation",
        entity_id=esc.id,
        action="updated",
        actor=actor,
        details={
            "escalation_reason": esc.escalation_reason,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(esc)
    return esc
