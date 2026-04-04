# VeloIQ Phase A — Foundation Design Spec

**Date:** 2026-04-05
**Author:** Atharva Singh (Zealogics Inc.)
**Status:** Approved pending final user review
**Phase:** Phase A (Foundation) — Backend scaffold, database schema, CRUD endpoints, data seeders
**Next step:** Implementation plan via `superpowers:writing-plans`

---

## Goal

Deliver a FastAPI backend with a 9-table PostgreSQL schema, full CRUD for entity resources, and synthetic-data seeders that reset to a known demo state. This establishes the foundation on top of which Phase B (Matching Engine), Phase C (TCC Workflow), and Phase D (Notifications/Sales) will be built.

## Scope

**IN scope:**
- FastAPI project scaffolding (Docker Compose, Alembic, pytest)
- 9-table PostgreSQL schema with indexes, foreign keys, check constraints
- Application-level audit log enforcement via `write_audit_entry()` helper
- Pydantic v2 schemas (Create/Read/Update) per resource
- FastAPI routers with `/api/v1/` prefix — read-only for system-generated tables, full CRUD for entity tables
- Data seeders: 30 customers, 50 standards, 200 certificates, 30 historical matches, 30 historical assessments, 20 historical notifications
- `make demo-reset` command: truncate all tables + reseed from scratch
- Test suite with transactional rollback isolation
- Custom exception hierarchy with HTTP status mapping

**OUT of scope (later phases):**
- Normalization pipeline and fuzzy matching engine (Phase B)
- Assessment POST endpoint with TCC decision workflow (Phase C)
- Notification dispatch, SLA tracking, sales escalation logic (Phase D)
- Frontend integration wiring beyond CORS configuration
- Real authentication (mock user header for POC)
- Natos/SAP integration (stubs directory reserved, empty in Phase A)

---

## Foundational Decisions (approved)

| Decision | Choice | Rationale |
|---|---|---|
| **Database driver** | Sync SQLAlchemy + psycopg2 | POC scale (~500 records), simpler test fixtures, faster debugging |
| **Audit log mechanism** | Application-level with `write_audit_entry()` enforcement helper | Testable, semantic-context-rich, TDD-friendly |
| **ID strategy** | UUID v4 + fixed Faker seed (`random.seed(42)`) | Production-ready UUIDs; reproducible synthetic data across runs |
| **Test isolation** | Transactional rollback per test | Fast (<1ms/test), matches production PostgreSQL |
| **Seeder strategy** | Fresh-run (TRUNCATE + seed) via single `make demo-reset` command | Demo reproducibility requires deterministic starting state |
| **Python version** | 3.12 | Matches AI OS stack per CLAUDE.md |
| **Pydantic version** | v2 | Industry standard, FastAPI-native |
| **API versioning** | `/api/v1/` prefix from day one | Standard REST practice |

---

## Section 1 — Architecture & File Structure

**Approach:** Hexagonal architecture with ports/stubs seams. Dependency injection via FastAPI's `Depends`. One responsibility per file.

```
veloIQ/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory, router registration, CORS, exception handlers
│   ├── config.py                  # Pydantic Settings (DB URL, env vars, seed values)
│   ├── database.py                # SQLAlchemy engine, SessionLocal, get_db dependency
│   ├── exceptions.py              # NotFoundError, ValidationError, AuditViolationError, BusinessRuleError
│   │
│   ├── models/                    # SQLAlchemy ORM models (one file per table)
│   │   ├── __init__.py            # Base declarative + exports
│   │   ├── standard.py
│   │   ├── certificate.py
│   │   ├── customer.py
│   │   ├── cert_standard_link.py
│   │   ├── match_result.py
│   │   ├── assessment.py
│   │   ├── notification.py
│   │   ├── sales_escalation.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                   # Pydantic v2 (Create/Read/Update per entity)
│   │   ├── __init__.py
│   │   ├── common.py              # Pagination envelope, error response schemas
│   │   ├── standard.py
│   │   ├── certificate.py
│   │   ├── customer.py
│   │   ├── match_result.py
│   │   ├── assessment.py
│   │   ├── notification.py
│   │   ├── sales_escalation.py
│   │   └── audit_log.py
│   │
│   ├── routers/                   # FastAPI routers (one per resource)
│   │   ├── __init__.py
│   │   ├── standards.py
│   │   ├── certificates.py
│   │   ├── customers.py
│   │   ├── matches.py
│   │   ├── assessments.py
│   │   ├── notifications.py
│   │   ├── escalations.py
│   │   └── audit.py
│   │
│   ├── services/                  # Business logic (audited mutations)
│   │   ├── __init__.py
│   │   ├── audit.py               # write_audit_entry() enforcement helper
│   │   ├── standards_service.py
│   │   ├── certificates_service.py
│   │   ├── customers_service.py
│   │   └── escalations_service.py
│   │
│   ├── ports/                     # Abstract interfaces (Phase B-D will populate)
│   │   ├── __init__.py
│   │   └── .gitkeep
│   │
│   └── stubs/                     # Stub implementations (Phase B-D will populate)
│       ├── __init__.py
│       └── .gitkeep
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # DB fixtures (transactional rollback), test client, mock actor
│   ├── models/
│   ├── services/
│   └── routers/
│
├── data_seeder/
│   ├── __init__.py
│   ├── seed_all.py                # Orchestrator: TRUNCATE + seed in dependency order
│   ├── seed_customers.py
│   ├── seed_standards.py
│   ├── seed_certificates.py       # Creates certs + cert_standard_links
│   ├── seed_historical.py         # match_results + assessments + notifications
│   └── providers.py               # Custom Faker providers for TIC domain
│
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── pyproject.toml                 # black, ruff, mypy config
├── Dockerfile
├── .env.example
├── .dockerignore
└── Makefile                       # demo-reset, test, dev, migrate, etc.

docker-compose.yml                 # at repo root — postgres + backend services
.gitignore                         # at repo root
```

**Directory responsibilities:**
- `models/`: SQLAlchemy ORM classes defining table structure
- `schemas/`: Pydantic models for request/response validation (separate from ORM)
- `routers/`: HTTP endpoint handlers (thin — delegate to services)
- `services/`: Business logic including mandatory audit log writes
- `ports/` + `stubs/`: Reserved for Phase B-D (empty with `.gitkeep` in Phase A)

---

## Section 2 — Database Schema (9 Tables)

All tables include `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` and `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` unless otherwise specified.

### Table 1: `customers`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `customer_number` | VARCHAR(50) | UNIQUE NOT NULL |
| `company_name` | VARCHAR(255) | NOT NULL |
| `country` | CHAR(2) | NOT NULL — ISO 3166-1 alpha-2 |
| `sales_area` | VARCHAR(100) | NOT NULL |
| `language` | CHAR(2) | NOT NULL |
| `contact_name` | VARCHAR(255) | NULL |
| `contact_email` | VARCHAR(255) | NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() |

Indexes: `customer_number`, `country`

### Table 2: `standards`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `ac_code` | VARCHAR(100) | UNIQUE NOT NULL |
| `title` | TEXT | NOT NULL |
| `status` | VARCHAR(10) | NOT NULL — ISO stages 00,10,20,30,40,50,60,90,95 |
| `replaced_by` | VARCHAR(100) | NULL |
| `normalized_code` | VARCHAR(100) | NOT NULL |
| `base_number` | VARCHAR(50) | NOT NULL |
| `version_year` | INT | NULL |
| `committee` | VARCHAR(100) | NULL |
| `ics_code` | VARCHAR(20) | NULL |
| `source_payload` | JSONB | NOT NULL |
| `ingested_at` | TIMESTAMPTZ | NOT NULL |
| `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL |

Indexes: `ac_code`, `status`, `base_number`

### Table 3: `certificates`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `certificate_number` | VARCHAR(50) | UNIQUE NOT NULL |
| `customer_id` | UUID | FK → customers.id NOT NULL |
| `product_description` | TEXT | NOT NULL |
| `status` | VARCHAR(20) | NOT NULL CHECK IN ('active','expiring','expired','suspended') |
| `issue_date` | DATE | NOT NULL |
| `expiry_date` | DATE | NOT NULL |
| `created_at`, `updated_at` | TIMESTAMPTZ | NOT NULL |

Indexes: `customer_id`, `status`, `expiry_date`

### Table 4: `cert_standard_links`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `certificate_id` | UUID | FK → certificates.id NOT NULL |
| `standard_ref` | VARCHAR(200) | NOT NULL — raw messy format as stored in SAP |
| `normalized_ref` | VARCHAR(200) | NOT NULL |
| `base_number` | VARCHAR(50) | NOT NULL |
| `linked_at` | TIMESTAMPTZ | NOT NULL |

Indexes: `certificate_id`, `base_number`

### Table 5: `match_results`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `natos_standard_id` | UUID | FK → standards.id NOT NULL |
| `cert_link_id` | UUID | FK → cert_standard_links.id NOT NULL |
| `similarity_score` | NUMERIC(4,3) | NOT NULL — composite |
| `levenshtein_score` | NUMERIC(4,3) | NULL |
| `jaro_winkler_score` | NUMERIC(4,3) | NULL |
| `token_set_score` | NUMERIC(4,3) | NULL |
| `confidence_tier` | VARCHAR(20) | NOT NULL CHECK IN ('auto_match','expert_review','manual_triage') |
| `status` | VARCHAR(20) | NOT NULL DEFAULT 'pending' |
| `matched_at` | TIMESTAMPTZ | NOT NULL |
| `reviewed_at` | TIMESTAMPTZ | NULL |

Indexes: `confidence_tier`, `status`, UNIQUE `(natos_standard_id, cert_link_id)`

### Table 6: `assessments`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `match_result_id` | UUID | FK → match_results.id NOT NULL |
| `assessor_id` | VARCHAR(100) | NOT NULL |
| `impact_classification` | VARCHAR(30) | NOT NULL CHECK IN ('no_change','administrative','minor_technical','major_technical','safety_critical') |
| `action_required` | VARCHAR(30) | NOT NULL CHECK IN ('reconfirm','retest','suspend','withdraw') |
| `reason_code` | VARCHAR(100) | NOT NULL |
| `notes` | TEXT | NULL |
| `decision` | VARCHAR(20) | NOT NULL CHECK IN ('approved','rejected','escalated') |
| `decided_at` | TIMESTAMPTZ | NOT NULL |
| `signature_hash` | VARCHAR(128) | NOT NULL |

Indexes: `match_result_id`, `assessor_id`, `decided_at`

### Table 7: `notifications`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `assessment_id` | UUID | FK → assessments.id NOT NULL |
| `customer_id` | UUID | FK → customers.id NOT NULL |
| `template_language` | CHAR(2) | NOT NULL |
| `subject` | TEXT | NOT NULL |
| `body_html` | TEXT | NOT NULL |
| `status` | VARCHAR(20) | NOT NULL CHECK IN ('queued','sent','delivered','opened','clicked','bounced','breached') |
| `sent_at`, `delivered_at`, `opened_at`, `clicked_at` | TIMESTAMPTZ | NULL |
| `sla_deadline` | TIMESTAMPTZ | NOT NULL |

Indexes: `customer_id`, `status`, `sla_deadline`

### Table 8: `sales_escalations`

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `notification_id` | UUID | FK → notifications.id NOT NULL |
| `customer_id` | UUID | FK → customers.id NOT NULL |
| `escalation_reason` | VARCHAR(50) | NOT NULL |
| `opportunity_value` | NUMERIC(12,2) | NOT NULL |
| `assigned_to` | VARCHAR(100) | NULL |
| `status` | VARCHAR(20) | NOT NULL CHECK IN ('open','contacted','resolved') |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `resolved_at` | TIMESTAMPTZ | NULL |

Indexes: `customer_id`, `status`

### Table 9: `audit_log` (APPEND-ONLY)

| Column | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `entity_type` | VARCHAR(50) | NOT NULL |
| `entity_id` | UUID | NOT NULL |
| `action` | VARCHAR(50) | NOT NULL |
| `actor` | VARCHAR(100) | NOT NULL |
| `details` | JSONB | NOT NULL |
| `ip_address` | VARCHAR(45) | NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() |

Indexes: `(entity_type, entity_id)`, `created_at`, `actor`

**Enforcement:** Alembic migration includes `REVOKE UPDATE, DELETE ON audit_log FROM veloiq_app_user;` — application user cannot mutate past entries.

---

## Section 3 — API Layer

### URL Structure

All endpoints under `/api/v1/`.

### CRUD Matrix

| Resource | GET list | GET one | POST | PATCH | DELETE | Notes |
|---|---|---|---|---|---|---|
| `/standards` | ✓ | ✓ | ✓ | ✓ | ✗ | Full CRUD |
| `/certificates` | ✓ | ✓ | ✓ | ✓ | ✗ | Full CRUD |
| `/customers` | ✓ | ✓ | ✓ | ✓ | ✗ | Full CRUD |
| `/matches` | ✓ | ✓ | ✗ | ✗ | ✗ | System-generated (Phase B populates) |
| `/assessments` | ✓ | ✓ | ✗ | ✗ | ✗ | POST added in Phase C |
| `/notifications` | ✓ | ✓ | ✗ | ✗ | ✗ | System-generated (Phase D populates) |
| `/escalations` | ✓ | ✓ | ✗ | ✓ | ✗ | PATCH for `status`, `assigned_to` only |
| `/audit` | ✓ | ✓ | ✗ | ✗ | ✗ | Immutable |

**No DELETE endpoints exist anywhere.** Compliance requirement.

### Pydantic Schema Pattern

Each entity has four schemas: `{Resource}Base`, `{Resource}Create`, `{Resource}Update`, `{Resource}Read`. Example:

```python
# app/schemas/standard.py
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

### Pagination

All list endpoints support `?page=1&limit=50&sort=created_at&order=desc`:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 147,
    "total_pages": 3
  }
}
```

### Error Response Pattern

| Exception | HTTP Status | Body Example |
|---|---|---|
| `NotFoundError` | 404 | `{"error": "Standard not found", "code": "NOT_FOUND", "entity": "standard", "id": "..."}` |
| `ValidationError` | 422 | `{"error": "...", "code": "VALIDATION_ERROR", "fields": {...}}` |
| `AuditViolationError` | 500 | `{"error": "Mutation attempted without audit", "code": "AUDIT_VIOLATION"}` |
| `BusinessRuleError` | 409 | `{"error": "...", "code": "BUSINESS_RULE", "rule": "..."}` |

### Filtering (exact-match query params)

- `/standards?status=60&committee=ISO/TC+176`
- `/certificates?customer_id=<uuid>&status=active`
- `/matches?confidence_tier=expert_review&status=pending`
- `/audit?entity_type=assessment&actor=Dr.+M.+Weber&from=2026-04-01&to=2026-04-05`

---

## Section 4 — Service Layer & Audit Enforcement

### Audit Enforcement Helper

`app/services/audit.py` provides the mandatory `write_audit_entry()` function. Every mutation service calls it as part of the same database transaction:

```python
# app/services/audit.py
from datetime import datetime
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
    """
    Write an immutable audit log entry.
    MUST be called within the same transaction as the mutation it audits.
    Returns the AuditLog entry (not yet committed).
    """
    entry = AuditLog(
        id=uuid4(),
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        details=details,
        ip_address=ip_address,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.flush()
    return entry
```

### Mutation Service Pattern

Every service function that mutates state follows this pattern:

```python
# app/services/standards_service.py
def create_standard(
    db: Session,
    payload: StandardCreate,
    actor: str,
) -> Standard:
    # 1. Validate business rules
    # 2. Normalize (placeholder in Phase A — real in Phase B)
    standard = Standard(
        id=uuid4(),
        ac_code=payload.ac_code,
        title=payload.title,
        status=payload.status,
        normalized_code=payload.ac_code.lower().strip(),  # Phase A placeholder
        base_number=payload.ac_code.lower().strip(),       # Phase A placeholder
        source_payload=payload.source_payload,
        ingested_at=datetime.utcnow(),
    )
    db.add(standard)
    db.flush()

    # 3. MANDATORY audit entry in same transaction
    write_audit_entry(
        db,
        entity_type="standard",
        entity_id=standard.id,
        action="created",
        actor=actor,
        details={"ac_code": standard.ac_code, "status": standard.status},
    )

    # 4. Commit (or let caller commit)
    db.commit()
    db.refresh(standard)
    return standard
```

### Actor Identification

Phase A uses a simple `X-User-Id` header for mock authentication. The `get_current_actor()` dependency reads this header and returns a string like `"Dr. M. Weber"` or `"system"`. Production replaces this with real OAuth/JWT.

```python
# app/dependencies.py
from fastapi import Header

def get_current_actor(x_user_id: str | None = Header(default="anonymous")) -> str:
    return x_user_id or "anonymous"
```

### Read-Only Endpoints

System-generated resources (`/matches`, `/notifications`, `/audit`) do NOT go through services. Routers query the database directly via SQLAlchemy sessions. No audit writes needed for reads.

---

## Section 5 — Testing Strategy

### Test Database Isolation

Transactional rollback pattern using pytest fixtures:

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.config import settings

TEST_DATABASE_URL = settings.database_url.replace("/veloiq", "/veloiq_test")

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection)
    session = TestSession()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def actor() -> str:
    return "test-actor"
```

Every test gets a fresh transaction that rolls back after the test — complete isolation with zero cleanup code.

### Test Organization

```
tests/
├── conftest.py
├── models/
│   ├── test_standard_model.py
│   ├── test_certificate_model.py
│   └── ...
├── services/
│   ├── test_audit.py              # write_audit_entry helper tests
│   ├── test_standards_service.py
│   └── ...
└── routers/
    ├── test_standards_router.py
    ├── test_certificates_router.py
    └── ...
```

### Coverage Targets

- **Models:** 100% — every model instantiable, every constraint exercised
- **Services:** 100% — every mutation path has audit log assertion
- **Routers:** >90% — happy path + 404 + validation error per endpoint
- **Overall:** >85% line coverage enforced in `pytest.ini`

### Test Pattern (TDD)

Every service function and router endpoint follows Red → Green → Refactor:

```python
# tests/services/test_standards_service.py
def test_create_standard_writes_audit_entry(db_session, actor):
    # RED: write failing test
    payload = StandardCreate(
        ac_code="ISO 9001:2015",
        title="Quality management systems — Requirements",
        status="60",
        source_payload={"raw": "test"},
    )
    standard = create_standard(db_session, payload, actor)

    audit_entries = db_session.query(AuditLog).filter_by(
        entity_type="standard", entity_id=standard.id
    ).all()

    assert len(audit_entries) == 1
    assert audit_entries[0].action == "created"
    assert audit_entries[0].actor == actor
    assert audit_entries[0].details["ac_code"] == "ISO 9001:2015"
```

---

## Section 6 — Data Seeder & Demo Reset

### Synthetic Data Volumes

| Entity | Count | Distribution |
|---|---|---|
| Customers | 30 | 10 DE, 8 CN, 5 IN, 4 UK, 3 US |
| Standards | 50 | Across ISO stages: 3×Stage 00, 5×10-20, 5×30, 5×40, 5×50, 15×60, 7×90, 5×95 |
| Certificates | 200 | Distributed across 30 customers, 1-10 per customer |
| Cert-standard links | 400 | ~2 standards per certificate |
| Match results | 30 | 10 auto_match, 15 expert_review, 5 manual_triage |
| Assessments | 30 | 10 no_change, 10 minor_technical, 5 major_technical, 5 safety_critical |
| Notifications | 20 | Mix of sent/delivered/opened/clicked/breached statuses |
| Sales escalations | 5 | For 5 breached notifications |

### Fuzzy Matching Test Pairs (seeded for Phase B validation)

The seeder deliberately creates cert_standard_links with messy SAP formats that test the future fuzzy matching engine:

| Natos Record | SAP Mock Record | Challenge |
|---|---|---|
| `ISO 9001:2015` | `DIN EN ISO 9001:2015-11` | National prefix + date variant |
| `ISO 14001:2015` | `BS EN ISO 14001:2015` | British prefix |
| `IEC 62368-1:2023` | `EN IEC 62368-1:2023/AC:2024` | Amendment suffix |
| `ISO 1234:1998` | `ANSI ABC 331:1999/ISO 1234:1998` | Dual numbering |
| `ISO 14001` | `ISO 1401` | Character-level typo |
| `ISO 45001:2018` | `GB/T 45001-2020` | Chinese national adoption |
| `IEC 61000-4-2:2008` | `DIN EN 61000-4-2 VDE 0847-4-2:2010-04` | German VDE overlay |

### Seeder Structure

```python
# data_seeder/seed_all.py
import random
from faker import Faker
from app.database import SessionLocal, engine
from app.models import Base

def reset_and_seed():
    random.seed(42)
    Faker.seed(42)

    # Truncate in dependency order (reverse of FK dependencies)
    with SessionLocal() as db:
        db.execute("TRUNCATE audit_log, sales_escalations, notifications, assessments, match_results, cert_standard_links, certificates, standards, customers RESTART IDENTITY CASCADE")
        db.commit()

    # Seed in dependency order
    with SessionLocal() as db:
        customers = seed_customers(db)
        standards = seed_standards(db)
        certificates, cert_links = seed_certificates(db, customers, standards)
        matches = seed_historical_matches(db, standards, cert_links)
        assessments = seed_historical_assessments(db, matches)
        notifications = seed_historical_notifications(db, assessments, customers)
        seed_historical_escalations(db, notifications, customers)
        db.commit()

    print("✓ Seeded: 30 customers, 50 standards, 200 certificates, 30 matches, 30 assessments, 20 notifications")

if __name__ == "__main__":
    reset_and_seed()
```

### Makefile Commands

```makefile
# Makefile (in backend/)
.PHONY: demo-reset test dev migrate lint

demo-reset:
	python -m data_seeder.seed_all

test:
	pytest -v --cov=app --cov-report=term-missing

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

lint:
	ruff check app tests data_seeder
	mypy app
```

---

## Verification Criteria (Definition of Done for Phase A)

Phase A is complete when ALL of the following are true:

1. **Scaffolding:** `docker-compose up` starts PostgreSQL + backend, backend reachable at `http://localhost:8000/docs` (Swagger UI).
2. **Schema:** All 9 tables exist with correct columns, FKs, check constraints. `audit_log` has REVOKE UPDATE/DELETE applied.
3. **Migrations:** `alembic upgrade head` creates schema from scratch. `alembic downgrade base` drops cleanly.
4. **CRUD:** Every endpoint in the CRUD matrix returns correct responses. `GET /api/v1/standards` returns 50 records after seeding.
5. **Audit enforcement:** Creating/updating any entity via service writes an audit_log entry in the same transaction. Tests assert this.
6. **Seeders:** `make demo-reset` truncates and reseeds deterministically. Running it twice produces identical data.
7. **Tests:** All tests pass. Coverage >85% overall. Transactional rollback isolation confirmed.
8. **Errors:** Requesting a nonexistent UUID returns proper 404 with error schema. Validation failures return 422.
9. **Frontend-ready:** CORS configured for `localhost:5173` (Vite default). API contract documented at `/docs`.

---

## Open Questions for Implementation Plan

These minor decisions will be resolved during plan-writing:

- Exact `pytest.ini` configuration (coverage thresholds, warning filters)
- Alembic `env.py` customization for test database URL override
- Whether to use Alembic auto-generated migrations or hand-write initial schema
- Specific Faker providers for TIC-domain data (standard names, product descriptions)
- Docker health check commands and dependency ordering

---

*Next step: Invoke `superpowers:writing-plans` to produce the bite-sized task plan for Phase A implementation.*
