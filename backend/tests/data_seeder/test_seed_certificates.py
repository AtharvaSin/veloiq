from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from data_seeder.seed_certificates import FUZZY_MATCH_SAP_REFS, seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_standards import seed_standards


def _bootstrap(db_session: Session):
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    return customers, standards


def test_seed_certificates_creates_10_records(db_session: Session) -> None:
    customers, standards = _bootstrap(db_session)
    certs, links = seed_certificates_and_links(db_session, customers, standards)

    assert len(certs) == 10
    assert db_session.query(Certificate).count() == 10


def test_seed_cert_links_count_around_15(db_session: Session) -> None:
    customers, standards = _bootstrap(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)

    assert 12 <= len(links) <= 18
    assert db_session.query(CertStandardLink).count() == len(links)


def test_fuzzy_match_sap_refs_present(db_session: Session) -> None:
    """All 5 messy SAP-format fuzzy-match refs must be present in cert_standard_links."""
    customers, standards = _bootstrap(db_session)
    seed_certificates_and_links(db_session, customers, standards)

    stored_refs = {link.standard_ref for link in db_session.query(CertStandardLink).all()}
    expected_sap_refs = {pair[1] for pair in FUZZY_MATCH_SAP_REFS}
    assert expected_sap_refs.issubset(stored_refs)


def test_certificate_statuses_all_valid(db_session: Session) -> None:
    customers, standards = _bootstrap(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    valid_statuses = {"active", "expiring", "expired", "suspended"}
    assert all(c.status in valid_statuses for c in certs)


def test_certificates_reference_existing_customers(db_session: Session) -> None:
    customers, standards = _bootstrap(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    customer_ids = {c.id for c in customers}
    assert all(cert.customer_id in customer_ids for cert in certs)


def test_seed_certificates_is_deterministic(db_session: Session) -> None:
    customers, standards = _bootstrap(db_session)
    certs1, links1 = seed_certificates_and_links(db_session, customers, standards)
    first_nums = [c.certificate_number for c in certs1]

    # Clear and redo
    db_session.query(CertStandardLink).delete()
    db_session.query(Certificate).delete()
    db_session.flush()

    certs2, _ = seed_certificates_and_links(db_session, customers, standards)
    assert first_nums == [c.certificate_number for c in certs2]
