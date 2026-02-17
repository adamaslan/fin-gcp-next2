# Database Password Rotation Guide

**Status:** This guide is for FUTURE reference only. Current database password is secure (never exposed in git history).

---

## Quick Summary

The database password is stored in `.env` (local only, not committed to git). It's protected by `.gitignore` patterns:
```
.env                    # Local environment variables
.env.*                  # All .env variants
*.local.json            # Local configuration files
```

**If you ever need to rotate the password**, follow the steps below.

---

## When to Rotate

Rotate the database password if:
- 🔴 **CRITICAL:** Password was exposed in git history or logs
- ⚠️ **IMPORTANT:** Employee with access leaves the team
- ⚠️ **IMPORTANT:** Security audit or penetration test finds exposure
- 📅 **ROUTINE:** Quarterly maintenance cycle (enterprise practice)

**Do NOT rotate if:** Password is securely stored locally in `.env` (current state ✓)

---

## Password Rotation Procedure

### Step 1: Generate New Password at Neon Console

1. Go to **https://console.neon.tech/**
2. Log in with your credentials
3. **Select your project** from the dashboard
4. Click **Connection** tab
5. Find **neondb_owner** user
6. Click **Reset password** button
7. **Copy the new password immediately** (you can only see it once)
   - Format: `npg_[40+ alphanumeric characters]`

---

### Step 2: Update Local Environment

```bash
# Option A: Using nano editor
nano .env

# Option B: Using vim
vim .env

# Option C: Direct echo (if .env doesn't exist)
echo "DATABASE_URL=postgresql://neondb_owner:[NEW_PASSWORD]@ep-broad-king-ah18435l-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require" > .env
```

**Replace `[NEW_PASSWORD]` with the password from Step 1**

Expected result in `.env`:
```
DATABASE_URL=postgresql://neondb_owner:npg_XXXXX...@ep-broad-king-ah18435l-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

---

### Step 3: Test the Connection

Choose ONE option to verify:

**Option A: Using psql**
```bash
psql "postgresql://neondb_owner:[NEW_PASSWORD]@ep-broad-king-ah18435l-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require" -c "SELECT version();"
```

**Option B: Using npm (if using Next.js)**
```bash
source .env
npm run db:studio
```

**Option C: Using Python**
```bash
mamba activate fin-ai1
python3 << 'EOF'
import psycopg2
try:
    conn = psycopg2.connect('postgresql://neondb_owner:[NEW_PASSWORD]@ep-broad-king-ah18435l-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require')
    print('✓ Connection successful')
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
EOF
```

**Expected Output:** `✓ Connection successful`

---

### Step 4: Verify .env is Protected

```bash
# Check .gitignore includes .env
grep "^\.env" .gitignore

# Expected output: .env

# Verify file is not tracked
git check-ignore -v .env

# Expected output: .gitignore:8:.env	.env
```

---

### Step 5: Clean Up Secure Information

```bash
# Clear password from clipboard/terminal history
history -c

# Optional: Verify no password in recent commands
history | grep -i password | wc -l
# Should output: 0
```

---

## Rotation Checklist

After completing password rotation:

- [ ] New password generated at Neon console
- [ ] `.env` file updated with new password
- [ ] Connection tested successfully
- [ ] `.env` is in `.gitignore`
- [ ] File is NOT tracked by git
- [ ] Old password cleared from memory
- [ ] Password not present in shell history
- [ ] Verified no exposure in logs

---

## Emergency: If Password Was Exposed

If the password was exposed in git history:

### Immediate Actions (Within 1 hour)
1. **STOP:** Don't commit anything else
2. **Rotate password immediately** (steps above)
3. **Check Neon logs** for unauthorized access
4. **Update all environments** that use this password

### Clean Git History (Within 24 hours)
```bash
# Install BFG (recommended, safer than git filter-branch)
brew install bfg

# Create mirror clone
git clone --mirror https://github.com/user/repo.git repo.git

# Remove the password (replace with actual old password)
bfg --delete-text-passwords repo.git

# Prune history
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Push cleaned history
git push --mirror --force

# Clean up
cd ..
rm -rf repo.git
```

### Team Communication
1. Notify all team members
2. Request fresh clone of repository
3. Confirm everyone has new password in `.env`

---

## Security Best Practices

### Before Each Rotation
- [ ] Verify new password policy compliance
- [ ] Check for other instances of old password (logs, backups)
- [ ] Plan maintenance window if needed
- [ ] Notify team of password change

### After Each Rotation
- [ ] Monitor database logs for 24-48 hours
- [ ] Verify all applications still connect successfully
- [ ] Archive old password securely (if needed for recovery)
- [ ] Document rotation in team records

### Ongoing
- [ ] Rotate passwords quarterly
- [ ] Never share passwords via email/chat
- [ ] Use `.env` files (local only, not committed)
- [ ] Enable database access logging
- [ ] Monitor failed connection attempts

---

## Connection String Reference

### Current Connection Details
```
Database:       neondb
Username:       neondb_owner
Host:          ep-broad-king-ah18435l-pooler.us-east-1.aws.neon.tech
Region:        us-east-1
Port:          5432 (default, can be different for pooler)
SSL:           Required (sslmode=require)
```

### Full Connection String Format
```
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

### Environment Variable Name
```
DATABASE_URL
```

---

## Troubleshooting

### Issue: "Password authentication failed"
**Cause:** Wrong password
**Fix:**
1. Verify password copied correctly from Neon console
2. Check for extra spaces or special characters
3. Reset password again in Neon console

### Issue: "Connection refused"
**Cause:** Can't reach database server
**Fix:**
1. Verify network connectivity: `ping ep-broad-king-ah18435l-pooler.us-east-1.aws.neon.tech`
2. Check Neon console for service status
3. Verify connection string host is correct

### Issue: "SSL certificate problem"
**Cause:** SSL verification failing
**Fix:** Ensure `sslmode=require` is in connection string

### Issue: ".env file not found"
**Cause:** File doesn't exist yet
**Fix:** Create it: `cp .env.example .env` or create manually

---

## Files & Locations

### Local Configuration
- **`.env`** - Your actual database password (NOT in git) ✓
- **`.env.example`** - Template (in git, no real values) ✓
- **`.gitignore`** - Protects `.env` ✓

### If Using `.claude/settings.local.json`
- **`.claude/settings.local.json`** - Local Claude settings (NOT in git) ✓
- **`.claude/*.local.json`** - Protected by `.gitignore` ✓

---

## Quick Reference Commands

```bash
# Test connection
psql "$DATABASE_URL" -c "SELECT 1;"

# Generate new password (Neon console only)
# https://console.neon.tech/ → Connection → Reset password

# Update .env
nano .env

# Verify git protection
git check-ignore .env .env.*

# Clean history (if exposed)
brew install bfg && bfg --delete-text-passwords

# Monitor database
psql "$DATABASE_URL" -c "SELECT datname, usename, application_name FROM pg_stat_activity;"
```

---

## Related Documentation

- [`.claude/CLAUDE.md`](/.claude/CLAUDE.md) - Project security guidelines
- [`.env.example`](/.env.example) - Environment variable template
- [`.gitignore`](/.gitignore) - Files protected from git
- [Neon Documentation](https://neon.tech/docs) - Database provider docs
- [`SECURITY_CONCERNS.md`](./SECURITY_CONCERNS.md) - Security analysis

---

## When NOT to Use This Guide

- ✗ If password is already securely protected in `.env`
- ✗ If no exposure has occurred
- ✗ If database is test-only with no sensitive data

**Current Status:** Password is SECURE ✓
Only use this guide if you need to rotate for routine maintenance or if a security incident occurs.

---

**Created:** January 22, 2026
**Updated:** January 22, 2026
**Status:** Ready for future reference
