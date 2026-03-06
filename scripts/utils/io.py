"""Handles reading JSON from stdin and writing hook output to stdout.

This is the contract between the agent (Claude Code / Gemini CLI)
and our hook scripts."""

from __future__ import annotations

import json
import sys
from typing import Optional


def read_hook_input() -> dict:
    """Read JSON from stdin (piped by the host agent)."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except (json.JSONDecodeError, IOError):
        return {}


def write_hook_output(
    additional_context: Optional[str] = None,
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    system_message: Optional[str] = None,
    continue_flag: Optional[bool] = None,
) -> None:
    """Write structured JSON to stdout for the host agent.

    For UserPromptSubmit: additional_context is injected into
    the conversation before the agent processes the prompt.

    For Stop: decision="block" prevents the agent from stopping.
    """
    output: dict = {}

    if additional_context:
        output["hookSpecificOutput"] = {
            "additionalContext": additional_context,
        }

    if decision:
        output["decision"] = decision
        if reason:
            output["reason"] = reason

    if system_message:
        output["systemMessage"] = system_message

    if continue_flag is not None:
        output["continue"] = continue_flag

    if output:
        print(json.dumps(output), flush=True)


def exit_allow() -> None:
    """Exit 0 = allow, continue normally."""
    sys.exit(0)


def exit_block(message: str) -> None:
    """Exit 2 = block the action. Message goes to stderr."""
    print(message, file=sys.stderr)
    sys.exit(2)