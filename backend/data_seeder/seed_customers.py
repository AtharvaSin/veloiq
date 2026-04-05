"""Seed 10 curated customers with realistic TIC-domain company names and contacts."""
from typing import Any

from sqlalchemy.orm import Session

from app.models.customer import Customer

CURATED_CUSTOMERS: list[dict[str, Any]] = [
    {"number": "CUST-0001", "company": "Siemens AG",                      "country": "DE", "area": "EMEA",          "lang": "DE", "contact": "Dr. Klaus Hoffmann",   "email": "klaus.hoffmann@siemens.example.com"},
    {"number": "CUST-0002", "company": "Bosch Rexroth GmbH",              "country": "DE", "area": "EMEA",          "lang": "DE", "contact": "Ingrid Müller",         "email": "ingrid.mueller@boschrexroth.example.com"},
    {"number": "CUST-0003", "company": "ABB Automation AG",               "country": "DE", "area": "EMEA",          "lang": "DE", "contact": "Stefan Weiss",          "email": "stefan.weiss@abb.example.com"},
    {"number": "CUST-0004", "company": "Schneider Electric SE",           "country": "DE", "area": "EMEA",          "lang": "EN", "contact": "Marie Laurent",         "email": "marie.laurent@schneider.example.com"},
    {"number": "CUST-0005", "company": "Huawei Technologies Co., Ltd.",   "country": "CN", "area": "Greater China", "lang": "ZH", "contact": "Li Wei",                "email": "li.wei@huawei.example.com"},
    {"number": "CUST-0006", "company": "Hitachi Energy Ltd.",             "country": "CN", "area": "Greater China", "lang": "EN", "contact": "Chen Hao",              "email": "chen.hao@hitachi-energy.example.com"},
    {"number": "CUST-0007", "company": "Honeywell International Inc.",    "country": "US", "area": "Americas",      "lang": "EN", "contact": "Sarah Johnson",         "email": "sarah.johnson@honeywell.example.com"},
    {"number": "CUST-0008", "company": "Tata Steel Limited",              "country": "IN", "area": "South Asia",    "lang": "EN", "contact": "Priya Sharma",          "email": "priya.sharma@tatasteel.example.com"},
    {"number": "CUST-0009", "company": "Mahindra & Mahindra Ltd.",        "country": "IN", "area": "South Asia",    "lang": "EN", "contact": "Rajesh Patel",          "email": "rajesh.patel@mahindra.example.com"},
    {"number": "CUST-0010", "company": "Rolls-Royce Holdings plc",        "country": "GB", "area": "EMEA",          "lang": "EN", "contact": "James Whitfield",       "email": "james.whitfield@rolls-royce.example.com"},
]


def seed_customers(db: Session, fake: object | None = None) -> list[Customer]:
    """Insert 10 curated customers. Caller must flush or commit.

    The ``fake`` parameter is accepted but unused — data is fully curated.
    """
    customers: list[Customer] = []
    for row in CURATED_CUSTOMERS:
        customer = Customer(
            customer_number=row["number"],
            company_name=row["company"],
            country=row["country"],
            sales_area=row["area"],
            language=row["lang"],
            contact_name=row["contact"],
            contact_email=row["email"],
        )
        db.add(customer)
        customers.append(customer)

    db.flush()
    return customers
