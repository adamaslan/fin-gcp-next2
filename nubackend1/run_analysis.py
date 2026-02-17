#!/usr/bin/env python3
"""Run options analysis on Firestore data and store optimized results.

Reads options chain data from Firestore (populated by Finnhub pipeline),
runs risk analysis, summary, vehicle selection, and comparison locally
using the existing analysis engines, then stores consolidated results
in an optimized Firestore collection (1 document per symbol).

Data flow:
    Finnhub -> Firestore (pipeline) -> FirestoreChainReader -> Analysis -> Firestore

Usage:
    python run_analysis.py                              # All tracked symbols
    python run_analysis.py --symbols AEM CRM            # Specific symbols
    python run_analysis.py --from-firestore             # Read symbols from Firestore
    python run_analysis.py --symbols AEM --dry-run      # Print results only
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from finnhub_pipeline.analysis_store import FirestoreAnalysisStore
from finnhub_pipeline.firestore_reader import FirestoreChainReader
from options_mcp.analysis.chain_analyzer import ChainAnalyzer, OptionsDataError
from options_mcp.analysis.risk_engine import RiskEngine
from options_mcp.analysis.vehicle_selector import VehicleSelector
from options_mcp.config import DEFAULT_MIN_DTE, DEFAULT_MIN_VOLUME, SUMMARY_MIN_DTE
from options_mcp.models import (
    ChainAnalysis,
    EnhancedFields,
    OptionsRiskResponse,
    OptionsSummaryResponse,
    PutCallRatio,
    SpreadOpportunity,
    UnusualContract,
    VolatilityRegime,
    Timeframe,
)

try:
    from options_mcp.analysis.ai_analyzer import OptionsAIAnalyzer

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_SYMBOLS = ["AEM", "CRM", "IGV", "QBTS", "JPM"]


class OptionsAnalysisRunner:
    """Analyze options data from Firestore and store optimized results.

    Reads Finnhub-sourced options chains from Firestore, runs analysis
    engines (risk, summary, vehicle selection, comparison), and writes
    consolidated per-symbol results back to Firestore.
    """

    def __init__(self, project_id: str = "ttb-lang1") -> None:
        self._store = FirestoreAnalysisStore(project_id=project_id)
        self._reader = FirestoreChainReader(project_id=project_id)
        self._chain_analyzer = ChainAnalyzer()
        self._risk_engine = RiskEngine()
        self._vehicle_selector = VehicleSelector()
        self._project_id = project_id

    def run(
        self,
        symbols: list[str] | None = None,
        from_firestore: bool = False,
        bias: str = "bullish",
        expected_move_percent: float = 3.0,
        dry_run: bool = False,
        use_ai: bool = False,
    ) -> dict[str, Any]:
        """Run full analysis pipeline on Firestore data.

        Args:
            symbols: Ticker symbols to analyze. Uses Firestore symbols if None.
            from_firestore: Explicitly read symbols from Firestore.
            bias: Directional bias for vehicle selection.
            expected_move_percent: Expected move for vehicle selection.
            dry_run: Print results without writing to Firestore.
            use_ai: Run Gemini AI analysis on results.

        Returns:
            Run metadata dict with timing, symbols, and per-tool status.
        """
        start_time = time.time()
        run_id = self._generate_run_id()

        resolved_symbols = self._resolve_symbols(symbols, from_firestore)
        logger.info(
            "Analyzing %d symbols from Firestore data: %s (run_id=%s)",
            len(resolved_symbols),
            resolved_symbols,
            run_id,
        )

        analyzed: list[str] = []
        failed: list[str] = []
        tool_results_summary: dict[str, dict[str, str]] = {}
        now = datetime.now(tz=timezone.utc).isoformat()

        # Process each symbol
        for sym in resolved_symbols:
            sym_result = self._analyze_symbol(
                sym, bias, expected_move_percent, use_ai=use_ai
            )

            # Build comparison data from the summary
            comp_rank = self._build_comparison_rank(sym_result)

            current_price = self._extract_price(sym_result)

            doc_data = {
                "symbol": sym,
                "analyzed_at": now,
                "run_id": run_id,
                "analysis_version": "2.0",
                "data_source": "firestore_finnhub",
                "current_price": current_price,
                "risk_analysis": sym_result.get(
                    "risk_analysis",
                    {"status": "error", "error": "not run", "data": None},
                ),
                "summary": sym_result.get(
                    "summary",
                    {"status": "error", "error": "not run", "data": None},
                ),
                "vehicle_recommendation": sym_result.get(
                    "vehicle_recommendation",
                    {"status": "error", "error": "not run", "data": None},
                ),
                "comparison_rank": comp_rank,
                "enhanced_fields": sym_result.get(
                    "enhanced_fields",
                    {"status": "error", "error": "not run", "data": None},
                ),
            }

            if use_ai:
                doc_data["ai_analysis"] = sym_result.get(
                    "ai_analysis",
                    {"status": "skipped", "error": "not run", "data": None},
                )

            statuses = [
                doc_data["risk_analysis"]["status"],
                doc_data["summary"]["status"],
                doc_data["vehicle_recommendation"]["status"],
            ]
            if any(s == "ok" for s in statuses):
                analyzed.append(sym)
            else:
                failed.append(sym)

            tool_results_summary[sym] = {
                "risk_analysis": doc_data["risk_analysis"]["status"],
                "summary": doc_data["summary"]["status"],
                "vehicle_recommendation": doc_data["vehicle_recommendation"]["status"],
                "comparison_rank": doc_data["comparison_rank"]["status"],
                "enhanced_fields": doc_data["enhanced_fields"]["status"],
            }
            if use_ai:
                tool_results_summary[sym]["ai_analysis"] = doc_data.get(
                    "ai_analysis", {}
                ).get("status", "skipped")

            if not dry_run:
                try:
                    self._store.store_symbol_analysis(sym, doc_data)
                except Exception as e:
                    logger.error("Failed to store analysis for %s: %s", sym, e)
            else:
                logger.info(
                    "[DRY RUN] Would store analysis for %s: %s",
                    sym,
                    tool_results_summary[sym],
                )

        elapsed = round(time.time() - start_time, 2)

        run_metadata = {
            "run_id": run_id,
            "started_at": datetime.fromtimestamp(
                start_time, tz=timezone.utc
            ).isoformat(),
            "completed_at": now,
            "total_elapsed_seconds": elapsed,
            "symbols_requested": resolved_symbols,
            "symbols_analyzed": analyzed,
            "symbols_failed": failed,
            "tool_results": tool_results_summary,
            "data_source": "firestore_finnhub",
            "source": "cli",
            "created_at": now,
        }

        if not dry_run:
            try:
                self._store.store_analysis_run(run_id, run_metadata)
            except Exception as e:
                logger.error("Failed to store run metadata: %s", e)

        return run_metadata

    def _resolve_symbols(
        self,
        symbols: list[str] | None,
        from_firestore: bool,
    ) -> list[str]:
        """Resolve the list of symbols to analyze.

        Args:
            symbols: Explicitly provided symbols.
            from_firestore: Whether to read from Firestore.

        Returns:
            List of uppercase ticker symbols.
        """
        if from_firestore or symbols is None:
            try:
                tracked = self._reader.get_tracked_symbols()
                if tracked:
                    return tracked
            except OptionsDataError as e:
                logger.warning("Could not read Firestore symbols: %s", e)

            if symbols is None:
                logger.warning("Falling back to default symbols")
                return DEFAULT_SYMBOLS

        return [s.upper().strip() for s in symbols]

    def _analyze_symbol(
        self,
        symbol: str,
        bias: str,
        expected_move_percent: float,
        use_ai: bool = False,
    ) -> dict[str, Any]:
        """Run all analysis tools on Firestore data for a single symbol.

        Args:
            symbol: Ticker symbol.
            bias: Directional bias for vehicle selection.
            expected_move_percent: Expected move percentage.
            use_ai: Whether to run Gemini AI analysis.

        Returns:
            Dict with risk_analysis, summary, vehicle_recommendation,
            enhanced_fields, and optionally ai_analysis results.
        """
        logger.info("Analyzing %s from Firestore data...", symbol)

        risk_result = self._run_risk_analysis(symbol)
        summary_result = self._run_summary(symbol)
        vehicle_result = self._run_vehicle_selection(
            symbol, bias, expected_move_percent
        )

        # Compute enhanced fields using nearest expiration
        enhanced_result: dict[str, Any] = {
            "status": "error", "error": "not run", "data": None
        }
        try:
            expirations = self._reader.get_expirations(symbol)
            selected_exp = self._chain_analyzer.select_expiration(
                tuple(expirations), None, symbol, min_dte=DEFAULT_MIN_DTE,
            )
            enhanced_result = self._compute_enhanced_fields(
                symbol, selected_exp
            )
        except Exception as e:
            logger.warning("Could not compute enhanced fields for %s: %s", symbol, e)

        result = {
            "risk_analysis": risk_result,
            "summary": summary_result,
            "vehicle_recommendation": vehicle_result,
            "enhanced_fields": enhanced_result,
        }

        # Run AI analysis if requested
        if use_ai:
            result["ai_analysis"] = self._run_ai_analysis(symbol, result)

        return result

    def _run_risk_analysis(self, symbol: str) -> dict[str, Any]:
        """Run full risk analysis on Firestore options data.

        Args:
            symbol: Ticker symbol.

        Returns:
            Tool result dict with status, error, and data fields.
        """
        try:
            current_price = self._reader.get_current_price(symbol)
            expirations = self._reader.get_expirations(symbol)
            selected_exp = self._chain_analyzer.select_expiration(
                tuple(expirations), None, symbol, min_dte=DEFAULT_MIN_DTE,
            )
            calls_df, puts_df = self._reader.get_option_chain(symbol, selected_exp)

            exp_date = datetime.strptime(selected_exp, "%Y-%m-%d")
            dte = (exp_date - datetime.now()).days

            calls_analysis = self._chain_analyzer.analyze_chain(
                calls_df, current_price, DEFAULT_MIN_VOLUME, "calls"
            )
            puts_analysis = self._chain_analyzer.analyze_chain(
                puts_df, current_price, DEFAULT_MIN_VOLUME, "puts"
            )

            pcr = _compute_pcr(calls_analysis, puts_analysis)
            warnings, opportunities = self._risk_engine.assess(
                calls_analysis, puts_analysis, pcr, dte
            )

            response = OptionsRiskResponse(
                symbol=symbol,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
                current_price=current_price,
                expiration_date=selected_exp,
                days_to_expiration=dte,
                available_expirations=expirations,
                calls=calls_analysis,
                puts=puts_analysis,
                put_call_ratio=pcr,
                risk_warnings=warnings,
                opportunities=opportunities,
                liquidity_threshold=DEFAULT_MIN_VOLUME,
            )

            logger.info("Risk analysis complete for %s", symbol)
            return {"status": "ok", "error": None, "data": response.model_dump()}

        except OptionsDataError as e:
            logger.warning("Risk analysis data error for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}
        except Exception as e:
            logger.error("Risk analysis failed for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}

    def _run_summary(self, symbol: str) -> dict[str, Any]:
        """Run quick summary on Firestore options data.

        Args:
            symbol: Ticker symbol.

        Returns:
            Tool result dict with status, error, and data fields.
        """
        try:
            current_price = self._reader.get_current_price(symbol)
            expirations = self._reader.get_expirations(symbol)
            selected_exp = self._chain_analyzer.select_expiration(
                tuple(expirations), None, symbol, min_dte=SUMMARY_MIN_DTE,
            )
            calls_df, puts_df = self._reader.get_option_chain(symbol, selected_exp)

            exp_date = datetime.strptime(selected_exp, "%Y-%m-%d")
            dte = (exp_date - datetime.now()).days

            calls_analysis = self._chain_analyzer.analyze_chain(
                calls_df, current_price, DEFAULT_MIN_VOLUME, "calls"
            )
            puts_analysis = self._chain_analyzer.analyze_chain(
                puts_df, current_price, DEFAULT_MIN_VOLUME, "puts"
            )

            pcr = _compute_pcr(calls_analysis, puts_analysis)
            sentiment = _derive_sentiment(pcr)
            risk_level = _derive_risk_level(calls_analysis, puts_analysis)

            response = OptionsSummaryResponse(
                symbol=symbol,
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
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

            logger.info("Summary complete for %s: %s / %s", symbol, sentiment, risk_level)
            return {"status": "ok", "error": None, "data": response.model_dump()}

        except OptionsDataError as e:
            logger.warning("Summary data error for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}
        except Exception as e:
            logger.error("Summary failed for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}

    def _run_vehicle_selection(
        self,
        symbol: str,
        bias: str,
        expected_move_percent: float,
    ) -> dict[str, Any]:
        """Run vehicle selection using Firestore candle data for volatility.

        Falls back to medium volatility if candle data unavailable.

        Args:
            symbol: Ticker symbol.
            bias: Directional bias.
            expected_move_percent: Expected move percentage.

        Returns:
            Tool result dict with status, error, and data fields.
        """
        try:
            vol_regime = self._estimate_volatility_regime(symbol)

            recommendation = self._vehicle_selector.select(
                timeframe=Timeframe.SWING,
                volatility_regime=vol_regime,
                bias=bias,
                expected_move_percent=expected_move_percent,
            )

            result = recommendation.model_dump()
            result["symbol"] = symbol
            result["volatility_regime"] = vol_regime.value
            result["timestamp"] = datetime.now(tz=timezone.utc).isoformat()

            logger.info(
                "Vehicle selection for %s: %s (vol=%s)",
                symbol,
                result["vehicle"],
                vol_regime.value,
            )
            return {"status": "ok", "error": None, "data": result}

        except Exception as e:
            logger.error("Vehicle selection failed for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}

    def _estimate_volatility_regime(self, symbol: str) -> VolatilityRegime:
        """Estimate volatility regime from Firestore expiration IV data.

        Uses the implied volatility from the nearest expiration summary
        stored by the Finnhub pipeline.

        Args:
            symbol: Ticker symbol.

        Returns:
            VolatilityRegime classification.
        """
        try:
            expirations = self._reader.get_expirations(symbol)
            selected_exp = self._chain_analyzer.select_expiration(
                tuple(expirations), None, symbol, min_dte=SUMMARY_MIN_DTE,
            )
            summary = self._reader.get_expiration_summary(symbol, selected_exp)
            iv = summary.get("implied_volatility")

            if iv is None:
                return VolatilityRegime.MEDIUM

            # Classify based on annualized IV
            # These thresholds align with the config.py volatility thresholds
            # but use IV instead of ATR since we're reading from Firestore
            if iv < 0.20:
                return VolatilityRegime.LOW
            if iv > 0.50:
                return VolatilityRegime.HIGH
            return VolatilityRegime.MEDIUM

        except Exception as e:
            logger.warning(
                "Could not estimate volatility for %s, defaulting to MEDIUM: %s",
                symbol,
                e,
            )
            return VolatilityRegime.MEDIUM

    def _compute_enhanced_fields(
        self,
        symbol: str,
        expiration: str,
    ) -> dict[str, Any]:
        """Compute 5 enhanced analysis fields from Firestore chain data.

        Fields: iv_rank, max_pain, unusual_activity, greeks_exposure,
        spread_opportunities.

        Args:
            symbol: Ticker symbol.
            expiration: Expiration date string.

        Returns:
            Tool result dict with status, error, and data (EnhancedFields).
        """
        try:
            calls_df, puts_df = self._reader.get_option_chain(symbol, expiration)
            current_price = self._reader.get_current_price(symbol)
            all_opts = pd.concat([calls_df, puts_df], ignore_index=True)

            if all_opts.empty:
                return {"status": "error", "error": "No options data", "data": None}

            iv_rank = self._calc_iv_rank(all_opts)
            max_pain = self._calc_max_pain(calls_df, puts_df)
            unusual = self._find_unusual_activity(calls_df, puts_df)
            greeks = self._calc_greeks_exposure(all_opts)
            spreads = self._find_spread_opportunities(
                calls_df, puts_df, current_price
            )

            enhanced = EnhancedFields(
                iv_rank=iv_rank,
                max_pain=max_pain,
                unusual_activity=unusual,
                greeks_exposure=greeks,
                spread_opportunities=spreads,
            )

            logger.info(
                "Enhanced fields for %s: iv_rank=%.1f, max_pain=%.2f, "
                "unusual=%d, spreads=%d",
                symbol,
                iv_rank or 0,
                max_pain or 0,
                len(unusual),
                len(spreads),
            )
            return {"status": "ok", "error": None, "data": enhanced.model_dump()}

        except Exception as e:
            logger.error("Enhanced fields failed for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}

    def _calc_iv_rank(self, all_opts: pd.DataFrame) -> float | None:
        """Compute IV rank as 0-100 percentile within the expiration.

        Args:
            all_opts: Combined calls + puts DataFrame.

        Returns:
            IV rank percentage or None if insufficient data.
        """
        if "impliedVolatility" not in all_opts.columns:
            return None

        iv_vals = all_opts["impliedVolatility"].dropna()
        if iv_vals.empty or len(iv_vals) < 2:
            return None

        iv_range = iv_vals.max() - iv_vals.min()
        if iv_range == 0:
            return 50.0

        current_iv = iv_vals.mean()
        return round(((current_iv - iv_vals.min()) / iv_range) * 100, 2)

    def _calc_max_pain(
        self,
        calls_df: pd.DataFrame,
        puts_df: pd.DataFrame,
    ) -> float | None:
        """Compute max pain: strike where most options expire worthless.

        Max pain minimizes total intrinsic value paid out to option holders.

        Args:
            calls_df: Calls DataFrame.
            puts_df: Puts DataFrame.

        Returns:
            Max pain strike price or None.
        """
        if calls_df.empty and puts_df.empty:
            return None

        all_strikes = set()
        if not calls_df.empty and "strike" in calls_df.columns:
            all_strikes.update(calls_df["strike"].dropna().unique())
        if not puts_df.empty and "strike" in puts_df.columns:
            all_strikes.update(puts_df["strike"].dropna().unique())

        if not all_strikes:
            return None

        def _total_pain_at(settlement: float) -> float:
            """Total intrinsic value paid out if stock settles at this price."""
            pain = 0.0
            if not calls_df.empty and "strike" in calls_df.columns:
                for _, row in calls_df.iterrows():
                    itm = max(0, settlement - row["strike"])
                    oi = row.get("openInterest", 0)
                    pain += itm * oi
            if not puts_df.empty and "strike" in puts_df.columns:
                for _, row in puts_df.iterrows():
                    itm = max(0, row["strike"] - settlement)
                    oi = row.get("openInterest", 0)
                    pain += itm * oi
            return pain

        pain_map = {s: _total_pain_at(s) for s in all_strikes}
        return min(pain_map, key=pain_map.get)

    def _find_unusual_activity(
        self,
        calls_df: pd.DataFrame,
        puts_df: pd.DataFrame,
    ) -> list[UnusualContract]:
        """Find contracts where volume > 3x open interest.

        Args:
            calls_df: Calls DataFrame.
            puts_df: Puts DataFrame.

        Returns:
            List of UnusualContract models.
        """
        unusual: list[UnusualContract] = []

        for df, opt_type in [(calls_df, "call"), (puts_df, "put")]:
            if df.empty:
                continue
            for col in ("volume", "openInterest", "strike"):
                if col not in df.columns:
                    break
            else:
                for _, row in df.iterrows():
                    vol = row.get("volume", 0)
                    oi = row.get("openInterest", 0)
                    if oi <= 0 or vol <= 0:
                        continue
                    ratio = vol / oi
                    if ratio > 3.0:
                        unusual.append(
                            UnusualContract(
                                strike=float(row["strike"]),
                                volume=int(vol),
                                open_interest=int(oi),
                                vol_oi_ratio=round(ratio, 2),
                                option_type=opt_type,
                            )
                        )

        unusual.sort(key=lambda x: x.vol_oi_ratio, reverse=True)
        return unusual[:10]

    def _calc_greeks_exposure(
        self, all_opts: pd.DataFrame
    ) -> dict[str, float]:
        """Aggregate delta, gamma, vega across the entire chain.

        Args:
            all_opts: Combined calls + puts DataFrame.

        Returns:
            Dict of greek name -> aggregate value.
        """
        greeks: dict[str, float] = {}
        for greek in ("delta", "gamma", "vega", "theta"):
            if greek in all_opts.columns:
                vals = pd.to_numeric(all_opts[greek], errors="coerce").dropna()
                if not vals.empty:
                    greeks[greek] = round(float(vals.sum()), 4)
        return greeks

    def _find_spread_opportunities(
        self,
        calls_df: pd.DataFrame,
        puts_df: pd.DataFrame,
        current_price: float,
    ) -> list[SpreadOpportunity]:
        """Find top 3 vertical spread opportunities by risk/reward.

        Looks for bull call spreads (buy lower, sell higher) and
        bear put spreads (buy higher, sell lower) near the money.

        Args:
            calls_df: Calls DataFrame.
            puts_df: Puts DataFrame.
            current_price: Current stock price.

        Returns:
            List of SpreadOpportunity models (max 3).
        """
        spreads: list[SpreadOpportunity] = []

        for df, opt_type in [(calls_df, "call"), (puts_df, "put")]:
            if df.empty or "strike" not in df.columns:
                continue
            if "ask" not in df.columns or "bid" not in df.columns:
                continue

            liquid = df[df.get("volume", pd.Series(dtype=int)) >= 10].copy()
            if liquid.empty:
                liquid = df.copy()

            liquid = liquid.sort_values("strike").reset_index(drop=True)
            if len(liquid) < 2:
                continue

            # Find ATM index
            distance = (liquid["strike"] - current_price).abs()
            atm_idx = distance.idxmin()

            # Look at nearby strikes for spreads
            start = max(0, atm_idx - 2)
            end = min(len(liquid) - 1, atm_idx + 3)

            for i in range(start, end):
                for j in range(i + 1, min(end + 1, len(liquid))):
                    buy_row = liquid.iloc[i]
                    sell_row = liquid.iloc[j]

                    buy_ask = buy_row.get("ask", 0) or 0
                    sell_bid = sell_row.get("bid", 0) or 0

                    if buy_ask <= 0 or sell_bid <= 0:
                        continue

                    width = sell_row["strike"] - buy_row["strike"]
                    if width <= 0:
                        continue

                    if opt_type == "call":
                        cost = buy_ask - sell_bid
                        profit = width - cost
                    else:
                        cost = sell_bid - buy_ask
                        profit = width - abs(cost)

                    if cost <= 0 or profit <= 0:
                        continue

                    spreads.append(
                        SpreadOpportunity(
                            buy_strike=float(buy_row["strike"]),
                            sell_strike=float(sell_row["strike"]),
                            spread_width=round(float(width), 2),
                            max_cost=round(float(abs(cost)), 2),
                            max_profit=round(float(profit), 2),
                            option_type=opt_type,
                        )
                    )

        # Sort by profit/cost ratio descending, take top 3
        spreads.sort(
            key=lambda s: (s.max_profit / s.max_cost) if s.max_cost else 0,
            reverse=True,
        )
        return spreads[:3]

    def _run_ai_analysis(
        self,
        symbol: str,
        sym_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Run Gemini AI analysis on combined options data.

        Args:
            symbol: Ticker symbol.
            sym_result: Full per-symbol analysis dict.

        Returns:
            Tool result dict with status, error, and data.
        """
        if not AI_AVAILABLE:
            return {"status": "skipped", "error": "AI module not available", "data": None}

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            return {"status": "skipped", "error": "GEMINI_API_KEY not set", "data": None}

        try:
            analyzer = OptionsAIAnalyzer(api_key=gemini_key)
            ai_result = analyzer.analyze_options_output(symbol, sym_result)
            logger.info("AI analysis complete for %s", symbol)
            return {"status": "ok", "error": None, "data": ai_result}
        except Exception as e:
            logger.error("AI analysis failed for %s: %s", symbol, e)
            return {"status": "error", "error": str(e), "data": None}

    def _build_comparison_rank(
        self, sym_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Build comparison rank data from analysis results.

        Extracts key metrics from risk and summary results to create
        a comparison-ready data structure.

        Args:
            sym_result: Per-symbol analysis results.

        Returns:
            Comparison rank dict with status, error, and data.
        """
        try:
            summary = sym_result.get("summary", {})
            risk = sym_result.get("risk_analysis", {})

            if summary.get("status") != "ok":
                return {"status": "error", "error": "summary not available", "data": None}

            summary_data = summary["data"]
            risk_data = risk.get("data", {}) if risk.get("status") == "ok" else {}

            # Extract liquid contracts from risk analysis if available
            liquid = 0
            if risk_data:
                calls = risk_data.get("calls")
                puts = risk_data.get("puts")
                if calls:
                    liquid += calls.get("liquid_contracts", 0)
                if puts:
                    liquid += puts.get("liquid_contracts", 0)

            return {
                "status": "ok",
                "error": None,
                "data": {
                    "atm_iv": summary_data.get("atm_call_iv"),
                    "put_call_ratio": summary_data.get("put_call_ratio_volume"),
                    "total_volume": (
                        summary_data.get("total_call_volume", 0)
                        + summary_data.get("total_put_volume", 0)
                    ),
                    "liquid_contracts": liquid,
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "data": None}

    def _extract_price(self, sym_result: dict[str, Any]) -> float | None:
        """Extract current_price from whichever tool succeeded first."""
        for tool_key in ("risk_analysis", "summary"):
            tool_result = sym_result.get(tool_key, {})
            if tool_result.get("status") == "ok" and tool_result.get("data"):
                price = tool_result["data"].get("current_price")
                if price is not None:
                    return price
        return None

    def _generate_run_id(self) -> str:
        """Generate a deterministic run ID from current timestamp."""
        now = datetime.now(tz=timezone.utc)
        return f"analysis_{now.strftime('%Y%m%d_%H%M%S')}"


# =============================================================================
# Helper Functions (from server.py, adapted for local use)
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


# =============================================================================
# CLI
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Options Analysis (Firestore data) -> Optimized Firestore Storage"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=None,
        help=(
            "Ticker symbols to analyze. "
            "If omitted, reads from Firestore or uses defaults."
        ),
    )
    parser.add_argument(
        "--from-firestore",
        action="store_true",
        help="Read symbols from Firestore options_chains collection",
    )
    parser.add_argument(
        "--project",
        default="ttb-lang1",
        help="GCP project ID for Firestore (default: ttb-lang1)",
    )
    parser.add_argument(
        "--bias",
        default="bullish",
        choices=["bullish", "bearish"],
        help="Directional bias for vehicle selection (default: bullish)",
    )
    parser.add_argument(
        "--expected-move",
        type=float,
        default=3.0,
        help="Expected move %% for vehicle selection (default: 3.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run analysis but do not write to Firestore",
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Run Gemini AI analysis on results (requires GEMINI_API_KEY)",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the analysis runner."""
    args = parse_args()

    runner = OptionsAnalysisRunner(project_id=args.project)

    try:
        result = runner.run(
            symbols=args.symbols,
            from_firestore=args.from_firestore,
            bias=args.bias,
            expected_move_percent=args.expected_move,
            dry_run=args.dry_run,
            use_ai=args.use_ai,
        )

        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(json.dumps(result, indent=2, default=str))

        if args.dry_run:
            print("\n[DRY RUN] No data written to Firestore")

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Analysis runner failed: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
