#!/bin/bash
# ============================================================================
# Quick Start: Backend Testing & Report Generation
# One-command execution of entire backend test suite
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/Users/adamaslan/code/gcp app w mcp"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
BACKEND_DIR="$PROJECT_ROOT/mcp-finance1"

# Helper functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

print_header "MCP Finance Backend - Quick Start"

# Check if backend is running
print_info "Checking backend health..."
if ! curl -s http://localhost:8080/ > /dev/null 2>&1; then
    print_error "Backend not running on http://localhost:8080"
    echo ""
    echo "To start the backend, run in another terminal:"
    echo "  cd $BACKEND_DIR"
    echo "  source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"
    echo "  mamba activate fin-ai1"
    echo "  python main.py"
    echo ""
    exit 1
fi
print_success "Backend is running"

# Run API tests
print_header "Step 1: Testing All API Endpoints"
bash "$SCRIPTS_DIR/test_backend_api.sh"

# Get the latest run directory
LATEST_RUN=$(ls -td "$PROJECT_ROOT/backend_test_results"/*/ 2>/dev/null | head -1)

if [ -z "$LATEST_RUN" ]; then
    print_error "No test results found"
    exit 1
fi

LATEST_RUN="${LATEST_RUN%/}"  # Remove trailing slash
print_success "Test results saved to: $LATEST_RUN"

# Generate analysis
print_header "Step 2: Analyzing API Responses"
python "$SCRIPTS_DIR/analyze_backend_responses.py" \
    "$LATEST_RUN" \
    "$LATEST_RUN/analysis.md"

# Generate comprehensive report
print_header "Step 3: Generating Comprehensive Report"
python "$SCRIPTS_DIR/generate_backend_report.py" \
    "$LATEST_RUN" \
    "$LATEST_RUN/COMPLETE_REPORT.md"

# Display summary
print_header "Backend Testing Complete"

echo -e "${GREEN}All tests and reports have been generated!${NC}\n"

echo "Results Location:"
echo "  $LATEST_RUN"
echo ""

echo "Generated Files:"
echo "  1. Analysis Report:"
echo "     cat $LATEST_RUN/analysis.md"
echo ""
echo "  2. Complete Report:"
echo "     cat $LATEST_RUN/COMPLETE_REPORT.md"
echo ""
echo "  3. All API Responses:"
ls -lh "$LATEST_RUN"/*.json | awk '{printf "     - %s (%s)\n", $9, $5}'
echo ""

echo "Next Steps:"
echo "  - Review the analysis: $LATEST_RUN/analysis.md"
echo "  - Review full report: $LATEST_RUN/COMPLETE_REPORT.md"
echo "  - Commit results to git"
echo ""

print_success "Complete!"
