"""
RULE 001 - Cards After 3x0
Category: Cards

In important leagues (first division) with elite teams,
when a team opens a 3-0 lead, there is a tendency for
no more yellow/red cards to be issued afterward.

The system should:
- Detect the moment when the score becomes 3-0 (or similar dominance)
- Monitor subsequent cards
- Record the result for statistical analysis

IMPORTANT: This is a statistical hypothesis, not a certainty.
"""
from __future__ import annotations
from typing import Optional
from backend.core.engine.base import BaseRule, MatchContext, RuleResult, RuleCategory


class Rule001CardAfter3x0(BaseRule):
    RULE_CODE = "RULE_001"
    RULE_NAME = "Sem Cartões Após 3x0"
    CATEGORY = RuleCategory.CARDS
    DESCRIPTION = (
        "Em ligas importantes (primeira divisão) com times de elite, "
        "quando um time abre 3x0, existe tendência de não receber mais cartões."
    )
    PRIORITY = 7
    VERSION = "1.0.0"

    def default_parameters(self) -> dict:
        return {
            "min_goal_diff": 3,          # minimum score difference to trigger
            "leading_score_min": 3,       # minimum goals by leading team
            "require_elite_team": True,   # at least one team must be elite
            "require_important_league": True,  # league must be important
            "require_first_division": True,    # must be first division
        }

    async def evaluate(self, ctx: MatchContext) -> Optional[RuleResult]:
        # Filters
        if self.get_param("require_important_league") and not ctx.league_is_important:
            return None
        if self.get_param("require_first_division") and ctx.league_division != 1:
            return None

        # Determine if score shows dominance (3-0 or equivalent)
        min_diff = self.get_param("min_goal_diff", 3)
        min_score = self.get_param("leading_score_min", 3)
        diff = ctx.home_score - ctx.away_score
        abs_diff = abs(diff)

        if abs_diff < min_diff:
            return None

        leading_goals = max(ctx.home_score, ctx.away_score)
        if leading_goals < min_score:
            return None

        # Determine leading team
        if diff > 0:
            leading_side = "home"
            leading_team = ctx.home_team_name
            leading_is_elite = ctx.home_is_elite
        else:
            leading_side = "away"
            leading_team = ctx.away_team_name
            leading_is_elite = ctx.away_is_elite

        # Check elite requirement
        if self.get_param("require_elite_team") and not leading_is_elite:
            return None

        # Rule fires when score reaches this threshold
        score_str = f"{ctx.home_score}-{ctx.away_score}"
        title = f"[{self.RULE_CODE}] {leading_team} vence por {score_str} — Monitorando Cartões"
        message = (
            f"O time {leading_team} abriu {score_str} aos {ctx.minute}' "
            f"na partida {ctx.home_team_name} x {ctx.away_team_name} "
            f"({ctx.league_name}). "
            f"Hipótese: tendência de não receber mais cartões. "
            f"[Regra estatística — não é previsão]"
        )

        return self._make_result(
            ctx,
            triggered=True,
            title=title,
            message=message,
            extra={
                "leading_team": leading_team,
                "leading_side": leading_side,
                "leading_is_elite": leading_is_elite,
                "score_at_trigger": score_str,
                "home_yellow": ctx.home_yellow_cards,
                "away_yellow": ctx.away_yellow_cards,
            }
        )
