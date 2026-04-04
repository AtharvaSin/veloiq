## Part 5 — Services & Audit Enforcement (Tasks 20-23)

This part builds the mutation service layer. Every service function that creates or updates an entity MUST write an audit_log entry in the same transaction via the `write_audit_entry()` helper. This is the enforcement mechanism that makes the audit trail tamper-evident at the application level.

**Pattern for every mutation service:**

1. Validate business rules (and 404 if updating non-existent entity)
2. Build/mutate the entity
3. `db.add(entity)` then `db.flush()` to get the entity_id
4. Call `write_audit_entry()` in the same transaction with entity_id, action, actor, details
5. `db.commit()`
6. `db.refresh(entity)`
7. Return the entity

---

### Task 20: Audit enforcement helper

**Files:**
- Create: `backend/app/services/audit.py`
- Create: `backend/tests/services/test_audit.py`

- [ ] **Step 1: Write failing test for `write_audit_entry` helper**

Create `backend/tests/services/test_audit.py`:

```python
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.services.audit import write_audit_entry


def test_write_audit_entry_persists_row(db_session: Session) -> None:
    entity_id = uuid4()
    entry = write_audit_entry(
        db_session,
        entity_type="standard",
        entity_id=entity_id,
        action="created",
        actor="Dr. M. Weber",
        details={"ac_code": "ISO 9001:2015", "status": "60"},
        ip_address="192.168.1.100",
    )

    assert entry.id is not None
    assert entry.entity_type == "standard"
    assert entry.entity_id == entity_id
    assert entry.action == "created"
    assert entry.actor == "Dr. M. Weber"
    assert entry.details["ac_code"] == "ISO 9001:2015"
    assert entry.ip_address == "192.168.1.100"
    assert entry.created_at is not None


def test_write_audit_entry_defaults_ip_to_none(db_session: Session) -> None:
    entry = write_audit_entry(
        db_session,
        entity_type="customer",
        entity_id=uuid4(),
        action="updated",
        actor="system",
        details={"changed": ["company_name"]},
    )

    assert entry.ip_address is None


def test_write_audit_entry_flushes_but_does_not_commit(db_session: Session) -> None:
    entity_id = uuid4()
    write_audit_entry(
        db_session,
        entity_type="certificate",
        entity_id=entity_id,
        action="created",
        actor="seeder",
        details={},
    )

    # Row is visible within the same transaction (flushed)
    rows = db_session.query(AuditLog).filter_by(entity_id=entity_id).all()
    assert len(rows) == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/services/test_audit.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.audit'`

- [ ] **Step 3: Create `backend/app/services/audit.py`**

```python
"""Audit log enforcement helper.

Every mutation service MUST call `write_audit_entry()` inside the same
transaction as the entity it is auditing. The application user is
REVOKE'd from UPDATE/DELETE on the audit_log table — entries are
append-only once committed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit_entry(
    db: Session,
    *,
    entity_type: str,
    entity_id: UUID,
    action: str,
    actor: str,
    details: dict,
    ip_address: str | None = None,
) -> AuditLog:
    """Write an immutable audit log entry.

    MUST be called within the same transaction as the mutation it audits.
    The returned AuditLog has been flushed but not committed — the caller
    is responsible for committing the containing transaction.

    Args:
        db: Active SQLAlchemy session.
        entity_type: Resource name (e.g., "standard", "customer").
        entity_id: UUID of the entity being mutated.
        action: Verb describing the mutation (e.g., "created", "updated").
        actor: Identifier for the user/service performing the action.
        details: JSON-serializable dict capturing what changed.
        ip_address: Optional IPv4/IPv6 address of the request source.

    Returns:
        The persisted AuditLog instance (flushed, not committed).
    """
    entry = AuditLog(
        id=uuid4(),
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        details=details,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.flush()
    return entry
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/services/test_audit.py -v --no-cov
```

Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/audit.py backend/tests/services/test_audit.py
git commit -m "feat(services): add write_audit_entry enforcement helper"
```

---

### Task 21: Standards service (create/update with audit)

**Files:**
- Create: `backend/app/services/standards_service.py`
- Create: `backend/tests/services/test_standards_service.py`

- [ ] **Step 1: Write failing tests for the standards service**

Create `backend/tests/services/test_standards_service.py`:

```python
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.models.standard import Standard
from app.schemas.standard import StandardCreate, StandardUpdate
from app.services.standards_service import create_standard, update_standard


def test_create_standard_returns_entity(db_session: Session) -> None:
    payload = StandardCreate(
        ac_code="ISO 9001:2015",
        title="Quality management systems — Requirements",
        status="60",
        source_payload={"raw": "iso-9001-2015"},
    )
    standard = create_standard(db_session, payload, actor="Dr. M. Weber")

    assert standard.id is not None
    assert standard.ac_code == "ISO 9001:2015"
    assert standard.status == "60"
    assert standard.normalized_code == "iso 9001:2015"
    assert standard.base_number == "iso 9001:2015"
    assert standard.ingested_at is not None


def test_create_standard_writes_audit_entry(db_session: Session) -> None:
    payload = StandardCreate(
        ac_code="IEC 62368-1:2023",
        title="Audio/video, information and communication technology equipment",
        status="60",
        source_payload={"raw": "iec-62368-1"},
    )
    standard = create_standard(db_session, payload, actor="Dr. M. Weber")

    entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=standard.id
    ).all()

    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].actor == "Dr. M. Weber"
    assert entries[0].details["ac_code"] == "IEC 62368-1:2023"
    assert entries[0].details["status"] == "60"


def test_update_standard_modifies_entity_and_audits(db_session: Session) -> None:
    created = create_standard(
        db_session,
        StandardCreate(
            ac_code="ISO 14001:2015",
            title="Environmental management systems",
            status="60",
            source_payload={"raw": "iso-14001"},
        ),
        actor="seeder",
    )

    updated = update_standard(
        db_session,
        created.id,
        StandardUpdate(status="95", replaced_by="ISO 14001:2026"),
        actor="Dr. M. Weber",
    )

    assert updated.id == created.id
    assert updated.status == "95"
    assert updated.replaced_by == "ISO 14001:2026"
    assert updated.title == "Environmental management systems"  # unchanged

    entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=created.id
    ).order_by(AuditLog.created_at).all()

    assert len(entries) == 2
    assert entries[0].action == "created"
    assert entries[0].actor == "seeder"
    assert entries[1].action == "updated"
    assert entries[1].actor == "Dr. M. Weber"
    assert entries[1].details["changed_fields"] == {
        "status": {"old": "60", "new": "95"},
        "replaced_by": {"old": None, "new": "ISO 14001:2026"},
    }


def test_update_standard_raises_not_found_for_missing_id(db_session: Session) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        update_standard(
            db_session,
            uuid4(),
            StandardUpdate(status="95"),
            actor="Dr. M. Weber",
        )

    assert excinfo.value.entity == "standard"


def test_update_standard_with_empty_payload_is_noop_but_still_audits(db_session: Session) -> None:
    created = create_standard(
        db_session,
        StandardCreate(
            ac_code="ISO 45001:2018",
            title="OH&S management systems",
            status="60",
            source_payload={},
        ),
        actor="seeder",
    )
    updated = update_standard(
        db_session, created.id, StandardUpdate(), actor="Dr. M. Weber"
    )

    assert updated.status == "60"
    entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=created.id, action="updated"
    ).all()
    assert len(entries) == 1
    assert entries[0].details["changed_fields"] == {}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/services/test_standards_service.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.standards_service'`

- [ ] **Step 3: Create `backend/app/services/standards_service.py`**

```python
"""Standards mutation service. Every mutation writes an audit_log entry."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.standard import Standard
from app.schemas.standard import StandardCreate, StandardUpdate
from app.services.audit import write_audit_entry


def create_standard(
    db: Session,
    payload: StandardCreate,
    actor: str,
) -> Standard:
    """Create a Standard and write a paired audit_log entry."""
    now = datetime.now(timezone.utc)
    # Phase A placeholder normalization — Phase B replaces with real engine
    normalized = payload.ac_code.lower().strip()

    standard = Standard(
        id=uuid4(),
        ac_code=payload.ac_code,
        title=payload.title,
        status=payload.status,
        replaced_by=payload.replaced_by,
        committee=payload.committee,
        ics_code=payload.ics_code,
        normalized_code=normalized,
        base_number=normalized,
        source_payload=payload.source_payload,
        ingested_at=now,
    )
    db.add(standard)
    db.flush()

    write_audit_entry(
        db,
        entity_type="standard",
        entity_id=standard.id,
        action="created",
        actor=actor,
        details={
            "ac_code": standard.ac_code,
            "status": standard.status,
            "title": standard.title,
        },
    )

    db.commit()
    db.refresh(standard)
    return standard


def update_standard(
    db: Session,
    standard_id: UUID,
    payload: StandardUpdate,
    actor: str,
) -> Standard:
    """Update a Standard and write a paired audit_log entry capturing diffs."""
    standard = db.get(Standard, standard_id)
    if standard is None:
        raise NotFoundError(entity="standard", entity_id=standard_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(standard, field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
            setattr(standard, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="standard",
        entity_id=standard.id,
        action="updated",
        actor=actor,
        details={
            "ac_code": standard.ac_code,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(standard)
    return standard
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend
pytest tests/services/test_standards_service.py -v --no-cov
```

Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/standards_service.py backend/tests/services/test_standards_service.py
git commit -m "feat(services): add standards_service with create/update audit enforcement"
```

---

### Task 22: Customers service (create/update with audit)

**Files:**
- Create: `backend/app/services/customers_service.py`
- Create: `backend/tests/services/test_customers_service.py`

- [ ] **Step 1: Write failing tests for the customers service**

Create `backend/tests/services/test_customers_service.py`:

```python
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customers_service import create_customer, update_customer


def test_create_customer_returns_entity(db_session: Session) -> None:
    payload = CustomerCreate(
        customer_number="CUST-0042",
        company_name="Siemens AG",
        country="DE",
        sales_area="EMEA",
        language="DE",
        contact_name="Ingrid Müller",
        contact_email="ingrid.mueller@siemens.example.com",
    )
    customer = create_customer(db_session, payload, actor="sales-ops")

    assert customer.id is not None
    assert customer.customer_number == "CUST-0042"
    assert customer.country == "DE"
    assert customer.contact_email == "ingrid.mueller@siemens.example.com"


def test_create_customer_writes_audit_entry(db_session: Session) -> None:
    payload = CustomerCreate(
        customer_number="CUST-0099",
        company_name="Huawei Technologies",
        country="CN",
        sales_area="Greater China",
        language="ZH",
    )
    customer = create_customer(db_session, payload, actor="sales-ops")

    entries = db_session.query(AuditLog).filter_by(
        entity_type="customer", entity_id=customer.id
    ).all()

    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].actor == "sales-ops"
    assert entries[0].details["customer_number"] == "CUST-0099"
    assert entries[0].details["country"] == "CN"


def test_update_customer_modifies_entity_and_audits(db_session: Session) -> None:
    created = create_customer(
        db_session,
        CustomerCreate(
            customer_number="CUST-0500",
            company_name="Tata Steel",
            country="IN",
            sales_area="South Asia",
            language="EN",
        ),
        actor="seeder",
    )

    updated = update_customer(
        db_session,
        created.id,
        CustomerUpdate(
            contact_name="Priya Sharma",
            contact_email="priya.sharma@tatasteel.example.com",
        ),
        actor="sales-ops",
    )

    assert updated.id == created.id
    assert updated.contact_name == "Priya Sharma"
    assert updated.contact_email == "priya.sharma@tatasteel.example.com"
    assert updated.company_name == "Tata Steel"  # unchanged

    entries = db_session.query(AuditLog).filter_by(
        entity_type="customer", entity_id=created.id
    ).order_by(AuditLog.created_at).all()

    assert len(entries) == 2
    assert entries[0].action == "created"
    assert entries[1].action == "updated"
    assert entries[1].actor == "sales-ops"
    assert "contact_name" in entries[1].details["changed_fields"]
    assert entries[1].details["changed_fields"]["contact_name"]["new"] == "Priya Sharma"


def test_update_customer_raises_not_found_for_missing_id(db_session: Session) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        update_customer(
            db_session,
            uuid4(),
            CustomerUpdate(contact_name="Ghost"),
            actor="sales-ops",
        )

    assert excinfo.value.entity == "customer"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/services/test_customers_service.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.customers_service'`

- [ ] **Step 3: Create `backend/app/services/customers_service.py`**

```python
"""Customers mutation service. Every mutation writes an audit_log entry."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit import write_audit_entry


def create_customer(
    db: Session,
    payload: CustomerCreate,
    actor: str,
) -> Customer:
    """Create a Customer and write a paired audit_log entry."""
    customer = Customer(
        id=uuid4(),
        customer_number=payload.customer_number,
        company_name=payload.company_name,
        country=payload.country,
        sales_area=payload.sales_area,
        language=payload.language,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
    )
    db.add(customer)
    db.flush()

    write_audit_entry(
        db,
        entity_type="customer",
        entity_id=customer.id,
        action="created",
        actor=actor,
        details={
            "customer_number": customer.customer_number,
            "company_name": customer.company_name,
            "country": customer.country,
        },
    )

    db.commit()
    db.refresh(customer)
    return customer


def update_customer(
    db: Session,
    customer_id: UUID,
    payload: CustomerUpdate,
    actor: str,
) -> Customer:
    """Update a Customer and write a paired audit_log entry capturing diffs."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise NotFoundError(entity="customer", entity_id=customer_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(customer, field)
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
            setattr(customer, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="customer",
        entity_id=customer.id,
        action="updated",
        actor=actor,
        details={
            "customer_number": customer.customer_number,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(customer)
    return customer
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend
pytest tests/services/test_customers_service.py -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/customers_service.py backend/tests/services/test_customers_service.py
git commit -m "feat(services): add customers_service with create/update audit enforcement"
```

---

### Task 23: Certificates service (create/update with audit)

**Files:**
- Create: `backend/app/services/certificates_service.py`
- Create: `backend/tests/services/test_certificates_service.py`

- [ ] **Step 1: Write failing tests for the certificates service**

Create `backend/tests/services/test_certificates_service.py`:

```python
from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.models.customer import Customer
from app.schemas.certificate import CertificateCreate, CertificateUpdate
from app.services.certificates_service import create_certificate, update_certificate


def _make_customer(db_session: Session, number: str = "CUST-CERT-1") -> Customer:
    customer = Customer(
        customer_number=number,
        company_name="CertTestCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()
    return customer


def test_create_certificate_returns_entity(db_session: Session) -> None:
    customer = _make_customer(db_session)
    payload = CertificateCreate(
        certificate_number="TC-55100",
        customer_id=customer.id,
        product_description="Medical Imaging Device",
        status="active",
        issue_date=date(2025, 1, 15),
        expiry_date=date(2028, 1, 14),
    )
    cert = create_certificate(db_session, payload, actor="certifier-01")

    assert cert.id is not None
    assert cert.certificate_number == "TC-55100"
    assert cert.customer_id == customer.id
    assert cert.status == "active"


def test_create_certificate_writes_audit_entry(db_session: Session) -> None:
    customer = _make_customer(db_session, number="CUST-CERT-2")
    payload = CertificateCreate(
        certificate_number="TC-55200",
        customer_id=customer.id,
        product_description="Industrial Robot Arm",
        status="active",
        issue_date=date(2025, 3, 1),
        expiry_date=date(2028, 2, 28),
    )
    cert = create_certificate(db_session, payload, actor="certifier-01")

    entries = db_session.query(AuditLog).filter_by(
        entity_type="certificate", entity_id=cert.id
    ).all()

    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].actor == "certifier-01"
    assert entries[0].details["certificate_number"] == "TC-55200"
    assert entries[0].details["status"] == "active"
    assert entries[0].details["customer_id"] == str(customer.id)


def test_update_certificate_modifies_entity_and_audits(db_session: Session) -> None:
    customer = _make_customer(db_session, number="CUST-CERT-3")
    created = create_certificate(
        db_session,
        CertificateCreate(
            certificate_number="TC-55300",
            customer_id=customer.id,
            product_description="Lab Analyzer",
            status="active",
            issue_date=date(2024, 6, 1),
            expiry_date=date(2027, 5, 31),
        ),
        actor="seeder",
    )

    updated = update_certificate(
        db_session,
        created.id,
        CertificateUpdate(status="suspended"),
        actor="compliance-officer",
    )

    assert updated.id == created.id
    assert updated.status == "suspended"
    assert updated.product_description == "Lab Analyzer"  # unchanged

    entries = db_session.query(AuditLog).filter_by(
        entity_type="certificate", entity_id=created.id
    ).order_by(AuditLog.created_at).all()

    assert len(entries) == 2
    assert entries[0].action == "created"
    assert entries[1].action == "updated"
    assert entries[1].actor == "compliance-officer"
    assert entries[1].details["changed_fields"]["status"] == {
        "old": "active",
        "new": "suspended",
    }


def test_update_certificate_raises_not_found_for_missing_id(db_session: Session) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        update_certificate(
            db_session,
            uuid4(),
            CertificateUpdate(status="expired"),
            actor="compliance-officer",
        )

    assert excinfo.value.entity == "certificate"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/services/test_certificates_service.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.certificates_service'`

- [ ] **Step 3: Create `backend/app/services/certificates_service.py`**

```python
"""Certificates mutation service. Every mutation writes an audit_log entry."""
from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateUpdate
from app.services.audit import write_audit_entry


def _serialize(value: object) -> object:
    """Coerce non-JSON-native values (UUID, date) to strings for audit details."""
    if isinstance(value, date):
        return value.isoformat()
    if hasattr(value, "hex"):  # UUID
        return str(value)
    return value


def create_certificate(
    db: Session,
    payload: CertificateCreate,
    actor: str,
) -> Certificate:
    """Create a Certificate and write a paired audit_log entry."""
    cert = Certificate(
        id=uuid4(),
        certificate_number=payload.certificate_number,
        customer_id=payload.customer_id,
        product_description=payload.product_description,
        status=payload.status,
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
    )
    db.add(cert)
    db.flush()

    write_audit_entry(
        db,
        entity_type="certificate",
        entity_id=cert.id,
        action="created",
        actor=actor,
        details={
            "certificate_number": cert.certificate_number,
            "customer_id": str(cert.customer_id),
            "status": cert.status,
            "issue_date": cert.issue_date.isoformat(),
            "expiry_date": cert.expiry_date.isoformat(),
        },
    )

    db.commit()
    db.refresh(cert)
    return cert


def update_certificate(
    db: Session,
    certificate_id: UUID,
    payload: CertificateUpdate,
    actor: str,
) -> Certificate:
    """Update a Certificate and write a paired audit_log entry capturing diffs."""
    cert = db.get(Certificate, certificate_id)
    if cert is None:
        raise NotFoundError(entity="certificate", entity_id=certificate_id)

    changed_fields: dict[str, dict[str, object]] = {}
    updates = payload.model_dump(exclude_unset=True)
    for field, new_value in updates.items():
        old_value = getattr(cert, field)
        if old_value != new_value:
            changed_fields[field] = {
                "old": _serialize(old_value),
                "new": _serialize(new_value),
            }
            setattr(cert, field, new_value)

    db.flush()

    write_audit_entry(
        db,
        entity_type="certificate",
        entity_id=cert.id,
        action="updated",
        actor=actor,
        details={
            "certificate_number": cert.certificate_number,
            "changed_fields": changed_fields,
        },
    )

    db.commit()
    db.refresh(cert)
    return cert
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend
pytest tests/services/test_certificates_service.py -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/certificates_service.py backend/tests/services/test_certificates_service.py
git commit -m "feat(services): add certificates_service with create/update audit enforcement"
```

---

**End of Part 5 — Services & audit enforcement complete.**

**Part 5 verification:**

```bash
cd backend
pytest tests/services/ -v --no-cov
```

Expected: all service tests pass (3 audit + 5 standards + 4 customers + 4 certificates = 16 tests).

```bash
cd backend
pytest tests/ -v --no-cov
```

Expected: entire suite green — services integrate cleanly with models, schemas, and transactional rollback fixtures.

Every mutation path now provably writes an audit_log entry in the same transaction. The `audit_log` table is append-only at the database level (REVOKE UPDATE/DELETE applied in the initial Alembic migration) and is append-only at the application level (only `write_audit_entry()` writes to it, and it is called from every service mutation).

---
