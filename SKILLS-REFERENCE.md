# Claude Skills Reference - MCP Finance

Complete reference for using and creating Claude Skills in the MCP Finance project.

---

## Table of Contents

1. [Skills Overview](#skills-overview)
2. [Skill Categories](#skill-categories)
3. [Quick Skill Reference](#quick-skill-reference)
4. [Hooks System](#hooks-system)
5. [Subskills](#subskills)
6. [Creating Custom Skills](#creating-custom-skills)
7. [Skill Workflows](#skill-workflows)
8. [Best Practices](#best-practices)

---

## Skills Overview

Claude Skills are intelligent automation patterns that combine:
- **File generation** from templates
- **Validation** of prerequisites
- **Best practices** enforcement
- **Testing** patterns
- **Documentation** generation

### Benefits

- **Consistency:** Every component follows the same patterns
- **Speed:** Generate complex features in seconds
- **Quality:** Built-in testing and validation
- **Documentation:** Auto-generated docs and examples
- **Learning:** Skills teach best practices

---

## Skill Categories

### Frontend Development
- Component creation
- Form handling
- API integration
- State management
- UI/UX patterns

### Backend Development
- API endpoints
- Business logic
- Data validation
- Background tasks
- Integration services

### DevOps & Infrastructure
- Deployment automation
- Container configuration
- Cloud Functions
- Monitoring setup

### Testing & Quality
- Unit tests
- Integration tests
- E2E tests
- Performance tests

### Database
- Schema design
- Migrations
- Repository patterns
- Query optimization

---

## Quick Skill Reference

### Frontend Skills Cheat Sheet

```bash
# Components
"Create card component with loading state"
"Add modal for stock selection"
"Create table with sorting and filtering"

# Forms
"Create watchlist form with validation"
"Add alert configuration form"

# Charts
"Add candlestick chart for AAPL"
"Create performance comparison chart"

# Pages
"Create portfolio dashboard page"
"Add settings page with tabs"

# Hooks
"Create useStockData custom hook"
"Add useWebSocket hook"
```

### Backend Skills Cheat Sheet

```bash
# API Endpoints
"Create endpoint for price alerts"
"Add REST API for watchlist CRUD"

# Services
"Create alert notification service"
"Add portfolio calculation service"

# Background Tasks
"Create daily analysis background job"
"Add email notification task"

# AI Integration
"Add Gemini analysis for earnings reports"
"Create sentiment analysis service"

# Data Processing
"Add stock data aggregation pipeline"
"Create technical indicator calculator"
```

### DevOps Skills Cheat Sheet

```bash
# Cloud Functions
"Create Cloud Function for market open trigger"
"Add serverless function for portfolio rebalancing"

# Scheduling
"Setup daily market analysis cron job"
"Add hourly price check scheduler"

# Monitoring
"Setup error tracking with Sentry"
"Add performance monitoring"

# Deployment
"Create staging deployment pipeline"
"Add blue-green deployment script"
```

---

## Hooks System

Hooks are automated actions triggered at specific lifecycle events.

### Hook Types

#### 1. Pre-Execution Hooks
Run **before** a skill executes to validate environment:

```json
{
  "hooks": {
    "pre": {
      "validate": ["npm install", "check environment"],
      "backup": "git stash",
      "clean": "rm -rf dist/"
    }
  }
}
```

**Example:**
```bash
# Before creating API endpoint, check Python version
{
  "pre": "python --version | grep '3.11'"
}
```

#### 2. Post-Execution Hooks
Run **after** skill completes successfully:

```json
{
  "hooks": {
    "post": {
      "format": "npm run lint:fix",
      "test": "npm test",
      "commit": "git add . && git commit -m 'Add: [skill-name]'"
    }
  }
}
```

**Example:**
```bash
# After creating component, run tests and format
{
  "post": [
    "npm run test [component].test.tsx",
    "npm run format"
  ]
}
```

#### 3. Error Hooks
Run when skill execution fails:

```json
{
  "hooks": {
    "error": {
      "cleanup": "rm -rf temp/",
      "restore": "git stash pop",
      "notify": "send-slack-notification 'Skill failed'"
    }
  }
}
```

#### 4. Watch Hooks
Trigger on file changes:

```json
{
  "hooks": {
    "watch": {
      "files": ["src/**/*.tsx"],
      "onChange": "npm run lint:fix"
    }
  }
}
```

### Hook Composition

Combine multiple hooks:

```json
{
  "hooks": {
    "pre": ["validate-env", "lint"],
    "post": ["test", "format", "commit"],
    "error": ["cleanup", "restore"]
  }
}
```

---

## Subskills

Subskills are variants of a parent skill with specialized behavior.

### Syntax

```
[parent-skill]:[subskill-variant]
```

### Component Subskills

**Parent:** `create-component`

```bash
# Basic component
create-component:basic
→ Component file only

# With state management
create-component:with-state
→ Component + useState/useReducer

# Form component
create-component:form
→ Component + React Hook Form + Zod validation

# Connected component
create-component:connected
→ Component + TanStack Query integration

# Chart component
create-component:chart
→ Component + Recharts setup
```

**Example Usage:**
```
"Create chart component for portfolio performance"
→ Invokes: create-component:chart
```

### API Endpoint Subskills

**Parent:** `create-api-endpoint`

```bash
# Basic CRUD
create-api-endpoint:crud
→ GET, POST, PUT, DELETE routes

# Read-only
create-api-endpoint:readonly
→ GET routes only

# Webhook receiver
create-api-endpoint:webhook
→ POST with signature validation

# Streaming endpoint
create-api-endpoint:stream
→ SSE or WebSocket endpoint
```

### Dashboard Page Subskills

**Parent:** `create-dashboard-page`

```bash
# Analytics dashboard
create-dashboard-page:analytics
→ Charts + KPI cards + filters

# Data table dashboard
create-dashboard-page:table
→ TanStack Table + export + filters

# Form dashboard
create-dashboard-page:form
→ Multi-step form + validation

# Real-time dashboard
create-dashboard-page:realtime
→ WebSocket integration + live updates
```

### Form Subskills

**Parent:** `create-form`

```bash
# Single-step form
create-form:single
→ One-page form

# Multi-step wizard
create-form:wizard
→ Step-by-step with progress

# Dynamic form
create-form:dynamic
→ Conditional fields based on input

# Search form
create-form:search
→ Autocomplete + debounce
```

---

## Creating Custom Skills

### Step 1: Define Skill Metadata

Create `docs/skills/my-skill.json`:

```json
{
  "skill": {
    "name": "create-price-alert",
    "version": "1.0.0",
    "displayName": "Create Price Alert Feature",
    "description": "Full-stack price alert with frontend, backend, and webhooks",
    "category": "feature",
    "author": "Your Name",
    "tags": ["alerts", "notifications", "webhooks"],

    "triggers": [
      "create price alert",
      "add stock alert",
      "setup price notifications"
    ],

    "prerequisites": {
      "required": [
        {
          "name": "Next.js",
          "version": ">=14.0.0",
          "check": "Check package.json"
        },
        {
          "name": "FastAPI",
          "check": "Check requirements.txt"
        }
      ],
      "optional": [
        {
          "name": "Stripe",
          "purpose": "Premium alerts feature"
        }
      ]
    }
  }
}
```

### Step 2: Define Files to Create

```json
{
  "files": {
    "create": [
      {
        "path": "src/components/alerts/PriceAlertForm.tsx",
        "template": "alert-form-template",
        "description": "Alert creation form"
      },
      {
        "path": "src/app/api/alerts/route.ts",
        "template": "alert-api-template",
        "description": "Alert CRUD API"
      },
      {
        "path": "mcp-finance1/cloud-run/services/alert_service.py",
        "template": "alert-service-template",
        "description": "Alert business logic"
      },
      {
        "path": "mcp-finance1/cloud-run/tasks/price_checker.py",
        "template": "price-checker-template",
        "description": "Background price checking"
      }
    ],
    "modify": [
      {
        "path": "src/lib/db/schema.ts",
        "action": "add-table",
        "content": "alerts table schema"
      }
    ]
  }
}
```

### Step 3: Create Templates

```typescript
// templates/alert-form-template.ts
export const alertFormTemplate = (options: TemplateOptions) => `
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const alertSchema = z.object({
  symbol: z.string().min(1).max(5),
  condition: z.enum(['above', 'below']),
  targetPrice: z.number().positive(),
  notifyVia: z.array(z.enum(['email', 'slack', 'discord'])),
});

type AlertFormData = z.infer<typeof alertSchema>;

export function PriceAlertForm() {
  const form = useForm<AlertFormData>({
    resolver: zodResolver(alertSchema),
  });

  const onSubmit = async (data: AlertFormData) => {
    const response = await fetch('/api/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      // Success handling
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
`;
```

### Step 4: Add Hooks

```json
{
  "hooks": {
    "pre": [
      "Check if Drizzle schema exists",
      "Validate environment variables"
    ],
    "post": [
      "npm run drizzle:generate",
      "npm run test:alerts",
      "npm run lint:fix"
    ],
    "error": [
      "Rollback database changes",
      "Delete created files"
    ]
  }
}
```

### Step 5: Add Validation

```json
{
  "validation": {
    "environmentVariables": [
      "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
      "SLACK_WEBHOOK_URL"
    ],
    "dependencies": [
      "@tanstack/react-query",
      "zod"
    ],
    "fileExists": [
      "src/lib/db/index.ts",
      "mcp-finance1/cloud-run/main.py"
    ]
  }
}
```

### Step 6: Add Testing

```json
{
  "testing": {
    "unit": {
      "files": [
        "src/components/alerts/PriceAlertForm.test.tsx",
        "mcp-finance1/tests/test_alert_service.py"
      ],
      "command": "npm test && pytest"
    },
    "integration": {
      "files": [
        "e2e/alerts/create-alert.spec.ts"
      ],
      "command": "npm run test:e2e"
    }
  }
}
```

### Step 7: Document the Skill

Create `docs/skills/create-price-alert.md`:

```markdown
# Create Price Alert Skill

## Overview
Full-stack implementation of price alert feature with real-time monitoring.

## What It Creates
- Frontend form with validation
- API endpoints (CRUD)
- Backend service layer
- Background price checker
- Webhook notifications
- Database schema

## Usage
"Create price alert feature"
"Add stock price notifications"

## Prerequisites
- Clerk authentication setup
- Database configured
- At least one webhook configured (Slack or Discord)

## Configuration
After creation, configure:
1. Set price check frequency (default: 5 minutes)
2. Configure notification channels
3. Set rate limits per user tier

## Testing
Run: npm run test:alerts
```

---

## Skill Workflows

### Workflow 1: Full-Stack Feature

```bash
# Step 1: Create database schema
"Add alerts table to database"
→ Creates: src/lib/db/schema/alerts.ts
→ Runs: drizzle:generate

# Step 2: Create backend service
"Create alert service in Python"
→ Creates: mcp-finance1/cloud-run/services/alert_service.py
→ Creates: mcp-finance1/cloud-run/models/alert.py

# Step 3: Create API routes
"Add API routes for alerts"
→ Creates: src/app/api/alerts/route.ts
→ Creates: src/app/api/alerts/[id]/route.ts

# Step 4: Create frontend components
"Create alert form component"
→ Creates: src/components/alerts/AlertForm.tsx
→ Creates: src/components/alerts/AlertList.tsx

# Step 5: Add background task
"Create price monitoring background job"
→ Creates: mcp-finance1/cloud-run/tasks/price_monitor.py

# Step 6: Setup webhooks
"Add Slack webhook for alert notifications"
→ Creates: src/lib/integrations/slack-alerts.ts

# Step 7: Add tests
"Create E2E test for alert creation"
→ Creates: e2e/alerts/create-alert.spec.ts
```

### Workflow 2: Component Library

```bash
# Create base components
"Create button component with variants"
"Create input component with validation"
"Create card component"
"Create modal component"

# Create composed components
"Create data table with buttons and inputs"
"Create form with validation and modals"
```

### Workflow 3: API Development

```bash
# Backend
"Create FastAPI router for watchlists"
"Add Pydantic models for watchlist"
"Create watchlist service with business logic"
"Add background task for watchlist sync"

# Frontend
"Create API client for watchlists"
"Add React Query hooks for watchlist"
"Create watchlist components"
```

---

## Best Practices

### 1. Skill Naming

✅ **Good:**
- `create-component` - Clear action
- `add-authentication` - Specific feature
- `setup-webhooks` - Setup task

❌ **Bad:**
- `component` - Too vague
- `do-auth-stuff` - Unclear
- `webhooks-thing` - Imprecise

### 2. Trigger Phrases

✅ **Good:**
```json
"triggers": [
  "create price alert",
  "add stock price notification",
  "setup price alerts"
]
```

❌ **Bad:**
```json
"triggers": [
  "alerts",
  "do something with prices",
  "create"
]
```

### 3. Template Organization

```
docs/
├── skills/
│   ├── frontend/
│   │   ├── create-component.json
│   │   ├── create-form.json
│   │   └── add-chart.json
│   ├── backend/
│   │   ├── create-endpoint.json
│   │   └── add-service.json
│   └── templates/
│       ├── component-template.ts
│       ├── api-template.py
│       └── test-template.ts
```

### 4. Version Control

```json
{
  "version": "1.0.0",
  "changelog": [
    {
      "version": "1.0.0",
      "date": "2024-01-18",
      "changes": ["Initial release"]
    }
  ],
  "compatibility": {
    "next": ">=14.0.0",
    "react": ">=18.0.0"
  }
}
```

### 5. Error Handling

```json
{
  "errorHandling": {
    "missingPrerequisite": "Show install command",
    "fileExists": "Ask to overwrite or merge",
    "validationFails": "Show specific error and fix suggestion"
  }
}
```

### 6. Documentation

Every skill should have:
- Clear description
- Prerequisites list
- Example usage
- Configuration options
- Testing instructions
- Troubleshooting guide

---

## Advanced Skill Patterns

### Composite Skills

Combine multiple skills:

```json
{
  "compositeSkill": {
    "name": "create-crud-feature",
    "steps": [
      { "skill": "create-database-schema", "params": { "entity": "$entity" } },
      { "skill": "create-api-endpoints", "params": { "entity": "$entity" } },
      { "skill": "create-form-component", "params": { "entity": "$entity" } },
      { "skill": "create-list-component", "params": { "entity": "$entity" } },
      { "skill": "add-e2e-test", "params": { "feature": "$entity" } }
    ]
  }
}
```

### Conditional Skills

Execute based on conditions:

```json
{
  "conditions": {
    "if": "user-tier === 'pro'",
    "then": "enable-advanced-features",
    "else": "show-upgrade-prompt"
  }
}
```

### Interactive Skills

Prompt for user input:

```json
{
  "prompts": [
    {
      "id": "entity-name",
      "question": "What is the entity name?",
      "type": "text",
      "validation": "^[A-Z][a-zA-Z]*$"
    },
    {
      "id": "add-tests",
      "question": "Generate tests?",
      "type": "boolean",
      "default": true
    }
  ]
}
```

---

## Skill Execution Lifecycle

```
1. Trigger Detection
   ↓
2. Prerequisite Validation
   ↓
3. Pre-Execution Hooks
   ↓
4. File Generation
   ↓
5. Post-Execution Hooks
   ↓
6. Testing (if configured)
   ↓
7. Success Report
```

If any step fails:
```
Error Detection
   ↓
Error Hooks
   ↓
Rollback (if configured)
   ↓
Error Report
```

---

## Quick Start: Your First Skill

```bash
# 1. Create skill definition
cat > docs/skills/hello-skill.json << EOF
{
  "skill": {
    "name": "hello-world",
    "displayName": "Hello World Skill",
    "triggers": ["create hello component"],
    "files": {
      "create": [{
        "path": "src/components/Hello.tsx",
        "content": "export function Hello() { return <div>Hello World</div>; }"
      }]
    }
  }
}
EOF

# 2. Test the skill
"Create hello component"

# 3. Verify
cat src/components/Hello.tsx
```

---

## Skill Registry

All skills are registered in `docs/skills/registry.json`:

```json
{
  "skills": [
    {
      "name": "create-component",
      "file": "frontend/create-component.json",
      "category": "frontend",
      "enabled": true
    },
    {
      "name": "create-api-endpoint",
      "file": "backend/create-endpoint.json",
      "category": "backend",
      "enabled": true
    }
  ]
}
```

---

## Resources

- **Example Skills:** `docs/skills/examples/`
- **Templates:** `docs/skills/templates/`
- **Testing:** `docs/skills/testing.md`
- **Contributing:** `docs/skills/CONTRIBUTING.md`

---

**Version:** 1.0
**Last Updated:** 2024-01-18
