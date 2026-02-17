# Finnhub Options Data Pipeline

## Overview

Automated pipeline that fetches options chain data from the Finnhub API and historical OHLCV candle data (Finnhub primary, Alpha Vantage fallback), then stores everything in Google Cloud Firestore.

## Architecture

```
                    +------------------+
                    |  run_pipeline.py |  (CLI entry point)
                    +--------+---------+
                             |
                    +--------v---------+
                    | OptionsPipeline  |  (orchestrator)
                    +--+-----+------+--+
                       |     |      |
          +------------+     |      +-------------+
          |                  |                    |
+---------v------+  +-------v--------+  +--------v---------+
| FinnhubOptions |  | CandleFetcher  |  | FirestoreOptions |
|    Client      |  | (dual-source)  |  |     Store        |
+-------+--------+  +---+------+-----+  +--------+---------+
        |                |      |                 |
   Finnhub API     Finnhub  Alpha Vantage    Firestore
   (options chain) (candles) (candles)        (ttb-lang1)
```

## Data Sources

### Finnhub API (Primary)

| Endpoint | Data | Free Tier |
|----------|------|-----------|
| `/stock/option-chain` | Full options chain (calls + puts) | Available |
| `/quote` | Current stock quote | Available |
| `/stock/candle` | Historical OHLCV candles | Paid only (403) |

### Alpha Vantage API (Fallback for candles)

| Function | Data | Free Tier |
|----------|------|-----------|
| `TIME_SERIES_DAILY` | Daily candles | Available |
| `TIME_SERIES_WEEKLY` | Weekly candles | Available |
| `TIME_SERIES_MONTHLY` | Monthly candles | Available |
| `TIME_SERIES_INTRADAY` | 1m/5m/15m/30m/60m candles | Paid only |

### Data Priority

The pipeline tries Finnhub first for all data. If Finnhub returns 403 (free tier limitation), it falls back to Alpha Vantage. When either API key is upgraded to a paid plan, intraday data becomes available automatically.

## Options Chain Data

For each symbol, the pipeline fetches the complete options chain including:

### Per Expiration Date
- Implied volatility (aggregate)
- Put volume / Call volume
- Put/Call volume ratio
- Put open interest / Call open interest
- Put/Call OI ratio
- Options count

### Per Contract (Call or Put)
- **Contract name** (e.g., `AEM260213C00180000`)
- **Type**: CALL or PUT
- **Strike price**
- **Last price**
- **Bid / Ask**
- **Change / Change percent**
- **Volume**
- **Open interest**
- **Implied volatility** (per contract)
- **In the money** (boolean)
- **Expiration date**
- **Last trade datetime**
- **Contract size** (REGULAR)
- **Contract period** (WEEKLY / MONTHLY)
- **Currency** (USD)
- **Greeks**: delta, gamma, theta, vega, rho
- **Theoretical value**
- **Intrinsic value / Time value**
- **Updated at** timestamp
- **Days before expiration**

## Historical Candle Data

Requested intervals and current availability:

| Interval | Finnhub (free) | Alpha Vantage (free) | Status |
|----------|----------------|----------------------|--------|
| 1 minute | Paid | Paid | Requires upgrade |
| 5 minutes | Paid | Paid | Requires upgrade |
| 15 minutes | Paid | Paid | Requires upgrade |
| 30 minutes | Paid | Paid | Requires upgrade |
| 1 hour | Paid | Paid | Requires upgrade |
| 1 day | Paid | **Available** | Working via AV |
| 1 week | Paid | **Available** | Working via AV |
| 1 month | Paid | **Available** | Working via AV |

Each candle includes: datetime, open, high, low, close, volume.

## Target Symbols

| Symbol | Name | Type |
|--------|------|------|
| AEM | Agnico Eagle Mines | Stock |
| CRM | Salesforce | Stock |
| IGV | iShares Expanded Tech-Software ETF | ETF |
| QBTS | D-Wave Quantum | Stock |
| JPM | JPMorgan Chase | Stock |

## Firestore Collections

### `options_chains/{symbol}`
Top-level document with metadata:
```json
{
  "symbol": "AEM",
  "exchange": "US",
  "last_trade_price": 211.89,
  "last_trade_date": "2026-02-10",
  "num_expirations": 20,
  "total_calls": 890,
  "total_puts": 890,
  "fetched_at": "2026-02-11T..."
}
```

### `options_chains/{symbol}/expirations/{date}`
Per-expiration summary:
```json
{
  "expiration_date": "2026-02-13",
  "implied_volatility": 72.8582,
  "put_volume": 3246,
  "call_volume": 8721,
  "put_call_volume_ratio": 0.372,
  "num_calls": 74,
  "num_puts": 74
}
```

### `options_chains/{symbol}/expirations/{date}/calls/{strike}`
### `options_chains/{symbol}/expirations/{date}/puts/{strike}`
Individual contract data with all fields listed above.

### `options_quotes/{symbol}`
Current quote snapshot:
```json
{
  "symbol": "AEM",
  "current": 215.50,
  "change": 3.61,
  "change_percent": 1.70,
  "high": 218.25,
  "low": 209.76,
  "open": 215.01,
  "previous_close": 211.89
}
```

### `candle_data/{symbol}/intervals/{interval}`
Historical candle data per interval:
```json
{
  "symbol": "AEM",
  "interval": "1day",
  "source": "alpha_vantage",
  "status": "ok",
  "num_candles": 100,
  "candles": [
    {"datetime": "2025-09-18", "open": 90.23, "high": 91.10, "low": 89.55, "close": 90.80, "volume": 1234567},
    ...
  ]
}
```

### `pipeline_runs/{auto_id}`
Pipeline execution metadata:
```json
{
  "status": "completed",
  "started_at": "2026-02-11T...",
  "completed_at": "2026-02-11T...",
  "elapsed_seconds": 120.5,
  "symbols_processed": 5,
  "symbols": ["AEM", "CRM", "IGV", "QBTS", "JPM"],
  "results": { ... }
}
```

## Usage

### CLI

```bash
# Activate environment
mamba activate fin-ai1

# Set API keys
export FINHUB_API_KEY=your-finnhub-key
export ALPHA_VANTAGE_KEY=your-alpha-vantage-key

# Run all 5 tickers (options + candles)
python run_pipeline.py

# Specific tickers
python run_pipeline.py --symbols AEM CRM

# Options chain only (no candles)
python run_pipeline.py --no-candles

# Single symbol with detailed output
python run_pipeline.py --symbols QBTS --single

# Custom GCP project
python run_pipeline.py --project my-gcp-project

# Adjust API rate limit delay
python run_pipeline.py --delay 2.0
```

### API Endpoints

The pipeline is also available via FastAPI endpoints:

```bash
# Run pipeline for multiple symbols
curl -X POST http://localhost:8080/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AEM", "CRM", "IGV", "QBTS", "JPM"], "fetch_candles": true}'

# Run for single symbol
curl -X POST http://localhost:8080/api/pipeline/run-single \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AEM", "fetch_candles": true}'
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FINHUB_API_KEY` | Yes | Finnhub API key (free tier works for options) |
| `ALPHA_VANTAGE_KEY` | No | Alpha Vantage API key (fallback for candles) |
| `GCP_PROJECT_ID` | No | Firestore project (default: `ttb-lang1`) |

## File Structure

```
nubackend1/
  run_pipeline.py                          # CLI entry point
  main.py                                  # FastAPI app with pipeline endpoints
  src/
    finnhub_pipeline/
      __init__.py                          # Package init
      finnhub_client.py                    # Finnhub API client (options chain + quote)
      candle_fetcher.py                    # Dual-source candle fetcher
      firestore_store.py                   # Firestore storage layer
      pipeline.py                          # Pipeline orchestrator
```

## Rate Limits

| Service | Free Tier Limit |
|---------|-----------------|
| Finnhub | 60 calls/minute |
| Alpha Vantage | 25 calls/day (free), 75/min (paid) |

The pipeline uses configurable delays between API calls (default: 1.5s) to respect rate limits. For 5 symbols with all 8 intervals, this means ~60-90 seconds of candle fetching.

## Upgrading for Intraday Data

To unlock 1min/5min/15min/30min/1hour candle data:

**Option A: Upgrade Finnhub** (recommended)
- Visit https://finnhub.io/pricing
- The pipeline tries Finnhub first, so upgraded keys get priority

**Option B: Upgrade Alpha Vantage**
- Visit https://www.alphavantage.co/premium/
- Premium plan unlocks intraday endpoints

No code changes needed - the pipeline automatically uses whichever source returns data.

## Sample Pipeline Output

```json
{
  "status": "completed",
  "elapsed_seconds": 95.2,
  "symbols_processed": 5,
  "results": {
    "AEM": {
      "options_chain": {
        "status": "ok",
        "expirations": 20,
        "total_calls": 890,
        "total_puts": 890,
        "last_trade_price": 211.89,
        "docs_written": 1801
      },
      "quote": {
        "status": "ok",
        "current": 215.50,
        "change_percent": 1.70
      },
      "candles": {
        "1min": {"status": "unavailable", "source": "none"},
        "5min": {"status": "unavailable", "source": "none"},
        "15min": {"status": "unavailable", "source": "none"},
        "30min": {"status": "unavailable", "source": "none"},
        "1hour": {"status": "unavailable", "source": "none"},
        "1day": {"status": "ok", "source": "alpha_vantage", "num_candles": 100},
        "1week": {"status": "ok", "source": "alpha_vantage", "num_candles": 260},
        "1month": {"status": "ok", "source": "alpha_vantage", "num_candles": 60}
      }
    }
  }
}
```
