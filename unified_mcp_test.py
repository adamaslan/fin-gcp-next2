#!/usr/bin/env python3
"""
UNIFIED MCP TEST - All 9 Tools with MU vs NVDA

Tests all 9 MCP tools using configuration from test_config.py
Minimizes API calls by caching data after first fetch.

Edit test_config.py to change test parameters.

Usage:
  mamba activate fin-ai1
  python unified_mcp_test.py
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Import configuration
from test_config import (
    CONFIG,
    E2E_CONFIG,
    get_test_symbols,
    get_comparison_symbols,
    get_screen_universe,
    get_scan_universe,
    print_config,
)

# Setup timestamp and directories
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path(__file__).parent / CONFIG["output_dir"] / f"unified_test_{timestamp}"
log_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO if CONFIG["verbose"] else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "unified_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add mcp-finance1 to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-finance1"))

# Import MCP tools
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


class DataCache:
    """Cache to minimize API calls - fetch once, use many times"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._fetch_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Get cached data"""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Cache data"""
        self._cache[key] = value

    def get_fetch_count(self) -> int:
        """Get total API fetch count"""
        return self._fetch_count

    def increment_fetch(self) -> None:
        """Increment fetch counter"""
        self._fetch_count += 1


class UnifiedMCPTest:
    """Test all 9 MCP tools with minimal API calls"""

    def __init__(self):
        self.output_dir = log_dir
        self.baseline_dir = self.output_dir / "baselines"
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

        self.cache = DataCache()
        self.results: Dict[str, Dict[str, Any]] = {}
        self.timestamp = timestamp

        # Get config values
        self.primary = CONFIG["primary_stock"]
        self.comparison = CONFIG["comparison_stock"]
        self.period = CONFIG["period"]
        self.use_ai = CONFIG["use_ai"]

    def save_result(self, tool_name: str, result: Dict[str, Any]) -> None:
        """Save tool result to file"""
        result_file = self.output_dir / f"{tool_name}.json"
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        if CONFIG["save_baselines"]:
            baseline_file = self.baseline_dir / f"{tool_name}_baseline.json"
            with open(baseline_file, "w") as f:
                json.dump(result, f, indent=2, default=str)

    async def prefetch_data(self) -> None:
        """Pre-fetch all stock data with single API call per symbol"""
        logger.info("=" * 80)
        logger.info("PRE-FETCHING DATA (Minimizing API Calls)")
        logger.info("=" * 80)

        symbols = get_test_symbols()
        logger.info(f"Symbols to fetch: {symbols}")

        for symbol in symbols:
            logger.info(f"Fetching {symbol}...")
            try:
                # Single fetch per symbol - result will be cached by MCP server
                result = await analyze_security(
                    symbol=symbol,
                    period=self.period,
                    use_ai=False,  # Don't use AI for prefetch
                )
                self.cache.set(f"analyze_{symbol}", result)
                self.cache.increment_fetch()
                logger.info(f"✅ Cached {symbol}: {len(result.get('signals', []))} signals")
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch {symbol}: {e}")

        logger.info(f"\n📊 Total API fetches: {self.cache.get_fetch_count()}")

    # =========================================================================
    # TEST 1: analyze_security
    # =========================================================================
    async def test_analyze_security(self) -> None:
        """Test 1: analyze_security with primary stock"""
        logger.info("=" * 80)
        logger.info(f"TEST 1: analyze_security ({self.primary})")
        logger.info("=" * 80)

        try:
            # Use cached result if available
            cached = self.cache.get(f"analyze_{self.primary}")
            if cached:
                result = cached
                logger.info("Using cached data")
            else:
                result = await analyze_security(
                    symbol=self.primary,
                    period=self.period,
                    use_ai=self.use_ai,
                )

            self.results["analyze_security"] = {
                "status": "success",
                "symbol": result.get("symbol"),
                "signal_count": len(result.get("signals", [])),
                "price": result.get("price"),
            }
            self.save_result("01_analyze_security", result)
            logger.info(f"✅ analyze_security: {len(result.get('signals', []))} signals")

        except Exception as e:
            logger.error(f"❌ analyze_security failed: {e}")
            self.results["analyze_security"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 2: compare_securities (MU vs NVDA)
    # =========================================================================
    async def test_compare_securities(self) -> None:
        """Test 2: compare_securities MU vs NVDA"""
        logger.info("=" * 80)
        logger.info(f"TEST 2: compare_securities ({self.primary} vs {self.comparison})")
        logger.info("=" * 80)

        try:
            result = await compare_securities(
                symbols=get_comparison_symbols(),
                metric="signals",
                period=self.period,
            )

            self.results["compare_securities"] = {
                "status": "success",
                "symbols": get_comparison_symbols(),
                "winner": result.get("winner", {}).get("symbol"),
                "winner_score": result.get("winner", {}).get("score"),
            }
            self.save_result("02_compare_securities", result)
            logger.info(f"✅ compare_securities: Winner = {result.get('winner', {}).get('symbol')}")

        except Exception as e:
            logger.error(f"❌ compare_securities failed: {e}")
            self.results["compare_securities"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 3: screen_securities
    # =========================================================================
    async def test_screen_securities(self) -> None:
        """Test 3: screen_securities"""
        logger.info("=" * 80)
        logger.info(f"TEST 3: screen_securities (universe: {get_screen_universe()})")
        logger.info("=" * 80)

        try:
            result = await screen_securities(
                universe=get_screen_universe(),  # Must be string: "sp500", "nasdaq100", etc.
                criteria=CONFIG["screen_criteria"],
                limit=CONFIG.get("screen_limit", 20),
                period=self.period,
            )

            self.results["screen_securities"] = {
                "status": "success",
                "matches": len(result.get("matches", [])),
                "universe": get_screen_universe(),
            }
            self.save_result("03_screen_securities", result)
            logger.info(f"✅ screen_securities: {len(result.get('matches', []))} matches")

        except Exception as e:
            logger.error(f"❌ screen_securities failed: {e}")
            self.results["screen_securities"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 4: get_trade_plan
    # =========================================================================
    async def test_get_trade_plan(self) -> None:
        """Test 4: get_trade_plan with primary stock"""
        logger.info("=" * 80)
        logger.info(f"TEST 4: get_trade_plan ({self.primary})")
        logger.info("=" * 80)

        try:
            result = await get_trade_plan(
                symbol=self.primary,
                period=self.period,
            )

            self.results["get_trade_plan"] = {
                "status": "success",
                "symbol": self.primary,
                "plans": len(result.get("plans", [])),
            }
            self.save_result("04_get_trade_plan", result)
            logger.info(f"✅ get_trade_plan: {len(result.get('plans', []))} plans")

        except Exception as e:
            logger.error(f"❌ get_trade_plan failed: {e}")
            self.results["get_trade_plan"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 5: scan_trades
    # =========================================================================
    async def test_scan_trades(self) -> None:
        """Test 5: scan_trades"""
        logger.info("=" * 80)
        logger.info(f"TEST 5: scan_trades (universe: {get_scan_universe()})")
        logger.info("=" * 80)

        try:
            result = await scan_trades(
                universe=get_scan_universe(),  # Must be string: "sp500", "nasdaq100", etc.
                max_results=CONFIG.get("scan_max_results", 10),
                period=self.period,
            )

            self.results["scan_trades"] = {
                "status": "success",
                "qualified_trades": len(result.get("qualified_trades", [])),
                "total_scanned": result.get("total_scanned", 0),
                "universe": get_scan_universe(),
            }
            self.save_result("05_scan_trades", result)
            logger.info(f"✅ scan_trades: {len(result.get('qualified_trades', []))} qualified trades")

        except Exception as e:
            logger.error(f"❌ scan_trades failed: {e}")
            self.results["scan_trades"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 6: portfolio_risk
    # =========================================================================
    async def test_portfolio_risk(self) -> None:
        """Test 6: portfolio_risk with MU and NVDA positions"""
        logger.info("=" * 80)
        logger.info("TEST 6: portfolio_risk")
        logger.info("=" * 80)

        try:
            result = await portfolio_risk(
                positions=CONFIG["portfolio_positions"],
                period=self.period,
            )

            self.results["portfolio_risk"] = {
                "status": "success",
                "positions": len(CONFIG["portfolio_positions"]),
                "risk_level": result.get("overall_risk_level"),
            }
            self.save_result("06_portfolio_risk", result)
            logger.info(f"✅ portfolio_risk: Risk level = {result.get('overall_risk_level')}")

        except Exception as e:
            logger.error(f"❌ portfolio_risk failed: {e}")
            self.results["portfolio_risk"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 7: morning_brief
    # =========================================================================
    async def test_morning_brief(self) -> None:
        """Test 7: morning_brief with watchlist"""
        logger.info("=" * 80)
        logger.info(f"TEST 7: morning_brief (watchlist: {CONFIG['watchlist']})")
        logger.info("=" * 80)

        try:
            result = await morning_brief(
                watchlist=CONFIG["watchlist"],
                market_region="US",
                period=self.period,
            )

            self.results["morning_brief"] = {
                "status": "success",
                "watchlist": CONFIG["watchlist"],
                "stocks_analyzed": len(CONFIG["watchlist"]),
            }
            self.save_result("07_morning_brief", result)
            logger.info(f"✅ morning_brief: {len(CONFIG['watchlist'])} stocks analyzed")

        except Exception as e:
            logger.error(f"❌ morning_brief failed: {e}")
            self.results["morning_brief"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 8: analyze_fibonacci
    # =========================================================================
    async def test_analyze_fibonacci(self) -> None:
        """Test 8: analyze_fibonacci with primary stock"""
        logger.info("=" * 80)
        logger.info(f"TEST 8: analyze_fibonacci ({self.primary})")
        logger.info("=" * 80)

        try:
            result = await analyze_fibonacci(
                symbol=self.primary,
                period=self.period,
                window=CONFIG["fibonacci_window"],
            )

            self.results["analyze_fibonacci"] = {
                "status": "success",
                "symbol": self.primary,
                "levels": len(result.get("levels", [])),
                "signals": len(result.get("signals", [])),
            }
            self.save_result("08_analyze_fibonacci", result)
            logger.info(f"✅ analyze_fibonacci: {len(result.get('levels', []))} levels")

        except Exception as e:
            logger.error(f"❌ analyze_fibonacci failed: {e}")
            self.results["analyze_fibonacci"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # TEST 9: options_risk_analysis
    # =========================================================================
    async def test_options_risk_analysis(self) -> None:
        """Test 9: options_risk_analysis with primary stock"""
        logger.info("=" * 80)
        logger.info(f"TEST 9: options_risk_analysis ({self.primary})")
        logger.info("=" * 80)

        try:
            result = await options_risk_analysis(
                symbol=self.primary,
                expiration_date=CONFIG.get("options_expiration_date"),  # None = nearest expiration
                option_type=CONFIG.get("options_type", "both"),  # "calls", "puts", or "both"
                min_volume=CONFIG.get("options_min_volume", 75),
            )

            self.results["options_risk_analysis"] = {
                "status": "success",
                "symbol": self.primary,
                "expiration": result.get("expiration_date"),
                "option_type": CONFIG.get("options_type", "both"),
                "calls_count": result.get("calls", {}).get("total_contracts", 0) if result.get("calls") else 0,
                "puts_count": result.get("puts", {}).get("total_contracts", 0) if result.get("puts") else 0,
            }
            self.save_result("09_options_risk_analysis", result)
            logger.info(f"✅ options_risk_analysis: Expiration={result.get('expiration_date')}")

        except Exception as e:
            logger.error(f"❌ options_risk_analysis failed: {e}")
            self.results["options_risk_analysis"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # RUN ALL TESTS
    # =========================================================================
    async def run_all_tests(self) -> None:
        """Run all 9 MCP tests"""
        logger.info("\n")
        logger.info("🚀 UNIFIED MCP TEST - All 9 Tools")
        logger.info("=" * 80)
        print_config()
        logger.info(f"Output: {self.output_dir}")
        logger.info("")

        # Pre-fetch data to minimize API calls
        await self.prefetch_data()

        # Run all 9 tests sequentially (uses cached data)
        await self.test_analyze_security()
        await self.test_compare_securities()
        await self.test_screen_securities()
        await self.test_get_trade_plan()
        await self.test_scan_trades()
        await self.test_portfolio_risk()
        await self.test_morning_brief()
        await self.test_analyze_fibonacci()
        await self.test_options_risk_analysis()

        # Generate report
        self.generate_report()

    def generate_report(self) -> None:
        """Generate test report"""
        passed = sum(1 for r in self.results.values() if r.get("status") == "success")
        errors = sum(1 for r in self.results.values() if r.get("status") == "error")

        report = {
            "timestamp": self.timestamp,
            "config": {
                "primary_stock": self.primary,
                "comparison_stock": self.comparison,
                "period": self.period,
                "use_ai": self.use_ai,
            },
            "api_stats": {
                "total_fetches": self.cache.get_fetch_count(),
                "cache_enabled": CONFIG["cache_enabled"],
            },
            "test_summary": {
                "total_tests": 9,
                "passed": passed,
                "errors": errors,
                "success_rate": f"{(passed/9)*100:.1f}%",
            },
            "results": self.results,
        }

        # Save report
        report_file = self.output_dir / "unified_test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        logger.info("\n")
        logger.info("=" * 80)
        logger.info("UNIFIED MCP TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Primary Stock:    {self.primary}")
        logger.info(f"Comparison Stock: {self.comparison}")
        logger.info(f"Period:           {self.period}")
        logger.info("")
        logger.info(f"Total Tests:      9")
        logger.info(f"Passed:           {passed}")
        logger.info(f"Errors:           {errors}")
        logger.info(f"Success Rate:     {(passed/9)*100:.1f}%")
        logger.info("")
        logger.info(f"API Fetches:      {self.cache.get_fetch_count()}")
        logger.info("")
        logger.info(f"📊 Report: {report_file}")
        logger.info(f"📁 Baselines: {self.baseline_dir}")
        logger.info("=" * 80)

        if passed == 9:
            logger.info("✅ ALL 9 TESTS PASSED!")
        else:
            logger.warning(f"⚠️ {errors} test(s) failed")

        # Print individual results
        logger.info("\nTest Results:")
        for tool, result in self.results.items():
            status = "✅" if result.get("status") == "success" else "❌"
            logger.info(f"  {status} {tool}")


async def main():
    """Run unified MCP test"""
    test = UnifiedMCPTest()
    await test.run_all_tests()

    print("\n" + "=" * 80)
    print("UNIFIED MCP TEST COMPLETE")
    print("=" * 80)
    print(f"Results: {test.output_dir}")
    print(f"Config:  test_config.py (edit to change parameters)")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Test interrupted")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
