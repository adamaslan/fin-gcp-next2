# Phase 5: Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Start the Frontend (Terminal 1)

```bash
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/nextjs-mcp-finance

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev
```

Expected output:
```
  ▲ Next.js 16.0.0
  - Local:        http://localhost:3000
  - Environments: .env.local

Ready in 2.3s
```

### Step 2: Open Browser

Visit: **http://localhost:3000**

You should see the MCP Finance landing page with:
- ✅ "MCP Finance" heading
- ✅ "Latest Analysis" section
- ✅ 9 tool cards (may be empty if cache is fresh)

---

## Quick Manual Testing (5 Tools)

### Test 1: Free Tier Sign-up

```
1. Click "Sign Up" button
2. Enter email: test-free@example.com
3. Set password: TestPass123!
4. Click "Sign up"
5. Should redirect to /dashboard
6. Default tier should be "Free"
```

**Expected**: Sees "Free Tier" badge, upgrade CTA visible

---

### Test 2: Access MCP Control Center

```
1. From dashboard, click "MCP Control Center"
2. Should land on /mcp-control page
3. Page layout: 3 columns
   - Left: Tool selector
   - Middle: Parameter form
   - Right: Results (empty)
```

**Expected**: 3-column layout loads correctly

---

### Test 3: Execute analyze_security Tool

```
1. In Tool Selector, select "analyze_security"
2. In Parameter Form:
   - Symbol: AAPL
   - Period: 1mo
3. Click "Execute" button
4. Wait for results (2-5s)
5. Results should show:
   - Symbol: AAPL
   - Bullish/Bearish counts
   - Top 3 signals (free tier limit)
```

**Expected**: Results display with data

---

### Test 4: Pro Tier Upgrade (Stripe)

```
1. Go to /dashboard
2. Click "Upgrade to Pro" button
3. Stripe checkout opens
4. Fill checkout form:
   - Email: test-pro@example.com
   - Card: 4242 4242 4242 4242
   - Expiry: 12/25
   - CVC: 123
5. Click "Subscribe"
6. Wait for redirect
7. Tier should update to "Pro"
```

**Expected**:
- Subscription created (Stripe test mode)
- Redirect to success page
- Tier shows "Pro"

---

### Test 5: AI Analysis as Pro User

```
1. Go to /mcp-control
2. Select a tool (e.g., "analyze_security")
3. Fill symbol: AAPL
4. Look for "AI Analysis" toggle
5. Toggle it ON (should be visible for Pro users)
6. Click "Execute"
7. Results should include:
   - Regular analysis
   - "Gemini AI Insights" card with:
     - Market Bias
     - Action Items
     - Risk Factors
     - Confidence score
```

**Expected**: AI insights card appears with formatted data

---

## Troubleshooting

### "Port 3000 already in use"

```bash
# Find process using port 3000
lsof -i :3000

# Kill it
kill -9 <PID>

# Or use different port
npm run dev -- -p 3001
```

### Frontend crashes

```bash
# Clear cache and dependencies
rm -rf .next node_modules
npm install
npm run dev
```

### Sign-up/auth not working

Check `.env.local` has:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

Get from: https://dashboard.clerk.com/apps

### Payment not working

Stripe test mode requires test credentials:
- Go to https://dashboard.stripe.com
- Switch to "Test mode" (toggle in top-right)
- Use test card: `4242 4242 4242 4242`

---

## Browser DevTools Checks

### Check 1: Console Errors

```
F12 → Console tab
Should show:
- ✅ No red error messages
- ✅ Only yellow warnings (acceptable)
- ✅ Blue info logs (expected)
```

### Check 2: Network Performance

```
F12 → Network tab
Load /mcp-control
Look for:
- ✅ Page load < 3 seconds
- ✅ No failed requests (red X)
- ✅ All images loaded
- ✅ API calls returning 200
```

### Check 3: Responsive Design

```
F12 → Device Emulation (Ctrl+Shift+M)
Test widths:
- 375px (mobile)
- 768px (tablet)
- 1024px (desktop)

Check:
- ✅ No horizontal scrollbar
- ✅ All buttons tappable
- ✅ Text readable
```

---

## Testing Checklist Summary

Quick boxes to check off:

### Landing Page (Public)
- [ ] Page loads at http://localhost:3000
- [ ] Shows "Latest Analysis" section
- [ ] Responsive on mobile/tablet/desktop
- [ ] No console errors

### Free Tier
- [ ] Can sign up
- [ ] Can access /mcp-control
- [ ] Can select tools
- [ ] Can fill parameters
- [ ] Can execute tools
- [ ] Results show with tier limits (3 signals, etc.)
- [ ] No "AI Analysis" toggle visible
- [ ] Cannot save presets

### Pro Tier
- [ ] Can upgrade to Pro (Stripe)
- [ ] "AI Analysis" toggle visible
- [ ] Can execute with AI enabled
- [ ] AIInsights card appears
- [ ] Can save presets
- [ ] Can load presets
- [ ] Can delete presets

### Performance
- [ ] Landing page < 2s load
- [ ] MCP Control page < 3s load
- [ ] Tool execution 2-5s
- [ ] No memory leaks (DevTools)
- [ ] Smooth interactions

### Error Handling
- [ ] Invalid symbol shows error
- [ ] Empty required fields blocked
- [ ] Network errors handled gracefully
- [ ] API failures show helpful messages

---

## What to Test First

**Order of priority:**
1. ✅ **Landing page loads** (most basic)
2. ✅ **Free user sign-up works**
3. ✅ **Can execute one tool** (analyze_security)
4. ✅ **Results display correctly**
5. ✅ **Pro upgrade works** (Stripe)
6. ✅ **AI toggle appears for Pro**
7. ✅ **AI results show insights**
8. ✅ **Presets save/load** (Pro feature)
9. ✅ **All 9 tools executable**
10. ✅ **Mobile responsive**

---

## Commands Quick Reference

```bash
# Start frontend
cd nextjs-mcp-finance && npm run dev

# Run E2E tests (after installing Playwright)
npm install --save-dev @playwright/test
npx playwright test

# View test report
npx playwright show-report

# Check for TypeScript errors
npm run type-check

# Build for production
npm run build

# Start production build
npm run start

# Run linting
npm run lint

# Format code
npm run format
```

---

## Next Steps After Testing

When manual testing is complete:

1. **Document findings** in PHASE_5_TESTING.md
2. **Fix any bugs** found
3. **Run E2E tests** with Playwright
4. **Get performance metrics** from DevTools
5. **Accessibility audit** with axe DevTools
6. **Mobile test** on real device (if possible)

Then mark Phase 5 as ✅ COMPLETE and proceed to deployment.

---

## Need Help?

- **Frontend not starting?** Check `.env.local` has all required keys
- **Auth issues?** Check Clerk dashboard for API keys
- **Payment not working?** Make sure you're in Stripe "Test mode"
- **Can't execute tools?** Check MCP backend is running (if local)
- **AI not working?** Check GEMINI_API_KEY in backend `.env`

---

**Time to first test**: ~5 minutes ⏱️
**Full testing cycle**: ~1 hour ⏱️

**Let's start testing! 🚀**
