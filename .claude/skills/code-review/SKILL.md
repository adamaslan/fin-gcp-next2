---
name: code-review
description: Review code for quality, security, performance, and best practices in MCP Finance app. Use when reviewing code, pull requests, diffs, or when user mentions code review, PR review, or asks to check code quality.
allowed-tools: Read, Grep, Glob, Bash(git *)
--- ww

# Code Review Skill

When reviewing code for MCP Finance, follow this comprehensive checklist.

## Review Process

### 1. Understand the Context
First, understand what changed:
```bash
# See what files changed
git diff --name-only main...HEAD

# See the actual changes
git diff main...HEAD
```

### 2. Code Quality Checklist

#### TypeScript/React Code
- [ ] **Type Safety**: No `any` types, proper type annotations
- [ ] **Server vs Client Components**: Correct `'use client'` usage
- [ ] **Async Patterns**: Proper async/await, error handling
- [ ] **Component Size**: Components under 200 lines
- [ ] **Props Interface**: Clear, well-typed props
- [ ] **Naming**: Descriptive variable/function names

**Example of good TypeScript:**
```typescript
✅ GOOD:
interface UserProps {
  userId: string;
  onUpdate: (user: User) => Promise<void>;
}

export async function UserProfile({ userId, onUpdate }: UserProps) {
  const user = await getUser(userId);
  return <div>{user.name}</div>;
}

❌ BAD:
export function UserProfile(props: any) {
  const user = props.user;
  return <div>{user.name}</div>;
}
```

#### Security Review
- [ ] **Authentication**: All API routes check `auth()`
- [ ] **Input Validation**: Use Zod schemas for validation
- [ ] **SQL Injection**: Using Drizzle ORM properly (no raw queries)
- [ ] **XSS Prevention**: Sanitizing user input
- [ ] **Secrets**: No hardcoded API keys, use env vars
- [ ] **Webhook Signatures**: Verify Clerk/Stripe webhooks

**Red flags:**
```typescript
❌ CRITICAL: No auth check
export async function GET() {
  const users = await db.query.users.findMany();
  return Response.json(users);
}

✅ FIXED: Auth check added
export async function GET() {
  const { userId } = await auth();
  if (!userId) return new Response('Unauthorized', { status: 401 });

  const users = await db.query.users.findMany();
  return Response.json(users);
}
```

#### Database Operations
- [ ] **Transactions**: Multi-step operations use transactions
- [ ] **Indexes**: Frequently queried columns have indexes
- [ ] **N+1 Queries**: Avoid in loops, use joins
- [ ] **Error Handling**: Database errors caught and logged
- [ ] **Migrations**: Schema changes have migrations

#### API Design
- [ ] **REST Conventions**: Proper HTTP methods and status codes
- [ ] **Error Responses**: Consistent error format
- [ ] **Validation**: Request validation before processing
- [ ] **Rate Limiting**: Consider for public endpoints
- [ ] **Documentation**: Complex endpoints documented

**Good API response structure:**
```typescript
✅ Consistent response format:
return Response.json({
  success: true,
  data: result,
});

// Error:
return Response.json({
  success: false,
  error: 'User not found',
}, { status: 404 });
```

#### Performance
- [ ] **Images**: Using next/image for optimization
- [ ] **Server Components**: Data fetching in server components
- [ ] **Lazy Loading**: Heavy components lazy loaded
- [ ] **Memoization**: Expensive calculations memoized
- [ ] **Database Queries**: Efficient, using indexes

### 3. Testing Review
- [ ] **Tests Included**: New features have tests
- [ ] **Test Coverage**: Critical paths covered
- [ ] **Test Quality**: Tests are meaningful, not just for coverage
- [ ] **E2E Tests**: User flows have E2E tests

Run tests to verify:
```bash
cd nextjs-mcp-finance
npm run test:e2e
```

### 4. Accessibility
- [ ] **Keyboard Navigation**: Interactive elements accessible
- [ ] **ARIA Labels**: Screen reader support
- [ ] **Color Contrast**: WCAG AA compliance
- [ ] **Semantic HTML**: Using correct HTML elements
- [ ] **Focus States**: Visible focus indicators

### 5. Code Style
- [ ] **Consistent Formatting**: Follows project style
- [ ] **No Console Logs**: Remove debug console.logs
- [ ] **Commented Code**: Remove unused code
- [ ] **TODOs**: Address or document TODOs
- [ ] **Import Order**: Organized imports

Run linter:
```bash
npm run lint
```

### 6. Documentation
- [ ] **Complex Logic**: Explained with comments
- [ ] **API Changes**: Updated documentation
- [ ] **README**: Updated if needed
- [ ] **Breaking Changes**: Noted in commit/PR

### 7. Git Hygiene
- [ ] **Commit Messages**: Clear, descriptive
- [ ] **Atomic Commits**: Each commit is logical unit
- [ ] **No Merge Conflicts**: Clean merge
- [ ] **Branch Name**: Follows convention (feature/, bugfix/)

## Review Severity Levels

### 🔴 CRITICAL (Must Fix)
- Security vulnerabilities
- Data loss risks
- Breaking changes without migration
- No authentication on protected routes

### 🟡 IMPORTANT (Should Fix)
- Performance issues
- Poor error handling
- Missing tests for critical paths
- Type safety issues

### 🟢 MINOR (Nice to Have)
- Code style improvements
- Better variable names
- Additional comments
- Refactoring opportunities

## Review Feedback Format

Structure feedback clearly:

```markdown
## Review Summary
[Overall assessment]

## Critical Issues 🔴
1. [Issue] - [Location] - [Why it matters] - [Suggested fix]

## Important Issues 🟡
1. [Issue] - [Location] - [Suggestion]

## Minor Suggestions 🟢
1. [Suggestion] - [Location]

## Positive Notes ✅
- [What was done well]
```

## Common Issues in MCP Finance

### Issue: Missing Auth Check
```typescript
❌ Problem:
export async function DELETE(req: Request) {
  await db.delete(users).where(eq(users.id, userId));
}

✅ Solution:
export async function DELETE(req: Request) {
  const { userId: authUserId } = await auth();
  if (!authUserId) return new Response('Unauthorized', { status: 401 });

  await db.delete(users).where(eq(users.id, authUserId));
}
```

### Issue: Unvalidated Input
```typescript
❌ Problem:
export async function POST(req: Request) {
  const body = await req.json();
  await db.insert(users).values(body);
}

✅ Solution:
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
});

export async function POST(req: Request) {
  const body = await req.json();
  const validated = userSchema.parse(body);
  await db.insert(users).values(validated);
}
```

### Issue: Client Component Overuse
```typescript
❌ Problem: Using client component for no reason
'use client';
export default function UserList() {
  const users = await fetchUsers(); // This should be server component!
  return <div>{users.map(u => <div>{u.name}</div>)}</div>;
}

✅ Solution: Server component
export default async function UserList() {
  const users = await fetchUsers();
  return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
```

## Automated Checks

Run these before requesting review:

```bash
# Type check
npx tsc --noEmit

# Lint
npm run lint

# Tests
npm run test:e2e

# Build
npm run build
```

## Review Best Practices

### For Reviewer:
- ✅ Be constructive, not critical
- ✅ Explain the "why" behind suggestions
- ✅ Acknowledge good work
- ✅ Prioritize issues by severity
- ✅ Provide code examples

### For Author:
- ✅ Test your changes before review
- ✅ Write clear PR description
- ✅ Respond to all comments
- ✅ Ask questions if unclear
- ✅ Don't take feedback personally

## Quick Review Checklist

Use this for fast reviews:

```
[ ] Auth checks present
[ ] Input validated
[ ] Tests included
[ ] No console.logs
[ ] TypeScript types correct
[ ] Error handling present
[ ] No secrets in code
[ ] Lint passes
[ ] Build succeeds
```

---

**Remember**: The goal is to maintain code quality while helping the team grow. Focus on education, not gatekeeping.
