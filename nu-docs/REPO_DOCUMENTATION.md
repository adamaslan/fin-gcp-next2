# Repository Documentation — "gcp app w mcp"

## Overview

This repository implements the MCP Finance application: a full-stack technical analysis platform (Next.js frontend + FastAPI backend) with cloud automation, CI-friendly skills/hook tooling, and multiple documentation artifacts. The project mixes production-ready services (Cloud Run, Firestore, Pub/Sub), serverless automation (Cloud Functions), developer tooling, and an internal Claude/Gemini-based skills system for automation and AI-assisted analysis.

---

## High-level architecture

- Frontend: `nextjs-mcp-finance` (Next.js app). Responsible for UI, tiers, quick symbols, and user workflows.
- Backend: `mcp-finance1/cloud-run/main.py` (FastAPI app) exposing analysis endpoints, cache-backed via Firestore, Pub/Sub for async work, and integration with the `technical_analysis_mcp` Python library.
- Core analysis library: `mcp-finance1/src/technical_analysis_mcp` — contains analysis logic (indicators, signals, ranking, scanners, risk, portfolio), intended as single source-of-truth for on-demand and scheduled analyses.
- Automation: `mcp-finance1/automation/functions` — Cloud Functions (e.g., `daily_analysis`) run scheduled or triggered jobs to analyze watchlists and store results.
- DevOps & Tooling: `scripts/`, `docker-compose.yml`, `Makefile`, and helpful docs for deployments and local emulation.
- Skills/AI helpers: `.claude/` — contains skills, commands and guidance to run AI-assisted tooling and project-specific automation.
- Logs & Diagnostics: `logs/` — saved health, performance and analysis outputs for debugging and audit.

---

## Top-level files and purpose (short):

- `GUIDE.md`, `GUIDE-ENHANCED.md` — primary developer/user guides and runbooks.
- `BACKEND_IMPLEMENTATION_COMPLETE.md`, `DEPLOYMENT_GUIDE.md` — backend implementation & deployment notes.
- `scripts/` — deploy and dev setup scripts (`dev-setup.sh`, `deploy-backend.sh`, `deploy-frontend.sh`).
- `docker-compose.yml` / `docker-compose.dev.yml` — local dev stack that includes frontend, backend, and emulators.
- `.claude/` — skills, commands and templates used to automate project tasks and scaffold features.
- `mcp-finance1/` — backend and analysis code + docs and tests.
- `nextjs-mcp-finance/` — frontend app (excluded from repo in some setups; referenced in docs for local dev).
- `logs/` — health, performance, and stock-data output files used in diagnostics and CI checks.

---

## `mcp-finance1/` — Detailed

- `src/technical_analysis_mcp/` (core):
  - `analysis.py` — `StockAnalyzer` and main orchestrator for fetching data, computing indicators and producing analysis outputs.
  - `signals.py` — modular signal detectors (MA, RSI, MACD, BB, Stoch, Volume, Trend) following protocol-based detectors.
  - `indicators.py` — implementations of indicator calculations used across detectors.
  - `ranking.py` / `formatting.py` / `models.py` — formatting, ranking, and data models (Pydantic) used by the API.
  - `server.py` — programmatic server/adapter functions that the Cloud Run `main.py` calls (trade plan, scans, portfolio, morning brief).
  - `universes.py` — canonical stock universes and utilities for listing/accessing them.
  - `portfolio/`, `risk/`, `scanners/` — domain-specific components for portfolio calculation, risk analysis and scanning.

- `cloud-run/main.py` — FastAPI app, endpoints include `/api/analyze`, `/api/signals/{symbol}`, `/api/scan`, `/api/trade-plan`, `/api/portfolio-risk`, `/api/morning-brief`, plus health checks and comparison/screen endpoints. Implements caching (Firestore), Pub/Sub publishing and mock fallbacks for local testing.

- `automation/functions/daily_analysis/main.py` — Cloud Function that runs scheduled daily analysis. Notable: contains indicator calculation and signal detection code intended for scheduled runs; it references the `StockAnalyzer` but also duplicates calculations (see Redundancies section).

- `test_endpoints.sh` — integration test runner exercising endpoints / health checks and validating response structures.

- Jupyter materials & notebooks: `jupyter1/`, `guide4-jupyter.md` — used for exploration and troubleshooting.

- Prototypes & legacy implementations: `nu-fib1.py`, `nu-signals1.py`, `old_code/` — prototypes for signal/fibonacci detection and explorations; many algorithms live here too but have not been fully consolidated.

---

## `.claude/` and skills

Contains structured skills (e.g., `dev-setup.md`, `docker-security/SKILL.md`, `api-test/SKILL.md`) and command templates for repetitive tasks (db migrate, health-check, test-all). These accelerate feature scaffolding, tests and security checks.

---

## Frontend (`nextjs-mcp-finance`)

Key frontend artifacts referenced in docs:
- `src/lib/auth/tiers.ts` — tier limits and feature gating.
- `src/components/ui/command-palette.tsx` — quick symbols UI.
- `MCP_INTEGRATION_ISSUES.md` — frontend/backend integration notes.

Note: The frontend folder may be excluded from the repo depending on `.gitignore` settings — docs explain local `npm install` and `.env` setup.

---

## Dev & Ops tooling

- `scripts/dev-setup.sh` — initial environment bootstrap (conda/mamba, env files, service emulators).
- `scripts/deploy-backend.sh`, `scripts/deploy-frontend.sh` — deploy to Cloud Run and frontend host.
- `docker-compose.yml` (+ `.dev`) — run backend + frontend + GCP emulators for local testing.
- `Makefile` — common commands and convenience tasks.

---

## Tests & CI

- `tests/` — unit and integration tests for core analysis components.
- `test_endpoints.sh` — integration check for API endpoints and response shapes.
- Additional test harnesses live in `mcp-finance1/IMPLEMENTATION_TEST.md` and `TESTING_GUIDE.md`.

---

## Logs & Observability

- `logs/` — diagnostics, health checks, performance summaries, and saved analysis outputs (sample JSONs).
- Many docs reference runtime observability best practices: `EXECUTION-LOG-ANALYSIS.md`, `ENVIRONMENT_TEST_REPORT.md`, `PERFORMANCE` logs.

---

## Redundancies & Consolidation Opportunities (observed)

1. Duplicate indicator/signal code: `automation/functions/daily_analysis/main.py` contains `calculate_indicators` and `detect_signals` that largely duplicate logic from `src/technical_analysis_mcp/indicators.py` and `signals.py`.
   - Impact: maintenance risk and inconsistent behavior between on-demand and scheduled analyses.
   - Fix: Remove duplicated functions in Cloud Function; import and use `StockAnalyzer` or specific indicator modules directly. Add tests to guarantee parity.

2. Prototype files vs canonical modules: `nu-signals1.py`, `nu-fib1.py`, and `old_code/` store advanced signal ideas not merged into the canonical detectors.
   - Impact: Valuable ideas are scattered; copying or divergence can occur.
   - Fix: Create a `prototypes/` folder and a short integration roadmap for high-quality prototypes to be merged (or archived) with clear owners and tests.

3. Overlapping docs: multiple detailed guides (`GUIDE.md`, `GUIDE-ENHANCED.md`, `QUICK_START_BETA1.md`, `BACKEND_IMPLEMENTATION_COMPLETE.md`, `DEPLOYMENT_GUIDE.md`).
   - Impact: Confusion for new contributors; drift between docs over time.
   - Fix: Consolidate to a smaller set of canonical docs (e.g., `README.md`, `DEVELOPER_GUIDE.md`, `DEPLOYMENT.md`) and keep specialized writeups as archived supplements.

4. Repeated configuration values: `DEFAULT_WATCHLIST` appears in both docs and Cloud Function default lists as well as possibly elsewhere.
   - Fix: Centralize watchlist and universe definitions in `universes.py` (or a config module), and import where needed.

5. Multiple refactoring documents: `REFACTORING-AND-FREE-TIER-OPTIMIZATION.md`, `REFACTORING-SUMMARY.md`, `REFACTORING-COMPLETE.txt` — consolidate into one source of truth.


---

## Recommendations & Next Steps (short)

1. Consolidate indicator/signal implementations into `src/technical_analysis_mcp` and remove duplicates from serverless functions and prototypes.
2. Prune or archive prototypes after extracting testable algorithms into modular detectors.
3. Consolidate documentation and add a single-page onboarding `README.md` that links to detailed guides.
4. Add an internal changelog or `docs/CHANGELOG.md` for major algorithm or model changes (important for reproducibility of AI-driven scores).
5. Add automated checks (pre-commit or CI) to ensure no duplication of core logic (e.g., tests asserting `StockAnalyzer` results match scheduled-run results for a set of sample symbols).

---

For a complete file-by-file map, or to expand any of the sections above into dedicated docs (e.g., `ARCHITECTURE.md`, `CONTRIBUTING.md`), tell me which area you want prioritized and I'll generate the file and suggested PR changes. ✅
