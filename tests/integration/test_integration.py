"""
Integration Tests — Provider + Monitor Service + Backtest
Run: pytest tests/integration/test_integration.py -v

Os testes de integração sempre usam MockSportsProvider
independentemente do .env, para funcionar offline.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import asyncio
from unittest.mock import patch
from backend.providers.mock_provider import MockSportsProvider
from backend.services.monitor_service import MonitorService
from backend.services.backtest_service import BacktestService


class TestMockProvider:
    def setup_method(self):
        self.provider = MockSportsProvider()

    def test_provider_name(self):
        assert self.provider.provider_name == "MockSportsProvider"

    def test_health_check(self):
        result = asyncio.run(self.provider.health_check())
        assert result is True

    def test_get_live_matches_returns_list(self):
        matches = asyncio.run(self.provider.get_live_matches())
        assert isinstance(matches, list)
        assert len(matches) > 0

    def test_live_matches_have_required_fields(self):
        matches = asyncio.run(self.provider.get_live_matches())
        for m in matches:
            assert m.match_id is not None
            assert m.home_team_name
            assert m.away_team_name
            assert m.league_name

    def test_get_match_by_id(self):
        matches = asyncio.run(self.provider.get_live_matches())
        first = matches[0]
        result = asyncio.run(self.provider.get_match_by_id(str(first.match_id)))
        assert result is not None
        assert result.match_id == first.match_id

    def test_get_match_by_unknown_id(self):
        result = asyncio.run(self.provider.get_match_by_id("99999"))
        assert result is None

    def test_historical_matches(self):
        history = asyncio.run(self.provider.get_historical_matches(limit=10))
        assert isinstance(history, list)
        assert len(history) == 10

    def test_historical_matches_have_scores(self):
        history = asyncio.run(self.provider.get_historical_matches(limit=5))
        for m in history:
            assert "home_score" in m
            assert "away_score" in m

    def test_rule001_scenario_present(self):
        """Mock must include a 3-0 scenario for Rule 001"""
        matches = asyncio.run(self.provider.get_live_matches())
        high_scores = [
            m for m in matches
            if abs(m.home_score - m.away_score) >= 3
        ]
        assert len(high_scores) > 0

    def test_two_legged_scenario_present(self):
        """Mock must include two-legged scenarios"""
        matches = asyncio.run(self.provider.get_live_matches())
        two_legged = [m for m in matches if m.is_two_legged]
        assert len(two_legged) > 0


class TestMonitorService:
    def setup_method(self):
        self.service = MonitorService()
        # Forçar uso do MockProvider independentemente do .env
        self.service._provider = MockSportsProvider()
        # Limpar estado do rule engine para evitar bleeding entre testes
        import backend.services.monitor_service as ms_mod
        ms_mod.rule_engine._fired.clear()

    def test_initial_state(self):
        assert not self.service._running
        assert self.service._total_evaluations == 0
        assert self.service._total_alerts == 0

    def test_cycle_fetches_matches(self):
        asyncio.run(self.service._cycle())
        assert len(self.service._live_matches) > 0
        assert self.service._total_evaluations == 1

    def test_cycle_generates_alerts(self):
        asyncio.run(self.service._cycle())
        assert self.service._total_alerts > 0

    def test_get_live_matches_format(self):
        asyncio.run(self.service._cycle())
        matches = self.service.get_live_matches()
        assert isinstance(matches, list)
        for m in matches:
            assert "match_id" in m
            assert "home_team" in m
            assert "away_team" in m
            assert "home_score" in m

    def test_get_alerts_format(self):
        asyncio.run(self.service._cycle())
        alerts = self.service.get_alerts()
        assert isinstance(alerts, list)
        for a in alerts:
            assert "rule_code" in a
            assert "title" in a
            assert "message" in a
            assert "match_id" in a

    def test_dismiss_alert(self):
        asyncio.run(self.service._cycle())
        alerts = self.service.get_alerts()
        if alerts:
            alert_id = alerts[0]["id"]
            ok = self.service.dismiss_alert(alert_id)
            assert ok
            remaining = [a for a in self.service.get_alerts() if a["id"] == alert_id]
            assert len(remaining) == 0

    def test_get_stats(self):
        stats = self.service.get_stats()
        assert "provider" in stats
        assert "running" in stats
        assert "live_matches" in stats
        assert "active_alerts" in stats
        assert "active_rules" in stats


class TestBacktestService:
    def setup_method(self):
        self.service = BacktestService()
        # Forçar mock provider para rodar offline
        self.service._mock_provider = MockSportsProvider()

    def _run(self, limit=20):
        """Roda backtest forçando mock provider."""
        with patch("backend.services.backtest_service.get_provider",
                   return_value=MockSportsProvider()):
            return asyncio.run(self.service.run(limit=limit))

    def test_backtest_runs(self):
        result = self._run(20)
        assert "rules" in result
        assert "matches_analyzed" in result
        assert result["matches_analyzed"] == 20

    def test_backtest_has_all_rules(self):
        result = self._run(10)
        codes = [r["rule_code"] for r in result["rules"]]
        for code in ["RULE_001", "RULE_002", "RULE_003", "RULE_004", "RULE_005"]:
            assert code in codes

    def test_backtest_result_structure(self):
        result = self._run(10)
        for rule in result["rules"]:
            assert "rule_code" in rule
            assert "occurrences" in rule
            assert "occurrence_rate_pct" in rule
            assert "sample_size" in rule
            assert "top_leagues" in rule
            assert "note" in rule

    def test_backtest_rate_is_percentage(self):
        result = self._run(10)
        for rule in result["rules"]:
            rate = rule["occurrence_rate_pct"]
            assert 0.0 <= rate <= 100.0
