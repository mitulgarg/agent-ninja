# System Architecture

Agent Ninja is a three-layer plugin that hooks into AI coding agents (Claude Code, Gemini CLI) to route prompts, observe workflows, and optimize development patterns.

## Three-Layer Design

```
                        Host Agent (Claude Code / Gemini CLI)
                                      |
                              Hook Event (stdin JSON)
                                      |
                                      v
                        +---------------------------+
                        |    scripts/entrypoint.py   |
                        |   (single entry point)     |
                        +---------------------------+
                           /         |          \
                          v          v           v
                    +---------+ +---------+ +-----------+
                    | Router  | |Observer | |Strategist |
                    | Layer 1 | |Layer 2  | | Layer 3   |
                    +---------+ +---------+ +-----------+
                         |           |            |
                         v           v            v
                    stdout JSON   JSONL append   JSONL read
                    (inject ctx)  (sessions.jsonl (slash commands
                                  routing.jsonl)  analyze data)
```

| Layer | Purpose | When it runs | Cost |
|-------|---------|-------------|------|
| **Router** | Classify prompts and recommend model/pattern/thinking | Every `UserPromptSubmit` | Zero (regex + context injection) |
| **Observer** | Capture tool usage and session metadata | Every `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd` | Zero (JSONL append) |
| **Strategist** | Analyze accumulated data, generate insights | On-demand via `/an:*` slash commands | Zero (Claude's own session) |

## Single Entry Point

All hook events flow through `scripts/entrypoint.py`. It reads JSON from stdin, determines the event type, and dispatches to the appropriate handler:

| Event Name | Handler | Layer |
|-----------|---------|-------|
| `UserPromptSubmit` / `BeforeModel` | `_handle_user_prompt()` | Router |
| `PostToolUse` / `AfterTool` / `BeforeTool` | `_handle_post_tool_use()` | Observer |
| `Stop` / `SubagentStop` | `_handle_stop()` | Observer |
| `SessionStart` | `_handle_session_start()` | Observer |
| `SessionEnd` | `_handle_session_end()` | Observer |

The entry point handles both Claude Code and Gemini CLI event names (e.g., `PostToolUse` and `AfterTool` both route to the same handler).

## Hook Lifecycle

A typical session flows through these events in order:

```
SessionStart
    |
    v
UserPromptSubmit  -----> Router classifies, injects context
    |
    v
PostToolUse x N   -----> Observer records tool metadata
    |
    v
Stop              -----> Observer logs session finalization
    |
    v
UserPromptSubmit  -----> (next prompt cycle)
    ...
    |
    v
SessionEnd        -----> Observer logs session cleanup
```

Each event is independent -- the entry point reads config fresh each time and does not maintain in-memory state between hook invocations.

## Data Flow

**Input:** The host agent pipes a JSON object to stdin with fields like `hook_event_name`, `session_id`, `user_prompt`, `tool_name`, `tool_input`, and `tool_response`.

**Output (Router):** Writes a JSON object to stdout with `hookSpecificOutput.additionalContext` containing the routing recommendation (or self-assessment prompt).

**Output (Observer):** Appends a JSON line to `.agent-ninja/data/sessions.jsonl` or `.agent-ninja/data/routing.jsonl`. No stdout output.

**Output (Strategist):** Reads JSONL logs and formats summaries. Invoked via `run_command.py`, not via hooks.

## Error Handling

Hooks must never crash the host agent. The entry point wraps all dispatch logic in a try/except:

```python
def main() -> None:
    try:
        _dispatch()
    except Exception as e:
        print(f"[agent-ninja] hook error: {e}", file=sys.stderr)
    exit_allow()
```

Any error is logged to stderr and the hook exits with code 0 (allow), ensuring the host agent continues normally.

## Layer Independence

Each layer operates independently:

- **Router** reads the prompt and writes to stdout. It also logs to `routing.jsonl` if the observer is enabled, but does not depend on observer state.
- **Observer** reads hook event data and appends to JSONL files. It does not depend on router decisions.
- **Strategist** reads JSONL files on demand. It does not participate in the hook lifecycle.

This means any layer can be disabled independently via configuration without affecting the others.

## Further Reading

- [Routing Reference](routing.md) -- how prompts are classified
- [Observer Reference](observer.md) -- what data is captured
- [Strategist & Slash Commands](strategist.md) -- on-demand analysis
- [Configuration Reference](configuration.md) -- tuning each layer
- [Platform Support](platforms.md) -- Claude Code vs Gemini CLI differences
