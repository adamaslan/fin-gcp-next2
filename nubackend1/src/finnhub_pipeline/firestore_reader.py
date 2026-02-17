"""Read options chain data from Firestore for analysis.

Provides a Firestore-backed data reader that returns options data in the same
pandas DataFrame format expected by ChainAnalyzer.analyze_chain(). This allows
analysis tools to run on Finnhub-sourced data stored in Firestore instead of
fetching from yfinance directly.

Data flow:
    Finnhub -> Firestore (via pipeline) -> FirestoreChainReader -> ChainAnalyzer
"""

import logging
from typing import Any

import pandas as pd
from google.cloud import firestore

from options_mcp.analysis.chain_analyzer import OptionsDataError

logger = logging.getLogger(__name__)

# Mapping from Finnhub/Firestore field names (snake_case) to
# yfinance DataFrame column names (camelCase) expected by ChainAnalyzer
_FIELD_MAP = {
    "strike": "strike",
    "volume": "volume",
    "open_interest": "openInterest",
    "implied_volatility": "impliedVolatility",
    "bid": "bid",
    "ask": "ask",
    "last_price": "lastPrice",
    "delta": "delta",
    "gamma": "gamma",
    "theta": "theta",
    "vega": "vega",
}


class FirestoreChainReader:
    """Read options chain data from Firestore and convert to DataFrames.

    Reads from the optimized Firestore collections populated by the
    Finnhub pipeline (options_chains/{symbol}/expirations/{date}).

    The embedded calls[] and puts[] arrays are converted to pandas
    DataFrames with column names matching yfinance format so they
    can be passed directly to ChainAnalyzer.analyze_chain().
    """

    def __init__(self, project_id: str = "ttb-lang1") -> None:
        self._db = firestore.Client(project=project_id)
        logger.info("Firestore chain reader connected to project: %s", project_id)

    def get_tracked_symbols(self) -> list[str]:
        """Read symbol IDs from the options_chains collection.

        Returns:
            List of ticker symbols tracked in Firestore.

        Raises:
            OptionsDataError: If no symbols found.
        """
        docs = self._db.collection("options_chains").stream()
        symbols = [doc.id for doc in docs]
        if not symbols:
            raise OptionsDataError("*", "No symbols found in Firestore options_chains")
        logger.info("Found %d tracked symbols: %s", len(symbols), symbols)
        return symbols

    def get_current_price(self, symbol: str) -> float:
        """Get current price from Firestore quote or chain metadata.

        Tries options_quotes first, falls back to options_chains metadata.

        Args:
            symbol: Ticker symbol.

        Returns:
            Current stock price.

        Raises:
            OptionsDataError: If no price data available.
        """
        # Try quote collection first
        quote_doc = self._db.collection("options_quotes").document(symbol).get()
        if quote_doc.exists:
            quote = quote_doc.to_dict()
            price = quote.get("current")
            if price and price > 0:
                logger.info("Price for %s from quote: %.2f", symbol, price)
                return float(price)

        # Fall back to chain metadata
        chain_doc = self._db.collection("options_chains").document(symbol).get()
        if chain_doc.exists:
            chain = chain_doc.to_dict()
            price = chain.get("last_trade_price")
            if price and price > 0:
                logger.info("Price for %s from chain metadata: %.2f", symbol, price)
                return float(price)

        raise OptionsDataError(symbol, "No price data in Firestore")

    def get_expirations(self, symbol: str) -> list[str]:
        """Get available expiration dates for a symbol from Firestore.

        Args:
            symbol: Ticker symbol.

        Returns:
            List of expiration date strings sorted ascending.

        Raises:
            OptionsDataError: If no expirations found.
        """
        exp_ref = (
            self._db.collection("options_chains")
            .document(symbol)
            .collection("expirations")
        )
        docs = exp_ref.stream()
        expirations = sorted(doc.id for doc in docs)

        if not expirations:
            raise OptionsDataError(symbol, "No expirations in Firestore")

        logger.info("Found %d expirations for %s: %s", len(expirations), symbol, expirations)
        return expirations

    def get_option_chain(
        self, symbol: str, expiration: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Read calls and puts for an expiration from Firestore.

        Supports two storage formats:
        1. Embedded arrays: calls[] and puts[] in the expiration document
        2. Sub-collections: calls/ and puts/ as nested document collections

        Tries embedded arrays first. If empty, reads from sub-collections.

        Args:
            symbol: Ticker symbol.
            expiration: Expiration date string (YYYY-MM-DD).

        Returns:
            Tuple of (calls_df, puts_df) with yfinance column names.

        Raises:
            OptionsDataError: If expiration document not found.
        """
        exp_ref = (
            self._db.collection("options_chains")
            .document(symbol)
            .collection("expirations")
            .document(expiration)
        )
        doc = exp_ref.get()

        if not doc.exists:
            raise OptionsDataError(
                symbol, f"Expiration {expiration} not found in Firestore"
            )

        data = doc.to_dict()

        # Try embedded arrays first (optimized format)
        calls_raw = data.get("calls", [])
        puts_raw = data.get("puts", [])

        if calls_raw or puts_raw:
            calls_df = self._contracts_to_dataframe(calls_raw)
            puts_df = self._contracts_to_dataframe(puts_raw)
            logger.info(
                "Read %s/%s from embedded arrays: %d calls, %d puts",
                symbol, expiration, len(calls_df), len(puts_df),
            )
            return calls_df, puts_df

        # Fall back to sub-collection documents (original format)
        calls_docs = list(exp_ref.collection("calls").stream())
        puts_docs = list(exp_ref.collection("puts").stream())

        calls_raw = [doc.to_dict() for doc in calls_docs]
        puts_raw = [doc.to_dict() for doc in puts_docs]

        calls_df = self._contracts_to_dataframe(calls_raw)
        puts_df = self._contracts_to_dataframe(puts_raw)

        logger.info(
            "Read %s/%s from sub-collections: %d calls, %d puts",
            symbol, expiration, len(calls_df), len(puts_df),
        )
        return calls_df, puts_df

    def get_expiration_summary(
        self, symbol: str, expiration: str
    ) -> dict[str, Any]:
        """Read the full expiration summary document from Firestore.

        Args:
            symbol: Ticker symbol.
            expiration: Expiration date string.

        Returns:
            Expiration summary dict with IV, PCR, volumes, etc.

        Raises:
            OptionsDataError: If not found.
        """
        doc_ref = (
            self._db.collection("options_chains")
            .document(symbol)
            .collection("expirations")
            .document(expiration)
        )
        doc = doc_ref.get()

        if not doc.exists:
            raise OptionsDataError(
                symbol, f"Expiration {expiration} not found"
            )

        return doc.to_dict()

    def _contracts_to_dataframe(
        self, contracts: list[dict[str, Any]]
    ) -> pd.DataFrame:
        """Convert Firestore contract dicts to a yfinance-compatible DataFrame.

        Maps Finnhub snake_case field names to yfinance camelCase column names.
        Fills missing numeric fields with 0 (volume, OI) or NaN (IV, Greeks).

        Args:
            contracts: List of contract dicts from Firestore.

        Returns:
            pandas DataFrame with yfinance-compatible columns.
        """
        if not contracts:
            return pd.DataFrame()

        rows = []
        for contract in contracts:
            row = {}
            for firestore_key, df_col in _FIELD_MAP.items():
                row[df_col] = contract.get(firestore_key)
            rows.append(row)

        df = pd.DataFrame(rows)

        # Ensure required columns exist with proper defaults
        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
        if "openInterest" in df.columns:
            df["openInterest"] = pd.to_numeric(df["openInterest"], errors="coerce").fillna(0).astype(int)
        if "impliedVolatility" in df.columns:
            df["impliedVolatility"] = pd.to_numeric(df["impliedVolatility"], errors="coerce").fillna(0.0)
            # Finnhub stores IV in percentage form (50.23 = 50.23%)
            # yfinance stores IV in decimal form (0.5023 = 50.23%)
            # ChainAnalyzer multiplies by 100, so convert to decimal
            if not df["impliedVolatility"].empty and df["impliedVolatility"].max() > 5.0:
                df["impliedVolatility"] = df["impliedVolatility"] / 100.0
        if "strike" in df.columns:
            df["strike"] = pd.to_numeric(df["strike"], errors="coerce")

        return df
