# MCP Finance Documentation

Welcome to the comprehensive documentation for **MCP Finance**, a full-stack financial analysis application combining Next.js frontend, Python backend (MCP), and PostgreSQL database with 150+ trading signals.

---

## 🚀 Quick Start

**Choose your path based on what you need to do:**

### I'm a New Developer
Start here: [**Getting Started (5 min)**](getting-started/quickstart-5min.md)
- Quick 5-minute setup
- [Full development setup guide](getting-started/development-setup.md)
- [Mamba environment setup](getting-started/mamba-environment.md)
- [First-run checklist](getting-started/first-run-checklist.md)

### I'm a Frontend Developer
Start here: [**Frontend Documentation**](frontend/README.md)
- Local frontend setup
- Component architecture
- Clerk authentication integration
- Stripe payments setup
- Testing with Playwright
- Deployment to Vercel

### I'm a Backend Developer
Start here: [**Backend Documentation**](backend/README.md)
- Backend environment setup
- Running the MCP server
- API endpoints reference
- Signal & indicator implementation
- Performance optimization
- Testing & debugging

### I'm Setting Up DevOps/Infrastructure
Start here: [**DevOps Documentation**](devops/README.md)
- Docker & container setup
- GCP Cloud Run deployment
- PostgreSQL/Neon database configuration
- CI/CD pipelines (GitHub Actions)
- Monitoring & logging
- Environment variables

### I Want to Understand the Architecture
Start here: [**Architecture Documentation**](architecture/README.md)
- System overview
- Database schema
- Frontend-backend connection
- Signal & indicator framework
- Tier system design

### I Need Security Information
Start here: [**Security Documentation**](security/README.md)
- Sensitive data handling
- Secrets management
- Authentication security
- Webhook verification
- Security audit checklist

---

## 📚 Complete Documentation Map

### Core Documentation

| Section | Purpose | Key Files |
|---------|---------|-----------|
| **[Getting Started](getting-started/)** | Onboarding & setup | `quickstart-5min.md`, `development-setup.md`, `mamba-environment.md` |
| **[Architecture](architecture/)** | System design & concepts | `system-overview.md`, `database-schema.md`, `frontend-backend-connection.md` |
| **[Frontend](frontend/)** | React/Next.js development | `setup.md`, `components.md`, `authentication.md`, `stripe-integration.md` |
| **[Backend](backend/)** | Python MCP server | `setup.md`, `running-the-server.md`, `api-endpoints.md`, `signals-implementation.md` |
| **[DevOps](devops/)** | Infrastructure & deployment | `docker-security.md`, `gcp-deployment.md`, `database-setup.md`, `ci-cd.md` |
| **[Security](security/)** | Security & compliance | `sensitive-data-handling.md`, `secrets-management.md`, `audit-checklist.md` |
| **[Testing](testing/)** | Testing & quality assurance | `unit-testing.md`, `e2e-testing.md`, `api-testing.md`, `test-data.md` |

### Reference Documentation

| Section | Purpose | Key Files |
|---------|---------|-----------|
| **[API Reference](api-reference/)** | API documentation | `analysis-endpoints.md`, `portfolio-endpoints.md`, `alerts-endpoints.md`, `errors.md` |
| **[Tools & Skills](tools-and-skills/)** | Claude Code automation | `available-skills.md`, `creating-custom-skills.md` |
| **[Guides & How-To](guides/)** | Task-based guides | `add-new-signal.md`, `deploy-changes.md`, `troubleshoot-issues.md` |
| **[Reference](reference/)** | Quick lookups | `command-line.md`, `environment-vars.md`, `glossary.md`, `naming-conventions.md` |
| **[Project Info](project-info/)** | Project metadata | `business-plan.md`, `roadmap.md`, `changelog.md`, `contributing.md` |

### Archive & Status

| Section | Purpose | Contents |
|---------|---------|----------|
| **[Archive](_archive/)** | Historical docs | Status reports, planning docs, experiments, design evolution |
| **[Reports](../reports/)** | Current status | Project status, what works, what doesn't |

---

## 👥 Documentation by Role

### New Developer
1. Read: [Getting Started](getting-started/README.md) - 30 minutes
2. Read: [Architecture Overview](architecture/system-overview.md) - 15 minutes
3. Setup: [Development Environment](getting-started/development-setup.md) - 45 minutes
4. Explore: [Frontend](frontend/) or [Backend](backend/) based on focus area
5. Reference: Keep `.claude/CLAUDE.md` nearby for coding standards

**Total onboarding time: ~2 hours**

### Frontend Developer
1. Setup: [Frontend Setup](frontend/setup.md) - 30 minutes
2. Learn: [Components Guide](frontend/components.md) - 30 minutes
3. Implement: [Authentication](frontend/authentication.md) & [Stripe](frontend/stripe-integration.md) - 1 hour
4. Test: [E2E Testing](testing/e2e-testing.md) - 30 minutes
5. Deploy: [Frontend Deployment](frontend/deployment.md) - 15 minutes
6. Reference: [API Reference](api-reference/) for backend integration

**Key files:** `frontend/setup.md`, `frontend/components.md`, `architecture/frontend-backend-connection.md`

### Backend Developer
1. Setup: [Backend Setup](backend/setup.md) - 30 minutes
2. Learn: [Running the Server](backend/running-the-server.md) - 30 minutes
3. Reference: [API Endpoints](api-reference/) - ongoing
4. Implement: [Signals](backend/signals-implementation.md) - 1-2 hours per signal
5. Test: [Backend Testing](testing/api-testing.md) - 30 minutes
6. Optimize: [Performance Guide](backend/performance.md) - as needed
7. Reference: [Architecture](architecture/) for system context

**Key files:** `backend/setup.md`, `backend/running-the-server.md`, `backend/api-endpoints.md`

### DevOps/Infrastructure
1. Learn: [Architecture](architecture/system-overview.md) - 30 minutes
2. Setup: [Docker Security](devops/docker-security.md) - 30 minutes
3. Deploy: [GCP Deployment](devops/gcp-deployment.md) - 1 hour
4. Configure: [Database Setup](devops/database-setup.md) & [Environment Vars](devops/environment-variables.md) - 45 minutes
5. Monitor: [Monitoring & Logging](devops/monitoring.md) - 30 minutes
6. Reference: [CI/CD Pipelines](devops/ci-cd.md) - as needed

**Key files:** `devops/README.md`, `devops/gcp-deployment.md`, `devops/docker-security.md`

### Security Auditor
1. Read: [Security Overview](security/README.md) - 30 minutes
2. Review: [Sensitive Data Handling](security/sensitive-data-handling.md) - 30 minutes
3. Check: [Secrets Management](security/secrets-management.md) - 30 minutes
4. Audit: [Audit Checklist](security/audit-checklist.md) - 1 hour
5. Reference: `.claude/CLAUDE.md` security sections, `SECURITY_CONCERNS.md`

**Key files:** `security/README.md`, `security/sensitive-data-handling.md`, `security/audit-checklist.md`

---

## 🔗 Useful Links

### Project Information
- [Project Root README](../README.md) - Project overview
- [Project Guidelines](./../.claude/CLAUDE.md) - Coding standards & best practices
- [Project Roadmap](project-info/roadmap.md) - What's planned
- [Contributing Guide](project-info/contributing.md) - How to contribute

### External Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python FastAPI](https://fastapi.tiangolo.com/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [Google Cloud Run](https://cloud.google.com/run/docs)

### Important Files
- `.claude/CLAUDE.md` - Project guidelines, code standards, security rules
- `.claude/skills/` - Claude Code automation skills
- `.env.example` - Environment variable template
- `.gitignore` - Git protection patterns
- `Makefile` - Convenient commands

---

## 🔍 Finding What You Need

### Search Tips

**Looking for API documentation?**
```bash
find docs/api-reference/ -type f -name "*.md"
grep -r "POST /api" docs/
```

**Looking for setup instructions?**
```bash
grep -r "setup\|install\|configure" docs/getting-started/ docs/frontend/ docs/backend/
```

**Looking for security information?**
```bash
find docs/security/ -type f -name "*.md"
grep -r "secret\|password\|auth" docs/security/
```

**Looking for deployment guides?**
```bash
find docs/ -type f -name "*deploy*"
grep -r "deploy\|production\|release" docs/devops/
```

### Document Index by Topic

**Authentication**
- [Clerk Setup](frontend/authentication.md)
- [API Authentication](api-reference/authentication.md)
- [Security Best Practices](security/authentication-security.md)

**Payments**
- [Stripe Integration](frontend/stripe-integration.md)
- [Stripe Webhooks](security/webhook-verification.md)

**Database**
- [Database Schema](architecture/database-schema.md)
- [Database Setup](devops/database-setup.md)
- [Migrations](../docs/database/migrations.md)

**Deployment**
- [Frontend Deployment](frontend/deployment.md)
- [Backend Deployment](backend/deployment.md)
- [GCP Deployment](devops/gcp-deployment.md)

**Testing**
- [Unit Testing](testing/unit-testing.md)
- [E2E Testing](testing/e2e-testing.md)
- [API Testing](testing/api-testing.md)

---

## 📝 Navigation Tips

1. **Each section has a README** - Start with `README.md` in any section for overview
2. **Progressive detail** - Quick summaries first, deep dives available via links
3. **Cross-references** - Related topics linked from each page
4. **Search friendly** - Consistent naming: `topic-subtopic.md`
5. **Archive preserved** - Historical docs in `_archive/` with dates

---

## ❓ Common Questions

**Q: Where do I start if I'm new?**
A: Go to [Getting Started](getting-started/README.md) and follow the quickstart.

**Q: Where are the API docs?**
A: In [API Reference](api-reference/README.md) - organized by endpoint type.

**Q: How do I set up locally?**
A: [Development Setup](getting-started/development-setup.md) has all the steps.

**Q: What are the coding standards?**
A: See `.claude/CLAUDE.md` in the project root.

**Q: Where's the architecture documentation?**
A: [Architecture](architecture/README.md) section covers system design.

**Q: How do I deploy to production?**
A: [DevOps](devops/README.md) section has deployment guides.

**Q: Where are the security guidelines?**
A: [Security](security/README.md) section covers all security topics.

---

## 📊 Documentation Statistics

- **Total sections:** 13
- **Total documents:** 50+ (growing)
- **Total lines:** 10,000+ (and growing)
- **Last updated:** January 22, 2026
- **Status:** Phase 1 Foundation Complete ✓

---

## 🔄 Documentation Maintenance

### How to Keep Docs Current
- Update docs when code changes
- Mark obsolete sections clearly
- Archive completed docs with dates
- Link related documentation
- Use consistent naming conventions

### Contributing to Docs
1. Choose appropriate section
2. Follow existing structure & naming
3. Add front-matter metadata (date, author)
4. Link from related docs
5. Include examples where helpful
6. Update this README if adding new section

### Reporting Issues
Found outdated documentation? Missing content? Broken links?
- File an issue with: section, what's wrong, suggested fix
- Or submit a PR with improvements

---

## 🏠 Back to Project

[← Return to Project Root](../)

---

**Welcome to MCP Finance Documentation!**
Start with your role above, and happy coding! 🚀

*Last Updated: January 22, 2026*
*Documentation organized for clarity, discoverability, and maintainability*
