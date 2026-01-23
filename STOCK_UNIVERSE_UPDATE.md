# S&P 500 Stock Universe Expansion

**Date:** 2026-01-19
**File Updated:** `mcp-finance1/src/technical_analysis_mcp/universes.py`

## Summary

Expanded the S&P 500 stock universe from **54 curated stocks** to **250 stocks ranked by market capitalization**, providing significantly better coverage of the actual S&P 500 index.

## Changes Made

### Before
- **Universe Size:** 54 stocks
- **Composition:** Heavily weighted toward mega-cap tech and established blue-chips
- **Coverage:** ~11% of S&P 500 constituents
- **Scope:** Limited to largest and most liquid stocks

### After
- **Universe Size:** 250 stocks
- **Composition:** Top 250 stocks by market cap (as of 2026-01-19)
- **Coverage:** ~50% of S&P 500 constituents
- **Scope:** Representative sample across all major sectors

## Why the Original Universe Was Poorly Planned

The original 54-stock universe had several fundamental design flaws:

### 1. Arbitrary and Meaningless Size

**54 stocks is not a standard benchmark.** There's no logical reason to choose 54 over 50, 100, or any other number. Standard financial benchmarks use round numbers (Top 50, Top 100, S&P 100) for a reason - they're easy to communicate, compare, and track. Picking 54 suggests no methodology was applied; someone just stopped adding stocks when they got tired.

### 2. Not Sorted by Market Capitalization

The original list started with `AAPL, MSFT, GOOGL, AMZN, NVDA...` but **NVDA is actually the largest company by market cap**. The list wasn't even in the correct order, making it impossible to know what criteria (if any) were used for selection. A properly planned universe would be ranked by market cap, index weight, or some other defensible metric.

### 3. Missing Major Market Players

The 54-stock list excluded significant companies that should have been included:

| Missing Stock | Current Rank | Why It Matters |
|--------------|--------------|----------------|
| GOOG | #6 | Alphabet Class C - major liquidity |
| MU | #20 | Micron - major semiconductor |
| PLTR | #21 | Palantir - high-volume tech stock |
| BAC | #22 | Bank of America - 2nd largest US bank |
| GE | #27 | GE Aerospace - industrial bellwether |
| CAT | #31 | Caterpillar - economic indicator |
| MS | #33 | Morgan Stanley - major investment bank |
| GS | #35 | Goldman Sachs - market-moving bank |

These aren't obscure small-caps - they're top 40 companies by market cap that were inexplicably omitted.

### 4. No Selection Methodology or Documentation

The original `universes.py` file contained only this comment:

```python
"""Stock universe lists for screening.

Hardcoded lists of symbols organized by universe type.
Update quarterly from official sources.
"""
```

**No explanation of:**
- Why these 54 specific stocks were chosen
- What "official sources" to use for updates
- When the list was last updated
- What criteria determined inclusion/exclusion

This made the list impossible to maintain correctly or justify to stakeholders.

### 5. Stale Data with No Update Process

The comment says "update quarterly" but provides no mechanism to actually do this. The list was clearly outdated:

- **NVDA's rise:** NVIDIA became the world's largest company but was listed 5th
- **Missing new entrants:** PLTR, UBER, HOOD, COIN - all major recent additions to S&P 500
- **Market cap drift:** Companies like INTC have fallen significantly but remained while larger companies were excluded

Without a defined update process or data source, the list was doomed to become increasingly irrelevant over time.

---

**Bottom line:** The original universe appears to have been created by someone manually typing stock tickers from memory, with no systematic approach, no documentation, and no maintenance plan. For a financial application where data quality directly impacts trading decisions, this level of carelessness is unacceptable.

## Stock List Ranking

**By Market Cap (largest first):**

Top 10:
1. NVDA - NVIDIA
2. AAPL - Apple
3. MSFT - Microsoft
4. AMZN - Amazon
5. GOOGL - Alphabet
6. GOOG - Alphabet (Class C)
7. AVGO - Broadcom
8. META - Meta Platforms
9. TSLA - Tesla
10. BRK.B - Berkshire Hathaway

Last 10 (positions 241-250):
- VST, O, ADSK, DLR, FTNT, VLO, PSX, ZTS, F, PYPL

See complete list in `universes.py` lines 10-36.

## Sector Representation

The 250-stock universe includes:

- **Technology:** NVDA, AAPL, MSFT, AMZN, GOOGL, META, TSLA, INTC, AMD, ADBE, CRM, INTU, SNPS, ANET, FTNT, DDOG, etc.
- **Financials:** JPM, BAC, MS, GS, WFC, AXP, COF, ICE, CME, BLK, SCHW, KKR, APO, BX, etc.
- **Healthcare:** UNH, JNJ, LLY, TMO, ABT, MRK, ABBV, PFE, AZO, VRTX, REGN, ISRG, DXC, etc.
- **Energy:** XOM, CVX, COP, MPC, OXY, SLB, EOG, DVN, KMI, WMB, PSX, etc.
- **Consumer:** WMT, COST, PG, KO, PEP, MCD, SBUX, CMG, NKE, LULU, TJX, ROST, etc.
- **Industrials:** CAT, BA, RTX, HON, ITW, LMT, NOC, GD, ETN, ROK, AEE, etc.

## Impact on Stock Scanning

### Performance
- **Scan Time:** Will increase from ~11.7 seconds (54 stocks) to estimated 40-60 seconds (250 stocks)
- **Rate Limiting:** Maintained at 10 concurrent requests maximum
- **API Load:** ~4.6x increase in total API calls per scan

### Trade Discovery
- **More Opportunities:** Broader market coverage increases chance of finding qualified trades
- **Filtering:** Strict risk/reward filters still apply (MIN_RR_RATIO ~1.5)
- **Quality:** Results remain limited by `max_results` parameter (default: 10, max: 50)

### Scanner Configuration
Current MCP server settings:
```python
scan_trades(
    universe: str = "sp500",      # Now 250 stocks
    max_results: int = 10,        # Top 10 trades returned
)
```

Concurrency:
- Max concurrent requests: 10
- Semaphore-based rate limiting prevents API throttling
- Graceful error handling for failed requests

## Technical Details

### File Changes
**Location:** `/mcp-finance1/src/technical_analysis_mcp/universes.py`

```python
UNIVERSES: Final[dict[str, list[str]]] = {
    "sp500": [
        # 250 stocks ranked by market cap
        # Lines 10-36 in universes.py
    ],
    # ... other universes unchanged
}
```

### Data Source
- **Source:** SlickCharts S&P 500 by Market Cap (slickcharts.com/sp500/marketcap)
- **Date:** 2026-01-19
- **Ranking:** Market capitalization (largest to smallest)

### Filtering Logic (Unchanged)
The scanner still applies:
- **Risk/Reward Ratio Check:** MIN_RR_RATIO threshold (default ~1.5-2.5)
- **Stop Distance:** 0.5-3.0 ATR range
- **Invalidation Level:** Must exist for clear stop placement
- **Volatility Regime:** Rejects if HIGH volatility
- **Signal Conflicts:** Rejects if too many conflicting signals

## Recommendations

### For Daily Scans
- Consider scheduling scans during lower-traffic times
- Monitor API response times and adjust `max_concurrent` if needed
- Expected scan duration: 40-60 seconds per scan

### For Future Updates
- **Quarterly Updates:** Stock universe should be updated quarterly from official S&P 500 sources
- **Alternative Universes:** Consider creating "sp500_large_cap" (top 100) for faster scanning
- **Weighted Universe:** Could prioritize by market cap to scan most liquid first

## Backwards Compatibility

- **API Unchanged:** `scan_trades()` tool works identically
- **Other Universes:** nasdaq100, etf_large_cap, etf_sector, crypto, tech_leaders unchanged
- **Database:** No migrations required
- **Config:** No configuration changes needed

## Testing Notes

After deployment, verify:
- [ ] Scan completes successfully with 250 stocks
- [ ] Qualified trades are returned (may be fewer if market conditions are unfavorable)
- [ ] API response times are acceptable
- [ ] Error handling works for any failed requests
- [ ] Risk assessment filters are applied correctly

## Rollback Plan

If performance issues arise:
1. Revert to 54-stock universe: `git checkout mcp-finance1/src/technical_analysis_mcp/universes.py`
2. Or reduce to top 100 stocks for balance between coverage and speed
3. Or adjust `max_concurrent` from 10 to 5 for lighter API load

---

**Next Action:** Run a test scan with `universe="sp500"` to verify the expanded universe works correctly before deploying to production.
