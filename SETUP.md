# Agent Pilot - Setup & Testing Guide

## Step 1: Clone the Repository

```bash
git clone https://github.com/mitul-s/agent-pilot.git
cd agent-pilot
```

## Step 2: Create the Hooks File

Create `~/.claude/hooks.json` (global) or `.claude/hooks.json` (project-level):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 /ABSOLUTE/PATH/TO/agent-pilot/scripts/entrypoint.py",
        "timeout": 10
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "type": "command",
        "command": "python3 /ABSOLUTE/PATH/TO/agent-pilot/scripts/entrypoint.py",
        "timeout": 5
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 /ABSOLUTE/PATH/TO/agent-pilot/scripts/entrypoint.py",
        "timeout": 5
      }
    ]
  }
}
```

Replace `/ABSOLUTE/PATH/TO/agent-pilot` with the actual path where you cloned the repo.

## Step 3: Add Instructions to Your CLAUDE.md

Add the following block to `~/.claude/CLAUDE.md` (global) or your project's `CLAUDE.md`:

```markdown
## Agent Pilot - Intelligent Routing

When you see `[Agent Pilot]` context injected at the start of a conversation turn,
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

## Step 4: Restart Claude Code

Hooks only load on session startup. Open a new terminal and start a fresh session:

```bash
claude
```

## Step 5: Test It

Try these prompts in order to see each routing behavior:

### Static rule → Haiku (simple task)
```
run tests
```
Expected: `[Agent Pilot] Recommended: model=haiku, pattern=direct, thinking=off`

### Static rule → Opus (complex task)
```
architect a new authentication system
```
Expected: `[Agent Pilot] Recommended: model=opus, pattern=plan-mode, thinking=high`

### Static rule → Sonnet + Plan Mode (multi-step)
```
implement a new feature for user notifications
```
Expected: `[Agent Pilot] Recommended: model=sonnet, pattern=plan-mode, thinking=low`

### Self-assessment (ambiguous prompt)
```
help me fix this bug
```
Expected: `[Agent Pilot] No static routing rule matched...` followed by Claude self-assessing before proceeding.

## Step 6: Check the Logs

After a few prompts, inspect what Agent Pilot captured:

```bash
# Routing decisions
cat .agent-pilot/data/routing.jsonl | python3 -m json.tool --json-lines

# Session events (tool usage, etc.)
cat .agent-pilot/data/sessions.jsonl | python3 -m json.tool --json-lines

# Quick status dashboard
python3 /path/to/agent-pilot/scripts/run_command.py status
```

## Step 7: Try the Slash Commands

After accumulating some session data, try:

- `/ap:status` — Quick dashboard of routing stats and tool usage
- `/ap:audit` — Deep environment health check with recommendations
- `/ap:strategize` — Workflow analysis with actionable optimization proposals
- `/ap:generate-skill` — Generate reusable skills from repeated patterns

## Optional: Project-Level Configuration

Create `.agent-pilot/config.json` in any project to customize routing rules:

```json
{
  "routing": {
    "enabled": true,
    "auto_switch": true,
    "always_opus_for": ["security review", "database migration"],
    "always_haiku_for": ["format", "lint", "check logs"]
  },
  "observer": {
    "enabled": true
  }
}
```

## Troubleshooting

**Hooks not firing?**
- Make sure you restarted Claude Code after adding `hooks.json`
- Verify the path in `hooks.json` is absolute and correct
- Check that `python3` is available in your PATH

**No output from hooks?**
- Test the entrypoint directly:
  ```bash
  echo '{"hook_event_name":"UserPromptSubmit","user_prompt":"run tests","session_id":"test"}' | python3 /path/to/agent-pilot/scripts/entrypoint.py
  ```
- You should see JSON output with `hookSpecificOutput.additionalContext`

**No data in `.agent-pilot/`?**
- The directory is created relative to `CLAUDE_PROJECT_DIR` (your project root)
- Check that the directory exists: `ls -la .agent-pilot/data/`

## Uninstall

1. Remove the hooks: delete `~/.claude/hooks.json` (or remove the Agent Pilot entries)
2. Remove the CLAUDE.md block: delete the "Agent Pilot - Intelligent Routing" section
3. Remove session data: `rm -rf .agent-pilot/` from any projects
