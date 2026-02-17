# MCP Integration Implementation Checklist

**Quick reference for developers implementing the MCP integration**

---

## Phase 1: Foundation (Week 1)

### Step 1.1: Create Shared Hooks

- [ ] Create `src/hooks/useMCPQuery.ts`
  - [ ] Generic `<T>` for any response type
  - [ ] endpoint, params, enabled parameters
  - [ ] Returns: data, loading, error, refetch
  - [ ] Handle all error cases
  - [ ] Support optional useAi parameter

- [ ] Create `src/hooks/useAIAnalysis.ts`
  - [ ] Request AI analysis on-demand
  - [ ] Cache results
  - [ ] Handle AI unavailable case

**Reference**: Integration Guide → "Shared Hooks"
**Code**: Implementation Guide → Tool #1

### Step 1.2: Create Shared MCP Components

- [ ] `src/components/mcp/AIInsightsPanel.tsx`
  - [ ] Display market bias
  - [ ] Display key drivers
  - [ ] Display action items
  - [ ] Display summary text
  - [ ] Tool-specific layouts

- [ ] `src/components/mcp/AIMarketBias.tsx`
  - [ ] Bias badge (BULLISH/BEARISH/NEUTRAL)
  - [ ] Explanation text
  - [ ] Color coding

- [ ] `src/components/mcp/AIActionItems.tsx`
  - [ ] List action items
  - [ ] Priority badges
  - [ ] Timeframe indicators

- [ ] `src/components/mcp/AIKeyDrivers.tsx`
  - [ ] List key drivers
  - [ ] Importance ratings
  - [ ] Expandable explanations

- [ ] `src/components/mcp/MCPLoadingState.tsx`
  - [ ] Tool-specific loading messages
  - [ ] Skeleton layouts
  - [ ] Spinner animation

- [ ] `src/components/mcp/MCPErrorState.tsx`
  - [ ] Error message display
  - [ ] Retry button
  - [ ] Error type detection

- [ ] `src/components/mcp/MCPEmptyState.tsx`
  - [ ] Empty state message
  - [ ] Call-to-action button
  - [ ] Tool-specific guidance

**Reference**: Integration Guide → "UI Component Layer"

### Step 1.3: Update Type Definitions

- [ ] Update `src/lib/mcp/types.ts`
  - [ ] Add `AIAnalysis` base interface
  - [ ] Add `AIKeyDriver` interface
  - [ ] Add `AIActionItem` interface
  - [ ] Add tool-specific AI types
  - [ ] Add `ai_analysis?` field to existing types
  - [ ] Add `OptionsRiskResult` type
  - [ ] Add `OptionsGreeks` type
  - [ ] Add `OptionsRiskMetrics` type

**Reference**: Refactor Plan → "New Types"

### Step 1.4: Test Shared Components

- [ ] Write unit tests for hooks
- [ ] Write unit tests for components
- [ ] Test with different data shapes
- [ ] Test loading states
- [ ] Test error states
- [ ] Test empty states

---

## Phase 2: AI Integration (Week 2)

### Step 2.1: Add AI Parameters to All MCP Tools

- [ ] Update `src/lib/mcp/client.ts`
  - [ ] `analyzeSecurity(..., useAi)` - already done
  - [ ] `compareSecurity(..., useAi)` - add parameter
  - [ ] `screenSecurities(..., useAi)` - add parameter
  - [ ] `getTradePlan(..., useAi)` - add parameter
  - [ ] `scanTrades(..., useAi)` - add parameter
  - [ ] `portfolioRisk(..., useAi)` - add parameter
  - [ ] `morningBrief(..., useAi)` - add parameter
  - [ ] `analyzeFibonacci(..., useAi)` - add parameter
  - [ ] ✅ `optionsRiskAnalysis(..., useAi)` - new method

**Reference**: Refactor Plan → "New MCP Client Methods"

### Step 2.2: Update API Routes to Support AI

- [ ] Update `/api/mcp/trade-plan/route.ts`
  - [ ] Add `use_ai` parameter parsing
  - [ ] Check tier for AI access
  - [ ] Pass to MCP client
  - [ ] Verify response includes ai_analysis

- [ ] Update `/api/mcp/scan/route.ts`
  - [ ] Same as above

- [ ] Update `/api/mcp/fibonacci/route.ts`
  - [ ] Same as above

- [ ] Update `/api/mcp/portfolio-risk/route.ts`
  - [ ] Same as above

- [ ] Update `/api/dashboard/morning-brief/route.ts`
  - [ ] Same as above

- [ ] Update `/api/mcp/analyze/route.ts`
  - [ ] Should already support AI
  - [ ] Verify working

**Reference**: Integration Guide → "API Routes Layer"

### Step 2.3: Refactor Pages to Use Shared Hooks

- [ ] Update `src/app/(dashboard)/page.tsx` (Dashboard)
  - [ ] Replace custom fetch with useMCPQuery
  - [ ] Remove useState/useEffect for loading
  - [ ] Use <MCPLoadingState>
  - [ ] Use <MCPErrorState>
  - [ ] Test thoroughly

- [ ] Update `src/app/(dashboard)/analyze/[symbol]/page.tsx`
  - [ ] Replace custom fetch with useMCPQuery
  - [ ] Add AI toggle (tier-gated)
  - [ ] Display <AIInsightsPanel> when available
  - [ ] Remove duplicated loading/error code

- [ ] Update `src/app/(dashboard)/scanner/page.tsx`
  - [ ] Same refactoring as above

- [ ] Update `src/app/(dashboard)/watchlist/page.tsx`
  - [ ] Same refactoring

- [ ] Update `src/app/(dashboard)/fibonacci/page.tsx`
  - [ ] Same refactoring

- [ ] Update `src/app/(dashboard)/portfolio/page.tsx`
  - [ ] Same refactoring

**Reference**: Implementation Guide → Page implementations

### Step 2.4: Add AI Tier Gating

- [ ] Update `src/lib/auth/tiers.ts`
  - [ ] Set `ai: true/false` for each tool per tier
  - [ ] Verify free tier has no AI
  - [ ] Verify pro tier has AI
  - [ ] Verify max tier has AI

- [ ] Add AI toggle to pages (tier-gated)
  - [ ] Use `<TierGate feature="ai-analysis" requiredTier="pro">`
  - [ ] Only show for pro+ tiers
  - [ ] Default to enabled for pro+
  - [ ] Default to disabled for free

**Reference**: Integration Guide → "Tier-Based Access Control"

### Step 2.5: Test AI Integration

- [ ] Test with real GEMINI_API_KEY
- [ ] Test AI toggle works
- [ ] Test tier restrictions enforced
- [ ] Test response includes ai_analysis
- [ ] Test display of AI insights
- [ ] Test with AI disabled
- [ ] Test error when AI unavailable

---

## Phase 3: New Features (Week 3)

### Step 3.1: Add options_risk_analysis to MCP Client

- [ ] Update `src/lib/mcp/client.ts`
  - [ ] Add `optionsRiskAnalysis()` method
  - [ ] Support: symbol, positionType, options?, useAi
  - [ ] Call correct endpoint
  - [ ] Handle response

**Reference**: Implementation Guide → Tool #9

### Step 3.2: Create Options Analysis Page

- [ ] Create `src/app/(dashboard)/options/page.tsx`
  - [ ] Copy structure from Implementation Guide
  - [ ] Symbol input
  - [ ] Position type selector (call/put/spread)
  - [ ] AI toggle (tier-gated)
  - [ ] Display Greeks
  - [ ] Display risk metrics
  - [ ] Display scenarios
  - [ ] Display AI insights
  - [ ] Tier gate entire page (Pro+)

**Reference**: Implementation Guide → Tool #9

### Step 3.3: Create Options API Route

- [ ] Create `src/app/api/mcp/options-risk/route.ts`
  - [ ] Follow standard pattern
  - [ ] Parse: symbol, position_type, use_ai
  - [ ] Validate tier
  - [ ] Call MCP client
  - [ ] Return response

**Reference**: Integration Guide → "API Routes Pattern"

### Step 3.4: Create compare_securities Page

- [ ] Create `src/app/(dashboard)/compare/page.tsx`
  - [ ] Symbol input/selector
  - [ ] Add/remove symbols (max per tier)
  - [ ] Metric selector
  - [ ] AI toggle
  - [ ] Comparison table
  - [ ] Rankings
  - [ ] AI insights

**Reference**: Implementation Guide → Tool #2

### Step 3.5: Create compare_securities API Route

- [ ] Create `src/app/api/mcp/compare/route.ts`
  - [ ] Follow standard pattern
  - [ ] Parse: symbols, metric, use_ai
  - [ ] Validate: max symbols per tier
  - [ ] Call MCP client
  - [ ] Return response

**Reference**: Integration Guide → "API Routes Pattern"

### Step 3.6: Update Navigation

- [ ] Update `src/components/dashboard/Sidebar.tsx`
  - [ ] Add `/options` link (tier-gated to Pro+)
  - [ ] Add `/compare` link (all tiers)
  - [ ] Update nav order
  - [ ] Add icons

- [ ] Update other nav if needed
  - [ ] Mobile nav
  - [ ] Command palette
  - [ ] Breadcrumbs

### Step 3.7: Test New Features

- [ ] Test options page
- [ ] Test compare page
- [ ] Test API routes
- [ ] Test tier restrictions
- [ ] Test navigation
- [ ] Test with real data

---

## Phase 4: Polish & Launch (Week 4)

### Step 4.1: Update Landing Page

- [ ] Update `src/app/page.tsx`
  - [ ] Add section showing all 9 tools
  - [ ] Add AI examples
  - [ ] Highlight new tools (options, compare)
  - [ ] Update feature list

- [ ] Create `src/components/landing/ToolGrid.tsx`
  - [ ] Display all 9 tools
  - [ ] Show what each does
  - [ ] Show AI icon where available
  - [ ] Link to tool pages

- [ ] Create `src/components/landing/AIInsightsShowcase.tsx`
  - [ ] Show example AI analysis
  - [ ] Show market bias example
  - [ ] Show action items example
  - [ ] Show key drivers example

- [ ] Create `src/components/landing/OptionsPreview.tsx`
  - [ ] Show options analysis preview
  - [ ] Show Greeks example
  - [ ] Show PnL scenario

- [ ] Create `src/components/landing/ComparePreview.tsx`
  - [ ] Show comparison preview
  - [ ] Show comparison table
  - [ ] Show rankings

**Reference**: Implementation Guide → Tool details

### Step 4.2: Update Pricing Page

- [ ] Update pricing tiers
  - [ ] Show AI as Pro+ feature
  - [ ] Show options as Pro+ feature
  - [ ] Show compare as all tiers
  - [ ] Highlight AI benefits

- [ ] Update feature matrix
  - [ ] Add AI column
  - [ ] Add options row
  - [ ] Add compare row
  - [ ] Verify tier restrictions

### Step 4.3: Full Testing

- [ ] Unit tests
  - [ ] All hooks
  - [ ] All components
  - [ ] All utilities

- [ ] Integration tests
  - [ ] All API routes
  - [ ] All data flows
  - [ ] Tier enforcement

- [ ] E2E tests (Playwright)
  - [ ] Sign up → analyze → AI insights
  - [ ] Navigate to each tool
  - [ ] Tier restrictions
  - [ ] Error handling
  - [ ] Loading states

- [ ] Manual testing
  - [ ] All 9 tools
  - [ ] All tiers (free/pro/max)
  - [ ] All browsers
  - [ ] Mobile responsiveness

### Step 4.4: Documentation

- [ ] Update API documentation
- [ ] Update component documentation
- [ ] Update user guides
- [ ] Create migration guide if needed
- [ ] Document new features

### Step 4.5: Deployment

- [ ] Build test
  - [ ] No TypeScript errors
  - [ ] No linting errors
  - [ ] Optimized build

- [ ] Staging deployment
  - [ ] Deploy to staging
  - [ ] Run full test suite
  - [ ] Test with real services
  - [ ] Performance check

- [ ] Production deployment
  - [ ] Backup database
  - [ ] Deploy (blue-green if possible)
  - [ ] Monitor errors
  - [ ] Verify all working
  - [ ] Announce to users

---

## Testing Checklist

### Unit Tests
- [ ] useMCPQuery hook
- [ ] useAIAnalysis hook
- [ ] All shared components
- [ ] AI type transformations
- [ ] Tier validation logic

### Integration Tests
- [ ] All 9 MCP tools return correct data
- [ ] API routes authenticate properly
- [ ] Tier restrictions enforced
- [ ] AI analysis included when requested
- [ ] Error handling works
- [ ] Usage limits enforced

### E2E Tests (Playwright)
- [ ] User can sign up
- [ ] User can analyze security
- [ ] User can request AI analysis (Pro+)
- [ ] User can view options page (Pro+)
- [ ] User can compare securities
- [ ] Tier restrictions work
- [ ] Error pages display correctly
- [ ] Mobile works

### Manual Testing
- [ ] All 9 tools work
- [ ] All tiers work (free/pro/max)
- [ ] AI toggle works
- [ ] Loading states display
- [ ] Error states display
- [ ] Empty states display
- [ ] Navigation works
- [ ] Responsive design works

---

## Verification Checklist

### Before Committing
- [ ] No TypeScript errors
- [ ] No linting errors
- [ ] Tests passing locally
- [ ] Code reviewed
- [ ] No console.logs left
- [ ] No commented code

### Before Deployment
- [ ] All tests passing
- [ ] Build succeeds
- [ ] No console errors
- [ ] Performance metrics good
- [ ] All features working
- [ ] Documentation updated

### After Deployment
- [ ] Monitor error tracking
- [ ] Monitor performance
- [ ] Monitor user feedback
- [ ] Check analytics
- [ ] Verify all features working
- [ ] Check mobile experience

---

## Quick Reference: Key Files

### Create New
```
src/hooks/
  ├── useMCPQuery.ts
  └── useAIAnalysis.ts

src/components/mcp/
  ├── AIInsightsPanel.tsx
  ├── AIMarketBias.tsx
  ├── AIActionItems.tsx
  ├── AIKeyDrivers.tsx
  ├── MCPLoadingState.tsx
  ├── MCPErrorState.tsx
  └── MCPEmptyState.tsx

src/app/(dashboard)/
  ├── options/page.tsx
  └── compare/page.tsx

src/app/api/mcp/
  ├── options-risk/route.ts
  └── compare/route.ts
```

### Modify
```
src/lib/mcp/
  ├── client.ts        (add AI params + 2 methods)
  └── types.ts         (add AI types)

src/lib/auth/
  └── tiers.ts         (update limits)

src/app/(dashboard)/
  ├── page.tsx         (refactor)
  ├── analyze/[symbol]/page.tsx
  ├── scanner/page.tsx
  ├── watchlist/page.tsx
  ├── fibonacci/page.tsx
  └── portfolio/page.tsx

src/app/api/mcp/
  ├── trade-plan/route.ts
  ├── scan/route.ts
  ├── fibonacci/route.ts
  └── portfolio-risk/route.ts

src/components/
  ├── dashboard/Sidebar.tsx
  └── landing/ (multiple files)

src/app/
  └── page.tsx         (landing)
```

---

## Common Pitfalls to Avoid

- ❌ Don't forget to add `use_ai` parameter to all MCP methods
- ❌ Don't forget to check tier before allowing AI
- ❌ Don't leave duplicate fetch code - use hooks
- ❌ Don't forget to handle null ai_analysis
- ❌ Don't forget tier validation in API routes
- ❌ Don't forget to update types.ts for new response fields
- ❌ Don't break existing pages while refactoring
- ❌ Don't forget error handling in new routes
- ❌ Don't forget loading/error/empty states
- ❌ Don't deploy without full test coverage

---

## Useful Commands

```bash
# Run tests
npm test

# Run specific test
npm test -- --testNamePattern="useMCPQuery"

# Build and check for errors
npm run build

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# E2E tests
npx playwright test

# Start dev server
npm run dev
```

---

## Success Indicators

✅ When you know Phase 1 is done:
- All shared hooks created and tested
- All shared components created and tested
- All types updated
- All existing pages still working

✅ When you know Phase 2 is done:
- AI parameter added to all 9 methods
- All API routes updated
- All pages refactored to use hooks
- AI toggle visible on all pages (tier-gated)

✅ When you know Phase 3 is done:
- Options page working
- Compare page working
- New API routes working
- Navigation updated
- All 9 tools fully functional

✅ When you know Phase 4 is done:
- Landing page updated
- Pricing updated
- All tests passing
- Documentation complete
- Ready to deploy

---

## Phase Completion Signs

### Phase 1 Complete
- Hooks work with all endpoint types
- Components display correctly
- Types match actual responses
- Tests passing

### Phase 2 Complete
- AI toggle visible on all pages
- AI analysis displays when available
- Tier restrictions enforced
- No duplicated fetch code

### Phase 3 Complete
- 9 tools accessible from nav
- All tools display their data
- New pages (options, compare) working
- All API routes tested

### Phase 4 Complete
- Landing page showcases all 9 tools
- Pricing reflects features
- All tests passing (unit + integration + E2E)
- Documentation complete
- Ready for production

---

## Getting Unstuck

**Problem**: Hook not getting data
→ Check endpoint is correct
→ Check params are correct
→ Check API route exists
→ Check MCP client method exists

**Problem**: AI analysis not showing
→ Check GEMINI_API_KEY is set
→ Check tier allows AI
→ Check response includes ai_analysis
→ Check use_ai parameter is true

**Problem**: Tier restrictions not working
→ Check tiers.ts is updated
→ Check API route checks tier
→ Check component uses TierGate
→ Check feature name matches

**Problem**: TypeScript errors
→ Check types.ts has all fields
→ Check response matches type
→ Run npm run type-check
→ Check for any type mismatches

---

**Version**: 1.0
**Last Updated**: February 2, 2026
**Print & Keep Handy**: ✅ Yes!

---

Good luck with implementation! 🚀
