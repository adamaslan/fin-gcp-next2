#!/usr/bin/env python3
"""Verify Firestore optimization results.

Checks if the pipeline optimization was successful by analyzing:
- Document count before/after
- Storage format (embedded arrays vs nested documents)
- Document breakdown by type
"""

import json
from google.cloud import firestore


def main() -> None:
    db = firestore.Client(project="ttb-lang1")

    print("\n" + "=" * 70)
    print("FIRESTORE OPTIMIZATION VERIFICATION")
    print("=" * 70)

    # Count all documents
    total_docs = 0
    breakdown = {
        "symbols": 0,
        "expirations": 0,
        "calls_nested": 0,
        "puts_nested": 0,
        "calls_embedded": 0,
        "puts_embedded": 0,
        "quotes": 0,
        "candle_data": 0,
        "pipeline_runs": 0,
    }

    # Check options_chains
    print("\n📊 OPTIONS CHAINS ANALYSIS")
    print("-" * 70)

    options_chains = list(db.collection("options_chains").stream())
    breakdown["symbols"] = len(options_chains)
    total_docs += len(options_chains)

    for symbol_doc in options_chains:
        symbol = symbol_doc.id
        symbol_ref = symbol_doc.reference

        expirations = list(symbol_ref.collection("expirations").stream())
        breakdown["expirations"] += len(expirations)
        total_docs += len(expirations)

        for exp in expirations:
            exp_data = exp.to_dict()
            exp_date = exp.id

            # Check if contracts are embedded in the expiration document
            has_calls = "calls" in exp_data and isinstance(
                exp_data.get("calls"), list
            )
            has_puts = "puts" in exp_data and isinstance(
                exp_data.get("puts"), list
            )

            if has_calls:
                num_calls = len(exp_data["calls"])
                breakdown["calls_embedded"] += num_calls
                print(
                    f"✅ {symbol}/{exp_date}: "
                    f"{num_calls} calls EMBEDDED"
                )
            else:
                # Check for nested documents
                calls = list(symbol_ref.collection("expirations")
                           .document(exp_date)
                           .collection("calls")
                           .stream())
                num_calls = len(calls)
                breakdown["calls_nested"] += num_calls
                total_docs += num_calls
                if num_calls > 0:
                    print(
                        f"⚠️  {symbol}/{exp_date}: "
                        f"{num_calls} calls NESTED (not optimized)"
                    )

            if has_puts:
                num_puts = len(exp_data["puts"])
                breakdown["puts_embedded"] += num_puts
                print(
                    f"   {symbol}/{exp_date}: "
                    f"{num_puts} puts EMBEDDED"
                )
            else:
                puts = list(symbol_ref.collection("expirations")
                          .document(exp_date)
                          .collection("puts")
                          .stream())
                num_puts = len(puts)
                breakdown["puts_nested"] += num_puts
                total_docs += num_puts
                if num_puts > 0:
                    print(
                        f"   {symbol}/{exp_date}: "
                        f"{num_puts} puts NESTED (not optimized)"
                    )

    # Check other collections
    print("\n📈 OTHER COLLECTIONS")
    print("-" * 70)

    quotes = list(db.collection("options_quotes").stream())
    breakdown["quotes"] = len(quotes)
    total_docs += len(quotes)
    print(f"✅ options_quotes: {len(quotes)} documents")

    candle_docs = list(db.collection("candle_data").stream())
    breakdown["candle_data"] = len(candle_docs)
    total_docs += len(candle_docs)

    for candle in candle_docs:
        intervals = list(candle.reference.collection("intervals").stream())
        breakdown["candle_data"] += len(intervals)
        total_docs += len(intervals)

    print(f"✅ candle_data: {len(candle_docs)} symbols + {len(intervals)} intervals")

    runs = list(db.collection("pipeline_runs").stream())
    breakdown["pipeline_runs"] = len(runs)
    total_docs += len(runs)
    print(f"✅ pipeline_runs: {len(runs)} documents")

    # Calculate reduction
    print("\n" + "=" * 70)
    print("OPTIMIZATION RESULTS")
    print("=" * 70)

    # Estimate old count
    estimated_old = breakdown["symbols"] + breakdown["expirations"]
    estimated_old += breakdown["calls_nested"] + breakdown["puts_nested"]
    estimated_old += breakdown["quotes"] + breakdown["candle_data"]
    estimated_old += breakdown["pipeline_runs"]

    # If contracts are nested, estimate what they would be if embedded
    if breakdown["calls_nested"] > 0 or breakdown["puts_nested"] > 0:
        estimated_old += breakdown["calls_nested"] + breakdown["puts_nested"]
        print(
            f"⚠️  DETECTION: Contracts stored as NESTED documents (not optimized)"
        )
        print(f"   Expected behavior: Contracts should be EMBEDDED in expiration docs")
    else:
        print(f"✅ CONFIRMED: All contracts stored as EMBEDDED arrays (optimized)")

    print(f"\nDocument Breakdown:")
    print(f"  • Symbols:              {breakdown['symbols']}")
    print(f"  • Expirations:          {breakdown['expirations']}")
    print(f"  • Calls embedded:       {breakdown['calls_embedded']}")
    print(f"  • Puts embedded:        {breakdown['puts_embedded']}")
    print(f"  • Calls nested:         {breakdown['calls_nested']}")
    print(f"  • Puts nested:          {breakdown['puts_nested']}")
    print(f"  • Quotes:               {breakdown['quotes']}")
    print(f"  • Candle data:          {breakdown['candle_data']}")
    print(f"  • Pipeline runs:        {breakdown['pipeline_runs']}")
    print(f"  ─────────────────────────────────")
    print(f"  • TOTAL:                {total_docs}")

    # Estimate reduction vs original
    estimated_original = 4500
    reduction_percent = ((estimated_original - total_docs) / estimated_original) * 100

    print(f"\nOptimization Impact:")
    print(f"  • Original estimate:    ~{estimated_original} documents")
    print(f"  • Current total:        {total_docs} documents")
    print(f"  • Reduction:            {reduction_percent:.1f}%")

    if reduction_percent >= 90:
        print(f"  • Status:               ✅ EXCELLENT (target: 95%)")
    elif reduction_percent >= 80:
        print(f"  • Status:               ✅ GOOD")
    elif reduction_percent >= 50:
        print(f"  • Status:               ⚠️  MODERATE")
    else:
        print(f"  • Status:               ❌ NOT OPTIMIZED")

    print("\n" + "=" * 70)
    print("DETAILS")
    print("=" * 70)
    print(json.dumps(breakdown, indent=2))
    print("=" * 70)


if __name__ == "__main__":
    main()
