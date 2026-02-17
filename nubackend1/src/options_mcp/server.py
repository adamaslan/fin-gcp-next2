"""MCP Server for Options Risk Analysis.

Exposes options analysis tools via the MCP protocol for Claude integration
and as importable async functions for the FastAPI layer.

Tools:
    1. options_risk_analysis - Full options chain risk analysis
    2. options_summary - Quick options snapshot
    3. options_vehicle_selection - Stock vs options recommendation
    4. options_compare - Multi-symbol options comparison
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import pandas as pd

from .analysis.chain_analyzer import ChainAnalyzer, OptionsDataError
from .analysis.risk_engine import RiskEngine
from .analysis.vehicle_selector import VehicleSelector
from .config import (
    DEFAULT_MIN_DTE,
    DEFAULT_MIN_VOLUME,
    MAX_EXPIRATIONS_RETURNED,
    SUMMARY_MIN_DTE,
)
from .models import (
    ChainAnalysis,
    OptionsSummaryResponse,
    OptionsRiskResponse,
    PutCallRatio,
    SymbolOptionsComparison,
    MultiSymbolOptionsResponse,
    VehicleRecommendation,
    OptionType,
    Timeframe,
    VolatilityRegime,
)

logger = logging.getLogger(__name__)

# Shared instances (dependency injection at module level)
_chain_analyzer = ChainAnalyzer()
_risk_engine = RiskEngine()
_vehicle_selector = VehicleSelector()


# =============================================================================
# Tool 1: Full Options Risk Analysis
# =============================================================================


async def options_risk_analysis(
    symbol: str,
    expiration_date: str | None = None,
    option_type: str = "both",
    min_volume: int = DEFAULT_MIN_VOLUME,
    min_dte: int = DEFAULT_MIN_DTE,
) -> dict[str, Any]:
    """Analyze options chain risk metrics for a security using real yfinance data.

    Comprehensive options risk analysis including:
    - Real options chain data from yfinance
    - IV (Implied Volatility) analysis
    - Greeks analysis (Delta when available)
    - Volume and open interest analysis
    - Put/Call ratio
    - Risk warnings and opportunities

    Args:
        symbol: Ticker symbol (e.g., AAPL, SPY).
        expiration_date: Specific expiration date (YYYY-MM-DD).
            If None, auto-selects based on min_dte.
        option_type: Type of options to analyze ('calls', 'puts', or 'both').
        min_volume: Minimum volume threshold for liquid options.
        min_dte: Minimum days to expiration for auto-selection (default 7).
            Set to 0 to allow same-day expiry.

    Returns:
        Comprehensive options risk analysis result dictionary.

    Raises:
        OptionsDataError: If options data cannot be fetched.
    """
    symbol = symbol.upper().strip()
    opt_type = OptionType(option_type)

    logger.info(
        "Analyzing options risk for %s (expiration: %s, type: %s, min_vol: %d)",
        symbol,
        expiration_date or "nearest",
        opt_type.value,
        min_volume,
    )

    try:
        ticker, current_price = _chain_analyzer.fetch_ticker_data(symbol)
        expirations = _chain_analyzer.get_expirations(ticker, symbol)
        selected_exp = _chain_analyzer.select_expiration(
            expirations, expiration_date, symbol, min_dte=min_dte,
        )
        calls_df, puts_df = _chain_analyzer.fetch_option_chain(ticker, selected_exp)

        # Calculate DTE
        exp_date = datetime.strptime(selected_exp, "%Y-%m-%d")
        dte = (exp_date - datetime.now()).days

        # Analyze chains
        calls_analysis = None
        if opt_type in (OptionType.CALLS, OptionType.BOTH):
            calls_analysis = _chain_analyzer.analyze_chain(
                calls_df, current_price, min_volume, "calls"
            )

        puts_analysis = None
        if opt_type in (OptionType.PUTS, OptionType.BOTH):
            puts_analysis = _chain_analyzer.analyze_chain(
                puts_df, current_price, min_volume, "puts"
            )

        # Put/Call ratio
        pcr = _compute_pcr(calls_analysis, puts_analysis)

        # Risk assessment
        warnings, opportunities = _risk_engine.assess(
            calls_analysis, puts_analysis, pcr, dte
        )

        response = OptionsRiskResponse(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            expiration_date=selected_exp,
            days_to_expiration=dte,
            available_expirations=list(expirations)[:MAX_EXPIRATIONS_RETURNED],
            calls=calls_analysis,
            puts=puts_analysis,
            put_call_ratio=pcr,
            risk_warnings=warnings,
            opportunities=opportunities,
            liquidity_threshold=min_volume,
        )

        logger.info(
            "Options risk analysis complete for %s: %d calls, %d puts, PCR: %.2f",
            symbol,
            calls_analysis.total_contracts if calls_analysis else 0,
            puts_analysis.total_contracts if puts_analysis else 0,
            pcr.volume if pcr and pcr.volume else 0,
        )

        return response.model_dump()

    except OptionsDataError:
        raise
    except Exception as e:
        logger.error("Options risk analysis failed for %s: %s", symbol, e)
        raise OptionsDataError(symbol, str(e))


# =============================================================================
# Tool 2: Quick Options Summary
# =============================================================================


async def options_summary(symbol: str) -> dict[str, Any]:
    """Get a quick options summary for a symbol.

    Returns ATM IV, PCR, total volumes, and sentiment assessment.

    Args:
        symbol: Ticker symbol.

    Returns:
        Quick summary dictionary.

    Raises:
        OptionsDataError: If data unavailable.
    """
    symbol = symbol.upper().strip()
    logger.info("Generating options summary for %s", symbol)

    try:
        ticker, current_price = _chain_analyzer.fetch_ticker_data(symbol)
        expirations = _chain_analyzer.get_expirations(ticker, symbol)
        selected_exp = _chain_analyzer.select_expiration(
            expirations, None, symbol, min_dte=SUMMARY_MIN_DTE,
        )
        calls_df, puts_df = _chain_analyzer.fetch_option_chain(ticker, selected_exp)

        exp_date = datetime.strptime(selected_exp, "%Y-%m-%d")
        dte = (exp_date - datetime.now()).days

        calls_analysis = _chain_analyzer.analyze_chain(
            calls_df, current_price, DEFAULT_MIN_VOLUME, "calls"
        )
        puts_analysis = _chain_analyzer.analyze_chain(
            puts_df, current_price, DEFAULT_MIN_VOLUME, "puts"
        )

        # Determine sentiment from PCR
        pcr = _compute_pcr(calls_analysis, puts_analysis)
        sentiment = _derive_sentiment(pcr)

        # Determine risk level from IV
        risk_level = _derive_risk_level(calls_analysis, puts_analysis)

        response = OptionsSummaryResponse(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            current_price=current_price,
            nearest_expiration=selected_exp,
            days_to_expiration=dte,
            atm_call_iv=calls_analysis.atm_iv if calls_analysis else None,
            atm_put_iv=puts_analysis.atm_iv if puts_analysis else None,
            put_call_ratio_volume=pcr.volume if pcr else None,
            total_call_volume=calls_analysis.total_volume if calls_analysis else 0,
            total_put_volume=puts_analysis.total_volume if puts_analysis else 0,
            sentiment=sentiment,
            risk_level=risk_level,
        )

        return response.model_dump()

    except OptionsDataError:
        raise
    except Exception as e:
        logger.error("Options summary failed for %s: %s", symbol, e)
        raise OptionsDataError(symbol, str(e))


# =============================================================================
# Tool 3: Vehicle Selection
# =============================================================================


async def options_vehicle_selection(
    symbol: str,
    timeframe: str = "swing",
    bias: str = "bullish",
    expected_move_percent: float = 3.0,
) -> dict[str, Any]:
    """Recommend stock vs options based on trade parameters.

    Uses the stock-first decision tree:
    1. Non-swing -> STOCK
    2. Move < 3% -> STOCK
    3. Medium vol -> Directional options
    4. High vol -> Spreads
    5. Low vol -> STOCK

    Args:
        symbol: Ticker symbol (for context logging).
        timeframe: Trading timeframe ('swing', 'day', 'scalp').
        bias: Directional bias ('bullish' or 'bearish').
        expected_move_percent: Expected price move percentage.

    Returns:
        Vehicle recommendation dictionary.
    """
    symbol = symbol.upper().strip()
    logger.info(
        "Vehicle selection for %s: tf=%s, bias=%s, move=%.1f%%",
        symbol,
        timeframe,
        bias,
        expected_move_percent,
    )

    tf = Timeframe(timeframe)

    # Determine volatility regime from real data
    vol_regime = await _fetch_volatility_regime(symbol)

    recommendation = _vehicle_selector.select(
        timeframe=tf,
        volatility_regime=vol_regime,
        bias=bias,
        expected_move_percent=expected_move_percent,
    )

    result = recommendation.model_dump()
    result["symbol"] = symbol
    result["volatility_regime"] = vol_regime.value
    result["timestamp"] = datetime.now().isoformat()

    return result


# =============================================================================
# Tool 4: Multi-Symbol Options Comparison
# =============================================================================


async def options_compare(
    symbols: list[str],
    metric: str = "iv",
) -> dict[str, Any]:
    """Compare options metrics across multiple symbols.

    Args:
        symbols: List of ticker symbols to compare.
        metric: Comparison metric ('iv', 'pcr', 'volume', 'liquidity').

    Returns:
        Comparison results sorted by metric.

    Raises:
        OptionsDataError: If no data available for any symbol.
    """
    logger.info("Comparing options for %s by %s", symbols, metric)

    comparisons: list[SymbolOptionsComparison] = []
    errors: list[str] = []

    # Fetch data for all symbols concurrently
    tasks = [_fetch_symbol_options_data(s.upper().strip()) for s in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for symbol, result in zip(symbols, results):
        if isinstance(result, Exception):
            logger.warning("Failed to fetch options for %s: %s", symbol, result)
            errors.append(f"{symbol}: {result}")
            continue
        comparisons.append(result)

    if not comparisons:
        raise OptionsDataError(
            ",".join(symbols), f"No options data for any symbol. Errors: {errors}"
        )

    # Sort by requested metric
    ranked_by = _sort_comparisons(comparisons, metric)

    response = MultiSymbolOptionsResponse(
        timestamp=datetime.now().isoformat(),
        metric=metric,
        symbols=comparisons,
        ranked_by=ranked_by,
    )

    return response.model_dump()


# =============================================================================
# Helper Functions
# =============================================================================


def _compute_pcr(
    calls: ChainAnalysis | None,
    puts: ChainAnalysis | None,
) -> PutCallRatio | None:
    """Compute Put/Call ratio from chain analyses."""
    if not calls or not puts:
        return None

    pcr_volume = None
    pcr_oi = None

    if calls.total_volume > 0:
        pcr_volume = puts.total_volume / calls.total_volume
    if calls.total_open_interest > 0:
        pcr_oi = puts.total_open_interest / calls.total_open_interest

    return PutCallRatio(volume=pcr_volume, open_interest=pcr_oi)


def _derive_sentiment(pcr: PutCallRatio | None) -> str:
    """Derive market sentiment from Put/Call ratio."""
    if pcr is None or pcr.volume is None:
        return "neutral"
    if pcr.volume > 1.5:
        return "bearish"
    if pcr.volume < 0.7:
        return "bullish"
    return "neutral"


def _derive_risk_level(
    calls: ChainAnalysis | None,
    puts: ChainAnalysis | None,
) -> str:
    """Derive risk level from implied volatility."""
    primary = calls or puts
    if primary is None:
        return "medium"

    if primary.avg_implied_volatility > 60:
        return "high"
    if primary.avg_implied_volatility < 20:
        return "low"
    return "medium"


async def _fetch_volatility_regime(symbol: str) -> VolatilityRegime:
    """Fetch current volatility regime for a symbol using ATR.

    Args:
        symbol: Ticker symbol.

    Returns:
        VolatilityRegime classification.
    """
    import yfinance as yf

    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1mo")

    if hist.empty or len(hist) < 14:
        return VolatilityRegime.MEDIUM

    # Calculate ATR
    high = hist["High"]
    low = hist["Low"]
    close = hist["Close"]

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=14).mean().iloc[-1]
    current_price = close.iloc[-1]

    atr_percent = (atr / current_price) * 100

    from .config import VOLATILITY_LOW_THRESHOLD, VOLATILITY_HIGH_THRESHOLD

    if atr_percent < VOLATILITY_LOW_THRESHOLD:
        return VolatilityRegime.LOW
    if atr_percent > VOLATILITY_HIGH_THRESHOLD:
        return VolatilityRegime.HIGH
    return VolatilityRegime.MEDIUM


async def _fetch_symbol_options_data(symbol: str) -> SymbolOptionsComparison:
    """Fetch options data for a single symbol for comparison.

    Args:
        symbol: Ticker symbol.

    Returns:
        SymbolOptionsComparison with key metrics.
    """
    ticker, current_price = _chain_analyzer.fetch_ticker_data(symbol)
    expirations = _chain_analyzer.get_expirations(ticker, symbol)
    selected_exp = _chain_analyzer.select_expiration(
        expirations, None, symbol, min_dte=SUMMARY_MIN_DTE,
    )
    calls_df, puts_df = _chain_analyzer.fetch_option_chain(ticker, selected_exp)

    calls_analysis = _chain_analyzer.analyze_chain(
        calls_df, current_price, DEFAULT_MIN_VOLUME, "calls"
    )
    puts_analysis = _chain_analyzer.analyze_chain(
        puts_df, current_price, DEFAULT_MIN_VOLUME, "puts"
    )

    pcr = _compute_pcr(calls_analysis, puts_analysis)

    total_volume = 0
    liquid_contracts = 0
    atm_iv = None

    if calls_analysis:
        total_volume += calls_analysis.total_volume
        liquid_contracts += calls_analysis.liquid_contracts
        atm_iv = calls_analysis.atm_iv
    if puts_analysis:
        total_volume += puts_analysis.total_volume
        liquid_contracts += puts_analysis.liquid_contracts

    return SymbolOptionsComparison(
        symbol=symbol,
        current_price=current_price,
        atm_iv=atm_iv,
        put_call_ratio=pcr.volume if pcr else None,
        total_volume=total_volume,
        liquid_contracts=liquid_contracts,
    )


def _sort_comparisons(
    comparisons: list[SymbolOptionsComparison], metric: str
) -> str:
    """Sort comparisons by metric and return ranking description.

    Sorts in-place and returns description of ranking.
    """
    if metric == "iv":
        comparisons.sort(key=lambda c: c.atm_iv or 0, reverse=True)
        return "Highest ATM implied volatility first"
    if metric == "pcr":
        comparisons.sort(key=lambda c: c.put_call_ratio or 0, reverse=True)
        return "Highest Put/Call ratio first (most bearish sentiment)"
    if metric == "volume":
        comparisons.sort(key=lambda c: c.total_volume, reverse=True)
        return "Highest total options volume first"
    if metric == "liquidity":
        comparisons.sort(key=lambda c: c.liquid_contracts, reverse=True)
        return "Most liquid contracts first"

    comparisons.sort(key=lambda c: c.atm_iv or 0, reverse=True)
    return "Highest ATM implied volatility first (default)"
