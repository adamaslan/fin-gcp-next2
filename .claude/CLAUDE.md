# MCP Finance - Project Guidelines

## Technology Stack

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript (strict mode)
- **UI**: React 19, Tailwind CSS, Radix UI
- **Auth**: Clerk
- **Payments**: Stripe
- **Data Fetching**: TanStack Query
- **Database**: PostgreSQL with Drizzle ORM

### Backend
- **MCP Server**: Python (FastAPI/Flask)
- **Stock Data**: Real-time market data integration
- **Database**: PostgreSQL

## Critical Rules

### NO MOCK DATA - EVER

**This is an absolute rule with no exceptions.**

- **Never create mock functions** that return fake/hardcoded data
- **Never use placeholder values** for prices, indicators, or analysis results
- **Never bypass real data sources** with synthetic data
- **If a service is unavailable**, return an error - do not fake results

**Why this matters:**
- Mock data in financial applications is dangerous - it can lead to incorrect trading decisions
- Fake prices/indicators give false confidence in untested code
- Mock data hides integration issues that will surface in production
- Users deserve real data or explicit errors, never silent fakes

**What to do instead:**
- Return HTTP 503 (Service Unavailable) if a dependency is down
- Log detailed errors explaining what's missing
- Provide clear setup instructions for required services
- Use real test data from sandbox/staging environments

```python
# WRONG - Never do this
if not service_available:
    return {"price": 100.0, "signal": "BUY"}  # FAKE DATA

# RIGHT - Fail explicitly
if not service_available:
    raise HTTPException(
        status_code=503,
        detail="MCP server required for analysis - see setup docs"
    )
```

## Code Standards

### TypeScript
- **Always use TypeScript strict mode**
- All functions must have explicit return types
- Use proper TypeScript types, avoid `any`
- Prefer `interface` over `type` for object shapes
- Use `const` by default, `let` only when reassignment needed

```typescript
// Good
interface User {
  id: string;
  email: string;
  name: string;
}

function getUser(id: string): Promise<User> {
  return db.query.users.findFirst({ where: eq(users.id, id) });
}

// Bad
function getUser(id: any): any {
  return db.query.users.findFirst({ where: eq(users.id, id) });
}
```

### React Components
- **Server Components by default** - Use client components only when needed
- Mark client components with `'use client'` directive
- Use client components for: interactivity, hooks, browser APIs
- Keep components focused and single-purpose
- Maximum 200 lines per component file

```typescript
// Server Component (default)
export default async function UserProfile({ userId }: { userId: string }) {
  const user = await getUser(userId);
  return <div>{user.name}</div>;
}

// Client Component (explicit)
'use client';
export function InteractiveButton() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

### File Organization
```
nextjs-mcp-finance/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── api/          # API routes
│   │   ├── (auth)/       # Auth-protected routes
│   │   └── (public)/     # Public routes
│   ├── components/       # React components
│   │   ├── ui/           # Reusable UI components
│   │   └── features/     # Feature-specific components
│   ├── lib/              # Utilities and helpers
│   │   ├── db/           # Database client and schema
│   │   ├── api/          # API clients
│   │   └── utils/        # Utility functions
│   └── types/            # TypeScript types and interfaces
```

## Database Standards

### Drizzle ORM
- Define schemas in `src/lib/db/schema/`
- Use snake_case for database columns
- Use camelCase in TypeScript
- Always use transactions for multi-step operations
- Add indexes for frequently queried columns

```typescript
// src/lib/db/schema/users.ts
import { pgTable, text, timestamp, varchar } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: text('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: text('name').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});
```

### Migrations
- Run migrations before deploying
- Never modify existing migrations
- Test migrations in development first
- Always have rollback plan

```bash
# Create migration
npm run db:generate

# Apply migration
npm run db:migrate

# Verify
npm run db:studio
```

## Authentication (Clerk)

### Rules
- Always check authentication in API routes
- Use `auth()` helper in Server Components
- Use `useAuth()` hook in Client Components
- Never expose user data without auth check
- Validate webhook signatures

```typescript
// API Route
import { auth } from '@clerk/nextjs/server';

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }
  // ... protected logic
}

// Server Component
import { auth } from '@clerk/nextjs/server';

export default async function ProtectedPage() {
  const { userId } = await auth();
  if (!userId) redirect('/sign-in');
  // ... render protected content
}
```

### Webhooks
- Verify all webhook signatures
- Handle webhooks idempotently
- Log all webhook events
- Return 200 even if processing fails (to avoid retries)

## Payments (Stripe)

### Rules
- Never store card details
- Always use Stripe.js for card collection
- Verify webhook signatures
- Handle all webhook events idempotently
- Use test mode keys in development

```typescript
// Webhook handler
import { headers } from 'next/headers';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  const body = await req.text();
  const signature = headers().get('stripe-signature')!;

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    return new Response('Invalid signature', { status: 400 });
  }

  // Handle event
  switch (event.type) {
    case 'payment_intent.succeeded':
      // Process payment
      break;
  }

  return new Response(JSON.stringify({ received: true }));
}
```

## API Design

### Conventions
- Use RESTful patterns
- Return proper HTTP status codes
- Include error messages in responses
- Use pagination for lists
- Version APIs if needed (/api/v1/)

### Status Codes
- 200: Success
- 201: Created
- 400: Bad request (client error)
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Server error

```typescript
// Good API response structure
export async function GET(req: Request) {
  try {
    const data = await fetchData();
    return Response.json({
      success: true,
      data,
    });
  } catch (error) {
    return Response.json(
      {
        success: false,
        error: error.message,
      },
      { status: 500 }
    );
  }
}
```

## Testing Standards

### Requirements
- Write tests for all new features
- Test critical paths (auth, payments, data access)
- Use Playwright for E2E tests
- Minimum 70% code coverage
- Run tests before committing

### Test Organization
```
nextjs-mcp-finance/
├── __tests__/        # Unit tests
└── e2e/              # E2E tests
    ├── auth/         # Authentication flows
    ├── api/          # API endpoint tests
    └── features/     # Feature tests
```

### E2E Test Patterns
```typescript
import { test, expect } from '@playwright/test';

test.describe('User Authentication', () => {
  test('should sign up new user', async ({ page }) => {
    await page.goto('/sign-up');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
  });
});
```

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent production fixes
- `refactor/description` - Code refactoring

### Commit Messages
```
type(scope): Brief description

Detailed explanation if needed

Fixes #123
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
- `feat(auth): Add Google OAuth integration`
- `fix(api): Handle null user in stock endpoint`
- `docs(readme): Update setup instructions`

### Pull Requests
- Link to issue/ticket
- Include screenshots for UI changes
- Update tests
- Run full test suite
- Get at least one review

## Security Best Practices

### Environment Variables
- **Never commit .env files**
- Use .env.local for local development
- Use .env.example as template (no real values)
- Validate all required env vars at startup

```typescript
// src/lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  CLERK_SECRET_KEY: z.string().min(1),
  STRIPE_SECRET_KEY: z.string().min(1),
});

export const env = envSchema.parse(process.env);
```

### Input Validation
- Validate all user input
- Use Zod for schema validation
- Sanitize data before database operations
- Never trust client-side validation alone

```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
});

export async function POST(req: Request) {
  const body = await req.json();
  const validated = userSchema.parse(body); // Throws if invalid
  // ... use validated data
}
```

## Error Handling

### Principles
- Catch errors at appropriate levels
- Log errors with context
- Return user-friendly messages
- Never expose stack traces to users
- Use proper error types

```typescript
// Good error handling
try {
  const result = await riskyOperation();
  return Response.json({ success: true, data: result });
} catch (error) {
  console.error('Operation failed:', {
    error: error.message,
    userId,
    timestamp: new Date().toISOString(),
  });

  return Response.json(
    {
      success: false,
      error: 'Operation failed. Please try again.',
    },
    { status: 500 }
  );
}
```

## Performance Guidelines

### Optimization
- Use React Server Components for data fetching
- Implement proper loading states
- Use Suspense boundaries
- Optimize images with next/image
- Enable caching where appropriate
- Monitor Core Web Vitals

```typescript
// Use streaming with Suspense
import { Suspense } from 'react';

export default function Page() {
  return (
    <div>
      <Suspense fallback={<LoadingSkeleton />}>
        <DataComponent />
      </Suspense>
    </div>
  );
}
```

## Accessibility

### Requirements
- All interactive elements must be keyboard accessible
- Use semantic HTML
- Include ARIA labels where needed
- Maintain color contrast ratios (WCAG AA)
- Test with screen readers

```typescript
// Good accessibility
<button
  onClick={handleClick}
  aria-label="Close dialog"
  className="focus:outline-none focus:ring-2"
>
  <XIcon aria-hidden="true" />
</button>
```

## Python Backend (MCP Server)

### Package Management - MAMBA FIRST!

**CRITICAL: Always use Mamba/Micromamba, never pip directly, use mamba activate fin-ai1 as the first environment always, fall back on other environments if there is an issue**




- **Mamba is the primary package manager** - 2-5x faster than conda
- Use `conda-forge` channel for all packages
- Only use pip for packages unavailable in conda-forge (rare)
- Prefer `micromamba` for CI/CD and containers (statically linked, no dependencies)

### Environment Setup

```bash
# Activate existing environment
mamba activate fin-ai1
```

### environment.yml Structure

```yaml
name: fin-ai1
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - fastapi
  - uvicorn
  - httpx
  - python-dotenv
  - psycopg2  # Database driver
  - pydantic
  - pytest
  - pip
  - pip:
    # Only use pip for packages NOT in conda-forge
    - some-pypi-only-package
```

### Lock Files for Reproducibility

```bash
# Generate lock file (multi-platform)
conda-lock -f environment.yml --lockfile conda-lock.yml

# Create from lock file (using existing fin-ai1)
# micromamba create -n fin-ai1 -f conda-lock.yml

# Commit both environment.yml and conda-lock.yml to git
```

### Standards
- Use type hints for all functions
- Follow PEP 8 style guide
- Use async/await for I/O operations
- Handle errors gracefully
- Log all important events
- Manage dependencies with mamba, not pip

```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

async def fetch_stock_data(symbol: str) -> Optional[StockData]:
    """Fetch real-time stock data for given symbol.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        StockData object or None if not found
    """
    try:
        data = await stock_api.get(symbol)
        return StockData.from_api(data)
    except Exception as e:
        logger.error(f"Failed to fetch {symbol}: {e}")
        return None
```

## Security & Sensitive Data Management

### CRITICAL: Handle Sensitive Data Properly

**Any documentation, reports, or data files that expose sensitive information MUST be immediately added to .gitignore**

### What Constitutes Sensitive Data

❌ **NEVER COMMIT**:
- API keys, tokens, or credentials
- Database passwords or connection strings
- Private financial data or trading information
- Customer data (PII - Personally Identifiable Information)
- Real account numbers, email addresses, phone numbers
- OAuth secrets or JWT signing keys
- AWS/GCP service account keys
- Real market data with timestamps (if it reveals patterns)
- Backend test results with real data (unless anonymized)
- Configuration files with secrets (even if encrypted)

### Adding Files to .gitignore

**If you generate documentation that contains ANY sensitive data**:

1. **Immediately add the file pattern to .gitignore**:
```bash
# Edit .gitignore
echo "reports/*.json" >> .gitignore
echo "backend_test_results/*/raw_data/" >> .gitignore
echo ".env" >> .gitignore
```

2. **Verify it's not already tracked**:
```bash
git status  # Should not show the sensitive file
```

3. **If already tracked, remove it**:
```bash
git rm --cached filename
git commit -m "Remove sensitive file from tracking"
```

4. **Create anonymized version if needed**:
```bash
# Create version with redacted/fake data for examples
# Document clearly that it's anonymized
# Keep original in .gitignore
```

### Backend Test Results Guidelines

**Reports generated from `/scripts/quick_start.sh` should**:
- ✅ Include API response structure (for debugging)
- ✅ Include timing and performance data
- ❌ **NOT include real account data**
- ❌ **NOT include real transaction history**
- ❌ **NOT include real API keys in responses**

**If test results contain sensitive data**:
```bash
# Add to .gitignore
echo "backend_test_results/" >> .gitignore

# Or create policy for each file
echo "backend_test_results/*_SAFE.json" >> .gitignore  # Safe to track
echo "!backend_test_results/*/analysis.md" >> .gitignore  # Keep analysis
```

### Documentation Files Policy

**For markdown documentation generated by AI or scripts**:
- ✅ **SAFE to commit**: Analysis reports, architecture docs, how-to guides
- ❌ **UNSAFE to commit**: Raw API responses with real data, test fixtures with PII
- ⚠️ **REVIEW FIRST**: Generated reports that might contain sensitive patterns

**Example .gitignore patterns**:
```
# Sensitive data
.env
.env.local
*.key
*.pem
credentials.json
service-account.json

# Generated test data with real values
backend_test_results/*/raw_responses/
backend_test_results/*_UNREVIEWED.md

# Safe to track
!backend_test_results/*/analysis.md
!backend_test_results/*/COMPLETE_REPORT.md
```

### Before Committing Documentation

**Checklist**:
- [ ] Searched file for API keys (grep -i "key\|token\|secret\|password")
- [ ] Searched for real account IDs (grep -E "[0-9]{10,}")
- [ ] Searched for PII (grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
- [ ] No real database credentials
- [ ] No real GCP project IDs (use "example-project" instead)
- [ ] File is in .gitignore if it contains any of the above

### Automation

**Create pre-commit hook to catch sensitive data**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for common sensitive patterns
patterns=("API_KEY" "password" "token" "secret" "credentials")

for pattern in "${patterns[@]}"; do
    if git diff --cached | grep -i "$pattern"; then
        echo "ERROR: Sensitive data detected (contains: $pattern)"
        echo "Please add file to .gitignore and remove from staging"
        exit 1
    fi
done
```

---

## Documentation

### Required Documentation
- README.md with setup instructions
- API documentation for endpoints
- Component documentation for complex components
- Database schema documentation
- Deployment guide

### Code Comments
- Document WHY, not WHAT
- Explain complex algorithms
- Note any workarounds or gotchas
- Keep comments up to date

```typescript
// Good comment
// Using setTimeout instead of setInterval to prevent overlapping requests
// if the API is slow to respond
setTimeout(fetchData, 5000);

// Bad comment
// Set timeout to 5000
setTimeout(fetchData, 5000);
```

## Deployment

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] No console.logs or debugger statements
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring enabled
- [ ] Webhooks configured (Clerk, Stripe)

### Environment-specific Settings
- **Development**: Debug mode, test API keys, local database
- **Staging**: Production-like, test data, test API keys
- **Production**: Production keys, real data, error tracking

---

**Remember**: These are guidelines, not rigid rules. Use judgment and discuss significant deviations with the team.

**Questions?** Ask Claude for clarification or check the detailed guides in `/docs`.
