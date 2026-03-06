"""Passive data capture from hook events. No API calls, no token cost.

Writes structured JSONL to disk for the strategist to analyze later."""

from __future__ import annotations

from core.config import AgentPilotConfig
from core.logger import JsonlLogger


class ObserverEngine:
    """Captures session metadata from hook events."""

    def __init__(self, config: AgentPilotConfig, project_dir: str):
        self.config = config
        self.sessions_log = JsonlLogger(config.data_dir / "sessions.jsonl")
        self.routing_log = JsonlLogger(config.data_dir / "routing.jsonl")

    def start_session(self, hook_input: dict) -> None:
        """Log session start."""
        self.sessions_log.log("session_start", {
            "session_id": hook_input.get("session_id", ""),
            "trigger": hook_input.get("trigger", ""),
        })

    def record_tool_use(self, hook_input: dict) -> None:
        """Capture tool usage from PostToolUse / AfterTool events."""
        tool_name = hook_input.get("tool_name", "unknown")
        tool_input = hook_input.get("tool_input", {})
        tool_response = hook_input.get("tool_response", {})

        event_data = {
            "session_id": hook_input.get("session_id", ""),
            "tool_name": tool_name,
            "success": True,
        }

        # Extract useful metadata without storing content
        if tool_name == "Bash":
            cmd = tool_input.get("command", "")
            event_data["command_type"] = _classify_command(cmd)
        elif tool_name in ("Write", "Edit", "MultiEdit"):
            event_data["file_ext"] = _get_extension(
                tool_input.get("file_path", "")
            )

        # Check for failure
        if isinstance(tool_response, dict):
            exit_code = tool_response.get("exit_code")
            if exit_code is not None and exit_code != 0:
                event_data["success"] = False

        self.sessions_log.log("tool_use", event_data)

    def finalize_session(self, hook_input: dict) -> None:
        """Log session stop/completion."""
        self.sessions_log.log("session_stop", {
            "session_id": hook_input.get("session_id", ""),
            "reason": hook_input.get("reason", ""),
        })

    def end_session(self, hook_input: dict) -> None:
        """Log session end (cleanup)."""
        self.sessions_log.log("session_end", {
            "session_id": hook_input.get("session_id", ""),
        })


def _classify_command(cmd: str) -> str:
    """Classify bash command type without storing the command."""
    cmd_lower = cmd.lower().strip()
    if any(t in cmd_lower for t in ["pytest", "npm test", "jest", "make test"]):
        return "test"
    if any(t in cmd_lower for t in ["npm run build", "make build", "cargo build"]):
        return "build"
    if any(t in cmd_lower for t in ["git "]):
        return "git"
    if any(t in cmd_lower for t in ["npm install", "pip install", "cargo add"]):
        return "install"
    if any(t in cmd_lower for t in ["curl ", "wget "]):
        return "network"
    return "other"


def _get_extension(file_path: str) -> str:
    """Extract file extension for analytics."""
    if "." in file_path:
        return file_path.rsplit(".", 1)[-1].lower()
    return ""
