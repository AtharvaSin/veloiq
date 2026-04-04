# VeloIQ POC Approach — Synthetic Data Demo Build

**Version:** 0.1  
**Author:** Atharva Singh (Zealogics Inc.)  
**Date:** 2026-04-04  
**Status:** Approved for internal POC execution  
**Audience:** Suneesh John (TUV POC), Sumedha (India SME), Abhilash (Zealogics Architect)

---

## 1. Purpose & Constraints

### What This Document Is
A concrete build plan for a **demo-grade, synthetic-data-powered VeloIQ POC** that walks through the full standards-automation pipeline end-to-end — from Natos ingestion to sales follow-up — without requiring a single real TUV system connection.

### Why Build a Synthetic POC Now
We have contract clearance from senior management but are blocked on critical discovery inputs from TUV (Natos API schema, SAP Core table structures, TCC taxonomy, legal sign-off requirements). Rather than waiting, we build a **fully functional demo** that:

1. **Proves the architecture works** — validates the 3-block pipeline design with realistic data flows.
2. **Gives Suneesh and Sumedha something tangible** — a clickable UI they can walk through, not a slide deck.
3. **Surfaces real questions** — seeing the system in action will accelerate the discovery conversation.
4. **De-risks the matching engine** — the fuzzy matching logic is the hardest technical problem; we can validate it now with synthetic standards data.
5. **Becomes the production codebase** — every stub has a clearly marked seam where the real integration plugs in later.

### What We Will NOT Build
- No SAP BTP integration (simulated via local REST APIs)
- No Camunda deployment (state machine in code, upgrade path to Camunda later)
- No real Natos connection (synthetic JSON payloads)
- No real transactional email dispatch (mock email service with logged outputs)
- No AI/ML features (Phase 2 scope — untouched)

---

## 2. Architecture for the POC

### Production Architecture (Target)
```
Natos API --> SAP BTP iFlow --> Python Matching --> Camunda BPMN --> SAP Event Mesh --> SendGrid --> SAP Sales Cloud
                                     |                  |                                  |
                                PostgreSQL        Expert UI (TCC)                   Sales Dashboard
```

### POC Architecture (What We Build)
```
Synthetic Natos    -->  FastAPI Backend  -->  Matching Engine  -->  Workflow State Machine  -->  Mock Notifier
(JSON generator)        (REST API)           (Python core)         (DB-driven states)           (logged events)
                             |                     |                       |                          |
                        PostgreSQL            PostgreSQL              Expert UI (TCC)          Sales Dashboard
                    (Standards Master)     (Match results +        (React frontend)         (React frontend)
                                            audit trail)
```

### Key Design Decision: Seam-Based Architecture
Every synthetic component is built behind a **clean interface** so it can be swapped for the real system without touching business logic:

| Synthetic Stub | Interface | Production Replacement |
|---|---|---|
| `NatosSimulator` | `StandardsIngestionPort` | SAP BTP iFlow + Natos API |
| `MockSAPCore` | `CertificateRegistryPort` | OData V2/V4 to SAP S/4HANA |
| `WorkflowStateMachine` | `WorkflowEnginePort` | Camunda BPMN |
| `MockEmailService` | `NotificationPort` | SendGrid/Mailjet transactional API |
| `MockSalesCloud` | `SalesEscalationPort` | SAP Sales Cloud API |

---

## 3. Synthetic Data Strategy

### 3.1 Standards Universe (Natos Simulator)

We generate a corpus of **50 synthetic standards** spanning realistic lifecycle stages:

| Stage | Code | Count | Example |
|---|---|---|---|
| Preliminary | 00 | 3 | PWI for upcoming battery safety standard |
| Preparatory | 10-20 | 5 | Working drafts in electrical equipment |
| Committee | 30 | 5 | Committee drafts for machinery safety |
| Enquiry | 40 | 5 | DIS published for environmental management |
| Approval | 50 | 5 | FDIS in ballot for quality management |
| Publication | 60 | 15 | Active published standards (ISO 9001, 14001, etc.) |
| Review | 90 | 7 | Systematic review cycle — reconfirm, amend, or withdraw |
| Withdrawal | 95 | 5 | Withdrawn standards requiring immediate action |

Each synthetic standard includes:
- `ac_code` (Document Identifier, e.g., `ISO 9001:2015`)
- `status` (ISO lifecycle stage code)
- `replaced_by` (successor mapping, if applicable)
- `title`, `committee`, `ics_code` (metadata)
- `publication_date`, `review_date`

### 3.2 SAP Core Mock Data (Certificate Registry)

We generate **200 synthetic certificate records** deliberately formatted differently from the Natos data to exercise the matching engine:

**Fuzzy Matching Test Pairs:**

| Natos Record | SAP Mock Record | Challenge Type |
|---|---|---|
| `ISO 9001:2015` | `DIN EN ISO 9001:2015-11` | National prefix + date variant |
| `ISO 14001:2015` | `BS EN ISO 14001:2015` | British prefix |
| `IEC 62368-1:2023` | `EN IEC 62368-1:2023/AC:2024` | Amendment suffix |
| `ISO 1234:1998` | `ANSI ABC 331:1999/ISO 1234:1998` | Dual numbering |
| `ISO 14001` | `ISO 1401` | Character-level typo |
| `ISO 45001:2018` | `GB/T 45001-2020` | Chinese national adoption |
| `IEC 61000-4-2:2008` | `DIN EN 61000-4-2 VDE 0847-4-2:2010-04` | German VDE overlay |

**Customer/Certificate Distribution:**
- **30 synthetic customers** across 5 jurisdictions (Germany, China, India, USA, UK)
- **200 certificates** (active, expired, suspended) with realistic distribution
- Each certificate links to 1-3 standards and 1 customer
- Customer data includes: company name, country, sales area, language, contact email
- Follows SAP naming conventions: `KNA1` (customer master), `MARA`/`MARC` (materials), simulated `QVEK`-style certificate-to-standard links

### 3.3 TCC Expert Decision History

We pre-seed **30 historical decisions** to demonstrate audit trail and provide context for the TCC Expert UI:
- 10 auto-matched (score > 0.95) — logged as system decisions
- 15 expert-reviewed (score 0.70-0.95) — with reason codes like "No technical change", "New mandatory safety test", "Administrative amendment only"
- 5 rejected/escalated (score < 0.70) — flagged for master data steward

### 3.4 Notification History

Pre-seed **20 notification records** showing:
- Emails sent with delivery/open/click timestamps
- 3 cases where SLA breach triggers sales escalation
- Multi-language templates (EN, DE, ZH) demonstrated

---

## 4. Technology Stack (POC)

| Layer | Technology | Why This Choice |
|---|---|---|
| **Backend API** | FastAPI (Python 3.12) | Matches production Python stack; async; auto-generated OpenAPI docs |
| **Database** | PostgreSQL 16 | Same as production Standards Master; supports full-text search; audit trail |
| **Matching Engine** | Python (`rapidfuzz`, `regex`) | `rapidfuzz` is a faster C-extension drop-in for `fuzzywuzzy`; same algorithms |
| **Workflow** | DB-driven state machine | Lightweight; clear upgrade path to Camunda; states stored in PostgreSQL |
| **Frontend** | React 18 + TypeScript + Vite | Fast dev cycle; component library reusable in production |
| **UI Components** | shadcn/ui + Tailwind CSS | Professional look out of the box; accessible; customizable |
| **Data Seeding** | Python scripts + Faker | Reproducible synthetic data generation |
| **Dev Environment** | Docker Compose | One command to spin up backend + DB + frontend |

---

## 5. Build Phases (Iterative, Demo-able at Each Phase)

### Phase A: Foundation (Days 1-3)
**Goal:** Backend scaffold + database + synthetic data seeded. API returns data.

**Deliverables:**
1. Project scaffolding (monorepo: `/backend`, `/frontend`, `/data-seeder`, `/docs`)
2. PostgreSQL schema design:
   - `standards` — the Standards Master (Natos-sourced)
   - `certificates` — certificate records (SAP-sourced)
   - `customers` — customer master (SAP-sourced)
   - `cert_standard_links` — certificate-to-standard mappings
   - `match_results` — fuzzy matching output with confidence scores
   - `assessments` — TCC expert decisions with reason codes
   - `notifications` — email dispatch log with delivery events
   - `audit_log` — immutable append-only audit trail
   - `sales_escalations` — SLA breach escalation records
3. Data seeder script that generates all synthetic data
4. FastAPI backend with CRUD endpoints for all entities
5. Docker Compose: `postgres` + `backend` services

**Demo checkpoint:** API explorer (Swagger UI) showing all endpoints returning realistic data.

### Phase B: Matching Engine (Days 4-6)
**Goal:** The core brain — ingest a Natos update and match it against the certificate registry.

**Deliverables:**
1. `NatosSimulator` — generates standards update events (new, amended, withdrawn, superseded)
2. Normalization pipeline:
   - Whitespace + case stripping
   - Punctuation standardization
   - Prefix decomposition (DIN, EN, BS, GB, ANSI, VDE, etc.)
   - Version extraction (year, month separators)
3. Blocking + indexing engine (sorted neighborhood on base document number)
4. Similarity scoring: Levenshtein distance + Jaro-Winkler + token set ratio
5. Three-tier confidence routing:
   - `> 0.95` → Auto-Match (queue for TCC sampling)
   - `0.70 - 0.95` → Expert Review (route to TCC UI)
   - `< 0.70` → Manual Triage (flag for master data steward)
6. Matching results persisted with full audit trail
7. API endpoint: `POST /api/v1/ingest` — accepts a Natos event, runs the pipeline, returns match results
8. API endpoint: `GET /api/v1/matches?status=pending_review` — returns queue for TCC

**Demo checkpoint:** Trigger a synthetic Natos event → watch it normalize, match, and route correctly. Show match scores and explain why "DIN EN ISO 9001:2015-11" matched "ISO 9001:2015" at 0.97.

### Phase C: TCC Expert UI (Days 7-10)
**Goal:** The human-in-the-loop dashboard where experts review, classify, and sign off.

**Deliverables:**
1. **Dashboard Overview** — queue of pending assessments with priority, SLA timer, risk indicator
2. **Assessment Detail View:**
   - Side-by-side standards diff (old standard vs. new/replacement)
   - Matched confidence score with visual indicator
   - Impacted certificates list with customer names and risk scores
   - Historical decisions for similar standards (consistency check)
3. **Decision Panel:**
   - Impact classification dropdown: `No Change`, `Administrative`, `Minor Technical`, `Major Technical`, `Safety Critical`
   - Action required: `Reconfirm`, `Re-test Required`, `Certificate Suspension`, `Certificate Withdrawal`
   - Mandatory reason code + free-text notes
   - "Approve" button (writes immutable audit record)
4. **Audit Trail Viewer** — chronological log of all system and human decisions
5. API endpoints for assessment CRUD, decision submission, audit retrieval

**Demo checkpoint:** Walk Suneesh through reviewing a matched standard, making a decision, and seeing the audit trail update in real-time.

### Phase D: Notifications & Sales Escalation (Days 11-13)
**Goal:** When an expert approves, notifications fire and sales sees the pipeline.

**Deliverables:**
1. **Event trigger:** Expert "Approve" click fires a notification event
2. **Template engine:** Multi-language compliance notification templates (EN, DE, ZH)
3. **Mock email service:** Generates realistic email HTML, logs to DB instead of sending
4. **Notification tracker:** Shows delivery status, open/click simulation, proof of acknowledgment
5. **Sales Dashboard:**
   - Pipeline view: all notifications grouped by customer
   - SLA tracker: visual countdown per notification (configurable: 7/14/30 days)
   - Escalation queue: unacknowledged notifications past SLA → auto-generated leads
   - Customer 360 view: all certificates, standards, notifications, decisions for one customer
6. **Sales escalation logic:** Time-based SLA check → generate mock SAP Sales Cloud opportunity

**Demo checkpoint:** Approve an assessment → watch notification fire → simulate customer non-response → see sales escalation create a lead.

### Phase E: Polish & Integration Seams (Days 14-15)
**Goal:** End-to-end walkthrough ready for stakeholder demo.

**Deliverables:**
1. **Landing dashboard:** System health, processing metrics, SLA compliance rates
2. **End-to-end demo script:** Pre-configured scenario that walks through all 3 blocks
3. **Integration seam documentation:** For each stub, document:
   - What it simulates
   - What the real integration requires
   - Exact API contract expected
   - Open questions for TUV
4. **Data reset script:** One-command reset to demo-ready state
5. **Docker Compose full stack:** `postgres` + `backend` + `frontend` — one command launch

---

## 6. Database Schema (High-Level)

```
standards
├── id (UUID)
├── ac_code (VARCHAR) — Document identifier from Natos
├── title (TEXT)
├── status (VARCHAR) — ISO lifecycle stage (00-95)
├── replaced_by (VARCHAR) — Successor standard ac_code
├── normalized_code (VARCHAR) — Processed by normalization pipeline
├── base_number (VARCHAR) — Core number extracted (e.g., "9001")
├── version_year (INT)
├── committee (VARCHAR)
├── ics_code (VARCHAR)
├── source_payload (JSONB) — Raw Natos event preserved
├── ingested_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

certificates
├── id (UUID)
├── certificate_number (VARCHAR)
├── customer_id (UUID → customers)
├── product_description (TEXT)
├── status (VARCHAR) — active, expired, suspended
├── issue_date (DATE)
├── expiry_date (DATE)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)

cert_standard_links
├── id (UUID)
├── certificate_id (UUID → certificates)
├── standard_ref (VARCHAR) — As stored in SAP (messy format)
├── normalized_ref (VARCHAR) — Processed
├── base_number (VARCHAR)
└── linked_at (TIMESTAMPTZ)

customers
├── id (UUID)
├── customer_number (VARCHAR) — SAP KNA1 equivalent
├── company_name (VARCHAR)
├── country (VARCHAR)
├── sales_area (VARCHAR)
├── language (VARCHAR) — notification template language
├── contact_email (VARCHAR)
├── contact_name (VARCHAR)
└── created_at (TIMESTAMPTZ)

match_results
├── id (UUID)
├── natos_standard_id (UUID → standards)
├── cert_link_id (UUID → cert_standard_links)
├── algorithm (VARCHAR) — levenshtein, jaro_winkler, token_set
├── similarity_score (DECIMAL)
├── composite_score (DECIMAL) — weighted final score
├── confidence_tier (VARCHAR) — auto_match, expert_review, manual_triage
├── status (VARCHAR) — pending, reviewed, auto_approved
├── matched_at (TIMESTAMPTZ)
└── reviewed_at (TIMESTAMPTZ)

assessments
├── id (UUID)
├── match_result_id (UUID → match_results)
├── assessor_id (VARCHAR) — expert user ID
├── impact_classification (VARCHAR) — no_change, administrative, minor, major, safety_critical
├── action_required (VARCHAR) — reconfirm, retest, suspend, withdraw
├── reason_code (VARCHAR) — structured dropdown value
├── notes (TEXT)
├── decision (VARCHAR) — approved, rejected, escalated
├── decided_at (TIMESTAMPTZ)
└── signature_hash (VARCHAR) — simulated digital signature

notifications
├── id (UUID)
├── assessment_id (UUID → assessments)
├── customer_id (UUID → customers)
├── template_language (VARCHAR)
├── subject (TEXT)
├── body_html (TEXT)
├── status (VARCHAR) — queued, sent, delivered, opened, clicked, bounced
├── sent_at (TIMESTAMPTZ)
├── delivered_at (TIMESTAMPTZ)
├── opened_at (TIMESTAMPTZ)
├── clicked_at (TIMESTAMPTZ)
└── sla_deadline (TIMESTAMPTZ)

sales_escalations
├── id (UUID)
├── notification_id (UUID → notifications)
├── customer_id (UUID → customers)
├── escalation_reason (VARCHAR) — sla_breach, high_priority_unacknowledged
├── opportunity_value (DECIMAL)
├── assigned_to (VARCHAR)
├── status (VARCHAR) — open, contacted, resolved
├── created_at (TIMESTAMPTZ)
└── resolved_at (TIMESTAMPTZ)

audit_log (APPEND-ONLY)
├── id (UUID)
├── entity_type (VARCHAR) — standard, match, assessment, notification, escalation
├── entity_id (UUID)
├── action (VARCHAR) — created, updated, approved, rejected, sent, escalated
├── actor (VARCHAR) — system or user ID
├── details (JSONB) — full change payload
├── ip_address (VARCHAR)
└── created_at (TIMESTAMPTZ)
```

---

## 7. Frontend Pages

| Page | Purpose | Block |
|---|---|---|
| **System Dashboard** | Pipeline health, processing metrics, SLA compliance rates, volume trends | All |
| **Ingestion Monitor** | Live feed of Natos events, normalization status, queue depths | Block 1 |
| **Match Results** | Table of all matches with scores, filters by confidence tier and status | Block 1 |
| **Match Detail** | Side-by-side comparison, algorithm breakdown, score explanation | Block 1 |
| **TCC Queue** | Expert review queue sorted by priority, SLA urgency, risk level | Block 2 |
| **Assessment Workspace** | Full assessment view: diff, impacts, history, decision panel | Block 2 |
| **Audit Trail** | Chronological, filterable log of all system and human actions | Block 2 |
| **Notification Center** | All dispatched notifications, delivery status, proof of acknowledgment | Block 3 |
| **Sales Pipeline** | Escalated leads, customer follow-up status, opportunity tracking | Block 3 |
| **Customer 360** | All certificates, standards, notifications, and decisions for one customer | Block 3 |

---

## 8. What the Demo Proves to Suneesh & Sumedha

### The Walkthrough Scenario
> "A safety standard (IEC 62368-1) is superseded. Here's what VeloIQ does automatically."

1. **Natos event arrives** — IEC 62368-1:2018 is superseded by IEC 62368-1:2023
2. **Normalization runs** — strips prefixes, extracts versions
3. **Matching engine fires** — finds 12 certificates across 4 customers linked to the old standard (some stored as "EN IEC 62368-1:2018", others as "DIN EN 62368-1 VDE 0868-1:2021-01")
4. **Confidence routing** — 8 auto-matched (>0.95), 3 expert review (0.82-0.91), 1 manual triage (0.64)
5. **TCC expert reviews** the 3 ambiguous matches, classifies impact as "Major Technical — Re-test Required"
6. **Notifications fire** — 12 compliance alerts in 3 languages (EN, DE, ZH) dispatched
7. **SLA tracking begins** — 14-day countdown per notification
8. **One customer doesn't respond** — after SLA breach, sales escalation auto-creates a lead
9. **Full audit trail** — every step logged with timestamps, actors, and decision rationale

### Questions This Demo Will Provoke (Intentionally)
- "The matching looks right, but our actual SAP data uses Z-tables, not QVEK — here's the real schema..." *(unlocks Block 1 integration)*
- "The TCC classification categories aren't quite right — here's how we actually categorize..." *(refines Block 2 taxonomy)*
- "The SLA should be 21 days for China, not 14 — and we need regional routing..." *(refines Block 3 rules)*
- "Can the system also handle [X]?" *(scope expansion conversations anchored in reality, not theory)*

---

## 9. Stub-to-Production Upgrade Path

| Stub | What It Does Now | To Go Production | Estimated Effort |
|---|---|---|---|
| `NatosSimulator` | Generates JSON events from synthetic corpus | Replace with SAP BTP iFlow consuming Natos REST/CSV | 2-3 weeks (pending schema) |
| `MockSAPCore` | PostgreSQL tables mimicking MARA/KNA1/QVEK | Replace with OData V2/V4 calls via SAP BTP | 3-4 weeks (pending Z-table mapping) |
| `WorkflowStateMachine` | DB columns tracking assessment state | Replace with Camunda BPMN deployment | 2 weeks |
| `MockEmailService` | Logs HTML emails to DB | Replace with SendGrid/Mailjet API + webhook listeners | 1 week |
| `MockSalesCloud` | Creates escalation records in PostgreSQL | Replace with SAP Sales Cloud API for opportunity creation | 1-2 weeks |
| Auth (mock users) | Hardcoded demo users | Replace with TUV SSO / OAuth 2.0 | 1-2 weeks |

**Total estimated lift from POC to production-connected Phase 1:** 10-14 weeks (heavily dependent on TUV discovery inputs).

---

## 10. Repository Structure

```
veloIQ/
├── docs/                          # This document and future specs
│   ├── POC_APPROACH.md            # You're reading this
│   ├── DEMO_SCRIPT.md             # Step-by-step demo walkthrough (Phase E)
│   └── INTEGRATION_SEAMS.md       # Stub-to-production mapping (Phase E)
│
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI application entry
│   │   ├── config.py              # Environment config
│   │   ├── database.py            # SQLAlchemy + async engine
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── standard.py
│   │   │   ├── certificate.py
│   │   │   ├── customer.py
│   │   │   ├── match_result.py
│   │   │   ├── assessment.py
│   │   │   ├── notification.py
│   │   │   ├── sales_escalation.py
│   │   │   └── audit_log.py
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── routers/               # API route handlers
│   │   │   ├── ingestion.py       # POST /ingest, GET /standards
│   │   │   ├── matching.py        # GET /matches, GET /matches/:id
│   │   │   ├── assessments.py     # GET/POST /assessments
│   │   │   ├── notifications.py   # GET /notifications
│   │   │   ├── escalations.py     # GET /escalations
│   │   │   ├── customers.py       # GET /customers, GET /customers/:id/360
│   │   │   └── audit.py           # GET /audit
│   │   ├── services/              # Business logic
│   │   │   ├── normalizer.py      # String normalization pipeline
│   │   │   ├── matcher.py         # Fuzzy matching engine
│   │   │   ├── workflow.py        # State machine (WorkflowEnginePort)
│   │   │   ├── notifier.py        # Mock notification service
│   │   │   └── escalation.py      # SLA check + escalation logic
│   │   ├── ports/                 # Interface definitions (ABCs)
│   │   │   ├── ingestion_port.py
│   │   │   ├── certificate_registry_port.py
│   │   │   ├── workflow_engine_port.py
│   │   │   ├── notification_port.py
│   │   │   └── sales_escalation_port.py
│   │   └── stubs/                 # Synthetic implementations
│   │       ├── natos_simulator.py
│   │       ├── mock_sap_core.py
│   │       ├── mock_email_service.py
│   │       └── mock_sales_cloud.py
│   ├── alembic/                   # Database migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                # shadcn/ui components
│   │   │   ├── layout/            # Shell, sidebar, header
│   │   │   ├── dashboard/         # System dashboard widgets
│   │   │   ├── ingestion/         # Ingestion monitor components
│   │   │   ├── matching/          # Match results + detail views
│   │   │   ├── tcc/               # Expert queue + assessment workspace
│   │   │   ├── notifications/     # Notification center
│   │   │   └── sales/             # Sales pipeline + customer 360
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── data-seeder/
│   ├── seed_standards.py          # 50 synthetic Natos standards
│   ├── seed_customers.py          # 30 customers across 5 jurisdictions
│   ├── seed_certificates.py       # 200 certificates with messy standard refs
│   ├── seed_history.py            # 30 historical decisions + 20 notifications
│   ├── seed_all.py                # Master seeder
│   └── faker_providers/           # Custom Faker providers for TIC domain
│       ├── standards_provider.py
│       └── certificates_provider.py
│
├── docker-compose.yml             # Full stack: postgres + backend + frontend
├── .env.example
├── .gitignore
└── README.md
```

---

## 11. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Synthetic data doesn't match real TUV patterns | Demo feels unrealistic | Use NotebookLM research + Sumedha's input to calibrate; design data seeder to be re-runnable with new patterns |
| Matching engine thresholds wrong for real data | Confidence routing miscalibrated | Thresholds are configurable; expose in admin UI; tune with real data later |
| TUV discovery takes longer than expected | POC sits idle | POC is self-contained; can demo independently; stubs document exact questions TUV needs to answer |
| Scope creep during demo conversations | Timeline slips | Phase E includes clear integration seam docs that separate "POC scope" from "production scope" |
| Sumedha's SAP matching logic doesn't align with our approach | Rework matching engine | Build matcher behind `CertificateRegistryPort` interface; core algorithms are reusable regardless of SAP schema |

---

## 12. Success Criteria

The POC is successful if, after the demo, Suneesh and Sumedha can:

1. **See** the end-to-end data flow from standards ingestion to sales escalation
2. **Interact** with the TCC Expert UI and make a classification decision
3. **Understand** where their real systems plug in (clearly marked stubs)
4. **Provide** concrete answers to the open discovery questions (provoked by seeing the system)
5. **Agree** on next steps for Phase 1 production build with real integrations

---

*This document is a living artifact. It will be updated as discovery inputs are received from TUV Rheinland.*
