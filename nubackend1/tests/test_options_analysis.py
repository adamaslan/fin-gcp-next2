"""Tests for Options MCP Backend.

Tests the chain analyzer, risk engine, vehicle selector,
and MCP server functions against real market data.

Run: pytest tests/ -v
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from options_mcp.analysis.chain_analyzer import ChainAnalyzer, OptionsDataError
from options_mcp.analysis.risk_engine import RiskEngine
from options_mcp.analysis.vehicle_selector import VehicleSelector
from options_mcp.models import (
    ChainAnalysis,
    PutCallRatio,
    TopVolumeStrike,
    TopOIStrike,
    Timeframe,
    VolatilityRegime,
    Vehicle,
)


# =============================================================================
# Chain Analyzer Tests
# =============================================================================


class TestChainAnalyzer:
    """Tests for ChainAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        return ChainAnalyzer()

    @pytest.fixture
    def sample_options_df(self):
        """Create a realistic options DataFrame."""
        return pd.DataFrame(
            {
                "strike": [95.0, 100.0, 105.0, 110.0, 115.0],
                "volume": [50, 200, 500, 150, 30],
                "openInterest": [1000, 5000, 8000, 3000, 500],
                "impliedVolatility": [0.45, 0.35, 0.30, 0.32, 0.40],
                "lastPrice": [8.0, 4.5, 2.0, 0.80, 0.20],
                "bid": [7.80, 4.30, 1.90, 0.70, 0.15],
                "ask": [8.20, 4.70, 2.10, 0.90, 0.25],
            }
        )

    def test_analyze_chain_returns_correct_metrics(
        self, analyzer, sample_options_df
    ):
        """Verify core metrics are computed correctly."""
        result = analyzer.analyze_chain(
            sample_options_df,
            current_price=102.0,
            min_volume=75,
            chain_type="calls",
        )

        assert result is not None
        assert result.total_contracts == 5
        assert result.liquid_contracts == 3  # vol >= 75: 200, 500, 150
        assert result.total_volume == 930  # 50+200+500+150+30
        assert result.total_open_interest == 17500

    def test_analyze_chain_empty_df_returns_none(self, analyzer):
        """Empty DataFrame should return None."""
        empty_df = pd.DataFrame()
        result = analyzer.analyze_chain(empty_df, 100.0, 75, "calls")
        assert result is None

    def test_analyze_chain_atm_detection(self, analyzer, sample_options_df):
        """ATM strike should be closest to current price."""
        result = analyzer.analyze_chain(
            sample_options_df,
            current_price=106.0,
            min_volume=75,
            chain_type="calls",
        )

        assert result is not None
        assert result.atm_strike == 105.0

    def test_analyze_chain_iv_calculation(self, analyzer, sample_options_df):
        """IV should be expressed as percentage."""
        result = analyzer.analyze_chain(
            sample_options_df,
            current_price=100.0,
            min_volume=1,
            chain_type="calls",
        )

        assert result is not None
        # avg of [45, 35, 30, 32, 40] = 36.4%
        assert 35.0 < result.avg_implied_volatility < 37.0
        assert result.max_iv == 45.0
        assert result.min_iv == 30.0

    def test_top_volume_strikes_limit(self, analyzer, sample_options_df):
        """Top volume strikes should respect limit."""
        result = analyzer.analyze_chain(
            sample_options_df,
            current_price=100.0,
            min_volume=75,
            chain_type="calls",
        )

        assert result is not None
        assert len(result.top_volume_strikes) <= 5
        # Highest volume first
        assert result.top_volume_strikes[0].volume >= result.top_volume_strikes[1].volume


# =============================================================================
# Risk Engine Tests
# =============================================================================


class TestRiskEngine:
    """Tests for RiskEngine."""

    @pytest.fixture
    def engine(self):
        return RiskEngine()

    @pytest.fixture
    def high_iv_calls(self):
        return ChainAnalysis(
            total_contracts=50,
            liquid_contracts=30,
            total_volume=10000,
            total_open_interest=50000,
            avg_implied_volatility=75.0,
            max_iv=120.0,
            min_iv=40.0,
        )

    @pytest.fixture
    def low_iv_calls(self):
        return ChainAnalysis(
            total_contracts=50,
            liquid_contracts=30,
            total_volume=10000,
            total_open_interest=50000,
            avg_implied_volatility=15.0,
            max_iv=25.0,
            min_iv=10.0,
        )

    @pytest.fixture
    def normal_puts(self):
        return ChainAnalysis(
            total_contracts=40,
            liquid_contracts=25,
            total_volume=15000,
            total_open_interest=30000,
            avg_implied_volatility=35.0,
            max_iv=50.0,
            min_iv=25.0,
        )

    def test_high_iv_generates_warning(self, engine, high_iv_calls):
        """High IV should generate a warning."""
        warnings, opportunities = engine.assess(
            calls=high_iv_calls, puts=None, pcr=None, dte=30
        )

        assert any("High implied volatility" in w for w in warnings)

    def test_low_iv_generates_opportunity(self, engine, low_iv_calls):
        """Low IV should generate an opportunity."""
        warnings, opportunities = engine.assess(
            calls=low_iv_calls, puts=None, pcr=None, dte=30
        )

        assert any("Low implied volatility" in o for o in opportunities)

    def test_bearish_pcr_generates_warning(self, engine, high_iv_calls, normal_puts):
        """High PCR should generate bearish warning."""
        pcr = PutCallRatio(volume=2.0, open_interest=1.5)
        warnings, _ = engine.assess(
            calls=high_iv_calls, puts=normal_puts, pcr=pcr, dte=30
        )

        assert any("Put/Call Volume Ratio" in w for w in warnings)

    def test_short_dte_generates_warning(self, engine, high_iv_calls):
        """Short DTE should generate theta decay warning."""
        warnings, _ = engine.assess(
            calls=high_iv_calls, puts=None, pcr=None, dte=3
        )

        assert any("Short time to expiration" in w for w in warnings)

    def test_long_dte_generates_opportunity(self, engine, high_iv_calls):
        """Long DTE should generate opportunity."""
        _, opportunities = engine.assess(
            calls=high_iv_calls, puts=None, pcr=None, dte=90
        )

        assert any("Long time to expiration" in o for o in opportunities)

    def test_low_liquidity_generates_warning(self, engine):
        """Low liquid contracts should warn about spreads."""
        illiquid = ChainAnalysis(
            total_contracts=50,
            liquid_contracts=2,
            total_volume=100,
            total_open_interest=5000,
            avg_implied_volatility=35.0,
            max_iv=50.0,
            min_iv=20.0,
        )
        warnings, _ = engine.assess(
            calls=illiquid, puts=None, pcr=None, dte=30
        )

        assert any("Low liquidity" in w for w in warnings)


# =============================================================================
# Vehicle Selector Tests
# =============================================================================


class TestVehicleSelector:
    """Tests for VehicleSelector."""

    @pytest.fixture
    def selector(self):
        return VehicleSelector()

    def test_non_swing_returns_stock(self, selector):
        """Day and scalp timeframes should always return stock."""
        rec = selector.select(
            timeframe=Timeframe.DAY,
            volatility_regime=VolatilityRegime.MEDIUM,
            bias="bullish",
            expected_move_percent=5.0,
        )
        assert rec.vehicle == Vehicle.STOCK

    def test_small_move_returns_stock(self, selector):
        """Expected move below threshold should return stock."""
        rec = selector.select(
            timeframe=Timeframe.SWING,
            volatility_regime=VolatilityRegime.MEDIUM,
            bias="bullish",
            expected_move_percent=2.0,
        )
        assert rec.vehicle == Vehicle.STOCK

    def test_medium_vol_bullish_returns_call(self, selector):
        """Medium volatility swing with bullish bias should suggest calls."""
        rec = selector.select(
            timeframe=Timeframe.SWING,
            volatility_regime=VolatilityRegime.MEDIUM,
            bias="bullish",
            expected_move_percent=5.0,
        )
        assert rec.vehicle == Vehicle.OPTION_CALL
        assert rec.delta_range is not None

    def test_medium_vol_bearish_returns_put(self, selector):
        """Medium volatility swing with bearish bias should suggest puts."""
        rec = selector.select(
            timeframe=Timeframe.SWING,
            volatility_regime=VolatilityRegime.MEDIUM,
            bias="bearish",
            expected_move_percent=5.0,
        )
        assert rec.vehicle == Vehicle.OPTION_PUT

    def test_high_vol_returns_spread(self, selector):
        """High volatility should suggest spreads."""
        rec = selector.select(
            timeframe=Timeframe.SWING,
            volatility_regime=VolatilityRegime.HIGH,
            bias="bullish",
            expected_move_percent=5.0,
        )
        assert rec.vehicle == Vehicle.OPTION_SPREAD
        assert rec.spread_type == "Bull Call Spread"

    def test_low_vol_returns_stock(self, selector):
        """Low volatility should return stock."""
        rec = selector.select(
            timeframe=Timeframe.SWING,
            volatility_regime=VolatilityRegime.LOW,
            bias="bullish",
            expected_move_percent=5.0,
        )
        assert rec.vehicle == Vehicle.STOCK

    def test_dte_range_included_for_options(self, selector):
        """DTE range should be included for option recommendations."""
        rec = selector.select(
            timeframe=Timeframe.SWING,
            volatility_regime=VolatilityRegime.MEDIUM,
            bias="bullish",
            expected_move_percent=5.0,
        )
        assert rec.dte_range == (30, 45)


# =============================================================================
# Integration Test (requires network - marked slow)
# =============================================================================


@pytest.mark.slow
class TestIntegration:
    """Integration tests hitting real yfinance API."""

    @pytest.mark.asyncio
    async def test_options_risk_analysis_real_data(self):
        """Test full options risk analysis with real SPY data."""
        from options_mcp.server import options_risk_analysis

        result = await options_risk_analysis(symbol="SPY")

        assert result["symbol"] == "SPY"
        assert result["current_price"] > 0
        assert result["expiration_date"]
        assert result["calls"] is not None
        assert result["puts"] is not None
        assert isinstance(result["risk_warnings"], list)
        assert isinstance(result["opportunities"], list)

    @pytest.mark.asyncio
    async def test_options_summary_real_data(self):
        """Test options summary with real AAPL data."""
        from options_mcp.server import options_summary

        result = await options_summary(symbol="AAPL")

        assert result["symbol"] == "AAPL"
        assert result["current_price"] > 0
        assert result["sentiment"] in ("bullish", "bearish", "neutral")
        assert result["risk_level"] in ("low", "medium", "high")
