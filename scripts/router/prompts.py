"""Prompt templates for Agent Pilot routing.

The self-assessment prompt is in engine.py (injected via additionalContext).
The classification prompt template below is used by the CLAUDE.md instruction
that teaches Claude how to self-assess tasks."""

from __future__ import annotations

CLASSIFICATION_GUIDE = """
Classification dimensions for self-assessment:

model -- which model should handle this:
  "haiku"  -> simple lookups, file reads, formatting, grep, run tests, git status
  "sonnet" -> standard coding, single-file work, writing tests, most daily tasks
  "opus"   -> multi-file architecture, complex debugging, system design, security review

pattern -- which agent pattern is optimal:
  "direct"           -> simple self-contained task, no orchestration needed
  "subagent"         -> delegatable subtask (run tests, fetch docs, lint)
  "agent-team"       -> multi-component parallel work across different concerns
  "skill-invocation" -> an installed skill handles this exactly
  "plan-mode"        -> complex task that needs planning before execution

thinking -- extended thinking budget:
  "off"  -> mechanical tasks, no reasoning needed
  "low"  -> standard coding, moderate reasoning
  "high" -> architecture decisions, complex debugging, novel problems
"""
