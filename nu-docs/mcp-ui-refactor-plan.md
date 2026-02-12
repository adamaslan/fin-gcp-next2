# MCP-UI Complete Integration Refactor Plan

**Date**: February 2, 2026
**Goal**: Integrate all 9 MCP tools with AI analysis into frontend with minimal code duplication

---

## Executive Summary

This document outlines the complete refactoring to integrate all 9 MCP tools into MCP Finance frontend:

1. **Complete MCP Integration** - All 9 tools fully functional
2. **Minimal Code Duplication** - Shared components and hooks reduce code by 70%
3. **Consistent AI Analysis** - Unified AI insights across all tools
4. **Tier-Based Access** - Proper gating for all features

---

## Current State Analysis

### Existing Implementation (7 of 9 tools)

| Tool | Status | Client Method | API Route | UI Page | AI |
|------|--------|---------------|-----------|---------|-----|
| analyze_security | ✅ Live | ✅ | ✅ | ✅ | ✅ |
| compare_securities | ❌ Missing | ❌ | ❌ | ❌ | ❌ |
| screen_securities | ✅ Live | ✅ | ✅ | ✅ | ❌ |
| get_trade_plan | ✅ Integrated | ✅ | ✅ | ✅ | ❌ |
| scan_trades | ✅ Live | ✅ | ✅ | ✅ | ❌ |
| portfolio_risk | ✅ Partial | ✅ | ✅ | ⏳ New UI | ❌ |
| morning_brief | ✅ Live | ✅ | ✅ | ✅ | ❌ |
| analyze_fibonacci | ✅ Live | ✅ | ✅ | ✅ | ❌ |
| options_risk_analysis | ❌ Missing | ❌ | ❌ | ❌ | ❌ |

### Key Gaps

1. **Missing Tools**: compare_securities, options_risk_analysis
2. **No AI Integration**: Only analyze_security has AI support
3. **Code Duplication**: Fetch/loading/error patterns repeated 8+ times
4. **Inconsistent UX**: Different loading/error states per page

---

## What Will Be ADDED

### 1. New MCP Client Methods

**Update**: `src/lib/mcp/client.ts`

```typescript
// Add AI parameter to ALL 9 methods
async compareSecurity(..., useAi = false)
async screenSecurities(..., useAi = false)
async scanTrades(..., useAi = false)
async portfolioRisk(..., useAi = false)
async morningBrief(..., useAi = false)
async analyzeFibonacci(..., useAi = false)

// NEW: Missing method
async optionsRiskAnalysis(..., useAi = false)
```

### 2. New TypeScript Types

**Create**: `src/lib/mcp/ai-types.ts`

```typescript
// Shared AI analysis types
export interface AIAnalysis { ... }
export interface AIKeyDriver { ... }
export interface AIActionItem { ... }

// Tool-specific AI extensions
export interface SecurityAIAnalysis extends AIAnalysis { ... }
export interface OptionsAIAnalysis extends AIAnalysis { ... }
export interface PortfolioAIAnalysis extends AIAnalysis { ... }

// Options types
export interface OptionsRiskResult { ... }
export interface OptionsGreeks { ... }
export interface OptionsRiskMetrics { ... }
```

### 3. New Reusable Hooks

**Create**:
- `src/hooks/useMCPQuery.ts` - Generic data fetching for all MCP tools
- `src/hooks/useAIAnalysis.ts` - AI-specific functionality

### 4. New Shared Components

**Create** in `src/components/mcp/`:
- `AIInsightsPanel.tsx` - Display AI analysis
- `AIMarketBias.tsx` - Market bias badge
- `AIActionItems.tsx` - Action items list
- `AIKeyDrivers.tsx` - Key drivers display
- `MCPLoadingState.tsx` - Consistent loading skeleton
- `MCPErrorState.tsx` - Consistent error display
- `MCPEmptyState.tsx` - Consistent empty state

### 5. New UI Pages

**Create**:
- `/src/app/(dashboard)/options/page.tsx` - Options analysis
- `/src/app/(dashboard)/compare/page.tsx` - Security comparison

### 6. New API Routes

**Create**:
- `/api/mcp/options-risk/route.ts`
- `/api/mcp/compare/route.ts`

### 7. Landing Page Enhancements

**Create**:
- `src/components/landing/ToolGrid.tsx` - All 9 tools showcase
- `src/components/landing/AIInsightsShowcase.tsx` - AI examples

**Update**:
- `src/app/page.tsx` - Add new sections

---

## What Will Be REMOVED

### 1. Duplicated Fetch Logic

**Remove from each page** (8+ occurrences):
```typescript
// ~30 lines per page duplicated:
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

useEffect(() => {
  const fetch = async () => { /* 20 lines of fetch logic */ };
  fetch();
}, [deps]);
```

**Lines removed**: 240 lines across 8 pages

### 2. Duplicated Loading Skeletons

**Remove** (8 implementations):
- Skeleton cards
- Loading messages
- Spinner animations

**Lines removed**: 160 lines

### 3. Duplicated Error Handling

**Remove** (8 implementations):
- Error message display
- Retry buttons
- Error type checking

**Lines removed**: 120 lines

### 4. Duplicated Tier Checking

**Remove** (12 implementations):
- Inline tier logic
- Feature toggles
- Upgrade CTAs

**Lines removed**: 180 lines

**Total removed**: ~700 lines of duplicated code

---

## What Will Be MODIFIED

### 1. MCP Client

**File**: `src/lib/mcp/client.ts`

Changes:
- Add `useAi` parameter to 7 existing methods
- Add 1 new method (optionsRiskAnalysis)
- Update all method signatures

### 2. Type System

**File**: `src/lib/mcp/types.ts`

Changes:
- Add `ai_analysis?` field to 8 result types
- Create new Options types (3 new interfaces)
- Create AI extension types (3 new interfaces)

### 3. Tier Configuration

**File**: `src/lib/auth/tiers.ts`

Changes:
- Add AI access per tier
- Add new tool limits
- Update feature matrix

### 4. Dashboard Pages (Refactor)

**Files**:
- `src/app/(dashboard)/page.tsx`
- `src/app/(dashboard)/analyze/[symbol]/page.tsx`
- `src/app/(dashboard)/scanner/page.tsx`
- `src/app/(dashboard)/watchlist/page.tsx`
- `src/app/(dashboard)/fibonacci/page.tsx`
- `src/app/(dashboard)/portfolio/page.tsx`

Changes per file:
- Replace custom fetch with `useMCPQuery` hook
- Remove useState/useEffect for loading/error
- Remove MCPLoadingState components
- Remove MCPErrorState components
- Add AI toggle (tier-gated)
- Add AIInsightsPanel display

### 5. API Routes (Add AI Support)

**Files**:
- `/api/mcp/trade-plan/route.ts`
- `/api/mcp/scan/route.ts`
- `/api/mcp/fibonacci/route.ts`
- `/api/mcp/portfolio-risk/route.ts`
- `/api/dashboard/morning-brief/route.ts`

Changes per file:
- Parse `use_ai` parameter
- Check tier allows AI
- Pass to MCP client
- Return response with ai_analysis

### 6. Navigation

**File**: `src/components/dashboard/Sidebar.tsx`

Changes:
- Add `/options` link (tier-gated)
- Add `/compare` link
- Update nav order

### 7. Landing Page

**File**: `src/app/page.tsx`

Changes:
- Add all 9 tools section
- Add AI examples
- Highlight new tools
- Update value proposition

---

## Code Duplication Reduction

### Before (Current)

| Pattern | Occurrences | Lines |
|---------|-------------|-------|
| Fetch + useState + useEffect | 8 pages | 240 |
| Loading skeleton | 8 pages | 160 |
| Error handling | 8 pages | 120 |
| Tier checking | 12 components | 180 |
| **Total** | | **700** |

### After (Refactored)

| Shared Utility | Replaces | Lines Saved |
|----------------|----------|-------------|
| `useMCPQuery` hook | 8 fetch patterns | 200 |
| `<MCPLoadingState>` | 8 skeletons | 140 |
| `<MCPErrorState>` | 8 error handlers | 100 |
| `<TierGate>` wrapper | 12 tier checks | 150 |
| **Total saved** | | **590** |

### Net Impact

- **Removed**: 700 lines of duplication
- **Added**: 180 lines of shared utilities
- **Net savings**: 520 lines
- **Reduction**: 74% fewer lines

---

## Implementation Priority

### Phase 1: Foundation (Week 1)
Priority: CRITICAL
- [ ] Create shared hooks
- [ ] Create shared components
- [ ] Update types
- [ ] No breaking changes

### Phase 2: AI Integration (Week 2)
Priority: HIGH
- [ ] Add AI to all tools
- [ ] Update API routes
- [ ] Refactor pages
- [ ] Add tier gating

### Phase 3: New Features (Week 3)
Priority: MEDIUM
- [ ] Add options_risk_analysis
- [ ] Create /options page
- [ ] Create /compare page
- [ ] Add API routes

### Phase 4: Polish (Week 4)
Priority: MEDIUM
- [ ] Update landing page
- [ ] Update pricing
- [ ] Full testing
- [ ] Deploy

---

## Tier Access Matrix

| Feature | Free | Pro | Max |
|---------|------|-----|-----|
| analyze_security | 5/day | 50/day | ∞ |
| compare_securities | ❌ | 5 symbols | 10 symbols |
| screen_securities | Basic | Advanced | All |
| get_trade_plan | Swing only | +Day | +Scalp |
| scan_trades | 1/day, 5 | 10/day, 25 | ∞ |
| portfolio_risk | ❌ | Basic | Full |
| morning_brief | Basic | Full | Full |
| analyze_fibonacci | 3 levels | 15 levels | ∞ |
| options_risk_analysis | ❌ | Basic | Full |
| **AI Analysis** | ❌ | Optional | Always |

---

## File Changes Summary

### New Files (21)

Shared utilities:
- `src/lib/mcp/ai-types.ts`
- `src/hooks/useMCPQuery.ts`
- `src/hooks/useAIAnalysis.ts`

Shared components (7):
- `src/components/mcp/AIInsightsPanel.tsx`
- `src/components/mcp/AIMarketBias.tsx`
- `src/components/mcp/AIActionItems.tsx`
- `src/components/mcp/AIKeyDrivers.tsx`
- `src/components/mcp/MCPLoadingState.tsx`
- `src/components/mcp/MCPErrorState.tsx`
- `src/components/mcp/MCPEmptyState.tsx`

Options components (4):
- `src/components/options/GreeksDisplay.tsx`
- `src/components/options/RiskScenarios.tsx`
- `src/components/options/OptionChainSelector.tsx`
- `src/components/options/ProfitLossChart.tsx`

Compare components (3):
- `src/components/compare/ComparisonTable.tsx`
- `src/components/compare/ComparisonChart.tsx`
- `src/components/compare/SecuritySelector.tsx`

Pages (2):
- `src/app/(dashboard)/options/page.tsx`
- `src/app/(dashboard)/compare/page.tsx`

API routes (2):
- `src/app/api/mcp/options-risk/route.ts`
- `src/app/api/mcp/compare/route.ts`

Landing components (4):
- `src/components/landing/ToolGrid.tsx`
- `src/components/landing/OptionsPreview.tsx`
- `src/components/landing/ComparePreview.tsx`
- `src/components/landing/AIInsightsShowcase.tsx`

### Modified Files (15)

Core:
- `src/lib/mcp/client.ts`
- `src/lib/mcp/types.ts`
- `src/lib/auth/tiers.ts`

Pages (6):
- `src/app/(dashboard)/page.tsx`
- `src/app/(dashboard)/analyze/[symbol]/page.tsx`
- `src/app/(dashboard)/scanner/page.tsx`
- `src/app/(dashboard)/watchlist/page.tsx`
- `src/app/(dashboard)/fibonacci/page.tsx`
- `src/app/(dashboard)/portfolio/page.tsx`

API routes (5):
- `src/app/api/mcp/trade-plan/route.ts`
- `src/app/api/mcp/scan/route.ts`
- `src/app/api/mcp/fibonacci/route.ts`
- `src/app/api/mcp/portfolio-risk/route.ts`
- `src/app/api/dashboard/morning-brief/route.ts`

Navigation (2):
- `src/components/dashboard/Sidebar.tsx`
- `src/app/page.tsx`

---

## Success Criteria

✅ All 9 MCP tools fully accessible in UI
✅ AI analysis on all tools (tier-gated)
✅ 70%+ less duplicated code
✅ Consistent loading/error/empty states
✅ Landing page showcases all 9 tools
✅ Full documentation included
✅ All tests passing
✅ Performance maintained

---

**Status**: Plan Complete
**Ready for**: Implementation Phase 1
**Effort**: 4 weeks
**Team**: 1-2 developers

See [mcp-frontend-integration-guide.md](mcp-frontend-integration-guide.md) for technical details.
