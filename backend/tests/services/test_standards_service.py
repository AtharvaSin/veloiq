from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.schemas.standard import StandardCreate, StandardUpdate
from app.services.standards_service import create_standard, update_standard


def test_create_standard_returns_entity(db_session: Session) -> None:
    payload = StandardCreate(
        ac_code="ISO 9001:2015",
        title="Quality management systems — Requirements",
        status="60",
        source_payload={"raw": "iso-9001-2015"},
    )
    standard = create_standard(db_session, payload, actor="Dr. M. Weber")

    assert standard.id is not None
    assert standard.ac_code == "ISO 9001:2015"
    assert standard.status == "60"
    assert standard.normalized_code == "iso 9001:2015"
    assert standard.base_number == "iso 9001:2015"
    assert standard.ingested_at is not None


def test_create_standard_writes_audit_entry(db_session: Session) -> None:
    payload = StandardCreate(
        ac_code="IEC 62368-1:2023",
        title="Audio/video, information and communication technology equipment",
        status="60",
        source_payload={"raw": "iec-62368-1"},
    )
    standard = create_standard(db_session, payload, actor="Dr. M. Weber")

    entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=standard.id
    ).all()

    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].actor == "Dr. M. Weber"
    assert entries[0].details["ac_code"] == "IEC 62368-1:2023"
    assert entries[0].details["status"] == "60"


def test_update_standard_modifies_entity_and_audits(db_session: Session) -> None:
    created = create_standard(
        db_session,
        StandardCreate(
            ac_code="ISO 14001:2015",
            title="Environmental management systems",
            status="60",
            source_payload={"raw": "iso-14001"},
        ),
        actor="seeder",
    )

    updated = update_standard(
        db_session,
        created.id,
        StandardUpdate(status="95", replaced_by="ISO 14001:2026"),
        actor="Dr. M. Weber",
    )

    assert updated.id == created.id
    assert updated.status == "95"
    assert updated.replaced_by == "ISO 14001:2026"
    assert updated.title == "Environmental management systems"  # unchanged

    entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=created.id
    ).order_by(AuditLog.created_at).all()

    assert len(entries) == 2
    assert entries[0].action == "created"
    assert entries[0].actor == "seeder"
    assert entries[1].action == "updated"
    assert entries[1].actor == "Dr. M. Weber"
    assert entries[1].details["changed_fields"] == {
        "status": {"old": "60", "new": "95"},
        "replaced_by": {"old": None, "new": "ISO 14001:2026"},
    }


def test_update_standard_raises_not_found_for_missing_id(db_session: Session) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        update_standard(
            db_session,
            uuid4(),
            StandardUpdate(status="95"),
            actor="Dr. M. Weber",
        )

    assert excinfo.value.entity == "standard"


def test_update_standard_with_empty_payload_is_noop_but_still_audits(db_session: Session) -> None:
    created = create_standard(
        db_session,
        StandardCreate(
            ac_code="ISO 45001:2018",
            title="OH&S management systems",
            status="60",
            source_payload={},
        ),
        actor="seeder",
    )
    updated = update_standard(
        db_session, created.id, StandardUpdate(), actor="Dr. M. Weber"
    )

    assert updated.status == "60"
    entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=created.id, action="updated"
    ).all()
    assert len(entries) == 1
    assert entries[0].details["changed_fields"] == {}
