# VeloIQ Phase A — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a FastAPI backend with 9-table PostgreSQL schema, CRUD endpoints, application-level audit log enforcement, and synthetic-data seeders that enable `make demo-reset` to a deterministic demo state.

**Architecture:** Hexagonal architecture with `ports/` and `stubs/` directories reserved (empty) for Phase B-D. Sync SQLAlchemy + psycopg2 (no async complexity), application-level audit via `write_audit_entry()` enforcement helper, transactional rollback test isolation.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, PostgreSQL 16, pytest, Docker Compose, psycopg2-binary, Faker

**Spec reference:** `docs/superpowers/specs/2026-04-05-phase-a-foundation-design.md`

**Working directory for all tasks:** `C:/Users/ASR/OneDrive/Desktop/Zealogics Work/Projects/TUV-Velo IQ/veloIQrepo/veloIQ/`

---

## Part 1 — Scaffolding (Tasks 1-4)

### Task 1: Create backend directory structure

**Files:**
- Create: `backend/` directory tree
- Create: `backend/.gitignore`

> **Note:** Git repo already initialized, linked to https://github.com/AtharvaSin/veloiq, and docs already pushed. Root `.gitignore` and `README.md` already exist from initial commit. This task only adds the backend scaffolding.

- [ ] **Step 1: Create backend directory tree**

Run from the veloIQ directory root:

```bash
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/routers
mkdir -p backend/app/services
mkdir -p backend/app/ports
mkdir -p backend/app/stubs
mkdir -p backend/alembic/versions
mkdir -p backend/tests/models
mkdir -p backend/tests/schemas
mkdir -p backend/tests/services
mkdir -p backend/tests/routers
mkdir -p backend/data_seeder
```

- [ ] **Step 2: Create placeholder `__init__.py` files**

Create empty `__init__.py` in each Python package:

```bash
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/services/__init__.py
touch backend/app/ports/__init__.py
touch backend/app/stubs/__init__.py
touch backend/tests/__init__.py
touch backend/tests/models/__init__.py
touch backend/tests/schemas/__init__.py
touch backend/tests/services/__init__.py
touch backend/tests/routers/__init__.py
touch backend/data_seeder/__init__.py
```

Add `.gitkeep` to reserved directories so git tracks empty dirs:

```bash
touch backend/app/ports/.gitkeep
touch backend/app/stubs/.gitkeep
touch backend/alembic/versions/.gitkeep
```

- [ ] **Step 3: Create `backend/.gitignore`**

Create `backend/.gitignore`:

```gitignore
# Alembic
alembic/versions/__pycache__/

# Pytest
.coverage
coverage.xml
htmlcov/

# Build
dist/
*.egg-info/
```

- [ ] **Step 4: Verify directory structure**

Run:

```bash
find backend -type d | sort
```

Expected output:
```
backend
backend/alembic
backend/alembic/versions
backend/app
backend/app/models
backend/app/ports
backend/app/routers
backend/app/schemas
backend/app/services
backend/app/stubs
backend/data_seeder
backend/tests
backend/tests/models
backend/tests/routers
backend/tests/schemas
backend/tests/services
```

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "chore: add backend directory scaffolding"
```

---

### Task 2: Python dependencies and project configuration

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/pytest.ini`

- [ ] **Step 1: Create `backend/requirements.txt`**

```
# Runtime dependencies
fastapi==0.115.4
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.14.0
pydantic==2.9.2
pydantic-settings==2.6.1
python-dateutil==2.9.0
```

- [ ] **Step 2: Create `backend/requirements-dev.txt`**

```
# Development dependencies
-r requirements.txt

pytest==8.3.3
pytest-cov==6.0.0
httpx==0.27.2
faker==33.0.0
black==24.10.0
ruff==0.7.4
mypy==1.13.0
```

- [ ] **Step 3: Create `backend/pyproject.toml`**

```toml
[tool.black]
line-length = 100
target-version = ["py312"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "B", "UP"]
ignore = ["E501"]  # line length handled by black

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["B008"]  # FastAPI Depends in test fixtures

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

- [ ] **Step 4: Create `backend/pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=app --cov-report=term-missing --cov-fail-under=85
filterwarnings =
    ignore::DeprecationWarning:pydantic.*
```

- [ ] **Step 5: Create Python virtual environment and install dependencies**

Run from `backend/`:

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Expected output (last line):
```
Successfully installed fastapi-0.115.4 ... pytest-8.3.3 ...
```

- [ ] **Step 6: Verify installation**

```bash
python -c "import fastapi, sqlalchemy, pytest, alembic; print('OK')"
```

Expected output:
```
OK
```

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/requirements-dev.txt backend/pyproject.toml backend/pytest.ini
git commit -m "chore: add Python dependencies and project configuration"
```

---

### Task 3: Configuration and database connection

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/.env.example`
- Create: `backend/tests/test_config.py`

- [ ] **Step 1: Write failing test for config**

Create `backend/tests/test_config.py`:

```python
from app.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/veloiq")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")

    settings = Settings()

    assert settings.database_url == "postgresql://user:pass@localhost:5432/veloiq"
    assert "http://localhost:5173" in settings.cors_origins


def test_settings_has_defaults():
    settings = Settings(database_url="postgresql://test/test")

    assert settings.api_v1_prefix == "/api/v1"
    assert settings.test_database_url is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.config'`

- [ ] **Step 3: Create `backend/app/config.py`**

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    test_database_url: str | None = Field(default=None, description="Test DB URL override")

    # API
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # Seeder
    faker_seed: int = Field(default=42, description="Fixed seed for reproducible data")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_config.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 5: Create `backend/app/database.py`**

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 6: Create `backend/.env.example`**

```bash
# Copy to .env and fill in values

DATABASE_URL=postgresql://veloiq:veloiq_dev_password@localhost:5432/veloiq
TEST_DATABASE_URL=postgresql://veloiq:veloiq_dev_password@localhost:5432/veloiq_test

API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

FAKER_SEED=42
```

- [ ] **Step 7: Verify database module imports**

```bash
cd backend
DATABASE_URL="postgresql://test/test" python -c "from app.database import engine, SessionLocal, Base, get_db; print('OK')"
```

Expected output:
```
OK
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/config.py backend/app/database.py backend/.env.example backend/tests/test_config.py
git commit -m "feat(config): add Pydantic Settings and SQLAlchemy database connection"
```

---

### Task 4: Exception hierarchy

**Files:**
- Create: `backend/app/exceptions.py`
- Create: `backend/tests/test_exceptions.py`

- [ ] **Step 1: Write failing test for exceptions**

Create `backend/tests/test_exceptions.py`:

```python
from uuid import uuid4

import pytest

from app.exceptions import (
    AuditViolationError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
    VeloIQException,
)


def test_not_found_error_has_entity_and_id():
    entity_id = uuid4()
    exc = NotFoundError(entity="standard", entity_id=entity_id)

    assert exc.entity == "standard"
    assert exc.entity_id == entity_id
    assert exc.code == "NOT_FOUND"
    assert "standard" in str(exc)


def test_validation_error_captures_fields():
    exc = ValidationError(message="Invalid payload", fields={"ac_code": "required"})

    assert exc.message == "Invalid payload"
    assert exc.fields == {"ac_code": "required"}
    assert exc.code == "VALIDATION_ERROR"


def test_audit_violation_error_is_critical():
    exc = AuditViolationError(message="Mutation without audit")

    assert exc.code == "AUDIT_VIOLATION"
    assert exc.message == "Mutation without audit"


def test_business_rule_error_includes_rule_name():
    exc = BusinessRuleError(message="Cannot suspend active cert", rule="cert_status_transition")

    assert exc.rule == "cert_status_transition"
    assert exc.code == "BUSINESS_RULE"


def test_all_exceptions_inherit_from_base():
    assert issubclass(NotFoundError, VeloIQException)
    assert issubclass(ValidationError, VeloIQException)
    assert issubclass(AuditViolationError, VeloIQException)
    assert issubclass(BusinessRuleError, VeloIQException)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/test_exceptions.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.exceptions'`

- [ ] **Step 3: Create `backend/app/exceptions.py`**

```python
from uuid import UUID


class VeloIQException(Exception):
    """Base exception for all VeloIQ application errors."""

    code: str = "VELOIQ_ERROR"
    message: str = "An error occurred"

    def __str__(self) -> str:
        return self.message


class NotFoundError(VeloIQException):
    """Raised when a requested entity does not exist."""

    code = "NOT_FOUND"

    def __init__(self, entity: str, entity_id: UUID | str) -> None:
        self.entity = entity
        self.entity_id = entity_id
        self.message = f"{entity} not found: {entity_id}"
        super().__init__(self.message)


class ValidationError(VeloIQException):
    """Raised when input data fails business validation (beyond Pydantic)."""

    code = "VALIDATION_ERROR"

    def __init__(self, message: str, fields: dict[str, str] | None = None) -> None:
        self.message = message
        self.fields = fields or {}
        super().__init__(self.message)


class AuditViolationError(VeloIQException):
    """Raised when a mutation is attempted without writing an audit entry.

    This is a safety-net exception. Should never fire in well-tested code.
    """

    code = "AUDIT_VIOLATION"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class BusinessRuleError(VeloIQException):
    """Raised when a business rule is violated."""

    code = "BUSINESS_RULE"

    def __init__(self, message: str, rule: str) -> None:
        self.message = message
        self.rule = rule
        super().__init__(self.message)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_exceptions.py -v
```

Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/exceptions.py backend/tests/test_exceptions.py
git commit -m "feat(exceptions): add custom exception hierarchy with HTTP-mappable codes"
```

---

**End of Part 1 — Scaffolding complete.**

**Part 1 verification:**

Run from `backend/`:

```bash
pytest tests/ -v --no-cov
```

Expected: 7 tests pass (2 config + 5 exceptions).

```bash
git log --oneline
```

Expected: 5 commits total (initial docs commit + backend scaffolding, dependencies, config, exceptions).

---

## Part 2 — Database Infrastructure (Tasks 5-7)

Goal: Stand up PostgreSQL via Docker Compose, initialize `veloiq` and `veloiq_test` databases, and create pytest fixtures for transactional rollback isolation. Enables TDD for all subsequent model/service/router tasks.

### Task 5: Docker Compose with PostgreSQL

**Files:**
- Create: `docker-compose.yml` (repo root)
- Create: `.env` (repo root, gitignored)

- [ ] **Step 1: Create `docker-compose.yml` at repo root**

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: veloiq-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-veloiq}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-veloiq_dev_password}
      POSTGRES_DB: ${POSTGRES_DB:-veloiq}
    ports:
      - "5432:5432"
    volumes:
      - veloiq_postgres_data:/var/lib/postgresql/data
      - ./backend/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-veloiq} -d ${POSTGRES_DB:-veloiq}"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  veloiq_postgres_data:
```

- [ ] **Step 2: Create root `.env` (for Docker Compose only)**

Create `.env` at repo root:

```bash
POSTGRES_USER=veloiq
POSTGRES_PASSWORD=veloiq_dev_password
POSTGRES_DB=veloiq
```

Verify it's gitignored:

```bash
git check-ignore -v .env
```

Expected output: `.gitignore:11:*.env      .env`

- [ ] **Step 3: Commit `docker-compose.yml`**

```bash
git add docker-compose.yml
git commit -m "feat(infra): add Docker Compose with PostgreSQL 16"
```

- [ ] **Step 4: Start PostgreSQL container**

```bash
docker compose up -d postgres
```

Expected output (last lines):
```
 ✔ Container veloiq-postgres  Started
```

- [ ] **Step 5: Verify PostgreSQL is ready**

Wait ~10 seconds, then:

```bash
docker compose exec postgres pg_isready -U veloiq -d veloiq
```

Expected output:
```
/var/run/postgresql:5432 - accepting connections
```

---

### Task 6: PostgreSQL init script for veloiq_test database

**Files:**
- Create: `backend/init-db.sql`

- [ ] **Step 1: Create `backend/init-db.sql`**

```sql
-- Runs automatically on first container start via docker-entrypoint-initdb.d
-- Creates the test database alongside the main veloiq database (already created by POSTGRES_DB env var)

CREATE DATABASE veloiq_test;

-- Grant privileges to the veloiq user on both databases
GRANT ALL PRIVILEGES ON DATABASE veloiq TO veloiq;
GRANT ALL PRIVILEGES ON DATABASE veloiq_test TO veloiq;

-- Enable pgcrypto for gen_random_uuid() on both databases
\c veloiq
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\c veloiq_test
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

- [ ] **Step 2: Recreate container so init script runs**

The init script only runs on fresh database initialization. Tear down and recreate:

```bash
docker compose down -v
docker compose up -d postgres
```

Wait ~10 seconds for healthcheck:

```bash
docker compose ps
```

Expected: `veloiq-postgres` status shows `(healthy)`.

- [ ] **Step 3: Verify both databases exist**

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "\l veloiq*"
```

Expected output (among other rows):
```
    Name     | Owner  | ...
-------------+--------+-----
 veloiq      | veloiq |
 veloiq_test | veloiq |
```

- [ ] **Step 4: Verify pgcrypto extension on both databases**

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "SELECT extname FROM pg_extension WHERE extname='pgcrypto';"
docker compose exec postgres psql -U veloiq -d veloiq_test -c "SELECT extname FROM pg_extension WHERE extname='pgcrypto';"
```

Both should return:
```
 extname
----------
 pgcrypto
(1 row)
```

- [ ] **Step 5: Create `backend/.env` from example**

```bash
cd backend
cp .env.example .env
```

- [ ] **Step 6: Verify Python can connect to PostgreSQL**

```bash
cd backend
source .venv/Scripts/activate
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://veloiq:veloiq_dev_password@localhost:5432/veloiq_test')
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1 AS ok'))
    print('Connection OK:', result.scalar())
"
```

Expected output:
```
Connection OK: 1
```

- [ ] **Step 7: Commit**

```bash
git add backend/init-db.sql
git commit -m "feat(infra): add DB init script creating veloiq and veloiq_test databases with pgcrypto"
```

---

### Task 7: Test conftest.py with transactional rollback fixtures

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_conftest_smoke.py`

- [ ] **Step 1: Write a smoke test that exercises the fixtures**

Create `backend/tests/test_conftest_smoke.py`:

```python
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_db_session_fixture_yields_working_session(db_session: Session) -> None:
    """Smoke test: the db_session fixture yields a working SQLAlchemy session."""
    result = db_session.execute(text("SELECT 1 AS ok"))
    assert result.scalar() == 1


def test_db_session_fixture_can_execute_transactional_writes(db_session: Session) -> None:
    """First test: create a temporary table and insert a row within the transaction."""
    db_session.execute(
        text("CREATE TEMPORARY TABLE _isolation_test (val INT) ON COMMIT DROP")
    )
    db_session.execute(text("INSERT INTO _isolation_test (val) VALUES (42)"))
    result = db_session.execute(text("SELECT val FROM _isolation_test"))
    assert result.scalar() == 42


def test_actor_fixture_returns_string(actor: str) -> None:
    """The actor fixture yields a non-empty string."""
    assert isinstance(actor, str)
    assert len(actor) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
source .venv/Scripts/activate
pytest tests/test_conftest_smoke.py -v --no-cov
```

Expected: FAIL with errors about missing `db_session` and `actor` fixtures.

- [ ] **Step 3: Create `backend/tests/conftest.py`**

```python
import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://veloiq:veloiq_dev_password@localhost:5432/veloiq_test",
)


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Session-scoped engine connected to the test database.

    Creates all tables via Base.metadata.create_all at session start.
    Drops all tables at session end.
    """
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.drop_all(engine)  # Clean slate in case prior run left tables
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_connection(test_engine: Engine) -> Generator[Connection, None, None]:
    """Per-test connection wrapped in a transaction that rolls back."""
    connection = test_engine.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()
    connection.close()


@pytest.fixture()
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    """Per-test SQLAlchemy session bound to the transactional connection.

    All writes are rolled back when the test completes — complete isolation.
    """
    TestSession = sessionmaker(bind=db_connection, autocommit=False, autoflush=False)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture()
def actor() -> str:
    """Default test actor identity for audited mutations."""
    return "test-actor"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_conftest_smoke.py -v --no-cov
```

Expected: PASS (3 tests).

- [ ] **Step 5: Verify isolation holds across runs (no state leaks)**

Run twice to confirm clean isolation:

```bash
pytest tests/test_conftest_smoke.py -v --no-cov
pytest tests/test_conftest_smoke.py -v --no-cov
```

Both runs: PASS (3 tests each).

- [ ] **Step 6: Run full test suite to confirm no regressions**

```bash
pytest tests/ -v --no-cov
```

Expected: 10 tests pass (2 config + 5 exceptions + 3 conftest smoke).

- [ ] **Step 7: Commit**

```bash
git add backend/tests/conftest.py backend/tests/test_conftest_smoke.py
git commit -m "test(infra): add pytest fixtures for transactional rollback DB isolation"
```

---

**End of Part 2 — Database infrastructure complete.**

**Part 2 verification:**

Run from repo root:

```bash
docker compose ps
```

Expected: `veloiq-postgres` status `(healthy)`.

Run from `backend/`:

```bash
pytest tests/ -v --no-cov
```

Expected: 10 tests pass (2 config + 5 exceptions + 3 conftest smoke).

```bash
git log --oneline | head -8
```

Expected: 8 commits total (1 initial docs + 4 Part 1 + 3 Part 2).

---

## Part 3 — SQLAlchemy Models & Alembic Migration (Tasks 8-14)

### Task 8: Customer and Standard models

**Files:**
- Create: `backend/app/models/customer.py`, `backend/app/models/standard.py`
- Create: `backend/tests/models/test_customer_model.py`, `backend/tests/models/test_standard_model.py`

- [ ] **Step 1: Write failing test for Customer model**

Create `backend/tests/models/test_customer_model.py`:

```python
from sqlalchemy.orm import Session

from app.models.customer import Customer


def test_customer_can_be_created_with_required_fields(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-0001",
        company_name="Huawei Technologies Co., Ltd.",
        country="CN",
        sales_area="Greater China",
        language="ZH",
        contact_email="li.wei@huawei.example.com",
    )
    db_session.add(customer)
    db_session.flush()

    assert customer.id is not None
    assert customer.customer_number == "CUST-0001"
    assert customer.country == "CN"
    assert customer.created_at is not None


def test_customer_number_must_be_unique(db_session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    db_session.add(Customer(
        customer_number="CUST-DUP", company_name="A", country="DE",
        sales_area="EMEA", language="DE",
    ))
    db_session.flush()

    db_session.add(Customer(
        customer_number="CUST-DUP", company_name="B", country="DE",
        sales_area="EMEA", language="DE",
    ))
    with pytest.raises(IntegrityError):
        db_session.flush()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/models/test_customer_model.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.models.customer'`

- [ ] **Step 3: Create `backend/app/models/customer.py`**

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    sales_area: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(2), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/models/test_customer_model.py -v --no-cov
```

Expected: PASS (2 tests)

- [ ] **Step 5: Write failing test for Standard model**

Create `backend/tests/models/test_standard_model.py`:

```python
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.standard import Standard


def test_standard_can_be_created_with_required_fields(db_session: Session) -> None:
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

    assert standard.id is not None
    assert standard.ac_code == "ISO 9001:2015"
    assert standard.status == "60"
    assert standard.source_payload == {"raw": "test"}


def test_standard_ac_code_must_be_unique(db_session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    common = dict(
        ac_code="ISO 9999:2025", title="T", status="60",
        normalized_code="iso 9999:2025", base_number="9999",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    db_session.add(Standard(**common))
    db_session.flush()
    db_session.add(Standard(**common))
    with pytest.raises(IntegrityError):
        db_session.flush()
```

- [ ] **Step 6: Run test to verify it fails, then create Standard model**

Run test (should fail):

```bash
pytest tests/models/test_standard_model.py -v --no-cov
```

Create `backend/app/models/standard.py`:

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Standard(Base):
    __tablename__ = "standards"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    ac_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    replaced_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    normalized_code: Mapped[str] = mapped_column(String(100), nullable=False)
    base_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    version_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    committee: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ics_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 7: Run both model tests**

```bash
pytest tests/models/ -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/customer.py backend/app/models/standard.py backend/tests/models/
git commit -m "feat(models): add Customer and Standard SQLAlchemy models"
```

---

### Task 9: Certificate and CertStandardLink models

**Files:**
- Create: `backend/app/models/certificate.py`, `backend/app/models/cert_standard_link.py`
- Create: test files for each

- [ ] **Step 1: Write failing test for Certificate model**

Create `backend/tests/models/test_certificate_model.py`:

```python
from datetime import date

from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.customer import Customer


def test_certificate_links_to_customer(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-9001", company_name="TestCo", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-44210",
        customer_id=customer.id,
        product_description="Industrial Control Panel",
        status="active",
        issue_date=date(2024, 3, 15),
        expiry_date=date(2027, 3, 14),
    )
    db_session.add(cert)
    db_session.flush()

    assert cert.id is not None
    assert cert.customer_id == customer.id
    assert cert.status == "active"


def test_certificate_status_check_constraint(db_session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    customer = Customer(
        customer_number="CUST-9002", company_name="TestCo2", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    db_session.add(Certificate(
        certificate_number="TC-BAD",
        customer_id=customer.id,
        product_description="Test",
        status="invalid_status",
        issue_date=date(2024, 1, 1),
        expiry_date=date(2027, 1, 1),
    ))
    with pytest.raises(IntegrityError):
        db_session.flush()
```

- [ ] **Step 2: Create `backend/app/models/certificate.py`**

```python
from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Date, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Certificate(Base):
    __tablename__ = "certificates"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','expiring','expired','suspended')",
            name="ck_certificates_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    certificate_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True
    )
    product_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 3: Run cert test, verify pass**

```bash
pytest tests/models/test_certificate_model.py -v --no-cov
```

Expected: PASS (2 tests)

- [ ] **Step 4: Write failing test for CertStandardLink**

Create `backend/tests/models/test_cert_standard_link_model.py`:

```python
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer


def test_link_captures_messy_sap_format(db_session: Session) -> None:
    customer = Customer(
        customer_number="CUST-L1", company_name="LinkTest", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-LINK-1", customer_id=customer.id,
        product_description="Test", status="active",
        issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
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

    assert link.id is not None
    assert link.standard_ref == "DIN EN ISO 14001:2015-11"
    assert link.base_number == "14001"
```

- [ ] **Step 5: Create `backend/app/models/cert_standard_link.py`**

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CertStandardLink(Base):
    __tablename__ = "cert_standard_links"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    certificate_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False, index=True
    )
    standard_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    base_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

- [ ] **Step 6: Run all model tests**

```bash
pytest tests/models/ -v --no-cov
```

Expected: PASS (7 tests: 2 customer + 2 standard + 2 certificate + 1 link)

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/certificate.py backend/app/models/cert_standard_link.py backend/tests/models/test_certificate_model.py backend/tests/models/test_cert_standard_link_model.py
git commit -m "feat(models): add Certificate and CertStandardLink models with FK to customers"
```

---

### Task 10: MatchResult model

**Files:**
- Create: `backend/app/models/match_result.py`
- Create: `backend/tests/models/test_match_result_model.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/models/test_match_result_model.py
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.match_result import MatchResult
from app.models.standard import Standard
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer


def _setup_parents(db_session: Session) -> tuple[Standard, CertStandardLink]:
    customer = Customer(
        customer_number="CUST-M1", company_name="MatchTest", country="DE",
        sales_area="EMEA", language="DE",
    )
    cert = Certificate(
        certificate_number="TC-M1", customer=None, customer_id=None,
        product_description="Test", status="active",
        issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    db_session.add(customer)
    db_session.flush()
    cert.customer_id = customer.id
    db_session.add(cert)
    db_session.flush()

    standard = Standard(
        ac_code="ISO 14001:2015", title="EMS", status="60",
        normalized_code="iso 14001:2015", base_number="14001",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    link = CertStandardLink(
        certificate_id=cert.id,
        standard_ref="DIN EN ISO 14001:2015-11",
        normalized_ref="14001:2015",
        base_number="14001",
        linked_at=datetime.now(timezone.utc),
    )
    db_session.add_all([standard, link])
    db_session.flush()
    return standard, link


def test_match_result_can_be_created(db_session: Session) -> None:
    standard, link = _setup_parents(db_session)
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

    assert mr.id is not None
    assert mr.similarity_score == Decimal("0.840")
    assert mr.confidence_tier == "expert_review"


def test_match_result_confidence_tier_constraint(db_session: Session) -> None:
    standard, link = _setup_parents(db_session)
    db_session.add(MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.5"), confidence_tier="invalid",
        status="pending", matched_at=datetime.now(timezone.utc),
    ))
    with pytest.raises(IntegrityError):
        db_session.flush()
```

- [ ] **Step 2: Create `backend/app/models/match_result.py`**

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"
    __table_args__ = (
        CheckConstraint(
            "confidence_tier IN ('auto_match','expert_review','manual_triage')",
            name="ck_match_results_tier",
        ),
        UniqueConstraint("natos_standard_id", "cert_link_id", name="uq_match_results_pair"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    natos_standard_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("standards.id"), nullable=False
    )
    cert_link_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cert_standard_links.id"), nullable=False
    )
    similarity_score: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    levenshtein_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    jaro_winkler_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    token_set_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    confidence_tier: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

- [ ] **Step 3: Run tests, verify pass**

```bash
pytest tests/models/test_match_result_model.py -v --no-cov
```

Expected: PASS (2 tests)

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/match_result.py backend/tests/models/test_match_result_model.py
git commit -m "feat(models): add MatchResult model with confidence tier check constraint"
```

---

### Task 11: Assessment and Notification models

**Files:**
- Create: `backend/app/models/assessment.py`, `backend/app/models/notification.py`
- Create: test files

- [ ] **Step 1: Create `backend/app/models/assessment.py`**

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "impact_classification IN ('no_change','administrative','minor_technical','major_technical','safety_critical')",
            name="ck_assessments_impact",
        ),
        CheckConstraint(
            "action_required IN ('reconfirm','retest','suspend','withdraw')",
            name="ck_assessments_action",
        ),
        CheckConstraint(
            "decision IN ('approved','rejected','escalated')",
            name="ck_assessments_decision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    match_result_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("match_results.id"), nullable=False, index=True
    )
    assessor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    impact_classification: Mapped[str] = mapped_column(String(30), nullable=False)
    action_required: Mapped[str] = mapped_column(String(30), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    signature_hash: Mapped[str] = mapped_column(String(128), nullable=False)
```

- [ ] **Step 2: Create `backend/app/models/notification.py`**

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','sent','delivered','opened','clicked','bounced','breached')",
            name="ck_notifications_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    assessment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False
    )
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True
    )
    template_language: Mapped[str] = mapped_column(String(2), nullable=False)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
```

- [ ] **Step 3: Write smoke tests for both**

Create `backend/tests/models/test_assessment_notification_models.py`:

```python
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.notification import Notification
from app.models.match_result import MatchResult
from app.models.standard import Standard
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer


def test_assessment_and_notification_can_be_created(db_session: Session) -> None:
    # Build the full chain
    customer = Customer(
        customer_number="CUST-A1", company_name="AssessTest", country="DE",
        sales_area="EMEA", language="DE",
    )
    db_session.add(customer)
    db_session.flush()

    cert = Certificate(
        certificate_number="TC-A1", customer_id=customer.id,
        product_description="Test", status="active",
        issue_date=date(2024, 1, 1), expiry_date=date(2027, 1, 1),
    )
    standard = Standard(
        ac_code="ISO 9001:2015", title="QMS", status="60",
        normalized_code="iso 9001:2015", base_number="9001",
        source_payload={}, ingested_at=datetime.now(timezone.utc),
    )
    db_session.add_all([cert, standard])
    db_session.flush()

    link = CertStandardLink(
        certificate_id=cert.id, standard_ref="DIN EN ISO 9001:2015",
        normalized_ref="9001:2015", base_number="9001",
        linked_at=datetime.now(timezone.utc),
    )
    db_session.add(link)
    db_session.flush()

    mr = MatchResult(
        natos_standard_id=standard.id, cert_link_id=link.id,
        similarity_score=Decimal("0.95"), confidence_tier="auto_match",
        status="reviewed", matched_at=datetime.now(timezone.utc),
    )
    db_session.add(mr)
    db_session.flush()

    assessment = Assessment(
        match_result_id=mr.id, assessor_id="Dr. M. Weber",
        impact_classification="minor_technical", action_required="reconfirm",
        reason_code="Administrative amendment only", decision="approved",
        decided_at=datetime.now(timezone.utc), signature_hash="abc123",
    )
    db_session.add(assessment)
    db_session.flush()

    notif = Notification(
        assessment_id=assessment.id, customer_id=customer.id,
        template_language="DE", subject="Standard update notification",
        body_html="<html></html>", status="delivered",
        sla_deadline=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db_session.add(notif)
    db_session.flush()

    assert assessment.id is not None
    assert notif.id is not None
    assert notif.assessment_id == assessment.id
```

- [ ] **Step 4: Run test, verify pass**

```bash
pytest tests/models/test_assessment_notification_models.py -v --no-cov
```

Expected: PASS (1 test)

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/assessment.py backend/app/models/notification.py backend/tests/models/test_assessment_notification_models.py
git commit -m "feat(models): add Assessment and Notification models with enum check constraints"
```

---

### Task 12: SalesEscalation and AuditLog models

**Files:**
- Create: `backend/app/models/sales_escalation.py`, `backend/app/models/audit_log.py`

- [ ] **Step 1: Create `backend/app/models/sales_escalation.py`**

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SalesEscalation(Base):
    __tablename__ = "sales_escalations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open','contacted','resolved')",
            name="ck_escalations_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    notification_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False
    )
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True
    )
    escalation_reason: Mapped[str] = mapped_column(String(50), nullable=False)
    opportunity_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

- [ ] **Step 2: Create `backend/app/models/audit_log.py`**

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_log_entity", "entity_type", "entity_id"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
```

- [ ] **Step 3: Write smoke test for both**

Create `backend/tests/models/test_escalation_audit_models.py`:

```python
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.sales_escalation import SalesEscalation
from app.models.audit_log import AuditLog
from app.models.customer import Customer


def test_audit_log_captures_structured_details(db_session: Session) -> None:
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

    assert entry.id is not None
    assert entry.details["ac_code"] == "ISO 9001:2015"
    assert entry.created_at is not None
```

- [ ] **Step 4: Run test, verify pass**

```bash
pytest tests/models/test_escalation_audit_models.py -v --no-cov
```

Expected: PASS (1 test)

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/sales_escalation.py backend/app/models/audit_log.py backend/tests/models/test_escalation_audit_models.py
git commit -m "feat(models): add SalesEscalation and AuditLog (append-only) models"
```

---

### Task 13: Model registry (__init__.py exports)

**Files:**
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Update `backend/app/models/__init__.py`** to export all models

```python
"""SQLAlchemy ORM models. Importing this module registers all tables with Base."""

from app.database import Base
from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard

__all__ = [
    "Base",
    "Customer",
    "Standard",
    "Certificate",
    "CertStandardLink",
    "MatchResult",
    "Assessment",
    "Notification",
    "SalesEscalation",
    "AuditLog",
]
```

- [ ] **Step 2: Verify all models import cleanly**

```bash
cd backend
python -c "from app.models import Base, Customer, Standard, Certificate, CertStandardLink, MatchResult, Assessment, Notification, SalesEscalation, AuditLog; print('All 9 models registered:', len(Base.metadata.tables))"
```

Expected output:
```
All 9 models registered: 9
```

- [ ] **Step 3: Run full test suite to verify no regressions**

```bash
pytest tests/ -v --no-cov
```

Expected: all tests pass (original 10 + new model tests).

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/__init__.py
git commit -m "feat(models): export all 9 models via models/__init__.py"
```

---

### Task 14: Initial Alembic migration with REVOKE on audit_log

**Files:**
- Create: `backend/alembic/env.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/versions/001_initial_schema.py`

- [ ] **Step 1: Initialize Alembic**

```bash
cd backend
alembic init alembic
```

This creates `alembic/env.py`, `alembic.ini`, and scaffolding.

- [ ] **Step 2: Edit `backend/alembic.ini`** to use the env var for DB URL

Replace the `sqlalchemy.url = ...` line with:

```ini
sqlalchemy.url =
```

(Leave empty — env.py will set it from settings.)

- [ ] **Step 3: Edit `backend/alembic/env.py`** to wire up settings and Base

Replace the generated `env.py` with:

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.models import Base  # noqa: F401 - registers all models with Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: Generate initial migration**

```bash
cd backend
alembic revision --autogenerate -m "initial schema"
```

Expected: A new file created in `alembic/versions/` like `xxxxxxxxxxxx_initial_schema.py`.

- [ ] **Step 5: Rename migration to `001_initial_schema.py`**

Rename the generated file to `001_initial_schema.py` (drop the hash prefix) for clarity.

Update the `revision = "..."` line inside the file to `revision = "001"`.

- [ ] **Step 6: Append REVOKE statement to migration**

Add to the end of the `upgrade()` function in `001_initial_schema.py`:

```python
    # Make audit_log append-only: revoke UPDATE and DELETE from the application user
    op.execute("REVOKE UPDATE, DELETE ON audit_log FROM veloiq;")
```

And to the start of `downgrade()`:

```python
    op.execute("GRANT UPDATE, DELETE ON audit_log TO veloiq;")
```

- [ ] **Step 7: Apply migration to the main veloiq database**

```bash
cd backend
alembic upgrade head
```

Expected output (last line):
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial schema
```

- [ ] **Step 8: Verify all 9 tables exist**

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "\dt"
```

Expected: 9 tables listed (customers, standards, certificates, cert_standard_links, match_results, assessments, notifications, sales_escalations, audit_log) + alembic_version.

- [ ] **Step 9: Verify REVOKE was applied**

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "\dp audit_log"
```

Expected: the `veloiq` user should NOT have `w` (UPDATE) or `d` (DELETE) in the access privileges.

- [ ] **Step 10: Verify migration is reversible**

```bash
cd backend
alembic downgrade base
alembic upgrade head
```

Both commands should succeed with no errors.

- [ ] **Step 11: Commit**

```bash
git add backend/alembic backend/alembic.ini
git commit -m "feat(db): initial Alembic migration with REVOKE UPDATE,DELETE on audit_log"
```

---

**End of Part 3 — SQLAlchemy models and Alembic migration complete.**

**Part 3 verification:**

```bash
cd backend
pytest tests/ -v --no-cov
```

Expected: all tests pass (10 + model tests).

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "\dt"
```

Expected: 9 VeloIQ tables + alembic_version.

---
