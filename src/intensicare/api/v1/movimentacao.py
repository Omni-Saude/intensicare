"""Patient Movement / ADT API Router — REST endpoints for bed grid and movements.

4 endpoints conforme contrato OpenAPI:
  GET    /patients/{mpi_id}/movements   — List patient movement history
  POST   /patients/{mpi_id}/movements   — Register a new movement
  GET    /beds                          — Bed grid with status summary
  PUT    /beds/{bed_id}                 — Update bed status
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User
from intensicare.schemas.movimentacao import (
    BedGridResponse,
    BedGridSummary,
    BedSchema,
    PatientMovementListResponse,
    PatientMovementSchema,
    RegisterMovementRequest,
)
from intensicare.services.domain_movimentacao import (
    get_bed_grid,
    get_patient_movements,
    register_movement,
    update_bed_status,
)

router = APIRouter(prefix="/api/v1", tags=["movimentacao"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_iso_to_datetime(iso_str: str | None) -> datetime:
    """Parse ISO-8601 string to datetime, falling back to now on failure."""
    if not iso_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def _to_movement_response(movement) -> PatientMovementSchema:
    """Map a domain MovementRecord to a PatientMovementSchema."""
    return PatientMovementSchema(
        id=movement.id,
        mpi_id=movement.mpi_id,
        type=movement.type,
        from_unit=movement.from_unit,
        to_unit=movement.to_unit,
        from_bed=movement.from_bed,
        to_bed=movement.to_bed,
        timestamp=_parse_iso_to_datetime(movement.timestamp),
        notes=movement.notes,
        registered_by=movement.registered_by,
        created_at=_parse_iso_to_datetime(movement.created_at),
    )


def _to_bed_response(bed) -> BedSchema:
    """Map a domain BedRecord to a BedSchema."""
    return BedSchema(
        id=bed.id,
        unit=bed.unit,
        status=bed.status,
        current_patient_mpi_id=bed.current_patient_mpi_id,
        last_updated=_parse_iso_to_datetime(getattr(bed, "last_cleaned_at", None))
        if bed.last_cleaned_at
        else datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/movements — List patient movement history
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/movements",
    response_model=PatientMovementListResponse,
)
async def list_movements(
    mpi_id: str,
    type: str | None = Query(
        None,
        alias="type",
        description="Filter by movement type: admission, transfer, discharge",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
) -> PatientMovementListResponse:
    """List movement history for a patient with optional type filter.

    Returns {movements, total} following AUDIT-007 pattern.
    """
    result = get_patient_movements(
        mpi_id=mpi_id,
        movement_type=type,
        limit=limit,
        offset=offset,
    )

    return PatientMovementListResponse(
        movements=[_to_movement_response(m) for m in result.movements],
        total=result.total,
    )


# ---------------------------------------------------------------------------
# POST /patients/{mpi_id}/movements — Register a new movement
# ---------------------------------------------------------------------------


@router.post(
    "/patients/{mpi_id}/movements",
    response_model=PatientMovementSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_movement(
    mpi_id: str,
    body: RegisterMovementRequest,
    current_user: User = Depends(get_current_user),
) -> PatientMovementSchema:
    """Register a patient movement (admission, transfer, discharge).

    Validates bed availability, patient state consistency, and movement rules.
    Returns 409 on conflicts (occupied bed, patient already admitted, etc.).
    """
    # Validate mpi_id consistency between path and body
    if body.mpi_id and body.mpi_id != mpi_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"mpi_id mismatch: path '{mpi_id}' vs body '{body.mpi_id}'",
        )

    try:
        movement = register_movement(
            mpi_id=mpi_id,
            movement_type=body.type,
            from_unit=body.from_unit,
            to_unit=body.to_unit,
            from_bed=body.from_bed,
            to_bed=body.to_bed,
            timestamp=body.timestamp.isoformat() if body.timestamp else "",
            notes=body.notes,
            registered_by=body.registered_by or current_user.username,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _to_movement_response(movement)


# ---------------------------------------------------------------------------
# GET /beds — Bed grid with status summary
# ---------------------------------------------------------------------------


@router.get(
    "/beds",
    response_model=BedGridResponse,
)
async def list_beds(
    unit: str | None = Query(None, description="Filter by unit name"),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by bed status: free, occupied, blocked, cleaning",
    ),
    current_user: User = Depends(get_current_user),
) -> BedGridResponse:
    """Return the full bed grid with status summary.

    Supports optional filters by unit and status.
    """
    result = get_bed_grid(unit=unit, status=status_filter)

    return BedGridResponse(
        beds=[_to_bed_response(b) for b in result.beds],
        summary=BedGridSummary(
            total=result.summary.get("total", 0),
            free=result.summary.get("free", 0),
            occupied=result.summary.get("occupied", 0),
            blocked=result.summary.get("blocked", 0),
            cleaning=result.summary.get("cleaning", 0),
        ),
    )


# ---------------------------------------------------------------------------
# PUT /beds/{bed_id} — Update bed status
# ---------------------------------------------------------------------------


@router.put(
    "/beds/{bed_id}",
    response_model=BedSchema,
)
async def update_bed(
    bed_id: str,
    status_value: str = Query(
        ...,
        alias="status",
        description="New status: free, occupied, blocked, cleaning",
    ),
    notes: str | None = Query(None, description="Optional notes about the change"),
    current_user: User = Depends(get_current_user),
) -> BedSchema:
    """Update bed status.

    Cannot free a bed that has an admitted patient — discharge or transfer
    the patient first.
    Returns 404 if bed not found, 409 on invalid transition.
    """
    try:
        bed = update_bed_status(bed_id=bed_id, status=status_value, notes=notes)
    except ValueError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _to_bed_response(bed)
