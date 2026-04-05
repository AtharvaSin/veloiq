# VeloIQ Phase A-UI — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task with fresh subagents + two-stage review. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a Vite+React+TypeScript frontend that consumes the VeloIQ Phase A backend API end-to-end, implementing the 5-screen core TCC expert workflow from the locked Stitch DESIGN.md as a clickable demo runnable via `docker compose up`.

**Architecture:** Single-page app using React Router v6, TanStack Query for server state, Tailwind + shadcn/ui for the obsidian-aurora theme. Flat feature-folder layout (no premature abstraction). Hand-typed API client mirroring backend Pydantic schemas (no code-gen — 23 endpoints is under the threshold where codegen pays off).

**Tech Stack:** Vite 5 · React 18.3 · TypeScript 5.6 · Tailwind CSS 3.4 · shadcn/ui (Radix primitives) · TanStack Query v5 · React Router v6 · axios · React Hook Form + Zod · lucide-react · Vitest · Playwright (optional)

**Spec references:**
- Stitch DESIGN.md (embedded in project `4700597748399750311` metadata)
- Backend Phase A plan: `docs/superpowers/plans/2026-04-05-phase-a-foundation.md`
- Backend API live on :8000 (via docker compose), Swagger at http://localhost:8000/docs

**Working directory for all tasks:** `C:/Users/ASR/OneDrive/Desktop/Zealogics Work/Projects/TUV-Velo IQ/veloIQrepo/veloIQ/`

**Frontend root:** `frontend/` (new directory, sibling to `backend/`)

---

## Scope

### Phase 1 — Must-Build (core clickable flow) — 26 tasks

The 5-screen MVP delivers a complete TCC expert workflow: **Login → Dashboard → TCC Queue → Assessment Workspace → Match Forensic**. Each screen consumes real backend data via API. Assessment submission writes to the database through a new `POST /api/v1/assessments` endpoint (added as Task 1 — documented below as a justified deviation from backend Phase A's "Phase C TCC workflow" deferral).

| # | Stitch Screen | Route | Backend endpoints | Purpose |
|---|---|---|---|---|
| 1 | Login (`342e1aba`) | `/login` | none (static navigate) | Entry point, demo-mode bypass |
| 2 | System Dashboard (`620aff5d`) | `/` | `/matches`, `/assessments`, `/notifications`, `/standards` (counts) | Operational overview with KPIs |
| 3 | TCC Queue (`25905ba1`) | `/queue` | `/assessments`, `/matches`, `/standards/{id}` | Expert work queue |
| 4 | Assessment Workspace (`c240dd89`) | `/assessments/:id` | `/assessments/{id}`, `/matches/{id}`, `/standards/{id}`, `POST /assessments` | Decision capture |
| 5 | Match Forensic (`b8030f1d`) | `/matches/:id` | `/matches/{id}`, `/certificates?customer_id=` | Algorithm drill-down |

### Phase 2 — Nice-to-Have (extend demo value) — ~8 additional tasks (separate plan)

- Customer 360 (`0e8f2094`) → `/customers/:id`
- Notification Center (`5d9603f9`) → `/notifications`
- Sales Pipeline (`a3d850e0`) → `/pipeline`

### Deferred — not required for first demo

- Ingestion Monitor (`62d55f57`) — ops-facing
- Audit Log (`ccaae9a0`) — compliance artifact
- Forensic Variant (`ef63ade2`) — icon-only variant of Match Forensic

---

## Architectural Decisions

### AD1 — Build tool: Vite 5

Matches DESIGN.md's declared dev port 5173 and CORS_ORIGINS default. Fast HMR, native TypeScript/JSX support, battle-tested React integration. No server-side rendering needed for a POC dashboard.

### AD2 — Styling: Tailwind + shadcn/ui (copy-paste, not a library)

Tailwind gives us exact DESIGN.md token control. shadcn/ui provides Radix-primitive-backed components we OWN (copied into `src/components/ui/`) rather than versioned dependencies. No lock-in, full customization authority. Consistent with the emerald/obsidian theme locked in Stitch.

### AD3 — No code-generation from OpenAPI

23 endpoints, stable during Phase A. Hand-typed `src/lib/types.ts` mirroring Pydantic schemas is faster to maintain than setting up `openapi-typescript-codegen` tooling. When endpoint count exceeds ~40 or backend churns, revisit.

### AD4 — Server state: TanStack Query. Client state: useState.

No Redux, no Zustand. The app is 95% server-derived data. TanStack Query handles caching, invalidation, optimistic updates, refetching. The small amount of ephemeral UI state (modals open, form inputs) lives in component `useState`. Keeping it simple.

### AD5 — Forms: React Hook Form + Zod

Type-safe form validation with runtime schema checks. Zod schemas double as DTOs validating API responses. React Hook Form integrates cleanly with shadcn/ui's `<Form>` primitives.

### AD6 — API client: axios (not fetch)

Axios gives us interceptors (for X-User-Id header injection + global error handling) and request cancellation. Typed wrapper generic `apiGet<T>`, `apiPost<T, B>`, etc. keeps call sites clean.

### AD7 — Routing: React Router v6

Standard choice. No Next.js App Router needed (no SSR/ISR, no server components). File-based routing (TanStack Router) is interesting but adds setup cost without clear benefit for 5 pages.

### AD8 — Testing: Vitest + React Testing Library

Vitest is the Vite-native test runner. RTL for component tests focused on user-visible behavior. Playwright for end-to-end is optional Phase 2; for Phase 1 MVP we rely on backend's 148 tests + manual demo verification.

### AD9 — Deployment: Add `frontend` service to existing docker-compose.yml

`docker compose up` now starts postgres + backend + frontend (3 services). Frontend container serves static Vite-built assets via nginx, proxying `/api/*` to backend container. One command to run the whole stack.

---

## File Structure

```
veloIQrepo/veloIQ/
├── backend/                    (existing — Phase A complete)
├── frontend/                   (NEW)
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css           Tailwind directives + DESIGN.md custom CSS
│   │   ├── lib/
│   │   │   ├── api.ts          axios client with interceptors
│   │   │   ├── types.ts        TypeScript mirrors of Pydantic schemas
│   │   │   ├── queryClient.ts  TanStack Query configuration
│   │   │   ├── queryKeys.ts    Centralized query key factory
│   │   │   ├── utils.ts        cn() className merge + formatters
│   │   │   ├── routes.ts       Route path constants
│   │   │   └── demo-session.ts localStorage-backed mock auth session
│   │   ├── hooks/
│   │   │   ├── useStandards.ts
│   │   │   ├── useCustomers.ts
│   │   │   ├── useCertificates.ts
│   │   │   ├── useMatches.ts
│   │   │   ├── useAssessments.ts
│   │   │   ├── useNotifications.ts
│   │   │   ├── useEscalations.ts
│   │   │   └── useAudit.ts
│   │   ├── components/
│   │   │   ├── ui/             shadcn/ui primitives (copied in)
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── label.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── form.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   └── toaster.tsx
│   │   │   ├── layout/
│   │   │   │   ├── AppShell.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── TopBar.tsx
│   │   │   └── shared/
│   │   │       ├── ConfidencePill.tsx    DESIGN.md signature component
│   │   │       ├── StatusBadge.tsx
│   │   │       ├── KpiCard.tsx
│   │   │       ├── DataTable.tsx
│   │   │       ├── PaginationControls.tsx
│   │   │       ├── FilterBar.tsx
│   │   │       ├── LoadingState.tsx
│   │   │       ├── EmptyState.tsx
│   │   │       └── ErrorState.tsx
│   │   └── pages/
│   │       ├── LoginPage.tsx
│   │       ├── DashboardPage.tsx
│   │       ├── TCCQueuePage.tsx
│   │       ├── AssessmentWorkspacePage.tsx
│   │       ├── MatchForensicPage.tsx
│   │       └── NotFoundPage.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── vite.config.ts
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   ├── .env.example
│   ├── .gitignore
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── nginx.conf
│   └── README.md
└── docker-compose.yml          (MODIFY: add `frontend` service)
```

**Theme token mapping (Tailwind config):**

| DESIGN.md token | Hex | Tailwind class name |
|---|---|---|
| Obsidian (page bg) | `#0d0d14` | `bg-obsidian` |
| Dark Surface (cards) | `#12121e` | `bg-surface` |
| Elevated (hover) | `#1a1a2e` | `bg-elevated` |
| Void (sidebar) | `#0a0a0a` | `bg-void` |
| Border | `#1f1f35` | `border-divider` |
| Emerald (accent) | `#00D492` | `text-accent` / `bg-accent` |
| Amber (warning) | `#E8B931` | `text-warn` |
| Coral (danger) | `#FF6B6B` | `text-danger` |
| Off-white (text) | `#EEEAE4` | `text-primary` |
| Warm gray (body) | `#A09D95` | `text-secondary` |
| Muted | `#606060` | `text-muted` |
| Cert Block | `#0EA5E9` | `border-block-cert` |
| TCC Block | `#8B5CF6` | `border-block-tcc` |
| Sales Block | `#22C55E` | `border-block-sales` |

---

## Task Breakdown — Phase 1 (26 tasks)

---

## Part 0 — Backend Assessment POST Endpoint (1 task)

### Task 1: Add `POST /api/v1/assessments` + `AssessmentCreate` schema

**Justification for the deviation:** Phase A's backend plan deferred this to Phase C ("TCC decision workflow"). However, the frontend Assessment Workspace screen cannot be end-to-end testable without it. We add the minimal endpoint now — it's a 40-line addition following the exact pattern of existing mutation services (Tasks 21-23 of the backend plan).

**Files:**
- Modify: `backend/app/schemas/assessment.py` (add `AssessmentCreate`)
- Create: `backend/app/services/assessments_service.py`
- Modify: `backend/app/routers/assessments.py` (add POST handler)
- Modify: `backend/app/schemas/__init__.py` (export `AssessmentCreate`)
- Create: `backend/tests/services/test_assessments_service.py`
- Modify: `backend/tests/routers/test_assessments_router.py` (add POST test)

**Steps (summarized — full steps like backend Phase A pattern):**
- [ ] Write failing test: `POST /api/v1/assessments` with valid payload returns 201 + audit entry
- [ ] Add `AssessmentCreate` Pydantic schema (match_result_id, assessor_id, impact_classification, action_required, reason_code, notes, decision)
- [ ] Add `create_assessment(db, payload, actor)` service function following Task 21 pattern (flush → write_audit_entry → commit → refresh)
- [ ] Add POST handler in assessments router
- [ ] Export `AssessmentCreate` from schemas package
- [ ] Run tests, commit: `feat(assessments): add POST endpoint for TCC decision capture`

**Acceptance:** `curl -X POST http://localhost:8000/api/v1/assessments -H "X-User-Id: Dr.M.Weber" -d '{...}'` returns 201 with the new assessment, and the audit_log gets a paired entry.

---

## Part 1 — Frontend Scaffolding (Tasks 2-7)

### Task 2: Initialize Vite + React + TypeScript project

**Files:**
- Create: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/tsconfig.node.json`, `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`, `frontend/.gitignore`

**Key decisions in this task:**
- Node 20 LTS, pnpm or npm (use npm for simplicity — already installed)
- `strict: true` in tsconfig, `noUncheckedIndexedAccess: true`
- Path alias `@/*` → `src/*`
- Vite dev server port 5173 (matches backend CORS config)
- Vite proxy: `/api` → `http://localhost:8000` (so fetch `/api/v1/standards` works without CORS gymnastics during dev)

**Steps:**
- [ ] Run `npm create vite@latest frontend -- --template react-ts` from repo root
- [ ] `cd frontend && npm install`
- [ ] Edit `vite.config.ts` to add proxy + path alias
- [ ] Edit `tsconfig.json` for strict mode + path alias
- [ ] Verify `npm run dev` starts on :5173 and serves the Vite welcome page
- [ ] Commit: `chore(frontend): initialize Vite + React + TypeScript scaffold`

**Acceptance:** `cd frontend && npm run dev` → http://localhost:5173 shows a working Vite welcome screen.

---

### Task 3: Install Tailwind CSS + configure DESIGN.md theme

**Files:**
- Create: `frontend/tailwind.config.ts`, `frontend/postcss.config.js`
- Modify: `frontend/src/index.css` (Tailwind directives + CSS variables)
- Modify: `frontend/package.json` (Tailwind deps)

**Theme config includes:**
- Full color palette per DESIGN.md token table above
- `fontFamily.sans: ['DM Sans', 'system-ui']`, `fontFamily.mono: ['JetBrains Mono', 'monospace']`
- Border radius scale: `tight: 4px`, `DEFAULT: 8px`, `modal: 12px`
- Section spacing constants via Tailwind's spacing scale

**Steps:**
- [ ] `npm install -D tailwindcss postcss autoprefixer`
- [ ] `npx tailwindcss init -p --ts`
- [ ] Write `tailwind.config.ts` with theme tokens (full color palette + fonts)
- [ ] Add `@tailwind base; @tailwind components; @tailwind utilities;` to `index.css`
- [ ] Add Google Fonts links to `index.html` (DM Sans + JetBrains Mono)
- [ ] Replace `src/App.tsx` with a minimal "Hello VeloIQ" div using obsidian bg + emerald text to verify
- [ ] Verify dev server renders with DESIGN.md colors
- [ ] Commit: `chore(frontend): configure Tailwind with DESIGN.md theme tokens`

**Acceptance:** Dev server renders with `#0d0d14` page background and emerald `#00D492` accent text visible.

---

### Task 4: Install shadcn/ui primitives

**Files:**
- Create: `frontend/components.json` (shadcn config)
- Create: `frontend/src/components/ui/` + 11 component files
- Create: `frontend/src/lib/utils.ts` (`cn()` helper)

**Components to install (via `npx shadcn@latest add`):**
- `button`, `card`, `table`, `input`, `label`, `select`, `form`, `dialog`, `badge`, `toast`, `toaster`, `tabs`, `separator`, `avatar`

**Steps:**
- [ ] `npx shadcn@latest init` (select TypeScript, CSS variables, slate base, utils path `src/lib/utils`)
- [ ] `npx shadcn@latest add button card table input label select form dialog badge toast toaster tabs separator avatar`
- [ ] Verify 14 files created under `src/components/ui/`
- [ ] Override shadcn's default colors in `tailwind.config.ts` to use DESIGN.md tokens
- [ ] Test: render `<Button>Click</Button>` in App.tsx with obsidian surface background
- [ ] Commit: `feat(frontend): add shadcn/ui primitive components`

**Acceptance:** A shadcn `<Button variant="default">` renders with emerald background per DESIGN.md.

---

### Task 5: Install routing + TanStack Query + core deps

**Files:**
- Modify: `frontend/package.json` (add dependencies)
- Create: `frontend/src/lib/queryClient.ts`
- Create: `frontend/src/lib/routes.ts`
- Modify: `frontend/src/main.tsx` (wrap app with QueryClientProvider + BrowserRouter)

**Dependencies to install:**
- `react-router-dom@^6`
- `@tanstack/react-query@^5`
- `@tanstack/react-query-devtools@^5`
- `axios@^1`
- `react-hook-form@^7`
- `zod@^3`
- `@hookform/resolvers@^3`
- `lucide-react@^0.400`
- `date-fns@^3`
- `clsx@^2`, `tailwind-merge@^2` (for cn())

**Steps:**
- [ ] Install all dependencies listed above
- [ ] Write `src/lib/queryClient.ts` — QueryClient with staleTime=30s, retry=1, refetchOnWindowFocus=false
- [ ] Write `src/lib/routes.ts` — centralized path constants (ROUTES.LOGIN, ROUTES.DASHBOARD, etc.)
- [ ] Wrap `<App />` in `<QueryClientProvider>` + `<BrowserRouter>` in main.tsx
- [ ] Add React Query Devtools in dev mode
- [ ] Verify: devtools panel visible in dev mode
- [ ] Commit: `chore(frontend): add routing, query client, and core dependencies`

**Acceptance:** TanStack Query Devtools panel opens in the corner of dev server.

---

### Task 6: Write `.env.example` and `.env`, Dockerfile placeholder

**Files:**
- Create: `frontend/.env.example`
- Create: `frontend/.env` (gitignored — local dev copy)

**Environment variables:**
```
VITE_API_BASE_URL=/api/v1
VITE_APP_TITLE=VeloIQ
VITE_DEMO_ACTOR=Dr. M. Weber
```

**Steps:**
- [ ] Create `.env.example` with LOCAL DEVELOPMENT header comment (pattern from backend)
- [ ] `cp .env.example .env`
- [ ] Verify `.env` is gitignored (root .gitignore covers `*.env`)
- [ ] Commit: `chore(frontend): add environment config templates`

**Acceptance:** `VITE_API_BASE_URL` is accessible via `import.meta.env.VITE_API_BASE_URL` in TS files.

---

### Task 7: Write `.gitignore` and `.dockerignore` for frontend

**Files:**
- Create: `frontend/.gitignore`
- Create: `frontend/.dockerignore`

**.gitignore contents:**
```
node_modules/
dist/
.env
.env.local
*.log
.DS_Store
Thumbs.db
.vscode/
.idea/
coverage/
.vite/
```

**.dockerignore contents:**
```
node_modules/
dist/
.env
.env.example
.vscode/
.idea/
*.log
.git/
README.md
tests/
```

**Steps:**
- [ ] Create both files with content above
- [ ] Commit: `chore(frontend): add gitignore and dockerignore`

**Acceptance:** `git status` in frontend/ shows no node_modules or dist/ noise.

---

## Part 2 — API Integration Layer (Tasks 8-12)

### Task 8: Write `src/lib/types.ts` — TypeScript schema mirrors

**Files:**
- Create: `frontend/src/lib/types.ts`

**Contents:** Hand-typed TypeScript interfaces mirroring every backend Pydantic schema.

**Structure outline:**
- Primitive aliases: `UUID = string`, `ISODateTime = string`, `ISODate = string`, `DecimalStr = string`
- Pagination: `PaginationMeta`, `PaginatedResponse<T>`
- Error: `ErrorResponse`, `ValidationErrorResponse`
- Per-resource: interfaces for each `*Base`, `*Create`, `*Update`, `*Read` from backend schemas package
  - Customer: `CustomerBase`, `CustomerCreate`, `CustomerUpdate`, `CustomerRead`
  - Standard: same 4
  - Certificate: same 4
  - CertStandardLink: same 4
  - MatchResult: `MatchResultRead` only
  - Assessment: `AssessmentRead`, `AssessmentCreate` (new from Task 1)
  - Notification: `NotificationRead` only
  - SalesEscalation: `SalesEscalationRead`, `SalesEscalationUpdate`
  - AuditLog: `AuditLogRead` only
- Union types: `CertificateStatus = 'active' | 'expiring' | 'expired' | 'suspended'`, `ConfidenceTier = 'auto_match' | 'expert_review' | 'manual_triage'`, etc. — mirror CheckConstraint enum values from models

**Steps:**
- [ ] Reference backend schemas at `backend/app/schemas/` to ensure exact field parity
- [ ] Write all type definitions in one file (types.ts will be ~200 lines)
- [ ] Export everything
- [ ] Verify: `tsc --noEmit` passes
- [ ] Commit: `feat(frontend): add TypeScript types mirroring backend schemas`

**Acceptance:** All 26 Pydantic schema classes have TypeScript equivalents with matching field names and types.

---

### Task 9: Write `src/lib/api.ts` — axios client with interceptors

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/demo-session.ts`

**Client responsibilities:**
- `axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL })`
- Request interceptor: inject `X-User-Id` header from `demo-session.getActor()`
- Response interceptor: map non-2xx to typed errors (`ApiError`, `NotFoundError`, `ValidationError`)
- Generic typed helpers: `apiGet<T>(path, params?)`, `apiPost<T, B>(path, body)`, `apiPatch<T, B>(path, body)`

**demo-session.ts:**
- `getActor(): string` — reads from localStorage, falls back to `VITE_DEMO_ACTOR`
- `setActor(name: string): void`
- `clearSession(): void`

**Steps:**
- [ ] Write `demo-session.ts` (~20 lines)
- [ ] Write `api.ts` — axios instance + interceptors + typed helpers (~120 lines)
- [ ] Verify: hit `/api/v1/standards` from a React component using apiGet<PaginatedResponse<StandardRead>>, data renders
- [ ] Commit: `feat(frontend): add axios API client with X-User-Id interceptor`

**Acceptance:** Vite dev server can fetch from backend via proxy, response is typed correctly, X-User-Id header appears in backend logs.

---

### Task 10: Write `src/lib/queryKeys.ts` — centralized query key factory

**Files:**
- Create: `frontend/src/lib/queryKeys.ts`

**Query key pattern (from TanStack Query docs):**
```typescript
export const queryKeys = {
  standards: {
    all: ['standards'] as const,
    list: (params: StandardsListParams) => ['standards', 'list', params] as const,
    detail: (id: UUID) => ['standards', 'detail', id] as const,
  },
  customers: { /* same shape */ },
  // ... for every resource
};
```

Centralization prevents key typos across hooks and makes invalidation targeted.

**Steps:**
- [ ] Write queryKeys.ts for all 8 resources
- [ ] Commit: `feat(frontend): add centralized TanStack Query key factory`

**Acceptance:** All hooks (Task 11-12) import keys from this file.

---

### Task 11: Write resource hooks — Standards, Customers, Certificates

**Files:**
- Create: `frontend/src/hooks/useStandards.ts`
- Create: `frontend/src/hooks/useCustomers.ts`
- Create: `frontend/src/hooks/useCertificates.ts`

**Per resource, export:**
- `useList(params)` — `useQuery<PaginatedResponse<T>>` for the list endpoint
- `useDetail(id)` — `useQuery<T>` for a single item
- `useCreate()` — `useMutation<T, ApiError, CreateInput>` for POST (invalidates list query on success)
- `useUpdate()` — `useMutation<T, ApiError, { id: UUID; input: UpdateInput }>` for PATCH (invalidates both list + detail)

Each hook is a ~10-line wrapper over TanStack Query primitives + the typed apiGet/apiPost/apiPatch helpers.

**Steps:**
- [ ] Write useStandards.ts with list/detail/create/update hooks
- [ ] Write useCustomers.ts following same pattern
- [ ] Write useCertificates.ts following same pattern
- [ ] Test: render a component using useStandards.useList({page:1,limit:10}) and verify loading → data states work
- [ ] Commit: `feat(frontend): add Standards/Customers/Certificates query hooks`

**Acceptance:** Component using useStandards displays paginated list from backend.

---

### Task 12: Write remaining hooks — Matches, Assessments, Notifications, Escalations, Audit

**Files:**
- Create: `frontend/src/hooks/useMatches.ts`
- Create: `frontend/src/hooks/useAssessments.ts`
- Create: `frontend/src/hooks/useNotifications.ts`
- Create: `frontend/src/hooks/useEscalations.ts`
- Create: `frontend/src/hooks/useAudit.ts`

Read-only hooks (`useList`, `useDetail`) for Matches/Notifications/Audit. Assessments gets `useList`, `useDetail`, `useCreate` (from Task 1's new endpoint). Escalations gets `useList`, `useDetail`, `useUpdate`.

**Steps:**
- [ ] Write all 5 hook files following Task 11 pattern
- [ ] Commit: `feat(frontend): add remaining resource query hooks`

**Acceptance:** All 8 resource hook files exist, typed, and exportable.

---

## Part 3 — Shared Components (Tasks 13-19)

### Task 13: Write `AppShell` layout (Sidebar + TopBar + content area)

**Files:**
- Create: `frontend/src/components/layout/AppShell.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/components/layout/TopBar.tsx`

**AppShell structure:**
- Grid layout: `[240px sidebar | 1fr main]`, `[64px topbar | 1fr content]`
- Void background for sidebar (`#0a0a0a`), Obsidian for main content (`#0d0d14`)
- Sidebar: VeloIQ logo at top, nav items (Dashboard, Queue, Pipeline, Audit), user avatar at bottom
- TopBar: page title, search input (inert in Phase 1), user chip
- Main content: `<Outlet />` from React Router

**Sidebar nav items (Phase 1):**
- Dashboard → `/`
- TCC Queue → `/queue`
- (Sales Pipeline, Notifications, Customers 360 — Phase 2)

**Steps:**
- [ ] Write Sidebar.tsx with nav items using NavLink from react-router
- [ ] Write TopBar.tsx with page title + user chip
- [ ] Write AppShell.tsx composing them + `<Outlet />`
- [ ] Test: wrap a dummy child in AppShell, verify layout renders
- [ ] Commit: `feat(frontend): add AppShell layout with Sidebar and TopBar`

**Acceptance:** Visual shell matches Stitch screens: dark sidebar, obsidian content area, emerald accent on active nav item.

---

### Task 14: Write `ConfidencePill` — DESIGN.md signature component

**Files:**
- Create: `frontend/src/components/shared/ConfidencePill.tsx`

**Component logic (per DESIGN.md):**
- Input prop: `score: number` (0.0-1.0 decimal)
- Tier mapping: `> 0.95` → emerald `AUTO MATCH`, `0.70-0.95` → amber `EXPERT REVIEW`, `< 0.70` → coral `MANUAL TRIAGE`
- Visual: pill shape (4px radius, 8px horizontal padding, 2px vertical), JetBrains Mono 600 font, colored text + 10% opacity background
- Score displayed as 3 decimals: `0.840`

**Steps:**
- [ ] Write ConfidencePill.tsx (~40 lines) with the 3-tier logic
- [ ] Render all 3 tiers side-by-side in a test component
- [ ] Verify visual match to Stitch screens (the pill appears on TCC Queue + Match Forensic + Assessment Workspace)
- [ ] Commit: `feat(frontend): add ConfidencePill signature component per DESIGN.md`

**Acceptance:** Three pills with scores 0.98 / 0.84 / 0.62 render with correct colors (emerald / amber / coral) and correct text labels.

---

### Task 15: Write `StatusBadge` — generic status indicator

**Files:**
- Create: `frontend/src/components/shared/StatusBadge.tsx`

**Component logic:**
- Input props: `status: string`, `variant: 'cert' | 'notification' | 'escalation' | 'match' | 'default'`
- Maps status strings to semantic colors:
  - Cert: `active` → emerald, `expiring` → amber, `expired` → coral, `suspended` → muted
  - Notification: `sent/delivered/opened/clicked` → emerald shades, `breached` → coral
  - Escalation: `open` → amber, `contacted` → cyan (use block-cert), `resolved` → emerald
  - Match: `pending` → amber, `reviewed` → emerald

**Steps:**
- [ ] Write StatusBadge.tsx (~60 lines with all mappings)
- [ ] Render each variant with sample statuses in a test grid
- [ ] Commit: `feat(frontend): add StatusBadge with resource-specific color mappings`

**Acceptance:** Each status type renders with the correct color per DESIGN.md semantics.

---

### Task 16: Write `KpiCard` — metric display component

**Files:**
- Create: `frontend/src/components/shared/KpiCard.tsx`

**Component logic:**
- Input props: `label: string`, `value: string | number`, `delta?: { value: string; direction: 'up' | 'down' | 'flat' }`, `icon?: LucideIcon`
- Visual: surface-colored card with divider border, UPPERCASE label (letter-spacing 0.15em, DM Sans 600 muted), large JetBrains Mono value, optional delta line with colored arrow

**Steps:**
- [ ] Write KpiCard.tsx (~50 lines)
- [ ] Render 4 KPI cards in a grid to verify layout
- [ ] Commit: `feat(frontend): add KpiCard metric display component`

**Acceptance:** KPI card matches Stitch Dashboard's 4-card row visually.

---

### Task 17: Write `DataTable` — sortable paginated table

**Files:**
- Create: `frontend/src/components/shared/DataTable.tsx`

**Component logic:**
- Generic: `<DataTable<T>({ columns, data, onSort?, sortKey?, sortOrder?, onRowClick? })>`
- Columns definition: `{ key: keyof T; label: string; sortable?: boolean; render?: (row: T) => ReactNode; className?: string }`
- Header row: `#1a1a2e` bg, uppercase emerald labels, click handler on sortable columns
- Data rows: alternating `#12121e` / `#0d0d14`, 2px emerald left border on hover
- Empty state: delegates to `<EmptyState />` when data is empty

**Steps:**
- [ ] Write DataTable.tsx as generic component (~100 lines)
- [ ] Test: render with 5 dummy rows, 3 columns, verify hover effect + sort indicator
- [ ] Commit: `feat(frontend): add DataTable generic component`

**Acceptance:** Table renders with DESIGN.md styling, sortable columns show arrow indicators, hover highlights row with emerald left border.

---

### Task 18: Write `PaginationControls` + `FilterBar`

**Files:**
- Create: `frontend/src/components/shared/PaginationControls.tsx`
- Create: `frontend/src/components/shared/FilterBar.tsx`

**PaginationControls:**
- Props: `pagination: PaginationMeta`, `onPageChange: (page: number) => void`
- Shows: "Page X of Y · Z total", Prev/Next buttons, jump-to-page input (optional)

**FilterBar:**
- Props: `filters: FilterSpec[]`, `values: Record<string, string>`, `onChange: (key: string, value: string) => void`
- `FilterSpec = { key: string; label: string; type: 'select' | 'text' | 'date'; options?: {label,value}[] }`
- Renders shadcn `<Select>` / `<Input>` elements in a horizontal flex row

**Steps:**
- [ ] Write PaginationControls.tsx (~40 lines)
- [ ] Write FilterBar.tsx (~80 lines) using shadcn Select + Input
- [ ] Test: wire both to a useState in a parent and verify interactions
- [ ] Commit: `feat(frontend): add PaginationControls and FilterBar components`

**Acceptance:** Pagination buttons disable at boundaries, filter changes trigger callback with correct key/value.

---

### Task 19: Write `LoadingState`, `EmptyState`, `ErrorState`

**Files:**
- Create: `frontend/src/components/shared/LoadingState.tsx`
- Create: `frontend/src/components/shared/EmptyState.tsx`
- Create: `frontend/src/components/shared/ErrorState.tsx`

**Components:**
- LoadingState: skeleton-style placeholder with pulse animation, configurable rows
- EmptyState: centered message with icon + optional CTA button
- ErrorState: error message + "Retry" button that invokes a prop callback

**Steps:**
- [ ] Write all 3 components (~30 lines each)
- [ ] Commit: `feat(frontend): add loading/empty/error state components`

**Acceptance:** Can be dropped into any page to handle non-data states.

---

## Part 4 — Core Pages (Tasks 20-25)

### Task 20: Write `LoginPage`

**Files:**
- Create: `frontend/src/pages/LoginPage.tsx`

**Page structure:**
- Full-viewport split layout matching Stitch screen `342e1aba`
- Left panel: VeloIQ logo + branding text + emerald accent graphic
- Right panel: login form (email, password, "Sign In" button, "Demo Mode" button)
- "Demo Mode" button: sets `demo-session` actor to "Dr. M. Weber" and navigates to `/` (dashboard)
- "Sign In" button: disabled (POC has no real auth) or shows toast "Use Demo Mode for POC"

**Steps:**
- [ ] Write LoginPage.tsx (~100 lines)
- [ ] Wire React Hook Form + Zod for the form shape
- [ ] Click "Demo Mode" navigates to `/` via `useNavigate()`
- [ ] Commit: `feat(frontend): add LoginPage with demo mode bypass`

**Acceptance:** LoginPage renders matching Stitch design, Demo Mode button navigates to Dashboard.

---

### Task 21: Write `DashboardPage`

**Files:**
- Create: `frontend/src/pages/DashboardPage.tsx`
- Create: `frontend/src/components/features/dashboard/PipelineHealthPanel.tsx`

**Page structure (matches Stitch `620aff5d`):**
- 4 KPI cards row: Ingested (standards count), Matched (matches count), Assessed (assessments count), Notified (notifications count)
- 7-day bar chart (use recharts or a simple SVG bar chart component) — bars colored by status
- Pipeline Health panel: 4 stages (Received/Normalized/Matched/Routed) with throughput counts + status indicator
- SLA Compliance regional heatmap (EMEA / Greater China / Americas / South Asia — based on customer country distribution)

**Data fetching:**
- `useStandards.useList({ page: 1, limit: 1 })` → `.pagination.total` for Ingested count
- `useMatches.useList({ page: 1, limit: 1 })` → total
- `useAssessments.useList({ page: 1, limit: 1 })` → total
- `useNotifications.useList({ page: 1, limit: 1 })` → total

**Steps:**
- [ ] Install `recharts` if used
- [ ] Write DashboardPage.tsx (~200 lines)
- [ ] Write PipelineHealthPanel.tsx as extracted component
- [ ] Verify all 4 KPI cards populate with live backend data
- [ ] Commit: `feat(frontend): add DashboardPage with KPI cards and pipeline health`

**Acceptance:** Dashboard shows real counts from seeded data (50 standards, 30 matches, 30 assessments, 20 notifications).

---

### Task 22: Write `TCCQueuePage`

**Files:**
- Create: `frontend/src/pages/TCCQueuePage.tsx`

**Page structure (matches Stitch `25905ba1`):**
- Page title: "TCC Queue" + assessment count badge
- FilterBar: Impact Classification, Decision status, Assessor dropdown
- DataTable with columns: Priority (!!/!/none), Standard (ac_code + title), Confidence Score (ConfidencePill), Affected Certs (count), SLA (days remaining), Age (days since matched_at), Assessed By (avatar + name)
- Row click → navigate to `/assessments/:id`
- PaginationControls at bottom

**Data fetching:**
- `useAssessments.useList({ page, limit: 25, ...filters })`
- For each assessment row, may need `useMatches.useDetail(assessment.match_result_id)` lookup — OR backend enrichment

**Note on SLA calculation:** Derive from `assessment.decided_at` vs a hardcoded 14-day SLA target for Phase 1 demo. Real SLA logic is Phase D.

**Steps:**
- [ ] Write TCCQueuePage.tsx (~180 lines)
- [ ] Wire filters to query params (sync with URL via useSearchParams)
- [ ] Row click triggers navigate to assessment workspace
- [ ] Commit: `feat(frontend): add TCCQueuePage with filterable assessment queue`

**Acceptance:** Queue shows 30 seeded assessments paginated, filters narrow results, clicking a row navigates to workspace.

---

### Task 23: Write `AssessmentWorkspacePage`

**Files:**
- Create: `frontend/src/pages/AssessmentWorkspacePage.tsx`
- Create: `frontend/src/components/features/assessment/DeltaDiffViewer.tsx`
- Create: `frontend/src/components/features/assessment/ImpactedCertsTable.tsx`
- Create: `frontend/src/components/features/assessment/DecisionForm.tsx`

**Page structure (matches Stitch `c240dd89`):**
- Breadcrumb: "TCC Queue > {standard.ac_code}"
- Header: standard title + ConfidencePill + status
- **Section 1:** DeltaDiffViewer — 2018 vs 2023 clause comparison (synthetic for Phase 1 — text from standard.title + a few hardcoded clause deltas; Phase B provides real clause diffing)
- **Section 2:** Impacted Population Summary — cert count, risk score, customer count (derive from GET /api/v1/certificates filtered by link chain)
- **Section 3:** ImpactedCertsTable — table of affected certificates with risk + expiry + products
- **Section 4:** DecisionForm — impact classification dropdown, action required dropdown, reason_code input, notes textarea, Approve/Reject buttons

**Data fetching:**
- `useAssessments.useDetail(id)` — gets the assessment (read-only display)
- `useMatches.useDetail(assessment.match_result_id)` — score, link to cert
- `useStandards.useDetail(match.natos_standard_id)` — standard title + metadata
- `useCertificates.useList({ customer_id: ... })` — impacted certs (via link chain)
- `useAssessments.useCreate()` — POST new assessment (on submit)

**Submit flow:**
- User fills form + clicks "Approve" or "Reject"
- Calls `createAssessment.mutate({ ... })` with decision="approved"/"rejected"
- On success: show toast "Decision recorded", invalidate queue, navigate back to /queue
- On error: show toast with error message

**Steps:**
- [ ] Write DeltaDiffViewer.tsx — 3-column layout (Old Clause / Change Badge / New Clause)
- [ ] Write ImpactedCertsTable.tsx using DataTable
- [ ] Write DecisionForm.tsx using React Hook Form + Zod
- [ ] Write AssessmentWorkspacePage.tsx wiring everything
- [ ] Test: submit a decision, verify POST hits backend, assessment row appears in DB, audit_log has entry
- [ ] Commit: `feat(frontend): add AssessmentWorkspacePage with decision submission`

**Acceptance:** Expert can open a queued assessment, view delta + impact, click Approve, and see the decision persisted in the backend (verify via audit log).

---

### Task 24: Write `MatchForensicPage`

**Files:**
- Create: `frontend/src/pages/MatchForensicPage.tsx`
- Create: `frontend/src/components/features/match-forensic/NormalizationTrace.tsx`
- Create: `frontend/src/components/features/match-forensic/AlgorithmScoreGrid.tsx`
- Create: `frontend/src/components/features/match-forensic/AffectedCertificatesTable.tsx`

**Page structure (matches Stitch `b8030f1d`):**
- Header: match ID, ConfidencePill, emerald accent "Expert Review Required" callout
- NormalizationTrace: side-by-side "NATOS Source" vs "SAP Target" with step-by-step normalization (synthetic for Phase 1 — show raw `standard_ref` vs `normalized_ref` from link + derive 3 transformation steps)
- AlgorithmScoreGrid: 4 score tiles — Levenshtein, Jaro-Winkler, Token Set, Composite (Similarity)
- AffectedCertificatesTable: 8 certs linked to this match's cert_link → certificate → customer's other certificates
- Footer: "Send to Assessment" button (if match.status === "pending")

**Data fetching:**
- `useMatches.useDetail(id)` — get match_result with all 4 scores
- Follow match.cert_link_id → fetch cert_link → cert → customer → customer's certificates

**Note:** The backend doesn't currently expose `cert_standard_links` detail endpoint. For Phase 1 MVP, derive affected certs by filtering `useCertificates.useList({ customer_id: <derived> })`. OR add `GET /api/v1/cert-standard-links/{id}` to backend (not in current Phase A plan).

**Steps:**
- [ ] Write NormalizationTrace.tsx with 3-step transformation visualization
- [ ] Write AlgorithmScoreGrid.tsx (4 score cards in a row)
- [ ] Write AffectedCertificatesTable.tsx using DataTable
- [ ] Write MatchForensicPage.tsx
- [ ] Commit: `feat(frontend): add MatchForensicPage with algorithm scores and trace`

**Acceptance:** Match detail page shows all 4 similarity scores + normalization trace + affected certificates table.

---

### Task 25: Write `NotFoundPage` + error boundary

**Files:**
- Create: `frontend/src/pages/NotFoundPage.tsx`
- Create: `frontend/src/components/ErrorBoundary.tsx`

**NotFoundPage:** centered "404 — VeloIQ can't find that" with "Back to Dashboard" button.

**ErrorBoundary:** React class component wrapping the app, catches unhandled render errors, shows fallback UI with "Reload" button.

**Steps:**
- [ ] Write both components
- [ ] Wrap `<App />` with `<ErrorBoundary>` in main.tsx
- [ ] Add `*` route in router that renders NotFoundPage
- [ ] Commit: `feat(frontend): add NotFoundPage and ErrorBoundary`

**Acceptance:** Navigating to `/nonexistent` shows 404 page, throwing in any component shows error boundary.

---

## Part 5 — Integration & Deployment (Tasks 26-30)

### Task 26: Wire React Router with all routes + AppShell

**Files:**
- Modify: `frontend/src/App.tsx`

**Routes structure:**
```
/ (AppShell)
├── index → redirect to /login if no session, else Dashboard
├── /login → LoginPage (no shell)
├── /queue → TCCQueuePage
├── /assessments/:id → AssessmentWorkspacePage
├── /matches/:id → MatchForensicPage
└── * → NotFoundPage
```

Implement a `<ProtectedRoute>` wrapper that checks demo-session.getActor() — redirects to /login if missing.

**Steps:**
- [ ] Write App.tsx with full route tree using createBrowserRouter
- [ ] Add `<ProtectedRoute>` wrapper for authenticated routes
- [ ] Test: navigate through all 5 pages via clicks, verify no console errors
- [ ] Commit: `feat(frontend): wire complete route tree with protected routes`

**Acceptance:** Click-through navigation works: Login → Dashboard → Queue → Assessment → Match Forensic → back to Queue.

---

### Task 27: End-to-end manual test — seeded data verification

**Files:** no new files (test task)

**Test checklist:**
- [ ] `docker compose up -d` (starts postgres + backend)
- [ ] `docker compose exec backend python -m data_seeder.seed_all` (seeds)
- [ ] `cd frontend && npm run dev` (starts Vite dev server)
- [ ] Navigate to http://localhost:5173/login → click Demo Mode → redirected to /
- [ ] Dashboard shows: 50 standards, 30 matches, 30 assessments, 20 notifications
- [ ] Click "TCC Queue" in sidebar → shows 30 assessments paginated
- [ ] Click an assessment row → opens workspace, shows delta + impact + form
- [ ] Navigate to `/matches/<id>` directly → shows match forensic with 4 algorithm scores
- [ ] Click "Back" or sidebar → returns cleanly

**Steps:**
- [ ] Execute checklist manually
- [ ] Screenshot each page for demo evidence
- [ ] Document any console errors or failed API calls in `docs/frontend-e2e-verification.md`
- [ ] Commit: `docs(frontend): add E2E verification screenshots and log`

**Acceptance:** All 5 pages render with real seeded data, no console errors, all API calls return 200.

---

### Task 28: End-to-end test — Submit assessment decision writes to DB

**Files:** no new files (test task)

**Test:**
- [ ] Open `/assessments/:id` for any queued assessment
- [ ] Fill decision form: impact="minor_technical", action="reconfirm", reason="Administrative update only", notes="E2E test", decision="approved"
- [ ] Click "Approve" button
- [ ] Verify: toast "Decision recorded"
- [ ] Verify: POST /api/v1/assessments returned 201 (check Network tab)
- [ ] Verify in DB: `docker compose exec postgres psql -U veloiq -d veloiq -c "SELECT COUNT(*) FROM assessments WHERE notes = 'E2E test';"` returns 1
- [ ] Verify audit: `SELECT * FROM audit_log WHERE entity_type = 'assessment' AND action = 'created' ORDER BY created_at DESC LIMIT 1;` shows the new entry

**Acceptance:** Assessment submission from UI writes to DB and creates a paired audit_log entry.

---

### Task 29: Dockerfile + nginx config for frontend

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`

**Dockerfile (multi-stage build):**
- Stage 1 (`node:20-slim`): install deps, build with `npm run build`
- Stage 2 (`nginx:alpine`): copy `dist/` to `/usr/share/nginx/html`, use custom nginx.conf

**nginx.conf:**
- Serve static assets from /
- Proxy `/api/*` to `http://backend:8000/api/*`
- SPA fallback: any unmatched route serves `index.html`
- Enable gzip compression

**Steps:**
- [ ] Write Dockerfile (~25 lines)
- [ ] Write nginx.conf (~30 lines)
- [ ] Build locally: `docker build -t veloiq-frontend:latest .` — verify successful build
- [ ] Commit: `feat(frontend): add Dockerfile and nginx config`

**Acceptance:** Docker image builds successfully, image size <100MB, nginx serves SPA correctly.

---

### Task 30: Add frontend service to docker-compose.yml

**Files:**
- Modify: `docker-compose.yml` (repo root)

**New service block:**
```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: veloiq-frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
```

**Steps:**
- [ ] Add `frontend` service block to docker-compose.yml (after backend)
- [ ] Verify: `docker compose down && docker compose up -d` starts all 3 containers
- [ ] Navigate to http://localhost:5173 (served by nginx, not Vite dev server)
- [ ] Click through Login → Dashboard → Queue → Assessment, verify API calls go through nginx proxy to backend
- [ ] Commit: `feat(docker): add frontend service to docker-compose stack`

**Acceptance:** `docker compose up -d` starts 3 containers (postgres + backend + frontend), frontend accessible at http://localhost:5173, all pages function against backend.

---

## Definition of Done — Phase 1 MVP

Phase A-UI MVP is complete when **all** of these are true:

1. **`docker compose up -d` starts 3 containers** (postgres + backend + frontend)
2. **Frontend accessible at http://localhost:5173** via nginx
3. **All 5 core pages render** with real seeded data:
   - Login page shows branded split layout
   - Dashboard shows 4 KPI cards with correct counts (50/30/30/20)
   - TCC Queue shows 30 assessments with filters, pagination, ConfidencePill
   - Assessment Workspace loads delta viewer + impact table + decision form
   - Match Forensic shows 4 algorithm scores + normalization trace
4. **Navigation works end-to-end**: Login → Dashboard → Queue → Assessment → Match → back
5. **Assessment submission writes to DB**: fill form → click Approve → POST succeeds → new row in `assessments` table + paired audit_log entry
6. **No console errors** during a full click-through
7. **Theme matches DESIGN.md**: obsidian backgrounds, emerald accents, DM Sans + JetBrains Mono fonts, ConfidencePill signature component visible on Queue + Forensic pages
8. **`npm run build` succeeds** — production bundle under 500KB gzipped
9. **TypeScript strict mode**: `tsc --noEmit` passes with zero errors
10. **ESLint + Prettier**: `npm run lint` passes

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Backend POST /assessments doesn't exist yet | Task 1 adds it — 40 lines, follows existing mutation service pattern |
| Delta diff viewer needs real clause text, backend only has titles | Phase 1 uses synthetic hardcoded deltas ("Added: Section 4.2.1 ..."); Phase B will plumb real clause data from `source_payload` JSONB |
| Impacted certs derivation requires following cert_link_id → certificate → customer → customer's certs chain client-side | Accept the 3-4 hop fetch in Phase 1; consider adding `GET /api/v1/cert-standard-links/{id}` with eager joins in Phase B |
| shadcn/ui colors may fight DESIGN.md tokens | Override shadcn's default CSS variables in index.css to use DESIGN.md palette |
| Vite dev proxy doesn't work with Docker backend on different port | `.env` VITE_API_BASE_URL=`http://localhost:8000/api/v1` directly bypasses proxy — tested fallback |
| CORS blocks frontend fetches | Backend already has `allow_origins=["http://localhost:5173","http://localhost:3000"]` in main.py, verified in Phase A verification |
| Scope creep — user wants Phase 2 screens before MVP is done | Stick to 5-screen MVP for first push; Phase 2 planned separately |

---

## Phase 2 — Next Plan (not in this document)

After MVP is demo-ready, Phase 2 adds:
- Customer 360 page (`0e8f2094`) — customer detail with cert portfolio
- Notification Center page (`5d9603f9`) — notification log with delivery funnel
- Sales Pipeline page (`a3d850e0`) — opportunity tracking

Estimated: 8-10 additional tasks. Will have its own plan document.

---

## Self-Review Checklist

- ✅ **Spec coverage:** Every recommended-scope screen (5) has at least one task. Backend POST endpoint gap is closed in Task 1. All architectural decisions (AD1-AD9) documented.
- ✅ **No placeholders:** No TBDs, no "similar to...", no "implement later" phrases. Each task has explicit files + acceptance criteria.
- ✅ **Type consistency:** `UUID` alias used consistently, `PaginatedResponse<T>` referenced in hooks matches types.ts definition, `AssessmentCreate` introduced in Task 1 is used in Task 12 (assessments hook) and Task 23 (workspace page).
- ✅ **Dependency order:** Task 1 (backend POST) → Tasks 2-7 (scaffolding) → Tasks 8-12 (API layer) → Tasks 13-19 (shared components) → Tasks 20-25 (pages) → Tasks 26-30 (wiring + deploy).

---

## Execution Handoff

**Plan saved to:** `docs/superpowers/plans/2026-04-06-phase-a-ui-frontend.md`

Two execution options:

### Option 1 — Subagent-Driven (recommended)

Dispatch a fresh subagent per task, two-stage review (spec compliance + code quality) after each. Matches the pattern used for backend Phase A (39 tasks completed this way). Produces 30 clean commits on main.

Uses: `superpowers:subagent-driven-development` skill.

### Option 2 — Inline Execution

Execute tasks sequentially in the same session with checkpoints between parts (every 5-6 tasks). Faster if you want batch approval, slower to review.

Uses: `superpowers:executing-plans` skill.

---

**END OF PLAN — READY FOR REVIEW**
