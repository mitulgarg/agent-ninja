"""The router classifies each user prompt and recommends:
  - Which model to use (haiku/sonnet/opus)
  - Which agent pattern (direct/subagent/agent-team/skill/plan-mode)
  - Thinking budget (off/low/high)
  - Optional skill suggestion

When static regex rules match, the recommendation is injected directly.
When no rule matches, a self-assessment prompt is injected so Claude
classifies the task itself within its own session (zero extra API cost)."""

from __future__ import annotations

from typing import Optional

from core.config import AgentPilotConfig
from core.models import (
    RoutingDecision,
    hash_prompt,
)
from router.rules import StaticRules

SELF_ASSESS_PROMPT = """[Agent Pilot] No static routing rule matched this prompt. \
Before proceeding, briefly self-assess this task:

1. **Model**: Would haiku (simple lookup/format/grep), sonnet (standard coding), \
or opus (multi-file architecture/complex debug/security review) be optimal?
2. **Pattern**: Should this be direct (inline), subagent (delegatable), \
agent-team (parallel), skill-invocation, or plan-mode (plan first)?
3. **Thinking**: Does this need extended thinking? (off/low/high)

State your assessment in one line, then proceed with execution. \
If you determine a different model would be better, suggest the user switch \
with `/model <tier>`. If plan-mode is warranted, suggest Shift+Tab twice."""


class RouterEngine:
    """Classifies prompts via static rules or self-assessment injection."""

    def __init__(self, config: AgentPilotConfig, project_dir: str):
        self.config = config
        self.project_dir = project_dir
        self.rules = StaticRules(config)

    def classify(self, prompt: str) -> Optional[RoutingDecision]:
        """Check static rules. Returns RoutingDecision if matched, None otherwise."""
        static = self.rules.match(prompt)
        if static:
            static.prompt_hash = hash_prompt(prompt)
            return static
        return None

    def get_self_assess_prompt(self) -> str:
        """Return the self-assessment prompt for ambiguous cases."""
        return SELF_ASSESS_PROMPT
