"""Vehicle selection logic: stock vs options.

Implements stock-first approach - default to stock trading, suggest options
only for swing trades with sufficient expected move and full suggestions
(DTE range, delta range, spread width).
"""

from ..config import (
    OPTION_MIN_EXPECTED_MOVE,
    OPTION_SWING_MIN_DTE,
    OPTION_SWING_MAX_DTE,
    OPTION_CALL_DELTA_MIN,
    OPTION_CALL_DELTA_MAX,
    OPTION_PUT_DELTA_MIN,
    OPTION_PUT_DELTA_MAX,
)
from ..models import (
    Timeframe,
    VolatilityRegime,
    Vehicle,
    VehicleRecommendation,
)


class VehicleSelector:
    """Selects trade vehicle (stock vs options) with full suggestions.

    Decision tree:
    1. Non-swing trades -> STOCK
    2. Expected move < 3% -> STOCK
    3. Medium volatility -> DIRECTIONAL OPTIONS (call/put)
    4. High volatility -> VERTICAL SPREADS
    5. Low volatility -> STOCK

    Args:
        min_move: Minimum expected % move for options consideration.
        swing_min_dte: Minimum DTE for swing options.
        swing_max_dte: Maximum DTE for swing options.
    """

    def __init__(
        self,
        min_move: float = OPTION_MIN_EXPECTED_MOVE,
        swing_min_dte: int = OPTION_SWING_MIN_DTE,
        swing_max_dte: int = OPTION_SWING_MAX_DTE,
    ):
        self._min_move = min_move
        self._swing_min_dte = swing_min_dte
        self._swing_max_dte = swing_max_dte

    def select(
        self,
        timeframe: Timeframe,
        volatility_regime: VolatilityRegime,
        bias: str,
        expected_move_percent: float,
    ) -> VehicleRecommendation:
        """Select appropriate trade vehicle.

        Args:
            timeframe: Selected trading timeframe.
            volatility_regime: Current volatility classification.
            bias: Trade bias ('bullish' or 'bearish').
            expected_move_percent: Expected price move percentage.

        Returns:
            VehicleRecommendation with full details.
        """
        # Rule 1: Non-swing trades use stock
        if timeframe != Timeframe.SWING:
            return VehicleRecommendation(
                vehicle=Vehicle.STOCK,
                reasoning=f"{timeframe.value} trades default to stock for liquidity",
            )

        # Rule 2: Small moves use stock
        if expected_move_percent < self._min_move:
            return VehicleRecommendation(
                vehicle=Vehicle.STOCK,
                reasoning=(
                    f"Expected move ({expected_move_percent:.1f}%) below "
                    f"{self._min_move}% threshold for options"
                ),
                expected_move_percent=expected_move_percent,
            )

        dte_range = (self._swing_min_dte, self._swing_max_dte)

        # Rule 3: Medium volatility -> directional options
        if volatility_regime == VolatilityRegime.MEDIUM:
            if bias == "bullish":
                return VehicleRecommendation(
                    vehicle=Vehicle.OPTION_CALL,
                    reasoning="Consider ATM calls for directional bullish play",
                    dte_range=dte_range,
                    delta_range=(OPTION_CALL_DELTA_MIN, OPTION_CALL_DELTA_MAX),
                    expected_move_percent=expected_move_percent,
                )
            return VehicleRecommendation(
                vehicle=Vehicle.OPTION_PUT,
                reasoning="Consider ATM puts for directional bearish play",
                dte_range=dte_range,
                delta_range=(OPTION_PUT_DELTA_MIN, OPTION_PUT_DELTA_MAX),
                expected_move_percent=expected_move_percent,
            )

        # Rule 4: High volatility -> spreads for defined risk
        if volatility_regime == VolatilityRegime.HIGH:
            if bias == "bullish":
                return VehicleRecommendation(
                    vehicle=Vehicle.OPTION_SPREAD,
                    reasoning=(
                        "High volatility suitable for spreads; "
                        "consider bull call spread for defined risk"
                    ),
                    dte_range=dte_range,
                    delta_range=(OPTION_CALL_DELTA_MIN, OPTION_CALL_DELTA_MAX),
                    spread_type="Bull Call Spread",
                    spread_width_info=(
                        f"Width typically 1x ATR equivalent for "
                        f"{expected_move_percent:.1f}% expected move"
                    ),
                    expected_move_percent=expected_move_percent,
                )
            return VehicleRecommendation(
                vehicle=Vehicle.OPTION_SPREAD,
                reasoning=(
                    "High volatility suitable for spreads; "
                    "consider bear put spread for defined risk"
                ),
                dte_range=dte_range,
                delta_range=(OPTION_PUT_DELTA_MIN, OPTION_PUT_DELTA_MAX),
                spread_type="Bear Put Spread",
                spread_width_info=(
                    f"Width typically 1x ATR equivalent for "
                    f"{expected_move_percent:.1f}% expected move"
                ),
                expected_move_percent=expected_move_percent,
            )

        # Rule 5: Low volatility -> stock
        return VehicleRecommendation(
            vehicle=Vehicle.STOCK,
            reasoning="Low volatility - options premiums too cheap, stock more efficient",
            expected_move_percent=expected_move_percent,
        )
