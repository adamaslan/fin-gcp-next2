# Phase 1 & 2: Database & Backend API Setup

Quick reference guide for implementing the database schema and API endpoints.

## Phase 1: Database Schema (30 min)

### Location
`/Users/adamaslan/code/gcp app w mcp/nextjs-mcp-finance/src/lib/db/schema.ts`

### Add 3 New Tables

```typescript
// 1. User Parameter Presets (for saving custom tool configs)
export const mcpPresets = pgTable("mcp_presets", {
  id: text("id").primaryKey(),
  userId: text("user_id").references(() => users.id).notNull(),
  name: text("name").notNull(),
  description: text("description"),
  toolName: text("tool_name").notNull(),
  parameters: jsonb("parameters").notNull(),
  isDefault: boolean("is_default").default(false),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// 2. MCP Run History (tracks all tool executions)
export const mcpRuns = pgTable("mcp_runs", {
  id: text("id").primaryKey(),
  userId: text("user_id").references(() => users.id),
  toolName: text("tool_name").notNull(),
  parameters: jsonb("parameters").notNull(),
  result: jsonb("result"),
  status: text("status").notNull(),
  executionTime: integer("execution_time"),
  errorMessage: text("error_message"),
  createdAt: timestamp("created_at").defaultNow(),
});

// 3. Public Latest Runs (cached for landing page)
export const publicLatestRuns = pgTable("public_latest_runs", {
  id: text("id").primaryKey(),
  toolName: text("tool_name").notNull().unique(),
  symbol: text("symbol"),
  result: jsonb("result").notNull(),
  updatedAt: timestamp("updated_at").defaultNow(),
});
```

### Deploy Migration

```bash
cd nextjs-mcp-finance
npm run db:generate    # Creates migration file
npm run db:migrate     # Applies migration to DB
```

---

## Phase 2: Backend API Endpoints (2 hours)

### 2.1: Execute Endpoint
**File**: `/nextjs-mcp-finance/src/app/api/gcloud/execute/route.ts`

```typescript
import { NextResponse } from "next/server";
import { ensureUserInitialized } from "@/lib/auth/user-init";
import { canAccessFeature } from "@/lib/auth/tiers";
import { getMCPClient } from "@/lib/mcp/client";
import { db } from "@/lib/db";
import { mcpRuns } from "@/lib/db/schema";
import { nanoid } from "nanoid";

export async function POST(request: Request) {
  try {
    // 1. Authenticate user
    const { userId, tier } = await ensureUserInitialized();

    // 2. Parse request body
    const { toolName, parameters } = await request.json();
    if (!toolName || !parameters) {
      return NextResponse.json({ error: "Missing toolName or parameters" }, { status: 400 });
    }

    // 3. Check tier access
    if (tier === "free") {
      // Free tier can only use analyze_security, get_trade_plan
      if (!["analyze_security", "get_trade_plan"].includes(toolName)) {
        return NextResponse.json({ error: "Upgrade to Pro for this tool" }, { status: 403 });
      }
    }

    // 4. Check usage limits
    const today = new Date().toISOString().split("T")[0];
    const todayCount = await db
      .select({ count: sql`count(*)` })
      .from(mcpRuns)
      .where(and(eq(mcpRuns.userId, userId), like(mcpRuns.createdAt, `${today}%`)));

    const limits = { free: 5, pro: 50, max: Infinity }[tier];
    if (todayCount[0].count >= limits) {
      return NextResponse.json({ error: "Daily limit reached" }, { status: 429 });
    }

    // 5. Create run record
    const runId = nanoid();
    await db.insert(mcpRuns).values({
      id: runId,
      userId,
      toolName,
      parameters,
      status: "running",
    });

    // 6. Execute MCP tool
    const startTime = Date.now();
    const mcp = getMCPClient();
    let result;

    switch (toolName) {
      case "analyze_security":
        result = await mcp.analyzeSecurity(
          parameters.symbol,
          parameters.period || "1mo",
          tier !== "free" ? parameters.use_ai : false
        );
        break;

      case "analyze_fibonacci":
        result = await mcp.analyzeFibonacci(
          parameters.symbol,
          parameters.period || "1mo",
          parameters.window || 150
        );
        break;

      case "get_trade_plan":
        result = await mcp.getTradePlan(parameters.symbol, parameters.period || "1mo");
        break;

      case "compare_securities":
        result = await mcp.compareSecurity(parameters.symbols, parameters.metric, tier !== "free");
        break;

      case "screen_securities":
        result = await mcp.screenSecurities(parameters.universe, parameters.criteria, parameters.limit);
        break;

      case "scan_trades":
        result = await mcp.scanTrades(parameters.universe, parameters.maxResults);
        break;

      case "portfolio_risk":
        result = await mcp.portfolioRisk(parameters.positions, tier !== "free");
        break;

      case "morning_brief":
        result = await mcp.morningBrief(parameters.watchlist, parameters.marketRegion);
        break;

      case "options_risk_analysis":
        result = await mcp.optionsRiskAnalysis(
          parameters.symbol,
          parameters.optionType || "both",
          parameters.minVolume || 10
        );
        break;

      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }

    const executionTime = Date.now() - startTime;

    // 7. Update run record with results
    await db
      .update(mcpRuns)
      .set({
        result: result as any,
        status: "success",
        executionTime,
      })
      .where(eq(mcpRuns.id, runId));

    return NextResponse.json({
      success: true,
      runId,
      result,
      executionTime,
      usage: { count: todayCount[0].count + 1, limit: limits },
    });

  } catch (error) {
    console.error("Execute error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
```

### 2.2: Presets Endpoint
**File**: `/nextjs-mcp-finance/src/app/api/gcloud/presets/route.ts`

```typescript
import { NextResponse } from "next/server";
import { ensureUserInitialized } from "@/lib/auth/user-init";
import { db } from "@/lib/db";
import { mcpPresets } from "@/lib/db/schema";
import { eq, desc } from "drizzle-orm";
import { nanoid } from "nanoid";

// GET: Fetch user's saved presets
export async function GET(request: Request) {
  try {
    const { userId } = await ensureUserInitialized();

    const userPresets = await db
      .select()
      .from(mcpPresets)
      .where(eq(mcpPresets.userId, userId))
      .orderBy(desc(mcpPresets.createdAt));

    return NextResponse.json({ presets: userPresets });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// POST: Save new preset (Pro tier only)
export async function POST(request: Request) {
  try {
    const { userId, tier } = await ensureUserInitialized();

    if (tier === "free") {
      return NextResponse.json(
        { error: "Upgrade to Pro to save presets" },
        { status: 403 }
      );
    }

    const { name, description, toolName, parameters } = await request.json();

    if (!name || !toolName || !parameters) {
      return NextResponse.json(
        { error: "Missing required fields: name, toolName, parameters" },
        { status: 400 }
      );
    }

    const preset = await db
      .insert(mcpPresets)
      .values({
        id: nanoid(),
        userId,
        name,
        description,
        toolName,
        parameters,
      })
      .returning();

    return NextResponse.json({ preset: preset[0] });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// DELETE: Remove a preset
export async function DELETE(request: Request) {
  try {
    const { userId } = await ensureUserInitialized();
    const { presetId } = await request.json();

    if (!presetId) {
      return NextResponse.json({ error: "Missing presetId" }, { status: 400 });
    }

    await db
      .delete(mcpPresets)
      .where(and(eq(mcpPresets.id, presetId), eq(mcpPresets.userId, userId)));

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
```

### 2.3: Latest Runs Endpoint
**File**: `/nextjs-mcp-finance/src/app/api/dashboard/latest-runs/route.ts`

```typescript
import { NextResponse } from "next/server";
import { db } from "@/lib/db";
import { publicLatestRuns } from "@/lib/db/schema";
import { desc } from "drizzle-orm";

// GET: Public endpoint for landing page (no auth required)
export async function GET(request: Request) {
  try {
    const runs = await db
      .select()
      .from(publicLatestRuns)
      .orderBy(desc(publicLatestRuns.updatedAt))
      .limit(9);

    return NextResponse.json({
      runs,
      lastUpdated: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
```

---

## Testing Endpoints

### Test Execute Endpoint
```bash
curl -X POST http://localhost:3000/api/gcloud/execute \
  -H "Content-Type: application/json" \
  -d '{
    "toolName": "analyze_security",
    "parameters": {
      "symbol": "AAPL",
      "period": "1mo",
      "use_ai": false
    }
  }'
```

### Test Presets Endpoint
```bash
# Get presets
curl http://localhost:3000/api/gcloud/presets

# Save preset
curl -X POST http://localhost:3000/api/gcloud/presets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Setup",
    "description": "Aggressive Fibonacci",
    "toolName": "analyze_fibonacci",
    "parameters": {"symbol": "AAPL", "window": 100}
  }'
```

### Test Latest Runs (Public)
```bash
curl http://localhost:3000/api/dashboard/latest-runs
```

---

## Checklist

- [ ] Add 3 tables to `schema.ts`
- [ ] Run `npm run db:generate` to create migration
- [ ] Run `npm run db:migrate` to apply migration
- [ ] Create `/api/gcloud/execute/route.ts`
- [ ] Create `/api/gcloud/presets/route.ts`
- [ ] Create `/api/dashboard/latest-runs/route.ts`
- [ ] Test all 3 endpoints with curl commands above
- [ ] Verify database tables created: `mcp_presets`, `mcp_runs`, `public_latest_runs`
- [ ] Check tier-based access control working (free vs pro)
- [ ] Verify usage limit counting

---

## Key Files
- **Schema**: `nextjs-mcp-finance/src/lib/db/schema.ts`
- **Execute**: `nextjs-mcp-finance/src/app/api/gcloud/execute/route.ts`
- **Presets**: `nextjs-mcp-finance/src/app/api/gcloud/presets/route.ts`
- **Latest**: `nextjs-mcp-finance/src/app/api/dashboard/latest-runs/route.ts`

**Estimated time**: 2.5 hours total (30 min database + 2 hours API endpoints)
