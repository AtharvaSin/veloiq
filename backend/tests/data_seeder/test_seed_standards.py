import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.seed_standards import seed_standards


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_standards_creates_50_records(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    assert len(standards) == 50
    assert db_session.query(Standard).count() == 50


def test_seed_standards_status_distribution(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    counts = Counter(s.status for s in standards)
    assert counts["00"] == 3
    assert counts["10"] + counts["20"] == 5
    assert counts["30"] == 5
    assert counts["40"] == 5
    assert counts["50"] == 5
    assert counts["60"] == 15
    assert counts["90"] == 7
    assert counts["95"] == 5


def test_seed_standards_includes_fuzzy_match_anchors(db_session: Session) -> None:
    """The 7 Natos sides of the fuzzy test pairs must be seeded as standards."""
    _seeded()
    seed_standards(db_session)
    codes = {s.ac_code for s in db_session.query(Standard).all()}
    expected_anchors = {
        "ISO 9001:2015",
        "ISO 14001:2015",
        "IEC 62368-1:2023",
        "ISO 1234:1998",
        "ISO 14001",
        "ISO 45001:2018",
        "IEC 61000-4-2:2008",
    }
    assert expected_anchors.issubset(codes)


def test_seed_standards_ac_codes_unique(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    codes = [s.ac_code for s in standards]
    assert len(codes) == len(set(codes))
