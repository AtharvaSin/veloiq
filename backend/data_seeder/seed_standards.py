"""Seed 10 curated real-world TIC standards with correct committees and ICS codes."""
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.standard import Standard

# Namespace UUID for deterministic standard IDs derived from ac_code
_STANDARDS_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

# (ac_code, title, status, base_number, version_year, committee, ics_code)
CURATED_STANDARDS: list[dict[str, Any]] = [
    {"ac_code": "ISO 9001:2015",        "title": "Quality management systems — Requirements",                                                                                                    "status": "60", "base": "9001",   "year": 2015, "committee": "ISO/TC 176",          "ics": "03.120.10"},
    {"ac_code": "ISO 14001:2015",       "title": "Environmental management systems — Requirements with guidance for use",                                                                        "status": "60", "base": "14001",  "year": 2015, "committee": "ISO/TC 207",          "ics": "13.020.10"},
    {"ac_code": "ISO 45001:2018",       "title": "Occupational health and safety management systems — Requirements",                                                                             "status": "60", "base": "45001",  "year": 2018, "committee": "ISO/TC 283",          "ics": "13.100.00"},
    {"ac_code": "IEC 62368-1:2023",     "title": "Audio/video, information and communication technology equipment — Part 1: Safety requirements",                                               "status": "60", "base": "62368",  "year": 2023, "committee": "IEC/TC 108",          "ics": "33.160.01"},
    {"ac_code": "IEC 61010-1:2010",     "title": "Safety requirements for electrical equipment for measurement, control, and laboratory use — Part 1: General requirements",                    "status": "60", "base": "61010",  "year": 2010, "committee": "IEC/TC 66",           "ics": "19.080.00"},
    {"ac_code": "ISO 13485:2016",       "title": "Medical devices — Quality management systems — Requirements for regulatory purposes",                                                          "status": "60", "base": "13485",  "year": 2016, "committee": "ISO/TC 210",          "ics": "11.040.01"},
    {"ac_code": "IEC 60601-1:2020",     "title": "Medical electrical equipment — Part 1: General requirements for basic safety and essential performance",                                       "status": "90", "base": "60601",  "year": 2020, "committee": "IEC/TC 62",           "ics": "11.040.01"},
    {"ac_code": "IEC 60601-1:2024",     "title": "Medical electrical equipment — Part 1: General requirements for basic safety and essential performance",                                       "status": "10", "base": "60601",  "year": 2024, "committee": "IEC/TC 62",           "ics": "11.040.01"},
    {"ac_code": "ISO 27001:2022",       "title": "Information security, cybersecurity and privacy protection — Information security management systems — Requirements",                          "status": "60", "base": "27001",  "year": 2022, "committee": "ISO/IEC JTC 1/SC 27", "ics": "35.030.00"},
    {"ac_code": "IEC 62443-3-3:2023",   "title": "Industrial communication networks — Network and system security — Part 3-3: System security requirements and security levels",                "status": "60", "base": "62443",  "year": 2023, "committee": "IEC/TC 65",           "ics": "25.040.40"},
]

# The 5 fuzzy-match SAP-format test refs (first 5 of CURATED_LINKS in seed_certificates)
# Exposed here so test_seed_standards can assert them via FUZZY_MATCH_ANCHORS if needed.
FUZZY_MATCH_ANCHORS: list[str] = [
    "ISO 9001:2015",
    "ISO 14001:2015",
    "IEC 62368-1:2023",
    "IEC 60601-1:2020",
    "IEC 62443-3-3:2023",
]


def seed_standards(db: Session, fake: object | None = None) -> list[Standard]:
    """Insert 10 curated standards. Caller must flush or commit.

    IEC 60601-1:2020 (status 90, withdrawn) has replaced_by set to IEC 60601-1:2024.
    The ``fake`` parameter is accepted but unused — data is fully curated.
    """
    now = datetime.now(UTC)
    standards: list[Standard] = []

    for row in CURATED_STANDARDS:
        ac_code = row["ac_code"]
        replaced_by = "IEC 60601-1:2024" if ac_code == "IEC 60601-1:2020" else None

        standard = Standard(
            id=uuid.uuid5(_STANDARDS_NAMESPACE, ac_code),
            ac_code=ac_code,
            title=row["title"],
            status=row["status"],
            replaced_by=replaced_by,
            normalized_code=ac_code.lower(),
            base_number=row["base"],
            version_year=row["year"],
            committee=row["committee"],
            ics_code=row["ics"],
            source_payload={"source": "curated", "ics": row["ics"], "committee": row["committee"]},
            ingested_at=now,
        )
        db.add(standard)
        standards.append(standard)

    db.flush()
    return standards
