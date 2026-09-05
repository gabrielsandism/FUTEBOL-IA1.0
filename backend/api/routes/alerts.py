"""Alerts API routes"""
from fastapi import APIRouter
from backend.services.monitor_service import monitor_service

router = APIRouter()


@router.get("/")
async def list_alerts(include_dismissed: bool = False):
    return {"alerts": monitor_service.get_alerts(include_dismissed)}


@router.post("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: int):
    ok = monitor_service.dismiss_alert(alert_id)
    return {"success": ok, "alert_id": alert_id}


@router.post("/{alert_id}/read")
async def mark_read(alert_id: int):
    ok = monitor_service.mark_read(alert_id)
    return {"success": ok, "alert_id": alert_id}
