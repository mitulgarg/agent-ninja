# Agent Ninja

**Intelligent routing, workflow observation, and proactive optimization for AI coding agents.**

Agent Ninja is a Claude Code / Gemini CLI plugin that:
- Routes each prompt to the optimal model tier (haiku/sonnet/opus) using static rules + self-assessment
- Observes your workflow patterns passively (zero API cost)
- Provides on-demand optimization via slash commands (`/an:audit`, `/an:strategize`, `/an:generate-skill`)

## Key Features

- **Zero API key required** — all intelligence runs through your existing Claude session
- **Zero external dependencies** — pure Python stdlib, no pip install needed
- **Privacy-first** — prompts are never stored, only hashes
- **Works with Claude Code and Gemini CLI**

## Quick Start

```bash
# 1. Clone
git clone https://github.com/mitulgarg/agent-ninja

# 2. Set up hooks (update path in hooks.json)
cp hooks/hooks.json ~/.claude/hooks.json

# 3. Add Agent Ninja instructions to your CLAUDE.md
# See INSTALL.md for the copy-paste block
```

## How It Works

### Layer 1: Router (every prompt)
A hook fires on each prompt. Static regex rules handle obvious cases:
- `"run tests"` → haiku, direct, thinking off
- `"architect a new auth system"` → opus, plan-mode, thinking high
- Ambiguous prompts → Claude self-assesses within its own session

### Layer 2: Observer (passive)
Logs tool usage, routing decisions, and session metadata to `.agent-ninja/data/`. Zero API calls.

### Layer 3: Strategist (on-demand)
Slash commands that Claude executes using its own capabilities:
- `/an:status` — quick dashboard
- `/an:audit` — environment health check
- `/an:strategize` — deep workflow analysis with proposals
- `/an:generate-skill` — create skills from repeated patterns

## Configuration

Create `.agent-ninja/config.json` in your project:

```json
{
  "routing": {
    "enabled": true,
    "auto_switch": true,
    "always_opus_for": ["security review", "architecture"],
    "always_haiku_for": ["format", "lint"]
  },
  "observer": {
    "enabled": true
  }
}
```

## Documentation

Detailed documentation is available in the [`docs/`](docs/) directory:

- **[Architecture](docs/architecture.md)** — Three-layer design, entry point dispatch, hook lifecycle, data flow
- **[Routing Reference](docs/routing.md)** — Static rules, regex patterns, self-assessment, additionalContext injection
- **[Observer Reference](docs/observer.md)** — Captured metadata, JSONL format, command classification, failure detection
- **[Strategist & Slash Commands](docs/strategist.md)** — `/an:status`, `/an:audit`, `/an:strategize`, `/an:generate-skill`
- **[Configuration Reference](docs/configuration.md)** — Precedence chain, all options, environment variables, example configs
- **[Privacy Design](docs/privacy.md)** — What is/isn't stored, prompt hashing, data retention
- **[Platform Support](docs/platforms.md)** — Claude Code vs Gemini CLI differences, setup instructions

## Development

```bash
# Run tests
python3 -m pytest tests/ -v

# Simulate a hook
echo '{"hook_event_name":"UserPromptSubmit","user_prompt":"run tests","session_id":"test"}' | python3 scripts/entrypoint.py
```

## License

MIT
