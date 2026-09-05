"""
Unit Tests — Rule Engine + 5 Rules
Run: pytest tests/unit/test_rules.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
import asyncio
from backend.core.engine.base import MatchContext
from backend.core.engine.rule_engine import RuleEngine
from backend.core.rules.rule_001 import Rule001CardAfter3x0
from backend.core.rules.rule_002 import Rule002NoGoalFirst10Min
from backend.core.rules.rule_003 import Rule003NoCardAfterBigWin
from backend.core.rules.rule_004 import Rule004MoreCornersAfterGoal
from backend.core.rules.rule_005 import Rule005ReversalAfterRedCard


def make_ctx(**kwargs) -> MatchContext:
    defaults = dict(
        match_id=1, home_team_name="Home FC", away_team_name="Away FC",
        league_name="Test League", home_score=0, away_score=0, minute=50,
        home_is_elite=True, away_is_elite=False, league_is_important=True,
        league_division=1, home_odds=1.80, away_odds=4.50, draw_odds=3.40,
        favorite_side="home", events=[], status="live",
    )
    defaults.update(kwargs)
    return MatchContext(**defaults)


# ─── RULE 001 ─────────────────────────────────────────────────────────────────

class TestRule001:
    def setup_method(self):
        self.rule = Rule001CardAfter3x0()

    def test_triggers_on_3x0_elite_important(self):
        ctx = make_ctx(home_score=3, away_score=0, minute=60)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None
        assert result.triggered
        assert result.rule_code == "RULE_001"

    def test_no_trigger_non_important_league(self):
        ctx = make_ctx(home_score=3, away_score=0, league_is_important=False)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_non_elite_team(self):
        ctx = make_ctx(home_score=3, away_score=0, home_is_elite=False)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_score_too_small(self):
        ctx = make_ctx(home_score=2, away_score=0)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_triggers_on_4x0(self):
        ctx = make_ctx(home_score=4, away_score=0)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None

    def test_triggers_on_3x0_away_team_elite(self):
        ctx = make_ctx(home_score=0, away_score=3, away_is_elite=True, home_is_elite=False)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None

    def test_no_trigger_second_division(self):
        ctx = make_ctx(home_score=3, away_score=0, league_division=2)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None


# ─── RULE 002 ─────────────────────────────────────────────────────────────────

def make_first_leg(home_score=2, away_score=1) -> MatchContext:
    return make_ctx(
        match_id=99, home_score=home_score, away_score=away_score,
        minute=90, status="finished", home_team_name="Team A", away_team_name="Team B",
    )


class TestRule002:
    def setup_method(self):
        self.rule = Rule002NoGoalFirst10Min()

    def test_triggers_on_return_leg_1goal_diff(self):
        first = make_first_leg(2, 1)  # 1-goal diff
        ctx = make_ctx(
            match_id=2, minute=5, is_two_legged=True, leg_number=2,
            first_leg_context=first, events=[]
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None
        assert result.triggered

    def test_no_trigger_not_two_legged(self):
        ctx = make_ctx(minute=5, is_two_legged=False)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_first_leg(self):
        first = make_first_leg(2, 1)
        ctx = make_ctx(minute=5, is_two_legged=True, leg_number=1, first_leg_context=first)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_diff_greater_than_1(self):
        first = make_first_leg(3, 0)  # 3-goal diff
        ctx = make_ctx(minute=5, is_two_legged=True, leg_number=2, first_leg_context=first)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_after_monitoring_window(self):
        first = make_first_leg(2, 1)
        ctx = make_ctx(minute=15, is_two_legged=True, leg_number=2, first_leg_context=first)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_if_goal_occurred(self):
        first = make_first_leg(2, 1)
        ctx = make_ctx(
            minute=7, is_two_legged=True, leg_number=2, first_leg_context=first,
            events=[{"event_type": "goal", "team_side": "home", "minute": 4}]
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None


# ─── RULE 003 ─────────────────────────────────────────────────────────────────

class TestRule003:
    def setup_method(self):
        self.rule = Rule003NoCardAfterBigWin()

    def test_triggers_on_return_after_4goal_diff(self):
        first = make_first_leg(5, 0)  # 5-goal diff
        ctx = make_ctx(
            match_id=3, minute=5, is_two_legged=True, leg_number=2,
            first_leg_context=first
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None
        assert result.triggered

    def test_no_trigger_diff_less_than_4(self):
        first = make_first_leg(3, 0)  # 3-goal diff
        ctx = make_ctx(minute=5, is_two_legged=True, leg_number=2, first_leg_context=first)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_single_leg(self):
        ctx = make_ctx(minute=5, is_two_legged=False)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_triggers_exactly_4goal_diff(self):
        first = make_first_leg(4, 0)
        ctx = make_ctx(minute=5, is_two_legged=True, leg_number=2, first_leg_context=first)
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None


# ─── RULE 004 ─────────────────────────────────────────────────────────────────

home_history_good = [
    {"played_at": "home", "corners": 6},
    {"played_at": "home", "corners": 7},
    {"played_at": "home", "corners": 5},
    {"played_at": "home", "corners": 8},
    {"played_at": "home", "corners": 6},
    {"played_at": "home", "corners": 7},
    {"played_at": "home", "corners": 5},
    {"played_at": "home", "corners": 6},
    {"played_at": "home", "corners": 8},
    {"played_at": "home", "corners": 7},
]

home_history_bad = [
    {"played_at": "home", "corners": 2},
    {"played_at": "home", "corners": 1},
    {"played_at": "home", "corners": 2},
    {"played_at": "home", "corners": 3},
    {"played_at": "home", "corners": 1},
]


class TestRule004:
    def setup_method(self):
        self.rule = Rule004MoreCornersAfterGoal()

    def test_triggers_when_fav_concedes_good_history(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=35,
            home_odds=1.55, favorite_side="home",
            events=[{"event_type": "goal", "team_side": "away", "minute": 28}],
            home_team_history=home_history_good,
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None
        assert result.triggered

    def test_no_trigger_bad_corner_history(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=35,
            home_odds=1.55, favorite_side="home",
            events=[{"event_type": "goal", "team_side": "away", "minute": 28}],
            home_team_history=home_history_bad,
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_home_winning(self):
        ctx = make_ctx(
            home_score=2, away_score=1, minute=35,
            home_odds=1.55, favorite_side="home",
            events=[{"event_type": "goal", "team_side": "away", "minute": 10}],
            home_team_history=home_history_good,
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_not_favorite(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=35,
            home_odds=3.50, away_odds=2.00, favorite_side="away",
            events=[{"event_type": "goal", "team_side": "away", "minute": 28}],
            home_team_history=home_history_good,
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_no_conceded_goal(self):
        ctx = make_ctx(
            home_score=0, away_score=0, minute=35,
            home_odds=1.55, favorite_side="home",
            events=[],
            home_team_history=home_history_good,
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_after_minute_80(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=85,
            home_odds=1.55, favorite_side="home",
            events=[{"event_type": "goal", "team_side": "away", "minute": 28}],
            home_team_history=home_history_good,
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None


# ─── RULE 005 ─────────────────────────────────────────────────────────────────

class TestRule005:
    def setup_method(self):
        self.rule = Rule005ReversalAfterRedCard()

    def test_triggers_full_scenario(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=55,
            home_odds=1.45, favorite_side="home",
            away_red_cards=1,
            events=[
                {"event_type": "goal", "team_side": "away", "minute": 30},
                {"event_type": "red_card", "team_side": "away", "minute": 52},
            ],
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is not None
        assert result.triggered

    def test_no_trigger_home_not_losing(self):
        ctx = make_ctx(
            home_score=1, away_score=1, minute=55,
            home_odds=1.45, favorite_side="home",
            events=[
                {"event_type": "goal", "team_side": "away", "minute": 30},
                {"event_type": "red_card", "team_side": "away", "minute": 52},
            ],
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_no_red_card(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=55,
            home_odds=1.45, favorite_side="home",
            events=[{"event_type": "goal", "team_side": "away", "minute": 30}],
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_red_before_goal(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=55,
            home_odds=1.45, favorite_side="home",
            events=[
                {"event_type": "red_card", "team_side": "away", "minute": 20},
                {"event_type": "goal", "team_side": "away", "minute": 30},
            ],
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_away_favorite(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=55,
            home_odds=3.50, away_odds=2.00, favorite_side="away",
            events=[
                {"event_type": "goal", "team_side": "away", "minute": 30},
                {"event_type": "red_card", "team_side": "away", "minute": 52},
            ],
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None

    def test_no_trigger_too_late(self):
        ctx = make_ctx(
            home_score=0, away_score=1, minute=88,
            home_odds=1.45, favorite_side="home",
            events=[
                {"event_type": "goal", "team_side": "away", "minute": 30},
                {"event_type": "red_card", "team_side": "away", "minute": 52},
            ],
        )
        result = asyncio.run(self.rule.evaluate(ctx))
        assert result is None


# ─── RULE ENGINE ──────────────────────────────────────────────────────────────

class TestRuleEngine:
    def setup_method(self):
        self.engine = RuleEngine()

    def test_engine_has_five_rules(self):
        rules = self.engine.get_rules_info()
        assert len(rules) == 5

    def test_all_rules_active_by_default(self):
        rules = self.engine.get_rules_info()
        assert all(r["is_active"] for r in rules)

    def test_toggle_rule_inactive(self):
        ok = self.engine.set_rule_active("RULE_001", False)
        assert ok
        rules = {r["rule_code"]: r for r in self.engine.get_rules_info()}
        assert not rules["RULE_001"]["is_active"]

    def test_update_parameters(self):
        ok = self.engine.update_parameters("RULE_001", {"min_goal_diff": 4})
        assert ok

    def test_evaluate_match_returns_results(self):
        ctx = make_ctx(home_score=3, away_score=0, minute=60)
        results = asyncio.run(self.engine.evaluate_match(ctx))
        codes = [r.rule_code for r in results]
        assert "RULE_001" in codes

    def test_evaluate_all_matches(self):
        ctxs = [
            make_ctx(match_id=1, home_score=3, away_score=0),
            make_ctx(match_id=2, home_score=1, away_score=1),
        ]
        all_results = asyncio.run(self.engine.evaluate_all_matches(ctxs))
        assert 1 in all_results
        assert 2 in all_results

    def test_inactive_rule_does_not_trigger(self):
        self.engine.set_rule_active("RULE_001", False)
        ctx = make_ctx(home_score=3, away_score=0)
        results = asyncio.run(self.engine.evaluate_match(ctx))
        codes = [r.rule_code for r in results]
        assert "RULE_001" not in codes

    def test_no_duplicate_alerts_within_5_minutes(self):
        ctx = make_ctx(match_id=99, home_score=3, away_score=0, minute=60)
        r1 = asyncio.run(self.engine.evaluate_match(ctx))
        r2 = asyncio.run(self.engine.evaluate_match(ctx))
        # Second evaluation at same minute should not re-trigger
        codes_r2 = [r.rule_code for r in r2]
        assert "RULE_001" not in codes_r2
