# MCP-Frontend Integration Guide

**Complete technical reference for integrating all 9 MCP tools into the frontend**

---

## Quick Navigation

- [Architecture Overview](#architecture-overview)
- [The 9 MCP Tools](#the-9-mcp-tools)
- [Data Flow](#data-flow)
- [MCP Client Layer](#mcp-client-layer)
- [API Routes Layer](#api-routes-layer)
- [UI Component Layer](#ui-component-layer)
- [AI Analysis](#ai-analysis)
- [How to Update MCP Tools](#how-to-update-mcp-tools)
- [Adding New Data](#adding-new-data-to-frontend)
- [Tier-Based Access](#tier-based-access-control)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Complete Data Flow

```
┌────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                  │
├────────────────────────────────────────────────────────┤
│                                                         │
│  React Components (9 Tool Pages)                       │
│          ↓                                              │
│  Hooks: useMCPQuery, useTier, useAIAnalysis            │
│          ↓                                              │
│  Shared Components: AIInsights, Loading, Error        │
│          ↓                                              │
│  Next.js API Routes (/api/mcp/[tool])                 │
│  - Authenticate (Clerk)                               │
│  - Check usage limits                                 │
│  - Validate tier                                      │
│          ↓                                              │
│  MCP Client (lib/mcp/client.ts)                       │
│  - 9 tool methods                                     │
│  - HTTP client                                        │
│          ↓                                              │
└────────────────────────────────────────────────────────┘
        HTTP POST ↓
┌────────────────────────────────────────────────────────┐
│                BACKEND (Python)                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│  FastAPI Server                                        │
│  - 9 endpoints (/api/[tool])                          │
│  - Market data fetching                               │
│  - Technical analysis                                 │
│  - AI analysis (if use_ai=true)                       │
│          ↓                                              │
│  Gemini 1.5 Flash (if use_ai=true)                   │
│  - Market bias analysis                               │
│  - Key drivers                                        │
│  - Action items                                       │
│          ↓                                              │
│  Response JSON → Frontend                             │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## The 9 MCP Tools

### Reference Table

| # | Tool | Purpose | Page | AI | Status |
|---|------|---------|------|-----|--------|
| 1 | analyze_security | Deep technical analysis | `/analyze/[symbol]` | ✅ | ✅ Live |
| 2 | compare_securities | Compare stocks | `/compare` | ❌ | 🔨 New |
| 3 | screen_securities | Filter by criteria | `/scanner` | ❌ | ✅ Live |
| 4 | get_trade_plan | Entry/stop/target | `/analyze/[symbol]` | ❌ | ✅ Live |
| 5 | scan_trades | Find setups | `/scanner` | ❌ | ✅ Live |
| 6 | portfolio_risk | Risk assessment | `/portfolio` | ❌ | ⏳ New |
| 7 | morning_brief | Market briefing | `/` (dashboard) | ❌ | ✅ Live |
| 8 | analyze_fibonacci | Fib levels | `/fibonacci` | ❌ | ✅ Live |
| 9 | options_risk_analysis | Options sentiment | `/options` | ❌ | 🔨 New |

---

## Data Flow

### Simple Example: User Analyzes AAPL

```
1. User types "AAPL" in symbol input
   ↓
2. Component calls useMCPQuery hook
   const { data, loading } = useMCPQuery({
     endpoint: '/api/mcp/analyze',
     params: { symbol: 'AAPL', use_ai: true }
   })
   ↓
3. Hook makes HTTP POST
   POST /api/mcp/analyze
   Body: { symbol: 'AAPL', use_ai: true }
   ↓
4. API route processes
   - Auth with Clerk
   - Check daily limit
   - Validate tier
   ↓
5. MCP Client calls
   await mcp.analyzeSecurity('AAPL', '1mo', true)
   ↓
6. HTTP to Python server
   POST http://mcp-server:8000/api/analyze
   ↓
7. Python server
   - Gets market data
   - Calculates indicators
   - (if use_ai) calls Gemini
   ↓
8. Response back through all layers
   ↓
9. Component receives data
   {
     symbol: 'AAPL',
     price: 150.25,
     indicators: {...},
     signals: [...],
     ai_analysis: {...}
   }
   ↓
10. Component renders
    <PriceDisplay price={data.price} />
    <SignalsList signals={data.signals} />
    <AIInsightsPanel analysis={data.ai_analysis} />
```

---

## MCP Client Layer

### Location
`src/lib/mcp/client.ts`

### Interface

```typescript
class MCPClient {
  // All 9 methods follow this pattern:
  async toolMethod(param1: T, param2?: T, useAi?: boolean): Promise<Result<T>>
}
```

### All 9 Methods

```typescript
// 1. Analyze Security
async analyzeSecurity(
  symbol: string,
  period: string = '1mo',
  useAi: boolean = false
): Promise<AnalysisResult>

// 2. Compare Securities (NEW)
async compareSecurity(
  symbols: string[],
  metric: string = 'signals',
  useAi: boolean = false
): Promise<ComparisonResult>

// 3. Screen Securities
async screenSecurities(
  universe: string = 'sp500',
  criteria: ScreeningCriteria = {},
  limit: number = 20,
  useAi: boolean = false
): Promise<ScreeningResult>

// 4. Get Trade Plan
async getTradePlan(
  symbol: string,
  period: string = '1mo',
  useAi: boolean = false
): Promise<TradePlanResult>

// 5. Scan Trades
async scanTrades(
  universe: string = 'sp500',
  maxResults: number = 10,
  useAi: boolean = false
): Promise<ScanResult>

// 6. Portfolio Risk
async portfolioRisk(
  positions: PortfolioPosition[],
  useAi: boolean = false
): Promise<PortfolioRiskResult>

// 7. Morning Brief
async morningBrief(
  watchlist: string[] = [],
  marketRegion: string = 'US',
  useAi: boolean = false
): Promise<MorningBriefResult>

// 8. Analyze Fibonacci
async analyzeFibonacci(
  symbol: string,
  period: string = '1d',
  window: number = 50,
  useAi: boolean = false
): Promise<FibonacciAnalysisResult>

// 9. Options Risk Analysis (NEW)
async optionsRiskAnalysis(
  symbol: string,
  positionType: 'call' | 'put' | 'spread',
  options?: OptionsParams,
  useAi: boolean = false
): Promise<OptionsRiskResult>
```

---

## API Routes Layer

### Standard Pattern

Every MCP API route follows this structure:

```typescript
// /api/mcp/[tool]/route.ts
import { NextResponse } from 'next/server';
import { getMCPClient } from '@/lib/mcp';
import { ensureUserInitialized } from '@/lib/auth/user-init';
import { checkUsageLimit } from '@/lib/auth/usage-limits';
import { TIER_LIMITS } from '@/lib/auth/tiers';

export async function POST(request: Request) {
  try {
    // 1. AUTHENTICATE
    const { userId, tier } = await ensureUserInitialized();

    // 2. PARSE REQUEST
    const { param1, param2, use_ai } = await request.json();

    // 3. VALIDATE INPUT
    if (!param1) {
      return NextResponse.json(
        { error: 'param1 required' },
        { status: 400 }
      );
    }

    // 4. CHECK USAGE (if applicable)
    const canUseFeature = await checkUsageLimit(userId, 'tool_name');
    if (!canUseFeature) {
      return NextResponse.json(
        { error: 'Daily limit reached' },
        { status: 429 }
      );
    }

    // 5. VALIDATE TIER
    const tierConfig = TIER_LIMITS[tier];
    if (!tierConfig.tool_name) {
      return NextResponse.json(
        { error: 'Upgrade required' },
        { status: 403 }
      );
    }

    // 6. CALL MCP CLIENT
    const mcp = getMCPClient();
    const canUseAi = tierConfig.tool_name.ai;
    const result = await mcp.toolMethod(
      param1,
      param2,
      use_ai && canUseAi
    );

    // 7. APPLY TIER FILTERING (if needed)
    const filtered = filterByTier(result, tier, 'tool_name');

    // 8. RETURN RESPONSE
    return NextResponse.json({
      ...filtered,
      tierLimit: { daily: tierConfig.tool_name.daily }
    });

  } catch (error) {
    console.error('[API /mcp/tool] Error:', error);

    if (error.message.includes('MCP API error')) {
      return NextResponse.json(
        { error: 'Service unavailable' },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: 'Request failed' },
      { status: 500 }
    );
  }
}
```

### Route Mapping

| Route | MCP Tool | Method |
|-------|----------|--------|
| `/api/mcp/analyze` | analyze_security | analyzeSecurity() |
| `/api/mcp/compare` | compare_securities | compareSecurity() |
| `/api/mcp/screen` | screen_securities | screenSecurities() |
| `/api/mcp/trade-plan` | get_trade_plan | getTradePlan() |
| `/api/mcp/scan` | scan_trades | scanTrades() |
| `/api/mcp/portfolio-risk` | portfolio_risk | portfolioRisk() |
| `/api/dashboard/morning-brief` | morning_brief | morningBrief() |
| `/api/mcp/fibonacci` | analyze_fibonacci | analyzeFibonacci() |
| `/api/mcp/options-risk` | options_risk_analysis | optionsRiskAnalysis() |

---

## UI Component Layer

### Page Structure Pattern

```typescript
// /app/(dashboard)/[tool]/page.tsx
'use client';

import { useState } from 'react';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { useTier } from '@/hooks/useTier';
import { MCPLoadingState } from '@/components/mcp/MCPLoadingState';
import { MCPErrorState } from '@/components/mcp/MCPErrorState';
import { AIInsightsPanel } from '@/components/mcp/AIInsightsPanel';
import { TierGate } from '@/components/gating/TierGate';

export default function ToolPage() {
  // STATE
  const [params, setParams] = useState({});
  const [aiEnabled, setAiEnabled] = useState(false);
  const { tier } = useTier();

  // DATA FETCHING
  const { data, loading, error, refetch } = useMCPQuery({
    endpoint: '/api/mcp/tool',
    params: { ...params, use_ai: aiEnabled },
    enabled: !!params.required,
  });

  // LOADING
  if (loading) return <MCPLoadingState tool="tool_name" />;

  // ERROR
  if (error) return <MCPErrorState error={error} onRetry={refetch} />;

  // EMPTY
  if (!data) return <div>No data</div>;

  // RENDER
  return (
    <div className="space-y-6">
      {/* Controls */}
      <ToolControls />

      {/* AI Toggle */}
      <TierGate feature="ai-analysis" requiredTier="pro">
        <label>
          <input
            type="checkbox"
            checked={aiEnabled}
            onChange={(e) => setAiEnabled(e.target.checked)}
          />
          AI Analysis
        </label>
      </TierGate>

      {/* Main Content */}
      <ToolDataDisplay data={data} />

      {/* AI Insights */}
      {data.ai_analysis && (
        <AIInsightsPanel analysis={data.ai_analysis} tool="tool_name" />
      )}
    </div>
  );
}
```

### Shared Components

All pages use these components:

1. **AIInsightsPanel** - Display AI analysis
2. **MCPLoadingState** - Consistent loading indicator
3. **MCPErrorState** - Consistent error message + retry
4. **MCPEmptyState** - Consistent empty state
5. **TierGate** - Feature access control

---

## AI Analysis

### How AI Works

```
1. User requests analysis with use_ai=true

2. API route checks tier
   const canUseAi = TIER_LIMITS[tier].tool.ai;

3. MCP client receives use_ai parameter
   await mcp.tool(symbol, period, use_ai && canUseAi)

4. Python server:
   - Gets raw data
   - If use_ai & GEMINI_API_KEY:
     • Sends to Gemini
     • Gets AI analysis
     • Adds to response

5. Response includes:
   {
     symbol: 'AAPL',
     price: 150.25,
     indicators: {...},
     ai_analysis: {
       market_bias: 'BULLISH',
       bias_explanation: '...',
       key_drivers: [...],
       action_items: [...],
       summary: '...'
     }
   }

6. Component displays with AIInsightsPanel
```

### AI Response Structure

All tools return consistent AI analysis:

```typescript
interface AIAnalysis {
  // Always present
  summary: string;

  // Common
  market_bias?: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  bias_explanation?: string;

  // Structured insights
  key_drivers?: {
    signal: string;
    importance: 'HIGH' | 'MEDIUM' | 'LOW';
    explanation: string;
  }[];

  // Actionable
  action_items?: {
    priority: number;
    timeframe: 'IMMEDIATE' | 'TODAY' | 'THIS_WEEK';
    action: string;
  }[];

  // Risk factors
  risk_factors?: string[];

  // Confidence
  confidence_score?: number;
}
```

---

## How to Update MCP Tools

### Adding a New Field

**Example**: Add `sector` field to analyze_security

#### Step 1: Update Python Server

```python
# server.py
async def analyze_security(symbol: str) -> dict:
    sector = await get_sector(symbol)
    return {
        "symbol": symbol,
        "sector": sector,  # NEW
        # ... rest
    }
```

#### Step 2: Update TypeScript Type

```typescript
// types.ts
export interface AnalysisResult {
  symbol: string;
  sector: string;  // NEW
  // ... rest
}
```

#### Step 3: Display in Component

```typescript
<Badge>{data.sector}</Badge>
```

### Adding a New MCP Tool

**Follow this checklist**:

1. ✅ Python server endpoint
2. ✅ AI analyzer method (if use_ai support)
3. ✅ TypeScript types
4. ✅ MCP client method
5. ✅ API route
6. ✅ Component/page
7. ✅ Navigation update
8. ✅ Tests

**Reference**: Implementation Guide → Each Tool section

---

## Adding New Data to Frontend

### Quick Checklist

- [ ] Python server returns the data
- [ ] TypeScript types updated
- [ ] MCP client method updated (if new param)
- [ ] API route passes data
- [ ] Component receives + displays
- [ ] Loading state handles shape
- [ ] Error state handles failures
- [ ] Tier restrictions applied

---

## Tier-Based Access Control

### Tier Configuration

```typescript
export const TIER_LIMITS = {
  free: {
    analyze_security: { daily: 5, ai: false },
    compare_securities: false,
    // ... etc
  },
  pro: {
    analyze_security: { daily: 50, ai: true },
    compare_securities: { maxSymbols: 5, ai: true },
    // ... etc
  },
  max: {
    analyze_security: { daily: Infinity, ai: true },
    // ... all enabled
  }
};
```

### Enforcement Points

1. **API Route** (backend security)
```typescript
if (!TIER_LIMITS[tier].tool_name) {
  return NextResponse.json({ error: '403' });
}
```

2. **Component Gating** (frontend UX)
```typescript
<TierGate feature="options_risk" requiredTier="pro">
  <OptionAnalysis />
</TierGate>
```

3. **Feature Toggling**
```typescript
const canUseAi = TIER_LIMITS[tier].tool.ai;
```

---

## Troubleshooting

### MCP Server Not Responding

**Error**: `MCP API error (503)`

**Solution**:
```bash
# Check server
curl http://localhost:8000/health

# Start server
cd mcp-finance1
mamba activate fin-ai1
uvicorn src.technical_analysis_mcp.server:app --port 8000
```

### AI Analysis Returns Null

**Error**: `ai_analysis: null`

**Solution**:
```bash
# Check API key
echo $GEMINI_API_KEY

# Set if missing
export GEMINI_API_KEY='your-key'
```

### Type Errors After Update

**Error**: `Type missing property 'newField'`

**Solution**:
1. Update types.ts
2. Run `npm run build`
3. Restart dev server

### Tier Restrictions Not Working

**Check**:
```typescript
const { tier } = useTier();
console.log('Tier:', tier);

// In API
console.log('Limit:', TIER_LIMITS[tier]);
```

---

**For complete examples**: See [mcp-tools-implementation-guide.md](mcp-tools-implementation-guide.md)

**For refactoring details**: See [mcp-ui-refactor-plan.md](mcp-ui-refactor-plan.md)
