"""Configuration models: EliteTeamConfig and ImportantLeagueConfig"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .base import Base


class ImportantLeagueConfig(Base):
    """User-defined important leagues (for Rule 1 and others)"""
    __tablename__ = "important_league_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    league_external_id = Column(String(50), nullable=True)
    league_name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=True)
    division = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<ImportantLeagueConfig '{self.league_name}' active={self.is_active}>"


class EliteTeamConfig(Base):
    """User-defined elite teams (for Rule 1 and others)"""
    __tablename__ = "elite_team_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_external_id = Column(String(50), nullable=True)
    team_name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=True)
    league_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<EliteTeamConfig '{self.team_name}' active={self.is_active}>"
