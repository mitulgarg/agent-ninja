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
3. **Agent Generation Opportunities** -- Sequential tasks that could be parallelized or long tool chains that should be encapsulated into a focused subagent. Flags candidates for `/an:generate-agent`.
4. **CLAUDE.md Improvements** -- Additions based on workflow patterns
5. **Context Waste** -- Loaded files/instructions that are rarely relevant

Each proposal includes the actual file content or config to create/modify.

### `/an:generate-skill`

Detects repeated workflow patterns and generates a complete SKILL.md file. The generated skill is saved to `.agent-ninja/proposed/skills/<skill-name>/SKILL.md` for human review.

### `/an:generate-agent`

Detects complex workflow patterns that warrant a dedicated subagent and generates a complete agent definition `.md` file. Claude looks for:

- **Long sequential tool chains** — 5+ tool calls on a single concern (e.g. read → grep → read → edit → test) that belong in a focused subagent
- **Repeated multi-file patterns** — the same file/directory combinations touched across multiple sessions
- **Parallelizable work** — sequential tasks (e.g. test + lint + type-check) that could run as parallel subagents

The generated agent definition includes YAML frontmatter, a system prompt, workflow steps, expected inputs/outputs, and guardrails. It is saved to `.agent-ninja/proposed/agents/<agent-name>.md` for human review.

To activate: copy the proposed file to `.claude/agents/`.

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

## Proposed Artifacts Workflow

Both `/an:generate-skill` and `/an:generate-agent` follow the same **proposed, not applied** pattern:

```
/an:generate-skill                        /an:generate-agent
        |                                         |
        v                                         v
save_proposed_skill()                   save_proposed_agent()
        |                                         |
        v                                         v
proposed/skills/<name>/SKILL.md         proposed/agents/<name>.md
        |                                         |
        v                                         v
Human reviews                           Human reviews
        |                                         |
        v                                         v
cp to .claude/skills/<name>/SKILL.md    cp to .claude/agents/<name>.md
        (activated)                               (activated)
```

Generated artifacts are always saved to the `proposed/` directory. They are **never automatically activated**. The user must review and manually copy them to enable them.

## The Strategist Subagent

The file `agents/strategist.md` defines a subagent prompt for deep analysis. When invoked via Claude's Agent tool, it provides thorough workflow analysis with full context of the JSONL log data, producing detailed recommendations that go beyond what the slash commands offer.

## Further Reading

- [Architecture](architecture.md) -- how the strategist fits in the three-layer design
- [Observer Reference](observer.md) -- the data that feeds the strategist
- [Configuration Reference](configuration.md) -- enabling/disabling the observer that collects data
