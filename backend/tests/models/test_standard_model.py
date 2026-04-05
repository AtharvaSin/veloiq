from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.standard import Standard


def test_standard_can_be_created_with_required_fields(db_session: Session) -> None:
    standard = Standard(
        ac_code="ISO 9001:2015",
        title="Quality management systems — Requirements",
        status="60",
        normalized_code="iso 9001:2015",
        base_number="9001",
        version_year=2015,
        source_payload={"raw": "test"},
        ingested_at=datetime.now(timezone.utc),
    )
    db_session.add(standard)
    db_session.flush()

    assert standard.id is not None
    assert standard.ac_code == "ISO 9001:2015"
    assert standard.status == "60"
    assert standard.source_payload == {"raw": "test"}


def test_standard_ac_code_must_be_unique(db_session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    common = dict(
        ac_code="ISO 9999:2025", title="T", status="60",
        normalized_code="iso 9999:2025", base_number="9999",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    db_session.add(Standard(**common))
    db_session.flush()
    db_session.add(Standard(**common))
    with pytest.raises(IntegrityError):
        db_session.flush()
