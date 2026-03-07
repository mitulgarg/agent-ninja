# Platform Support

Agent Ninja supports both Claude Code and Gemini CLI as host agents. The core logic is platform-agnostic -- platform differences are handled at the hook wiring layer.

## Hook Event Name Mapping

The host agents use different event names for equivalent lifecycle events:

| Lifecycle stage | Claude Code | Gemini CLI |
|----------------|-------------|------------|
| User submits prompt | `UserPromptSubmit` | `BeforeModel` |
| After tool execution | `PostToolUse` | `AfterTool` |
| Before tool execution | `BeforeTool` | `BeforeTool` |
| Agent wants to stop | `Stop` | -- |
| Subagent stops | `SubagentStop` | -- |
| Session begins | `SessionStart` | -- |
| Session ends | `SessionEnd` | -- |

The entry point (`scripts/entrypoint.py`) handles both naming conventions:

```python
if event in ("UserPromptSubmit", "BeforeModel"):
    _handle_user_prompt(...)
elif event in ("PostToolUse", "AfterTool", "BeforeTool"):
    _handle_post_tool_use(...)
```

## Hook Config Files

### Claude Code (`platforms/claude_code.json`)

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/entrypoint.py",
        "timeout": 10
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/entrypoint.py",
        "timeout": 5
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/entrypoint.py",
        "timeout": 5
      }
    ]
  }
}
```

Claude Code provides `${CLAUDE_PLUGIN_ROOT}` for absolute path resolution. The `PostToolUse` hook uses `"matcher": ".*"` to capture all tool events.

### Gemini CLI (`platforms/gemini_cli.json`)

```json
{
  "hooks": {
    "BeforeModel": [
      {
        "type": "command",
        "command": "python3 ./scripts/entrypoint.py",
        "timeout": 10
      }
    ],
    "AfterTool": [
      {
        "matcher": ".*",
        "type": "command",
        "command": "python3 ./scripts/entrypoint.py",
        "timeout": 5
      }
    ]
  }
}
```

Gemini CLI uses relative paths and different event names.

## Environment Variable Differences

| Variable | Claude Code | Gemini CLI |
|----------|-------------|------------|
| Project directory | `CLAUDE_PROJECT_DIR` | `GEMINI_PROJECT_DIR` |
| Plugin root | `CLAUDE_PLUGIN_ROOT` | -- |

The entry point resolves the project directory with a fallback chain:

```python
project_dir = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    os.environ.get("GEMINI_PROJECT_DIR", os.getcwd()),
)
```

## Per-Platform Setup

### Claude Code

1. Copy the hook config:
   ```bash
   cp platforms/claude_code.json ~/.claude/hooks.json
   ```
   Or merge into your existing `hooks.json`.

2. Update the path in `hooks.json` to point to your Agent Ninja installation, or set `CLAUDE_PLUGIN_ROOT`.

3. Add Agent Ninja instructions to your project's `CLAUDE.md` (see `INSTALL.md`).

### Gemini CLI

1. Copy the hook config:
   ```bash
   cp platforms/gemini_cli.json <gemini-config-dir>/hooks.json
   ```

2. Ensure the `scripts/` directory is accessible from your project root (or update paths in the config).

3. Set `GEMINI_PROJECT_DIR` if it's not automatically provided.

## Feature Parity

Gemini CLI has fewer lifecycle events than Claude Code:

| Feature | Claude Code | Gemini CLI |
|---------|-------------|------------|
| Prompt routing | Yes (`UserPromptSubmit`) | Yes (`BeforeModel`) |
| Tool observation | Yes (`PostToolUse`) | Yes (`AfterTool`) |
| Session start tracking | Yes (`SessionStart`) | No |
| Session end tracking | Yes (`SessionEnd`) | No |
| Stop event capture | Yes (`Stop`, `SubagentStop`) | No |
| Slash commands | Yes (`/an:*`) | Depends on CLI support |

When running on Gemini CLI, session lifecycle events (start, stop, end) are not captured. Tool observation and prompt routing work normally.

## Further Reading

- [Architecture](architecture.md) -- how the entry point dispatches events
- [Configuration](configuration.md) -- environment variables and config precedence
