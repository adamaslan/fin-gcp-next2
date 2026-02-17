# Testing Cheat Sheet - Phase 5

**Print this out or keep it handy while testing!**

---

## 1. Quick Setup

```bash
# Terminal 1: Start frontend
cd /Users/adamaslan/code/gcp\ app\ w\ mcp/nextjs-mcp-finance
npm run dev

# Browser: Visit http://localhost:3000
```

**Expected**: Landing page loads with "MCP Finance" heading ✅

---

## 2. Test Credentials

### Free Tier Sign-up
```
Email: test-free-[random]@example.com
Password: TestPass123!
```

### Pro Tier Payment
```
Card: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123
Zip: 12345
```

---

## 3. Quick Test Cases

### Test A: Free Tier (5 min)
```
1. Click "Sign Up"
2. Enter email & password above
3. Click "Sign up"
4. Click "MCP Control Center"
5. Select "analyze_security" tool
6. Enter symbol: AAPL
7. Click "Execute"
8. Verify results show ≤3 signals
9. Check: No "AI Analysis" toggle visible
```

✅ **PASS**: Results display, no AI toggle
❌ **FAIL**: Results missing, AI toggle visible

---

### Test B: Pro Tier (10 min)
```
1. From dashboard, click "Upgrade to Pro"
2. Fill card: 4242 4242 4242 4242 | 12/25 | 123
3. Click "Subscribe"
4. Wait for redirect
5. Go to /mcp-control
6. Select "analyze_security"
7. Enter symbol: AAPL
8. Toggle "AI Analysis" ON (should be visible now!)
9. Click "Execute"
10. Verify "Gemini AI Insights" card appears
11. Check: Market Bias, Action Items, Risk Factors visible
```

✅ **PASS**: AI insights card appears with data
❌ **FAIL**: AI toggle missing, insights don't appear

---

### Test C: All 9 Tools (30 sec each)
```
For each tool, just execute once with AAPL:

1. analyze_security      → [results]
2. analyze_fibonacci     → [results]
3. get_trade_plan        → [results]
4. compare_securities    → [results]
5. screen_securities     → [results]
6. scan_trades           → [results]
7. portfolio_risk        → [results]
8. morning_brief         → [results]
9. options_risk_analysis → [results]

All should return data in < 5 seconds
```

✅ **PASS**: All 9 tools return data
❌ **FAIL**: Any tool hangs or errors

---

## 4. Browser DevTools Checks

### Open DevTools: F12 or Cmd+Option+I

#### Console Tab
```
✅ No red errors
✅ Only yellow warnings (OK)
✅ Blue info logs (expected)

If red error: TAKE SCREENSHOT and report
```

#### Network Tab
```
✅ Page loads < 3 seconds
✅ All requests green (200 OK)
✅ No failed requests (red X)

If slow: Check "Size" and "Time" columns
```

#### Performance Tab
```
1. Go to Performance
2. Click record circle
3. Load /mcp-control
4. Click stop
5. Check: TTI (Time to Interactive) < 3s

Target: < 3 seconds
```

---

## 5. Mobile Check

### DevTools Device Emulation: Ctrl+Shift+M

Test these widths:
```
320px  (iPhone SE)        ✅ [Test here]
375px  (iPhone 12)        ✅ [Test here]
768px  (iPad)             ✅ [Test here]
1024px (iPad Pro)         ✅ [Test here]
```

For each width, check:
- ✅ No horizontal scrollbar
- ✅ Text readable (no zoom needed)
- ✅ Buttons tappable (48px+)
- ✅ Form fills width

---

## 6. Common Errors & Fixes

### "Port 3000 already in use"
```bash
lsof -i :3000
kill -9 [PID]
```

### "Module not found"
```bash
rm -rf node_modules
npm install
npm run dev
```

### "Clerk API key missing"
Check `.env.local` has:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```
Get from: https://dashboard.clerk.com

### "Stripe payment fails"
```bash
# Go to https://dashboard.stripe.com
# Toggle "Test mode" ON (top-right)
# Use test card: 4242 4242 4242 4242
```

---

## 7. Pass/Fail Criteria

### MUST PASS (Critical)
- [x] Landing page loads
- [x] Free user can execute tools
- [x] Pro user can upgrade (Stripe)
- [x] Pro user sees AI insights
- [x] Results display correctly
- [x] No console errors

### SHOULD PASS (Important)
- [x] All 9 tools execute
- [x] Presets save/load
- [x] Mobile responsive
- [x] Performance < 5s
- [x] Error handling works
- [x] Keyboard navigation

### NICE TO HAVE (Extra)
- [x] Accessibility 90%+
- [x] Performance optimized
- [x] All browsers work
- [x] Network offline handled
- [x] Dark mode (if implemented)

---

## 8. Test Results Template

**When you finish, fill this out:**

```
PHASE 5 TEST REPORT
===================

Date: [Today]
Time: [Start - End]
Tester: [Your name]

FREE TIER TEST
✅ Sign-up: PASS / FAIL
✅ Execute: PASS / FAIL
✅ Results: PASS / FAIL
✅ No AI toggle: PASS / FAIL

PRO TIER TEST
✅ Upgrade: PASS / FAIL
✅ AI toggle appears: PASS / FAIL
✅ Execute with AI: PASS / FAIL
✅ Insights display: PASS / FAIL

9 TOOLS TEST
✅ All 9 execute: PASS / FAIL
✅ No hangs: PASS / FAIL
✅ Results display: PASS / FAIL

MOBILE TEST (375px)
✅ Responsive: PASS / FAIL
✅ No scroll: PASS / FAIL
✅ Buttons tappable: PASS / FAIL

PERFORMANCE
✅ Landing < 2s: PASS / FAIL
✅ Control < 3s: PASS / FAIL
✅ Execute < 5s: PASS / FAIL

ERRORS
✅ No console errors: PASS / FAIL
✅ No network failures: PASS / FAIL
✅ Error handling works: PASS / FAIL

OVERALL
✅ READY FOR PRODUCTION: YES / NO

Issues Found:
[List any bugs, minor issues, observations]

Tester Signature: _______________
```

---

## 9. Keyboard Navigation Test

Just use TAB and ENTER:

```
1. Press TAB multiple times
   → Should highlight all buttons/inputs

2. Press SHIFT+TAB
   → Should go backward

3. On button, press ENTER
   → Should activate

4. Check focus indicator visible
   → Blue/purple outline around focused element
```

✅ **PASS**: All interactive elements reachable via keyboard
❌ **FAIL**: Some elements skip focus, focus not visible

---

## 10. Accessibility Quick Check

Use free browser extension: **axe DevTools**

```
1. Install: axe DevTools (Chrome/Firefox)
2. Go to /mcp-control
3. Click axe icon
4. Click "Scan ALL of my page"
5. Check results:
   ✅ Green checkmarks = good
   ⚠️ Yellow warnings = review
   ❌ Red errors = fix
```

Target: **WCAG AA compliance**

---

## 11. Screenshot Checklist

Take screenshots for these moments:

```
□ Landing page (public, no auth)
□ Free tier: /dashboard
□ Free tier: /mcp-control with results
□ Pro tier: Stripe payment flow
□ Pro tier: AI Analysis toggle
□ Pro tier: Gemini insights card
□ Preset selector (loaded)
□ Mobile view (375px)
□ Error message (e.g., invalid symbol)
□ DevTools: Network tab (< 3s load)
□ DevTools: Performance tab (TTI)
```

Store in: `/testing-screenshots/[date]/`

---

## 12. Quick Reference URLs

```
Landing Page:      http://localhost:3000
Sign In:           http://localhost:3000/sign-in
Sign Up:           http://localhost:3000/sign-up
Dashboard:         http://localhost:3000/dashboard
MCP Control:       http://localhost:3000/mcp-control

Dashboards:
Clerk:             https://dashboard.clerk.com
Stripe (Test):     https://dashboard.stripe.com (toggle Test mode)
```

---

## 13. Time Tracking

| Task | Estimate | Actual |
|------|----------|--------|
| Free tier test | 10 min | ___ min |
| Pro tier test | 10 min | ___ min |
| 9 tools test | 5 min | ___ min |
| Mobile test | 5 min | ___ min |
| Performance | 5 min | ___ min |
| DevTools check | 5 min | ___ min |
| **Total** | **40 min** | **___ min** |

---

## 14. Issue Reporting Template

**When you find a bug, report like this:**

```
TITLE: [Short description]

SEVERITY: 🔴 Critical / 🟡 High / 🟢 Low

ENVIRONMENT: Development (localhost:3000)

STEPS TO REPRODUCE:
1. [First step]
2. [Second step]
3. [Third step]

EXPECTED:
[What should happen]

ACTUAL:
[What actually happens]

SCREENSHOT:
[Include if possible]

BROWSER/DEVICE:
[Chrome/Firefox/Safari/Mobile, etc]

CONSOLE ERROR:
[Paste error if applicable]
```

---

## 15. Sign-Off Checklist

✅ All 9 tools tested
✅ Free + Pro tiers tested
✅ AI insights verified
✅ Mobile responsive
✅ No critical bugs
✅ Performance acceptable
✅ No console errors
✅ Error handling verified
✅ Results documented
✅ Screenshots taken

**Date tested**: _______________
**Tester name**: _______________
**Status**: ✅ PASS / ⚠️ CONDITIONAL / ❌ FAIL

---

## Need Help?

- **Docs**: Read PHASE_5_QUICK_START.md
- **Errors**: See section #6 above
- **Questions**: Check PHASE_5_TESTING.md
- **Issues**: Fill out Issue Report (#14)

---

**Happy Testing! 🚀**

**Estimated time to complete: 40 minutes**
**Critical path: Free → Pro → 9 tools**

Let's ship it! 🎯
