#!/usr/bin/env python3
"""
Quick Regression Test - Single Stock (MU) with Minimal API Calls

Purpose: Validate regression testing framework without hitting rate limits
- Uses MU (Micron Technology) stock only
- Single API attempt (no retries)
- Fast execution for testing framework
- Establishes baseline with minimal data

Usage:
  mamba activate fin-ai1
  python quick_regression_test.py
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_dir = Path(__file__).parent / "nu-logs" / f"quick_test_{timestamp}"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "quick_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add mcp-finance1 to path
sys.path.insert(0, str(Path(__file__).parent / "mcp-finance1"))

from src.technical_analysis_mcp.server import (
    analyze_security,
    compare_securities,
    get_trade_plan,
)


class QuickRegressionTest:
    """Lightweight regression test with single stock (MU)"""

    def __init__(self, output_dir: Path = log_dir):
        """Initialize quick test"""
        self.output_dir = output_dir
        self.baseline_dir = self.output_dir / "baselines"
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

        self.results = {}
        self.timestamp = timestamp

        # Minimal swing trading config
        self.config = {
            "stock": "MU",
            "period": "3mo",
            "test_type": "quick",
            "api_attempts": 1,
        }

    def save_baseline(self, test_name: str, result: Dict[str, Any]) -> None:
        """Save result as baseline"""
        baseline_file = self.baseline_dir / f"{test_name}_baseline.json"
        with open(baseline_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"✅ Saved baseline for {test_name}")

    async def test_analyze_security(self) -> None:
        """Test analyze_security with MU"""
        logger.info("=" * 80)
        logger.info("TEST 1: analyze_security (MU stock)")
        logger.info("=" * 80)

        try:
            result = await analyze_security(
                symbol="MU",
                period="3mo",
                use_ai=False,
            )

            self.results["analyze_security"] = {
                "status": "success",
                "symbol": result.get("symbol"),
                "signal_count": len(result.get("signals", [])),
                "price": result.get("price"),
            }

            self.save_baseline("analyze_security", result)
            logger.info(f"✅ analyze_security completed: {len(result.get('signals', []))} signals")

        except Exception as e:
            logger.error(f"❌ analyze_security failed: {e}")
            self.results["analyze_security"] = {"status": "error", "error": str(e)}

    async def test_compare_securities(self) -> None:
        """Test compare_securities with MU and peers"""
        logger.info("=" * 80)
        logger.info("TEST 2: compare_securities (MU vs peers)")
        logger.info("=" * 80)

        try:
            result = await compare_securities(
                symbols=["MU", "SK", "NAND"],  # MU and memory chip competitors
                metric="signals",
                period="3mo",
            )

            self.results["compare_securities"] = {
                "status": "success",
                "winner": result.get("winner", {}).get("symbol"),
                "winner_score": result.get("winner", {}).get("score"),
            }

            self.save_baseline("compare_securities", result)
            logger.info(f"✅ compare_securities completed: winner={result.get('winner', {}).get('symbol')}")

        except Exception as e:
            logger.error(f"❌ compare_securities failed: {e}")
            self.results["compare_securities"] = {"status": "error", "error": str(e)}

    async def test_get_trade_plan(self) -> None:
        """Test get_trade_plan with MU"""
        logger.info("=" * 80)
        logger.info("TEST 3: get_trade_plan (MU)")
        logger.info("=" * 80)

        try:
            result = await get_trade_plan(
                symbol="MU",
                period="3mo",
            )

            self.results["get_trade_plan"] = {
                "status": "success",
                "symbol": result.get("symbol"),
                "plans": len(result.get("plans", [])),
            }

            self.save_baseline("get_trade_plan", result)
            logger.info(f"✅ get_trade_plan completed: {len(result.get('plans', []))} plans")

        except Exception as e:
            logger.error(f"❌ get_trade_plan failed: {e}")
            self.results["get_trade_plan"] = {"status": "error", "error": str(e)}

    async def run_tests(self) -> None:
        """Run all tests"""
        logger.info("")
        logger.info("🚀 Quick Regression Test - MU Stock Only")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {self.timestamp}")
        logger.info(f"Stock: MU (Micron Technology)")
        logger.info(f"Period: 3mo")
        logger.info(f"API Attempts: 1 (minimal)")
        logger.info("")

        # Run tests sequentially (not parallel for single stock)
        await self.test_analyze_security()
        await self.test_compare_securities()
        await self.test_get_trade_plan()

        self.generate_report()

    def generate_report(self) -> None:
        """Generate test report"""
        report = {
            "timestamp": self.timestamp,
            "test_type": "quick",
            "stock": "MU",
            "config": self.config,
            "test_summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results.values() if r.get("status") == "success"),
                "errors": sum(1 for r in self.results.values() if r.get("status") == "error"),
            },
            "results": self.results,
        }

        # Save report
        report_file = self.output_dir / "quick_test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("")
        logger.info("=" * 80)
        logger.info("QUICK TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {report['test_summary']['total_tests']}")
        logger.info(f"Passed: {report['test_summary']['passed']}")
        logger.info(f"Errors: {report['test_summary']['errors']}")
        logger.info("")
        logger.info(f"📊 Report saved to: {report_file}")
        logger.info(f"📁 Baselines saved to: {self.baseline_dir}")
        logger.info("")

        if report['test_summary']['passed'] == report['test_summary']['total_tests']:
            logger.info("✅ All tests passed!")
        else:
            logger.warning(f"⚠️ {report['test_summary']['errors']} test(s) failed")


async def main():
    """Run quick test"""
    test = QuickRegressionTest()
    await test.run_tests()

    print("\n" + "=" * 80)
    print("QUICK REGRESSION TEST COMPLETE")
    print("=" * 80)
    print(f"Results: {test.output_dir}")
    print(f"Baselines: {test.baseline_dir}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
