"""
Match Monitor Service
Polls the sports data provider on a configurable interval,
evaluates all active rules, and persists alerts.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from config.settings import settings
from backend.core.engine.rule_engine import rule_engine
from backend.core.engine.base import MatchContext, RuleResult
from backend.providers import get_provider, SportsDataProvider


class MonitorService:
    """
    Background service that:
    1. Fetches live matches from the provider
    2. Evaluates all rules
    3. Stores triggered alerts in memory (and optionally DB)
    """

    def __init__(self):
        self._provider: Optional[SportsDataProvider] = None
        self._running = False
        self._interval = settings.rule_engine_interval
        self._alerts: list[dict] = []          # in-memory alert store
        self._live_matches: list[MatchContext] = []
        self._last_update: Optional[datetime] = None
        self._total_evaluations = 0
        self._total_alerts = 0

    @property
    def provider(self) -> SportsDataProvider:
        if self._provider is None:
            self._provider = get_provider(settings.sports_api_provider)
        return self._provider

    async def start(self) -> None:
        self._running = True
        logger.info(f"MonitorService started | provider={self.provider.provider_name} | interval={self._interval}s")
        while self._running:
            try:
                await self._cycle()
            except Exception as e:
                logger.error(f"Monitor cycle error: {e}")
            await asyncio.sleep(self._interval)

    def stop(self) -> None:
        self._running = False
        logger.info("MonitorService stopped")

    async def _cycle(self) -> None:
        """Single monitoring cycle: fetch → evaluate → store."""
        logger.debug("Monitor cycle starting...")

        # Fetch live matches
        contexts = await self.provider.get_live_matches()
        self._live_matches = contexts
        self._last_update = datetime.utcnow()
        self._total_evaluations += 1

        logger.debug(f"Fetched {len(contexts)} live matches")

        # Evaluate rules
        all_results = await rule_engine.evaluate_all_matches(contexts)

        # Process results
        for match_id, results in all_results.items():
            for result in results:
                self._store_alert(result, contexts)

    def _store_alert(self, result: RuleResult, contexts: list[MatchContext]) -> None:
        """Store alert in memory."""
        # Find match context
        ctx = next((c for c in contexts if c.match_id == result.match_id), None)
        expires = datetime.utcnow() + timedelta(hours=settings.alert_retention_hours)

        alert = {
            "id": self._total_alerts + 1,
            "rule_code": result.rule_code,
            "rule_name": result.rule_name,
            "match_id": result.match_id,
            "priority": result.priority,
            "title": result.alert_title,
            "message": result.alert_message,
            "home_team": ctx.home_team_name if ctx else "",
            "away_team": ctx.away_team_name if ctx else "",
            "league": ctx.league_name if ctx else "",
            "minute": result.minute,
            "score": f"{ctx.home_score}-{ctx.away_score}" if ctx else "",
            "is_read": False,
            "is_dismissed": False,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires.isoformat(),
            "context": result.context_snapshot,
            "extra": result.extra_data,
        }

        # Avoid exact duplicates in last 5 minutes
        recent_dupes = [
            a for a in self._alerts
            if a["rule_code"] == result.rule_code
            and a["match_id"] == result.match_id
            and not a["is_dismissed"]
        ]
        if not recent_dupes:
            self._alerts.insert(0, alert)
            self._total_alerts += 1
            logger.info(f"Alert stored: [{result.rule_code}] {result.alert_title}")

        # Keep last 200 alerts
        self._alerts = self._alerts[:200]

    def get_live_matches(self) -> list[dict]:
        """Return live matches as serializable dicts."""
        result = []
        for ctx in self._live_matches:
            # Count active alerts per match
            active_alerts = [
                a for a in self._alerts
                if a["match_id"] == ctx.match_id and not a["is_dismissed"]
            ]
            result.append({
                "match_id": ctx.match_id,
                "home_team": ctx.home_team_name,
                "away_team": ctx.away_team_name,
                "league": ctx.league_name,
                "home_score": ctx.home_score,
                "away_score": ctx.away_score,
                "minute": ctx.minute,
                "status": ctx.status,
                "active_alerts": len(active_alerts),
                "alert_rules": [a["rule_code"] for a in active_alerts],
            })
        return result

    def get_alerts(self, include_dismissed: bool = False) -> list[dict]:
        """Return all alerts, optionally filtering dismissed."""
        now = datetime.utcnow().isoformat()
        return [
            a for a in self._alerts
            if (include_dismissed or not a["is_dismissed"])
            and a["expires_at"] > now
        ]

    def dismiss_alert(self, alert_id: int) -> bool:
        for alert in self._alerts:
            if alert["id"] == alert_id:
                alert["is_dismissed"] = True
                return True
        return False

    def mark_read(self, alert_id: int) -> bool:
        for alert in self._alerts:
            if alert["id"] == alert_id:
                alert["is_read"] = True
                return True
        return False

    def get_stats(self) -> dict:
        return {
            "provider": self.provider.provider_name,
            "running": self._running,
            "interval_seconds": self._interval,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "total_evaluations": self._total_evaluations,
            "total_alerts_generated": self._total_alerts,
            "active_alerts": len([a for a in self._alerts if not a["is_dismissed"]]),
            "live_matches": len(self._live_matches),
            "active_rules": len([r for r in rule_engine.get_rules_info() if r["is_active"]]),
        }


# Global singleton
monitor_service = MonitorService()
