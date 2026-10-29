# app/engine/decision.py
"""
Decision engine module (stub - P3 will replace with full explainable decision + fairness engine).
"""
from __future__ import annotations
from typing import List, Optional
from app.contracts import Decision, Verdict, RequestCtx, ResourceCtx, BookingCtx

def evaluate_request(
    request: RequestCtx,
    resource: ResourceCtx,
    history: Optional[List[BookingCtx]] = None,
) -> Decision:
    """
    Evaluate a booking request against resource rules and fairness history.
    P1 stub: returns NEEDS_HUMAN until P3 implements the deterministic engine.
    """
    return Decision(
        verdict=Verdict.NEEDS_HUMAN,
        rule_results=[],
        priority=None,
        waitlist_position=None,
        explanation="Owner review required (decision engine stub).",
    )
