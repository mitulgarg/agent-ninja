# Routing Reference

The Router is Layer 1 of Agent Ninja. It classifies every user prompt and injects a recommendation (or self-assessment prompt) into the agent's context via `additionalContext`.

## How Routing Works

1. User submits a prompt in Claude Code / Gemini CLI
2. The host agent fires a `UserPromptSubmit` (or `BeforeModel`) hook
3. `entrypoint.py` dispatches to `_handle_user_prompt()`
4. `RouterEngine.classify()` checks static regex rules in priority order
5. If a rule matches: a `RoutingDecision` is created and injected as `additionalContext`
6. If no rule matches: the self-assessment prompt is injected instead
7. The routing decision (or self-assess event) is logged to `routing.jsonl`

## RoutingDecision

The `RoutingDecision` dataclass (`scripts/core/models.py`) contains:

| Field | Type | Description |
|-------|------|-------------|
| `model` | `ModelTier` | `haiku`, `sonnet`, or `opus` |
| `pattern` | `AgentPattern` | `direct`, `subagent`, `agent-team`, `skill-invocation`, or `plan-mode` |
| `thinking` | `ThinkingLevel` | `off`, `low`, or `high` |
| `skill_suggestion` | `str` (optional) | Name of a skill that handles this task |
| `reasoning` | `str` | Why this classification was chosen |
| `timestamp` | `float` | Unix timestamp of the decision |
| `prompt_hash` | `str` | SHA-256 hash (first 16 hex chars) of the prompt |
| `confidence` | `float` | Confidence score (0.0-1.0) |

## Built-in Regex Patterns

Rules are evaluated from `scripts/router/rules.py`. All matching is case-insensitive.

### Haiku Patterns (simple tasks)

| Pattern | Example matches |
|---------|----------------|
| `^(format\|lint\|prettify\|fix typo)` | "format this file", "lint the code" |
| `^(what is\|explain\|show me\|list\|read)\b` | "what is this function", "explain the error" |
| `^(run tests?\|npm test\|pytest\|make test)` | "run tests", "pytest -v" |
| `^(git (status\|log\|diff\|add\|commit))` | "git status", "git diff main" |

Result: `model=haiku, pattern=direct, thinking=off`

### Opus Patterns (complex tasks)

| Pattern | Example matches |
|---------|----------------|
| `(architect\|design\|refactor.*entire\|redesign)` | "architect a new auth system" |
| `(security (audit\|review)\|vulnerability)` | "security audit this codebase" |
| `(migrate\|migration.*strategy)` | "migrate from REST to GraphQL" |
| `(why (does\|is\|are).*broken\|debug.*across.*files)` | "why is the build broken" |

Result: `model=opus, pattern=plan-mode, thinking=high`

### Plan-Mode Patterns (multi-step tasks)

| Pattern | Example matches |
|---------|----------------|
| `(implement.*feature\|add.*new.*feature\|build.*system)` | "implement user auth feature" |
| `(refactor\|rewrite).*multiple` | "refactor multiple services" |
| `(create.*from scratch\|set up\|initialize.*project)` | "set up a new React project" |

Result: `model=sonnet, pattern=plan-mode, thinking=low`

## Rule Evaluation Order

Rules are evaluated in this priority order (first match wins):

1. **User opus overrides** -- `always_opus_for` patterns from config
2. **User haiku overrides** -- `always_haiku_for` patterns from config
3. **Built-in haiku patterns** -- `HAIKU_PATTERNS` list
4. **Built-in opus patterns** -- `OPUS_PATTERNS` list
5. **Built-in plan-mode patterns** -- `PLAN_PATTERNS` list
6. **Self-assessment fallback** -- no static match, inject self-assessment prompt

## User Overrides

Add custom patterns to `.agent-ninja/config.json`:

```json
{
  "routing": {
    "always_opus_for": ["security review", "architecture"],
    "always_haiku_for": ["format", "lint", "prettify"]
  }
}
```

User overrides are compiled as regex patterns and checked before built-in rules. `always_opus_for` patterns produce `model=opus, pattern=plan-mode, thinking=high`. `always_haiku_for` patterns produce `model=haiku, pattern=direct, thinking=off`.

## Self-Assessment Mechanism

When no static rule matches, Agent Ninja injects a self-assessment prompt into the agent's context. The full prompt text (from `scripts/router/engine.py`):

```
[Agent Ninja] No static routing rule matched this prompt.
Before proceeding, briefly self-assess this task:

1. **Model**: Would haiku (simple lookup/format/grep), sonnet (standard coding),
   or opus (multi-file architecture/complex debug/security review) be optimal?
2. **Pattern**: Should this be direct (inline), subagent (delegatable),
   agent-team (parallel), skill-invocation, or plan-mode (plan first)?
3. **Thinking**: Does this need extended thinking? (off/low/high)

State your assessment in one line, then proceed with execution.
If you determine a different model would be better, suggest the user switch
with `/model <tier>`. If plan-mode is warranted, suggest Shift+Tab twice.
```

This costs zero extra API calls -- Claude assesses the task within its own session context.

## additionalContext Injection

When a static rule matches, the routing decision is formatted via `to_context_string()` and injected as `additionalContext` in the hook output:

```json
{
  "hookSpecificOutput": {
    "additionalContext": "[Agent Ninja] Recommended: model=haiku, pattern=direct, thinking=off\nReasoning: Static rule: simple task pattern"
  }
}
```

### Context String Format

A typical context string looks like:

```
[Agent Ninja] Recommended: model=opus, pattern=plan-mode, thinking=high
Reasoning: Static rule: complex task pattern
```

With a skill suggestion:

```
[Agent Ninja] Recommended: model=sonnet, pattern=skill-invocation, thinking=low
Reasoning: Static rule: multi-step task -> plan first
Suggested skill: deploy-workflow
```

## Further Reading

- [Architecture](architecture.md) -- how routing fits in the three-layer design
- [Configuration](configuration.md) -- tuning routing rules
- [Privacy](privacy.md) -- how prompt hashes protect privacy
