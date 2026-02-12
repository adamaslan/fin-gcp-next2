# Backend Documentation

This section covers the Python MCP server - everything from setup through deployment and optimization.

---

## Quick Navigation

- **Setup:** [`setup.md`](setup.md) - Backend environment setup
- **Running:** [`running-the-server.md`](running-the-server.md) - Execute the MCP server
- **API Endpoints:** [`api-endpoints.md`](api-endpoints.md) - REST API reference
- **Signals:** [`signals-implementation.md`](signals-implementation.md) - 150+ trading signals
- **Testing:** [`testing.md`](testing.md) - Unit & integration tests
- **Deployment:** [`deployment.md`](deployment.md) - Deploy to Google Cloud Run
- **Performance:** [`performance.md`](performance.md) - Optimization guide
- **Troubleshooting:** [`troubleshooting.md`](troubleshooting.md) - Common issues & fixes

---

## Tech Stack

- **Framework:** FastAPI (Python)
- **Language:** Python 3.11
- **Package Manager:** Mamba (conda-forge)
- **Database:** PostgreSQL (Neon)
- **Server:** Uvicorn
- **Async:** asyncio for async/await
- **Testing:** pytest
- **Deployment:** Google Cloud Run
- **Monitoring:** Cloud Logging

---

## Architecture

The MCP backend is a specialized financial analysis server:

```
FastAPI Server
├── Routes (REST endpoints)
├── Signal Calculation (150+ indicators)
├── Market Data Processing
├── Database Operations
└── Risk Analysis
```

**Key Responsibilities:**
- Calculate trading signals for stocks
- Manage user watchlists
- Process market data
- Handle user portfolios
- Generate alerts

---

## Setup & Development

### New to Backend?
1. Start with: [`setup.md`](setup.md) - Environment setup
2. Learn: [`running-the-server.md`](running-the-server.md) - How to run it
3. Study: [`api-endpoints.md`](api-endpoints.md) - Available endpoints
4. Implement: [`signals-implementation.md`](signals-implementation.md) - Signals

### Ready to Code?
- Reference: [`api-endpoints.md`](api-endpoints.md) for endpoint specs
- Study: [`signals-implementation.md`](signals-implementation.md) for signal patterns
- Check: `./.claude/CLAUDE.md` - Python code standards
- Run tests: [`testing.md`](testing.md)

---

## Key Features

### REST API
- User management
- Portfolio operations
- Watchlist management
- Signal analysis
- Alert configuration

See: [`api-endpoints.md`](api-endpoints.md)

### Trading Signals
150+ indicators including:
- Momentum (RSI, MACD, Stochastic)
- Trend (MA, EMA, TEMA)
- Volatility (Bollinger Bands, ATR)
- Volume indicators
- Sentiment analysis

See: [`signals-implementation.md`](signals-implementation.md)

### Data Processing
- Real-time market data intake
- Historical data analysis
- Caching strategies
- Batch processing

See: [`performance.md`](performance.md)

---

## Common Tasks

| Task | File | Time |
|------|------|------|
| Setup environment | `setup.md` | 30 min |
| Start server | `running-the-server.md` | 5 min |
| Understand API | `api-endpoints.md` | 30 min |
| Implement signal | `signals-implementation.md` | 1 hour+ |
| Write test | `testing.md` | 30 min |
| Deploy changes | `deployment.md` | 15 min |

---

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/signal-name
   ```

2. **Setup Environment**
   ```bash
   mamba activate fin-ai1
   ```

3. **Make Changes**
   - Add signals in `signals/`
   - Update routes in `app/routes/`
   - Add tests in `tests/`

4. **Follow Standards**
   - Type hints on all functions
   - Docstrings on public functions
   - Follow `./.claude/CLAUDE.md` guidelines

5. **Test Locally**
   ```bash
   pytest
   python -m uvicorn app:app --reload
   ```

6. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: Add new signal"
   git push
   ```

7. **Deploy**
   - Cloud Run auto-deploys on merge
   - See [`deployment.md`](deployment.md)

---

## Code Structure

```
mcp-finance1/
├── app/
│   ├── main.py              # FastAPI app
│   ├── routes/              # API endpoints
│   ├── models/              # Data models
│   └── services/            # Business logic
├── signals/
│   ├── __init__.py
│   ├── momentum.py          # Momentum indicators
│   ├── trend.py             # Trend indicators
│   ├── volatility.py        # Volatility indicators
│   └── sentiment.py         # Sentiment indicators
├── database/
│   ├── models.py            # SQLAlchemy models
│   └── operations.py        # DB operations
├── tests/
│   ├── test_api.py
│   ├── test_signals.py
│   └── test_db.py
└── requirements.txt         # Dependencies
```

---

## Code Standards

### Python
- ✅ Type hints on all functions
- ✅ Docstrings on public functions
- ✅ Follow PEP 8 style guide
- ✅ Use async/await for I/O

### Functions
- ✅ Single responsibility
- ✅ Pure functions where possible
- ✅ Error handling with specific exceptions
- ✅ Logging important operations

See: `./.claude/CLAUDE.md` for complete guidelines

---

## API Reference

### Endpoint Categories
- **Analysis:** `/api/analysis/*` - Stock analysis endpoints
- **Portfolio:** `/api/portfolio/*` - Portfolio management
- **Watchlist:** `/api/watchlist/*` - Watchlist operations
- **Alerts:** `/api/alerts/*` - Alert management

See: [`api-endpoints.md`](api-endpoints.md) for complete reference

### Authentication
- Bearer token in `Authorization` header
- Verified by frontend (Clerk)
- All endpoints protected

---

## Testing

### Unit Tests
- Test individual functions
- Mock external dependencies
- Test signal calculations

### Integration Tests
- Test API endpoints
- Test database operations
- Test complete workflows

### Run Tests
```bash
pytest                    # Run all tests
pytest tests/test_signals.py  # Run specific file
pytest -v                # Verbose output
pytest --cov            # Coverage report
```

See: [`testing.md`](testing.md) for detailed guide

---

## Performance Optimization

### Caching
- Cache signal calculations
- Cache market data
- Cache user preferences

### Database
- Proper indexing
- Query optimization
- Connection pooling

### Async Processing
- Use async for I/O
- Parallel signal calculation
- Background tasks

See: [`performance.md`](performance.md) for optimization strategies

---

## Troubleshooting

### Setup Issues
See: [`troubleshooting.md`](troubleshooting.md)

### Server Won't Start
1. Check Python version: `python --version` (need 3.11+)
2. Verify dependencies: `mamba list`
3. Check database connection
4. See: [`running-the-server.md`](running-the-server.md)

### API Errors
1. Check request format in [`api-endpoints.md`](api-endpoints.md)
2. Verify authentication token
3. Check database connection
4. Review server logs

### Signal Issues
1. Verify market data available
2. Check signal implementation
3. See: [`signals-implementation.md`](signals-implementation.md)

---

## Important Files

- **Project Guidelines:** `./.claude/CLAUDE.md` - Code standards
- **Environment Template:** `.env.example` - Env variables
- **Dependencies:** `requirements.txt` - Python packages
- **Entry Point:** `app/main.py` - FastAPI app

---

## Integration with Frontend

The frontend calls this backend via REST API.

See: [`../architecture/frontend-backend-connection.md`](../architecture/frontend-backend-connection.md)

Key integration points:
- User authentication (via Clerk)
- Portfolio data
- Signal analysis
- Alert management

---

## Next Steps

1. **Setup:**
   - Follow [`setup.md`](setup.md)
   - Verify environment working

2. **Understand API:**
   - Study [`api-endpoints.md`](api-endpoints.md)
   - Test with curl or Postman

3. **Implement:**
   - Choose signal to add
   - Follow [`signals-implementation.md`](signals-implementation.md)
   - Add tests in [`testing.md`](testing.md)

4. **Deploy:**
   - Setup Cloud Run: [`deployment.md`](deployment.md)
   - Monitor: Check Cloud Logging

5. **Optimize:**
   - Profile code
   - Apply optimizations: [`performance.md`](performance.md)
   - Monitor in production

---

[← Back to Documentation](../README.md)
