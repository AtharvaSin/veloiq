# VeloIQ Backend

FastAPI backend for VeloIQ — a TÜV Rheinland Standards Automation POC. Phase A delivers the foundation: 9-table PostgreSQL schema, 23 REST endpoints, service-layer audit enforcement, and deterministic seeders for demo/test data.

## Quick Start (Docker Compose)

From the repo root:

```bash
docker compose up -d            # starts postgres + backend
docker compose exec backend python -m data_seeder.seed_all   # seeds demo data
```

Then open:
- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **Sample endpoint:** http://localhost:8000/api/v1/standards?limit=10

Teardown:
```bash
docker compose down      # keeps postgres volume
docker compose down -v   # wipes postgres volume
```

## Local Development (no Docker for backend)

Postgres still runs via Docker, but the backend runs natively against it.

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash
# source .venv/bin/activate          # macOS/Linux
pip install -r requirements-dev.txt

# Start postgres only
docker compose up -d postgres

# Apply migrations
alembic upgrade head

# Seed demo data
python -m data_seeder.seed_all

# Start FastAPI with auto-reload
uvicorn app.main:app --reload --port 8000
```

## Make Targets

From `backend/`:

| Target | What it does |
|---|---|
| `make dev` | Start uvicorn with `--reload` |
| `make migrate` | `alembic upgrade head` |
| `make migration m="message"` | Generate new autogenerate migration |
| `make demo-reset` | TRUNCATE all tables + reseed deterministic data |
| `make test` | Run full pytest suite with coverage |
| `make test-no-cov` | Faster test run without coverage overhead |
| `make lint` | `ruff check` + `mypy app` |
| `make format` | `black` + `ruff --fix` |
| `make clean` | Remove `__pycache__/`, `.pytest_cache/`, etc. |

*Note: Windows users without `make` can run the underlying commands directly.*

## Architecture

```
backend/
├── app/
│   ├── main.py              FastAPI app factory (CORS, exception handlers, 8 routers)
│   ├── config.py            Pydantic Settings (env vars, .env file loading)
│   ├── database.py          SQLAlchemy engine + SessionLocal + get_db + Base
│   ├── dependencies.py      get_current_actor (X-User-Id header mock auth)
│   ├── exceptions.py        VeloIQException hierarchy → HTTP mapping
│   ├── models/              9 SQLAlchemy 2.x ORM models
│   ├── schemas/             Pydantic v2 schemas (Base/Create/Update/Read per entity)
│   ├── routers/             8 FastAPI routers under /api/v1/
│   ├── services/            Mutation services with audit enforcement
│   ├── ports/               RESERVED — Phase B-D hexagonal ports
│   └── stubs/               RESERVED — Phase B-D test doubles
├── alembic/                 Migration scripts
├── data_seeder/             Deterministic synthetic data generators
└── tests/                   pytest suite with transactional rollback isolation
```

## Resources & Endpoints

All endpoints live under `/api/v1/`.

| Resource | Methods | Purpose |
|---|---|---|
| `/standards` | GET list/detail, POST, PATCH | TÜV AC standards catalog |
| `/customers` | GET list/detail, POST, PATCH | Client companies |
| `/certificates` | GET list/detail, POST, PATCH | Issued certifications |
| `/escalations` | GET list/detail, PATCH | Sales escalations (status + assignee only) |
| `/matches` | GET list/detail | Fuzzy-match results (read-only — populated by Phase B) |
| `/assessments` | GET list/detail | TCC review decisions (read-only — POST arrives in Phase C) |
| `/notifications` | GET list/detail | Customer notifications (read-only — populated by Phase D) |
| `/audit` | GET list/detail | Immutable audit trail |

All mutations write a paired `audit_log` entry in the same transaction. The `audit_log` table has `REVOKE UPDATE, DELETE` applied — it is append-only at the database level (subject to production role configuration — see `docker-compose.yml` notes).

## Phase A — Scope

**IN scope:**
- Full CRUD for Customer, Standard, Certificate; PATCH for SalesEscalation
- Read-only endpoints for system-generated resources
- Application-level audit enforcement via `write_audit_entry()`
- Deterministic synthetic seeders (30 customers, 50 standards, 200 certificates, ~400 links, 30 matches, 30 assessments, 20 notifications, 5 escalations)
- 7 fuzzy-match test pairs embedded verbatim for Phase B ground-truth validation

**OUT of scope (future phases):**
- Normalization + fuzzy-match engine (Phase B)
- TCC decision workflow POST (Phase C)
- Notification dispatch + SLA enforcement + sales escalation logic (Phase D)
- Real authentication (currently mock `X-User-Id` header)
- Observability (structured logging, metrics, tracing)

## Testing

```bash
cd backend
source .venv/Scripts/activate
DATABASE_URL="postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq" \
TEST_DATABASE_URL="postgresql://veloiq:veloiq_dev_password@localhost:5434/veloiq_test" \
pytest -v --cov=app --cov=data_seeder
```

- 148 tests (models + schemas + services + routers + E2E smoke + seeders)
- Coverage threshold: 85% (currently 96.9%)
- Transactional rollback isolation — each test gets a clean DB state via rollback, no teardown code needed

## Configuration Reference

Environment variables (via `.env` file or process env):

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | *(required)* | Main database connection string |
| `TEST_DATABASE_URL` | `None` | Separate test database connection |
| `API_V1_PREFIX` | `/api/v1` | REST API prefix |
| `CORS_ORIGINS` | `["http://localhost:5173","http://localhost:3000"]` | Allowed origins (JSON array) |
| `FAKER_SEED` | `42` | Seeder determinism |

Copy `backend/.env.example` → `backend/.env` and customize.
