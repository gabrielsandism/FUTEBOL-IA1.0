"""
Backtest Service
Runs all rules against historical match data and produces statistics.
"""
from __future__ import annotations
import asyncio
from datetime import datetime
from loguru import logger
from backend.core.engine.rule_engine import rule_engine
from backend.core.engine.base import MatchContext
from backend.providers import get_provider
from config.settings import settings


class BacktestService:
    """Executes rules on historical data and aggregates results."""

    async def run(self, limit: int = 50) -> dict:
        """
        Run backtest on historical data.
        Returns per-rule statistics.
        """
        logger.info(f"Starting backtest | limit={limit}")
        provider = get_provider(settings.sports_api_provider)
        raw_matches = await provider.get_historical_matches(limit=limit)

        # Convert raw historical data to MatchContext
        contexts = self._convert_to_contexts(raw_matches)
        logger.info(f"Converted {len(contexts)} historical matches to contexts")

        # Evaluate all rules per match
        stats: dict[str, dict] = {}
        for rule in rule_engine.get_rules_info():
            stats[rule["rule_code"]] = {
                "rule_code": rule["rule_code"],
                "rule_name": rule["name"],
                "category": str(rule["category"]),
                "occurrences": 0,
                "total_matches": len(contexts),
                "leagues": {},
                "seasons": {},
                "triggered_matches": [],
            }

        for ctx in contexts:
            results = await rule_engine.evaluate_match(ctx)
            for result in results:
                code = result.rule_code
                if code not in stats:
                    continue
                stats[code]["occurrences"] += 1
                league = ctx.league_name or "Unknown"
                season = ctx.season or "Unknown"
                stats[code]["leagues"][league] = stats[code]["leagues"].get(league, 0) + 1
                stats[code]["seasons"][season] = stats[code]["seasons"].get(season, 0) + 1
                stats[code]["triggered_matches"].append({
                    "match_id": ctx.match_id,
                    "home": ctx.home_team_name,
                    "away": ctx.away_team_name,
                    "score": f"{ctx.home_score}-{ctx.away_score}",
                    "minute": ctx.minute,
                    "league": league,
                    "season": season,
                })

        # Compute rates
        output = []
        for code, data in stats.items():
            total = data["total_matches"]
            occ = data["occurrences"]
            rate = round(occ / total * 100, 2) if total > 0 else 0.0

            # Best performing leagues
            top_leagues = sorted(
                data["leagues"].items(), key=lambda x: x[1], reverse=True
            )[:5]

            output.append({
                "rule_code": code,
                "rule_name": data["rule_name"],
                "category": data["category"],
                "total_matches_analyzed": total,
                "occurrences": occ,
                "occurrence_rate_pct": rate,
                "sample_size": total,
                "top_leagues": [{"league": l, "occurrences": c} for l, c in top_leagues],
                "by_season": data["seasons"],
                "sample_matches": data["triggered_matches"][:5],
                "note": "Estatística histórica — hipótese, não previsão.",
            })

        return {
            "backtest_run_at": datetime.utcnow().isoformat(),
            "matches_analyzed": len(contexts),
            "rules": output,
        }

    def _convert_to_contexts(self, raw: list[dict]) -> list[MatchContext]:
        """Convert raw historical match dicts to MatchContext objects."""
        contexts = []
        for i, m in enumerate(raw):
            ctx = MatchContext(
                match_id=m.get("match_id", 1000 + i),
                home_team_name=m.get("home_team", "Home"),
                away_team_name=m.get("away_team", "Away"),
                league_name=m.get("league", ""),
                home_score=m.get("home_score", 0),
                away_score=m.get("away_score", 0),
                minute=90,  # Historical = finished
                status="finished",
                home_yellow_cards=m.get("home_yellow_cards", 0),
                away_yellow_cards=m.get("away_yellow_cards", 0),
                home_corners=m.get("home_corners", 0),
                away_corners=m.get("away_corners", 0),
                season=m.get("season", ""),
                league_is_important=True,
                home_is_elite=True,
                league_division=1,
            )
            contexts.append(ctx)
        return contexts


backtest_service = BacktestService()
