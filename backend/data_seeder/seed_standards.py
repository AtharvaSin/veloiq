"""Seed 50 standards across ISO stages including 7 fuzzy-match anchor codes."""
import uuid
from datetime import UTC, datetime

from faker import Faker
from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.providers import TICProvider

# Namespace UUID for deterministic standard IDs derived from ac_code
_STANDARDS_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

# (status, count) — totals to 50
STATUS_DISTRIBUTION: list[tuple[str, int]] = [
    ("00", 3),
    ("10", 3),
    ("20", 2),
    ("30", 5),
    ("40", 5),
    ("50", 5),
    ("60", 15),
    ("90", 7),
    ("95", 5),
]

# 7 anchor codes that pair with messy SAP refs in Task 34 (fuzzy-match test pairs)
FUZZY_MATCH_ANCHORS: list[tuple[str, str, str, str, int | None]] = [
    # (ac_code, title, base_number, normalized_code, version_year)
    ("ISO 9001:2015", "Quality management systems — Requirements", "9001", "iso 9001:2015", 2015),
    ("ISO 14001:2015", "Environmental management systems — Requirements", "14001", "iso 14001:2015", 2015),
    ("IEC 62368-1:2023", "Audio/video, information and communication technology equipment — Safety", "62368", "iec 62368-1:2023", 2023),
    ("ISO 1234:1998", "Gear tooth modifications", "1234", "iso 1234:1998", 1998),
    ("ISO 14001", "Environmental management systems", "14001", "iso 14001", None),
    ("ISO 45001:2018", "Occupational health and safety management systems", "45001", "iso 45001:2018", 2018),
    ("IEC 61000-4-2:2008", "Electromagnetic compatibility — ESD immunity test", "61000", "iec 61000-4-2:2008", 2008),
]


def _parse_version_year(ac_code: str) -> int | None:
    if ":" in ac_code:
        tail = ac_code.rsplit(":", 1)[1]
        if tail.isdigit():
            return int(tail)
    return None


def seed_standards(db: Session, fake: Faker | None = None) -> list[Standard]:
    """Insert 50 deterministic standards. Includes 7 fuzzy-match anchor codes."""
    if fake is None:
        fake = Faker()
    fake.add_provider(TICProvider)
    now = datetime.now(UTC)

    standards: list[Standard] = []
    used_codes: set[str] = set()

    # Pre-seed the 7 fuzzy anchors with status="60" (active, most common bucket)
    for ac_code, title, base_number, normalized_code, version_year in FUZZY_MATCH_ANCHORS:
        standard = Standard(
            id=uuid.uuid5(_STANDARDS_NAMESPACE, ac_code),
            ac_code=ac_code,
            title=title,
            status="60",
            normalized_code=normalized_code,
            base_number=base_number,
            version_year=version_year,
            committee=fake.committee_name(),
            ics_code=fake.ics_code(),
            source_payload={"source": "fuzzy_anchor", "raw": ac_code},
            ingested_at=now,
        )
        db.add(standard)
        standards.append(standard)
        used_codes.add(ac_code)

    # Distribution tracker: how many of each status we still need.
    remaining: dict[str, int] = dict(STATUS_DISTRIBUTION)
    # Anchors consumed 7 "60" slots already
    remaining["60"] = max(0, remaining["60"] - 7)

    # Fill remainder
    for status, count in remaining.items():
        for _ in range(count):
            while True:
                ac_code = fake.standard_code()
                if ac_code not in used_codes:
                    used_codes.add(ac_code)
                    break
            base_number = ac_code.split()[1].split(":")[0].split("-")[0]
            version_year = _parse_version_year(ac_code)
            standard = Standard(
                id=uuid.uuid5(_STANDARDS_NAMESPACE, ac_code),
                ac_code=ac_code,
                title=fake.sentence(nb_words=8).rstrip("."),
                status=status,
                normalized_code=ac_code.lower(),
                base_number=base_number,
                version_year=version_year,
                committee=fake.committee_name(),
                ics_code=fake.ics_code(),
                source_payload={"source": "synthetic", "raw": ac_code},
                ingested_at=now,
            )
            db.add(standard)
            standards.append(standard)

    db.flush()
    return standards
