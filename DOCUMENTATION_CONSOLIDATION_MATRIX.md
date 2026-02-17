# Documentation Consolidation Matrix
## Quick Reference - Which Files to Keep, Consolidate, or Archive

**Purpose:** Visual reference for where each of the 128 documentation files should go

---

## Quick Navigation

- [Root Level (24 files)](#root-level-files)
- [Backend Documentation](#backend-documentation)
- [Frontend Documentation](#frontend-documentation)
- [DevOps & Infrastructure](#devops--infrastructure)
- [Tools & Automation](#tools--automation)
- [Internal (.claude/)](#internal-claude-directory)
- [To Archive](#to-archive)
- [Consolidation Instructions](#consolidation-instructions)

---

## ROOT LEVEL FILES

### 24 Files Currently at Root - PROBLEM!

#### Setup & Getting Started (3 files → CONSOLIDATE)
```
❌ DEV-SETUP-USAGE.md (437 lines)
❌ DEV-SETUP-SKILL-SUMMARY.md (466 lines)
❌ BACKEND-SETUP-COMPLETE.md (446 lines)
         ↓
✅ NEW: docs/GETTING-STARTED.md (consolidate all 3)
```

**Action:** Create single comprehensive guide covering:
- Prerequisites and requirements
- Quick start (5 min)
- Frontend setup
- Backend setup
- Database setup
- Verification checks

**Deprecate:** Archive the 3 original files after consolidation

---

#### Main Guides (2 files → CONSOLIDATE)
```
❌ GUIDE.md (612 lines)
❌ GUIDE-ENHANCED.md (1,017 lines)
         ↓
✅ KEEP: docs/README.md (reference both as "See also")
✅ NEW: docs/ARCHITECTURE.md (moved from GUIDE-ENHANCED)
```

**Action:**
- Determine which is most current (GUIDE or GUIDE-ENHANCED?)
- Keep the better one as `docs/README.md` main guide
- Extract architecture sections into `docs/ARCHITECTURE.md`
- Archive the other version

**Decision needed:** Are both versions needed or can one be archived?

---

#### Backend Execution (3 files → CONSOLIDATE)
```
❌ QUICK_START_BETA1.md (117 lines)
❌ GUIDE_TO_BACKEND_EXECUTION.md (nu-docs/, ~400 lines)
❌ BACKEND_EXECUTION_RUNBOOK.md (nu-docs/, ~400 lines)
         ↓
✅ NEW: docs/backend/EXECUTION.md
✅ NEW: docs/backend/BETA1.md
```

**Action:**
- Create `docs/backend/EXECUTION.md` - general backend execution
- Create `docs/backend/BETA1.md` - beta1 specific procedures
- Archive originals after content migration

**Content mapping:**
- GUIDE_TO_BACKEND_EXECUTION.md → docs/backend/EXECUTION.md (main)
- QUICK_START_BETA1.md → docs/backend/BETA1.md (quick reference)
- BACKEND_EXECUTION_RUNBOOK.md → docs/backend/EXECUTION.md (merge)

---

#### Deployment (6 files → CONSOLIDATE)
```
❌ DEPLOYMENT-QUICKSTART.md (cloud-run/docs/, ~250 lines)
❌ DEPLOYMENT-README.md (cloud-run/docs/, ~300 lines)
❌ DEPLOYMENT-SETUP-REVIEW.md (cloud-run/docs/, ~250 lines)
❌ DEPLOYMENT-REVIEW-SUMMARY.md (cloud-run/docs/, ~250 lines)
❌ DEPLOYMENT-LOG-TEMPLATE.md (cloud-run/docs/, ~100 lines)
❌ RUN_BETA1_LOCALLY.md (cloud-run/docs/, ~400 lines - actually execution)
         ↓
✅ NEW: docs/DEPLOYMENT.md (general deployment)
✅ NEW: docs/devops/CLOUD-RUN.md (Cloud Run specific)
✅ NEW: docs/backend/BETA1.md (beta1 execution - move here)
```

**Action:**
- Create `docs/DEPLOYMENT.md` - deployment overview & general procedures
- Create `docs/devops/CLOUD-RUN.md` - Google Cloud Run specific
- Move `RUN_BETA1_LOCALLY.md` content to `docs/backend/BETA1.md`
- Archive all 6 original files

**Content mapping:**
- DEPLOYMENT-README.md → docs/DEPLOYMENT.md (main)
- DEPLOYMENT-QUICKSTART.md → docs/DEPLOYMENT.md (quick section)
- DEPLOYMENT-SETUP-REVIEW.md → docs/devops/CLOUD-RUN.md (prereqs)
- DEPLOYMENT-LOG-TEMPLATE.md → templates/deployment-log.md (if needed)
- Others → Archive

---

#### Environment & Mamba (2 files at root → CONSOLIDATE)
```
❌ MAMBA-AND-DOCKER-SECURITY-UPDATE.md (402 lines)
❌ (+ 2 more in other directories)
         ↓
✅ NEW: docs/devops/ENVIRONMENT.md (consolidated)
```

**Action:** Create single environment guide combining:
- Mamba first philosophy
- fin-ai1 environment setup
- Docker security
- Activation procedures
- Troubleshooting

**Files to consolidate:**
- MAMBA-AND-DOCKER-SECURITY-UPDATE.md (root)
- MAMBA_FIN_AI1_RULES.md (nu-docs/)
- ENVIRONMENT-SETUP.md (cloud-run/docs/)

---

#### Skills Documentation (5 files → CONSOLIDATE)
```
❌ claude-skills-how-to.md (830 lines)
❌ SKILLS-REFERENCE.md (911 lines)
❌ SKILLS-QUICK-REFERENCE.md (321 lines)
❌ SKILLS-AND-HOOKS-SUMMARY.md (634 lines)
❌ .claude/skills/README.md (~100 lines)
         ↓
✅ NEW: docs/tools/SKILLS.md (comprehensive)
✅ ARCHIVE: docs/tools/SKILLS-QUICK-REFERENCE.md (if needed)
```

**Action:**
- Create `docs/tools/SKILLS.md` as comprehensive reference
- Include quick reference table (from SKILLS-QUICK-REFERENCE.md)
- Archive other 4 versions after migration
- Keep `.claude/skills/` structure unchanged (internal tooling)

**Content hierarchy:**
- Level 1: Skills overview + table (from SKILLS-QUICK-REFERENCE.md)
- Level 2: Individual skill details (from SKILLS-REFERENCE.md)
- Level 3: Creating custom skills (from claude-skills-how-to.md)
- Level 4: Hooks system (from SKILLS-AND-HOOKS-SUMMARY.md)

---

#### Reference & Guides (4 files)
```
✅ STOCK_UNIVERSE_UPDATE.md → docs/reference/STOCK-UNIVERSE.md
❌ SECURITY_CONCERNS.md → Integrate into docs/SECURITY.md (new)
❓ TOOLING-SUMMARY.md → Review: still current?
❓ FILE_REORGANIZATION_PLAN.md → This is a meta-doc, archive after implementing
```

**Action:**
- Move STOCK_UNIVERSE_UPDATE.md to docs/reference/
- Merge SECURITY_CONCERNS.md into new docs/SECURITY.md with remediations
- Review TOOLING-SUMMARY.md for content value
- Archive FILE_REORGANIZATION_PLAN.md after this restructuring is complete

---

#### Status/Temporal Markers (5 files → ARCHIVE) ⚠️ CRITICAL
```
❌ IMPLEMENTATION_COMPLETE.md (466 lines)
❌ REORGANIZATION_COMPLETE.md (276 lines)
❌ BACKEND_IMPLEMENTATION_COMPLETE.md (289 lines)
❌ BACKEND-SETUP-COMPLETE.md (446 lines)
❌ SCRIPT_EXECUTION_REPORT.md (671 lines - also test output)
         ↓
🗂️ ARCHIVE: archive/temporal-markers/
📌 REPLACEMENT: Use git tags (git tag v0.1-setup-complete)
```

**Action:**
- These serve no documentation purpose
- Move to archive/ directory
- Use git tags for version marking instead
- Delete after 30 days if not referenced

**Why archive?**
- They're timestamps, not living documentation
- Create noise and confusion
- Suggest completion when work is ongoing
- Git already tracks completion via commits/tags

---

#### Test Reports (4 files → MOVE TO reports/)
```
❌ ENVIRONMENT_TEST_REPORT.md (845 lines)
❌ SHELL_CONFIG_REPORT.md (313 lines)
❌ MAMBA_ACTIVATION_DIAGNOSTIC.md (249 lines)
❌ EXECUTION_METHODS_SUMMARY.md (164 lines)
❌ + More in backend_test_results/
         ↓
📊 MOVE TO: reports/ directory
📅 RENAME: reports/2026-01-22-environment-test.md
```

**Action:**
- Create `reports/` directory in root
- Move all test output with date prefix: `YYYY-MM-DD-name.md`
- Create `reports/archive/` for reports older than 30 days
- Update git to ignore old reports

**Benefit:**
- Keeps documentation clean
- Easy to find latest test run
- Can quickly clean up old reports
- Doesn't clutter permanent documentation

---

#### Misc/Undocumented (1 file)
```
❓ things.md (18 lines - unclear purpose)
```

**Action:** Review and either:
- Move to `archive/misc/` if historical interest
- Delete if obsolete
- Move to issue tracker if tasks

---

## BACKEND DOCUMENTATION

### Current locations:
```
- Root: BACKEND_IMPLEMENTATION_COMPLETE.md (to archive)
- Root: QUICK_START_BETA1.md (to consolidate)
- nu-docs/: BACKEND_EXECUTION_REPORT.md
- nu-docs/: BACKEND_EXECUTION_RUNBOOK.md
- nu-docs/: GUIDE_TO_BACKEND_EXECUTION.md
- cloud-run/docs/: BETA1-SCAN-GUIDE.md
- cloud-run/docs/: RUN_BETA1_LOCALLY.md
- cloud-run/docs/: Various deployment docs
```

### New structure:
```
✅ docs/backend/SETUP.md
   ├─ Backend development environment setup
   ├─ Python 3.11 installation
   ├─ fin-ai1 environment creation
   └─ Dependency installation

✅ docs/backend/EXECUTION.md
   ├─ Running backend server
   ├─ Available API endpoints
   ├─ Stock analysis features
   ├─ Running scans and retrieving results
   └─ Troubleshooting

✅ docs/backend/BETA1.md
   ├─ What is Beta1 scan
   ├─ Prerequisites
   ├─ Running locally (RUN_BETA1_LOCALLY.md content)
   ├─ Quick start methods (QUICK_START_BETA1.md content)
   └─ Interpretation of results

✅ docs/backend/ANALYSIS.md (NEW)
   ├─ Technical analysis implementation
   ├─ Available indicators
   ├─ Custom analysis setup
   └─ Performance metrics
```

---

## FRONTEND DOCUMENTATION

### Current locations:
```
- nextjs-mcp-finance/docs/: CLAUDE_DEVELOPMENT_GUIDE.md
- nextjs-mcp-finance/docs/: clerk-* (4 Clerk-specific docs)
- nextjs-mcp-finance/docs/: FRONTEND_BACKEND_CONNECTION.md
- nextjs-mcp-finance/docs/: START-HERE.md
- nextjs-mcp-finance/docs/: README-CLERK-SKILL.md
```

### New structure:
```
✅ docs/frontend/README.md
   ├─ Frontend overview
   ├─ Technology stack (Next.js 16, React 19, TailwindCSS)
   └─ Quick start

✅ docs/frontend/SETUP.md
   ├─ Node.js requirements
   ├─ Next.js project setup
   ├─ Dependencies installation
   ├─ Environment variables
   └─ Running development server

✅ docs/frontend/AUTH.md
   ├─ Clerk authentication integration
   ├─ Setup instructions (consolidate clerk-* docs)
   ├─ Sign-up flow
   ├─ Login flow
   ├─ Logout and session management
   └─ Testing authentication

✅ docs/frontend/API-INTEGRATION.md
   ├─ Connecting to backend MCP server
   ├─ Available endpoints
   ├─ Request/response examples
   ├─ Error handling
   └─ Testing API integration

✅ docs/frontend/COMPONENTS.md (NEW)
   ├─ Core components overview
   ├─ Component patterns
   ├─ Props and usage
   └─ Examples

✅ docs/frontend/STYLING.md (NEW)
   ├─ TailwindCSS configuration
   ├─ Design system
   ├─ Theme variables
   └─ Accessibility guidelines
```

---

## DEVOPS & INFRASTRUCTURE

### Current locations:
```
- Root: MAMBA-AND-DOCKER-SECURITY-UPDATE.md
- Root: SECURITY_CONCERNS.md (isolated)
- cloud-run/docs/: DOCKER-SECURITY-SETUP.md
- cloud-run/docs/: ENVIRONMENT-SETUP.md
- cloud-run/docs/: DEPLOYMENT-* (5 files)
- nu-docs/: MAMBA_FIN_AI1_RULES.md
```

### New structure:
```
✅ docs/devops/ENVIRONMENT.md
   ├─ Mamba first philosophy (from MAMBA-AND-DOCKER-SECURITY-UPDATE.md)
   ├─ fin-ai1 environment setup
   ├─ Dependency management
   ├─ Docker & containerization
   ├─ fin-ai1 rules and standards
   └─ Troubleshooting activation

✅ docs/devops/DOCKER.md (NEW)
   ├─ Docker setup
   ├─ Security best practices
   ├─ Image optimization
   ├─ Non-root users
   ├─ Building images
   └─ Docker compose setup

✅ docs/devops/CLOUD-RUN.md
   ├─ Google Cloud Run overview
   ├─ Deployment process
   ├─ Environment configuration
   ├─ Monitoring and logging
   ├─ Scaling and performance
   └─ Troubleshooting

✅ docs/DEPLOYMENT.md
   ├─ Deployment overview
   ├─ Deployment strategies
   ├─ Pre-deployment checklist
   ├─ Rollback procedures
   └─ References to cloud-run/devops specific docs

✅ docs/SECURITY.md (NEW)
   ├─ Project security standards
   ├─ Integration of SECURITY_CONCERNS.md audit findings
   ├─ Remediation steps for 7 critical issues
   ├─ Best practices for secrets management
   ├─ Compliance checklist
   └─ Security review checklist

✅ docs/devops/MONITORING.md (NEW)
   ├─ Health checks
   ├─ Logging strategy
   ├─ Metrics and alerts
   ├─ Error tracking
   └─ Performance monitoring
```

---

## TOOLS & AUTOMATION

### Current locations:
```
- Root: claude-skills-how-to.md
- Root: SKILLS-REFERENCE.md
- Root: SKILLS-QUICK-REFERENCE.md
- Root: SKILLS-AND-HOOKS-SUMMARY.md
- Root: TOOLING-SUMMARY.md
- .claude/CLAUDE.md
- .claude/skills/README.md
- .claude/commands/: 5 command docs
```

### New structure:
```
✅ docs/tools/SKILLS.md
   ├─ Skills overview and philosophy
   ├─ Quick reference table (from SKILLS-QUICK-REFERENCE.md)
   ├─ Available skills with descriptions
   ├─ Using skills (syntax, arguments, examples)
   ├─ Creating custom skills (from claude-skills-how-to.md)
   ├─ Hooks system (from SKILLS-AND-HOOKS-SUMMARY.md)
   ├─ Best practices
   └─ Examples and workflows

✅ docs/tools/COMMANDS.md (NEW)
   ├─ Available Claude commands
   ├─ Each command with arguments and usage
   ├─ Examples
   ├─ Output interpretation
   └─ Troubleshooting

✅ docs/tools/HOOKS.md (NEW)
   ├─ Skill hooks system
   ├─ Hook types and lifecycle
   ├─ Creating hooks
   ├─ Examples
   └─ Best practices

✅ .claude/ (KEEP AS-IS)
   ├─ CLAUDE.md - project guidelines
   ├─ commands/ - command implementations
   ├─ skills/ - skill implementations
   └─ settings.local.json - local settings
```

**Note:** Keep .claude/ structure unchanged - it's internal tooling configuration

---

## INTERNAL (.claude/ DIRECTORY)

### Status: ✅ KEEP AS-IS (Well-organized)

```
.claude/
├── CLAUDE.md (18.2 KB)
│   ├─ MCP Finance project guidelines
│   ├─ Technology stack
│   ├─ Code standards (TypeScript, React, Python)
│   ├─ Database standards (Drizzle ORM)
│   ├─ Authentication (Clerk)
│   ├─ Payment (Stripe)
│   ├─ API design
│   ├─ Testing
│   ├─ Git workflow
│   ├─ Security & sensitive data
│   └─ Python backend guidelines with Mamba rules
│
├── commands/ (5 command definitions)
│   ├─ db-migrate.md → Drizzle ORM migrations
│   ├─ db-seed.md → Seed test data
│   ├─ health-check.md → System health
│   ├─ mcp-check.md → MCP server status
│   └─ test-all.md → Run complete test suite
│
└── skills/
    ├─ README.md → Skills system overview
    ├─ api-test/ → API testing skill
    ├─ code-review/ → Code review skill
    ├─ deployment-checklist/ → Deployment verification
    ├─ docker-security/ → Docker security
    ├─ sensitive-data-scan/ → Credential detection (with patterns/)
    ├─ sensitive-doc-creator/ → Safe documentation creation
    ├─ dev-setup.md → Development setup
    ├─ dev-setup.json → Skill configuration
    └─ claude-tooling-guide.md → How to use Claude tooling
```

**Action:** No changes needed. This structure is appropriate for internal configuration.

---

## TO ARCHIVE

### Archive Directory Structure:
```
archive/
├── README.md (explains what's archived and why)
├── temporal-markers/
│   ├─ IMPLEMENTATION_COMPLETE.md
│   ├─ REORGANIZATION_COMPLETE.md
│   ├─ BACKEND_IMPLEMENTATION_COMPLETE.md
│   └─ BACKEND-SETUP-COMPLETE.md
│
├── test-outputs/
│   ├─ ENVIRONMENT_TEST_REPORT.md
│   ├─ SHELL_CONFIG_REPORT.md
│   ├─ MAMBA_ACTIVATION_DIAGNOSTIC.md
│   ├─ EXECUTION_METHODS_SUMMARY.md
│   └─ SCRIPT_EXECUTION_REPORT.md
│
├── legacy-features/
│   ├─ FIBONACCI_IMPLEMENTATION_SUMMARY.md
│   ├─ FIBONACCI_TEST_CHECKLIST.md
│   ├─ FIBONACCI_TEST_VALIDATION_REPORT.md
│   └─ FINAL_TEST_DELIVERY_SUMMARY.txt
│
├── planning/
│   ├─ NEXTJS_4_TIER_DASHBOARD_PLAN.md
│   ├─ NEXTJS_INTEGRATION_PLAN.md
│   └─ FILE_REORGANIZATION_PLAN.md (after implemented)
│
├── orphaned/
│   ├─ nu-docs/ (entire directory if confirmed as legacy)
│   ├─ things.md
│   └─ REPO_DOCUMENTATION.md
│
└── old-reports/
    ├─ BACKEND_EXECUTION_REPORT.md
    ├─ TEST_SUITE_README.md (if outdated)
    └─ AI_OPTIMIZATIONS.md (if outdated)
```

---

## CONSOLIDATION INSTRUCTIONS

### How to Execute Consolidation

#### Step 1: Create New Directory Structure
```bash
mkdir -p docs/{frontend,backend,devops,tools,reference}
mkdir -p reports/archive
mkdir -p archive/{temporal-markers,test-outputs,legacy-features,planning,orphaned}
```

#### Step 2: Move Files (In This Order)

**Frontend:**
```bash
mv nextjs-mcp-finance/docs/START-HERE.md docs/frontend/README.md
mv nextjs-mcp-finance/docs/FRONTEND_BACKEND_CONNECTION.md docs/frontend/API-INTEGRATION.md
# Consolidate Clerk docs into one
cat nextjs-mcp-finance/docs/clerk-*.md > docs/frontend/AUTH.md
```

**Backend:**
```bash
# Consolidate execution guides
cat GUIDE_TO_BACKEND_EXECUTION.md BACKEND_EXECUTION_RUNBOOK.md > docs/backend/EXECUTION.md
mv QUICK_START_BETA1.md docs/backend/BETA1.md
mv cloud-run/docs/RUN_BETA1_LOCALLY.md >> docs/backend/BETA1.md
```

**DevOps:**
```bash
# Consolidate environment setup
cat MAMBA-AND-DOCKER-SECURITY-UPDATE.md cloud-run/docs/ENVIRONMENT-SETUP.md > docs/devops/ENVIRONMENT.md
mv MAMBA_FIN_AI1_RULES.md >> docs/devops/ENVIRONMENT.md
mv cloud-run/docs/DOCKER-SECURITY-SETUP.md docs/devops/DOCKER.md
```

**Tools:**
```bash
# Consolidate skills documentation
cat claude-skills-how-to.md SKILLS-REFERENCE.md SKILLS-QUICK-REFERENCE.md SKILLS-AND-HOOKS-SUMMARY.md > docs/tools/SKILLS.md
```

**Reference:**
```bash
mv STOCK_UNIVERSE_UPDATE.md docs/reference/STOCK-UNIVERSE.md
# Create new files
cat SECURITY_CONCERNS.md > docs/SECURITY.md  # Then add remediation content
```

**Reports:**
```bash
mv ENVIRONMENT_TEST_REPORT.md reports/2026-01-22-environment-test.md
mv SHELL_CONFIG_REPORT.md reports/2026-01-22-shell-config.md
# And others...
```

**Archive:**
```bash
mv IMPLEMENTATION_COMPLETE.md archive/temporal-markers/
mv REORGANIZATION_COMPLETE.md archive/temporal-markers/
mv FIBONACCI_*.md archive/legacy-features/
mv NEXTJS_*.md archive/planning/
mv nu-docs archive/
```

#### Step 3: Create New Documentation Files

```bash
# Create root entry point
touch README.md  # Add main documentation entry point

# Create documentation index
touch docs/README.md  # Document index

# Create missing documentation
touch docs/ARCHITECTURE.md
touch docs/GETTING-STARTED.md (consolidate 3 setup guides)
touch docs/API.md
touch docs/DATABASE.md
touch docs/TESTING.md
touch docs/CONTRIBUTING.md
touch docs/TROUBLESHOOTING.md
touch docs/frontend/COMPONENTS.md
touch docs/frontend/STYLING.md
touch docs/devops/CLOUD-RUN.md
touch docs/devops/MONITORING.md
touch docs/tools/COMMANDS.md
touch docs/tools/HOOKS.md
touch docs/reference/ENVIRONMENT-VARS.md
touch docs/reference/GLOSSARY.md
```

#### Step 4: Update References

```bash
# Find all references to moved files
grep -r "SKILLS-REFERENCE.md" .
grep -r "GUIDE.md" .
grep -r "DEPLOYMENT.md" .
# Update to new locations
```

#### Step 5: Update git
```bash
git add docs/ reports/ archive/
git rm SKILLS-REFERENCE.md GUIDE.md IMPLEMENTATION_COMPLETE.md  # etc
git commit -m "docs: reorganize documentation structure

- Create docs/ directory with hierarchical structure
- Consolidate duplicate setup guides (3 → 1)
- Consolidate skills documentation (5 → 1)
- Consolidate deployment guides (6 → 2)
- Archive temporal markers and legacy content
- Move test reports to dated reports/ directory
- Create missing documentation (architecture, API, database, testing)

Documentation now follows:
docs/
├── Getting Started & Architecture
├── frontend/ - Frontend-specific
├── backend/ - Backend-specific
├── devops/ - Operations & infrastructure
├── tools/ - Claude tooling
└── reference/ - Technical references

This improves discoverability and reduces redundancy."
```

---

## Summary Table: Where Everything Goes

| Current Location | Current Filename | New Location | New Filename | Action |
|-----------------|-----------------|--------------|-------------|--------|
| Root | GUIDE.md | docs/ | README.md | Consolidate |
| Root | GUIDE-ENHANCED.md | docs/ | ARCHITECTURE.md (extract) | Consolidate |
| Root | DEV-SETUP-USAGE.md | docs/ | GETTING-STARTED.md | Consolidate |
| Root | DEV-SETUP-SKILL-SUMMARY.md | docs/ | GETTING-STARTED.md | Consolidate |
| Root | BACKEND-SETUP-COMPLETE.md | docs/ | GETTING-STARTED.md | Consolidate |
| Root | QUICK_START_BETA1.md | docs/backend/ | BETA1.md | Move |
| nu-docs | GUIDE_TO_BACKEND_EXECUTION.md | docs/backend/ | EXECUTION.md | Move |
| nu-docs | BACKEND_EXECUTION_RUNBOOK.md | docs/backend/ | EXECUTION.md | Merge |
| cloud-run/docs | RUN_BETA1_LOCALLY.md | docs/backend/ | BETA1.md | Merge |
| cloud-run/docs | DEPLOYMENT-README.md | docs/ | DEPLOYMENT.md | Move |
| cloud-run/docs | DEPLOYMENT-QUICKSTART.md | docs/ | DEPLOYMENT.md | Merge |
| cloud-run/docs | Multiple DEPLOYMENT-*.md | docs/devops/ | CLOUD-RUN.md | Consolidate |
| Root | MAMBA-AND-DOCKER-SECURITY-UPDATE.md | docs/devops/ | ENVIRONMENT.md | Move |
| nu-docs | MAMBA_FIN_AI1_RULES.md | docs/devops/ | ENVIRONMENT.md | Merge |
| cloud-run/docs | ENVIRONMENT-SETUP.md | docs/devops/ | ENVIRONMENT.md | Merge |
| Cloud-run/docs | DOCKER-SECURITY-SETUP.md | docs/devops/ | DOCKER.md | Move |
| Root | claude-skills-how-to.md | docs/tools/ | SKILLS.md | Consolidate |
| Root | SKILLS-REFERENCE.md | docs/tools/ | SKILLS.md | Consolidate |
| Root | SKILLS-QUICK-REFERENCE.md | docs/tools/ | SKILLS.md | Consolidate |
| Root | SKILLS-AND-HOOKS-SUMMARY.md | docs/tools/ | SKILLS.md | Consolidate |
| Root | SECURITY_CONCERNS.md | docs/ | SECURITY.md | Merge+Enhance |
| Root | STOCK_UNIVERSE_UPDATE.md | docs/reference/ | STOCK-UNIVERSE.md | Move |
| Root | TOOLING-SUMMARY.md | docs/tools/ | Reference/Archive | Review |
| nextjs-mcp-finance/docs | START-HERE.md | docs/frontend/ | README.md | Move |
| nextjs-mcp-finance/docs | clerk-*.md (4 files) | docs/frontend/ | AUTH.md | Consolidate |
| nextjs-mcp-finance/docs | FRONTEND_BACKEND_CONNECTION.md | docs/frontend/ | API-INTEGRATION.md | Move |
| Root | IMPLEMENTATION_COMPLETE.md | archive/temporal-markers/ | IMPLEMENTATION_COMPLETE.md | Archive |
| Root | REORGANIZATION_COMPLETE.md | archive/temporal-markers/ | REORGANIZATION_COMPLETE.md | Archive |
| Root | BACKEND_IMPLEMENTATION_COMPLETE.md | archive/temporal-markers/ | BACKEND_IMPLEMENTATION_COMPLETE.md | Archive |
| Root | BACKEND-SETUP-COMPLETE.md | archive/temporal-markers/ | BACKEND-SETUP-COMPLETE.md | Archive |
| Root | ENVIRONMENT_TEST_REPORT.md | reports/ | 2026-01-22-environment-test.md | Archive |
| Root | SHELL_CONFIG_REPORT.md | reports/ | 2026-01-22-shell-config.md | Archive |
| Root | MAMBA_ACTIVATION_DIAGNOSTIC.md | reports/ | 2026-01-22-mamba-diagnostic.md | Archive |
| Root | EXECUTION_METHODS_SUMMARY.md | reports/ | 2026-01-22-execution-methods.md | Archive |
| Root | SCRIPT_EXECUTION_REPORT.md | reports/ | 2026-01-22-script-execution.md | Archive |
| Root | FIBONACCI_*.md (4 files) | archive/legacy-features/ | Same | Archive |
| mcp-finance1/docs | NEXTJS_*.md (2 files) | archive/planning/ | Same | Archive |
| nu-docs | Entire directory | archive/ | nu-docs/ | Archive |
| Root | things.md | archive/orphaned/ | things.md | Archive |
| Root | FILE_REORGANIZATION_PLAN.md | archive/planning/ | FILE_REORGANIZATION_PLAN.md | Archive (after implemented) |

---

## Validation Checklist

After consolidation, verify:

- [ ] `docs/README.md` exists and lists all documentation
- [ ] New developer can find GETTING-STARTED.md in < 10 seconds
- [ ] All 24 root files are either consolidated, moved, or archived
- [ ] No duplicate documentation remains in separate locations
- [ ] All internal links updated to point to new locations
- [ ] No broken links in documentation
- [ ] `reports/` directory exists with dated test files
- [ ] `archive/` directory exists with all deprecated docs
- [ ] `.claude/` directory structure unchanged
- [ ] git status is clean (all files tracked or ignored)
- [ ] Documentation builds successfully (if using doc generator)
- [ ] Team can find any documentation in < 2 minutes

---

**Next Steps:** Execute Phase 1-2 of the implementation plan from the detailed strategy document.
