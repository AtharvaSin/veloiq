from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.customer import Customer


def _make_customer(db: Session, **overrides) -> Customer:
    defaults = dict(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="Acme Test GmbH",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    defaults.update(overrides)
    c = Customer(**defaults)
    db.add(c)
    db.flush()
    return c


def test_list_customers_returns_paginated_envelope(client: TestClient, db_session: Session) -> None:
    for _ in range(3):
        _make_customer(db_session)
    db_session.commit()

    response = client.get("/api/v1/customers")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 3
    assert len(body["data"]) >= 3


def test_list_customers_filters_by_country(client: TestClient, db_session: Session) -> None:
    _make_customer(db_session, country="DE")
    _make_customer(db_session, country="CN")
    db_session.commit()

    response = client.get("/api/v1/customers?country=CN")

    assert response.status_code == 200
    assert all(item["country"] == "CN" for item in response.json()["data"])


def test_get_customer_returns_record(client: TestClient, db_session: Session) -> None:
    customer = _make_customer(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/customers/{customer.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(customer.id)


def test_get_customer_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/customers/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["entity"] == "customer"


def test_create_customer_returns_201(client: TestClient, actor: str) -> None:
    payload = {
        "customer_number": "CUST-API-01",
        "company_name": "API Test Corp",
        "country": "US",
        "sales_area": "Americas",
        "language": "EN",
    }

    response = client.post(
        "/api/v1/customers",
        json=payload,
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 201
    assert response.json()["customer_number"] == "CUST-API-01"


def test_patch_customer_updates_fields(client: TestClient, db_session: Session, actor: str) -> None:
    customer = _make_customer(db_session, contact_email=None)
    db_session.commit()

    response = client.patch(
        f"/api/v1/customers/{customer.id}",
        json={"contact_email": "new@example.com"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 200
    assert response.json()["contact_email"] == "new@example.com"
