"""
ShareSafe — Pydantic models (v2)
Covers: resources, borrow requests, users, and all action payloads.
"""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

# ─── User ─────────────────────────────────────────────────────────────────────

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    role: Literal["owner", "borrower", "both"] = "both"

# ─── Resource ─────────────────────────────────────────────────────────────────

ResourceStatus   = Literal["available", "requested", "approved", "checked_out"]
ResourceCategory = Literal["lab-equipment", "av-equipment", "tools", "sports", "spaces", "other"]

class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: ResourceCategory = "other"
    location: str
    description: str
    owner_id: str
    status: ResourceStatus = "available"
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
    owner_id: str
    image_url: Optional[str] = None
    training_required: bool = False
    training_description: Optional[str] = None
    usage_rules: Optional[str] = None
    max_duration_days: int = 7
    bay_tag: Optional[str] = None
    item_code: Optional[str] = None

# ─── Borrow Request ───────────────────────────────────────────────────────────

RequestStatus = Literal[
    "pending", "approved", "rejected", "waitlisted",
    "checked_out", "returned", "cancelled"
]

class BorrowRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    requester_id: str
    owner_id: str
    status: RequestStatus = "pending"
    # Borrower inputs
    message: Optional[str] = None
    purpose: Optional[str] = None
    start_date: str
    end_date: str
    training_acknowledged: bool = False
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    approved_at: Optional[str] = None
    rejected_at: Optional[str] = None
    waitlisted_at: Optional[str] = None
    checked_out_at: Optional[str] = None
    returned_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    # Owner action
    owner_reason: Optional[str] = None
    # Condition recording
    condition_on_checkout: Optional[str] = None
    condition_on_return: Optional[str] = None
    # Incident
    incident_type: Optional[str] = None        # "damage" | "delay" | "other"
    incident_description: Optional[str] = None

class BorrowRequestCreate(BaseModel):
    resource_id: str
    requester_id: str
    message: Optional[str] = None
    purpose: Optional[str] = None
    start_date: str
    end_date: str
    training_acknowledged: bool = False

# ─── Action Payloads ──────────────────────────────────────────────────────────

class OwnerActionPayload(BaseModel):
    owner_reason: Optional[str] = None

class CheckoutPayload(BaseModel):
    condition_on_checkout: Optional[str] = None

class ReturnPayload(BaseModel):
    condition_on_return: Optional[str] = None
    incident_type: Optional[str] = None
    incident_description: Optional[str] = None

class IncidentPayload(BaseModel):
    incident_type: Literal["damage", "delay", "other"]
    incident_description: str
