"""Seed 10 certificates + ~15 cert_standard_links including 5 fuzzy-match SAP test pairs."""
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.standard import Standard

# 5 fuzzy-match test pairs (first 5 entries of CURATED_LINKS).
# Exposed as module constant so tests can import and assert on them.
# (anchor_ac_code, messy_sap_ref, normalized_ref, base_number)
FUZZY_MATCH_SAP_REFS: list[tuple[str, str, str, str]] = [
    ("IEC 62443-3-3:2023", "DIN EN 62443-3-3 VDE 0802-3-3:2023-12",  "62443-3-3:2023",  "62443"),
    ("ISO 9001:2015",       "DIN EN ISO 9001:2015-11",                 "9001:2015",        "9001"),
    ("IEC 62368-1:2023",    "EN IEC 62368-1:2023/AC:2024",             "62368-1:2023",     "62368"),
    ("ISO 14001:2015",      "BS EN ISO 14001:2015",                    "14001:2015",       "14001"),
    ("IEC 60601-1:2020",    "IEC 60601-1 Ed.3.2:2020",                 "60601-1:2020",     "60601"),
]

# (cert_number, customer_idx 0-based, product, status, issue_offset_days, expiry_offset_days)
CURATED_CERTS: list[dict[str, Any]] = [
    {"tc": "TC-00001", "cust": 0, "product": "Industrial PLC Module S7-1500 (Siemens Safety Integrated)",   "status": "active",    "issue_d": -720,  "expiry_d": 365},
    {"tc": "TC-00002", "cust": 0, "product": "SINAMICS Motion Control Drive S120 Booksize",                 "status": "active",    "issue_d": -540,  "expiry_d": 545},
    {"tc": "TC-00003", "cust": 1, "product": "Hydraulic Pressure Transducer HM20",                          "status": "expiring",  "issue_d": -1020, "expiry_d": 60},
    {"tc": "TC-00004", "cust": 3, "product": "Modicon M580 Safety PLC — BMEP58",                            "status": "active",    "issue_d": -365,  "expiry_d": 730},
    {"tc": "TC-00005", "cust": 4, "product": "5G Base Station Unit BBU5900 (Huawei RAN)",                   "status": "active",    "issue_d": -280,  "expiry_d": 815},
    {"tc": "TC-00006", "cust": 5, "product": "HVDC Transformer Unit 800kV (UHVDC Grid)",                    "status": "active",    "issue_d": -450,  "expiry_d": 645},
    {"tc": "TC-00007", "cust": 6, "product": "BW Solo Single-Gas Detector (H2S variant)",                   "status": "expired",   "issue_d": -1460, "expiry_d": -365},
    {"tc": "TC-00008", "cust": 7, "product": "Continuous Caster Mold Assembly (CC-MLD-420)",                "status": "active",    "issue_d": -210,  "expiry_d": 885},
    {"tc": "TC-00009", "cust": 8, "product": "Agricultural Tractor Cab Frame — Arjun Novo Series",          "status": "active",    "issue_d": -150,  "expiry_d": 945},
    {"tc": "TC-00010", "cust": 9, "product": "Trent XWB Turbofan Engine Control Unit (EECU)",               "status": "suspended", "issue_d": -1825, "expiry_d": -100},
]

# 15 cert_standard_links — indices refer to CURATED_CERTS and CURATED_STANDARDS (both 0-based)
# First 5 are the FUZZY-MATCH TEST PAIRS; remainder are clean links.
CURATED_LINKS: list[dict[str, Any]] = [
    # FUZZY PAIRS (cert_idx, std_idx, raw SAP ref, normalized_ref, base_number)
    {"cert": 0, "std": 9, "raw": "DIN EN 62443-3-3 VDE 0802-3-3:2023-12",  "norm": "62443-3-3:2023",  "base": "62443"},
    {"cert": 0, "std": 0, "raw": "DIN EN ISO 9001:2015-11",                 "norm": "9001:2015",        "base": "9001"},
    {"cert": 4, "std": 3, "raw": "EN IEC 62368-1:2023/AC:2024",             "norm": "62368-1:2023",     "base": "62368"},
    {"cert": 5, "std": 1, "raw": "BS EN ISO 14001:2015",                    "norm": "14001:2015",       "base": "14001"},
    {"cert": 9, "std": 6, "raw": "IEC 60601-1 Ed.3.2:2020",                 "norm": "60601-1:2020",     "base": "60601"},
    # CLEAN LINKS
    {"cert": 1, "std": 3, "raw": "IEC 62368-1:2023",                        "norm": "62368-1:2023",     "base": "62368"},
    {"cert": 2, "std": 4, "raw": "IEC 61010-1:2010",                        "norm": "61010-1:2010",     "base": "61010"},
    {"cert": 3, "std": 9, "raw": "IEC 62443-3-3:2023",                      "norm": "62443-3-3:2023",   "base": "62443"},
    {"cert": 5, "std": 4, "raw": "IEC 61010-1:2010",                        "norm": "61010-1:2010",     "base": "61010"},
    {"cert": 6, "std": 4, "raw": "IEC 61010-1:2010",                        "norm": "61010-1:2010",     "base": "61010"},
    {"cert": 7, "std": 0, "raw": "ISO 9001:2015",                           "norm": "9001:2015",        "base": "9001"},
    {"cert": 7, "std": 1, "raw": "ISO 14001:2015",                          "norm": "14001:2015",       "base": "14001"},
    {"cert": 7, "std": 2, "raw": "ISO 45001:2018",                          "norm": "45001:2018",       "base": "45001"},
    {"cert": 8, "std": 2, "raw": "ISO 45001:2018",                          "norm": "45001:2018",       "base": "45001"},
    {"cert": 9, "std": 5, "raw": "ISO 13485:2016",                          "norm": "13485:2016",       "base": "13485"},
]


def seed_certificates_and_links(
    db: Session,
    customers: list[Customer],
    standards: list[Standard],
    fake: object | None = None,
) -> tuple[list[Certificate], list[CertStandardLink]]:
    """Insert 10 curated certificates + 15 cert_standard_links (5 fuzzy SAP test pairs).

    The ``fake`` parameter is accepted but unused — data is fully curated.
    """
    now = datetime.now(UTC)
    today = date.today()

    certificates: list[Certificate] = []
    for row in CURATED_CERTS:
        issue_date = today + timedelta(days=row["issue_d"])
        expiry_date = today + timedelta(days=row["expiry_d"])
        cert = Certificate(
            certificate_number=row["tc"],
            customer_id=customers[row["cust"]].id,
            product_description=row["product"],
            status=row["status"],
            issue_date=issue_date,
            expiry_date=expiry_date,
        )
        db.add(cert)
        certificates.append(cert)

    db.flush()

    links: list[CertStandardLink] = []
    for row in CURATED_LINKS:
        link = CertStandardLink(
            certificate_id=certificates[row["cert"]].id,
            standard_ref=row["raw"],
            normalized_ref=row["norm"],
            base_number=row["base"],
            linked_at=now,
        )
        db.add(link)
        links.append(link)

    db.flush()
    return certificates, links
