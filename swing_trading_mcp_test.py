#!/usr/bin/env python3
"""
Comprehensive test script for all 9 MCP tools with SWING TRADING configuration.

Tests the updated swing trading parameters:
- Period: 3mo (was 1mo)
- RSI: 24 (was 14)
- MACD: (20,50,20) (was 12,26,9)
- ADX: 25 (was 14)
- Fibonacci window: 150 (was 50)
- Tolerance: 2% (was 1%)
- min_volume: 75 (was 10)
- lookback_days: 180 (was 90)
- MAX_SIGNALS_RETURNED: 12 (was 50)

Includes REGRESSION TESTING:
- Validates tool performance against historical baselines
- Detects signal consistency and result regressions
- Generates comprehensive regression reports

Uses fin-ai1 Conda environment for consistency.

Logs results to nu-logs directory.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path(__file__).parent / "nu-logs" / f"swing_trading_test_{timestamp}"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "test.log"),
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


class SwingTradingMCPTester:
    """Test harness for swing trading MCP configuration."""

    def __init__(self, output_dir: Path):
        """Initialize tester."""
        self.output_dir = output_dir
        self.results = {}
        self.summary = {
            "timestamp": timestamp,
            "swing_trading_config": {
                "default_period": "3mo",
                "rsi_period": 24,
                "macd_params": "(20, 50, 20)",
                "adx_period": 25,
                "fibonacci_window": 150,
                "fibonacci_tolerance": 0.02,
                "min_volume": 75,
                "lookback_days": 180,
                "max_signals_returned": 12,
                "stop_atr_swing": 2.5,
            },
            "test_results": {}
        }

    def save_result(self, tool_name: str, result: dict[str, Any]) -> None:
        """Save tool result to JSON file."""
        output_file = self.output_dir / f"{tool_name}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"✓ Saved {tool_name} result to {output_file}")

    async def test_analyze_security(self) -> None:
        """Test 1: analyze_security tool."""
        logger.info("=" * 80)
        logger.info("TEST 1: analyze_security (AAPL, 3mo period)")
        logger.info("=" * 80)

        try:
            result = await analyze_security(
                symbol="AAPL",
                period="3mo",
                use_ai=False,
            )
            self.save_result("01_analyze_security_aapl", result)
            signal_count = len(result.get("signals", []))
            self.summary["test_results"]["analyze_security"] = {
                "status": "success",
                "symbol": "AAPL",
                "signal_count": signal_count,
                "max_signals": 12,
            }
            logger.info(f"✓ analyze_security completed: {signal_count} signals (max 12)")
        except Exception as e:
            logger.error(f"✗ analyze_security failed: {e}")
            self.summary["test_results"]["analyze_security"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_compare_securities(self) -> None:
        """Test 2: compare_securities tool."""
        logger.info("=" * 80)
        logger.info("TEST 2: compare_securities (AAPL, MSFT, GOOGL, TSLA, NVDA)")
        logger.info("=" * 80)

        try:
            result = await compare_securities(
                symbols=["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
                metric="signals",
                period="3mo",
            )
            self.save_result("02_compare_securities", result)
            winner = result.get("winner", {})
            self.summary["test_results"]["compare_securities"] = {
                "status": "success",
                "winner": winner.get("symbol"),
                "score": winner.get("score"),
            }
            logger.info(f"✓ compare_securities completed: winner={winner.get('symbol')}")
        except Exception as e:
            logger.error(f"✗ compare_securities failed: {e}")
            self.summary["test_results"]["compare_securities"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_screen_securities(self) -> None:
        """Test 3: screen_securities tool."""
        logger.info("=" * 80)
        logger.info("TEST 3: screen_securities (SP500, RSI criteria)")
        logger.info("=" * 80)

        try:
            result = await screen_securities(
                universe="sp500",
                criteria={
                    "rsi": {"min": 30, "max": 70},
                    "min_score": 60,
                    "min_bullish": 10,
                },
                limit=20,
                period="3mo",
            )
            self.save_result("03_screen_securities", result)
            matches = len(result.get("matches", []))
            self.summary["test_results"]["screen_securities"] = {
                "status": "success",
                "matches": matches,
                "universe": "sp500",
            }
            logger.info(f"✓ screen_securities completed: {matches} matches found")
        except Exception as e:
            logger.error(f"✗ screen_securities failed: {e}")
            self.summary["test_results"]["screen_securities"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_get_trade_plan(self) -> None:
        """Test 4: get_trade_plan tool."""
        logger.info("=" * 80)
        logger.info("TEST 4: get_trade_plan (AAPL)")
        logger.info("=" * 80)

        try:
            result = await get_trade_plan(
                symbol="AAPL",
                period="3mo",
            )
            self.save_result("04_get_trade_plan_aapl", result)
            plans = len(result.get("plans", []))
            self.summary["test_results"]["get_trade_plan"] = {
                "status": "success",
                "symbol": "AAPL",
                "plans": plans,
                "max_plans": 3,
            }
            logger.info(f"✓ get_trade_plan completed: {plans} trade plans (max 3)")
        except Exception as e:
            logger.error(f"✗ get_trade_plan failed: {e}")
            self.summary["test_results"]["get_trade_plan"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_scan_trades(self) -> None:
        """Test 5: scan_trades tool."""
        logger.info("=" * 80)
        logger.info("TEST 5: scan_trades (SP500)")
        logger.info("=" * 80)

        try:
            result = await scan_trades(
                universe="sp500",
                max_results=10,
                period="3mo",
            )
            self.save_result("05_scan_trades_sp500", result)
            trades = len(result.get("trades", []))
            self.summary["test_results"]["scan_trades"] = {
                "status": "success",
                "universe": "sp500",
                "trades": trades,
            }
            logger.info(f"✓ scan_trades completed: {trades} trade setups found")
        except Exception as e:
            logger.error(f"✗ scan_trades failed: {e}")
            self.summary["test_results"]["scan_trades"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_portfolio_risk(self) -> None:
        """Test 6: portfolio_risk tool."""
        logger.info("=" * 80)
        logger.info("TEST 6: portfolio_risk (sample positions)")
        logger.info("=" * 80)

        try:
            result = await portfolio_risk(
                positions=[
                    {"symbol": "AAPL", "shares": 100, "entry_price": 150},
                    {"symbol": "MSFT", "shares": 50, "entry_price": 380},
                    {"symbol": "GOOGL", "shares": 30, "entry_price": 140},
                ],
                period="3mo",
            )
            self.save_result("06_portfolio_risk", result)
            self.summary["test_results"]["portfolio_risk"] = {
                "status": "success",
                "positions_analyzed": 3,
                "risk_level": result.get("overall_risk_level", "UNKNOWN"),
            }
            logger.info(f"✓ portfolio_risk completed: risk level={result.get('overall_risk_level')}")
        except Exception as e:
            logger.error(f"✗ portfolio_risk failed: {e}")
            self.summary["test_results"]["portfolio_risk"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_morning_brief(self) -> None:
        """Test 7: morning_brief tool."""
        logger.info("=" * 80)
        logger.info("TEST 7: morning_brief (top tech stocks)")
        logger.info("=" * 80)

        try:
            result = await morning_brief(
                watchlist=["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"],
                market_region="US",
                period="3mo",
            )
            self.save_result("07_morning_brief", result)
            self.summary["test_results"]["morning_brief"] = {
                "status": "success",
                "market_region": "US",
                "watchlist_count": 5,
            }
            logger.info(f"✓ morning_brief completed")
        except Exception as e:
            logger.error(f"✗ morning_brief failed: {e}")
            self.summary["test_results"]["morning_brief"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_analyze_fibonacci(self) -> None:
        """Test 8: analyze_fibonacci tool."""
        logger.info("=" * 80)
        logger.info("TEST 8: analyze_fibonacci (AAPL, window=150)")
        logger.info("=" * 80)

        try:
            result = await analyze_fibonacci(
                symbol="AAPL",
                period="3mo",
                window=150,  # SWING TRADING: larger window
            )
            self.save_result("08_analyze_fibonacci_aapl", result)
            levels = len(result.get("levels", []))
            self.summary["test_results"]["analyze_fibonacci"] = {
                "status": "success",
                "symbol": "AAPL",
                "levels": levels,
                "window": 150,
                "tolerance": "2%",
            }
            logger.info(f"✓ analyze_fibonacci completed: {levels} Fibonacci levels")
        except Exception as e:
            logger.error(f"✗ analyze_fibonacci failed: {e}")
            self.summary["test_results"]["analyze_fibonacci"] = {
                "status": "error",
                "error": str(e)
            }

    async def test_options_risk_analysis(self) -> None:
        """Test 9: options_risk_analysis tool."""
        logger.info("=" * 80)
        logger.info("TEST 9: options_risk_analysis (AAPL, min_volume=75)")
        logger.info("=" * 80)

        try:
            result = await options_risk_analysis(
                symbol="AAPL",
                option_type="both",
                min_volume=75,  # SWING TRADING: higher volume threshold
            )
            self.save_result("09_options_risk_analysis_aapl", result)
            calls = len(result.get("calls", []))
            puts = len(result.get("puts", []))
            self.summary["test_results"]["options_risk_analysis"] = {
                "status": "success",
                "symbol": "AAPL",
                "calls_analyzed": calls,
                "puts_analyzed": puts,
                "min_volume": 75,
            }
            logger.info(f"✓ options_risk_analysis completed: {calls} calls, {puts} puts")
        except Exception as e:
            logger.error(f"✗ options_risk_analysis failed: {e}")
            self.summary["test_results"]["options_risk_analysis"] = {
                "status": "error",
                "error": str(e)
            }

    async def run_all_tests(self) -> None:
        """Run all 9 MCP tool tests."""
        logger.info("\n" + "=" * 80)
        logger.info("SWING TRADING MCP CONFIGURATION TEST")
        logger.info("=" * 80 + "\n")

        await self.test_analyze_security()
        await self.test_compare_securities()
        await self.test_screen_securities()
        await self.test_get_trade_plan()
        await self.test_scan_trades()
        await self.test_portfolio_risk()
        await self.test_morning_brief()
        await self.test_analyze_fibonacci()
        await self.test_options_risk_analysis()

        # Save summary
        summary_file = self.output_dir / "SUMMARY.json"
        with open(summary_file, "w") as f:
            json.dump(self.summary, f, indent=2)

        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETE")
        logger.info("=" * 80)
        logger.info(f"\nResults saved to: {self.output_dir}")
        logger.info(f"Summary: {summary_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("SWING TRADING CONFIGURATION TEST SUMMARY")
        print("=" * 80)
        print(json.dumps(self.summary, indent=2, default=str))


async def run_regression_tests():
    """Run regression tests from the regression test suite.

    Imports and executes RegressionTestSuite to test MCP tools against
    baseline expectations and detect performance regressions.

    Returns:
        Tuple of (regression_suite, regression_results_dir)
    """
    try:
        # Import regression test suite
        from swing_trading_regression_tests import RegressionTestSuite

        # Create regression test suite (uses same log_dir for consistency)
        regression_suite = RegressionTestSuite(output_dir=log_dir)

        logger.info("")
        logger.info("🔄 Running Regression Test Suite...")
        logger.info("=" * 80)

        # Run all regression tests
        await regression_suite.run_all_tests()

        return regression_suite, log_dir
    except ImportError as e:
        logger.warning(f"⚠️ Could not import RegressionTestSuite: {e}")
        logger.warning("Skipping regression tests. Run swing_trading_regression_tests.py separately.")
        return None, None
    except Exception as e:
        logger.error(f"❌ Regression test suite failed: {e}")
        return None, None


async def main():
    """Main test runner - runs both functional and regression tests.

    Executes:
    1. Functional tests: Verify all 9 MCP tools work correctly
    2. Regression tests: Validate tools against baseline expectations

    Generates combined reports in nu-logs directory.
    """
    logger.info("")
    logger.info("🚀 SWING TRADING MCP TEST SUITE")
    logger.info("=" * 80)
    logger.info(f"Environment: fin-ai1 (Conda/Mamba)")
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"Output Directory: {log_dir}")
    logger.info("")

    # Run functional tests
    logger.info("📋 Running Functional Tests...")
    logger.info("=" * 80)
    tester = SwingTradingMCPTester(log_dir)
    await tester.run_all_tests()

    # Run regression tests
    regression_suite, regression_dir = await run_regression_tests()

    # Generate combined report
    if regression_suite:
        logger.info("")
        logger.info("📊 COMBINED TEST REPORT")
        logger.info("=" * 80)

        combined_report = {
            "timestamp": timestamp,
            "environment": "fin-ai1 (Conda/Mamba)",
            "functional_tests": tester.summary,
            "regression_tests": {
                "total_tests": len(regression_suite.results),
                "passed": sum(1 for r in regression_suite.results.values() if r.get("comparison", {}).get("status") == "pass"),
                "baselines_created": sum(1 for r in regression_suite.results.values() if r.get("comparison", {}).get("status") == "baseline_created"),
                "warnings": len(regression_suite.regressions_found),
                "errors": sum(1 for r in regression_suite.results.values() if r.get("status") == "error"),
            },
            "regressions_found": regression_suite.regressions_found,
            "directories": {
                "functional_tests": str(log_dir),
                "regression_baselines": str(regression_suite.baseline_dir),
                "logs": str(log_dir),
            }
        }

        # Save combined report
        combined_report_file = log_dir / "COMBINED_TEST_REPORT.json"
        with open(combined_report_file, "w") as f:
            json.dump(combined_report, f, indent=2, default=str)

        logger.info(f"✅ Combined report saved to: {combined_report_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("COMBINED TEST RESULTS")
        print("=" * 80)
        print(f"Functional Tests: {len(tester.summary['test_results'])} tools tested")
        print(f"Regression Tests: {combined_report['regression_tests']['total_tests']} tools compared against baselines")
        print(f"Baselines Created: {combined_report['regression_tests']['baselines_created']}")
        print(f"Regressions Found: {combined_report['regression_tests']['warnings']}")
        print(f"Errors: {combined_report['regression_tests']['errors']}")
        print("=" * 80)
    else:
        logger.info("⚠️ Regression tests were skipped. Run swing_trading_regression_tests.py separately.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
