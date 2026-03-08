---
name: an:generate-agent
description: >
  Detect complex multi-step or parallelizable patterns in session data
  and generate a subagent definition (.md file).
  Optionally takes a focus area as argument.
---

First, gather the session data:

```bash
python3 scripts/run_command.py summary
```

Then read the raw session logs at `.agent-ninja/data/sessions.jsonl` to identify:

1. **Long sequential tool chains** — sessions where 5+ tool calls ran back-to-back on a single concern (e.g., read → grep → read → edit → test). These are candidates for a focused subagent.
2. **Repeated multi-file patterns** — the same combination of files or directories touched across multiple sessions.
3. **Parallelizable work** — tasks where independent subtasks (e.g., test suite + lint + type check) were done sequentially but could run as parallel subagents.

Generate a complete agent definition `.md` file with:

- YAML frontmatter with `name` and `description`
- A clear system prompt explaining the agent's role and scope
- What tools the agent should use and in what order
- What inputs the agent expects (file paths, error messages, etc.)
- What output the agent should return
- Guardrails — what the agent should NOT do (e.g., "do not modify files outside of X")

Example structure:

```markdown
---
name: <agent-name>
description: >
  <One-line description of what this agent does>
---

You are a specialized agent for <purpose>.

## When to use this agent
<criteria for when this agent should be invoked>

## Inputs
<what context/arguments this agent expects>

## Workflow
1. <step 1>
2. <step 2>
...

## Output
<what to return to the caller>

## Guardrails
- <constraint 1>
- <constraint 2>
```

Save the generated agent:

```bash
mkdir -p .agent-ninja/proposed/agents
```

Then write the agent definition to `.agent-ninja/proposed/agents/<agent-name>.md`.

Tell the user to review the proposed agent and copy it to `.claude/agents/` to activate it.