---
name: db-migrate
description: Run database migrations safely with backup and rollback capability for PostgreSQL with Drizzle ORM
---

Run database migrations safely for MCP Finance. This command includes backup, migration, and verification steps.

## Prerequisites Check

First, verify the environment is ready:

```bash
# Check PostgreSQL is running
pg_isready || echo "⚠️ PostgreSQL not running"

# Check DATABASE_URL is set
cd nextjs-mcp-finance
node -e "console.log(process.env.DATABASE_URL ? '✓ DATABASE_URL set' : '✗ DATABASE_URL not set')"
```

**If DATABASE_URL not set:**
- Check `.env.local` file exists
- Ensure DATABASE_URL is defined
- Format: `postgresql://user:password@localhost:5432/mcp_finance`

## Step 1: Create Backup

Create a timestamped backup before migrating:

```bash
BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).sql"
pg_dump $DATABASE_URL > "../backups/$BACKUP_FILE" 2>/dev/null || mkdir -p ../backups && pg_dump $DATABASE_URL > "../backups/$BACKUP_FILE"
echo "✓ Backup created: backups/$BACKUP_FILE"
```

**Why backup?**
- Migrations can fail
- Data could be corrupted
- Provides rollback option

## Step 2: Check Migration Status

See what migrations are pending:

```bash
npx drizzle-kit status
```

**Output interpretation:**
- "No migrations found" = Schema is up to date
- Lists pending migrations = Need to apply
- "Schema drift detected" = Local schema differs from database

## Step 3: Generate Migration (if schema changed)

If you modified the schema files, generate migration:

```bash
npx drizzle-kit generate
```

**This creates:**
- New migration file in `drizzle/` directory
- SQL statements to apply changes
- Timestamp-prefixed filename

**Review the generated migration:**
```bash
ls -lt drizzle/*.sql | head -1
cat $(ls -t drizzle/*.sql | head -1)
```

**Check for:**
- DROP TABLE statements (are they intentional?)
- Data loss operations
- Complex alterations

## Step 4: Apply Migrations

Push the schema changes to the database:

```bash
npx drizzle-kit push
```

**What this does:**
- Applies pending migrations
- Updates database schema
- Creates/modifies tables
- Adds indexes

**During migration:**
- Watch for errors
- Don't interrupt the process
- Note any warnings

## Step 5: Verify Migration

Confirm the migration succeeded:

```bash
# Check database connection
node -e "const { drizzle } = require('drizzle-orm/postgres-js'); const postgres = require('postgres'); const sql = postgres(process.env.DATABASE_URL); const db = drizzle(sql); db.execute('SELECT NOW()').then(() => console.log('✓ Database accessible')).catch(e => console.error('✗ Database error:', e.message)).finally(() => sql.end());"
```

**Manual verification:**
```bash
# Open Drizzle Studio to inspect
npx drizzle-kit studio
```

This opens a web UI at http://localhost:4983 to browse your database.

## Step 6: Test with Sample Query

Run a simple query to ensure tables exist:

```bash
node -e "const { drizzle } = require('drizzle-orm/postgres-js'); const postgres = require('postgres'); const sql = postgres(process.env.DATABASE_URL); const db = drizzle(sql); db.execute('SELECT * FROM users LIMIT 1').then(() => console.log('✓ Tables accessible')).catch(e => console.error('⚠️ Query failed:', e.message)).finally(() => sql.end());"
```

## Rollback (if migration failed)

If something went wrong, restore from backup:

```bash
# List available backups
ls -lh ../backups/

# Restore latest backup (CAUTION: This overwrites current database)
LATEST_BACKUP=$(ls -t ../backups/*.sql | head -1)
echo "Restoring from: $LATEST_BACKUP"
psql $DATABASE_URL < $LATEST_BACKUP

echo "✓ Database restored"
```

## Common Issues & Solutions

### "Error: relation already exists"
- Schema is already up to date
- Or conflicting migration
- **Solution**: Check `drizzle-kit status` and review generated migrations

### "Error: column does not exist"
- Breaking change in migration
- **Solution**: Write custom migration to handle data transformation

### "Connection timeout"
- PostgreSQL not running
- **Solution**: Start PostgreSQL
  - macOS: `brew services start postgresql`
  - Linux: `sudo systemctl start postgresql`

### "Permission denied"
- Database user lacks privileges
- **Solution**: Grant permissions:
  ```sql
  GRANT ALL PRIVILEGES ON DATABASE mcp_finance TO your_user;
  ```

### "Syntax error in migration"
- Generated migration has issues
- **Solution**: Manually edit migration file in `drizzle/` directory

## Migration Best Practices

### Before Migrating
- ✅ Review generated migration files
- ✅ Test migrations in development first
- ✅ Backup database
- ✅ Notify team if in production

### During Migration
- ✅ Watch for errors
- ✅ Don't interrupt the process
- ✅ Keep terminal output for logs

### After Migration
- ✅ Verify application still works
- ✅ Test critical features
- ✅ Check for data loss
- ✅ Run test suite: `/test-all`

## Production Migration Checklist

For production migrations, follow these additional steps:

1. **Test in staging first**
   ```bash
   DATABASE_URL=$STAGING_DATABASE_URL npx drizzle-kit push
   ```

2. **Schedule maintenance window** (if needed)
   - For breaking changes
   - For large data migrations

3. **Create production backup**
   ```bash
   pg_dump $PRODUCTION_DATABASE_URL > prod-backup-$(date +%Y%m%d-%H%M%S).sql
   ```

4. **Apply migration**
   ```bash
   DATABASE_URL=$PRODUCTION_DATABASE_URL npx drizzle-kit push
   ```

5. **Verify immediately**
   - Check application health
   - Monitor error rates
   - Test critical flows

6. **Have rollback plan ready**
   - Keep backup accessible
   - Know rollback commands
   - Have team on standby

## Success Indicators

Migration succeeded if:
- ✅ No errors during `drizzle-kit push`
- ✅ Database connection works
- ✅ Sample queries succeed
- ✅ Application starts without errors
- ✅ Tests pass: `/test-all`

## Next Steps

After successful migration:
1. Commit migration files to git
2. Update team in Slack/Discord
3. Deploy application (migrations auto-run)
4. Monitor for issues

---

**Remember**: Always backup before migrating, especially in production!
