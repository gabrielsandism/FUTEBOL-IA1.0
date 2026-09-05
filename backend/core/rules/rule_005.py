"""
RULE 005 - Reversal After Red Card (Favorite Scenario)
Category: Reversal

When:
- Favorite plays at home
- Concedes first goal
- Opponent receives red card

There is a tendency for a reversal to occur.

Record:
- Minute of goal
- Minute of red card
- Score at the time
- Final result
- Whether reversal occurred

IMPORTANT: Statistical hypothesis, not a certainty.
"""
from __future__ import annotations
from typing import Optional
from backend.core.engine.base import BaseRule, MatchContext, RuleResult, RuleCategory


class Rule005ReversalAfterRedCard(BaseRule):
    RULE_CODE = "RULE_005"
    RULE_NAME = "Virada Após Vermelho (Favorito em Casa)"
    CATEGORY = RuleCategory.REVERSAL
    DESCRIPTION = (
        "Quando favorito joga em casa, sofre o primeiro gol "
        "e o adversário recebe cartão vermelho, "
        "existe tendência de ocorrer virada."
    )
    PRIORITY = 9
    VERSION = "1.0.0"

    def default_parameters(self) -> dict:
        return {
            "max_home_odds": 2.0,
            "require_home_favorite": True,
            "max_trigger_minute": 85,    # don't alert too late
        }

    def _is_home_favorite(self, ctx: MatchContext) -> bool:
        if ctx.favorite_side == "home":
            return True
        if ctx.home_odds is None:
            return False
        return ctx.home_odds <= self.get_param("max_home_odds", 2.0)

    def _get_first_away_goal_minute(self, ctx: MatchContext) -> Optional[int]:
        """Find minute of first goal scored by away team."""
        for event in sorted(ctx.events, key=lambda e: e.get("minute", 0)):
            if event.get("event_type") == "goal" and event.get("team_side") == "away":
                return event.get("minute")
        return None

    def _get_away_red_card_minute(self, ctx: MatchContext) -> Optional[int]:
        """Find minute of first red card received by away team."""
        for event in sorted(ctx.events, key=lambda e: e.get("minute", 0)):
            if event.get("event_type") == "red_card" and event.get("team_side") == "away":
                return event.get("minute")
        return None

    async def evaluate(self, ctx: MatchContext) -> Optional[RuleResult]:
        # Must be home favorite
        if self.get_param("require_home_favorite") and not self._is_home_favorite(ctx):
            return None

        # Away must currently be leading (home conceded first goal)
        if ctx.home_score >= ctx.away_score:
            return None

        # Don't trigger too late
        if ctx.minute > self.get_param("max_trigger_minute", 85):
            return None

        # Check: home conceded first goal
        first_conceded_min = self._get_first_away_goal_minute(ctx)
        if first_conceded_min is None:
            return None

        # Check: away team has a red card
        away_red_min = self._get_away_red_card_minute(ctx)
        if away_red_min is None:
            return None

        # Red card must happen AFTER the first away goal
        if away_red_min < first_conceded_min:
            return None  # Red card before goal — different scenario

        # Home still needs to be losing at moment of evaluation
        if ctx.home_score >= ctx.away_score:
            return None

        score_str = f"{ctx.home_score}-{ctx.away_score}"
        title = (
            f"[{self.RULE_CODE}] ⚡ ALERTA VIRADA — {ctx.home_team_name} (favorito) "
            f"trailing {score_str} c/ adversário c/ 10 jogadores"
        )
        message = (
            f"CENÁRIO DE VIRADA — {ctx.home_team_name} x {ctx.away_team_name} ({ctx.league_name}). "
            f"Placar: {score_str} | Minuto: {ctx.minute}'. "
            f"Favorito {ctx.home_team_name} sofreu gol no min {first_conceded_min}. "
            f"Adversário recebeu VERMELHO no min {away_red_min}. "
            f"Hipótese: tendência de ocorrer virada. "
            f"[Regra estatística — não é previsão]"
        )

        return self._make_result(
            ctx,
            triggered=True,
            title=title,
            message=message,
            extra={
                "first_conceded_minute": first_conceded_min,
                "red_card_minute": away_red_min,
                "score_at_trigger": score_str,
                "home_odds": ctx.home_odds,
                "away_red_cards": ctx.away_red_cards,
            }
        )
