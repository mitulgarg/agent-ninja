#!/usr/bin/env python3
"""agent-pilot hook entry point.

Called by the host agent (Claude Code / Gemini CLI) for every
lifecycle event. Reads hook JSON from stdin, dispatches to the
appropriate engine, writes response to stdout.

Usage in hooks.json:
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/entrypoint.py"
"""

from __future__ import annotations

import os
import sys

# Ensure scripts/ is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.io import read_hook_input, write_hook_output, exit_allow


def main() -> None:
    try:
        _dispatch()
    except Exception as e:
        # Hooks must never crash — fail silently to stderr
        print(f"[agent-pilot] hook error: {e}", file=sys.stderr)
    exit_allow()


def _dispatch() -> None:
    hook_input = read_hook_input()
    event = hook_input.get("hook_event_name", "")

    project_dir = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.environ.get("GEMINI_PROJECT_DIR", os.getcwd()),
    )

    from core.config import AgentPilotConfig
    config = AgentPilotConfig.load(project_dir)

    # Dispatch based on event type
    if event in ("UserPromptSubmit", "BeforeModel"):
        _handle_user_prompt(hook_input, config, project_dir)

    elif event in ("PostToolUse", "AfterTool", "BeforeTool"):
        _handle_post_tool_use(hook_input, config, project_dir)

    elif event in ("Stop", "SubagentStop"):
        _handle_stop(hook_input, config, project_dir)

    elif event == "SessionStart":
        _handle_session_start(hook_input, config, project_dir)

    elif event == "SessionEnd":
        _handle_session_end(hook_input, config, project_dir)


def _handle_user_prompt(
    hook_input: dict,
    config: AgentPilotConfig,
    project_dir: str,
) -> None:
    """Route: classify the prompt and inject recommendation or self-assessment."""
    if not config.routing_enabled:
        return

    prompt = (
        hook_input.get("user_prompt", "")
        or hook_input.get("prompt", "")
    )
    if not prompt:
        return

    from router.engine import RouterEngine
    from core.logger import JsonlLogger

    router = RouterEngine(config, project_dir)
    decision = router.classify(prompt)

    if decision:
        # Static rule matched — inject direct recommendation
        write_hook_output(additional_context=decision.to_context_string())

        # Log the routing decision
        if config.observer_enabled:
            logger = JsonlLogger(config.data_dir / "routing.jsonl")
            logger.log("route", decision.to_dict())
    else:
        # No static match — inject self-assessment prompt for Claude
        write_hook_output(
            additional_context=router.get_self_assess_prompt()
        )

        # Log that self-assessment was triggered
        if config.observer_enabled:
            from core.models import hash_prompt
            logger = JsonlLogger(config.data_dir / "routing.jsonl")
            logger.log("self_assess", {
                "prompt_hash": hash_prompt(prompt),
                "model": "self",
                "pattern": "self-assess",
            })


def _handle_post_tool_use(
    hook_input: dict,
    config: AgentPilotConfig,
    project_dir: str,
) -> None:
    """Observe: capture tool usage metadata."""
    if not config.observer_enabled:
        return

    from observer.engine import ObserverEngine
    observer = ObserverEngine(config, project_dir)
    observer.record_tool_use(hook_input)


def _handle_stop(
    hook_input: dict,
    config: AgentPilotConfig,
    project_dir: str,
) -> None:
    """Observe: finalize session record on stop."""
    if not config.observer_enabled:
        return

    from observer.engine import ObserverEngine
    observer = ObserverEngine(config, project_dir)
    observer.finalize_session(hook_input)


def _handle_session_start(
    hook_input: dict,
    config: AgentPilotConfig,
    project_dir: str,
) -> None:
    """Initialize session tracking."""
    if not config.observer_enabled:
        return

    from observer.engine import ObserverEngine
    observer = ObserverEngine(config, project_dir)
    observer.start_session(hook_input)


def _handle_session_end(
    hook_input: dict,
    config: AgentPilotConfig,
    project_dir: str,
) -> None:
    """Cleanup and final logging."""
    if not config.observer_enabled:
        return

    from observer.engine import ObserverEngine
    observer = ObserverEngine(config, project_dir)
    observer.end_session(hook_input)


if __name__ == "__main__":
    main()