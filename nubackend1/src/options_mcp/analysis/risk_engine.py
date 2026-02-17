"""Risk assessment engine for options analysis.

Generates risk warnings and opportunities based on chain analysis metrics.
Uses configurable thresholds from config.py.
"""

import logging

from ..config import (
    IV_HIGH_THRESHOLD,
    IV_LOW_THRESHOLD,
    PCR_BEARISH_THRESHOLD,
    PCR_BULLISH_THRESHOLD,
    LIQUIDITY_WARNING_CONTRACTS,
    DTE_SHORT_WARNING,
    DTE_LONG_OPPORTUNITY,
    OI_CONCENTRATION_WARNING,
    UNUSUAL_VOLUME_RATIO,
    IV_SKEW_SIGNIFICANT,
)
from ..models import ChainAnalysis, PutCallRatio

logger = logging.getLogger(__name__)


class RiskEngine:
    """Evaluates risk warnings and opportunities from options data.

    Stateless engine that takes analysis results and produces
    actionable risk assessments.
    """

    def assess(
        self,
        calls: ChainAnalysis | None,
        puts: ChainAnalysis | None,
        pcr: PutCallRatio | None,
        dte: int,
    ) -> tuple[list[str], list[str]]:
        """Run full risk assessment on analyzed options data.

        Args:
            calls: Calls chain analysis (None if not requested).
            puts: Puts chain analysis (None if not requested).
            pcr: Put/Call ratio metrics.
            dte: Days to expiration.

        Returns:
            Tuple of (risk_warnings, opportunities).
        """
        warnings: list[str] = []
        opportunities: list[str] = []

        self._assess_iv(calls, puts, warnings, opportunities)
        self._assess_pcr(pcr, warnings, opportunities)
        self._assess_liquidity(calls, puts, warnings)
        self._assess_dte(dte, warnings, opportunities)
        self._assess_iv_skew(calls, puts, warnings, opportunities)
        self._assess_oi_concentration(calls, puts, warnings)
        self._assess_unusual_activity(calls, puts, warnings, opportunities)

        logger.info(
            "Risk assessment: %d warnings, %d opportunities",
            len(warnings),
            len(opportunities),
        )

        return warnings, opportunities

    def _assess_iv(
        self,
        calls: ChainAnalysis | None,
        puts: ChainAnalysis | None,
        warnings: list[str],
        opportunities: list[str],
    ) -> None:
        """Assess implied volatility levels."""
        # Use calls IV as primary, fall back to puts
        primary = calls or puts
        if primary is None:
            return

        avg_iv = primary.avg_implied_volatility

        if avg_iv > IV_HIGH_THRESHOLD:
            warnings.append(
                f"High implied volatility ({avg_iv:.1f}%) - "
                "options are expensive, consider selling strategies or spreads"
            )
        elif avg_iv < IV_LOW_THRESHOLD:
            opportunities.append(
                f"Low implied volatility ({avg_iv:.1f}%) - "
                "options are cheap, consider buying strategies"
            )

    def _assess_pcr(
        self,
        pcr: PutCallRatio | None,
        warnings: list[str],
        opportunities: list[str],
    ) -> None:
        """Assess Put/Call ratio sentiment."""
        if pcr is None or pcr.volume is None:
            return

        if pcr.volume > PCR_BEARISH_THRESHOLD:
            warnings.append(
                f"High Put/Call Volume Ratio ({pcr.volume:.2f}) - "
                "bearish sentiment, heavy put buying"
            )
        elif pcr.volume < PCR_BULLISH_THRESHOLD:
            opportunities.append(
                f"Low Put/Call Volume Ratio ({pcr.volume:.2f}) - "
                "bullish sentiment, heavy call buying"
            )

    def _assess_liquidity(
        self,
        calls: ChainAnalysis | None,
        puts: ChainAnalysis | None,
        warnings: list[str],
    ) -> None:
        """Assess liquidity conditions."""
        if calls and calls.liquid_contracts < LIQUIDITY_WARNING_CONTRACTS:
            warnings.append(
                f"Low liquidity in calls ({calls.liquid_contracts} liquid contracts) - "
                "wide bid-ask spreads likely"
            )
        if puts and puts.liquid_contracts < LIQUIDITY_WARNING_CONTRACTS:
            warnings.append(
                f"Low liquidity in puts ({puts.liquid_contracts} liquid contracts) - "
                "wide bid-ask spreads likely"
            )

    def _assess_dte(
        self,
        dte: int,
        warnings: list[str],
        opportunities: list[str],
    ) -> None:
        """Assess days to expiration impact."""
        if dte < DTE_SHORT_WARNING:
            warnings.append(
                f"Short time to expiration ({dte} days) - "
                "high theta decay, rapid price movement needed"
            )
        elif dte > DTE_LONG_OPPORTUNITY:
            opportunities.append(
                f"Long time to expiration ({dte} days) - "
                "lower theta decay, suitable for longer-term positions"
            )

    def _assess_iv_skew(
        self,
        calls: ChainAnalysis | None,
        puts: ChainAnalysis | None,
        warnings: list[str],
        opportunities: list[str],
    ) -> None:
        """Assess IV skew between calls and puts ATM strikes."""
        if not calls or not puts:
            return
        if calls.atm_iv is None or puts.atm_iv is None:
            return

        skew = puts.atm_iv - calls.atm_iv

        if abs(skew) > IV_SKEW_SIGNIFICANT:
            if skew > 0:
                warnings.append(
                    f"Significant put skew ({skew:.1f}pp) - "
                    "demand for downside protection elevated"
                )
            else:
                opportunities.append(
                    f"Significant call skew ({abs(skew):.1f}pp) - "
                    "upside positioning favored by options market"
                )

    def _assess_oi_concentration(
        self,
        calls: ChainAnalysis | None,
        puts: ChainAnalysis | None,
        warnings: list[str],
    ) -> None:
        """Assess open interest concentration at single strikes."""
        for chain, label in [(calls, "calls"), (puts, "puts")]:
            if chain is None or chain.total_open_interest == 0:
                continue
            if not chain.top_oi_strikes:
                continue

            max_oi = chain.top_oi_strikes[0].open_interest
            concentration = max_oi / chain.total_open_interest

            if concentration > OI_CONCENTRATION_WARNING:
                warnings.append(
                    f"High OI concentration in {label} at "
                    f"${chain.top_oi_strikes[0].strike:.0f} strike "
                    f"({concentration:.0%} of total) - potential pin risk"
                )

    def _assess_unusual_activity(
        self,
        calls: ChainAnalysis | None,
        puts: ChainAnalysis | None,
        warnings: list[str],
        opportunities: list[str],
    ) -> None:
        """Assess unusual volume vs open interest ratios."""
        for chain, label in [(calls, "calls"), (puts, "puts")]:
            if chain is None or chain.total_open_interest == 0:
                continue

            vol_oi_ratio = chain.total_volume / chain.total_open_interest

            if vol_oi_ratio > UNUSUAL_VOLUME_RATIO:
                opportunities.append(
                    f"Unusual {label} activity - volume/OI ratio {vol_oi_ratio:.1f}x "
                    "suggests new positioning"
                )
