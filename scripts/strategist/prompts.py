"""Prompt guidance for strategist slash commands.

The actual LLM analysis is done by Claude itself when the user
invokes /ap:audit, /ap:strategize, or /ap:generate-skill.
These are Claude Code command definitions (.md files in commands/).

This module provides data formatting helpers used by run_command.py
to prepare session data for Claude to analyze."""

from __future__ import annotations

import json
from typing import Any


def format_data_summary(summary: dict[str, Any]) -> str:
    """Format a data summary as readable text for Claude to analyze."""
    lines = [
        f"Sessions tracked: {summary.get('total_sessions', 0)}",
        f"Total prompts routed: {summary.get('total_prompts', 0)}",
        f"Data period: {summary.get('data_period_days', 0):.1f} days",
        "",
        "Model distribution:",
    ]

    for model, count in summary.get("model_distribution", {}).items():
        lines.append(f"  {model}: {count}")

    lines.append("")
    lines.append("Pattern distribution:")
    for pattern, count in summary.get("pattern_distribution", {}).items():
        lines.append(f"  {pattern}: {count}")

    lines.append("")
    lines.append("Tool usage frequency:")
    for tool, count in sorted(
        summary.get("tool_frequency", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        lines.append(f"  {tool}: {count}")

    lines.append("")
    lines.append("Bash command types:")
    for cmd_type, count in summary.get("command_types", {}).items():
        lines.append(f"  {cmd_type}: {count}")

    return "\n".join(lines)