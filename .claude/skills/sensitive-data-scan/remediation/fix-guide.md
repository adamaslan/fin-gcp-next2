# Security Remediation Guide

This guide provides step-by-step instructions for fixing each type of exposed sensitive data found by the sensitive-data-scan skill.

## Table of Contents

1. [API Keys Remediation](#api-keys-remediation)
2. [Database Credentials](#database-credentials)
3. [PII & Personal Data](#pii--personal-data)
4. [Financial Data](#financial-data)
5. [GCP Resources](#gcp-resources)
6. [Removing from Git History](#removing-from-git-history)
7. [Auditing Unauthorized Access](#auditing-unauthorized-access)

---

## API Keys Remediation

### Google API Keys (Gemini/VertexAI)

**Severity:** 🔴 CRITICAL - Rotate immediately

**Steps:**

1. **Stop the bleeding**
   ```bash
   # Identify all instances
   git log -p -S"AIzaSyArpa-oXY6lWHR3qI5F7hHCMcE2Pny02UU" | head -20
   ```

2. **Rotate the key**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Select your project
   - Find the exposed key
   - Click delete
   - Create new API key:
     - Restrict by IP (add your office/CI/CD IP)
     - Restrict by HTTP referrer if web app
     - Restrict to specific APIs (Gemini only)

3. **Remove from git**
   ```bash
   git rm --cached nu-docs/BACKEND_EXECUTION_REPORT.md
   git commit -m "security: Remove file with exposed Google API key"
   ```

4. **Clean environment**
   ```bash
   # Update .env with new key
   export GOOGLE_API_KEY="AIzaSy[YOUR_NEW_KEY_HERE]"

   # Verify
   python -c "import os; print(os.environ.get('GOOGLE_API_KEY'))"
   ```

5. **Audit logs** (optional, if already pushed)
   - Go to: https://console.cloud.google.com/logs/
   - Search for your old key usage
   - Verify no unauthorized API calls

### Stripe API Keys (Live or Test)

**Severity:** 🔴 CRITICAL - Rotate immediately for live keys, soon for test keys

**Steps:**

1. **Access dashboard**
   - Go to: https://dashboard.stripe.com/apikeys

2. **Delete exposed key**
   - Find the exposed key
   - Click the trash icon
   - Confirm deletion

3. **Create replacement**
   - Click "Create restricted key" or "Create secret key"
   - Select appropriate permissions
   - Choose name (e.g., "Production - API Server")

4. **Update environment**
   ```bash
   # Update .env
   STRIPE_SECRET_KEY="sk_live_[YOUR_NEW_KEY]"
   STRIPE_PUBLISHABLE_KEY="pk_live_[YOUR_NEW_KEY]"
   ```

5. **Notify services**
   - Update all deployed environments
   - Update webhook endpoints if needed
   - Update CI/CD secrets

### OpenAI API Keys

**Severity:** 🔴 CRITICAL - Rotate immediately

**Steps:**

1. **Access API keys**
   - Go to: https://platform.openai.com/api-keys

2. **Revoke exposed key**
   - Find the key
   - Click the trash icon

3. **Create new key**
   - Click "Create new secret key"
   - Name it (e.g., "Production API")
   - Copy immediately (can't see again)

4. **Update environment**
   ```bash
   OPENAI_API_KEY="sk-proj-[YOUR_NEW_KEY]"
   ```

5. **Check usage**
   - Go to: https://platform.openai.com/account/usage/overview
   - Monitor for unusual activity

### GitHub Personal Access Tokens

**Severity:** 🔴 CRITICAL - Rotate immediately

**Steps:**

1. **Revoke token**
   - Go to: https://github.com/settings/tokens
   - Find the token
   - Click "Delete" or "Regenerate"

2. **Create new token**
   - Click "Generate new token" (or classic)
   - Select scopes: `repo`, `workflow` (if needed)
   - Set expiration: 90 days recommended

3. **Update authentication**
   ```bash
   # For gh CLI
   gh auth login

   # For git credentials
   git credential-osxkeychain erase
   # Next git push will prompt for credentials
   ```

### Bearer Tokens & JWT Secrets

**Severity:** 🔴 CRITICAL - Rotate based on scope

**Steps:**

1. **Identify token type**
   - Check what service the token is for
   - Determine scope of access

2. **Revoke if possible**
   - OAuth tokens: Revoke through provider
   - JWT: Shortcut expiration in code
   - API tokens: Delete through service dashboard

3. **Generate replacement**
   - Use service-specific process
   - Update all environments

4. **Invalidate old tokens**
   ```bash
   # Update token blacklist if you maintain one
   # Force logout of all sessions
   ```

---

## Database Credentials

### PostgreSQL/Neon Database Password

**Severity:** 🔴 CRITICAL - Rotate immediately

**Steps:**

1. **Reset password (Neon)**
   - Go to: https://console.neon.tech/
   - Select project
   - Select database branch
   - Click "Connection"
   - Find "Reset password" button
   - Copy new password

2. **Update .env**
   ```bash
   DATABASE_URL=postgresql://[USER]:[NEW_PASSWORD]@[HOST]:5432/[DB]
   ```

3. **Test connection**
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1;"
   ```

4. **Deploy to production**
   - Update production environment variables
   - No restart needed (new connections use new password)
   - Old connections will disconnect when replaced

5. **Verify access**
   ```bash
   # Check logs for successful connections
   tail -f logs/database-connections.log
   ```

### AWS RDS Database Password

**Severity:** 🔴 CRITICAL - Rotate immediately

**Steps:**

1. **Modify database**
   - AWS Console → RDS → Databases
   - Select database
   - Click "Modify"
   - Scroll to "Credentials"
   - Select "Generate new password" or enter custom
   - Apply immediately or during maintenance window

2. **Update connection strings**
   ```bash
   # AWS Secrets Manager (recommended)
   aws secretsmanager put-secret-value \
     --secret-id rds/prod/password \
     --secret-string "[NEW_PASSWORD]"
   ```

3. **Update application**
   - Update .env and environment variables
   - Restart application services
   - Monitor for connection errors

### SSH Keys (Server Access)

**Severity:** 🔴 CRITICAL - Rotate immediately

**Steps:**

1. **Generate new SSH key**
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_new -C "work-key-2025"
   ```

2. **Add new key to servers**
   ```bash
   # If you have SSH access still
   ssh-copy-id -i ~/.ssh/id_ed25519_new.pub user@server
   ```

3. **Remove old key**
   ```bash
   # Connect to each server
   ssh user@server
   # Edit ~/.ssh/authorized_keys
   # Remove the old public key
   ```

4. **Update SSH config**
   ```bash
   # ~/.ssh/config
   Host myserver
       HostName server.example.com
       User ubuntu
       IdentityFile ~/.ssh/id_ed25519_new
   ```

5. **Verify access**
   ```bash
   ssh myserver "echo 'SSH working'"
   ```

---

## PII & Personal Data

### Email Addresses in Code

**Severity:** 🟡 WARNING to 🔴 CRITICAL (context-dependent)

**Remediation:**

- **If in .env.example:** Safe, no action needed
- **If in test data:** Anonymize (replace with test@example.com)
- **If customer data:** Remove immediately, redact from git history

**Steps:**

```bash
# Find all instances
git log -p -S "real.email@company.com" | head -30

# Remove from current files
sed -i 's/real\.email@company\.com/test@example.com/g' filename.txt

# Commit fix
git add filename.txt
git commit -m "security: Anonymize email addresses"
```

### Phone Numbers in Code

**Severity:** 🟡 WARNING to 🔴 CRITICAL

**Steps:**

```bash
# Find instances
git grep -n "555-.*-.*"

# Remove or redact
sed -i 's/[0-9]\{3\}-[0-9]\{3\}-[0-9]\{4\}/555-***-****/g' filename.txt

# Commit
git commit -m "security: Redact phone numbers"
```

### Social Security Numbers

**Severity:** 🔴 CRITICAL - MUST BE REMOVED

**Steps:**

```bash
# Find SSN patterns
git log -p -G "^\s*[0-9]{3}-[0-9]{2}-[0-9]{4}\s*$" | head -50

# Immediate action: Remove files from git history (see "Removing from Git History" section)
```

---

## Financial Data

### Credit Card Numbers

**Severity:** 🔴 CRITICAL - MUST BE REMOVED IMMEDIATELY

**Steps:**

```bash
# Find instances
git log -p -G "[0-9]{4}[ -][0-9]{4}[ -][0-9]{4}[ -][0-9]{4}" | head -20

# MUST use git filter-branch or BFG (see "Removing from Git History")
```

**Preventative:** Never test with real credit cards; use Stripe test mode

### Account Numbers

**Severity:** 🔴 CRITICAL

**Steps:**

```bash
# Find account references
git grep -n "account.*[0-9]\{10,\}" | head -20

# Remove from code/docs
git rm filename.md
git commit -m "security: Remove account numbers from documentation"
```

---

## GCP Resources

### GCP API Keys (AIzaSy...)

**Severity:** 🔴 CRITICAL - Same as Google API Keys

**Steps:**

1. **Rotate**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Delete old key
   - Create new key with IP restrictions

2. **Remove from code**
   ```bash
   git rm --cached files-with-keys
   git commit -m "security: Remove exposed GCP API key"
   ```

### Service Account JSON Files

**Severity:** 🔴 CRITICAL - Full GCP access

**Steps:**

1. **Delete from GCP Console**
   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Select service account
   - Click "Keys" tab
   - Delete the exposed key

2. **Remove from git**
   ```bash
   git rm --cached service-account.json
   git commit -m "security: Remove service account key"
   ```

3. **Audit usage**
   - Check GCP logs for unauthorized access
   - Review IAM activity

4. **Create new key** (if needed)
   - Same location in GCP Console
   - Download immediately
   - Store securely

### GCP Project IDs

**Severity:** 🟡 WARNING to ⚠️ INFO (context-dependent)

**Remediation:**

- Production IDs in public repos: Redact
- Development IDs: Usually OK
- Test IDs: Usually OK

```bash
# If production project exposed in documentation
sed -i 's/my-production-project-123456/[YOUR_PROJECT_ID]/g' docs/*.md
git commit -m "docs: Anonymize GCP project ID"
```

---

## Removing from Git History

### When to Use

Use only if credentials are already pushed to remote and still valid:
- Exposed API keys (pushed to public repo)
- Database passwords (pushed to shared repo)
- OAuth secrets (pushed to any repo)

Do NOT use for:
- Just committed locally (not pushed)
- Already rotated/invalidated keys
- Non-sensitive data

### Option 1: Using BFG Repo-Cleaner (Recommended)

**Installation:**

```bash
# macOS
brew install bfg

# Linux
apt-get install bfg

# Or download from https://rtyley.github.io/bfg-repo-cleaner/
```

**Steps:**

```bash
# 1. Create a mirror clone
git clone --mirror https://github.com/user/repo.git repo.git

# 2. Remove the secret (BFG)
bfg --delete-files AIzaSyArpa-oXY6lWHR3qI5F7hHCMcE2Pny02UU repo.git

# Or replace text
bfg --replace-text passwords.txt repo.git

# 3. Prune the history
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Push the cleaned history (FORCE PUSH - coordinate with team!)
git push --mirror

# 5. Cleanup
cd ..
rm -rf repo.git
```

### Option 2: Using git filter-branch

**Warning:** More complex than BFG; coordinate with team

```bash
# 1. Backup first
git clone . ../backup

# 2. Remove specific file
git filter-branch -f --index-filter \
  'git rm --cached --ignore-unmatch nu-docs/BACKEND_EXECUTION_REPORT.md' \
  -- --all

# 3. Clean up refs
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push (COORDINATE WITH TEAM)
git push --mirror --force
```

### After Cleanup

```bash
# All team members must:
git clone fresh-copy-of-repo
# Or
git fetch origin
git reset --hard origin/main
```

---

## Auditing Unauthorized Access

### Google Cloud

```bash
# View Cloud Audit Logs
# Console: https://console.cloud.google.com/logs/

# Or via gcloud CLI
gcloud logging read "protoPayload.authenticationInfo.principalEmail=exposed-key@project.iam.gserviceaccount.com" \
  --format=json | head -50
```

**What to look for:**
- Unusual API calls
- Access from unexpected IPs
- Off-hours activity
- Permission elevation attempts

### AWS

```bash
# Check CloudTrail
# Console: https://console.aws.amazon.com/cloudtrail/

aws cloudtrail lookup-events \
  --access-key-id AKIA1234567890ABCDEF \
  --start-time 2025-01-01 \
  --end-time 2025-01-22
```

### Database

```bash
# Check recent access logs
psql -c "SELECT * FROM pg_stat_statements ORDER BY query_start DESC LIMIT 20;"

# Or check database logs
tail -n 100 /var/log/postgresql/postgresql.log | grep "authentication"
```

### Git

```bash
# Check git log for suspicious activity
git log --all --pretty=format:"%h %an %ad %s" --date=iso | grep -i "security\|removed\|deleted"

# Check for force pushes
git reflog
```

---

## Post-Remediation Checklist

After fixing any security issue:

- [ ] **Rotated credentials** - New credentials created and working
- [ ] **Updated environments** - All deployments using new credentials
- [ ] **Removed from git** - File removed or git history cleaned
- [ ] **Updated .gitignore** - Path added to prevent future exposure
- [ ] **Audited access logs** - No unauthorized access detected
- [ ] **Notified team** - All developers aware of changes
- [ ] **Documented incident** - Record of what happened and fix
- [ ] **Tested functionality** - Application still working correctly
- [ ] **Updated documentation** - Links and references updated
- [ ] **Monitored for anomalies** - 24-48 hours of additional monitoring

---

## Incident Response Process

### Immediate (Within 1 hour)

1. Rotate all exposed credentials
2. Remove sensitive files from git
3. Update .gitignore
4. Notify team members
5. Start access audit

### Short-term (Within 24 hours)

1. Complete access audit
2. Update all environments
3. Verify no further exposure
4. Document incident
5. Implement preventative measures

### Long-term (Ongoing)

1. Install pre-commit hooks
2. Implement secrets scanning in CI/CD
3. Regular security audits
4. Team training on credential management
5. Credential rotation schedule

---

## Prevention Strategies

### For Development

```bash
# Install pre-commit hook
/sensitive-data-scan --install-hook

# Use environment variables instead of hardcoding
export DATABASE_URL="postgresql://..."

# Use .env files (with .env in .gitignore)
cp .env.example .env
# Edit .env with real values
```

### For CI/CD

```yaml
# GitHub Actions example
- name: Security Scan Before Merge
  run: /sensitive-data-scan --quick --fail-on-critical
```

### For Team

- Use credential management tools (1Password, Vault, etc.)
- Rotate credentials quarterly
- Use least-privilege access
- Enable MFA for all critical services
- Audit access logs weekly

---

## Support & Escalation

For help with remediation:
- Check **sensitive-data-scan** error output
- Review the pattern database in **patterns/** directory
- Follow specific service documentation
- Escalate to security team if major incident

