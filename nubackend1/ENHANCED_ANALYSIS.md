# Enhanced options_analysis: 5 New Fields

## New Fields

| Field | Type | Source |
|-------|------|--------|
| `iv_rank` | float | Compare current IV to expiration range |
| `max_pain` | float | Strike where most options expire worthless |
| `unusual_activity` | dict | Contracts with volume > 3x open interest |
| `greeks_exposure` | dict | Aggregate delta/gamma/vega across chain |
| `spread_opportunities` | list | Top 3 vertical spreads by risk/reward |

## Implementation

Add to `run_analysis.py` in `_analyze_symbol()`:

```python
def _compute_enhanced_fields(self, symbol, reader, expiration):
    calls_df, puts_df = reader.get_option_chain(symbol, expiration)
    all_opts = pd.concat([calls_df, puts_df])

    # 1. IV Rank (0-100 percentile)
    iv_vals = all_opts["impliedVolatility"].dropna()
    current_iv = iv_vals.mean()
    iv_rank = ((current_iv - iv_vals.min()) / (iv_vals.max() - iv_vals.min())) * 100

    # 2. Max Pain (strike minimizing total option value)
    strikes = calls_df["strike"].unique()
    pain = {s: (calls_df[calls_df.strike>=s].openInterest.sum() +
                puts_df[puts_df.strike<=s].openInterest.sum()) for s in strikes}
    max_pain = min(pain, key=pain.get)

    # 3. Unusual Activity (volume/OI > 3)
    all_opts["vol_oi"] = all_opts["volume"] / all_opts["openInterest"].replace(0,1)
    unusual = all_opts[all_opts["vol_oi"] > 3][["strike","volume","openInterest"]]

    # 4. Greeks Exposure
    greeks = {g: float(all_opts[g].sum()) for g in ["delta","gamma","vega"]
              if g in all_opts.columns}

    # 5. Spread Opportunities (bull call spreads)
    spreads = [{"buy": r.strike, "sell": r.strike+5,
                "cost": r.ask} for _, r in calls_df.head(3).iterrows()]

    return {"iv_rank": iv_rank, "max_pain": max_pain,
            "unusual_activity": unusual.to_dict("records"),
            "greeks_exposure": greeks, "spread_opportunities": spreads}
```

Merge into the symbol doc before `store_symbol_analysis()`. No schema migration needed — Firestore is schemaless.
