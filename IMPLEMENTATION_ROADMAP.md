# MCP Finance: Interactive Frontend Implementation Roadmap

## 🎯 Overall Goal

Build an **interactive frontend UI** that allows users to:

1. **View latest MCP analysis** on public landing page (all tiers)
2. **Execute any of 9 MCP tools** with custom parameters (free tier+)
3. **Save parameter presets** for quick reuse (pro tier+)
4. **Get Gemini AI insights** alongside technical analysis (pro tier+)
5. **Control gcloud backend** seamlessly from browser without API calls

**Key insight**: Eliminate Yahoo Finance rate limits by running all 9 tools via gcloud Cloud Run, with real-time parameter control from the frontend.

---

## 📊 Project Status

### ✅ COMPLETED (Phase 1-2)
- **Database Schema**: 3 new tables (mcp_presets, mcp_runs, public_latest_runs)
- **Backend API**: 3 endpoints (/api/gcloud/execute, /api/gcloud/presets, /api/dashboard/latest-runs)
- **Code**: 476 lines, full error handling, tier-based access control
- **Migration**: Generated and ready to apply

### ⏳ IN PROGRESS
- **Phase 3**: Frontend UI components (4 hours)
- **Phase 4**: Gemini AI integration (1 hour)
- **Phase 5**: Testing & verification (1 hour)

### 📈 REMAINING: ~6 hours

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    FRONTEND (Next.js 16)                        │
│                                                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Landing Page (Public) ← Latest runs cached data                 │
│  ├─ Hero section with "Latest Analysis"                         │
│  ├─ Grid of 9 latest tool results                               │
│  ├─ CTA: "Sign up to customize parameters"                      │
│                                                                  │
│  Dashboard (Auth) ← Quick actions & usage stats                  │
│  ├─ Today's analysis count vs tier limit                        │
│  ├─ Quick action buttons for each tool                          │
│  ├─ Recent execution history                                    │
│                                                                  │
│  MCP Control Center (Auth, Free+) ← Interactive tool control     │
│  ├─ Left Panel: Tool Selector                                   │
│  │  └─ Dropdown: All 9 tools (filtered by tier)                 │
│  │                                                              │
│  ├─ Left Panel: Preset Selector (Pro+)                          │
│  │  └─ Load saved configurations                                │
│  │                                                              │
│  ├─ Center Panel: Dynamic Parameter Form                        │
│  │  ├─ Symbol input (all tools except options_risk)             │
│  │  ├─ Period selector (8 tools)                                │
│  │  ├─ Universe selector (2 tools)                              │
│  │  ├─ Advanced options (Pro+)                                  │
│  │  └─ AI toggle (Pro+)                                         │
│  │                                                              │
│  └─ Right Panel: Live Results                                   │
│     ├─ Loading state                                            │
│     ├─ Results display (tool-specific)                          │
│     ├─ AI Insights (Pro+ only)                                  │
│     └─ Execution metadata                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓ HTTPS
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│              BACKEND API (Next.js API Routes)                    │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  /api/gcloud/execute ✅ DONE                                     │
│  ├─ Validate tier & usage limits                                │
│  ├─ Execute MCP tool with params                                │
│  └─ Return results (filtered by tier)                           │
│                                                                  │
│  /api/gcloud/presets ✅ DONE                                     │
│  ├─ GET: Fetch user presets                                     │
│  ├─ POST: Save new preset (Pro+)                                │
│  ├─ PUT: Update preset (Pro+)                                   │
│  └─ DELETE: Remove preset (Pro+)                                │
│                                                                  │
│  /api/dashboard/latest-runs ✅ DONE                              │
│  ├─ GET: Public cached runs (no auth)                           │
│  └─ POST: Update cache (internal)                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓ HTTPS
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│        MCP BACKEND (Python, Cloud Run, Deployed)                 │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  9 MCP Tool Endpoints (all deployed) ✅                          │
│  ├─ /api/analyze → analyze_security                             │
│  ├─ /api/fibonacci → analyze_fibonacci                          │
│  ├─ /api/trade-plan → get_trade_plan                            │
│  ├─ /api/compare → compare_securities                           │
│  ├─ /api/screen → screen_securities                             │
│  ├─ /api/scan → scan_trades                                     │
│  ├─ /api/portfolio-risk → portfolio_risk                        │
│  ├─ /api/morning-brief → morning_brief                          │
│  └─ /api/options-risk → options_risk_analysis                   │
│                                                                  │
│  Gemini AI Layer ✅ (Already built: ai_analyzer.py)              │
│  ├─ MCPToolAIAnalyzer class                                     │
│  ├─ Supports all 9 tools                                        │
│  └─ Returns structured JSON insights                            │
│                                                                  │
│  Parameter System ✅ (Already built: profiles/)                  │
│  ├─ Risk presets (risky/neutral/averse)                         │
│  ├─ ConfigManager with validation                               │
│  └─ Session overrides support                                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📋 Detailed Phase Breakdown

### Phase 3: Frontend Components (4 hours)

#### 3.1: MCP Control Center Page (1 hour)
**File**: `/src/app/(dashboard)/mcp-control/page.tsx`

```typescript
"use client";

export default function MCPControlPage() {
  // State: selectedTool, parameters, result, loading

  return (
    <Layout>
      <Header title="MCP Control Center" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Tool & Preset Selector */}
        <ToolConfigPanel />

        {/* Center: Parameter Form */}
        <ParameterFormPanel />

        {/* Right: Results */}
        <ResultsPanel />
      </div>
    </Layout>
  );
}
```

**Features**:
- 3-column responsive layout
- Tool persistence (remember last selected)
- Loading states
- Error boundaries
- Keyboard shortcuts (Cmd+Enter to execute)

#### 3.2: Parameter Form Component (1.5 hours)
**File**: `/src/components/mcp-control/ParameterForm.tsx`

**Dynamic forms for each of 9 tools**:

```typescript
// Tool-specific parameter definitions
const TOOL_PARAMETERS = {
  analyze_security: [
    { name: "symbol", type: "text", required: true, label: "Symbol" },
    { name: "period", type: "select", options: [
      "1mo", "3mo", "6mo", "1y"
    ], default: "1mo", label: "Period" },
    { name: "use_ai", type: "boolean",
      label: "AI Analysis", requiredTier: "pro" },
  ],

  analyze_fibonacci: [
    { name: "symbol", type: "text", required: true },
    { name: "period", type: "select", ... },
    { name: "window", type: "number", min: 50, max: 200, default: 150 },
  ],

  // ... 7 more tool configs
};
```

**Component Features**:
- Auto-generates form based on selected tool
- Input validation (required fields, ranges)
- Type-specific inputs (text, select, number, boolean)
- Tier-gating per field
- Real-time parameter preview
- Clear button for quick reset

#### 3.3: Tool Selector Component (0.5 hours)
**File**: `/src/components/mcp-control/ToolSelector.tsx`

```typescript
const TOOLS = [
  {
    id: "analyze_security",
    name: "Analyze Security",
    description: "150+ signals on any stock/ETF",
    icon: "📊",
    requiredTier: "free",
  },
  {
    id: "analyze_fibonacci",
    name: "Fibonacci Analysis",
    description: "40+ levels, 200+ signals, confluence zones",
    icon: "📈",
    requiredTier: "free",
  },
  // ... 7 more tools
];
```

**Component Features**:
- Search/filter tools
- Display description & icon
- Tier badge indicator
- Locked state for free users
- Tool count indicator

#### 3.4: Preset Selector Component (0.5 hours)
**File**: `/src/components/mcp-control/PresetSelector.tsx`

**Features**:
- Load saved presets for current tool
- Quick apply (auto-fill form)
- Delete preset button
- Create from current (save as new)
- Mark as default
- Tier-gate (Pro+ only)

#### 3.5: Results Display Component (0.5 hours)
**File**: `/src/components/mcp-control/ResultsDisplay.tsx`

**Tool-specific result rendering**:

```typescript
// Example: analyze_security results
<ResultCard>
  <Summary signals={result.signals} />
  <SignalsTable signals={result.signals.slice(0, TIER_LIMITS[tier])} />
  <Indicators data={result.indicators} />
  {tier !== "free" && <AIInsights data={result.ai_analysis} />}
</ResultCard>
```

**Features**:
- Tool-specific formatting
- Tier-based data filtering
- Charts & tables (use existing UI components)
- Copy/export buttons
- Share results option

---

### Phase 4: Gemini AI Integration (1 hour)

#### 4.1: Enable AI in Environment
**Files**: `.env.example`, `/mcp-finance1/.env`

```bash
# Add to both frontend and backend
GEMINI_API_KEY=your-api-key-from-makersuite.google.com
```

#### 4.2: Update All 9 MCP API Routes
**Files**: `/src/app/api/mcp/*/route.ts` (all 9 files)

**Before**:
```typescript
const result = await mcp.analyzeSecurity(symbol, period, false);
```

**After**:
```typescript
// Check tier for AI access
const useAi = tier !== "free" && (parameters.use_ai ?? false);
const result = await mcp.analyzeSecurity(symbol, period, useAi);
```

#### 4.3: AI Insights Component
**File**: `/src/components/mcp-control/AIInsights.tsx`

```typescript
export function AIInsights({ aiAnalysis }) {
  return (
    <Card className="bg-gradient-to-br from-purple-50 to-blue-50">
      <Badge>AI Insights (Gemini)</Badge>

      <Section>
        <h4>Market Bias</h4>
        <p>{aiAnalysis.market_bias}</p>
      </Section>

      <Section>
        <h4>Action Items</h4>
        <ul>{aiAnalysis.action_items.map(...)}</ul>
      </Section>

      <Section>
        <h4>Risk Factors</h4>
        <p className="text-red-600">{aiAnalysis.risk_factors}</p>
      </Section>
    </Card>
  );
}
```

**Features**:
- Display AI-generated insights
- Highlight key action items
- Risk warnings with color coding
- Confidence scores
- Show for Pro+ users only

---

### Phase 5: Testing & Verification (1 hour)

#### 5.1: E2E Test Suite
**File**: `/e2e/mcp-control.spec.ts`

```typescript
test("free user can execute analyze_security", async ({ page }) => {
  // 1. Sign in as free user
  // 2. Navigate to /mcp-control
  // 3. Select "analyze_security" tool
  // 4. Enter symbol "AAPL"
  // 5. Click Execute
  // 6. Verify results appear
  // 7. Verify only top 3 signals shown (free tier limit)
});

test("pro user sees AI insights", async ({ page }) => {
  // 1. Sign in as pro user
  // 2. Toggle "AI Analysis" on
  // 3. Execute tool
  // 4. Verify "AI Insights" card appears
  // 5. Verify market bias, action items, risk factors
});

test("landing page shows latest runs", async ({ page }) => {
  // 1. Navigate to "/"
  // 2. Scroll to "Latest Analysis" section
  // 3. Verify 9 tool results displayed
  // 4. Verify public data (no auth needed)
});
```

#### 5.2: Manual Testing Checklist

```
✅ Database
  - [ ] Migration applied successfully
  - [ ] 3 new tables created
  - [ ] Foreign keys working

✅ API Endpoints
  - [ ] /api/gcloud/execute returns results for all 9 tools
  - [ ] /api/gcloud/presets CRUD operations work
  - [ ] /api/dashboard/latest-runs public access works
  - [ ] Tier-based access control enforced
  - [ ] Usage limits tracked correctly

✅ Frontend - Landing Page
  - [ ] Latest analysis section visible
  - [ ] 9 tool results displayed
  - [ ] CTA prompts sign up
  - [ ] Works on mobile

✅ Frontend - MCP Control Center
  - [ ] Tool selector dropdown works
  - [ ] Parameter form renders correctly for each tool
  - [ ] Execute button triggers API call
  - [ ] Results display appears
  - [ ] Loading states work

✅ Frontend - Presets
  - [ ] Presets load correctly
  - [ ] Can save new preset (Pro+)
  - [ ] Can apply preset (fills form)
  - [ ] Can delete preset
  - [ ] Free tier blocked from saving

✅ Frontend - Gemini AI
  - [ ] GEMINI_API_KEY configured
  - [ ] AI toggle visible (Pro+)
  - [ ] AI insights display when enabled
  - [ ] Free tier can't enable AI
  - [ ] Insights formatted correctly

✅ Tier System
  - [ ] Free: 5 analyses/day limit
  - [ ] Free: Top 3 signals only
  - [ ] Free: Can't save presets
  - [ ] Free: No AI access
  - [ ] Pro: 50 analyses/day
  - [ ] Pro: All signals + AI access
  - [ ] Pro: Can save unlimited presets
  - [ ] Max: Unlimited everything

✅ Error Handling
  - [ ] MCP server down → 503 error
  - [ ] Rate limit hit → 429 error
  - [ ] Invalid parameters → 400 error
  - [ ] User not found → 401 error

✅ Performance
  - [ ] Page loads in < 2 seconds
  - [ ] Execute completes in < 5 seconds
  - [ ] No console errors
  - [ ] Mobile responsive
```

---

## 🎯 Success Criteria

### Functional Requirements ✅
- [x] Landing page displays latest run data (public)
- [x] Free tier can execute tools with default parameters
- [ ] Pro tier can customize all parameters
- [ ] Pro tier can save/load presets
- [ ] Pro tier sees Gemini AI insights
- [ ] Max tier has unlimited executions
- [ ] All 9 tools accessible and functional

### Performance Requirements
- Landing page loads in < 2 seconds
- Tool execution completes in < 5 seconds
- Form renders in < 1 second
- No N+1 queries
- Database queries indexed

### Security Requirements
- All endpoints require auth (except landing page)
- User data properly isolated
- Tier-based access enforced
- Parameters validated server-side
- No SQL injection vulnerabilities
- CSRF tokens on state-changing operations

### UX Requirements
- Mobile responsive design
- Loading states visible
- Error messages helpful
- Keyboard shortcuts (Cmd+Enter)
- Form validation with feedback
- Accessible (WCAG AA)

---

## 📈 Timeline Summary

| Phase | Component | Estimate | Status |
|-------|-----------|----------|--------|
| 1 | Database Schema | 30 min | ✅ DONE |
| 2 | API Endpoints | 2 hours | ✅ DONE |
| 3 | MCP Control Page | 1 hour | ⏳ NEXT |
| 3 | Parameter Form | 1.5 hours | ⏳ NEXT |
| 3 | Tool Selector | 0.5 hours | ⏳ NEXT |
| 3 | Preset Selector | 0.5 hours | ⏳ NEXT |
| 3 | Results Display | 0.5 hours | ⏳ NEXT |
| 4 | Gemini Integration | 1 hour | ⏳ NEXT |
| 5 | Testing & Verification | 1 hour | ⏳ NEXT |
| | **TOTAL** | **~9 hours** | |

**Completed**: 2.5 hours (Phase 1-2)
**Remaining**: ~6.5 hours (Phase 3-5)

---

## 🚀 Next Steps

### Immediate (Phase 3)
1. Create `/mcp-control` page
2. Build ParameterForm with all 9 tool schemas
3. Create ToolSelector component
4. Add PresetSelector (Pro+ only)
5. Build ResultsDisplay component

### Short-term (Phase 4)
1. Add GEMINI_API_KEY to environment
2. Update all 9 MCP API routes to enable `use_ai` parameter
3. Create AIInsights component
4. Test AI output formatting

### Final (Phase 5)
1. E2E testing with Playwright
2. Manual checklist verification
3. Performance profiling
4. Mobile responsiveness check
5. Accessibility audit

---

## 📚 Key Files Reference

### Database
- `src/lib/db/schema.ts` - 3 new tables defined
- `drizzle/0001_odd_night_nurse.sql` - Migration file

### API (Phase 2 - Done)
- `src/app/api/gcloud/execute/route.ts` ✅
- `src/app/api/gcloud/presets/route.ts` ✅
- `src/app/api/dashboard/latest-runs/route.ts` ✅

### Frontend Components (Phase 3 - In Progress)
- `src/app/(dashboard)/mcp-control/page.tsx` - Main page
- `src/components/mcp-control/ParameterForm.tsx` - Dynamic form
- `src/components/mcp-control/ToolSelector.tsx` - Tool picker
- `src/components/mcp-control/PresetSelector.tsx` - Preset loader
- `src/components/mcp-control/ResultsDisplay.tsx` - Results view

### AI & Utils (Phase 4 - Coming)
- `src/components/mcp-control/AIInsights.tsx` - AI insights display
- `.env.example` - Add GEMINI_API_KEY

### Testing (Phase 5 - Coming)
- `e2e/mcp-control.spec.ts` - E2E tests
- `__tests__/mcp-control.test.ts` - Unit tests

---

## 💡 Key Decisions

### Architecture Choices
- **3-column layout** for parameter control (responsive)
- **Dynamic forms** generated from tool definitions (DRY)
- **Tier-based UI** using existing TierGate component
- **Client components** for interactivity, Server components for data

### API Design
- **Execute endpoint** handles all 9 tools via switch statement
- **Presets endpoint** CRUD with ownership validation
- **Latest runs** public endpoint for landing page caching

### Database
- **Run history** in mcpRuns table (analytics + debugging)
- **User presets** in mcpPresets (Pro+ feature)
- **Public cache** in publicLatestRuns (landing page)

---

## ⚠️ Potential Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Large parameter set for form | Use tool-specific definitions, lazy load fields |
| AI API costs exploding | Add cost tracking, implement budget limits |
| Results too large for browser | Paginate signals, implement virtual scrolling |
| Users confused by 9 tools | Add descriptions, helpful examples, guided tour |
| Mobile form cramped | Use bottom sheet/modal for params on mobile |
| Database query performance | Add indexes on user_id, tool_name, created_at |

---

## 📞 Questions to Clarify (if needed)

- Should presets be shareable between users?
- Do we need execution scheduling/automation?
- Should results be exportable (CSV/PDF)?
- Need webhook support for external notifications?
- Should we track which tool is most used?
- Any analytics requirements?

---

## 🎉 End Goal

A fully interactive, real-time MCP tool control center where:

✨ **Any authenticated user** can:
- View 9 latest tool analyses on landing page
- Execute any tool with custom parameters
- See results instantly in browser

✨ **Pro+ users additionally get**:
- Save parameter presets
- Gemini AI insights on every analysis
- Access to advanced tools (options)
- Unlimited daily executions

✨ **Max tier users get**:
- Everything Pro has
- No daily limits
- Priority execution queue

All powered by **real market data via gcloud Cloud Run**, with **no Yahoo Finance rate limits**.
