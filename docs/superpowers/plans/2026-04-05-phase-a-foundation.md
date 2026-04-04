# VeloIQ Phase A — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a FastAPI backend with 9-table PostgreSQL schema, CRUD endpoints, application-level audit log enforcement, and synthetic-data seeders that enable `make demo-reset` to a deterministic demo state.

**Architecture:** Hexagonal architecture with `ports/` and `stubs/` directories reserved (empty) for Phase B-D. Sync SQLAlchemy + psycopg2 (no async complexity), application-level audit via `write_audit_entry()` enforcement helper, transactional rollback test isolation.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, PostgreSQL 16, pytest, Docker Compose, psycopg2-binary, Faker

**Spec reference:** `docs/superpowers/specs/2026-04-05-phase-a-foundation-design.md`

**Working directory for all tasks:** `C:/Users/ASR/OneDrive/Desktop/Zealogics Work/Projects/TUV-Velo IQ/veloIQrepo/veloIQ/`

---

## Part 1 — Scaffolding (Tasks 1-4)

### Task 1: Initialize git repository and directory structure

**Files:**
- Create: `.gitignore` (repo root)
- Create: `README.md` (repo root, brief)
- Create: `backend/` directory tree
- Create: `backend/.gitignore`

- [ ] **Step 1: Initialize git repository**

Run from the veloIQ directory root:

```bash
git init
git branch -M main
```

Expected output:
```
Initialized empty Git repository in .../veloIQ/.git/
```

- [ ] **Step 2: Create root `.gitignore`**

Create `.gitignore` at the repo root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Virtual environments
.venv/
venv/
env/

# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db

# Node (frontend — future phases)
node_modules/
dist/
build/
```

- [ ] **Step 3: Create `README.md`**

Create `README.md` at repo root:

```markdown
# VeloIQ — Standards Automation Platform

**Client:** TÜV Rheinland  **Vendor:** Zealogics Inc.

A compliance automation platform for product certification standards management.
POC demo with synthetic data — see `docs/POC_APPROACH.md` for the full build plan.

## Quick Start

```bash
# Start PostgreSQL + backend
docker compose up -d

# Apply migrations and seed demo data
cd backend && make migrate && make demo-reset

# Run tests
make test

# Access API docs
open http://localhost:8000/docs
```

## Documentation

- `docs/POC_APPROACH.md` — 5-phase build plan
- `docs/UI_UX_DESIGN.md` — Frontend design spec
- `docs/PHASE_A_FOUNDATION_DESIGN.md` — Phase A detailed spec
- `docs/superpowers/` — Superpowers-driven specs and plans
```

- [ ] **Step 4: Create backend directory tree**

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

- [ ] **Step 5: Create placeholder `__init__.py` files**

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

- [ ] **Step 6: Create `backend/.gitignore`**

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

- [ ] **Step 7: Verify directory structure**

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

- [ ] **Step 8: Commit**

```bash
git add .gitignore README.md backend/
git commit -m "chore: initialize veloIQ repo with backend scaffolding"
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

Expected: 4 commits (repo init + scaffolding, dependencies, config, exceptions).

---
