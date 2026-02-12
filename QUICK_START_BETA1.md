# Quick Start Guide - Running beta1 Scan

**Environment**: fin-ai1 (Python 3.10.17)
**Script Location**: `/Users/adamaslan/code/gcp app w mcp/mcp-finance1/cloud-run/run_beta1_scan.py`
**Status**: ✅ Environment configured and working

---

## Method 1: Interactive Terminal (Recommended)

Open a new terminal window and run:

```bash
# Activate the environment
mamba activate fin-ai1

# Navigate to the script directory
cd "/Users/adamaslan/code/gcp app w mcp/mcp-finance1/cloud-run"

# Run the script
python run_beta1_scan.py
```

**Note**: You only need to activate the environment once per terminal session.

---

## Method 2: One-Line Command

```bash
zsh -i -c 'mamba activate fin-ai1 && cd "/Users/adamaslan/code/gcp app w mcp/mcp-finance1/cloud-run" && python run_beta1_scan.py'
```

This activates the environment and runs the script in a single command.

---

## Method 3: Direct Python Path (No Activation)

```bash
cd "/Users/adamaslan/code/gcp app w mcp/mcp-finance1/cloud-run"
/opt/homebrew/Caskroom/miniforge/base/envs/fin-ai1/bin/python run_beta1_scan.py
```

This uses the environment's Python directly without activation. Useful for automated scripts.

---

## Available Environments

You have these conda/mamba environments available:

- `base` - Default miniforge environment
- `fin-ai1` - Financial AI environment (Python 3.10.17) ⭐ **Use this for beta1**
- `mcp-finance-backend` - MCP Finance backend
- `ai-text-opt` - AI text optimization
- `browz1` - Browser automation
- `lightrag-viz` - LightRAG visualization

To list all environments:
```bash
mamba env list
```

---

## Verification

To verify everything is working:

```bash
# Check mamba installation
which mamba

# Activate environment and check Python
mamba activate fin-ai1
which python
python --version
```

Expected output:
```
/opt/homebrew/Caskroom/miniforge/base/envs/fin-ai1/bin/python
Python 3.10.17
```

---

## Troubleshooting

### "command not found: mamba"
- Open a **new terminal window** (not just a new tab)
- The terminal needs to load `.zshrc` on startup

### Script not found error
- Make sure you're in the correct directory:
  ```bash
  cd "/Users/adamaslan/code/gcp app w mcp/mcp-finance1/cloud-run"
  ls -la run_beta1_scan.py
  ```

### Environment activation doesn't work
- Use Method 3 (direct Python path) which doesn't require activation
- Or use `zsh -i -c` to run in an interactive shell context

---

## Next Steps

For detailed information about the shell configuration, see:
- `/Users/adamaslan/code/gcp app w mcp/SHELL_CONFIG_REPORT.md` - Full configuration analysis
- `/Users/adamaslan/code/gcp app w mcp/MAMBA_ACTIVATION_DIAGNOSTIC.md` - Original diagnostic report

---

**Last Updated**: 2026-01-20
**Configuration Status**: ✅ Working correctly
