# MCP Tools - Complete Implementation Guide

**Detailed implementation examples for all 9 MCP tools with UI integration**

---

## Table of Contents

1. [Tool #1: analyze_security](#tool-1-analyze_security)
2. [Tool #2: compare_securities](#tool-2-compare_securities)
3. [Tool #3: screen_securities](#tool-3-screen_securities)
4. [Tool #4: get_trade_plan](#tool-4-get_trade_plan)
5. [Tool #5: scan_trades](#tool-5-scan_trades)
6. [Tool #6: portfolio_risk](#tool-6-portfolio_risk)
7. [Tool #7: morning_brief](#tool-7-morning_brief)
8. [Tool #8: analyze_fibonacci](#tool-8-analyze_fibonacci)
9. [Tool #9: options_risk_analysis](#tool-9-options_risk_analysis)

---

## Tool #1: analyze_security

### Purpose
Deep technical analysis of a single stock examining price action, momentum, volatility, and trend strength across multiple timeframes.

### Frontend Page
**Location**: `/src/app/(dashboard)/analyze/[symbol]/page.tsx`

**URL**: `/analyze/AAPL`

### Data Flow

```
User enters symbol "AAPL"
     ↓
Component calls useMCPQuery()
     ↓
POST /api/mcp/analyze
Body: { symbol: "AAPL", period: "1mo", use_ai: true }
     ↓
MCP Client: analyzeSecurity("AAPL", "1mo", true)
     ↓
Python Server: /api/analyze
     ↓
Returns: AnalysisResult with signals, indicators, AI analysis
     ↓
Component displays: Price, signals, indicators, AI insights
```

### Complete Example Implementation

**1. Component (Page)**

```typescript
// src/app/(dashboard)/analyze/[symbol]/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { useTier } from '@/hooks/useTier';
import { AnalysisResult } from '@/lib/mcp/types';
import { MCPLoadingState } from '@/components/mcp/MCPLoadingState';
import { MCPErrorState } from '@/components/mcp/MCPErrorState';
import { AIInsightsPanel } from '@/components/mcp/AIInsightsPanel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TierGate } from '@/components/gating/TierGate';

interface PageProps {
  params: Promise<{ symbol: string }>;
}

const PERIODS = ['1w', '1mo', '3mo', '6mo', '1y'];
const TIMEFRAMES = ['1h', '4h', '1d'];

export default function AnalyzePage({ params }: PageProps) {
  const { symbol: initialSymbol } = use(params);
  const { tier } = useTier();

  // State
  const [symbol, setSymbol] = useState(initialSymbol.toUpperCase());
  const [period, setPeriod] = useState('1mo');
  const [aiEnabled, setAiEnabled] = useState(tier !== 'free');
  const [userSymbol, setUserSymbol] = useState('');

  // Data fetching
  const { data, loading, error, refetch } = useMCPQuery<AnalysisResult>({
    endpoint: '/api/mcp/analyze',
    params: { symbol, period, use_ai: aiEnabled },
    enabled: !!symbol,
  });

  // Handle custom symbol search
  const handleAnalyze = () => {
    if (userSymbol.trim()) {
      setSymbol(userSymbol.toUpperCase());
    }
  };

  // Loading state
  if (loading) {
    return <MCPLoadingState tool="analyze_security" />;
  }

  // Error state
  if (error) {
    return <MCPErrorState error={error} onRetry={refetch} />;
  }

  // No data
  if (!data) {
    return (
      <div className="space-y-4">
        <SymbolSearchInput onAnalyze={handleAnalyze} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-baseline gap-4">
          <h1 className="text-4xl font-bold">{data.symbol}</h1>
          <span className="text-2xl font-semibold">${data.price.toFixed(2)}</span>
          <Badge variant={data.change >= 0 ? 'default' : 'destructive'}>
            {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}%
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          {new Date(data.timestamp).toLocaleString()}
        </p>
      </div>

      {/* Controls */}
      <div className="flex gap-4 flex-wrap">
        <div>
          <label className="text-sm font-medium">Period</label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="border rounded px-2 py-1"
          >
            {PERIODS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        {/* AI Toggle */}
        <TierGate feature="ai-analysis" requiredTier="pro">
          <div>
            <label className="text-sm font-medium">AI Analysis</label>
            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={(e) => setAiEnabled(e.target.checked)}
              className="border rounded px-2 py-1"
            />
          </div>
        </TierGate>

        <button
          onClick={refetch}
          className="px-4 py-2 bg-primary text-white rounded"
        >
          Refresh
        </button>
      </div>

      {/* Main Data - Signals */}
      <Card>
        <CardHeader>
          <CardTitle>Technical Signals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.signals.map((signal, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2 border rounded"
              >
                <div>
                  <p className="font-medium">{signal.signal}</p>
                  <p className="text-sm text-muted-foreground">{signal.desc}</p>
                </div>
                <div className="flex gap-2">
                  <Badge variant="outline">{signal.strength}</Badge>
                  {signal.ai_score && (
                    <Badge className="bg-purple-500">
                      AI: {signal.ai_score}%
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Indicators */}
      <Card>
        <CardHeader>
          <CardTitle>Key Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">RSI</p>
              <p className="text-2xl font-bold">{data.indicators.rsi.toFixed(1)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">MACD</p>
              <p className="text-2xl font-bold">{data.indicators.macd.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">ADX</p>
              <p className="text-2xl font-bold">{data.indicators.adx.toFixed(1)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Volume</p>
              <p className="text-2xl font-bold">
                {(data.indicators.volume / 1000000).toFixed(1)}M
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Signal Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Total Signals</p>
              <p className="text-2xl font-bold">{data.summary.total_signals}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Bullish</p>
              <p className="text-2xl font-bold text-green-600">
                {data.summary.bullish}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Bearish</p>
              <p className="text-2xl font-bold text-red-600">
                {data.summary.bearish}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Avg Score</p>
              <p className="text-2xl font-bold">{data.summary.avg_score.toFixed(0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Analysis */}
      {data.ai_analysis && (
        <AIInsightsPanel analysis={data.ai_analysis} tool="analyze_security" />
      )}

      {/* Tier Limit */}
      {data.tierLimit && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded text-sm">
          Daily limit: {data.tierLimit.daily} analyses remaining
        </div>
      )}
    </div>
  );
}

function SymbolSearchInput({ onAnalyze }: { onAnalyze: () => void }) {
  const [input, setInput] = useState('');
  return (
    <div className="flex gap-2">
      <input
        type="text"
        placeholder="Enter symbol (e.g., AAPL)"
        value={input}
        onChange={(e) => setInput(e.target.value.toUpperCase())}
        onKeyPress={(e) => e.key === 'Enter' && onAnalyze()}
        className="flex-1 border rounded px-3 py-2"
      />
      <button
        onClick={onAnalyze}
        className="px-4 py-2 bg-primary text-white rounded"
      >
        Analyze
      </button>
    </div>
  );
}
```

**2. API Route**

```typescript
// src/app/api/mcp/analyze/route.ts
import { NextResponse } from 'next/server';
import { getMCPClient } from '@/lib/mcp';
import { ensureUserInitialized } from '@/lib/auth/user-init';
import { checkUsageLimit, recordUsage } from '@/lib/auth/usage-limits';
import { TIER_LIMITS } from '@/lib/auth/tiers';

export async function POST(request: Request) {
  try {
    // 1. Auth
    const { userId, tier } = await ensureUserInitialized();

    // 2. Parse
    const { symbol, period = '1mo', use_ai } = await request.json();

    // 3. Validate
    if (!symbol) {
      return NextResponse.json(
        { error: 'Symbol is required' },
        { status: 400 }
      );
    }

    // 4. Check usage
    const canProceed = await checkUsageLimit(userId, 'analyze_security');
    if (!canProceed) {
      return NextResponse.json(
        { error: 'Daily analysis limit reached', tier_limit: true },
        { status: 429 }
      );
    }

    // 5. Validate tier
    const tierLimit = TIER_LIMITS[tier];
    const canUseAi = tierLimit.analyze_security.ai;

    // 6. Call MCP
    const mcp = getMCPClient();
    const result = await mcp.analyzeSecurity(
      symbol,
      period,
      use_ai && canUseAi  // Only use AI if tier allows and requested
    );

    // 7. Record usage
    await recordUsage(userId, 'analyze_security');

    // 8. Return
    return NextResponse.json({
      ...result,
      tierLimit: {
        daily: tierLimit.analyze_security.daily,
        ai: canUseAi,
      },
    });

  } catch (error) {
    console.error('[API /mcp/analyze] Error:', error);

    if (error.message.includes('MCP API error')) {
      return NextResponse.json(
        { error: 'Analysis service unavailable' },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to analyze symbol' },
      { status: 500 }
    );
  }
}
```

---

## Tool #2: compare_securities

### Purpose
Compare multiple stocks side-by-side across fundamental metrics, technical signals, and relative performance.

### Frontend Page
**Location**: `/src/app/(dashboard)/compare/page.tsx`

**URL**: `/compare`

### Implementation

**Component**

```typescript
// src/app/(dashboard)/compare/page.tsx
'use client';

import { useState } from 'react';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { ComparisonResult } from '@/lib/mcp/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const METRICS = ['signals', 'volatility', 'momentum', 'trend'];
const MAX_SYMBOLS = 5;

export default function ComparePage() {
  const [symbols, setSymbols] = useState<string[]>(['AAPL', 'MSFT']);
  const [metric, setMetric] = useState('signals');
  const [aiEnabled, setAiEnabled] = useState(false);

  const { data, loading, error } = useMCPQuery<ComparisonResult>({
    endpoint: '/api/mcp/compare',
    params: { symbols, metric, use_ai: aiEnabled },
    enabled: symbols.length > 0,
  });

  const addSymbol = (sym: string) => {
    if (symbols.length < MAX_SYMBOLS && !symbols.includes(sym)) {
      setSymbols([...symbols, sym]);
    }
  };

  const removeSymbol = (sym: string) => {
    setSymbols(symbols.filter((s) => s !== sym));
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Compare Securities</h1>

      {/* Controls */}
      <div className="space-y-4">
        <SymbolSelector
          symbols={symbols}
          onAdd={addSymbol}
          onRemove={removeSymbol}
          maxSymbols={MAX_SYMBOLS}
        />

        <div className="flex gap-4">
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="border rounded px-3 py-2"
          >
            {METRICS.map((m) => (
              <option key={m} value={m}>
                {m.charAt(0).toUpperCase() + m.slice(1)}
              </option>
            ))}
          </select>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={(e) => setAiEnabled(e.target.checked)}
            />
            AI Analysis
          </label>
        </div>
      </div>

      {loading && <div>Loading comparison...</div>}
      {error && <div className="text-red-600">Error: {error}</div>}

      {data && (
        <>
          {/* Comparison Table */}
          <Card>
            <CardHeader>
              <CardTitle>Comparison Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Metric</th>
                      {data.comparisons.map((comp) => (
                        <th key={comp.symbol} className="text-right p-2">
                          {comp.symbol}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.metrics.map((metricKey) => (
                      <tr key={metricKey} className="border-b">
                        <td className="p-2 font-medium">{metricKey}</td>
                        {data.comparisons.map((comp) => (
                          <td key={comp.symbol} className="text-right p-2">
                            {comp.metrics[metricKey]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Rankings */}
          <Card>
            <CardHeader>
              <CardTitle>Rankings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.comparisons.map((comp, idx) => (
                  <div key={comp.symbol} className="flex items-center gap-4">
                    <Badge className="bg-blue-500">{idx + 1}</Badge>
                    <div className="flex-1">
                      <p className="font-semibold">{comp.symbol}</p>
                      <p className="text-sm text-muted-foreground">
                        {comp.ranking_reason}
                      </p>
                    </div>
                    {comp.recommended && (
                      <Badge className="bg-green-500">Recommended</Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Analysis */}
          {data.ai_analysis && (
            <AIInsightsPanel
              analysis={data.ai_analysis}
              tool="compare_securities"
            />
          )}
        </>
      )}
    </div>
  );
}
```

**API Route**

```typescript
// src/app/api/mcp/compare/route.ts
import { NextResponse } from 'next/server';
import { getMCPClient } from '@/lib/mcp';
import { ensureUserInitialized } from '@/lib/auth/user-init';
import { TIER_LIMITS } from '@/lib/auth/tiers';

export async function POST(request: Request) {
  try {
    const { userId, tier } = await ensureUserInitialized();
    const { symbols, metric = 'signals', use_ai } = await request.json();

    if (!symbols || symbols.length === 0) {
      return NextResponse.json(
        { error: 'At least 2 symbols required' },
        { status: 400 }
      );
    }

    // Tier limit on number of symbols
    const tierLimit = TIER_LIMITS[tier];
    const maxSymbols = tierLimit.compare_securities.maxSymbols;
    const filteredSymbols = symbols.slice(0, maxSymbols);

    const mcp = getMCPClient();
    const result = await mcp.compareSecurity(
      filteredSymbols,
      metric,
      use_ai && tierLimit.compare_securities.ai
    );

    return NextResponse.json(result);
  } catch (error) {
    console.error('[API /mcp/compare] Error:', error);
    return NextResponse.json({ error: 'Failed to compare' }, { status: 500 });
  }
}
```

---

## Tool #3: screen_securities

### Purpose
Filter stocks against customizable technical and fundamental criteria to identify matching patterns.

### Frontend Page
**Location**: `/src/app/(dashboard)/scanner/page.tsx`

**URL**: `/scanner`

### Implementation (Shared with scan_trades)

```typescript
// src/app/(dashboard)/scanner/page.tsx
'use client';

import { useState } from 'react';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { ScreeningResult, ScanResult } from '@/lib/mcp/types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const UNIVERSES = ['sp500', 'nasdaq100', 'etf', 'crypto'];

export default function ScannerPage() {
  const [universe, setUniverse] = useState('sp500');
  const [activeTab, setActiveTab] = useState('scan');
  const [aiEnabled, setAiEnabled] = useState(false);

  // Screen Securities
  const screening = useMCPQuery<ScreeningResult>({
    endpoint: '/api/mcp/screen',
    params: { universe, use_ai: aiEnabled },
    enabled: activeTab === 'screen',
  });

  // Scan Trades
  const scanning = useMCPQuery<ScanResult>({
    endpoint: '/api/mcp/scan',
    params: { universe, use_ai: aiEnabled },
    enabled: activeTab === 'scan',
  });

  const data = activeTab === 'scan' ? scanning.data : screening.data;
  const loading = activeTab === 'scan' ? scanning.loading : screening.loading;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Trade Scanner</h1>

      {/* Controls */}
      <div className="flex gap-4">
        <select
          value={universe}
          onChange={(e) => setUniverse(e.target.value)}
          className="border rounded px-3 py-2"
        >
          {UNIVERSES.map((u) => (
            <option key={u} value={u}>
              {u.toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="scan">Scan Trades</TabsTrigger>
          <TabsTrigger value="screen">Screen Securities</TabsTrigger>
        </TabsList>

        <TabsContent value="scan">
          <ScanTradesContent data={scanning.data} loading={scanning.loading} />
        </TabsContent>

        <TabsContent value="screen">
          <ScreenSecuritiesContent
            data={screening.data}
            loading={screening.loading}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function ScanTradesContent({ data, loading }) {
  if (loading) return <div>Scanning...</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Scanned {data.total_scanned} securities, found {data.qualified_trades.length} trades
      </p>
      {data.qualified_trades.map((trade, idx) => (
        <TradeCard key={idx} trade={trade} />
      ))}
    </div>
  );
}

function ScreenSecuritiesContent({ data, loading }) {
  if (loading) return <div>Screening...</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="space-y-4">
      {data.matches.map((security, idx) => (
        <SecurityCard key={idx} security={security} />
      ))}
    </div>
  );
}
```

---

## Tool #4: get_trade_plan

### Purpose
Develop entry-to-exit strategy with risk levels, position sizing, and price targets.

### Implementation (Integrated in analyze page)

```typescript
// In the analyze page, after displaying analysis:

{data.trade_plans && data.trade_plans.length > 0 && (
  <Card>
    <CardHeader>
      <CardTitle>Trade Plans</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      {data.trade_plans.map((plan, idx) => (
        <div key={idx} className="border rounded p-4 space-y-3">
          {/* Timeframe & Bias */}
          <div className="flex items-center justify-between">
            <Badge>{plan.timeframe.toUpperCase()}</Badge>
            <Badge
              className={
                plan.bias === 'bullish'
                  ? 'bg-green-500'
                  : plan.bias === 'bearish'
                  ? 'bg-red-500'
                  : 'bg-gray-500'
              }
            >
              {plan.bias.toUpperCase()}
            </Badge>
          </div>

          {/* Trade Details */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Entry</p>
              <p className="font-semibold">${plan.entry_price.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Stop</p>
              <p className="font-semibold text-red-600">
                ${plan.stop_price.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Target</p>
              <p className="font-semibold text-green-600">
                ${plan.target_price.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">R:R</p>
              <p className="font-semibold">
                1:{plan.risk_reward_ratio.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Max Loss</p>
              <p className="font-semibold">
                {plan.max_loss_percent.toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Primary Signal */}
          <div>
            <p className="text-sm font-medium">Primary Signal</p>
            <p className="text-sm text-muted-foreground">
              {plan.primary_signal}
            </p>
          </div>

          {/* Supporting Signals */}
          {plan.supporting_signals.length > 0 && (
            <div>
              <p className="text-sm font-medium">Supporting Signals</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {plan.supporting_signals.map((sig, idx) => (
                  <Badge key={idx} variant="outline">
                    {sig}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Risk Quality */}
          <div className="flex items-center justify-between">
            <span className="text-sm">Risk Quality</span>
            <Badge
              className={
                plan.risk_quality === 'high'
                  ? 'bg-green-500'
                  : plan.risk_quality === 'medium'
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }
            >
              {plan.risk_quality.toUpperCase()}
            </Badge>
          </div>

          {/* Suppression */}
          {plan.is_suppressed && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
              <p className="font-medium text-yellow-900">Trade Suppressed</p>
              {plan.suppression_reasons.map((reason, idx) => (
                <p key={idx} className="text-yellow-800 text-xs">
                  • {reason.message}
                </p>
              ))}
            </div>
          )}
        </div>
      ))}
    </CardContent>
  </Card>
)}
```

---

## Tool #5: scan_trades

### Purpose
Identify emerging trading opportunities across watchlist by detecting high-probability setups.

### Implementation (Shared in scanner page, see above)

---

## Tool #6: portfolio_risk

### Purpose
Quantify total portfolio risk exposure and analyze concentration.

### Frontend Page
**Location**: `/src/app/(dashboard)/portfolio/page.tsx`

**URL**: `/portfolio`

### Implementation

```typescript
// src/app/(dashboard)/portfolio/page.tsx
'use client';

import { useState } from 'react';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { PortfolioRiskResult } from '@/lib/mcp/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function PortfolioPage() {
  const [positions, setPositions] = useState([
    { symbol: 'AAPL', shares: 100, entry_price: 150 },
    { symbol: 'MSFT', shares: 50, entry_price: 300 },
  ]);
  const [aiEnabled, setAiEnabled] = useState(false);

  const { data, loading, error } = useMCPQuery<PortfolioRiskResult>({
    endpoint: '/api/mcp/portfolio-risk',
    params: { positions, use_ai: aiEnabled },
    enabled: positions.length > 0,
  });

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW':
        return 'text-green-600';
      case 'MEDIUM':
        return 'text-yellow-600';
      case 'HIGH':
        return 'text-orange-600';
      case 'CRITICAL':
        return 'text-red-600';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Portfolio Risk</h1>

      {loading && <div>Calculating risk metrics...</div>}
      {error && <div className="text-red-600">Error: {error}</div>}

      {data && (
        <>
          {/* Risk Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="text-xs text-muted-foreground">Total Value</p>
                <p className="text-2xl font-bold">
                  ${data.total_value.toLocaleString('en-US', { maximumFractionDigits: 2 })}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Max Loss ($)</p>
                <p className="text-2xl font-bold text-red-600">
                  -${data.total_max_loss.toLocaleString('en-US', { maximumFractionDigits: 2 })}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Max Loss (%)</p>
                <p className="text-2xl font-bold text-red-600">
                  -{data.risk_percent_of_portfolio.toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Risk Level</p>
                <p className={`text-2xl font-bold ${getRiskColor(data.overall_risk_level)}`}>
                  {data.overall_risk_level}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Positions */}
          <Card>
            <CardHeader>
              <CardTitle>Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.positions.map((pos, idx) => (
                  <div key={idx} className="border rounded p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{pos.symbol}</h3>
                      <Badge
                        className={
                          pos.risk_quality === 'high'
                            ? 'bg-green-500'
                            : pos.risk_quality === 'medium'
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }
                      >
                        {pos.risk_quality.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-xs text-muted-foreground">Shares</p>
                        <p className="font-medium">{pos.shares}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Current</p>
                        <p className="font-medium">
                          ${pos.current_price.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Stop Level</p>
                        <p className="font-medium">
                          ${pos.stop_level.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Max Loss</p>
                        <p className="font-medium text-red-600">
                          -${Math.abs(pos.max_loss_dollar).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Sector Concentration */}
          <Card>
            <CardHeader>
              <CardTitle>Sector Concentration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(data.sector_concentration).map(([sector, pct]) => (
                  <div key={sector} className="flex items-center justify-between">
                    <span className="text-sm">{sector}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500"
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-10 text-right">
                        {pct.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Hedge Suggestions */}
          {data.hedge_suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Hedge Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {data.hedge_suggestions.map((suggestion, idx) => (
                    <li key={idx} className="text-sm flex gap-2">
                      <span>•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* AI Analysis */}
          {data.ai_analysis && (
            <AIInsightsPanel analysis={data.ai_analysis} tool="portfolio_risk" />
          )}
        </>
      )}
    </div>
  );
}
```

---

## Tool #7: morning_brief

### Purpose
Daily market briefing combining overnight trends, key levels, and sector rotation clues.

### Frontend Page
**Location**: `/src/app/(dashboard)/page.tsx` (Dashboard Home)

**URL**: `/` (When authenticated)

### Implementation (Dashboard integration)

```typescript
// In src/app/(dashboard)/page.tsx
// Fetch morning brief as part of dashboard

const { data: briefData } = useMCPQuery<MorningBriefResult>({
  endpoint: '/api/dashboard/morning-brief',
  params: { use_ai: true },
  enabled: true,
});

// Display in dashboard:

{briefData && (
  <Card>
    <CardHeader>
      <CardTitle>Market Brief</CardTitle>
    </CardHeader>
    <CardContent className="space-y-6">
      {/* Market Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <p className="text-xs text-muted-foreground">Status</p>
          <p className="font-semibold capitalize">
            {briefData.market_status.market_status}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">ES Futures</p>
          <p className={`font-semibold ${briefData.market_status.futures_es.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {briefData.market_status.futures_es.change_percent >= 0 ? '+' : ''}
            {briefData.market_status.futures_es.change_percent.toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">NQ Futures</p>
          <p className={`font-semibold ${briefData.market_status.futures_nq.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {briefData.market_status.futures_nq.change_percent >= 0 ? '+' : ''}
            {briefData.market_status.futures_nq.change_percent.toFixed(2)}%
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">VIX</p>
          <p className="font-semibold">{briefData.market_status.vix.toFixed(2)}</p>
        </div>
      </div>

      {/* Sector Leaders */}
      <div>
        <h3 className="font-semibold mb-3">Sector Leaders</h3>
        <div className="space-y-2">
          {briefData.sector_leaders.map((sector, idx) => (
            <div key={idx} className="flex items-center justify-between text-sm">
              <span>{sector.sector}</span>
              <Badge className="bg-green-500">
                +{sector.change_percent.toFixed(2)}%
              </Badge>
            </div>
          ))}
        </div>
      </div>

      {/* Key Themes */}
      {briefData.key_themes.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Key Themes</h3>
          <div className="flex flex-wrap gap-2">
            {briefData.key_themes.map((theme, idx) => (
              <Badge key={idx} variant="outline">
                {theme}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Economic Events */}
      {briefData.economic_events.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Economic Events</h3>
          <div className="space-y-2 text-sm">
            {briefData.economic_events.slice(0, 5).map((event, idx) => (
              <div key={idx} className="flex items-start justify-between">
                <div>
                  <p className="font-medium">{event.event_name}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                <Badge
                  className={
                    event.importance === 'HIGH'
                      ? 'bg-red-500'
                      : event.importance === 'MEDIUM'
                      ? 'bg-yellow-500'
                      : 'bg-gray-500'
                  }
                >
                  {event.importance}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </CardContent>
  </Card>
)}
```

---

## Tool #8: analyze_fibonacci

### Purpose
Identify Fibonacci retracement/extension levels and confluence zones.

### Frontend Page
**Location**: `/src/app/(dashboard)/fibonacci/page.tsx`

**URL**: `/fibonacci`

### Implementation

```typescript
// src/app/(dashboard)/fibonacci/page.tsx
'use client';

import { useState } from 'react';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { FibonacciAnalysisResult } from '@/lib/mcp/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const PERIODS = ['1h', '4h', '1d', '1w'];
const WINDOWS = [14, 20, 50, 100, 200];

export default function FibonacciPage() {
  const [symbol, setSymbol] = useState('AAPL');
  const [period, setPeriod] = useState('1d');
  const [window, setWindow] = useState(50);
  const [aiEnabled, setAiEnabled] = useState(false);

  const { data, loading, error } = useMCPQuery<FibonacciAnalysisResult>({
    endpoint: '/api/mcp/fibonacci',
    params: { symbol, period, window, use_ai: aiEnabled },
    enabled: !!symbol,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Fibonacci Analysis</h1>

      {/* Controls */}
      <div className="flex gap-4 flex-wrap">
        <input
          type="text"
          placeholder="Symbol"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          className="border rounded px-3 py-2"
        />
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="border rounded px-3 py-2"
        >
          {PERIODS.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select
          value={window}
          onChange={(e) => setWindow(Number(e.target.value))}
          className="border rounded px-3 py-2"
        >
          {WINDOWS.map((w) => (
            <option key={w} value={w}>
              {w} bar window
            </option>
          ))}
        </select>
      </div>

      {loading && <div>Calculating Fibonacci levels...</div>}
      {error && <div className="text-red-600">Error: {error}</div>}

      {data && (
        <>
          {/* Price Info */}
          <Card>
            <CardHeader>
              <CardTitle>{data.symbol} Fibonacci Setup</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Current Price</p>
                <p className="text-2xl font-bold">${data.price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Swing High</p>
                <p className="text-2xl font-bold">${data.swingHigh.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Swing Low</p>
                <p className="text-2xl font-bold">${data.swingLow.toFixed(2)}</p>
              </div>
            </CardContent>
          </Card>

          {/* Fibonacci Levels */}
          <Card>
            <CardHeader>
              <CardTitle>Key Levels</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.levels.map((level, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 border rounded"
                  >
                    <div>
                      <p className="font-medium">{level.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {level.ratio.toFixed(3)} ratio
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">${level.price.toFixed(2)}</p>
                      <Badge
                        variant={
                          level.strength === 'STRONG'
                            ? 'default'
                            : 'outline'
                        }
                      >
                        {level.strength}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Confluence Zones */}
          {data.confluenceZones.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Confluence Zones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.confluenceZones.map((zone, idx) => (
                    <div key={idx} className="border rounded p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <p className="font-semibold">${zone.price.toFixed(2)}</p>
                        <Badge
                          className={
                            zone.strength === 'VERY_STRONG'
                              ? 'bg-green-500'
                              : zone.strength === 'STRONG'
                              ? 'bg-blue-500'
                              : zone.strength === 'SIGNIFICANT'
                              ? 'bg-yellow-500'
                              : 'bg-gray-500'
                          }
                        >
                          {zone.strength}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {zone.levelName}
                      </p>
                      <p className="text-xs">
                        {zone.signalCount} signals | Confluence: {zone.confluenceScore.toFixed(1)}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* AI Analysis */}
          {data.ai_analysis && (
            <AIInsightsPanel analysis={data.ai_analysis} tool="analyze_fibonacci" />
          )}
        </>
      )}
    </div>
  );
}
```

---

## Tool #9: options_risk_analysis

### Purpose
Decode market sentiment from options flow and provide strategy recommendations.

### Frontend Page
**Location**: `/src/app/(dashboard)/options/page.tsx` (NEW)

**URL**: `/options`

### Implementation

```typescript
// src/app/(dashboard)/options/page.tsx
'use client';

import { useState } from 'react';
import { useMCPQuery } from '@/hooks/useMCPQuery';
import { OptionsRiskResult } from '@/lib/mcp/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TierGate } from '@/components/gating/TierGate';

const POSITION_TYPES = ['call', 'put', 'spread'];

export default function OptionsPage() {
  const [symbol, setSymbol] = useState('SPY');
  const [positionType, setPositionType] = useState<'call' | 'put' | 'spread'>('call');
  const [aiEnabled, setAiEnabled] = useState(false);

  const { data, loading, error } = useMCPQuery<OptionsRiskResult>({
    endpoint: '/api/mcp/options-risk',
    params: { symbol, position_type: positionType, use_ai: aiEnabled },
    enabled: !!symbol,
  });

  return (
    <TierGate feature="options_risk_analysis" requiredTier="pro">
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Options Risk Analysis</h1>

        {/* Controls */}
        <div className="flex gap-4 flex-wrap">
          <input
            type="text"
            placeholder="Symbol"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="border rounded px-3 py-2"
          />
          <select
            value={positionType}
            onChange={(e) => setPositionType(e.target.value as any)}
            className="border rounded px-3 py-2"
          >
            {POSITION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </select>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={(e) => setAiEnabled(e.target.checked)}
            />
            AI Analysis
          </label>
        </div>

        {loading && <div>Analyzing options...</div>}
        {error && <div className="text-red-600">Error: {error}</div>}

        {data && (
          <>
            {/* Position Overview */}
            <Card>
              <CardHeader>
                <CardTitle>{data.symbol} Options</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground">Underlying</p>
                    <p className="text-2xl font-bold">
                      ${data.underlying_price.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Strike</p>
                    <p className="text-2xl font-bold">
                      ${data.position.strike.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Premium</p>
                    <p className="text-2xl font-bold">
                      ${data.position.premium.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">IV</p>
                    <p className="text-2xl font-bold">
                      {data.position.implied_volatility.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Type</p>
                    <p className="text-lg font-bold capitalize">
                      {data.position.type}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Greeks */}
            <Card>
              <CardHeader>
                <CardTitle>Greeks</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-5 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Delta</p>
                  <p className="text-lg font-bold">{data.greeks.delta.toFixed(3)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Gamma</p>
                  <p className="text-lg font-bold">{data.greeks.gamma.toFixed(4)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Theta</p>
                  <p className="text-lg font-bold">{data.greeks.theta.toFixed(3)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Vega</p>
                  <p className="text-lg font-bold">{data.greeks.vega.toFixed(3)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Rho</p>
                  <p className="text-lg font-bold">{data.greeks.rho.toFixed(3)}</p>
                </div>
              </CardContent>
            </Card>

            {/* Risk Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Risk Metrics</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Max Profit</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${data.risk_metrics.max_profit.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Max Loss</p>
                  <p className="text-2xl font-bold text-red-600">
                    -${Math.abs(data.risk_metrics.max_loss).toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Break Even</p>
                  <p className="text-2xl font-bold">
                    ${data.risk_metrics.breakeven.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">POP</p>
                  <p className="text-2xl font-bold">
                    {(data.risk_metrics.probability_of_profit * 100).toFixed(0)}%
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Price Scenarios */}
            <Card>
              <CardHeader>
                <CardTitle>Price Scenarios</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.scenarios.map((scenario, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 border rounded"
                    >
                      <div>
                        <p className="font-medium">{scenario.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {scenario.price_change_percent >= 0 ? '+' : ''}
                          {scenario.price_change_percent.toFixed(2)}%
                        </p>
                      </div>
                      <div className="text-right">
                        <p
                          className={`font-bold ${
                            scenario.pnl >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {scenario.pnl >= 0 ? '+' : ''}${scenario.pnl.toFixed(2)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Delta: {scenario.new_delta.toFixed(3)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Analysis */}
            {data.ai_analysis && (
              <AIInsightsPanel
                analysis={data.ai_analysis}
                tool="options_risk_analysis"
              />
            )}
          </>
        )}
      </div>
    </TierGate>
  );
}
```

**API Route**

```typescript
// src/app/api/mcp/options-risk/route.ts
import { NextResponse } from 'next/server';
import { getMCPClient } from '@/lib/mcp';
import { ensureUserInitialized } from '@/lib/auth/user-init';
import { TIER_LIMITS } from '@/lib/auth/tiers';

export async function POST(request: Request) {
  try {
    const { userId, tier } = await ensureUserInitialized();
    const { symbol, position_type, use_ai } = await request.json();

    if (!symbol || !position_type) {
      return NextResponse.json(
        { error: 'Symbol and position_type required' },
        { status: 400 }
      );
    }

    const tierLimit = TIER_LIMITS[tier];
    if (!tierLimit.options_risk_analysis) {
      return NextResponse.json(
        { error: 'Upgrade required for options analysis' },
        { status: 403 }
      );
    }

    const mcp = getMCPClient();
    const result = await mcp.optionsRiskAnalysis(
      symbol,
      position_type,
      {},
      use_ai && tierLimit.options_risk_analysis.ai
    );

    return NextResponse.json(result);
  } catch (error) {
    console.error('[API /mcp/options-risk] Error:', error);
    return NextResponse.json({ error: 'Failed to analyze' }, { status: 500 });
  }
}
```

---

## Summary Table

| Tool | Page | Route | Client Method | Status |
|------|------|-------|---------------|--------|
| #1 analyze_security | `/analyze/[symbol]` | `/api/mcp/analyze` | `analyzeSecurity()` | ✅ Implemented |
| #2 compare_securities | `/compare` | `/api/mcp/compare` | `compareSecurity()` | ⏳ New |
| #3 screen_securities | `/scanner` | `/api/mcp/screen` | `screenSecurities()` | ⏳ Update |
| #4 get_trade_plan | `/analyze/[symbol]` | `/api/mcp/trade-plan` | `getTradePlan()` | ✅ Integrated |
| #5 scan_trades | `/scanner` | `/api/mcp/scan` | `scanTrades()` | ✅ Implemented |
| #6 portfolio_risk | `/portfolio` | `/api/mcp/portfolio-risk` | `portfolioRisk()` | ⏳ New UI |
| #7 morning_brief | `/` (dashboard) | `/api/dashboard/morning-brief` | `morningBrief()` | ✅ Implemented |
| #8 analyze_fibonacci | `/fibonacci` | `/api/mcp/fibonacci` | `analyzeFibonacci()` | ✅ Implemented |
| #9 options_risk_analysis | `/options` | `/api/mcp/options-risk` | `optionsRiskAnalysis()` | ⏳ New |

---

**Document Version**: 1.0
**Last Updated**: February 2, 2026
**Related**: [MCP-UI Integration Guide](mcp-frontend-integration-guide.md) | [Refactor Plan](mcp-ui-refactor-plan.md)
