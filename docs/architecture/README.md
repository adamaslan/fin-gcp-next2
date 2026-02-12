# Architecture Documentation

This section covers the overall system design, how components interact, and the architectural decisions behind MCP Finance.

---

## Quick Navigation

### Core Architecture
- **System Overview:** [`system-overview.md`](system-overview.md) - High-level system design
- **Database Schema:** [`database-schema.md`](database-schema.md) - Table structures and relationships
- **Frontend-Backend Connection:** [`frontend-backend-connection.md`](frontend-backend-connection.md) - How frontend talks to MCP server
- **Signal Framework:** [`signal-indicators.md`](signal-indicators.md) - 150+ trading signals explained
- **Tier System:** [`tier-system.md`](tier-system.md) - Pricing tiers and features

---

## Architecture Overview

MCP Finance is a three-tier system:

```
┌─────────────────────────────────┐
│   Frontend (Next.js/React)      │  User Interface
│   - Clerk Authentication        │  - Portfolio Dashboard
│   - Stripe Payments             │  - Signal Analysis
│   - TanStack Query              │  - Watchlists
└────────────┬────────────────────┘
             │ API Calls
┌────────────▼────────────────────┐
│   Backend (Python MCP Server)   │  Business Logic
│   - FastAPI Routes              │  - 150+ Indicators
│   - Signal Calculation          │  - Risk Analysis
│   - Market Data Integration     │  - Watchlist Management
└────────────┬────────────────────┘
             │ SQL Queries
┌────────────▼────────────────────┐
│   Database (PostgreSQL/Neon)    │  Data Storage
│   - Users & Portfolios          │  - Market Data
│   - Watchlists & Alerts         │  - Calculation Cache
└─────────────────────────────────┘
```

---

## Key Architectural Patterns

### 1. MCP (Model Context Protocol) Backend
- Specialized Python server for financial analysis
- Real-time signal calculation
- Market data processing
- Scales independently from frontend

### 2. Next.js Server Components
- Server-side rendering for performance
- Reduced JavaScript bundle size
- Better data fetching at source
- Secure API calls from server

### 3. PostgreSQL Persistence
- User data and portfolios
- Watchlists and alerts
- Market data cache
- Transaction history

### 4. Signal-Based Analysis
- 150+ built-in trading signals
- Custom indicator combinations
- Risk layer framework
- Extensible signal system

---

## Topics Covered

| Topic | File | Focus |
|-------|------|-------|
| System design | `system-overview.md` | High-level architecture |
| Database | `database-schema.md` | Table structures, relationships |
| API Integration | `frontend-backend-connection.md` | How frontend calls backend |
| Signals | `signal-indicators.md` | 150+ indicators explained |
| Features | `tier-system.md` | Feature tiers, pricing logic |

---

## For Different Roles

**Frontend Developers:**
- Read: [`frontend-backend-connection.md`](frontend-backend-connection.md)
- Reference: [`system-overview.md`](system-overview.md) for context
- Check: API endpoint structure in backend docs

**Backend Developers:**
- Read: [`system-overview.md`](system-overview.md)
- Study: [`database-schema.md`](database-schema.md)
- Implement: [`signal-indicators.md`](signal-indicators.md)

**Full-Stack Developers:**
- Read ALL in this section
- Understand end-to-end data flow
- Know all component responsibilities

**DevOps/Infrastructure:**
- Read: [`system-overview.md`](system-overview.md)
- Reference: [`database-schema.md`](database-schema.md) for storage needs
- Plan: Infrastructure based on component requirements

---

## Key Concepts

### Trading Signals
150+ indicators that evaluate stock performance. Examples:
- Momentum indicators (RSI, MACD)
- Trend indicators (Moving Averages)
- Volatility indicators (Bollinger Bands)
- Volume indicators
- Sentiment indicators

See: [`signal-indicators.md`](signal-indicators.md)

### Risk Layers
Multi-level risk assessment:
- Signal confidence scores
- Portfolio concentration risk
- Market volatility assessment
- Custom risk thresholds

See: [`tier-system.md`](tier-system.md)

### Watchlists
User-created portfolios of stocks:
- Custom alert thresholds
- Signal tracking
- Performance monitoring
- Automated analysis updates

See: [`database-schema.md`](database-schema.md)

---

## Data Flow Examples

### User Views Dashboard
1. User loads `/dashboard` in browser (Next.js)
2. Next.js server calls MCP backend API
3. MCP calculates signals for user's portfolios
4. Database provides portfolio data
5. Frontend renders with results

See: [`frontend-backend-connection.md`](frontend-backend-connection.md)

### Signal Calculation
1. Market data arrives (via external API)
2. MCP backend processes data
3. All 150+ signals calculated
4. Results cached in database
5. Frontend displays latest analysis

See: [`signal-indicators.md`](signal-indicators.md)

---

## Important Files to Reference

- **Project Guidelines:** `./.claude/CLAUDE.md`
- **Database Migrations:** `./docs/backend/`
- **API Endpoints:** `./docs/api-reference/`
- **Frontend Setup:** `./docs/frontend/`
- **Backend Setup:** `./docs/backend/`

---

## Next Steps

1. **Understand the System:**
   - Start with [`system-overview.md`](system-overview.md)

2. **Know the Database:**
   - Study [`database-schema.md`](database-schema.md)

3. **Learn Component Integration:**
   - Read [`frontend-backend-connection.md`](frontend-backend-connection.md)

4. **Dive Into Your Area:**
   - Frontend? → [`../frontend/README.md`](../frontend/README.md)
   - Backend? → [`../backend/README.md`](../backend/README.md)
   - DevOps? → [`../devops/README.md`](../devops/README.md)

---

[← Back to Documentation](../README.md)
