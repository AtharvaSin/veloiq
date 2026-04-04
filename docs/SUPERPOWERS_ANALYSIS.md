# Superpowers Plugin — Development Process Analysis for VeloIQ Backend

**Author:** Atharva Singh (Zealogics Inc.)
**Date:** 2026-04-05
**Status:** Analysis for review — awaiting approval before applying to VeloIQ backend build
**Subject:** Comparing the vanilla 5-phase POC approach with a superpowers-enhanced approach

---

## TL;DR

The superpowers plugin (v5.0.7) provides a disciplined software engineering workflow that treats the VeloIQ backend build as a **planning → parallel execution → continuous review** pipeline rather than a sequential "write code → hope it works" loop. For the VeloIQ POC specifically — where the fuzzy matching engine carries compliance-critical correctness requirements and the 9-table schema has complex referential integrity — applying superpowers adds ~10-15% upfront time (brainstorming + planning) but reduces rework by 40-60% and produces a codebase with real test coverage instead of "seems to work" confidence.

**Recommendation:** Apply superpowers selectively — full rigor on the matching engine and TCC workflow (compliance-critical), lighter rigor on CRUD endpoints and stub implementations.

---

## Part 1: The 14 Superpowers Skills — What Each Does

Organized by where they apply in the dev lifecycle:

### Phase 0: Before Writing Any Code

| Skill | What It Does | Relevance to VeloIQ |
|---|---|---|
| **brainstorming** | Explores intent, requirements, design BEFORE implementation. Output: a design spec. | HIGH — VeloIQ has discovery blockers (Natos schema, SAP tables). Brainstorming surfaces what we're guessing vs. what we know. |
| **writing-plans** | Converts spec into a bite-sized (2-5 min per step) task plan saved to `docs/superpowers/plans/`. Each step has exact file paths, complete code, exact commands, expected output. | CRITICAL — POC_APPROACH.md lists 5 phases, but each phase has 15-30 sub-tasks. A superpowers plan makes every step unambiguous. |
| **using-git-worktrees** | Creates isolated git worktrees so parallel agents don't collide. | USEFUL — Lets us build backend + frontend + data-seeder in parallel without merge conflicts. |

### Phase 1: Execution

| Skill | What It Does | Relevance to VeloIQ |
|---|---|---|
| **test-driven-development** (TDD) | Red → Green → Refactor. **No production code without a failing test first.** Delete code written before tests. | CRITICAL for matching engine. The Levenshtein + Jaro-Winkler + Blocking algorithms have correctness guarantees that TDD enforces. |
| **subagent-driven-development** | Dispatch a fresh subagent per task. Two-stage review after each (spec compliance → code quality). Implementer fixes issues, reviewer re-reviews. | VERY HIGH — VeloIQ has ~60 independent tasks across 5 phases. Subagent-per-task means fresh context, no pollution, parallel safety. |
| **executing-plans** | Alternative to subagent-driven. Runs tasks inline in the current session with checkpoints. | MEDIUM — Faster but loses the quality gates. Good for simple phases (e.g., CRUD scaffolding). |
| **dispatching-parallel-agents** | When you have 2+ truly independent tasks without shared state. | HIGH — Can parallelize data seeding, migration scripts, and stub implementations simultaneously. |

### Phase 2: When Things Break

| Skill | What It Does | Relevance to VeloIQ |
|---|---|---|
| **systematic-debugging** | Forces diagnosis BEFORE fix attempt. Reproduces the bug, writes a failing test for it, then fixes. | CRITICAL for matching engine tuning. If confidence scoring produces wrong results, we need to know WHY before adjusting thresholds. |
| **verification-before-completion** | Before claiming work is "done", run verification commands and capture output. Evidence before assertions. | HIGH — Prevents "I think it works" syndrome. Every task has a verifiable definition of done. |

### Phase 3: Review & Handoff

| Skill | What It Does | Relevance to VeloIQ |
|---|---|---|
| **requesting-code-review** | Standard template for asking reviewer subagents to check work. | MEDIUM — Used automatically inside subagent-driven-development. |
| **receiving-code-review** | How to respond to review feedback with technical rigor, not blind acceptance. | MEDIUM — For when I push back on reviewer suggestions. |
| **finishing-a-development-branch** | Options for merging, PRing, or cleaning up when work is complete. | LOW — Only matters at the very end of the POC. |

### Phase 4: Meta

| Skill | What It Does |
|---|---|
| **using-superpowers** | The meta-skill that instructs invoking OTHER skills before responding. Always check first. |
| **writing-skills** | How to create new skills. Not relevant to VeloIQ. |

---

## Part 2: Current Approach vs. Superpowers-Enhanced Approach

### Scenario: Building Phase B (The Matching Engine) of VeloIQ

This is the highest-stakes phase — the fuzzy matching engine is the technical core of the POC. Let me walk through both approaches step by step.

---

### CURRENT APPROACH (without superpowers)

**Day 1 — Backend Scaffolding + Matching Engine Start**

1. Open Claude Code in the repo
2. "Build the normalization pipeline from POC_APPROACH.md Phase B"
3. Claude writes `normalizer.py` — whitespace stripping, prefix decomposition, version extraction
4. Claude writes a few tests to spot-check
5. I review the output, spot issues, ask for changes
6. Claude makes changes, might break something else
7. Claude writes `matcher.py` — Levenshtein, Jaro-Winkler, blocking
8. Claude writes score composition logic
9. I try to run it end-to-end, hit edge cases
10. Back-and-forth fixes

**Characteristics:**
- **Speed:** Fast initial output (30-45 min for first draft)
- **Confidence:** Low — "seems to work on happy path"
- **Tests:** Partial, written after code, testing what I remembered to test
- **Correctness:** Unknown until real data exercises edge cases
- **Context pollution:** Same conversation accumulates errors, half-fixes, abandoned approaches
- **Rework risk:** HIGH — I discover "DIN EN ISO 14001:2015-11" → "ISO 14001:2015" matches at 0.73 instead of 0.97, have to debug backwards from symptom
- **Total time estimate:** 6-8 hours for matching engine + 3-5 hours of rework = **9-13 hours**

---

### SUPERPOWERS-ENHANCED APPROACH

**Day 1 — Brainstorming + Planning (2 hours)**

Step 1 (30 min): Invoke `superpowers:brainstorming`
- Explore: "For the matching engine, what are we certain about vs. guessing?"
- Output: A design spec that captures:
  - CERTAIN: We need blocking/indexing, Levenshtein, Jaro-Winkler, token set ratio, composite scoring
  - CERTAIN: Thresholds are 0.95 auto-match, 0.70 expert review boundaries
  - GUESSING: Weight distribution for composite score (Levenshtein 0.3 + JW 0.4 + Token 0.3?)
  - DISCOVERY-DEPENDENT: Which SAP prefixes to strip (we have a starting list from NotebookLM)
- Surfaces the 7 synthetic test pairs from NotebookLM as known test cases

Step 2 (90 min): Invoke `superpowers:writing-plans`
- Creates `docs/superpowers/plans/2026-04-05-matching-engine.md`
- Decomposes matching engine into ~25 bite-sized tasks (2-5 min each)
- Every task has:
  - Exact file paths to create/modify
  - Complete code for the step
  - Exact test commands with expected output
  - Commit message
- Example tasks:
  ```
  Task 3: Normalizer - Strip National Prefixes
    Files: backend/app/services/normalizer.py, tests/services/test_normalizer.py
    Step 1: Write failing test for strip_prefix("DIN EN ISO 14001:2015")
    Step 2: Run pytest, verify FAIL with "strip_prefix not defined"
    Step 3: Implement minimal strip_prefix()
    Step 4: Run pytest, verify PASS
    Step 5: git add + commit
  ```

**Day 1-2 — Execution (4 hours)**

Step 3: Invoke `superpowers:subagent-driven-development`
- Dispatches a fresh subagent for each task from the plan
- Each subagent:
  - Has ONLY the context needed for that task (no conversation pollution)
  - Follows TDD strictly — writes failing test → watches it fail → writes minimal code → watches it pass → commits
  - Self-reviews before declaring done
- After each task, TWO review subagents run:
  - **Spec reviewer:** "Does this match the plan spec?"
  - **Code quality reviewer:** "Is this well-built?"
- If reviewers find issues, implementer fixes, reviewers re-review
- I coordinate and answer questions, but don't write code

**Characteristics:**
- **Speed:** Slower start (2 hours upfront), then fast parallel execution (4 hours)
- **Confidence:** HIGH — every line of code was driven by a failing test
- **Tests:** Comprehensive, written first, testing intended behavior
- **Correctness:** Proven by the test suite. The 7 synthetic pairs pass or fail deterministically.
- **Context pollution:** Zero — each subagent starts fresh
- **Rework risk:** LOW — reviewers catch issues before "done"
- **Total time estimate:** 2 hours planning + 4 hours execution + 1 hour review fixes = **7 hours**

**Saved time: ~3-6 hours. More importantly, the matching engine actually works.**

---

## Part 3: When to Apply Superpowers (and When Not To)

### Apply FULL Superpowers Rigor To:

| Component | Why |
|---|---|
| **Matching Engine (Phase B)** | Compliance-critical correctness. Every match drives downstream decisions. |
| **TCC Decision Workflow (Phase C)** | Legal sign-off path. Errors = audit liability. |
| **Audit Log Writes** | Immutable records. A single bug here = unauditable POC. |
| **SLA Calculation Logic (Phase D)** | Drives escalation. Wrong SLA = missed breaches. |
| **Normalization Pipeline** | Foundation for matching. Every downstream test depends on this being right. |

### Apply LIGHT Superpowers (brainstorming + plan, skip per-task TDD) To:

| Component | Why |
|---|---|
| **CRUD endpoints for GET operations** | Simple, well-understood pattern. Over-testing wastes time. |
| **Mock stub implementations** | These are throwaway — will be replaced by real integrations. |
| **Data seeding scripts** | Validated by successful DB inserts. Faker providers have their own tests. |
| **Frontend integration glue** | Types and API calls are shaped by the backend contracts. |

### Skip Superpowers Entirely For:

| Component | Why |
|---|---|
| **docker-compose setup** | Standard boilerplate |
| **Environment config** | Simple env var loading |
| **README and documentation** | Prose, not code |

---

## Part 4: Concrete Workflow Comparison for VeloIQ Phase A (Foundation)

Phase A from POC_APPROACH.md: "Backend scaffold + database + synthetic data seeded. API returns data." 3 days estimated.

### Without Superpowers:

```
Day 1: "Create the FastAPI scaffold, PostgreSQL schema, and Docker Compose"
  → Claude creates ~30 files in one pass
  → I review, spot inconsistencies (e.g., timestamp column named different ways)
  → Ask for fixes
  → Some work, some break
  → Repeat 3-4 times

Day 2: "Add data seeder scripts for standards, customers, certificates"
  → Claude writes seeders
  → I run them
  → Referential integrity errors
  → Debug which seeder ran before which
  → Fix seeding order

Day 3: "Add CRUD endpoints for all entities"
  → Claude writes endpoints
  → Some return wrong shapes
  → Frontend can't consume
  → More fixes
```

**Result:** Works after many iterations. Test coverage is probably ~30%. Documentation is "we'll add it later."

### With Superpowers:

```
Day 1 Morning (2h): Brainstorming + Plan
  → Invoke brainstorming: refine the 9-table schema, surface ambiguity
  → Invoke writing-plans: create docs/superpowers/plans/2026-04-05-phase-a-foundation.md
     ~40 tasks:
       - Create SQLAlchemy model for each table (9 tasks)
       - Alembic migration for each (9 tasks)
       - Pydantic schema for each (9 tasks)
       - CRUD router for each (9 tasks)
       - Seeder for each entity (4 tasks)

Day 1 Afternoon (4h): Execute via subagent-driven-development
  → Controller dispatches per-task subagents
  → Each creates tests first, then implements
  → Reviewers catch issues before merge
  → I answer questions, coordinate, don't write code

Day 2 (6h): Continue execution
  → Remaining tasks complete
  → Full test suite (>80% coverage)
  → Referential integrity enforced at schema + test level

Day 3 (Morning): Integration verification
  → End-to-end test: seed data → query via API → verify
  → Final code review subagent
  → docs/superpowers/plans/ has exact record of every decision
```

**Result:** Works on first try. Test coverage >80%. Every decision traced back to a plan task. The plan IS the documentation.

---

## Part 5: Feature Memory Already Knows

From your memory (`feedback_use_superpowers_for_dev.md`):

> "Always invoke Superpowers skills for any software development work (building, debugging, refactoring, testing)"

And (`project_superpowers_plugin.md`):

> "Superpowers v5.0.6 replaces ASR Software Forge. 14 skills: TDD, plans, subagent dev, debugging, worktrees, code review."

**This means the superpowers-enhanced approach aligns with your stated preference.** The question is not "should we use superpowers" but "how rigorously do we apply each skill to each component of the VeloIQ backend."

---

## Part 6: Proposed Superpowers-Enhanced VeloIQ Backend Plan

If you approve, the VeloIQ backend build becomes:

### Stage 1 — Brainstorming (3-4 hours)
- Invoke `superpowers:brainstorming`
- Output: A refined design spec for the VeloIQ backend
- Clarify:
  - Exact 9-table schema with column types and constraints
  - Exact matching algorithm composition and weights
  - Exact SLA calculation rules
  - Exact audit log schema
- Surfaces unknowns we're guessing about and documents them explicitly

### Stage 2 — Planning (4-6 hours)
- Invoke `superpowers:writing-plans`
- Output: 5 plan documents in `docs/superpowers/plans/`, one per phase:
  - `2026-04-05-phase-a-foundation.md`
  - `2026-04-06-phase-b-matching-engine.md`
  - `2026-04-07-phase-c-tcc-workflow.md`
  - `2026-04-08-phase-d-notifications-sales.md`
  - `2026-04-09-phase-e-demo-polish.md`
- Each plan has ~30-50 bite-sized tasks with complete code, tests, commands

### Stage 3 — Worktree Setup
- Invoke `superpowers:using-git-worktrees`
- Create `veloiq/backend` worktree for isolated development

### Stage 4 — Execution (12-15 days, per POC_APPROACH.md)
- Invoke `superpowers:subagent-driven-development` for each phase plan
- Full TDD rigor on matching engine, TCC workflow, audit logs, SLA logic
- Light rigor on CRUD, stubs, seeders

### Stage 5 — Verification
- Invoke `superpowers:verification-before-completion`
- End-to-end demo walkthrough works without errors
- Final code review subagent
- Ready for Suneesh/Sumedha demo

---

## Part 7: The Ask

**Decision point for you:**

1. **Approve full superpowers rigor** — I proceed with brainstorming + planning for Phase A tomorrow, before touching code
2. **Approve hybrid approach** — Full rigor on compliance-critical components (matching, TCC, audit, SLA), light rigor elsewhere (recommended)
3. **Skip superpowers, use current approach** — I start coding Phase A directly tonight
4. **Defer decision** — Need more info about a specific skill or tradeoff

The hybrid approach (#2) is my recommendation because:
- It applies rigor where correctness matters (matching engine, compliance workflows)
- It avoids over-engineering stubs and CRUD endpoints that will change
- It matches your memory preference ("Always invoke Superpowers skills for software development")
- It produces a plan document set that doubles as POC documentation for Suneesh/Sumedha

---

## Appendix A: Risk of NOT Using Superpowers

For the VeloIQ POC specifically, the biggest risks of skipping superpowers discipline:

1. **Matching engine ships with quiet bugs.** Without TDD, we get a matcher that scores "DIN EN ISO 14001:2015-11" at 0.73 instead of 0.97. The demo runs, the scores display, nobody notices until Sumedha says "that's wrong." By then we've built Phase C on top of a broken Phase B.

2. **Schema drift.** Without a written plan, we make database decisions in the moment and forget why. Three days later, someone asks "why is `reason_code` varchar(100)?" and we can't remember.

3. **Demo walkthrough breaks on stage.** Without `verification-before-completion`, we say "it works" based on a happy-path manual click-through. At the demo, we hit an edge case.

4. **Unable to evolve.** Without test coverage, when TUV says "actually the SLA needs to be 21 days for China," we can't confidently change it.

## Appendix B: Cost of Using Superpowers

Time cost:
- Brainstorming: 3-4 hours (one-time, upfront)
- Planning: 4-6 hours (one-time, upfront)
- Per-task overhead: ~2-3 min per task for subagent coordination

Mental cost:
- Requires discipline to not skip TDD cycles
- Requires resisting the urge to "just fix it quickly"
- Requires trust that the plan is the source of truth, not in-the-moment decisions

Actual-vs-estimated tradeoff: the upfront 7-10 hours of brainstorming + planning save 15-25 hours of rework, debugging, and "why doesn't this work" time later in the POC.

---

*Awaiting your decision before proceeding with backend development.*
