# Agent Ninja - Installation Guide

## Quick Start

### 1. Clone the repository

```bash
git https://github.com/mitulgarg/agent-ninja
```

### 2. Set up hooks

Copy the hook configuration to your Claude Code settings:

```bash
# Copy hooks to your global Claude settings
cp hooks/hooks.json ~/.claude/hooks.json
```

Or for project-level hooks, copy to your project's `.claude/` directory.

**Important:** Update the `command` paths in `hooks.json` to point to where you cloned agent-ninja:

```json
"command": "python3 /path/to/agent-ninja/scripts/entrypoint.py"
```

### 3. Add to your CLAUDE.md

Add the following block to your project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for global):

```markdown
## Agent Ninja - Intelligent Routing

When you see `[Agent Ninja]` context injected at the start of a conversation turn,
it contains a routing recommendation. Follow these instructions:

1. **If a direct recommendation is provided** (model/pattern/thinking), acknowledge it
   briefly and follow the guidance:
   - If the recommended model differs from your current model, suggest the user switch
     with `/model <tier>`
   - If plan-mode is recommended, suggest using plan mode before executing
   - If subagent is recommended, consider delegating the subtask
   - If thinking level is "off", keep your response concise and mechanical

2. **If a self-assessment is requested** (no static rule matched), briefly self-assess
   the task before proceeding:
   - State your model/pattern/thinking assessment in one line
   - If you determine a different model would be better, suggest switching
   - Then proceed with execution immediately — do not wait for confirmation

3. **Always be brief** about routing — one line of assessment, then get to work.
   The routing context is there to help you optimize, not to slow you down.
```

### 4. Verify installation

Start a Claude Code session and try a simple prompt like "run tests". You should see
`[Agent Ninja]` context in the conversation indicating the routing recommendation.

## For Gemini CLI

Use the Gemini-specific hook config:

```bash
cp platforms/gemini_cli.json .gemini/settings.json
```

## Configuration

Create `.agent-ninja/config.json` in your project root to customize routing:

```json
{
  "routing": {
    "enabled": true,
    "auto_switch": true,
    "always_opus_for": ["security review", "architecture"],
    "always_haiku_for": ["format", "lint", "check logs"]
  },
  "observer": {
    "enabled": true
  }
}
```

## Slash Commands

After installation, you can use these commands in Claude Code:

- `/an:status` — Quick dashboard of routing stats
- `/an:audit` — Deep environment health check
- `/an:strategize` — Workflow analysis with optimization proposals
- `/an:generate-skill` — Generate skills from repeated patterns