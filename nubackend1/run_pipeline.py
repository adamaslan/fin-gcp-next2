#!/usr/bin/env python3
"""Run the Finnhub options pipeline.

Fetches options chain data from Finnhub and historical candle data
(Finnhub primary, Alpha Vantage fallback) for target symbols,
then stores everything in Firestore.

Usage:
    python run_pipeline.py                          # All 5 default tickers
    python run_pipeline.py --symbols AEM CRM        # Specific tickers
    python run_pipeline.py --no-candles             # Options chain only
    python run_pipeline.py --symbols QBTS --single  # Single symbol detail
"""

import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from finnhub_pipeline.pipeline import OptionsPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Finnhub Options Pipeline -> Firestore"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["AEM", "CRM", "IGV", "QBTS", "JPM"],
        help="Ticker symbols to process (default: AEM CRM IGV QBTS JPM)",
    )
    parser.add_argument(
        "--no-candles",
        action="store_true",
        help="Skip historical candle data (options chain only)",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Run single-symbol mode with detailed output",
    )
    parser.add_argument(
        "--project",
        default="ttb-lang1",
        help="GCP project ID for Firestore (default: ttb-lang1)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between candle API calls in seconds (default: 1.5)",
    )
    parser.add_argument(
        "--store-contracts",
        action="store_true",
        help="Store individual contracts as separate documents (original behavior, slower)",
    )
    parser.add_argument(
        "--max-expirations",
        type=int,
        default=3,
        help="Maximum number of expirations to store (default: 3, use 0 for all)",
    )
    args = parser.parse_args()

    finnhub_key = os.getenv("FINHUB_API_KEY")
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")

    if not finnhub_key:
        logger.error("FINHUB_API_KEY environment variable required")
        sys.exit(1)

    if not alpha_vantage_key:
        logger.warning(
            "ALPHA_VANTAGE_KEY not set - Alpha Vantage fallback disabled"
        )
        alpha_vantage_key = ""

    # Handle max_expirations: 0 = unlimited
    max_expirations = None if args.max_expirations == 0 else args.max_expirations

    pipeline = OptionsPipeline(
        finnhub_key=finnhub_key,
        alpha_vantage_key=alpha_vantage_key,
        gcp_project=args.project,
        store_contracts=args.store_contracts,
        max_expirations=max_expirations,
    )

    try:
        if args.single and len(args.symbols) == 1:
            result = pipeline.run_single(
                symbol=args.symbols[0],
                fetch_candles=not args.no_candles,
                candle_delay=args.delay,
            )
        else:
            result = pipeline.run(
                symbols=args.symbols,
                fetch_candles=not args.no_candles,
                candle_delay=args.delay,
            )

        print("\n" + "=" * 60)
        print("PIPELINE RESULTS")
        print("=" * 60)
        print(json.dumps(result, indent=2, default=str))

    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
