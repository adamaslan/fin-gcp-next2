---
name: health-check
description: Check health of all MCP Finance system components (frontend, backend, database, external services)
---

Perform a comprehensive health check of the MCP Finance system.

## System Health Check

Run these checks in parallel to verify all components are operational:

### 1. Frontend Health
```bash
cd nextjs-mcp-finance

# Check if dev server is running
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend server: Running" || echo "❌ Frontend server: Not running (run: npm run dev)"

# Check build works
npm run build 2>&1 | tail -5 && echo "✅ Frontend build: OK" || echo "❌ Frontend build: Failed"
```

### 2. Database Health
```bash
# Check PostgreSQL is running
pg_isready && echo "✅ PostgreSQL: Running" || echo "❌ PostgreSQL: Not running"

# Test database connection
psql $DATABASE_URL -c "SELECT NOW();" > /dev/null 2>&1 && echo "✅ Database connection: OK" || echo "❌ Database connection: Failed"

# Check table count
TABLE_COUNT=$(psql $DATABASE_URL -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
echo "✅ Database tables: $TABLE_COUNT tables found"
```

### 3. MCP Backend Server Health
```bash
cd ../mcp-finance1/cloud-run

# Check if MCP server is running
curl -s http://localhost:8000/health > /dev/null && echo "✅ MCP Server: Running" || echo "❌ MCP Server: Not running (activate mamba env & run: python3 main.py)"

# Check Mamba/Micromamba
mamba --version > /dev/null 2>&1 && echo "✅ Mamba: Installed" || (micromamba --version > /dev/null 2>&1 && echo "✅ Micromamba: Installed" || echo "❌ Mamba/Micromamba: Not installed")

# Check mamba environment exists
mamba env list | grep fin-ai1 > /dev/null 2>&1 && echo "✅ MCP Backend Environment: Exists" || echo "❌ MCP Backend Environment: Not created"

# Check Python (within mamba environment)
python3 --version && echo "✅ Python: Installed" || echo "❌ Python: Not found"
```

### 4. External Services Health

**Clerk Authentication:**
```bash
cd nextjs-mcp-finance
node -e "const key = process.env.CLERK_SECRET_KEY; console.log(key ? '✅ Clerk: API key configured' : '❌ Clerk: API key missing');"
```

**Stripe Payments:**
```bash
node -e "const key = process.env.STRIPE_SECRET_KEY; console.log(key ? '✅ Stripe: API key configured' : '❌ Stripe: API key missing');"
```

### 5. Environment Variables
```bash
# Check critical env vars
node -e "
const required = ['DATABASE_URL', 'CLERK_SECRET_KEY', 'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', 'STRIPE_SECRET_KEY'];
required.forEach(key => {
  console.log(process.env[key] ? \`✅ \${key}: Set\` : \`❌ \${key}: Missing\`);
});
"
```

### 6. Dependencies
```bash
# Check node_modules
[ -d "node_modules" ] && echo "✅ Dependencies: Installed" || echo "❌ Dependencies: Not installed (run: npm install)"

# Check if packages are up to date
npm outdated | head -10 || echo "✅ Packages: Up to date"
```

### 7. Disk Space
```bash
df -h . | tail -1 | awk '{print "💾 Disk space: " $5 " used, " $4 " available"}'
```

## Health Summary Dashboard

Generate a formatted summary:

```bash
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║      MCP FINANCE HEALTH CHECK REPORT      ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Date: $(date)"
echo ""
echo "COMPONENT STATUS:"
echo "─────────────────────────────────────────────"
```

Run all checks above, then:

```bash
echo "─────────────────────────────────────────────"
echo ""
echo "RECOMMENDATIONS:"
echo ""
```

## Automated Fix Suggestions

Based on check results, suggest fixes:

**If Frontend Not Running:**
```bash
cd nextjs-mcp-finance && npm run dev
```

**If Database Not Connected:**
```bash
# Check .env.local exists and has DATABASE_URL
cat .env.local | grep DATABASE_URL || echo "Add DATABASE_URL to .env.local"
```

**If MCP Server Not Running:**
```bash
cd mcp-finance1/cloud-run
mamba activate fin-ai1
python3 main.py
```

**If Dependencies Missing:**
```bash
cd nextjs-mcp-finance && npm install
```

## Quick Health Check (Fast Mode)

For a rapid status check during development:

```bash
# One-liner health check
echo "Frontend:$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)" && \
echo "Database:$(pg_isready > /dev/null && echo OK || echo FAIL)" && \
echo "MCP:$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)"
```

## Health Check Exit Codes

Use exit codes for CI/CD:
- 0 = All systems healthy
- 1 = Critical failures (database, services down)
- 2 = Warnings (dependencies outdated, low disk space)

## When to Run Health Checks

- ✅ Before starting development
- ✅ After pulling code changes
- ✅ Before deploying
- ✅ After system updates
- ✅ When debugging issues
- ✅ As part of CI/CD pipeline

## Integration with Other Commands

Health check should pass before:
- Running `/test-all`
- Executing `/db-migrate`
- Deploying with `/deploy`
- Seeding with `/db-seed`

---

**Pro Tip**: Add this to your daily workflow: `/health-check && npm run dev`
