# Observer Reference

The Observer is Layer 2 of Agent Ninja. It passively captures session metadata and tool usage from hook events, writing structured JSONL to disk. Zero API calls, zero token cost.

## What Is Captured

The observer records metadata about your development sessions:

- **Session lifecycle events**: start, stop, end
- **Tool usage**: which tools were used, success/failure
- **Bash command classification**: test, build, git, install, network, or other (never the raw command)
- **File extensions**: only the extension of edited files (never the full path)
- **Failure detection**: exit codes from tool responses

## JSONL Log Format

All records are appended to JSONL files in `.agent-ninja/data/`. Each line is a self-contained JSON object with a common structure:

```json
{"ts": 1709856000.123, "type": "<event_type>", ...event-specific fields}
```

| Field | Type | Description |
|-------|------|-------------|
| `ts` | `float` | Unix timestamp |
| `type` | `string` | Event type identifier |
| Additional fields | varies | Event-specific data |

### sessions.jsonl

Records session lifecycle and tool usage events.

**Session start:**
```json
{"ts": 1709856000.0, "type": "session_start", "session_id": "abc123", "trigger": ""}
```

**Tool use (Bash):**
```json
{"ts": 1709856010.5, "type": "tool_use", "session_id": "abc123", "tool_name": "Bash", "success": true, "command_type": "test"}
```

**Tool use (file edit):**
```json
{"ts": 1709856020.3, "type": "tool_use", "session_id": "abc123", "tool_name": "Edit", "success": true, "file_ext": "py"}
```

**Tool use (failure):**
```json
{"ts": 1709856030.1, "type": "tool_use", "session_id": "abc123", "tool_name": "Bash", "success": false, "command_type": "build"}
```

**Session stop:**
```json
{"ts": 1709856100.0, "type": "session_stop", "session_id": "abc123", "reason": ""}
```

**Session end:**
```json
{"ts": 1709856105.0, "type": "session_end", "session_id": "abc123"}
```

### routing.jsonl

Records routing decisions made by the Router layer.

**Static rule match:**
```json
{"ts": 1709856005.0, "type": "route", "model": "haiku", "pattern": "direct", "thinking": "off", "reasoning": "Static rule: simple task pattern", "prompt_hash": "a1b2c3d4e5f67890", "confidence": 0.0}
```

**Self-assessment fallback:**
```json
{"ts": 1709856006.0, "type": "self_assess", "prompt_hash": "f0e1d2c3b4a59876", "model": "self", "pattern": "self-assess"}
```

## Command Classification

When a `Bash` tool use is observed, the raw command is never stored. Instead, it is classified into one of these categories:

| Classification | Matched keywords |
|---------------|-----------------|
| `test` | `pytest`, `npm test`, `jest`, `make test` |
| `build` | `npm run build`, `make build`, `cargo build` |
| `git` | `git ` |
| `install` | `npm install`, `pip install`, `cargo add` |
| `network` | `curl `, `wget ` |
| `other` | Everything else |

Only the classification string is stored, never the command itself.

## File Extension Extraction

For `Write`, `Edit`, and `MultiEdit` tool events, the observer extracts only the file extension from the path:

- `/src/components/Button.tsx` -> `tsx`
- `config/settings.json` -> `json`
- `Makefile` (no extension) -> `""`

The full file path is never stored.

## Failure Detection

The observer checks `tool_response.exit_code` to determine success or failure:

- `exit_code` is `None` or `0` -> `success: true`
- `exit_code` is non-zero -> `success: false`

## Session Lifecycle

```
SessionStart ---------> session_start logged
     |
UserPromptSubmit -----> (handled by Router, not Observer)
     |
PostToolUse x N ------> tool_use logged (per tool)
     |
Stop -----------------> session_stop logged
     |
     ... (more prompt cycles possible)
     |
SessionEnd -----------> session_end logged
```

## JsonlLogger

The `JsonlLogger` class (`scripts/core/logger.py`) provides the storage layer:

| Method | Description |
|--------|-------------|
| `log(event_type, data)` | Append a JSON line with `ts` and `type` fields |
| `read_all(max_records=10000)` | Read all records (oldest first), capped at 10,000 |
| `read_since(since_ts)` | Read records newer than a given timestamp |

Files are opened in append mode (`"a"`), making writes thread-safe on most operating systems. Records are never modified or deleted by Agent Ninja.

## Further Reading

- [Architecture](architecture.md) -- how the observer fits in the three-layer design
- [Privacy](privacy.md) -- what is and isn't stored
- [Strategist & Slash Commands](strategist.md) -- how observer data is analyzed
