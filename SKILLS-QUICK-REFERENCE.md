# Claude Skills Quick Reference Card

**One-page reference for the most common skills and hooks in MCP Finance**

---

## Essential Skills

### Authentication & User Management
```bash
/clerk-signup     # Complete user signup flow
/clerk-signin     # User authentication
/user-profile     # View/edit user profile
/reset-password   # Password reset flow
```

### Development Workflow
```bash
/dev-setup        # Initialize development environment
/test-all         # Run complete test suite
/build-deploy     # Build and deploy to production
/db-migrate       # Run database migrations
```

### Database Operations
```bash
/db-query         # Query database with SQL
/db-seed          # Seed development data
/db-backup        # Backup database
/db-reset         # Reset to clean state
```

### API & Integration
```bash
/api-test         # Test API endpoints
/webhook-setup    # Configure webhooks
/mcp-check        # Check MCP server status
/api-generate     # Generate API documentation
```

---

## Quick Hooks Reference

### Pre-Tool Hooks (Before Actions)
- **pre-bash**: Validate commands before execution
- **pre-edit**: Backup files before changes
- **pre-write**: Check permissions before creating files
- **pre-git**: Verify branch before git operations

### Post-Tool Hooks (After Actions)
- **post-bash**: Log command execution
- **post-edit**: Auto-format modified files
- **post-write**: Trigger build/test on file creation
- **post-git**: Notify team on push

### Event Hooks
- **on-test-fail**: Auto-debug failed tests
- **on-build-error**: Analyze build errors
- **on-deploy-success**: Send notifications
- **on-error**: Capture and log errors

---

## Skill Composition Patterns

### Pattern 1: Development Workflow
```
/dev-setup → /db-migrate → /db-seed → /test-all
```

### Pattern 2: API Development
```
/api-generate → /api-test → /api-document → /deploy-api
```

### Pattern 3: Feature Development
```
/feature-branch → /scaffold-component → /write-tests → /review-code
```

### Pattern 4: Debugging
```
/check-logs → /run-diagnostics → /fix-errors → /verify-fix
```

---

## Common Skill Arguments

### User Management
```bash
/clerk-signup --email user@example.com --password secure123
/user-profile --user-id abc123 --update-field email
```

### Database
```bash
/db-query --sql "SELECT * FROM users WHERE active=true"
/db-migrate --version 20240115
/db-seed --env development
```

### Testing
```bash
/test-all --coverage --watch
/test-unit --file authentication.test.ts
/test-e2e --browser chrome
```

### Deployment
```bash
/build-deploy --env production --region us-west-2
/rollback --version v1.2.3
```

---

## Webhook Quick Config

### Setup Pattern
```json
{
  "event": "user.created",
  "url": "https://api.example.com/webhooks/clerk",
  "secret": "${CLERK_WEBHOOK_SECRET}",
  "active": true
}
```

### Common Events
- `user.created` - New user registration
- `user.updated` - Profile changes
- `session.created` - User login
- `transaction.completed` - Payment processed
- `alert.triggered` - Price alert fired

---

## Pro Tips

### 1. Chain Skills with &&
```bash
/db-migrate && /db-seed && /test-all
```

### 2. Use Subskills for Complex Workflows
```bash
/deploy:build → /deploy:test → /deploy:push → /deploy:notify
```

### 3. Create Project-Specific Shortcuts
```bash
/daily - Runs: git pull, npm install, db-migrate, test-all
/ship - Runs: test-all, build-deploy, notify-team
```

### 4. Debug with Verbose Mode
```bash
/test-all --verbose --no-cache
```

### 5. Use Hooks for Auto-Documentation
```bash
post-edit: "generate-docs --file $FILE"
```

---

## Environment-Specific Skills

### Development
- `/mock-data` - Generate test data
- `/reset-dev` - Reset to clean state
- `/hot-reload` - Enable live reloading

### Staging
- `/smoke-test` - Run smoke tests
- `/load-test` - Performance testing
- `/staging-deploy` - Deploy to staging

### Production
- `/health-check` - System health status
- `/rollback` - Emergency rollback
- `/scale` - Scale resources

---

## Skill Categories by Role

### Frontend Developer
- `/component-generate`
- `/style-audit`
- `/a11y-check`
- `/ui-test`

### Backend Developer
- `/api-generate`
- `/db-migrate`
- `/cache-clear`
- `/perf-profile`

### DevOps
- `/deploy`
- `/monitor`
- `/backup`
- `/scale`

### QA/Testing
- `/test-all`
- `/coverage-report`
- `/e2e-test`
- `/perf-test`

---

## Integration Patterns

### Clerk + Database
```
/clerk-signup → [webhook] → /user-create-db → /send-welcome-email
```

### Stripe + Notifications
```
/payment-process → [webhook] → /update-subscription → /notify-user
```

### CI/CD Pipeline
```
[git push] → /run-tests → /build → /deploy → /notify-slack
```

---

## Keyboard Shortcuts

When using Claude Code CLI:
- `/` - Start skill command
- `Tab` - Auto-complete skill name
- `Up/Down` - Navigate skill history
- `Ctrl+C` - Cancel skill execution
- `Ctrl+D` - Exit skill mode

---

## Error Handling

### Common Issues
1. **Skill Not Found**: Check spelling, use Tab completion
2. **Permission Denied**: Verify environment variables and secrets
3. **Timeout**: Use `--timeout 300` for longer operations
4. **Rate Limited**: Add delays with `--throttle 1000ms`

### Debug Commands
```bash
/skill-list          # Show all available skills
/skill-info <name>   # Get skill details
/skill-validate      # Check skill configuration
/hook-list          # Show active hooks
```

---

## Best Practices

✅ **DO:**
- Use descriptive skill names
- Chain related operations
- Set up error hooks
- Document custom skills
- Version control skill definitions

❌ **DON'T:**
- Hard-code secrets in skills
- Skip validation in pre-hooks
- Ignore error states
- Create overly complex chains
- Bypass security checks

---

## Quick Setup Checklist

```bash
□ Install dependencies: npm install
□ Set environment variables in .env.local
□ Configure Claude CLI: claude-code init
□ Load skill definitions: claude-code skills load
□ Set up hooks: claude-code hooks enable
□ Test basic skill: /health-check
□ Configure webhooks in dashboard
□ Run smoke test: /smoke-test
```

---

## Resources

- **Full Guide**: See `GUIDE-ENHANCED.md`
- **Skill Reference**: See `SKILLS-REFERENCE.md`
- **Hook Documentation**: See `nextjs-mcp-finance/docs/`
- **API Docs**: `http://localhost:3000/api-docs`
- **Claude Code Docs**: `https://docs.anthropic.com/claude/docs/claude-code`

---

## Support

**Issues?**
1. Check skill logs: `/logs --skill <name>`
2. Validate config: `/skill-validate`
3. Review error output
4. Check GitHub issues
5. Ask Claude for help: "Debug my skill setup"

---

**Version**: 1.0.0
**Last Updated**: January 2024
**Project**: MCP Finance with Claude Skills Integration
