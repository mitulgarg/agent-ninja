"""End-to-end tests for the hook entrypoint."""

import subprocess
import json
import os
import tempfile
from pathlib import Path

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _run_entrypoint(fixture_name: str, env_overrides: dict = None) -> subprocess.CompletedProcess:
    """Run entrypoint.py with a fixture as stdin."""
    fixture_path = os.path.join(FIXTURES_DIR, fixture_name)
    with open(fixture_path) as f:
        fixture_data = f.read()

    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = tempfile.mkdtemp()
    if env_overrides:
        env.update(env_overrides)

    return subprocess.run(
        ["python3", os.path.join(SCRIPTS_DIR, "entrypoint.py")],
        input=fixture_data,
        capture_output=True,
        text=True,
        env=env,
    )


class TestEntrypointE2E:
    """Test the entrypoint with real fixture data."""

    def test_user_prompt_submit_with_static_match(self):
        """Prompt 'refactor the authentication module' should match opus pattern."""
        result = _run_entrypoint("user_prompt_submit.json")
        # Should exit cleanly
        assert result.returncode == 0
        # Should output JSON with additionalContext
        if result.stdout.strip():
            output = json.loads(result.stdout)
            assert "hookSpecificOutput" in output
            ctx = output["hookSpecificOutput"]["additionalContext"]
            assert "[Agent Ninja]" in ctx

    def test_post_tool_use(self):
        """PostToolUse should log to sessions.jsonl."""
        result = _run_entrypoint("post_tool_use.json")
        assert result.returncode == 0

    def test_stop_event(self):
        """Stop event should log session finalization."""
        result = _run_entrypoint("stop.json")
        assert result.returncode == 0

    def test_routing_disabled(self):
        """When routing is disabled, no additionalContext is injected."""
        result = _run_entrypoint(
            "user_prompt_submit.json",
            env_overrides={"AGENT_NINJA_ROUTING_ENABLED": "false"},
        )
        assert result.returncode == 0
        # Should not output any routing context
        assert result.stdout.strip() == ""

    def test_empty_stdin(self):
        """Empty stdin should not crash."""
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = tempfile.mkdtemp()

        result = subprocess.run(
            ["python3", os.path.join(SCRIPTS_DIR, "entrypoint.py")],
            input="",
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0

    def test_malformed_json_stdin(self):
        """Malformed JSON should not crash."""
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = tempfile.mkdtemp()

        result = subprocess.run(
            ["python3", os.path.join(SCRIPTS_DIR, "entrypoint.py")],
            input="not valid json {{{",
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0