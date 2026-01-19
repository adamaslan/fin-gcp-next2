# Claude Skills - How-To Guide

**Practical guide for creating, using, and managing Claude Skills in your project**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Skill](#creating-your-first-skill)
3. [Skill Anatomy](#skill-anatomy)
4. [Advanced Skill Patterns](#advanced-skill-patterns)
5. [Hook Integration](#hook-integration)
6. [Testing Skills](#testing-skills)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What Are Claude Skills?

Claude Skills are reusable commands that automate common development tasks. They're like bash aliases on steroids - they can:
- Execute complex multi-step workflows
- Use context from your codebase
- Handle errors intelligently
- Chain together with other skills
- Integrate with webhooks and external services

### Prerequisites

```bash
# Install Claude Code CLI
npm install -g @anthropic/claude-code

# Initialize in your project
claude-code init

# Verify installation
claude-code --version
```

---

## Creating Your First Skill

### Step 1: Create the Skill File

Create a new file: `.claude/skills/hello-world.json`

```json
{
  "name": "hello-world",
  "description": "A simple hello world skill",
  "version": "1.0.0",
  "command": "echo 'Hello from Claude Skills!'",
  "category": "example"
}
```

### Step 2: Register the Skill

```bash
claude-code skills load .claude/skills/
```

### Step 3: Use the Skill

In Claude Code:
```
/hello-world
```

**Output:**
```
Hello from Claude Skills!
```

---

## Skill Anatomy

### Basic Skill Structure

```json
{
  "name": "skill-name",
  "description": "What this skill does",
  "version": "1.0.0",
  "author": "Your Name",
  "category": "development|database|api|testing|deployment",

  "command": "npm test",

  "parameters": [
    {
      "name": "file",
      "description": "File to test",
      "required": false,
      "default": "all"
    }
  ],

  "environment": {
    "NODE_ENV": "test",
    "CI": "true"
  },

  "pre_hooks": ["backup", "validate"],
  "post_hooks": ["notify", "cleanup"],

  "timeout": 30000,
  "retry": {
    "attempts": 3,
    "delay": 1000
  }
}
```

### Multi-Step Skills

```json
{
  "name": "deploy-app",
  "description": "Deploy application to production",
  "steps": [
    {
      "name": "test",
      "command": "npm test",
      "on_failure": "abort"
    },
    {
      "name": "build",
      "command": "npm run build",
      "on_failure": "abort"
    },
    {
      "name": "deploy",
      "command": "vercel --prod",
      "on_failure": "rollback"
    },
    {
      "name": "notify",
      "command": "node scripts/notify-team.js",
      "on_failure": "continue"
    }
  ]
}
```

---

## Advanced Skill Patterns

### Pattern 1: Conditional Execution

```json
{
  "name": "smart-test",
  "description": "Run tests based on changed files",
  "steps": [
    {
      "name": "detect-changes",
      "command": "git diff --name-only HEAD~1",
      "output_to": "CHANGED_FILES"
    },
    {
      "name": "test-frontend",
      "command": "npm run test:frontend",
      "condition": "CHANGED_FILES contains 'src/components'"
    },
    {
      "name": "test-backend",
      "command": "npm run test:backend",
      "condition": "CHANGED_FILES contains 'src/api'"
    },
    {
      "name": "test-all",
      "command": "npm run test:all",
      "condition": "CHANGED_FILES contains 'package.json'"
    }
  ]
}
```

### Pattern 2: Parallel Execution

```json
{
  "name": "parallel-checks",
  "description": "Run multiple checks in parallel",
  "parallel": true,
  "steps": [
    {
      "name": "lint",
      "command": "npm run lint"
    },
    {
      "name": "type-check",
      "command": "npm run type-check"
    },
    {
      "name": "security-scan",
      "command": "npm audit"
    }
  ]
}
```

### Pattern 3: Interactive Skills

```json
{
  "name": "create-component",
  "description": "Create a new React component with tests",
  "interactive": true,
  "steps": [
    {
      "name": "prompt-name",
      "prompt": "Component name:",
      "output_to": "COMPONENT_NAME"
    },
    {
      "name": "prompt-type",
      "prompt": "Component type (functional/class):",
      "options": ["functional", "class"],
      "output_to": "COMPONENT_TYPE"
    },
    {
      "name": "generate",
      "command": "node scripts/generate-component.js $COMPONENT_NAME $COMPONENT_TYPE"
    },
    {
      "name": "create-test",
      "command": "node scripts/generate-test.js $COMPONENT_NAME"
    }
  ]
}
```

### Pattern 4: Database Migration Skill

```json
{
  "name": "db-migrate",
  "description": "Run database migrations safely",
  "steps": [
    {
      "name": "backup",
      "command": "pg_dump $DATABASE_URL > backup-$(date +%Y%m%d-%H%M%S).sql"
    },
    {
      "name": "check-pending",
      "command": "npm run db:migrate:status",
      "output_to": "MIGRATION_STATUS"
    },
    {
      "name": "confirm",
      "prompt": "Found pending migrations. Continue?",
      "type": "confirm",
      "condition": "MIGRATION_STATUS contains 'pending'"
    },
    {
      "name": "migrate",
      "command": "npm run db:migrate:up"
    },
    {
      "name": "verify",
      "command": "npm run db:verify"
    }
  ],
  "on_failure": {
    "command": "npm run db:migrate:down",
    "message": "Migration failed! Rolling back..."
  }
}
```

---

## Hook Integration

### What Are Hooks?

Hooks are functions that run before or after skill execution. They enable:
- Validation and safety checks
- Logging and monitoring
- Cleanup operations
- Integration with external services

### Creating a Pre-Hook

Create `.claude/hooks/pre-deploy.js`:

```javascript
module.exports = async (context) => {
  const { skill, parameters, env } = context;

  // Check if tests have passed
  const testsPass = await runTests();
  if (!testsPass) {
    throw new Error('Tests must pass before deployment');
  }

  // Check if on correct branch
  const branch = await getCurrentBranch();
  if (branch !== 'main') {
    const confirm = await prompt('Not on main branch. Continue?');
    if (!confirm) {
      throw new Error('Deployment cancelled');
    }
  }

  // Log deployment attempt
  await logDeployment({
    user: env.USER,
    timestamp: new Date().toISOString(),
    branch: branch
  });

  return { allowed: true };
};
```

Register in skill:
```json
{
  "name": "deploy",
  "pre_hooks": ["pre-deploy"]
}
```

### Creating a Post-Hook

Create `.claude/hooks/post-deploy.js`:

```javascript
module.exports = async (context) => {
  const { skill, result, duration, env } = context;

  // Send notification
  await sendSlackNotification({
    message: `🚀 Deployment complete in ${duration}ms`,
    user: env.USER,
    status: result.success ? 'success' : 'failed'
  });

  // Update deployment dashboard
  await updateDashboard({
    timestamp: new Date(),
    version: result.version,
    status: result.success ? 'live' : 'failed'
  });

  // Create GitHub deployment
  if (result.success) {
    await createGitHubDeployment({
      ref: await getCurrentCommit(),
      environment: 'production',
      description: `Deployed by ${env.USER}`
    });
  }
};
```

### Error Hook

Create `.claude/hooks/on-error.js`:

```javascript
module.exports = async (context) => {
  const { skill, error, parameters } = context;

  // Log detailed error
  console.error({
    skill: skill.name,
    error: error.message,
    stack: error.stack,
    parameters,
    timestamp: new Date().toISOString()
  });

  // Send alert
  await sendErrorAlert({
    title: `Skill Error: ${skill.name}`,
    message: error.message,
    severity: 'high'
  });

  // Create GitHub issue for recurring errors
  const errorCount = await getErrorCount(skill.name, error.message);
  if (errorCount > 3) {
    await createGitHubIssue({
      title: `[Auto] Recurring error in ${skill.name}`,
      body: `Error occurred ${errorCount} times:\n\n${error.message}\n\n${error.stack}`,
      labels: ['bug', 'auto-generated']
    });
  }
};
```

---

## Subskills

### What Are Subskills?

Subskills are modular components that can be reused across multiple skills.

### Creating a Subskill

Create `.claude/skills/test.subskill.json`:

```json
{
  "name": "test",
  "type": "subskill",
  "variants": {
    "unit": {
      "command": "npm run test:unit",
      "description": "Run unit tests"
    },
    "integration": {
      "command": "npm run test:integration",
      "description": "Run integration tests"
    },
    "e2e": {
      "command": "npm run test:e2e",
      "description": "Run end-to-end tests"
    },
    "all": {
      "command": "npm test",
      "description": "Run all tests"
    }
  }
}
```

### Using Subskills

```json
{
  "name": "pre-commit",
  "steps": [
    { "subskill": "test:unit" },
    { "subskill": "lint" },
    { "command": "git add -A" },
    { "command": "git commit" }
  ]
}
```

---

## Real-World Examples

### Example 1: Feature Branch Workflow

```json
{
  "name": "feature-start",
  "description": "Start working on a new feature",
  "parameters": [
    {
      "name": "feature-name",
      "description": "Name of the feature",
      "required": true
    }
  ],
  "steps": [
    {
      "name": "pull-latest",
      "command": "git checkout main && git pull origin main"
    },
    {
      "name": "create-branch",
      "command": "git checkout -b feature/$FEATURE_NAME"
    },
    {
      "name": "update-deps",
      "command": "npm install"
    },
    {
      "name": "db-migrate",
      "subskill": "db:migrate"
    },
    {
      "name": "run-tests",
      "subskill": "test:all"
    },
    {
      "name": "open-editor",
      "command": "code ."
    }
  ]
}
```

Usage:
```
/feature-start --feature-name user-authentication
```

### Example 2: API Development Workflow

```json
{
  "name": "api-develop",
  "description": "Complete API development workflow",
  "parameters": [
    {
      "name": "endpoint",
      "description": "API endpoint name",
      "required": true
    }
  ],
  "steps": [
    {
      "name": "generate-route",
      "command": "node scripts/generate-api-route.js $ENDPOINT"
    },
    {
      "name": "generate-tests",
      "command": "node scripts/generate-api-tests.js $ENDPOINT"
    },
    {
      "name": "update-docs",
      "command": "node scripts/generate-api-docs.js"
    },
    {
      "name": "run-tests",
      "command": "npm run test:api -- $ENDPOINT"
    },
    {
      "name": "start-dev",
      "command": "npm run dev",
      "background": true
    },
    {
      "name": "test-endpoint",
      "command": "curl http://localhost:3000/api/$ENDPOINT",
      "delay": 3000
    }
  ]
}
```

### Example 3: Database Workflow

```json
{
  "name": "db-workflow",
  "description": "Complete database development workflow",
  "steps": [
    {
      "name": "create-migration",
      "prompt": "Migration name:",
      "output_to": "MIGRATION_NAME"
    },
    {
      "name": "generate-migration",
      "command": "npm run db:migration:create -- $MIGRATION_NAME"
    },
    {
      "name": "edit-migration",
      "prompt": "Edit migration file now? (y/n)",
      "output_to": "EDIT_NOW"
    },
    {
      "name": "open-editor",
      "command": "code migrations/$(ls -t migrations | head -1)",
      "condition": "EDIT_NOW == 'y'"
    },
    {
      "name": "pause",
      "prompt": "Press enter when ready to run migration",
      "type": "pause"
    },
    {
      "name": "run-migration",
      "command": "npm run db:migrate:up"
    },
    {
      "name": "verify",
      "command": "npm run db:verify"
    },
    {
      "name": "seed-test-data",
      "prompt": "Seed test data? (y/n)",
      "output_to": "SEED_DATA"
    },
    {
      "name": "seed",
      "command": "npm run db:seed",
      "condition": "SEED_DATA == 'y'"
    }
  ]
}
```

---

## Testing Skills

### Unit Test Your Skills

Create `.claude/skills/test-skill.sh`:

```bash
#!/bin/bash

# Test skill execution
test_skill() {
  local skill_name=$1

  echo "Testing skill: $skill_name"

  # Run skill in test mode
  output=$(claude-code skill run "$skill_name" --dry-run 2>&1)
  exit_code=$?

  if [ $exit_code -eq 0 ]; then
    echo "✓ $skill_name passed"
    return 0
  else
    echo "✗ $skill_name failed"
    echo "$output"
    return 1
  fi
}

# Test all skills
for skill in .claude/skills/*.json; do
  skill_name=$(basename "$skill" .json)
  test_skill "$skill_name"
done
```

### Integration Testing

```javascript
// tests/skills.test.js
const { executeSkill } = require('@anthropic/claude-code');

describe('Skills Integration', () => {
  test('deploy skill executes all steps', async () => {
    const result = await executeSkill('deploy', {
      dryRun: true,
      env: 'staging'
    });

    expect(result.steps).toHaveLength(4);
    expect(result.steps[0].name).toBe('test');
    expect(result.steps[1].name).toBe('build');
  });

  test('db-migrate skill handles errors', async () => {
    const result = await executeSkill('db-migrate', {
      dryRun: true,
      simulateError: true
    });

    expect(result.success).toBe(false);
    expect(result.rolledBack).toBe(true);
  });
});
```

---

## Troubleshooting

### Common Issues

#### 1. Skill Not Found
```bash
# List all skills
claude-code skills list

# Reload skills
claude-code skills reload

# Check skill path
claude-code config get skills-path
```

#### 2. Permission Denied
```bash
# Make skill executable
chmod +x .claude/skills/my-skill.sh

# Check file permissions
ls -la .claude/skills/
```

#### 3. Environment Variables Not Set
```json
{
  "name": "my-skill",
  "environment": {
    "DATABASE_URL": "${DATABASE_URL}",
    "API_KEY": "${API_KEY}"
  },
  "validate_env": ["DATABASE_URL", "API_KEY"]
}
```

#### 4. Hook Errors
```bash
# Debug hook execution
claude-code hooks debug my-hook

# Disable hook temporarily
claude-code hooks disable my-hook

# Check hook logs
claude-code logs hooks
```

### Debug Mode

Run skills with verbose logging:
```bash
claude-code skill run deploy --debug --verbose
```

### Skill Validation

Validate skill configuration:
```bash
claude-code skills validate .claude/skills/deploy.json
```

---

## Best Practices

### 1. Name Skills Clearly
```
✅ deploy-production
✅ test-frontend
✅ db-migrate-up

❌ deploy
❌ test
❌ migrate
```

### 2. Add Descriptive Documentation
```json
{
  "name": "deploy-production",
  "description": "Deploy application to production with tests and rollback",
  "usage": "/deploy-production [--skip-tests]",
  "examples": [
    "/deploy-production",
    "/deploy-production --skip-tests"
  ]
}
```

### 3. Handle Errors Gracefully
```json
{
  "steps": [
    {
      "name": "critical-step",
      "command": "npm test",
      "on_failure": "abort",
      "error_message": "Tests failed! Fix errors before deploying."
    },
    {
      "name": "optional-step",
      "command": "npm run lint",
      "on_failure": "continue",
      "error_message": "Lint warnings detected (non-blocking)"
    }
  ]
}
```

### 4. Use Timeouts
```json
{
  "steps": [
    {
      "name": "long-running-task",
      "command": "npm run build",
      "timeout": 300000,
      "timeout_message": "Build timed out after 5 minutes"
    }
  ]
}
```

### 5. Document Dependencies
```json
{
  "name": "deploy",
  "dependencies": {
    "tools": ["git", "npm", "vercel"],
    "env_vars": ["VERCEL_TOKEN", "DATABASE_URL"],
    "services": ["postgres", "redis"]
  }
}
```

---

## Next Steps

1. **Start Simple**: Create basic skills for your daily tasks
2. **Add Hooks**: Implement safety checks and logging
3. **Create Subskills**: Build reusable components
4. **Test Thoroughly**: Write tests for critical skills
5. **Share with Team**: Document and version control your skills

---

## Resources

- **Full Guide**: `GUIDE-ENHANCED.md`
- **Quick Reference**: `SKILLS-QUICK-REFERENCE.md`
- **Skills Reference**: `SKILLS-REFERENCE.md`
- **Claude Code Docs**: https://docs.anthropic.com/claude/docs/claude-code
- **Examples**: `.claude/skills/examples/`

---

**Happy Automating! 🚀**
