"""Backtest API routes"""
from fastapi import APIRouter, Query
from backend.services.backtest_service import backtest_service

router = APIRouter()


@router.post("/run")
async def run_backtest(limit: int = Query(default=50, ge=10, le=500)):
    result = await backtest_service.run(limit=limit)
    return result


@router.get("/status")
async def backtest_status():
    return {"status": "ready", "note": "POST /api/backtest/run to execute"}
