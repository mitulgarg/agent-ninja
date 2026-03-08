# Contributing to Agent Ninja

Thank you for your interest in contributing! This document covers how to get started, the development workflow, and guidelines for submitting changes.

## Getting Started

```bash
git clone https://github.com/mitulgarg/agent-ninja
cd agent-ninja
```

No pip install required — Agent Ninja uses Python stdlib only. For tests:

```bash
pip install pytest  # dev dependency only
pytest
```

## Project Structure

Key areas to understand before contributing:

| Path | Purpose |
|------|---------|
| `scripts/entrypoint.py` | Single entry point for all hook events |
| `scripts/router/` | Static rules + self-assessment routing logic |
| `scripts/observer/` | Passive JSONL session logging |
| `scripts/strategist/` | Slash command data aggregation |
| `scripts/core/` | Config, logger, shared dataclasses |
| `tests/` | pytest test suite |

## Development Workflow

1. **Fork** the repo and create a branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes.** Keep them focused — one concern per PR.

3. **Run tests** before pushing:
   ```bash
   pytest
   ```

4. **Test the hook manually** to verify end-to-end behavior:
   ```bash
   echo '{"hook_event_name":"UserPromptSubmit","user_prompt":"run tests","session_id":"test"}' | python3 scripts/entrypoint.py
   ```

5. **Open a pull request** against `main` with a clear description of what and why.

## Design Principles (please follow these)

- **Zero external dependencies** — stdlib only. Do not add pip packages to core logic.
- **Zero API key required** — routing uses static rules + Claude self-assessment. No separate LLM calls.
- **Privacy-first** — never store raw prompts or file contents. Use hashes/extensions only.
- **Static rules first** — add regex rules in `scripts/router/rules.py` before reaching for self-assessment.
- **Proposed, not applied** — generated artifacts go to `proposed/` for human review.

## What to Contribute

Good areas for contribution:

- New routing rules in `scripts/router/rules.py` for common prompt patterns
- Additional observer metadata (new tool-use signals, session lifecycle events)
- Improved slash command output formatting in `scripts/strategist/`
- Bug fixes and test coverage improvements
- Platform support (e.g., new AI CLI tools beyond Claude Code and Gemini CLI)

## Submitting Issues

- Search existing issues before opening a new one
- For bugs, include: OS, Python version, the hook event JSON that triggered it, and the error output
- For feature requests, explain the use case and how it fits the zero-dependency, privacy-first design

## Code Style

- Follow PEP 8
- Keep functions small and focused
- Add tests for new behavior in `tests/`
- Do not add comments for self-evident code

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).