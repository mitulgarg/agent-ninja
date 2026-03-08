# Changelog

All notable changes to Agent Ninja will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-03-08

### Added
- **Router** — static regex rules classify prompts to haiku/sonnet/opus; self-assessment injection for ambiguous prompts
- **Observer** — passive session logging to JSONL with zero API cost; captures tool usage, routing decisions, and session lifecycle
- **Strategist** — on-demand analysis via slash commands (`/an:audit`, `/an:strategize`, `/an:generate-skill`, `/an:status`)
- Single entrypoint (`scripts/entrypoint.py`) handles all hook events dispatched from stdin JSON
- Hierarchical config system: env vars > project config > plugin defaults > hardcoded defaults
- Privacy-first design: prompts stored as SHA-256 hashes only; file paths stored as extensions only
- Support for Claude Code and Gemini CLI via platform-specific hook configs
- `ninja-advisor` skill to guide the agent in following routing recommendations
- `agents/strategist.md` subagent for deep session analysis
- Pure Python stdlib implementation — no external dependencies

[Unreleased]: https://github.com/mitulgarg/agent-ninja/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mitulgarg/agent-ninja/releases/tag/v1.0.0