# ✅ Phase 5: Testing & Verification

**Date**: February 6, 2026
**Status**: 🚀 IN PROGRESS
**Estimated Time**: 1 hour
**Focus**: End-to-end testing and quality assurance

---

## Overview

Phase 5 verifies that the entire MCP Finance interactive system works correctly across all tiers and tools. This includes:
- Manual testing of all 9 tools
- E2E testing with Playwright
- Performance validation
- Accessibility audit
- Mobile responsiveness

---

## Testing Checklist

### 1. ✅ Landing Page (Public)

- [ ] Page loads without authentication
- [ ] Latest runs grid displays 9 tools
- [ ] Each tool shows:
  - Tool name
  - Latest analysis timestamp
  - Key metrics (e.g., bullish/bearish signals)
  - Link to /mcp-control for signed-in users
- [ ] Responsive on mobile/tablet/desktop
- [ ] No console errors
- [ ] Page load time < 2 seconds (cached)

**Test Command**:
```bash
# Start dev server
npm run dev

# Visit http://localhost:3000
# Inspect console for errors
# Check Network tab for page load time
```

---

### 2. ✅ Authentication Flow

#### Free Tier Sign-up
- [ ] Sign-up page loads
- [ ] User can create account with email/password
- [ ] Redirect to `/mcp-control` after sign-up
- [ ] Default tier is "free"
- [ ] User can sign out

#### Pro Tier Sign-up
- [ ] Click "Upgrade to Pro"
- [ ] Stripe checkout opens
- [ ] Use test card: `4242 4242 4242 4242`
- [ ] Subscription created
- [ ] Tier updates to "pro"
- [ ] Pro features unlock

**Test Command**:
```bash
# Test with Clerk test credentials
# Email: test@example.com
# Password: Test123!

# For Stripe, use test card:
# Card: 4242 4242 4242 4242
# Expiry: 12/25
# CVC: 123
```

---

### 3. ✅ MCP Control Center - Free Tier

#### Tool Selector
- [ ] Shows only free-tier tools (all 9 tools now)
- [ ] Can switch between tools
- [ ] Tool description displays
- [ ] "Upgrade to Pro" CTA visible (if applicable)

#### Parameter Form
- [ ] Form renders with correct input types per tool
- [ ] Required fields marked with *
- [ ] Input placeholders visible
- [ ] Help tooltips appear on hover
- [ ] Defaults populate correctly
- [ ] Validation prevents empty required fields

#### Execute Button
- [ ] Button enabled only when required params filled
- [ ] Button disabled during execution (shows spinner)
- [ ] Loading state displays

#### Results Display
- [ ] Results render correctly for each tool
- [ ] Data is properly filtered for free tier:
  - Analyze Security: 3 signals max
  - Fibonacci: 10 levels max
  - Others: Appropriate tier limits
- [ ] No AI Analysis toggle visible (free tier)
- [ ] Error messages display clearly

**Test Scenario**:
```bash
# As Free User
1. Go to /mcp-control
2. Select "analyze_security"
3. Enter symbol: "AAPL"
4. Click Execute
5. Verify results show ≤ 3 signals
6. No AI Analysis button visible
```

---

### 4. ✅ MCP Control Center - Pro Tier

#### Premium Parameters
- [ ] AI Analysis toggle visible
- [ ] Can toggle AI on/off
- [ ] Toggle is properly labeled

#### Execute with AI
- [ ] Click AI Analysis toggle
- [ ] Execute tool
- [ ] Results include ai_analysis field
- [ ] AIInsights component renders:
  - [ ] Purple/blue gradient card
  - [ ] Gemini badge
  - [ ] Market Bias section
  - [ ] Action Items (bulleted)
  - [ ] Key Takeaways
  - [ ] Risk Factors (red highlighted)
  - [ ] Confidence score with progress bar

#### Presets (Pro Feature)
- [ ] Can save preset after executing
- [ ] Save preset dialog appears
- [ ] Can name and describe preset
- [ ] Preset appears in PresetSelector
- [ ] Can load preset (parameters auto-populate)
- [ ] Can delete preset
- [ ] Presets persist after page reload

**Test Scenario**:
```bash
# As Pro User
1. Go to /mcp-control
2. Select "analyze_security"
3. Set parameters: symbol="AAPL", period="3mo"
4. Toggle AI Analysis ON
5. Click Execute
6. Verify AIInsights card appears
7. Click Save Preset
8. Name it "My 3-Month Analysis"
9. Save and verify it appears in PresetSelector
10. Click Load to test preset loading
```

---

### 5. ✅ Test All 9 Tools

For each tool, test:
1. Free tier execution (basic parameters)
2. Pro tier execution (with AI)
3. Error handling (invalid inputs)

#### Tool 1: analyze_security
- [ ] Free: Can analyze with symbol + period
- [ ] Pro: AI analysis shows market bias
- [ ] Results show bullish/bearish counts
- [ ] Signals list displays correctly

#### Tool 2: analyze_fibonacci
- [ ] Free: Can analyze with symbol
- [ ] Pro: AI analysis for retracements
- [ ] Fibonacci levels display
- [ ] Swing high/low show

#### Tool 3: get_trade_plan
- [ ] Free: Can generate trades
- [ ] Pro: AI analysis for trade setup
- [ ] Entry/stop/target prices display
- [ ] Risk:reward ratio shows

#### Tool 4: compare_securities
- [ ] Free: Can compare up to 5 symbols (if limit applied)
- [ ] Pro: AI comparison insights
- [ ] Comparison scores display
- [ ] Symbol rankings appear

#### Tool 5: screen_securities
- [ ] Free: Can run screen
- [ ] Pro: AI analysis of matches
- [ ] Match count displays
- [ ] Symbol list scrollable

#### Tool 6: scan_trades
- [ ] Free: Can scan trades
- [ ] Pro: AI scan insights
- [ ] Trade count displays
- [ ] Quality scores show

#### Tool 7: portfolio_risk
- [ ] Free: Can analyze portfolio
- [ ] Pro: AI risk assessment
- [ ] Total value displays
- [ ] Max loss calculates
- [ ] Hedge suggestions appear

#### Tool 8: morning_brief
- [ ] Free: Can generate brief
- [ ] Pro: AI brief enhancement
- [ ] Market status displays
- [ ] Summary text shows
- [ ] Timestamp accurate

#### Tool 9: options_risk_analysis
- [ ] Free: Can analyze options
- [ ] Pro: AI risk warnings
- [ ] Risk warnings display
- [ ] Opportunities show
- [ ] Greeks calculate

---

### 6. ✅ Error Handling

#### Invalid Inputs
- [ ] Empty symbol shows error: "Symbol required"
- [ ] Invalid symbol shows clear error
- [ ] Non-numeric number inputs rejected
- [ ] API errors display user-friendly messages

#### Rate Limiting
- [ ] Executing 5+ times within minute shows: "Daily limit reached"
- [ ] Upgrade CTA appears
- [ ] Execute button disabled during limit

#### API Errors
- [ ] 503 (service down) shows helpful message
- [ ] 500 errors don't expose stack traces
- [ ] Network errors handled gracefully

**Test Commands**:
```bash
# Test invalid symbol
1. Go to /mcp-control
2. Select "analyze_security"
3. Enter symbol: "INVALID_SYMBOL_XXXXXX"
4. Click Execute
5. Should show: "Symbol not found" or similar

# Test rate limiting
1. Execute same tool 5 times rapidly
2. 6th execution should fail with rate limit message
```

---

### 7. ✅ Performance Testing

#### Page Load Performance
- [ ] Landing page: < 2s (with cache)
- [ ] MCP Control page: < 3s
- [ ] Tool switching: < 500ms

#### Execution Performance
- [ ] Tool execution: 2-5s typical
- [ ] With AI: 3-8s typical
- [ ] No memory leaks (check DevTools)
- [ ] Results render immediately

**Test with DevTools**:
```bash
# 1. Open Chrome DevTools
# 2. Go to Performance tab
# 3. Load /mcp-control
# 4. Execute a tool
# 5. Check:
#    - Time to interactive (TTI): < 3s
#    - Largest contentful paint (LCP): < 2.5s
#    - Cumulative layout shift (CLS): < 0.1
```

---

### 8. ✅ Accessibility (WCAG AA)

#### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] All buttons focusable
- [ ] Form inputs focusable
- [ ] Focus outline visible on all elements
- [ ] Escape key closes modals

#### Screen Reader Testing
- [ ] Page heading announced
- [ ] Form labels properly associated
- [ ] Button purposes clear
- [ ] Error messages announced
- [ ] Loading states announced

#### Color Contrast
- [ ] All text meets WCAG AA (4.5:1 ratio)
- [ ] Buttons have sufficient contrast
- [ ] No information conveyed by color alone

**Test with Tools**:
```bash
# 1. Use WAVE browser extension (Web Accessibility Evaluation Tool)
# 2. Use axe DevTools
# 3. Test with screen reader:
#    - Mac: VoiceOver (Cmd+F5)
#    - Windows: NVDA (free download)
#    - Windows: Narrator (built-in)

# 4. Keyboard navigation:
#    - Tab to move forward
#    - Shift+Tab to move backward
#    - Enter/Space to activate
#    - Arrow keys for menus
```

---

### 9. ✅ Mobile Responsiveness

#### Viewport Sizes
- [ ] 320px (mobile small)
- [ ] 375px (mobile regular)
- [ ] 768px (tablet)
- [ ] 1024px (desktop)

#### Layout
- [ ] Responsive stacking on mobile
- [ ] Touch targets ≥ 48x48px
- [ ] No horizontal scroll
- [ ] Text readable without zoom
- [ ] Buttons easily tappable

#### Features
- [ ] Tool dropdown responsive
- [ ] Parameter form fills screen width
- [ ] Results readable on small screens
- [ ] Preset selector scrollable on mobile
- [ ] AI insights card responsive

**Test on Device**:
```bash
# 1. Use Chrome DevTools device emulation
# 2. Test on actual devices:
#    - iPhone (iOS)
#    - Android phone
# 3. Use Responsive Design Mode (Ctrl+Shift+M)
```

---

### 10. ✅ Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## Manual Testing Workflow

### Daily Testing Loop (30 min)

```bash
# 1. Start dev server
npm run dev

# 2. Clear cache and reload
# Ctrl+Shift+Delete (Chrome)
# Cmd+Shift+Delete (Mac)

# 3. Test as Free User
# a) Sign-up with new email
# b) Try all 9 tools
# c) Verify tier limits

# 4. Test as Pro User
# a) Upgrade to Pro
# b) Enable AI for each tool
# c) Verify AI insights appear

# 5. Check console for errors
# F12 → Console tab
# Should be clean (no red errors)

# 6. Check network performance
# F12 → Network tab
# Check page load time < 3s
```

---

## E2E Test Suite (Playwright)

### Setup

```bash
# Install Playwright (if not installed)
npm install --save-dev @playwright/test

# Create tests directory
mkdir -p e2e/tests

# Generate basic test config
npx playwright codegen http://localhost:3000
```

### Test File: Landing Page

**File**: `e2e/tests/landing-page.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('should load without authentication', async ({ page }) => {
    await page.goto('/');

    // Check title
    await expect(page).toHaveTitle(/MCP Finance/);

    // Check h1
    await expect(page.locator('h1')).toContainText('MCP Finance');

    // Check latest runs grid
    await expect(page.locator('text=Latest Analysis')).toBeVisible();
  });

  test('should display 9 tools', async ({ page }) => {
    await page.goto('/');

    const tools = [
      'analyze_security',
      'analyze_fibonacci',
      'get_trade_plan',
      'compare_securities',
      'screen_securities',
      'scan_trades',
      'portfolio_risk',
      'morning_brief',
      'options_risk_analysis',
    ];

    for (const tool of tools) {
      const toolCard = page.locator(`text=${tool}`);
      await expect(toolCard).toBeVisible();
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Check no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = 375;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // +1 for rounding
  });
});
```

### Test File: MCP Control (Free Tier)

**File**: `e2e/tests/mcp-control-free.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('MCP Control - Free Tier', () => {
  test.beforeEach(async ({ page }) => {
    // Sign up as free user
    await page.goto('/sign-up');
    await page.fill('input[placeholder="email@example.com"]', `free-${Date.now()}@example.com`);
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.click('button:has-text("Sign up")');
    await page.waitForURL('/dashboard');
  });

  test('should execute analyze_security tool', async ({ page }) => {
    await page.goto('/mcp-control');

    // Select tool
    await page.click('text=analyze_security');

    // Fill parameters
    await page.fill('input[placeholder="Symbol"]', 'AAPL');

    // Execute
    await page.click('button:has-text("Execute")');

    // Wait for results
    await expect(page.locator('text=Results')).toBeVisible();
    await expect(page.locator('text=AAPL')).toBeVisible();

    // Verify free tier limits (3 signals)
    const signals = page.locator('[class*="signal"]');
    const count = await signals.count();
    expect(count).toBeLessThanOrEqual(3);
  });

  test('should not show AI Analysis toggle', async ({ page }) => {
    await page.goto('/mcp-control');

    const aiToggle = page.locator('text=AI Analysis');
    await expect(aiToggle).not.toBeVisible();
  });

  test('should not allow saving presets', async ({ page }) => {
    await page.goto('/mcp-control');

    const saveButton = page.locator('button:has-text("Save Preset")');
    await expect(saveButton).not.toBeVisible();
  });
});
```

### Test File: MCP Control (Pro Tier)

**File**: `e2e/tests/mcp-control-pro.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('MCP Control - Pro Tier', () => {
  test.beforeEach(async ({ page }) => {
    // Sign up and upgrade to pro
    await page.goto('/sign-up');
    const email = `pro-${Date.now()}@example.com`;
    await page.fill('input[placeholder="email@example.com"]', email);
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.click('button:has-text("Sign up")');

    // Upgrade to Pro (using test Stripe card)
    await page.waitForURL('/dashboard');
    await page.click('button:has-text("Upgrade to Pro")');

    // Fill Stripe form
    await page.fill('[name="cardNumber"]', '4242424242424242');
    await page.fill('[name="expiryDate"]', '12/25');
    await page.fill('[name="cvc"]', '123');

    // Complete payment
    await page.click('button:has-text("Subscribe")');
    await page.waitForURL('/dashboard');
  });

  test('should show AI Analysis toggle', async ({ page }) => {
    await page.goto('/mcp-control');

    const aiToggle = page.locator('text=AI Analysis');
    await expect(aiToggle).toBeVisible();
  });

  test('should execute with AI and show insights', async ({ page }) => {
    await page.goto('/mcp-control');

    // Enable AI
    await page.click('input[type="checkbox"][name="use_ai"]');

    // Execute
    await page.fill('input[placeholder="Symbol"]', 'AAPL');
    await page.click('button:has-text("Execute")');

    // Wait for AI insights
    await expect(page.locator('text=Gemini AI Insights')).toBeVisible();
    await expect(page.locator('text=Market Bias')).toBeVisible();
    await expect(page.locator('text=Action Items')).toBeVisible();
  });

  test('should save and load presets', async ({ page }) => {
    await page.goto('/mcp-control');

    // Execute first
    await page.fill('input[placeholder="Symbol"]', 'AAPL');
    await page.fill('select', '3mo');
    await page.click('button:has-text("Execute")');

    // Wait for results
    await page.waitForSelector('text=Results');

    // Save preset
    await page.click('button:has-text("Save Preset")');
    await page.fill('input[placeholder="Preset name"]', 'My Test Preset');
    await page.click('button:has-text("Save")');

    // Verify preset appears
    await expect(page.locator('text=My Test Preset')).toBeVisible();

    // Change symbol
    await page.fill('input[placeholder="Symbol"]', 'MSFT');
    expect(await page.inputValue('input[placeholder="Symbol"]')).toBe('MSFT');

    // Load preset
    await page.click('button:has-text("Load")');
    expect(await page.inputValue('input[placeholder="Symbol"]')).toBe('AAPL');
  });
});
```

### Run Tests

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test e2e/tests/landing-page.spec.ts

# Run in UI mode (interactive)
npx playwright test --ui

# Run in headed mode (visible browser)
npx playwright test --headed

# Generate test trace for debugging
npx playwright test --trace on
npx playwright show-trace trace.zip
```

---

## Continuous Integration (GitHub Actions)

**File**: `.github/workflows/test.yml`

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: npm install

      - name: Install Playwright browsers
        run: npx playwright install

      - name: Start dev server
        run: npm run dev &
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          CLERK_SECRET_KEY: ${{ secrets.CLERK_SECRET_KEY }}
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}

      - name: Wait for server
        run: npx wait-on http://localhost:3000

      - name: Run Playwright tests
        run: npx playwright test

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Testing Metrics

### Target Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Landing page load | < 2s | ⏳ |
| MCP Control load | < 3s | ⏳ |
| Tool execution | 2-5s | ⏳ |
| With AI | 3-8s | ⏳ |
| E2E tests pass rate | 100% | ⏳ |
| Accessibility score | 90+ | ⏳ |
| Mobile viewport score | 90+ | ⏳ |

---

## Sign-off Checklist

- [ ] All 9 tools tested on free tier
- [ ] All 9 tools tested on pro tier
- [ ] AI insights verified working
- [ ] Presets save/load working
- [ ] Error handling verified
- [ ] Mobile responsive verified
- [ ] Accessibility audit passed
- [ ] E2E tests all passing
- [ ] Performance benchmarks met
- [ ] No console errors
- [ ] No memory leaks
- [ ] Cross-browser testing passed

---

## What's Next: Production Deployment

When testing is complete:
1. Deploy to Vercel staging
2. Run smoke tests on staging
3. Get user acceptance testing (UAT)
4. Deploy to production
5. Monitor error rates (Sentry)
6. Monitor performance (Web Vitals)

---

**Status**: Phase 5 Testing & Verification - IN PROGRESS 🚀
