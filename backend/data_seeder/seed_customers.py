"""Seed 30 customers with fixed country distribution (10 DE, 8 CN, 5 IN, 4 GB, 3 US)."""
from faker import Faker
from sqlalchemy.orm import Session

from app.models.customer import Customer
from data_seeder.providers import TICProvider

COUNTRY_DISTRIBUTION: list[tuple[str, str, str, int]] = [
    # (country ISO2, sales_area, language, count)
    ("DE", "EMEA", "DE", 10),
    ("CN", "Greater China", "ZH", 8),
    ("IN", "South Asia", "EN", 5),
    ("GB", "EMEA", "EN", 4),
    ("US", "Americas", "EN", 3),
]


def seed_customers(db: Session, fake: Faker | None = None) -> list[Customer]:
    """Insert 30 deterministic customers. Caller must flush or commit."""
    if fake is None:
        fake = Faker()
    fake.add_provider(TICProvider)

    customers: list[Customer] = []
    counter = 1
    for country, sales_area, language, count in COUNTRY_DISTRIBUTION:
        for _ in range(count):
            customer = Customer(
                customer_number=f"CUST-{counter:04d}",
                company_name=fake.tic_company_name(),
                country=country,
                sales_area=sales_area,
                language=language,
                contact_name=fake.name(),
                contact_email=fake.company_email(),
            )
            db.add(customer)
            customers.append(customer)
            counter += 1

    db.flush()
    return customers
