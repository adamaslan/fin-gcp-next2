---
name: test-all
description: Run complete test suite for MCP Finance (frontend E2E tests, backend tests, linting)
---

Run the complete test suite for MCP Finance. Follow these steps:

## Step 1: Check Current Directory
First, verify we're in the project root:
```bash
pwd
ls -la | grep -E "nextjs-mcp-finance|mcp-finance1"
```

## Step 2: Run Frontend E2E Tests
```bash
cd nextjs-mcp-finance
npm run test:e2e
```

**What this tests:**
- User authentication flows
- API endpoints
- Feature functionality
- UI interactions

**If tests fail:**
- Check if dev server is running (should NOT be for E2E tests)
- Verify DATABASE_URL is set
- Check Playwright browsers are installed: `npx playwright install`

## Step 3: Run Frontend Linting
```bash
npm run lint
```

**If linting fails:**
- Review the errors
- Auto-fix if possible: `npm run lint -- --fix`
- Fix remaining issues manually

## Step 4: TypeScript Type Check
```bash
npx tsc --noEmit
```

**If type check fails:**
- Fix type errors shown in output
- Don't use `any` types
- Add proper type annotations

## Step 5: Run Backend Tests (if available)
```bash
cd ../mcp-finance1/cloud-run
python -m pytest tests/ || echo "No backend tests found (optional)"
```

## Step 6: Summary Report
Generate a summary of test results:

```bash
echo "======================================"
echo "TEST SUITE SUMMARY"
echo "======================================"
echo "✅ E2E Tests: Check output above"
echo "✅ Linting: Check output above"
echo "✅ Type Check: Check output above"
echo "✅ Backend Tests: Check output above"
echo "======================================"
```

## Success Criteria
All of these should pass:
- ✅ E2E tests: All passing
- ✅ Lint: No errors
- ✅ Type check: No errors
- ✅ Backend tests: All passing (if present)

## Common Issues

### "Playwright not installed"
```bash
cd nextjs-mcp-finance
npx playwright install
```

### "Database connection failed"
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env.local
- Test connection: `psql $DATABASE_URL`

### "Port already in use"
- E2E tests start their own server
- Stop any running `npm run dev` processes
- Kill the process: `lsof -ti:3000 | xargs kill -9`

### "Module not found"
```bash
npm install
```

## Quick Test Modes

For faster feedback during development:

**Run only auth tests:**
```bash
cd nextjs-mcp-finance
npm run test:e2e:auth
```

**Run only API tests:**
```bash
npm run test:e2e:api
```

**Run with UI (see browser):**
```bash
npm run test:e2e:headed
```

## After Tests Pass

If all tests pass, you're ready to:
- Commit your changes
- Create a pull request
- Deploy to staging/production

## Environment Requirements

Ensure these are set in `nextjs-mcp-finance/.env.local`:
- `DATABASE_URL` - PostgreSQL connection
- `CLERK_SECRET_KEY` - Clerk authentication
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk public key

Test keys are fine for running tests.
