"""
ShareSafe — FastAPI Application
Campus platform for safely sharing equipment and spaces.

Run:
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    (uses the venv in the chatbot/ parent directory)

Visit: http://127.0.0.1:8000
"""
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.store import JsonStore
from app.sharesafe_models import (
    BorrowRequest,
    BorrowRequestCreate,
    Resource,
    ResourceCreate,
    ReturnPayload,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sharesafe")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ShareSafe — Campus Resource Sharing",
    description="Safely share equipment and spaces across campus.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Paths & Stores
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

resources_store = JsonStore(DATA_DIR / "resources.json")
requests_store = JsonStore(DATA_DIR / "requests.json")
users_store = JsonStore(DATA_DIR / "users.json")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.utcnow().isoformat()


def _get_resource_or_404(resource_id: str) -> dict:
    r = resources_store.get(resource_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Resource '{resource_id}' not found.")
    return r


def _get_request_or_404(request_id: str) -> dict:
    req = requests_store.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Request '{request_id}' not found.")
    return req


def _enrich_request(req: dict) -> dict:
    """Attach resource details and requester name to a request dict for the UI."""
    res = resources_store.get(req.get("resource_id", ""))
    user = users_store.get(req.get("requester_id", ""))
    owner = users_store.get(req.get("owner_id", ""))
    return {
        **req,
        "resource_name": res["name"] if res else "Unknown",
        "resource_location": res["location"] if res else "",
        "resource_category": res["category"] if res else "",
        "resource_image": res.get("image_url") if res else None,
        "bay_tag": res.get("bay_tag") if res else "",
        "item_code": res.get("item_code") if res else "",
        "requester_name": user["name"] if user else "Unknown",
        "requester_title": user.get("title", "") if user else "",
        "owner_name": owner["name"] if owner else "Unknown",
    }

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.get("/api/users")
async def list_users():
    """Return all demo users (for the role switcher)."""
    return users_store.all()

# ---------------------------------------------------------------------------
# Resources  —  GET /api/resources  &  POST /api/resources
# ---------------------------------------------------------------------------

@app.get("/api/resources")
async def list_resources(status: Optional[str] = None, category: Optional[str] = None):
    """
    List all resources.
    Optional query params: ?status=available|requested|checked_out
                           ?category=lab-equipment|av-equipment|tools|sports|spaces|other
    """
    items = resources_store.all()
    if status:
        items = [i for i in items if i.get("status") == status]
    if category:
        items = [i for i in items if i.get("category") == category]
    return items


@app.post("/api/resources", status_code=201)
async def create_resource(payload: ResourceCreate):
    """List a new resource for sharing."""
    resource = Resource(**payload.model_dump())
    resources_store.insert(resource.model_dump())
    logger.info(f"Resource created: {resource.name} ({resource.id})")
    return resource


# ---------------------------------------------------------------------------
# Single resource  —  GET /api/resources/{id}
# ---------------------------------------------------------------------------

@app.get("/api/resources/{resource_id}")
async def get_resource(resource_id: str):
    return _get_resource_or_404(resource_id)


# ---------------------------------------------------------------------------
# Borrow Requests  —  POST /api/requests
# ---------------------------------------------------------------------------

@app.post("/api/requests", status_code=201)
async def create_request(payload: BorrowRequestCreate):
    """
    Borrower submits a request for a resource.
    Validates that the resource is currently available and sets it to 'requested'.
    """
    resource = _get_resource_or_404(payload.resource_id)

    if resource["status"] != "available":
        raise HTTPException(
            status_code=409,
            detail=f"Resource is currently '{resource['status']}' and cannot be requested.",
        )

    borrow_req = BorrowRequest(
        resource_id=payload.resource_id,
        requester_id=payload.requester_id,
        owner_id=resource["owner_id"],
        message=payload.message,
        purpose=payload.purpose,
        start_date=payload.start_date,
        end_date=payload.end_date,
        training_acknowledged=payload.training_acknowledged,
    )
    requests_store.insert(borrow_req.model_dump())
    resources_store.update(payload.resource_id, {"status": "requested"})
    logger.info(f"Request created: {borrow_req.id} for resource {payload.resource_id}")
    return _enrich_request(borrow_req.model_dump())


# ---------------------------------------------------------------------------
# List Requests  —  GET /api/requests
# ---------------------------------------------------------------------------

@app.get("/api/requests")
async def list_requests(
    owner_id: Optional[str] = None,
    requester_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """
    List requests with optional filters:
      ?owner_id=u1        → requests the owner needs to action
      ?requester_id=u2    → requests the borrower made
      ?resource_id=r1     → history for a specific resource
      ?status=pending     → filter by status
    """
    items = requests_store.all()
    if owner_id:
        items = [i for i in items if i.get("owner_id") == owner_id]
    if requester_id:
        items = [i for i in items if i.get("requester_id") == requester_id]
    if resource_id:
        items = [i for i in items if i.get("resource_id") == resource_id]
    if status:
        items = [i for i in items if i.get("status") == status]

    # Sort newest first
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return [_enrich_request(i) for i in items]


# ---------------------------------------------------------------------------
# Approve  —  PATCH /api/requests/{id}/approve
# ---------------------------------------------------------------------------

@app.patch("/api/requests/{request_id}/approve")
async def approve_request(request_id: str):
    """Owner approves the pending request."""
    req = _get_request_or_404(request_id)
    if req["status"] != "pending":
        raise HTTPException(
            status_code=409, detail=f"Request is '{req['status']}', not 'pending'."
        )
    updated = requests_store.update(request_id, {"status": "approved", "approved_at": _now()})
    logger.info(f"Request approved: {request_id}")
    return _enrich_request(updated)


# ---------------------------------------------------------------------------
# Reject  —  PATCH /api/requests/{id}/reject
# ---------------------------------------------------------------------------

@app.patch("/api/requests/{request_id}/reject")
async def reject_request(request_id: str):
    """Owner rejects the pending request; resource reverts to 'available'."""
    req = _get_request_or_404(request_id)
    if req["status"] != "pending":
        raise HTTPException(
            status_code=409, detail=f"Request is '{req['status']}', not 'pending'."
        )
    updated = requests_store.update(request_id, {"status": "rejected", "rejected_at": _now()})
    resources_store.update(req["resource_id"], {"status": "available"})
    logger.info(f"Request rejected: {request_id}")
    return _enrich_request(updated)


# ---------------------------------------------------------------------------
# Check Out  —  PATCH /api/requests/{id}/checkout
# ---------------------------------------------------------------------------

@app.patch("/api/requests/{request_id}/checkout")
async def checkout_request(request_id: str):
    """Borrower checks out an approved request; resource becomes 'checked_out'."""
    req = _get_request_or_404(request_id)
    if req["status"] != "approved":
        raise HTTPException(
            status_code=409, detail=f"Request is '{req['status']}', must be 'approved' to check out."
        )
    updated = requests_store.update(
        request_id, {"status": "checked_out", "checked_out_at": _now()}
    )
    resources_store.update(req["resource_id"], {"status": "checked_out"})
    logger.info(f"Checked out: {request_id}")
    return _enrich_request(updated)


# ---------------------------------------------------------------------------
# Return  —  PATCH /api/requests/{id}/return
# ---------------------------------------------------------------------------

@app.patch("/api/requests/{request_id}/return")
async def return_request(request_id: str, payload: ReturnPayload = ReturnPayload()):
    """Borrower returns the item; resource reverts to 'available'."""
    req = _get_request_or_404(request_id)
    if req["status"] != "checked_out":
        raise HTTPException(
            status_code=409,
            detail=f"Request is '{req['status']}', must be 'checked_out' to return.",
        )
    patch = {
        "status": "returned",
        "returned_at": _now(),
        "condition_note": payload.condition_note or "Returned in good condition.",
    }
    updated = requests_store.update(request_id, patch)
    resources_store.update(req["resource_id"], {"status": "available"})
    logger.info(f"Returned: {request_id}")
    return _enrich_request(updated)


# ---------------------------------------------------------------------------
# Resource History  —  GET /api/resources/{id}/history
# ---------------------------------------------------------------------------

@app.get("/api/resources/{resource_id}/history")
async def resource_history(resource_id: str):
    """Return the full chronological request history for a single resource."""
    _get_resource_or_404(resource_id)  # 404 check
    history = requests_store.filter(resource_id=resource_id)
    history.sort(key=lambda x: x.get("created_at", ""))
    return [_enrich_request(h) for h in history]


# ---------------------------------------------------------------------------
# Static files + root
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_index():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return JSONResponse({"status": "ShareSafe API online. Visit /docs for the API explorer."})


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "resources": len(resources_store.all()),
        "requests": len(requests_store.all()),
        "users": len(users_store.all()),
    }
