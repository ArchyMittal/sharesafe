# app/core/authority.py
"""
Authority gate module (stub - P2 will replace with full authority matrix and audit logging).
"""
from __future__ import annotations
from typing import Any, Dict, Callable
from app.contracts import Actor

_action_handlers: Dict[str, Callable[[dict], dict]] = {}

def register_action_handler(action: str, handler: Callable[[dict], dict]) -> None:
    _action_handlers[action] = handler

def execute(actor: Actor, action: str, args: dict) -> dict:
    """
    Execute an action under the authority gate.
    P1 stub calls the registered tool/handler directly, or returns args.
    """
    if action in _action_handlers:
        return _action_handlers[action](args)
    return {"action": action, "actor": actor.id, "args": args, "status": "executed"}
