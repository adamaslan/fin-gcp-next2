---
name: mcp-check
description: Check MCP server health, connectivity, and stock data functionality for the Python backend
---

Check the health and functionality of the MCP (Model Context Protocol) server for stock data.

## Step 1: Check if MCP Server is Running

```bash
# Check if process is running
ps aux | grep "python.*main.py" | grep -v grep || echo "MCP server not running"

# Check port 8000
lsof -i:8000 || echo "Port 8000 not in use"

# Try to connect
curl -s http://localhost:8000/health && echo "✅ MCP Server is running" || echo "❌ MCP Server is not responding"
```

## Step 2: Start MCP Server (if not running)

```bash
cd mcp-finance1/cloud-run

# Activate mamba environment first
mamba activate mcp-finance-backend || micromamba activate mcp-finance-backend

# Start server
python3 main.py &
echo "MCP server starting... waiting 3 seconds"
sleep 3
```

## Step 3: Test Health Endpoint

```bash
curl -X GET http://localhost:8000/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-18T...",
  "version": "1.0.0"
}
```

## Step 4: Test Stock Data Endpoint

```bash
# Get stock data for AAPL
curl -X GET "http://localhost:8000/stocks/AAPL" | jq

# Get multiple stocks
curl -X GET "http://localhost:8000/stocks?symbols=AAPL,GOOGL,MSFT" | jq
```

**Expected Response:**
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 1.25,
  "changePercent": 0.84,
  "timestamp": "2024-01-18T..."
}
```

## Step 5: Verify Database Connection

```bash
# MCP server should connect to same database as frontend
curl -X GET http://localhost:8000/db-status | jq
```

## Step 6: Check Logs

```bash
cd mcp-finance1/cloud-run

# View recent logs
tail -f logs/mcp-server.log 2>/dev/null || echo "No log file found"

# Or check stdout if running in terminal
ps aux | grep "python.*main.py" | grep -v grep
```

## Common Issues

### Issue: "Connection refused"
**Cause:** MCP server not running
**Solution:**
```bash
cd mcp-finance1/cloud-run
python3 main.py
```

### Issue: "Module not found"
**Cause:** Python dependencies not installed or environment not activated
**Solution:**
```bash
cd mcp-finance1/cloud-run

# Activate mamba environment
mamba activate mcp-finance-backend

# If environment doesn't exist, create it
mamba env create -f environment.yml -n mcp-finance-backend

# Verify packages installed
mamba list
```

### Issue: "Port 8000 already in use"
**Cause:** Another process using port 8000
**Solution:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8001 python3 main.py
```

### Issue: "Stock data not found"
**Cause:** API key missing or invalid
**Solution:**
Check `.env` file has:
```
ALPHA_VANTAGE_API_KEY=your_key_here
```

## Quick Health Check

Run this one-liner:
```bash
curl -s http://localhost:8000/health && echo " - MCP Server OK" || (echo " - MCP Server DOWN" && cd mcp-finance1/cloud-run && python3 main.py &)
```

## Integration Test

Test full integration between frontend and MCP server:

```bash
# 1. Ensure both servers running
curl -s http://localhost:3000/api/health > /dev/null && echo "✅ Frontend OK" || echo "❌ Frontend DOWN"
curl -s http://localhost:8000/health > /dev/null && echo "✅ MCP Server OK" || echo "❌ MCP Server DOWN"

# 2. Test frontend calling MCP
curl -s http://localhost:3000/api/stocks/AAPL | jq
```

---

**Remember**: The MCP server provides real-time stock data to the frontend. Both must be running for full functionality.
