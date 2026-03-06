---
name: ap:status
description: >
  Quick Agent Pilot dashboard showing sessions logged, routing
  stats, model distribution, and tool usage.
---

Run the Agent Pilot status check:

```bash
python3 scripts/run_command.py status
```

Display the results as a compact dashboard. If there's no data yet, let the user know they need to use Agent Pilot for a few sessions first.