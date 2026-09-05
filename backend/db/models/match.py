"""Match, MatchEvent and MatchStatistics database models"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, JSON,
    ForeignKey, func, Text
)
from .base import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(50), unique=True, nullable=True, index=True)

    # Teams
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    home_team_name = Column(String(200), nullable=False)
    away_team_name = Column(String(200), nullable=False)

    # League
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=True)
    league_name = Column(String(200), nullable=True)
    season = Column(String(20), nullable=True)
    round = Column(String(100), nullable=True)

    # Score
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    home_score_ht = Column(Integer, nullable=True)  # halftime
    away_score_ht = Column(Integer, nullable=True)

    # Match state
    status = Column(String(50), default="scheduled")
    # scheduled | live | finished | postponed | cancelled
    minute = Column(Integer, nullable=True)
    is_live = Column(Boolean, default=False)

    # Two-legged match support
    is_two_legged = Column(Boolean, default=False)
    leg_number = Column(Integer, nullable=True)  # 1 = ida, 2 = volta
    first_leg_match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)

    # Odds/favorite
    home_odds = Column(Float, nullable=True)
    away_odds = Column(Float, nullable=True)
    draw_odds = Column(Float, nullable=True)
    favorite_side = Column(String(10), nullable=True)  # home | away | none

    # Match date
    match_date = Column(DateTime, nullable=True)

    # Extra metadata
    venue = Column(String(200), nullable=True)
    extra_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return (
            f"<Match id={self.id} "
            f"{self.home_team_name} {self.home_score}x{self.away_score} {self.away_team_name} "
            f"status={self.status}>"
        )


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    external_id = Column(String(100), nullable=True)

    event_type = Column(String(50), nullable=False)
    # goal | yellow_card | red_card | corner | substitution | var | penalty

    minute = Column(Integer, nullable=True)
    minute_extra = Column(Integer, nullable=True)  # added time
    team_side = Column(String(10), nullable=True)  # home | away
    team_name = Column(String(200), nullable=True)
    player_name = Column(String(200), nullable=True)
    detail = Column(String(200), nullable=True)  # own_goal, penalty, etc.

    created_at = Column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<MatchEvent match={self.match_id} type={self.event_type} min={self.minute}>"


class MatchStatistics(Base):
    __tablename__ = "match_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    recorded_at_minute = Column(Integer, nullable=True)

    # Shots
    home_shots = Column(Integer, default=0)
    away_shots = Column(Integer, default=0)
    home_shots_on_target = Column(Integer, default=0)
    away_shots_on_target = Column(Integer, default=0)

    # Corners
    home_corners = Column(Integer, default=0)
    away_corners = Column(Integer, default=0)

    # Cards
    home_yellow_cards = Column(Integer, default=0)
    away_yellow_cards = Column(Integer, default=0)
    home_red_cards = Column(Integer, default=0)
    away_red_cards = Column(Integer, default=0)

    # Possession
    home_possession = Column(Float, nullable=True)
    away_possession = Column(Float, nullable=True)

    # Attacks
    home_attacks = Column(Integer, default=0)
    away_attacks = Column(Integer, default=0)
    home_dangerous_attacks = Column(Integer, default=0)
    away_dangerous_attacks = Column(Integer, default=0)

    # Fouls
    home_fouls = Column(Integer, default=0)
    away_fouls = Column(Integer, default=0)

    created_at = Column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<MatchStatistics match={self.match_id} min={self.recorded_at_minute}>"
