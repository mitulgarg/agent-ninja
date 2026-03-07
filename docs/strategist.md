# Strategist & Slash Commands

The Strategist is Layer 3 of Agent Ninja. It provides on-demand analysis of accumulated session data through slash commands that Claude executes within its own session -- zero extra API cost.

## Slash Commands

### `/an:status`

Quick dashboard showing sessions logged, routing stats, model distribution, and tool usage.

Runs `python3 scripts/run_command.py status` under the hood, which calls `StrategistEngine.get_status()`.

Example output:

```
Sessions tracked: 12
Total prompts routed: 47
Data period: 3.2 days

Model distribution:
  haiku: 18
  sonnet: 22
  opus: 7

Pattern distribution:
  direct: 25
  plan-mode: 12
  subagent: 8
  skill-invocation: 2

Tool usage frequency:
  Edit: 89
  Read: 67
  Bash: 45
  Grep: 23

Bash command types:
  test: 15
  git: 12
  build: 8
  other: 10
```

### `/an:audit`

Environment health check. Gathers data via `run_command.py summary`, then Claude analyzes it to produce a structured report covering:

1. **Model Efficiency** -- Are expensive models used for simple tasks?
2. **Pattern Utilization** -- Are subagents, plan mode, and skills underused?
3. **Tool Patterns** -- Repetitive tool sequences that should be skills
4. **Self-Assessment Rate** -- Static rules vs. self-assessment fallback ratio
5. **Specific Recommendations** -- Ordered by expected impact

Claude also reads the raw JSONL logs at `.agent-ninja/data/routing.jsonl` and `.agent-ninja/data/sessions.jsonl` for deeper pattern detection.

### `/an:strategize`

Deep workflow analysis with actionable optimization proposals. Produces:

1. **Skills to Create** -- Repeated multi-step patterns with draft SKILL.md content
2. **Routing Rule Adjustments** -- New static rules for config.json
3. **Agent Team Opportunities** -- Sequential tasks that could be parallelized
4. **CLAUDE.md Improvements** -- Additions based on workflow patterns
5. **Context Waste** -- Loaded files/instructions that are rarely relevant

Each proposal includes the actual file content or config to create/modify.

### `/an:generate-skill`

Detects repeated workflow patterns and generates a complete SKILL.md file. The generated skill is saved to `.agent-ninja/proposed/skills/<skill-name>/SKILL.md` for human review.

## Data Aggregation

The `StrategistEngine.build_data_summary()` method (`scripts/strategist/engine.py`) aggregates JSONL logs into a privacy-safe statistical summary:

```json
{
  "total_sessions": 12,
  "total_prompts": 47,
  "model_distribution": {"haiku": 18, "sonnet": 22, "opus": 7},
  "pattern_distribution": {"direct": 25, "plan-mode": 12, "subagent": 8, "skill-invocation": 2},
  "tool_frequency": {"Edit": 89, "Read": 67, "Bash": 45, "Grep": 23},
  "command_types": {"test": 15, "git": 12, "build": 8, "other": 10},
  "data_period_days": 3.2
}
```

This summary contains only aggregate counts -- no prompt content, file paths, or command text.

## Proposed Skills Workflow

```
/an:generate-skill
        |
        v
StrategistEngine.save_proposed_skill()
        |
        v
.agent-ninja/proposed/skills/<name>/SKILL.md   (generated, needs review)
        |
        v
Human reviews the proposed skill
        |
        v
cp to ~/.claude/skills/<name>/SKILL.md         (activated)
```

Generated skills are always saved to the `proposed/` directory. They are **never automatically activated**. The user must review and manually copy them to their skills directory to enable them.

## The Strategist Subagent

The file `agents/strategist.md` defines a subagent prompt for deep analysis. When invoked via Claude's Agent tool, it provides thorough workflow analysis with full context of the JSONL log data, producing detailed recommendations that go beyond what the slash commands offer.

## Further Reading

- [Architecture](architecture.md) -- how the strategist fits in the three-layer design
- [Observer Reference](observer.md) -- the data that feeds the strategist
- [Configuration Reference](configuration.md) -- enabling/disabling the observer that collects data
