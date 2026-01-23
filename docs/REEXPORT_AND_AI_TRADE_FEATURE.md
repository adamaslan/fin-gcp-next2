# Re-export Indexes & `Trade Idea Analyzer` Feature

## Summary ✅
The import error "Module not found: Can't resolve '@/lib/db'" was caused because `src/lib/db` did not have an `index.ts` entry point. I added central `index.ts` files to the following locations:

- `src/lib/db/index.ts` (exports: `db`, schema, queries, fibonacci_signals)
- `src/lib/auth/index.ts` (exports: `tiers`, `usage-limits`, `user-init`)
- `src/lib/mcp/index.ts` (exports: `client`, `types`)

This ensures imports like `import { db } from "@/lib/db"` work reliably across the app.

---

## Why a central `index.ts` helps 🔧
- Provides a single entrypoint for a logical module (e.g., `@/lib/db`) so other modules don't need to know internal filenames.
- Simplifies refactors: move files internally without changing external imports.
- Reduces module resolution failures in bundlers (Next.js) and TypeScript path-based imports.
- Encourages explicit public surface area for each folder.

---

## How to apply the pattern across the repo (quick checklist) 📋
1. For every folder that contains multiple exports (e.g., `lib/*`, `components/*`, `hooks/*`), add an `index.ts` that re-exports the public API.
2. Run a repo-wide search for `from "@/lib/` and ensure the folder referenced has an `index.ts` (or update imports to point at specific files).
3. Add an ESLint rule or codemod to prevent direct folder imports without an index in new modules.
4. Add unit tests that import from the folder root to validate exports.
5. Document each module's public API in a README or central docs file.

---

## 5 suggested improvements for major areas (concise, actionable) 💡

Note: the list below addresses the folders you named: *stripe, mcp, db, auth, hooks, components, ui, trade-plan, subscription, settings, portfolio, onboarding, landing, gating, fibonacci, dashboard(s), calendar, analysis, alerts, marketing, api, webhooks, watchlist, public, export, mcp alerts*.

- stripe
  1. Add strong TypeScript types for price IDs, products, and session payloads.
  2. Add integration tests that mock Stripe webhooks and webhook signature verification.
  3. Centralize config and env validation (required STRIPE_SECRET, PRICE_IDS).
  4. Implement retry + idempotency helpers for webhook handlers and checkout flows.
  5. Add a reconciliation job to verify subscription states with Stripe and DB.

- mcp
  1. Export typed client helper functions and stable types in `index.ts`.
  2. Add caching for repeated indicator requests (Redis or in-process memoization).
  3. Add unit tests for common analysis flows.
  4. Add request/response validation and timeouts for external MCP APIs.
  5. Add metrics (latency, error rate) for MCP calls and retries.

- db
  1. Add `index.ts` (done) and keep public schema exports explicit.
  2. Add migrations and a clear schema versioning strategy (eg. Liquibase, Flyway, or SQL migrations via drizzle plugins).
  3. Add DB connection pooling and health checks & graceful reconnect logic.
  4. Add query-level tests (integration tests against a test DB) and seed data.
  5. Add database indexes for frequently filtered columns and run explain plans for slow queries.

- auth
  1. Strong typing for user/session objects and central `index.ts` (done).
  2. Harden server-side tier checks and ensure all gating uses centralized helpers.
  3. Add audit logs for admin actions and user-tier changes.
  4. Add rate-limiting middleware for endpoints that initialize users and tiers.
  5. Add end-to-end tests that simulate login and access gating.

- hooks
  1. Create typed hooks with well-defined return types and JSDoc.
  2. Ensure hooks are SSR-safe when used in Next.js (avoid window only usage in render paths).
  3. Add tests via React Testing Library for core behaviors.
  4. Memoize heavy computations and avoid unnecessary re-renders.
  5. Bundle commonly used hooks in a public `index.ts` in `src/hooks/`.

- components
  1. Add Storybook for visual testing and documentation.
  2. Add accessibility (a11y) tests and enforce keyboard navigation and ARIA roles.
  3. Split large components into smaller presentational and container parts.
  4. Add unit tests for rendering logic and props.
  5. Centralize common component exports via `components/index.ts`.

- ui
  1. Use design tokens (colors, spacing, typography) and a consistent theme provider.
  2. Add a component library boundary: small, composable primitives (Button, Input, Card).
  3. Document intent and accessibility for each UI primitive.
  4. Optimize bundle size by lazy-loading non-critical UI code.
  5. Add visual regression tests.

- trade-plan
  1. Version trade-plan snapshots and store `tradePlanSnapshot` in DB (done in tradeJournal).
  2. Validate trade plans with a schema and provide helpful errors.
  3. Add diff/restore UI for plan iterations.
  4. Add permission checks for editing/sharing plans.
  5. Add unit + integration tests for plan creation and persistence.

- subscription
  1. Secure webhook endpoints (signature verification and idempotency keys).
  2. Reconcile subscription state with Stripe regularly.
  3. Provide clear billing UI and subscription history.
  4. Add tests for upgrades/downgrades and proration behavior.
  5. Implement background job for expired trial handling and grace periods.

- settings, portfolio, onboarding, landing, gating
  - Provide typed APIs, unit & end-to-end tests, and accessibility checks; centralize config & i18n if needed.

- fibonacci
  1. Add robust tests for level detection and confluence logic (unit + integration).
  2. Persist analysis requests and cache previous results.
  3. Add versioned analysis schemas so backtests remain reproducible.
  4. Make performance improvements (vectorized math, batched queries).
  5. Provide adjustable sensitivity/tolerance via UI and store those preferences.

- dashboards, calendar, analysis, alerts, marketing, api, webhooks, watchlist, public, export, mcp alerts
  - For each: add clear contracts (DTOs), webhook security, background workers for heavy tasks (export, backtests), monitoring, and tests. Prefer event-driven patterns for long-running tasks and add retry and durable logs for failures.

---

## Suggested enforcement (developer ergonomics) 🔧
- Add an ESLint rule that warns when importing from a folder that lacks an `index.ts`.
- Add a CI check that runs `tsc` and validates barrel exports by attempting to import from module roots.
- Add a small migration codemod that updates imports to `@/lib/<module>` when you add an index.

---

## Trade Idea Analyzer — Fullstack AI-powered feature (overview) 🤖💼

Objective: Let a user submit a trade idea (symbol, direction, price/size, timeframe) and receive an AI-assisted analysis that includes: signal consensus, risk metrics, probabilistic outcomes, an explanation, and a final `riskRank` recommendation.

High-level flow:
1. Frontend: `TradeIdeaModal` captures idea and POSTs to `/api/ai/trade-analyze`.
2. API: lightweight validation and enqueues a job for full analysis; returns job id and optimistic quick checks.
3. Worker/Orchestrator: spins up multiple *subagents* (4–6) to collaborate on the analysis and aggregate results.
4. Persistence: store the trade idea, agent outputs, the final decision, and user feedback in `db.tradeJournal`/`analysis_logs`.
5. UI: Polls job status (or uses WebSocket) and renders results + explanation + a suggested position size and stop-loss levels.

Subagents (6 agents recommended):
- 1) Ingest Agent: Normalize inputs, fetch OHLC data, recent news, and user portfolio exposure.
- 2) Signal Aggregator Agent: Run technical indicator suite (MCP: Fibonacci, Moving Averages, RSI, MACD, etc.) and compute a signal consensus and confidence per indicator.
- 3) Backtest / Simulator Agent: Run quick backtest simulations over historical windows and return probable return distributions for the proposed entry + stop + target.
- 4) Risk Model Agent: Calculate position sizing, expected drawdown, VaR, Kelly fraction, and suggested stop/take levels; produce a risk score.
- 5) Sentiment & Context Agent: Pulls news/sentiment and important events (earnings, macro) and computes contextual impact.
- 6) Explanation & Rank Agent: Use a small LLM to synthesize the above into a human-readable rationale, produce a `riskRank` (e.g., Low/Medium/High), and recommend yes/no/hold.

Implementation notes:
- Orchestration: Use a job queue (BullMQ, Redis streams, or Cloud Tasks) and implement each agent as a job step or microservice.
- Data sources: MCP indicators, price history (1d, 30d, 90d), optional news sentiment API.
- LLM: Use a specialist instruct-tuned model for explainability; keep prompts small by sending structured agent outputs rather than raw data.
- Observability: Log intermediate agent states, latencies, costs for LLM usage, and a full audit trail for compliance.
- Privacy & security: Rate-limit usage, redact PII from logs, and ensure users opt-in for analyses that may call external paid APIs.
- UX: Provide a transparent explanation page showing which signals contributed to the recommendation and let users provide feedback to improve models.

---

## Next steps I recommend ✅
1. Run a repo search for other folder imports like `@/lib/<folder>` and add `index.ts` where missing (start with `lib/mcp`, `lib/auth`, `lib/db`).
2. Add the docs file to your developer docs and reference it in contributor guidelines.
3. If you want, I can open a PR with these changes and a test demonstrating that `import { db } from "@/lib/db"` now resolves.

If you want, I can also scaffold the `/api/ai/trade-analyze` endpoint and a worker prototype to run the subagents.
