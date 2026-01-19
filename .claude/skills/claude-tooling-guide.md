---
name: claude-tooling-guide
description: Guide for creating Claude Code tooling including Skills, hooks, subagents, slash commands, CLAUDE.md, and MCP servers. Use when the user wants to create or customize Claude Code functionality, automation, or integrations.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

When helping users create Claude Code tooling, first understand what they want to accomplish, then guide them to the right solution:

## Decision Tree: Which Tool Should I Create?

Ask these questions to determine the right approach:

### 1. When should this run?
- **User types a command** → Slash command
- **Automatically when relevant** → Skill
- **On every conversation** → CLAUDE.md
- **On file/tool events** → Hook
- **When Claude needs external data/tools** → MCP server
- **Complex task needing isolation** → Subagent

### 2. Quick Reference Table

| Use Case | Solution | Example |
|----------|----------|---------|
| "Always use TypeScript strict mode" | CLAUDE.md | Project-wide coding standards |
| "Review PRs using our standards" | Skill | Automated code review guidance |
| "Type /deploy to deploy to staging" | Slash command | Reusable deployment command |
| "Lint files after I edit them" | Hook | Auto-format on save |
| "Let Claude query our database" | MCP server | External data access |
| "Explore codebase separately" | Subagent | Isolated exploration context |

## Creating Skills

Skills teach Claude specialized knowledge that applies automatically when relevant.

### Analogy
Think of Skills like **expert consultants**. You don't call them directly - they show up automatically when their expertise is needed. If you're discussing database design, your database architect (Skill) automatically joins the conversation.

### Skill Structure
```
skill-name/
├── SKILL.md              # Required: Main skill file
├── reference.md          # Optional: Detailed documentation
├── examples.md           # Optional: Usage examples
└── scripts/
    └── helper.py         # Optional: Utility scripts
```

### SKILL.md Template
```yaml
---
name: your-skill-name
description: What this does and WHEN to use it. Include trigger keywords users would say.
allowed-tools: Read, Write, Edit  # Optional: Restrict tools
model: claude-sonnet-4-20250514   # Optional: Specific model
context: fork                      # Optional: Run in isolated context
agent: general-purpose             # Optional: Which subagent type (if context: fork)
user-invocable: true              # Optional: Show in slash menu (default: true)
---

# Your Skill Name

## When to use this skill
List specific scenarios and trigger phrases.

## Step-by-step instructions
1. First, do this...
2. Then, check that...
3. Finally, verify...

## Examples
Show concrete usage examples.

## Common issues
- Issue 1: Solution
- Issue 2: Solution
```

### Key Principles for Skills

1. **Description is critical**: Claude uses it to decide when to trigger
   - ❌ Bad: "Helps with code"
   - ✅ Good: "Reviews Python code for PEP 8 compliance, type hints, and security issues. Use when reviewing Python files or when user mentions code review, linting, or Python best practices."

2. **Progressive disclosure**: Keep SKILL.md focused, put details in separate files
   - `SKILL.md`: Overview, when to use, quick instructions (< 500 lines)
   - `reference.md`: Complete API docs, detailed examples
   - `scripts/`: Utility scripts Claude can execute

3. **Link supporting files**: Claude discovers files through links
   ```markdown
   For complete API details, see [reference.md](reference.md)
   To validate input, run: `python scripts/validate.py input.txt`
   ```

4. **Use allowed-tools for safety**: Restrict capabilities
   ```yaml
   allowed-tools: Read, Grep, Glob  # Read-only operations
   ```

### Skill Locations
- **Personal** (~/.claude/skills/): Available across all your projects
- **Project** (.claude/skills/): Shared with team via git
- **Enterprise**: Managed by admin
- **Plugin**: Bundled in plugins

## Creating Hooks

Hooks run scripts automatically on events (file edits, tool calls, etc.).

### Analogy
Hooks are like **automatic triggers** - motion sensor lights that turn on when you enter a room. You don't tell them to run; they react to events.

### Hook Types
1. **PreToolUse**: Run BEFORE a tool executes (validation, backups)
2. **PostToolUse**: Run AFTER a tool executes (formatting, notifications)
3. **Stop**: Run when conversation/skill ends (cleanup)

### Hook Configuration (.claude/settings.json or settings.local.json)

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": "Edit",
      "hooks": [
        {
          "type": "command",
          "command": "npx prettier --write $FILE_PATH",
          "name": "format-on-edit"
        }
      ]
    },
    {
      "event": "PreToolUse",
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "./scripts/validate-command.sh '$TOOL_INPUT'",
          "name": "validate-bash",
          "once": true
        }
      ]
    }
  ]
}
```

### Available Variables
- `$FILE_PATH`: Path to file being edited
- `$TOOL_INPUT`: Input passed to the tool
- `$TOOL_OUTPUT`: Output from the tool (PostToolUse only)
- `$TOOL_NAME`: Name of tool being used
- `${CLAUDE_SESSION_ID}`: Current session ID

### Common Hook Patterns

**Auto-format on save:**
```json
{
  "event": "PostToolUse",
  "matcher": "Edit",
  "hooks": [
    {
      "type": "command",
      "command": "npm run format $FILE_PATH"
    }
  ]
}
```

**Backup before editing:**
```json
{
  "event": "PreToolUse",
  "matcher": "Edit",
  "hooks": [
    {
      "type": "command",
      "command": "cp $FILE_PATH $FILE_PATH.backup"
    }
  ]
}
```

**Run tests after code changes:**
```json
{
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "npm test",
      "background": true
    }
  ]
}
```

## Creating Slash Commands

Slash commands are reusable prompts you invoke explicitly with `/command`.

### Analogy
Slash commands are like **speed dial** - you explicitly press the button to call a specific person. Type `/deploy` and Claude follows your deployment script.

### Location
`.claude/commands/` (project) or `~/.claude/commands/` (personal)

### Command Structure
```yaml
---
name: deploy-staging
description: Deploy application to staging environment
---

Follow these steps to deploy to staging:

1. Run tests: npm test
2. Build: npm run build
3. Deploy: vercel --env staging
4. Verify: curl https://staging.example.com/health
5. Notify team in #deployments Slack channel

Use environment variables:
- VERCEL_TOKEN
- SLACK_WEBHOOK_URL
```

### When to Use Slash Commands vs Skills
- **Slash command**: User must type `/command` explicitly
  - Use for: Specific workflows, deployments, releases
  - Example: `/deploy staging`, `/create-migration`

- **Skill**: Claude triggers automatically based on context
  - Use for: Ongoing guidance, standards, automatic assistance
  - Example: Code review standards, testing patterns

## Creating CLAUDE.md

CLAUDE.md sets project-wide instructions loaded in every conversation.

### Analogy
CLAUDE.md is like **house rules** - they apply to everyone, all the time. No matter what room (conversation) you're in, these rules are active.

### Location
Project root or `.claude/CLAUDE.md`

### CLAUDE.md Template
```markdown
# Project Guidelines

## Code Standards
- Use TypeScript strict mode
- All functions must have JSDoc comments
- Maximum line length: 100 characters

## Testing Requirements
- Write tests for all new features
- Minimum 80% code coverage
- E2E tests for user-facing features

## Git Workflow
- Branch naming: feature/*, bugfix/*, hotfix/*
- Commits must reference ticket numbers
- Squash merge to main

## Architecture
- API routes in src/app/api/
- Components in src/components/
- Use server components by default
- Client components only when needed (interactivity, hooks)

## Security
- Never commit .env files
- Use environment variables for secrets
- Validate all user input
- Sanitize database queries
```

### Best Practices
- Keep focused on project-specific standards
- Include examples of preferred patterns
- Link to detailed docs for complex topics
- Update as project evolves

## Creating Subagents

Subagents are separate Claude contexts with their own tools and conversation history.

### Analogy
Subagents are like **contractors** - you hire them for specific jobs with specific tools. They work independently and report back when done.

### Subagent Structure (.claude/agents/agent-name.md)
```yaml
---
name: code-reviewer
description: Reviews code for quality, security, and best practices
skills: pr-review, security-check  # Optional: Give access to specific skills
tools: Read, Grep, Glob             # Optional: Restrict tools
---

You are a senior code reviewer. When reviewing code:

1. Check for security vulnerabilities
2. Verify error handling
3. Look for performance issues
4. Ensure tests are included
5. Verify documentation

Provide specific, actionable feedback with examples.
```

### Built-in Subagents
- **Explore**: Fast codebase exploration
- **Plan**: Design implementation plans
- **general-purpose**: Default subagent
- **Bash**: Command execution specialist

### Using Subagents in Skills
```yaml
---
name: detailed-analysis
description: Perform deep code analysis
context: fork          # Run in isolated context
agent: Explore         # Use Explore subagent
---

Perform thorough analysis using the Explore agent...
```

## Creating MCP Servers

MCP (Model Context Protocol) servers connect Claude to external tools and data sources.

### Analogy
MCP servers are like **APIs for Claude** - they provide tools and data that Claude can call. Like how your app calls Stripe's API for payments, Claude calls your MCP server for custom functionality.

### When to Create an MCP Server
- Need to access external databases
- Integrate with third-party APIs
- Provide custom tools/functions
- Access system resources (files, processes)
- Real-time data sources

### MCP Server Structure
```
my-mcp-server/
├── package.json
├── src/
│   └── index.ts
└── README.md
```

### Basic MCP Server (TypeScript)
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
  {
    name: 'my-custom-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// Define a tool
server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'query_database',
      description: 'Query the company database',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'SQL query' },
        },
        required: ['query'],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'query_database') {
    const result = await executeQuery(request.params.arguments.query);
    return {
      content: [{ type: 'text', text: JSON.stringify(result) }],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Registering MCP Server (.claude/mcp.json)
```json
{
  "mcpServers": {
    "my-custom-server": {
      "command": "node",
      "args": ["path/to/server/build/index.js"]
    }
  }
}
```

## Decision Workflow

Guide users through this decision tree:

### "I want Claude to always remember something"
→ **CLAUDE.md**
- Project coding standards
- Architecture decisions
- Naming conventions

### "I want Claude to help with X automatically"
→ **Skill**
- Code review guidance
- Testing patterns
- Documentation generation
- Write SKILL.md with clear description

### "I want a command I can run"
→ **Slash Command**
- Deployment workflows
- Database migrations
- Report generation
- Write command file in .claude/commands/

### "I want something to happen after I edit a file"
→ **Hook**
- Auto-formatting
- Running tests
- Linting
- Add hook to settings.json

### "I want Claude to explore the codebase separately"
→ **Subagent**
- Create custom agent in .claude/agents/
- Or use built-in Explore agent

### "I want Claude to access external data/tools"
→ **MCP Server**
- Database access
- API integrations
- Custom tools
- Create MCP server + register in mcp.json

## Common Patterns & Examples

### Pattern 1: Code Review Workflow
**Skill** (automatic) + **Slash Command** (manual) + **Hook** (on PR)

```yaml
# .claude/skills/pr-review/SKILL.md
---
name: pr-review
description: Review pull requests for code quality, security, and best practices. Use when reviewing code, PRs, or when user mentions code review.
---
[Review instructions]
```

```yaml
# .claude/commands/review-pr.md
---
name: review-pr
---
Review the current branch against main using pr-review skill
```

```json
// .claude/settings.json
{
  "hooks": [{
    "event": "PostToolUse",
    "matcher": "Bash(git push)",
    "hooks": [{ "command": "./scripts/notify-pr-ready.sh" }]
  }]
}
```

### Pattern 2: Testing Workflow
**CLAUDE.md** (standards) + **Hook** (auto-run) + **Skill** (guidance)

```markdown
# CLAUDE.md
## Testing Standards
- All features need tests
- Use Jest for unit tests
- Use Playwright for E2E
```

```json
// .claude/settings.json
{
  "hooks": [{
    "event": "PostToolUse",
    "matcher": "Write|Edit",
    "hooks": [{
      "command": "npm test -- --bail",
      "background": true
    }]
  }]
}
```

### Pattern 3: Database Workflow
**MCP Server** (data access) + **Skill** (guidance) + **Slash Commands** (operations)

MCP server provides database tools, skill provides schema knowledge, commands provide common operations.

## Troubleshooting Guide

### Skill Not Triggering
1. **Check description**: Include keywords users would say
2. **Test description**: Ask Claude "What skills are available?"
3. **Make it specific**: "Reviews Python code for PEP 8" not "Helps with code"

### Hook Not Running
1. **Check event name**: PostToolUse, PreToolUse, Stop
2. **Check matcher**: Exact tool name or regex pattern
3. **Check command**: Test script manually first
4. **Check permissions**: Scripts need execute permissions

### Command Not Appearing
1. **Check location**: .claude/commands/ or ~/.claude/commands/
2. **Check filename**: Must end in .md
3. **Check YAML**: Frontmatter must be valid

### MCP Server Not Connecting
1. **Check mcp.json**: Correct path and command
2. **Check server**: Run manually to test
3. **Check logs**: Look in Claude Code logs
4. **Test transport**: Verify stdio communication works

## Step-by-Step Creation Process

When user wants to create something:

1. **Clarify goal**: "What do you want to accomplish?"
2. **Choose tool**: Use decision tree above
3. **Create structure**: Set up files/directories
4. **Write content**: Use templates above
5. **Test**: Verify it works
6. **Document**: Add usage examples
7. **Iterate**: Refine based on usage

## Best Practices Summary

### Skills
✅ Clear, specific descriptions with trigger keywords
✅ Keep SKILL.md under 500 lines
✅ Use progressive disclosure for details
✅ Restrict tools with allowed-tools when needed
✅ Test: Ask "What skills are available?"

### Hooks
✅ Keep hooks fast (<1 second)
✅ Test scripts manually first
✅ Use background: true for slow operations
✅ Log hook execution for debugging

### Slash Commands
✅ Name commands clearly (/deploy-staging not /ds)
✅ Include verification steps
✅ List required environment variables
✅ Provide examples

### CLAUDE.md
✅ Focus on project-specific standards
✅ Use examples over abstract rules
✅ Keep it current
✅ Link to detailed docs

### Subagents
✅ Use for isolation, not just organization
✅ Give only needed tools
✅ Provide clear instructions
✅ Return structured results

### MCP Servers
✅ Implement proper error handling
✅ Validate all inputs
✅ Provide clear tool descriptions
✅ Test thoroughly

---

Remember: Start simple, test thoroughly, iterate based on usage!
