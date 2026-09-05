"""
Football-Data.org Provider — v4 API
https://www.football-data.org/documentation/quickstart

Autenticação: header X-Auth-Token
Rate limit: 10 req/minuto no plano gratuito

Endpoints usados:
  GET /v4/matches?status=LIVE               → partidas ao vivo
  GET /v4/matches/{id}                      → detalhes completos (goals, bookings, stats)
  GET /v4/teams/{id}/matches?status=FINISHED&limit=10  → histórico do time

Campos mapeados do JSON real (documentado em docs.football-data.org/general/v4/match.html):
  match.status           → SCHEDULED | TIMED | IN_PLAY | PAUSED | FINISHED ...
  match.minute           → minuto atual
  match.score.fullTime   → {home, away}
  match.score.halfTime   → {home, away}
  match.goals[]          → {minute, type, team.id, score}
  match.bookings[]       → {minute, team.id, card: YELLOW|YELLOW_RED|RED}
  match.homeTeam.statistics → {corner_kicks, yellow_cards, red_cards, shots, ball_possession}
  match.odds             → {homeWin, draw, awayWin}
  match.competition.code → PL, CL, PD, BL1, SA, FL1 ...
  match.stage            → REGULAR_SEASON | LAST_16 | SEMI_FINALS | FINAL ...
"""
from __future__ import annotations
import asyncio
from datetime import datetime, date
from typing import Optional
import aiohttp
from loguru import logger

from backend.providers.base_provider import SportsDataProvider
from backend.core.engine.base import MatchContext

# ── Ligas disponíveis no plano gratuito (TIER_ONE acesso básico) ──────────────
MONITORED_LEAGUES = [
    "PL",   # Premier League (England)
    "CL",   # UEFA Champions League
    "PD",   # La Liga (Spain)
    "BL1",  # Bundesliga (Germany)
    "SA",   # Serie A (Italy)
    "FL1",  # Ligue 1 (France)
    "EL",   # UEFA Europa League
    "DED",  # Eredivisie (Netherlands)
    "PPL",  # Primeira Liga (Portugal)
    "BSA",  # Brasileirão Série A
]

# Códigos de competições que são mata-mata (para detectar ida/volta)
KNOCKOUT_COMPETITIONS = {"CL", "EL", "UCL", "CDR", "DFB", "FAC", "CIT"}

# Estágios que indicam mata-mata
KNOCKOUT_STAGES = {
    "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL",
    "ROUND_1", "ROUND_2", "ROUND_3", "ROUND_4",
    "LAST_32", "LAST_64", "PLAYOFF_ROUND_1", "PLAYOFF_ROUND_2",
}

BASE_URL = "https://api.football-data.org/v4"


def _safe_int(v) -> int:
    try:
        return int(v) if v is not None else 0
    except (ValueError, TypeError):
        return 0


def _safe_float(v) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (ValueError, TypeError):
        return None


class FootballDataProvider(SportsDataProvider):
    """
    Provider real para football-data.org API v4.
    Respeita o rate limit de 10 req/minuto usando sleep entre chamadas.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._headers = {
            "X-Auth-Token": api_key,
            "X-Unfold-Goals": "true",
            "X-Unfold-Bookings": "true",
        }
        self._session: Optional[aiohttp.ClientSession] = None
        # Cache de histórico de times para não fazer requests excessivos
        self._team_history_cache: dict[int, list[dict]] = {}
        self._cache_ttl: dict[int, datetime] = {}
        # Cache de partida da ida (para regras 2 e 3)
        self._first_leg_cache: dict[str, Optional[MatchContext]] = {}

    @property
    def provider_name(self) -> str:
        return "FootballData.org v4"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self._session

    async def _get(self, path: str, params: dict | None = None) -> dict:
        """Faz GET com tratamento de erros e rate limiting."""
        session = await self._get_session()
        url = f"{BASE_URL}{path}"
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                remaining = resp.headers.get("X-RequestsAvailable", "?")
                reset_in = resp.headers.get("X-RequestCounter-Reset", "?")

                if resp.status == 429:
                    logger.warning(f"Rate limit atingido. Reset em {reset_in}s. Aguardando 65s...")
                    await asyncio.sleep(65)
                    return {}

                if resp.status == 403:
                    logger.error("API Key inválida ou sem permissão para este endpoint (plano gratuito).")
                    return {}

                if resp.status != 200:
                    logger.warning(f"API retornou {resp.status} para {path}")
                    return {}

                logger.debug(f"GET {path} | status={resp.status} | requests restantes={remaining}")
                return await resp.json()

        except asyncio.TimeoutError:
            logger.error(f"Timeout na requisição: {url}")
            return {}
        except Exception as e:
            logger.error(f"Erro na requisição {url}: {e}")
            return {}

    async def health_check(self) -> bool:
        data = await self._get("/competitions/PL")
        return bool(data.get("id"))

    async def get_live_matches(self) -> list[MatchContext]:
        """
        Busca todas as partidas ao vivo.
        Endpoint: GET /v4/matches?status=LIVE
        Retorna IN_PLAY + PAUSED.
        """
        data = await self._get("/matches", params={"status": "LIVE"})
        raw_matches = data.get("matches", [])

        if not raw_matches:
            logger.info("Nenhuma partida ao vivo no momento.")
            return []

        logger.info(f"Partidas ao vivo encontradas: {len(raw_matches)}")
        contexts = []

        for raw in raw_matches:
            try:
                # Buscar detalhes completos (com goals e bookings expandidos)
                match_id = raw.get("id")
                detail = await self._get(f"/matches/{match_id}")
                await asyncio.sleep(6.5)  # respeitar 10 req/min

                if not detail:
                    continue

                ctx = await self._build_context(detail)
                if ctx:
                    contexts.append(ctx)

            except Exception as e:
                logger.error(f"Erro ao processar partida {raw.get('id')}: {e}")

        return contexts

    async def get_match_by_id(self, external_id: str) -> Optional[MatchContext]:
        data = await self._get(f"/matches/{external_id}")
        if not data:
            return None
        return await self._build_context(data)

    async def get_historical_matches(
        self,
        team_id: Optional[str] = None,
        league_id: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        Busca histórico de partidas finalizadas.
        Endpoint: GET /v4/matches?status=FINISHED&competitions=PL,CL,...
        """
        params = {
            "status": "FINISHED",
            "limit": min(limit, 50),
        }
        if league_id:
            params["competitions"] = league_id
        else:
            params["competitions"] = ",".join(MONITORED_LEAGUES[:5])

        data = await self._get("/matches", params=params)
        raw_matches = data.get("matches", [])

        result = []
        for m in raw_matches:
            score = m.get("score", {})
            ft = score.get("fullTime", {}) or {}
            ht = score.get("halfTime", {}) or {}
            home_team = m.get("homeTeam", {})
            away_team = m.get("awayTeam", {})
            home_stats = home_team.get("statistics") or {}
            away_stats = away_team.get("statistics") or {}

            result.append({
                "match_id": m.get("id"),
                "home_team": home_team.get("name", ""),
                "away_team": away_team.get("name", ""),
                "home_score": _safe_int(ft.get("home")),
                "away_score": _safe_int(ft.get("away")),
                "home_score_ht": _safe_int(ht.get("home")),
                "away_score_ht": _safe_int(ht.get("away")),
                "league": m.get("competition", {}).get("name", ""),
                "league_code": m.get("competition", {}).get("code", ""),
                "season": str(m.get("season", {}).get("startDate", "")[:4]),
                "status": m.get("status"),
                "date": m.get("utcDate"),
                "stage": m.get("stage"),
                "home_yellow_cards": _safe_int(home_stats.get("yellow_cards")),
                "away_yellow_cards": _safe_int(away_stats.get("yellow_cards")),
                "home_red_cards": _safe_int(home_stats.get("red_cards")),
                "away_red_cards": _safe_int(away_stats.get("red_cards")),
                "home_corners": _safe_int(home_stats.get("corner_kicks")),
                "away_corners": _safe_int(away_stats.get("corner_kicks")),
                "home_shots": _safe_int(home_stats.get("shots")),
                "away_shots": _safe_int(away_stats.get("shots")),
                "home_possession": _safe_float(home_stats.get("ball_possession")),
                "away_possession": _safe_float(away_stats.get("ball_possession")),
            })

        return result

    async def _build_context(self, m: dict) -> Optional[MatchContext]:
        """Converte um match dict da API real em MatchContext."""
        if not m:
            return None

        match_id = m.get("id")
        home_team = m.get("homeTeam") or {}
        away_team = m.get("awayTeam") or {}
        competition = m.get("competition") or {}
        score = m.get("score") or {}
        ft = score.get("fullTime") or {}
        ht = score.get("halfTime") or {}
        odds = m.get("odds") or {}

        home_stats = home_team.get("statistics") or {}
        away_stats = away_team.get("statistics") or {}

        # Score
        home_score = _safe_int(ft.get("home"))
        away_score = _safe_int(ft.get("away"))

        # Status / minute
        status_raw = m.get("status", "")
        minute = _safe_int(m.get("minute"))
        status_map = {
            "IN_PLAY": "live", "PAUSED": "live",
            "FINISHED": "finished", "SCHEDULED": "scheduled",
            "TIMED": "scheduled", "POSTPONED": "postponed",
            "CANCELLED": "cancelled", "SUSPENDED": "suspended",
        }
        status = status_map.get(status_raw, status_raw.lower())

        # League
        league_code = competition.get("code", "")
        league_name = competition.get("name", "")
        league_id = competition.get("id")
        league_important = league_code in MONITORED_LEAGUES

        # Odds
        home_odds = _safe_float(odds.get("homeWin"))
        away_odds = _safe_float(odds.get("awayWin"))
        draw_odds = _safe_float(odds.get("draw"))

        # Favorite
        favorite_side: Optional[str] = None
        if home_odds and away_odds:
            if home_odds < away_odds:
                favorite_side = "home"
            elif away_odds < home_odds:
                favorite_side = "away"

        # Cards e escanteios das estatísticas do time
        home_yellow = _safe_int(home_stats.get("yellow_cards"))
        away_yellow = _safe_int(away_stats.get("yellow_cards"))
        home_red = _safe_int(home_stats.get("red_cards")) + _safe_int(home_stats.get("yellow_red_cards"))
        away_red = _safe_int(away_stats.get("red_cards")) + _safe_int(away_stats.get("yellow_red_cards"))
        home_corners = _safe_int(home_stats.get("corner_kicks"))
        away_corners = _safe_int(away_stats.get("corner_kicks"))
        home_shots = _safe_int(home_stats.get("shots"))
        away_shots = _safe_int(away_stats.get("shots"))

        # Construir eventos a partir de goals[] e bookings[]
        events = []

        # Gols
        for goal in m.get("goals") or []:
            team_id = (goal.get("team") or {}).get("id")
            if team_id == home_team.get("id"):
                side = "home"
            else:
                side = "away"
            detail = goal.get("type", "REGULAR")  # REGULAR | OWN | PENALTY
            events.append({
                "event_type": "goal",
                "team_side": side,
                "minute": _safe_int(goal.get("minute")),
                "detail": detail,
                "player": (goal.get("scorer") or {}).get("name"),
            })

        # Cartões (bookings)
        for booking in m.get("bookings") or []:
            team_id = (booking.get("team") or {}).get("id")
            if team_id == home_team.get("id"):
                side = "home"
            else:
                side = "away"
            card = booking.get("card", "YELLOW")  # YELLOW | YELLOW_RED | RED
            evt_type = "red_card" if card in ("RED", "YELLOW_RED") else "yellow_card"
            events.append({
                "event_type": evt_type,
                "team_side": side,
                "minute": _safe_int(booking.get("minute")),
                "detail": card,
                "player": (booking.get("player") or {}).get("name"),
            })

        # Dois jogos (mata-mata) — detectar ida/volta
        stage = m.get("stage", "")
        is_knockout = (
            league_code in KNOCKOUT_COMPETITIONS
            or stage in KNOCKOUT_STAGES
        )

        # Por ora leg_number não é fornecido diretamente pela API gratuita
        # Será resolvido via comparação de datas e cabeçalhos futuros
        is_two_legged = is_knockout
        leg_number: Optional[int] = None
        first_leg_ctx: Optional[MatchContext] = None

        # Histórico de escanteios do time da casa (para Regra 4)
        home_history = await self._get_team_history(
            home_team.get("id"),
            league_code,
        )

        ctx = MatchContext(
            match_id=match_id,
            external_id=str(match_id),
            home_team_id=home_team.get("id"),
            away_team_id=away_team.get("id"),
            home_team_name=home_team.get("name", ""),
            away_team_name=away_team.get("name", ""),
            league_id=league_id,
            league_name=league_name,
            league_is_important=league_important,
            league_division=1,
            season=str((m.get("season") or {}).get("startDate", "")[:4]),
            home_score=home_score,
            away_score=away_score,
            minute=minute,
            status=status,
            home_odds=home_odds,
            away_odds=away_odds,
            draw_odds=draw_odds,
            favorite_side=favorite_side,
            home_yellow_cards=home_yellow,
            away_yellow_cards=away_yellow,
            home_red_cards=home_red,
            away_red_cards=away_red,
            home_corners=home_corners,
            away_corners=away_corners,
            home_shots=home_shots,
            away_shots=away_shots,
            events=events,
            is_two_legged=is_two_legged,
            leg_number=leg_number,
            first_leg_context=first_leg_ctx,
            home_team_history=home_history,
        )
        return ctx

    async def _get_team_history(
        self, team_id: Optional[int], league_code: str
    ) -> list[dict]:
        """
        Busca últimas 10 partidas do time para calcular média de escanteios (Regra 4).
        Usa cache TTL de 1 hora para não estourar o rate limit.
        """
        if not team_id:
            return []

        # Cache hit
        now = datetime.utcnow()
        cached_at = self._cache_ttl.get(team_id)
        if cached_at and (now - cached_at).seconds < 3600:
            return self._team_history_cache.get(team_id, [])

        try:
            data = await self._get(
                f"/teams/{team_id}/matches",
                params={"status": "FINISHED", "limit": 10},
            )
            await asyncio.sleep(6.5)  # rate limit

            raw = data.get("matches", [])
            history = []
            for m in raw:
                home_t = m.get("homeTeam", {})
                is_home = home_t.get("id") == team_id
                home_stats = home_t.get("statistics") or {}
                away_stats = (m.get("awayTeam") or {}).get("statistics") or {}
                stats = home_stats if is_home else away_stats
                corners = _safe_int(stats.get("corner_kicks"))
                history.append({
                    "played_at": "home" if is_home else "away",
                    "corners": corners,
                    "date": m.get("utcDate", ""),
                })

            self._team_history_cache[team_id] = history
            self._cache_ttl[team_id] = now
            return history

        except Exception as e:
            logger.warning(f"Erro ao buscar histórico do time {team_id}: {e}")
            return []
