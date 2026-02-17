"""Options MCP Backend - FastAPI Application for Cloud Run.

Focused options risk analysis backend optimized for GCloud MCP with Claude.
Exposes REST API endpoints for a Next.js frontend and MCP protocol for Claude.

Endpoints:
    POST /api/options-risk          Full options chain risk analysis
    POST /api/options-summary       Quick options snapshot
    POST /api/options-vehicle       Stock vs options recommendation
    POST /api/options-compare       Multi-symbol options comparison
    POST /api/options-enhanced      Enhanced analysis with AI insights
    POST /api/options-ai            Risk analysis with Gemini AI
    POST /api/spread-trade          Analyze specific spread trades (open/close)
    POST /api/pipeline/run          Run Finnhub pipeline for symbols
    POST /api/pipeline/run-single   Run pipeline for a single symbol
    GET  /                          Health check
    GET  /health                    Detailed health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import logging
import os
import sys
from pathlib import Path

# Load local env file (for dev; Cloud Run sets env vars directly)
_env_file = Path(__file__).parent / ".env.cloud-run"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import MCP server functions
try:
    from options_mcp.server import (
        options_risk_analysis,
        options_summary,
        options_vehicle_selection,
        options_compare,
    )
    from options_mcp.analysis.chain_analyzer import OptionsDataError

    MCP_AVAILABLE = True
    logger.info("Options MCP server functions imported successfully")
except ImportError as e:
    logger.error("Options MCP server functions not available: %s", e)
    MCP_AVAILABLE = False
    options_risk_analysis = None
    options_summary = None
    options_vehicle_selection = None
    options_compare = None

# Import Finnhub pipeline
try:
    from finnhub_pipeline.pipeline import OptionsPipeline

    PIPELINE_AVAILABLE = True
    logger.info("Finnhub pipeline module imported successfully")
except ImportError as e:
    logger.error("Finnhub pipeline not available: %s", e)
    PIPELINE_AVAILABLE = False

# Import AI analyzer
try:
    from options_mcp.analysis.ai_analyzer import OptionsAIAnalyzer

    AI_AVAILABLE = True
    logger.info("Options AI Analyzer imported successfully")
except ImportError as e:
    logger.warning("Options AI Analyzer not available: %s", e)
    AI_AVAILABLE = False

# Import analysis runner for enhanced fields
try:
    from run_analysis import OptionsAnalysisRunner

    RUNNER_AVAILABLE = True
except ImportError as e:
    logger.warning("Analysis runner not available: %s", e)
    RUNNER_AVAILABLE = False


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Options MCP Backend",
    description="Focused options risk analysis API for GCloud MCP with Claude",
    version="1.0.0",
)

# CORS - allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request Models
# =============================================================================


class OptionsRiskRequest(BaseModel):
    """Request body for options risk analysis."""

    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    expiration_date: str | None = Field(
        None, description="Expiration date (YYYY-MM-DD). Auto-selects if omitted."
    )
    option_type: str = Field("both", description="calls, puts, or both")
    min_volume: int = Field(75, ge=1, description="Minimum volume filter")
    min_dte: int = Field(
        7, ge=0,
        description="Minimum days to expiration for auto-selection. "
        "Default 7 skips near-term expirations with extreme theta decay. "
        "Set to 0 to allow same-day (0 DTE) options.",
    )


class OptionsSummaryRequest(BaseModel):
    """Request body for options summary."""

    symbol: str = Field(..., description="Stock symbol")


class VehicleRequest(BaseModel):
    """Request body for vehicle selection."""

    symbol: str = Field(..., description="Stock symbol")
    timeframe: str = Field("swing", description="swing, day, or scalp")
    bias: str = Field("bullish", description="bullish or bearish")
    expected_move_percent: float = Field(
        3.0, ge=0, description="Expected move %"
    )


class CompareRequest(BaseModel):
    """Request body for multi-symbol comparison."""

    symbols: list[str] = Field(
        ..., min_length=2, max_length=10, description="Symbols to compare"
    )
    metric: str = Field("iv", description="iv, pcr, volume, or liquidity")


class PipelineRunRequest(BaseModel):
    """Request body for running the Finnhub options pipeline."""

    symbols: list[str] = Field(
        default=["AEM", "CRM", "IGV", "QBTS", "JPM"],
        min_length=1,
        max_length=20,
        description="Ticker symbols to process",
    )
    fetch_candles: bool = Field(True, description="Include historical candle data")


class PipelineSingleRequest(BaseModel):
    """Request body for running pipeline on a single symbol."""

    symbol: str = Field(..., description="Single ticker symbol")
    fetch_candles: bool = Field(True, description="Include historical candle data")


class AIAnalysisRequest(BaseModel):
    """Request body for AI-enhanced options analysis."""

    symbol: str = Field(..., description="Stock symbol")
    use_ai: bool = Field(True, description="Include Gemini AI insights")
    bias: str = Field("bullish", description="bullish or bearish")
    expected_move_percent: float = Field(3.0, ge=0, description="Expected move %")


class SpreadTradeRequest(BaseModel):
    """Request body for analyzing a specific option spread trade."""

    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    spread_type: str = Field(
        ...,
        description=(
            "Spread type: bull_call, bear_put, bull_put_credit, "
            "bear_call_credit, iron_condor, straddle, strangle"
        ),
    )
    buy_strike: float = Field(..., description="Long leg strike price")
    sell_strike: float = Field(..., description="Short leg strike price")
    expiration_date: str | None = Field(
        None, description="Expiration date (YYYY-MM-DD). Auto-selects if omitted."
    )
    contracts: int = Field(1, ge=1, le=100, description="Number of contracts")
    action: str = Field(
        "open",
        description="open = entering the trade, close = exiting the trade",
    )
    entry_price: float | None = Field(
        None,
        description="Entry price per spread (required for close action)",
    )
    min_dte: int = Field(
        1, ge=0,
        description="Minimum days to expiration for auto-selection. "
        "Default 1 skips same-day expiry. Set to 0 to allow 0 DTE.",
    )


# =============================================================================
# Health Check
# =============================================================================


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Options MCP Backend",
        "version": "2.0.0",
        "status": "healthy",
        "mcp_available": MCP_AVAILABLE,
        "ai_available": AI_AVAILABLE,
        "pipeline_available": PIPELINE_AVAILABLE,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    checks = {
        "mcp_server": "ok" if MCP_AVAILABLE else "unavailable",
        "python": sys.version,
    }

    # Quick yfinance connectivity test
    try:
        import yfinance as yf

        ticker = yf.Ticker("SPY")
        _ = ticker.options
        checks["yfinance"] = "ok"
    except Exception as e:
        checks["yfinance"] = f"error: {e}"

    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"

    return {"status": status, "checks": checks}


# =============================================================================
# API Endpoints
# =============================================================================


@app.post("/api/options-risk")
async def options_risk_endpoint(request: OptionsRiskRequest):
    """Full options chain risk analysis.

    Returns IV analysis, PCR, volume/OI metrics, risk warnings,
    and opportunities for calls, puts, or both.
    """
    _require_mcp()

    try:
        logger.info(
            "Options risk analysis: %s (type=%s, exp=%s)",
            request.symbol,
            request.option_type,
            request.expiration_date or "nearest",
        )
        result = await options_risk_analysis(
            symbol=request.symbol,
            expiration_date=request.expiration_date,
            option_type=request.option_type,
            min_volume=request.min_volume,
            min_dte=request.min_dte,
        )
        return {"success": True, "data": result}
    except OptionsDataError as e:
        logger.warning("Options data error: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Options risk analysis error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/options-summary")
async def options_summary_endpoint(request: OptionsSummaryRequest):
    """Quick options snapshot.

    Returns ATM IV, PCR, sentiment, and risk level for a symbol.
    """
    _require_mcp()

    try:
        logger.info("Options summary: %s", request.symbol)
        result = await options_summary(symbol=request.symbol)
        return {"success": True, "data": result}
    except OptionsDataError as e:
        logger.warning("Options data error: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Options summary error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/options-vehicle")
async def options_vehicle_endpoint(request: VehicleRequest):
    """Stock vs options recommendation.

    Uses the stock-first decision tree based on timeframe,
    volatility regime, bias, and expected move.
    """
    _require_mcp()

    try:
        logger.info(
            "Vehicle selection: %s (tf=%s, bias=%s, move=%.1f%%)",
            request.symbol,
            request.timeframe,
            request.bias,
            request.expected_move_percent,
        )
        result = await options_vehicle_selection(
            symbol=request.symbol,
            timeframe=request.timeframe,
            bias=request.bias,
            expected_move_percent=request.expected_move_percent,
        )
        return {"success": True, "data": result}
    except OptionsDataError as e:
        logger.warning("Options data error: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Vehicle selection error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/options-compare")
async def options_compare_endpoint(request: CompareRequest):
    """Compare options metrics across multiple symbols.

    Compares by IV, PCR, volume, or liquidity and returns
    ranked results.
    """
    _require_mcp()

    try:
        logger.info(
            "Options compare: %s by %s",
            request.symbols,
            request.metric,
        )
        result = await options_compare(
            symbols=request.symbols,
            metric=request.metric,
        )
        return {"success": True, "data": result}
    except OptionsDataError as e:
        logger.warning("Options data error: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Options compare error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AI-Enhanced Analysis Endpoints
# =============================================================================


@app.post("/api/options-enhanced")
async def options_enhanced_endpoint(request: AIAnalysisRequest):
    """Full options analysis with enhanced fields and optional AI insights.

    Returns risk analysis, summary, vehicle recommendation, plus:
    - iv_rank, max_pain, unusual_activity, greeks_exposure, spread_opportunities
    - Gemini AI natural language insights (if use_ai=True)
    """
    if not RUNNER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Analysis runner not available",
        )

    try:
        logger.info(
            "Enhanced analysis: %s (ai=%s, bias=%s)",
            request.symbol,
            request.use_ai,
            request.bias,
        )
        runner = OptionsAnalysisRunner()
        result = runner.run(
            symbols=[request.symbol],
            bias=request.bias,
            expected_move_percent=request.expected_move_percent,
            dry_run=True,
            use_ai=request.use_ai,
        )

        # Extract the single symbol result from the runner metadata
        # The actual analysis data is stored during run; for dry_run we
        # need to re-run _analyze_symbol directly
        sym_result = runner._analyze_symbol(
            request.symbol,
            request.bias,
            request.expected_move_percent,
            use_ai=request.use_ai,
        )

        return {"success": True, "data": sym_result}
    except Exception as e:
        logger.error("Enhanced analysis error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/options-ai")
async def options_ai_endpoint(request: OptionsRiskRequest):
    """Options risk analysis with Gemini AI insights.

    Runs standard risk analysis then passes results through AI
    for natural language interpretation and strategy recommendations.
    """
    _require_mcp()

    if not AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI analyzer not available - install google-generativeai",
        )

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY not configured",
        )

    try:
        logger.info("AI options analysis: %s", request.symbol)

        # Run standard risk analysis first
        risk_result = await options_risk_analysis(
            symbol=request.symbol,
            expiration_date=request.expiration_date,
            option_type=request.option_type,
            min_volume=request.min_volume,
            min_dte=request.min_dte,
        )

        # Pass through AI analyzer
        analyzer = OptionsAIAnalyzer(api_key=gemini_key)
        enhanced = analyzer.analyze_risk_output(risk_result)

        return {"success": True, "data": enhanced}
    except OptionsDataError as e:
        logger.warning("Options data error: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("AI analysis error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/spread-trade")
async def spread_trade_endpoint(request: SpreadTradeRequest):
    """Analyze a specific option spread trade (open or close).

    Evaluates a defined spread with real chain data: computes Greeks,
    max profit/loss, breakeven, probability estimates, and provides
    AI-powered trade assessment if GEMINI_API_KEY is configured.

    Supported spread types:
    - bull_call: Buy lower call, sell higher call (debit)
    - bear_put: Buy higher put, sell lower put (debit)
    - bull_put_credit: Sell higher put, buy lower put (credit)
    - bear_call_credit: Sell lower call, buy higher call (credit)
    - iron_condor: Bull put + bear call credit spreads
    - straddle: Buy ATM call + put at same strike
    - strangle: Buy OTM call + put at different strikes
    """
    _require_mcp()

    try:
        logger.info(
            "Spread trade analysis: %s %s %s %.2f/%.2f x%d (%s)",
            request.action.upper(),
            request.symbol,
            request.spread_type,
            request.buy_strike,
            request.sell_strike,
            request.contracts,
            request.expiration_date or "nearest",
        )

        result = await _analyze_spread_trade(request)
        return {"success": True, "data": result}

    except OptionsDataError as e:
        logger.warning("Spread trade data error: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Spread trade error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _analyze_spread_trade(request: SpreadTradeRequest) -> dict:
    """Core spread trade analysis logic.

    Fetches real chain data, computes spread metrics, and optionally
    runs AI analysis for trade assessment.

    Args:
        request: SpreadTradeRequest with trade parameters.

    Returns:
        Dict with spread metrics, risk/reward, and optional AI analysis.
    """
    from options_mcp.analysis.chain_analyzer import ChainAnalyzer

    analyzer = ChainAnalyzer()
    ticker, current_price = analyzer.fetch_ticker_data(request.symbol)
    expirations = analyzer.get_expirations(ticker, request.symbol)
    exp = analyzer.select_expiration(
        expirations, request.expiration_date, request.symbol,
        min_dte=request.min_dte,
    )
    calls_df, puts_df = analyzer.fetch_option_chain(ticker, exp)

    from datetime import datetime

    exp_date = datetime.strptime(exp, "%Y-%m-%d")
    dte = (exp_date - datetime.now()).days

    # Determine which chain to use based on spread type
    spread_type = request.spread_type.lower()
    is_credit = spread_type in ("bull_put_credit", "bear_call_credit")

    if spread_type in ("bull_call", "bear_call_credit"):
        chain = calls_df
        opt_label = "calls"
    elif spread_type in ("bear_put", "bull_put_credit"):
        chain = puts_df
        opt_label = "puts"
    elif spread_type in ("iron_condor", "straddle", "strangle"):
        chain = None
        opt_label = "both"
    else:
        raise ValueError(
            f"Unknown spread type: {spread_type}. "
            "Use: bull_call, bear_put, bull_put_credit, bear_call_credit, "
            "iron_condor, straddle, strangle"
        )

    # Find the specific contracts
    buy_leg = _find_contract(
        chain if chain is not None else calls_df,
        request.buy_strike,
        request.symbol,
        "buy",
    )
    sell_leg = _find_contract(
        chain if chain is not None else puts_df,
        request.sell_strike,
        request.symbol,
        "sell",
    )

    # Compute spread metrics
    spread_width = abs(request.sell_strike - request.buy_strike)

    if is_credit:
        net_premium = (sell_leg.get("bid", 0) or 0) - (buy_leg.get("ask", 0) or 0)
        max_profit = net_premium * 100 * request.contracts
        max_loss = (spread_width - net_premium) * 100 * request.contracts
        breakeven = (
            request.sell_strike - net_premium
            if "put" in spread_type
            else request.sell_strike + net_premium
        )
    else:
        net_debit = (buy_leg.get("ask", 0) or 0) - (sell_leg.get("bid", 0) or 0)
        max_loss = net_debit * 100 * request.contracts
        max_profit = (spread_width - net_debit) * 100 * request.contracts
        breakeven = (
            request.buy_strike + net_debit
            if "call" in spread_type
            else request.buy_strike - net_debit
        )

    # Greeks for the spread
    buy_iv = buy_leg.get("impliedVolatility", 0) or 0
    sell_iv = sell_leg.get("impliedVolatility", 0) or 0
    buy_delta = buy_leg.get("delta", 0) or 0
    sell_delta = sell_leg.get("delta", 0) or 0

    rr_ratio = abs(max_profit / max_loss) if max_loss != 0 else 0

    spread_result = {
        "symbol": request.symbol,
        "spread_type": spread_type,
        "action": request.action,
        "current_price": current_price,
        "expiration": exp,
        "dte": dte,
        "buy_strike": request.buy_strike,
        "sell_strike": request.sell_strike,
        "contracts": request.contracts,
        "spread_width": round(spread_width, 2),
        "buy_leg": {
            "strike": request.buy_strike,
            "bid": buy_leg.get("bid"),
            "ask": buy_leg.get("ask"),
            "iv": round(buy_iv * 100, 2) if buy_iv < 5 else round(buy_iv, 2),
            "delta": round(buy_delta, 4) if buy_delta else None,
            "volume": buy_leg.get("volume", 0),
            "open_interest": buy_leg.get("openInterest", 0),
        },
        "sell_leg": {
            "strike": request.sell_strike,
            "bid": sell_leg.get("bid"),
            "ask": sell_leg.get("ask"),
            "iv": round(sell_iv * 100, 2) if sell_iv < 5 else round(sell_iv, 2),
            "delta": round(sell_delta, 4) if sell_delta else None,
            "volume": sell_leg.get("volume", 0),
            "open_interest": sell_leg.get("openInterest", 0),
        },
        "is_credit": is_credit,
        "max_profit": round(max_profit, 2),
        "max_loss": round(abs(max_loss), 2),
        "risk_reward_ratio": round(rr_ratio, 2),
        "breakeven": round(breakeven, 2),
        "net_delta": round(buy_delta - sell_delta, 4),
    }

    # For close action, calculate P&L
    if request.action == "close" and request.entry_price is not None:
        if is_credit:
            current_value = (
                (sell_leg.get("ask", 0) or 0) - (buy_leg.get("bid", 0) or 0)
            )
        else:
            current_value = (
                (buy_leg.get("bid", 0) or 0) - (sell_leg.get("ask", 0) or 0)
            )

        pnl_per_spread = (
            (request.entry_price - current_value)
            if is_credit
            else (current_value - request.entry_price)
        )

        spread_result["close_analysis"] = {
            "entry_price": request.entry_price,
            "current_value": round(current_value, 2),
            "pnl_per_spread": round(pnl_per_spread, 2),
            "total_pnl": round(pnl_per_spread * 100 * request.contracts, 2),
            "pnl_percent": (
                round((pnl_per_spread / request.entry_price) * 100, 2)
                if request.entry_price != 0
                else 0
            ),
        }

    # Optional AI analysis
    gemini_key = os.getenv("GEMINI_API_KEY")
    if AI_AVAILABLE and gemini_key:
        try:
            ai_analyzer = OptionsAIAnalyzer(api_key=gemini_key)
            ai_prompt = _build_spread_ai_prompt(spread_result)
            response = ai_analyzer._model.generate_content(ai_prompt)
            spread_result["ai_analysis"] = ai_analyzer._parse_ai_response(
                response.text
            )
        except Exception as e:
            logger.warning("AI analysis for spread failed: %s", e)
            spread_result["ai_analysis"] = {
                "status": "error",
                "error": str(e),
            }

    return spread_result


def _find_contract(
    chain_df,
    strike: float,
    symbol: str,
    leg: str,
) -> dict:
    """Find the nearest contract to a given strike.

    Args:
        chain_df: Options chain DataFrame.
        strike: Target strike price.
        symbol: Symbol for error messages.
        leg: 'buy' or 'sell' for logging.

    Returns:
        Dict of contract data.

    Raises:
        OptionsDataError: If chain is empty.
    """
    if chain_df.empty:
        raise OptionsDataError(symbol, f"No options data for {leg} leg")

    distance = (chain_df["strike"] - strike).abs()
    idx = distance.idxmin()
    row = chain_df.loc[idx]
    return row.to_dict()


def _build_spread_ai_prompt(spread_data: dict) -> str:
    """Build AI prompt for spread trade analysis.

    Args:
        spread_data: Computed spread metrics dict.

    Returns:
        Prompt string for Gemini.
    """
    action = spread_data["action"].upper()
    spread_type = spread_data["spread_type"].replace("_", " ").title()
    symbol = spread_data["symbol"]

    prompt = f"""You are an expert options spread trader. Analyze this {action} {spread_type} trade.

# SPREAD TRADE: {action} {spread_type} on {symbol}
- Current Price: ${spread_data['current_price']:.2f}
- Expiration: {spread_data['expiration']} ({spread_data['dte']} DTE)
- Buy Strike: ${spread_data['buy_strike']:.2f}
- Sell Strike: ${spread_data['sell_strike']:.2f}
- Contracts: {spread_data['contracts']}
- Spread Width: ${spread_data['spread_width']:.2f}
- Is Credit: {spread_data['is_credit']}

# RISK/REWARD
- Max Profit: ${spread_data['max_profit']:.2f}
- Max Loss: ${spread_data['max_loss']:.2f}
- Risk/Reward Ratio: {spread_data['risk_reward_ratio']:.2f}
- Breakeven: ${spread_data['breakeven']:.2f}
- Net Delta: {spread_data['net_delta']:.4f}

# BUY LEG
- Strike: ${spread_data['buy_leg']['strike']:.2f}
- Bid/Ask: ${spread_data['buy_leg'].get('bid', 0):.2f} / ${spread_data['buy_leg'].get('ask', 0):.2f}
- IV: {spread_data['buy_leg'].get('iv', 0):.1f}%
- Volume: {spread_data['buy_leg'].get('volume', 0)}
- OI: {spread_data['buy_leg'].get('open_interest', 0)}

# SELL LEG
- Strike: ${spread_data['sell_leg']['strike']:.2f}
- Bid/Ask: ${spread_data['sell_leg'].get('bid', 0):.2f} / ${spread_data['sell_leg'].get('ask', 0):.2f}
- IV: {spread_data['sell_leg'].get('iv', 0):.1f}%
- Volume: {spread_data['sell_leg'].get('volume', 0)}
- OI: {spread_data['sell_leg'].get('open_interest', 0)}
"""

    if "close_analysis" in spread_data:
        ca = spread_data["close_analysis"]
        prompt += f"""
# CLOSE ANALYSIS
- Entry Price: ${ca['entry_price']:.2f}
- Current Value: ${ca['current_value']:.2f}
- P&L per Spread: ${ca['pnl_per_spread']:.2f}
- Total P&L: ${ca['total_pnl']:.2f}
- P&L %: {ca['pnl_percent']:.1f}%
"""

    prompt += f"""

# YOUR TASK

Analyze this {action} trade and provide actionable guidance in JSON format:

1. **trade_assessment**: Is this a good trade to {action.lower()}? Quality rating.
2. **timing**: Is the timing right given DTE and market conditions?
3. **risk_analysis**: Evaluate the risk/reward profile
4. **execution_tips**: How to get the best fill
5. **management_plan**: How to manage once in the trade (or why to close now)
6. **alternatives**: Better trades to consider
7. **verdict**: Clear GO/NO-GO recommendation with reasoning

Return ONLY valid JSON:

{{
  "trade_assessment": {{
    "quality": "EXCELLENT|GOOD|FAIR|POOR",
    "conviction": "HIGH|MEDIUM|LOW",
    "explanation": "string"
  }},
  "timing": {{
    "is_good_timing": true,
    "dte_assessment": "string",
    "iv_context": "string",
    "recommendation": "string"
  }},
  "risk_analysis": {{
    "risk_reward_quality": "string",
    "max_loss_acceptable": "string",
    "probability_estimate": "string",
    "key_risks": ["string"]
  }},
  "execution_tips": [
    "string"
  ],
  "management_plan": {{
    "profit_target": "string",
    "stop_loss": "string",
    "adjustment_triggers": ["string"],
    "time_stop": "string"
  }},
  "alternatives": [
    {{
      "strategy": "string",
      "why_better": "string",
      "strikes": "string"
    }}
  ],
  "verdict": {{
    "decision": "GO|NO_GO|WAIT",
    "reasoning": "string",
    "conditions_to_revisit": "string"
  }}
}}
"""
    return prompt


# =============================================================================
# Finnhub Pipeline Endpoints
# =============================================================================


@app.post("/api/pipeline/run")
async def pipeline_run_endpoint(request: PipelineRunRequest):
    """Run the Finnhub options pipeline for multiple symbols.

    Fetches options chain from Finnhub and historical candles
    (Finnhub primary, Alpha Vantage fallback), stores in Firestore.
    """
    _require_pipeline()

    finnhub_key = os.getenv("FINHUB_API_KEY", "")
    av_key = os.getenv("ALPHA_VANTAGE_KEY", "")
    if not finnhub_key:
        raise HTTPException(status_code=500, detail="FINHUB_API_KEY not configured")

    try:
        pipeline = OptionsPipeline(
            finnhub_key=finnhub_key,
            alpha_vantage_key=av_key,
        )
        result = pipeline.run(
            symbols=request.symbols,
            fetch_candles=request.fetch_candles,
        )
        pipeline.close()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error("Pipeline run error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline/run-single")
async def pipeline_single_endpoint(request: PipelineSingleRequest):
    """Run the Finnhub options pipeline for a single symbol."""
    _require_pipeline()

    finnhub_key = os.getenv("FINHUB_API_KEY", "")
    av_key = os.getenv("ALPHA_VANTAGE_KEY", "")
    if not finnhub_key:
        raise HTTPException(status_code=500, detail="FINHUB_API_KEY not configured")

    try:
        pipeline = OptionsPipeline(
            finnhub_key=finnhub_key,
            alpha_vantage_key=av_key,
        )
        result = pipeline.run_single(
            symbol=request.symbol,
            fetch_candles=request.fetch_candles,
        )
        pipeline.close()
        return {"success": True, "data": result}
    except Exception as e:
        logger.error("Pipeline single error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Utility
# =============================================================================


def _require_mcp() -> None:
    """Raise 503 if MCP server functions are not available."""
    if not MCP_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Options MCP server not available - see setup docs",
        )


def _require_pipeline() -> None:
    """Raise 503 if Finnhub pipeline is not available."""
    if not PIPELINE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Finnhub pipeline not available - check imports",
        )


# =============================================================================
# HTML Dashboard
# =============================================================================

FRONTEND_SIGN_IN_URL = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/sign-in"
FRONTEND_DASHBOARD_URL = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/dashboard"


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Interactive HTML dashboard with sign-in navbar."""
    tools = [
        {"id": "options-risk", "name": "Options Risk", "desc": "Full chain risk analysis with warnings and opportunities", "method": "POST", "path": "/api/options-risk", "body": '{"symbol": "AAPL", "min_dte": 7}'},
        {"id": "options-summary", "name": "Options Summary", "desc": "Quick snapshot: IV, PCR, sentiment, risk level", "method": "POST", "path": "/api/options-summary", "body": '{"symbol": "AAPL"}'},
        {"id": "options-vehicle", "name": "Vehicle Selector", "desc": "Stock vs options recommendation based on bias", "method": "POST", "path": "/api/options-vehicle", "body": '{"symbol": "AAPL", "timeframe": "swing", "bias": "bullish", "expected_move_percent": 5.0}'},
        {"id": "options-compare", "name": "Compare Symbols", "desc": "Multi-symbol IV and options comparison", "method": "POST", "path": "/api/options-compare", "body": '{"symbols": ["AAPL", "MSFT", "NVDA"], "metric": "iv"}'},
        {"id": "spread-trade", "name": "Spread Trade", "desc": "Put in a trade idea and get full analysis with AI verdict", "method": "POST", "path": "/api/spread-trade", "body": '{"symbol": "AAPL", "spread_type": "bull_call", "buy_strike": 260, "sell_strike": 265, "contracts": 2, "action": "open", "min_dte": 7}'},
        {"id": "options-enhanced", "name": "Enhanced Analysis", "desc": "Risk + summary + vehicle + 5 enhanced fields", "method": "POST", "path": "/api/options-enhanced", "body": '{"symbol": "AAPL", "use_ai": false}'},
        {"id": "options-ai", "name": "AI Analysis", "desc": "Gemini-powered strategy recommendations", "method": "POST", "path": "/api/options-ai", "body": '{"symbol": "AAPL", "min_dte": 7}'},
        {"id": "pipeline-single", "name": "Pipeline (Single)", "desc": "Fetch and store options chain for one symbol", "method": "POST", "path": "/api/pipeline/run-single", "body": '{"symbol": "AAPL"}'},
    ]

    tool_cards = ""
    for t in tools:
        tool_cards += f"""
        <div class="card" id="card-{t['id']}">
          <h3>{t['name']}</h3>
          <p class="desc">{t['desc']}</p>
          <pre class="body-preview">{t['body']}</pre>
          <textarea id="body-{t['id']}" rows="3">{t['body']}</textarea>
          <button onclick="runTool('{t['id']}', '{t['method']}', '{t['path']}')">Execute</button>
          <div class="result" id="result-{t['id']}"></div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Options MCP Lab</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0f; color: #e0e0e0; }}
  nav {{ display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: #111118; border-bottom: 1px solid #222; position: sticky; top: 0; z-index: 10; }}
  nav .brand {{ font-size: 18px; font-weight: 700; color: #7c3aed; }}
  nav .brand span {{ color: #a78bfa; font-weight: 400; }}
  nav .nav-links {{ display: flex; gap: 16px; align-items: center; }}
  nav a {{ color: #a0a0b0; text-decoration: none; font-size: 14px; transition: color .2s; }}
  nav a:hover {{ color: #fff; }}
  .btn-signin {{ background: #7c3aed; color: #fff; padding: 8px 18px; border-radius: 8px; font-size: 13px; font-weight: 600; }}
  .btn-signin:hover {{ background: #6d28d9; color: #fff; }}
  .btn-dashboard {{ background: transparent; border: 1px solid #7c3aed; color: #a78bfa; padding: 8px 18px; border-radius: 8px; font-size: 13px; font-weight: 600; }}
  .btn-dashboard:hover {{ background: #7c3aed22; }}
  .hero {{ text-align: center; padding: 40px 24px 24px; }}
  .hero h1 {{ font-size: 28px; color: #fff; margin-bottom: 8px; }}
  .hero p {{ color: #888; font-size: 15px; }}
  .status {{ display: flex; gap: 12px; justify-content: center; margin-top: 16px; flex-wrap: wrap; }}
  .status .badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
  .badge.ok {{ background: #064e3b; color: #6ee7b7; }}
  .badge.off {{ background: #451a03; color: #fbbf24; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; padding: 24px; max-width: 1400px; margin: 0 auto; }}
  .card {{ background: #16161e; border: 1px solid #222; border-radius: 12px; padding: 20px; }}
  .card h3 {{ color: #a78bfa; font-size: 16px; margin-bottom: 6px; }}
  .card .desc {{ color: #777; font-size: 13px; margin-bottom: 12px; }}
  .card .body-preview {{ display: none; }}
  .card textarea {{ width: 100%; background: #0d0d14; color: #ccc; border: 1px solid #333; border-radius: 6px; padding: 8px; font-family: monospace; font-size: 12px; resize: vertical; margin-bottom: 10px; }}
  .card button {{ background: #7c3aed; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; transition: background .2s; }}
  .card button:hover {{ background: #6d28d9; }}
  .card button:disabled {{ background: #444; cursor: wait; }}
  .result {{ margin-top: 12px; max-height: 400px; overflow-y: auto; }}
  .result pre {{ background: #0d0d14; padding: 12px; border-radius: 6px; font-size: 11px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; color: #9ca3af; }}
  .result .error {{ color: #f87171; }}
  .result .ok {{ color: #6ee7b7; }}
  footer {{ text-align: center; padding: 24px; color: #555; font-size: 12px; border-top: 1px solid #1a1a1a; margin-top: 24px; }}
</style>
</head>
<body>

<nav>
  <div class="brand">Options MCP <span>Lab</span></div>
  <div class="nav-links">
    <a href="/">API Health</a>
    <a href="/docs">API Docs</a>
    <a href="{FRONTEND_DASHBOARD_URL}" class="btn-dashboard">Dashboard</a>
    <a href="{FRONTEND_SIGN_IN_URL}" class="btn-signin">Sign In</a>
  </div>
</nav>

<div class="hero">
  <h1>Options Analysis Tools</h1>
  <p>Execute any of the 8 options analysis endpoints below. Edit the JSON body and click Execute.</p>
  <div class="status">
    <span class="badge {'ok' if MCP_AVAILABLE else 'off'}">MCP: {'Ready' if MCP_AVAILABLE else 'Unavailable'}</span>
    <span class="badge {'ok' if AI_AVAILABLE else 'off'}">AI: {'Ready' if AI_AVAILABLE else 'Unavailable'}</span>
    <span class="badge {'ok' if PIPELINE_AVAILABLE else 'off'}">Pipeline: {'Ready' if PIPELINE_AVAILABLE else 'Unavailable'}</span>
  </div>
</div>

<div class="grid">
  {tool_cards}
</div>

<footer>Options MCP Backend v2.0.0 &middot; Powered by FastAPI + yfinance + Gemini AI</footer>

<script>
async function runTool(id, method, path) {{
  const btn = document.querySelector('#card-' + id + ' button');
  const resultDiv = document.getElementById('result-' + id);
  const bodyEl = document.getElementById('body-' + id);
  btn.disabled = true;
  btn.textContent = 'Running...';
  resultDiv.innerHTML = '';

  try {{
    const opts = {{ method, headers: {{ 'Content-Type': 'application/json' }} }};
    if (method === 'POST') opts.body = bodyEl.value;
    const start = performance.now();
    const res = await fetch(path, opts);
    const elapsed = ((performance.now() - start) / 1000).toFixed(2);
    const data = await res.json();
    const cls = res.ok ? 'ok' : 'error';
    resultDiv.innerHTML = '<pre class="' + cls + '">' + elapsed + 's — ' + res.status + '\\n' + JSON.stringify(data, null, 2) + '</pre>';
  }} catch (err) {{
    resultDiv.innerHTML = '<pre class="error">Error: ' + err.message + '</pre>';
  }} finally {{
    btn.disabled = false;
    btn.textContent = 'Execute';
  }}
}}
</script>
</body>
</html>"""


# =============================================================================
# Startup / Shutdown
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """Log startup info."""
    logger.info("Options MCP Backend starting...")
    logger.info("MCP available: %s", MCP_AVAILABLE)
    logger.info("Port: %s", os.getenv("PORT", "8080"))


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown."""
    logger.info("Options MCP Backend shutting down...")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
