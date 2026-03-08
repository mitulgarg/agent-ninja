---
name: an:strategize
description: >
  Deep workflow analysis with actionable optimization proposals.
  Analyzes accumulated session data and suggests skills to create,
  routing rule adjustments, and CLAUDE.md improvements.
---

First, gather the data:

```bash
python3 scripts/run_command.py summary
```

Then read the raw logs for deeper analysis:
- `.agent-ninja/data/routing.jsonl` — all routing decisions
- `.agent-ninja/data/sessions.jsonl` — all session events

Analyze the workflow patterns and produce actionable proposals:

1. **Skills to Create**: Identify repeated multi-step patterns that should become skills. For each, draft the actual SKILL.md content.
2. **Routing Rule Adjustments**: Suggest new static rules for the user's `.agent-ninja/config.json` based on patterns in self-assessment data.
3. **Agent Generation Opportunities**: Identify tasks that were done sequentially but could benefit from parallel subagents, or long tool chains that should be encapsulated into a focused agent. Suggest running `/an:generate-agent` for promising candidates.
4. **CLAUDE.md Improvements**: Suggest additions to the user's CLAUDE.md based on workflow patterns.
5. **Context Waste**: Identify files/instructions that are loaded but rarely relevant.

For each proposal, include the actual file content or config that should be created/modified.