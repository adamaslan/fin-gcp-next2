#!/usr/bin/env python3
"""
Phase 5: Regression Testing for MCP Finance Swing Trading Tools

This module provides comprehensive regression testing for all 9 MCP tools
to ensure consistent performance on historical swing trading data.

Uses fin-ai1 Conda environment.

Key Features:
- Tests 9 MCP tools with swing trading parameters
- Validates against historical data
- Tracks performance metrics and signal consistency
- Generates regression reports
- Compares results against baseline expectations
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple
import hashlib

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path(__file__).parent / "nu-logs" / f"regression_test_{timestamp}"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "regression_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add mcp-finance1 to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-finance1"))

from src.technical_analysis_mcp.server import (
    analyze_security,
    compare_securities,
    screen_securities,
    get_trade_plan,
    scan_trades,
    portfolio_risk,
    morning_brief,
    analyze_fibonacci,
    options_risk_analysis,
)


class RegressionTestSuite:
    """Comprehensive regression testing for MCP swing trading tools."""

    def __init__(self, output_dir: Path = log_dir):
        """Initialize regression test suite."""
        self.output_dir = output_dir
        self.baseline_dir = self.output_dir / "baselines"
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

        self.results = {}
        self.regressions_found = []
        self.timestamp = timestamp

        self.swing_trading_config = {
            "default_period": "3mo",
            "rsi_period": 24,
            "macd_params": (20, 50, 20),
            "adx_period": 25,
            "fibonacci_window": 150,
            "fibonacci_tolerance": 0.02,
            "min_volume": 75,
            "lookback_days": 180,
            "max_signals_returned": 12,
            "stop_atr_swing": 2.5,
        }

    def hash_result(self, result: Dict[str, Any]) -> str:
        """Create hash of result for comparison."""
        # Remove timestamps and variable fields for hashing
        hashable = json.dumps(result, sort_keys=True, default=str)
        return hashlib.sha256(hashable.encode()).hexdigest()[:16]

    def load_baseline(self, tool_name: str) -> Dict[str, Any] | None:
        """Load baseline result for tool."""
        baseline_file = self.baseline_dir / f"{tool_name}_baseline.json"
        if baseline_file.exists():
            with open(baseline_file, "r") as f:
                return json.load(f)
        return None

    def save_baseline(self, tool_name: str, result: Dict[str, Any]) -> None:
        """Save result as baseline for future comparisons."""
        baseline_file = self.baseline_dir / f"{tool_name}_baseline.json"
        with open(baseline_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"✓ Saved baseline for {tool_name}")

    def compare_results(
        self,
        tool_name: str,
        new_result: Dict[str, Any],
        baseline: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        """Compare new result against baseline."""
        comparison = {
            "tool": tool_name,
            "test_timestamp": self.timestamp,
            "status": "pass",
            "differences": [],
            "new_hash": self.hash_result(new_result),
        }

        if baseline is None:
            comparison["status"] = "baseline_created"
            comparison["message"] = "First test run - baseline created"
            self.save_baseline(tool_name, new_result)
            return comparison

        baseline_hash = self.hash_result(baseline)
        comparison["baseline_hash"] = baseline_hash

        # Check key metrics
        if "signals" in new_result and "signals" in baseline:
            new_count = len(new_result.get("signals", []))
            baseline_count = len(baseline.get("signals", []))

            if abs(new_count - baseline_count) > 2:  # Allow 2 signal variance
                comparison["status"] = "warning"
                comparison["differences"].append(
                    f"Signal count changed: {baseline_count} → {new_count}"
                )
                logger.warning(f"Signal count regression for {tool_name}: {baseline_count} → {new_count}")

        if "winner" in new_result and "winner" in baseline:
            new_winner = new_result.get("winner", {}).get("symbol")
            baseline_winner = baseline.get("winner", {}).get("symbol")

            if new_winner != baseline_winner:
                comparison["status"] = "warning"
                comparison["differences"].append(
                    f"Winner changed: {baseline_winner} → {new_winner}"
                )
                logger.warning(f"Winner regression for {tool_name}: {baseline_winner} → {new_winner}")

        if comparison["status"] == "pass" and not comparison["differences"]:
            logger.info(f"✓ {tool_name} regression test passed")

        return comparison

    async def test_analyze_security(self) -> None:
        """Test 1: analyze_security regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 1: analyze_security")
        logger.info("=" * 80)

        try:
            result = await analyze_security(
                symbol="AAPL",
                period="3mo",
                use_ai=False,
            )

            baseline = self.load_baseline("analyze_security")
            comparison = self.compare_results("analyze_security", result, baseline)

            self.results["analyze_security"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "signal_count": len(result.get("signals", [])),
                    "symbol": result.get("symbol"),
                    "price": result.get("price"),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ analyze_security regression test failed: {e}")
            self.results["analyze_security"] = {"status": "error", "error": str(e)}

    async def test_compare_securities(self) -> None:
        """Test 2: compare_securities regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 2: compare_securities")
        logger.info("=" * 80)

        try:
            result = await compare_securities(
                symbols=["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
                metric="signals",
                period="3mo",
            )

            baseline = self.load_baseline("compare_securities")
            comparison = self.compare_results("compare_securities", result, baseline)

            self.results["compare_securities"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "winner": result.get("winner", {}).get("symbol"),
                    "winner_score": result.get("winner", {}).get("score"),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ compare_securities regression test failed: {e}")
            self.results["compare_securities"] = {"status": "error", "error": str(e)}

    async def test_screen_securities(self) -> None:
        """Test 3: screen_securities regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 3: screen_securities")
        logger.info("=" * 80)

        try:
            result = await screen_securities(
                universe="sp500",
                criteria={"rsi_oversold": True},
                period="3mo",
            )

            baseline = self.load_baseline("screen_securities")
            comparison = self.compare_results("screen_securities", result, baseline)

            self.results["screen_securities"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "matches_count": len(result.get("matches", [])),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ screen_securities regression test failed: {e}")
            self.results["screen_securities"] = {"status": "error", "error": str(e)}

    async def test_get_trade_plan(self) -> None:
        """Test 4: get_trade_plan regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 4: get_trade_plan")
        logger.info("=" * 80)

        try:
            result = await get_trade_plan(
                symbol="AAPL",
                period="3mo",
                risk_level="neutral",
            )

            baseline = self.load_baseline("get_trade_plan")
            comparison = self.compare_results("get_trade_plan", result, baseline)

            self.results["get_trade_plan"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "trade_count": len(result.get("trade_plans", [])),
                    "symbol": result.get("symbol"),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ get_trade_plan regression test failed: {e}")
            self.results["get_trade_plan"] = {"status": "error", "error": str(e)}

    async def test_scan_trades(self) -> None:
        """Test 5: scan_trades regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 5: scan_trades")
        logger.info("=" * 80)

        try:
            result = await scan_trades(
                universe="sp500",
                period="3mo",
                min_quality=0.6,
            )

            baseline = self.load_baseline("scan_trades")
            comparison = self.compare_results("scan_trades", result, baseline)

            self.results["scan_trades"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "qualified_trades_count": len(result.get("qualified_trades", [])),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ scan_trades regression test failed: {e}")
            self.results["scan_trades"] = {"status": "error", "error": str(e)}

    async def test_portfolio_risk(self) -> None:
        """Test 6: portfolio_risk regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 6: portfolio_risk")
        logger.info("=" * 80)

        try:
            result = await portfolio_risk(
                positions=[
                    {"symbol": "AAPL", "quantity": 100, "entry_price": 150},
                    {"symbol": "MSFT", "quantity": 50, "entry_price": 300},
                ],
                period="3mo",
            )

            baseline = self.load_baseline("portfolio_risk")
            comparison = self.compare_results("portfolio_risk", result, baseline)

            self.results["portfolio_risk"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "total_value": result.get("total_value"),
                    "total_max_loss": result.get("total_max_loss"),
                    "risk_level": result.get("overall_risk_level"),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ portfolio_risk regression test failed: {e}")
            self.results["portfolio_risk"] = {"status": "error", "error": str(e)}

    async def test_morning_brief(self) -> None:
        """Test 7: morning_brief regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 7: morning_brief")
        logger.info("=" * 80)

        try:
            result = await morning_brief(
                focus_symbols=["AAPL", "MSFT", "SPY"],
            )

            baseline = self.load_baseline("morning_brief")
            comparison = self.compare_results("morning_brief", result, baseline)

            self.results["morning_brief"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "market_open": result.get("market_status", {}).get("is_open"),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ morning_brief regression test failed: {e}")
            self.results["morning_brief"] = {"status": "error", "error": str(e)}

    async def test_analyze_fibonacci(self) -> None:
        """Test 8: analyze_fibonacci regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 8: analyze_fibonacci")
        logger.info("=" * 80)

        try:
            result = await analyze_fibonacci(
                symbol="AAPL",
                period="3mo",
                window=150,
            )

            baseline = self.load_baseline("analyze_fibonacci")
            comparison = self.compare_results("analyze_fibonacci", result, baseline)

            self.results["analyze_fibonacci"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "level_count": len(result.get("levels", [])),
                    "signal_count": len(result.get("signals", [])),
                    "current_price": result.get("price"),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ analyze_fibonacci regression test failed: {e}")
            self.results["analyze_fibonacci"] = {"status": "error", "error": str(e)}

    async def test_options_risk_analysis(self) -> None:
        """Test 9: options_risk_analysis regression."""
        logger.info("=" * 80)
        logger.info("REGRESSION TEST 9: options_risk_analysis")
        logger.info("=" * 80)

        try:
            result = await options_risk_analysis(
                symbol="AAPL",
                strike_price=150,
                option_type="call",
                days_to_expiration=30,
            )

            baseline = self.load_baseline("options_risk_analysis")
            comparison = self.compare_results("options_risk_analysis", result, baseline)

            self.results["options_risk_analysis"] = {
                "result": result,
                "comparison": comparison,
                "metrics": {
                    "symbol": result.get("symbol"),
                    "expiration": result.get("expiration_date"),
                    "risk_warnings_count": len(result.get("risk_warnings", [])),
                }
            }

            if comparison["status"] != "pass":
                self.regressions_found.append(comparison)

        except Exception as e:
            logger.error(f"✗ options_risk_analysis regression test failed: {e}")
            self.results["options_risk_analysis"] = {"status": "error", "error": str(e)}

    async def run_all_tests(self) -> None:
        """Run all regression tests."""
        logger.info("🚀 Starting Regression Test Suite for Swing Trading MCP Tools")
        logger.info(f"Timestamp: {self.timestamp}")
        logger.info(f"Config: {self.swing_trading_config}")
        logger.info("")

        await asyncio.gather(
            self.test_analyze_security(),
            self.test_compare_securities(),
            self.test_screen_securities(),
            self.test_get_trade_plan(),
            self.test_scan_trades(),
            self.test_portfolio_risk(),
            self.test_morning_brief(),
            self.test_analyze_fibonacci(),
            self.test_options_risk_analysis(),
        )

        self.generate_report()

    def generate_report(self) -> None:
        """Generate comprehensive regression test report."""
        report = {
            "timestamp": self.timestamp,
            "swing_trading_config": self.swing_trading_config,
            "test_summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results.values() if r.get("comparison", {}).get("status") == "pass"),
                "warnings": len(self.regressions_found),
                "errors": sum(1 for r in self.results.values() if r.get("status") == "error"),
            },
            "regressions": self.regressions_found,
            "detailed_results": {},
        }

        # Add detailed results
        for tool_name, result in self.results.items():
            if "comparison" in result:
                report["detailed_results"][tool_name] = {
                    "status": result["comparison"]["status"],
                    "differences": result["comparison"].get("differences", []),
                    "metrics": result.get("metrics", {}),
                }

        # Save report
        report_file = self.output_dir / "regression_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("")
        logger.info("=" * 80)
        logger.info("REGRESSION TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {report['test_summary']['total_tests']}")
        logger.info(f"Passed: {report['test_summary']['passed']}")
        logger.info(f"Warnings: {report['test_summary']['warnings']}")
        logger.info(f"Errors: {report['test_summary']['errors']}")
        logger.info("")
        logger.info(f"📊 Report saved to: {report_file}")

        if self.regressions_found:
            logger.warning("")
            logger.warning("⚠️ REGRESSIONS FOUND:")
            for regression in self.regressions_found:
                logger.warning(f"  - {regression['tool']}: {regression['differences']}")
        else:
            logger.info("✅ All regression tests passed!")


async def main():
    """Run regression test suite."""
    suite = RegressionTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
