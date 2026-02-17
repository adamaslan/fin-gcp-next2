"""Pydantic models for Options MCP Backend.

Request models, response models, and domain types for options analysis.
All response models are frozen (immutable) for thread safety.
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Domain Enums
# =============================================================================


class OptionType(str, Enum):
    """Option type filter."""

    CALLS = "calls"
    PUTS = "puts"
    BOTH = "both"


class Timeframe(str, Enum):
    """Active trading timeframe."""

    SWING = "swing"  # 2-10 days
    DAY = "day"  # Intraday
    SCALP = "scalp"  # Minutes to hours


class VolatilityRegime(str, Enum):
    """Current volatility classification."""

    LOW = "low"  # ATR < 1.5% of price
    MEDIUM = "medium"  # ATR 1.5-3% of price
    HIGH = "high"  # ATR > 3% of price


class Vehicle(str, Enum):
    """Trade expression vehicle."""

    STOCK = "stock"
    OPTION_CALL = "option_call"
    OPTION_PUT = "option_put"
    OPTION_SPREAD = "option_spread"


class Bias(str, Enum):
    """Directional bias for the trade."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


# =============================================================================
# Request Models
# =============================================================================


class OptionsRiskRequest(BaseModel):
    """Request for options risk analysis."""

    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, SPY)")
    expiration_date: str | None = Field(
        None, description="Specific expiration date (YYYY-MM-DD). Defaults to nearest."
    )
    option_type: OptionType = Field(
        OptionType.BOTH, description="Option type: calls, puts, or both"
    )
    min_volume: int = Field(75, ge=1, description="Minimum volume for liquidity filter")


class OptionsChainRequest(BaseModel):
    """Request for raw options chain data."""

    symbol: str = Field(..., description="Stock symbol")
    expiration_date: str | None = Field(
        None, description="Specific expiration date (YYYY-MM-DD)"
    )


class OptionsSummaryRequest(BaseModel):
    """Request for quick options summary."""

    symbol: str = Field(..., description="Stock symbol")


class VehicleSelectionRequest(BaseModel):
    """Request for vehicle selection recommendation."""

    symbol: str = Field(..., description="Stock symbol")
    timeframe: Timeframe = Field(Timeframe.SWING, description="Trading timeframe")
    bias: Bias = Field(..., description="Directional bias")
    expected_move_percent: float = Field(
        ..., ge=0, description="Expected price move percentage"
    )


class MultiSymbolOptionsRequest(BaseModel):
    """Request for multi-symbol options comparison."""

    symbols: list[str] = Field(
        ..., min_length=2, max_length=10, description="Symbols to compare"
    )
    metric: str = Field(
        "iv", description="Comparison metric: iv, pcr, volume, liquidity"
    )


# =============================================================================
# Response Models (Frozen/Immutable)
# =============================================================================


class StrikeData(BaseModel):
    """Data for a single strike price."""

    model_config = ConfigDict(frozen=True)

    strike: float
    volume: int
    open_interest: int
    implied_volatility: float  # Percentage
    bid: float | None = None
    ask: float | None = None
    last_price: float | None = None


class TopVolumeStrike(BaseModel):
    """Top strike by volume."""

    model_config = ConfigDict(frozen=True)

    strike: float
    volume: int
    iv: float  # Percentage


class TopOIStrike(BaseModel):
    """Top strike by open interest."""

    model_config = ConfigDict(frozen=True)

    strike: float
    open_interest: int
    iv: float  # Percentage


class ChainAnalysis(BaseModel):
    """Analysis of a single option chain (calls or puts)."""

    model_config = ConfigDict(frozen=True)

    total_contracts: int
    liquid_contracts: int
    total_volume: int
    total_open_interest: int
    avg_implied_volatility: float  # Percentage
    max_iv: float  # Percentage
    min_iv: float  # Percentage
    atm_strike: float | None = None
    atm_iv: float | None = None
    atm_delta: float | None = None
    top_volume_strikes: list[TopVolumeStrike] = Field(default_factory=list)
    top_oi_strikes: list[TopOIStrike] = Field(default_factory=list)


class PutCallRatio(BaseModel):
    """Put/Call ratio metrics."""

    model_config = ConfigDict(frozen=True)

    volume: float | None = None
    open_interest: float | None = None


class OptionsRiskResponse(BaseModel):
    """Full options risk analysis response."""

    model_config = ConfigDict(frozen=True)

    symbol: str
    timestamp: str
    current_price: float
    expiration_date: str
    days_to_expiration: int
    available_expirations: list[str] = Field(default_factory=list)
    calls: ChainAnalysis | None = None
    puts: ChainAnalysis | None = None
    put_call_ratio: PutCallRatio | None = None
    risk_warnings: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    liquidity_threshold: int


class OptionsSummaryResponse(BaseModel):
    """Quick options summary for a symbol."""

    model_config = ConfigDict(frozen=True)

    symbol: str
    timestamp: str
    current_price: float
    nearest_expiration: str
    days_to_expiration: int
    atm_call_iv: float | None = None
    atm_put_iv: float | None = None
    put_call_ratio_volume: float | None = None
    total_call_volume: int = 0
    total_put_volume: int = 0
    sentiment: str  # "bullish", "bearish", "neutral"
    risk_level: str  # "low", "medium", "high"


class VehicleRecommendation(BaseModel):
    """Vehicle selection recommendation."""

    model_config = ConfigDict(frozen=True)

    vehicle: Vehicle
    reasoning: str | None = None
    dte_range: tuple[int, int] | None = None
    delta_range: tuple[float, float] | None = None
    spread_type: str | None = None
    spread_width_info: str | None = None
    expected_move_percent: float | None = None


class SymbolOptionsComparison(BaseModel):
    """Options metrics for a single symbol in a comparison."""

    model_config = ConfigDict(frozen=True)

    symbol: str
    current_price: float
    atm_iv: float | None = None
    put_call_ratio: float | None = None
    total_volume: int = 0
    liquid_contracts: int = 0


class UnusualContract(BaseModel):
    """Contract with unusual volume relative to open interest."""

    model_config = ConfigDict(frozen=True)

    strike: float
    volume: int
    open_interest: int
    vol_oi_ratio: float
    option_type: str  # "call" or "put"


class SpreadOpportunity(BaseModel):
    """Vertical spread opportunity identified from the chain."""

    model_config = ConfigDict(frozen=True)

    buy_strike: float
    sell_strike: float
    spread_width: float
    max_cost: float | None = None
    max_profit: float | None = None
    option_type: str  # "call" or "put"


class EnhancedFields(BaseModel):
    """Enhanced options analysis fields computed from chain data.

    Adds iv_rank, max_pain, unusual_activity, greeks_exposure,
    and spread_opportunities beyond the base risk analysis.
    """

    model_config = ConfigDict(frozen=True)

    iv_rank: float | None = Field(
        None, description="IV rank 0-100 percentile within the expiration"
    )
    max_pain: float | None = Field(
        None, description="Strike where most options expire worthless"
    )
    unusual_activity: list[UnusualContract] = Field(
        default_factory=list,
        description="Contracts with volume > 3x open interest",
    )
    greeks_exposure: dict[str, float] = Field(
        default_factory=dict,
        description="Aggregate delta/gamma/vega across the chain",
    )
    spread_opportunities: list[SpreadOpportunity] = Field(
        default_factory=list,
        description="Top vertical spreads by risk/reward",
    )


class MultiSymbolOptionsResponse(BaseModel):
    """Multi-symbol options comparison response."""

    model_config = ConfigDict(frozen=True)

    timestamp: str
    metric: str
    symbols: list[SymbolOptionsComparison] = Field(default_factory=list)
    ranked_by: str  # Description of ranking
