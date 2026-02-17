# Mamba & fin-ai1 Environment Rules for MCP Finance Project

**Purpose**: Establish strict, consistent rules for using Mamba and the fin-ai1 environment
**Status**: Official Project Standards
**Last Updated**: January 21, 2026
**Applies To**: All developers and CI/CD pipelines

---

## Table of Contents

1. [Core Rules](#core-rules)
2. [fin-ai1 Environment Standards](#fin-ai1-environment-standards)
3. [Mamba Command Reference](#mamba-command-reference)
4. [Shell Initialization](#shell-initialization)
5. [Package Management](#package-management)
6. [Development Workflow](#development-workflow)
7. [CI/CD Guidelines](#cicd-guidelines)
8. [Troubleshooting](#troubleshooting)

---

## Core Rules

### Rule 1: MAMBA ONLY - Never Use conda, micromamba, or pip Directly

**This is ABSOLUTE. No exceptions.**

❌ **FORBIDDEN**:
```bash
conda activate fin-ai1          # WRONG
source activate fin-ai1         # WRONG
micromamba activate fin-ai1     # WRONG
pip install package             # WRONG
```

✅ **REQUIRED**:
```bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1          # CORRECT
mamba install -c conda-forge package  # CORRECT
```

**Why**: Mamba is:
- 5x faster than conda for dependency resolution
- More reliable for complex dependencies
- Industry standard for scientific Python
- Fully compatible with all conda packages

**Penalty for violation**: Unpredictable environments, slow builds, broken dependencies

---

### Rule 2: fin-ai1 is the ONLY Environment for This Project

**No other environments. Period.**

❌ **DO NOT CREATE**:
```bash
mamba create -n new_env ...
mamba create -n venv ...
python -m venv ...
```

✅ **USE EXCLUSIVELY**:
```bash
mamba activate fin-ai1
```

**Why**:
- Consistent across all team members
- Reproducible builds
- Single source of truth for dependencies
- Easier troubleshooting

**If fin-ai1 needs a package**: Update fin-ai1 directly

---

### Rule 3: Always Source conda.sh Before Mamba Commands

**Every shell session requires initialization.**

❌ **WRONG**:
```bash
mamba activate fin-ai1  # Will fail - mamba function not available
```

✅ **CORRECT**:
```bash
# Method 1: One-liner
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh && mamba activate fin-ai1

# Method 2: Two-liner
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
```

**Why**: Conda.sh defines the `mamba` shell function. Without it, the shell doesn't know what `mamba` is.

**In scripts**: Always include this at the top:
```bash
#!/bin/bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
```

---

### Rule 4: Verify Environment Activation Before Running Code

**Never assume fin-ai1 is active.**

✅ **ALWAYS CHECK**:
```bash
echo "Active environment: $CONDA_DEFAULT_ENV"
# Expected output: Active environment: fin-ai1

python --version
# Expected output: Python 3.10.17

mamba list | grep fastapi
# Expected output: fastapi 0.115.13
```

❌ **Running code without verification**:
- May use wrong Python
- May use system packages
- May fail silently
- Wastes debugging time

---

### Rule 5: Check Package Availability in conda-forge Before Using pip

**Conda-forge has 99% of packages. Use pip only as last resort.**

```bash
# Always check first
mamba search -c conda-forge package_name

# If found: Install via mamba
mamba install -c conda-forge package_name

# If NOT found: Only then consider pip
pip install package_name
```

**For this project**: All required packages are in conda-forge. Never use pip for package installation.

---

## fin-ai1 Environment Standards

### What fin-ai1 Contains

**Python Version**:
- Python 3.10.17 (FIXED - do not change)

**Core Backend Packages**:
```
fastapi==0.115.13          # Web framework
uvicorn==0.34.3            # ASGI server
pydantic==2.11.7           # Data validation
pandas==2.2.3              # Data analysis
numpy==2.1.3               # Numerical computing
yfinance==0.2.65           # Stock data
httpx==0.28.1              # HTTP client
```

**MCP Integration**:
```
mcp==1.22.0                # Model Context Protocol
technical-analysis-mcp==0.1.0  # Local MCP server
```

**Google Cloud**:
```
google-cloud-firestore==2.13.1      # Database
google-cloud-storage==2.10.0        # Object storage
google-cloud-pubsub==2.18.4         # Messaging
google-cloud-logging==3.8.0         # Logging
```

**Development Tools**:
```
pytest>=7.4.0              # Testing
black>=23.0.0              # Code formatting
ruff>=0.1.0                # Linting
mypy>=1.5.0                # Type checking
```

### Adding Packages to fin-ai1

**If you need a new package**:

1. Check if available in conda-forge:
   ```bash
   mamba search -c conda-forge package_name
   ```

2. Install via mamba:
   ```bash
   mamba activate fin-ai1
   mamba install -c conda-forge package_name
   ```

3. Verify it works:
   ```bash
   python -c "import package_name; print('✓')"
   ```

4. Update project documentation:
   - Add to MAMBA_FIN_AI1_RULES.md (this file)
   - Update environment.yml if modifying official environment

**Never install via pip** unless absolutely necessary (which it's not for this project)

---

## Mamba Command Reference

### Essential Commands for This Project

```bash
# Initialize mamba in current shell
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh

# Activate fin-ai1
mamba activate fin-ai1

# Deactivate current environment
mamba deactivate

# List all environments
mamba env list

# List packages in fin-ai1
mamba list -n fin-ai1
mamba list                 # If fin-ai1 already active

# Search for package
mamba search -c conda-forge package_name

# Install package to fin-ai1
mamba install -c conda-forge package_name
mamba install -c conda-forge -n fin-ai1 package_name

# Update all packages in fin-ai1
mamba update -n fin-ai1 --all

# Update specific package
mamba update -n fin-ai1 package_name

# Remove package
mamba remove -n fin-ai1 package_name

# Show package info
mamba info -c conda-forge package_name

# Export environment to YAML
mamba env export -n fin-ai1 > environment_backup.yml

# Create lock file (advanced)
conda-lock -f environment.yml --lockfile conda-lock.yml

# Check environment info
mamba info
```

### Never Use These Commands

```bash
# ❌ conda activate
# ❌ conda install
# ❌ pip install
# ❌ micromamba activate
# ❌ python -m venv
# ❌ virtualenv
```

---

## Shell Initialization

### In Interactive Shells

**Every time you open a terminal**:

```bash
# Add this to your shell (Terminal, iTerm, etc.)
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
```

**To make permanent** (add to ~/.zshrc or ~/.bash_profile):
```bash
# At end of ~/.zshrc
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
```

### In Bash Scripts

```bash
#!/bin/bash
# Always start with this
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Your code here
python main.py
```

### In Python Scripts

```python
# Not needed - mamba activation is shell-level
# Just ensure the script is run with activated environment:
# mamba activate fin-ai1 && python my_script.py
```

### In GitHub Actions / CI/CD

```yaml
name: CI Pipeline

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Mamba
        uses: conda-incubator/setup-miniconda@v2
        with:
          mamba-version: latest
          environment-file: environment.yml
          environment-name: fin-ai1
          auto-activate-base: false
          activate-environment: fin-ai1

      - name: Run Tests
        shell: bash -l {0}
        run: |
          source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
          mamba activate fin-ai1
          python -m pytest
```

---

## Package Management

### Adding a New Package

**Step-by-step process**:

```bash
# 1. Activate fin-ai1
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# 2. Search package on conda-forge
mamba search -c conda-forge new_package

# 3. Install it
mamba install -c conda-forge new_package

# 4. Verify it works
python -c "import new_package; print('✓ OK')"

# 5. Verify no conflicts
python main.py  # Run your code

# 6. Document the change
# - Add to this file (MAMBA_FIN_AI1_RULES.md)
# - Update environment.yml if needed
# - Create git commit
```

### Updating Packages

**To update a single package**:
```bash
mamba activate fin-ai1
mamba update package_name
```

**To update all packages**:
```bash
mamba activate fin-ai1
mamba update --all
```

⚠️ **Warning**: Only update if necessary. Test thoroughly afterward.

### Removing Packages

```bash
mamba activate fin-ai1
mamba remove package_name
```

**Note**: You almost never need to do this. Just leave unused packages - they don't affect performance.

---

## Development Workflow

### Daily Development Flow

```bash
# 1. Open terminal
# 2. Initialize mamba
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh

# 3. Activate fin-ai1
mamba activate fin-ai1

# 4. Verify environment
echo "Environment: $CONDA_DEFAULT_ENV"  # Should show: fin-ai1
python --version                         # Should show: Python 3.10.17

# 5. Navigate to project
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1

# 6. Start backend
python main.py

# 7. In another terminal, run tests
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh
```

### Running Tests

```bash
# Activate environment
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Run pytest
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python -m pytest

# Or run specific test
python -m pytest tests/test_api.py -v
```

### Running Backend

```bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python main.py  # Starts on http://localhost:8080
```

### Running Test Suite & Generating Reports

```bash
# One-command execution
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh

# Or step-by-step
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Test all endpoints
bash /Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/test_backend_api.sh

# Analyze responses
python /Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/analyze_backend_responses.py \
  backend_test_results/TIMESTAMP analysis.md

# Generate report
python /Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/generate_backend_report.py \
  backend_test_results/TIMESTAMP report.md
```

---

## CI/CD Guidelines

### GitHub Actions Setup

```yaml
name: Backend Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: macos-latest
    defaults:
      run:
        shell: bash -l {0}

    steps:
      - uses: actions/checkout@v3

      - name: Setup Mamba
        uses: conda-incubator/setup-miniconda@v2
        with:
          mamba-version: latest
          environment-file: mcp-finance1/environment.yml
          activate-environment: fin-ai1

      - name: Verify Environment
        run: |
          echo "Environment: $CONDA_DEFAULT_ENV"
          python --version
          mamba list | grep fastapi

      - name: Run Backend Tests
        run: |
          cd mcp-finance1
          python -m pytest

      - name: Run API Tests
        run: |
          # Start backend in background
          cd mcp-finance1
          python main.py &
          BACKEND_PID=$!
          sleep 5  # Wait for startup

          # Run API tests
          bash ../scripts/test_backend_api.sh

          # Kill backend
          kill $BACKEND_PID
```

### Local Pre-Commit Checks

```bash
#!/bin/bash
# hooks/pre-commit

source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# Type checking
mypy mcp-finance1/main.py

# Linting
ruff check mcp-finance1/

# Code formatting check (don't auto-format in pre-commit)
black --check mcp-finance1/

# Run tests
python -m pytest mcp-finance1/tests/

echo "✓ Pre-commit checks passed"
```

---

## Troubleshooting

### Issue 1: "mamba: command not found"

**Cause**: Haven't sourced conda.sh

**Solution**:
```bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba --version
```

**Verify**:
```bash
echo $MAMBA_EXE
# Should show: /opt/homebrew/Caskroom/miniforge/base/bin/mamba
```

---

### Issue 2: "fin-ai1: command not found" (During mamba activate)

**Cause**: fin-ai1 environment doesn't exist

**Solution**:
```bash
mamba env list | grep fin-ai1
# If not found, you need to recreate it

mamba create -n fin-ai1 -c conda-forge \
  python=3.10 \
  fastapi uvicorn pydantic \
  pandas numpy yfinance httpx \
  google-cloud-firestore google-cloud-storage google-cloud-pubsub
```

---

### Issue 3: "ModuleNotFoundError: No module named 'X'"

**Cause**: Package not installed in fin-ai1

**Solution**:
```bash
# Verify fin-ai1 is active
echo $CONDA_DEFAULT_ENV  # Should show: fin-ai1

# Install missing package
mamba install -c conda-forge missing_package

# Verify it was installed
python -c "import missing_package; print('✓')"
```

---

### Issue 4: "Requires: python >=3.11" (Incompatible package)

**Cause**: fin-ai1 is Python 3.10, but package requires 3.11+

**Solution**:
- Find alternative package compatible with Python 3.10
- Or request approval to upgrade fin-ai1 to Python 3.11
- Contact: [Project Lead]

---

### Issue 5: "CondaError: HTTP 000 CONNECTION FAILED"

**Cause**: No internet connection or conda-forge is down

**Solution**:
```bash
# Check internet
ping google.com

# Try again later, or use cached packages:
mamba install --offline package_name
```

---

### Issue 6: Slow Dependency Resolution

**Cause**: Using conda instead of mamba (mamba is faster)

**Solution**:
```bash
# Make sure you're using mamba
which mamba
# Should show: /opt/homebrew/Caskroom/miniforge/base/bin/mamba

# Verify not using conda
conda --version  # OK to have conda installed
mamba --version  # Must use mamba
```

---

## Quick Reference Cheat Sheet

```bash
# SESSION INITIALIZATION
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh
mamba activate fin-ai1

# VERIFICATION
echo $CONDA_DEFAULT_ENV          # Should show: fin-ai1
python --version                 # Should show: Python 3.10.17
mamba list | head -10

# PACKAGE MANAGEMENT
mamba search -c conda-forge pkg
mamba install -c conda-forge pkg
mamba update pkg
mamba remove pkg

# ENVIRONMENT INFO
mamba info
mamba env list
mamba list
mamba list -c conda-forge

# DEVELOPMENT
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/mcp-finance1
python main.py                   # Start backend

# TESTING
/Users/adamaslan/code/gcp\ app\ w\ mcp/scripts/quick_start.sh
```

---

## Project-Specific Standards

### For MCP Finance Developers

✅ **ALWAYS**:
1. Source conda.sh before using mamba
2. Use fin-ai1 environment exclusively
3. Check environment with: `echo $CONDA_DEFAULT_ENV`
4. Install packages via: `mamba install -c conda-forge pkg`
5. Test after installing: `python -c "import pkg"`
6. Document changes in this file

❌ **NEVER**:
1. Use `conda` directly
2. Use `pip install` for new packages
3. Create new environments
4. Use `micromamba`
5. Use `python -m venv`
6. Switch to different Python version

### File Locations

- **Runbook**: `/Users/adamaslan/code/gcp app w mcp/BACKEND_EXECUTION_RUNBOOK.md`
- **This File**: `/Users/adamaslan/code/gcp app w mcp/MAMBA_FIN_AI1_RULES.md`
- **Backend**: `/Users/adamaslan/code/gcp app w mcp/mcp-finance1/main.py`
- **Scripts**: `/Users/adamaslan/code/gcp app w mcp/scripts/`
- **Tests**: `/Users/adamaslan/code/gcp app w mcp/backend_test_results/`

---

## Contact & Support

- **Project Lead**: [Name]
- **Mamba Documentation**: https://mamba.readthedocs.io/
- **Conda-forge**: https://conda-forge.org/
- **Issue Tracker**: GitHub Issues

---

**Last Updated**: January 21, 2026
**Version**: 1.0
**Status**: Official Project Standard

**All developers must follow these rules strictly.**
