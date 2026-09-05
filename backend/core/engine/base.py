"""
Rule Engine - Base types and abstractions.
All rules inherit from BaseRule.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime


class RuleCategory(str, Enum):
    CARDS = "cards"
    CORNERS = "corners"
    GOALS = "goals"
    REVERSAL = "reversal"
    TWO_LEGGED = "two_legged"
    GENERAL = "general"


class RuleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"


@dataclass
class MatchContext:
    """
    Full snapshot of a match at the moment of rule evaluation.
    Passed to every rule's evaluate() method.
    """
    # Identifiers
    match_id: int
    external_id: Optional[str] = None

    # Teams
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_team_name: str = ""
    away_team_name: str = ""
    home_is_elite: bool = False
    away_is_elite: bool = False

    # League
    league_id: Optional[int] = None
    league_name: str = ""
    league_is_important: bool = False
    league_division: int = 1
    season: str = ""

    # Score & Time
    home_score: int = 0
    away_score: int = 0
    minute: int = 0
    status: str = "live"

    # Odds & favorite
    home_odds: Optional[float] = None
    away_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    favorite_side: Optional[str] = None  # "home" | "away" | None

    # Statistics (current)
    home_corners: int = 0
    away_corners: int = 0
    home_yellow_cards: int = 0
    away_yellow_cards: int = 0
    home_red_cards: int = 0
    away_red_cards: int = 0
    home_shots: int = 0
    away_shots: int = 0
    home_shots_on_target: int = 0
    away_shots_on_target: int = 0

    # Events history (list of dicts)
    events: list[dict] = field(default_factory=list)

    # Two-legged support
    is_two_legged: bool = False
    leg_number: Optional[int] = None
    first_leg_context: Optional["MatchContext"] = None

    # Historical stats (last N matches)
    home_team_history: list[dict] = field(default_factory=list)
    away_team_history: list[dict] = field(default_factory=list)

    # Timestamp
    evaluated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RuleResult:
    """Result returned by a rule's evaluate() method."""
    triggered: bool
    rule_code: str
    rule_name: str
    match_id: int
    minute: int
    context_snapshot: dict = field(default_factory=dict)
    alert_title: str = ""
    alert_message: str = ""
    priority: int = 5
    extra_data: dict = field(default_factory=dict)


class BaseRule(ABC):
    """
    Abstract base class for all Football Scanner AI rules.
    Every rule must implement evaluate().
    """

    # These are overridden in each subclass
    RULE_CODE: str = "RULE_000"
    RULE_NAME: str = "Base Rule"
    CATEGORY: RuleCategory = RuleCategory.GENERAL
    DESCRIPTION: str = ""
    PRIORITY: int = 5
    VERSION: str = "1.0.0"

    def __init__(self, parameters: Optional[dict] = None):
        self.parameters = parameters or self.default_parameters()
        self.is_active: bool = True

    def default_parameters(self) -> dict:
        """Override in subclasses to define configurable parameters."""
        return {}

    @abstractmethod
    async def evaluate(self, ctx: MatchContext) -> Optional[RuleResult]:
        """
        Evaluate the rule against the current match context.
        Return RuleResult if triggered, None otherwise.
        """
        ...

    def _make_result(
        self,
        ctx: MatchContext,
        triggered: bool,
        title: str = "",
        message: str = "",
        extra: dict | None = None,
    ) -> Optional[RuleResult]:
        if not triggered:
            return None
        return RuleResult(
            triggered=True,
            rule_code=self.RULE_CODE,
            rule_name=self.RULE_NAME,
            match_id=ctx.match_id,
            minute=ctx.minute,
            context_snapshot={
                "home_team": ctx.home_team_name,
                "away_team": ctx.away_team_name,
                "score": f"{ctx.home_score}-{ctx.away_score}",
                "minute": ctx.minute,
                "league": ctx.league_name,
            },
            alert_title=title,
            alert_message=message,
            priority=self.PRIORITY,
            extra_data=extra or {},
        )

    def get_param(self, key: str, default: Any = None) -> Any:
        return self.parameters.get(key, default)

    def __repr__(self) -> str:
        return f"<Rule {self.RULE_CODE} '{self.RULE_NAME}' active={self.is_active}>"
