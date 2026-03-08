"""Data aggregation for the strategist layer.

The actual analysis is done by Claude itself via slash commands.
This engine builds privacy-safe statistical summaries from JSONL logs
that Claude can then read and analyze within its own session."""

from __future__ import annotations

import json
from pathlib import Path

from core.config import AgentNinjaConfig
from core.logger import JsonlLogger


class StrategistEngine:
    """Aggregates session data for Claude to analyze via slash commands."""

    def __init__(self, config: AgentNinjaConfig, project_dir: str):
        self.config = config
        self.project_dir = project_dir
        self.sessions_log = JsonlLogger(config.data_dir / "sessions.jsonl")
        self.routing_log = JsonlLogger(config.data_dir / "routing.jsonl")

    def build_data_summary(self) -> dict:
        """Build a privacy-safe statistical summary from logs."""
        sessions = self.sessions_log.read_all()
        routing = self.routing_log.read_all()

        model_dist: dict[str, int] = {}
        pattern_dist: dict[str, int] = {}
        tool_freq: dict[str, int] = {}
        command_types: dict[str, int] = {}
        total_sessions = 0
        total_prompts = 0

        for record in routing:
            model = record.get("model", "unknown")
            model_dist[model] = model_dist.get(model, 0) + 1
            pattern = record.get("pattern", "unknown")
            pattern_dist[pattern] = pattern_dist.get(pattern, 0) + 1
            total_prompts += 1

        for record in sessions:
            if record.get("type") == "session_start":
                total_sessions += 1
            elif record.get("type") == "tool_use":
                tool = record.get("tool_name", "unknown")
                tool_freq[tool] = tool_freq.get(tool, 0) + 1
                cmd_type = record.get("command_type", "")
                if cmd_type:
                    command_types[cmd_type] = (
                        command_types.get(cmd_type, 0) + 1
                    )

        return {
            "total_sessions": total_sessions,
            "total_prompts": total_prompts,
            "model_distribution": model_dist,
            "pattern_distribution": pattern_dist,
            "tool_frequency": tool_freq,
            "command_types": command_types,
            "data_period_days": self._data_age_days(sessions + routing),
        }

    def get_status(self) -> str:
        """Quick status dashboard."""
        summary = self.build_data_summary()

        if not summary["total_sessions"] and not summary["total_prompts"]:
            return (
                "No session data collected yet. "
                "Use Agent Ninja for a few sessions first."
            )

        from strategist.prompts import format_data_summary
        return format_data_summary(summary)

    def save_proposed_skill(self, name: str, content: str) -> Path:
        """Save a proposed skill to the proposed/ directory."""
        skill_dir = self.config.proposed_dir / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(content)
        return skill_path

    def save_proposed_agent(self, name: str, content: str) -> Path:
        """Save a proposed agent to the proposed/ directory."""
        agents_dir = self.config.proposed_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        agent_path = agents_dir / f"{name}.md"
        agent_path.write_text(content)
        return agent_path

    def _data_age_days(self, records: list[dict]) -> float:
        if not records:
            return 0
        timestamps = [r.get("ts", 0) for r in records if r.get("ts")]
        if not timestamps:
            return 0
        return (max(timestamps) - min(timestamps)) / 86400