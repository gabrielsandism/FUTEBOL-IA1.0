"""
RULE 004 - More Corners After Favorite Concedes at Home
Category: Corners

When a home favorite concedes the first goal,
there is a tendency to produce more corners afterward.

Before generating alert, analyze:
- Corner history
- Home average (last 5 and 10 games)
- Behavior after conceding a goal

All filters are configurable.

IMPORTANT: Statistical hypothesis, not a certainty.
"""
from __future__ import annotations
from typing import Optional
from backend.core.engine.base import BaseRule, MatchContext, RuleResult, RuleCategory


class Rule004MoreCornersAfterGoal(BaseRule):
    RULE_CODE = "RULE_004"
    RULE_NAME = "Mais Escanteios Após Favorito Sofrer Gol"
    CATEGORY = RuleCategory.CORNERS
    DESCRIPTION = (
        "Quando um favorito joga em casa e sofre o primeiro gol, "
        "existe tendência de produzir mais escanteios. "
        "Analisa histórico de escanteios antes do alerta."
    )
    PRIORITY = 7
    VERSION = "1.0.0"

    def default_parameters(self) -> dict:
        return {
            # Favorite detection
            "max_home_odds": 2.0,          # home odds <= this = favorite
            "require_home_favorite": True,  # must be home favorite

            # Historical filters (configurable)
            "min_home_corners_avg_last5": 4.0,   # min avg corners in last 5 home games
            "min_home_corners_avg_last10": 4.0,  # min avg corners in last 10 home games
            "use_historical_filter": True,        # apply historical filter

            # Match state
            "max_trigger_minute": 80,    # don't trigger too late
        }

    def _is_home_favorite(self, ctx: MatchContext) -> bool:
        """Determine if home team is favorite based on odds."""
        if ctx.favorite_side == "home":
            return True
        if ctx.home_odds is None:
            return False
        max_odds = self.get_param("max_home_odds", 2.0)
        return ctx.home_odds <= max_odds

    def _get_first_conceded_goal_minute(self, ctx: MatchContext) -> Optional[int]:
        """Find the minute of the first goal conceded by home team."""
        for event in sorted(ctx.events, key=lambda e: e.get("minute", 0)):
            if event.get("event_type") == "goal" and event.get("team_side") == "away":
                return event.get("minute")
        return None

    def _calc_home_corners_avg(self, history: list[dict], last_n: int) -> float:
        """Calculate average corners in last N home games."""
        home_games = [g for g in history if g.get("played_at") == "home"]
        recent = home_games[-last_n:] if len(home_games) >= last_n else home_games
        if not recent:
            return 0.0
        return sum(g.get("corners", 0) for g in recent) / len(recent)

    async def evaluate(self, ctx: MatchContext) -> Optional[RuleResult]:
        # Must be a home favorite situation
        if self.get_param("require_home_favorite") and not self._is_home_favorite(ctx):
            return None

        # Don't trigger too late in the match
        if ctx.minute > self.get_param("max_trigger_minute", 80):
            return None

        # Find when (and if) home team conceded first goal
        first_conceded_min = self._get_first_conceded_goal_minute(ctx)
        if first_conceded_min is None:
            return None  # Home hasn't conceded yet

        # Home must currently be trailing or level after conceding
        if ctx.home_score > ctx.away_score:
            return None  # Home is already winning — different scenario

        # Historical corner filter
        if self.get_param("use_historical_filter") and ctx.home_team_history:
            avg5 = self._calc_home_corners_avg(ctx.home_team_history, 5)
            avg10 = self._calc_home_corners_avg(ctx.home_team_history, 10)
            min_avg5 = self.get_param("min_home_corners_avg_last5", 4.0)
            min_avg10 = self.get_param("min_home_corners_avg_last10", 4.0)

            if avg5 < min_avg5 or avg10 < min_avg10:
                return None  # Historical corner rate too low

            historical_info = f"Média escanteios em casa: {avg5:.1f} (últ. 5), {avg10:.1f} (últ. 10)."
        else:
            historical_info = "Histórico de escanteios não disponível."

        score_str = f"{ctx.home_score}-{ctx.away_score}"
        title = (
            f"[{self.RULE_CODE}] {ctx.home_team_name} (favorito) sofreu gol em casa — "
            f"Monitorar Escanteios"
        )
        message = (
            f"{ctx.home_team_name} x {ctx.away_team_name} ({ctx.league_name}) — "
            f"Placar: {score_str} aos {ctx.minute}'. "
            f"Favorito {ctx.home_team_name} sofreu o 1° gol no minuto {first_conceded_min}. "
            f"{historical_info} "
            f"Hipótese: tendência de produzir mais escanteios. "
            f"[Regra estatística — não é previsão]"
        )

        avg5 = self._calc_home_corners_avg(ctx.home_team_history, 5) if ctx.home_team_history else 0
        avg10 = self._calc_home_corners_avg(ctx.home_team_history, 10) if ctx.home_team_history else 0

        return self._make_result(
            ctx,
            triggered=True,
            title=title,
            message=message,
            extra={
                "first_conceded_minute": first_conceded_min,
                "home_odds": ctx.home_odds,
                "home_corners_now": ctx.home_corners,
                "away_corners_now": ctx.away_corners,
                "home_corners_avg_last5": round(avg5, 2),
                "home_corners_avg_last10": round(avg10, 2),
            }
        )
