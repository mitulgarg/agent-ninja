---
name: pilot-advisor
description: >
  Interprets Agent Pilot routing recommendations injected via hooks.
  When you see [Agent Pilot] context in the conversation, follow
  the model/pattern/thinking recommendations. Use when routing
  decisions appear in context, when deciding which model to use,
  or when considering subagents vs direct execution.
---

# Agent Pilot Advisor

When you see a message starting with `[Agent Pilot]` in the conversation
context, it contains an intelligent routing recommendation based on
analysis of the current prompt.

## How to interpret recommendations

The recommendation includes:
- **model**: Which model tier to use (haiku/sonnet/opus)
- **pattern**: Which execution pattern is optimal
- **thinking**: Extended thinking budget level
- **skill_suggestion**: An installed skill that matches (if any)

## Actions to take

1. If `model` differs from your current model, suggest switching:
   "Agent Pilot recommends using {model} for this task because: {reasoning}.
   You can switch with `/model {model}`."

2. If `pattern` is `subagent`, suggest delegation:
   "This task could be delegated to a subagent to save context tokens."

3. If `pattern` is `plan-mode`, suggest planning first:
   "Consider using plan mode (Shift+Tab twice) before executing."

4. If `pattern` is `agent-team`, suggest parallel execution:
   "This task has multiple independent components that could run in parallel."

5. If `skill_suggestion` is provided, suggest using it:
   "The {skill_name} skill is designed for this type of task."

6. If `thinking` is `off`, note that extended thinking can be disabled
   for this task to save tokens.

## Self-assessment mode

When the `[Agent Pilot]` context asks you to self-assess, briefly evaluate
the task complexity before proceeding:
- State your model/pattern/thinking assessment in one line
- If you determine a different model would be better, suggest switching
- Then proceed with execution immediately

## When auto_switch is enabled

If the user has enabled auto_switch in their agent-pilot config,
act on the recommendation directly without asking for confirmation.