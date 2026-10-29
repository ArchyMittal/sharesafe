# app/core/audit.py
"""
Audit log module (stub - P2 will replace with hash-chained tamper-evident log).
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime
from typing import Any, List, Dict

_in_memory_audit: List[Dict[str, Any]] = []

def append_audit(actor_id: str, action: str, payload: dict) -> str:
    """
    Append an entry to the audit log and return the entry hash.
    P1 stub: stores in memory and returns SHA-256 hash.
    """
    prev_hash = _in_memory_audit[-1]["hash"] if _in_memory_audit else "0" * 64
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "actor_id": actor_id,
        "action": action,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    raw = json.dumps(entry, sort_keys=True, default=str)
    entry_hash = hashlib.sha256((prev_hash + raw).encode("utf-8")).hexdigest()
    entry["hash"] = entry_hash
    _in_memory_audit.append(entry)
    return entry_hash

def get_audit_trail() -> List[Dict[str, Any]]:
    return list(_in_memory_audit)

