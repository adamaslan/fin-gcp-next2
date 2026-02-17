"""Options chain analysis using real yfinance data.

Analyzes calls/puts chains for volume, open interest, IV, and ATM metrics.
NEVER returns mock data - raises errors if data unavailable.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf

from ..config import (
    DEFAULT_MIN_DTE,
    MAX_EXPIRATIONS_RETURNED,
    TOP_STRIKES_LIMIT,
)
from ..models import (
    ChainAnalysis,
    TopVolumeStrike,
    TopOIStrike,
)

logger = logging.getLogger(__name__)


class OptionsDataError(Exception):
    """Raised when options data cannot be fetched or is invalid."""

    def __init__(self, symbol: str, detail: str):
        self.symbol = symbol
        self.detail = detail
        super().__init__(f"Options data error for {symbol}: {detail}")


class ChainAnalyzer:
    """Analyzes options chains from yfinance data.

    Fetches real market data and computes chain-level metrics.
    Never returns mock or synthetic data.
    """

    def fetch_ticker_data(
        self, symbol: str
    ) -> tuple[yf.Ticker, float]:
        """Fetch ticker object and current price.

        Args:
            symbol: Ticker symbol (e.g., AAPL).

        Returns:
            Tuple of (yfinance Ticker, current price).

        Raises:
            OptionsDataError: If ticker or price data unavailable.
        """
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)

        try:
            info = ticker.info
            current_price = info.get("currentPrice") or info.get(
                "regularMarketPrice", 0
            )
        except Exception:
            hist = ticker.history(period="1d")
            if hist.empty:
                raise OptionsDataError(symbol, "No price data available")
            current_price = float(hist["Close"].iloc[-1])

        if not current_price or current_price <= 0:
            raise OptionsDataError(symbol, "Invalid current price")

        return ticker, current_price

    def get_expirations(self, ticker: yf.Ticker, symbol: str) -> tuple[str, ...]:
        """Get available expiration dates.

        Args:
            ticker: yfinance Ticker object.
            symbol: Symbol for error messages.

        Returns:
            Tuple of expiration date strings.

        Raises:
            OptionsDataError: If no options data available.
        """
        expirations = ticker.options
        if not expirations:
            raise OptionsDataError(symbol, "No options data available for this symbol")
        return expirations

    def select_expiration(
        self,
        expirations: tuple[str, ...],
        requested: str | None,
        symbol: str,
        min_dte: int = DEFAULT_MIN_DTE,
    ) -> str:
        """Select the best expiration date, skipping near-zero DTE by default.

        Options expiring today (0 DTE) have extreme theta decay and gamma risk,
        making them unsuitable for most analysis. This method picks the nearest
        expiration that meets the minimum DTE requirement.

        Priority:
        1. User-requested date (always honored if available)
        2. Nearest expiration with at least min_dte days remaining
        3. Fallback to nearest available if all expirations are below min_dte

        Args:
            expirations: Available expiration dates (sorted nearest-first).
            requested: User-requested date (YYYY-MM-DD) or None for auto-select.
            symbol: Symbol for logging.
            min_dte: Minimum days to expiration (default from config).
                Set to 0 to allow same-day expiry.

        Returns:
            Selected expiration date string.
        """
        # Honor explicit user request
        if requested and requested in expirations:
            return requested

        if requested:
            logger.warning(
                "Requested expiration %s not found for %s, auto-selecting",
                requested,
                symbol,
            )

        today = datetime.now().date()

        # Find the nearest expiration that meets min_dte
        for exp in expirations:
            try:
                exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
                dte = (exp_date - today).days
                if dte >= min_dte:
                    if exp != expirations[0]:
                        logger.info(
                            "Skipped %d near-term expiration(s) for %s, "
                            "selected %s (%d DTE, min_dte=%d)",
                            expirations.index(exp),
                            symbol,
                            exp,
                            dte,
                            min_dte,
                        )
                    return exp
            except ValueError:
                continue

        # All expirations are below min_dte - fall back to the furthest out
        logger.warning(
            "All expirations for %s are under %d DTE, using furthest: %s",
            symbol,
            min_dte,
            expirations[-1],
        )
        return expirations[-1]

    def fetch_option_chain(
        self, ticker: yf.Ticker, expiration: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch calls and puts DataFrames for an expiration.

        Args:
            ticker: yfinance Ticker object.
            expiration: Expiration date string.

        Returns:
            Tuple of (calls_df, puts_df).
        """
        chain = ticker.option_chain(expiration)
        return chain.calls, chain.puts

    def analyze_chain(
        self,
        options_df: pd.DataFrame,
        current_price: float,
        min_volume: int,
        chain_type: str,
    ) -> ChainAnalysis | None:
        """Analyze a single option chain (calls or puts).

        Args:
            options_df: DataFrame with options data.
            current_price: Current stock price.
            min_volume: Minimum volume threshold for liquid options.
            chain_type: 'calls' or 'puts' for logging.

        Returns:
            ChainAnalysis or None if DataFrame is empty.
        """
        if options_df.empty:
            return None

        liquid_options = options_df[options_df["volume"] >= min_volume]

        # Core metrics
        total_volume = int(options_df["volume"].sum())
        total_oi = int(options_df["openInterest"].sum())
        avg_iv = float(options_df["impliedVolatility"].mean() * 100)
        max_iv = float(options_df["impliedVolatility"].max() * 100)
        min_iv = float(options_df["impliedVolatility"].min() * 100)

        # ATM option detection
        atm_strike = None
        atm_iv = None
        atm_delta = None

        if not liquid_options.empty:
            distance = (liquid_options["strike"] - current_price).abs()
            atm_idx = distance.argsort().iloc[:1]
            atm_row = liquid_options.iloc[atm_idx]

            if not atm_row.empty:
                atm_strike = float(atm_row["strike"].iloc[0])
                atm_iv = float(atm_row["impliedVolatility"].iloc[0] * 100)
                if "delta" in atm_row.columns:
                    delta_val = atm_row["delta"].iloc[0]
                    if not np.isnan(delta_val):
                        atm_delta = float(delta_val)

        # Top strikes by volume
        top_volume_strikes = self._top_by_volume(liquid_options)

        # Top strikes by open interest
        top_oi_strikes = self._top_by_oi(liquid_options)

        logger.info(
            "Analyzed %s chain: %d total, %d liquid, vol=%d, OI=%d, avg_iv=%.1f%%",
            chain_type,
            len(options_df),
            len(liquid_options),
            total_volume,
            total_oi,
            avg_iv,
        )

        return ChainAnalysis(
            total_contracts=len(options_df),
            liquid_contracts=len(liquid_options),
            total_volume=total_volume,
            total_open_interest=total_oi,
            avg_implied_volatility=avg_iv,
            max_iv=max_iv,
            min_iv=min_iv,
            atm_strike=atm_strike,
            atm_iv=atm_iv,
            atm_delta=atm_delta,
            top_volume_strikes=top_volume_strikes,
            top_oi_strikes=top_oi_strikes,
        )

    def _top_by_volume(
        self, liquid_options: pd.DataFrame
    ) -> list[TopVolumeStrike]:
        """Extract top strikes by volume.

        Args:
            liquid_options: Filtered DataFrame of liquid options.

        Returns:
            List of TopVolumeStrike models.
        """
        if liquid_options.empty:
            return []

        top = liquid_options.nlargest(TOP_STRIKES_LIMIT, "volume")[
            ["strike", "volume", "impliedVolatility"]
        ]
        return [
            TopVolumeStrike(
                strike=float(row["strike"]),
                volume=int(row["volume"]),
                iv=float(row["impliedVolatility"] * 100),
            )
            for _, row in top.iterrows()
        ]

    def _top_by_oi(
        self, liquid_options: pd.DataFrame
    ) -> list[TopOIStrike]:
        """Extract top strikes by open interest.

        Args:
            liquid_options: Filtered DataFrame of liquid options.

        Returns:
            List of TopOIStrike models.
        """
        if liquid_options.empty:
            return []

        top = liquid_options.nlargest(TOP_STRIKES_LIMIT, "openInterest")[
            ["strike", "openInterest", "impliedVolatility"]
        ]
        return [
            TopOIStrike(
                strike=float(row["strike"]),
                open_interest=int(row["openInterest"]),
                iv=float(row["impliedVolatility"] * 100),
            )
            for _, row in top.iterrows()
        ]
