"""Configuration and constants for Options MCP Backend.

Centralizes all configuration values for options analysis,
risk assessment, and vehicle selection.
"""

import os
from typing import Final


# =============================================================================
# Cache Configuration
# =============================================================================

CACHE_TTL_SECONDS: Final[int] = 300  # 5 minutes
CACHE_MAX_SIZE: Final[int] = 200  # Maximum symbols to cache


# =============================================================================
# Options Chain Analysis
# =============================================================================

# Volume thresholds for liquidity filtering
DEFAULT_MIN_VOLUME: Final[int] = 75
HIGH_LIQUIDITY_VOLUME: Final[int] = 500

# Maximum expirations to return in response
MAX_EXPIRATIONS_RETURNED: Final[int] = 10

# Top strikes to return per category
TOP_STRIKES_LIMIT: Final[int] = 5

# IV thresholds (as percentage)
IV_HIGH_THRESHOLD: Final[float] = 60.0  # Above = expensive options
IV_LOW_THRESHOLD: Final[float] = 20.0  # Below = cheap options

# Put/Call ratio thresholds
PCR_BEARISH_THRESHOLD: Final[float] = 1.5  # Above = bearish sentiment
PCR_BULLISH_THRESHOLD: Final[float] = 0.7  # Below = bullish sentiment

# Liquidity warning threshold (minimum liquid contracts)
LIQUIDITY_WARNING_CONTRACTS: Final[int] = 5

# DTE warning thresholds
DTE_SHORT_WARNING: Final[int] = 7  # High theta decay
DTE_LONG_OPPORTUNITY: Final[int] = 60  # Lower theta decay

# Smart DTE selection defaults (skip near-zero DTE by default)
# General analysis: skip anything under 7 days (avoids extreme theta decay)
DEFAULT_MIN_DTE: Final[int] = 7
# Quick summaries: just skip 0 DTE (expiring today is rarely useful)
SUMMARY_MIN_DTE: Final[int] = 1
# Spread trade minimum: at least 1 day to avoid same-day expiry
SPREAD_MIN_DTE: Final[int] = 1


# =============================================================================
# Vehicle Selection (Stock vs Options)
# =============================================================================

# Minimum expected move percentage to consider options
OPTION_MIN_EXPECTED_MOVE: Final[float] = 3.0  # 3%

# DTE range for swing trade options
OPTION_SWING_MIN_DTE: Final[int] = 30
OPTION_SWING_MAX_DTE: Final[int] = 45

# Delta ranges
OPTION_CALL_DELTA_MIN: Final[float] = 0.40
OPTION_CALL_DELTA_MAX: Final[float] = 0.60
OPTION_PUT_DELTA_MIN: Final[float] = -0.60
OPTION_PUT_DELTA_MAX: Final[float] = -0.40

# Spread width as ATR multiple
OPTION_SPREAD_WIDTH_ATR: Final[float] = 1.0


# =============================================================================
# Volatility Regime Thresholds (ATR as % of price)
# =============================================================================

VOLATILITY_LOW_THRESHOLD: Final[float] = 1.5  # < 1.5% = LOW
VOLATILITY_HIGH_THRESHOLD: Final[float] = 3.0  # > 3.0% = HIGH


# =============================================================================
# Risk Assessment
# =============================================================================

# Risk-to-Reward requirements
MIN_RR_RATIO: Final[float] = 1.5
PREFERRED_RR_RATIO: Final[float] = 2.0

# Maximum open interest concentration (single strike vs total)
OI_CONCENTRATION_WARNING: Final[float] = 0.30  # 30% of total OI in one strike

# IV skew thresholds
IV_SKEW_SIGNIFICANT: Final[float] = 10.0  # Percentage points between ATM put/call IV

# Unusual activity thresholds
UNUSUAL_VOLUME_RATIO: Final[float] = 3.0  # Volume > 3x open interest
UNUSUAL_OI_CHANGE: Final[float] = 0.50  # 50% change in OI day-over-day


# =============================================================================
# API Configuration
# =============================================================================

GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: Final[str] = "gemini-2.0-flash"

# GCP Project
GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "ttb-lang1")

# Server
DEFAULT_PORT: Final[int] = int(os.getenv("PORT", "8080"))
