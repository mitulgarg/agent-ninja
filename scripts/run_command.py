#!/usr/bin/env python3
"""CLI entry point for Agent Pilot slash commands.

Usage:
  python3 scripts/run_command.py status
  python3 scripts/run_command.py summary

These are invoked by Claude Code slash commands (/ap:audit, /ap:status, etc.)
The actual deep analysis is done by Claude reading the output —
this script just prepares the data."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: run_command.py <command>")
        print("Commands: status, summary")
        sys.exit(1)

    command = sys.argv[1]
    project_dir = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.environ.get("GEMINI_PROJECT_DIR", os.getcwd()),
    )

    from core.config import AgentPilotConfig
    config = AgentPilotConfig.load(project_dir)

    from strategist.engine import StrategistEngine
    engine = StrategistEngine(config, project_dir)

    if command == "status":
        print(engine.get_status())
    elif command == "summary":
        import json
        print(json.dumps(engine.build_data_summary(), indent=2))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()