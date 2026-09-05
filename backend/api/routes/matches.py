"""Matches API routes"""
from fastapi import APIRouter
from backend.services.monitor_service import monitor_service

router = APIRouter()


@router.get("/live")
async def get_live_matches():
    return {"matches": monitor_service.get_live_matches()}


@router.get("/live/{match_id}")
async def get_match_detail(match_id: int):
    matches = monitor_service.get_live_matches()
    match = next((m for m in matches if m["match_id"] == match_id), None)
    if not match:
        return {"error": "Match not found"}

    alerts = [
        a for a in monitor_service.get_alerts()
        if a["match_id"] == match_id
    ]
    return {"match": match, "alerts": alerts}
