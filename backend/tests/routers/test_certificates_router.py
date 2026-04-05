from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.customer import Customer


def _make_customer(db: Session) -> Customer:
    c = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="Cert Test GmbH",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db.add(c)
    db.flush()
    return c


def _make_certificate(db: Session, customer_id, **overrides) -> Certificate:
    defaults = dict(
        certificate_number=f"TC-{uuid4().hex[:8]}",
        customer_id=customer_id,
        product_description="Test product",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    defaults.update(overrides)
    cert = Certificate(**defaults)
    db.add(cert)
    db.flush()
    return cert


def test_list_certificates_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    customer = _make_customer(db_session)
    for _ in range(3):
        _make_certificate(db_session, customer.id)
    db_session.commit()

    response = client.get("/api/v1/certificates")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 3


def test_list_certificates_filters_by_customer_and_status(
    client: TestClient, db_session: Session
) -> None:
    customer = _make_customer(db_session)
    _make_certificate(db_session, customer.id, status="active")
    _make_certificate(db_session, customer.id, status="expired")
    db_session.commit()

    response = client.get(
        f"/api/v1/certificates?customer_id={customer.id}&status=expired"
    )

    assert response.status_code == 200
    body = response.json()
    assert all(item["status"] == "expired" for item in body["data"])
    assert all(item["customer_id"] == str(customer.id) for item in body["data"])


def test_get_certificate_returns_record(client: TestClient, db_session: Session) -> None:
    customer = _make_customer(db_session)
    cert = _make_certificate(db_session, customer.id)
    db_session.commit()

    response = client.get(f"/api/v1/certificates/{cert.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(cert.id)


def test_get_certificate_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/certificates/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["entity"] == "certificate"


def test_create_certificate_returns_201(
    client: TestClient, db_session: Session, actor: str
) -> None:
    customer = _make_customer(db_session)
    db_session.commit()

    payload = {
        "certificate_number": "TC-API-01",
        "customer_id": str(customer.id),
        "product_description": "API test product",
        "status": "active",
        "issue_date": "2025-01-01",
        "expiry_date": "2028-01-01",
    }

    response = client.post(
        "/api/v1/certificates",
        json=payload,
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 201
    assert response.json()["certificate_number"] == "TC-API-01"


def test_patch_certificate_updates_status(
    client: TestClient, db_session: Session, actor: str
) -> None:
    customer = _make_customer(db_session)
    cert = _make_certificate(db_session, customer.id, status="active")
    db_session.commit()

    response = client.patch(
        f"/api/v1/certificates/{cert.id}",
        json={"status": "suspended"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "suspended"
