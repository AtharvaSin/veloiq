"""Seed 200 certificates + ~400 cert_standard_links including 7 fuzzy-match test pairs."""
import random
from datetime import UTC, date, datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.standard import Standard
from data_seeder.providers import TICProvider

# 7 fuzzy-match test pairs: (anchor_ac_code, messy_sap_ref, normalized_ref, base_number)
FUZZY_MATCH_SAP_REFS: list[tuple[str, str, str, str]] = [
    ("ISO 9001:2015", "DIN EN ISO 9001:2015-11", "9001:2015", "9001"),
    ("ISO 14001:2015", "BS EN ISO 14001:2015", "14001:2015", "14001"),
    ("IEC 62368-1:2023", "EN IEC 62368-1:2023/AC:2024", "62368-1:2023", "62368"),
    ("ISO 1234:1998", "ANSI ABC 331:1999/ISO 1234:1998", "1234:1998", "1234"),
    ("ISO 14001", "ISO 1401", "1401", "1401"),
    ("ISO 45001:2018", "GB/T 45001-2020", "45001:2020", "45001"),
    ("IEC 61000-4-2:2008", "DIN EN 61000-4-2 VDE 0847-4-2:2010-04", "61000-4-2:2010", "61000"),
]

CERT_STATUSES: list[tuple[str, float]] = [
    ("active", 0.65),
    ("expiring", 0.15),
    ("expired", 0.15),
    ("suspended", 0.05),
]


def _choose_status() -> str:
    r = random.random()
    cumulative = 0.0
    for status, weight in CERT_STATUSES:
        cumulative += weight
        if r <= cumulative:
            return status
    return "active"


def _distribute_certs_across_customers(num_customers: int, total_certs: int) -> list[int]:
    """Return list of length num_customers where each entry is 1-10 and sum == total_certs."""
    # Start with 1 per customer (ensures min=1)
    counts = [1] * num_customers
    remaining = total_certs - num_customers

    while remaining > 0:
        idx = random.randrange(num_customers)
        if counts[idx] < 10:
            counts[idx] += 1
            remaining -= 1
    return counts


def seed_certificates_and_links(
    db: Session,
    customers: list[Customer],
    standards: list[Standard],
    fake: Faker | None = None,
) -> tuple[list[Certificate], list[CertStandardLink]]:
    """Insert 200 certs + ~400 links. Includes 7 fuzzy-match SAP-format test pairs."""
    if fake is None:
        fake = Faker()
    fake.add_provider(TICProvider)
    now = datetime.now(UTC)
    today = date.today()

    certs_per_customer = _distribute_certs_across_customers(len(customers), 200)

    certificates: list[Certificate] = []
    cert_counter = 1
    for customer, cert_count in zip(customers, certs_per_customer, strict=True):
        for _ in range(cert_count):
            status = _choose_status()
            # Issue date 0-5 years ago
            issue_offset_days = random.randint(0, 5 * 365)
            issue_date = today - timedelta(days=issue_offset_days)
            # Certificates are 3-year cycles typically
            expiry_date = issue_date + timedelta(days=3 * 365)

            cert = Certificate(
                certificate_number=f"TC-{40000 + cert_counter:05d}",
                customer_id=customer.id,
                product_description=fake.product_description(),
                status=status,
                issue_date=issue_date,
                expiry_date=expiry_date,
            )
            db.add(cert)
            certificates.append(cert)
            cert_counter += 1

    db.flush()

    # --- Links: ~2 per certificate, plus embed the 7 fuzzy pairs ---
    links: list[CertStandardLink] = []

    # 1) Embed 7 fuzzy-match SAP refs onto the first 7 certificates
    for idx, (_, sap_ref, normalized_ref, base_number) in enumerate(FUZZY_MATCH_SAP_REFS):
        link = CertStandardLink(
            certificate_id=certificates[idx].id,
            standard_ref=sap_ref,
            normalized_ref=normalized_ref,
            base_number=base_number,
            linked_at=now,
        )
        db.add(link)
        links.append(link)

    # 2) For every certificate, add 1-3 synthetic links (~2 avg)
    for cert in certificates:
        num_links = random.choices([1, 2, 3], weights=[0.25, 0.5, 0.25], k=1)[0]
        chosen = random.sample(standards, k=min(num_links, len(standards)))
        for std in chosen:
            link = CertStandardLink(
                certificate_id=cert.id,
                standard_ref=std.ac_code,
                normalized_ref=std.normalized_code,
                base_number=std.base_number,
                linked_at=now,
            )
            db.add(link)
            links.append(link)

    db.flush()
    return certificates, links
