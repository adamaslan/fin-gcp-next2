"""Firestore storage layer for options analysis results.

Stores consolidated analysis data in optimized collections:
  - options_analysis/{symbol}           -> all 4 tool results in 1 document
  - options_analysis_runs/{run_id}      -> run metadata and per-symbol status
"""

import logging
from typing import Any

from google.cloud import firestore

logger = logging.getLogger(__name__)


class FirestoreAnalysisStore:
    """Store options analysis results in Firestore.

    Writes consolidated per-symbol analysis (risk, summary, vehicle, comparison)
    into a single document per symbol, minimizing document count.
    """

    def __init__(self, project_id: str = "ttb-lang1") -> None:
        self._db = firestore.Client(project=project_id)
        logger.info("Analysis store connected to Firestore project: %s", project_id)

    def read_tracked_symbols(self) -> list[str]:
        """Read symbol IDs from the options_chains collection.

        Returns:
            List of ticker symbols currently tracked in Firestore.
        """
        docs = self._db.collection("options_chains").stream()
        symbols = [doc.id for doc in docs]
        logger.info(
            "Read %d tracked symbols from Firestore: %s", len(symbols), symbols
        )
        return symbols

    def store_symbol_analysis(self, symbol: str, data: dict[str, Any]) -> None:
        """Write or overwrite consolidated analysis for a single symbol.

        Args:
            symbol: Ticker symbol (used as document ID).
            data: Consolidated analysis dict with risk_analysis, summary,
                vehicle_recommendation, and comparison_rank.
        """
        self._db.collection("options_analysis").document(symbol).set(data)
        logger.info("Stored analysis for %s", symbol)

    def store_analysis_run(self, run_id: str, data: dict[str, Any]) -> None:
        """Write run metadata document.

        Args:
            run_id: Deterministic run ID (used as document ID).
            data: Run metadata including timing, symbols, and per-tool status.
        """
        self._db.collection("options_analysis_runs").document(run_id).set(data)
        logger.info("Stored analysis run: %s", run_id)
