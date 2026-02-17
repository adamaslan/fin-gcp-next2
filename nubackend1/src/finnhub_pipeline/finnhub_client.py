"""Finnhub API client for options chain data.

Fetches full options chains (calls & puts) organized by expiration date,
including strike, bid/ask, last price, volume, open interest, and Greeks.
"""

import json
import logging
from typing import Any

import finnhub

logger = logging.getLogger(__name__)


class FinnhubOptionsClient:
    """Client for fetching options chain data from Finnhub API."""

    def __init__(self, api_key: str) -> None:
        self._client = finnhub.Client(api_key=api_key)
        logger.info("Finnhub client initialized")

    def fetch_option_chain(self, symbol: str) -> dict[str, Any]:
        """Fetch full options chain for a symbol.

        Args:
            symbol: Stock/ETF ticker symbol (e.g., 'AEM').

        Returns:
            Dict with keys: symbol, last_trade_price, last_trade_date,
            expirations (list of expiration data with calls and puts).

        Raises:
            FinnhubOptionsError: If the API call fails.
        """
        logger.info("Fetching options chain for %s", symbol)

        try:
            raw = self._client.option_chain(symbol=symbol)
        except finnhub.exceptions.FinnhubAPIException as e:
            raise FinnhubOptionsError(
                f"Finnhub API error for {symbol}: {e}"
            ) from e

        if isinstance(raw, str):
            data = json.loads(raw)
        elif isinstance(raw, dict):
            data = raw
        else:
            data = {}
        expirations = []

        for exp_data in data.get("data", []):
            calls = [
                _parse_contract(c)
                for c in exp_data.get("options", {}).get("CALL", [])
            ]
            puts = [
                _parse_contract(p)
                for p in exp_data.get("options", {}).get("PUT", [])
            ]

            expirations.append({
                "expiration_date": exp_data.get("expirationDate"),
                "implied_volatility": exp_data.get("impliedVolatility"),
                "put_volume": exp_data.get("putVolume"),
                "call_volume": exp_data.get("callVolume"),
                "put_call_volume_ratio": exp_data.get("putCallVolumeRatio"),
                "put_open_interest": exp_data.get("putOpenInterest"),
                "call_open_interest": exp_data.get("callOpenInterest"),
                "put_call_oi_ratio": exp_data.get("putCallOpenInterestRatio"),
                "options_count": exp_data.get("optionsCount"),
                "calls": calls,
                "puts": puts,
            })

        result = {
            "symbol": data.get("code", symbol),
            "exchange": data.get("exchange"),
            "last_trade_price": data.get("lastTradePrice"),
            "last_trade_date": data.get("lastTradeDate"),
            "num_expirations": len(expirations),
            "total_calls": sum(len(e["calls"]) for e in expirations),
            "total_puts": sum(len(e["puts"]) for e in expirations),
            "expirations": expirations,
        }

        logger.info(
            "Fetched %s: %d expirations, %d calls, %d puts",
            symbol,
            result["num_expirations"],
            result["total_calls"],
            result["total_puts"],
        )
        return result

    def fetch_quote(self, symbol: str) -> dict[str, Any]:
        """Fetch current quote for a symbol.

        Args:
            symbol: Stock/ETF ticker symbol.

        Returns:
            Dict with current, high, low, open, previous close, and timestamp.
        """
        try:
            raw = self._client.quote(symbol)
            return {
                "symbol": symbol,
                "current": raw.get("c"),
                "change": raw.get("d"),
                "change_percent": raw.get("dp"),
                "high": raw.get("h"),
                "low": raw.get("l"),
                "open": raw.get("o"),
                "previous_close": raw.get("pc"),
                "timestamp": raw.get("t"),
            }
        except finnhub.exceptions.FinnhubAPIException as e:
            raise FinnhubOptionsError(
                f"Finnhub quote error for {symbol}: {e}"
            ) from e


def _parse_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Parse a single options contract from Finnhub response."""
    return {
        "contract_name": contract.get("contractName"),
        "type": contract.get("type"),
        "strike": contract.get("strike"),
        "last_price": contract.get("lastPrice"),
        "bid": contract.get("bid"),
        "ask": contract.get("ask"),
        "change": contract.get("change"),
        "change_percent": contract.get("changePercent"),
        "volume": contract.get("volume"),
        "open_interest": contract.get("openInterest"),
        "implied_volatility": contract.get("impliedVolatility"),
        "in_the_money": contract.get("inTheMoney") == "TRUE",
        "expiration_date": contract.get("expirationDate"),
        "last_trade_datetime": contract.get("lastTradeDateTime"),
        "contract_size": contract.get("contractSize"),
        "contract_period": contract.get("contractPeriod"),
        "currency": contract.get("currency"),
        "delta": contract.get("delta"),
        "gamma": contract.get("gamma"),
        "theta": contract.get("theta"),
        "vega": contract.get("vega"),
        "rho": contract.get("rho"),
        "theoretical": contract.get("theoretical"),
        "intrinsic_value": contract.get("intrinsicValue"),
        "time_value": contract.get("timeValue"),
        "updated_at": contract.get("updatedAt"),
        "days_before_expiration": contract.get("daysBeforeExpiration"),
    }


class FinnhubOptionsError(Exception):
    """Raised when Finnhub options API call fails."""
    pass
