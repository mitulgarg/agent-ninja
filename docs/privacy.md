# Privacy Design

Agent Ninja is designed with privacy as a core principle. It captures only the minimum metadata needed for workflow analysis, never storing sensitive content.

## What IS Stored

| Data | Storage location | Example |
|------|-----------------|---------|
| Prompt hash | `routing.jsonl` | `"a1b2c3d4e5f67890"` |
| Model/pattern/thinking decisions | `routing.jsonl` | `"model": "haiku"` |
| Tool names | `sessions.jsonl` | `"tool_name": "Edit"` |
| Command classification | `sessions.jsonl` | `"command_type": "test"` |
| File extensions | `sessions.jsonl` | `"file_ext": "py"` |
| Success/failure status | `sessions.jsonl` | `"success": false` |
| Session IDs | `sessions.jsonl` | `"session_id": "abc123"` |
| Timestamps | Both files | `"ts": 1709856000.0` |

## What is NOT Stored

- Prompt text or content
- File paths (only extensions)
- Bash command text (only classification)
- File contents
- Tool output or responses
- API keys or credentials
- User identity information

## Prompt Hashing

The `hash_prompt()` function (`scripts/core/models.py`) creates a privacy-safe identifier:

```python
def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]
```

- Uses SHA-256, truncated to the first 16 hex characters
- One-way: the original prompt cannot be recovered from the hash
- Deterministic: the same prompt always produces the same hash
- Used to detect repeated prompts without storing content

## Command Classification

When a `Bash` tool use is observed, the raw command is classified into a category and the command text is discarded:

```python
def _classify_command(cmd: str) -> str:
    cmd_lower = cmd.lower().strip()
    if any(t in cmd_lower for t in ["pytest", "npm test", "jest", "make test"]):
        return "test"
    # ... other categories
    return "other"
```

The classification (`"test"`, `"build"`, `"git"`, `"install"`, `"network"`, `"other"`) is stored. The command string is never written to disk.

## File Path Handling

For file edit operations, only the extension is extracted:

```python
def _get_extension(file_path: str) -> str:
    if "." in file_path:
        return file_path.rsplit(".", 1)[-1].lower()
    return ""
```

`/home/user/project/src/auth/login.tsx` becomes `"tsx"`. The directory structure and filename are discarded.

## Data Location

All data is stored locally in the project directory:

```
<project-root>/.agent-ninja/
    data/
        sessions.jsonl    # Session and tool events
        routing.jsonl     # Routing decisions
    proposed/
        skills/           # Generated skills (human review)
```

This directory should be added to `.gitignore` to prevent accidental commits.

## No Network Communication

Agent Ninja makes zero network calls. All processing happens locally:

- Router uses regex matching and context injection (no API calls)
- Observer appends to local JSONL files
- Strategist reads local files and uses Claude's own session for analysis

There are no telemetry endpoints, no analytics services, no external dependencies.

## Data Retention

- **Append-only**: Data is only ever appended, never modified in place
- **No auto-rotation**: Log files grow indefinitely until manually managed
- **User-controlled deletion**: Users can delete `.agent-ninja/data/` at any time to clear all collected data
- **No backups**: Data exists only in the local `.agent-ninja/` directory

To clear all data:

```bash
rm -rf .agent-ninja/data/
```

Agent Ninja will recreate the directory on next use.

## Further Reading

- [Observer Reference](observer.md) -- details on what the observer captures
- [Configuration Reference](configuration.md) -- disabling observation entirely
