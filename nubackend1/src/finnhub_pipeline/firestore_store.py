"""Firestore storage layer for options and candle data.

Stores data in Firestore collections organized by:
  - options_chains/{symbol}/expirations/{date} -> calls and puts
  - options_quotes/{symbol} -> current quote snapshot
  - candle_data/{symbol}/intervals/{interval} -> OHLCV candles
  - pipeline_runs/{run_id} -> pipeline execution metadata
"""

import logging
from datetime import datetime, timezone
from typing import Any

from google.cloud import firestore

logger = logging.getLogger(__name__)

BATCH_LIMIT = 450


class FirestoreOptionsStore:
    """Store options chain and candle data in Firestore."""

    def __init__(
        self,
        project_id: str = "ttb-lang1",
        store_contracts: bool = False,
        max_expirations: int | None = 3,
    ) -> None:
        self._db = firestore.Client(project=project_id)
        self._store_contracts = store_contracts
        self._max_expirations = max_expirations
        logger.info(
            "Firestore connected to project: %s "
            "(store_contracts=%s, max_expirations=%d)",
            project_id,
            store_contracts,
            max_expirations,
        )

    def store_options_chain(self, chain_data: dict[str, Any]) -> int:
        """Store options chain in Firestore (optimized for minimal document count).

        By default (store_contracts=False), stores ONLY expiration summaries:
          options_chains/{symbol} -> metadata
          options_chains/{symbol}/expirations/{date} -> expiration summary with array of contracts

        Optionally can store individual contracts as nested documents:
          options_chains/{symbol}/expirations/{date}/calls/{strike} -> call data
          options_chains/{symbol}/expirations/{date}/puts/{strike} -> put data

        Args:
            chain_data: Options chain dict from FinnhubOptionsClient.

        Returns:
            Number of documents written.
        """
        symbol = chain_data["symbol"]
        now = datetime.now(tz=timezone.utc).isoformat()
        docs_written = 0

        # Store symbol metadata
        symbol_ref = self._db.collection("options_chains").document(symbol)
        symbol_ref.set({
            "symbol": symbol,
            "exchange": chain_data.get("exchange"),
            "last_trade_price": chain_data.get("last_trade_price"),
            "last_trade_date": chain_data.get("last_trade_date"),
            "num_expirations": chain_data.get("num_expirations"),
            "total_calls": chain_data.get("total_calls"),
            "total_puts": chain_data.get("total_puts"),
            "max_expirations_stored": self._max_expirations,
            "fetched_at": now,
        })
        docs_written += 1

        # Store only nearest N expirations (or all if max_expirations=None)
        expirations = chain_data.get("expirations", [])
        expirations_to_store = (
            expirations
            if self._max_expirations is None
            else expirations[:self._max_expirations]
        )

        for exp in expirations_to_store:
            exp_date = exp["expiration_date"]
            exp_ref = symbol_ref.collection("expirations").document(exp_date)

            # Build expiration summary document
            exp_summary = {
                "expiration_date": exp_date,
                "implied_volatility": exp.get("implied_volatility"),
                "put_volume": exp.get("put_volume"),
                "call_volume": exp.get("call_volume"),
                "put_call_volume_ratio": exp.get("put_call_volume_ratio"),
                "put_open_interest": exp.get("put_open_interest"),
                "call_open_interest": exp.get("call_open_interest"),
                "put_call_oi_ratio": exp.get("put_call_oi_ratio"),
                "options_count": exp.get("options_count"),
                "num_calls": len(exp.get("calls", [])),
                "num_puts": len(exp.get("puts", [])),
                "fetched_at": now,
            }

            # Option 1: Store contracts as embedded arrays (minimal documents)
            if not self._store_contracts:
                exp_summary["calls"] = exp.get("calls", [])
                exp_summary["puts"] = exp.get("puts", [])
                exp_ref.set(exp_summary)
                docs_written += 1
                logger.info(
                    "Stored %s/%s: summary + %d calls + %d puts (embedded)",
                    symbol,
                    exp_date,
                    len(exp.get("calls", [])),
                    len(exp.get("puts", [])),
                )
            # Option 2: Store contracts as separate documents (original behavior)
            else:
                exp_ref.set(exp_summary)
                docs_written += 1

                docs_written += self._batch_write_contracts(
                    exp_ref.collection("calls"),
                    exp.get("calls", []),
                )
                docs_written += self._batch_write_contracts(
                    exp_ref.collection("puts"),
                    exp.get("puts", []),
                )
                logger.info(
                    "Stored %s/%s: summary + %d individual contracts (nested)",
                    symbol,
                    exp_date,
                    docs_written - 1,
                )

        logger.info(
            "Stored options chain for %s: %d documents "
            "(%d/%d expirations, contracts: %s)",
            symbol,
            docs_written,
            len(expirations_to_store),
            chain_data.get("num_expirations", 0),
            "embedded" if not self._store_contracts else "nested",
        )
        return docs_written

    def store_quote(self, quote_data: dict[str, Any]) -> None:
        """Store a current quote snapshot.

        Args:
            quote_data: Quote dict from FinnhubOptionsClient.
        """
        symbol = quote_data["symbol"]
        now = datetime.now(tz=timezone.utc).isoformat()

        self._db.collection("options_quotes").document(symbol).set({
            **quote_data,
            "fetched_at": now,
        })
        logger.info("Stored quote for %s", symbol)

    def store_candle_data(self, symbol: str, interval_data: dict[str, Any]) -> int:
        """Store candle data for one interval.

        Creates documents at:
          candle_data/{symbol}/intervals/{interval} -> metadata + candle array

        Args:
            symbol: Ticker symbol.
            interval_data: Candle data dict from CandleFetcher.

        Returns:
            Number of documents written.
        """
        interval = interval_data.get("interval", "unknown")
        now = datetime.now(tz=timezone.utc).isoformat()

        doc_ref = (
            self._db.collection("candle_data")
            .document(symbol)
            .collection("intervals")
            .document(interval)
        )

        doc_ref.set({
            "symbol": symbol,
            "interval": interval,
            "status": interval_data.get("status"),
            "error": interval_data.get("error"),
            "num_candles": interval_data.get("num_candles", 0),
            "candles": interval_data.get("candles", []),
            "fetched_at": now,
        })

        symbol_ref = self._db.collection("candle_data").document(symbol)
        symbol_ref.set(
            {"symbol": symbol, "last_updated": now},
            merge=True,
        )

        logger.info(
            "Stored %s candle data for %s: %d candles",
            interval,
            symbol,
            interval_data.get("num_candles", 0),
        )
        return 1

    def store_pipeline_run(self, run_data: dict[str, Any]) -> str:
        """Store pipeline run metadata.

        Args:
            run_data: Pipeline run summary.

        Returns:
            Document ID of the stored run.
        """
        now = datetime.now(tz=timezone.utc).isoformat()
        run_data["created_at"] = now

        _, doc_ref = self._db.collection("pipeline_runs").add(run_data)
        logger.info("Stored pipeline run: %s", doc_ref.id)
        return doc_ref.id

    def _batch_write_contracts(
        self,
        collection_ref: Any,
        contracts: list[dict[str, Any]],
    ) -> int:
        """Write contracts in batches to avoid Firestore limits.

        Args:
            collection_ref: Firestore collection reference.
            contracts: List of contract dicts.

        Returns:
            Number of documents written.
        """
        written = 0
        batch = self._db.batch()
        batch_count = 0

        for contract in contracts:
            doc_id = str(contract.get("strike", written))
            doc_ref = collection_ref.document(doc_id)
            batch.set(doc_ref, contract)
            batch_count += 1
            written += 1

            if batch_count >= BATCH_LIMIT:
                batch.commit()
                batch = self._db.batch()
                batch_count = 0

        if batch_count > 0:
            batch.commit()

        return written
