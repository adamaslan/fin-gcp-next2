# Options Spread Support Implementation Plan

**Date:** February 7, 2026
**Status:** Ready for Implementation
**Estimated Time:** 10-12 hours

---

## Executive Summary

Expand the existing `options_risk_analysis` MCP tool to support comprehensive spread analysis for any stock or ETF. This enables users to analyze complex options strategies like credit spreads, debit spreads, iron condors, and iron butterflies with real market data and AI-powered insights.

---

## Supported Spread Types

| Spread Type | Strategy | Direction | Risk Profile |
|-------------|----------|-----------|--------------|
| `call_credit` | Bear Call Spread | Bearish | Defined risk, credit received |
| `put_credit` | Bull Put Spread | Bullish | Defined risk, credit received |
| `call_debit` | Bull Call Spread | Bullish | Defined risk, debit paid |
| `put_debit` | Bear Put Spread | Bearish | Defined risk, debit paid |
| `iron_condor` | Neutral Spread | Neutral | Profit from low volatility |
| `iron_butterfly` | ATM Neutral | Neutral | Max profit at center strike |

---

## Architecture Decision

**Extend existing endpoint** rather than create a new one:

```
┌─────────────────────────────────────────────────────────────────┐
│  User Request: Analyze MU 90-94 Call Credit Spread              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  POST /api/mcp/options-risk                                     │
│  {                                                              │
│    "symbol": "MU",                                              │
│    "position_type": "spread",                                   │
│    "spread_type": "call_credit",    ← NEW PARAMETER             │
│    "short_strike": 90,              ← NEW PARAMETER             │
│    "long_strike": 94,               ← NEW PARAMETER             │
│    "expiration": "2026-03-21",                                  │
│    "contracts": 1,                                              │
│    "use_ai": true                                               │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Cloud Run MCP Server                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  if spread_type provided:                                │   │
│  │      → SpreadAnalyzer.analyze_call_credit_spread()       │   │
│  │  else:                                                   │   │
│  │      → existing chain analysis (backward compatible)     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Response: SpreadAnalysisResult                                 │
│  {                                                              │
│    "symbol": "MU",                                              │
│    "current_price": 87.50,                                      │
│    "spread_type": "call_credit",                                │
│    "max_profit": 125.00,                                        │
│    "max_loss": 275.00,                                          │
│    "breakeven": 91.25,                                          │
│    "probability_of_profit": 0.72,                               │
│    "net_theta": 3.45,                                           │
│    "ai_analysis": { ... }                                       │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Maintains backward compatibility with single-leg chain analysis
- Reuses existing authentication, tier-checking, and AI integration
- Consistent API design pattern

---

## Implementation Phases

### Phase 1: Backend Core (Python) — 3-4 hours

#### Create: `/mcp-finance1/src/technical_analysis_mcp/spreads.py`

Port and adapt from existing prototype `/nu-logs/options_risk_example.py`:

```python
from dataclasses import dataclass
from typing import Literal, Optional, List
import yfinance as yf
from scipy.stats import norm

SpreadType = Literal[
    "call_credit", "put_credit",
    "call_debit", "put_debit",
    "iron_condor", "iron_butterfly"
]

@dataclass
class SpreadLeg:
    type: Literal["long_call", "short_call", "long_put", "short_put"]
    strike: float
    premium: float
    contracts: int
    delta: float
    gamma: float
    theta: float
    vega: float

@dataclass
class SpreadAnalysisResult:
    symbol: str
    current_price: float
    spread_type: SpreadType
    expiration: str
    days_to_expiration: int
    legs: List[SpreadLeg]
    max_profit: float
    max_loss: float
    breakeven: Optional[float]
    breakeven_lower: Optional[float]
    breakeven_upper: Optional[float]
    probability_of_profit: float
    risk_reward_ratio: float
    net_credit_or_debit: float
    net_delta: float
    net_gamma: float
    net_theta: float
    net_vega: float
    current_status: str
    warnings: List[str]
    ai_analysis: Optional[dict] = None


class SpreadAnalyzer:
    """Analyze options spreads with real market data."""

    def analyze_call_credit_spread(
        self,
        symbol: str,
        short_strike: float,
        long_strike: float,
        expiration: str,
        contracts: int = 1
    ) -> SpreadAnalysisResult:
        """
        Analyze a call credit spread (bear call spread).

        SELL short_strike call (lower) - collect premium
        BUY long_strike call (higher) - pay premium for protection

        Max Profit = Net Credit Received
        Max Loss = Spread Width - Net Credit
        Breakeven = Short Strike + Net Credit
        """
        # Fetch real options data
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get("currentPrice")
        chain = ticker.option_chain(expiration)
        calls = chain.calls

        # Get option premiums
        short_call = calls[calls["strike"] == short_strike].iloc[0]
        long_call = calls[calls["strike"] == long_strike].iloc[0]

        short_premium = float(short_call["lastPrice"])
        long_premium = float(long_call["lastPrice"])
        net_credit = short_premium - long_premium

        # Calculate risk metrics
        spread_width = long_strike - short_strike
        max_profit = net_credit * 100 * contracts
        max_loss = (spread_width - net_credit) * 100 * contracts
        breakeven = short_strike + net_credit

        # Calculate probability of profit using IV
        iv = float(short_call["impliedVolatility"])
        dte = self._calculate_dte(expiration)
        pop = self._calculate_pop(current_price, breakeven, dte, iv)

        # Build legs
        legs = [
            SpreadLeg(
                type="short_call",
                strike=short_strike,
                premium=short_premium,
                contracts=contracts,
                delta=-float(short_call.get("delta", 0.5)),
                gamma=-float(short_call.get("gamma", 0.02)),
                theta=float(short_call.get("theta", 0) or 0),
                vega=-float(short_call.get("vega", 0) or 0),
            ),
            SpreadLeg(
                type="long_call",
                strike=long_strike,
                premium=long_premium,
                contracts=contracts,
                delta=float(long_call.get("delta", 0.3)),
                gamma=float(long_call.get("gamma", 0.02)),
                theta=-float(long_call.get("theta", 0) or 0),
                vega=float(long_call.get("vega", 0) or 0),
            ),
        ]

        return SpreadAnalysisResult(
            symbol=symbol,
            current_price=current_price,
            spread_type="call_credit",
            expiration=expiration,
            days_to_expiration=dte,
            legs=legs,
            max_profit=max_profit,
            max_loss=max_loss,
            breakeven=breakeven,
            breakeven_lower=None,
            breakeven_upper=None,
            probability_of_profit=pop,
            risk_reward_ratio=max_loss / max_profit if max_profit > 0 else 0,
            net_credit_or_debit=net_credit,
            net_delta=sum(leg.delta for leg in legs),
            net_gamma=sum(leg.gamma for leg in legs),
            net_theta=sum(leg.theta for leg in legs),
            net_vega=sum(leg.vega for leg in legs),
            current_status=self._get_status(current_price, short_strike, breakeven),
            warnings=self._generate_warnings(current_price, short_strike, dte, iv),
        )

    def _calculate_pop(
        self,
        current_price: float,
        breakeven: float,
        dte: int,
        iv: float
    ) -> float:
        """Calculate probability of profit using Black-Scholes."""
        if dte <= 0 or iv <= 0:
            return 0.5

        # Standard deviation of price movement
        time_years = dte / 365
        std_dev = iv * current_price * (time_years ** 0.5)

        # For credit spread: profit if price stays below breakeven
        z_score = (breakeven - current_price) / std_dev
        return float(norm.cdf(z_score))

    # Similar methods for:
    # - analyze_put_credit_spread()
    # - analyze_call_debit_spread()
    # - analyze_put_debit_spread()
    # - analyze_iron_condor()
    # - analyze_iron_butterfly()
```

#### Modify: `/mcp-finance1/src/technical_analysis_mcp/server.py`

Update `options_risk_analysis()` function (lines 1263-1449):

```python
async def options_risk_analysis(
    symbol: str,
    expiration_date: str | None = None,
    option_type: str = "both",
    min_volume: int = 75,
    # NEW spread parameters
    spread_type: str | None = None,
    short_strike: float | None = None,
    long_strike: float | None = None,
    contracts: int = 1,
    # Iron condor/butterfly
    short_put_strike: float | None = None,
    long_put_strike: float | None = None,
    short_call_strike: float | None = None,
    long_call_strike: float | None = None,
    use_ai: bool = False,
) -> dict[str, Any]:
    """Analyze options risk - supports both chain analysis and spread strategies."""

    # Route to spread analysis if spread_type provided
    if spread_type:
        from .spreads import SpreadAnalyzer
        analyzer = SpreadAnalyzer()

        if spread_type == "call_credit":
            result = analyzer.analyze_call_credit_spread(
                symbol, short_strike, long_strike, expiration_date, contracts
            )
        elif spread_type == "put_credit":
            result = analyzer.analyze_put_credit_spread(
                symbol, short_strike, long_strike, expiration_date, contracts
            )
        # ... other spread types

        # Add AI analysis if requested
        if use_ai:
            from .options_ai_analyzer import OptionsAIAnalyzer
            ai = OptionsAIAnalyzer()
            result.ai_analysis = ai.analyze_spread(result)

        return asdict(result)

    # Existing chain analysis code continues here...
```

Update tool schema in `list_tools()`:

```python
{
    "name": "options_risk_analysis",
    "description": "Analyze options risk - chain analysis or spread strategies",
    "inputSchema": {
        "type": "object",
        "properties": {
            "symbol": {"type": "string", "description": "Stock/ETF ticker"},
            # Existing params...

            # NEW spread params
            "spread_type": {
                "type": "string",
                "enum": ["call_credit", "put_credit", "call_debit",
                         "put_debit", "iron_condor", "iron_butterfly"],
                "description": "Type of spread strategy to analyze"
            },
            "short_strike": {
                "type": "number",
                "description": "Strike price for short leg(s)"
            },
            "long_strike": {
                "type": "number",
                "description": "Strike price for long leg(s)"
            },
            "contracts": {
                "type": "integer",
                "default": 1,
                "description": "Number of spread contracts"
            },
            # Iron condor/butterfly strikes
            "short_put_strike": {"type": "number"},
            "long_put_strike": {"type": "number"},
            "short_call_strike": {"type": "number"},
            "long_call_strike": {"type": "number"},
        },
        "required": ["symbol"]
    }
}
```

---

### Phase 2: TypeScript Types — 30 minutes

#### Modify: `/nextjs-mcp-finance/src/lib/mcp/types.ts`

Add after line 312:

```typescript
// ============================================
// Spread Analysis Types
// ============================================

export type SpreadType =
  | "call_credit"
  | "put_credit"
  | "call_debit"
  | "put_debit"
  | "iron_condor"
  | "iron_butterfly";

export interface SpreadLeg {
  type: "long_call" | "short_call" | "long_put" | "short_put";
  strike: number;
  premium: number;
  contracts: number;
  greeks: {
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
  };
}

export interface SpreadAnalysisResult {
  symbol: string;
  current_price: number;
  spread_type: SpreadType;
  expiration: string;
  days_to_expiration: number;
  legs: SpreadLeg[];

  // Risk Metrics
  max_profit: number;
  max_loss: number;
  breakeven?: number;
  breakeven_lower?: number;  // For iron condor/butterfly
  breakeven_upper?: number;  // For iron condor/butterfly
  probability_of_profit: number;
  risk_reward_ratio: number;
  net_credit_or_debit: number;

  // Aggregate Greeks
  net_delta: number;
  net_gamma: number;
  net_theta: number;
  net_vega: number;

  // Status
  current_status: "MAX_PROFIT" | "PROFITABLE" | "BREAKEVEN" | "AT_RISK" | "MAX_LOSS";
  warnings: string[];

  // Optional AI & tier info
  ai_analysis?: AIAnalysis;
  tierLimit?: {
    spreadsAvailable: SpreadType[];
    ai: boolean;
  };
}
```

---

### Phase 3: API Layer — 1 hour

#### Modify: `/nextjs-mcp-finance/src/lib/mcp/client.ts`

Update `optionsRiskAnalysis()` method:

```typescript
async optionsRiskAnalysis(
  symbol: string,
  positionType: "call" | "put" | "spread",
  options: {
    strike?: number;
    expiry?: string;
    contracts?: number;
    premium?: number;
    // NEW spread params
    spread_type?: SpreadType;
    short_strike?: number;
    long_strike?: number;
    short_put_strike?: number;
    long_put_strike?: number;
    short_call_strike?: number;
    long_call_strike?: number;
  } = {},
  useAi = false,
): Promise<OptionsRiskResult | SpreadAnalysisResult> {
  const response = await fetch(`${this.baseUrl}/api/options-risk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      symbol,
      position_type: positionType,
      ...options,
      use_ai: useAi,
    }),
  });

  return this.handleResponse(response, `/api/options-risk (symbol=${symbol})`);
}
```

#### Modify: `/nextjs-mcp-finance/src/app/api/mcp/options-risk/route.ts`

Add spread parameter handling:

```typescript
export async function POST(request: Request) {
  // ... existing tier checks ...

  const {
    symbol,
    position_type,
    // Existing params
    strike,
    expiry,
    contracts = 1,
    premium,
    // NEW spread params
    spread_type,
    short_strike,
    long_strike,
    short_put_strike,
    long_put_strike,
    short_call_strike,
    long_call_strike,
    use_ai = false,
  } = await request.json();

  // Validate spread parameters
  if (spread_type) {
    const validSpreadTypes = [
      "call_credit", "put_credit", "call_debit",
      "put_debit", "iron_condor", "iron_butterfly"
    ];

    if (!validSpreadTypes.includes(spread_type)) {
      return NextResponse.json(
        { error: "Invalid spread_type" },
        { status: 400 }
      );
    }

    // Validate required strikes for vertical spreads
    if (["call_credit", "put_credit", "call_debit", "put_debit"].includes(spread_type)) {
      if (!short_strike || !long_strike) {
        return NextResponse.json(
          { error: "short_strike and long_strike required for vertical spreads" },
          { status: 400 }
        );
      }
    }

    // Check tier access for spread types
    const tierSpreads = TIER_LIMITS[tier].tools.options_risk_analysis?.spreads || [];
    if (!tierSpreads.includes(spread_type) && !tierSpreads.includes("all")) {
      return NextResponse.json(
        {
          error: `${spread_type} requires Pro tier`,
          upgrade_required: true
        },
        { status: 403 }
      );
    }
  }

  // ... rest of implementation ...
}
```

---

### Phase 4: Frontend Components — 2-3 hours

#### Modify: `/nextjs-mcp-finance/src/components/mcp-control/ParameterForm.tsx`

Add spread parameters to `TOOL_PARAMETERS`:

```typescript
options_risk_analysis: [
  {
    name: "symbol",
    type: "text",
    required: true,
    label: "Stock Symbol",
    placeholder: "AAPL, SPY, MU...",
  },
  {
    name: "spread_type",
    type: "select",
    required: false,
    label: "Spread Type",
    options: [
      { value: "", label: "-- Chain Analysis (No Spread) --" },
      { value: "call_credit", label: "Call Credit Spread (Bearish)" },
      { value: "put_credit", label: "Put Credit Spread (Bullish)" },
      { value: "call_debit", label: "Call Debit Spread (Bullish)" },
      { value: "put_debit", label: "Put Debit Spread (Bearish)" },
      { value: "iron_condor", label: "Iron Condor (Neutral)" },
      { value: "iron_butterfly", label: "Iron Butterfly (Neutral)" },
    ],
    help: "Select a spread strategy or leave blank for chain analysis",
  },
  {
    name: "short_strike",
    type: "number",
    required: false,
    label: "Short Strike",
    placeholder: "90",
    help: "Strike price for the option you're selling",
    visibleWhen: { spread_type: ["call_credit", "put_credit", "call_debit", "put_debit"] },
  },
  {
    name: "long_strike",
    type: "number",
    required: false,
    label: "Long Strike",
    placeholder: "94",
    help: "Strike price for the option you're buying",
    visibleWhen: { spread_type: ["call_credit", "put_credit", "call_debit", "put_debit"] },
  },
  {
    name: "expiration",
    type: "text",
    required: false,
    label: "Expiration Date",
    placeholder: "2026-03-21",
    help: "Options expiration in YYYY-MM-DD format",
    visibleWhen: { spread_type: ["call_credit", "put_credit", "call_debit", "put_debit", "iron_condor", "iron_butterfly"] },
  },
  {
    name: "contracts",
    type: "number",
    required: false,
    label: "Contracts",
    default: 1,
    min: 1,
    max: 100,
    help: "Number of spread contracts",
  },
  // ... existing optionType and min_volume for chain analysis ...
],
```

#### Modify: `/nextjs-mcp-finance/src/components/mcp-control/ResultsDisplay.tsx`

Add `SpreadAnalysisResults` component:

```tsx
function SpreadAnalysisResults({ result }: { result: SpreadAnalysisResult }) {
  const formatSpreadType = (type: string) => {
    const labels: Record<string, string> = {
      call_credit: "Call Credit Spread",
      put_credit: "Put Credit Spread",
      call_debit: "Call Debit Spread",
      put_debit: "Put Debit Spread",
      iron_condor: "Iron Condor",
      iron_butterfly: "Iron Butterfly",
    };
    return labels[type] || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "MAX_PROFIT": return "bg-green-100 border-green-500";
      case "PROFITABLE": return "bg-green-50 border-green-400";
      case "BREAKEVEN": return "bg-yellow-50 border-yellow-400";
      case "AT_RISK": return "bg-orange-50 border-orange-400";
      case "MAX_LOSS": return "bg-red-100 border-red-500";
      default: return "bg-gray-50 border-gray-400";
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-bold">{result.symbol}</Badge>
          <Badge className="bg-purple-600">{formatSpreadType(result.spread_type)}</Badge>
        </div>
        <Badge variant={result.net_credit_or_debit > 0 ? "default" : "secondary"}>
          {result.net_credit_or_debit > 0 ? "Credit" : "Debit"}:
          ${Math.abs(result.net_credit_or_debit).toFixed(2)}
        </Badge>
      </div>

      {/* Current Price */}
      <div className="text-sm text-muted-foreground">
        {result.symbol} @ ${result.current_price.toFixed(2)} |
        Expires: {result.expiration} ({result.days_to_expiration} DTE)
      </div>

      {/* Risk/Reward Card */}
      <Card className="p-4">
        <h4 className="text-sm font-semibold mb-3">Risk / Reward</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Max Profit</p>
            <p className="text-xl font-bold text-green-600">
              +${result.max_profit.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Max Loss</p>
            <p className="text-xl font-bold text-red-600">
              -${Math.abs(result.max_loss).toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Breakeven</p>
            <p className="text-lg font-semibold">
              {result.breakeven_lower && result.breakeven_upper
                ? `$${result.breakeven_lower.toFixed(2)} / $${result.breakeven_upper.toFixed(2)}`
                : result.breakeven
                  ? `$${result.breakeven.toFixed(2)}`
                  : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Win Probability</p>
            <p className="text-lg font-semibold">
              {(result.probability_of_profit * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      </Card>

      {/* Position Legs */}
      <Card className="p-4">
        <h4 className="text-sm font-semibold mb-3">Position Legs</h4>
        <div className="space-y-2">
          {result.legs.map((leg, i) => (
            <div key={i} className="flex items-center justify-between p-2 bg-muted rounded">
              <div className="flex items-center gap-2">
                <Badge
                  variant={leg.type.includes("short") ? "destructive" : "default"}
                  className="text-xs"
                >
                  {leg.type.includes("short") ? "SELL" : "BUY"}
                </Badge>
                <span className="text-sm font-medium">
                  {leg.type.includes("call") ? "Call" : "Put"} @ ${leg.strike}
                </span>
              </div>
              <div className="text-right text-sm">
                <span className="text-muted-foreground">Premium: </span>
                <span className="font-mono">${leg.premium.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Net Greeks */}
      <Card className="p-4">
        <h4 className="text-sm font-semibold mb-3">Net Greeks</h4>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div>
            <p className="text-xs text-muted-foreground">Delta</p>
            <p className="font-bold">{result.net_delta.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Gamma</p>
            <p className="font-bold">{result.net_gamma.toFixed(3)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Theta</p>
            <p className="font-bold text-green-600">
              ${result.net_theta.toFixed(2)}/day
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Vega</p>
            <p className="font-bold">{result.net_vega.toFixed(2)}</p>
          </div>
        </div>
      </Card>

      {/* Status & Warnings */}
      <Card className={`p-4 border-2 ${getStatusColor(result.current_status)}`}>
        <div className="flex items-center justify-between">
          <span className="font-semibold">Current Status</span>
          <Badge variant="outline">{result.current_status.replace("_", " ")}</Badge>
        </div>
        {result.warnings.length > 0 && (
          <div className="mt-3 space-y-1">
            {result.warnings.map((warning, i) => (
              <p key={i} className="text-xs text-amber-600 flex items-center gap-1">
                <span>⚠️</span> {warning}
              </p>
            ))}
          </div>
        )}
      </Card>

      {/* AI Analysis (if available) */}
      {result.ai_analysis && (
        <Card className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <span>🤖</span> AI Analysis
          </h4>
          <div className="text-sm space-y-2">
            {result.ai_analysis.summary && (
              <p>{result.ai_analysis.summary}</p>
            )}
            {result.ai_analysis.recommendation && (
              <p className="font-medium text-purple-700">
                {result.ai_analysis.recommendation}
              </p>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

// Update OptionsRiskResults to detect spreads
function OptionsRiskResults({ result, tier }: { result: any; tier: string }) {
  // Route to spread display if spread_type present
  if (result.spread_type) {
    return <SpreadAnalysisResults result={result} />;
  }

  // Existing chain analysis display
  return (
    <div className="space-y-3">
      {/* ... existing code ... */}
    </div>
  );
}
```

---

### Phase 5: AI Integration — 1-2 hours

#### Create: `/mcp-finance1/src/technical_analysis_mcp/options_ai_analyzer.py`

Adapt from `/nu-logs/options_ai_analyzer.py`:

```python
import google.generativeai as genai
import json
import os

class OptionsAIAnalyzer:
    """AI-powered analysis for options spreads."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    def analyze_spread(self, spread_result: dict) -> dict:
        """Generate AI insights for a spread position."""
        if not self.model:
            return {"error": "GEMINI_API_KEY not configured"}

        prompt = f"""You are an expert options trader. Analyze this spread position:

POSITION: {spread_result['spread_type'].replace('_', ' ').title()}
SYMBOL: {spread_result['symbol']} @ ${spread_result['current_price']:.2f}
EXPIRATION: {spread_result['expiration']} ({spread_result['days_to_expiration']} days)

LEGS:
{self._format_legs(spread_result['legs'])}

RISK METRICS:
- Max Profit: ${spread_result['max_profit']:.2f}
- Max Loss: ${spread_result['max_loss']:.2f}
- Breakeven: ${spread_result.get('breakeven', 'N/A')}
- Probability of Profit: {spread_result['probability_of_profit']*100:.0f}%
- Risk/Reward Ratio: {spread_result['risk_reward_ratio']:.2f}

NET GREEKS:
- Delta: {spread_result['net_delta']:.2f}
- Theta: ${spread_result['net_theta']:.2f}/day
- Vega: {spread_result['net_vega']:.2f}

CURRENT STATUS: {spread_result['current_status']}

Provide a brief analysis with:
1. ASSESSMENT: Is this a good setup? (1-2 sentences)
2. KEY RISKS: What could go wrong? (2-3 bullets)
3. MANAGEMENT: When to close or adjust?
4. VERDICT: ENTER / HOLD / AVOID

Return as JSON with keys: assessment, risks, management, verdict"""

        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            return {"error": str(e)}

    def _format_legs(self, legs: list) -> str:
        lines = []
        for leg in legs:
            action = "SELL" if "short" in leg["type"] else "BUY"
            opt_type = "Call" if "call" in leg["type"] else "Put"
            lines.append(f"  {action} {opt_type} @ ${leg['strike']} for ${leg['premium']:.2f}")
        return "\n".join(lines)

    def _parse_response(self, text: str) -> dict:
        # Clean and parse JSON from response
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            return json.loads(text.strip())
        except:
            return {"raw_analysis": text}
```

---

### Phase 6: Tier Limits — 30 minutes

#### Modify: `/nextjs-mcp-finance/src/lib/auth/tiers.ts`

Update options tool limits:

```typescript
export const TIER_LIMITS: Record<Tier, TierLimits> = {
  free: {
    // ... existing ...
    tools: {
      // ... existing ...
      options_risk_analysis: {
        enabled: true,
        monthly: 5,
        ai: false,
        spreads: ["call_credit", "put_credit"],  // Basic spreads only
      },
    },
  },
  pro: {
    // ... existing ...
    tools: {
      // ... existing ...
      options_risk_analysis: {
        enabled: true,
        monthly: Infinity,
        ai: true,
        spreads: ["call_credit", "put_credit", "call_debit",
                  "put_debit", "iron_condor", "iron_butterfly"],
      },
    },
  },
  max: {
    // ... existing ...
    tools: {
      // ... existing ...
      options_risk_analysis: {
        enabled: true,
        monthly: Infinity,
        ai: true,
        spreads: ["all"],  // All spread types
      },
    },
  },
};
```

---

## File Summary

| File | Action | Lines Changed |
|------|--------|---------------|
| `spreads.py` | CREATE | ~300 lines |
| `options_ai_analyzer.py` | CREATE | ~100 lines |
| `server.py` | MODIFY | ~50 lines |
| `types.ts` | MODIFY | ~60 lines |
| `client.ts` | MODIFY | ~20 lines |
| `route.ts` | MODIFY | ~40 lines |
| `ParameterForm.tsx` | MODIFY | ~50 lines |
| `ResultsDisplay.tsx` | MODIFY | ~150 lines |
| `tiers.ts` | MODIFY | ~15 lines |

**Total New/Modified Code:** ~785 lines

---

## Verification Plan

### Backend Testing

```bash
# Activate environment
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/mamba.sh
mamba activate fin-ai1

# Test spread analyzer directly
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python -c "
import asyncio
from src.technical_analysis_mcp.spreads import SpreadAnalyzer

async def test():
    analyzer = SpreadAnalyzer()
    result = analyzer.analyze_call_credit_spread('MU', 90, 94, '2026-03-21', 1)
    print(f'Symbol: {result.symbol}')
    print(f'Spread: {result.spread_type}')
    print(f'Max Profit: \${result.max_profit:.2f}')
    print(f'Max Loss: \${result.max_loss:.2f}')
    print(f'Breakeven: \${result.breakeven:.2f}')
    print(f'Probability of Profit: {result.probability_of_profit*100:.0f}%')

asyncio.run(test())
"
```

### API Testing

```bash
# Test via curl
curl -X POST http://localhost:3000/api/mcp/options-risk \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MU",
    "position_type": "spread",
    "spread_type": "call_credit",
    "short_strike": 90,
    "long_strike": 94,
    "expiration": "2026-03-21",
    "contracts": 1,
    "use_ai": true
  }'
```

### E2E Testing

```typescript
// e2e/options-spread.spec.ts
test("analyze MU call credit spread", async ({ page }) => {
  await page.goto("/mcp-control");
  await page.selectOption('[data-testid="tool-selector"]', "options_risk_analysis");
  await page.fill('[name="symbol"]', "MU");
  await page.selectOption('[name="spread_type"]', "call_credit");
  await page.fill('[name="short_strike"]', "90");
  await page.fill('[name="long_strike"]', "94");
  await page.fill('[name="expiration"]', "2026-03-21");
  await page.click('button:has-text("Execute")');

  await expect(page.locator("text=Max Profit")).toBeVisible();
  await expect(page.locator("text=Max Loss")).toBeVisible();
  await expect(page.locator("text=Breakeven")).toBeVisible();
});
```

### Manual Testing Checklist

- [ ] MU 90-94 call credit spread
- [ ] SPY put credit spread
- [ ] AAPL call debit spread
- [ ] QQQ iron condor
- [ ] Verify Greeks sum correctly
- [ ] Verify breakeven calculations
- [ ] Test AI analysis (Pro tier)
- [ ] Verify tier limits enforced
- [ ] Test error handling
- [ ] Mobile responsive check

---

## Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Backend | 3-4 hours | 3-4 hours |
| Phase 2: Types | 30 min | 4-4.5 hours |
| Phase 3: API | 1 hour | 5-5.5 hours |
| Phase 4: Frontend | 2-3 hours | 7-8.5 hours |
| Phase 5: AI | 1-2 hours | 8-10.5 hours |
| Phase 6: Tiers | 30 min | 8.5-11 hours |
| Testing | 1-2 hours | 10-12 hours |

**Total: ~10-12 hours**

---

## Success Criteria

- [ ] Can analyze any stock/ETF spread (MU, AAPL, SPY, QQQ, etc.)
- [ ] All 6 spread types working
- [ ] Max profit/loss calculations accurate
- [ ] Breakeven calculations accurate
- [ ] Greeks aggregated correctly
- [ ] AI analysis provides useful insights
- [ ] Tier limits enforced
- [ ] No mock data - all real market data
- [ ] Error handling graceful
- [ ] Mobile responsive
