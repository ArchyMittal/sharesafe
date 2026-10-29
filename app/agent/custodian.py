# app/agent/custodian.py
"""
Custodian agent module (stub - P4 will replace with bounded autonomy agent & evidence packet generation).
"""
from __future__ import annotations
from typing import Optional
from app.contracts import EvidencePacket

def on_incident(incident_id: str, resource_id: str, context: Optional[dict] = None) -> Optional[EvidencePacket]:
    """
    Called when an incident/fault is reported.
    P1 stub: no-op until P4 lands.
    """
    return None
