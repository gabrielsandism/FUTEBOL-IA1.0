"""League database model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .base import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=True)
    logo_url = Column(String(500), nullable=True)
    is_important = Column(Boolean, default=False, nullable=False)
    division = Column(Integer, default=1, nullable=False)  # 1 = primeira divisão
    season = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<League id={self.id} name='{self.name}' country='{self.country}'>"
