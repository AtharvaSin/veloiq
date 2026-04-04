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
