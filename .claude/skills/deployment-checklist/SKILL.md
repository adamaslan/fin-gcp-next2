---
name: deployment-checklist
description: Pre-deployment checklist and verification for MCP Finance. Use when deploying, preparing to deploy, or when user mentions deployment, going live, or production readiness.
allowed-tools: Read, Bash(npm *), Bash(git *), Bash(curl *)
---

# Deployment Checklist Skill

Before deploying MCP Finance to production, verify all these items.

## Pre-Deployment Checklist

### 1. Code Quality ✅
```bash
# Run all tests
cd nextjs-mcp-finance
npm run test:e2e
```

- [ ] All E2E tests passing
- [ ] No console.log statements
- [ ] No debugger statements
- [ ] No commented code

### 2. Build Verification ✅
```bash
# Test production build
npm run build
```

- [ ] Build succeeds without errors
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Build size reasonable (< 5MB)

### 3. Environment Variables ✅
```bash
# Check production env vars are set
echo "Checking required env vars..."
```

**Required in Production:**
- [ ] `DATABASE_URL` - Production database
- [ ] `CLERK_SECRET_KEY` - Production Clerk key
- [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Production Clerk public key
- [ ] `STRIPE_SECRET_KEY` - Production Stripe key
- [ ] `STRIPE_WEBHOOK_SECRET` - Production webhook secret
- [ ] `NEXT_PUBLIC_APP_URL` - Production URL

**Verify NO test/dev keys in production!**

### 4. Database ✅
```bash
# Check migrations are applied
cd nextjs-mcp-finance
npx drizzle-kit status
```

- [ ] All migrations applied
- [ ] Database backup created
- [ ] Connection pool configured
- [ ] Indexes in place
- [ ] No seed data in production

### 5. Security ✅

- [ ] All API routes have auth checks
- [ ] Webhook signatures verified
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] No secrets in code/git
- [ ] HTTPS enforced
- [ ] Security headers set

**Check for hardcoded secrets:**
```bash
git grep -i "sk_live" || echo "✅ No Stripe live keys in code"
git grep -i "api_key" | grep -v ".env" || echo "✅ No API keys in code"
```

### 6. Performance ✅

- [ ] Images optimized (next/image)
- [ ] Server components used where possible
- [ ] Database queries optimized
- [ ] Caching strategy implemented
- [ ] CDN configured
- [ ] Monitoring enabled

### 7. Error Handling ✅

- [ ] Error tracking configured (Sentry)
- [ ] All errors logged
- [ ] User-friendly error pages
- [ ] Fallback UI for errors
- [ ] No stack traces exposed

### 8. Webhooks ✅

**Clerk Webhooks:**
```bash
# Verify webhook endpoint
curl -X POST https://your-domain.com/api/webhooks/clerk \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

- [ ] Clerk webhook URL configured
- [ ] Webhook secret set
- [ ] Signature verification working
- [ ] Handles all event types

**Stripe Webhooks:**
- [ ] Stripe webhook URL configured
- [ ] Webhook secret set
- [ ] Signature verification working
- [ ] Payment events handled

### 9. Monitoring & Logging ✅

- [ ] Application logs configured
- [ ] Error tracking enabled
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring configured
- [ ] Alert notifications set up

### 10. Documentation ✅

- [ ] README updated
- [ ] API documentation current
- [ ] Environment variables documented
- [ ] Deployment process documented
- [ ] Rollback procedure documented

## Deployment Steps

### 1. Final Code Review
```bash
git status
git log -5 --oneline
```

### 2. Run Full Test Suite
```bash
/test-all
```

### 3. Create Release Branch
```bash
git checkout -b release/$(date +%Y-%m-%d)
git push origin release/$(date +%Y-%m-%d)
```

### 4. Deploy to Staging First
```bash
# Deploy to staging
vercel --env staging

# Test staging
curl https://staging.your-domain.com/api/health
```

### 5. Smoke Test Staging
- [ ] Can sign up
- [ ] Can sign in
- [ ] Can view stocks
- [ ] Can create transaction
- [ ] Webhooks working

### 6. Deploy to Production
```bash
# Deploy to production
vercel --prod

# Verify deployment
curl https://your-domain.com/api/health
```

### 7. Post-Deployment Verification
```bash
# Run smoke tests
cd nextjs-mcp-finance
npm run test:e2e:production
```

- [ ] Homepage loads
- [ ] Sign in works
- [ ] Core features work
- [ ] No console errors
- [ ] Webhooks firing

### 8. Monitor for Issues
```bash
# Watch logs
vercel logs --follow

# Check error rate
# (in your monitoring dashboard)
```

## Post-Deployment Checklist

### Immediate (First 5 minutes)
- [ ] Application loads
- [ ] No 500 errors
- [ ] Database responsive
- [ ] Authentication working

### Short Term (First hour)
- [ ] No error spikes
- [ ] Performance acceptable
- [ ] Webhooks processing
- [ ] Users can complete flows

### Long Term (First day)
- [ ] Error rate normal
- [ ] Performance metrics good
- [ ] No customer complaints
- [ ] All features working

## Rollback Procedure

If deployment fails:

### 1. Immediate Rollback
```bash
# Rollback to previous version
vercel rollback

# Or redeploy last known good version
git checkout main~1
vercel --prod
```

### 2. Investigate Issue
```bash
# Check logs
vercel logs --since 1h

# Check errors
# (in error tracking dashboard)
```

### 3. Fix and Redeploy
```bash
# Fix the issue
git commit -m "fix: deployment issue"

# Test thoroughly
/test-all

# Deploy again
vercel --prod
```

## Emergency Contacts

**If deployment fails:**
1. Check #deployments Slack channel
2. Review error logs
3. Rollback if critical
4. Contact on-call engineer

## Success Indicators

Deployment succeeded if:
- ✅ Build and deploy complete
- ✅ Health checks passing
- ✅ No error spikes
- ✅ Users can access app
- ✅ Core features working
- ✅ Webhooks processing
- ✅ Performance acceptable

---

**Remember**: Always deploy to staging first, test thoroughly, then deploy to production during low-traffic hours!
