# Agent Ninja — End-to-End Walkthrough

This guide shows what actually happens when you use Agent Ninja — from setup to routing to strategy — with real example output at each step.

---

## 1. Setup

Clone and run the installer:

```bash
git clone https://github.com/mitulgarg/agent-ninja
cd agent-ninja
bash install.sh
```

The installer asks:

```
Agent Ninja installer
Repo path: /Users/alice/tools/agent-ninja

Where do you want to install the hooks?
  1) Global  — ~/.claude/hooks.json (all Claude Code sessions)
  2) Project — .claude/hooks.json   (current directory only)

Enter 1 or 2: 1

Installing to: /Users/alice/.claude/hooks.json

Done! Hooks installed to /Users/alice/.claude/hooks.json

Next steps:
  1. Add the Agent Ninja instructions to your CLAUDE.md
     See SETUP.md for the copy-paste block.
  2. Start a Claude Code session and try a prompt.
     You should see [Agent Ninja] context in the response.
```

After adding the CLAUDE.md block (see `SETUP.md`), restart Claude Code.

---

## 2. Routing in Action

Every prompt you send triggers the router hook before Claude sees it. Here's what happens behind the scenes for three different prompts:

### Simple task → Haiku

You type:
```
run tests
```

The `UserPromptSubmit` hook fires. The router matches the static rule `run tests → haiku`:

```json
{
  "model": "haiku",
  "pattern": "direct",
  "thinking": "off",
  "method": "static",
  "rule_matched": "run_tests"
}
```

Claude receives the prompt with this injected at the top:

```
[Agent Ninja] Recommended: model=haiku, pattern=direct, thinking=off
```

Claude responds:
```
[Agent Ninja] Routing: haiku/direct — acknowledged.

Running tests now...
```

---

### Complex task → Opus + Plan Mode

You type:
```
architect a new authentication system with OAuth2 and refresh tokens
```

No static rule matches exactly, but the self-assessment injection fires:

```
[Agent Ninja] No static routing rule matched. Please briefly self-assess
before proceeding: what model tier, agent pattern, and thinking level
does this task warrant?
```

Claude responds:
```
[Agent Ninja] Self-assessment: model=opus, pattern=plan-mode, thinking=high
— this is a complex architectural decision with security implications.

Switching to /model opus recommended before proceeding.

Here's the plan:
1. Define the OAuth2 flow (authorization code + PKCE)
2. Design the token storage schema
3. Implement refresh token rotation
...
```

---

### Routine task → Haiku + Direct

You type:
```
format this file
```

Router matches `format → haiku, direct, thinking=off`. Claude gets the context and responds without ceremony:

```
[Agent Ninja] haiku/direct — formatting.
```

---

## 3. Observer Logging

After a few sessions, your `.agent-ninja/data/` directory fills up:

```
.agent-ninja/
└── data/
    ├── routing.jsonl      ← one line per prompt routed
    └── sessions.jsonl     ← tool usage, session start/stop events
```

A routing entry looks like this (prompts are never stored, only hashes):

```json
{
  "ts": 1741420800,
  "type": "route",
  "prompt_hash": "a3f5c2...",
  "model": "haiku",
  "pattern": "direct",
  "thinking": "off",
  "method": "static",
  "rule_matched": "run_tests",
  "session_id": "sess_abc123"
}
```

A session tool-use entry:

```json
{
  "ts": 1741420812,
  "type": "tool_use",
  "tool_name": "Bash",
  "command_type": "test",
  "file_ext": null,
  "session_id": "sess_abc123"
}
```

No prompt text, no file contents, no command arguments — just metadata.

---

## 4. Slash Commands in Action

### `/an:status` — Quick Dashboard

```
Sessions tracked: 12
Total prompts routed: 47
Data period: 3.2 days

Model distribution:
  haiku: 18
  sonnet: 22
  opus: 7

Pattern distribution:
  direct: 25
  plan-mode: 12
  subagent: 8
  skill-invocation: 2

Tool usage frequency:
  Edit: 89
  Read: 67
  Bash: 45
  Grep: 23

Bash command types:
  test: 15
  git: 12
  build: 8
  other: 10
```

---

### `/an:audit` — Environment Health Check

Claude reads the logs and produces a structured report:

```
## Agent Ninja Audit Report

### Model Efficiency
- 7 opus calls detected. 3 were for tasks matching "explain" or "summarize"
  — these could be served by sonnet. Consider adding rules to config.json.

### Pattern Utilization
- plan-mode used in 25% of prompts. Subagent pattern used in 17%.
  Skill invocations are low (4%) — you may have skills defined that
  aren't being triggered.

### Repeated Tool Sequences
- Detected 8 sessions with the pattern: Read → Grep → Read → Edit → Bash(test)
  This is a strong candidate for a skill or subagent.

### Recommendations (by impact)
1. Add routing rule: "explain * → sonnet" to config.json
2. Run /an:generate-skill to capture the Read→Grep→Edit→Test pattern
3. Review .claude/skills/ — 2 skills may have stale trigger conditions
```

---

### `/an:generate-skill` — Create a Skill

Claude detects the repeated `Read → Grep → Edit → Test` pattern and generates:

**`.agent-ninja/proposed/skills/edit-and-test/SKILL.md`**

```markdown
---
name: edit-and-test
description: >
  Read relevant files, locate the target code, make the edit, and run tests.
  Use for targeted bug fixes and small feature additions.
---

When asked to fix a bug or make a targeted code change:

1. Read the relevant file(s) to understand the current implementation
2. Use Grep to locate the specific function or pattern
3. Make the edit using the Edit tool
4. Run tests with Bash to verify the change
5. Report the result — pass or fail with the relevant output

Keep edits minimal. Do not refactor surrounding code unless explicitly asked.
```

```
Proposed skill saved to .agent-ninja/proposed/skills/edit-and-test/SKILL.md

Review it, then activate with:
  cp -r .agent-ninja/proposed/skills/edit-and-test ~/.claude/skills/
```

---

### `/an:generate-agent` — Create a Subagent

Claude detects that test + lint + type-check always run sequentially but are fully independent, and generates:

**`.agent-ninja/proposed/agents/ci-runner.md`**

```markdown
---
name: ci-runner
description: >
  Runs test suite, linter, and type checker in parallel and returns
  a consolidated pass/fail report. Use before committing or opening a PR.
---

You are a CI runner agent. Your job is to execute the project's full
local validation suite and return a structured summary.

## When to use this agent
When the user asks to "run CI", "check everything", "validate before PR",
or similar.

## Inputs
- Project root directory (inferred from context)
- Optional: specific test file or module to scope the run

## Workflow
1. Read pyproject.toml or package.json to discover test/lint/typecheck commands
2. Run each command via Bash (these are independent — run them in parallel if possible)
3. Collect exit codes and output for each
4. Return a structured summary

## Output
A consolidated report:
- Overall: PASS / FAIL
- Tests: pass/fail + summary line
- Lint: pass/fail + any violations
- Types: pass/fail + error count

## Guardrails
- Do not modify any files
- Do not install packages
- Do not push or commit
```

```
Proposed agent saved to .agent-ninja/proposed/agents/ci-runner.md

Review it, then activate with:
  cp .agent-ninja/proposed/agents/ci-runner.md ~/.claude/agents/
```

---

## 5. The Full Loop

```
You type a prompt
        │
        ▼
[Hook fires] Router classifies it
        │
        ├─ Static rule matched → inject recommendation
        └─ No match → inject self-assessment request
        │
        ▼
Claude responds (with routing guidance)
        │
        ▼
[Hook fires] Observer logs tool usage
        │
        ▼
[Session ends] Observer logs session stop
        │
        ▼
Data accumulates in .agent-ninja/data/
        │
        ▼
You run /an:audit or /an:strategize
        │
        ▼
Claude analyzes patterns → proposes improvements
        │
        ├─ /an:generate-skill → proposed/skills/<name>/SKILL.md
        └─ /an:generate-agent → proposed/agents/<name>.md
        │
        ▼
You review → copy to .claude/ to activate
```

Everything runs within your existing Claude session. No separate API key, no external services, no data leaving your machine.