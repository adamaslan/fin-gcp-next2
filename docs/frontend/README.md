# Frontend Documentation

This section covers everything related to the Next.js/React frontend, from local setup through deployment.

---

## Quick Navigation

- **Setup:** [`setup.md`](setup.md) - Get your frontend environment running
- **Components:** [`components.md`](components.md) - UI component library
- **Authentication:** [`authentication.md`](authentication.md) - Clerk integration
- **Payments:** [`stripe-integration.md`](stripe-integration.md) - Stripe payment setup
- **Testing:** [`testing.md`](testing.md) - E2E tests with Playwright
- **Deployment:** [`deployment.md`](deployment.md) - Deploy to Vercel
- **Troubleshooting:** [`troubleshooting.md`](troubleshooting.md) - Common issues & fixes

---

## Tech Stack

- **Framework:** Next.js 16 with App Router
- **Language:** TypeScript (strict mode)
- **UI Library:** React 19
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI
- **Data Fetching:** TanStack Query
- **Authentication:** Clerk
- **Payments:** Stripe
- **Testing:** Playwright (E2E)
- **Hosting:** Vercel

---

## Setup & Development

### New to Frontend?
1. Start with: [`setup.md`](setup.md) - Local development setup
2. Learn: [`components.md`](components.md) - How components work
3. Review: [`../architecture/frontend-backend-connection.md`](../architecture/frontend-backend-connection.md) - API integration
4. Check: `./.claude/CLAUDE.md` - Code standards

### Ready to Code?
- Check [`components.md`](components.md) for available components
- Reference: [`authentication.md`](authentication.md) for user features
- See [`stripe-integration.md`](stripe-integration.md) for payments
- Run tests: [`testing.md`](testing.md)

---

## Key Features

### Authentication (Clerk)
- User sign-up/login
- Social login (Google, GitHub, etc.)
- Multi-factor authentication
- Session management

See: [`authentication.md`](authentication.md)

### Payments (Stripe)
- Credit card processing
- Subscription management
- Webhook handling
- Test mode for development

See: [`stripe-integration.md`](stripe-integration.md)

### Dashboard
- Portfolio overview
- Signal analysis
- Watchlist management
- Alert configuration

See: [`components.md`](components.md)

---

## Common Tasks

| Task | File | Time |
|------|------|------|
| Setup local environment | `setup.md` | 30 min |
| Understand components | `components.md` | 30 min |
| Add user authentication | `authentication.md` | 15 min |
| Setup payments | `stripe-integration.md` | 30 min |
| Write E2E tests | `testing.md` | 45 min |
| Deploy changes | `deployment.md` | 15 min |

---

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/description
   ```

2. **Make Changes**
   - Create components in `src/components/`
   - Update pages in `src/app/`
   - Add types in `src/types/`

3. **Follow Standards**
   - TypeScript strict mode
   - Use Tailwind CSS for styling
   - Follow `./.claude/CLAUDE.md` guidelines

4. **Test Locally**
   - `npm run dev` - Start dev server
   - `npm run test` - Run tests
   - `npm run build` - Build for production

5. **Commit & Push**
   - Clear commit messages
   - Link to issues/PRs
   - Run tests before committing

6. **Deploy**
   - Vercel automatically deploys on merge
   - See [`deployment.md`](deployment.md) for details

---

## Directory Structure

```
nextjs-mcp-finance/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── api/               # API routes
│   │   ├── (auth)/            # Auth-protected routes
│   │   └── (public)/          # Public routes
│   ├── components/             # React components
│   │   ├── ui/                # Reusable UI components
│   │   └── features/          # Feature-specific components
│   ├── lib/                    # Utilities & helpers
│   │   ├── db/                # Database operations
│   │   ├── api/               # API clients
│   │   └── utils/             # Utility functions
│   └── types/                  # TypeScript types
├── public/                     # Static files
├── tests/                      # Test files
└── package.json
```

---

## Code Standards

### TypeScript
- ✅ Use `interface` for object shapes
- ✅ All functions must have return types
- ✅ Avoid `any` type
- ✅ Use strict mode

### React Components
- ✅ Server Components by default
- ✅ Mark client components with `'use client'`
- ✅ Maximum 200 lines per file
- ✅ Single responsibility principle

See: `./.claude/CLAUDE.md` for complete guidelines

---

## Testing

### Unit Tests
- Jest framework
- Mock external APIs
- Test utility functions

### E2E Tests
- Playwright framework
- Test user workflows
- Test authentication flows
- Test payment flows

See: [`testing.md`](testing.md) for setup & examples

---

## Troubleshooting

### Setup Issues
See: [`troubleshooting.md`](troubleshooting.md) - Common problems & solutions

### Component Issues
See: [`components.md`](components.md) - Component API reference

### Authentication Issues
See: [`authentication.md`](authentication.md) - Clerk troubleshooting

### Payment Issues
See: [`stripe-integration.md`](stripe-integration.md) - Stripe troubleshooting

---

## Important Files

- **Project Guidelines:** `./.claude/CLAUDE.md` - Code standards
- **Environment Template:** `.env.example` - Env variables
- **TypeScript Config:** `tsconfig.json`
- **Tailwind Config:** `tailwind.config.ts`
- **ESLint Config:** `.eslintrc.json`

---

## Next Steps

1. **Setup:**
   - Follow [`setup.md`](setup.md)
   - Run local dev server

2. **Learn:**
   - Study [`components.md`](components.md)
   - Review code standards in `./.claude/CLAUDE.md`

3. **Integrate:**
   - Read [`../architecture/frontend-backend-connection.md`](../architecture/frontend-backend-connection.md)
   - Check backend API docs in [`../api-reference/`](../api-reference/)

4. **Features:**
   - Setup authentication: [`authentication.md`](authentication.md)
   - Setup payments: [`stripe-integration.md`](stripe-integration.md)

5. **Test & Deploy:**
   - Write tests: [`testing.md`](testing.md)
   - Deploy: [`deployment.md`](deployment.md)

---

[← Back to Documentation](../README.md)
