# Agent Ninja 

An intelligent Claude Code / Gemini CLI plugin that routes tasks to the right model/agent pattern, observes workflow, and proactively optimizes the development environment.

## Architecture

Three layers, zero external API cost:

- **Router** (Layer 1) — Static regex rules classify obvious prompts (haiku/sonnet/opus). For ambiguous prompts, injects a self-assessment prompt via `additionalContext` so Claude classifies itself within its own session.
- **Observer** (Layer 2) — Passive session logging to JSONL. No API calls, no token cost. Captures tool usage metadata, routing decisions, session lifecycle.
- **Strategist** (Layer 3) — On-demand analysis via Claude Code slash commands (`/an:audit`, `/an:strategize`, `/an:generate-skill`, `/an:generate-agent`). Claude reads the JSONL logs and analyzes patterns using its own session — no separate API key needed.

Single entry point (`scripts/entrypoint.py`) handles ALL hook events — dispatches based on `hook_event_name` from stdin JSON.

## Tech Stack

- **Language:** Python 3.8+ (stdlib only — no pip dependencies)
- **Storage:** Append-only JSONL files in `.agent-ninja/data/`
- **Testing:** pytest (dev dependency only)
- **No external API key required** — all intelligence runs through Claude's own session

## Project Structure

```
agent-ninja/
├── .claude-plugin/plugin.json         # Claude Code plugin manifest
├── hooks/hooks.json                   # Claude Code hook definitions
├── platforms/
│   ├── claude_code.json               # Hook config for Claude Code
│   └── gemini_cli.json                # Hook config for Gemini CLI
├── scripts/
│   ├── entrypoint.py                  # Single entry point for ALL hooks
│   ├── run_command.py                 # CLI for slash commands (status, summary)
│   ├── core/
│   │   ├── config.py                  # Hierarchical config (env > project > defaults)
│   │   ├── logger.py                  # Structured JSONL logging
│   │   └── models.py                  # Dataclasses: RoutingDecision, SessionRecord, etc.
│   ├── router/
│   │   ├── engine.py                  # Static rules + self-assessment injection
│   │   ├── prompts.py                 # Classification guide for self-assessment
│   │   └── rules.py                   # Regex-based static override rules
│   ├── observer/
│   │   └── engine.py                  # Passive session data capture
│   ├── strategist/
│   │   ├── engine.py                  # Data aggregation for slash commands
│   │   └── prompts.py                 # Data formatting helpers
│   └── utils/
│       ├── io.py                      # stdin/stdout helpers for hooks
│       └── hash.py                    # (hash_prompt lives in models.py)
├── skills/ninja-advisor/SKILL.md      # Teaches agent to follow routing
├── agents/strategist.md               # Deep analysis subagent
├── commands/                          # Slash command definitions
│   ├── audit.md                       # /an:audit
│   ├── strategize.md                  # /an:strategize
│   ├── generate-skill.md              # /an:generate-skill
│   ├── generate-agent.md              # /an:generate-agent
│   └── status.md                      # /an:status
├── config/defaults.json               # Default routing rules
├── tests/
│   ├── test_router.py
│   ├── test_observer.py
│   ├── test_strategist.py
│   ├── test_entrypoint.py
│   └── fixtures/                      # Sample hook input JSON
├── pyproject.toml
├── SETUP.md                           # User installation guide
└── README.md
```

Runtime data (gitignored):
```
.agent-ninja/
├── data/
│   ├── sessions.jsonl                 # Session observations
│   ├── routing.jsonl                  # Routing decisions + outcomes
├── proposed/                          # Generated skills (needs human review)
```

## Commands

```bash
# Run tests
pytest

# Run a specific test
pytest tests/test_router.py

# Simulate hook calls
echo '{"hook_event_name":"UserPromptSubmit","user_prompt":"run tests","session_id":"test"}' | python3 scripts/entrypoint.py
echo '{"hook_event_name":"PostToolUse","tool_name":"Bash","session_id":"test"}' | python3 scripts/entrypoint.py

# Check status
python3 scripts/run_command.py status
```

## Design Principles

- **Zero API key required** — Router uses static regex rules + Claude self-assessment. Strategist runs as Claude slash commands within the session.
- **Zero external dependencies** — stdlib only (json, hashlib, re). No pip install needed.
- **Privacy-first** — prompts are never stored, only SHA-256 hashes. File paths store only extensions. Bash commands store only type classification.
- **Static rules first** — regex matching handles obvious cases at zero cost. Self-assessment only for ambiguous prompts.
- **Proposed, not applied** — generated skills go to `proposed/` and require human review before activation.
- **Platform-agnostic core** — all business logic in `scripts/core/`, platform-specific hook wiring in `platforms/`.

## Key Enums

- `ModelTier`: haiku, sonnet, opus
- `AgentPattern`: direct, subagent, agent-team, skill-invocation, plan-mode
- `ThinkingLevel`: off, low, high

## Config Precedence (highest to lowest)

1. Environment variables (`AGENT_NINJA_*`)
2. Project config (`.agent-ninja/config.json`)
3. Plugin defaults (`config/defaults.json`)
4. Hardcoded defaults in `AgentNinjaConfig`

## User Setup

Users add the Agent Ninja instructions to their CLAUDE.md — see SETUP.md for the copy-paste block.
