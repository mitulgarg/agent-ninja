"""Tests for the router engine."""

import sys
import os

# Add scripts/ to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from core.models import ModelTier, AgentPattern, ThinkingLevel
from core.config import AgentPilotConfig
from router.engine import RouterEngine
from router.rules import StaticRules


class TestStaticRules:
    """Test pattern-based routing without LLM calls."""

    def setup_method(self):
        self.config = AgentPilotConfig()
        self.rules = StaticRules(self.config)

    def test_simple_read_routes_to_haiku(self):
        result = self.rules.match("read the file src/main.py")
        assert result is not None
        assert result.model == ModelTier.HAIKU
        assert result.pattern == AgentPattern.DIRECT

    def test_explain_routes_to_haiku(self):
        result = self.rules.match("explain this function")
        assert result is not None
        assert result.model == ModelTier.HAIKU

    def test_run_tests_routes_to_haiku(self):
        result = self.rules.match("run tests")
        assert result is not None
        assert result.model == ModelTier.HAIKU

    def test_git_status_routes_to_haiku(self):
        result = self.rules.match("git status")
        assert result is not None
        assert result.model == ModelTier.HAIKU

    def test_format_routes_to_haiku(self):
        result = self.rules.match("format this file")
        assert result is not None
        assert result.model == ModelTier.HAIKU

    def test_architecture_routes_to_opus(self):
        result = self.rules.match("architect a new auth system")
        assert result is not None
        assert result.model == ModelTier.OPUS
        assert result.pattern == AgentPattern.PLAN_MODE
        assert result.thinking == ThinkingLevel.HIGH

    def test_security_audit_routes_to_opus(self):
        result = self.rules.match("security audit of the API")
        assert result is not None
        assert result.model == ModelTier.OPUS

    def test_debug_across_files_routes_to_opus(self):
        result = self.rules.match("debug across files why is auth broken")
        assert result is not None
        assert result.model == ModelTier.OPUS

    def test_implement_feature_routes_to_plan_mode(self):
        result = self.rules.match("implement a new feature for user profiles")
        assert result is not None
        assert result.model == ModelTier.SONNET
        assert result.pattern == AgentPattern.PLAN_MODE

    def test_refactor_multiple_routes_to_plan_mode(self):
        result = self.rules.match("refactor multiple modules to use new API")
        assert result is not None
        assert result.pattern == AgentPattern.PLAN_MODE

    def test_ambiguous_prompt_returns_none(self):
        result = self.rules.match("help me with this code")
        assert result is None

    def test_user_override_opus(self):
        config = AgentPilotConfig(always_opus_for=["database migration"])
        rules = StaticRules(config)
        result = rules.match("plan the database migration")
        assert result is not None
        assert result.model == ModelTier.OPUS

    def test_user_override_haiku(self):
        config = AgentPilotConfig(always_haiku_for=["check logs"])
        rules = StaticRules(config)
        result = rules.match("check logs for errors")
        assert result is not None
        assert result.model == ModelTier.HAIKU


class TestRouterEngine:
    """Test the full router engine."""

    def setup_method(self):
        self.config = AgentPilotConfig()

    def test_static_match_returns_decision(self):
        engine = RouterEngine(self.config, "/tmp/project")
        result = engine.classify("run tests")
        assert result is not None
        assert result.model == ModelTier.HAIKU
        assert result.prompt_hash != ""

    def test_no_match_returns_none(self):
        engine = RouterEngine(self.config, "/tmp/project")
        result = engine.classify("help me with something")
        assert result is None

    def test_self_assess_prompt_returned(self):
        engine = RouterEngine(self.config, "/tmp/project")
        prompt = engine.get_self_assess_prompt()
        assert "[Agent Pilot]" in prompt
        assert "self-assess" in prompt.lower()