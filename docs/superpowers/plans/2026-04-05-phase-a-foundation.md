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

DATABASE_URL=postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq
TEST_DATABASE_URL=postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq_test

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
engine = create_engine('postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq_test')
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
    "postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq_test",
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

## Part 7 — App Integration & E2E Tests (Tasks 30-31)

This is the final part of Phase A. It wires together everything built in Parts 1-6 into a runnable FastAPI application and proves end-to-end that the stack works: HTTP request arrives → router dispatches → service mutates DB → audit entry is written → response is returned.

By the end of Part 7:
- `uvicorn app.main:app` boots a working API at `http://localhost:8000`.
- All 8 routers are registered under `/api/v1/` with working CRUD behaviour.
- Custom exceptions map to correct HTTP status codes with structured error bodies.
- CORS is configured for the frontend origin (Vite default at `http://localhost:5173`).
- A `client` fixture in `conftest.py` allows writing HTTP-level integration tests.
- An end-to-end smoke test drives the full stack and verifies overall coverage ≥ 85%.

---

### Task 30: FastAPI app factory with exception handlers, CORS, and router registration

**Files:**
- Create: `backend/tests/test_main_app_factory.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Write a failing test for the app factory**

Create `backend/tests/test_main_app_factory.py`:

```python
"""Unit tests for the FastAPI app factory in app/main.py.

These tests verify structural properties of the FastAPI app (title, version,
registered routes, middleware, exception handlers) without hitting the DB.
End-to-end HTTP behaviour is covered in tests/test_smoke.py.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.exceptions import (
    AuditViolationError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
)
from app.main import app, create_app


def test_create_app_returns_fastapi_instance() -> None:
    """create_app() returns a configured FastAPI instance."""
    new_app = create_app()
    assert isinstance(new_app, FastAPI)
    assert new_app.title == "VeloIQ API"
    assert new_app.version == "0.1.0"


def test_module_level_app_is_fastapi_instance() -> None:
    """The module-level `app` object is a FastAPI instance (uvicorn entry point)."""
    assert isinstance(app, FastAPI)
    assert app.title == "VeloIQ API"


def test_health_endpoint_is_registered() -> None:
    """The /health route is registered on the app."""
    paths = {route.path for route in app.routes}
    assert "/health" in paths


def test_all_api_v1_routers_are_registered() -> None:
    """All 8 resource routers are registered under /api/v1/."""
    paths = {route.path for route in app.routes}
    expected_prefixes = [
        "/api/v1/standards",
        "/api/v1/certificates",
        "/api/v1/customers",
        "/api/v1/matches",
        "/api/v1/assessments",
        "/api/v1/notifications",
        "/api/v1/escalations",
        "/api/v1/audit",
    ]
    for prefix in expected_prefixes:
        assert any(p.startswith(prefix) for p in paths), (
            f"No route registered for prefix {prefix}. Registered: {sorted(paths)}"
        )


def test_cors_middleware_is_configured() -> None:
    """CORSMiddleware is attached to the app."""
    middleware_classes = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_classes


def test_all_custom_exception_handlers_are_registered() -> None:
    """All 4 VeloIQ custom exceptions have handlers registered."""
    handled = set(app.exception_handlers.keys())
    assert NotFoundError in handled
    assert ValidationError in handled
    assert BusinessRuleError in handled
    assert AuditViolationError in handled
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
source .venv/Scripts/activate
pytest tests/test_main_app_factory.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.main'` (or `ImportError: cannot import name 'create_app'`).

- [ ] **Step 3: Create `backend/app/main.py`**

```python
"""FastAPI application factory for VeloIQ.

Wires together configuration, middleware, exception handlers, and routers into a
single ASGI application. Exposes both a `create_app()` factory (for testing and
programmatic use) and a module-level `app` instance (for uvicorn / Docker).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import (
    AuditViolationError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
)
from app.routers import (
    assessments,
    audit,
    certificates,
    customers,
    escalations,
    matches,
    notifications,
    standards,
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Returns a fully-wired FastAPI instance with CORS, exception handlers,
    health check, and all /api/v1 routers registered.
    """
    app = FastAPI(
        title="VeloIQ API",
        version="0.1.0",
        description="TÜV Rheinland Standards Automation Platform",
    )

    # --- CORS ------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception handlers ----------------------------------------------
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": str(exc),
                "code": exc.code,
                "entity": exc.entity,
                "id": str(exc.entity_id),
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": exc.message,
                "code": exc.code,
                "fields": exc.fields,
            },
        )

    @app.exception_handler(BusinessRuleError)
    async def business_rule_handler(request: Request, exc: BusinessRuleError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": exc.message,
                "code": exc.code,
                "rule": exc.rule,
            },
        )

    @app.exception_handler(AuditViolationError)
    async def audit_violation_handler(
        request: Request, exc: AuditViolationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": exc.message, "code": exc.code},
        )

    # --- Routers ---------------------------------------------------------
    for module in (
        standards,
        customers,
        certificates,
        matches,
        assessments,
        notifications,
        escalations,
        audit,
    ):
        app.include_router(module.router, prefix=settings.api_v1_prefix)

    # --- Health check ----------------------------------------------------
    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness probe — returns 200 OK with a status payload."""
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/test_main_app_factory.py -v --no-cov
```

Expected: PASS (6 tests).

- [ ] **Step 5: Confirm uvicorn can import the app**

```bash
cd backend
python -c "from app.main import app; print(f'OK: {app.title} v{app.version}')"
```

Expected output: `OK: VeloIQ API v0.1.0`.

- [ ] **Step 6: Run full test suite to confirm no regressions**

```bash
cd backend
pytest tests/ -v --no-cov
```

Expected: all tests from Parts 1-6 still pass, plus the 6 new app-factory tests.

- [ ] **Step 7: Commit**

```bash
git add backend/tests/test_main_app_factory.py backend/app/main.py
git commit -m "feat(api): add FastAPI app factory with CORS, exception handlers, router registration"
```

---

### Task 31: TestClient fixture + end-to-end smoke test

**Files:**
- Modify: `backend/tests/conftest.py` (append `client` fixture)
- Create: `backend/tests/test_smoke.py`

- [ ] **Step 1: Write a failing end-to-end smoke test**

Create `backend/tests/test_smoke.py`:

```python
"""End-to-end smoke tests for the VeloIQ API.

These tests exercise the full HTTP stack: request -> router -> service -> DB ->
audit log -> response. They are the definition-of-done proof for Phase A and
the last line of defence before Phase B begins.
"""
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """GET /health returns 200 OK with a status payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_post_standards_creates_record_and_writes_audit_entry(
    client: TestClient, db_session: Session
) -> None:
    """POST /api/v1/standards creates a standard AND writes an audit_log row.

    This is the core Phase A guarantee: every mutation through the API
    produces an audit entry in the same transaction.
    """
    payload = {
        "ac_code": "ISO 9001:2015",
        "title": "Quality management systems — Requirements",
        "status": "60",
        "source_payload": {"raw": "smoke-test"},
    }
    response = client.post(
        "/api/v1/standards",
        json=payload,
        headers={"X-User-Id": "smoke-test-actor"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ac_code"] == "ISO 9001:2015"
    assert body["status"] == "60"
    assert "id" in body

    # Verify audit log entry was written in the same transaction
    audit_entries = (
        db_session.query(AuditLog)
        .filter_by(entity_type="standard", entity_id=body["id"])
        .all()
    )
    assert len(audit_entries) == 1
    assert audit_entries[0].action == "created"
    assert audit_entries[0].actor == "smoke-test-actor"
    assert audit_entries[0].details["ac_code"] == "ISO 9001:2015"


def test_get_standards_returns_paginated_list(client: TestClient) -> None:
    """GET /api/v1/standards returns a paginated envelope with data + pagination."""
    # Seed 3 records via the API so we have something to list
    for i in range(3):
        client.post(
            "/api/v1/standards",
            json={
                "ac_code": f"ISO {9000 + i}:2015",
                "title": f"Standard {i}",
                "status": "60",
                "source_payload": {"i": i},
            },
            headers={"X-User-Id": "smoke-test-actor"},
        )

    response = client.get("/api/v1/standards?page=1&limit=50")
    assert response.status_code == 200
    body = response.json()

    assert "data" in body
    assert "pagination" in body
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 3

    pagination = body["pagination"]
    assert pagination["page"] == 1
    assert pagination["limit"] == 50
    assert pagination["total"] >= 3
    assert pagination["total_pages"] >= 1


def test_get_standard_by_id_returns_single_record(client: TestClient) -> None:
    """GET /api/v1/standards/{id} returns the matching standard."""
    create_resp = client.post(
        "/api/v1/standards",
        json={
            "ac_code": "ISO 14001:2015",
            "title": "Environmental management systems",
            "status": "60",
            "source_payload": {"raw": "env"},
        },
        headers={"X-User-Id": "smoke-test-actor"},
    )
    assert create_resp.status_code == 201
    standard_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/standards/{standard_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == standard_id
    assert body["ac_code"] == "ISO 14001:2015"


def test_get_nonexistent_standard_returns_404(client: TestClient) -> None:
    """GET /api/v1/standards/{unknown-uuid} returns 404 with structured error body."""
    unknown_id = uuid4()
    response = client.get(f"/api/v1/standards/{unknown_id}")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NOT_FOUND"
    assert body["entity"] == "standard"
    assert body["id"] == str(unknown_id)
    assert "error" in body
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
source .venv/Scripts/activate
pytest tests/test_smoke.py -v --no-cov
```

Expected: FAIL with `fixture 'client' not found` (the `client` fixture doesn't exist in `conftest.py` yet).

- [ ] **Step 3: Append `client` fixture to `backend/tests/conftest.py`**

Open `backend/tests/conftest.py` and append the following at the end of the file:

```python
# --- HTTP client fixture ---------------------------------------------------
# (appended for Part 7: wires FastAPI TestClient to the transactional db_session
# fixture so end-to-end tests share the same rollback-isolated transaction.)
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with the get_db dependency overridden.

    All DB work performed through the client shares the same transactional
    db_session, so writes roll back after the test finishes — complete
    isolation between tests without any cleanup code.
    """
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

**Note:** `pytest`, `Generator`, and `Session` are already imported at the top of `conftest.py` from Task 7 — no additional imports needed at the module top.

- [ ] **Step 4: Run smoke test to verify it passes**

```bash
cd backend
pytest tests/test_smoke.py -v --no-cov
```

Expected: PASS (5 tests).

- [ ] **Step 5: Run full test suite with coverage**

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

Expected:
- All tests from Parts 1-7 pass.
- Overall line coverage **≥ 85%** (per `pytest.ini` threshold from Task 2).
- Coverage per package meets spec targets: models 100%, services 100%, routers ≥ 90%.

- [ ] **Step 6: Boot the app end-to-end and hit it manually**

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 2
curl -s http://localhost:8000/health
curl -s http://localhost:8000/docs -o /dev/null -w "docs: %{http_code}\n"
curl -s http://localhost:8000/api/v1/standards -o /dev/null -w "list: %{http_code}\n"
kill %1
```

Expected output:
```
{"status":"ok"}
docs: 200
list: 200
```

(Note: a live PostgreSQL instance must be running at the URL from `settings.database_url` for the `/api/v1/standards` call to succeed. If using Docker Compose, run `docker compose up -d postgres` first.)

- [ ] **Step 7: Commit**

```bash
git add backend/tests/conftest.py backend/tests/test_smoke.py
git commit -m "test(e2e): add TestClient fixture and end-to-end smoke tests"
```

---

## Part 7 Verification

Phase A is complete when ALL of the following hold:

1. **App factory works:**
   ```bash
   cd backend && python -c "from app.main import app; print(app.title, app.version)"
   ```
   Prints `VeloIQ API 0.1.0`.

2. **Uvicorn boots and serves:**
   ```bash
   uvicorn app.main:app --port 8000
   ```
   `GET http://localhost:8000/health` → `200 {"status": "ok"}`.
   `GET http://localhost:8000/docs` → Swagger UI renders with all 8 resource groups.

3. **All 8 routers are mounted under `/api/v1/`:** visible in `/docs` — standards, customers, certificates, matches, assessments, notifications, escalations, audit.

4. **CORS works for the frontend:** preflight OPTIONS request from `http://localhost:5173` returns 200 with `access-control-allow-origin` header.

5. **Exception handlers map correctly:**
   - `NotFoundError` → 404 with `{error, code, entity, id}`.
   - `ValidationError` → 422 with `{error, code, fields}`.
   - `BusinessRuleError` → 409 with `{error, code, rule}`.
   - `AuditViolationError` → 500 with `{error, code}`.

6. **End-to-end smoke tests pass:**
   ```bash
   cd backend && pytest tests/test_smoke.py -v --no-cov
   ```
   All 5 tests green.

7. **Overall coverage ≥ 85%:**
   ```bash
   cd backend && pytest tests/ --cov=app --cov-report=term-missing
   ```
   The final `TOTAL` line shows coverage ≥ 85% and pytest exits 0 (meaning the threshold in `pytest.ini` is satisfied).

8. **Audit invariant holds end-to-end:** the `test_post_standards_creates_record_and_writes_audit_entry` test proves that an HTTP POST produces both an entity row AND an audit_log row in the same transaction.

9. **Git history is clean:** two commits for Part 7 (`feat(api): ...` and `test(e2e): ...`), both on the Phase A branch, all pre-existing tests still green.

When all 9 items above are satisfied, **Phase A is done**. Phase B (Matching Engine) can begin against this foundation.

## Part 8 — Data Seeders (Tasks 32-36)

> **Spec reference:** Section 6 (Data Seeder & Demo Reset) of `docs/superpowers/specs/2026-04-05-phase-a-foundation-design.md`

This part builds the deterministic synthetic-data seeder suite that powers `make demo-reset`. All randomness is seeded with `42` (via `settings.faker_seed`), so running the full pipeline twice produces byte-identical data. The 7 fuzzy-match test pairs from the spec are seeded verbatim into `cert_standard_links` so that Phase B's matching engine has a known ground truth to validate against.

**Dependency order (seed):** customers → standards → certificates + cert_standard_links → match_results → assessments → notifications → sales_escalations
**Truncate order (reverse of FK dependencies):** audit_log → sales_escalations → notifications → assessments → match_results → cert_standard_links → certificates → standards → customers

---

### Task 32: Faker providers for TIC domain

**Files:**
- Create: `backend/data_seeder/providers.py`
- Create: `backend/tests/data_seeder/__init__.py`
- Create: `backend/tests/data_seeder/test_providers.py`

- [ ] **Step 1: Write failing test for TIC providers**

Create `backend/tests/data_seeder/__init__.py` (empty).

Create `backend/tests/data_seeder/test_providers.py`:

```python
import random

from faker import Faker

from data_seeder.providers import TICProvider


def _make_faker() -> Faker:
    random.seed(42)
    Faker.seed(42)
    fake = Faker()
    fake.add_provider(TICProvider)
    return fake


def test_standard_code_returns_iso_iec_or_en_code() -> None:
    fake = _make_faker()
    code = fake.standard_code()
    assert any(code.startswith(p) for p in ("ISO ", "IEC ", "EN ", "ISO/IEC "))
    # "<prefix> <number>[:<year>]" shape
    assert len(code.split()) >= 2


def test_committee_name_returns_technical_committee_format() -> None:
    fake = _make_faker()
    committee = fake.committee_name()
    assert committee.startswith(("ISO/TC", "IEC/TC", "CEN/TC"))


def test_product_description_returns_tic_domain_text() -> None:
    fake = _make_faker()
    desc = fake.product_description()
    assert isinstance(desc, str)
    assert len(desc) > 10


def test_certificate_number_matches_tc_pattern() -> None:
    fake = _make_faker()
    cert_no = fake.certificate_number()
    assert cert_no.startswith("TC-")
    assert cert_no[3:].isdigit()


def test_tic_company_name_returns_industrial_style_name() -> None:
    fake = _make_faker()
    name = fake.tic_company_name()
    assert isinstance(name, str)
    assert len(name) > 3


def test_providers_are_deterministic_with_seed() -> None:
    fake1 = _make_faker()
    values1 = [fake1.standard_code() for _ in range(10)]

    fake2 = _make_faker()
    values2 = [fake2.standard_code() for _ in range(10)]

    assert values1 == values2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/data_seeder/test_providers.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'data_seeder.providers'`

- [ ] **Step 3: Create `backend/data_seeder/providers.py`**

```python
"""Custom Faker providers for TIC (Testing/Inspection/Certification) domain data."""
from faker.providers import BaseProvider


class TICProvider(BaseProvider):
    """Faker provider producing realistic TIC-industry synthetic values."""

    _STANDARD_PREFIXES = ("ISO ", "IEC ", "ISO/IEC ", "EN ")
    _COMMITTEE_ROOTS = ("ISO/TC", "IEC/TC", "CEN/TC")
    _PRODUCT_CATEGORIES = (
        "Industrial Control Panel",
        "LED Lighting Module",
        "Medical Infusion Pump",
        "Automotive ECU",
        "Household Refrigerator",
        "Power Converter",
        "Safety Relay",
        "Surge Protection Device",
        "Photovoltaic Inverter",
        "Electric Motor Drive",
        "Switchgear Assembly",
        "Smart Meter",
        "HVAC Controller",
        "Emergency Lighting Unit",
        "UPS System",
        "Battery Management System",
    )
    _COMPANY_SUFFIXES = (
        "Technologies Co., Ltd.",
        "Industries GmbH",
        "Electric Ltd.",
        "Systems AG",
        "Manufacturing Pvt. Ltd.",
        "Automation Inc.",
        "Power Solutions Corp.",
        "Engineering Works",
    )
    _COMPANY_ROOTS = (
        "Siemens", "Bosch", "ABB", "Schneider", "Huawei", "Hitachi",
        "Mitsubishi", "Honeywell", "Emerson", "Rockwell", "Yokogawa",
        "Delta", "Omron", "Panasonic", "Danfoss", "Fuji", "Tata",
        "Mahindra", "Larsen", "Reliance", "Wipro",
    )

    def standard_code(self) -> str:
        """Return a synthetic standard code like 'ISO 9001:2015' or 'IEC 61010-1:2010'."""
        prefix = self.random_element(self._STANDARD_PREFIXES)
        number = self.random_int(min=1000, max=99999)
        part = self.random_element((None, None, None, 1, 2, 3, 4))
        year = self.random_int(min=1998, max=2024)
        base = f"{number}-{part}" if part else str(number)
        return f"{prefix}{base}:{year}"

    def committee_name(self) -> str:
        """Return a technical committee designation like 'ISO/TC 176'."""
        root = self.random_element(self._COMMITTEE_ROOTS)
        number = self.random_int(min=1, max=350)
        return f"{root} {number}"

    def product_description(self) -> str:
        """Return a TIC-domain product description with modifiers."""
        category = self.random_element(self._PRODUCT_CATEGORIES)
        rating = self.random_element(("24V DC", "230V AC", "400V AC", "48V DC", "12V DC"))
        current = self.random_int(min=1, max=63)
        return f"{category} — {rating}, {current}A, IP54 enclosure"

    def certificate_number(self) -> str:
        """Return a TÜV-style certificate number like 'TC-44210'."""
        return f"TC-{self.random_int(min=10000, max=99999)}"

    def tic_company_name(self) -> str:
        """Return a synthetic industrial/TIC customer company name."""
        root = self.random_element(self._COMPANY_ROOTS)
        suffix = self.random_element(self._COMPANY_SUFFIXES)
        return f"{root} {suffix}"

    def ics_code(self) -> str:
        """Return an ICS (International Classification for Standards) code like '29.130.20'."""
        group = self.random_int(min=1, max=99)
        sub = self.random_int(min=0, max=200)
        item = self.random_int(min=0, max=99)
        return f"{group:02d}.{sub:03d}.{item:02d}"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend
pytest tests/data_seeder/test_providers.py -v --no-cov
```

Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/data_seeder/providers.py backend/tests/data_seeder/__init__.py backend/tests/data_seeder/test_providers.py
git commit -m "feat(seeder): add TIC-domain Faker providers"
```

---

### Task 33: Customer + Standard seeders

**Files:**
- Create: `backend/data_seeder/seed_customers.py`, `backend/data_seeder/seed_standards.py`
- Create: `backend/tests/data_seeder/test_seed_customers.py`, `backend/tests/data_seeder/test_seed_standards.py`

- [ ] **Step 1: Write failing test for customer seeder**

Create `backend/tests/data_seeder/test_seed_customers.py`:

```python
import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.customer import Customer
from data_seeder.seed_customers import seed_customers


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_customers_creates_30_records(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    assert len(customers) == 30
    assert db_session.query(Customer).count() == 30


def test_seed_customers_country_distribution(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    counts = Counter(c.country for c in customers)
    assert counts["DE"] == 10
    assert counts["CN"] == 8
    assert counts["IN"] == 5
    assert counts["GB"] == 4
    assert counts["US"] == 3


def test_seed_customers_have_unique_customer_numbers(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    numbers = [c.customer_number for c in customers]
    assert len(numbers) == len(set(numbers))


def test_seed_customers_is_deterministic(db_session: Session) -> None:
    _seeded()
    first = [c.customer_number for c in seed_customers(db_session)]
    db_session.query(Customer).delete()
    db_session.flush()

    _seeded()
    second = [c.customer_number for c in seed_customers(db_session)]
    assert first == second
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest tests/data_seeder/test_seed_customers.py -v --no-cov
```

Expected: FAIL with `ModuleNotFoundError: No module named 'data_seeder.seed_customers'`

- [ ] **Step 3: Create `backend/data_seeder/seed_customers.py`**

```python
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


def seed_customers(db: Session) -> list[Customer]:
    """Insert 30 deterministic customers. Caller must flush or commit."""
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
```

- [ ] **Step 4: Run customer seeder test**

```bash
cd backend
pytest tests/data_seeder/test_seed_customers.py -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 5: Write failing test for standard seeder**

Create `backend/tests/data_seeder/test_seed_standards.py`:

```python
import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.seed_standards import seed_standards


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_standards_creates_50_records(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    assert len(standards) == 50
    assert db_session.query(Standard).count() == 50


def test_seed_standards_status_distribution(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    counts = Counter(s.status for s in standards)
    assert counts["00"] == 3
    assert counts["10"] + counts["20"] == 5
    assert counts["30"] == 5
    assert counts["40"] == 5
    assert counts["50"] == 5
    assert counts["60"] == 15
    assert counts["90"] == 7
    assert counts["95"] == 5


def test_seed_standards_includes_fuzzy_match_anchors(db_session: Session) -> None:
    """The 7 Natos sides of the fuzzy test pairs must be seeded as standards."""
    _seeded()
    seed_standards(db_session)
    codes = {s.ac_code for s in db_session.query(Standard).all()}
    expected_anchors = {
        "ISO 9001:2015",
        "ISO 14001:2015",
        "IEC 62368-1:2023",
        "ISO 1234:1998",
        "ISO 14001",
        "ISO 45001:2018",
        "IEC 61000-4-2:2008",
    }
    assert expected_anchors.issubset(codes)


def test_seed_standards_ac_codes_unique(db_session: Session) -> None:
    _seeded()
    standards = seed_standards(db_session)
    codes = [s.ac_code for s in standards]
    assert len(codes) == len(set(codes))
```

- [ ] **Step 6: Create `backend/data_seeder/seed_standards.py`**

```python
"""Seed 50 standards across ISO stages including 7 fuzzy-match anchor codes."""
from datetime import datetime, timezone

from faker import Faker
from sqlalchemy.orm import Session

from app.models.standard import Standard
from data_seeder.providers import TICProvider

# (status, count) — totals to 50
STATUS_DISTRIBUTION: list[tuple[str, int]] = [
    ("00", 3),
    ("10", 3),
    ("20", 2),
    ("30", 5),
    ("40", 5),
    ("50", 5),
    ("60", 15),
    ("90", 7),
    ("95", 5),
]

# 7 anchor codes that pair with messy SAP refs in Task 34 (fuzzy-match test pairs)
FUZZY_MATCH_ANCHORS: list[tuple[str, str, str, str, int | None]] = [
    # (ac_code, title, base_number, normalized_code, version_year)
    ("ISO 9001:2015", "Quality management systems — Requirements", "9001", "iso 9001:2015", 2015),
    ("ISO 14001:2015", "Environmental management systems — Requirements", "14001", "iso 14001:2015", 2015),
    ("IEC 62368-1:2023", "Audio/video, information and communication technology equipment — Safety", "62368", "iec 62368-1:2023", 2023),
    ("ISO 1234:1998", "Gear tooth modifications", "1234", "iso 1234:1998", 1998),
    ("ISO 14001", "Environmental management systems", "14001", "iso 14001", None),
    ("ISO 45001:2018", "Occupational health and safety management systems", "45001", "iso 45001:2018", 2018),
    ("IEC 61000-4-2:2008", "Electromagnetic compatibility — ESD immunity test", "61000", "iec 61000-4-2:2008", 2008),
]


def _parse_version_year(ac_code: str) -> int | None:
    if ":" in ac_code:
        tail = ac_code.rsplit(":", 1)[1]
        if tail.isdigit():
            return int(tail)
    return None


def seed_standards(db: Session) -> list[Standard]:
    """Insert 50 deterministic standards. Includes 7 fuzzy-match anchor codes."""
    fake = Faker()
    fake.add_provider(TICProvider)
    now = datetime.now(timezone.utc)

    standards: list[Standard] = []
    used_codes: set[str] = set()

    # Pre-seed the 7 fuzzy anchors with status="60" (active, most common bucket)
    for ac_code, title, base_number, normalized_code, version_year in FUZZY_MATCH_ANCHORS:
        standard = Standard(
            ac_code=ac_code,
            title=title,
            status="60",
            normalized_code=normalized_code,
            base_number=base_number,
            version_year=version_year,
            committee=fake.committee_name(),
            ics_code=fake.ics_code(),
            source_payload={"source": "fuzzy_anchor", "raw": ac_code},
            ingested_at=now,
        )
        db.add(standard)
        standards.append(standard)
        used_codes.add(ac_code)

    # Distribution tracker: how many of each status we still need.
    remaining: dict[str, int] = dict(STATUS_DISTRIBUTION)
    # Anchors consumed 7 "60" slots already
    remaining["60"] = max(0, remaining["60"] - 7)

    # Fill remainder
    for status, count in remaining.items():
        for _ in range(count):
            while True:
                ac_code = fake.standard_code()
                if ac_code not in used_codes:
                    used_codes.add(ac_code)
                    break
            base_number = ac_code.split()[1].split(":")[0].split("-")[0]
            version_year = _parse_version_year(ac_code)
            standard = Standard(
                ac_code=ac_code,
                title=fake.sentence(nb_words=8).rstrip("."),
                status=status,
                normalized_code=ac_code.lower(),
                base_number=base_number,
                version_year=version_year,
                committee=fake.committee_name(),
                ics_code=fake.ics_code(),
                source_payload={"source": "synthetic", "raw": ac_code},
                ingested_at=now,
            )
            db.add(standard)
            standards.append(standard)

    db.flush()
    return standards
```

- [ ] **Step 7: Run standard seeder test**

```bash
cd backend
pytest tests/data_seeder/test_seed_standards.py -v --no-cov
```

Expected: PASS (4 tests)

- [ ] **Step 8: Commit**

```bash
git add backend/data_seeder/seed_customers.py backend/data_seeder/seed_standards.py backend/tests/data_seeder/test_seed_customers.py backend/tests/data_seeder/test_seed_standards.py
git commit -m "feat(seeder): add customer and standard seeders with fuzzy-match anchors"
```

---

### Task 34: Certificate + CertStandardLink seeder (with fuzzy test pairs)

**Files:**
- Create: `backend/data_seeder/seed_certificates.py`
- Create: `backend/tests/data_seeder/test_seed_certificates.py`

This seeder creates 200 certificates distributed 1-10 per customer, then adds ~400 cert_standard_links. Critically, it seeds the **7 fuzzy-match SAP-side refs** verbatim so Phase B has a deterministic test set.

- [ ] **Step 1: Write failing test for certificate + link seeder**

Create `backend/tests/data_seeder/test_seed_certificates.py`:

```python
import random

from faker import Faker
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from data_seeder.seed_certificates import FUZZY_MATCH_SAP_REFS, seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_standards import seed_standards


def _seeded() -> None:
    random.seed(42)
    Faker.seed(42)


def test_seed_certificates_creates_200_records(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, links = seed_certificates_and_links(db_session, customers, standards)

    assert len(certs) == 200
    assert db_session.query(Certificate).count() == 200


def test_seed_certificates_distributed_across_customers(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    # Every certificate should reference an existing customer
    customer_ids = {c.id for c in customers}
    assert all(cert.customer_id in customer_ids for cert in certs)

    # No customer has more than 10 certificates, none has zero
    from collections import Counter
    counts = Counter(cert.customer_id for cert in certs)
    assert max(counts.values()) <= 10
    assert min(counts.values()) >= 1


def test_seed_cert_links_count_around_400(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)

    assert 380 <= len(links) <= 420  # ~2 per cert ± noise
    assert db_session.query(CertStandardLink).count() == len(links)


def test_fuzzy_match_sap_refs_present(db_session: Session) -> None:
    """All 7 messy SAP-format refs must be present in cert_standard_links."""
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    seed_certificates_and_links(db_session, customers, standards)

    stored_refs = {link.standard_ref for link in db_session.query(CertStandardLink).all()}
    expected_sap_refs = {pair[1] for pair in FUZZY_MATCH_SAP_REFS}
    assert expected_sap_refs.issubset(stored_refs)


def test_certificate_statuses_all_valid(db_session: Session) -> None:
    _seeded()
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    certs, _ = seed_certificates_and_links(db_session, customers, standards)

    valid_statuses = {"active", "expiring", "expired", "suspended"}
    assert all(c.status in valid_statuses for c in certs)
```

- [ ] **Step 2: Create `backend/data_seeder/seed_certificates.py`**

```python
"""Seed 200 certificates + ~400 cert_standard_links including 7 fuzzy-match test pairs."""
import random
from datetime import date, datetime, timedelta, timezone

from faker import Faker
from sqlalchemy.orm import Session

from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.standard import Standard
from data_seeder.providers import TICProvider

# 7 fuzzy-match test pairs: (anchor_ac_code, messy_sap_ref, normalized_ref, base_number)
FUZZY_MATCH_SAP_REFS: list[tuple[str, str, str, str]] = [
    ("ISO 9001:2015", "DIN EN ISO 9001:2015-11", "9001:2015", "9001"),
    ("ISO 14001:2015", "BS EN ISO 14001:2015", "14001:2015", "14001"),
    ("IEC 62368-1:2023", "EN IEC 62368-1:2023/AC:2024", "62368-1:2023", "62368"),
    ("ISO 1234:1998", "ANSI ABC 331:1999/ISO 1234:1998", "1234:1998", "1234"),
    ("ISO 14001", "ISO 1401", "1401", "1401"),
    ("ISO 45001:2018", "GB/T 45001-2020", "45001:2020", "45001"),
    ("IEC 61000-4-2:2008", "DIN EN 61000-4-2 VDE 0847-4-2:2010-04", "61000-4-2:2010", "61000"),
]

CERT_STATUSES: list[tuple[str, float]] = [
    ("active", 0.65),
    ("expiring", 0.15),
    ("expired", 0.15),
    ("suspended", 0.05),
]


def _choose_status() -> str:
    r = random.random()
    cumulative = 0.0
    for status, weight in CERT_STATUSES:
        cumulative += weight
        if r <= cumulative:
            return status
    return "active"


def _distribute_certs_across_customers(num_customers: int, total_certs: int) -> list[int]:
    """Return list of length num_customers where each entry is 1-10 and sum == total_certs."""
    # Start with 1 per customer (ensures min=1)
    counts = [1] * num_customers
    remaining = total_certs - num_customers

    while remaining > 0:
        idx = random.randrange(num_customers)
        if counts[idx] < 10:
            counts[idx] += 1
            remaining -= 1
    return counts


def seed_certificates_and_links(
    db: Session,
    customers: list[Customer],
    standards: list[Standard],
) -> tuple[list[Certificate], list[CertStandardLink]]:
    """Insert 200 certs + ~400 links. Includes 7 fuzzy-match SAP-format test pairs."""
    fake = Faker()
    fake.add_provider(TICProvider)
    now = datetime.now(timezone.utc)
    today = date.today()

    certs_per_customer = _distribute_certs_across_customers(len(customers), 200)

    certificates: list[Certificate] = []
    cert_counter = 1
    for customer, cert_count in zip(customers, certs_per_customer, strict=True):
        for _ in range(cert_count):
            status = _choose_status()
            # Issue date 0-5 years ago
            issue_offset_days = random.randint(0, 5 * 365)
            issue_date = today - timedelta(days=issue_offset_days)
            # Certificates are 3-year cycles typically
            expiry_date = issue_date + timedelta(days=3 * 365)

            cert = Certificate(
                certificate_number=f"TC-{40000 + cert_counter:05d}",
                customer_id=customer.id,
                product_description=fake.product_description(),
                status=status,
                issue_date=issue_date,
                expiry_date=expiry_date,
            )
            db.add(cert)
            certificates.append(cert)
            cert_counter += 1

    db.flush()

    # --- Links: ~2 per certificate, plus embed the 7 fuzzy pairs ---
    links: list[CertStandardLink] = []

    # 1) Embed 7 fuzzy-match SAP refs onto the first 7 certificates
    for idx, (_, sap_ref, normalized_ref, base_number) in enumerate(FUZZY_MATCH_SAP_REFS):
        link = CertStandardLink(
            certificate_id=certificates[idx].id,
            standard_ref=sap_ref,
            normalized_ref=normalized_ref,
            base_number=base_number,
            linked_at=now,
        )
        db.add(link)
        links.append(link)

    # 2) For every certificate, add 1-3 synthetic links (~2 avg)
    for cert in certificates:
        num_links = random.choices([1, 2, 3], weights=[0.25, 0.5, 0.25], k=1)[0]
        chosen = random.sample(standards, k=min(num_links, len(standards)))
        for std in chosen:
            link = CertStandardLink(
                certificate_id=cert.id,
                standard_ref=std.ac_code,
                normalized_ref=std.normalized_code,
                base_number=std.base_number,
                linked_at=now,
            )
            db.add(link)
            links.append(link)

    db.flush()
    return certificates, links
```

- [ ] **Step 3: Run certificate seeder test**

```bash
cd backend
pytest tests/data_seeder/test_seed_certificates.py -v --no-cov
```

Expected: PASS (5 tests)

- [ ] **Step 4: Commit**

```bash
git add backend/data_seeder/seed_certificates.py backend/tests/data_seeder/test_seed_certificates.py
git commit -m "feat(seeder): add certificate + cert_standard_link seeder with 7 fuzzy test pairs"
```

---

### Task 35: Historical data seeder (matches, assessments, notifications, escalations)

**Files:**
- Create: `backend/data_seeder/seed_historical.py`
- Create: `backend/tests/data_seeder/test_seed_historical.py`

This seeder creates the historical demo context: 30 match_results, 30 assessments, 20 notifications, 5 sales_escalations. These records give Phase B-D workflows a realistic starting state.

- [ ] **Step 1: Write failing test for historical seeder**

Create `backend/tests/data_seeder/test_seed_historical.py`:

```python
import random
from collections import Counter

from faker import Faker
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards


def _bootstrap(db_session: Session):
    random.seed(42)
    Faker.seed(42)
    customers = seed_customers(db_session)
    standards = seed_standards(db_session)
    _, links = seed_certificates_and_links(db_session, customers, standards)
    return standards, links, customers


def test_seed_historical_creates_30_matches(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(matches) == 30
    assert db_session.query(MatchResult).count() == 30


def test_match_confidence_tier_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(m.confidence_tier for m in matches)
    assert counts["auto_match"] == 10
    assert counts["expert_review"] == 15
    assert counts["manual_triage"] == 5


def test_match_similarity_scores_match_tier_bands(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, _, _, _ = seed_historical(db_session, standards, links, customers)
    for m in matches:
        score = float(m.similarity_score)
        if m.confidence_tier == "auto_match":
            assert score > 0.95
        elif m.confidence_tier == "expert_review":
            assert 0.70 <= score <= 0.95
        elif m.confidence_tier == "manual_triage":
            assert score < 0.70


def test_seed_historical_creates_30_assessments(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    assert len(assessments) == 30
    assert db_session.query(Assessment).count() == 30


def test_assessment_impact_classification_distribution(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, assessments, _, _ = seed_historical(db_session, standards, links, customers)
    counts = Counter(a.impact_classification for a in assessments)
    assert counts["no_change"] == 10
    assert counts["minor_technical"] == 10
    assert counts["major_technical"] == 5
    assert counts["safety_critical"] == 5


def test_seed_historical_creates_20_notifications(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, _ = seed_historical(db_session, standards, links, customers)
    assert len(notifications) == 20
    assert db_session.query(Notification).count() == 20


def test_seed_historical_creates_5_escalations_for_breached(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    _, _, notifications, escalations = seed_historical(db_session, standards, links, customers)
    assert len(escalations) == 5
    breached_ids = {n.id for n in notifications if n.status == "breached"}
    assert {e.notification_id for e in escalations} == breached_ids


def test_historical_seeder_referential_integrity(db_session: Session) -> None:
    standards, links, customers = _bootstrap(db_session)
    matches, assessments, notifications, escalations = seed_historical(
        db_session, standards, links, customers
    )
    match_ids = {m.id for m in matches}
    for a in assessments:
        assert a.match_result_id in match_ids
    assessment_ids = {a.id for a in assessments}
    for n in notifications:
        assert n.assessment_id in assessment_ids
    notification_ids = {n.id for n in notifications}
    for e in escalations:
        assert e.notification_id in notification_ids
```

- [ ] **Step 2: Create `backend/data_seeder/seed_historical.py`**

```python
"""Seed 30 match_results + 30 assessments + 20 notifications + 5 sales_escalations."""
import hashlib
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.cert_standard_link import CertStandardLink
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard

MATCH_TIER_DISTRIBUTION: list[tuple[str, int, tuple[float, float]]] = [
    # (confidence_tier, count, (score_min, score_max))
    ("auto_match", 10, (0.951, 0.999)),
    ("expert_review", 15, (0.700, 0.950)),
    ("manual_triage", 5, (0.400, 0.699)),
]

ASSESSMENT_IMPACT_DISTRIBUTION: list[tuple[str, int]] = [
    ("no_change", 10),
    ("minor_technical", 10),
    ("major_technical", 5),
    ("safety_critical", 5),
]

IMPACT_TO_ACTION: dict[str, str] = {
    "no_change": "reconfirm",
    "administrative": "reconfirm",
    "minor_technical": "reconfirm",
    "major_technical": "retest",
    "safety_critical": "suspend",
}

NOTIFICATION_STATUS_MIX: list[tuple[str, int]] = [
    # Total = 20; 5 breached drives the 5 escalations
    ("sent", 3),
    ("delivered", 3),
    ("opened", 4),
    ("clicked", 5),
    ("breached", 5),
]

ASSESSORS = (
    "Dr. M. Weber", "Dr. S. Chen", "Dr. R. Kumar", "Dr. A. Müller", "Dr. L. Schmidt",
)


def _round(value: float) -> Decimal:
    return Decimal(f"{value:.3f}")


def seed_historical(
    db: Session,
    standards: list[Standard],
    cert_links: list[CertStandardLink],
    customers: list[Customer],
) -> tuple[list[MatchResult], list[Assessment], list[Notification], list[SalesEscalation]]:
    """Seed historical match_results, assessments, notifications, sales_escalations."""
    fake = Faker()
    now = datetime.now(timezone.utc)

    # --- 30 match_results ---
    matches: list[MatchResult] = []
    used_pairs: set[tuple] = set()
    link_pool = list(cert_links)
    random.shuffle(link_pool)
    link_idx = 0

    for tier, count, (score_min, score_max) in MATCH_TIER_DISTRIBUTION:
        for _ in range(count):
            # Pick a unique (standard, link) pair
            while True:
                std = random.choice(standards)
                link = link_pool[link_idx % len(link_pool)]
                link_idx += 1
                pair = (std.id, link.id)
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    break

            score = random.uniform(score_min, score_max)
            lev = random.uniform(score_min - 0.05, min(score_max + 0.02, 1.0))
            jw = random.uniform(score_min - 0.03, min(score_max + 0.03, 1.0))
            ts = random.uniform(score_min - 0.04, min(score_max + 0.02, 1.0))

            status = "reviewed" if tier != "manual_triage" else "pending"
            reviewed_at = now - timedelta(days=random.randint(1, 60)) if status == "reviewed" else None
            matched_at = (reviewed_at or now) - timedelta(hours=random.randint(1, 72))

            match = MatchResult(
                natos_standard_id=std.id,
                cert_link_id=link.id,
                similarity_score=_round(max(0.0, min(1.0, score))),
                levenshtein_score=_round(max(0.0, min(1.0, lev))),
                jaro_winkler_score=_round(max(0.0, min(1.0, jw))),
                token_set_score=_round(max(0.0, min(1.0, ts))),
                confidence_tier=tier,
                status=status,
                matched_at=matched_at,
                reviewed_at=reviewed_at,
            )
            db.add(match)
            matches.append(match)

    db.flush()

    # --- 30 assessments (one per match) ---
    assessments: list[Assessment] = []
    match_pool = list(matches)
    random.shuffle(match_pool)
    match_idx = 0

    for impact, count in ASSESSMENT_IMPACT_DISTRIBUTION:
        for _ in range(count):
            match = match_pool[match_idx]
            match_idx += 1

            action = IMPACT_TO_ACTION[impact]
            decision = "approved" if impact != "safety_critical" else "escalated"
            decided_at = now - timedelta(days=random.randint(1, 45))
            assessor = random.choice(ASSESSORS)

            sig_input = f"{match.id}:{assessor}:{decided_at.isoformat()}".encode()
            signature = hashlib.sha256(sig_input).hexdigest()

            assessment = Assessment(
                match_result_id=match.id,
                assessor_id=assessor,
                impact_classification=impact,
                action_required=action,
                reason_code=f"RC-{impact.upper()}-{random.randint(100, 999)}",
                notes=fake.sentence(nb_words=12),
                decision=decision,
                decided_at=decided_at,
                signature_hash=signature,
            )
            db.add(assessment)
            assessments.append(assessment)

    db.flush()

    # --- 20 notifications (pick first 20 assessments; assign customers via match→link→cert) ---
    from app.models.certificate import Certificate  # local import to avoid cycle

    notifications: list[Notification] = []
    link_by_id = {link.id: link for link in cert_links}
    cert_id_to_customer: dict = {}
    cert_ids = {link.certificate_id for link in cert_links}
    for cert in db.query(Certificate).filter(Certificate.id.in_(cert_ids)).all():
        cert_id_to_customer[cert.id] = cert.customer_id
    customer_lang = {c.id: c.language for c in customers}

    expanded_statuses: list[str] = []
    for status, count in NOTIFICATION_STATUS_MIX:
        expanded_statuses.extend([status] * count)

    for idx in range(20):
        assessment = assessments[idx]
        match = next(m for m in matches if m.id == assessment.match_result_id)
        link = link_by_id[match.cert_link_id]
        customer_id = cert_id_to_customer[link.certificate_id]
        language = customer_lang.get(customer_id, "EN")

        status = expanded_statuses[idx]
        sent_at = now - timedelta(days=random.randint(5, 30))
        delivered_at = sent_at + timedelta(minutes=random.randint(1, 30)) if status in {"delivered", "opened", "clicked", "breached"} else None
        opened_at = (delivered_at + timedelta(hours=random.randint(1, 48))) if status in {"opened", "clicked"} and delivered_at else None
        clicked_at = (opened_at + timedelta(minutes=random.randint(1, 120))) if status == "clicked" and opened_at else None
        sla_deadline = sent_at + timedelta(days=14)

        notification = Notification(
            assessment_id=assessment.id,
            customer_id=customer_id,
            template_language=language,
            subject=f"Certificate action required: {assessment.action_required}",
            body_html=f"<p>{fake.paragraph(nb_sentences=3)}</p>",
            status=status,
            sent_at=sent_at,
            delivered_at=delivered_at,
            opened_at=opened_at,
            clicked_at=clicked_at,
            sla_deadline=sla_deadline,
        )
        db.add(notification)
        notifications.append(notification)

    db.flush()

    # --- 5 sales_escalations (one per breached notification) ---
    escalations: list[SalesEscalation] = []
    for notification in notifications:
        if notification.status != "breached":
            continue
        escalation = SalesEscalation(
            notification_id=notification.id,
            customer_id=notification.customer_id,
            escalation_reason="sla_breach",
            opportunity_value=Decimal(f"{random.randint(5_000, 150_000)}.00"),
            assigned_to=fake.name(),
            status=random.choice(["open", "contacted"]),
            created_at=notification.sla_deadline + timedelta(hours=1),
            resolved_at=None,
        )
        db.add(escalation)
        escalations.append(escalation)

    db.flush()
    return matches, assessments, notifications, escalations
```

- [ ] **Step 3: Run historical seeder tests**

```bash
cd backend
pytest tests/data_seeder/test_seed_historical.py -v --no-cov
```

Expected: PASS (8 tests)

- [ ] **Step 4: Commit**

```bash
git add backend/data_seeder/seed_historical.py backend/tests/data_seeder/test_seed_historical.py
git commit -m "feat(seeder): add historical matches/assessments/notifications/escalations seeder"
```

---

### Task 36: `seed_all.py` orchestrator with TRUNCATE + verification

**Files:**
- Create: `backend/data_seeder/seed_all.py`
- Create: `backend/tests/data_seeder/test_seed_all.py`

This is the one-command entry point invoked by `make demo-reset`. It TRUNCATEs in reverse FK order, reseeds deterministically, and prints a summary. A final idempotency test verifies that two full runs produce identical UUIDs.

- [ ] **Step 1: Write failing test for orchestrator**

Create `backend/tests/data_seeder/test_seed_all.py`:

```python
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.audit_log import AuditLog
from app.models.cert_standard_link import CertStandardLink
from app.models.certificate import Certificate
from app.models.customer import Customer
from app.models.match_result import MatchResult
from app.models.notification import Notification
from app.models.sales_escalation import SalesEscalation
from app.models.standard import Standard
from data_seeder.seed_all import run_seed_pipeline


def test_orchestrator_seeds_expected_counts(db_session: Session) -> None:
    run_seed_pipeline(db_session)

    assert db_session.query(Customer).count() == 30
    assert db_session.query(Standard).count() == 50
    assert db_session.query(Certificate).count() == 200
    assert 380 <= db_session.query(CertStandardLink).count() <= 420
    assert db_session.query(MatchResult).count() == 30
    assert db_session.query(Assessment).count() == 30
    assert db_session.query(Notification).count() == 20
    assert db_session.query(SalesEscalation).count() == 5


def test_orchestrator_is_deterministic_across_runs(db_session: Session) -> None:
    """Two runs of the pipeline produce IDENTICAL data (counts + sample UUIDs)."""
    run_seed_pipeline(db_session)
    first_customer_ids = [
        c.id for c in db_session.query(Customer).order_by(Customer.customer_number).all()
    ]
    first_standard_codes = [
        s.ac_code for s in db_session.query(Standard).order_by(Standard.ac_code).all()
    ]

    # Clear everything, re-run
    for model in (
        AuditLog, SalesEscalation, Notification, Assessment, MatchResult,
        CertStandardLink, Certificate, Standard, Customer,
    ):
        db_session.query(model).delete()
    db_session.flush()

    run_seed_pipeline(db_session)
    second_customer_ids = [
        c.id for c in db_session.query(Customer).order_by(Customer.customer_number).all()
    ]
    second_standard_codes = [
        s.ac_code for s in db_session.query(Standard).order_by(Standard.ac_code).all()
    ]

    assert first_customer_ids == second_customer_ids
    assert first_standard_codes == second_standard_codes
```

- [ ] **Step 2: Create `backend/data_seeder/seed_all.py`**

```python
"""Orchestrator: TRUNCATE all tables (reverse FK order) then reseed deterministically.

Entry point for `make demo-reset`. Running this twice MUST produce identical data.
"""
import random

from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, engine
from data_seeder.seed_certificates import seed_certificates_and_links
from data_seeder.seed_customers import seed_customers
from data_seeder.seed_historical import seed_historical
from data_seeder.seed_standards import seed_standards

TRUNCATE_SQL = text(
    "TRUNCATE audit_log, sales_escalations, notifications, assessments, "
    "match_results, cert_standard_links, certificates, standards, customers "
    "RESTART IDENTITY CASCADE"
)


def _reset_seeds() -> None:
    """Reset both `random` and `Faker` to the configured fixed seed."""
    random.seed(settings.faker_seed)
    Faker.seed(settings.faker_seed)


def run_seed_pipeline(db: Session) -> dict[str, int]:
    """Reset seeds and execute all seeders in dependency order. Returns summary counts.

    Caller is responsible for commit/rollback. Used by both the CLI entry point
    and the test suite.
    """
    _reset_seeds()

    customers = seed_customers(db)
    standards = seed_standards(db)
    certificates, cert_links = seed_certificates_and_links(db, customers, standards)
    matches, assessments, notifications, escalations = seed_historical(
        db, standards, cert_links, customers
    )

    return {
        "customers": len(customers),
        "standards": len(standards),
        "certificates": len(certificates),
        "cert_standard_links": len(cert_links),
        "match_results": len(matches),
        "assessments": len(assessments),
        "notifications": len(notifications),
        "sales_escalations": len(escalations),
    }


def reset_and_seed() -> None:
    """CLI entry point: TRUNCATE all tables, then run full seeder pipeline."""
    # 1. Truncate in a fresh connection (outside the Session)
    with engine.connect() as conn:
        conn.execute(TRUNCATE_SQL)
        conn.commit()

    # 2. Re-seed inside a Session and commit
    with SessionLocal() as db:
        counts = run_seed_pipeline(db)
        db.commit()

    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    print(f"Seeded: {summary}")


if __name__ == "__main__":
    reset_and_seed()
```

- [ ] **Step 3: Run orchestrator test**

```bash
cd backend
pytest tests/data_seeder/test_seed_all.py -v --no-cov
```

Expected: PASS (2 tests)

- [ ] **Step 4: Run full seeder suite**

```bash
cd backend
pytest tests/data_seeder/ -v --no-cov
```

Expected: PASS (all tests from Tasks 32-36)

- [ ] **Step 5: Execute `make demo-reset` against dev DB**

```bash
cd backend
source .venv/Scripts/activate  # Windows Git Bash
make demo-reset
```

Expected output:
```
Seeded: 30 customers, 50 standards, 200 certificates, 400 cert_standard_links, 30 match_results, 30 assessments, 20 notifications, 5 sales_escalations
```

(Actual `cert_standard_links` count varies 380-420 due to weighted random fan-out.)

- [ ] **Step 6: Verify idempotency via running demo-reset twice**

```bash
cd backend
make demo-reset
make demo-reset
psql "$DATABASE_URL" -c "SELECT count(*) FROM customers;"
psql "$DATABASE_URL" -c "SELECT customer_number, id FROM customers ORDER BY customer_number LIMIT 3;"
```

Record the first UUID. Run `make demo-reset` once more and re-query — the UUIDs must be identical.

- [ ] **Step 7: Commit**

```bash
git add backend/data_seeder/seed_all.py backend/tests/data_seeder/test_seed_all.py
git commit -m "feat(seeder): add seed_all orchestrator with TRUNCATE + determinism test"
```

---

## Part 8 Verification

Part 8 is complete when **all** of the following are true:

1. **Faker providers:** `backend/data_seeder/providers.py` exposes `TICProvider` with `standard_code`, `committee_name`, `product_description`, `certificate_number`, `tic_company_name`, `ics_code`. All provider tests pass.
2. **Customer seeder:** Produces exactly 30 customers with distribution 10 DE / 8 CN / 5 IN / 4 GB / 3 US. Customer numbers are unique `CUST-0001`..`CUST-0030`.
3. **Standard seeder:** Produces exactly 50 standards matching the ISO-stage distribution (3/5/5/5/5/15/7/5). The 7 fuzzy-match anchor codes (`ISO 9001:2015`, `ISO 14001:2015`, `IEC 62368-1:2023`, `ISO 1234:1998`, `ISO 14001`, `ISO 45001:2018`, `IEC 61000-4-2:2008`) are present verbatim.
4. **Certificate seeder:** Produces exactly 200 certificates distributed 1-10 per customer and ~400 `cert_standard_links` (weighted 1-3 per cert). All 7 messy SAP-format refs from the spec table are stored verbatim in `cert_standard_links.standard_ref`.
5. **Historical seeder:** Produces 30 matches (10 auto / 15 expert / 5 triage with matching similarity bands), 30 assessments (10 no_change / 10 minor_technical / 5 major_technical / 5 safety_critical), 20 notifications (status mix spanning sent → breached), 5 escalations (one per breached notification). Full referential integrity across matches → assessments → notifications → escalations.
6. **Orchestrator:** `python -m data_seeder.seed_all` TRUNCATEs all 9 tables (reverse FK order) and reseeds cleanly. Prints summary line.
7. **Determinism:** Running the pipeline twice produces identical `customer_number`-ordered UUID lists and identical sorted `ac_code` lists. Verified by `test_orchestrator_is_deterministic_across_runs`.
8. **All tests pass:** `pytest tests/data_seeder/ -v` shows all tests green (≥25 tests across Tasks 32-36). Overall suite still meets the 85% coverage floor.
9. **Makefile command works:** `make demo-reset` runs end-to-end in <5 seconds against the dev Postgres and produces the expected console summary.

## Part 9 — Final Integration & Verification (Tasks 37-39)

### Task 37: Makefile with all commands

**Files:**
- Create: `backend/Makefile`

- [ ] **Step 1: Create `backend/Makefile`**

```makefile
.PHONY: demo-reset test test-no-cov dev migrate migration lint format install clean

demo-reset:
	python -m data_seeder.seed_all

test:
	pytest -v --cov=app --cov-report=term-missing

test-no-cov:
	pytest -v --no-cov

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

lint:
	ruff check app tests data_seeder
	mypy app

format:
	black app tests data_seeder
	ruff check --fix app tests data_seeder

install:
	pip install -r requirements-dev.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
```

- [ ] **Step 2: Verify Make is available**

```bash
cd backend
make --version
```

Expected: GNU Make 4.x output. If unavailable on Windows, document that `make` requires Git Bash + GnuWin32 make, or use the raw commands.

- [ ] **Step 3: Test `make install` target**

```bash
cd backend
source .venv/Scripts/activate
make install
```

Expected: dependencies already satisfied (installed in earlier tasks), no errors.

- [ ] **Step 4: Test `make lint` target**

```bash
cd backend
make lint
```

Expected: ruff and mypy both pass with 0 errors. If errors appear, fix them before proceeding.

- [ ] **Step 5: Test `make format` target**

```bash
cd backend
make format
```

Expected: black reformats files (or reports no changes); ruff applies fixes. Commit any reformatting changes as a separate chore commit if needed.

- [ ] **Step 6: Test `make test-no-cov` target**

```bash
cd backend
make test-no-cov
```

Expected: all tests pass without coverage overhead.

- [ ] **Step 7: Test `make clean` target**

```bash
cd backend
make clean
ls -la | grep -E "(pycache|cache)" || echo "Clean complete"
```

Expected: all cache directories removed.

- [ ] **Step 8: Commit**

```bash
git add backend/Makefile
git commit -m "chore: add Makefile with dev, test, lint, format, and demo-reset commands"
```

---

### Task 38: Dockerfile and docker-compose backend service

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/.dockerignore`
- Update: `docker-compose.yml` (at repo root) — add backend service

- [ ] **Step 1: Create `backend/.dockerignore`**

```
# Virtual environments
.venv/
venv/
env/

# Python caches
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
coverage.xml

# Local env files
.env
.env.local

# Git
.git/
.gitignore

# Editor
.vscode/
.idea/
*.swp

# Tests
tests/

# Docs
README.md
docs/
```

- [ ] **Step 2: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY data_seeder/ ./data_seeder/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Build Docker image locally**

```bash
cd backend
docker build -t veloiq-backend:latest .
```

Expected: successful build ending with `Successfully tagged veloiq-backend:latest`.

- [ ] **Step 4: Read current `docker-compose.yml`**

```bash
cat docker-compose.yml
```

Confirm the `postgres` service exists (from earlier tasks) with healthcheck. Note the service name, network, and volume definitions.

- [ ] **Step 5: Update `docker-compose.yml` to add backend service**

Add the following service block after the `postgres` service (preserve existing postgres config and volumes):

```yaml
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: veloiq-backend
    environment:
      DATABASE_URL: postgresql://veloiq:veloiq_dev_password@postgres:5432/veloiq
      TEST_DATABASE_URL: postgresql://veloiq:veloiq_dev_password@postgres:5432/veloiq_test
      API_V1_PREFIX: /api/v1
      CORS_ORIGINS: '["http://localhost:5173","http://localhost:3000"]'
      FAKER_SEED: "42"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

- [ ] **Step 6: Start the full stack**

```bash
docker compose up -d
```

Expected: both `veloiq-postgres` and `veloiq-backend` containers running. Check with `docker compose ps`.

- [ ] **Step 7: Verify backend is reachable**

```bash
curl -s http://localhost:8000/docs | head -5
curl -s http://localhost:8000/api/v1/standards | head -c 200
```

Expected: Swagger UI HTML from `/docs`; empty `{"data":[],"pagination":...}` JSON from standards endpoint (DB is empty, migrations only).

- [ ] **Step 8: Check backend logs**

```bash
docker compose logs backend | tail -30
```

Expected: alembic migrations applied (`Running upgrade ... -> 001_initial_schema`), then uvicorn `Application startup complete.`

- [ ] **Step 9: Stop the stack**

```bash
docker compose down
```

- [ ] **Step 10: Commit**

```bash
git add backend/Dockerfile backend/.dockerignore docker-compose.yml
git commit -m "feat(docker): add backend Dockerfile and docker-compose service"
```

---

### Task 39: End-to-end verification and final push

**Files:**
- No new files — runs the complete Definition of Done checklist.

- [ ] **Step 1: Clean slate — rebuild containers from scratch**

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

Expected: fresh postgres volume, fresh backend image, both containers healthy within 30 seconds.

- [ ] **Step 2: Verification check 1-2 — Stack starts, Swagger loads**

```bash
docker compose ps
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
```

Expected: both services running (postgres healthy, backend up); HTTP 200 from `/docs`.

- [ ] **Step 3: Verification check 3 — All 9 tables exist**

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "\dt"
```

Expected: 9 tables listed — `audit_log`, `assessments`, `cert_standard_links`, `certificates`, `customers`, `match_results`, `notifications`, `sales_escalations`, `standards` (plus `alembic_version`).

- [ ] **Step 4: Verification check 4 — audit_log REVOKE applied**

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "\dp audit_log"
```

Expected: `veloiq` user has INSERT + SELECT only; no UPDATE or DELETE in the access privileges column. Alternatively:

```bash
docker compose exec postgres psql -U veloiq -d veloiq -c "UPDATE audit_log SET action='tampered' WHERE id=(SELECT id FROM audit_log LIMIT 1);"
```

Expected: `ERROR: permission denied for table audit_log`.

- [ ] **Step 5: Verification check 5 — Alembic upgrade/downgrade cycle**

```bash
docker compose exec backend alembic downgrade base
docker compose exec postgres psql -U veloiq -d veloiq -c "\dt" | grep -c "row" || echo "All tables dropped"
docker compose exec backend alembic upgrade head
docker compose exec postgres psql -U veloiq -d veloiq -c "\dt"
```

Expected: `downgrade base` drops all 9 tables cleanly; `upgrade head` recreates them.

- [ ] **Step 6: Verification check 6 — Deterministic seed**

```bash
docker compose exec backend python -m data_seeder.seed_all
docker compose exec postgres psql -U veloiq -d veloiq -c "SELECT md5(string_agg(id::text, ',' ORDER BY id::text)) FROM standards;" > /tmp/seed_hash_1.txt

docker compose exec backend python -m data_seeder.seed_all
docker compose exec postgres psql -U veloiq -d veloiq -c "SELECT md5(string_agg(id::text, ',' ORDER BY id::text)) FROM standards;" > /tmp/seed_hash_2.txt

diff /tmp/seed_hash_1.txt /tmp/seed_hash_2.txt && echo "DETERMINISTIC" || echo "NON-DETERMINISTIC (FAIL)"
```

Expected: `DETERMINISTIC` — same MD5 hash of standard IDs across two runs.

- [ ] **Step 7: Verification check 7 — GET /api/v1/standards returns 50**

```bash
curl -s http://localhost:8000/api/v1/standards?limit=100 | python -c "import sys, json; d = json.load(sys.stdin); print(f'standards={len(d[\"data\"])}, total={d[\"pagination\"][\"total\"]}')"
```

Expected: `standards=50, total=50`.

- [ ] **Step 8: Verification check 8 — Creating a standard writes audit entry**

```bash
curl -s -X POST http://localhost:8000/api/v1/standards \
  -H "Content-Type: application/json" \
  -H "X-User-Id: verification-test" \
  -d '{"ac_code":"ISO 99999:2026","title":"Verification test standard","status":"60","source_payload":{"raw":"test"}}' \
  | python -c "import sys, json; d = json.load(sys.stdin); print('id=' + d['id'])" > /tmp/new_standard.txt

NEW_ID=$(cat /tmp/new_standard.txt | cut -d'=' -f2)
curl -s "http://localhost:8000/api/v1/audit?entity_type=standard&entity_id=${NEW_ID}" \
  | python -c "import sys, json; d = json.load(sys.stdin); entries = d['data']; print(f'audit_entries={len(entries)}, action={entries[0][\"action\"] if entries else None}, actor={entries[0][\"actor\"] if entries else None}')"
```

Expected: `audit_entries=1, action=created, actor=verification-test`.

- [ ] **Step 9: Verification check 9 — Tests pass with coverage >= 85%**

```bash
cd backend
source .venv/Scripts/activate
# Use host python env with local postgres from docker-compose
DATABASE_URL="postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq" \
TEST_DATABASE_URL="postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq_test" \
make test
```

Expected: all tests pass; coverage line reads `TOTAL ... XX%` where XX >= 85. `--cov-fail-under=85` in pytest.ini will exit non-zero if threshold missed.

- [ ] **Step 10: Verification check 10 — 404 on nonexistent UUID**

```bash
curl -s -w "\nHTTP=%{http_code}\n" http://localhost:8000/api/v1/standards/00000000-0000-0000-0000-000000000000
```

Expected:
```
{"error":"Standard not found","code":"NOT_FOUND","entity":"standard","id":"00000000-0000-0000-0000-000000000000"}
HTTP=404
```

- [ ] **Step 11: Verification check 11 — CORS for localhost:5173**

```bash
curl -s -X OPTIONS http://localhost:8000/api/v1/standards \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -i | grep -i "access-control-allow-origin"
```

Expected: `access-control-allow-origin: http://localhost:5173`.

- [ ] **Step 12: Verification check 12 — git push succeeds**

```bash
git status
git log --oneline -20
```

Confirm all 39 tasks' commits are present on `main` branch. Then:

```bash
git push origin main
```

Expected: `To https://github.com/AtharvaSin/veloiq.git` with success (no conflicts, no force push needed).

- [ ] **Step 13: Print final Phase A completion summary**

```bash
echo "========================================="
echo "  VeloIQ Phase A — Foundation COMPLETE"
echo "========================================="
echo ""
echo "Infrastructure:"
echo "  - PostgreSQL 16 (via docker compose)"
echo "  - FastAPI backend on :8000"
echo "  - Swagger UI at http://localhost:8000/docs"
echo ""
echo "Database schema (9 tables):"
echo "  customers, standards, certificates, cert_standard_links,"
echo "  match_results, assessments, notifications,"
echo "  sales_escalations, audit_log (append-only, REVOKE enforced)"
echo ""
echo "API endpoints: /api/v1/{standards,certificates,customers,"
echo "  matches,assessments,notifications,escalations,audit}"
echo ""
echo "Seeded data: 30 customers, 50 standards, 200 certificates,"
echo "  400 cert-standard links, 30 matches, 30 assessments,"
echo "  20 notifications, 5 escalations"
echo ""
echo "Test suite: transactional rollback, coverage >= 85%"
echo ""
echo "Next: Phase B (Matching Engine) — fuzzy matching on"
echo "  cert_standard_links with normalization pipeline"
echo "========================================="
```

- [ ] **Step 14: Create final commit marker**

```bash
git commit --allow-empty -m "feat: complete VeloIQ Phase A foundation implementation

Phase A delivers:
- FastAPI backend scaffold (Docker, Alembic, pytest)
- 9-table PostgreSQL schema with FKs, check constraints, audit REVOKE
- Full CRUD for standards/certificates/customers
- Read-only endpoints for matches/assessments/notifications/audit
- Application-level audit enforcement via write_audit_entry()
- Deterministic seeder (30/50/200/400/30/30/20/5 records)
- Transactional-rollback test isolation, >=85% coverage
- docker compose up brings full stack online

Definition of Done: all 12 verification checks pass.
Next: Phase B (Matching Engine)."
git push origin main
```

- [ ] **Step 15: Tear down and verify reproducibility**

```bash
docker compose down -v
docker compose up -d
sleep 10
curl -s http://localhost:8000/api/v1/standards | python -c "import sys, json; d = json.load(sys.stdin); print(f'total={d[\"pagination\"][\"total\"]}')"
docker compose exec backend python -m data_seeder.seed_all
curl -s http://localhost:8000/api/v1/standards | python -c "import sys, json; d = json.load(sys.stdin); print(f'total={d[\"pagination\"][\"total\"]}')"
docker compose down
```

Expected: fresh stack starts cleanly, initially `total=0` after migrations, `total=50` after seed. Phase A is reproducible from `docker compose up` + `make demo-reset`.

---

## Phase A — Definition of Done Checklist

All 12 criteria from the design spec must be verified green before declaring Phase A complete:

| # | Criterion | Verified By |
|---|---|---|
| 1 | `docker compose up` starts PostgreSQL + backend | Task 39 Step 2 |
| 2 | `http://localhost:8000/docs` loads Swagger UI | Task 39 Step 2 |
| 3 | All 9 tables exist with correct schemas | Task 39 Step 3 |
| 4 | `audit_log` has REVOKE UPDATE/DELETE applied | Task 39 Step 4 |
| 5 | `alembic upgrade head` and `alembic downgrade base` both work | Task 39 Step 5 |
| 6 | `make demo-reset` seeds deterministic data (run twice, identical output) | Task 39 Step 6 |
| 7 | `GET /api/v1/standards` returns 50 records | Task 39 Step 7 |
| 8 | Creating a standard writes an audit_log entry in same transaction | Task 39 Step 8 |
| 9 | `make test` passes with coverage >= 85% | Task 39 Step 9 |
| 10 | `GET /api/v1/{nonexistent-uuid}` returns proper 404 | Task 39 Step 10 |
| 11 | CORS configured for localhost:5173 | Task 39 Step 11 |
| 12 | `git push origin main` succeeds (no merge conflicts) | Task 39 Step 12 |

When all 12 rows are checked green, Phase A is officially complete and Phase B (Matching Engine) can begin.

---

**End of Phase A Implementation Plan**
