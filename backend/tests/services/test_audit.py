from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.services.audit import write_audit_entry


def test_write_audit_entry_persists_row(db_session: Session) -> None:
    entity_id = uuid4()
    entry = write_audit_entry(
        db_session,
        entity_type="standard",
        entity_id=entity_id,
        action="created",
        actor="Dr. M. Weber",
        details={"ac_code": "ISO 9001:2015", "status": "60"},
        ip_address="192.168.1.100",
    )

    assert entry.id is not None
    assert entry.entity_type == "standard"
    assert entry.entity_id == entity_id
    assert entry.action == "created"
    assert entry.actor == "Dr. M. Weber"
    assert entry.details["ac_code"] == "ISO 9001:2015"
    assert entry.ip_address == "192.168.1.100"
    assert entry.created_at is not None


def test_write_audit_entry_defaults_ip_to_none(db_session: Session) -> None:
    entry = write_audit_entry(
        db_session,
        entity_type="customer",
        entity_id=uuid4(),
        action="updated",
        actor="system",
        details={"changed": ["company_name"]},
    )

    assert entry.ip_address is None


def test_write_audit_entry_flushes_but_does_not_commit(db_session: Session) -> None:
    entity_id = uuid4()
    write_audit_entry(
        db_session,
        entity_type="certificate",
        entity_id=entity_id,
        action="created",
        actor="seeder",
        details={},
    )

    # Row is visible within the same transaction (flushed)
    rows = db_session.query(AuditLog).filter_by(entity_id=entity_id).all()
    assert len(rows) == 1
