"""
Football Scanner AI - FastAPI Backend
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config.settings import settings
from backend.db.database import init_db
from backend.services.monitor_service import monitor_service
from backend.api.routes import dashboard, matches, rules, alerts, backtest, config_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Football Scanner AI starting...")

    # Init database
    await init_db()

    # Start monitoring in background
    asyncio.create_task(monitor_service.start())
    logger.info("Monitor service launched")

    yield

    # Shutdown
    monitor_service.stop()
    logger.info("Football Scanner AI stopped")


app = FastAPI(
    title="Football Scanner AI",
    description="Sistema de monitoramento e análise estatística de partidas de futebol",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Routers
app.include_router(dashboard.router, prefix="", tags=["Dashboard"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"])
app.include_router(config_routes.router, prefix="/api/config", tags=["Config"])


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "db_mode": settings.db_mode,
        "provider": settings.sports_api_provider,
    }


@app.get("/api/stats")
async def stats():
    return monitor_service.get_stats()
