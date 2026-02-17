#!/usr/bin/env python3
"""
MU Call Credit Spread Analysis
Analyze risk for selling a 90-94 call credit spread on Micron (MU)

A call credit spread (bear call spread):
- SELL the lower strike call (90) - collect premium
- BUY the higher strike call (94) - pay premium for protection
- Net credit received = premium collected

This is a BEARISH strategy - profits if MU stays below short strike (90)
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import yfinance as yf
import google.generativeai as genai


def fetch_with_retry(ticker: yf.Ticker, method: str, *args, max_retries: int = 3, **kwargs):
    """Fetch data with retry logic for rate limiting."""
    for attempt in range(max_retries):
        try:
            func = getattr(ticker, method)
            return func(*args, **kwargs)
        except Exception as e:
            if "Rate" in str(e) or "429" in str(e):
                wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                print(f"   Rate limited, waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")


# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def analyze_mu_call_credit_spread() -> dict[str, Any]:
    """
    Analyze MU 90-94 call credit spread.

    Strategy: SELL 90 call, BUY 94 call (bear call spread)
    """
    print("=" * 70)
    print("MU CALL CREDIT SPREAD ANALYSIS")
    print("Strategy: SELL 90 Call / BUY 94 Call (Bear Call Spread)")
    print("=" * 70)

    # Fetch MU data
    print("\n[1/5] Fetching MU stock data...")
    mu = yf.Ticker("MU")

    # Get current price with retry
    hist = fetch_with_retry(mu, "history", period="1d")
    if hist.empty:
        raise ValueError("Could not fetch MU price data")

    current_price = float(hist["Close"].iloc[-1])
    print(f"   Current MU Price: ${current_price:.2f}")

    # Get options expirations
    print("\n[2/5] Fetching options chain...")
    time.sleep(2)  # Small delay to avoid rate limits
    expirations = mu.options
    if not expirations:
        raise ValueError("No options expirations available for MU")

    # Find expiration ~30-45 days out (ideal for credit spreads)
    today = datetime.now()
    target_dte = 30  # Days to expiration

    best_exp = None
    best_dte_diff = float('inf')

    for exp in expirations:
        exp_date = datetime.strptime(exp, "%Y-%m-%d")
        dte = (exp_date - today).days
        if 20 <= dte <= 60:  # Look for 20-60 DTE
            if abs(dte - target_dte) < best_dte_diff:
                best_dte_diff = abs(dte - target_dte)
                best_exp = exp

    if not best_exp:
        best_exp = expirations[0]  # Fallback to nearest

    exp_date = datetime.strptime(best_exp, "%Y-%m-%d")
    dte = (exp_date - today).days
    print(f"   Selected Expiration: {best_exp} ({dte} DTE)")

    # Get options chain for selected expiration
    opt_chain = mu.option_chain(best_exp)
    calls = opt_chain.calls

    # Find the 90 and 94 strikes
    short_strike = 90.0  # SELL this call
    long_strike = 94.0   # BUY this call (protection)

    # Get closest available strikes
    available_strikes = calls["strike"].tolist()

    def find_closest_strike(target: float, strikes: list) -> float:
        return min(strikes, key=lambda x: abs(x - target))

    actual_short_strike = find_closest_strike(short_strike, available_strikes)
    actual_long_strike = find_closest_strike(long_strike, available_strikes)

    print(f"\n[3/5] Analyzing spread strikes...")
    print(f"   Short Strike (SELL): ${actual_short_strike:.2f}")
    print(f"   Long Strike (BUY):   ${actual_long_strike:.2f}")

    # Get option data for each leg
    short_call = calls[calls["strike"] == actual_short_strike].iloc[0]
    long_call = calls[calls["strike"] == actual_long_strike].iloc[0]

    # Calculate spread metrics
    short_premium = float(short_call["lastPrice"])  # Premium received
    long_premium = float(long_call["lastPrice"])    # Premium paid
    net_credit = short_premium - long_premium

    spread_width = actual_long_strike - actual_short_strike
    max_profit = net_credit * 100  # Per contract (100 shares)
    max_loss = (spread_width - net_credit) * 100
    breakeven = actual_short_strike + net_credit

    # Risk/reward ratio
    risk_reward = max_loss / max_profit if max_profit > 0 else float('inf')

    # Probability calculations (simplified)
    # Distance from current price to short strike
    distance_to_short = actual_short_strike - current_price
    distance_percent = (distance_to_short / current_price) * 100

    print(f"\n[4/5] Calculating risk metrics...")

    # Build analysis result
    analysis = {
        "symbol": "MU",
        "current_price": current_price,
        "strategy": "Call Credit Spread (Bear Call)",
        "expiration": best_exp,
        "dte": dte,
        "legs": {
            "short_leg": {
                "action": "SELL",
                "strike": actual_short_strike,
                "premium": short_premium,
                "bid": float(short_call["bid"]),
                "ask": float(short_call["ask"]),
                "volume": int(short_call["volume"]) if short_call["volume"] == short_call["volume"] else 0,
                "open_interest": int(short_call["openInterest"]) if short_call["openInterest"] == short_call["openInterest"] else 0,
                "implied_volatility": float(short_call["impliedVolatility"]) * 100,
            },
            "long_leg": {
                "action": "BUY",
                "strike": actual_long_strike,
                "premium": long_premium,
                "bid": float(long_call["bid"]),
                "ask": float(long_call["ask"]),
                "volume": int(long_call["volume"]) if long_call["volume"] == long_call["volume"] else 0,
                "open_interest": int(long_call["openInterest"]) if long_call["openInterest"] == long_call["openInterest"] else 0,
                "implied_volatility": float(long_call["impliedVolatility"]) * 100,
            },
        },
        "risk_metrics": {
            "net_credit": net_credit,
            "net_credit_per_contract": max_profit,
            "spread_width": spread_width,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "breakeven": breakeven,
            "risk_reward_ratio": f"1:{1/risk_reward:.2f}" if risk_reward > 0 else "N/A",
            "profit_probability_estimate": f"{min(95, max(20, 50 + distance_percent * 2)):.0f}%",
        },
        "position_analysis": {
            "current_vs_short_strike": f"${distance_to_short:.2f} {'below' if distance_to_short > 0 else 'above'}",
            "distance_percent": f"{distance_percent:.1f}%",
            "position_status": "OTM (Profitable Zone)" if current_price < actual_short_strike else "ITM (At Risk)",
            "margin_requirement_estimate": max_loss,  # Simplified
        },
        "greeks_summary": {
            "net_delta": -(float(short_call.get("delta", 0) or 0)) + float(long_call.get("delta", 0) or 0),
            "short_leg_iv": float(short_call["impliedVolatility"]) * 100,
            "long_leg_iv": float(long_call["impliedVolatility"]) * 100,
            "iv_skew": (float(long_call["impliedVolatility"]) - float(short_call["impliedVolatility"])) * 100,
        },
        "scenarios": [
            {
                "scenario": f"MU at ${actual_short_strike - 5:.2f} at expiration",
                "result": f"MAX PROFIT: +${max_profit:.2f}",
                "explanation": "Both calls expire worthless, keep full credit"
            },
            {
                "scenario": f"MU at ${breakeven:.2f} at expiration",
                "result": "BREAKEVEN: $0.00",
                "explanation": "Short call ITM but offset by credit received"
            },
            {
                "scenario": f"MU at ${actual_long_strike + 5:.2f} at expiration",
                "result": f"MAX LOSS: -${max_loss:.2f}",
                "explanation": "Both calls ITM, spread at max width"
            },
        ],
    }

    # Print summary
    print("\n" + "=" * 70)
    print("SPREAD ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"\n📊 POSITION:")
    print(f"   SELL {actual_short_strike} Call @ ${short_premium:.2f}")
    print(f"   BUY  {actual_long_strike} Call @ ${long_premium:.2f}")
    print(f"   Net Credit: ${net_credit:.2f} per share (${max_profit:.2f} per contract)")

    print(f"\n💰 RISK/REWARD:")
    print(f"   Max Profit: ${max_profit:.2f} (if MU < ${actual_short_strike:.2f})")
    print(f"   Max Loss:   ${max_loss:.2f} (if MU > ${actual_long_strike:.2f})")
    print(f"   Breakeven:  ${breakeven:.2f}")
    print(f"   Risk/Reward: {analysis['risk_metrics']['risk_reward_ratio']}")

    print(f"\n📍 CURRENT POSITION:")
    print(f"   MU Price: ${current_price:.2f}")
    print(f"   Status: {analysis['position_analysis']['position_status']}")
    print(f"   Distance to Short Strike: {analysis['position_analysis']['current_vs_short_strike']}")

    # AI Analysis
    print("\n[5/5] Getting AI analysis...")
    ai_analysis = await get_ai_analysis(analysis)
    analysis["ai_insights"] = ai_analysis

    return analysis


async def get_ai_analysis(data: dict) -> dict[str, Any]:
    """Get Gemini AI analysis of the spread."""

    if not GEMINI_API_KEY:
        return {
            "status": "unavailable",
            "message": "GEMINI_API_KEY not configured. Set environment variable for AI analysis.",
        }

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are an expert options trader analyzing a call credit spread. Provide a comprehensive risk analysis.

POSITION DETAILS:
- Symbol: MU (Micron Technology)
- Current Price: ${data['current_price']:.2f}
- Strategy: Call Credit Spread (Bear Call)
- Expiration: {data['expiration']} ({data['dte']} days)

SPREAD STRUCTURE:
- SELL {data['legs']['short_leg']['strike']} Call @ ${data['legs']['short_leg']['premium']:.2f}
- BUY {data['legs']['long_leg']['strike']} Call @ ${data['legs']['long_leg']['premium']:.2f}
- Net Credit: ${data['risk_metrics']['net_credit']:.2f}

RISK METRICS:
- Max Profit: ${data['risk_metrics']['max_profit']:.2f}
- Max Loss: ${data['risk_metrics']['max_loss']:.2f}
- Breakeven: ${data['risk_metrics']['breakeven']:.2f}
- Current Position: {data['position_analysis']['position_status']}

IMPLIED VOLATILITY:
- Short Leg IV: {data['greeks_summary']['short_leg_iv']:.1f}%
- Long Leg IV: {data['greeks_summary']['long_leg_iv']:.1f}%

Please provide:
1. TRADE ASSESSMENT (1-2 sentences): Is this a good entry? Rate the setup.
2. KEY RISKS (2-3 bullet points): What could go wrong?
3. PROFIT PROBABILITY: Estimate likelihood of profit based on position.
4. MANAGEMENT RECOMMENDATIONS: When to close, adjust, or hold?
5. VERDICT: ENTER / WAIT / AVOID with brief reasoning.

Format your response as structured JSON with these keys: assessment, risks, probability, management, verdict"""

        response = model.generate_content(prompt)
        response_text = response.text

        # Try to parse as JSON
        try:
            # Clean up response if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            ai_result = json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Return as raw analysis if not valid JSON
            ai_result = {
                "raw_analysis": response_text,
                "parse_status": "returned_as_text"
            }

        print("\n" + "=" * 70)
        print("🤖 AI ANALYSIS (Gemini)")
        print("=" * 70)

        if isinstance(ai_result, dict):
            if "assessment" in ai_result:
                print(f"\n📋 ASSESSMENT: {ai_result.get('assessment', 'N/A')}")
            if "risks" in ai_result:
                print(f"\n⚠️  RISKS:")
                risks = ai_result.get('risks', [])
                if isinstance(risks, list):
                    for risk in risks:
                        print(f"   • {risk}")
                else:
                    print(f"   {risks}")
            if "probability" in ai_result:
                print(f"\n📊 PROFIT PROBABILITY: {ai_result.get('probability', 'N/A')}")
            if "management" in ai_result:
                print(f"\n🎯 MANAGEMENT: {ai_result.get('management', 'N/A')}")
            if "verdict" in ai_result:
                print(f"\n✅ VERDICT: {ai_result.get('verdict', 'N/A')}")
            if "raw_analysis" in ai_result:
                print(f"\n{ai_result['raw_analysis']}")

        return {
            "status": "success",
            "model": "gemini-1.5-flash",
            "analysis": ai_result,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


async def main():
    """Run the analysis."""
    try:
        result = await analyze_mu_call_credit_spread()

        # Save results to file
        output_file = "mu_spread_analysis_result.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n✅ Full analysis saved to: {output_file}")
        print("=" * 70)

        return result

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
