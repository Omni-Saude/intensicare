"""Prescription API Router — REST endpoints for ICU prescriptions.

5 endpoints conforme contrato OpenAPI + ADR-027:
  GET    /patients/{mpi_id}/prescriptions  — List patient prescriptions
  POST   /patients/{mpi_id}/prescriptions  — Create a new prescription
  GET    /prescriptions/{id}               — Get a single prescription
  PUT    /prescriptions/{id}               — Update a prescription (state machine)
  POST   /prescriptions/{id}/state         — Execute a state transition (ADR-027)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.user import User
from intensicare.schemas.prescricao import (
    InteracaoAlertaSchema,
    PrescriptionCreate,
    PrescriptionListResponse,
    PrescriptionSchema,
    PrescriptionStateTransition,
    PrescriptionUpdate,
)
from intensicare.services.domain_prescricao import (
    ConcurrencyError,
    InteractionAlert,
    PrescriptionRecord,
    PrescriptionStateMachine,
    create_prescription,
    get_prescription,
    get_state_machine,
    list_prescriptions,
    update_prescription,
    _transition_state,
)

router = APIRouter(prefix="/api/v1", tags=["prescricao"])


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


def _parse_dosage(dosage_str: str) -> tuple[float, str]:
    """Parse a dosage string like '500mg' into (dose, unit).

    Returns (0.0, 'mg') if unable to parse.
    """
    if not dosage_str:
        return 0.0, "mg"

    dosage_str = dosage_str.strip()
    # Try common patterns: 500mg, 1g, 50mcg, 10UI, 100mL, 2.5mcg/kg/min
    import re

    match = re.match(r"^([\d.]+)\s*([a-zA-Z/%]+)$", dosage_str)
    if match:
        dose = float(match.group(1))
        unit = match.group(2)
        return dose, unit

    # Fallback: try to parse as just a number
    try:
        return float(dosage_str), "mg"
    except ValueError:
        return 0.0, "mg"


def _to_prescription_response(rx: PrescriptionRecord) -> PrescriptionSchema:
    """Map a domain PrescriptionRecord to a PrescriptionSchema."""
    return PrescriptionSchema(
        id=rx.id,
        mpi_id=rx.mpi_id,
        medication=rx.drug,
        dosage=f"{rx.dose}{rx.unit}" if rx.unit else str(rx.dose),
        route=rx.route,
        frequency=rx.frequency,
        start_time=_parse_iso_to_datetime(rx.start_time),
        end_time=_parse_iso_to_datetime(rx.end_time) if rx.end_time else None,
        status=rx.status,
        version=rx.version,
        prescribed_by=rx.prescribed_by,
        notes=rx.notes,
        created_at=_parse_iso_to_datetime(rx.created_at),
        updated_at=_parse_iso_to_datetime(rx.updated_at),
    )


def _to_alert_response(alert: InteractionAlert) -> InteracaoAlertaSchema:
    """Map a domain InteractionAlert to an InteracaoAlertaSchema."""
    return InteracaoAlertaSchema(
        id=alert.id or 0,
        prescricao_id=0,  # not tracked separately in domain alerts
        severity=alert.severity,
        interaction_type=alert.interaction_type,
        description=alert.description,
        resolved=alert.resolved,
        created_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/prescriptions — List patient prescriptions
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/prescriptions",
    response_model=PrescriptionListResponse,
)
async def list_patient_prescriptions(
    mpi_id: str,
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status: draft, active, completed, discontinued, suspended, or 'all'",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionListResponse:
    """List prescriptions for a patient with optional status filter.

    Returns {prescriptions, total} following AUDIT-007 pattern.
    """
    result = await list_prescriptions(
        mpi_id=mpi_id,
        status=status_filter or "all",
        limit=limit,
        offset=offset,
        db=db,
    )

    return PrescriptionListResponse(
        prescriptions=[_to_prescription_response(rx) for rx in result.prescriptions],
        total=result.total,
    )


# ---------------------------------------------------------------------------
# POST /patients/{mpi_id}/prescriptions — Create a new prescription
# ---------------------------------------------------------------------------


@router.post(
    "/patients/{mpi_id}/prescriptions",
    response_model=PrescriptionSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient_prescription(
    mpi_id: str,
    body: PrescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionSchema:
    """Create a new prescription for a patient.

    Validates drug, dose, route, frequency, interactions, and dose safety.
    Returns 409 on validation errors or contraindicated interactions.
    """
    # Validate mpi_id consistency
    if body.mpi_id and body.mpi_id != mpi_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"mpi_id mismatch: path '{mpi_id}' vs body '{body.mpi_id}'",
        )

    # Parse dosage string into dose + unit
    dose, unit = _parse_dosage(body.dosage)

    try:
        result = await create_prescription(
            mpi_id=mpi_id,
            drug=body.medication,
            dose=dose,
            unit=unit,
            route=body.route,
            frequency=body.frequency,
            start_time=body.start_time.isoformat() if body.start_time else "",
            notes=body.notes,
            prescribed_by=body.prescribed_by or current_user.username,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return _to_prescription_response(result.prescription)


# ---------------------------------------------------------------------------
# GET /prescriptions/state-machine — State machine definition
# ---------------------------------------------------------------------------


@router.get(
    "/prescriptions/state-machine",
    response_model=dict,
)
async def get_state_machine_definition(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return the prescription state machine definition (ADR-027).

    Exposes all valid states, allowed transitions, required clinical
    justifications, and terminal states for the prescription lifecycle.
    """
    sm = get_state_machine()
    return sm.to_dict()


# ---------------------------------------------------------------------------
# GET /prescriptions/{prescription_id} — Get a single prescription
# ---------------------------------------------------------------------------


@router.get(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionSchema,
)
async def get_single_prescription(
    prescription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionSchema:
    """Get a single prescription by ID.

    Returns 404 if not found.
    """
    rx = await get_prescription(prescription_id, db)

    if rx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found",
        )

    return _to_prescription_response(rx)


# ---------------------------------------------------------------------------
# PUT /prescriptions/{prescription_id} — Update a prescription
# ---------------------------------------------------------------------------


@router.put(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionSchema,
)
async def update_single_prescription(
    prescription_id: int,
    body: PrescriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionSchema:
    """Update a prescription with state machine support.

    Handles partial updates — only provided fields are changed.
    Supports ADR-027 state transitions via the 'status' field.
    Uses optimistic locking via 'version' field.

    Returns 404 if not found, 409 on version conflict or invalid transition.
    """
    # Build updates dict from non-None fields
    updates: dict = {}
    if body.dosage is not None:
        dose, unit = _parse_dosage(body.dosage)
        updates["dose"] = dose
        updates["unit"] = unit
    if body.route is not None:
        updates["route"] = body.route
    if body.frequency is not None:
        updates["frequency"] = body.frequency
    if body.status is not None:
        updates["status"] = body.status
    if body.notes is not None:
        updates["notes"] = body.notes
    if body.version is not None:
        updates["version"] = body.version

    try:
        rx = await update_prescription(
            prescription_id=prescription_id,
            updates=updates,
            changed_by=current_user.username,
            db=db,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found",
        )
    except ConcurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return _to_prescription_response(rx)


# ---------------------------------------------------------------------------
# POST /prescriptions/{prescription_id}/state — Transition prescription state
# ---------------------------------------------------------------------------


@router.post(
    "/prescriptions/{prescription_id}/state",
    response_model=PrescriptionSchema,
)
async def transition_prescription_state(
    prescription_id: int,
    body: PrescriptionStateTransition,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PrescriptionSchema:
    """Execute a state transition on a prescription (ADR-027).

    Validates the transition against the state machine, enforces required
    clinical justifications, and applies auto-end_time for terminal states.

    Returns 404 if not found, 409 on version conflict or invalid transition.
    """
    # Load current prescription
    rx = await get_prescription(prescription_id, db)
    if rx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found",
        )

    # Optimistic locking check
    if body.version != rx.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Version conflict: expected version {body.version}, "
                f"but current version is {rx.version}. Reload and retry."
            ),
        )

    try:
        updated_rx = _transition_state(
            prescription=rx,
            new_status=body.to_status,
            reason=body.reason,
            changed_by=body.changed_by or current_user.username,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    # Persist the state change to DB via update_prescription
    try:
        persisted_rx = await update_prescription(
            prescription_id=prescription_id,
            updates={
                "status": updated_rx.status,
                "reason": body.reason,
                "version": body.version,
            },
            changed_by=body.changed_by or current_user.username,
            db=db,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found",
        )
    except ConcurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return _to_prescription_response(persisted_rx)
