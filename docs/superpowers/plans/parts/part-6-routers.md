## Part 6 — API Routers (Tasks 24-29)

Goal: Build the FastAPI routers that expose the 8 REST resources under `/api/v1/`. Thin handlers delegate mutations to services (which write audit entries) and perform direct SQLAlchemy queries for read-only resources. All list endpoints support pagination (`page`, `limit`, `sort`, `order`) and per-resource filtering. No DELETE anywhere.

**Router responsibility boundary:**
- Mutation handlers: parse payload, extract actor from `X-User-Id` header, delegate to service, return serialized model.
- List handlers: build SQLAlchemy query, apply filters + sort + pagination, return `PaginatedResponse` envelope.
- Detail handlers: query by UUID, raise `NotFoundError` if missing, return serialized model.
- 404s come from raising `NotFoundError` (mapped to HTTP 404 by exception handlers registered in Part 7).

**Pre-requisites assumed from Part 4 (schemas) and Part 5 (services):**
- `backend/app/schemas/common.py` exports `Pagination` and `PaginatedResponse[T]` (generic envelope).
- `backend/app/schemas/{standard,customer,certificate,match_result,assessment,notification,sales_escalation,audit_log}.py` each export `{Entity}Create`, `{Entity}Read`, `{Entity}Update` as applicable.
- `backend/app/services/{standards,customers,certificates,escalations}_service.py` each expose `create_*`, `update_*` functions with `(db, payload, actor)` signatures that write audit entries in the same transaction.

**Client fixture note:** Router tests depend on a `client: TestClient` fixture that overrides `get_db` with the test session. This fixture is added to `tests/conftest.py` in Part 7 (App Integration). For Part 6, write the test files assuming the fixture exists — they will run green as soon as Part 7 lands. In each task we **verify the router module imports cleanly** (`python -c "from app.routers.xxx import router"`) as the concrete green-bar signal for this part. Full end-to-end TestClient assertions run in Part 7's verification.

---

### Task 24: Standards router with full CRUD

**Files:**
- Create: `backend/app/dependencies.py` (if not created in Part 5)
- Create: `backend/app/routers/standards.py`
- Create: `backend/tests/routers/test_standards_router.py`

- [ ] **Step 1: Create `backend/app/dependencies.py` (skip if already exists)**

Check first:

```bash
cd backend
ls app/dependencies.py 2>/dev/null && echo "EXISTS - skip" || echo "MISSING - create"
```

If missing, create `backend/app/dependencies.py`:

```python
from fastapi import Header


def get_current_actor(x_user_id: str | None = Header(default="anonymous")) -> str:
    """Extract the acting user's identity from the X-User-Id header.

    Phase A mock auth. Production replaces this with real OAuth/JWT-derived identity.
    Returns 'anonymous' when the header is missing or empty.
    """
    return x_user_id or "anonymous"
```

- [ ] **Step 2: Write failing router test**

Create `backend/tests/routers/test_standards_router.py`:

```python
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.standard import Standard


def _make_standard(db: Session, **overrides) -> Standard:
    defaults = dict(
        ac_code=f"ISO {uuid4().hex[:6]}:2015",
        title="Quality management systems",
        status="60",
        normalized_code="iso 9001:2015",
        base_number="9001",
        source_payload={},
        ingested_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    std = Standard(**defaults)
    db.add(std)
    db.flush()
    return std


def test_list_standards_returns_paginated_envelope(client: TestClient, db_session: Session) -> None:
    for _ in range(3):
        _make_standard(db_session)
    db_session.commit()

    response = client.get("/api/v1/standards")

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["limit"] == 50
    assert body["pagination"]["total"] >= 3
    assert len(body["data"]) >= 3


def test_list_standards_filters_by_status(client: TestClient, db_session: Session) -> None:
    _make_standard(db_session, status="60")
    _make_standard(db_session, status="90")
    db_session.commit()

    response = client.get("/api/v1/standards?status=90")

    assert response.status_code == 200
    body = response.json()
    assert all(item["status"] == "90" for item in body["data"])


def test_get_standard_by_id_returns_record(client: TestClient, db_session: Session) -> None:
    std = _make_standard(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/standards/{std.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(std.id)


def test_get_standard_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/standards/{uuid4()}")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NOT_FOUND"
    assert body["entity"] == "standard"


def test_create_standard_returns_201(client: TestClient, actor: str) -> None:
    payload = {
        "ac_code": "ISO 14001:2015",
        "title": "Environmental management systems",
        "status": "60",
        "source_payload": {"raw": "test"},
    }

    response = client.post(
        "/api/v1/standards",
        json=payload,
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["ac_code"] == "ISO 14001:2015"
    assert data["status"] == "60"
    assert "id" in data


def test_patch_standard_updates_fields(client: TestClient, db_session: Session, actor: str) -> None:
    std = _make_standard(db_session, status="60")
    db_session.commit()

    response = client.patch(
        f"/api/v1/standards/{std.id}",
        json={"status": "95"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "95"


def test_patch_standard_nonexistent_returns_404(client: TestClient, actor: str) -> None:
    response = client.patch(
        f"/api/v1/standards/{uuid4()}",
        json={"status": "95"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 404
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd backend
pytest tests/routers/test_standards_router.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.routers.standards'` (or import errors for `client` fixture — that's OK, it comes from Part 7).

- [ ] **Step 4: Create `backend/app/routers/standards.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.standard import Standard
from app.schemas.common import PaginatedResponse, Pagination
from app.schemas.standard import StandardCreate, StandardRead, StandardUpdate
from app.services import standards_service

router = APIRouter(prefix="/standards", tags=["standards"])

ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "ac_code", "status", "base_number"}


@router.get("", response_model=PaginatedResponse[StandardRead])
def list_standards(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    committee: str | None = Query(None),
    base_number: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[StandardRead]:
    query = db.query(Standard)

    if status is not None:
        query = query.filter(Standard.status == status)
    if committee is not None:
        query = query.filter(Standard.committee == committee)
    if base_number is not None:
        query = query.filter(Standard.base_number == base_number)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(Standard, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[StandardRead](
        data=[StandardRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{standard_id}", response_model=StandardRead)
def get_standard(standard_id: UUID, db: Session = Depends(get_db)) -> StandardRead:
    standard = db.query(Standard).filter(Standard.id == standard_id).first()
    if standard is None:
        raise NotFoundError(entity="standard", entity_id=standard_id)
    return StandardRead.model_validate(standard)


@router.post("", response_model=StandardRead, status_code=201)
def create_standard(
    payload: StandardCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> StandardRead:
    standard = standards_service.create_standard(db, payload, actor)
    return StandardRead.model_validate(standard)


@router.patch("/{standard_id}", response_model=StandardRead)
def update_standard(
    standard_id: UUID,
    payload: StandardUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> StandardRead:
    standard = standards_service.update_standard(db, standard_id, payload, actor)
    return StandardRead.model_validate(standard)
```

- [ ] **Step 5: Verify router module imports cleanly**

```bash
cd backend
python -c "from app.routers.standards import router; print('routes:', [r.path for r in router.routes])"
```

Expected output:
```
routes: ['/standards', '/standards/{standard_id}', '/standards', '/standards/{standard_id}']
```

- [ ] **Step 6: Run router tests (will be skipped/errored until Part 7 adds client fixture)**

```bash
pytest tests/routers/test_standards_router.py -v --no-cov
```

Expected: tests error with "fixture 'client' not found" — this is expected; Part 7 provides it. The router module must still import cleanly.

- [ ] **Step 7: Commit**

```bash
git add backend/app/dependencies.py backend/app/routers/standards.py backend/tests/routers/test_standards_router.py
git commit -m "feat(routers): add standards router with full CRUD and pagination"
```

---

### Task 25: Customers router with full CRUD

**Files:**
- Create: `backend/app/routers/customers.py`
- Create: `backend/tests/routers/test_customers_router.py`

- [ ] **Step 1: Write failing router test**

Create `backend/tests/routers/test_customers_router.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/routers/test_customers_router.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.routers.customers'`.

- [ ] **Step 3: Create `backend/app/routers/customers.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.customer import Customer
from app.schemas.common import PaginatedResponse, Pagination
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import customers_service

router = APIRouter(prefix="/customers", tags=["customers"])

ALLOWED_SORT_FIELDS = {"created_at", "company_name", "customer_number", "country"}


@router.get("", response_model=PaginatedResponse[CustomerRead])
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    country: str | None = Query(None),
    sales_area: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CustomerRead]:
    query = db.query(Customer)

    if country is not None:
        query = query.filter(Customer.country == country)
    if sales_area is not None:
        query = query.filter(Customer.sales_area == sales_area)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(Customer, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[CustomerRead](
        data=[CustomerRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)) -> CustomerRead:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise NotFoundError(entity="customer", entity_id=customer_id)
    return CustomerRead.model_validate(customer)


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CustomerRead:
    customer = customers_service.create_customer(db, payload, actor)
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CustomerRead:
    customer = customers_service.update_customer(db, customer_id, payload, actor)
    return CustomerRead.model_validate(customer)
```

- [ ] **Step 4: Verify router module imports cleanly**

```bash
python -c "from app.routers.customers import router; print('routes:', [r.path for r in router.routes])"
```

Expected: 4 paths listed (list, detail, create, update).

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/customers.py backend/tests/routers/test_customers_router.py
git commit -m "feat(routers): add customers router with full CRUD and country filter"
```

---

### Task 26: Certificates router with full CRUD

**Files:**
- Create: `backend/app/routers/certificates.py`
- Create: `backend/tests/routers/test_certificates_router.py`

- [ ] **Step 1: Write failing router test**

Create `backend/tests/routers/test_certificates_router.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/routers/test_certificates_router.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.routers.certificates'`.

- [ ] **Step 3: Create `backend/app/routers/certificates.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateRead, CertificateUpdate
from app.schemas.common import PaginatedResponse, Pagination
from app.services import certificates_service

router = APIRouter(prefix="/certificates", tags=["certificates"])

ALLOWED_SORT_FIELDS = {
    "created_at",
    "updated_at",
    "certificate_number",
    "status",
    "expiry_date",
    "issue_date",
}


@router.get("", response_model=PaginatedResponse[CertificateRead])
def list_certificates(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    customer_id: UUID | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CertificateRead]:
    query = db.query(Certificate)

    if customer_id is not None:
        query = query.filter(Certificate.customer_id == customer_id)
    if status is not None:
        query = query.filter(Certificate.status == status)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(Certificate, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[CertificateRead](
        data=[CertificateRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{certificate_id}", response_model=CertificateRead)
def get_certificate(certificate_id: UUID, db: Session = Depends(get_db)) -> CertificateRead:
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if cert is None:
        raise NotFoundError(entity="certificate", entity_id=certificate_id)
    return CertificateRead.model_validate(cert)


@router.post("", response_model=CertificateRead, status_code=201)
def create_certificate(
    payload: CertificateCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CertificateRead:
    cert = certificates_service.create_certificate(db, payload, actor)
    return CertificateRead.model_validate(cert)


@router.patch("/{certificate_id}", response_model=CertificateRead)
def update_certificate(
    certificate_id: UUID,
    payload: CertificateUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CertificateRead:
    cert = certificates_service.update_certificate(db, certificate_id, payload, actor)
    return CertificateRead.model_validate(cert)
```

- [ ] **Step 4: Verify router module imports cleanly**

```bash
python -c "from app.routers.certificates import router; print('routes:', [r.path for r in router.routes])"
```

Expected: 4 paths listed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/certificates.py backend/tests/routers/test_certificates_router.py
git commit -m "feat(routers): add certificates router with full CRUD and customer/status filters"
```

---

### Task 27: Read-only routers (matches, notifications, audit)

**Files:**
- Create: `backend/app/routers/matches.py`
- Create: `backend/app/routers/notifications.py`
- Create: `backend/app/routers/audit.py`
- Create: `backend/tests/routers/test_readonly_routers.py`

Three routers share the same read-only pattern: list + detail, no POST/PATCH/DELETE. System-generated data populated by later phases (matches = Phase B, notifications = Phase D, audit = service layer from Part 5).

- [ ] **Step 1: Write failing test for all three read-only routers**

Create `backend/tests/routers/test_readonly_routers.py`:

```python
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.standard import Standard


def _build_full_chain(db: Session) -> dict:
    """Helper: create one full row-chain across all entities."""
    customer = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="RO Test", country="DE",
        sales_area="EMEA", language="DE",
    )
    db.add(customer)
    db.flush()

    standard = Standard(
        ac_code=f"ISO {uuid4().hex[:4]}:2015", title="QMS", status="60",
        normalized_code="iso 9001:2015", base_number="9001",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    cert = Certificate(
        certificate_number=f"TC-{uuid4().hex[:8]}",
        customer_id=customer.id, product_description="Test",
        status="active", issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db.add_all([standard, cert])
    db.flush()

    link = CertStandardLink(
        certificate_id=cert.id, standard_ref="DIN EN ISO 9001:2015",
        normalized_ref="9001:2015", base_number="9001",
        linked_at=datetime.now(timezone.utc),
    )
    db.add(link)
    db.flush()

    match = MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.95"), confidence_tier="auto_match",
        status="reviewed", matched_at=datetime.now(timezone.utc),
    )
    db.add(match)
    db.flush()

    assessment = Assessment(
        match_result_id=match.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Administrative amendment", decision="approved",
        decided_at=datetime.now(timezone.utc), signature_hash="abc123",
    )
    db.add(assessment)
    db.flush()

    notif = Notification(
        assessment_id=assessment.id, customer_id=customer.id,
        template_language="DE", subject="Update", body_html="<p/>",
        status="delivered",
        sla_deadline=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(notif)
    db.flush()

    audit = AuditLog(
        entity_type="standard", entity_id=standard.id,
        action="created", actor="Dr. M. Weber",
        details={"ac_code": standard.ac_code},
    )
    db.add(audit)
    db.flush()

    return {
        "customer": customer, "standard": standard, "cert": cert, "link": link,
        "match": match, "assessment": assessment, "notif": notif, "audit": audit,
    }


def test_list_matches_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/matches")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 1
    assert len(body["data"]) >= 1


def test_list_matches_filters_by_confidence_tier(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/matches?confidence_tier=auto_match")

    assert response.status_code == 200
    assert all(
        item["confidence_tier"] == "auto_match" for item in response.json()["data"]
    )


def test_get_match_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/matches/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["entity"] == "match_result"


def test_list_notifications_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/notifications")

    assert response.status_code == 200
    assert response.json()["pagination"]["total"] >= 1


def test_list_notifications_filters_by_status(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/notifications?status=delivered")

    assert response.status_code == 200
    assert all(item["status"] == "delivered" for item in response.json()["data"])


def test_get_notification_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/notifications/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["entity"] == "notification"


def test_list_audit_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get("/api/v1/audit")

    assert response.status_code == 200
    assert response.json()["pagination"]["total"] >= 1


def test_list_audit_filters_by_entity_type_and_actor(
    client: TestClient, db_session: Session
) -> None:
    _build_full_chain(db_session)
    db_session.commit()

    response = client.get(
        "/api/v1/audit?entity_type=standard&actor=Dr.%20M.%20Weber"
    )

    assert response.status_code == 200
    body = response.json()
    assert all(item["entity_type"] == "standard" for item in body["data"])
    assert all(item["actor"] == "Dr. M. Weber" for item in body["data"])


def test_get_audit_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/audit/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["entity"] == "audit_log"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/routers/test_readonly_routers.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.routers.matches'` (or the first missing module).

- [ ] **Step 3: Create `backend/app/routers/matches.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.match_result import MatchResult
from app.schemas.common import PaginatedResponse, Pagination
from app.schemas.match_result import MatchResultRead

router = APIRouter(prefix="/matches", tags=["matches"])

ALLOWED_SORT_FIELDS = {"matched_at", "similarity_score", "confidence_tier", "status"}


@router.get("", response_model=PaginatedResponse[MatchResultRead])
def list_matches(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("matched_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    confidence_tier: str | None = Query(None),
    status: str | None = Query(None),
    natos_standard_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[MatchResultRead]:
    query = db.query(MatchResult)

    if confidence_tier is not None:
        query = query.filter(MatchResult.confidence_tier == confidence_tier)
    if status is not None:
        query = query.filter(MatchResult.status == status)
    if natos_standard_id is not None:
        query = query.filter(MatchResult.natos_standard_id == natos_standard_id)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "matched_at"
    sort_column = getattr(MatchResult, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[MatchResultRead](
        data=[MatchResultRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{match_id}", response_model=MatchResultRead)
def get_match(match_id: UUID, db: Session = Depends(get_db)) -> MatchResultRead:
    match = db.query(MatchResult).filter(MatchResult.id == match_id).first()
    if match is None:
        raise NotFoundError(entity="match_result", entity_id=match_id)
    return MatchResultRead.model_validate(match)
```

- [ ] **Step 4: Create `backend/app/routers/notifications.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.notification import Notification
from app.schemas.common import PaginatedResponse, Pagination
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])

ALLOWED_SORT_FIELDS = {"sla_deadline", "sent_at", "status"}


@router.get("", response_model=PaginatedResponse[NotificationRead])
def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("sla_deadline"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    customer_id: UUID | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[NotificationRead]:
    query = db.query(Notification)

    if customer_id is not None:
        query = query.filter(Notification.customer_id == customer_id)
    if status is not None:
        query = query.filter(Notification.status == status)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "sla_deadline"
    sort_column = getattr(Notification, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[NotificationRead](
        data=[NotificationRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification(
    notification_id: UUID, db: Session = Depends(get_db)
) -> NotificationRead:
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif is None:
        raise NotFoundError(entity="notification", entity_id=notification_id)
    return NotificationRead.model_validate(notif)
```

- [ ] **Step 5: Create `backend/app/routers/audit.py`**

```python
from datetime import datetime
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import PaginatedResponse, Pagination

router = APIRouter(prefix="/audit", tags=["audit"])

ALLOWED_SORT_FIELDS = {"created_at", "entity_type", "actor", "action"}


@router.get("", response_model=PaginatedResponse[AuditLogRead])
def list_audit(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    entity_type: str | None = Query(None),
    entity_id: UUID | None = Query(None),
    actor: str | None = Query(None),
    action: str | None = Query(None),
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AuditLogRead]:
    query = db.query(AuditLog)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if actor is not None:
        query = query.filter(AuditLog.actor == actor)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if from_ is not None:
        query = query.filter(AuditLog.created_at >= from_)
    if to is not None:
        query = query.filter(AuditLog.created_at <= to)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(AuditLog, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[AuditLogRead](
        data=[AuditLogRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{audit_id}", response_model=AuditLogRead)
def get_audit_entry(audit_id: UUID, db: Session = Depends(get_db)) -> AuditLogRead:
    entry = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    if entry is None:
        raise NotFoundError(entity="audit_log", entity_id=audit_id)
    return AuditLogRead.model_validate(entry)
```

- [ ] **Step 6: Verify all three modules import cleanly**

```bash
python -c "from app.routers.matches import router as m; from app.routers.notifications import router as n; from app.routers.audit import router as a; print('matches:', len(m.routes), 'notifications:', len(n.routes), 'audit:', len(a.routes))"
```

Expected output:
```
matches: 2 notifications: 2 audit: 2
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers/matches.py backend/app/routers/notifications.py backend/app/routers/audit.py backend/tests/routers/test_readonly_routers.py
git commit -m "feat(routers): add read-only matches, notifications, and audit routers"
```

---

### Task 28: Assessments router (read-only for Phase A)

**Files:**
- Create: `backend/app/routers/assessments.py`
- Create: `backend/tests/routers/test_assessments_router.py`

POST comes in Phase C (TCC decision workflow). Phase A exposes list + detail only.

- [ ] **Step 1: Write failing router test**

Create `backend/tests/routers/test_assessments_router.py`:

```python
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.standard import Standard


def _build_assessment(db: Session, **overrides) -> Assessment:
    customer = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="AS Test", country="DE",
        sales_area="EMEA", language="DE",
    )
    db.add(customer)
    db.flush()

    standard = Standard(
        ac_code=f"ISO {uuid4().hex[:4]}:2015", title="QMS", status="60",
        normalized_code="iso 9001:2015", base_number="9001",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    cert = Certificate(
        certificate_number=f"TC-{uuid4().hex[:8]}",
        customer_id=customer.id, product_description="Test",
        status="active", issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db.add_all([standard, cert])
    db.flush()

    link = CertStandardLink(
        certificate_id=cert.id, standard_ref="raw", normalized_ref="norm",
        base_number="9001", linked_at=datetime.now(timezone.utc),
    )
    db.add(link)
    db.flush()

    match = MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.95"), confidence_tier="auto_match",
        status="reviewed", matched_at=datetime.now(timezone.utc),
    )
    db.add(match)
    db.flush()

    defaults = dict(
        match_result_id=match.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Admin amendment", decision="approved",
        decided_at=datetime.now(timezone.utc), signature_hash="hash-xyz",
    )
    defaults.update(overrides)
    a = Assessment(**defaults)
    db.add(a)
    db.flush()
    return a


def test_list_assessments_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_assessment(db_session)
    _build_assessment(db_session)
    db_session.commit()

    response = client.get("/api/v1/assessments")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 2


def test_list_assessments_filters_by_assessor_id(
    client: TestClient, db_session: Session
) -> None:
    _build_assessment(db_session, assessor_id="Dr. M. Weber")
    _build_assessment(db_session, assessor_id="A. Schmidt")
    db_session.commit()

    response = client.get("/api/v1/assessments?assessor_id=A.%20Schmidt")

    assert response.status_code == 200
    assert all(
        item["assessor_id"] == "A. Schmidt" for item in response.json()["data"]
    )


def test_list_assessments_filters_by_decision(
    client: TestClient, db_session: Session
) -> None:
    _build_assessment(db_session, decision="approved")
    _build_assessment(db_session, decision="rejected")
    db_session.commit()

    response = client.get("/api/v1/assessments?decision=rejected")

    assert response.status_code == 200
    assert all(item["decision"] == "rejected" for item in response.json()["data"])


def test_get_assessment_returns_record(client: TestClient, db_session: Session) -> None:
    a = _build_assessment(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/assessments/{a.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(a.id)


def test_get_assessment_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/assessments/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["entity"] == "assessment"


def test_post_assessments_returns_405(client: TestClient, actor: str) -> None:
    # Phase A: POST not supported yet (Phase C feature).
    response = client.post(
        "/api/v1/assessments",
        json={},
        headers={"X-User-Id": actor},
    )
    assert response.status_code == 405
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/routers/test_assessments_router.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.routers.assessments'`.

- [ ] **Step 3: Create `backend/app/routers/assessments.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentRead
from app.schemas.common import PaginatedResponse, Pagination

router = APIRouter(prefix="/assessments", tags=["assessments"])

ALLOWED_SORT_FIELDS = {"decided_at", "assessor_id", "decision", "impact_classification"}


@router.get("", response_model=PaginatedResponse[AssessmentRead])
def list_assessments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("decided_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    assessor_id: str | None = Query(None),
    decision: str | None = Query(None),
    impact_classification: str | None = Query(None),
    match_result_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AssessmentRead]:
    query = db.query(Assessment)

    if assessor_id is not None:
        query = query.filter(Assessment.assessor_id == assessor_id)
    if decision is not None:
        query = query.filter(Assessment.decision == decision)
    if impact_classification is not None:
        query = query.filter(Assessment.impact_classification == impact_classification)
    if match_result_id is not None:
        query = query.filter(Assessment.match_result_id == match_result_id)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "decided_at"
    sort_column = getattr(Assessment, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[AssessmentRead](
        data=[AssessmentRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{assessment_id}", response_model=AssessmentRead)
def get_assessment(assessment_id: UUID, db: Session = Depends(get_db)) -> AssessmentRead:
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if a is None:
        raise NotFoundError(entity="assessment", entity_id=assessment_id)
    return AssessmentRead.model_validate(a)
```

- [ ] **Step 4: Verify router imports cleanly**

```bash
python -c "from app.routers.assessments import router; print('routes:', [r.path for r in router.routes])"
```

Expected: 2 paths (`/assessments`, `/assessments/{assessment_id}`).

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/assessments.py backend/tests/routers/test_assessments_router.py
git commit -m "feat(routers): add assessments read-only router (POST comes in Phase C)"
```

---

### Task 29: Escalations router (list + detail + PATCH)

**Files:**
- Create: `backend/app/routers/escalations.py`
- Create: `backend/tests/routers/test_escalations_router.py`

PATCH restricted to `status` and `assigned_to` fields only — use `SalesEscalationUpdate` schema from Part 4 which should only expose those fields.

- [ ] **Step 1: Write failing router test**

Create `backend/tests/routers/test_escalations_router.py`:

```python
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard


def _build_escalation(db: Session, **overrides) -> SalesEscalation:
    customer = Customer(
        customer_number=f"CUST-{uuid4().hex[:8]}",
        company_name="Esc Test", country="DE",
        sales_area="EMEA", language="DE",
    )
    db.add(customer)
    db.flush()

    standard = Standard(
        ac_code=f"ISO {uuid4().hex[:4]}:2015", title="QMS", status="60",
        normalized_code="iso 9001:2015", base_number="9001",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    cert = Certificate(
        certificate_number=f"TC-{uuid4().hex[:8]}",
        customer_id=customer.id, product_description="Test",
        status="active", issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db.add_all([standard, cert])
    db.flush()

    link = CertStandardLink(
        certificate_id=cert.id, standard_ref="raw", normalized_ref="norm",
        base_number="9001", linked_at=datetime.now(timezone.utc),
    )
    db.add(link)
    db.flush()

    match = MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.95"), confidence_tier="auto_match",
        status="reviewed", matched_at=datetime.now(timezone.utc),
    )
    db.add(match)
    db.flush()

    assessment = Assessment(
        match_result_id=match.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Admin", decision="approved",
        decided_at=datetime.now(timezone.utc), signature_hash="hash",
    )
    db.add(assessment)
    db.flush()

    notif = Notification(
        assessment_id=assessment.id, customer_id=customer.id,
        template_language="DE", subject="S", body_html="<p/>",
        status="breached",
        sla_deadline=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db.add(notif)
    db.flush()

    defaults = dict(
        notification_id=notif.id, customer_id=customer.id,
        escalation_reason="sla_breached",
        opportunity_value=Decimal("50000.00"), assigned_to=None,
        status="open", created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    esc = SalesEscalation(**defaults)
    db.add(esc)
    db.flush()
    return esc


def test_list_escalations_returns_paginated_envelope(
    client: TestClient, db_session: Session
) -> None:
    _build_escalation(db_session)
    _build_escalation(db_session)
    db_session.commit()

    response = client.get("/api/v1/escalations")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] >= 2


def test_list_escalations_filters_by_status(
    client: TestClient, db_session: Session
) -> None:
    _build_escalation(db_session, status="open")
    _build_escalation(db_session, status="resolved")
    db_session.commit()

    response = client.get("/api/v1/escalations?status=resolved")

    assert response.status_code == 200
    assert all(item["status"] == "resolved" for item in response.json()["data"])


def test_get_escalation_returns_record(client: TestClient, db_session: Session) -> None:
    esc = _build_escalation(db_session)
    db_session.commit()

    response = client.get(f"/api/v1/escalations/{esc.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(esc.id)


def test_get_escalation_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/escalations/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["entity"] == "sales_escalation"


def test_patch_escalation_updates_status(
    client: TestClient, db_session: Session, actor: str
) -> None:
    esc = _build_escalation(db_session, status="open")
    db_session.commit()

    response = client.patch(
        f"/api/v1/escalations/{esc.id}",
        json={"status": "contacted", "assigned_to": "sales-rep-7"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "contacted"
    assert body["assigned_to"] == "sales-rep-7"


def test_patch_escalation_nonexistent_returns_404(
    client: TestClient, actor: str
) -> None:
    response = client.patch(
        f"/api/v1/escalations/{uuid4()}",
        json={"status": "resolved"},
        headers={"X-User-Id": actor},
    )

    assert response.status_code == 404


def test_post_escalations_returns_405(client: TestClient, actor: str) -> None:
    # No POST endpoint exists.
    response = client.post(
        "/api/v1/escalations",
        json={},
        headers={"X-User-Id": actor},
    )
    assert response.status_code == 405
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/routers/test_escalations_router.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.routers.escalations'`.

- [ ] **Step 3: Create `backend/app/routers/escalations.py`**

```python
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.sales_escalation import SalesEscalation
from app.schemas.common import PaginatedResponse, Pagination
from app.schemas.sales_escalation import SalesEscalationRead, SalesEscalationUpdate
from app.services import escalations_service

router = APIRouter(prefix="/escalations", tags=["escalations"])

ALLOWED_SORT_FIELDS = {"created_at", "status", "opportunity_value", "resolved_at"}


@router.get("", response_model=PaginatedResponse[SalesEscalationRead])
def list_escalations(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    customer_id: UUID | None = Query(None),
    assigned_to: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[SalesEscalationRead]:
    query = db.query(SalesEscalation)

    if status is not None:
        query = query.filter(SalesEscalation.status == status)
    if customer_id is not None:
        query = query.filter(SalesEscalation.customer_id == customer_id)
    if assigned_to is not None:
        query = query.filter(SalesEscalation.assigned_to == assigned_to)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(SalesEscalation, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[SalesEscalationRead](
        data=[SalesEscalationRead.model_validate(item) for item in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{escalation_id}", response_model=SalesEscalationRead)
def get_escalation(
    escalation_id: UUID, db: Session = Depends(get_db)
) -> SalesEscalationRead:
    esc = (
        db.query(SalesEscalation)
        .filter(SalesEscalation.id == escalation_id)
        .first()
    )
    if esc is None:
        raise NotFoundError(entity="sales_escalation", entity_id=escalation_id)
    return SalesEscalationRead.model_validate(esc)


@router.patch("/{escalation_id}", response_model=SalesEscalationRead)
def update_escalation(
    escalation_id: UUID,
    payload: SalesEscalationUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> SalesEscalationRead:
    esc = escalations_service.update_escalation(db, escalation_id, payload, actor)
    return SalesEscalationRead.model_validate(esc)
```

- [ ] **Step 4: Verify router imports cleanly**

```bash
python -c "from app.routers.escalations import router; print('routes:', [r.path for r in router.routes])"
```

Expected: 3 paths (list, detail, update).

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/escalations.py backend/tests/routers/test_escalations_router.py
git commit -m "feat(routers): add escalations router with PATCH limited to status+assigned_to"
```

---

**End of Part 6 — API routers complete.**

**Part 6 verification:**

Run from `backend/`:

```bash
python -c "
from app.routers.standards import router as r_std
from app.routers.customers import router as r_cust
from app.routers.certificates import router as r_cert
from app.routers.matches import router as r_match
from app.routers.assessments import router as r_asmt
from app.routers.notifications import router as r_notif
from app.routers.escalations import router as r_esc
from app.routers.audit import router as r_audit
print('standards:', len(r_std.routes), 'expected 4')
print('customers:', len(r_cust.routes), 'expected 4')
print('certificates:', len(r_cert.routes), 'expected 4')
print('matches:', len(r_match.routes), 'expected 2')
print('assessments:', len(r_asmt.routes), 'expected 2')
print('notifications:', len(r_notif.routes), 'expected 2')
print('escalations:', len(r_esc.routes), 'expected 3')
print('audit:', len(r_audit.routes), 'expected 2')
"
```

Expected output:
```
standards: 4 expected 4
customers: 4 expected 4
certificates: 4 expected 4
matches: 2 expected 2
assessments: 2 expected 2
notifications: 2 expected 2
escalations: 3 expected 3
audit: 2 expected 2
```

Total route count across all 8 routers: **23 endpoints**.

```bash
git log --oneline | head -10
```

Expected: 6 new commits from Part 6 (standards, customers, certificates, read-only trio, assessments, escalations).

**Router test files exist but won't run green until Part 7:** They depend on the `client: TestClient` fixture added in Part 7. This is intentional — Part 7's verification step runs the full router test suite end-to-end against the integrated FastAPI app.

```bash
ls tests/routers/
```

Expected files:
```
test_standards_router.py
test_customers_router.py
test_certificates_router.py
test_readonly_routers.py
test_assessments_router.py
test_escalations_router.py
```

---
