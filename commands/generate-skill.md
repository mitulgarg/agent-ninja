---
name: an:generate-skill
description: >
  Detect repeated workflow patterns and generate a SKILL.md file.
  Optionally takes a focus area as argument.
---

First, gather the session data:

```bash
python3 scripts/run_command.py summary
```

Then read the raw session logs at `.agent-ninja/data/sessions.jsonl` to identify repeated tool usage patterns.

Generate a complete SKILL.md file with:
- YAML frontmatter with name and description
- Clear instructions for when to use this skill
- Step-by-step workflow based on the observed pattern
- Any relevant context or configuration

Save the generated skill:

```bash
mkdir -p .agent-ninja/proposed/skills/<skill-name>
```

Then write the SKILL.md content to `.agent-ninja/proposed/skills/<skill-name>/SKILL.md`.

Tell the user to review the proposed skill and copy it to `.claude/skills/` to activate it.