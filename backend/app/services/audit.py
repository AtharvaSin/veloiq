"""Audit log enforcement helper.

Every mutation service MUST call `write_audit_entry()` inside the same
transaction as the entity it is auditing. The application user is
REVOKE'd from UPDATE/DELETE on the audit_log table — entries are
append-only once committed.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit_entry(
    db: Session,
    *,
    entity_type: str,
    entity_id: UUID,
    action: str,
    actor: str,
    details: dict[str, Any],
    ip_address: str | None = None,
) -> AuditLog:
    """Write an immutable audit log entry.

    MUST be called within the same transaction as the mutation it audits.
    The returned AuditLog has been flushed but not committed — the caller
    is responsible for committing the containing transaction.

    Args:
        db: Active SQLAlchemy session.
        entity_type: Resource name (e.g., "standard", "customer").
        entity_id: UUID of the entity being mutated.
        action: Verb describing the mutation (e.g., "created", "updated").
        actor: Identifier for the user/service performing the action.
        details: JSON-serializable dict capturing what changed.
        ip_address: Optional IPv4/IPv6 address of the request source.

    Returns:
        The persisted AuditLog instance (flushed, not committed).
    """
    entry = AuditLog(
        id=uuid4(),
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        details=details,
        ip_address=ip_address,
        created_at=datetime.now(UTC),
    )
    db.add(entry)
    db.flush()
    return entry
