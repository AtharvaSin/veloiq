import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.customer import Customer
from data_seeder.seed_customers import seed_customers


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_customers_creates_30_records(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    assert len(customers) == 30
    assert db_session.query(Customer).count() == 30


def test_seed_customers_country_distribution(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    counts = Counter(c.country for c in customers)
    assert counts["DE"] == 10
    assert counts["CN"] == 8
    assert counts["IN"] == 5
    assert counts["GB"] == 4
    assert counts["US"] == 3


def test_seed_customers_have_unique_customer_numbers(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    numbers = [c.customer_number for c in customers]
    assert len(numbers) == len(set(numbers))


def test_seed_customers_is_deterministic(db_session: Session) -> None:
    _seeded()
    first = [c.customer_number for c in seed_customers(db_session)]
    db_session.query(Customer).delete()
    db_session.flush()

    _seeded()
    second = [c.customer_number for c in seed_customers(db_session)]
    assert first == second
