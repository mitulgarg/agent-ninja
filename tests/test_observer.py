"""Tests for the observer engine."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from core.config import AgentNinjaConfig
from observer.engine import ObserverEngine, _classify_command, _get_extension


class TestObserverEngine:
    """Test passive session data capture."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config = AgentNinjaConfig(
            data_dir=Path(self.tmpdir) / "data",
            proposed_dir=Path(self.tmpdir) / "proposed",
        )
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        self.engine = ObserverEngine(self.config, self.tmpdir)

    def test_start_session_logs(self):
        self.engine.start_session({
            "session_id": "test-123",
            "trigger": "manual",
        })
        log_file = self.config.data_dir / "sessions.jsonl"
        assert log_file.exists()
        records = [json.loads(l) for l in log_file.read_text().splitlines()]
        assert len(records) == 1
        assert records[0]["type"] == "session_start"
        assert records[0]["session_id"] == "test-123"

    def test_record_tool_use_logs(self):
        self.engine.record_tool_use({
            "session_id": "test-123",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"exit_code": 0},
        })
        log_file = self.config.data_dir / "sessions.jsonl"
        records = [json.loads(l) for l in log_file.read_text().splitlines()]
        assert len(records) == 1
        assert records[0]["type"] == "tool_use"
        assert records[0]["tool_name"] == "Bash"
        assert records[0]["command_type"] == "test"
        assert records[0]["success"] is True

    def test_record_tool_use_failure(self):
        self.engine.record_tool_use({
            "session_id": "test-123",
            "tool_name": "Bash",
            "tool_input": {"command": "npm test"},
            "tool_response": {"exit_code": 1},
        })
        log_file = self.config.data_dir / "sessions.jsonl"
        records = [json.loads(l) for l in log_file.read_text().splitlines()]
        assert records[0]["success"] is False

    def test_record_file_edit(self):
        self.engine.record_tool_use({
            "session_id": "test-123",
            "tool_name": "Edit",
            "tool_input": {"file_path": "/src/main.py"},
        })
        log_file = self.config.data_dir / "sessions.jsonl"
        records = [json.loads(l) for l in log_file.read_text().splitlines()]
        assert records[0]["file_ext"] == "py"

    def test_finalize_session_logs(self):
        self.engine.finalize_session({
            "session_id": "test-123",
            "reason": "user_requested",
        })
        log_file = self.config.data_dir / "sessions.jsonl"
        records = [json.loads(l) for l in log_file.read_text().splitlines()]
        assert records[0]["type"] == "session_stop"

    def test_end_session_logs(self):
        self.engine.end_session({"session_id": "test-123"})
        log_file = self.config.data_dir / "sessions.jsonl"
        records = [json.loads(l) for l in log_file.read_text().splitlines()]
        assert records[0]["type"] == "session_end"


class TestCommandClassification:
    """Test bash command type classification."""

    def test_test_commands(self):
        assert _classify_command("pytest tests/ -v") == "test"
        assert _classify_command("npm test") == "test"
        assert _classify_command("jest --watch") == "test"

    def test_build_commands(self):
        assert _classify_command("npm run build") == "build"
        assert _classify_command("cargo build --release") == "build"

    def test_git_commands(self):
        assert _classify_command("git status") == "git"
        assert _classify_command("git diff HEAD") == "git"

    def test_install_commands(self):
        assert _classify_command("pip install flask") == "install"
        assert _classify_command("npm install express") == "install"

    def test_network_commands(self):
        assert _classify_command("curl https://example.com") == "network"
        assert _classify_command("wget file.zip") == "network"

    def test_other_commands(self):
        assert _classify_command("ls -la") == "other"
        assert _classify_command("echo hello") == "other"


class TestGetExtension:
    def test_python_file(self):
        assert _get_extension("/src/main.py") == "py"

    def test_typescript_file(self):
        assert _get_extension("/src/index.ts") == "ts"

    def test_no_extension(self):
        assert _get_extension("Makefile") == ""

    def test_nested_dots(self):
        assert _get_extension("/src/test.spec.ts") == "ts"