"""Hierarchical configuration: defaults -> user config -> env vars."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AgentNinjaConfig:
    routing_enabled: bool = True
    auto_switch: bool = True
    default_model: str = "sonnet"
    always_opus_for: list[str] = field(default_factory=list)
    always_haiku_for: list[str] = field(default_factory=list)

    observer_enabled: bool = True

    data_dir: Path = Path(".agent-ninja/data")
    proposed_dir: Path = Path(".agent-ninja/proposed")

    @classmethod
    def load(cls, project_dir: Optional[str] = None) -> AgentNinjaConfig:
        """Load config with precedence: env > project config > defaults."""
        config = cls()

        # 1. Plugin-level defaults
        plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
        if plugin_root:
            defaults_path = Path(plugin_root) / "config" / "defaults.json"
            if defaults_path.exists():
                with open(defaults_path) as f:
                    config._apply_dict(json.load(f))

        # 2. Load project config if exists
        if project_dir:
            config_path = Path(project_dir) / ".agent-ninja" / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    user_cfg = json.load(f)
                config._apply_dict(user_cfg)

        # 3. Environment overrides (highest precedence)
        if os.environ.get("AGENT_NINJA_ROUTING_ENABLED") == "false":
            config.routing_enabled = False

        if os.environ.get("AGENT_NINJA_AUTO_SWITCH") == "false":
            config.auto_switch = False

        # Resolve data dirs relative to project directory
        base = Path(project_dir) if project_dir else Path.cwd()
        config.data_dir = base / ".agent-ninja" / "data"
        config.proposed_dir = base / ".agent-ninja" / "proposed"

        # Ensure data dirs exist
        config.data_dir.mkdir(parents=True, exist_ok=True)
        config.proposed_dir.mkdir(parents=True, exist_ok=True)

        return config

    def _apply_dict(self, d: dict) -> None:
        routing = d.get("routing", {})
        if "enabled" in routing:
            self.routing_enabled = routing["enabled"]
        if "auto_switch" in routing:
            self.auto_switch = routing["auto_switch"]
        if "default_model" in routing:
            self.default_model = routing["default_model"]
        if "always_opus_for" in routing:
            self.always_opus_for = routing["always_opus_for"]
        if "always_haiku_for" in routing:
            self.always_haiku_for = routing["always_haiku_for"]

        observer = d.get("observer", {})
        if "enabled" in observer:
            self.observer_enabled = observer["enabled"]
