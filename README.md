# Agent Ninja

**Intelligent routing, workflow observation, and proactive optimization for AI coding agents.**

Agent Ninja is a Claude Code / Gemini CLI plugin that:
- Routes each prompt to the optimal model tier (haiku/sonnet/opus) using static rules + self-assessment
- Observes your workflow patterns passively (zero API cost)
- Provides on-demand optimization via slash commands (`/an:audit`, `/an:strategize`, `/an:generate-skill`, `/an:generate-agent`)

## Key Features

- **Zero API key required** — all intelligence runs through your existing Claude session
- **Zero external dependencies** — pure Python stdlib, no pip install needed
- **Privacy-first** — prompts are never stored, only hashes
- **Works with Claude Code and Gemini CLI**

## Quick Start

**Requirements:** Python 3.8+, Claude Code or Gemini CLI

### Option A — Install via Claude Code Marketplace (fastest)

```
/plugin marketplace add mitulgarg/agent-ninja
/plugin install agent-ninja
```

Then add the CLAUDE.md block from [SETUP.md](SETUP.md) Step 3 and restart Claude Code.

### Option B — Manual clone (Gemini CLI, or if you want the repo on disk)

### Step 1 — Clone Agent Ninja (once, anywhere on your machine)

We recommend cloning to `~/tools/` so it's easy to reference from any project.
(You can clone it anywhere — just use that path in Step 2.)

```bash
git clone https://github.com/mitulgarg/agent-ninja ~/tools/agent-ninja
```

### Step 2 — Enable it for a project (or globally)

**To enable inside a specific project:**
```bash
cd ~/work/my-project
bash ~/tools/agent-ninja/install.sh          # macOS / Linux
~/tools/agent-ninja/install.ps1             # Windows (PowerShell)
```

**To enable globally (all Claude Code sessions on your machine):**
```bash
bash ~/tools/agent-ninja/install.sh          # macOS / Linux
~/tools/agent-ninja/install.ps1             # Windows (PowerShell)
# → choose option 1 when prompted
```

The installer writes the hook config with the correct path automatically — no manual editing needed. If a `hooks.json` already exists, it will ask before overwriting.

### Step 3 — Add instructions to your CLAUDE.md

See [SETUP.md](SETUP.md) for the copy-paste block to add to your project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for global).

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
- `/an:generate-agent` — create subagent definitions from complex workflow patterns

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

- **[Walkthrough](docs/walkthrough.md)** — End-to-end setup and live examples of routing, logging, and all slash commands
- **[Architecture](docs/architecture.md)** — Three-layer design, entry point dispatch, hook lifecycle, data flow
- **[Routing Reference](docs/routing.md)** — Static rules, regex patterns, self-assessment, additionalContext injection
- **[Observer Reference](docs/observer.md)** — Captured metadata, JSONL format, command classification, failure detection
- **[Strategist & Slash Commands](docs/strategist.md)** — `/an:status`, `/an:audit`, `/an:strategize`, `/an:generate-skill`, `/an:generate-agent`
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
