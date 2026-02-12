# Complete Guide to MCP Finance Backend Execution & Reporting

**Purpose**: Master document for running backend, collecting data, and generating reports
**Status**: Official Procedure
**Last Updated**: January 21, 2026

---

## Overview

This guide provides complete instructions for:
1. **Running the entire MCP Finance backend**
2. **Testing all API endpoints**
3. **Collecting all data from responses**
4. **Generating AI insights from data**
5. **Creating comprehensive markdown reports**

The process is designed to be:
- ✅ **Efficient** - Automated scripts, minimal manual work
- ✅ **Repeatable** - Same results every time
- ✅ **Mamba-native** - Uses only mamba, never conda/pip
- ✅ **fin-ai1 exclusive** - Single environment, no conflicts
- ✅ **Documented** - Everything tracked in timestamped reports

---

## Quick Links to Documentation

| Document | Purpose |
|----------|---------|
| **BACKEND_EXECUTION_RUNBOOK.md** | Step-by-step execution guide |
| **MAMBA_FIN_AI1_RULES.md** | Strict rules for Mamba & fin-ai1 |
| **BACKEND_EXECUTION_REPORT.md** | Example report output |
| **scripts/quick_start.sh** | One-command test execution |
| **scripts/test_backend_api.sh** | API endpoint testing |
| **scripts/analyze_backend_responses.py** | Response analysis |
| **scripts/generate_backend_report.py** | Report generation |

---

## 5-Minute Quick Start

### Prerequisites

```bash
# Verify mamba is installed
which mamba
mamba --version

# Verify fin-ai1 environment exists
mamba env list | grep fin-ai1
```

### One-Command Execution

```bash
# Terminal 1: Start backend
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python main.py

# Terminal 2: Run full test suite & generate reports
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh
```

Results will be saved to:
```
/Users/adamaslan/code/gcp\ app\ w\ mcp/backend_test_results/YYYYMMDD_HHMMSS/
```

---

## Detailed Workflow

### Phase 1: Environment Setup (One-Time)

```bash
# 1. Source mamba
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh

# 2. Verify fin-ai1 exists
mamba env list | grep fin-ai1

# 3. Activate fin-ai1
mamba activate fin-ai1

# 4. Verify all packages
python -c "
import fastapi, uvicorn, pydantic
import pandas, numpy, yfinance
import mcp
print('✓ All packages available')
"
```

**If any import fails**, install missing package:
```bash
mamba install -c conda-forge package_name
```

### Phase 2: Backend Startup

**Terminal 1: Backend Server**

```bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
✅ MCP server functions imported successfully
INFO:     Application startup complete
```

⚠️ **If errors appear**:
- Check GCP_PROJECT_ID in .env
- Verify google-cloud-* packages installed
- See troubleshooting in BACKEND_EXECUTION_RUNBOOK.md

### Phase 3: API Testing

**Terminal 2: Test All Endpoints**

```bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Option A: Run full automated test suite
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh

# Option B: Manual testing
bash /Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/test_backend_api.sh
```

**What gets tested** (9 endpoint groups):
1. ✅ Health checks
2. ✅ Trade planning (AAPL, MSFT, GOOGL)
3. ✅ Trade scanning (SP500, Nasdaq)
4. ✅ Portfolio risk assessment
5. ✅ Morning briefing
6. ✅ Security analysis
7. ✅ Signal retrieval
8. ✅ Comparison tool
9. ✅ Backend statistics

**Results Location**:
```
backend_test_results/YYYYMMDD_HHMMSS/
├── 01_health.json
├── 02_health_detailed.json
├── 03_trade_plan_aapl.json
├── 04_trade_plan_msft.json
├── ... (all API responses)
└── COMPLETE_REPORT.md
```

### Phase 4: Data Analysis & Insights

**Automatic** (with quick_start.sh):
```bash
# This happens automatically:
# 1. API responses collected to JSON
# 2. Analysis performed
# 3. Insights extracted
# 4. Reports generated
```

**Manual** (if needed):
```bash
RUN_DIR="/Users/adamaslan/code/gcp app w mcp/backend_test_results/YYYYMMDD_HHMMSS"

# Analyze responses
python /Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/analyze_backend_responses.py \
  "$RUN_DIR" \
  "$RUN_DIR/analysis.md"

# Generate comprehensive report
python /Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/generate_backend_report.py \
  "$RUN_DIR" \
  "$RUN_DIR/COMPLETE_REPORT.md"
```

### Phase 5: Review Results

```bash
RUN_DIR="/Users/adamaslan/code/gcp app w\ mcp/backend_test_results/YYYYMMDD_HHMMSS"

# View analysis
cat "$RUN_DIR/analysis.md"

# View complete report
cat "$RUN_DIR/COMPLETE_REPORT.md"

# View all API responses
cat "$RUN_DIR"/*.json | jq .

# View specific endpoint
cat "$RUN_DIR/03_trade_plan_aapl.json" | jq .trade_plans
```

---

## What Gets Reported

### Analysis Report (analysis.md)

Extracts key insights:

✅ **System Health**
- Service version
- GCP service status
- API availability

✅ **Trade Planning Insights**
- Symbols analyzed
- Trade plans generated
- Entry/stop/target prices
- Risk-reward ratios
- Primary signals

✅ **Universe Scanning Insights**
- Total securities scanned
- Qualified trade setups
- Conversion rates
- Top performers
- Signal strengths

✅ **Portfolio Risk Insights**
- Total portfolio value
- Maximum loss calculation
- Risk level assessment
- Sector concentration
- Hedge suggestions

✅ **Market Intelligence**
- Market status (open/closed)
- VIX level
- Economic events
- Signal distribution (buy/hold/sell)
- Sector leaders
- Key market themes

### Complete Report (COMPLETE_REPORT.md)

Includes:
- Full API response for each endpoint
- Executive summary
- Data insights
- Response statistics
- All raw JSON data

---

## Data Collection Specifics

### What Data Is Captured

For **each API request**, we capture:
1. HTTP request details (endpoint, method, payload)
2. Full HTTP response (status code, headers, body)
3. Response timestamp
4. Response size
5. Processing duration (if available)

### Data Structure

Each endpoint returns a JSON response structured like:

```json
{
  "symbol": "AAPL",
  "timestamp": "2026-01-21T19:30:45.123456",
  "trade_plans": [
    {
      "bias": "bullish",
      "entry_price": 150.25,
      "stop_price": 145.00,
      "target_price": 160.00,
      "risk_reward_ratio": 2.0
    }
  ]
}
```

### AI Insights Generated

The analysis phase extracts:

1. **Signal Analysis**
   - What signals are being detected
   - Signal strength/confidence
   - Primary vs supporting signals

2. **Trade Opportunities**
   - Qualified trade setups found
   - Entry/stop/target points
   - Risk assessment
   - Best opportunities ranked

3. **Portfolio Assessment**
   - Aggregate risk level
   - Sector concentration
   - Hedge recommendations
   - Position sizing insights

4. **Market Intelligence**
   - Sentiment indicators (VIX)
   - Economic events
   - Sector leadership
   - Market themes

---

## Efficiency Tips for Future Runs

### Automate with Aliases

Add to ~/.zshrc:
```bash
# MCP Finance aliases
alias mcp-setup='source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh && mamba activate fin-ai1'
alias mcp-backend='cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1 && python main.py'
alias mcp-test='/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh'
```

Then use:
```bash
mcp-setup   # Initialize environment
mcp-backend # Start server
mcp-test    # Run all tests and generate reports
```

### Create Daily Test Script

```bash
#!/bin/bash
# daily_backend_test.sh

source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Start backend
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python main.py &
BACKEND_PID=$!
sleep 5

# Run tests
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh

# Kill backend
kill $BACKEND_PID

# Git commit results
cd /Users/adamaslan/code/gcp\ app\ w\ mcp
git add backend_test_results/
git commit -m "Daily backend test: $(date +%Y-%m-%d)"
```

### Set Up GitHub Actions

See CI/CD section in MAMBA_FIN_AI1_RULES.md for automated testing on every commit.

---

## Troubleshooting & Common Issues

### Backend Won't Start

```bash
# Check Python
python --version          # Should be 3.10.17

# Check imports
python -c "from technical_analysis_mcp.server import app; print('OK')"

# Check environment variables
cat .env                 # Should have GCP_PROJECT_ID

# Check packages
mamba list | grep fastapi  # Should be installed

# Full debug
python -u main.py 2>&1 | head -50
```

### API Tests Fail

```bash
# Verify backend is running
curl -s http://localhost:8080/ | jq .

# Check port availability
lsof -i :8080

# Test single endpoint
curl -s -X POST http://localhost:8080/api/trade-plan \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}'
```

### Missing fin-ai1 Environment

```bash
# Create it
mamba create -n fin-ai1 -c conda-forge \
  python=3.10 \
  fastapi uvicorn pydantic \
  pandas numpy yfinance httpx \
  google-cloud-firestore google-cloud-storage google-cloud-pubsub google-cloud-logging

# Verify
mamba activate fin-ai1
python --version  # Should be 3.10.17
```

### Package Installation Issues

```bash
# Try again with clean cache
mamba clean -a
mamba install -c conda-forge package_name

# Or update mamba itself
mamba update -n base -c conda-forge mamba
```

---

## Documentation Files Structure

```
/Users/adamaslan/code/gcp app w mcp/
├── GUIDE_TO_BACKEND_EXECUTION.md          ← THIS FILE
├── BACKEND_EXECUTION_RUNBOOK.md           ← Step-by-step guide
├── MAMBA_FIN_AI1_RULES.md                 ← Mamba rules
├── BACKEND_EXECUTION_REPORT.md            ← Example report
│
├── scripts/
│   ├── quick_start.sh                     ← One-command execution
│   ├── test_backend_api.sh                ← API testing
│   ├── analyze_backend_responses.py       ← Response analysis
│   └── generate_backend_report.py         ← Report generation
│
├── backend_test_results/
│   ├── 20260121_193045/
│   │   ├── 01_health.json
│   │   ├── 02_health_detailed.json
│   │   ├── 03_trade_plan_aapl.json
│   │   ├── ... (all API responses)
│   │   ├── analysis.md
│   │   └── COMPLETE_REPORT.md
│   └── ... (other dated runs)
│
└── mcp-finance1/
    ├── main.py                            ← Backend server
    ├── .env                               ← Config
    └── src/technical_analysis_mcp/        ← MCP server
```

---

## Checklist: Running Backend & Generating Reports

### Pre-Flight
- [ ] Terminal 1 available for backend
- [ ] Terminal 2 available for testing
- [ ] Port 8080 is free (`lsof -i :8080`)
- [ ] fin-ai1 environment exists (`mamba env list`)
- [ ] All packages installed (`mamba list | grep fastapi`)

### Execution
- [ ] Source conda.sh: `source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh`
- [ ] Activate fin-ai1: `mamba activate fin-ai1`
- [ ] Start backend: `python main.py` (Terminal 1)
- [ ] Verify health: `curl http://localhost:8080/` (Terminal 2)
- [ ] Run tests: `/scripts/quick_start.sh` (Terminal 2)

### Post-Execution
- [ ] Check results directory created: `backend_test_results/YYYYMMDD_HHMMSS/`
- [ ] Verify 13+ JSON files generated (one per endpoint)
- [ ] Review analysis.md for insights
- [ ] Review COMPLETE_REPORT.md for full data
- [ ] Commit results to git (optional)

### Troubleshooting
- [ ] If backend fails: Check .env and GCP packages
- [ ] If tests fail: Verify backend health with curl
- [ ] If no reports: Check Python script permissions (`ls -lh scripts/`)

---

## Example: Running a Complete Backend Test

```bash
# ============================================================================
# Complete Backend Execution Example
# ============================================================================

# Step 1: Open two terminals

# === TERMINAL 1 ===
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python main.py

# Wait for output:
# INFO:     Uvicorn running on http://0.0.0.0:8080
# ✅ MCP server functions imported successfully

# === TERMINAL 2 ===
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Run everything automatically
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh

# Wait for completion... (~30-60 seconds)

# === RESULTS ===
# View the latest results
LATEST=$(ls -td /Users/adamaslan/code/gcp\ app\ w\ mcp/backend_test_results/*/ | head -1)
echo "Results: $LATEST"

# Review analysis
cat "$LATEST/analysis.md"

# Review full report
cat "$LATEST/COMPLETE_REPORT.md"

# View specific endpoint data
cat "$LATEST/03_trade_plan_aapl.json" | jq .

# List all files
ls -lh "$LATEST"
```

---

## Next Steps After Running Backend

1. **Review the Analysis**: Read `analysis.md` for extracted insights
2. **Examine Raw Data**: Check individual JSON files in the results directory
3. **Update Documentation**: If new patterns emerge, update these guides
4. **Commit Results**: Save results to git with appropriate commit message
5. **Run Again**: Run tests weekly/monthly to track changes and trends

---

## Support & Questions

- **Mamba issues**: See MAMBA_FIN_AI1_RULES.md
- **Backend issues**: See BACKEND_EXECUTION_RUNBOOK.md
- **Script issues**: Check scripts/ directory permissions (`ls -lh scripts/`)
- **Data issues**: Check backend logs in Terminal 1

---

**Status**: Production Ready
**Last Verified**: January 21, 2026
**Version**: 1.0.0

**All developers must use this guide for backend execution and reporting.**
