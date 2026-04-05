from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.seed_standards import FUZZY_MATCH_ANCHORS, seed_standards


def test_seed_standards_creates_10_records(db_session: Session) -> None:
    standards = seed_standards(db_session)
    assert len(standards) == 10
    assert db_session.query(Standard).count() == 10


def test_seed_standards_ac_codes_unique(db_session: Session) -> None:
    standards = seed_standards(db_session)
    codes = [s.ac_code for s in standards]
    assert len(codes) == len(set(codes))


def test_seed_standards_includes_fuzzy_match_anchors(db_session: Session) -> None:
    """The 5 fuzzy-match anchor ac_codes must be present in the seeded standards."""
    seed_standards(db_session)
    codes = {s.ac_code for s in db_session.query(Standard).all()}
    assert set(FUZZY_MATCH_ANCHORS).issubset(codes)


def test_seed_standards_real_standard_codes_present(db_session: Session) -> None:
    """All 10 curated real-world ac_codes must be seeded."""
    seed_standards(db_session)
    codes = {s.ac_code for s in db_session.query(Standard).all()}
    expected = {
        "ISO 9001:2015",
        "ISO 14001:2015",
        "ISO 45001:2018",
        "IEC 62368-1:2023",
        "IEC 61010-1:2010",
        "ISO 13485:2016",
        "IEC 60601-1:2020",
        "IEC 60601-1:2024",
        "ISO 27001:2022",
        "IEC 62443-3-3:2023",
    }
    assert expected == codes


def test_seed_standards_iec_60601_replaced_by_set(db_session: Session) -> None:
    """IEC 60601-1:2020 (withdrawn) must have replaced_by pointing to the 2024 draft."""
    seed_standards(db_session)
    withdrawn = db_session.query(Standard).filter_by(ac_code="IEC 60601-1:2020").one()
    assert withdrawn.replaced_by == "IEC 60601-1:2024"
    assert withdrawn.status == "90"


def test_seed_standards_is_deterministic(db_session: Session) -> None:
    first = [(s.ac_code, s.title) for s in seed_standards(db_session)]
    db_session.query(Standard).delete()
    db_session.flush()

    second = [(s.ac_code, s.title) for s in seed_standards(db_session)]
    assert first == second
