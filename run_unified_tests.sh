#!/bin/bash
#
# UNIFIED TEST RUNNER - All MCP + E2E Tests
#
# Runs all tests using configuration from test_config.py
# Edit test_config.py to change test parameters (MU, NVDA, period, etc.)
#
# Usage:
#   bash run_unified_tests.sh          # Run all tests
#   bash run_unified_tests.sh mcp      # Run MCP tests only
#   bash run_unified_tests.sh e2e      # Run E2E tests only
#   bash run_unified_tests.sh config   # Show current config
#

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "🚀 UNIFIED TEST SUITE"
echo "========================================"
echo "📍 Directory: $PROJECT_DIR"
echo "📋 Config: test_config.py"
echo ""

# Show config
show_config() {
    echo "Current Test Configuration:"
    echo "----------------------------------------"
    python3 -c "from test_config import print_config; print_config()"
    echo ""
}

# Run MCP tests
run_mcp_tests() {
    echo "🧪 Running MCP Tests (9 tools)..."
    echo "========================================"

    # Activate conda and run
    source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
    conda activate fin-ai1

    python unified_mcp_test.py

    echo ""
    echo "✅ MCP Tests Complete"
    echo ""
}

# Run E2E tests
run_e2e_tests() {
    echo "🌐 Running E2E Tests..."
    echo "========================================"

    cd "$PROJECT_DIR/nextjs-mcp-finance"

    # Check if frontend is running
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend detected at localhost:3000"
    else
        echo "⚠️  Frontend not running. Start it with: npm run dev"
        echo "   Attempting to run tests anyway..."
    fi

    # Run E2E tests
    npm run test:e2e -- e2e/unified/ || echo "⚠️ Some E2E tests may have failed"

    cd "$PROJECT_DIR"

    echo ""
    echo "✅ E2E Tests Complete"
    echo ""
}

# Main execution
case "${1:-all}" in
    config)
        show_config
        ;;
    mcp)
        show_config
        run_mcp_tests
        ;;
    e2e)
        show_config
        run_e2e_tests
        ;;
    all|*)
        show_config
        run_mcp_tests
        run_e2e_tests

        echo ""
        echo "========================================"
        echo "✅ ALL TESTS COMPLETE"
        echo "========================================"
        echo ""
        echo "Results:"
        echo "  MCP:  nu-logs/unified_test_*/unified_test_report.json"
        echo "  E2E:  nextjs-mcp-finance/test-results/"
        echo ""
        echo "To change parameters, edit: test_config.py"
        echo ""
        ;;
esac
