# Configuration Reference

Agent Ninja uses a hierarchical configuration system. Settings can be specified at multiple levels, with higher-precedence sources overriding lower ones.

## Precedence Chain

Settings are resolved in this order (highest precedence first):

1. **Environment variables** (`AGENT_NINJA_*`)
2. **Project config** (`.agent-ninja/config.json` in the project directory)
3. **Plugin defaults** (`config/defaults.json` in the plugin directory)
4. **Hardcoded defaults** in the `AgentNinjaConfig` dataclass

## Complete Options Table

| Option | Config path | Default | Description |
|--------|------------|---------|-------------|
| Routing enabled | `routing.enabled` | `true` | Enable/disable the Router layer entirely |
| Auto switch | `routing.auto_switch` | `true` | Allow automatic model switching recommendations |
| Default model | `routing.default_model` | `"sonnet"` | Fallback model when no rule matches |
| Always opus for | `routing.always_opus_for` | `[]` | Regex patterns that always route to opus |
| Always haiku for | `routing.always_haiku_for` | `[]` | Regex patterns that always route to haiku |
| Observer enabled | `observer.enabled` | `true` | Enable/disable the Observer layer |

## Environment Variables

| Variable | Effect |
|----------|--------|
| `AGENT_NINJA_ROUTING_ENABLED` | Set to `"false"` to disable routing |
| `AGENT_NINJA_AUTO_SWITCH` | Set to `"false"` to disable auto-switch recommendations |
| `CLAUDE_PROJECT_DIR` | Project directory for Claude Code (used to locate `.agent-ninja/`) |
| `GEMINI_PROJECT_DIR` | Project directory for Gemini CLI (fallback if `CLAUDE_PROJECT_DIR` not set) |
| `CLAUDE_PLUGIN_ROOT` | Plugin installation directory (set automatically by Claude Code) |

## Config File Location

Place your project-specific config at:

```
<project-root>/.agent-ninja/config.json
```

This file is automatically read by `AgentNinjaConfig.load()` when the project directory is known.

## Config File Format

```json
{
  "routing": {
    "enabled": true,
    "auto_switch": true,
    "default_model": "sonnet",
    "always_opus_for": [],
    "always_haiku_for": []
  },
  "observer": {
    "enabled": true
  }
}
```

All fields are optional. Only include the ones you want to override.

## Example Configurations

### Minimal (defaults)

```json
{}
```

Everything enabled with default settings.

### Security-Focused

```json
{
  "routing": {
    "always_opus_for": [
      "security",
      "vulnerability",
      "auth",
      "permissions",
      "encryption"
    ]
  }
}
```

Routes any security-related prompt to opus with high thinking.

### High-Throughput

```json
{
  "routing": {
    "always_haiku_for": [
      "format",
      "lint",
      "fix typo",
      "rename",
      "add import",
      "run tests?"
    ]
  }
}
```

Aggressively routes simple tasks to haiku for faster responses.

### Observation-Only

```json
{
  "routing": {
    "enabled": false
  },
  "observer": {
    "enabled": true
  }
}
```

Disables routing recommendations but continues capturing session data for later analysis with `/an:audit` and `/an:strategize`.

### Routing-Only

```json
{
  "routing": {
    "enabled": true
  },
  "observer": {
    "enabled": false
  }
}
```

Enables routing without session observation. Note: `/an:status` and other slash commands will have no data to analyze.

## Data Directories

Agent Ninja creates two directories under `.agent-ninja/`:

| Directory | Purpose |
|-----------|---------|
| `.agent-ninja/data/` | JSONL log files (`sessions.jsonl`, `routing.jsonl`) |
| `.agent-ninja/proposed/` | Generated skills awaiting human review |

Both directories are created automatically on first use and should be added to `.gitignore`.

## Further Reading

- [Routing Reference](routing.md) -- how `always_opus_for` and `always_haiku_for` work
- [Observer Reference](observer.md) -- what data the observer captures
- [Privacy](privacy.md) -- data storage and privacy guarantees
