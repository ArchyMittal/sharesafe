"""
ShareSafe — Pydantic models (v2)
Covers: resources, borrow requests, users, auth, conditions, and action payloads.
"""
from __future__ import annotations
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginPayload(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: Dict[str, Any]

# ─── User ─────────────────────────────────────────────────────────────────────

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    role: Literal["owner", "borrower", "inspector", "admin", "agent", "both"] = "borrower"
    kind: Literal["human", "agent"] = "human"
    year: int = 1
    training: List[str] = Field(default_factory=list)
    team_id: Optional[str] = None
    avatar: Optional[str] = None
    title: Optional[str] = None

# ─── Resource ─────────────────────────────────────────────────────────────────

ResourceStatus = Literal["available", "requested", "approved", "checked_out", "not_ready", "maintenance"]
ResourceCategory = Literal["lab-equipment", "av-equipment", "tools", "sports", "spaces", "other"]

class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: ResourceCategory = "other"
    location: str
    description: str
    owner_id: str
    status: ResourceStatus = "available"
    readiness_state: Literal["ready", "ready_with_conditions", "not_ready"] = "ready"
    hold_id: Optional[str] = None
    rules_json: Optional[str] = None
    image_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    training_required: bool = False
    training_description: Optional[str] = None
    usage_rules: Optional[str] = None
    max_duration_days: int = 7
    bay_tag: Optional[str] = None
    item_code: Optional[str] = None

class ResourceCreate(BaseModel):
    name: str
    category: ResourceCategory = "other"
    location: str
    description: str
    owner_id: Optional[str] = None
    image_url: Optional[str] = None
    training_required: bool = False
    training_description: Optional[str] = None
    usage_rules: Optional[str] = None
    max_duration_days: int = 7
    bay_tag: Optional[str] = None
    item_code: Optional[str] = None
    rules_json: Optional[str] = None

# ─── Borrow Request ───────────────────────────────────────────────────────────

RequestStatus = Literal[
    "requested", "pending", "approved", "rejected", "waitlisted",
    "checked_in", "checked_out", "returned", "cancelled", "overdue", "incident_open"
]

class BorrowRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    requester_id: str
    owner_id: str
    status: RequestStatus = "requested"
    # Borrower inputs
    message: Optional[str] = None
    purpose: Optional[str] = None
    justification: Optional[str] = None
    start_date: str
    end_date: str
    training_acknowledged: bool = False
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    approved_at: Optional[str] = None
    rejected_at: Optional[str] = None
    waitlisted_at: Optional[str] = None
    checked_in_at: Optional[str] = None
    checked_out_at: Optional[str] = None
    returned_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    # Owner action
    owner_reason: Optional[str] = None
    # Decision trace
    decision_trace_json: Optional[str] = None

class BorrowRequestCreate(BaseModel):
    resource_id: str
    requester_id: Optional[str] = None
    message: Optional[str] = None
    purpose: Optional[str] = None
    justification: Optional[str] = None
    start_date: str
    end_date: str
    training_acknowledged: bool = False

# ─── Action Payloads ──────────────────────────────────────────────────────────

class OwnerActionPayload(BaseModel):
    owner_reason: Optional[str] = None

class CheckoutPayload(BaseModel):
    condition_note: Optional[str] = None
    condition_on_checkout: Optional[str] = None

    def get_note(self) -> str:
        return (self.condition_note or self.condition_on_checkout or "").strip()

class ReturnPayload(BaseModel):
    condition_note: Optional[str] = None
    condition_on_return: Optional[str] = None
    incident_type: Optional[str] = None
    incident_description: Optional[str] = None

    def get_note(self) -> str:
        return (self.condition_note or self.condition_on_return or "").strip()

class IncidentPayload(BaseModel):
    incident_type: Literal["damage", "fault", "delay", "missing_parts", "other"] = "fault"
    incident_description: str
    resource_id: Optional[str] = None
    booking_id: Optional[str] = None

class ClearHoldPayload(BaseModel):
    cleared_note: str
