#!/bin/bash
#
# Run Swing Trading MCP Test Suite with fin-ai1 Environment
#
# This script ensures the fin-ai1 Conda/Mamba environment is activated
# before running the comprehensive swing trading test suite.
#
# Features:
# - Activates fin-ai1 Conda environment
# - Runs functional tests on all 9 MCP tools
# - Runs regression tests against baselines
# - Generates combined test reports
#
# Usage:
#   bash run_swing_tests.sh              # Run functional + regression tests
#   bash run_swing_tests.sh --functional # Run functional tests only
#   bash run_swing_tests.sh --regression # Run regression tests only
#

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Swing Trading MCP Test Suite"
echo "================================"
echo ""
echo "📍 Project directory: $PROJECT_DIR"
echo "🐍 Environment: fin-ai1"
echo ""

# Detect shell and setup mamba
setup_mamba() {
    # Try different methods to activate mamba
    if command -v mamba &> /dev/null; then
        eval "$(mamba shell hook --shell bash)"
    elif command -v conda &> /dev/null; then
        eval "$(conda shell.bash hook)"
    else
        echo "❌ Neither mamba nor conda found!"
        echo "Please install mamba from: https://mamba.readthedocs.io"
        exit 1
    fi
}

# Activate fin-ai1 environment
activate_environment() {
    setup_mamba

    if ! mamba activate fin-ai1 2>/dev/null; then
        echo "❌ Failed to activate fin-ai1 environment"
        echo ""
        echo "Available mamba environments:"
        mamba env list
        echo ""
        echo "To create fin-ai1, run:"
        echo "  mamba create -n fin-ai1 python=3.11 -c conda-forge"
        exit 1
    fi

    echo "✅ fin-ai1 environment activated"
    python --version
    echo ""
}

# Run the test suite
run_tests() {
    local test_type="${1:-all}"

    case "$test_type" in
        functional)
            echo "Running functional tests only..."
            python swing_trading_mcp_test.py
            ;;
        regression)
            echo "Running regression tests only..."
            python swing_trading_regression_tests.py
            ;;
        all|*)
            echo "Running combined test suite (functional + regression)..."
            python swing_trading_mcp_test.py
            ;;
    esac
}

# Main execution
echo "⏳ Activating environment..."
activate_environment

echo "⏳ Running tests..."
run_tests "$1"

echo ""
echo "✅ Test suite complete!"
echo ""
echo "📊 Results saved to: nu-logs/"
echo ""
echo "To view results:"
echo "  cat nu-logs/swing_trading_test_*/test.log"
echo "  cat nu-logs/swing_trading_test_*/SUMMARY.json"
echo "  cat nu-logs/swing_trading_test_*/COMBINED_TEST_REPORT.json"
