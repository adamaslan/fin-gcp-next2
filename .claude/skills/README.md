# Claude Skills Directory

This directory contains Claude Skills definitions for automating common tasks in the MCP Finance project.

## What Are Skills?

Skills are reusable automation commands that you can invoke in Claude Code using the `/skill-name` syntax. They automate complex, multi-step workflows with proper error handling, logging, and rollback capabilities.

## Available Skills

### `/dev-setup`
Complete development environment initialization.

**Usage:**
```bash
/dev-setup
/dev-setup --skip-install
/dev-setup --skip-db
```

**What it does:**
1. Checks for required tools (Node.js, Python, PostgreSQL)
2. Installs frontend dependencies (Next.js, React, etc.)
3. Installs backend dependencies (Python packages)
4. Sets up environment configuration files
5. Installs Playwright browsers for E2E testing
6. Tests database connection
7. Runs database migrations
8. Verifies the complete setup

**When to use:**
- First time setting up the project
- After cloning the repository
- When resetting your development environment
- When onboarding new team members

## How to Use Skills

### In Claude Code CLI

Simply type the skill name with a forward slash:
```
/dev-setup
```

With parameters:
```
/dev-setup --skip-install
```

### Direct Script Execution

You can also run the helper scripts directly:
```bash
bash scripts/dev-setup.sh
bash scripts/dev-setup.sh --verbose
bash scripts/dev-setup.sh --skip-install --skip-db
```

## Creating New Skills

### Basic Skill Structure

Create a new JSON file in this directory:

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "What this skill does",
  "category": "development|testing|deployment|database",

  "parameters": [
    {
      "name": "param-name",
      "description": "Parameter description",
      "type": "string|boolean|number",
      "required": false,
      "default": "default-value"
    }
  ],

  "steps": [
    {
      "name": "step-name",
      "description": "What this step does",
      "command": "command to run",
      "on_failure": "abort|continue|warn",
      "timeout": 30000
    }
  ]
}
```

### Skill Properties

- **name**: Unique identifier for the skill (use kebab-case)
- **version**: Semantic version (e.g., "1.0.0")
- **description**: Clear explanation of what the skill does
- **category**: Group similar skills together
- **parameters**: Optional command-line arguments
- **steps**: Array of sequential commands to execute
- **environment**: Environment variables to set
- **pre_hooks**: Hooks to run before execution
- **post_hooks**: Hooks to run after execution
- **on_failure**: Global failure handling strategy

### Step Properties

- **name**: Step identifier
- **description**: What this step does
- **command**: Shell command to execute
- **condition**: Optional condition to check before running
- **timeout**: Maximum execution time in milliseconds
- **on_failure**: How to handle step failure (abort/continue/warn)
- **error_message**: Custom error message

## Best Practices

### 1. Clear Naming
Use descriptive, action-oriented names:
- ✅ `deploy-production`
- ✅ `test-frontend`
- ❌ `deploy`
- ❌ `test`

### 2. Proper Error Handling
Always specify what should happen on failure:
```json
{
  "on_failure": "abort",
  "error_message": "Tests failed! Fix errors before deploying."
}
```

### 3. Reasonable Timeouts
Set appropriate timeouts for long-running operations:
```json
{
  "command": "npm install",
  "timeout": 300000
}
```

### 4. Use Conditions
Skip unnecessary steps with conditions:
```json
{
  "command": "npm test",
  "condition": "!skip-tests"
}
```

### 5. Informative Messages
Provide clear feedback to users:
```json
{
  "success_message": "✅ Deployment complete!",
  "error_message": "❌ Deployment failed. Check logs above."
}
```

## Environment Variables

Skills can access environment variables:

```json
{
  "environment": {
    "NODE_ENV": "test",
    "DATABASE_URL": "${DATABASE_URL}"
  }
}
```

## Hooks

Add pre and post execution hooks:

```json
{
  "pre_hooks": ["validate-environment"],
  "post_hooks": ["notify-team", "update-dashboard"]
}
```

## Testing Skills

Test your skills before committing:

```bash
# Validate skill JSON
claude-code skills validate .claude/skills/my-skill.json

# Test skill execution
claude-code skills test my-skill

# Debug skill
claude-code skills run my-skill --debug
```

## Common Patterns

### Pattern 1: Multi-Environment Skill
```json
{
  "parameters": [
    {
      "name": "env",
      "options": ["development", "staging", "production"],
      "default": "development"
    }
  ],
  "steps": [
    {
      "command": "deploy-to-${env}.sh"
    }
  ]
}
```

### Pattern 2: Conditional Steps
```json
{
  "steps": [
    {
      "name": "test",
      "command": "npm test",
      "condition": "!skip-tests"
    },
    {
      "name": "deploy",
      "command": "deploy.sh",
      "condition": "test.success"
    }
  ]
}
```

### Pattern 3: Parallel Execution
```json
{
  "parallel": true,
  "steps": [
    { "command": "npm run lint" },
    { "command": "npm run type-check" },
    { "command": "npm run test:unit" }
  ]
}
```

## Troubleshooting

### Skill Not Found
```bash
# Reload skills
claude-code skills reload

# List available skills
claude-code skills list
```

### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Environment Variables Not Set
```bash
# Check environment
claude-code config env

# Set required variables in .env.local files
```

## Resources

- **How-To Guide**: `claude-skills-how-to.md`
- **Quick Reference**: `SKILLS-QUICK-REFERENCE.md`
- **Full Skills Reference**: `SKILLS-REFERENCE.md`
- **Enhanced Guide**: `GUIDE-ENHANCED.md`

## Contributing

When adding new skills:

1. Create skill JSON file in this directory
2. Add corresponding script in `scripts/` directory (if needed)
3. Test thoroughly with `--debug` flag
4. Update this README with skill documentation
5. Add examples to `SKILLS-REFERENCE.md`

## Support

If you encounter issues:
1. Check skill syntax with `claude-code skills validate`
2. Run with `--debug` flag for detailed output
3. Review logs in `.claude/logs/`
4. Check `claude-skills-how-to.md` for troubleshooting tips

---

**Version**: 1.0.0
**Last Updated**: January 2024
**Maintainer**: MCP Finance Team
