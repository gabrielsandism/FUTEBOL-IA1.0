"""
RULE 002 - No Goal in First 10 Minutes (Two-Legged)
Category: Two-Legged / Goals

In two-legged competitions, when the first leg ends with
only 1 goal difference, there is a tendency for no goals
to be scored in the first 10 minutes of the return leg.

The system should:
- Identify two-legged fixtures automatically
- Locate the first leg match
- Monitor the first 10 minutes of the return leg
- Record the behavior for statistical analysis

IMPORTANT: Statistical hypothesis, not a certainty.
"""
from __future__ import annotations
from typing import Optional
from backend.core.engine.base import BaseRule, MatchContext, RuleResult, RuleCategory


class Rule002NoGoalFirst10Min(BaseRule):
    RULE_CODE = "RULE_002"
    RULE_NAME = "Sem Gol Primeiros 10min (Volta)"
    CATEGORY = RuleCategory.TWO_LEGGED
    DESCRIPTION = (
        "Em competições com ida e volta, quando a ida termina com diferença "
        "de apenas 1 gol, existe tendência de não ocorrer gol nos primeiros "
        "10 minutos da partida de volta."
    )
    PRIORITY = 6
    VERSION = "1.0.0"

    def default_parameters(self) -> dict:
        return {
            "max_first_leg_diff": 1,      # max goal diff to trigger
            "monitoring_minutes": 10,      # minutes to monitor at start
            "trigger_at_minute": 1,        # fire alert at match start
        }

    async def evaluate(self, ctx: MatchContext) -> Optional[RuleResult]:
        # Must be return leg of a two-legged fixture
        if not ctx.is_two_legged:
            return None
        if ctx.leg_number != 2:
            return None
        if ctx.first_leg_context is None:
            return None

        # Check first leg goal difference
        first_leg = ctx.first_leg_context
        first_leg_diff = abs(first_leg.home_score - first_leg.away_score)
        max_diff = self.get_param("max_first_leg_diff", 1)

        if first_leg_diff > max_diff:
            return None

        # Monitor only in the defined window (start of match)
        monitor_min = self.get_param("monitoring_minutes", 10)
        trigger_min = self.get_param("trigger_at_minute", 1)

        # Fire alert at the beginning of monitoring window
        if ctx.minute < trigger_min:
            return None
        if ctx.minute > monitor_min:
            return None

        # Don't fire again if goal already happened in window
        early_goals = [
            e for e in ctx.events
            if e.get("event_type") == "goal" and (e.get("minute") or 0) <= monitor_min
        ]
        if early_goals:
            return None  # Pattern not confirmed, will record outcome

        first_leg_score = f"{first_leg.home_score}-{first_leg.away_score}"
        title = (
            f"[{self.RULE_CODE}] Jogo de Volta — 1° Leg ({first_leg_score}) — "
            f"Monitorando Primeiros {monitor_min}min"
        )
        message = (
            f"Partida de VOLTA: {ctx.home_team_name} x {ctx.away_team_name} ({ctx.league_name}). "
            f"Resultado da IDA: {first_leg.home_team_name} {first_leg_score} {first_leg.away_team_name} "
            f"(diferença de {first_leg_diff} gol). "
            f"Hipótese: tendência de não ocorrer gol nos primeiros {monitor_min} minutos. "
            f"[Regra estatística — não é previsão]"
        )

        return self._make_result(
            ctx,
            triggered=True,
            title=title,
            message=message,
            extra={
                "first_leg_score": first_leg_score,
                "first_leg_diff": first_leg_diff,
                "monitoring_window": monitor_min,
                "goals_in_window_so_far": len(early_goals),
            }
        )
