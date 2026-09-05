"""
RULE 003 - No Cards After Big Win in First Leg
Category: Cards / Two-Legged

When a team wins the first leg by 4 or more goals,
there is a tendency for that team not to receive cards
in the return leg.

IMPORTANT: Statistical hypothesis, not a certainty.
"""
from __future__ import annotations
from typing import Optional
from backend.core.engine.base import BaseRule, MatchContext, RuleResult, RuleCategory


class Rule003NoCardAfterBigWin(BaseRule):
    RULE_CODE = "RULE_003"
    RULE_NAME = "Sem Cartões na Volta Após Goleada"
    CATEGORY = RuleCategory.TWO_LEGGED
    DESCRIPTION = (
        "Quando um time vence a ida por 4 ou mais gols, "
        "existe tendência de não receber cartões na partida de volta."
    )
    PRIORITY = 6
    VERSION = "1.0.0"

    def default_parameters(self) -> dict:
        return {
            "min_first_leg_goal_diff": 4,   # minimum first leg goal difference
            "trigger_at_minute": 1,          # fire when match starts
        }

    async def evaluate(self, ctx: MatchContext) -> Optional[RuleResult]:
        # Must be return leg
        if not ctx.is_two_legged:
            return None
        if ctx.leg_number != 2:
            return None
        if ctx.first_leg_context is None:
            return None

        first_leg = ctx.first_leg_context
        min_diff = self.get_param("min_first_leg_goal_diff", 4)

        # Identify which team won by 4+ goals in first leg
        home_diff = first_leg.home_score - first_leg.away_score

        if abs(home_diff) < min_diff:
            return None

        # Identify winning team and their side in return leg
        if home_diff > 0:
            big_winner_name = first_leg.home_team_name
        else:
            big_winner_name = first_leg.away_team_name

        # Only trigger at match start
        trigger_min = self.get_param("trigger_at_minute", 1)
        if ctx.minute < trigger_min:
            return None

        first_leg_score = f"{first_leg.home_score}-{first_leg.away_score}"
        diff_str = abs(home_diff)

        title = (
            f"[{self.RULE_CODE}] {big_winner_name} venceu IDA por {diff_str} gols — "
            f"Monitorando Cartões na Volta"
        )
        message = (
            f"VOLTA: {ctx.home_team_name} x {ctx.away_team_name} ({ctx.league_name}). "
            f"Na IDA: {first_leg.home_team_name} {first_leg_score} {first_leg.away_team_name}. "
            f"{big_winner_name} venceu por {diff_str} gols. "
            f"Hipótese: tendência de não receber cartões nesta partida. "
            f"[Regra estatística — não é previsão]"
        )

        return self._make_result(
            ctx,
            triggered=True,
            title=title,
            message=message,
            extra={
                "big_winner": big_winner_name,
                "first_leg_score": first_leg_score,
                "first_leg_diff": diff_str,
            }
        )
