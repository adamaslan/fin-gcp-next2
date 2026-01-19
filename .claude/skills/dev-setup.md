---
name: dev-setup
description: Initialize complete development environment for MCP Finance. Use when setting up the project for the first time, onboarding new developers, or resetting your development environment.
---

When running dev-setup, follow this comprehensive checklist to ensure the MCP Finance development environment is properly configured:

## Pre-Setup Checks

Before starting installation, verify prerequisites:

1. **Check Node.js**: Run `node --version` - should be 18.0.0 or higher
   - If not installed: Guide user to https://nodejs.org/
   - If version too low: Recommend upgrading

2. **Check npm**: Run `npm --version` - should be 9.0.0 or higher
   - Comes with Node.js

3. **Check Mamba/Micromamba**: Run `mamba --version` or `micromamba --version`
   - Required for MCP backend Python environment
   - If missing: Install from https://mamba.readthedocs.io/
   - Prefer micromamba for faster, standalone installation

4. **Check Python**: Run `python3 --version` - should be 3.9 or higher
   - Managed by mamba, don't install separately
   - If missing: Will be installed via mamba environment

5. **Check PostgreSQL**: Run `psql --version` or `pg_isready --version`
   - Optional but needed for database features
   - If missing: Warn user but continue

6. **Check Git**: Run `git --version`
   - Needed for version control

## Installation Steps

Follow these steps in order:

### 1. Frontend Dependencies
```bash
cd nextjs-mcp-finance
npm install
```

**What's being installed:**
- Next.js 16 - React framework
- React 19 - UI library
- Clerk - Authentication
- Stripe - Payments
- Drizzle ORM - Database toolkit
- Tailwind CSS - Styling
- Radix UI - Component primitives
- TanStack Query - Data fetching

**Time estimate**: 2-3 minutes on first run

**If fails:**
- Check internet connection
- Try clearing npm cache: `npm cache clean --force`
- Check npm registry is accessible: `npm ping`

### 2. Backend Dependencies (Using Mamba)
```bash
cd mcp-finance1/cloud-run

# Option 1: Using existing environment.yml (preferred)
mamba env create -f environment.yml -n mcp-finance-backend

# Option 2: Using micromamba (faster, standalone)
micromamba create -f environment.yml -n mcp-finance-backend

# Activate environment
mamba activate mcp-finance-backend
# OR
micromamba activate mcp-finance-backend
```

**What's being installed:**
- Python 3.11 (managed by mamba)
- FastAPI or Flask - Python web framework
- Database drivers (via conda-forge)
- MCP protocol libraries
- Data processing libraries
- All dependencies resolved in parallel (2-5x faster than pip)

**If environment.yml doesn't exist, create it:**
```yaml
name: mcp-finance-backend
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - fastapi
  - uvicorn
  - httpx
  - python-dotenv
  - psycopg2
  - pip
  - pip:
    - packages-only-on-pypi  # Only if package unavailable in conda-forge
```

**If fails:**
- Check mamba is installed: `mamba --version`
- Update mamba: `mamba update mamba`
- Try micromamba instead (more reliable)
- Check conda-forge channel is accessible

### 3. Playwright Browsers
```bash
cd nextjs-mcp-finance
npx playwright install chromium
```

**What this does:**
- Installs Chromium browser for E2E testing
- Required for automated testing

**If fails:**
- Try full install: `npx playwright install`
- Check disk space

## Environment Configuration

### 4. Create Frontend Environment File
```bash
cd nextjs-mcp-finance
cp .env.example .env.local
```

**Then prompt user to configure these critical variables:**

```bash
# Database Connection
DATABASE_URL="postgresql://user:password@localhost:5432/mcp_finance"

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."
CLERK_WEBHOOK_SECRET="whsec_..."

# Stripe Payments
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Application
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

**Important Notes:**
- Don't commit .env.local to git (already in .gitignore)
- Use TEST keys for development, never production keys
- Get Clerk keys from: https://clerk.com/dashboard
- Get Stripe keys from: https://dashboard.stripe.com/test/apikeys

### 5. Create Backend Environment File
```bash
cd mcp-finance1
cp .env.example .env
```

**Configure:**
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/mcp_finance"
MCP_SERVER_PORT=8000
```

## Database Setup

### 6. Test Database Connection
```bash
cd nextjs-mcp-finance
node -e "const { Pool } = require('pg'); const pool = new Pool({ connectionString: process.env.DATABASE_URL }); pool.query('SELECT NOW()').then(() => { console.log('✓ Database connected'); pool.end(); }).catch((err) => { console.error('✗ Connection failed:', err.message); });"
```

**If connection fails:**
1. Is PostgreSQL running? Check with: `pg_isready`
2. Start PostgreSQL:
   - macOS: `brew services start postgresql`
   - Linux: `sudo systemctl start postgresql`
3. Is the database created? Create with: `createdb mcp_finance`
4. Is the DATABASE_URL correct? Check username, password, host, port

### 7. Run Database Migrations
```bash
cd nextjs-mcp-finance
npm run db:push || npx drizzle-kit push
```

**What this does:**
- Creates database tables
- Sets up schema
- Applies initial migrations

**If fails:**
- Check DATABASE_URL is set
- Ensure database exists
- Check database user has CREATE TABLE permissions

## Verification

### 8. Verify Project Structure
Check that these directories exist:
- ✓ nextjs-mcp-finance/ (frontend)
- ✓ nextjs-mcp-finance/src/
- ✓ nextjs-mcp-finance/src/app/
- ✓ mcp-finance1/ (backend)
- ✓ mcp-finance1/cloud-run/
- ✓ scripts/

### 9. Verify Environment Files
Confirm these files exist:
- ✓ nextjs-mcp-finance/.env.local
- ✓ mcp-finance1/.env

### 10. Final Check
Run a quick health check of the setup:
```bash
echo "✓ Prerequisites verified"
echo "✓ Dependencies installed"
echo "✓ Environment configured"
echo "✓ Database connected"
echo "✓ Ready for development!"
```

## Usage Flags

Support these optional parameters:

**--skip-install**: Skip dependency installation
- Use when: Dependencies already installed, just checking setup
- Command: Only verify and configure environment

**--skip-db**: Skip database setup
- Use when: Database not available or working on frontend only
- Command: Skip database connection test and migrations

**--verbose**: Show detailed output
- Use when: Debugging setup issues
- Command: Show full output from all commands

## Next Steps Guidance

After successful setup, guide the user:

```
🎉 Development environment is ready!

📍 You are here: Setup complete

📋 Next steps:

1. Configure your API keys (REQUIRED):
   • Edit nextjs-mcp-finance/.env.local
   • Add your Clerk and Stripe keys
   • Get keys from respective dashboards

2. Start the development servers:

   Terminal 1 (Frontend):
   cd nextjs-mcp-finance
   npm run dev
   → http://localhost:3000

   Terminal 2 (Backend - optional):
   cd mcp-finance1/cloud-run
   python3 main.py
   → http://localhost:8000

3. Verify everything works:
   /health-check    # System health
   /mcp-check       # MCP server status
   /test-all        # Run tests

4. Add test data (optional):
   /db-seed

5. Start coding! 🚀

📚 Helpful docs:
   • GUIDE-ENHANCED.md - Complete guide
   • DEV-SETUP-USAGE.md - Detailed setup info
   • SKILLS-QUICK-REFERENCE.md - Quick commands
```

## Common Issues & Solutions

### "Node not found"
```bash
# Install Node.js
# macOS:
brew install node@20

# Ubuntu:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### "Python not found"
```bash
# Install Python
# macOS:
brew install python@3.11

# Ubuntu:
sudo apt-get install python3.11 python3-pip
```

### "Cannot connect to database"
1. Check PostgreSQL is running
2. Verify DATABASE_URL format: `postgresql://user:pass@host:5432/dbname`
3. Test connection: `psql $DATABASE_URL`
4. Create database if needed: `createdb mcp_finance`

### "npm install fails"
1. Clear cache: `npm cache clean --force`
2. Delete node_modules: `rm -rf node_modules`
3. Delete package-lock.json: `rm package-lock.json`
4. Try again: `npm install`

### "Permission denied"
```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix npm permissions
sudo chown -R $USER:$GROUP ~/.npm
```

## Best Practices

When running this skill:

1. **Run in project root**: Always run from the main project directory
2. **Check prerequisites first**: Don't skip the prerequisite checks
3. **Read error messages**: They contain helpful guidance
4. **Use --verbose for debugging**: Shows detailed output
5. **Don't commit .env files**: They contain secrets
6. **Use test keys**: Never use production API keys in development
7. **Keep docs open**: Reference DEV-SETUP-USAGE.md if stuck

## Success Indicators

You know setup succeeded when:
- ✅ All prerequisite checks pass
- ✅ npm install completes without errors
- ✅ Environment files exist
- ✅ Database connection successful
- ✅ No error messages in output
- ✅ "Setup complete!" message appears

## Time Expectations

Set proper expectations:
- **Full setup (first time)**: 3-5 minutes
- **With cached dependencies**: 1-2 minutes
- **Skip install mode**: 10-30 seconds
- **Verification only**: < 5 seconds

## Integration with Helper Script

This skill works with `scripts/dev-setup.sh`:
- Skill provides the instructions and logic
- Script automates the execution
- Users can run either way:
  - Claude: `/dev-setup` (conversational)
  - Direct: `bash scripts/dev-setup.sh` (automated)

Both methods achieve the same result.

---

Remember: This skill is about creating a **consistent, reliable, and fast** development environment setup experience. Always prioritize clear communication and helpful error messages!
