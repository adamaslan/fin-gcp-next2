"""Gemini AI Analyzer for Options Analysis.

Provides natural language insights for options risk analysis, enhanced fields,
vehicle selection, and summary data. Uses Gemini to synthesize chain metrics
into actionable trading guidance.
"""

import json
import logging
import os
from typing import Any

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ..config import GEMINI_MODEL

logger = logging.getLogger(__name__)


class OptionsAIAnalyzer:
    """Use Gemini to analyze and explain options analysis outputs.

    Generates natural language insights from risk analysis, enhanced fields,
    vehicle recommendations, and summary data.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize Gemini AI analyzer.

        Args:
            api_key: Gemini API key. Falls back to GEMINI_API_KEY env var.

        Raises:
            ImportError: If google-generativeai not installed.
            ValueError: If no API key provided.
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai not installed. "
                "Install with: mamba install -c conda-forge google-generativeai"
            )

        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY not set")

        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info("Options AI Analyzer initialized with %s", GEMINI_MODEL)

    def analyze_options_output(
        self,
        symbol: str,
        sym_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Run comprehensive AI analysis on all options data for a symbol.

        Combines risk analysis, enhanced fields, summary, and vehicle
        recommendation into a single AI prompt for holistic insights.

        Args:
            symbol: Ticker symbol.
            sym_result: Full per-symbol analysis dict from OptionsAnalysisRunner.

        Returns:
            Parsed AI analysis dict with actionable insights.
        """
        prompt = self._build_comprehensive_prompt(symbol, sym_result)
        response = self._model.generate_content(prompt)
        return self._parse_ai_response(response.text)

    def analyze_risk_output(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze options risk analysis output specifically.

        Args:
            result: Risk analysis tool output dict.

        Returns:
            AI-enhanced result with analysis added.
        """
        prompt = self._build_risk_prompt(result)
        response = self._model.generate_content(prompt)
        ai_analysis = self._parse_ai_response(response.text)

        enhanced = result.copy()
        enhanced["ai_analysis"] = ai_analysis
        return enhanced

    def _build_comprehensive_prompt(
        self,
        symbol: str,
        sym_result: dict[str, Any],
    ) -> str:
        """Build a comprehensive prompt combining all analysis outputs.

        Args:
            symbol: Ticker symbol.
            sym_result: Full per-symbol analysis dict.

        Returns:
            Prompt string for Gemini.
        """
        prompt = f"""You are an expert options trader and risk analyst. Analyze this comprehensive options data for {symbol} and provide actionable trading insights.

# SYMBOL: {symbol}

"""
        # Risk Analysis section
        risk = sym_result.get("risk_analysis", {})
        if risk.get("status") == "ok" and risk.get("data"):
            rd = risk["data"]
            prompt += f"""# RISK ANALYSIS
- Current Price: ${rd.get('current_price', 0):.2f}
- Expiration: {rd.get('expiration_date', 'N/A')}
- DTE: {rd.get('days_to_expiration', 0)}
"""
            calls = rd.get("calls")
            if calls:
                prompt += f"""
## Calls
- Liquid Contracts: {calls.get('liquid_contracts', 0)}
- Total Volume: {calls.get('total_volume', 0):,}
- Avg IV: {calls.get('avg_implied_volatility', 0):.1f}%
- ATM Strike: ${calls.get('atm_strike', 0):.2f}
- ATM IV: {calls.get('atm_iv', 0):.1f}%
"""
            puts = rd.get("puts")
            if puts:
                prompt += f"""
## Puts
- Liquid Contracts: {puts.get('liquid_contracts', 0)}
- Total Volume: {puts.get('total_volume', 0):,}
- Avg IV: {puts.get('avg_implied_volatility', 0):.1f}%
- ATM Strike: ${puts.get('atm_strike', 0):.2f}
- ATM IV: {puts.get('atm_iv', 0):.1f}%
"""
            pcr = rd.get("put_call_ratio")
            if pcr:
                prompt += f"""
## Put/Call Ratio
- Volume: {pcr.get('volume', 'N/A')}
- Open Interest: {pcr.get('open_interest', 'N/A')}
"""
            warnings = rd.get("risk_warnings", [])
            if warnings:
                prompt += "\n## Risk Warnings\n"
                for w in warnings:
                    prompt += f"- {w}\n"

            opps = rd.get("opportunities", [])
            if opps:
                prompt += "\n## Opportunities\n"
                for o in opps:
                    prompt += f"- {o}\n"

        # Summary section
        summary = sym_result.get("summary", {})
        if summary.get("status") == "ok" and summary.get("data"):
            sd = summary["data"]
            prompt += f"""
# SUMMARY
- Sentiment: {sd.get('sentiment', 'N/A')}
- Risk Level: {sd.get('risk_level', 'N/A')}
- Total Call Volume: {sd.get('total_call_volume', 0):,}
- Total Put Volume: {sd.get('total_put_volume', 0):,}
"""

        # Enhanced Fields section
        enhanced = sym_result.get("enhanced_fields", {})
        if enhanced.get("status") == "ok" and enhanced.get("data"):
            ed = enhanced["data"]
            prompt += f"""
# ENHANCED ANALYSIS
- IV Rank: {ed.get('iv_rank', 'N/A')}
- Max Pain: ${ed.get('max_pain', 0):.2f}
"""
            unusual = ed.get("unusual_activity", [])
            if unusual:
                prompt += "\n## Unusual Activity\n"
                for u in unusual[:5]:
                    prompt += (
                        f"- {u['option_type'].upper()} ${u['strike']:.2f}: "
                        f"vol={u['volume']:,}, OI={u['open_interest']:,}, "
                        f"ratio={u['vol_oi_ratio']:.1f}x\n"
                    )

            greeks = ed.get("greeks_exposure", {})
            if greeks:
                prompt += "\n## Greeks Exposure\n"
                for g, v in greeks.items():
                    prompt += f"- {g.capitalize()}: {v:.4f}\n"

            spreads = ed.get("spread_opportunities", [])
            if spreads:
                prompt += "\n## Spread Opportunities\n"
                for s in spreads:
                    prompt += (
                        f"- {s['option_type'].upper()} ${s['buy_strike']:.2f}/"
                        f"${s['sell_strike']:.2f} "
                        f"(cost=${s.get('max_cost', 0):.2f}, "
                        f"profit=${s.get('max_profit', 0):.2f})\n"
                    )

        # Vehicle Recommendation section
        vehicle = sym_result.get("vehicle_recommendation", {})
        if vehicle.get("status") == "ok" and vehicle.get("data"):
            vd = vehicle["data"]
            prompt += f"""
# VEHICLE RECOMMENDATION
- Vehicle: {vd.get('vehicle', 'N/A')}
- Reasoning: {vd.get('reasoning', 'N/A')}
- Volatility Regime: {vd.get('volatility_regime', 'N/A')}
"""

        prompt += """

# YOUR TASK

Provide a comprehensive options trading analysis in JSON format:

1. **market_sentiment**: What does the options flow tell us?
2. **iv_analysis**: IV rank context, historical comparison, buyer vs seller edge
3. **max_pain_analysis**: Significance of max pain vs current price
4. **unusual_activity_interpretation**: What does the unusual flow signal?
5. **greeks_assessment**: Net exposure implications
6. **strategy_recommendations**: 3 specific strategies with strike/expiration guidance
7. **spread_analysis**: Evaluate the identified spreads
8. **risk_factors**: Top 3 risks with severity and mitigation
9. **position_sizing**: How much to allocate based on IV and DTE
10. **action_plan**: Step-by-step execution guide
11. **plain_english_summary**: 3-sentence summary for non-experts

Return ONLY valid JSON (no markdown, no code blocks):

{
  "market_sentiment": {
    "bias": "BULLISH|BEARISH|NEUTRAL",
    "confidence": "HIGH|MEDIUM|LOW",
    "reasoning": "string",
    "key_flow_signals": ["string"]
  },
  "iv_analysis": {
    "iv_rank_interpretation": "string",
    "level": "HIGH|MEDIUM|LOW",
    "buyer_vs_seller_edge": "string",
    "skew_analysis": "string"
  },
  "max_pain_analysis": {
    "max_pain_price": 0.0,
    "vs_current_price": "string",
    "pin_risk": "HIGH|MEDIUM|LOW",
    "trading_implication": "string"
  },
  "unusual_activity_interpretation": {
    "notable_flow": ["string"],
    "likely_positioning": "string",
    "smart_money_signal": "BULLISH|BEARISH|MIXED|NONE"
  },
  "greeks_assessment": {
    "net_delta_bias": "string",
    "gamma_exposure": "string",
    "vega_sensitivity": "string"
  },
  "strategy_recommendations": [
    {
      "strategy_name": "string",
      "bias": "BULLISH|BEARISH|NEUTRAL",
      "strikes": "string",
      "reasoning": "string",
      "risk_reward": "string",
      "suitability": "AGGRESSIVE|MODERATE|CONSERVATIVE"
    }
  ],
  "spread_analysis": {
    "best_spread": "string",
    "why": "string",
    "alternatives": ["string"]
  },
  "risk_factors": [
    {
      "factor": "string",
      "severity": "HIGH|MEDIUM|LOW",
      "mitigation": "string"
    }
  ],
  "position_sizing": {
    "recommended_allocation": "string",
    "max_risk_per_trade": "string",
    "scaling_guidance": "string"
  },
  "action_plan": [
    {
      "step": 1,
      "action": "string",
      "timing": "BEFORE_ENTRY|AT_ENTRY|AFTER_ENTRY"
    }
  ],
  "plain_english_summary": "string"
}
"""
        return prompt

    def _build_risk_prompt(self, result: dict[str, Any]) -> str:
        """Build a focused prompt for risk-only AI analysis.

        Args:
            result: Risk analysis data dict.

        Returns:
            Prompt string for Gemini.
        """
        symbol = result.get("symbol", "UNKNOWN")
        price = result.get("current_price", 0)
        dte = result.get("days_to_expiration", 0)
        calls = result.get("calls", {})
        puts = result.get("puts", {})
        pcr = result.get("put_call_ratio", {})
        warnings = result.get("risk_warnings", [])
        opportunities = result.get("opportunities", [])

        prompt = f"""You are an expert options risk analyst. Analyze this options chain data.

# OPTIONS CHAIN FOR {symbol}
- Current Price: ${price:.2f}
- Expiration: {result.get('expiration_date', 'N/A')}
- DTE: {dte}

# CALLS
"""
        if calls:
            prompt += f"""- Liquid Contracts: {calls.get('liquid_contracts', 0)}
- Total Volume: {calls.get('total_volume', 0):,}
- Avg IV: {calls.get('avg_implied_volatility', 0):.1f}%
- ATM IV: {calls.get('atm_iv', 0):.1f}%
"""

        prompt += "\n# PUTS\n"
        if puts:
            prompt += f"""- Liquid Contracts: {puts.get('liquid_contracts', 0)}
- Total Volume: {puts.get('total_volume', 0):,}
- Avg IV: {puts.get('avg_implied_volatility', 0):.1f}%
- ATM IV: {puts.get('atm_iv', 0):.1f}%
"""

        if pcr:
            prompt += f"\n# PUT/CALL RATIO\n- Volume: {pcr.get('volume', 'N/A')}\n"

        if warnings:
            prompt += "\n# RISK WARNINGS\n"
            for w in warnings:
                prompt += f"- {w}\n"

        if opportunities:
            prompt += "\n# OPPORTUNITIES\n"
            for o in opportunities:
                prompt += f"- {o}\n"

        prompt += """

Provide analysis in JSON format with: market_sentiment, iv_analysis,
strategy_recommendations (3 strategies), risk_factors (top 3),
position_sizing, and action_plan (5 steps).

Return ONLY valid JSON (no markdown, no code blocks).

{
  "market_sentiment": {
    "bias": "BULLISH|BEARISH|NEUTRAL",
    "confidence": "HIGH|MEDIUM|LOW",
    "reasoning": "string"
  },
  "iv_analysis": {
    "level": "HIGH|MEDIUM|LOW",
    "buyer_vs_seller_edge": "string"
  },
  "strategy_recommendations": [
    {
      "strategy_name": "string",
      "bias": "BULLISH|BEARISH|NEUTRAL",
      "strikes": "string",
      "reasoning": "string",
      "suitability": "AGGRESSIVE|MODERATE|CONSERVATIVE"
    }
  ],
  "risk_factors": [
    {
      "factor": "string",
      "severity": "HIGH|MEDIUM|LOW",
      "mitigation": "string"
    }
  ],
  "position_sizing": {
    "recommended_allocation": "string",
    "max_risk_per_trade": "string"
  },
  "action_plan": [
    {"step": 1, "action": "string", "timing": "string"}
  ]
}
"""
        return prompt

    def _parse_ai_response(self, response_text: str) -> dict[str, Any]:
        """Parse JSON response from Gemini, handling markdown wrapping.

        Args:
            response_text: Raw text from Gemini.

        Returns:
            Parsed JSON dict, or fallback with raw text on parse failure.
        """
        cleaned = response_text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("Error parsing AI response: %s", e)
            logger.debug("Raw response:\n%s", response_text)
            return {
                "error": "AI response parsing failed",
                "raw_response": response_text,
                "parse_error": str(e),
            }
