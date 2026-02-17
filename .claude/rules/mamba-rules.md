# Mamba Package Manager Rules for MCP Finance

Claude should follow these conventions when working with mamba environments in this project.

## Project-Specific Environment

**Primary environment for this project: `fin-ai1`**

### Activation Command

Always activate the fin-ai1 environment before running Python scripts:

```bash
eval "$(mamba shell hook --shell zsh)" && mamba activate fin-ai1
```

### Correct Activation (VERIFIED):

```bash
source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh && source /opt/homebrew/Caskroom/miniforge/base/etc/profile.d/mamba.sh && mamba activate fin-ai1
```

Or check the user's shell config:
```bash
# Find mamba installation
mamba info --base
```

## Mamba-First Philosophy

- **Mamba is the primary package manager** - 2-5x faster than conda
- Use `conda-forge` channel for all packages
- Only use pip for packages unavailable in conda-forge (rare)

## Key Commands

```bash
# Activate environment
mamba activate fin-ai1

# Install packages
mamba install -c conda-forge package_name

# List installed packages
mamba list

# Search for packages
mamba search package_name

# Update packages
mamba update package_name
```

## Running Python Scripts

When running Python scripts in this project, always ensure fin-ai1 is activated first:

```bash
eval "$(mamba shell hook --shell zsh)" && mamba activate fin-ai1 && python script.py
```

## Exception: conda config

The **only exception** is `conda config` - this command is not provided by mamba.
For configuration tasks, use: `conda config --add channels conda-forge`
