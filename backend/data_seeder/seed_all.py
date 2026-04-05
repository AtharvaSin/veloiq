"""Orchestrator: TRUNCATE all tables (reverse FK order) then reseed deterministically.

Entry point for `make demo-reset`. Running this twice MUST produce identical data.
"""
import random

from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, engine
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards

TRUNCATE_SQL = text(
    "TRUNCATE audit_log, sales_escalations, notifications, assessments, "
    "match_results, cert_standard_links, certificates, standards, customers "
    "RESTART IDENTITY CASCADE"
)


def _reset_seeds() -> tuple[Faker, int]:
    """Reset both `random` and `Faker` to the configured fixed seed. Return Faker instance."""
    seed_val = settings.faker_seed
    random.seed(seed_val)
    Faker.seed(seed_val)
    fake = Faker()
    return fake, seed_val


def run_seed_pipeline(db: Session) -> dict[str, int]:
    """Reset seeds and execute all seeders in dependency order. Returns summary counts.

    Caller is responsible for commit/rollback. Used by both the CLI entry point
    and the test suite.
    """
    fake, _ = _reset_seeds()

    customers = seed_customers(db, fake)
    standards = seed_standards(db, fake)
    certificates, cert_links = seed_certificates_and_links(db, customers, standards, fake)
    matches, assessments, notifications, escalations = seed_historical(
        db, standards, cert_links, customers, fake
    )

    return {
        "customers": len(customers),
        "standards": len(standards),
        "certificates": len(certificates),
        "cert_standard_links": len(cert_links),
        "match_results": len(matches),
        "assessments": len(assessments),
        "notifications": len(notifications),
        "sales_escalations": len(escalations),
    }


def reset_and_seed() -> None:
    """CLI entry point: TRUNCATE all tables, then run full seeder pipeline."""
    # 1. Truncate in a fresh connection (outside the Session)
    with engine.connect() as conn:
        conn.execute(TRUNCATE_SQL)
        conn.commit()

    # 2. Re-seed inside a Session and commit
    with SessionLocal() as db:
        counts = run_seed_pipeline(db)
        db.commit()

    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    print(f"Seeded: {summary}")


if __name__ == "__main__":
    reset_and_seed()
