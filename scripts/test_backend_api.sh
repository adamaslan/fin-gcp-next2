#!/bin/bash
# ============================================================================
# Backend API Test Suite
# Tests all endpoints and saves responses
# Usage: ./test_backend_api.sh
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8080}"
RUN_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/backend_test_results"
RUN_DIR="$RESULTS_DIR/$RUN_TIMESTAMP"

# Create directories
mkdir -p "$RUN_DIR"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

test_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local output_file=$4

    log_info "Testing: $method $endpoint"

    if [ "$method" = "GET" ]; then
        curl -s -w "\n" "$API_URL$endpoint" | jq . > "$output_file" 2>/dev/null || echo "{}" > "$output_file"
    else
        curl -s -w "\n" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" | jq . > "$output_file" 2>/dev/null || echo "{}" > "$output_file"
    fi

    if [ -s "$output_file" ]; then
        log_success "Response saved: $output_file"
    else
        log_warning "Empty response: $output_file"
    fi
}

# ============================================================================
# EXECUTION
# ============================================================================

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          MCP Finance Backend API Test Suite                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo "API URL: $API_URL"
echo "Run ID: $RUN_TIMESTAMP"
echo "Results: $RUN_DIR"
echo ""

# Check if server is running
log_info "Checking backend health..."
if ! curl -s "$API_URL/" > /dev/null 2>&1; then
    log_error "Backend not responding on $API_URL"
    log_error "Please start the backend with: python main.py"
    exit 1
fi
log_success "Backend is running"
echo ""

# Test 1: Health Endpoints
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}1. HEALTH ENDPOINTS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/" "GET" "" "$RUN_DIR/01_health.json"
test_endpoint "/health" "GET" "" "$RUN_DIR/02_health_detailed.json"

echo ""

# Test 2: Trade Plan
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}2. TRADE PLANNING${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/trade-plan" "POST" \
    '{"symbol":"AAPL","period":"1mo"}' \
    "$RUN_DIR/03_trade_plan_aapl.json"

test_endpoint "/api/trade-plan" "POST" \
    '{"symbol":"MSFT","period":"1mo"}' \
    "$RUN_DIR/04_trade_plan_msft.json"

test_endpoint "/api/trade-plan" "POST" \
    '{"symbol":"GOOGL","period":"1mo"}' \
    "$RUN_DIR/05_trade_plan_googl.json"

echo ""

# Test 3: Scan Trades
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}3. TRADE SCANNING${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/scan" "POST" \
    '{"universe":"sp500","max_results":10}' \
    "$RUN_DIR/06_scan_sp500.json"

test_endpoint "/api/scan" "POST" \
    '{"universe":"nasdaq100","max_results":5}' \
    "$RUN_DIR/07_scan_nasdaq.json"

echo ""

# Test 4: Portfolio Risk
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}4. PORTFOLIO RISK ASSESSMENT${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/portfolio-risk" "POST" \
    '{
        "positions": [
            {"symbol":"AAPL","shares":100,"entry_price":150.0},
            {"symbol":"MSFT","shares":50,"entry_price":400.0},
            {"symbol":"GOOGL","shares":75,"entry_price":140.0}
        ]
    }' \
    "$RUN_DIR/08_portfolio_risk.json"

echo ""

# Test 5: Morning Brief
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}5. MORNING BRIEF${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/morning-brief" "POST" \
    '{
        "watchlist":["AAPL","MSFT","GOOGL","TSLA","NVDA"],
        "market_region":"US"
    }' \
    "$RUN_DIR/09_morning_brief.json"

echo ""

# Test 6: Analyze Security
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}6. SECURITY ANALYSIS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/analyze" "POST" \
    '{"symbol":"AAPL","period":"1mo","include_ai":false}' \
    "$RUN_DIR/10_analyze_aapl.json"

echo ""

# Test 7: Get Signals
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}7. SIGNAL RETRIEVAL${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/signals/AAPL" "GET" "" "$RUN_DIR/11_signals_aapl.json"

echo ""

# Test 8: Compare Securities
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}8. SECURITY COMPARISON${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/compare" "POST" \
    '{"symbols":["AAPL","MSFT","GOOGL"],"period":"1mo"}' \
    "$RUN_DIR/12_compare.json"

echo ""

# Test 9: Statistics
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}9. BACKEND STATISTICS${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "/api/stats" "GET" "" "$RUN_DIR/13_stats.json"

echo ""

# Summary
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All tests completed!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Count results
TOTAL_FILES=$(find "$RUN_DIR" -name "*.json" -type f | wc -l)
echo "Results Location: $RUN_DIR"
echo "Total Responses: $TOTAL_FILES"
echo ""

# List files with sizes
echo "Generated Files:"
ls -lh "$RUN_DIR"/*.json | awk '{printf "  %-50s %8s\n", $9, $5}'

echo ""
echo "Next Steps:"
echo "  1. Analyze responses:"
echo "     python $PROJECT_ROOT/scripts/analyze_responses.py $RUN_DIR $RUN_DIR/analysis.md"
echo ""
echo "  2. Generate full report:"
echo "     python $PROJECT_ROOT/scripts/generate_backend_report.py $RUN_DIR $RUN_DIR/COMPLETE_REPORT.md"
echo ""
echo "  3. View results:"
echo "     ls -lh $RUN_DIR/"
echo ""
