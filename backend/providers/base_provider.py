"""
SportsDataProvider - Abstract interface.
Allows swapping between different sports APIs without changing core logic.
"""
from abc import ABC, abstractmethod
from typing import Optional
from backend.core.engine.base import MatchContext


class SportsDataProvider(ABC):
    """Abstract interface for sports data sources."""

    @abstractmethod
    async def get_live_matches(self) -> list[MatchContext]:
        """Return all currently live matches."""
        ...

    @abstractmethod
    async def get_match_by_id(self, external_id: str) -> Optional[MatchContext]:
        """Return a specific match by external ID."""
        ...

    @abstractmethod
    async def get_historical_matches(
        self,
        team_id: Optional[str] = None,
        league_id: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Return historical match data for backtesting."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is reachable."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...
