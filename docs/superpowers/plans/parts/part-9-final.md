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
