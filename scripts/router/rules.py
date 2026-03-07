"""Fast pattern-matching rules that skip the LLM call entirely.

These handle obvious cases where classification is unambiguous."""

from __future__ import annotations

import re
from typing import Optional

from core.config import AgentNinjaConfig
from core.models import (
    AgentPattern,
    ModelTier,
    RoutingDecision,
    ThinkingLevel,
)

# Patterns that are clearly simple (Haiku-level)
HAIKU_PATTERNS = [
    r"^(format|lint|prettify|fix typo)",
    r"^(what is|explain|show me|list|read)\b",
    r"^(run tests?|npm test|pytest|make test)",
    r"^(git (status|log|diff|add|commit))",
]

# Patterns that clearly need deep reasoning (Opus-level)
OPUS_PATTERNS = [
    r"(architect|design|refactor.*entire|redesign)",
    r"(security (audit|review)|vulnerability)",
    r"(migrate|migration.*strategy)",
    r"(why (does|is|are).*broken|debug.*across.*files)",
]

# Patterns that should use plan mode
PLAN_PATTERNS = [
    r"(implement.*feature|add.*new.*feature|build.*system)",
    r"(refactor|rewrite).*multiple",
    r"(create.*from scratch|set up|initialize.*project)",
]


class StaticRules:
    """Pattern-based routing that skips the LLM call."""

    def __init__(self, config: AgentNinjaConfig):
        self.config = config
        self._opus_extra = [
            re.compile(p, re.IGNORECASE) for p in config.always_opus_for
        ]
        self._haiku_extra = [
            re.compile(p, re.IGNORECASE) for p in config.always_haiku_for
        ]

    def match(self, prompt: str) -> Optional[RoutingDecision]:
        """Check static rules. Returns None if no match (-> use LLM)."""
        lower = prompt.lower().strip()

        # User-defined overrides first
        for pat in self._opus_extra:
            if pat.search(lower):
                return RoutingDecision(
                    model=ModelTier.OPUS,
                    pattern=AgentPattern.PLAN_MODE,
                    thinking=ThinkingLevel.HIGH,
                    reasoning="Static rule: user override -> opus",
                )

        for pat in self._haiku_extra:
            if pat.search(lower):
                return RoutingDecision(
                    model=ModelTier.HAIKU,
                    pattern=AgentPattern.DIRECT,
                    thinking=ThinkingLevel.OFF,
                    reasoning="Static rule: user override -> haiku",
                )

        # Built-in haiku patterns
        for pat in HAIKU_PATTERNS:
            if re.search(pat, lower):
                return RoutingDecision(
                    model=ModelTier.HAIKU,
                    pattern=AgentPattern.DIRECT,
                    thinking=ThinkingLevel.OFF,
                    reasoning="Static rule: simple task pattern",
                )

        # Built-in opus patterns
        for pat in OPUS_PATTERNS:
            if re.search(pat, lower):
                return RoutingDecision(
                    model=ModelTier.OPUS,
                    pattern=AgentPattern.PLAN_MODE,
                    thinking=ThinkingLevel.HIGH,
                    reasoning="Static rule: complex task pattern",
                )

        # Built-in plan mode patterns
        for pat in PLAN_PATTERNS:
            if re.search(pat, lower):
                return RoutingDecision(
                    model=ModelTier.SONNET,
                    pattern=AgentPattern.PLAN_MODE,
                    thinking=ThinkingLevel.LOW,
                    reasoning="Static rule: multi-step task -> plan first",
                )

        return None
