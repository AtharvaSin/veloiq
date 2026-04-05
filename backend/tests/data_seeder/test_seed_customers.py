from collections import Counter

from sqlalchemy.orm import Session

from app.models.customer import Customer
from data_seeder.seed_customers import seed_customers


def test_seed_customers_creates_10_records(db_session: Session) -> None:
    customers = seed_customers(db_session)
    assert len(customers) == 10
    assert db_session.query(Customer).count() == 10


def test_seed_customers_country_distribution(db_session: Session) -> None:
    customers = seed_customers(db_session)
    counts = Counter(c.country for c in customers)
    # DE: Siemens, Bosch, ABB, Schneider
    assert counts["DE"] == 4
    # CN: Huawei, Hitachi Energy
    assert counts["CN"] == 2
    # IN: Tata Steel, Mahindra
    assert counts["IN"] == 2
    # GB: Rolls-Royce
    assert counts["GB"] == 1
    # US: Honeywell
    assert counts["US"] == 1


def test_seed_customers_have_unique_customer_numbers(db_session: Session) -> None:
    customers = seed_customers(db_session)
    numbers = [c.customer_number for c in customers]
    assert len(numbers) == len(set(numbers))


def test_seed_customers_is_deterministic(db_session: Session) -> None:
    first = [(c.customer_number, c.company_name) for c in seed_customers(db_session)]
    db_session.query(Customer).delete()
    db_session.flush()

    second = [(c.customer_number, c.company_name) for c in seed_customers(db_session)]
    assert first == second


def test_seed_customers_named_companies_present(db_session: Session) -> None:
    """Key real-world company names must be seeded."""
    customers = seed_customers(db_session)
    names = {c.company_name for c in customers}
    expected = {
        "Siemens AG",
        "Bosch Rexroth GmbH",
        "ABB Automation AG",
        "Schneider Electric SE",
        "Huawei Technologies Co., Ltd.",
        "Hitachi Energy Ltd.",
        "Honeywell International Inc.",
        "Tata Steel Limited",
        "Mahindra & Mahindra Ltd.",
        "Rolls-Royce Holdings plc",
    }
    assert expected == names
