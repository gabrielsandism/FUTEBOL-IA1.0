"""Config API routes - Elite teams and Important leagues"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory config store (will be DB-backed in full version)
_elite_teams: list[dict] = [
    {"id": 1, "name": "Real Madrid", "country": "Spain", "league": "La Liga", "is_active": True},
    {"id": 2, "name": "Barcelona", "country": "Spain", "league": "La Liga", "is_active": True},
    {"id": 3, "name": "Manchester City", "country": "England", "league": "Premier League", "is_active": True},
    {"id": 4, "name": "Liverpool", "country": "England", "league": "Premier League", "is_active": True},
    {"id": 5, "name": "Bayern Munich", "country": "Germany", "league": "Bundesliga", "is_active": True},
    {"id": 6, "name": "PSG", "country": "France", "league": "Ligue 1", "is_active": True},
    {"id": 7, "name": "Juventus", "country": "Italy", "league": "Serie A", "is_active": True},
]

_important_leagues: list[dict] = [
    {"id": 1, "name": "La Liga", "country": "Spain", "division": 1, "is_active": True},
    {"id": 2, "name": "Premier League", "country": "England", "division": 1, "is_active": True},
    {"id": 3, "name": "Bundesliga", "country": "Germany", "division": 1, "is_active": True},
    {"id": 4, "name": "Serie A", "country": "Italy", "division": 1, "is_active": True},
    {"id": 5, "name": "Ligue 1", "country": "France", "division": 1, "is_active": True},
    {"id": 6, "name": "UEFA Champions League", "country": "Europe", "division": 1, "is_active": True},
    {"id": 7, "name": "UEFA Europa League", "country": "Europe", "division": 1, "is_active": True},
]

_next_team_id = 8
_next_league_id = 8


class EliteTeamCreate(BaseModel):
    name: str
    country: Optional[str] = None
    league: Optional[str] = None
    notes: Optional[str] = None


class ImportantLeagueCreate(BaseModel):
    name: str
    country: Optional[str] = None
    division: int = 1
    notes: Optional[str] = None


# ── Elite Teams ────────────────────────────────────────────────────────────────

@router.get("/elite-teams")
async def list_elite_teams():
    return {"teams": _elite_teams}


@router.post("/elite-teams")
async def add_elite_team(body: EliteTeamCreate):
    global _next_team_id
    team = {
        "id": _next_team_id,
        "name": body.name,
        "country": body.country,
        "league": body.league,
        "is_active": True,
        "notes": body.notes,
    }
    _elite_teams.append(team)
    _next_team_id += 1
    return {"team": team}


@router.delete("/elite-teams/{team_id}")
async def remove_elite_team(team_id: int):
    global _elite_teams
    before = len(_elite_teams)
    _elite_teams = [t for t in _elite_teams if t["id"] != team_id]
    return {"removed": len(_elite_teams) < before, "team_id": team_id}


@router.patch("/elite-teams/{team_id}/toggle")
async def toggle_elite_team(team_id: int):
    for team in _elite_teams:
        if team["id"] == team_id:
            team["is_active"] = not team["is_active"]
            return {"team": team}
    return {"error": "Not found"}


# ── Important Leagues ──────────────────────────────────────────────────────────

@router.get("/important-leagues")
async def list_important_leagues():
    return {"leagues": _important_leagues}


@router.post("/important-leagues")
async def add_important_league(body: ImportantLeagueCreate):
    global _next_league_id
    league = {
        "id": _next_league_id,
        "name": body.name,
        "country": body.country,
        "division": body.division,
        "is_active": True,
        "notes": body.notes,
    }
    _important_leagues.append(league)
    _next_league_id += 1
    return {"league": league}


@router.delete("/important-leagues/{league_id}")
async def remove_important_league(league_id: int):
    global _important_leagues
    before = len(_important_leagues)
    _important_leagues = [l for l in _important_leagues if l["id"] != league_id]
    return {"removed": len(_important_leagues) < before, "league_id": league_id}


@router.patch("/important-leagues/{league_id}/toggle")
async def toggle_important_league(league_id: int):
    for league in _important_leagues:
        if league["id"] == league_id:
            league["is_active"] = not league["is_active"]
            return {"league": league}
    return {"error": "Not found"}
