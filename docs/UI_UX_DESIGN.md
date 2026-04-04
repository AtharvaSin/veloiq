# VeloIQ UI/UX Design Document

**Version:** 0.1  
**Author:** Atharva Singh (Zealogics Inc.)  
**Date:** 2026-04-05  
**Status:** Design direction committed  
**Research basis:** NotebookLM VeloIQ Standards Automation Deep Research Brief (977 curated sources)

---

## Design Context Declaration

```
BRAND CONTEXT: A — AI OS System (professional/Zealogics work product)
CONTENT TYPE: dashboard / data-view / workflow / form
ACCENT COLOR: Emerald #00D492
DISPLAY FONT: DM Sans 800
TOKEN SOURCE:
  --a-bg-void:       #0a0a0a   (deepest background)
  --a-bg-base:       #0d0d14   (page background)
  --a-bg-surface:    #12121e   (cards, panels)
  --a-bg-elevated:   #1a1a2e   (hover states)
  --a-border:        #1f1f35   (dividers, borders)
  --a-accent-primary: #00D492  (THE accent — max 3-5 per screen)
  --a-text-primary:  #EEEAE4   (headings)
  --a-text-secondary: #A09D95  (body)
  --a-text-muted:    #606060   (labels)
  DATA FONT: JetBrains Mono (all metrics, scores, timestamps, IDs)
```

---

## Part 1: User Personas

Five distinct user types interact with VeloIQ. Each has different cognitive loads, decision authority, and time-on-screen patterns.

### Persona 1: TCC Technical Expert (The Domain Authority)

| Attribute | Detail |
|---|---|
| **Role** | Senior technical reviewer in TUV's Technical Competence Centre |
| **Decision authority** | Legally binding — their "Approve" carries FDA 21 CFR Part 11 weight |
| **Daily volume** | Reviews 8-15 standards assessments per day |
| **Session pattern** | Deep focus blocks of 2-3 hours; needs eye comfort on dark surfaces |
| **Primary pain** | Reviewer fatigue from reading entire PDFs; disconnected systems for impact data |
| **Needs at a glance** | The "delta" (what changed), who's affected, how similar cases were decided before |
| **Technical comfort** | High — understands standards nomenclature, regulatory stages, matching logic |
| **Critical task** | Review fuzzy match → classify impact → sign off with reason code |

### Persona 2: Master Data Steward (The Taxonomy Gatekeeper)

| Attribute | Detail |
|---|---|
| **Role** | Manages standards taxonomy and resolves low-confidence matches |
| **Decision authority** | Creates canonical mappings that affect all future matching |
| **Daily volume** | Handles 3-8 complex edge cases per day (score < 0.70) |
| **Session pattern** | Investigative — toggles between Natos data and SAP records |
| **Primary pain** | Manual VLOOKUPs between exported CSVs and messy SAP data |
| **Needs at a glance** | Raw identifiers side-by-side, searchable SAP index, normalization trace |
| **Technical comfort** | Very high — the deepest data expertise in the pipeline |
| **Critical task** | Manually map orphaned standard → create canonical link → update global dictionary |

### Persona 3: Sales Account Manager (The Revenue Securer)

| Attribute | Detail |
|---|---|
| **Role** | Follows up with clients who must re-certify due to standard changes |
| **Decision authority** | Commercial — closes recertification deals |
| **Daily volume** | Manages 15-25 customer accounts; 3-5 escalations per day |
| **Session pattern** | Quick scans between calls; needs fast filtering and clear priorities |
| **Primary pain** | No visibility into which clients face immediate compliance gaps |
| **Needs at a glance** | Who hasn't responded, SLA countdown, portfolio value at risk |
| **Technical comfort** | Medium — understands standards impact but not matching algorithms |
| **Critical task** | Identify unresponsive customer → assess risk → initiate outreach |

### Persona 4: Operations Leadership (The Compliance Overseer)

| Attribute | Detail |
|---|---|
| **Role** | Monitors global regulatory exposure, ensures SLA compliance, maintains audit readiness |
| **Decision authority** | Strategic — staffing, escalation policies, process changes |
| **Daily volume** | One 15-minute dashboard check in the morning; deeper dives before audits |
| **Session pattern** | Scan and drill — needs everything at a glance, with drill-down on exceptions |
| **Primary pain** | Shadow IT — teams use side spreadsheets, creating blind spots |
| **Needs at a glance** | Pipeline throughput, queue depths, SLA adherence, regional distribution |
| **Technical comfort** | Medium — cares about outcomes and trends, not algorithm internals |
| **Critical task** | Spot bottlenecks → identify SLA risks → make resourcing decisions |

### Persona 5: System Administrator (The Platform Keeper)

| Attribute | Detail |
|---|---|
| **Role** | Configures thresholds, manages users, monitors integration health |
| **Decision authority** | Technical — system configuration, not business decisions |
| **Daily volume** | Reactive — steps in when something breaks or needs tuning |
| **Session pattern** | Diagnostic — enters when alerted, needs fast root-cause visibility |
| **Primary pain** | Integration failures between Natos/SAP stubs and the matching engine |
| **Needs at a glance** | Service health, error logs, configuration state, queue overflow |
| **Technical comfort** | Highest — understands the full technical stack |
| **Critical task** | Adjust matching thresholds → manage user permissions → resolve integration errors |

---

## Part 2: User Journeys

### Journey 1: TCC Expert — "Review and Decide"

```
                                                     EMOTIONAL STATE
STEP  ACTION                                         ─────────────────
 1    Opens VeloIQ → lands on TCC Queue              Focused, scanning
      Sees: 12 items in queue, 2 flagged urgent
      
 2    Clicks top-priority assessment                  Engaged, orienting
      Page: Assessment Workspace loads
      
 3    Reads Delta View (side-by-side diff)            Analytical, comparing
      Left: old standard clauses
      Right: new standard clauses (changes highlighted)
      
 4    Scrolls to Impacted Population panel            Concerned, evaluating
      Sees: 8 certificates, 4 customers, risk score 7.2/10
      
 5    Checks Historical Precedent sidebar             Confident, contextualizing
      Sees: 3 prior similar decisions, all classified "Major"
      
 6    Opens Decision Panel                            Decisive, committing
      Selects: Impact = "Major Technical"
      Selects: Action = "Re-test Required"
      Selects: Reason code = "New mandatory safety test"
      Types: brief note (optional)
      
 7    Clicks "Approve & Sign Off"                     Authoritative, accountable
      System: records immutable audit entry
      System: fires notification event to Block 3
      
 8    Returns to TCC Queue → next item                Productive, rhythm
      Queue count: 11 remaining
```

**Design implication:** The workspace must minimize navigation. Steps 3-7 happen on ONE page. No tab-switching. No popup modals. Everything the expert needs is spatially organized in a single scrollable view.

### Journey 2: Master Data Steward — "Resolve the Exception"

```
 1    Opens VeloIQ → lands on Ingestion Monitor       Investigative
      Sees: 3 items in "Manual Triage" queue (score < 0.70)
      
 2    Clicks a low-confidence match                   Curious, diagnosing
      Page: Match Detail loads
      
 3    Reviews Normalization Trace                     Analytical
      Sees: raw Natos string → each transformation step → final normalized form
      Sees: SAP string → each transformation step → final normalized form
      Sees: why the score was low (e.g., "GB/T prefix not in decomposition rules")
      
 4    Opens SAP Index Search panel                    Searching, cross-referencing
      Searches for the base standard number
      Finds: 2 potential SAP records that could match
      
 5    Selects the correct mapping                     Confident, resolving
      System: creates canonical link
      System: updates global normalization dictionary
      System: re-routes the record to appropriate confidence tier
      
 6    Returns to Ingestion Monitor → next exception   Systematic
```

**Design implication:** The steward needs a forensic UI — every string transformation must be traceable. The SAP search must be inline (not a separate page). The normalization trace is the hero widget.

### Journey 3: Sales Account Manager — "Chase the Escalation"

```
 1    Opens VeloIQ → lands on Sales Pipeline          Scanning, prioritizing
      Sees: 5 SLA-breached escalations, sorted by portfolio value
      
 2    Clicks highest-value escalation                 Focused, assessing
      Page: Customer 360 loads
      
 3    Reviews notification history                    Understanding
      Sees: compliance alert sent 16 days ago, SLA was 14 days
      Sees: email delivered but not opened
      
 4    Reviews customer's certificate portfolio        Strategic
      Sees: 3 active certificates, 1 affected by withdrawn standard
      Sees: total portfolio value: EUR 240,000
      
 5    Clicks "Mark as Contacted"                      Active, following up
      Types: "Called Hans Mueller, meeting scheduled for Thursday"
      System: updates escalation status
      
 6    Returns to Sales Pipeline → next escalation     Productive
```

**Design implication:** This is a CRM-like view. Quick scan, fast action. SLA countdown timers must be visually loud. Portfolio value must be the first number the eye sees.

### Journey 4: Operations Leadership — "Morning Health Check"

```
 1    Opens VeloIQ → lands on System Dashboard        Scanning, assessing
      Sees: 4 KPI cards (ingested today, matched, assessed, notified)
      Sees: pipeline throughput trend (7-day sparkline)
      
 2    Notices SLA compliance rate dropped to 87%      Alerted, drilling
      Clicks the SLA metric card
      
 3    Drills into SLA breakdown by region             Diagnostic
      Sees: Greater China at 72% (below threshold)
      Sees: Germany at 96%, India at 91%
      
 4    Drills into China queue                         Decisive
      Sees: 8 assessments stuck in TCC queue > 5 days
      Sees: assigned to 2 reviewers who are at capacity
      
 5    Makes a note to reassign resources              Strategic
      Returns to dashboard satisfied with diagnosis
```

**Design implication:** The dashboard must be a 15-second scan. KPI cards → trend lines → drill-down. No cognitive overhead. The drill-down must be click-to-expand, not page navigation.

---

## Part 3: Aesthetic Direction

### Direction Statement

> **Operational Command** for a compliance automation control center. The interface feels like a precision instrument — dark obsidian surfaces with data rendered in JetBrains Mono, creating the sense of a system that processes thousands of standards with mechanical certainty. Emerald (#00D492) marks exactly three things per screen: the active item, the primary action button, and the single most important metric. Everything else recedes into the obsidian surface hierarchy. The user should feel **informed, in control, and legally confident** — not excited, not entertained.

### The ONE Unforgettable Thing

> **The Confidence Score Pill.** Every match result displays a `JetBrains Mono` rendered similarity score inside a pill-shaped indicator that shifts along a three-zone color gradient: Emerald (#00D492) for auto-match (>0.95), amber (#E8B931) for expert review (0.70-0.95), and danger (#FF6B6B) for manual triage (<0.70). This pill appears everywhere — in queue tables, in assessment headers, in the dashboard KPIs. It becomes the visual signature of VeloIQ: "the score tells you everything."

### Semantic Color System (VeloIQ-Specific)

Beyond the Context A base tokens, VeloIQ adds a semantic layer for compliance states:

| Token | Hex | Usage |
|---|---|---|
| `--v-confidence-high` | `#00D492` | Auto-match (score > 0.95) — maps to accent-primary |
| `--v-confidence-medium` | `#E8B931` | Expert review (0.70-0.95) — maps to accent-warning |
| `--v-confidence-low` | `#FF6B6B` | Manual triage (< 0.70) — maps to accent-danger |
| `--v-sla-safe` | `#00D492` | SLA on track |
| `--v-sla-warning` | `#E8B931` | SLA at risk (< 48h remaining) |
| `--v-sla-breach` | `#FF6B6B` | SLA breached |
| `--v-status-pending` | `#606060` | Awaiting action |
| `--v-status-in-review` | `#E8B931` | Under expert review |
| `--v-status-approved` | `#00D492` | Decision finalized |
| `--v-status-escalated` | `#FF6B6B` | Escalated to higher authority |
| `--v-block-cert` | `#0EA5E9` | Certification Block indicator (sky blue) |
| `--v-block-tcc` | `#8B5CF6` | TCC Block indicator (purple) |
| `--v-block-sales` | `#22C55E` | Sales & Marketing Block indicator (green) |

**Rule:** Block colors (`cert`, `tcc`, `sales`) appear ONLY as thin top-borders on block-specific cards and as sidebar navigation indicators. They never compete with the emerald accent.

---

## Part 4: Page Inventory

### Complete Page List (14 Pages)

| # | Page | URL Route | Primary Persona | Block | Priority |
|---|---|---|---|---|---|
| 1 | **System Dashboard** | `/` | Ops Leadership | All | P0 |
| 2 | **Ingestion Monitor** | `/ingestion` | Master Data Steward | 1 | P0 |
| 3 | **Match Results** | `/matches` | Master Data Steward | 1 | P0 |
| 4 | **Match Detail** | `/matches/:matchId` | Master Data Steward | 1 | P0 |
| 5 | **TCC Queue** | `/tcc` | TCC Expert | 2 | P0 |
| 6 | **Assessment Workspace** | `/tcc/:assessmentId` | TCC Expert | 2 | P0 |
| 7 | **Audit Trail** | `/audit` | TCC Expert / Ops | 2 | P1 |
| 8 | **Notification Center** | `/notifications` | Sales Manager | 3 | P0 |
| 9 | **Sales Pipeline** | `/sales` | Sales Manager | 3 | P0 |
| 10 | **Customer 360** | `/customers/:customerId` | Sales Manager | 3 | P1 |
| 11 | **Standards Explorer** | `/standards` | All | 1 | P1 |
| 12 | **Analytics** | `/analytics` | Ops Leadership | All | P2 |
| 13 | **Settings** | `/settings` | Sys Admin | — | P2 |
| 14 | **Login** | `/login` | All | — | P0 |

**Total: 14 pages** — 9 at P0 (must-have for demo), 3 at P1 (enhances demo), 2 at P2 (post-demo).

---

## Part 5: Site Map & Navigation Architecture

### Navigation Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│  PERSISTENT SHELL                                                   │
│  ┌──────────┐ ┌───────────────────────────────────────────────────┐ │
│  │          │ │ TOP BAR                                           │ │
│  │          │ │ [VeloIQ logo]  [Search]  [Notifications bell]    │ │
│  │ SIDEBAR  │ │ [User avatar + role badge]                       │ │
│  │          │ ├───────────────────────────────────────────────────┤ │
│  │ ┌──────┐ │ │                                                   │ │
│  │ │DASHBD│ │ │                                                   │ │
│  │ └──────┘ │ │                                                   │ │
│  │          │ │                                                   │ │
│  │ BLOCK 1  │ │              MAIN CONTENT AREA                   │ │
│  │ ┌──────┐ │ │                                                   │ │
│  │ │INGEST│ │ │         (page-specific content)                  │ │
│  │ │MATCH │ │ │                                                   │ │
│  │ │STNDRD│ │ │                                                   │ │
│  │ └──────┘ │ │                                                   │ │
│  │          │ │                                                   │ │
│  │ BLOCK 2  │ │                                                   │ │
│  │ ┌──────┐ │ │                                                   │ │
│  │ │TCC Q │ │ │                                                   │ │
│  │ │AUDIT │ │ │                                                   │ │
│  │ └──────┘ │ │                                                   │ │
│  │          │ │                                                   │ │
│  │ BLOCK 3  │ │                                                   │ │
│  │ ┌──────┐ │ │                                                   │ │
│  │ │NOTIFS│ │ │                                                   │ │
│  │ │SALES │ │ │                                                   │ │
│  │ │CUST  │ │ │                                                   │ │
│  │ └──────┘ │ │                                                   │ │
│  │          │ │                                                   │ │
│  │ ─────── │ │                                                   │ │
│  │ ANALYTCS│ │                                                   │ │
│  │ SETTINGS│ │                                                   │ │
│  └──────────┘ └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Sidebar Design

- **Width:** 240px expanded, 60px collapsed (icon-only)
- **Background:** `--a-bg-void` (#0a0a0a) — one shade darker than main content
- **Block grouping:** Three sections separated by 1px `--a-border` dividers
- **Block indicators:** 3px left border on each group using block color (`--v-block-cert`, `--v-block-tcc`, `--v-block-sales`)
- **Active item:** `--a-bg-elevated` background + `--a-accent-primary` left border (2px)
- **Badge counts:** JetBrains Mono, small pill showing pending items per queue
- **Collapsed state:** Icons only + badge counts; tooltip on hover

### Page Connection Map

```
                    ┌──────────────┐
                    │   LOGIN      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
           ┌────── │  DASHBOARD    │ ──────┐
           │       └──┬───┬───┬───┘       │
           │          │   │   │            │
     ┌─────▼────┐  ┌──▼───▼┐  ┌──▼──────┐  │
     │ BLOCK 1  │  │BLOCK 2│  │ BLOCK 3 │  │
     │          │  │       │  │         │  │
     ├──────────┤  ├───────┤  ├─────────┤  │
     │Ingestion │  │TCC    │  │Notif.   │  │
     │ Monitor  │  │Queue  │  │Center   │  │
     │    │     │  │  │    │  │   │     │  │
     │    ▼     │  │  ▼    │  │   ▼     │  │
     │Match     │  │Assess-│  │Sales    │  │
     │Results   │  │ment   │  │Pipeline │  │
     │    │     │  │Work-  │  │   │     │  │
     │    ▼     │  │space  │  │   ▼     │  │
     │Match     │  │  │    │  │Customer │  │
     │Detail ───┼──┼──┘    │  │360    ◄─┼──┤
     │          │  │       │  │         │  │
     └────┬─────┘  └───┬───┘  └────┬────┘  │
          │            │           │        │
          ▼            ▼           ▼        │
     ┌──────────┐ ┌────────┐ ┌──────────┐  │
     │Standards │ │Audit   │ │Analytics │◄─┘
     │Explorer  │ │Trail   │ └──────────┘
     └──────────┘ └────────┘

    LEGEND:
    ─── = sidebar navigation
    ──► = contextual drill-down (click within page)
    ◄── = cross-block link (e.g., customer 360 from dashboard)
```

### Cross-Page Navigation Flows

| From | To | Trigger |
|---|---|---|
| Dashboard → TCC Queue | Click "Expert Review" KPI card | Drill into pending assessments |
| Dashboard → Sales Pipeline | Click "SLA Breached" KPI card | Drill into escalated notifications |
| Dashboard → Ingestion Monitor | Click "Ingested Today" KPI card | Drill into today's pipeline |
| Match Results → Match Detail | Click any row in match table | View full match forensics |
| Match Detail → Assessment Workspace | Click "Route to TCC" button | When steward confirms match |
| TCC Queue → Assessment Workspace | Click any assessment row | Begin expert review |
| Assessment Workspace → Audit Trail | Click "View Full History" link | Expand audit for this record |
| Assessment Workspace → Customer 360 | Click any customer name | View customer's full portfolio |
| Notification Center → Customer 360 | Click customer name on notification | See all customer context |
| Sales Pipeline → Customer 360 | Click escalation row | Full customer view with SLA context |
| Customer 360 → Assessment Workspace | Click linked assessment | View the decision behind a notification |

---

## Part 6: Detailed Page Designs

### Page 1: System Dashboard (`/`)

**The ONE job:** "The user needs to assess pipeline health in 15 seconds in order to spot bottlenecks before they become SLA breaches."

**Emotional register:** Clarity

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  SECTION LABEL: 01 — PIPELINE STATUS                           │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ INGESTED │ │ MATCHED  │ │ ASSESSED │ │ NOTIFIED │          │
│  │   47     │ │   41     │ │   38     │ │   35     │          │
│  │ today    │ │ today    │ │ today    │ │ today    │          │
│  │ ▲12%     │ │ ▲8%      │ │ ▼3%      │ │ ▲15%     │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                 │
│  7-DAY THROUGHPUT TREND                                        │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  ╱╲    ╱╲                                           │       │
│  │ ╱  ╲  ╱  ╲─╱╲   ← ingested (muted line)           │       │
│  │╱    ╲╱    ╲╱  ╲  ← assessed (emerald line)         │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  SECTION LABEL: 02 — QUEUE HEALTH                              │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ TCC EXPERT QUEUE    │  │ EXCEPTIONS QUEUE     │              │
│  │ 12 pending          │  │ 3 pending            │              │
│  │ ████████░░ 80%      │  │ ██░░░░░░░░ 20%       │              │
│  │ Oldest: 2.4 days    │  │ Oldest: 1.1 days     │              │
│  │ Avg response: 4.2h  │  │ Avg response: 8.1h   │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  SECTION LABEL: 03 — SLA COMPLIANCE                            │
│                                                                 │
│  ┌───────────────────────────────────────────┐ ┌─────────────┐ │
│  │ SLA COMPLIANCE BY REGION                  │ │ BREACHED (5) │ │
│  │                                           │ │             │ │
│  │ Germany     ████████████████████ 96%      │ │ Siemens AG  │ │
│  │ India       █████████████████░░ 91%       │ │ 2d overdue  │ │
│  │ UK          █████████████████░░ 89%       │ │             │ │
│  │ China       ████████████░░░░░░ 72% ⚠     │ │ Huawei Tech │ │
│  │ USA         ██████████████████░ 94%       │ │ 1d overdue  │ │
│  │                                           │ │    ...      │ │
│  └───────────────────────────────────────────┘ └─────────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  SECTION LABEL: 04 — RECENT ACTIVITY                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 14:32  System   Auto-matched ISO 9001:2015 → 3 certs  [●] ││
│  │ 14:28  M.Weber  Approved IEC 62368-1 assessment        [●] ││
│  │ 14:15  System   SLA breach: Huawei — IEC 61000-4-2     [!] ││
│  │ 13:58  K.Chen   Classified GB/T 45001 as Minor         [●] ││
│  │ 13:41  System   Ingested 3 Natos updates (Stage 60)    [○] ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Component details:**
- KPI cards: `--a-bg-surface` with 3px top border in `--v-block-*` color per block. Large metric in JetBrains Mono 36px. Delta percentage in emerald (positive) or danger (negative).
- Throughput trend: Area chart, emerald fill at 10% opacity, muted secondary line.
- Queue bars: Horizontal progress bars. Emerald fill for healthy, amber for at-risk, red for overloaded.
- SLA bars: Horizontal bars with threshold markers. China's bar shows amber + warning icon.
- Activity feed: Monospace timestamps (JetBrains Mono 13px), actor name in DM Sans 600, action description in DM Sans 400. Status dot: emerald (success), amber (warning), red (breach).

### Page 2: Ingestion Monitor (`/ingestion`)

**The ONE job:** "The steward needs to see what came in from Natos and where it got stuck in order to resolve pipeline exceptions fast."

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  01 — INGESTION PIPELINE                                       │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │ RECEIVED │ ─► │NORMALIZED│ ─► │ MATCHED  │ ─► │ ROUTED   │ │
│  │    47    │    │    45    │    │    41    │    │    41    │ │
│  │          │    │  2 error │    │  4 pend. │    │          │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  02 — TODAY'S INGESTION FEED                                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ FILTERS: [All ▼] [Stage ▼] [Status ▼] [Date range]        ││
│  ├────────┬──────────────────┬────────┬────────┬──────────────┤│
│  │ TIME   │ STANDARD         │ STAGE  │ ACTION │ STATUS       ││
│  ├────────┼──────────────────┼────────┼────────┼──────────────┤│
│  │ 14:32  │ ISO 9001:2015    │ 95→WD  │ Repl.  │ [0.97] ✓    ││
│  │ 14:28  │ IEC 62368-1:2023 │ 60 Pub │ New    │ [0.84] ◐    ││
│  │ 14:15  │ GB/T 45001-2020  │ 60 Pub │ Amend  │ [0.62] ✕    ││
│  │ 13:58  │ EN 1090-2:2018   │ 90 Rev │ Review │ [pending]   ││
│  └────────┴──────────────────┴────────┴────────┴──────────────┘│
│                                                                 │
│  Confidence pills: [0.97] = emerald │ [0.84] = amber │         │
│                    [0.62] = red     │ [pending] = muted        │
└─────────────────────────────────────────────────────────────────┘
```

**Key widgets:**
- **Pipeline funnel:** Four connected step cards showing volume at each stage. Arrows between steps. Error/pending counts in amber/red.
- **Ingestion table:** Sortable, filterable. Confidence Score Pill is the visual anchor per row. Click any row → navigates to Match Detail.

### Page 3: Match Results (`/matches`)

**The ONE job:** "The user needs to triage matches by confidence tier in order to prioritize expert review and resolve exceptions."

**Layout:** Three-tab view organized by confidence tier:

- **Tab 1: Auto-Match (> 0.95)** — Green-tinted header. Table of auto-processed matches. Sampling checkbox for periodic review.
- **Tab 2: Expert Review (0.70-0.95)** — Amber-tinted header. Table of matches awaiting TCC decision. Priority sort by risk score.
- **Tab 3: Manual Triage (< 0.70)** — Red-tinted header. Table of exceptions for master data steward. Normalization failure details visible.

Each row shows: `Natos Standard | SAP Record | Score Pill | Affected Certs Count | Status | Assigned To`

### Page 4: Match Detail (`/matches/:matchId`)

**The ONE job:** "The steward needs to see exactly WHY the score is what it is in order to decide whether to accept, correct, or escalate the match."

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Results    Match #M-2026-0412   Score: [0.84]       │
│                                                                 │
│  01 — NORMALIZATION TRACE                                      │
│  ┌───────────────────────────┐ ┌───────────────────────────────┐│
│  │ NATOS SOURCE              │ │ SAP TARGET                    ││
│  │                           │ │                               ││
│  │ Raw:    "ISO 14001:2015"  │ │ Raw:    "DIN EN ISO           ││
│  │                           │ │          14001:2015-11"       ││
│  │ Step 1: lowercase         │ │ Step 1: lowercase             ││
│  │  → "iso 14001:2015"       │ │  → "din en iso 14001:2015-11"││
│  │                           │ │                               ││
│  │ Step 2: strip prefix      │ │ Step 2: strip prefix          ││
│  │  → "14001:2015"           │ │  → "14001:2015-11"           ││
│  │                           │ │                               ││
│  │ Step 3: extract version   │ │ Step 3: extract version       ││
│  │  base: "14001"            │ │  base: "14001"               ││
│  │  year: 2015               │ │  year: 2015  month: 11       ││
│  └───────────────────────────┘ └───────────────────────────────┘│
│                                                                 │
│  02 — ALGORITHM SCORES                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Levenshtein    ████████████████████░░░ 0.82                ││
│  │ Jaro-Winkler   █████████████████████░░ 0.89                ││
│  │ Token Set      █████████████████████░░ 0.91                ││
│  │ ─────────────────────────────────────────                  ││
│  │ Composite      █████████████████████░░ 0.84  [EXPERT REV] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  03 — AFFECTED CERTIFICATES (8)                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Cert #    │ Customer        │ Country │ Expiry   │ Risk│    │
│  │ TC-44210  │ Siemens AG      │ DE      │ 2027-03  │ Med │    │
│  │ TC-51893  │ Huawei Tech     │ CN      │ 2026-11  │ High│    │
│  │ TC-38771  │ Tata Motors     │ IN      │ 2027-06  │ Low │    │
│  │ ...                                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Accept Match] [Correct Mapping] [Escalate to Senior Expert]  │
└─────────────────────────────────────────────────────────────────┘
```

**Key widgets:**
- **Normalization Trace:** Two-column forensic view. Each transformation step shown as a monospace "pipeline" with arrows. Changed characters highlighted in emerald.
- **Algorithm Scores:** Horizontal bar chart per algorithm. Composite score is the bolded final row with the Confidence Score Pill.
- **Affected Certificates:** Compact data table. Risk column uses the semantic color pills.

### Page 5: TCC Queue (`/tcc`)

**The ONE job:** "The expert needs to see their assessment queue sorted by urgency in order to process the highest-risk items first."

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  01 — YOUR QUEUE (12 assessments)                              │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SORT: [Priority ▼]  FILTER: [All impacts ▼] [All stages ▼]│ │
│  ├──────┬──────────────────┬───────┬────────┬────────┬───────┤ │
│  │ PRI  │ STANDARD         │ SCORE │ CERTS  │ SLA    │ AGE   │ │
│  ├──────┼──────────────────┼───────┼────────┼────────┼───────┤ │
│  │ !!   │ IEC 62368-1:2023 │[0.84] │ 12     │ 1d 4h  │ 2.1d  │ │
│  │ !!   │ ISO 13485:2016   │[0.78] │ 8      │ 2d 12h │ 1.8d  │ │
│  │ !    │ EN 1090-2:2018   │[0.91] │ 4      │ 5d 0h  │ 0.5d  │ │
│  │ ·    │ ISO 22000:2018   │[0.88] │ 3      │ 8d 4h  │ 0.2d  │ │
│  │ ...                                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Priority: !! = urgent (SLA < 2d or high risk)                 │
│            !  = normal (SLA 2-5d)                               │
│            ·  = low (SLA > 5d)                                  │
│                                                                 │
│  SLA COLUMN: countdown timer in JetBrains Mono.                │
│  < 2 days = red bg pill.  < 5 days = amber.  > 5 days = muted.│
└─────────────────────────────────────────────────────────────────┘
```

Click any row → Assessment Workspace.

### Page 6: Assessment Workspace (`/tcc/:assessmentId`)

**The ONE job:** "The expert needs to review the delta, see who's affected, check precedent, and make a legally binding classification — all on one page."

**This is the most important page in the entire application.**

**Layout (single scrollable page, no tabs):**

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Queue    Assessment #A-2026-0847    Score: [0.84]   │
│  Standard: IEC 62368-1:2018 → IEC 62368-1:2023                │
│  Stage: 60 (Publication)  │  Assigned: Dr. M. Weber            │
│  SLA: 1d 4h remaining [██████░░░░]                             │
│                                                                 │
├─────────────────────────────┬───────────────────────────────────┤
│  01 — DELTA VIEW            │  CONTEXT SIDEBAR                 │
│                             │                                   │
│  ┌────────────┬────────────┐│  03 — HISTORICAL PRECEDENT       │
│  │ OLD (2018) │ NEW (2023) ││                                   │
│  ├────────────┼────────────┤│  IEC 62368-1:2014 → 2018         │
│  │ Clause 4.2 │ Clause 4.2 ││  Decision: Major Technical       │
│  │ [original  │ [modified  ││  By: K. Chen, 2019-03-14         │
│  │  text in   │  text with ││  Reason: New EMC test required   │
│  │  muted     │  changes   ││                                   │
│  │  color]    │  in EMERALD││  IEC 60950-1 → 62368-1           │
│  │            │  highlight]││  Decision: Major Technical       │
│  │ Clause 5.1 │ Clause 5.1 ││  By: Dr. M. Weber, 2020-11-02  │
│  │ [unchanged │ [unchanged ││  Reason: Complete standard       │
│  │  — dimmed] │  — dimmed] ││          replacement              │
│  │            │            ││                                   │
│  │ Clause 6.3 │ [REMOVED]  ││  ────────────────────────────────│
│  │ [struck    │            ││                                   │
│  │  through   │ Clause 6.3 ││  04 — MATCH FORENSICS           │
│  │  in red]   │ [NEW — in  ││  Levenshtein:  0.82             │
│  │            │  emerald]  ││  Jaro-Winkler: 0.89             │
│  │            │            ││  Token Set:    0.91             │
│  └────────────┴────────────┘│  Composite:    0.84  [REVIEW]   │
│                             │                                   │
├─────────────────────────────┴───────────────────────────────────┤
│  02 — IMPACTED POPULATION (12 certificates, 4 customers)       │
│                                                                 │
│  Aggregate Risk Score: [7.2 / 10] ████████░░                   │
│                                                                 │
│  ┌────────┬──────────────┬─────────┬──────┬────────┬──────────┐│
│  │ Cert # │ Customer     │ Country │ Risk │ Expiry │ Products ││
│  │ TC-512 │ Huawei Tech  │ CN      │ HIGH │ Nov 26 │ 3 items  ││
│  │ TC-441 │ Siemens AG   │ DE      │ MED  │ Mar 27 │ 1 item   ││
│  │ TC-387 │ Tata Motors  │ IN      │ LOW  │ Jun 27 │ 2 items  ││
│  │ TC-298 │ BSI Group    │ UK      │ MED  │ Feb 27 │ 1 item   ││
│  └────────┴──────────────┴─────────┴──────┴────────┴──────────┘│
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  05 — DECISION PANEL                                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                             ││
│  │  Impact Classification:  [Major Technical        ▼]         ││
│  │                                                             ││
│  │  Action Required:        [Re-test Required       ▼]         ││
│  │                                                             ││
│  │  Reason Code:            [New mandatory safety test ▼]      ││
│  │                                                             ││
│  │  Notes (optional):                                          ││
│  │  ┌─────────────────────────────────────────────────┐        ││
│  │  │ Clause 6.3 introduces new thermal management    │        ││
│  │  │ requirements not present in 2018 edition.       │        ││
│  │  └─────────────────────────────────────────────────┘        ││
│  │                                                             ││
│  │  [ Cancel ]                        [ Approve & Sign Off ●] ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  06 — AUDIT TRAIL FOR THIS ASSESSMENT                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ○ 2026-04-04 14:32  System   Created from match M-2026-041 ││
│  │ ○ 2026-04-04 14:35  System   Routed to TCC Expert queue    ││
│  │ ○ 2026-04-04 15:12  M.Weber  Opened for review             ││
│  │ ● NOW                                                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Critical design details:**
- **Delta View:** Two-column diff. Unchanged clauses are dimmed (`--a-text-muted`). Modified text highlighted in emerald. Removed text in red strikethrough. New text in emerald with "NEW" badge.
- **Context sidebar:** Fixed position on right side at desktop widths. Scrolls with content on mobile. Shows precedent cards and match forensics.
- **Decision Panel:** Sticky at bottom of viewport on large screens. Three mandatory dropdowns + optional textarea. "Approve" button uses `--a-accent-primary` — the ONLY emerald button on the page.
- **Audit Trail:** Vertical timeline with dots. Past events: muted dots. Current state: pulsing emerald dot.

### Page 7: Audit Trail (`/audit`)

**Layout:** Full-page filterable event log. Filters: entity type, actor, action type, date range. Each row: timestamp (JetBrains Mono) | actor | action | entity link | details expandable.

### Page 8: Notification Center (`/notifications`)

**The ONE job:** "The user needs to track which compliance alerts have been acknowledged in order to prove regulatory delivery."

**Layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  01 — DELIVERY FUNNEL                                          │
│                                                                 │
│  Dispatched ████████████████████████████████████  35            │
│  Delivered  ██████████████████████████████████░░  33            │
│  Opened     ████████████████████████░░░░░░░░░░░  24            │
│  Clicked    ██████████████████░░░░░░░░░░░░░░░░░  18            │
│                                                                 │
│  Funnel conversion: 51% click-through                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  02 — NOTIFICATION LOG                                         │
│                                                                 │
│  ┌──────┬──────────────┬──────────────┬─────┬─────┬───────────┐│
│  │ SENT │ CUSTOMER     │ STANDARD     │ LNG │ SLA │ STATUS    ││
│  │ 04/04│ Huawei Tech  │ IEC 62368-1  │ ZH  │ 12d │ Delivered ││
│  │ 04/04│ Siemens AG   │ IEC 62368-1  │ DE  │ 12d │ Opened    ││
│  │ 04/03│ Tata Motors  │ ISO 14001    │ EN  │ 8d  │ Clicked ✓ ││
│  │ 03/28│ BSI Group    │ ISO 9001     │ EN  │ 0d  │ BREACHED  ││
│  └──────┴──────────────┴──────────────┴─────┴─────┴───────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Page 9: Sales Pipeline (`/sales`)

**The ONE job:** "The sales manager needs to see which customers require follow-up in order to secure recertification revenue before compliance deadlines."

**Layout:** Kanban-style board with three columns:

| Column | Content | Visual |
|---|---|---|
| **Monitoring** | Notifications sent, within SLA | Muted cards, countdown timer |
| **At Risk** | SLA < 48h, not yet acknowledged | Amber-bordered cards, pulsing timer |
| **Escalated** | SLA breached, lead created | Red top-border, portfolio value prominent |

Each card shows: Customer name, standard affected, portfolio value (JetBrains Mono, large), SLA countdown, notification status icons (sent/delivered/opened/clicked).

### Page 10: Customer 360 (`/customers/:customerId`)

**The ONE job:** "The user needs to see everything about one customer — certificates, standards, decisions, notifications — in order to have a complete conversation."

**Layout:** Single customer page with four horizontal sections:
1. **Customer header:** Company name, country, sales area, language, contact info
2. **Certificate portfolio:** Table of all certificates with status, linked standards, expiry dates
3. **Assessment history:** All TCC decisions affecting this customer, with impact classifications
4. **Notification timeline:** All compliance alerts sent, delivery status, SLA compliance

### Pages 11-14 (Lower Priority)

| Page | Layout Notes |
|---|---|
| **Standards Explorer** | Searchable, filterable table of all 50 synthetic standards. Lifecycle stage badge per row. Click → shows linked matches and certificates. |
| **Analytics** | Time-series charts: throughput by week, match score distribution histogram, SLA compliance trend, regional volume heatmap. |
| **Settings** | Tabbed form: matching thresholds (sliders), SLA definitions (number inputs), user management (table + invite form), integration health (status cards for each stub). |
| **Login** | Centered card on `--a-bg-void`. VeloIQ logo. Email + password fields. Single emerald "Sign In" button. No decorative elements. |

---

## Part 7: Component Library

### Shared Components

| Component | Usage | Design Notes |
|---|---|---|
| `ConfidenceScorePill` | Everywhere — tables, headers, cards | JetBrains Mono score inside rounded pill. Color by tier. THE signature element. |
| `SLACountdown` | TCC Queue, Notifications, Sales cards | JetBrains Mono countdown. Color shifts as deadline approaches. |
| `BlockIndicator` | Sidebar, card headers | 3px colored left border identifying which block (cert/tcc/sales). |
| `AuditTimelineEntry` | Assessment Workspace, Audit Trail | Vertical dot + line. Timestamp + actor + action. Expandable details. |
| `DataTable` | All list pages | Sortable columns, clickable rows, filter bar. Header row in `--a-bg-elevated`. Hover: 2px emerald left border. |
| `KPICard` | Dashboard | Large JetBrains Mono metric, DM Sans label, delta indicator, 3px top border in block color. |
| `StatusBadge` | Tables, cards | Pill with semantic color + label. States: pending/in_review/approved/escalated/breached. |
| `SectionLabel` | All pages | "01 — SECTION TITLE" in DM Sans 11px, uppercase, tracked, emerald accent. JetBrains Mono for the number. |
| `DeltaViewer` | Match Detail, Assessment Workspace | Two-column diff with emerald additions, red removals, muted unchanged. |
| `NormalizationTrace` | Match Detail | Step-by-step string transformation pipeline. JetBrains Mono for all strings. |
| `DecisionPanel` | Assessment Workspace | Sticky bottom panel with dropdowns + textarea + approve button. |
| `DeliveryFunnel` | Notification Center | Horizontal bar chart showing dispatch→deliver→open→click conversion. |
| `EscalationCard` | Sales Pipeline | Kanban card with customer, value, SLA timer, notification status icons. |

### Layout Components

| Component | Details |
|---|---|
| `AppShell` | Sidebar + top bar + main content area. Sidebar collapsible. |
| `Sidebar` | 240px expanded / 60px collapsed. Block-grouped nav with badge counts. |
| `TopBar` | VeloIQ logo, global search (Cmd+K), notification bell, user avatar with role badge. |
| `PageHeader` | Back arrow + page title + breadcrumb + primary action button. |
| `FilterBar` | Horizontal strip of dropdown filters + search input + sort control. |

---

## Part 8: Interaction Patterns

### Global Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Cmd/Ctrl + K` | Global search (standards, customers, certificates) |
| `Cmd/Ctrl + /` | Toggle sidebar collapse |
| `Esc` | Close modals, cancel forms, return to list from detail |
| `J / K` | Navigate up/down in queue tables |
| `Enter` | Open selected item in detail view |

### Micro-interactions

| Interaction | Animation | Purpose |
|---|---|---|
| Confidence Score Pill hover | Scale 1.05 + tooltip with algorithm breakdown | Instant forensics without page navigation |
| SLA countdown reaches < 24h | Pulse animation (amber glow) | Urgency escalation — draws eye without being aggressive |
| "Approve" button click | Brief emerald flash + checkmark morph | Confirms the legal weight of the action |
| New ingestion event | Row slides in from top of feed with fade-in | Shows system is alive and processing |
| Audit trail entry added | Dot appears with scale-in animation | Confirms immutable record was created |

### Empty States

| Page | Empty State Content |
|---|---|
| TCC Queue (0 items) | Large JetBrains Mono "0" + "All assessments reviewed" in DM Sans. No illustration. |
| Sales Pipeline (0 escalations) | "No SLA breaches" + last-checked timestamp. |
| Match Results (no matches today) | "No Natos events ingested today" + link to trigger synthetic event (demo mode). |

---

## Part 9: Responsive Strategy

| Breakpoint | Layout Change |
|---|---|
| **>1440px** | Full layout: sidebar expanded + main content + context sidebar (Assessment Workspace) |
| **1024-1440px** | Sidebar collapsed to icons. Context sidebar becomes a collapsible panel. |
| **768-1024px** | Sidebar becomes top hamburger menu. Single-column layouts. Tables become scrollable. |
| **<768px** | Not a primary target (this is a desktop professional tool). Basic mobile: stacked cards, simplified tables. |

**Primary design target:** 1280px-1440px (most common analyst workstation resolution).

---

## Part 10: Demo Flow (Pre-Configured Walkthrough)

For the demo with Suneesh and Sumedha, the UI includes a **Demo Mode** toggle (Settings page) that:

1. Seeds fresh synthetic data
2. Shows a guided overlay highlighting key features
3. Allows triggering synthetic Natos events on demand
4. Auto-advances SLA timers to show escalation behavior
5. Includes a "Reset Demo" button

### Demo Script Pages in Order

```
Login → Dashboard (health check) → Ingestion Monitor (trigger event) 
→ Match Detail (forensics) → TCC Queue (see it arrive) 
→ Assessment Workspace (full review + approve) 
→ Notification Center (see alerts fire) → Sales Pipeline (see SLA breach) 
→ Customer 360 (full customer context) → Dashboard (updated metrics)
```

**Total demo duration:** 12-15 minutes for full walkthrough.

---

## Anti-Slop Verification

```
[x] No hero with gradient text — the dashboard leads with KPI cards
[x] No three-column feature cards — this is a data application, not a SaaS landing page
[x] No cookie-cutter glassmorphism — borders define edges, not blur
[x] No purple/blue gradient — emerald is THE accent, used sparingly
[x] No generic "dark theme" — Context A tokens with precise obsidian hierarchy
[x] No light-mode layout with dark background slapped on — born dark
[x] No more than 1 accent active per screen area — emerald marks the active thing
[x] No Inter — DM Sans for text, JetBrains Mono for data
[x] Sidebar nav exists because 14 pages across 3 blocks genuinely needs it
[x] The Confidence Score Pill is the unforgettable signature element
```

---

*This document serves as the design specification for the VeloIQ POC frontend. Implementation begins with the component library and AppShell, followed by the P0 pages in order: Dashboard, TCC Queue, Assessment Workspace, Match Detail, Notification Center, Sales Pipeline.*
