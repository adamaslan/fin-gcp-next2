# Makefile for MCP Finance Project
# Provides convenient commands for running scans and managing environments

# Environment Configuration
PYTHON_BIN := /opt/homebrew/Caskroom/miniforge/base/envs/fin-ai1/bin/python3
CONDA_BASE := /opt/homebrew/Caskroom/miniforge/base
ENV_NAME := fin-ai1

# Directories
PROJECT_ROOT := $(shell pwd)
CLOUD_RUN_DIR := $(PROJECT_ROOT)/mcp-finance1/cloud-run
BACKEND_DIR := $(PROJECT_ROOT)/backend

# Scripts
BETA1_SCRIPT := $(CLOUD_RUN_DIR)/scripts/run_beta1_scan.py
ACTIVATE_SCRIPT := $(PROJECT_ROOT)/activate_and_run.sh

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  MCP Finance - Available Commands$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Environment:$(NC) $(ENV_NAME)"
	@echo "$(YELLOW)Python:$(NC)      $(PYTHON_BIN)"
	@echo ""

.PHONY: beta1-scan
beta1-scan: ## Run Beta1 universe scan (direct Python method)
	@echo "$(BLUE)Running Beta1 Scan (Direct Python Method)...$(NC)"
	@cd "$(CLOUD_RUN_DIR)" && "$(PYTHON_BIN)" scripts/run_beta1_scan.py

.PHONY: beta1-scan-activate
beta1-scan-activate: ## Run Beta1 scan using activation script
	@echo "$(BLUE)Running Beta1 Scan (Activation Script Method)...$(NC)"
	@"$(ACTIVATE_SCRIPT)"

.PHONY: beta1-scan-verbose
beta1-scan-verbose: ## Run Beta1 scan with verbose output
	@echo "$(BLUE)Running Beta1 Scan (Verbose Mode)...$(NC)"
	@echo "$(YELLOW)Working Directory:$(NC) $(CLOUD_RUN_DIR)"
	@echo "$(YELLOW)Python Binary:$(NC)     $(PYTHON_BIN)"
	@echo "$(YELLOW)Script:$(NC)            scripts/run_beta1_scan.py"
	@echo ""
	@cd "$(CLOUD_RUN_DIR)" && "$(PYTHON_BIN)" scripts/run_beta1_scan.py

.PHONY: verify-env
verify-env: ## Verify environment setup
	@echo "$(BLUE)Verifying Environment Setup...$(NC)"
	@echo ""
	@echo "$(YELLOW)Python Binary:$(NC)"
	@if [ -f "$(PYTHON_BIN)" ]; then \
		echo "  $(GREEN)✓$(NC) Found: $(PYTHON_BIN)"; \
		echo "  Version: $$("$(PYTHON_BIN)" --version)"; \
	else \
		echo "  $(RED)✗$(NC) Not found: $(PYTHON_BIN)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Beta1 Script:$(NC)"
	@if [ -f "$(BETA1_SCRIPT)" ]; then \
		echo "  $(GREEN)✓$(NC) Found: $(BETA1_SCRIPT)"; \
	else \
		echo "  $(RED)✗$(NC) Not found: $(BETA1_SCRIPT)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Activation Script:$(NC)"
	@if [ -x "$(ACTIVATE_SCRIPT)" ]; then \
		echo "  $(GREEN)✓$(NC) Found and executable: $(ACTIVATE_SCRIPT)"; \
	elif [ -f "$(ACTIVATE_SCRIPT)" ]; then \
		echo "  $(YELLOW)⚠$(NC)  Found but not executable: $(ACTIVATE_SCRIPT)"; \
		echo "     Run: chmod +x $(ACTIVATE_SCRIPT)"; \
	else \
		echo "  $(RED)✗$(NC) Not found: $(ACTIVATE_SCRIPT)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Conda/Mamba Base:$(NC)"
	@if [ -d "$(CONDA_BASE)" ]; then \
		echo "  $(GREEN)✓$(NC) Found: $(CONDA_BASE)"; \
	else \
		echo "  $(RED)✗$(NC) Not found: $(CONDA_BASE)"; \
	fi
	@echo ""

.PHONY: test-python
test-python: ## Test Python environment and imports
	@echo "$(BLUE)Testing Python Environment...$(NC)"
	@echo ""
	@"$(PYTHON_BIN)" -c "import sys; print('Python:', sys.version); print('Executable:', sys.executable)"
	@echo ""
	@echo "$(YELLOW)Testing critical imports:$(NC)"
	@"$(PYTHON_BIN)" -c "import pandas; print('  $(GREEN)✓$(NC) pandas:', pandas.__version__)" || echo "  $(RED)✗$(NC) pandas: FAILED"
	@"$(PYTHON_BIN)" -c "import numpy; print('  $(GREEN)✓$(NC) numpy:', numpy.__version__)" || echo "  $(RED)✗$(NC) numpy: FAILED"
	@"$(PYTHON_BIN)" -c "import yfinance; print('  $(GREEN)✓$(NC) yfinance:', yfinance.__version__)" || echo "  $(RED)✗$(NC) yfinance: FAILED"
	@"$(PYTHON_BIN)" -c "from google.cloud import firestore; print('  $(GREEN)✓$(NC) google-cloud-firestore')" || echo "  $(RED)✗$(NC) google-cloud-firestore: FAILED"
	@echo ""

.PHONY: list-envs
list-envs: ## List all mamba/conda environments
	@echo "$(BLUE)Available Mamba/Conda Environments:$(NC)"
	@echo ""
	@if [ -d "$(CONDA_BASE)/envs" ]; then \
		ls -1 "$(CONDA_BASE)/envs" | sed 's/^/  - /'; \
	else \
		echo "  $(RED)✗$(NC) No environments directory found"; \
	fi
	@echo ""

.PHONY: activate-env
activate-env: ## Show command to activate environment manually
	@echo "$(BLUE)To manually activate the environment:$(NC)"
	@echo ""
	@echo "  mamba activate $(ENV_NAME)"
	@echo ""
	@echo "$(YELLOW)If 'mamba' command is not found, run:$(NC)"
	@echo ""
	@echo "  source $(CONDA_BASE)/etc/profile.d/conda.sh"
	@echo "  source $(CONDA_BASE)/etc/profile.d/mamba.sh"
	@echo "  mamba activate $(ENV_NAME)"
	@echo ""

.PHONY: clean
clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓$(NC) Cleaned Python cache files"

.PHONY: install-deps
install-deps: ## Install/update dependencies in fin-ai1 environment
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@echo "$(YELLOW)Note: Run this in an activated mamba environment$(NC)"
	@echo ""
	@echo "Run manually:"
	@echo "  mamba activate $(ENV_NAME)"
	@echo "  mamba install -c conda-forge pandas numpy yfinance google-cloud-firestore"
	@echo ""

.PHONY: check-firestore
check-firestore: ## Check Firebase/Firestore configuration
	@echo "$(BLUE)Checking Firebase Configuration...$(NC)"
	@echo ""
	@echo "$(YELLOW)GCP_PROJECT_ID:$(NC)"
	@if [ -n "$$GCP_PROJECT_ID" ]; then \
		echo "  $(GREEN)✓$(NC) Set: $$GCP_PROJECT_ID"; \
	else \
		echo "  $(YELLOW)⚠$(NC)  Not set (will use default: ttb-lang1)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Google Application Credentials:$(NC)"
	@if [ -n "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "  $(GREEN)✓$(NC) Set: $$GOOGLE_APPLICATION_CREDENTIALS"; \
		if [ -f "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
			echo "  $(GREEN)✓$(NC) File exists"; \
		else \
			echo "  $(RED)✗$(NC) File not found"; \
		fi \
	else \
		echo "  $(YELLOW)⚠$(NC)  Not set (using default credentials)"; \
	fi
	@echo ""
	@echo "$(YELLOW)To authenticate with gcloud:$(NC)"
	@echo "  gcloud auth application-default login"
	@echo ""

.PHONY: all-checks
all-checks: verify-env test-python check-firestore ## Run all verification checks
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  All checks complete!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo ""

# ============================================================================
# Security Scanning Commands
# ============================================================================

.PHONY: security-scan-quick
security-scan-quick: ## Quick security scan of staged files only
	@echo "$(BLUE)Running quick security scan (staged files)...$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking for sensitive patterns in staged files...$(NC)"
	@/sensitive-data-scan --quick 2>&1 || echo "$(RED)Security issues found. See above for details.$(NC)"

.PHONY: security-scan-full
security-scan-full: ## Full security scan of entire repository
	@echo "$(BLUE)Running full security scan...$(NC)"
	@echo ""
	@/sensitive-data-scan --full --output=security-audit-$(shell date +%Y-%m-%d).md
	@echo "$(GREEN)✓$(NC) Full scan complete: security-audit-$(shell date +%Y-%m-%d).md"
	@echo ""
	@echo "Review the report for findings and remediation steps."

.PHONY: security-verify-file
security-verify-file: ## Verify specific file for sensitive data
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: FILE variable required$(NC)"; \
		echo "Usage: make security-verify-file FILE=path/to/file.md"; \
		exit 1; \
	fi
	@echo "$(BLUE)Verifying $(FILE) for sensitive data...$(NC)"
	@echo ""
	@/sensitive-data-scan --verify=$(FILE)

.PHONY: security-hook-install
security-hook-install: ## Install pre-commit security hook
	@echo "$(BLUE)Installing pre-commit security hook...$(NC)"
	@echo ""
	@/sensitive-data-scan --install-hook
	@echo "$(GREEN)✓$(NC) Pre-commit hook installed"
	@echo "$(YELLOW)Security scan will run automatically on next commit$(NC)"

.PHONY: security-hook-remove
security-hook-remove: ## Remove pre-commit security hook
	@echo "$(BLUE)Removing pre-commit security hook...$(NC)"
	@echo ""
	@/sensitive-data-scan --remove-hook || rm -f .git/hooks/pre-commit
	@echo "$(GREEN)✓$(NC) Pre-commit hook removed"

.PHONY: security-doc-create
security-doc-create: ## Create safe documentation (interactive)
	@if [ -z "$(INPUT)" ]; then \
		echo "$(RED)Error: INPUT variable required$(NC)"; \
		echo "Usage: make security-doc-create INPUT=path/to/source OUTPUT=path/to/output.md"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		echo "$(RED)Error: OUTPUT variable required$(NC)"; \
		echo "Usage: make security-doc-create INPUT=path/to/source OUTPUT=path/to/output.md"; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating safe documentation...$(NC)"
	@echo "Input:  $(INPUT)"
	@echo "Output: $(OUTPUT)"
	@echo ""
	@/sensitive-doc-creator --input=$(INPUT) --output=$(OUTPUT) --interactive
	@echo "$(GREEN)✓$(NC) Safe documentation created: $(OUTPUT)"

# Default target
.DEFAULT_GOAL := help
