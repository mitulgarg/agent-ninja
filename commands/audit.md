---
name: ap:audit
description: >
  Run an Agent Pilot environment health check. Analyzes routing
  accuracy, model efficiency, context waste, and feature utilization.
---

First, run this command to get the current Agent Pilot data:

```bash
python3 scripts/run_command.py summary
```

Then analyze the data and produce a structured audit report covering:

1. **Model Efficiency**: Are expensive models being used for simple tasks? What percentage of prompts could have used a cheaper model?
2. **Pattern Utilization**: Are subagents, plan mode, and skills being underused? What patterns dominate and are they appropriate?
3. **Tool Patterns**: Are there repetitive tool sequences that should be codified as skills?
4. **Self-Assessment Rate**: What percentage of prompts fell through to self-assessment vs. static rules?
5. **Specific Recommendations**: Ordered by expected impact, with concrete actions.

Also read the routing log at `.agent-pilot/data/routing.jsonl` and session log at `.agent-pilot/data/sessions.jsonl` for deeper patterns.

Present the audit as a clear, structured report. Highlight the most impactful recommendations first.