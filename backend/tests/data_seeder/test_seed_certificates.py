import random

from faker import Faker
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from data_seeder.seed_certificates import FUZZY_MATCH_SAP_REFS, seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_standards import seed_standards


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_certificates_creates_200_records(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, links = seed_certificates_and_links(db_session, customers, standards)

    assert len(certs) == 200
    assert db_session.query(Certificate).count() == 200


def test_seed_certificates_distributed_across_customers(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    # Every certificate should reference an existing customer
    customer_ids = {c.id for c in customers}
    assert all(cert.customer_id in customer_ids for cert in certs)

    # No customer has more than 10 certificates, none has zero
    from collections import Counter
    counts = Counter(cert.customer_id for cert in certs)
    assert max(counts.values()) <= 10
    assert min(counts.values()) >= 1


def test_seed_cert_links_count_around_400(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)

    assert 380 <= len(links) <= 420  # ~2 per cert ± noise
    assert db_session.query(CertStandardLink).count() == len(links)


def test_fuzzy_match_sap_refs_present(db_session: Session) -> None:
    """All 7 messy SAP-format refs must be present in cert_standard_links."""
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    seed_certificates_and_links(db_session, customers, standards)

    stored_refs = {link.standard_ref for link in db_session.query(CertStandardLink).all()}
    expected_sap_refs = {pair[1] for pair in FUZZY_MATCH_SAP_REFS}
    assert expected_sap_refs.issubset(stored_refs)


def test_certificate_statuses_all_valid(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    valid_statuses = {"active", "expiring", "expired", "suspended"}
    assert all(c.status in valid_statuses for c in certs)
