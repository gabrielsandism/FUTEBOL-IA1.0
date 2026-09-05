"""Rules API routes"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.core.engine.rule_engine import rule_engine

router = APIRouter()


class RuleUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    parameters: Optional[dict] = None


@router.get("/")
async def list_rules():
    return {"rules": rule_engine.get_rules_info()}


@router.get("/{rule_code}")
async def get_rule(rule_code: str):
    rules = rule_engine.get_rules_info()
    rule = next((r for r in rules if r["rule_code"] == rule_code.upper()), None)
    if not rule:
        return {"error": "Rule not found"}
    return {"rule": rule}


@router.patch("/{rule_code}")
async def update_rule(rule_code: str, body: RuleUpdateRequest):
    code = rule_code.upper()
    changes = {}

    if body.is_active is not None:
        ok = rule_engine.set_rule_active(code, body.is_active)
        if ok:
            changes["is_active"] = body.is_active

    if body.parameters:
        ok = rule_engine.update_parameters(code, body.parameters)
        if ok:
            changes["parameters"] = body.parameters

    if not changes:
        return {"error": "Rule not found or no changes applied"}

    return {"rule_code": code, "updated": changes}
