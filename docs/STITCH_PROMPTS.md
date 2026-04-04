# VeloIQ — Stitch Generation Prompts

**Usage:** Open each prompt below in Google Stitch as a separate screen within one project. Start with Screen 1 (System Dashboard) to establish the visual language, then generate remaining screens in order. Attach `UI_UX_DESIGN.md` and `POC_APPROACH.md` as context files when creating the project.

**Project name in Stitch:** `VeloIQ — Standards Automation Platform`

---

## Master Design System Brief

> Copy this block into every screen prompt as the design system section, OR set it once as the Stitch project-level design system.

```
DESIGN SYSTEM (REQUIRED — apply to every screen):

Platform: Web, Desktop-first (1280px-1440px primary target)
Theme: Dark, operational command center aesthetic — precision instrument feel
Font Import: DM Sans (400, 600, 700, 800) + JetBrains Mono (400, 600)

BACKGROUNDS (obsidian hierarchy — never use pure black):
- Page Background: Deep Obsidian (#0d0d14)
- Card/Panel Surface: Dark Surface (#12121e)
- Elevated Surface (hover, active rows): Elevated (#1a1a2e)
- Deepest (sidebar, overlays): Void (#0a0a0a)
- Borders/Dividers: Subtle Border (#1f1f35)

ACCENT COLORS (use sparingly — emerald appears max 3-5 times per screen):
- Primary Accent: Emerald (#00D492) — active state, primary CTA, key metric ONLY
- Warning: Amber (#E8B931) — at-risk items, medium confidence, caution states
- Danger: Coral Red (#FF6B6B) — breached SLA, low confidence, errors, destructive
- Muted: Dark Gray (#606060) — inactive, disabled, pending states

BLOCK IDENTITY COLORS (thin top-borders and sidebar indicators ONLY, never as fills):
- Certification Block: Sky Blue (#0EA5E9)
- TCC Block: Purple (#8B5CF6)
- Sales Block: Green (#22C55E)

TEXT HIERARCHY:
- Headings: Off-White (#EEEAE4) in DM Sans 700-800
- Body text: Warm Gray (#A09D95) in DM Sans 400
- Labels/Captions: Muted (#606060) in DM Sans 600 uppercase tracked (letter-spacing 0.15em)
- Data/Metrics/IDs/Timestamps: ALWAYS JetBrains Mono — never DM Sans for numbers
- Large metrics: JetBrains Mono 600 at 32-48px in Off-White (#EEEAE4)
- Section labels: "01 — SECTION TITLE" pattern — number in JetBrains Mono emerald, title in DM Sans uppercase

COMPONENT RULES:
- Cards: (#12121e) surface, 1px (#1f1f35) border, 8px radius. NO box-shadow. Border defines edge.
- Tables: Header row (#1a1a2e), alternating rows (#12121e / #0d0d14). Hover row gets 2px emerald left border.
- Buttons — Primary: Emerald (#00D492) bg, dark text. ONE per screen section max.
- Buttons — Secondary: Transparent, 1px (#1f1f35) border, (#A09D95) text.
- Buttons — Danger: (#FF6B6B) text, transparent bg, red border on hover.
- Border radius: 4px (tight elements), 8px (cards), 12px (modals). Never > 12px.
- Spacing: Generous between sections (64px), tight within components (8-16px).

SIGNATURE ELEMENT — Confidence Score Pill:
- A pill-shaped badge displaying a similarity score (e.g., "0.84") in JetBrains Mono 600
- Score > 0.95: Emerald (#00D492) text on (#00D492) at 10% opacity background
- Score 0.70-0.95: Amber (#E8B931) text on (#E8B931) at 10% opacity background
- Score < 0.70: Red (#FF6B6B) text on (#FF6B6B) at 10% opacity background
- 4px radius, horizontal padding 8px, vertical padding 2px
- This pill appears on every table row that involves a match result

ANTI-PATTERNS (never do these):
- No glassmorphism or blur effects
- No gradient text
- No illustrations or decorative icons
- No Inter, Roboto, or system-ui fonts
- No box-shadows on dark surfaces
- No more than one accent color dominating any section
- No border-radius > 12px
- No light mode or white backgrounds anywhere
```

---

## Screen 1: System Dashboard (P0)

```
VeloIQ System Dashboard — the command center overview for an enterprise standards automation platform. This is the landing page after login. Designed for operations leadership who need a 15-second health check of the entire pipeline.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Full-width content area with a fixed left sidebar navigation. The sidebar is 240px wide on a Void (#0a0a0a) background with navigation items grouped into three blocks separated by thin (#1f1f35) dividers. Each block group has a 3px left border in its block color: Sky Blue (#0EA5E9) for Certification items, Purple (#8B5CF6) for TCC items, Green (#22C55E) for Sales items. The active nav item has an Emerald (#00D492) left border and (#1a1a2e) background. Sidebar items show small JetBrains Mono badge counts (e.g., "12") for pending items.

Top bar spans the full width above the content area: left-aligned "VeloIQ" wordmark in DM Sans 700 off-white, right-aligned search input (pill-shaped, (#12121e) bg, magnifying glass icon), notification bell icon with red dot indicator, and a user avatar circle with "Dr. M. Weber" name and "TCC Expert" role badge.

MAIN CONTENT (scrollable, 4 sections):

Section 1 — "01 — PIPELINE STATUS"
Section label in emerald JetBrains Mono "01" + DM Sans uppercase "PIPELINE STATUS".
Four KPI metric cards in a horizontal row:
- Card 1: "47" (JetBrains Mono 36px off-white) with label "Ingested Today" (DM Sans 12px muted). Delta "+12%" in emerald. 3px Sky Blue (#0EA5E9) top border.
- Card 2: "41" with label "Matched Today". Delta "+8%" in emerald. 3px Sky Blue top border.
- Card 3: "38" with label "Assessed Today". Delta "-3%" in coral red. 3px Purple (#8B5CF6) top border.
- Card 4: "35" with label "Notified Today". Delta "+15%" in emerald. 3px Green (#22C55E) top border.
Cards use (#12121e) surface, 1px (#1f1f35) border, 8px radius.

Below the cards: a 7-day throughput trend area chart. X-axis shows days (Mon-Sun) in JetBrains Mono muted text. Two lines: "Ingested" in muted gray, "Assessed" in emerald with 10% opacity fill beneath it. Dark background (#12121e) card with border.

Section 2 — "02 — QUEUE HEALTH"
Two side-by-side cards:
- Left card "TCC Expert Queue": "12 pending" in DM Sans body text. Horizontal progress bar (80% filled in amber (#E8B931), remaining in (#1f1f35)). Below: "Oldest: 2.4 days" and "Avg response: 4.2h" in JetBrains Mono muted.
- Right card "Exceptions Queue": "3 pending". Progress bar (20% filled in coral red). Below: "Oldest: 1.1 days" and "Avg response: 8.1h".

Section 3 — "03 — SLA COMPLIANCE"
Two-column layout:
- Left (wider): "SLA Compliance by Region" — five horizontal bar rows. Each row: region name in DM Sans (Germany, India, UK, China, USA), horizontal bar filled proportionally, percentage in JetBrains Mono. Germany 96% (emerald fill), India 91% (emerald), UK 89% (amber), China 72% (coral red with a small warning triangle icon), USA 94% (emerald).
- Right (narrower): "Breached (5)" — a compact list of customer names with "Xd overdue" in coral red JetBrains Mono. Each row is a mini card with company name in DM Sans 600 and overdue duration.

Section 4 — "04 — RECENT ACTIVITY"
A vertical activity feed in a single card. Each row: timestamp in JetBrains Mono 13px muted | actor name in DM Sans 600 off-white | action description in DM Sans 400 warm gray | status dot (emerald for success, amber for warning, red for breach). Show 5-6 rows of realistic compliance activity like "Auto-matched ISO 9001:2015 → 3 certs", "Approved IEC 62368-1 assessment", "SLA breach: Huawei — IEC 61000-4-2".

OVERALL FEEL: Dense but organized. Like a flight control dashboard — every pixel earns its space. The eye flows from KPI cards → trend → queues → SLA → activity feed in a natural Z-pattern scan.
```

---

## Screen 2: TCC Queue (P0)

```
VeloIQ TCC Expert Queue — the task queue where technical compliance experts see their pending assessments sorted by urgency. This is a "triage table" designed for fast scanning and prioritization.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar as Dashboard (carried over from Screen 1). Active sidebar item: "TCC Queue" under the TCC block group (Purple left border indicator).

MAIN CONTENT:

Page header: "TCC Queue" in DM Sans 700 24px off-white. Right-aligned: "12 assessments" count in JetBrains Mono muted.

Section 1 — "01 — YOUR QUEUE"
A filter bar at the top of the table: three dropdown selects ("Sort: Priority", "All impacts", "All stages") in (#12121e) surface with (#1f1f35) border, plus a search input. All in DM Sans 400.

Below: a data table filling the full content width.
Table header row: (#1a1a2e) background with columns: PRI | STANDARD | SCORE | CERTS | SLA | AGE | ASSIGNED. Column headers in DM Sans 600 11px uppercase tracked muted text.

Table rows (show 8 rows of realistic data):

Row 1 (urgent): Priority shows double exclamation "!!" in coral red. Standard: "IEC 62368-1:2023" in DM Sans 400 off-white. Score: Confidence Score Pill showing "0.84" in amber text on amber 10% bg, JetBrains Mono 600, 4px radius pill. Certs: "12" in JetBrains Mono. SLA: "1d 4h" in JetBrains Mono inside a coral red background pill (SLA < 2 days). Age: "2.1d" in JetBrains Mono muted. Assigned: "Dr. M. Weber".

Row 2 (urgent): "!!" red. "ISO 13485:2016". Score pill "0.78" amber. Certs "8". SLA "2d 12h" amber pill. Age "1.8d".

Row 3 (normal): "!" amber. "EN 1090-2:2018". Score pill "0.91" amber (close to green). Certs "4". SLA "5d 0h" in muted text (safe). Age "0.5d".

Row 4-8: additional rows with decreasing urgency — single dot "·" priority, higher scores, longer SLA times, progressively more muted visual treatment.

Each row: (#12121e) background. On hover: (#1a1a2e) background with a 2px emerald left border appearing. Rows are clickable (cursor pointer) — they navigate to the Assessment Workspace.

Below the table: a subtle legend bar in muted text: "!! = urgent (SLA < 2d or high risk) | ! = normal (SLA 2-5d) | · = low (SLA > 5d)"

VISUAL SIGNATURE: The Confidence Score Pills in the SCORE column create a color pattern down the table — amber, amber, amber, then gradually shifting to emerald for lower-priority items. The SLA column countdown timers shift from red pills to amber to plain muted text. Together these two columns form a "heat gradient" that the expert's eye scans instantly.

OVERALL FEEL: Clean, scannable, no-nonsense task list. Every row is a decision waiting to happen. The color coding does the prioritization work so the expert doesn't have to think — just start from the top.
```

---

## Screen 3: Assessment Workspace (P0 — Most Important Screen)

```
VeloIQ Assessment Workspace — the full-context expert review page where a TCC technical expert makes a legally binding classification decision on a standards match. This is the MOST IMPORTANT screen in the entire application. Everything the expert needs is on ONE scrollable page — no tabs, no modals, no page switching.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar (collapsed to 60px icon-only mode to maximize workspace) and top bar.

PAGE HEADER:
Left: back arrow icon + "Back to Queue" link in muted text. Center: "Assessment #A-2026-0847" in DM Sans 700 20px. Right: Confidence Score Pill "0.84" in amber, large size (JetBrains Mono 16px).

Below header: a context bar spanning full width in (#12121e) surface:
- "Standard: IEC 62368-1:2018 → IEC 62368-1:2023" in DM Sans 400 off-white (arrow in emerald)
- "Stage: 60 (Publication)" in muted
- "Assigned: Dr. M. Weber" in muted
- Right side: "SLA: 1d 4h remaining" in JetBrains Mono amber with a horizontal progress bar (60% elapsed, amber fill)

MAIN CONTENT (two-column layout: 65% left / 35% right sidebar):

LEFT COLUMN:

Section 1 — "01 — DELTA VIEW"
A side-by-side comparison panel in a single card. Two columns inside the card:
- Left column header: "OLD (2018)" on a muted background strip
- Right column header: "NEW (2023)" on a muted background strip

Content shows clause-by-clause comparison:
- "Clause 4.2 — Thermal Management": Left side shows original text in DM Sans 400 muted color. Right side shows modified text with changed words/phrases highlighted in emerald (#00D492) background at 15% opacity with emerald text.
- "Clause 5.1 — EMC Requirements": Both sides show identical text, both dimmed to (#606060) to indicate no change. A small "No change" tag in muted.
- "Clause 6.3 — Safety Testing": Left side shows text with coral red strikethrough indicating removal. Right side shows entirely new text with emerald "NEW" badge and emerald-highlighted content.
- Show 4-5 clause pairs with realistic technical standards language about electrical safety testing.

The card has 1px (#1f1f35) border, 8px radius, and a thin 3px Purple (#8B5CF6) top border indicating TCC block.

Section 2 — "02 — IMPACTED POPULATION"
Below the delta view. A card showing:
- Header row: "12 certificates across 4 customers" in DM Sans 600. Right side: "Aggregate Risk Score" with a large "7.2 / 10" in JetBrains Mono 24px off-white, next to a horizontal bar (72% filled, amber color).
- Data table below with columns: CERT # | CUSTOMER | COUNTRY | RISK | EXPIRY | PRODUCTS
- Row 1: "TC-51893" (JetBrains Mono) | "Huawei Technologies" | "CN" with a small flag or country code badge | Risk badge "HIGH" in coral red pill | "Nov 2026" | "3 products"
- Row 2: "TC-44210" | "Siemens AG" | "DE" | "MED" amber pill | "Mar 2027" | "1 product"
- Row 3: "TC-38771" | "Tata Motors" | "IN" | "LOW" emerald pill | "Jun 2027" | "2 products"
- Row 4: "TC-29842" | "BSI Group" | "UK" | "MED" amber pill | "Feb 2027" | "1 product"

RIGHT COLUMN (context sidebar, sticky on scroll):

Section 3 — "03 — HISTORICAL PRECEDENT"
Two compact precedent cards stacked vertically:
- Card 1: "IEC 62368-1:2014 → 2018" in DM Sans 600. "Decision: Major Technical" with a coral red status dot. "By: K. Chen, 2019-03-14" in JetBrains Mono muted. "Reason: New EMC test required" in DM Sans 400 warm gray.
- Card 2: "IEC 60950-1 → 62368-1" in DM Sans 600. "Decision: Major Technical" with coral red dot. "By: Dr. M. Weber, 2020-11-02" in JetBrains Mono muted. "Reason: Complete standard replacement" in DM Sans 400.
Each card: (#12121e) bg, 1px border, 8px radius.

Section 4 — "04 — MATCH FORENSICS"
A compact card showing algorithm breakdown:
- "Levenshtein" label + horizontal bar (82% fill, muted) + "0.82" in JetBrains Mono
- "Jaro-Winkler" + bar (89% fill) + "0.89"
- "Token Set" + bar (91% fill) + "0.91"
- Divider line
- "Composite" + bar (84% fill, amber) + "0.84" in JetBrains Mono 600 + amber Confidence Score Pill "[EXPERT REVIEW]"

FULL WIDTH (below both columns):

Section 5 — "05 — DECISION PANEL"
A prominent card with (#1a1a2e) elevated background and a 2px emerald top border to signal "this is where you act."

Three form rows:
- "Impact Classification:" label in DM Sans 600 uppercase muted + dropdown select showing "Major Technical" with options: No Change, Administrative, Minor Technical, Major Technical, Safety Critical. Select has (#12121e) bg, (#1f1f35) border.
- "Action Required:" + dropdown showing "Re-test Required" with options: Reconfirm, Re-test Required, Certificate Suspension, Certificate Withdrawal.
- "Reason Code:" + dropdown showing "New mandatory safety test" with options: No technical change, Administrative amendment only, New mandatory safety test, Updated performance thresholds, Complete standard replacement.

Below dropdowns: "Notes (optional):" label + a textarea with 3 rows, (#12121e) bg, (#1f1f35) border, placeholder "Add decision rationale..." in muted. Pre-filled with: "Clause 6.3 introduces new thermal management requirements not present in 2018 edition."

Bottom row: left-aligned "Cancel" secondary button (transparent, border, muted text). Right-aligned "Approve & Sign Off" primary button — this is THE emerald (#00D492) button on the page, DM Sans 700, with a small checkmark icon. This is the only emerald-filled element in the entire decision panel.

Section 6 — "06 — AUDIT TRAIL"
A vertical timeline at the very bottom:
- Each entry: a small circle (dot) connected by a vertical line. Past events use muted (#606060) dots and lines.
- Entry 1: "○ 2026-04-04 14:32 — System — Created from match M-2026-0412" all in JetBrains Mono 13px muted
- Entry 2: "○ 2026-04-04 14:35 — System — Routed to TCC Expert queue"
- Entry 3: "○ 2026-04-04 15:12 — Dr. M. Weber — Opened for review"
- Entry 4: "● NOW" — this dot is emerald (#00D492) and slightly larger, indicating current state. A subtle pulse animation glow.

OVERALL FEEL: This page is a cockpit. The expert looks left (delta view — what changed), looks right (precedent — what we did before), looks down (who's affected), then acts (decision panel). No wasted space, no decorative elements. The emerald Approve button is the gravitational center of the entire page — everything above it leads to that one click.
```

---

## Screen 4: Match Detail (P0)

```
VeloIQ Match Detail — a forensic view showing exactly WHY a standards match scored what it scored. Used by master data stewards to understand the normalization and matching pipeline for a specific record. This is a diagnostic page, not a decision page.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Sidebar expanded (240px). Active item: "Matches" under Certification block.

PAGE HEADER:
Left: back arrow + "Back to Results" in muted. Center: "Match #M-2026-0412" in DM Sans 700. Right: Confidence Score Pill "0.84" amber (large).

MAIN CONTENT (single column, full width):

Section 1 — "01 — NORMALIZATION TRACE"
Two side-by-side cards of equal width, forming a visual pipeline:

Left card — "NATOS SOURCE":
A step-by-step transformation displayed as a vertical pipeline in JetBrains Mono 14px:
- "Raw:" followed by "ISO 14001:2015" in off-white on a slightly lighter (#1a1a2e) inline code block
- Arrow down (thin emerald line with small arrow)
- "Step 1: lowercase" label in DM Sans 12px muted
- Result: "iso 14001:2015" in JetBrains Mono, changed characters subtly highlighted
- Arrow down
- "Step 2: strip prefix" label
- Result: "14001:2015" (the "iso " part shown as struck-through in muted before the arrow)
- Arrow down
- "Step 3: extract version" label
- Results shown as two inline fields: base: "14001" in emerald | year: "2015" in muted

Right card — "SAP TARGET":
Same vertical pipeline format:
- Raw: "DIN EN ISO 14001:2015-11" in off-white
- Step 1: "din en iso 14001:2015-11"
- Step 2: "14001:2015-11" (stripped prefixes "din en iso " shown struck-through)
- Step 3: base: "14001" in emerald | year: "2015" | month: "11" in muted

Between the two cards at the bottom: a horizontal connector line joining both "base" results, with a checkmark icon and "Base match: 14001 = 14001" in emerald JetBrains Mono.

Section 2 — "02 — ALGORITHM SCORES"
Full-width card with three horizontal score bars stacked vertically:
- Each bar: algorithm name in DM Sans 400 (left), horizontal bar visualization (center), score in JetBrains Mono 600 (right)
- "Levenshtein" — bar 82% filled in warm gray — "0.82"
- "Jaro-Winkler" — bar 89% filled in warm gray — "0.89"
- "Token Set Ratio" — bar 91% filled in warm gray — "0.91"
- Thin divider line
- "Composite Score" — bar 84% filled in amber — "0.84" in JetBrains Mono 700 16px with amber Confidence Score Pill "[EXPERT REVIEW]"
The composite row is visually distinct: slightly larger text, amber color, bolder weight.

Section 3 — "03 — AFFECTED CERTIFICATES (8)"
Data table with columns: CERT # | CUSTOMER | COUNTRY | RISK | EXPIRY | PRODUCTS
Show 4-5 rows of realistic data. Country column shows two-letter codes (DE, CN, IN, UK). Risk column uses colored status pills: HIGH (red), MED (amber), LOW (emerald). Customer names are clickable links (underline on hover) that would navigate to Customer 360.

Bottom action bar:
Three buttons: "Accept Match" (emerald primary), "Correct Mapping" (secondary/outline), "Escalate to Senior Expert" (danger text, no fill).

OVERALL FEEL: Forensic and transparent. The normalization trace is the hero — it shows the system's work. Nothing is a black box. A data steward should look at this page and understand EXACTLY why "DIN EN ISO 14001:2015-11" scored 0.84 against "ISO 14001:2015".
```

---

## Screen 5: Ingestion Monitor (P0)

```
VeloIQ Ingestion Monitor — a real-time pipeline view showing Natos standards events as they arrive, get normalized, matched, and routed. Used by master data stewards and operations leadership to monitor pipeline health and catch exceptions.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Active: "Ingestion" under Certification block.

MAIN CONTENT:

Section 1 — "01 — INGESTION PIPELINE"
Four connected stage cards in a horizontal row representing the pipeline stages:
- Card 1: "RECEIVED" label in DM Sans 600 uppercase. Large number "47" in JetBrains Mono 32px off-white. Small text "from Natos" in muted.
- Arrow connector (thin line with chevron, emerald color) between cards
- Card 2: "NORMALIZED". Number "45". Below: "2 errors" in coral red JetBrains Mono.
- Arrow connector
- Card 3: "MATCHED". Number "41". Below: "4 pending" in amber.
- Arrow connector
- Card 4: "ROUTED". Number "41". Below: small breakdown "29 auto | 9 review | 3 manual" in muted JetBrains Mono.

Each card: (#12121e) surface, 8px radius, 1px border. Cards with errors/pending have a subtle glow or highlighted border in the appropriate warning/danger color.

Section 2 — "02 — TODAY'S INGESTION FEED"
Filter bar: four controls in a horizontal row — dropdown "All Sources", dropdown "Stage", dropdown "Status", date range picker. All in (#12121e) bg with borders.

Below: a data table filling full width.
Columns: TIME | STANDARD | STAGE | ACTION | STATUS

Row examples (show 8 rows):
- 14:32 | ISO 9001:2015 | "95 → WD" (stage badge: red bg pill "Withdrawn") | Replaced | Confidence Score Pill "0.97" emerald + checkmark icon
- 14:28 | IEC 62368-1:2023 | "60 Pub" (stage badge: emerald bg pill) | New | Score pill "0.84" amber + half-circle icon indicating "in review"
- 14:15 | GB/T 45001-2020 | "60 Pub" | Amended | Score pill "0.62" red + X icon indicating "manual triage"
- 13:58 | EN 1090-2:2018 | "90 Rev" (stage badge: amber) | Review | gray pill "[pending]" with spinner icon
- Additional rows with varied stages and statuses.

TIME column: JetBrains Mono 13px muted. STANDARD column: DM Sans 400 off-white, clickable. STAGE column: small colored badge pills. STATUS column: Confidence Score Pills — this creates the visual signature column.

OVERALL FEEL: A live operations feed. The pipeline funnel at top gives instant health. The table below is the detailed log. The eye goes: pipeline status (are we healthy?) → table (what's stuck?).
```

---

## Screen 6: Notification Center (P0)

```
VeloIQ Notification Center — tracks all compliance alert dispatches, delivery status, and proof of acknowledgment. Used by sales managers and compliance officers. This is NOT a marketing dashboard — it's a legal compliance evidence view.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Active: "Notifications" under Sales block (Green indicator).

MAIN CONTENT:

Section 1 — "01 — DELIVERY FUNNEL"
A horizontal funnel visualization in a full-width card:
Four stacked horizontal bars of decreasing width, creating a funnel shape:
- "Dispatched" label (DM Sans 400) + full-width bar in muted (#606060) + "35" count (JetBrains Mono)
- "Delivered" + slightly shorter bar in warm gray + "33"
- "Opened" + medium bar in amber (#E8B931) + "24"
- "Clicked" + shortest bar in emerald (#00D492) + "18"
Below funnel: "Funnel conversion: 51% click-through" in JetBrains Mono muted. A small "Proof of Acknowledgment" label in DM Sans 600 emerald uppercase — emphasizing the legal significance.

Section 2 — "02 — NOTIFICATION LOG"
Filter bar with dropdowns: Status (All, Delivered, Opened, Clicked, Bounced, Breached), Language, Customer, Date range.

Data table:
Columns: SENT | CUSTOMER | STANDARD | LNG | TEMPLATE | SLA | STATUS

Row examples (show 6-8 rows):
- 04/04 | Huawei Technologies | IEC 62368-1:2023 | "ZH" (small badge) | Compliance Alert | "12d" JetBrains Mono muted | "Delivered" amber status badge
- 04/04 | Siemens AG | IEC 62368-1:2023 | "DE" badge | Compliance Alert | "12d" | "Opened" emerald badge
- 04/03 | Tata Motors | ISO 14001:2015 | "EN" badge | Re-certification Notice | "8d" | "Clicked ✓" emerald badge with check
- 03/28 | BSI Group | ISO 9001:2015 | "EN" | Compliance Alert | "0d" | "BREACHED" coral red badge, bold, with warning icon
- Additional rows with varied statuses.

Language column uses small country/language code badges. SLA column: countdown in JetBrains Mono — "0d" entries are in coral red. STATUS column uses colored status badges: Delivered (amber), Opened (emerald), Clicked (emerald with check), BREACHED (coral red, bold).

OVERALL FEEL: Evidence collection. Every row is a legal record. The funnel proves the system works. The breached rows demand immediate attention. Clean, auditable, defensible.
```

---

## Screen 7: Sales Pipeline (P0)

```
VeloIQ Sales Pipeline — a Kanban-style board showing customer follow-up status after compliance notifications. Used by sales account managers to prioritize outreach for recertification revenue.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Active: "Sales Pipeline" under Sales block.

MAIN CONTENT:

Section 1 — "01 — PIPELINE"
Three Kanban columns side by side, each taking 33% width:

COLUMN 1 — "MONITORING" (header bar in muted (#606060)):
- Column header: "Monitoring" in DM Sans 600, count "18" in JetBrains Mono muted
- Stacked vertical cards (show 3):
  - Card: (#12121e) surface, 8px radius, 1px border. Inside:
    - Company: "Bosch GmbH" in DM Sans 600 off-white
    - Standard: "ISO 9001:2015" in DM Sans 400 muted
    - Portfolio value: "EUR 85,000" in JetBrains Mono 600 off-white (prominent)
    - SLA: "9d remaining" in JetBrains Mono muted with a thin emerald progress bar
    - Status icons row: ✓ Sent, ✓ Delivered, · Opened, · Clicked (small icon row)

COLUMN 2 — "AT RISK" (header bar in amber (#E8B931)):
- Column header: "At Risk" + count "4"
- Cards have a 1px amber left border:
  - "LG Electronics" | "IEC 61000-4-2:2008" | "EUR 120,000" | SLA: "1d 8h" in amber JetBrains Mono with pulsing amber dot | Status: ✓ Sent, ✓ Delivered, ✗ Not opened

COLUMN 3 — "ESCALATED" (header bar in coral red (#FF6B6B)):
- Column header: "Escalated" + count "5"
- Cards have a 2px coral red top border and slightly elevated (#1a1a2e) background:
  - "Huawei Technologies" | "IEC 62368-1:2023" | "EUR 240,000" in JetBrains Mono 700 18px (very prominent — this is the revenue at stake) | SLA: "BREACHED — 2d overdue" in coral red | "Lead created in Sales Cloud" small emerald tag | Button: "Mark as Contacted" secondary button

Show 2-3 cards per column. Cards in the Escalated column are visually heavier — larger font for the euro value, red accents, more prominent action button.

OVERALL FEEL: Sales urgency. The Kanban layout creates a left-to-right narrative: monitoring (calm) → at risk (tension) → escalated (action needed). The portfolio value in JetBrains Mono is the first thing a sales manager reads — it answers "how much money is at stake?"
```

---

## Screen 8: Customer 360 (P1)

```
VeloIQ Customer 360 — a comprehensive single-customer view showing all certificates, standards, decisions, and notifications for one customer. Used when a sales manager or TCC expert needs full context before a call or decision.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Sidebar collapsed. Back arrow: "Back to Sales Pipeline" or "Back to Notifications".

CUSTOMER HEADER (full-width banner card):
- Left: Large company name "Huawei Technologies Co., Ltd." in DM Sans 800 24px off-white
- Below: "CN" country badge (small pill) + "Sales Area: Greater China" + "Language: ZH" + "Contact: li.wei@huawei.example.com" — all in DM Sans 400 muted
- Right side: Three mini KPI boxes:
  - "4" certificates (JetBrains Mono 24px) with "Active Certificates" label
  - "EUR 360,000" total portfolio value (JetBrains Mono 24px emerald)
  - "2" open alerts (JetBrains Mono 24px amber) with "Pending Notifications" label

Section 1 — "01 — CERTIFICATE PORTFOLIO"
Data table: CERT # | PRODUCT | STANDARD | STATUS | ISSUED | EXPIRY
Show 4 rows. Status column: "Active" in emerald pill, "Expiring" in amber pill, "Suspended" in red pill. Standards column shows the standard identifier with a small Confidence Score Pill if a recent match exists.

Section 2 — "02 — ASSESSMENT HISTORY"
Compact timeline of TCC decisions affecting this customer:
Each entry: date (JetBrains Mono) | standard change description | impact classification badge (colored pill) | assessor name | reason summary. Show 3-4 entries.

Section 3 — "03 — NOTIFICATION TIMELINE"
Vertical timeline showing all compliance alerts:
Each entry: sent date | standard | template language "ZH" badge | delivery status progression (sent → delivered → opened → clicked shown as a horizontal step indicator with dots) | SLA status. Entries where SLA was breached have a coral red "BREACHED" tag and "Escalated to sales" note.

Section 4 — "04 — NOTES & FOLLOW-UP"
A simple card with a textarea for sales notes and a history of previous notes with timestamps and author names. "Add Note" secondary button.

OVERALL FEEL: Complete customer dossier. A sales manager opens this before dialing a customer and has EVERYTHING — certificates, what changed, what was decided, what was communicated, what's outstanding. No tab switching, no system hopping.
```

---

## Screen 9: Login (P0)

```
VeloIQ Login — minimal, authoritative authentication screen. No decorative elements. The dark surface and precise typography communicate "enterprise compliance system."

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

FULL PAGE LAYOUT:
Background: Void (#0a0a0a) — the deepest background, filling the entire viewport.

Centered vertically and horizontally: a single card (480px max-width).

Card contents:
- Top: "VeloIQ" wordmark in DM Sans 800 28px off-white. Below: "Standards Automation Platform" in DM Sans 400 14px muted. No logo image — just typography.
- Spacer (32px)
- "Email" label in DM Sans 600 11px uppercase tracked muted. Below: text input with (#12121e) background, 1px (#1f1f35) border, 8px radius, DM Sans 400 placeholder "you@tuv.com" in (#606060).
- Spacer (16px)
- "Password" label. Below: password input, same styling. Right side: "Forgot password?" link in emerald (#00D492) DM Sans 400 14px.
- Spacer (24px)
- "Sign In" button — full width, emerald (#00D492) background, dark text (#0d0d14) in DM Sans 700. 8px radius. The ONLY color on the page.
- Spacer (16px)
- "Demo mode? Use test credentials" link in muted text, centered.

Card: (#12121e) surface, 1px (#1f1f35) border, 12px radius (slightly larger for the login card).

Below the card: "Zealogics Inc. — Confidential" in DM Sans 400 12px muted, centered.

OVERALL FEEL: Quiet authority. The void background, single card, and one emerald button say "this is a serious system." No hero images, no gradients, no decorative elements. Typography alone carries the brand.
```

---

## Screen 10: Audit Trail (P1)

```
VeloIQ Audit Trail — a full-page, filterable, immutable event log showing every system and human action. Designed for compliance officers and auditors who need to prove regulatory accountability.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Active: "Audit Trail" under TCC block.

MAIN CONTENT:

Filter bar (prominent, full width): Five filter controls:
- "Entity Type" dropdown: All, Standard, Match, Assessment, Notification, Escalation
- "Actor" dropdown: All, System, Dr. M. Weber, K. Chen, etc.
- "Action" dropdown: All, Created, Updated, Approved, Rejected, Sent, Escalated
- Date range picker (from/to)
- "Export CSV" secondary button on the right end

Data table (full width, high density — this is a log viewer):
Columns: TIMESTAMP | ACTOR | ACTION | ENTITY | DETAILS

Show 12-15 rows of realistic audit entries:
- "2026-04-04 15:42:18" (JetBrains Mono 13px muted) | "Dr. M. Weber" (DM Sans 600 off-white) | "Approved" (emerald status badge) | "Assessment #A-2026-0847" (clickable link) | expandable chevron →
- "2026-04-04 15:42:18" | "System" (muted italic) | "Created" (muted badge) | "Notification #N-2026-1204" | expandable
- "2026-04-04 15:12:03" | "Dr. M. Weber" | "Opened" (amber badge) | "Assessment #A-2026-0847" |
- "2026-04-04 14:35:41" | "System" | "Routed" (muted) | "Assessment #A-2026-0847" | "→ TCC Expert queue"
- More entries spanning multiple entity types...

When a row's chevron is expanded: shows a JSON-like detail panel in (#0a0a0a) background with JetBrains Mono 13px, showing the full change payload — field names in muted, values in off-white, changed values highlighted in emerald.

Bottom: pagination controls in muted — "Showing 1-50 of 1,247 entries" in JetBrains Mono. Page number controls.

OVERALL FEEL: This is the regulatory evidence room. Every row is legally significant. The monospace timestamps, the expandable detail payloads, the CSV export button — all designed for an auditor who needs to prove "who did what, when, and why." Dense, precise, undecorated.
```

---

## Screen 11: Standards Explorer (P1)

```
VeloIQ Standards Explorer — a searchable, filterable reference table of all standards in the system. Used by all personas to look up a specific standard's status, linked certificates, and match history.

DESIGN SYSTEM (REQUIRED):
[Paste the Master Design System Brief above]

PAGE LAYOUT:
Same sidebar and top bar. Active: "Standards" under Certification block.

MAIN CONTENT:

Search bar (prominent, centered, 600px wide): Large search input with magnifying glass icon. Placeholder: "Search by standard ID, title, or committee..." in muted. (#12121e) bg, 12px radius (slightly larger for emphasis — this is the primary interaction).

Filter row below search: "Stage" multi-select, "Committee" dropdown, "Status" dropdown (Active, Withdrawn, Under Review).

Data table:
Columns: AC CODE | TITLE | STAGE | REPLACED BY | LINKED CERTS | LAST MATCH

Row examples (show 8-10):
- "ISO 9001:2015" (JetBrains Mono off-white) | "Quality management systems — Requirements" (DM Sans muted, truncated) | Stage badge "60" emerald pill | "—" | "23" (JetBrains Mono) | Score pill "0.97" emerald
- "IEC 62368-1:2018" | "Audio/video, IT and communication technology equipment..." | "95" red pill "Withdrawn" | "IEC 62368-1:2023" as emerald link | "12" | "0.84" amber
- "GB/T 45001-2020" | "Occupational health and safety..." | "60" emerald | "—" | "6" | "0.62" red

Stage column: colored pills — "60" (emerald = published), "95" (red = withdrawn), "90" (amber = under review), "40" (muted = enquiry).

OVERALL FEEL: Reference library. Clean search-first interface. The stage badges and score pills add color but the design stays quiet — this is a lookup tool, not a decision-making page.
```

---

## Generation Order & Tips

**Recommended generation sequence in Stitch:**

| Order | Screen | Why This Order |
|---|---|---|
| 1 | Login | Simplest — establishes dark theme and typography baseline |
| 2 | System Dashboard | Establishes the full layout shell (sidebar + top bar + content) |
| 3 | TCC Queue | Establishes the data table pattern |
| 4 | Assessment Workspace | The crown jewel — builds on all previous patterns |
| 5 | Match Detail | Reuses table patterns, adds normalization trace |
| 6 | Ingestion Monitor | Reuses table + adds pipeline funnel |
| 7 | Notification Center | Reuses table + adds delivery funnel |
| 8 | Sales Pipeline | Kanban layout — new pattern |
| 9 | Customer 360 | Combines elements from all previous screens |
| 10 | Audit Trail | Dense log table — reuses existing patterns |
| 11 | Standards Explorer | Search-first variant of existing table pattern |

**Tips for Stitch:**
- Generate Screen 2 (Dashboard) first to lock in the sidebar + top bar shell, then reference it in subsequent screens with "Same sidebar and top bar layout as the Dashboard screen"
- If Stitch defaults to light mode, re-emphasize: "Dark theme only. Page background #0d0d14. Never use white or light gray backgrounds."
- If JetBrains Mono doesn't render, substitute with "monospace font" in the prompt and note the font requirement for dev
- For the Confidence Score Pill, describe it in detail on the FIRST screen that uses it, then say "same Confidence Score Pill pattern" on subsequent screens
- Review each screen before generating the next — adjust the design system section if Stitch misinterprets any tokens
