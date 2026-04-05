from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard
from data_seeder.seed_all import run_seed_pipeline


def test_orchestrator_seeds_expected_counts(db_session: Session) -> None:
    run_seed_pipeline(db_session)

    assert db_session.query(Customer).count() == 30
    assert db_session.query(Standard).count() == 50
    assert db_session.query(Certificate).count() == 200
    assert 380 <= db_session.query(CertStandardLink).count() <= 420
    assert db_session.query(MatchResult).count() == 30
    assert db_session.query(Assessment).count() == 30
    assert db_session.query(Notification).count() == 20
    assert db_session.query(SalesEscalation).count() == 5


def test_orchestrator_is_deterministic_across_runs(db_session: Session) -> None:
    """Two runs of the pipeline produce IDENTICAL data (counts + deterministic fields)."""
    run_seed_pipeline(db_session)
    first_customers = [
        (c.customer_number, c.company_name, c.country)
        for c in db_session.query(Customer).order_by(Customer.customer_number).all()
    ]
    first_standards = [
        (s.ac_code, s.title, s.status)
        for s in db_session.query(Standard).order_by(Standard.ac_code).all()
    ]

    # Clear everything, re-run
    for model in (
        AuditLog, SalesEscalation, Notification, Assessment, MatchResult,
        CertStandardLink, Certificate, Standard, Customer,
    ):
        db_session.query(model).delete()
    db_session.flush()

    run_seed_pipeline(db_session)
    second_customers = [
        (c.customer_number, c.company_name, c.country)
        for c in db_session.query(Customer).order_by(Customer.customer_number).all()
    ]
    second_standards = [
        (s.ac_code, s.title, s.status)
        for s in db_session.query(Standard).order_by(Standard.ac_code).all()
    ]

    assert first_customers == second_customers
    assert first_standards == second_standards
