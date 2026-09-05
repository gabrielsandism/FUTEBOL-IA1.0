from .base_provider import SportsDataProvider
from .mock_provider import MockSportsProvider
from .footballdata_provider import FootballDataProvider


def get_provider(provider_name: str = "mock") -> SportsDataProvider:
    """
    Factory: retorna o provider configurado.
    - 'mock'         → MockSportsProvider (desenvolvimento/testes)
    - 'footballdata' → FootballDataProvider (football-data.org v4, dados reais)
    """
    from config.settings import settings

    name = provider_name.lower()

    if name == "footballdata":
        if not settings.sports_api_key:
            raise ValueError(
                "SPORTS_API_KEY não configurada no .env. "
                "Defina sua chave da football-data.org."
            )
        return FootballDataProvider(api_key=settings.sports_api_key)

    return MockSportsProvider()


__all__ = [
    "SportsDataProvider",
    "MockSportsProvider",
    "FootballDataProvider",
    "get_provider",
]
