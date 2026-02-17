# Options MCP Backend - API Routes Guide

**Version**: 2.0.0
**Base URL**: `http://localhost:8080` (local) or your Cloud Run URL
**Total Routes**: 15

---

## Table of Contents

| # | Route | Method | Category |
|---|-------|--------|----------|
| 1 | [`/`](#1-health-check) | GET | Health |
| 2 | [`/health`](#2-detailed-health-check) | GET | Health |
| 3 | [`/api/options-risk`](#3-options-risk-analysis) | POST | Core Analysis |
| 4 | [`/api/options-summary`](#4-options-summary) | POST | Core Analysis |
| 5 | [`/api/options-vehicle`](#5-vehicle-selection) | POST | Core Analysis |
| 6 | [`/api/options-compare`](#6-multi-symbol-comparison) | POST | Core Analysis |
| 7 | [`/api/options-enhanced`](#7-enhanced-analysis--ai) | POST | AI-Enhanced |
| 8 | [`/api/options-ai`](#8-ai-risk-analysis) | POST | AI-Enhanced |
| 9 | [`/api/spread-trade`](#9-spread-trade-analysis) | POST | Spread Trading |
| 10 | [`/api/pipeline/run`](#10-pipeline-run-multi) | POST | Data Pipeline |
| 11 | [`/api/pipeline/run-single`](#11-pipeline-run-single) | POST | Data Pipeline |
| 12 | [`/docs`](#12-swagger-ui) | GET | Documentation |
| 13 | [`/redoc`](#13-redoc) | GET | Documentation |
| 14 | [`/openapi.json`](#14-openapi-schema) | GET | Documentation |
| 15 | [`/docs/oauth2-redirect`](#15-oauth2-redirect) | GET | Documentation |

---

## Health Routes

### 1. Health Check

```
GET /
```

Quick ping to verify the service is running. Returns module availability flags.

**Request**: None

**Response**:
```json
{
  "service": "Options MCP Backend",
  "version": "2.0.0",
  "status": "healthy",
  "mcp_available": true,
  "ai_available": true,
  "pipeline_available": true
}
```

**Status Codes**: `200 OK`

**Use When**: Load balancer health probes, quick connectivity checks.

---

### 2. Detailed Health Check

```
GET /health
```

Deep health check that tests yfinance connectivity and reports Python version.

**Request**: None

**Response**:
```json
{
  "status": "healthy",
  "checks": {
    "mcp_server": "ok",
    "python": "3.10.17 | packaged by conda-forge | ...",
    "yfinance": "ok"
  }
}
```

**Status Codes**:
- `200 OK` - All checks pass (status: "healthy") or partial (status: "degraded")

**Use When**: Deployment verification, debugging connectivity issues, monitoring dashboards.

---

## Core Analysis Routes

### 3. Options Risk Analysis

```
POST /api/options-risk
```

Full options chain risk analysis. Returns IV metrics, Put/Call ratio, volume/OI data, risk warnings, and trading opportunities for calls, puts, or both.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "expiration_date": "2026-03-21",
  "option_type": "both",
  "min_volume": 75
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock ticker symbol |
| `expiration_date` | string | no | nearest | Expiration date (YYYY-MM-DD) |
| `option_type` | string | no | `"both"` | `"calls"`, `"puts"`, or `"both"` |
| `min_volume` | int | no | `75` | Minimum volume for liquidity filter |

**Response**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "timestamp": "2026-02-12T18:00:00Z",
    "current_price": 228.50,
    "expiration_date": "2026-03-21",
    "days_to_expiration": 37,
    "available_expirations": ["2026-02-14", "2026-02-21", "2026-03-21"],
    "calls": {
      "total_contracts": 142,
      "liquid_contracts": 45,
      "total_volume": 125000,
      "total_open_interest": 890000,
      "avg_implied_volatility": 28.5,
      "max_iv": 65.2,
      "min_iv": 18.1,
      "atm_strike": 230.0,
      "atm_iv": 24.3,
      "atm_delta": 0.48,
      "top_volume_strikes": [
        {"strike": 230.0, "volume": 15200, "iv": 24.3}
      ],
      "top_oi_strikes": [
        {"strike": 230.0, "open_interest": 45000, "iv": 24.3}
      ]
    },
    "puts": { ... },
    "put_call_ratio": {
      "volume": 0.82,
      "open_interest": 1.15
    },
    "risk_warnings": [
      "High OI concentration in calls at $230 strike (32% of total) - potential pin risk"
    ],
    "opportunities": [
      "Low Put/Call Volume Ratio (0.82) - bullish sentiment, heavy call buying"
    ],
    "liquidity_threshold": 75
  }
}
```

**Status Codes**:
- `200 OK` - Analysis complete
- `404 Not Found` - No options data for this symbol
- `500 Internal Server Error` - Analysis engine failure
- `503 Service Unavailable` - MCP server not loaded

**Use When**: Full risk assessment before entering any options position. This is the most comprehensive single-symbol analysis.

---

### 4. Options Summary

```
POST /api/options-summary
```

Quick snapshot of options sentiment and risk level. Much faster than full risk analysis - ideal for dashboards and watchlists.

**Request Body**:
```json
{
  "symbol": "AAPL"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symbol` | string | yes | Stock ticker symbol |

**Response**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "timestamp": "2026-02-12T18:00:00Z",
    "current_price": 228.50,
    "nearest_expiration": "2026-02-14",
    "days_to_expiration": 2,
    "atm_call_iv": 24.3,
    "atm_put_iv": 26.1,
    "put_call_ratio_volume": 0.82,
    "total_call_volume": 125000,
    "total_put_volume": 102500,
    "sentiment": "bullish",
    "risk_level": "medium"
  }
}
```

**Status Codes**: `200`, `404`, `500`, `503`

**Use When**: Watchlist displays, quick sentiment checks, deciding whether to dig deeper with `/api/options-risk`.

---

### 5. Vehicle Selection

```
POST /api/options-vehicle
```

Should you trade stock or options? Returns a recommendation based on timeframe, volatility regime, directional bias, and expected move size using a stock-first decision tree.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "timeframe": "swing",
  "bias": "bullish",
  "expected_move_percent": 5.0
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock ticker symbol |
| `timeframe` | string | no | `"swing"` | `"swing"` (2-10d), `"day"`, or `"scalp"` |
| `bias` | string | no | `"bullish"` | `"bullish"` or `"bearish"` |
| `expected_move_percent` | float | no | `3.0` | Expected price move as percentage |

**Response**:
```json
{
  "success": true,
  "data": {
    "vehicle": "option_call",
    "reasoning": "Swing timeframe with bullish bias and 5.0% expected move favors call options for leverage",
    "dte_range": [30, 45],
    "delta_range": [0.40, 0.60],
    "spread_type": null,
    "spread_width_info": null,
    "expected_move_percent": 5.0
  }
}
```

**Vehicle Types**:
- `stock` - Trade the stock directly
- `option_call` - Buy calls
- `option_put` - Buy puts
- `option_spread` - Use a spread strategy

**Status Codes**: `200`, `404`, `500`, `503`

**Use When**: Before placing a trade, to decide the best expression vehicle.

---

### 6. Multi-Symbol Comparison

```
POST /api/options-compare
```

Compare options metrics across 2-10 symbols. Ranks symbols by the chosen metric.

**Request Body**:
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"],
  "metric": "iv"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbols` | list[string] | yes | - | 2-10 ticker symbols |
| `metric` | string | no | `"iv"` | `"iv"`, `"pcr"`, `"volume"`, or `"liquidity"` |

**Response**:
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-02-12T18:00:00Z",
    "metric": "iv",
    "symbols": [
      {
        "symbol": "NVDA",
        "current_price": 132.50,
        "atm_iv": 45.2,
        "put_call_ratio": 0.95,
        "total_volume": 850000,
        "liquid_contracts": 120
      },
      ...
    ],
    "ranked_by": "Implied Volatility (highest first)"
  }
}
```

**Metric Options**:
- `iv` - Rank by ATM implied volatility (highest first)
- `pcr` - Rank by put/call ratio (most bearish first)
- `volume` - Rank by total options volume (highest first)
- `liquidity` - Rank by liquid contracts count (most liquid first)

**Status Codes**: `200`, `404`, `500`, `503`

**Use When**: Choosing which stock has the best options setup, comparing IV levels across a sector, finding the most liquid options chain.

---

## AI-Enhanced Routes

### 7. Enhanced Analysis + AI

```
POST /api/options-enhanced
```

The most comprehensive endpoint. Combines all core analysis tools plus 5 enhanced fields and optional Gemini AI natural language insights.

**Requires**: `RUNNER_AVAILABLE` (Firestore access for enhanced fields)

**Request Body**:
```json
{
  "symbol": "AAPL",
  "use_ai": true,
  "bias": "bullish",
  "expected_move_percent": 3.0
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock ticker symbol |
| `use_ai` | bool | no | `true` | Include Gemini AI insights |
| `bias` | string | no | `"bullish"` | `"bullish"` or `"bearish"` |
| `expected_move_percent` | float | no | `3.0` | Expected move percentage |

**Response**:
```json
{
  "success": true,
  "data": {
    "risk_analysis": {
      "status": "ok",
      "error": null,
      "data": { ... }
    },
    "summary": {
      "status": "ok",
      "error": null,
      "data": { ... }
    },
    "vehicle_recommendation": {
      "status": "ok",
      "error": null,
      "data": { ... }
    },
    "enhanced_fields": {
      "status": "ok",
      "error": null,
      "data": {
        "iv_rank": 72.5,
        "max_pain": 225.0,
        "unusual_activity": [
          {
            "strike": 240.0,
            "volume": 12000,
            "open_interest": 3200,
            "vol_oi_ratio": 3.75,
            "option_type": "call"
          }
        ],
        "greeks_exposure": {
          "delta": 1250.45,
          "gamma": 89.23,
          "vega": 3200.10,
          "theta": -450.80
        },
        "spread_opportunities": [
          {
            "buy_strike": 225.0,
            "sell_strike": 230.0,
            "spread_width": 5.0,
            "max_cost": 2.15,
            "max_profit": 2.85,
            "option_type": "call"
          }
        ]
      }
    },
    "ai_analysis": {
      "status": "ok",
      "error": null,
      "data": {
        "market_sentiment": {
          "bias": "BULLISH",
          "confidence": "MEDIUM",
          "reasoning": "...",
          "key_flow_signals": ["..."]
        },
        "iv_analysis": { ... },
        "max_pain_analysis": { ... },
        "unusual_activity_interpretation": { ... },
        "greeks_assessment": { ... },
        "strategy_recommendations": [ ... ],
        "spread_analysis": { ... },
        "risk_factors": [ ... ],
        "position_sizing": { ... },
        "action_plan": [ ... ],
        "plain_english_summary": "..."
      }
    }
  }
}
```

**Enhanced Fields Explained**:

| Field | Description |
|-------|-------------|
| `iv_rank` | 0-100 percentile of current IV within the expiration's range. 80+ = expensive options, 20- = cheap |
| `max_pain` | Strike price where most options expire worthless. Price tends to gravitate here near expiration |
| `unusual_activity` | Contracts where daily volume > 3x open interest, signaling new large positions |
| `greeks_exposure` | Aggregate delta/gamma/vega/theta across the entire chain - shows net market maker exposure |
| `spread_opportunities` | Top 3 vertical spreads ranked by profit/cost ratio using real bid/ask data |

**Status Codes**: `200`, `500`, `503`

**Use When**: Full portfolio-level analysis before making any options trade. This is the "give me everything" endpoint.

---

### 8. AI Risk Analysis

```
POST /api/options-ai
```

Runs standard risk analysis then passes the results through Gemini AI for natural language interpretation, strategy recommendations, and an action plan.

**Requires**: `GEMINI_API_KEY` environment variable

**Request Body**: Same as [`/api/options-risk`](#3-options-risk-analysis)
```json
{
  "symbol": "AAPL",
  "expiration_date": null,
  "option_type": "both",
  "min_volume": 75
}
```

**Response**: Same structure as `/api/options-risk` plus an `ai_analysis` field:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "current_price": 228.50,
    "calls": { ... },
    "puts": { ... },
    "risk_warnings": [ ... ],
    "opportunities": [ ... ],
    "ai_analysis": {
      "market_sentiment": {
        "bias": "BULLISH",
        "confidence": "MEDIUM",
        "reasoning": "Call volume significantly outpaces puts..."
      },
      "iv_analysis": {
        "level": "MEDIUM",
        "buyer_vs_seller_edge": "Slight edge to option buyers..."
      },
      "strategy_recommendations": [
        {
          "strategy_name": "Bull Call Spread",
          "bias": "BULLISH",
          "strikes": "$225/$235 March expiration",
          "reasoning": "Captures upside with defined risk...",
          "suitability": "MODERATE"
        }
      ],
      "risk_factors": [
        {
          "factor": "Earnings in 3 weeks",
          "severity": "HIGH",
          "mitigation": "Close position before earnings or widen stops"
        }
      ],
      "position_sizing": {
        "recommended_allocation": "2-3% of portfolio",
        "max_risk_per_trade": "$500 per spread"
      },
      "action_plan": [
        {"step": 1, "action": "Check pre-market price action", "timing": "BEFORE_ENTRY"},
        {"step": 2, "action": "Enter bull call spread at limit", "timing": "AT_ENTRY"}
      ]
    }
  }
}
```

**Status Codes**: `200`, `404`, `500`, `503`

**Use When**: You want AI-powered interpretation of risk analysis without the full enhanced fields. Lighter than `/api/options-enhanced`.

---

## Spread Trading Route

### 9. Spread Trade Analysis

```
POST /api/spread-trade
```

Analyze a specific option spread trade you're considering opening or an existing position you're considering closing. Uses real chain data to compute exact risk/reward, breakeven, Greeks, and provides an AI-powered GO/NO-GO verdict.

**Request Body (Open)**:
```json
{
  "symbol": "AAPL",
  "spread_type": "bull_call",
  "buy_strike": 225.0,
  "sell_strike": 230.0,
  "expiration_date": "2026-03-21",
  "contracts": 5,
  "action": "open"
}
```

**Request Body (Close)**:
```json
{
  "symbol": "AAPL",
  "spread_type": "bull_put_credit",
  "buy_strike": 210.0,
  "sell_strike": 220.0,
  "expiration_date": "2026-03-21",
  "contracts": 3,
  "action": "close",
  "entry_price": 2.50
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Stock ticker symbol |
| `spread_type` | string | yes | - | See spread types below |
| `buy_strike` | float | yes | - | Long leg strike price |
| `sell_strike` | float | yes | - | Short leg strike price |
| `expiration_date` | string | no | nearest | Expiration (YYYY-MM-DD) |
| `contracts` | int | no | `1` | Number of contracts (1-100) |
| `action` | string | no | `"open"` | `"open"` or `"close"` |
| `entry_price` | float | no | null | Entry price per spread (required for close) |

**Supported Spread Types**:

| Type | Strategy | Direction | Credit/Debit |
|------|----------|-----------|-------------|
| `bull_call` | Buy lower call, sell higher call | Bullish | Debit |
| `bear_put` | Buy higher put, sell lower put | Bearish | Debit |
| `bull_put_credit` | Sell higher put, buy lower put | Bullish | Credit |
| `bear_call_credit` | Sell lower call, buy higher call | Bearish | Credit |
| `iron_condor` | Bull put credit + bear call credit | Neutral | Credit |
| `straddle` | Buy ATM call + put at same strike | Volatility | Debit |
| `strangle` | Buy OTM call + put at different strikes | Volatility | Debit |

**Response (Open)**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "spread_type": "bull_call",
    "action": "open",
    "current_price": 228.50,
    "expiration": "2026-03-21",
    "dte": 37,
    "buy_strike": 225.0,
    "sell_strike": 230.0,
    "contracts": 5,
    "spread_width": 5.0,
    "buy_leg": {
      "strike": 225.0,
      "bid": 8.20,
      "ask": 8.45,
      "iv": 25.3,
      "delta": 0.62,
      "volume": 3200,
      "open_interest": 15000
    },
    "sell_leg": {
      "strike": 230.0,
      "bid": 5.80,
      "ask": 6.10,
      "iv": 24.1,
      "delta": 0.48,
      "volume": 4100,
      "open_interest": 22000
    },
    "is_credit": false,
    "max_profit": 1175.0,
    "max_loss": 1325.0,
    "risk_reward_ratio": 0.89,
    "breakeven": 227.65,
    "net_delta": 0.14,
    "ai_analysis": {
      "trade_assessment": {
        "quality": "GOOD",
        "conviction": "MEDIUM",
        "explanation": "Solid defined-risk bullish setup..."
      },
      "timing": {
        "is_good_timing": true,
        "dte_assessment": "37 DTE gives adequate time...",
        "iv_context": "IV at 25% is near average...",
        "recommendation": "Enter on a pullback to $226-227"
      },
      "risk_analysis": {
        "risk_reward_quality": "Acceptable at 0.89:1...",
        "max_loss_acceptable": "$1,325 total risk for 5 contracts...",
        "probability_estimate": "~55% probability of profit...",
        "key_risks": ["Earnings event", "Market-wide selloff"]
      },
      "execution_tips": [
        "Use limit order at mid-price ($2.55)",
        "Enter during high-volume hours (10am-3pm ET)"
      ],
      "management_plan": {
        "profit_target": "Close at 50% of max profit ($587)",
        "stop_loss": "Close if spread value drops to $1.00",
        "adjustment_triggers": ["Stock drops below $222"],
        "time_stop": "Close with 14 DTE remaining"
      },
      "alternatives": [
        {
          "strategy": "Bull put credit spread",
          "why_better": "Positive theta, higher probability",
          "strikes": "Sell $220P / Buy $215P"
        }
      ],
      "verdict": {
        "decision": "GO",
        "reasoning": "Solid setup with defined risk...",
        "conditions_to_revisit": "If stock drops below $224"
      }
    }
  }
}
```

**Response (Close)** includes an additional `close_analysis` section:
```json
{
  "data": {
    ...
    "close_analysis": {
      "entry_price": 2.50,
      "current_value": 3.80,
      "pnl_per_spread": 1.30,
      "total_pnl": 390.0,
      "pnl_percent": 52.0
    },
    "ai_analysis": {
      "verdict": {
        "decision": "GO",
        "reasoning": "52% profit captured, close to lock in gains..."
      }
    }
  }
}
```

**Status Codes**:
- `200 OK` - Analysis complete
- `400 Bad Request` - Invalid spread type
- `404 Not Found` - No options data for symbol
- `500 Internal Server Error` - Analysis failure
- `503 Service Unavailable` - MCP server not loaded

**Use When**: Evaluating a specific trade before entering, or deciding whether to close an existing spread position.

---

## Data Pipeline Routes

### 10. Pipeline Run (Multi-Symbol)

```
POST /api/pipeline/run
```

Run the Finnhub options data pipeline for multiple symbols. Fetches options chains and historical candle data, stores everything in Firestore.

**Requires**: `FINHUB_API_KEY` environment variable

**Request Body**:
```json
{
  "symbols": ["AEM", "CRM", "IGV", "QBTS", "JPM"],
  "fetch_candles": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbols` | list[string] | no | `["AEM","CRM","IGV","QBTS","JPM"]` | Tickers to process (1-20) |
| `fetch_candles` | bool | no | `true` | Include historical candle data |

**Response**:
```json
{
  "success": true,
  "data": {
    "symbols_processed": ["AEM", "CRM", "IGV", "QBTS", "JPM"],
    "symbols_failed": [],
    "total_expirations": 15,
    "total_contracts": 4200,
    "duration_seconds": 12.5
  }
}
```

**Status Codes**: `200`, `500`, `503`

**Use When**: Populating Firestore with fresh options data before running enhanced analysis. Run this daily or before each analysis session.

---

### 11. Pipeline Run (Single Symbol)

```
POST /api/pipeline/run-single
```

Run the Finnhub pipeline for a single symbol. Faster than the multi-symbol endpoint.

**Requires**: `FINHUB_API_KEY` environment variable

**Request Body**:
```json
{
  "symbol": "AAPL",
  "fetch_candles": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `symbol` | string | yes | - | Single ticker symbol |
| `fetch_candles` | bool | no | `true` | Include historical candle data |

**Response**:
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "expirations_stored": 5,
    "contracts_stored": 850,
    "candles_stored": 252,
    "duration_seconds": 3.2
  }
}
```

**Status Codes**: `200`, `500`, `503`

**Use When**: Refreshing data for a single symbol you're about to analyze.

---

## Documentation Routes

### 12. Swagger UI

```
GET /docs
```

Interactive API documentation with a "Try it out" button for every endpoint. Auto-generated from the FastAPI route definitions and Pydantic models.

**Use When**: Exploring the API interactively, testing endpoints from the browser.

---

### 13. ReDoc

```
GET /redoc
```

Alternative API documentation with a clean, readable layout. Same content as Swagger but in a different format.

**Use When**: Reading API docs in a more traditional reference format.

---

### 14. OpenAPI Schema

```
GET /openapi.json
```

Raw OpenAPI 3.0 JSON schema for the entire API. Machine-readable specification of all endpoints, request/response models, and validation rules.

**Use When**: Generating client SDKs, importing into Postman, CI/CD validation.

---

### 15. OAuth2 Redirect

```
GET /docs/oauth2-redirect
```

Internal redirect handler used by the Swagger UI for OAuth2 authentication flows. Not called directly.

---

## Quick Reference

### Common curl Examples

```bash
# Health check
curl http://localhost:8080/

# Quick summary
curl -X POST http://localhost:8080/api/options-summary \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'

# Full risk analysis
curl -X POST http://localhost:8080/api/options-risk \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "option_type": "both"}'

# Vehicle selection
curl -X POST http://localhost:8080/api/options-vehicle \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "bias": "bullish", "expected_move_percent": 5}'

# Compare symbols
curl -X POST http://localhost:8080/api/options-compare \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"], "metric": "iv"}'

# Enhanced + AI
curl -X POST http://localhost:8080/api/options-enhanced \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "use_ai": true}'

# AI risk analysis
curl -X POST http://localhost:8080/api/options-ai \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'

# Open a bull call spread
curl -X POST http://localhost:8080/api/spread-trade \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "spread_type": "bull_call",
    "buy_strike": 225,
    "sell_strike": 230,
    "contracts": 5,
    "action": "open"
  }'

# Close a credit spread with P&L
curl -X POST http://localhost:8080/api/spread-trade \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "spread_type": "bull_put_credit",
    "buy_strike": 210,
    "sell_strike": 220,
    "contracts": 3,
    "action": "close",
    "entry_price": 2.50
  }'

# Run pipeline for symbols
curl -X POST http://localhost:8080/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"]}'

# Run pipeline for single symbol
curl -X POST http://localhost:8080/api/pipeline/run-single \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

### Environment Variables

| Variable | Required For | Description |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | AI routes (7, 8, 9 AI) | Gemini API key for AI insights |
| `FINHUB_API_KEY` | Pipeline routes (10, 11) | Finnhub API key for data fetching |
| `ALPHA_VANTAGE_KEY` | Pipeline routes (fallback) | Alpha Vantage key (candle fallback) |
| `FRONTEND_URL` | CORS | Production frontend URL |
| `PORT` | Server | Server port (default: 8080) |

### Error Response Format

All endpoints return errors in a consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Invalid request parameters |
| `404` | No options data found for the symbol |
| `500` | Internal server error |
| `503` | Required service not available (MCP, pipeline, or AI) |

### Route Decision Tree

```
What do you need?
|
+-- Quick check ---------> GET /
|                          GET /health
|
+-- Single symbol
|   |
|   +-- Fast overview ---> POST /api/options-summary
|   +-- Full risk -------> POST /api/options-risk
|   +-- Risk + AI -------> POST /api/options-ai
|   +-- Everything + AI -> POST /api/options-enhanced
|   +-- Stock or opts? --> POST /api/options-vehicle
|
+-- Multiple symbols ----> POST /api/options-compare
|
+-- Specific trade
|   |
|   +-- Opening spread --> POST /api/spread-trade (action: "open")
|   +-- Closing spread --> POST /api/spread-trade (action: "close")
|
+-- Data refresh
    |
    +-- Many symbols ----> POST /api/pipeline/run
    +-- One symbol ------> POST /api/pipeline/run-single
```
