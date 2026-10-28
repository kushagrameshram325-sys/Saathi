"""
SAATHI REST API routes.

Endpoints
---------
GET  /health                  – Health check
GET  /services                – List support-service directory (q, category filters)
GET  /services/{id}           – Retrieve one service
POST /hazards                 – Create a public-space hazard report
GET  /hazards                 – List recent hazard reports (status filter)
POST /support-requests        – Save a private support preference / request

Privacy notes
-------------
* Coordinates supplied to POST /hazards are stored but intentionally omitted from
  every API response to prevent location inference via reference-code guessing.
* POST /support-requests has no public GET counterpart.  Reference codes are
  returned only in the 201 response body; they cannot be looked up later.
* Consent (boolean) must be True in every support-request submission.
"""

from datetime import datetime, timezone
from secrets import token_hex
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import HazardReport, SupportRequest, SupportService
from app.schemas.api import (
    HazardCreate,
    HazardOut,
    ServiceOut,
    SupportRequestCreate,
    SupportRequestOut,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    summary="Health check",
    tags=["Meta"],
)
def health():
    """Confirm that the API is reachable and the server clock is accessible."""
    return {
        "status": "ok",
        "service": "SAATHI API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Support-service directory
# ---------------------------------------------------------------------------

@router.get(
    "/services",
    response_model=list[ServiceOut],
    summary="List support services",
    tags=["Services"],
)
def list_services(
    q: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Free-text search across name, description, category, and city.",
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter by category slug (e.g. 'helpline', 'emergency', 'counselling'). "
                    "Pass 'all' or omit to return all categories.",
    ),
    db: Session = Depends(get_db),
):
    """
    Return the list of support-service directory entries.

    All entries in the seed data are explicitly **not verified** and marked
    `verified=false`.  The demo listings are illustrative only.
    """
    query = db.query(SupportService)

    if category and category.strip().lower() not in ("", "all"):
        query = query.filter(SupportService.category == category.strip().lower())

    if q and q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                SupportService.name.ilike(like),
                SupportService.description.ilike(like),
                SupportService.category.ilike(like),
                SupportService.city.ilike(like),
            )
        )

    return query.order_by(SupportService.name.asc()).all()


@router.get(
    "/services/{service_id}",
    response_model=ServiceOut,
    summary="Get one service",
    tags=["Services"],
    responses={404: {"description": "Service not found"}},
)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Return the directory entry with the given integer id."""
    item = db.get(SupportService, service_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
    return item


# ---------------------------------------------------------------------------
# Hazard reports
# ---------------------------------------------------------------------------

@router.post(
    "/hazards",
    response_model=HazardOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a hazard report",
    tags=["Hazards"],
)
def create_hazard(payload: HazardCreate, db: Session = Depends(get_db)):
    """
    Store a public-space safety hazard report and return a reference code.

    **Privacy**: latitude/longitude, if supplied, are stored in the database
    but are **not returned** in any API response.  This prevents location
    exposure through reference-code enumeration.

    No authority is contacted automatically by this endpoint.
    """
    reference_code = f"SAF-{token_hex(8).upper()}"
    report = HazardReport(
        reference_code=reference_code,
        category=payload.category.strip().lower(),
        description=payload.description.strip(),
        location_text=payload.location_text.strip(),
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get(
    "/hazards",
    response_model=list[HazardOut],
    summary="List hazard reports",
    tags=["Hazards"],
)
def list_hazards(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filter by status string (e.g. 'received', 'reviewed', 'resolved').",
    ),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Return recent hazard reports, newest first.

    Coordinates are intentionally omitted from every response item.
    """
    query = db.query(HazardReport)
    if status_filter:
        query = query.filter(HazardReport.status == status_filter.strip().lower())
    return query.order_by(HazardReport.created_at.desc()).limit(limit).all()


# ---------------------------------------------------------------------------
# Support preference / request
# ---------------------------------------------------------------------------

@router.post(
    "/support-requests",
    response_model=SupportRequestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Save a private support preference",
    tags=["Support Requests"],
)
def create_support_request(payload: SupportRequestCreate, db: Session = Depends(get_db)):
    """
    Record a support category preference and return a private reference code.

    **Privacy contract**
    * No public GET endpoint exists for support requests; the reference code
      cannot be looked up by a third party.
    * `consent` must be `true`; the request is rejected with HTTP 422 otherwise.
    * This demo does **not** contact any support provider automatically.
    * The `message` field is stored in the local SQLite database and is **not**
      returned in the response body.
    """
    if not payload.consent:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="consent must be true to submit a support preference.",
        )

    reference_code = f"SUP-{token_hex(8).upper()}"
    request = SupportRequest(
        reference_code=reference_code,
        support_type=payload.support_type.strip().lower(),
        preferred_contact=payload.preferred_contact.strip().lower(),
        message=payload.message.strip() if payload.message else "",
        status="received",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
