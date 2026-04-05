from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead


def test_audit_log_read_from_orm_model(db_session: Session) -> None:
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

    read = AuditLogRead.model_validate(entry)
    assert read.id == entry.id
    assert read.entity_type == "standard"
    assert read.action == "created"
    assert read.actor == "Dr. M. Weber"
    assert read.details == {"ac_code": "ISO 9001:2015", "status": "60"}
    assert read.ip_address == "192.168.1.100"
    assert read.created_at is not None


def test_audit_log_read_preserves_nullable_ip(db_session: Session) -> None:
    entry = AuditLog(
        entity_type="assessment",
        entity_id=uuid4(),
        action="decision_recorded",
        actor="system",
        details={"decision": "approved"},
        ip_address=None,
    )
    db_session.add(entry)
    db_session.flush()

    read = AuditLogRead.model_validate(entry)
    assert read.ip_address is None
    assert read.details["decision"] == "approved"


def test_audit_log_read_uses_from_attributes() -> None:
    from app.schemas.audit_log import AuditLogRead

    assert isinstance(AuditLogRead.model_config, dict)
    assert AuditLogRead.model_config.get("from_attributes") is True
