# AI Optimization & Efficiency — 25 Actionable Improvements

This document lists 25 concrete ways AI features in the MCP Finance project can be optimized, leveraged more effectively, and made more cost- and runtime-efficient. Each entry includes a short description, suggested changes (files/areas impacted), effort estimate, and expected benefit.

---

1) Smart Pre-filtering (Low effort)
- Description: Before invoking Gemini/Claude for a symbol, run a lightweight rule-based filter to discard low-information cases (e.g., low vol, no trend, no significant signals). Only send candidates passing a threshold to the LLM.
- Impact: `mcp-finance1/cloud-run/main.py`, `src/technical_analysis_mcp/analysis.py`, `signals.py`
- Benefit: Reduced model calls → lower cost and latency.

2) Batch & Parallel Model Calls (Medium)
- Description: Batch prompts or use concurrent requests for universe scans to amortize latency and reduce total wall-clock time.
- Impact: `automation/functions/*`, API worker that calls model
- Benefit: Faster scans; better throughput.

3) Response Caching (Low)
- Description: Cache model outputs per symbol+period+prompt-hash (Firestore or in-memory LRU). Reuse if cache is fresh.
- Impact: `main.py` caching logic, Firestore collections (`ai_cache`)
- Benefit: Cost savings; consistent responses.

4) Adaptive Model Selection (Medium)
- Description: Use different model sizes / endpoints depending on task (e.g., small distilled model for scoring, large model for detailed briefs).
- Impact: Analysis orchestration in `StockAnalyzer` and the model client wrapper
- Benefit: Lower cost while keeping quality for intensive tasks.

5) Prompt Templates & Guardrails (Low)
- Description: Standardize prompt templates and strict output format enforcement (JSON schema validation); log prompts and responses for auditing.
- Impact: `src/technical_analysis_mcp/ranking.py`, `signals.py`, logging configuration
- Benefit: More stable, parseable AI outputs and easier debugging.

6) Rate Limit-aware Retry & Backoff (Low)
- Description: Centralized retry strategy using exponential backoff and jitter; track quotas per project and alert if approaching limits.
- Impact: All model call locations (Cloud Functions, backend workers)
- Benefit: Fewer failed requests and graceful degradation.

7) Local Rule-based Fallbacks (Low)
- Description: If LLM fails or costs exceed threshold, fallback to deterministic rule-based scoring (already present as `rule_based_score`) and surface confidence score.
- Impact: `signals.py`, `analysis.py`
- Benefit: Availability & determinism.

8) Tier-aware AI Features (Low)
- Description: Gate expensive AI features by customer tier (pro vs free). Use cheaper models or rate-limited AI features for free users.
- Impact: Frontend `tiers.ts`, backend request handling
- Benefit: Predictable cost and monetization flexibility.

9) AI Usage Instrumentation (Low)
- Description: Track model call counts, token usage, latency, and cost per endpoint. Add dashboards and alerts.
- Impact: Logging & observability (Ops dashboards), `main.py`
- Benefit: Cost tracking and optimization insights.

10) Precompute & Batch Offline Analyses (Medium)
- Description: Run nightly batch analyses for large universes and persist results; serve precomputed scores for non-real-time pages (e.g., scanner index).
- Impact: `automation/` functions, Firestore schemas
- Benefit: Lower real-time load and faster UI responses.

11) Model Output Schema Validation + Unit Tests (Low)
- Description: Validate that AI outputs conform to a strict schema and add unit/integration tests using stored sample model responses.
- Impact: `tests/`, `ranking.py`
- Benefit: Regression safety and parseability.

12) Prompt Compression & Token Minimization (Low)
- Description: Strip unnecessary context and compress prompt information (use hashed references to shared context stored server-side).
- Impact: Prompt generation code and cache layer
- Benefit: Lower token usage and cost.

13) Use Embeddings + Vector DB for Contextual Retrieval (Medium)
- Description: Keep historical analyst notes and previous briefings in a vector DB to provide concise, relevant context to LLMs instead of long histories.
- Impact: Persistent store (Firestore/Vector DB), `ranking.py`, `analysis.py`
- Benefit: Better contextual responses with lower token overhead.

14) Distill & Fine-tune Small Models (High)
- Description: Collect curated pairs (signals → desired short JSON outputs) and fine-tune a small model (or distilled variant) for scoring to reduce reliance on expensive general LLM calls.
- Impact: Data collection hooks, training pipeline, model wrapper
- Benefit: Big cost & latency improvements for scoring tasks.

15) Progressive Answering (Low)
- Description: Use incremental analysis: a cheap pass (rule-based) produces answers quickly; the AI-enhanced result replaces it once ready (optimistic UX). Use WebSockets or check endpoints.
- Impact: `main.py`, frontend UX changes
- Benefit: Better perceived latency.

16) Streaming Responses for Briefs (Medium)
- Description: Stream AI-generated briefs to the UI while model is generating to improve UX for long responses.
- Impact: API endpoints & frontend to support SSE/WebSocket
- Benefit: Improved UX and engagement.

17) Model Cost Budgeting & Alerts (Low)
- Description: Set a daily/weekly budget for model usage and enforce by throttling non-critical AI calls when close to the budget.
- Impact: Ops, usage instrumentation
- Benefit: Cost control.

18) Use Deterministic Instructions for Repeatability (Low)
- Description: Pin model parameters (temperature=0.0 for scoring), log seeds and prompt versions for reproducibility.
- Impact: Prompt wrapper and `ranking.py`
- Benefit: Repeatable outputs and easier debugging.

19) Human-in-the-loop Labeling (Medium)
- Description: Surface a small set of borderline or high-impact AI decisions to human reviewers for labeling to create training data.
- Impact: Admin UI, Firestore labeling collection, data-collection pipeline
- Benefit: High-quality fine-tuning dataset.

20) Model Output Explainability (Medium)
- Description: Ask the model to produce short rationale/explainers (2-3 bullets) and/or highlight which signals drove the score.
- Impact: Prompt template & UI changes
- Benefit: Trust and auditability for AI-driven recommendations.

21) Adaptive Frequency Based on Volatility (Low)
- Description: Analyze symbol volatility and adapt how frequently AI scoring is run (higher for volatile symbols, lower for quiet ones).
- Impact: `automation/`, `StockAnalyzer`, scheduled jobs
- Benefit: Resource allocation -> cost and throughput savings.

22) Canary & A/B Testing for Model Changes (Medium)
- Description: Roll out model changes or prompt updates to a fraction of traffic for measured comparisons (CTR/engagement/accuracy), store metrics for analysis.
- Impact: Feature flags, telemetry, experiment tracking
- Benefit: Safer improvements and measurable wins.

23) Safety Filters & Output Sanitization (Low)
- Description: Ensure AI output strictly adheres to expected JSON keys and numbers. Sanitize text fields to remove hallucinations and keep summaries short.
- Impact: Output parsing layer and `ranking.py`
- Benefit: Robustness and fewer downstream errors.

24) Queueing Work & Concurrency Controls (Low to Medium)
- Description: Push AI tasks to a controlled worker pool (Pub/Sub + worker instances). Use concurrency limits per worker to avoid hitting rate limits.
- Impact: `main.py` (already publishes to Pub/Sub), worker code
- Benefit: Reliability and scale control.

25) Continuous Monitoring & Drift Detection (Medium)
- Description: Monitor input distribution (signal counts, feature distributions) and AI output distributions; alert when distributions drift (possible model degradation or upstream data changes).
- Impact: Metrics pipeline, dashboards, alerts
- Benefit: Early detection of model issues and data changes.

---

## Prioritization & Quick Wins

- Quick wins (Low effort, High ROI): 1 (Pre-filtering), 3 (Response caching), 5 (Prompt templates), 6 (Retry/backoff), 8 (Tier-aware features), 9 (Instrumentation), 18 (Deterministic instructions), 23 (Output sanitization).

- Medium-term (Medium effort): 2 (Batch calls), 10 (Nightly precompute), 13 (Embeddings), 15 (Progressive answers), 16 (Streaming), 21 (Adaptive frequency), 24 (Queueing/concurrency), 22 (A/B testing).

- Longer-term (High effort): 14 (Fine-tune small model), 19 (Human-in-loop labeling), 25 (Drift detection).

---

## Final notes

- Most optimizations are complementary: combine pre-filtering + caching + tier-aware selection to quickly reduce costs and latency.
- Implement instrumentation early — it’s required to measure impact of changes and guide prioritization.

If you'd like, I can implement the top 5 quick wins as PRs (tests + docs + small code changes). Tell me which items to start with and I will open branches and draft the changes. ✅
