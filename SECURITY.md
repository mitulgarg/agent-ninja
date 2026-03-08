# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (main) | Yes |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, report it by opening a [GitHub Security Advisory](https://github.com/mitulgarg/agent-ninja/security/advisories/new) or emailing the maintainer directly.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Any relevant logs or output (redact personal data)

You can expect an acknowledgment within 48 hours and a resolution or mitigation plan within 7 days for confirmed vulnerabilities.

## Security Design

Agent Ninja is designed with privacy and security in mind:

- **No raw prompt storage** — only SHA-256 hashes of prompts are logged
- **No file content storage** — only file extensions are recorded
- **No external network calls** — all logic runs locally; no data leaves your machine
- **No API keys stored** — routing uses Claude's own session; no separate credentials required
- **Local JSONL only** — all session data stays in `.agent-ninja/data/` in your project directory

## Scope

Security issues of interest include:

- Path traversal or arbitrary file write via hook input
- Command injection through hook event fields
- Unintended exfiltration of prompt content or file data
- Privilege escalation via the entrypoint script