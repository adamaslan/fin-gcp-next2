#!/bin/bash
# Pre-commit hook for sensitive data scanning
# Install with: /sensitive-data-scan --install-hook
# Remove with: /sensitive-data-scan --remove-hook
#
# This hook runs on every git commit and prevents committing sensitive data

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PATTERNS_DIR="$(git rev-parse --show-toplevel)/.claude/skills/sensitive-data-scan/patterns"
TMPFILE=$(mktemp)
CRITICAL_FOUND=0
WARNING_FOUND=0

# Cleanup function
cleanup() {
    rm -f "$TMPFILE"
}
trap cleanup EXIT

# Function to print colored output
print_error() {
    echo -e "${RED}$1${NC}" >&2
}

print_warning() {
    echo -e "${YELLOW}$1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}" >&2
}

print_info() {
    echo -e "${BLUE}$1${NC}" >&2
}

# Function to scan patterns from YAML file
scan_patterns() {
    local pattern_file=$1
    local severity=$2

    # Extract regex patterns from YAML (simplified parsing)
    while IFS= read -r line; do
        if [[ $line =~ ^\ \ \ \ regex: ]]; then
            # Extract regex pattern
            regex=$(echo "$line" | sed "s/.*regex: '\(.*\)'/\1/")

            # Search staged files for pattern
            git diff --cached --name-only | while read -r staged_file; do
                if [[ -f "$staged_file" ]] && [[ ! "$staged_file" =~ \.git ]]; then
                    if grep -q "$regex" "$staged_file" 2>/dev/null; then
                        echo "$staged_file|$regex|$severity" >> "$TMPFILE"
                    fi
                fi
            done
        fi
    done < "$pattern_file"
}

# Function to analyze finding with context
analyze_finding() {
    local file=$1
    local pattern=$2
    local severity=$3

    # Get line number and context
    local line_num=$(grep -n "$pattern" "$file" 2>/dev/null | head -1 | cut -d: -f1)
    local context=$(sed -n "${line_num}p" "$file")

    # Truncate long lines
    if [[ ${#context} -gt 80 ]]; then
        context="${context:0:77}..."
    fi

    echo "$file:$line_num|$context|$severity"
}

# Main scanning logic
echo -e "${BLUE}🔒 Scanning staged files for sensitive data...${NC}"
echo ""

# Check if patterns directory exists
if [[ ! -d "$PATTERNS_DIR" ]]; then
    echo -e "${YELLOW}⚠️  Pattern directory not found: $PATTERNS_DIR${NC}"
    echo "    Skipping detailed pattern checking"
    echo ""
fi

# Scan for critical patterns
CRITICAL_PATTERNS=(
    # API Keys
    'AIzaSy[A-Za-z0-9_-]{35}'
    'sk_live_[A-Za-z0-9_]{24,}'
    'sk_test_[A-Za-z0-9_]{24,}'
    'sk-proj-[A-Za-z0-9_-]{48,}'
    'GOCSPX-[A-Za-z0-9_-]{24,}'

    # Credentials
    '-----BEGIN.*PRIVATE KEY-----'
    'AKIA[0-9A-Z]{16}'
    'npg_[A-Za-z0-9_]{20,}'
    'password\s*[=:]\s*["\047]?([^\s"\047;]+)["\047]?'
    'aws_secret_access_key\s*[=:]\s*[A-Za-z0-9/+=]{40}'

    # Service Accounts
    '"type":\s*"service_account"'
    'private_key'
)

FINDINGS=()

echo "Checking staged files against critical patterns..."

for pattern in "${CRITICAL_PATTERNS[@]}"; do
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            if grep -E "$pattern" "$file" > /dev/null 2>&1; then
                line_num=$(grep -nE "$pattern" "$file" | head -1 | cut -d: -f1)
                context=$(sed -n "${line_num}p" "$file")

                # Truncate long lines for display
                if [[ ${#context} -gt 70 ]]; then
                    context="${context:0:67}..."
                fi

                FINDINGS+=("CRITICAL|$file|$line_num|$context|$pattern")
                CRITICAL_FOUND=1
            fi
        fi
    done < <(git diff --cached --name-only --diff-filter=ACM)
done

# Display results
if [[ $CRITICAL_FOUND -eq 1 ]]; then
    echo ""
    print_error "❌ SENSITIVE DATA DETECTED IN STAGED FILES"
    echo ""
    echo -e "${RED}Critical Issues Found:${NC}"

    for finding in "${FINDINGS[@]}"; do
        IFS='|' read -r severity file line context pattern <<< "$finding"
        echo ""
        echo -e "${RED}  🔴 $file:$line${NC}"
        echo "     Pattern: $pattern"
        echo "     Content: $context"
    done

    echo ""
    echo -e "${RED}DO NOT COMMIT SENSITIVE DATA!${NC}"
    echo ""
    echo "Recommended fixes:"
    echo "  1. Remove the sensitive data from the file"
    echo "  2. Stage the fix: git add <file>"
    echo "  3. Try commit again"
    echo ""
    echo "To identify the secret type:"
    echo "  - If starts with 'AIzaSy': Google API Key (rotate at console.cloud.google.com)"
    echo "  - If starts with 'sk_live': Stripe Live Key (rotate at dashboard.stripe.com)"
    echo "  - If starts with 'sk_test': Stripe Test Key (rotate at dashboard.stripe.com)"
    echo "  - If starts with 'AKIA': AWS Access Key (deactivate at console.aws.amazon.com)"
    echo "  - If contains 'PRIVATE KEY': SSH Key (regenerate immediately)"
    echo "  - If contains 'password': Database credentials (rotate password)"
    echo ""
    echo "For help, run: /sensitive-doc-creator --verify=<file>"
    echo ""
    echo "To bypass this check (not recommended):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi

# Check for warning patterns
WARNING_PATTERNS=(
    # PII
    '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    '(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'

    # Financial
    '\bpy_[A-Za-z0-9]{20,}\b'
    '\binv_[A-Za-z0-9]{20,}\b'

    # GCP
    'projects/([a-z-]+)/secrets/([a-z0-9_-]+)'
)

WARNING_FINDINGS=()

echo "Checking for potential PII and financial data..."

for pattern in "${WARNING_PATTERNS[@]}"; do
    while IFS= read -r file; do
        # Skip certain files
        if [[ "$file" =~ \.env\.example$ ]] || \
           [[ "$file" =~ README\.md$ ]] || \
           [[ "$file" =~ /templates/ ]]; then
            continue
        fi

        if [[ -f "$file" ]]; then
            if grep -E "$pattern" "$file" > /dev/null 2>&1; then
                line_num=$(grep -nE "$pattern" "$file" | head -1 | cut -d: -f1)
                context=$(sed -n "${line_num}p" "$file")

                # Truncate
                if [[ ${#context} -gt 70 ]]; then
                    context="${context:0:67}..."
                fi

                WARNING_FINDINGS+=("WARNING|$file|$line_num|$context|$pattern")
                WARNING_FOUND=1
            fi
        fi
    done < <(git diff --cached --name-only --diff-filter=ACM)
done

# Display warnings
if [[ $WARNING_FOUND -eq 1 ]]; then
    echo ""
    print_warning "⚠️  POTENTIAL SENSITIVE DATA - PLEASE REVIEW"
    echo ""
    echo -e "${YELLOW}Findings (may be false positives - please verify):${NC}"

    for finding in "${WARNING_FINDINGS[@]}"; do
        IFS='|' read -r severity file line context pattern <<< "$finding"
        echo ""
        echo -e "${YELLOW}  🟡 $file:$line${NC}"
        echo "     Content: $context"
    done

    echo ""
    echo -e "${YELLOW}These may be false positives if:${NC}"
    echo "  - Data is in .env.example (safe)"
    echo "  - Email is generic like user@example.com (safe)"
    echo "  - Transaction ID is from test data (safe)"
    echo ""
    echo "To verify, run: /sensitive-doc-creator --verify=<file>"
    echo ""
    echo "If these are real customer data, please fix before committing."
    echo ""
fi

# Final status
if [[ $CRITICAL_FOUND -eq 0 ]]; then
    echo ""
    print_success "✅ Security scan passed - no critical issues found"
    if [[ $WARNING_FOUND -eq 1 ]]; then
        print_warning "⚠️  Some warnings found - review if needed"
    fi
    echo ""
    exit 0
else
    exit 1
fi

