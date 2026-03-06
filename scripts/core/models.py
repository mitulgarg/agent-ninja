"""All data structures used across agent-pilot.

Pure dataclasses, no dependencies."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class ModelTier(str, Enum):
    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"


class AgentPattern(str, Enum):
    DIRECT = "direct"
    SUBAGENT = "subagent"
    AGENT_TEAM = "agent-team"
    SKILL_INVOKE = "skill-invocation"
    PLAN_MODE = "plan-mode"


class ThinkingLevel(str, Enum):
    OFF = "off"
    LOW = "low"
    HIGH = "high"


@dataclass
class RoutingDecision:
    """Output of the router classification."""

    model: ModelTier
    pattern: AgentPattern
    thinking: ThinkingLevel
    skill_suggestion: Optional[str] = None
    reasoning: str = ""
    timestamp: float = field(default_factory=time.time)
    prompt_hash: str = ""
    confidence: float = 0.0

    def to_context_string(self) -> str:
        """Format as additionalContext for the agent."""
        lines = [
            f"[Agent Pilot] Recommended: model={self.model.value}, "
            f"pattern={self.pattern.value}, thinking={self.thinking.value}",
            f"Reasoning: {self.reasoning}",
        ]
        if self.skill_suggestion:
            lines.append(f"Suggested skill: {self.skill_suggestion}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["model"] = self.model.value
        d["pattern"] = self.pattern.value
        d["thinking"] = self.thinking.value
        return d


@dataclass
class ToolUseEvent:
    """Captured from PostToolUse hooks."""

    tool_name: str
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    duration_ms: Optional[float] = None
    file_path: Optional[str] = None
    command: Optional[str] = None


@dataclass
class SessionRecord:
    """Accumulated per-session data."""

    session_id: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    routing_decisions: list[RoutingDecision] = field(default_factory=list)
    tool_events: list[ToolUseEvent] = field(default_factory=list)
    model_overrides: int = 0
    compact_count: int = 0
    prompt_count: int = 0

    @property
    def duration_s(self) -> Optional[float]:
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_s": self.duration_s,
            "prompt_count": self.prompt_count,
            "tool_events": len(self.tool_events),
            "routing_decisions": len(self.routing_decisions),
            "model_overrides": self.model_overrides,
            "compact_count": self.compact_count,
            "tools_used": list({e.tool_name for e in self.tool_events}),
            "model_distribution": self._model_distribution(),
        }

    def _model_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for rd in self.routing_decisions:
            dist[rd.model.value] = dist.get(rd.model.value, 0) + 1
        return dist


@dataclass
class AuditReport:
    """Output of the /ap:audit command."""

    timestamp: float = field(default_factory=time.time)
    sessions_analyzed: int = 0
    routing_accuracy: float = 0.0
    model_distribution: dict[str, float] = field(default_factory=dict)
    pattern_distribution: dict[str, float] = field(default_factory=dict)
    estimated_savings_pct: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    context_waste: list[str] = field(default_factory=list)


def hash_prompt(prompt: str) -> str:
    """Privacy-safe prompt hash. No content stored."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]
