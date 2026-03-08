# Agent Ninja - Setup Guide

## Requirements

- Python 3.8+
- Claude Code or Gemini CLI

---

## Step 1: Clone Agent Ninja

Clone it once to a permanent location on your machine. We recommend `~/tools/` so it's easy to reference from any project.

```bash
git clone https://github.com/mitulgarg/agent-ninja ~/tools/agent-ninja
```

> You can clone it anywhere — just use that path in Step 2.

---

## Step 2: Run the Installer

The installer wires up the hooks pointing to your clone. Run it from inside the project you want to enable Agent Ninja for:

```bash
cd ~/work/my-project

# macOS / Linux
bash ~/tools/agent-ninja/install.sh

# Windows (PowerShell)
~/tools/agent-ninja/install.ps1
```

> Windows users: if you see an execution policy error, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then retry.

The installer will ask:

```
Where do you want to install the hooks?
  1) Global  — ~/.claude/hooks.json (all Claude Code sessions)
  2) Project — .claude/hooks.json   (current directory only)
```

- Choose **1 (Global)** to activate Agent Ninja across all your projects — run from anywhere, only need to do this once.
- Choose **2 (Project)** to enable it for only the current directory — run from inside that project.

The installer automatically patches the hook config with the correct path — no manual editing needed. If a `hooks.json` already exists, it will ask before overwriting.

### For Gemini CLI

Use the Gemini-specific hook config instead:

```bash
cp platforms/gemini_cli.json .gemini/settings.json
```

---

## Step 3: Add Instructions to Your CLAUDE.md

Add the following block to `~/.claude/CLAUDE.md` (global) or your project's `CLAUDE.md`:

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

---

## Step 4: Restart Claude Code

Hooks only load on session startup. Open a new terminal and start a fresh session:

```bash
claude
```

---

## Step 5: Test It

Try these prompts to see each routing behavior:

### Simple task → Haiku
```
run tests
```
Expected: `[Agent Ninja] Recommended: model=haiku, pattern=direct, thinking=off`

### Complex task → Opus
```
architect a new authentication system
```
Expected: `[Agent Ninja] Recommended: model=opus, pattern=plan-mode, thinking=high`

### Multi-step task → Sonnet
```
implement a new feature for user notifications
```
Expected: `[Agent Ninja] Recommended: model=sonnet, pattern=plan-mode, thinking=low`

### Ambiguous prompt → Self-assessment
```
help me fix this bug
```
Expected: `[Agent Ninja] No static routing rule matched...` followed by Claude self-assessing before proceeding.

---

## Step 6: Check the Logs

After a few prompts, inspect what Agent Ninja captured:

```bash
# Routing decisions
cat .agent-ninja/data/routing.jsonl | python3 -m json.tool --json-lines

# Session events (tool usage, etc.)
cat .agent-ninja/data/sessions.jsonl | python3 -m json.tool --json-lines

# Quick status dashboard
python3 scripts/run_command.py status
```

---

## Step 7: Try the Slash Commands

After accumulating some session data:

- `/an:status` — Quick dashboard of routing stats and tool usage
- `/an:audit` — Deep environment health check with recommendations
- `/an:strategize` — Workflow analysis with actionable optimization proposals
- `/an:generate-skill` — Generate reusable skills from repeated patterns

---

## Optional: Custom Configuration

Create `.agent-ninja/config.json` in any project to customize routing rules:

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

---

## Troubleshooting

**Hooks not firing?**
- Make sure you restarted Claude Code after running the installer
- Verify the installer completed without errors — re-run it if unsure
- Check that `python3` is available in your PATH: `python3 --version`

**No output from hooks?**
- Test the entrypoint directly:
  ```bash
  echo '{"hook_event_name":"UserPromptSubmit","user_prompt":"run tests","session_id":"test"}' | python3 scripts/entrypoint.py
  ```
- You should see JSON output with `hookSpecificOutput.additionalContext`

**No data in `.agent-ninja/`?**
- The directory is created relative to `CLAUDE_PROJECT_DIR` (your project root)
- Check that the directory exists: `ls -la .agent-ninja/data/`

---

## Uninstall

1. Remove the hooks: delete `~/.claude/hooks.json` (or remove the Agent Ninja entries)
2. Remove the CLAUDE.md block: delete the "Agent Ninja - Intelligent Routing" section
3. Remove session data: `rm -rf .agent-ninja/` from any projects