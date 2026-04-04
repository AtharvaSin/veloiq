## Part 4 — Pydantic Schemas (Tasks 15-19)

> **For agentic workers:** Schemas mirror the 9 SQLAlchemy models from Part 3. Each entity gets four Pydantic v2 schemas — `{Resource}Base`, `{Resource}Create`, `{Resource}Update`, `{Resource}Read`. Read schemas use `ConfigDict(from_attributes=True)` to enable construction from ORM instances. System-generated resources (MatchResult, Notification, AuditLog) get Read-only schemas. Assessment is Read-only for Phase A (POST added in Phase C). SalesEscalation gets Read + Update (for `status`/`assigned_to` PATCH per the CRUD matrix). Every schema file is paired with a test that exercises: (1) valid instantiation, (2) required-field enforcement, (3) `from_attributes` construction from a SQLAlchemy model built via Part 3 fixtures.

---

### Task 15: Common schemas — pagination envelope and error responses

**Files:**
- Create: `backend/app/schemas/common.py`
- Create: `backend/tests/schemas/test_common_schemas.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/schemas/test_common_schemas.py`:

```python
import pytest
from pydantic import ValidationError

from app.schemas.common import (
    PaginationMeta,
    PaginatedResponse,
    ErrorResponse,
    ValidationErrorResponse,
)


def test_pagination_meta_computes_valid_envelope() -> None:
    meta = PaginationMeta(page=1, limit=50, total=147, total_pages=3)
    assert meta.page == 1
    assert meta.limit == 50
    assert meta.total == 147
    assert meta.total_pages == 3


def test_pagination_meta_rejects_negative_page() -> None:
    with pytest.raises(ValidationError):
        PaginationMeta(page=0, limit=50, total=147, total_pages=3)


def test_paginated_response_wraps_arbitrary_data() -> None:
    resp = PaginatedResponse[dict](
        data=[{"id": 1}, {"id": 2}],
        pagination=PaginationMeta(page=1, limit=2, total=10, total_pages=5),
    )
    assert len(resp.data) == 2
    assert resp.pagination.total == 10


def test_error_response_shape() -> None:
    err = ErrorResponse(
        error="Standard not found",
        code="NOT_FOUND",
        entity="standard",
        id="abc-123",
    )
    assert err.code == "NOT_FOUND"
    assert err.entity == "standard"


def test_error_response_requires_error_and_code() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse(error="missing code")  # type: ignore[call-arg]


def test_validation_error_response_captures_field_errors() -> None:
    err = ValidationErrorResponse(
        error="Validation failed",
        code="VALIDATION_ERROR",
        fields={"ac_code": "required", "status": "must be ISO stage code"},
    )
    assert err.fields["ac_code"] == "required"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/schemas/test_common_schemas.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.common'`

- [ ] **Step 3: Create `backend/app/schemas/common.py`**

```python
"""Shared response envelopes and error schemas used across all routers."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination envelope metadata returned with every list response."""

    page: int = Field(..., ge=1, description="1-indexed current page")
    limit: int = Field(..., ge=1, le=500, description="Items per page")
    total: int = Field(..., ge=0, description="Total matching records")
    total_pages: int = Field(..., ge=0, description="Total pages available")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper: `{data: [...], pagination: {...}}`."""

    data: list[T]
    pagination: PaginationMeta


class ErrorResponse(BaseModel):
    """Standard error body. Maps to NotFoundError, BusinessRuleError, AuditViolationError."""

    model_config = ConfigDict(extra="allow")

    error: str
    code: str
    entity: str | None = None
    id: str | None = None
    rule: str | None = None


class ValidationErrorResponse(BaseModel):
    """422 response body for Pydantic/business validation failures."""

    error: str
    code: str = "VALIDATION_ERROR"
    fields: dict[str, str] = Field(default_factory=dict)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/schemas/test_common_schemas.py -v --no-cov
```

Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/common.py backend/tests/schemas/test_common_schemas.py
git commit -m "feat(schemas): add common pagination envelope and error response schemas"
```

---

### Task 16: Entity schemas — Customer, Standard, Certificate, CertStandardLink

**Files:**
- Create: `backend/app/schemas/customer.py`
- Create: `backend/app/schemas/standard.py`
- Create: `backend/app/schemas/certificate.py`
- Create: `backend/app/schemas/cert_standard_link.py`
- Create: `backend/tests/schemas/test_entity_schemas.py`

- [ ] **Step 1: Write failing test for all four entity schemas**

Create `backend/tests/schemas/test_entity_schemas.py`:

```python
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.cert_standard_link import CertStandardLink
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
        ingested_at=datetime.now(timezone.utc),
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
        linked_at=datetime.now(timezone.utc),
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/schemas/test_entity_schemas.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.customer'`

- [ ] **Step 3: Create `backend/app/schemas/customer.py`**

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    customer_number: str
    company_name: str
    country: str
    sales_area: str
    language: str
    contact_name: str | None = None
    contact_email: EmailStr | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_name: str | None = None
    country: str | None = None
    sales_area: str | None = None
    language: str | None = None
    contact_name: str | None = None
    contact_email: EmailStr | None = None


class CustomerRead(CustomerBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 4: Create `backend/app/schemas/standard.py`**

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StandardBase(BaseModel):
    ac_code: str
    title: str
    status: str
    replaced_by: str | None = None
    committee: str | None = None
    ics_code: str | None = None


class StandardCreate(StandardBase):
    source_payload: dict


class StandardUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    replaced_by: str | None = None
    committee: str | None = None
    ics_code: str | None = None


class StandardRead(StandardBase):
    id: UUID
    normalized_code: str
    base_number: str
    version_year: int | None
    ingested_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 5: Create `backend/app/schemas/certificate.py`**

```python
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CertificateBase(BaseModel):
    certificate_number: str
    customer_id: UUID
    product_description: str
    status: str
    issue_date: date
    expiry_date: date


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    product_description: str | None = None
    status: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None


class CertificateRead(CertificateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 6: Create `backend/app/schemas/cert_standard_link.py`**

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CertStandardLinkBase(BaseModel):
    standard_ref: str
    normalized_ref: str
    base_number: str


class CertStandardLinkCreate(CertStandardLinkBase):
    certificate_id: UUID


class CertStandardLinkUpdate(BaseModel):
    standard_ref: str | None = None
    normalized_ref: str | None = None
    base_number: str | None = None


class CertStandardLinkRead(CertStandardLinkBase):
    id: UUID
    certificate_id: UUID
    linked_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 7: Run test to verify it passes**

```bash
cd backend
pytest tests/schemas/test_entity_schemas.py -v --no-cov
```

Expected: PASS (12 tests)

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/customer.py backend/app/schemas/standard.py backend/app/schemas/certificate.py backend/app/schemas/cert_standard_link.py backend/tests/schemas/test_entity_schemas.py
git commit -m "feat(schemas): add Customer, Standard, Certificate, CertStandardLink schemas (Base/Create/Update/Read)"
```

---

### Task 17: Workflow schemas — MatchResult and Assessment

**Files:**
- Create: `backend/app/schemas/match_result.py`
- Create: `backend/app/schemas/assessment.py`
- Create: `backend/tests/schemas/test_workflow_schemas.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/schemas/test_workflow_schemas.py`:

```python
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.standard import Standard
from app.schemas.assessment import AssessmentRead
from app.schemas.match_result import MatchResultRead


def _build_match_result(db_session: Session) -> MatchResult:
    customer = Customer(
        customer_number="CUST-WF-1",
        company_name="WorkflowCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-WF-1",
        customer_id=customer.id,
        product_description="T",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    standard = Standard(
        ac_code="ISO 14001:2015",
        title="EMS",
        status="60",
        normalized_code="iso 14001:2015",
        base_number="14001",
        source_payload={},
        ingested_at=datetime.now(timezone.utc),
    )
    db_session.add_all([cert, standard])
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 14001:2015-11",
        normalized_ref="14001:2015",
        base_number="14001",
        linked_at=datetime.now(timezone.utc),
    )
    db_session.add(link)
    db_session.flush()

    mr = MatchResult(
        natos_standard_id=standard.id,
        cert_link_id=link.id,
        similarity_score=Decimal("0.840"),
        levenshtein_score=Decimal("0.820"),
        jaro_winkler_score=Decimal("0.890"),
        token_set_score=Decimal("0.910"),
        confidence_tier="expert_review",
        status="pending",
        matched_at=datetime.now(timezone.utc),
    )
    db_session.add(mr)
    db_session.flush()
    return mr


def test_match_result_read_from_orm_model(db_session: Session) -> None:
    mr = _build_match_result(db_session)

    read = MatchResultRead.model_validate(mr)
    assert read.id == mr.id
    assert read.natos_standard_id == mr.natos_standard_id
    assert read.similarity_score == Decimal("0.840")
    assert read.confidence_tier == "expert_review"
    assert read.status == "pending"
    assert read.reviewed_at is None


def test_match_result_read_preserves_optional_sub_scores(db_session: Session) -> None:
    mr = _build_match_result(db_session)
    read = MatchResultRead.model_validate(mr)
    assert read.levenshtein_score == Decimal("0.820")
    assert read.jaro_winkler_score == Decimal("0.890")
    assert read.token_set_score == Decimal("0.910")


def test_assessment_read_from_orm_model(db_session: Session) -> None:
    mr = _build_match_result(db_session)
    assessment = Assessment(
        match_result_id=mr.id,
        assessor_id="Dr. M. Weber",
        impact_classification="minor_technical",
        action_required="reconfirm",
        reason_code="Administrative amendment only",
        notes="No structural changes; section renumbering only.",
        decision="approved",
        decided_at=datetime.now(timezone.utc),
        signature_hash="abc123def456",
    )
    db_session.add(assessment)
    db_session.flush()

    read = AssessmentRead.model_validate(assessment)
    assert read.id == assessment.id
    assert read.assessor_id == "Dr. M. Weber"
    assert read.impact_classification == "minor_technical"
    assert read.action_required == "reconfirm"
    assert read.decision == "approved"
    assert read.signature_hash == "abc123def456"
    assert read.notes is not None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/schemas/test_workflow_schemas.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.match_result'`

- [ ] **Step 3: Create `backend/app/schemas/match_result.py`**

```python
"""MatchResult schemas — Read-only in Phase A (Phase B matcher populates this table)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MatchResultRead(BaseModel):
    id: UUID
    natos_standard_id: UUID
    cert_link_id: UUID
    similarity_score: Decimal
    levenshtein_score: Decimal | None
    jaro_winkler_score: Decimal | None
    token_set_score: Decimal | None
    confidence_tier: str
    status: str
    matched_at: datetime
    reviewed_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 4: Create `backend/app/schemas/assessment.py`**

```python
"""Assessment schemas — Read-only in Phase A (POST added in Phase C TCC workflow)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssessmentRead(BaseModel):
    id: UUID
    match_result_id: UUID
    assessor_id: str
    impact_classification: str
    action_required: str
    reason_code: str
    notes: str | None
    decision: str
    decided_at: datetime
    signature_hash: str
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd backend
pytest tests/schemas/test_workflow_schemas.py -v --no-cov
```

Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/match_result.py backend/app/schemas/assessment.py backend/tests/schemas/test_workflow_schemas.py
git commit -m "feat(schemas): add MatchResult and Assessment Read schemas (system-generated, Phase A read-only)"
```

---

### Task 18: Communication schemas — Notification and SalesEscalation

**Files:**
- Create: `backend/app/schemas/notification.py`
- Create: `backend/app/schemas/sales_escalation.py`
- Create: `backend/tests/schemas/test_communication_schemas.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/schemas/test_communication_schemas.py`:

```python
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard
from app.schemas.notification import NotificationRead
from app.schemas.sales_escalation import SalesEscalationRead, SalesEscalationUpdate


def _build_notification(db_session: Session) -> tuple[Notification, Customer]:
    customer = Customer(
        customer_number="CUST-NOTIF-1",
        company_name="NotifCo",
        country="DE",
        sales_area="EMEA",
        language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-NOTIF-1",
        customer_id=customer.id,
        product_description="T",
        status="active",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    )
    standard = Standard(
        ac_code="ISO 9001:2015",
        title="QMS",
        status="60",
        normalized_code="iso 9001:2015",
        base_number="9001",
        source_payload={},
        ingested_at=datetime.now(timezone.utc),
    )
    db_session.add_all([cert, standard])
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 9001:2015",
        normalized_ref="9001:2015",
        base_number="9001",
        linked_at=datetime.now(timezone.utc),
    )
    db_session.add(link)
    db_session.flush()

    mr = MatchResult(
        natos_standard_id=standard.id,
        cert_link_id=link.id,
        similarity_score=Decimal("0.95"),
        confidence_tier="auto_match",
        status="reviewed",
        matched_at=datetime.now(timezone.utc),
    )
    db_session.add(mr)
    db_session.flush()

    assessment = Assessment(
        match_result_id=mr.id,
        assessor_id="Dr. M. Weber",
        impact_classification="minor_technical",
        action_required="reconfirm",
        reason_code="Administrative amendment",
        decision="approved",
        decided_at=datetime.now(timezone.utc),
        signature_hash="hash1",
    )
    db_session.add(assessment)
    db_session.flush()

    notif = Notification(
        assessment_id=assessment.id,
        customer_id=customer.id,
        template_language="DE",
        subject="Standard update notification",
        body_html="<html><body>Test</body></html>",
        status="delivered",
        sent_at=datetime.now(timezone.utc),
        delivered_at=datetime.now(timezone.utc),
        sla_deadline=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db_session.add(notif)
    db_session.flush()
    return notif, customer


def test_notification_read_from_orm_model(db_session: Session) -> None:
    notif, _ = _build_notification(db_session)

    read = NotificationRead.model_validate(notif)
    assert read.id == notif.id
    assert read.template_language == "DE"
    assert read.status == "delivered"
    assert read.subject == "Standard update notification"
    assert read.sent_at is not None
    assert read.delivered_at is not None
    assert read.opened_at is None
    assert read.clicked_at is None
    assert read.sla_deadline is not None


def test_sales_escalation_read_from_orm_model(db_session: Session) -> None:
    notif, customer = _build_notification(db_session)

    escalation = SalesEscalation(
        notification_id=notif.id,
        customer_id=customer.id,
        escalation_reason="sla_breached",
        opportunity_value=Decimal("125000.00"),
        assigned_to="sales.rep@tuv.example.com",
        status="open",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(escalation)
    db_session.flush()

    read = SalesEscalationRead.model_validate(escalation)
    assert read.id == escalation.id
    assert read.notification_id == notif.id
    assert read.opportunity_value == Decimal("125000.00")
    assert read.status == "open"
    assert read.assigned_to == "sales.rep@tuv.example.com"
    assert read.resolved_at is None


def test_sales_escalation_update_allows_status_only_patch() -> None:
    patch = SalesEscalationUpdate(status="contacted")
    assert patch.status == "contacted"
    assert patch.assigned_to is None


def test_sales_escalation_update_allows_assigned_to_only_patch() -> None:
    patch = SalesEscalationUpdate(assigned_to="new.rep@tuv.example.com")
    assert patch.assigned_to == "new.rep@tuv.example.com"
    assert patch.status is None


def test_sales_escalation_update_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        SalesEscalationUpdate(opportunity_value=Decimal("999"))  # type: ignore[call-arg]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/schemas/test_communication_schemas.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.notification'`

- [ ] **Step 3: Create `backend/app/schemas/notification.py`**

```python
"""Notification schemas — Read-only in Phase A (Phase D dispatcher populates this table)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: UUID
    assessment_id: UUID
    customer_id: UUID
    template_language: str
    subject: str
    body_html: str
    status: str
    sent_at: datetime | None
    delivered_at: datetime | None
    opened_at: datetime | None
    clicked_at: datetime | None
    sla_deadline: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 4: Create `backend/app/schemas/sales_escalation.py`**

```python
"""SalesEscalation schemas — Read + Update (PATCH status/assigned_to only per CRUD matrix)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SalesEscalationRead(BaseModel):
    id: UUID
    notification_id: UUID
    customer_id: UUID
    escalation_reason: str
    opportunity_value: Decimal
    assigned_to: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class SalesEscalationUpdate(BaseModel):
    """Only `status` and `assigned_to` are mutable post-creation (compliance)."""

    model_config = ConfigDict(extra="forbid")

    status: str | None = None
    assigned_to: str | None = None
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd backend
pytest tests/schemas/test_communication_schemas.py -v --no-cov
```

Expected: PASS (5 tests)

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/notification.py backend/app/schemas/sales_escalation.py backend/tests/schemas/test_communication_schemas.py
git commit -m "feat(schemas): add Notification (Read) and SalesEscalation (Read+Update) schemas"
```

---

### Task 19: AuditLog schema and schemas package registry

**Files:**
- Create: `backend/app/schemas/audit_log.py`
- Create: `backend/tests/schemas/test_audit_log_schema.py`
- Modify: `backend/app/schemas/__init__.py`

- [ ] **Step 1: Write failing test for AuditLog schema**

Create `backend/tests/schemas/test_audit_log_schema.py`:

```python
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead


def test_audit_log_read_from_orm_model(db_session: Session) -> None:
    entry = AuditLog(
        entity_type="standard",
        entity_id=uuid4(),
        action="created",
        actor="Dr. M. Weber",
        details={"ac_code": "ISO 9001:2015", "status": "60"},
        ip_address="192.168.1.100",
    )
    db_session.add(entry)
    db_session.flush()

    read = AuditLogRead.model_validate(entry)
    assert read.id == entry.id
    assert read.entity_type == "standard"
    assert read.action == "created"
    assert read.actor == "Dr. M. Weber"
    assert read.details == {"ac_code": "ISO 9001:2015", "status": "60"}
    assert read.ip_address == "192.168.1.100"
    assert read.created_at is not None


def test_audit_log_read_preserves_nullable_ip(db_session: Session) -> None:
    entry = AuditLog(
        entity_type="assessment",
        entity_id=uuid4(),
        action="decision_recorded",
        actor="system",
        details={"decision": "approved"},
        ip_address=None,
    )
    db_session.add(entry)
    db_session.flush()

    read = AuditLogRead.model_validate(entry)
    assert read.ip_address is None
    assert read.details["decision"] == "approved"


def test_audit_log_read_uses_from_attributes() -> None:
    from app.schemas.audit_log import AuditLogRead
    from pydantic import ConfigDict

    assert isinstance(AuditLogRead.model_config, dict)
    assert AuditLogRead.model_config.get("from_attributes") is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/schemas/test_audit_log_schema.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.audit_log'`

- [ ] **Step 3: Create `backend/app/schemas/audit_log.py`**

```python
"""AuditLog schema — Read-only (append-only table, no Create/Update/Delete exposed)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    actor: str
    details: dict
    ip_address: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 4: Run audit log test to verify it passes**

```bash
cd backend
pytest tests/schemas/test_audit_log_schema.py -v --no-cov
```

Expected: PASS (3 tests)

- [ ] **Step 5: Update `backend/app/schemas/__init__.py`** to export all schemas

Replace the contents of `backend/app/schemas/__init__.py`:

```python
"""Pydantic v2 schemas for request/response validation — mirrors app.models structure."""

from app.schemas.assessment import AssessmentRead
from app.schemas.audit_log import AuditLogRead
from app.schemas.cert_standard_link import (
    CertStandardLinkBase,
    CertStandardLinkCreate,
    CertStandardLinkRead,
    CertStandardLinkUpdate,
)
from app.schemas.certificate import (
    CertificateBase,
    CertificateCreate,
    CertificateRead,
    CertificateUpdate,
)
from app.schemas.common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    ValidationErrorResponse,
)
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
)
from app.schemas.match_result import MatchResultRead
from app.schemas.notification import NotificationRead
from app.schemas.sales_escalation import (
    SalesEscalationRead,
    SalesEscalationUpdate,
)
from app.schemas.standard import (
    StandardBase,
    StandardCreate,
    StandardRead,
    StandardUpdate,
)

__all__ = [
    # Common
    "PaginationMeta",
    "PaginatedResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    # Customer
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerRead",
    # Standard
    "StandardBase",
    "StandardCreate",
    "StandardUpdate",
    "StandardRead",
    # Certificate
    "CertificateBase",
    "CertificateCreate",
    "CertificateUpdate",
    "CertificateRead",
    # CertStandardLink
    "CertStandardLinkBase",
    "CertStandardLinkCreate",
    "CertStandardLinkUpdate",
    "CertStandardLinkRead",
    # Workflow
    "MatchResultRead",
    "AssessmentRead",
    # Communication
    "NotificationRead",
    "SalesEscalationRead",
    "SalesEscalationUpdate",
    # Audit
    "AuditLogRead",
]
```

- [ ] **Step 6: Verify all schemas import cleanly via the package**

```bash
cd backend
python -c "from app.schemas import CustomerRead, StandardRead, CertificateRead, CertStandardLinkRead, MatchResultRead, AssessmentRead, NotificationRead, SalesEscalationRead, AuditLogRead, PaginationMeta, PaginatedResponse, ErrorResponse; print('All schemas exported:', 11)"
```

Expected output:
```
All schemas exported: 11
```

- [ ] **Step 7: Run full schema test suite**

```bash
cd backend
pytest tests/schemas/ -v --no-cov
```

Expected: PASS (6 common + 12 entity + 3 workflow + 5 communication + 3 audit = 29 tests)

- [ ] **Step 8: Run full test suite to confirm no regressions**

```bash
cd backend
pytest tests/ -v --no-cov
```

Expected: all tests pass (Parts 1-3 tests + Part 4 schema tests).

- [ ] **Step 9: Commit**

```bash
git add backend/app/schemas/audit_log.py backend/app/schemas/__init__.py backend/tests/schemas/test_audit_log_schema.py
git commit -m "feat(schemas): add AuditLogRead and export all schemas via schemas/__init__.py"
```

---

**End of Part 4 — Pydantic schemas for all 9 resources complete.**

**Part 4 verification:**

```bash
cd backend
pytest tests/schemas/ -v --no-cov
```

Expected: 29 tests pass across 5 test files (common, entity, workflow, communication, audit).

```bash
cd backend
python -c "from app.schemas import *; print('OK')"
```

Expected: `OK` — all schemas importable from the package root.

```bash
cd backend
pytest tests/ --no-cov -q
```

Expected: full suite green (Parts 1-3 tests + ~29 new schema tests).

---
