"""Rule, RuleOccurrence and Alert database models"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, JSON,
    ForeignKey, func, Text
)
from .base import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    # e.g. RULE_001, RULE_002, ...

    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    # cards | corners | goals | reversal | two_legged

    description = Column(Text, nullable=True)
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    version = Column(String(20), default="1.0.0")
    is_active = Column(Boolean, default=True)

    # Rule parameters (configurable per rule)
    parameters = Column(JSON, nullable=True)
    # e.g. {"min_score_diff": 3, "elite_only": True, "top_league_only": True}

    # Statistics
    total_occurrences = Column(Integer, default=0)
    total_matches_monitored = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    # success = the expected pattern occurred

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    @property
    def success_rate(self) -> float:
        if self.total_occurrences == 0:
            return 0.0
        return self.success_count / self.total_occurrences

    def __repr__(self) -> str:
        return f"<Rule {self.rule_code} '{self.name}' active={self.is_active}>"


class RuleOccurrence(Base):
    """Records each time a rule was triggered"""
    __tablename__ = "rule_occurrences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)

    triggered_at_minute = Column(Integer, nullable=True)
    triggered_at = Column(DateTime, default=func.now())

    # Context when rule fired
    context_data = Column(JSON, nullable=True)
    # e.g. {"score": "3-0", "minute": 67, "home_team": "Barcelona"}

    # Outcome (filled after match ends)
    outcome_data = Column(JSON, nullable=True)
    # e.g. {"cards_after": 0, "expected": True}

    is_success = Column(Boolean, nullable=True)
    # None = pending, True = pattern confirmed, False = not confirmed

    league_name = Column(String(200), nullable=True)
    season = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<RuleOccurrence rule={self.rule_id} match={self.match_id}>"


class Alert(Base):
    """Active alerts displayed in the dashboard"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    occurrence_id = Column(Integer, ForeignKey("rule_occurrences.id"), nullable=True)

    rule_code = Column(String(50), nullable=False)
    rule_name = Column(String(200), nullable=False)
    priority = Column(Integer, default=5)

    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)

    # Match context
    home_team = Column(String(200), nullable=False)
    away_team = Column(String(200), nullable=False)
    league_name = Column(String(200), nullable=True)
    minute = Column(Integer, nullable=True)
    score = Column(String(20), nullable=True)  # "3-0"

    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<Alert rule={self.rule_code} match={self.match_id} '{self.title}'>"
