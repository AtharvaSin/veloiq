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
