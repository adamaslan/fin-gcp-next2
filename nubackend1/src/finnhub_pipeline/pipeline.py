"""Options data pipeline orchestrator.

Coordinates fetching options chain data from Finnhub, historical candle data
from Finnhub/Alpha Vantage, and storing everything in Firestore.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any

from .candle_fetcher import CandleFetcher
from .finnhub_client import FinnhubOptionsClient
from .firestore_store import FirestoreOptionsStore

logger = logging.getLogger(__name__)

DEFAULT_TICKERS = ["AEM", "CRM", "IGV", "QBTS", "JPM"]


class OptionsPipeline:
    """Orchestrate options chain + candle data fetch and Firestore storage."""

    def __init__(
        self,
        finnhub_key: str,
        alpha_vantage_key: str,
        gcp_project: str = "ttb-lang1",
        store_contracts: bool = False,
        max_expirations: int | None = 3,
    ) -> None:
        self._options_client = FinnhubOptionsClient(api_key=finnhub_key)
        self._candle_fetcher = CandleFetcher(
            finnhub_key=finnhub_key,
            alpha_vantage_key=alpha_vantage_key,
        )
        self._store = FirestoreOptionsStore(
            project_id=gcp_project,
            store_contracts=store_contracts,
            max_expirations=max_expirations,
        )
        logger.info(
            "Pipeline initialized (Finnhub + Alpha Vantage -> Firestore/%s) "
            "store_contracts=%s max_expirations=%d",
            gcp_project,
            store_contracts,
            max_expirations,
        )

    def run(
        self,
        symbols: list[str] | None = None,
        fetch_candles: bool = True,
        candle_delay: float = 1.5,
    ) -> dict[str, Any]:
        """Run the full pipeline for all symbols.

        Args:
            symbols: List of ticker symbols. Defaults to AEM, CRM, IGV, QBTS, JPM.
            fetch_candles: Whether to fetch historical candle data.
            candle_delay: Delay between candle API calls (rate limit).

        Returns:
            Pipeline run summary with per-symbol results.
        """
        symbols = symbols or DEFAULT_TICKERS
        start_time = time.time()
        run_start = datetime.now(tz=timezone.utc).isoformat()

        logger.info("Pipeline starting for %d symbols: %s", len(symbols), symbols)

        results: dict[str, Any] = {}

        for symbol in symbols:
            symbol_result = self._process_symbol(
                symbol, fetch_candles, candle_delay
            )
            results[symbol] = symbol_result
            time.sleep(0.5)

        elapsed = round(time.time() - start_time, 2)

        summary = {
            "status": "completed",
            "started_at": run_start,
            "completed_at": datetime.now(tz=timezone.utc).isoformat(),
            "elapsed_seconds": elapsed,
            "symbols_processed": len(symbols),
            "symbols": symbols,
            "results": results,
        }

        run_id = self._store.store_pipeline_run(summary)
        summary["run_id"] = run_id

        logger.info(
            "Pipeline complete: %d symbols in %.1fs (run_id=%s)",
            len(symbols),
            elapsed,
            run_id,
        )
        return summary

    def run_single(
        self,
        symbol: str,
        fetch_candles: bool = True,
        candle_delay: float = 1.5,
    ) -> dict[str, Any]:
        """Run the pipeline for a single symbol.

        Args:
            symbol: Ticker symbol.
            fetch_candles: Whether to fetch historical candle data.
            candle_delay: Delay between candle API calls.

        Returns:
            Result dict for the symbol.
        """
        return self._process_symbol(symbol, fetch_candles, candle_delay)

    def _process_symbol(
        self,
        symbol: str,
        fetch_candles: bool,
        candle_delay: float,
    ) -> dict[str, Any]:
        """Process a single symbol: fetch + store options and candles."""
        result: dict[str, Any] = {"symbol": symbol}

        # Fetch and store options chain
        try:
            chain = self._options_client.fetch_option_chain(symbol)
            docs_written = self._store.store_options_chain(chain)
            result["options_chain"] = {
                "status": "ok",
                "expirations": chain["num_expirations"],
                "total_calls": chain["total_calls"],
                "total_puts": chain["total_puts"],
                "last_trade_price": chain["last_trade_price"],
                "docs_written": docs_written,
            }
            logger.info(
                "%s options: %d expirations, %d docs",
                symbol, chain["num_expirations"], docs_written,
            )
        except Exception as e:
            logger.error("Options chain error for %s: %s", symbol, e)
            result["options_chain"] = {"status": "error", "error": str(e)}

        # Fetch and store quote
        try:
            quote = self._options_client.fetch_quote(symbol)
            self._store.store_quote(quote)
            result["quote"] = {
                "status": "ok",
                "current": quote["current"],
                "change_percent": quote["change_percent"],
            }
        except Exception as e:
            logger.error("Quote error for %s: %s", symbol, e)
            result["quote"] = {"status": "error", "error": str(e)}

        # Fetch and store candle data
        if fetch_candles:
            try:
                candle_results = self._candle_fetcher.fetch_all_intervals(
                    symbol, delay=candle_delay
                )
                candle_summary: dict[str, Any] = {}

                for interval, candle_data in candle_results.items():
                    self._store.store_candle_data(symbol, candle_data)
                    candle_summary[interval] = {
                        "status": candle_data.get("status"),
                        "source": candle_data.get("source", "none"),
                        "num_candles": candle_data.get("num_candles", 0),
                    }
                    if candle_data.get("error"):
                        candle_summary[interval]["error"] = candle_data["error"]

                result["candles"] = candle_summary
            except Exception as e:
                logger.error("Candle data error for %s: %s", symbol, e)
                result["candles"] = {"status": "error", "error": str(e)}

        return result

    def close(self) -> None:
        """Clean up resources."""
        self._candle_fetcher.close()
