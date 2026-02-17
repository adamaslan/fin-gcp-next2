# MCP 9 Tools Frontend Integration Guide

A comprehensive guide for understanding and implementing the 9 MCP tools in the frontend UI, with minimal code duplication through shared hooks and components.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [The 9 MCP Tools](#the-9-mcp-tools)
3. [Shared Infrastructure](#shared-infrastructure)
4. [Tier-Based Access Control](#tier-based-access-control)
5. [AI Integration](#ai-integration)
6. [Creating a New Dashboard Page](#creating-a-new-dashboard-page)
7. [Updating MCP Tools](#updating-mcp-tools)
8. [Tool-Specific Examples](#tool-specific-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The MCP (Model Context Protocol) integration is built on three core layers:

### 1. **MCP Client Layer** (`src/lib/mcp/client.ts`)

The client provides a unified interface to all 9 MCP tools. Each method:
- Accepts tool-specific parameters
- Has an optional `useAi` parameter for AI-powered analysis
- Returns structured TypeScript types
- Handles error cases gracefully

```typescript
// Example: All MCP methods support useAi
const result = await mcpClient.compareSecurity(
  { symbols: ['AAPL', 'MSFT'] },
  useAi: true  // Enable Gemini AI analysis
);
```

### 2. **API Routes Layer** (`src/app/api/mcp/*/route.ts`)

Next.js API routes provide:
- Authentication enforcement (Clerk)
- Tier validation and enforcement
- Tool-specific request validation
- AI feature gating per subscription tier

```typescript
// Tier enforcement pattern
const { userId } = await auth();
const { tier } = await getTierForUser(userId);

if (params.useAi && !canAccessAI(tier, 'tool_name')) {
  return Response.json({ error: 'AI not available' }, { status: 403 });
}
```

### 3. **Frontend Component Layer** (`src/app/(dashboard)/**`)

Dashboard pages use shared hooks and components:
- **Hooks**: `useMCPQuery`, `useLazyMCPQuery` - Data fetching logic
- **Components**: `MCPLoadingState`, `MCPErrorState`, `MCPEmptyState`, `AIInsightsPanel` - Consistent UI/UX

```typescript
const { data, loading, error } = useMCPQuery({
  endpoint: '/api/mcp/fibonacci',
  params: { symbol },
  enabled: !!symbol,
});
```

---

## The 9 MCP Tools

| Tool | Purpose | Tier | AI Support | Endpoint |
|------|---------|------|-----------|----------|
| `analyze_security` | Deep analysis of a single security | Free | ✅ | `/api/mcp/analyze` |
| `compare_securities` | Compare multiple securities side-by-side | Pro | ✅ | `/api/mcp/compare` |
| `screen_securities` | Filter stocks by technical criteria | Pro | ✅ | `/api/mcp/screen` |
| `get_trade_plan` | Generate trading strategy | Pro | ✅ | `/api/mcp/trade-plan` |
| `scan_trades` | Identify trading opportunities | Pro | ✅ | `/api/mcp/scan` |
| `portfolio_risk` | Analyze portfolio risk metrics | Pro | ✅ | `/api/mcp/portfolio-risk` |
| `morning_brief` | Daily market summary | Pro | ✅ | `/api/mcp/morning-brief` |
| `analyze_fibonacci` | Fibonacci retracement analysis | Free | ✅ | `/api/mcp/fibonacci` |
| `options_risk_analysis` | Options Greeks and risk metrics | Pro | ✅ | `/api/mcp/options-risk` |

### Free Tier Access
- `analyze_security` (no AI)
- `analyze_fibonacci` (no AI)

### Pro Tier Access (includes Free + Pro)
- All 9 tools with AI analysis

### Max Tier Access
- All 9 tools with AI analysis
- Advanced features and export capabilities

---

## Shared Infrastructure

### useMCPQuery Hook

For tools that run immediately when the page loads:

```typescript
import { useMCPQuery } from '@/hooks/useMCPQuery';

export default function Page({ params: { symbol } }: { params: { symbol: string } }) {
  const { data, loading, error } = useMCPQuery({
    endpoint: '/api/mcp/fibonacci',
    params: { symbol, useAi: true },
    enabled: !!symbol,
    refetchOnParamsChange: true,
  });

  if (loading) return <MCPLoadingState tool="fibonacci" />;
  if (error) return <MCPErrorState error={error} onRetry={() => refetch()} />;
  if (!data) return <MCPEmptyState tool="fibonacci" />;

  return (
    <div>
      {/* Display data */}
      {data.ai_analysis && <AIInsightsPanel analysis={data.ai_analysis} />}
    </div>
  );
}
```

### useLazyMCPQuery Hook

For tools triggered by user action (form submission, button click):

```typescript
import { useLazyMCPQuery } from '@/hooks/useMCPQuery';

export function ComparePage() {
  const { data, loading, error, execute, reset } = useLazyMCPQuery();

  const handleCompare = async (symbols: string[]) => {
    const result = await execute('/api/mcp/compare', {
      symbols,
      useAi: true,
    });
    if (result) {
      // Display results
    }
  };

  return (
    <div>
      <button onClick={() => handleCompare(['AAPL', 'MSFT'])}>
        Compare
      </button>
      {loading && <MCPLoadingState tool="compare" />}
      {error && <MCPErrorState error={error} onRetry={reset} />}
    </div>
  );
}
```

### Shared UI Components

All loading/error/empty states are consistent across tools:

#### MCPLoadingState

```typescript
<MCPLoadingState
  tool="fibonacci" // Shows "Analyzing Fibonacci retracement..."
/>
```

#### MCPErrorState

```typescript
<MCPErrorState
  error="Connection timeout"
  onRetry={() => refetch()}
/>
```

#### MCPEmptyState

```typescript
<MCPEmptyState
  tool="compare" // Shows "Enter symbols to compare"
/>
```

#### AIInsightsPanel

Displays AI analysis in a consistent format:

```typescript
<AIInsightsPanel
  analysis={data.ai_analysis}
  tool="fibonacci"
/>
```

Features:
- Market bias indicator (Bullish/Bearish/Neutral)
- Key drivers with confidence scores
- Action items with priority levels
- Summary of AI reasoning

---

## Tier-Based Access Control

### Client-Side Tier Checking

Use the `useTier` hook to check tier on the frontend:

```typescript
import { useTier } from '@/hooks/useTier';

export function AnalyzePage() {
  const { tier } = useTier();
  const canAccessAI = canAccessAI(tier, 'analyze_security');

  return (
    <div>
      {canAccessAI && (
        <label>
          <input type="checkbox" defaultChecked={true} />
          Enable AI Analysis
        </label>
      )}
    </div>
  );
}
```

### Server-Side Tier Enforcement

Tier validation is enforced at API routes:

```typescript
// src/app/api/mcp/fibonacci/route.ts
import { auth } from '@clerk/nextjs/server';
import { getTierForUser, canAccessAI } from '@/lib/auth/tiers';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) return Response.json({ error: 'Unauthorized' }, { status: 401 });

  const { symbol, useAi } = await req.json();
  const { tier } = await getTierForUser(userId);

  // AI is free for this tool, but check anyway
  if (useAi && !canAccessAI(tier, 'analyze_fibonacci')) {
    return Response.json(
      { error: 'AI analysis not available on your tier' },
      { status: 403 }
    );
  }

  // Call MCP client
  const result = await mcpClient.analyzeFibonacci(symbol, useAi);
  return Response.json(result);
}
```

### Tier-Based Feature Display

Show/hide features based on user tier in the sidebar:

```typescript
// src/components/dashboard/Sidebar.tsx
const navItems: NavItem[] = [
  {
    label: "Analyze",
    href: "/dashboard/analyze/AAPL",
    icon: <Zap className="h-5 w-5" />,
    // No requiresTier = Free tier access
  },
  {
    label: "Compare",
    href: "/dashboard/compare",
    icon: <Scale className="h-5 w-5" />,
    requiresTier: "pro", // Only Pro+ users see this
  },
  {
    label: "Options",
    href: "/dashboard/options",
    icon: <Activity className="h-5 w-5" />,
    requiresTier: "pro",
  },
];
```

---

## AI Integration

### Enabling AI for a Tool

All MCP methods accept a `useAi` parameter:

```typescript
// Without AI
const result = await mcpClient.analyzeFibonacci('AAPL', false);

// With AI
const result = await mcpClient.analyzeFibonacci('AAPL', true);
```

### AI Response Structure

When `useAi: true`, results include an `ai_analysis` field:

```typescript
interface AIAnalysis {
  summary: string;
  market_bias: 'bullish' | 'bearish' | 'neutral';
  confidence: number; // 0-100
  key_drivers: AIKeyDriver[];
  action_items: AIActionItem[];
  risk_assessment: string;
  time_horizon: 'short_term' | 'medium_term' | 'long_term';
}

interface AIKeyDriver {
  driver: string;
  impact: number; // 0-100
  supporting_data: string;
}

interface AIActionItem {
  action: string;
  priority: 'high' | 'medium' | 'low';
  rationale: string;
}
```

### Displaying AI Analysis

Use the `AIInsightsPanel` component to display AI results consistently:

```typescript
{data.ai_analysis && (
  <AIInsightsPanel
    analysis={data.ai_analysis}
    tool="fibonacci"
  />
)}
```

The panel automatically formats:
- **Summary**: AI's interpretation
- **Market Bias**: Visual indicator (bullish/bearish/neutral)
- **Key Drivers**: Impact scored insights
- **Action Items**: Prioritized recommendations
- **Confidence**: Visual confidence indicator

---

## Creating a New Dashboard Page

### Step 1: Create the Page Component

```typescript
// src/app/(dashboard)/my-tool/page.tsx
'use client';

import { useState } from 'react';
import { useLazyMCPQuery } from '@/hooks/useMCPQuery';
import { useTier } from '@/hooks/useTier';
import { canAccessAI } from '@/lib/auth/tiers';
import {
  MCPLoadingState,
  MCPErrorState,
  MCPEmptyState,
  AIInsightsPanel,
} from '@/components/mcp';

export default function MyToolPage() {
  const { tier } = useTier();
  const { data, loading, error, execute, reset } = useLazyMCPQuery();
  const [useAi, setUseAi] = useState(false);

  const handleExecute = async () => {
    await execute('/api/mcp/my-tool', {
      // Your params
      useAi: useAi && canAccessAI(tier, 'my_tool'),
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Tool</h1>
        <p className="text-muted-foreground mt-2">Description</p>
      </div>

      {/* Control panel */}
      <div className="bg-card border rounded-lg p-6 space-y-4">
        {canAccessAI(tier, 'my_tool') && (
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={useAi}
              onChange={(e) => setUseAi(e.target.checked)}
            />
            <span>Enable AI Analysis</span>
          </label>
        )}
        <button onClick={handleExecute} className="w-full">
          Analyze
        </button>
      </div>

      {/* Results */}
      {loading && <MCPLoadingState tool="my-tool" />}
      {error && <MCPErrorState error={error} onRetry={reset} />}
      {!data && !loading && <MCPEmptyState tool="my-tool" />}

      {data && (
        <div className="space-y-6">
          {/* Display your data */}

          {data.ai_analysis && <AIInsightsPanel analysis={data.ai_analysis} />}
        </div>
      )}
    </div>
  );
}
```

### Step 2: Create API Route

```typescript
// src/app/api/mcp/my-tool/route.ts
import { auth } from '@clerk/nextjs/server';
import { getTierForUser, canAccessAI } from '@/lib/auth/tiers';
import { mcpClient } from '@/lib/mcp/client';

export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { tier } = await getTierForUser(userId);
  const { params, useAi } = await req.json();

  // Validate tier access
  if (useAi && !canAccessAI(tier, 'my_tool')) {
    return Response.json(
      { error: 'AI analysis not available on your tier' },
      { status: 403 }
    );
  }

  try {
    const result = await mcpClient.myTool(params, useAi);
    return Response.json(result);
  } catch (error) {
    return Response.json(
      { error: 'Failed to analyze' },
      { status: 500 }
    );
  }
}
```

### Step 3: Add to Sidebar Navigation

```typescript
// src/components/dashboard/Sidebar.tsx
const navItems: NavItem[] = [
  // ... existing items
  {
    label: "My Tool",
    href: "/dashboard/my-tool",
    icon: <IconComponent className="h-5 w-5" />,
    requiresTier: "pro", // If Pro-only
  },
];
```

### Step 4: Add Type Definitions

```typescript
// src/lib/mcp/types.ts
export interface MyToolResult {
  // Your result structure
  data: any;
  ai_analysis?: AIAnalysis;
}
```

### Step 5: Update MCP Client (if needed)

```typescript
// src/lib/mcp/client.ts
async myTool(
  params: MyToolParams,
  useAi = false,
): Promise<MyToolResult> {
  const response = await fetch(`${this.baseUrl}/api/mcp/my-tool`, {
    method: 'POST',
    body: JSON.stringify({ params, useAi }),
  });
  return response.json();
}
```

---

## Updating MCP Tools

### To Add a New Feature to an Existing Tool

1. **Update MCP Server** (Python backend)
   - Add the feature to the MCP tool implementation
   - Return new data in the response

2. **Update Frontend Types** (`src/lib/mcp/types.ts`)
   ```typescript
   export interface AnalyzeFibonacciResult {
     levels: FibonacciLevel[];
     support_resistance: SupportResistance;
     // New field
     momentum_indicators: MomentumIndicators;
     ai_analysis?: AIAnalysis;
   }
   ```

3. **Update MCP Client** (`src/lib/mcp/client.ts`)
   - No changes needed if the backend returns the new field automatically

4. **Update Dashboard Pages**
   - Display the new field in your component

### To Update AI Analysis for a Tool

1. **Update MCP Server** (Python backend)
   - Modify the AI prompt in the MCP tool
   - Return enhanced `ai_analysis` structure

2. **Update Frontend Types** (if structure changed)
   ```typescript
   interface SecurityAIAnalysis extends AIAnalysis {
     // Tool-specific AI fields
     technical_score: number;
     sentiment_analysis: SentimentAnalysis;
   }
   ```

3. **Update AIInsightsPanel** (if displaying new fields)
   - Add custom sections for tool-specific AI data

### Example: Adding Stock Momentum to Analyze

**Backend Change** (Python MCP):
```python
async def analyze_security(symbol: str, use_ai: bool = False):
    # Existing analysis
    result = {
        "price": ...,
        "indicators": ...,
        # New field
        "momentum": calculate_momentum(symbol),
    }
    if use_ai:
        result["ai_analysis"] = await get_ai_analysis(symbol, result)
    return result
```

**Frontend Change**:
```typescript
export interface SecurityAnalysisResult {
  price: PriceData;
  indicators: TechnicalIndicators;
  momentum: MomentumData; // New field
  ai_analysis?: AIAnalysis;
}

// In component
<div className="grid grid-cols-2 gap-4">
  <Card title="Technical Indicators">{/* ... */}</Card>
  <Card title="Momentum">{/* Display momentum data */}</Card>
</div>
```

---

## Tool-Specific Examples

### 1. Analyze Security (Free)

```typescript
// Usage
const result = await mcpClient.analyzeSecurity('AAPL', true);

// Response
{
  symbol: 'AAPL',
  price: { current: 150.25, change: 2.5 },
  technical_indicators: { rsi: 65, macd: 'bullish' },
  sentiment: 'positive',
  ai_analysis: {
    summary: "AAPL shows strong technical signals...",
    market_bias: "bullish",
    key_drivers: [
      { driver: "Strong RSI", impact: 85 },
      { driver: "Positive MACD", impact: 75 }
    ],
    action_items: [
      { action: "Monitor resistance at $155", priority: "high" }
    ]
  }
}
```

### 2. Compare Securities (Pro)

```typescript
const result = await mcpClient.compareSecurity(
  { symbols: ['AAPL', 'MSFT'] },
  true
);

// Response
{
  comparison: [
    {
      symbol: 'AAPL',
      metrics: { pe_ratio: 25, dividend_yield: 0.5 },
      score: 8.5
    },
    {
      symbol: 'MSFT',
      metrics: { pe_ratio: 30, dividend_yield: 0.8 },
      score: 8.2
    }
  ],
  winner: 'AAPL',
  ai_analysis: {
    summary: "AAPL offers better value at current price levels...",
    market_bias: "bullish",
    key_drivers: [...],
    action_items: [...]
  }
}
```

### 3. Screen Securities (Pro)

```typescript
const result = await mcpClient.screenSecurities(
  {
    min_price: 50,
    max_price: 500,
    min_volume: 1000000,
    sectors: ['tech', 'finance']
  },
  true
);

// Response
{
  results: [
    { symbol: 'AAPL', score: 8.5, matches: 5 },
    { symbol: 'MSFT', score: 8.2, matches: 5 }
  ],
  ai_analysis: { /* summary of screening results */ }
}
```

### 4. Get Trade Plan (Pro)

```typescript
const result = await mcpClient.getTradePlan('AAPL', true);

// Response
{
  symbol: 'AAPL',
  signal: 'buy',
  entry_price: 149.50,
  stop_loss: 145.00,
  take_profit: 160.00,
  risk_reward_ratio: 2.1,
  ai_analysis: {
    summary: "Setup meets risk/reward criteria...",
    market_bias: "bullish",
    key_drivers: [...]
  }
}
```

### 5. Scan Trades (Pro)

```typescript
const result = await mcpClient.scanTrades(
  { min_score: 7.0 },
  true
);

// Response
{
  opportunities: [
    {
      symbol: 'AAPL',
      signal: 'buy',
      score: 8.5,
      setup_type: 'breakout'
    }
  ],
  ai_analysis: { /* market-wide summary */ }
}
```

### 6. Portfolio Risk (Pro)

```typescript
const result = await mcpClient.portfolioRisk(
  {
    holdings: [
      { symbol: 'AAPL', quantity: 100 },
      { symbol: 'MSFT', quantity: 50 }
    ]
  },
  true
);

// Response
{
  portfolio_value: 25000,
  var_95: 1250,
  beta: 1.1,
  sharpe_ratio: 1.8,
  sector_allocation: { tech: 100 },
  ai_analysis: {
    summary: "Portfolio is well-diversified within tech sector...",
    risk_level: "moderate",
    key_drivers: [
      { driver: "Tech concentration", impact: 60 }
    ]
  }
}
```

### 7. Morning Brief (Pro)

```typescript
const result = await mcpClient.morningBrief(true);

// Response
{
  date: '2024-01-15',
  market_overview: { trend: 'up', sentiment: 'bullish' },
  key_events: ['Fed Meeting', 'Earnings: AAPL'],
  top_gainers: [{ symbol: 'NVDA', change: 5.2 }],
  ai_analysis: {
    summary: "Market momentum remains strong...",
    opportunities: [...]
  }
}
```

### 8. Analyze Fibonacci (Free)

```typescript
const result = await mcpClient.analyzeFibonacci('AAPL', true);

// Response
{
  symbol: 'AAPL',
  levels: [
    { level: 0.236, price: 148.50, proximity: 'near' },
    { level: 0.382, price: 146.75, proximity: 'support' },
    { level: 0.618, price: 143.00, proximity: 'strong_support' }
  ],
  trend: 'uptrend',
  ai_analysis: {
    summary: "Price near 23.6% retracement level...",
    market_bias: "bullish",
    key_drivers: [
      { driver: "Above 23.6% level", impact: 70 }
    ]
  }
}
```

### 9. Options Risk Analysis (Pro)

```typescript
const result = await mcpClient.optionsRiskAnalysis(
  'AAPL',
  'call',
  { strike: 155, expiry: '2024-02-16', contracts: 5 },
  true
);

// Response
{
  symbol: 'AAPL',
  position: {
    type: 'call',
    strike: 155,
    expiry: '2024-02-16',
    contracts: 5
  },
  greeks: {
    delta: 0.65,
    gamma: 0.025,
    theta: -0.15,
    vega: 0.45
  },
  risk_metrics: {
    max_loss: 5000,
    max_gain: 10000,
    breakeven: 156.50
  },
  ai_analysis: {
    summary: "Position has favorable risk/reward...",
    risk_level: "moderate",
    key_drivers: [...]
  }
}
```

---

## Best Practices

### 1. Always Check Tier Before Offering Features

```typescript
const canUseAI = canAccessAI(tier, 'tool_name');

{canUseAI && (
  <button onClick={() => setUseAi(true)}>
    Enhance with AI
  </button>
)}
```

### 2. Show Clear Error Messages

Use specific error messages that help users understand what went wrong:

```typescript
{error && (
  <MCPErrorState
    error={error}
    suggestion="Check your internet connection or try again later"
    onRetry={reset}
  />
)}
```

### 3. Handle Loading States Gracefully

Show meaningful loading messages specific to the tool:

```typescript
<MCPLoadingState
  tool="compare"
  message="Comparing securities..."
/>
```

### 4. Leverage Hooks for Code Reuse

Don't duplicate fetch logic across pages:

```typescript
// ✅ Good: Use shared hook
const { data, loading, error } = useMCPQuery({
  endpoint: '/api/mcp/analyze',
  params: { symbol }
});

// ❌ Avoid: Duplicating fetch logic
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);
useEffect(() => {
  setLoading(true);
  fetch('/api/mcp/analyze', { body: JSON.stringify({ symbol }) })
    .then(r => r.json())
    .then(setData)
    .finally(() => setLoading(false));
}, [symbol]);
```

### 5. Use Lazy Queries for User-Triggered Actions

For tools that run on demand:

```typescript
const { data, execute } = useLazyMCPQuery();

<button onClick={() => execute('/api/mcp/compare', { symbols })}>
  Compare
</button>
```

### 6. Display AI Analysis Consistently

Always use `AIInsightsPanel` for AI results:

```typescript
{data?.ai_analysis && (
  <AIInsightsPanel analysis={data.ai_analysis} />
)}
```

### 7. Validate Inputs Before Sending

```typescript
const handleAnalyze = async (symbols: string[]) => {
  if (!symbols.length) {
    setError('Please select at least one symbol');
    return;
  }

  if (symbols.length > 10) {
    setError('Maximum 10 symbols allowed');
    return;
  }

  const result = await execute('/api/mcp/compare', { symbols });
};
```

### 8. Cache Results When Appropriate

The `useMCPQuery` hook automatically handles caching:

```typescript
const { data, loading } = useMCPQuery({
  endpoint: '/api/mcp/analyze',
  params: { symbol },
  // Hook automatically caches based on params
});
```

### 9. Handle Rate Limiting Gracefully

```typescript
if (error?.includes('429')) {
  return (
    <div className="bg-yellow-50 p-4 rounded">
      <p>Too many requests. Please wait a moment before trying again.</p>
    </div>
  );
}
```

### 10. Test AI Features with Different Tier Levels

```typescript
// Ensure Pro-only features are properly gated
const canAccessAI = tier === 'pro' || tier === 'max';

if (useAi && !canAccessAI) {
  setError('AI analysis requires Pro tier');
}
```

---

## Troubleshooting

### Issue: AI Analysis Not Appearing

**Causes:**
1. User's tier doesn't allow AI
2. API route not validating `useAi` correctly
3. AI analysis failed to generate

**Solution:**
```typescript
// Check tier first
if (useAi && !canAccessAI(tier, 'tool_name')) {
  console.log('AI not available for this tier');
  return;
}

// Check API response
console.log('Response includes ai_analysis:', !!data?.ai_analysis);

// Check component is rendering
{data?.ai_analysis && <AIInsightsPanel analysis={data.ai_analysis} />}
```

### Issue: Tool Page Not Appearing in Sidebar

**Solution:**
1. Check `requiresTier` matches your tier
2. Verify page file exists at correct path
3. Check sidebar import of icon

```typescript
// src/components/dashboard/Sidebar.tsx
import { YourIcon } from 'lucide-react';

const navItems: NavItem[] = [
  {
    label: "Your Tool",
    href: "/dashboard/your-tool", // Must match page file
    icon: <YourIcon className="h-5 w-5" />,
    requiresTier: "pro", // Check your tier
  },
];
```

### Issue: API Route Returns 403

**Cause:** Tier enforcement is preventing access

**Solution:**
```typescript
// Verify user tier
const { tier } = await getTierForUser(userId);
console.log('User tier:', tier);

// Check canAccessAI function
console.log('Can access AI:', canAccessAI(tier, 'tool_name'));

// Ensure API validation matches frontend
if (useAi && !canAccessAI(tier, 'tool_name')) {
  // This is expected behavior for tier gating
  return Response.json({ error: 'Upgrade to Pro' }, { status: 403 });
}
```

### Issue: Data Not Loading

**Causes:**
1. Symbol/params are empty
2. Network connectivity issue
3. MCP server is down

**Solution:**
```typescript
// Check enabled condition
const { data, loading, error } = useMCPQuery({
  endpoint: '/api/mcp/analyze',
  params: { symbol },
  enabled: !!symbol, // Make sure this is true
});

console.log('Loading:', loading);
console.log('Error:', error);
console.log('Data:', data);

// Check MCP server status
// Run: npm run health-check
```

### Issue: Duplicate Data Fetches

**Cause:** Not using hooks properly

**Solution:**
```typescript
// ✅ Correct: Use hook once
const { data } = useMCPQuery({ endpoint, params });

// ❌ Wrong: Multiple fetches
useEffect(() => {
  fetch(endpoint); // First fetch
}, []);

const { data } = useMCPQuery({ endpoint, params }); // Second fetch
```

---

## Code Examples by Tool

### Complete Compare Page Example

```typescript
// src/app/(dashboard)/compare/page.tsx
'use client';

import { useState } from 'react';
import { useLazyMCPQuery } from '@/hooks/useMCPQuery';
import { useTier } from '@/hooks/useTier';
import { canAccessAI } from '@/lib/auth/tiers';
import {
  MCPLoadingState,
  MCPErrorState,
  MCPEmptyState,
  AIInsightsPanel,
} from '@/components/mcp';

export default function ComparePage() {
  const { tier } = useTier();
  const { data, loading, error, execute, reset } = useLazyMCPQuery();
  const [symbols, setSymbols] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const [useAi, setUseAi] = useState(false);

  const handleAddSymbol = () => {
    if (input && !symbols.includes(input.toUpperCase())) {
      setSymbols([...symbols, input.toUpperCase()]);
      setInput('');
    }
  };

  const handleRemoveSymbol = (symbol: string) => {
    setSymbols(symbols.filter(s => s !== symbol));
  };

  const handleCompare = async () => {
    const result = await execute('/api/mcp/compare', {
      symbols,
      useAi: useAi && canAccessAI(tier, 'compare_securities'),
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Compare Securities</h1>
        <p className="text-muted-foreground">
          Compare up to 10 securities side-by-side
        </p>
      </div>

      <div className="bg-card border rounded-lg p-6 space-y-4">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value.toUpperCase())}
            placeholder="Enter symbol (e.g., AAPL)"
            onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
          />
          <button onClick={handleAddSymbol}>Add</button>
        </div>

        <div className="flex flex-wrap gap-2">
          {symbols.map(symbol => (
            <div key={symbol} className="bg-primary/10 px-3 py-1 rounded-full flex items-center gap-2">
              <span>{symbol}</span>
              <button
                onClick={() => handleRemoveSymbol(symbol)}
                className="text-xs hover:text-red-500"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        {canAccessAI(tier, 'compare_securities') && (
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={useAi}
              onChange={(e) => setUseAi(e.target.checked)}
            />
            <span>Enable AI Analysis</span>
          </label>
        )}

        <button
          onClick={handleCompare}
          disabled={!symbols.length || loading}
          className="w-full"
        >
          {loading ? 'Comparing...' : 'Compare'}
        </button>
      </div>

      {loading && <MCPLoadingState tool="compare" />}
      {error && <MCPErrorState error={error} onRetry={() => reset()} />}
      {!data && !loading && symbols.length === 0 && (
        <MCPEmptyState tool="compare" />
      )}

      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.comparison.map((item: any) => (
              <div key={item.symbol} className="border rounded-lg p-4">
                <h3 className="font-bold">{item.symbol}</h3>
                <div className="mt-4 space-y-2">
                  <div>P/E Ratio: {item.metrics.pe_ratio}</div>
                  <div>Dividend Yield: {item.metrics.dividend_yield}%</div>
                  <div>Score: {item.score}/10</div>
                </div>
              </div>
            ))}
          </div>

          {data.winner && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="font-semibold text-green-900">
                Winner: {data.winner}
              </p>
            </div>
          )}

          {data.ai_analysis && <AIInsightsPanel analysis={data.ai_analysis} />}
        </div>
      )}
    </div>
  );
}
```

---

## Summary

The 9 MCP tools are integrated into the frontend through:

1. **Shared Hooks** (`useMCPQuery`, `useLazyMCPQuery`) - Eliminate duplicated fetch logic
2. **Shared Components** (MCPLoadingState, MCPErrorState, etc.) - Consistent UI/UX
3. **Type-Safe Client** (mcpClient) - Unified interface to all tools
4. **Tier-Based Access** - Enforce subscription limits at API and UI layers
5. **AI Integration** - Optional AI analysis for all tools with `useAi` parameter

To add a new dashboard page:
1. Create page component with hooks
2. Create API route with tier validation
3. Add sidebar navigation link
4. Update types if needed

For more details on the MCP server implementation, see `MCP-IMPLEMENTATION-CHECKLIST.md` and `mcp-tools-implementation-guide.md`.
