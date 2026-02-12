#!/bin/zsh
# Activate fin-ai1 environment and run Beta1 scan script
# This script properly initializes mamba and runs the scan in one command

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print formatted messages
print_info() {
    echo "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo "${GREEN}✓${NC} $1"
}

print_error() {
    echo "${RED}✗${NC} $1"
}

print_warning() {
    echo "${YELLOW}⚠${NC} $1"
}

# Header
echo ""
echo "============================================"
echo "  Beta1 Scan - Activation & Execution"
echo "============================================"
echo ""

# 1. Source conda/mamba initialization scripts
print_info "Initializing mamba environment..."

CONDA_BASE="/opt/homebrew/Caskroom/miniforge/base"
CONDA_SH="${CONDA_BASE}/etc/profile.d/conda.sh"
MAMBA_SH="${CONDA_BASE}/etc/profile.d/mamba.sh"

if [ -f "$CONDA_SH" ]; then
    source "$CONDA_SH"
    print_success "Conda shell support loaded"
else
    print_error "Conda shell support not found at: $CONDA_SH"
    exit 1
fi

if [ -f "$MAMBA_SH" ]; then
    source "$MAMBA_SH"
    print_success "Mamba shell support loaded"
else
    print_warning "Mamba shell support not found (optional)"
fi

# 2. Activate the fin-ai1 environment
print_info "Activating fin-ai1 environment..."
mamba activate fin-ai1

if [ $? -eq 0 ]; then
    print_success "Environment activated: fin-ai1"
    print_info "Python: $(which python3)"
    print_info "Version: $(python3 --version)"
else
    print_error "Failed to activate fin-ai1 environment"
    exit 1
fi

# 3. Change to script directory
SCRIPT_DIR="/Users/adamaslan/code/gcp app w mcp/mcp-finance1/cloud-run"
print_info "Changing to script directory..."
cd "$SCRIPT_DIR"

if [ $? -eq 0 ]; then
    print_success "Working directory: $SCRIPT_DIR"
else
    print_error "Failed to change to directory: $SCRIPT_DIR"
    exit 1
fi

# 4. Verify script exists
SCRIPT_NAME="scripts/run_beta1_scan.py"
if [ ! -f "$SCRIPT_NAME" ]; then
    print_error "Script not found: $SCRIPT_NAME"
    print_info "Current directory contents:"
    ls -la
    exit 1
fi

print_success "Script found: $SCRIPT_NAME"
echo ""

# 5. Run the script with any arguments passed to this script
print_info "Executing scan script..."
echo "============================================"
echo ""

python3 "$SCRIPT_NAME" "$@"

SCRIPT_EXIT_CODE=$?

echo ""
echo "============================================"

if [ $SCRIPT_EXIT_CODE -eq 0 ]; then
    print_success "Script completed successfully"
else
    print_error "Script failed with exit code: $SCRIPT_EXIT_CODE"
fi

exit $SCRIPT_EXIT_CODE
