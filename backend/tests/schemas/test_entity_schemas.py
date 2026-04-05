from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.standard import Standard
from app.schemas.cert_standard_link import (
    CertStandardLinkCreate,
    CertStandardLinkRead,
    CertStandardLinkUpdate,
)
from app.schemas.certificate import (
    CertificateCreate,
    CertificateRead,
    CertificateUpdate,
)
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.schemas.standard import StandardCreate, StandardRead, StandardUpdate

# ---------- Customer ----------

def test_customer_create_accepts_valid_payload() -> None:
    payload = CustomerCreate(
        customer_number="CUST-0001",
        company_name="Huawei Technologies Co., Ltd.",
        country="CN",
        sales_area="Greater China",
        language="ZH",
        contact_email="li.wei@huawei.example.com",
    )
    assert payload.customer_number == "CUST-0001"
    assert payload.contact_name is None


def test_customer_create_requires_customer_number() -> None:
    with pytest.raises(ValidationError):
        CustomerCreate(  # type: ignore[call-arg]
            company_name="Missing number",
            country="DE",
            sales_area="EMEA",
            language="DE",
        )


def test_customer_update_all_fields_optional() -> None:
    patch = CustomerUpdate(contact_email="new@example.com")
    assert patch.contact_email == "new@example.com"
    assert patch.company_name is None


def test_customer_read_from_orm_model(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-SCHEMA-1",
        company_name="Schema Test Co.",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    read = CustomerRead.model_validate(customer)
    assert read.id == customer.id
    assert read.customer_number == "CUST-SCHEMA-1"
    assert read.created_at is not None


# ---------- Standard ----------

def test_standard_create_requires_source_payload() -> None:
    with pytest.raises(ValidationError):
        StandardCreate(  # type: ignore[call-arg]
            ac_code="ISO 9001:2015",
            title="QMS",
            status="60",
        )


def test_standard_update_partial_patch() -> None:
    patch = StandardUpdate(status="95", replaced_by="ISO 9001:2025")
    assert patch.status == "95"
    assert patch.title is None


def test_standard_read_from_orm_model(db_session: Session) -> None:
    standard = Standard(
        ac_code="ISO 9001:2015",
        title="Quality management systems — Requirements",
        status="60",
        normalized_code="iso 9001:2015",
        base_number="9001",
        version_year=2015,
        source_payload={"raw": "test"},
        ingested_at=datetime.now(UTC),
    )
    db_session.add(standard)
    db_session.flush()

    read = StandardRead.model_validate(standard)
    assert read.ac_code == "ISO 9001:2015"
    assert read.normalized_code == "iso 9001:2015"
    assert read.version_year == 2015
    assert read.ingested_at is not None


# ---------- Certificate ----------

def test_certificate_create_accepts_valid_payload() -> None:
    payload = CertificateCreate(
        certificate_number="TC-44210",
        customer_id="00000000-0000-0000-0000-000000000001",
        product_description="Industrial Control Panel",
        status="active",
        issue_date=date(2024, 3, 15),
        expiry_date=date(2027, 3, 14),
    )
    assert payload.status == "active"


def test_certificate_update_allows_status_change() -> None:
    patch = CertificateUpdate(status="expired")
    assert patch.status == "expired"


def test_certificate_read_from_orm_model(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-CERT-1",
        company_name="CertCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-READ-1",
        customer_id=customer.id,
        product_description="Test product",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    db_session.add(cert)
    db_session.flush()

    read = CertificateRead.model_validate(cert)
    assert read.certificate_number == "TC-READ-1"
    assert read.customer_id == customer.id
    assert read.status == "active"


# ---------- CertStandardLink ----------

def test_cert_standard_link_create_and_read(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-LNK-1",
        company_name="LinkCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-LNK-1",
        customer_id=customer.id,
        product_description="T",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    db_session.add(cert)
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 14001:2015-11",
        normalized_ref="14001:2015",
        base_number="14001",
        linked_at=datetime.now(UTC),
    )
    db_session.add(link)
    db_session.flush()

    read = CertStandardLinkRead.model_validate(link)
    assert read.standard_ref == "DIN EN ISO 14001:2015-11"
    assert read.base_number == "14001"


def test_cert_standard_link_create_requires_certificate_id() -> None:
    with pytest.raises(ValidationError):
        CertStandardLinkCreate(  # type: ignore[call-arg]
            standard_ref="ISO 9001:2015",
            normalized_ref="9001:2015",
            base_number="9001",
        )


def test_cert_standard_link_update_accepts_normalized_fields() -> None:
    patch = CertStandardLinkUpdate(normalized_ref="updated:ref", base_number="0000")
    assert patch.normalized_ref == "updated:ref"
    assert patch.base_number == "0000"
