# VeloIQ — Standards Automation Platform

**Client:** TÜV Rheinland
**Vendor:** Zealogics Inc.
**Status:** POC / Demo in progress

A compliance automation platform for product certification standards management. Automates the pipeline from Natos standards ingestion → fuzzy matching → expert review → customer notification → sales follow-up.

## Architecture

Three integrated blocks on SAP BTP:
1. **Certification Block** — Natos ingestion, normalization, fuzzy matching
2. **TCC Block** — Expert review, impact classification, audit trail
3. **Sales & Marketing Block** — Compliance notifications, SLA tracking, escalation

## POC Demo

This repository contains a synthetic-data-powered demo build that walks through the full 3-block pipeline without requiring real TÜV systems. See `docs/POC_APPROACH.md`.

## Documentation

| Document | Purpose |
|---|---|
| [POC_APPROACH.md](docs/POC_APPROACH.md) | 5-phase build plan |
| [UI_UX_DESIGN.md](docs/UI_UX_DESIGN.md) | User personas, journeys, 14-page site map |
| [PHASE_A_FOUNDATION_DESIGN.md](docs/PHASE_A_FOUNDATION_DESIGN.md) | Phase A backend design spec |
| [STITCH_PROMPTS.md](docs/STITCH_PROMPTS.md) | Google Stitch screen generation prompts |
| [SUPERPOWERS_ANALYSIS.md](docs/SUPERPOWERS_ANALYSIS.md) | Dev process analysis |

## Design System

- **Identity:** Operational command center — precision instrument aesthetic
- **Theme:** Dark obsidian surfaces (#0d0d14) with emerald accent (#00D492)
- **Typography:** DM Sans + JetBrains Mono (for all data/metrics)
- **Frontend mockups:** Generated on Google Stitch (see `docs/STITCH_PROMPTS.md`)

## Development (Phase A in progress)

Implementation follows the Superpowers workflow: spec → plan → subagent-driven execution with TDD.

Current plan: `docs/superpowers/plans/2026-04-05-phase-a-foundation.md`
