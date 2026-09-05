"""
Football Scanner AI - Rule Engine
Orchestrates evaluation of all active rules against live matches.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from backend.core.engine.base import BaseRule, MatchContext, RuleResult
from backend.core.rules.rule_001 import Rule001CardAfter3x0
from backend.core.rules.rule_002 import Rule002NoGoalFirst10Min
from backend.core.rules.rule_003 import Rule003NoCardAfterBigWin
from backend.core.rules.rule_004 import Rule004MoreCornersAfterGoal
from backend.core.rules.rule_005 import Rule005ReversalAfterRedCard


class RuleEngine:
    """
    Central Rule Engine.
    - Registers all active rules.
    - Evaluates rules against match contexts.
    - Returns triggered results.
    - Tracks which rules already fired per match to avoid duplicates.
    """

    def __init__(self):
        self._rules: list[BaseRule] = []
        # {match_id: {rule_code: triggered_at_minute}}
        self._fired: dict[int, dict[str, int]] = {}
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Register all built-in rules."""
        self.register(Rule001CardAfter3x0())
        self.register(Rule002NoGoalFirst10Min())
        self.register(Rule003NoCardAfterBigWin())
        self.register(Rule004MoreCornersAfterGoal())
        self.register(Rule005ReversalAfterRedCard())
        logger.info(f"Rule Engine initialized with {len(self._rules)} rules")

    def register(self, rule: BaseRule) -> None:
        self._rules.append(rule)
        logger.debug(f"Registered rule: {rule.RULE_CODE} - {rule.RULE_NAME}")

    def set_rule_active(self, rule_code: str, active: bool) -> bool:
        for rule in self._rules:
            if rule.RULE_CODE == rule_code:
                rule.is_active = active
                return True
        return False

    def update_parameters(self, rule_code: str, parameters: dict) -> bool:
        for rule in self._rules:
            if rule.RULE_CODE == rule_code:
                rule.parameters.update(parameters)
                return True
        return False

    def get_rules_info(self) -> list[dict]:
        return [
            {
                "rule_code": r.RULE_CODE,
                "name": r.RULE_NAME,
                "category": r.CATEGORY,
                "description": r.DESCRIPTION,
                "priority": r.PRIORITY,
                "version": r.VERSION,
                "is_active": r.is_active,
                "parameters": r.parameters,
            }
            for r in self._rules
        ]

    async def evaluate_match(self, ctx: MatchContext) -> list[RuleResult]:
        """
        Evaluate all active rules against a single match context.
        Returns list of triggered RuleResults.
        """
        results: list[RuleResult] = []
        fired_map = self._fired.setdefault(ctx.match_id, {})

        for rule in self._rules:
            if not rule.is_active:
                continue

            # Avoid re-triggering same rule within 5 minutes
            last_fired_min = fired_map.get(rule.RULE_CODE)
            if last_fired_min is not None:
                if (ctx.minute - last_fired_min) < 5:
                    continue

            try:
                result = await rule.evaluate(ctx)
                if result and result.triggered:
                    results.append(result)
                    fired_map[rule.RULE_CODE] = ctx.minute
                    logger.info(
                        f"RULE TRIGGERED: {rule.RULE_CODE} | "
                        f"Match: {ctx.home_team_name} vs {ctx.away_team_name} | "
                        f"Min: {ctx.minute} | Score: {ctx.home_score}-{ctx.away_score}"
                    )
            except Exception as e:
                logger.error(f"Error evaluating {rule.RULE_CODE} on match {ctx.match_id}: {e}")

        return results

    async def evaluate_all_matches(self, contexts: list[MatchContext]) -> dict[int, list[RuleResult]]:
        """Evaluate all rules against multiple matches concurrently."""
        tasks = [self.evaluate_match(ctx) for ctx in contexts]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        output: dict[int, list[RuleResult]] = {}
        for ctx, result in zip(contexts, results_list):
            if isinstance(result, Exception):
                logger.error(f"Match {ctx.match_id} evaluation error: {result}")
                output[ctx.match_id] = []
            else:
                output[ctx.match_id] = result

        return output

    def clear_match_state(self, match_id: int) -> None:
        """Remove tracking state for a finished match."""
        self._fired.pop(match_id, None)


# Global singleton
rule_engine = RuleEngine()
