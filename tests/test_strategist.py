"""Tests for the strategist engine."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from core.config import AgentPilotConfig
from core.logger import JsonlLogger
from strategist.engine import StrategistEngine
from strategist.prompts import format_data_summary


class TestStrategistEngine:
    """Test data aggregation and summary building."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config = AgentPilotConfig(
            data_dir=Path(self.tmpdir) / "data",
            proposed_dir=Path(self.tmpdir) / "proposed",
        )
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        self.config.proposed_dir.mkdir(parents=True, exist_ok=True)
        self.engine = StrategistEngine(self.config, self.tmpdir)

    def test_empty_data_summary(self):
        summary = self.engine.build_data_summary()
        assert summary["total_sessions"] == 0
        assert summary["total_prompts"] == 0

    def test_status_no_data(self):
        status = self.engine.get_status()
        assert "No session data" in status

    def test_data_summary_with_routing(self):
        logger = JsonlLogger(self.config.data_dir / "routing.jsonl")
        logger.log("route", {"model": "haiku", "pattern": "direct"})
        logger.log("route", {"model": "sonnet", "pattern": "plan-mode"})
        logger.log("route", {"model": "haiku", "pattern": "direct"})

        summary = self.engine.build_data_summary()
        assert summary["total_prompts"] == 3
        assert summary["model_distribution"]["haiku"] == 2
        assert summary["model_distribution"]["sonnet"] == 1

    def test_data_summary_with_sessions(self):
        logger = JsonlLogger(self.config.data_dir / "sessions.jsonl")
        logger.log("session_start", {"session_id": "s1"})
        logger.log("tool_use", {
            "session_id": "s1",
            "tool_name": "Bash",
            "command_type": "test",
        })
        logger.log("tool_use", {
            "session_id": "s1",
            "tool_name": "Edit",
        })
        logger.log("tool_use", {
            "session_id": "s1",
            "tool_name": "Bash",
            "command_type": "git",
        })

        summary = self.engine.build_data_summary()
        assert summary["total_sessions"] == 1
        assert summary["tool_frequency"]["Bash"] == 2
        assert summary["tool_frequency"]["Edit"] == 1
        assert summary["command_types"]["test"] == 1
        assert summary["command_types"]["git"] == 1

    def test_save_proposed_skill(self):
        path = self.engine.save_proposed_skill(
            "test-skill",
            "# Test Skill\nSome content",
        )
        assert path.exists()
        assert path.read_text() == "# Test Skill\nSome content"
        assert "proposed/skills/test-skill/SKILL.md" in str(path)

    def test_status_with_data(self):
        logger = JsonlLogger(self.config.data_dir / "sessions.jsonl")
        logger.log("session_start", {"session_id": "s1"})
        routing_logger = JsonlLogger(self.config.data_dir / "routing.jsonl")
        routing_logger.log("route", {"model": "haiku", "pattern": "direct"})

        status = self.engine.get_status()
        assert "Sessions tracked: 1" in status
        assert "Total prompts routed: 1" in status


class TestFormatDataSummary:
    """Test the data formatting helper."""

    def test_format_empty(self):
        result = format_data_summary({
            "total_sessions": 0,
            "total_prompts": 0,
            "data_period_days": 0,
            "model_distribution": {},
            "pattern_distribution": {},
            "tool_frequency": {},
            "command_types": {},
        })
        assert "Sessions tracked: 0" in result

    def test_format_with_data(self):
        result = format_data_summary({
            "total_sessions": 5,
            "total_prompts": 42,
            "data_period_days": 3.5,
            "model_distribution": {"haiku": 20, "sonnet": 18, "opus": 4},
            "pattern_distribution": {"direct": 30, "plan-mode": 12},
            "tool_frequency": {"Bash": 50, "Edit": 30, "Read": 20},
            "command_types": {"test": 15, "git": 10},
        })
        assert "Sessions tracked: 5" in result
        assert "haiku: 20" in result
        assert "Bash: 50" in result