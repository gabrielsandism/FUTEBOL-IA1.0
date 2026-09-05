"""
Mock Sports Data Provider
Generates realistic simulated match data for development and testing.
Covers all 5 rules with representative scenarios.
"""
from __future__ import annotations
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional
from backend.providers.base_provider import SportsDataProvider
from backend.core.engine.base import MatchContext


def _make_ctx(
    match_id: int,
    home: str,
    away: str,
    league: str,
    home_score: int,
    away_score: int,
    minute: int,
    home_is_elite: bool = True,
    away_is_elite: bool = False,
    league_important: bool = True,
    home_odds: float = 1.80,
    away_odds: float = 4.50,
    draw_odds: float = 3.40,
    home_yellow: int = 0,
    away_yellow: int = 0,
    home_red: int = 0,
    away_red: int = 0,
    home_corners: int = 0,
    away_corners: int = 0,
    events: list | None = None,
    is_two_legged: bool = False,
    leg_number: int | None = None,
    first_leg_ctx: MatchContext | None = None,
    home_history: list | None = None,
) -> MatchContext:
    favorite = "home" if home_odds < away_odds else "away"
    return MatchContext(
        match_id=match_id,
        external_id=str(match_id),
        home_team_name=home,
        away_team_name=away,
        league_name=league,
        home_score=home_score,
        away_score=away_score,
        minute=minute,
        home_is_elite=home_is_elite,
        away_is_elite=away_is_elite,
        league_is_important=league_important,
        league_division=1,
        home_odds=home_odds,
        away_odds=away_odds,
        draw_odds=draw_odds,
        favorite_side=favorite,
        home_yellow_cards=home_yellow,
        away_yellow_cards=away_yellow,
        home_red_cards=home_red,
        away_red_cards=away_red,
        home_corners=home_corners,
        away_corners=away_corners,
        events=events or [],
        is_two_legged=is_two_legged,
        leg_number=leg_number,
        first_leg_context=first_leg_ctx,
        home_team_history=home_history or [],
        status="live",
    )


# ── Pre-built first leg context for two-legged rules ──────────────────────────
FIRST_LEG_RULE002 = _make_ctx(
    match_id=90, home="Atlético Madrid", away="RB Leipzig",
    league="UEFA Champions League",
    home_score=2, away_score=1,  # 1-goal diff
    minute=90, home_is_elite=True, away_is_elite=True,
    league_important=True,
)

FIRST_LEG_RULE003 = _make_ctx(
    match_id=91, home="Bayern Munich", away="FC Porto",
    league="UEFA Champions League",
    home_score=5, away_score=0,  # 5-goal diff (>= 4)
    minute=90, home_is_elite=True, away_is_elite=False,
    league_important=True,
)

# ── Mock match library ─────────────────────────────────────────────────────────
def _build_mock_matches() -> list[MatchContext]:
    minute = 67

    # RULE 1: Elite team 3-0 in important league → no more cards
    m1 = _make_ctx(
        match_id=1, home="Real Madrid", away="Getafe",
        league="La Liga", home_score=3, away_score=0,
        minute=minute, home_is_elite=True, away_is_elite=False,
        league_important=True,
        home_odds=1.40, away_odds=7.00, draw_odds=5.00,
        home_yellow=1, away_yellow=2,
        events=[
            {"event_type": "goal", "team_side": "home", "minute": 22},
            {"event_type": "goal", "team_side": "home", "minute": 44},
            {"event_type": "goal", "team_side": "home", "minute": 61},
        ]
    )

    # RULE 2: Two-legged return leg, 1-goal diff in first leg, early minutes
    m2 = _make_ctx(
        match_id=2, home="RB Leipzig", away="Atlético Madrid",
        league="UEFA Champions League",
        home_score=0, away_score=0,
        minute=5, home_is_elite=True, away_is_elite=True,
        league_important=True,
        home_odds=2.80, away_odds=2.60, draw_odds=3.30,
        is_two_legged=True, leg_number=2,
        first_leg_ctx=FIRST_LEG_RULE002,
        events=[],
    )

    # RULE 3: Return leg after 5-0 first leg → no cards
    m3 = _make_ctx(
        match_id=3, home="FC Porto", away="Bayern Munich",
        league="UEFA Champions League",
        home_score=0, away_score=1,
        minute=30, home_is_elite=False, away_is_elite=True,
        league_important=True,
        home_odds=6.50, away_odds=1.50, draw_odds=4.20,
        is_two_legged=True, leg_number=2,
        first_leg_ctx=FIRST_LEG_RULE003,
        events=[
            {"event_type": "goal", "team_side": "away", "minute": 18},
        ],
    )

    # RULE 4: Home favorite concedes first goal → more corners
    home_history = [
        {"played_at": "home", "corners": 6, "date": "2024-10-01"},
        {"played_at": "home", "corners": 7, "date": "2024-10-15"},
        {"played_at": "home", "corners": 5, "date": "2024-10-29"},
        {"played_at": "home", "corners": 8, "date": "2024-11-12"},
        {"played_at": "home", "corners": 6, "date": "2024-11-26"},
        {"played_at": "away", "corners": 4, "date": "2024-12-01"},
        {"played_at": "home", "corners": 7, "date": "2024-12-10"},
        {"played_at": "home", "corners": 5, "date": "2024-12-17"},
        {"played_at": "away", "corners": 3, "date": "2024-12-22"},
        {"played_at": "home", "corners": 6, "date": "2025-01-05"},
    ]
    m4 = _make_ctx(
        match_id=4, home="Manchester City", away="Brighton",
        league="Premier League",
        home_score=0, away_score=1,
        minute=35, home_is_elite=True, away_is_elite=False,
        league_important=True,
        home_odds=1.55, away_odds=6.00, draw_odds=4.00,
        home_corners=3, away_corners=2,
        events=[
            {"event_type": "goal", "team_side": "away", "minute": 28},
        ],
        home_history=home_history,
    )

    # RULE 5: Favorite concedes + away red card → reversal scenario
    m5 = _make_ctx(
        match_id=5, home="Liverpool", away="Brentford",
        league="Premier League",
        home_score=0, away_score=1,
        minute=55, home_is_elite=True, away_is_elite=False,
        league_important=True,
        home_odds=1.45, away_odds=7.50, draw_odds=4.50,
        home_corners=5, away_corners=2,
        home_yellow=1, away_yellow=1, away_red=1,
        events=[
            {"event_type": "goal", "team_side": "away", "minute": 31},
            {"event_type": "yellow_card", "team_side": "away", "minute": 40},
            {"event_type": "red_card", "team_side": "away", "minute": 52},
        ],
    )

    # Extra match — no rule trigger (normal game)
    m6 = _make_ctx(
        match_id=6, home="Wolves", away="Crystal Palace",
        league="Premier League",
        home_score=1, away_score=1,
        minute=60, home_is_elite=False, away_is_elite=False,
        league_important=True,
        home_odds=2.40, away_odds=3.10, draw_odds=3.20,
        events=[
            {"event_type": "goal", "team_side": "home", "minute": 22},
            {"event_type": "goal", "team_side": "away", "minute": 48},
        ],
    )

    return [m1, m2, m3, m4, m5, m6]


class MockSportsProvider(SportsDataProvider):
    """
    Mock provider for development and testing.
    Returns pre-built scenarios that test each of the 5 rules.
    """

    @property
    def provider_name(self) -> str:
        return "MockSportsProvider"

    async def get_live_matches(self) -> list[MatchContext]:
        await asyncio.sleep(0)
        matches = _build_mock_matches()
        # Slightly randomize minutes to simulate live updates
        for m in matches:
            m.minute = max(1, m.minute + random.randint(-2, 2))
        return matches

    async def get_match_by_id(self, external_id: str) -> Optional[MatchContext]:
        matches = await self.get_live_matches()
        for m in matches:
            if m.external_id == external_id:
                return m
        return None

    async def get_historical_matches(
        self,
        team_id: Optional[str] = None,
        league_id: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Return synthetic historical data for backtest module."""
        await asyncio.sleep(0)
        results = []
        for i in range(limit):
            results.append({
                "match_id": 1000 + i,
                "home_team": "Team A",
                "away_team": "Team B",
                "home_score": random.randint(0, 5),
                "away_score": random.randint(0, 3),
                "league": "Test League",
                "season": "2024/2025",
                "home_yellow_cards": random.randint(0, 4),
                "away_yellow_cards": random.randint(0, 4),
                "home_corners": random.randint(2, 12),
                "away_corners": random.randint(2, 12),
                "date": (datetime.utcnow() - timedelta(days=i * 7)).isoformat(),
                "status": "finished",
            })
        return results

    async def health_check(self) -> bool:
        return True
