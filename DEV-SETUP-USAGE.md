# /dev-setup Skill - Usage Guide

## Overview

The `/dev-setup` skill automates the complete development environment setup for the MCP Finance project.

## Quick Start

### Using Claude Code
```
/dev-setup
```

### Using the Script Directly
```bash
bash scripts/dev-setup.sh
```

## What It Does

The skill performs these steps automatically:

1. ✅ **Checks Prerequisites**
   - Verifies Node.js 18+ is installed
   - Checks for Python 3
   - Verifies PostgreSQL installation
   - Confirms Git is available

2. ✅ **Installs Dependencies**
   - Frontend: Next.js, React, Clerk, Stripe, Drizzle ORM
   - Backend: Python packages for MCP server
   - Testing: Playwright browsers for E2E tests

3. ✅ **Configures Environment**
   - Creates `.env.local` from `.env.example` (frontend)
   - Creates `.env` from `.env.example` (backend)
   - Lists required environment variables

4. ✅ **Sets Up Database**
   - Tests database connection
   - Runs database migrations
   - Prepares database schema

5. ✅ **Verifies Setup**
   - Confirms all components are ready
   - Displays next steps

## Usage Options

### Full Setup (Recommended for First Time)
```bash
/dev-setup
```
Installs everything and sets up the complete environment.

**Estimated Time**: 3-5 minutes

### Skip Dependency Installation
```bash
/dev-setup --skip-install
```
Only sets up environment files and runs verification.

**Use When**: Dependencies are already installed.

### Skip Database Setup
```bash
/dev-setup --skip-db
```
Installs dependencies but skips database operations.

**Use When**: Working on frontend only or database isn't available.

### Minimal Setup
```bash
/dev-setup --skip-install --skip-db
```
Only verifies prerequisites and environment files.

**Use When**: Doing a quick verification.

### Verbose Mode
```bash
bash scripts/dev-setup.sh --verbose
```
Shows detailed output from all commands.

**Use When**: Debugging setup issues.

## What You Need Before Running

### Required Tools
- **Node.js 18+** - [Download](https://nodejs.org/)
- **npm** - Comes with Node.js
- **Git** - For version control

### Recommended Tools
- **Python 3.9+** - For MCP backend server
- **PostgreSQL 14+** - For database
- **Homebrew** (macOS) or package manager

### Install Prerequisites (macOS)
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node@20

# Install Python
brew install python@3.11

# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15
```

### Install Prerequisites (Ubuntu/Debian)
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt-get install -y python3.11 python3-pip

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Environment Variables

After running `/dev-setup`, you need to configure these variables:

### Frontend (.env.local)
```bash
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/mcp_finance"

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."
CLERK_WEBHOOK_SECRET="whsec_..."

# Stripe Payments
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# App URL
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### Backend (.env)
```bash
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/mcp_finance"

# MCP Server
MCP_SERVER_PORT=8000

# API Keys (if needed)
ALPHA_VANTAGE_API_KEY="your_key"
```

## After Setup - Next Steps

### 1. Start Development Servers

**Frontend:**
```bash
cd nextjs-mcp-finance
npm run dev
```
Access at: http://localhost:3000

**Backend:**
```bash
cd mcp-finance1/cloud-run
python3 main.py
```
Access at: http://localhost:8000

### 2. Verify Everything Works

Use other skills to verify:
```bash
/health-check    # Check system health
/mcp-check       # Verify MCP server
/test-all        # Run all tests
```

### 3. Explore the Application

- 📱 **Frontend**: http://localhost:3000
- 🔧 **API**: http://localhost:8000
- 📊 **Database**: Connect via PostgreSQL client

## Troubleshooting

### Node.js Not Found
```bash
# Install Node.js
brew install node@20  # macOS
# or
sudo apt-get install nodejs  # Ubuntu
```

### Python Not Found
```bash
# Install Python
brew install python@3.11  # macOS
# or
sudo apt-get install python3  # Ubuntu
```

### PostgreSQL Not Running
```bash
# macOS
brew services start postgresql

# Ubuntu
sudo systemctl start postgresql

# Check status
pg_isready
```

### Dependencies Won't Install
```bash
# Clear npm cache
npm cache clean --force

# Clear pip cache
pip3 cache purge

# Run with verbose output
bash scripts/dev-setup.sh --verbose
```

### Database Connection Failed
1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL in `.env.local`
3. Test connection: `psql $DATABASE_URL`
4. Create database if needed:
   ```bash
   createdb mcp_finance
   ```

### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix npm permissions
sudo chown -R $USER:$GROUP ~/.npm
sudo chown -R $USER:$GROUP ~/.config
```

## Common Scenarios

### Scenario 1: First Time Setup
```bash
# Full setup
/dev-setup

# Configure environment variables
code nextjs-mcp-finance/.env.local

# Start servers
cd nextjs-mcp-finance && npm run dev
```

### Scenario 2: After Pulling Updates
```bash
# Update dependencies only
/dev-setup

# Run migrations
/db-migrate
```

### Scenario 3: Quick Environment Check
```bash
# Verify setup without reinstalling
/dev-setup --skip-install --skip-db
```

### Scenario 4: Database Reset
```bash
# Setup everything including fresh database
/dev-setup

# Seed with test data
/db-seed
```

## Performance

### Expected Times

| Operation | Duration |
|-----------|----------|
| Full setup (first time) | 3-5 minutes |
| With dependencies cached | 1-2 minutes |
| Skip install | 10-30 seconds |
| Skip everything | < 5 seconds |

### Speed It Up

1. **Cache npm packages**: Dependencies are cached after first install
2. **Use --skip-install**: When deps haven't changed
3. **Use --skip-db**: When working on frontend only
4. **Run in background**: Use `&` to run async

## Integration with Other Skills

The `/dev-setup` skill works well with:

```bash
# Complete onboarding workflow
/dev-setup
/db-seed           # Add test data
/test-all          # Verify everything works
/health-check      # Final verification

# Development workflow
/dev-setup --skip-install
/mcp-check
npm run dev
```

## Logs and Debugging

### View Setup Logs
```bash
# Run with verbose output
bash scripts/dev-setup.sh --verbose

# Check Claude logs
tail -f .claude/logs/skills.log
```

### Common Log Messages

✓ **Success**: Green checkmarks indicate completed steps
⚠ **Warning**: Yellow warnings are non-critical issues
✗ **Error**: Red X marks indicate failures

## Getting Help

1. **Check Prerequisites**: Ensure all tools are installed
2. **Review Logs**: Run with `--verbose` flag
3. **Check Documentation**: Read `GUIDE-ENHANCED.md`
4. **Test Individual Steps**: Break down the process
5. **Ask Claude**: Describe the specific error

## Advanced Usage

### Custom Setup Script

Create your own variation:
```bash
#!/bin/bash
# my-setup.sh

# Run base setup
bash scripts/dev-setup.sh --skip-db

# Custom steps
npm install -g some-global-tool
code .
```

### Environment-Specific Setup

```bash
# Development
/dev-setup

# Staging (different config)
/dev-setup --skip-db
# Then manually set staging DATABASE_URL

# Production
# Don't use /dev-setup in production!
# Use /build-deploy instead
```

## Success Indicators

You'll know setup succeeded when you see:

✅ All prerequisites found
✅ Dependencies installed
✅ Environment files created
✅ Database connected
✅ Migrations completed
✅ "Setup Complete!" message

## Next Skills to Try

After `/dev-setup`, try these:

- `/db-seed` - Add test data
- `/test-all` - Run complete test suite
- `/health-check` - Verify system health
- `/mcp-check` - Check MCP server status
- `/clerk-signup` - Test authentication flow

---

## Summary

The `/dev-setup` skill is your **one-command solution** to get the MCP Finance development environment ready. It handles all the tedious setup steps automatically, letting you focus on building features.

**Quick Commands:**
```bash
# Full setup
/dev-setup

# Quick check
/dev-setup --skip-install --skip-db

# With script
bash scripts/dev-setup.sh --verbose
```

**Questions?** Check `claude-skills-how-to.md` or ask Claude for help!

---

**Version**: 1.0.0
**Last Updated**: January 2024
**Skill Category**: Development Environment
**Estimated Time**: 3-5 minutes
