"""Dual-source historical candle data fetcher.

Priority: Finnhub first, Alpha Vantage fallback.

Finnhub (free tier): Stock candles require a paid plan (403 on free tier).
Alpha Vantage (free tier): Daily, weekly, monthly available. Intraday is premium.

When API keys are upgraded, intraday data becomes available automatically.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any

import finnhub
import httpx

logger = logging.getLogger(__name__)

INTERVALS = {
    "1min": {"finnhub": "1", "av_function": "TIME_SERIES_INTRADAY", "av_interval": "1min"},
    "5min": {"finnhub": "5", "av_function": "TIME_SERIES_INTRADAY", "av_interval": "5min"},
    "15min": {"finnhub": "15", "av_function": "TIME_SERIES_INTRADAY", "av_interval": "15min"},
    "30min": {"finnhub": "30", "av_function": "TIME_SERIES_INTRADAY", "av_interval": "30min"},
    "1hour": {"finnhub": "60", "av_function": "TIME_SERIES_INTRADAY", "av_interval": "60min"},
    "1day": {"finnhub": "D", "av_function": "TIME_SERIES_DAILY", "av_interval": None},
    "1week": {"finnhub": "W", "av_function": "TIME_SERIES_WEEKLY", "av_interval": None},
    "1month": {"finnhub": "M", "av_function": "TIME_SERIES_MONTHLY", "av_interval": None},
}

FINNHUB_LOOKBACK_DAYS = {
    "1min": 1, "5min": 1, "15min": 5, "30min": 5,
    "1hour": 10, "1day": 30, "1week": 90, "1month": 365,
}

AV_TIME_SERIES_KEYS = {
    "TIME_SERIES_INTRADAY": lambda iv: f"Time Series ({iv})",
    "TIME_SERIES_DAILY": lambda _: "Time Series (Daily)",
    "TIME_SERIES_WEEKLY": lambda _: "Weekly Time Series",
    "TIME_SERIES_MONTHLY": lambda _: "Monthly Time Series",
}

AV_BASE_URL = "https://www.alphavantage.co/query"


class CandleFetcher:
    """Fetch historical OHLCV candle data. Finnhub first, Alpha Vantage fallback."""

    def __init__(self, finnhub_key: str, alpha_vantage_key: str) -> None:
        self._finnhub = finnhub.Client(api_key=finnhub_key)
        self._av_key = alpha_vantage_key
        self._http = httpx.Client(timeout=30)

    def fetch_candles(self, symbol: str, interval: str) -> dict[str, Any]:
        """Fetch candle data for a symbol at a specific interval.

        Tries Finnhub first, then Alpha Vantage as fallback.

        Args:
            symbol: Stock/ETF ticker symbol.
            interval: One of: 1min, 5min, 15min, 30min, 1hour, 1day, 1week, 1month.

        Returns:
            Dict with symbol, interval, source, status, candles list.
        """
        if interval not in INTERVALS:
            raise CandleFetchError(
                f"Invalid interval '{interval}'. Valid: {list(INTERVALS.keys())}"
            )

        result = self._try_finnhub(symbol, interval)
        if result and result.get("status") == "ok":
            return result

        result = self._try_alpha_vantage(symbol, interval)
        if result and result.get("status") == "ok":
            return result

        return {
            "symbol": symbol,
            "interval": interval,
            "source": "none",
            "status": "unavailable",
            "error": (
                "Neither Finnhub nor Alpha Vantage returned data for this interval. "
                "Intraday data requires paid plans on both services."
            ),
            "candles": [],
        }

    def _try_finnhub(self, symbol: str, interval: str) -> dict[str, Any] | None:
        """Attempt to fetch candles from Finnhub."""
        resolution = INTERVALS[interval]["finnhub"]
        lookback_days = FINNHUB_LOOKBACK_DAYS[interval]
        now = int(time.time())
        from_ts = now - (lookback_days * 86400)

        try:
            raw = self._finnhub.stock_candles(symbol, resolution, from_ts, now)
        except finnhub.exceptions.FinnhubAPIException:
            logger.debug("Finnhub candle %s/%s unavailable", symbol, interval)
            return None

        if raw.get("s") != "ok":
            return None

        candles = _build_candle_list(
            raw.get("t", []),
            raw.get("o", []),
            raw.get("h", []),
            raw.get("l", []),
            raw.get("c", []),
            raw.get("v", []),
        )

        logger.info("Finnhub: %d %s candles for %s", len(candles), interval, symbol)
        return {
            "symbol": symbol,
            "interval": interval,
            "source": "finnhub",
            "status": "ok",
            "num_candles": len(candles),
            "candles": candles,
        }

    def _try_alpha_vantage(self, symbol: str, interval: str) -> dict[str, Any] | None:
        """Attempt to fetch candles from Alpha Vantage."""
        config = INTERVALS[interval]
        av_func = config["av_function"]
        av_interval = config["av_interval"]

        params: dict[str, str] = {
            "function": av_func,
            "symbol": symbol,
            "apikey": self._av_key,
            "outputsize": "compact",
        }
        if av_interval:
            params["interval"] = av_interval

        try:
            resp = self._http.get(AV_BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as e:
            logger.debug("Alpha Vantage %s/%s request failed: %s", symbol, interval, e)
            return None

        if "Information" in data:
            logger.debug("Alpha Vantage premium required for %s/%s", symbol, interval)
            return None

        if "Error Message" in data:
            logger.debug(
                "Alpha Vantage error for %s/%s: %s",
                symbol, interval, data["Error Message"],
            )
            return None

        ts_key_fn = AV_TIME_SERIES_KEYS.get(av_func)
        if not ts_key_fn:
            return None

        ts_key = ts_key_fn(av_interval)
        time_series = data.get(ts_key, {})

        if not time_series:
            return None

        candles = []
        for dt_str, vals in sorted(time_series.items()):
            candles.append({
                "datetime": dt_str,
                "open": float(vals.get("1. open", 0)),
                "high": float(vals.get("2. high", 0)),
                "low": float(vals.get("3. low", 0)),
                "close": float(vals.get("4. close", 0)),
                "volume": int(vals.get("5. volume", 0)),
            })

        logger.info("Alpha Vantage: %d %s candles for %s", len(candles), interval, symbol)
        return {
            "symbol": symbol,
            "interval": interval,
            "source": "alpha_vantage",
            "status": "ok",
            "num_candles": len(candles),
            "candles": candles,
        }

    def fetch_all_intervals(self, symbol: str, delay: float = 1.0) -> dict[str, Any]:
        """Fetch candle data across all supported intervals.

        Args:
            symbol: Stock/ETF ticker symbol.
            delay: Seconds between API calls to respect rate limits.

        Returns:
            Dict mapping interval names to candle data.
        """
        results: dict[str, Any] = {}

        for interval in INTERVALS:
            try:
                results[interval] = self.fetch_candles(symbol, interval)
            except CandleFetchError as e:
                logger.warning("Candle fetch failed for %s/%s: %s", symbol, interval, e)
                results[interval] = {
                    "symbol": symbol,
                    "interval": interval,
                    "source": "none",
                    "status": "error",
                    "error": str(e),
                    "candles": [],
                }
            time.sleep(delay)

        return results

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()


def _build_candle_list(
    timestamps: list[int],
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[int],
) -> list[dict[str, Any]]:
    """Build candle list from parallel arrays (Finnhub format)."""
    candles = []
    for i in range(len(timestamps)):
        candles.append({
            "timestamp": timestamps[i],
            "datetime": datetime.fromtimestamp(
                timestamps[i], tz=timezone.utc
            ).isoformat(),
            "open": opens[i],
            "high": highs[i],
            "low": lows[i],
            "close": closes[i],
            "volume": volumes[i],
        })
    return candles


class CandleFetchError(Exception):
    """Raised when candle data fetch fails."""
    pass
