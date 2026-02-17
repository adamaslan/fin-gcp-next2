#!/usr/bin/env python3
"""
Quick MCP test - Tests all 9 MCP tools with minimal symbols to avoid rate limiting.
Also tests AI layer (Gemini) if GEMINI_API_KEY is set.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
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


async def test_all_mcp_tools():
    """Test all 9 MCP tools with minimal API calls."""
    results = {}
    test_symbol = "AAPL"  # Use single cached symbol to avoid rate limits

    print("\n" + "=" * 60)
    print("QUICK MCP TOOLS TEST - ALL 9 TOOLS")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test symbol: {test_symbol}")
    print(f"GEMINI_API_KEY set: {bool(os.environ.get('GEMINI_API_KEY'))}")
    print("=" * 60 + "\n")

    # Test 1: analyze_security (without AI)
    print("[1/10] Testing analyze_security (rule-based)...")
    try:
        result = await analyze_security(symbol=test_symbol, period="3mo", use_ai=False)
        results["analyze_security"] = {
            "status": "success",
            "signals": result.get("summary", {}).get("total_signals", 0),
            "avg_score": result.get("summary", {}).get("avg_score", 0),
            "price": result.get("price", 0),
        }
        print(f"   ✓ SUCCESS - {results['analyze_security']['signals']} signals, price=${results['analyze_security']['price']:.2f}")
    except Exception as e:
        results["analyze_security"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 1b: analyze_security WITH AI (if available)
    print("[1b/10] Testing analyze_security (WITH AI layer)...")
    try:
        result = await analyze_security(symbol=test_symbol, period="3mo", use_ai=True)
        results["analyze_security_ai"] = {
            "status": "success",
            "signals": result.get("summary", {}).get("total_signals", 0),
            "avg_score": result.get("summary", {}).get("avg_score", 0),
            "ai_enabled": True,
        }
        print(f"   ✓ SUCCESS - AI ranking applied, avg_score={results['analyze_security_ai']['avg_score']:.1f}")
    except Exception as e:
        results["analyze_security_ai"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 2: compare_securities
    print("[2/10] Testing compare_securities...")
    try:
        result = await compare_securities(
            symbols=["AAPL", "MSFT", "GOOGL"],
            metric="signals",
            period="3mo",
        )
        winner = result.get("winner", {})
        results["compare_securities"] = {
            "status": "success",
            "winner": winner.get("symbol") if winner else None,
            "compared": len(result.get("comparison", [])),
        }
        print(f"   ✓ SUCCESS - Winner: {results['compare_securities']['winner']}")
    except Exception as e:
        results["compare_securities"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 3: screen_securities (with very relaxed criteria)
    print("[3/10] Testing screen_securities (nasdaq100 - smaller universe)...")
    try:
        result = await screen_securities(
            universe="nasdaq100",  # Smaller universe
            criteria={"rsi": {"min": 10, "max": 90}},  # Very relaxed
            limit=5,  # Only top 5
            period="3mo",
        )
        results["screen_securities"] = {
            "status": "success",
            "matches": len(result.get("matches", [])),
        }
        print(f"   ✓ SUCCESS - {results['screen_securities']['matches']} matches found")
    except Exception as e:
        results["screen_securities"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 4: get_trade_plan
    print("[4/10] Testing get_trade_plan...")
    try:
        result = await get_trade_plan(symbol=test_symbol, period="3mo")
        results["get_trade_plan"] = {
            "status": "success",
            "has_trades": result.get("has_trades", False),
            "plans": len(result.get("trade_plans", [])),
        }
        print(f"   ✓ SUCCESS - has_trades={results['get_trade_plan']['has_trades']}, plans={results['get_trade_plan']['plans']}")
    except Exception as e:
        results["get_trade_plan"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 5: scan_trades (etf_large_cap - smallest universe)
    print("[5/10] Testing scan_trades (etf_large_cap - smallest universe)...")
    try:
        result = await scan_trades(
            universe="etf_large_cap",  # Smallest universe
            max_results=3,
            period="3mo",
        )
        results["scan_trades"] = {
            "status": "success",
            "qualified_trades": len(result.get("qualified_trades", [])),
        }
        print(f"   ✓ SUCCESS - {results['scan_trades']['qualified_trades']} qualified trades")
    except Exception as e:
        results["scan_trades"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 6: portfolio_risk
    print("[6/10] Testing portfolio_risk...")
    try:
        result = await portfolio_risk(
            positions=[
                {"symbol": "AAPL", "shares": 100, "entry_price": 150},
                {"symbol": "MSFT", "shares": 50, "entry_price": 380},
            ],
            period="3mo",
        )
        results["portfolio_risk"] = {
            "status": "success",
            "total_value": result.get("total_value", 0),
            "risk_level": result.get("overall_risk_level", "UNKNOWN"),
        }
        print(f"   ✓ SUCCESS - total_value=${results['portfolio_risk']['total_value']:,.2f}, risk={results['portfolio_risk']['risk_level']}")
    except Exception as e:
        results["portfolio_risk"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 7: morning_brief
    print("[7/10] Testing morning_brief...")
    try:
        result = await morning_brief(
            watchlist=["AAPL", "MSFT", "NVDA"],
            market_region="US",
            period="3mo",
        )
        results["morning_brief"] = {
            "status": "success",
            "signals_count": len(result.get("watchlist_signals", [])),
            "themes_count": len(result.get("key_themes", [])),
        }
        print(f"   ✓ SUCCESS - {results['morning_brief']['signals_count']} signals, {results['morning_brief']['themes_count']} themes")
    except Exception as e:
        results["morning_brief"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 8: analyze_fibonacci
    print("[8/10] Testing analyze_fibonacci (window=150)...")
    try:
        result = await analyze_fibonacci(
            symbol=test_symbol,
            period="3mo",
            window=150,  # Swing trading config
        )
        results["analyze_fibonacci"] = {
            "status": "success",
            "levels": len(result.get("levels", [])),
            "signals": len(result.get("signals", [])),
            "clusters": len(result.get("clusters", [])),
            "confluence_zones": len(result.get("confluenceZones", [])),
        }
        print(f"   ✓ SUCCESS - {results['analyze_fibonacci']['levels']} levels, {results['analyze_fibonacci']['signals']} signals, {results['analyze_fibonacci']['confluence_zones']} confluence zones")
    except Exception as e:
        results["analyze_fibonacci"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Test 9: options_risk_analysis
    print("[9/10] Testing options_risk_analysis (min_volume=75)...")
    try:
        result = await options_risk_analysis(
            symbol=test_symbol,
            option_type="both",
            min_volume=75,  # Swing trading config
        )
        results["options_risk_analysis"] = {
            "status": "success",
            "dte": result.get("days_to_expiration", 0),
            "pcr_volume": result.get("put_call_ratio", {}).get("volume"),
            "warnings": len(result.get("risk_warnings", [])),
            "opportunities": len(result.get("opportunities", [])),
        }
        print(f"   ✓ SUCCESS - DTE={results['options_risk_analysis']['dte']}, PCR={results['options_risk_analysis']['pcr_volume']:.2f if results['options_risk_analysis']['pcr_volume'] else 'N/A'}")
    except Exception as e:
        results["options_risk_analysis"] = {"status": "error", "error": str(e)}
        print(f"   ✗ ERROR: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    error_count = sum(1 for r in results.values() if r.get("status") == "error")
    total = len(results)

    print(f"Total tests: {total}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {success_count / total * 100:.0f}%")
    print()

    for tool, result in results.items():
        status = "✓" if result.get("status") == "success" else "✗"
        print(f"  {status} {tool}")

    print("=" * 60)

    # Save results
    output_file = Path(__file__).parent / "nu-logs" / f"quick_mcp_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    asyncio.run(test_all_mcp_tools())
