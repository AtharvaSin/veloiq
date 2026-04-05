from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def test_audit_log_captures_structured_details(db_session: Session) -> None:
    entry = AuditLog(
        entity_type="standard",
        entity_id=uuid4(),
        action="created",
        actor="Dr. M. Weber",
        details={"ac_code": "ISO 9001:2015", "status": "60"},
        ip_address="192.168.1.100",
    )
    db_session.add(entry)
    db_session.flush()

    assert entry.id is not None
    assert entry.details["ac_code"] == "ISO 9001:2015"
    assert entry.created_at is not None
