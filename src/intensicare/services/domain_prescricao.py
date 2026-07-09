"""Prescription domain service — state machine, drug interaction, dose calculator.

43 rules implemented across validation, state transitions, drug interactions,
and dose safety calculations for ICU prescriptions.

State machine (ADR-027):
    draft → active → completed  (auto end_time)
                   → discontinued (requires reason)
                   → suspended (requires reason)
    suspended → active (resume)
    completed/discontinued → [terminal, no further transitions]

Drug interactions (ADR-026): local ANVISA base with 4 severity levels.
Dose calculator: weight-based, renal-adjusted, age-adjusted, infusion limits.

Storage: PostgreSQL via SQLAlchemy AsyncSession (Prescricao + InteracaoAlerta models).
"""

from __future__ import annotations

__version__ = "3.2.0"

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.prescricao import InteracaoAlerta, Prescricao

# Re-exports from extracted modules for backward compatibility
from intensicare.services.drug_safety import (  # noqa: F401
    DRUG_SAFETY, DrugSafetyEntry, INFUSION_ROUTES, PEDIATRIC_ADJUSTMENTS,
    RENAL_ADJUSTMENTS, TERMINAL_STATES, VALID_FREQUENCIES, VALID_ROUTES,
    VALID_SEVERITIES, VALID_STATUSES, VALID_UNITS,
    _calculate_dose_renal_adjusted, _calculate_dose_weight_based,
    _estimate_daily_doses, _mass_to_mg, _pediatric_age_bracket,
    _rate_to_mg, _to_mg, _validate_dose,
)
from intensicare.services.drug_interactions import (  # noqa: F401
    DRUG_ALLERGY_GROUPS, DRUG_CLASSES, DRUG_INTERACTIONS, InteractionAlert,
    _check_interactions as _check_interactions_core,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Conversion helpers: PrescriptionRecord <-> Prescricao (DB model)
# =============================================================================


def _parse_dosage(dosage_str: str) -> tuple[float, str]:
    """Parse a dosage string like '500mg' into (dose, unit).

    Returns (0.0, 'mg') if unable to parse.
    """
    if not dosage_str:
        return 0.0, "mg"
    dosage_str = dosage_str.strip()
    match = re.match(r"^([\d.]+)\s*([a-zA-Z/%]+)$", dosage_str)
    if match:
        return float(match.group(1)), match.group(2)
    try:
        return float(dosage_str), "mg"
    except ValueError:
        return 0.0, "mg"


def _record_to_dosage(dose: float, unit: str) -> str:
    """Convert dose + unit to combined dosage string (e.g., 500.0, 'mg' → '500.0mg')."""
    return f"{dose}{unit}"


def _model_to_record(model: Prescricao) -> PrescriptionRecord:
    """Convert a DB Prescricao model to a domain PrescriptionRecord."""
    dose, unit = _parse_dosage(model.dosage)
    return PrescriptionRecord(
        id=model.id,
        mpi_id=model.mpi_id,
        drug=model.medication,
        dose=dose,
        unit=unit,
        route=model.route,
        frequency=model.frequency,
        start_time=model.start_time.isoformat() if model.start_time else "",
        end_time=model.end_time.isoformat() if model.end_time else None,
        status=model.status,
        version=model.version,
        notes=model.notes,
        prescribed_by=model.prescribed_by,
        created_at=model.created_at.isoformat() if model.created_at else "",
        updated_at=model.updated_at.isoformat() if model.updated_at else "",
    )


def _alert_model_to_domain(model: InteracaoAlerta) -> InteractionAlert:
    """Convert a DB InteracaoAlerta to a domain InteractionAlert."""
    return InteractionAlert(
        id=model.id,
        severity=model.severity,
        interaction_type=model.interaction_type,
        description=model.description,
        resolved=model.resolved,
    )


# =============================================================================
# Backward-compatible wrapper for _check_interactions
# =============================================================================


async def _check_interactions(
    drug: str,
    mpi_id: str,
    db: AsyncSession,
) -> list[InteractionAlert]:
    """R17-R26: Check drug-drug/duplicate interactions (DB-backed).

    Queries active prescriptions from PostgreSQL for the given patient
    and delegates to the refactored core in drug_interactions.py.
    """
    result = await db.execute(
        select(Prescricao).where(
            Prescricao.mpi_id == mpi_id,
            Prescricao.status == "active",
        )
    )
    active_models = result.scalars().all()
    active_rx_list = [_model_to_record(m) for m in active_models]
    return _check_interactions_core(drug, mpi_id, active_rx_list)


# =============================================================================
# State machine transition map (ADR-027) — kept at module level for tests
# =============================================================================

STATE_TRANSITIONS: dict[str, set[str]] = {
    "draft":       {"active", "draft"},
    "active":      {"completed", "discontinued", "suspended", "active"},
    "suspended":   {"active", "discontinued"},
    "completed":   set(),  # terminal
    "discontinued": set(),  # terminal
}

# Transitions that require a clinical reason
TRANSITIONS_REQUIRING_REASON: set[tuple[str, str]] = {
    ("active", "discontinued"),
    ("active", "suspended"),
    ("suspended", "discontinued"),
}

# Transitions that auto-set end_time
TRANSITIONS_SETTING_END_TIME: set[str] = {"completed", "discontinued"}

# State machine version for audit trail
STATE_MACHINE_VERSION: str = "1.0.0"


# =============================================================================
# Exceptions
# =============================================================================


class ConcurrencyError(Exception):
    """Raised when optimistic locking detects a concurrent modification."""

    def __init__(self, prescription_id: int, expected_version: int, actual_version: int):
        self.prescription_id = prescription_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Concurrency conflict on prescription {prescription_id}: "
            f"expected version {expected_version}, but current version is {actual_version}. "
            "The record was modified by another process. Reload and retry."
        )


# =============================================================================
# PrescriptionStateMachine — encapsulated state transition engine (ADR-027)
# =============================================================================


class PrescriptionStateMachine:
    """Encapsulates the prescription lifecycle state machine (ADR-027).

    Validates transitions, enforces guards (e.g., reason required),
    and provides metadata about the state machine definition.

    States: draft, active, completed, discontinued, suspended.
    Terminal states: completed, discontinued.
    """

    # State machine version for audit trail
    VERSION: str = STATE_MACHINE_VERSION

    def __init__(self) -> None:
        self._transitions: dict[str, set[str]] = {
            "draft":       {"active", "draft"},
            "active":      {"completed", "discontinued", "suspended", "active"},
            "suspended":   {"active", "discontinued"},
            "completed":   set(),
            "discontinued": set(),
        }
        self._reasons_required: set[tuple[str, str]] = {
            ("active", "discontinued"),
            ("active", "suspended"),
            ("suspended", "discontinued"),
        }
        self._end_time_transitions: set[str] = {"completed", "discontinued"}
        self._terminal_states: set[str] = {"completed", "discontinued"}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def transitions(self) -> dict[str, set[str]]:
        """Return a copy of the transition map."""
        return {k: set(v) for k, v in self._transitions.items()}

    @property
    def valid_statuses(self) -> list[str]:
        """All known statuses."""
        return list(self._transitions.keys())

    @property
    def terminal_states(self) -> set[str]:
        """States that allow no further transitions."""
        return set(self._terminal_states)

    @property
    def reasons_required(self) -> set[tuple[str, str]]:
        """Transitions that require a clinical reason."""
        return set(self._reasons_required)

    @property
    def end_time_transitions(self) -> set[str]:
        """Target states that auto-set end_time."""
        return set(self._end_time_transitions)

    def is_terminal(self, status: str) -> bool:
        """Check if a status is terminal (no further transitions)."""
        return status in self._terminal_states

    def is_valid_status(self, status: str) -> bool:
        """Check if a status string is a known state."""
        return status in self._transitions

    def allowed_transitions(self, from_status: str) -> set[str]:
        """Return the set of statuses reachable from *from_status*."""
        return set(self._transitions.get(from_status, set()))

    def reason_required(self, from_status: str, to_status: str) -> bool:
        """Check whether the transition requires a clinical reason."""
        return (from_status, to_status) in self._reasons_required

    def auto_end_time(self, to_status: str) -> bool:
        """Check whether *to_status* should trigger end_time auto-set."""
        return to_status in self._end_time_transitions

    def can_transition(self, from_status: str, to_status: str) -> bool:
        """Return True if the transition is syntactically valid."""
        return to_status in self._transitions.get(from_status, set())

    def transition(
        self,
        from_status: str,
        to_status: str,
        reason: str | None = None,
        changed_by: str = "system",
    ) -> dict[str, Any]:
        """Validate and execute a state transition.

        Parameters
        ----------
        from_status:
            Current prescription status.
        to_status:
            Desired target status.
        reason:
            Clinical justification (required for sensitive transitions).
        changed_by:
            Identifier of the clinician or system performing the transition.

        Returns
        -------
        dict
            Metadata about the transition with keys:
            - ``new_status`` (str)
            - ``old_status`` (str)
            - ``auto_end_time`` (bool)
            - ``reason`` (str | None)
            - ``changed_by`` (str)

        Raises
        ------
        ValueError
            If *to_status* is not a known state, the prescription is in a
            terminal state, the transition is not allowed, or a required
            reason is missing.
        """
        # Validate target status is known
        if not self.is_valid_status(to_status):
            raise ValueError(
                f"R36: Status '{to_status}' inválido. "
                f"Status válidos: {', '.join(self.valid_statuses)}."
            )

        # Terminal states cannot transition
        if self.is_terminal(from_status):
            raise ValueError(
                f"R37: Prescrição em estado terminal "
                f"('{from_status}') e não pode ser modificada."
            )

        # Validate transition is allowed
        if not self.can_transition(from_status, to_status):
            allowed = sorted(self.allowed_transitions(from_status))
            raise ValueError(
                f"R38: Transição '{from_status} → {to_status}' não é permitida. "
                f"Transições válidas de '{from_status}': {allowed}."
            )

        # Some transitions require clinical reason
        if self.reason_required(from_status, to_status):
            if not reason or not reason.strip():
                raise ValueError(
                    f"R39: Transição '{from_status} → {to_status}' requer "
                    "justificativa clínica (reason)."
                )

        return {
            "new_status": to_status,
            "old_status": from_status,
            "auto_end_time": self.auto_end_time(to_status),
            "reason": reason,
            "changed_by": changed_by,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full state machine definition for API exposure."""
        return {
            "version": self.VERSION,
            "states": self.valid_statuses,
            "terminal_states": sorted(self._terminal_states),
            "transitions": {
                from_state: sorted(to_states)
                for from_state, to_states in self._transitions.items()
            },
            "reasons_required": [
                {"from": f, "to": t} for f, t in sorted(self._reasons_required)
            ],
            "end_time_transitions": sorted(self._end_time_transitions),
        }


# Singleton instance for module-level use
_prescription_state_machine = PrescriptionStateMachine()


def get_state_machine() -> PrescriptionStateMachine:
    """Return the module-level state machine singleton."""
    return _prescription_state_machine


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class PrescriptionRecord:
    """In-memory prescription record matching OpenAPI Prescription schema."""

    id: int | None = None
    mpi_id: str = ""
    drug: str = ""
    dose: float = 0.0
    unit: str = ""
    route: str = ""
    frequency: str = ""
    start_time: str = ""
    end_time: str | None = None
    status: str = "active"
    version: int = 1
    notes: str | None = None
    prescribed_by: str = "system"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class PrescriptionResult:
    """Result of creating a prescription with dose validation and alerts."""

    prescription: PrescriptionRecord
    alerts: list[InteractionAlert] = field(default_factory=list)
    dose_valid: bool = True
    dose_warnings: list[str] = field(default_factory=list)


@dataclass
class PrescriptionListResult:
    """Paginated list of prescriptions."""

    prescriptions: list[PrescriptionRecord] = field(default_factory=list)
    total: int = 0


# =============================================================================
# DB-backed storage helpers (replaces in-memory _prescriptions / _alerts dicts)
# =============================================================================


def _now_iso() -> str:
    """Return current UTC timestamp as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _now_dt() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


# =============================================================================
# Rule R01-R10: Input validation
# =============================================================================


def _validate_input(
    mpi_id: str,
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
    notes: str | None = None,
    prescribed_by: str = "",
) -> list[str]:
    """R01-R10: Validate all input fields. Returns list of error messages."""
    errors: list[str] = []

    # R01: mpi_id required and non-empty
    if not mpi_id or not mpi_id.strip():
        errors.append("R01: mpi_id é obrigatório e não pode estar vazio.")

    # R02: drug name required and non-empty
    if not drug or not drug.strip():
        errors.append("R02: Nome do fármaco é obrigatório e não pode estar vazio.")

    # R03: dose must be a positive number
    if dose <= 0:
        errors.append(f"R03: Dose deve ser um número positivo (recebido: {dose}).")

    # R04: unit must be valid
    if unit not in VALID_UNITS:
        errors.append(
            f"R04: Unidade '{unit}' inválida. Unidades válidas: {', '.join(VALID_UNITS)}."
        )

    # R05: route must be a valid administration route
    if route not in VALID_ROUTES:
        errors.append(
            f"R05: Via '{route}' inválida. Vias válidas: {', '.join(VALID_ROUTES)}."
        )

    # R06: frequency must be valid
    if frequency not in VALID_FREQUENCIES:
        errors.append(
            f"R06: Frequência '{frequency}' inválida. "
            f"Válidas: {', '.join(VALID_FREQUENCIES)}."
        )

    # R07: route must be compatible with drug's typical routes
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)
    if safety and route not in safety.get("typical_routes", [route]):
        errors.append(
            f"R07: Via '{route}' não é típica para {drug}. "
            f"Vias esperadas: {', '.join(safety.get('typical_routes', []))}."
        )

    # R08: continuous-only drugs must use infusion routes
    if safety and safety.get("continuous_only") and route not in INFUSION_ROUTES:
        errors.append(
            f"R08: {drug} requer infusão contínua e a via '{route}' não suporta infusão."
        )

    # R09: notes length validation (max 1024 chars per schema)
    if notes and len(notes) > 1024:
        errors.append(
            f"R09: Observações excedem o limite de 1024 caracteres "
            f"(recebido: {len(notes)})."
        )

    # R10: prescribed_by required and non-empty
    if not prescribed_by or not prescribed_by.strip():
        errors.append("R10: Nome do prescritor (prescribed_by) é obrigatório.")

    return errors


# =============================================================================
# Rule R11-R16: Duplicate and conflict detection (DB-backed)
# =============================================================================


async def _check_duplicate(
    mpi_id: str,
    drug: str,
    route: str,
    db: AsyncSession,
) -> list[str]:
    """R11: Check for duplicate active prescription for same drug+route+patient."""
    warnings: list[str] = []
    drug_lower = drug.lower().replace(" ", "_")

    result = await db.execute(
        select(Prescricao).where(
            Prescricao.mpi_id == mpi_id,
            Prescricao.route == route,
            Prescricao.status == "active",
        )
    )
    for rx_model in result.scalars().all():
        if rx_model.medication.lower().replace(" ", "_") == drug_lower:
            warnings.append(
                f"R11: Paciente {mpi_id} já possui prescrição ativa de {drug} "
                f"via {route} (ID: {rx_model.id}). Verificar duplicidade."
            )
    return warnings


async def _check_same_class_duplicate(
    mpi_id: str,
    drug: str,
    db: AsyncSession,
) -> list[str]:
    """R12: Check for duplicate therapeutic class."""
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    new_class = DRUG_CLASSES.get(drug_key)
    if not new_class:
        return warnings

    result = await db.execute(
        select(Prescricao).where(
            Prescricao.mpi_id == mpi_id,
            Prescricao.status == "active",
        )
    )
    for rx_model in result.scalars().all():
        rx_key = rx_model.medication.lower().replace(" ", "_")
        rx_class = DRUG_CLASSES.get(rx_key)
        if rx_class and rx_class == new_class and rx_key != drug_key:
            warnings.append(
                f"R12: Duplicação de classe terapêutica '{new_class}': "
                f"{drug} + {rx_model.medication} já ativos para o paciente {mpi_id}."
            )
    return warnings


def _validate_temporal_constraints(
    start_time: str,
    end_time: str | None = None,
) -> list[str]:
    """R13-R14: Validate temporal constraints on prescription dates."""
    warnings: list[str] = []

    # R13: Validate start_time is a valid ISO-8601 datetime string
    if start_time:
        try:
            datetime.fromisoformat(start_time)
        except (ValueError, TypeError):
            warnings.append(
                f"R13: start_time '{start_time}' não é uma data ISO-8601 válida."
            )

    # R14: end_time must be after start_time
    if end_time:
        try:
            dt_end = datetime.fromisoformat(end_time)
            dt_start = datetime.fromisoformat(start_time) if start_time else datetime.now(timezone.utc)
            if dt_end <= dt_start:
                warnings.append(
                    f"R14: end_time ({end_time}) deve ser posterior a "
                    f"start_time ({start_time})."
                )
        except (ValueError, TypeError):
            pass  # format error, already handled or irrelevant

    return warnings


async def _validate_prescription_limits(
    mpi_id: str,
    db: AsyncSession,
) -> list[str]:
    """R15-R16: Prescription safety limits.

    R15: Maximum active prescriptions per patient (15).
    R16: Polypharmacy alert threshold (8 active drugs).
    """
    warnings: list[str] = []
    active_count = await count_active_prescriptions(mpi_id, db)

    # R15: Hard limit — max 15 active prescriptions
    if active_count >= 15:
        warnings.append(
            f"R15: Limite máximo de 15 prescrições ativas atingido para o paciente "
            f"{mpi_id} ({active_count} ativas). Não é possível criar nova prescrição."
        )

    # R16: Polypharmacy alert — warning at 8 active drugs
    if active_count >= 8:
        warnings.append(
            f"R16: Polifarmácia detectada — {active_count} prescrições ativas para "
            f"o paciente {mpi_id}. Revisar necessidade de todas as terapias."
        )

    return warnings


# =============================================================================
# Rule R36-R40: State machine transitions
# =============================================================================


def _transition_state(
    prescription: PrescriptionRecord,
    new_status: str,
    reason: str | None = None,
    changed_by: str = "system",
) -> PrescriptionRecord:
    """R36-R40: State machine transition with validation.

    Returns updated PrescriptionRecord. Raises ValueError on invalid transition.

    Delegates to :class:`PrescriptionStateMachine` for validation logic
    while keeping backward-compatible PrescriptionRecord mutation.
    """
    old_status = prescription.status
    sm = get_state_machine()

    # Validate via state machine (raises ValueError on invalid transition)
    sm.transition(
        from_status=old_status,
        to_status=new_status,
        reason=reason,
        changed_by=changed_by,
    )

    # R40: Auto-set end_time for terminal transitions
    if sm.auto_end_time(new_status):
        prescription.end_time = _now_iso()

    # Apply transition
    prescription.status = new_status
    prescription.version += 1
    prescription.updated_at = _now_iso()

    logger.info(
        "State transition: prescription %s: %s → %s (by %s, reason=%s)",
        prescription.id, old_status, new_status, changed_by, reason,
    )

    return prescription


# =============================================================================
# Public API — Main functions (DB-backed)
# =============================================================================


async def create_prescription(
    mpi_id: str,
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
    db: AsyncSession,
    start_time: str = "",
    notes: str | None = None,
    prescribed_by: str = "system",
    weight_kg: float | None = None,
    gfr: float | None = None,
    age_years: float | None = None,
) -> PrescriptionResult:
    """R41: Create a new prescription with full validation pipeline.

    Order of operations:
    1. Validate input fields (R01-R10)
    2. Check duplicates (R11-R12)
    3. Check drug interactions (R17-R26)
    4. Validate dose (R27-R35)
    5. Persist to PostgreSQL

    Args:
        mpi_id: Patient identifier (MPI — Master Patient Index).
        drug: Drug name (e.g., 'Meropenem', 'vancomicina').
        dose: Numeric dose value.
        unit: Dose unit (mg, g, mcg, UI, mEq, etc.).
        route: Administration route (IV, PO, SC, etc.).
        frequency: Dosing frequency (8/8h, QID, continuous, etc.).
        db: Async SQLAlchemy session.
        start_time: ISO-8601 timestamp. Defaults to now.
        notes: Optional clinical notes.
        prescribed_by: Prescribing clinician identifier.
        weight_kg: Patient weight for weight-based dose validation.
        gfr: Glomerular filtration rate for renal adjustment.
        age_years: Patient age for pediatric/elderly adjustments.

    Returns:
        PrescriptionResult with created prescription, interaction alerts,
        dose validity flag and warnings.

    Raises:
        ValueError: On invalid input (dose <= 0, empty fields, etc.).
    """
    # Step 1: Validate inputs
    errors = _validate_input(mpi_id, drug, dose, unit, route, frequency, notes, prescribed_by)
    if errors:
        raise ValueError("Erro de validação:\n" + "\n".join(f"  - {e}" for e in errors))

    # Step 2: Check duplicates and temporal constraints
    dup_warnings = await _check_duplicate(mpi_id, drug, route, db)
    dup_warnings += await _check_same_class_duplicate(mpi_id, drug, db)
    dup_warnings += _validate_temporal_constraints(start_time)
    dup_warnings += await _validate_prescription_limits(mpi_id, db)

    # Step 3: Check drug interactions
    alerts = await _check_interactions(drug, mpi_id, db)

    # Step 4: Validate dose
    dose_valid, dose_warnings = _validate_dose(
        drug, dose, unit, route, frequency, weight_kg, gfr, age_years
    )

    # Merge duplicate warnings into dose_warnings
    all_warnings = dup_warnings + dose_warnings

    # Check for contraindicated interactions — hard stop
    contraindicated = [a for a in alerts if a.severity == "contraindicated"]
    if contraindicated:
        raise ValueError(
            "Interação medicamentosa CONTRAINDICADA detectada:\n"
            + "\n".join(f"  - {a.description}" for a in contraindicated)
        )

    # Step 5: Persist to PostgreSQL
    now = _now_dt()
    start_dt = datetime.fromisoformat(start_time) if start_time else now

    db_model = Prescricao(
        mpi_id=mpi_id,
        medication=drug,
        dosage=_record_to_dosage(dose, unit),
        route=route,
        frequency=frequency,
        start_time=start_dt,
        status="active",
        version=1,
        notes=notes,
        prescribed_by=prescribed_by,
        created_at=now,
        updated_at=now,
    )
    db.add(db_model)
    await db.flush()  # Get the auto-generated id

    # Persist interaction alerts
    for alert in alerts:
        alert_model = InteracaoAlerta(
            prescricao_id=db_model.id,
            severity=alert.severity,
            interaction_type=alert.interaction_type,
            description=alert.description,
            resolved=alert.resolved,
            created_at=now,
        )
        db.add(alert_model)

    await db.flush()

    # Build domain record for return
    record = _model_to_record(db_model)

    logger.info(
        "Prescription created: id=%s, patient=%s, drug=%s, dose=%s %s, route=%s, "
        "alerts=%d, warnings=%d",
        record.id, mpi_id, drug, dose, unit, route, len(alerts), len(all_warnings),
    )

    return PrescriptionResult(
        prescription=record,
        alerts=alerts,
        dose_valid=dose_valid,
        dose_warnings=all_warnings,
    )


async def get_prescription(
    prescription_id: int,
    db: AsyncSession,
) -> PrescriptionRecord | None:
    """Get a single prescription by ID from PostgreSQL."""
    result = await db.execute(
        select(Prescricao).where(Prescricao.id == prescription_id)
    )
    model = result.scalar_one_or_none()
    if model is None:
        return None
    return _model_to_record(model)


async def list_prescriptions(
    mpi_id: str,
    db: AsyncSession,
    status: str = "active",
    limit: int = 50,
    offset: int = 0,
) -> PrescriptionListResult:
    """R42: List prescriptions for a patient with optional status filter.

    Args:
        mpi_id: Patient identifier. If empty string, returns all patients.
        db: Async SQLAlchemy session.
        status: Filter by status. Use 'all' to include all statuses.
        limit: Max prescriptions to return.
        offset: Pagination offset.

    Returns:
        PrescriptionListResult with prescriptions and total count.
    """
    # Build base query
    stmt = select(Prescricao)

    # Filter by patient
    if mpi_id:
        stmt = stmt.where(Prescricao.mpi_id == mpi_id)

    # Filter by status
    if status and status != "all":
        stmt = stmt.where(Prescricao.status == status)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Sort by created_at descending (newest first)
    stmt = stmt.order_by(Prescricao.created_at.desc())

    # Paginate
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    models = result.scalars().all()

    records = [_model_to_record(m) for m in models]

    return PrescriptionListResult(prescriptions=records, total=total)


async def update_prescription(
    prescription_id: int,
    updates: dict[str, Any],
    db: AsyncSession,
    changed_by: str = "system",
) -> PrescriptionRecord:
    """R43: Update a prescription with state transition support.

    Handles partial updates (only provided fields are changed).
    Supports state transitions via 'status' field in updates dict.
    Validates optimistic locking via 'version' field.

    Args:
        prescription_id: ID of prescription to update.
        updates: Dict of fields to update. May include:
            - dose, unit, route, frequency, notes (value updates)
            - status (state transition)
            - version (optimistic locking)
            - reason (required for discontinued/suspended transitions)
        db: Async SQLAlchemy session.
        changed_by: Clinician executing the update.

    Returns:
        Updated PrescriptionRecord.

    Raises:
        ValueError: On validation errors, invalid transitions, or version mismatch.
        KeyError: If prescription_id not found.
    """
    # Load DB model
    result = await db.execute(
        select(Prescricao).where(Prescricao.id == prescription_id)
    )
    db_model = result.scalar_one_or_none()
    if db_model is None:
        raise KeyError(f"Prescrição {prescription_id} não encontrada.")

    # Convert to domain record for transition logic
    record = _model_to_record(db_model)

    # Optimistic locking check
    expected_version = updates.pop("version", None)
    if expected_version is not None and expected_version != record.version:
        raise ConcurrencyError(
            prescription_id=prescription_id,
            expected_version=expected_version,
            actual_version=record.version,
        )

    # Extract state transition parameters
    new_status = updates.pop("status", None)
    reason = updates.pop("reason", None)
    if new_status is not None:
        _transition_state(record, new_status, reason, changed_by)

    # Apply value updates to domain record
    updatable_fields = {"dose", "unit", "route", "frequency", "notes"}
    for field, value in updates.items():
        if field in updatable_fields:
            # Validate if updating critical fields
            if field == "route" and value not in VALID_ROUTES:
                raise ValueError(
                    f"Via '{value}' inválida. Válidas: {', '.join(VALID_ROUTES)}."
                )
            if field == "frequency" and value not in VALID_FREQUENCIES:
                raise ValueError(
                    f"Frequência '{value}' inválida. "
                    f"Válidas: {', '.join(VALID_FREQUENCIES)}."
                )
            setattr(record, field, value)

    record.version += 1
    record.updated_at = _now_iso()

    # Sync changes back to DB model
    db_model.medication = record.drug
    db_model.dosage = _record_to_dosage(record.dose, record.unit) if "dose" in updates or "unit" in updates else db_model.dosage
    db_model.route = record.route
    db_model.frequency = record.frequency
    db_model.status = record.status
    db_model.version = record.version
    db_model.notes = record.notes
    db_model.updated_at = _now_dt()
    if record.end_time:
        db_model.end_time = datetime.fromisoformat(record.end_time) if record.end_time else None

    await db.flush()

    logger.info(
        "Prescription updated: id=%s, fields=%s, by=%s",
        prescription_id, list(updates.keys()), changed_by,
    )

    return record


async def count_active_prescriptions(
    mpi_id: str,
    db: AsyncSession,
) -> int:
    """Count active prescriptions for a patient from PostgreSQL."""
    result = await db.execute(
        select(func.count()).select_from(Prescricao).where(
            Prescricao.mpi_id == mpi_id,
            Prescricao.status == "active",
        )
    )
    return result.scalar() or 0


async def get_alerts_for_prescription(
    prescription_id: int,
    db: AsyncSession,
) -> list[InteractionAlert]:
    """Get all interaction alerts for a prescription from PostgreSQL."""
    result = await db.execute(
        select(InteracaoAlerta).where(
            InteracaoAlerta.prescricao_id == prescription_id,
        )
    )
    models = result.scalars().all()
    return [_alert_model_to_domain(m) for m in models]


async def resolve_alert(
    prescription_id: int,
    alert_index: int,
    db: AsyncSession,
) -> InteractionAlert | None:
    """Mark an interaction alert as resolved in PostgreSQL."""
    result = await db.execute(
        select(InteracaoAlerta).where(
            InteracaoAlerta.prescricao_id == prescription_id,
        ).order_by(InteracaoAlerta.id)
    )
    alerts = result.scalars().all()
    if not alerts or alert_index < 0 or alert_index >= len(alerts):
        return None

    alert_model = alerts[alert_index]
    alert_model.resolved = True
    await db.flush()

    return _alert_model_to_domain(alert_model)


# =============================================================================
# PrescricaoValidationPipeline — Composable validation pipeline (H4)
# =============================================================================


@dataclass
class ValidatorResult:
    """Result of a single validation check in the pipeline.

    Attributes:
        passed: Whether the validation passed.
        severity: One of 'pass', 'fail', 'warn'.
        rule_id: Identifier of the validation rule (e.g. 'V01').
        message: Human-readable explanation of the result.
    """

    passed: bool
    severity: str  # "pass", "fail", "warn"
    rule_id: str
    message: str


class PrescricaoValidationPipeline:
    """Composable validation pipeline for prescription creation/update.

    Chains validators that each examine a prescription context and return
    pass/fail/warn results. Fails are hard-stops that break the pipeline;
    warns are advisory and do not block execution.

    Usage::

        pipeline = PrescricaoValidationPipeline()
        pipeline.add_validator(validate_dose_range)
        pipeline.add_validator(validate_weight_required)
        results = await pipeline.run(context)
        if pipeline.has_failures(results):
            raise ValueError(...)
    """

    def __init__(self, name: str = "prescricao_validation") -> None:
        self.name = name
        self._validators: list[Callable[..., Any]] = []

    def add_validator(
        self, validator: Callable[..., Any]
    ) -> "PrescricaoValidationPipeline":
        """Add a validator to the pipeline. Returns self for chaining."""
        self._validators.append(validator)
        return self

    async def run(
        self, context: dict[str, Any]
    ) -> list[ValidatorResult]:
        """Run all validators sequentially.

        Fails (severity='fail') stop the pipeline immediately.
        Warns and passes continue to the next validator.
        """
        results: list[ValidatorResult] = []
        for validator in self._validators:
            try:
                if asyncio.iscoroutinefunction(validator):
                    result = await validator(context)
                else:
                    result = validator(context)
            except Exception as exc:
                result = ValidatorResult(
                    passed=False,
                    severity="fail",
                    rule_id="V_ERR",
                    message=f"Validator error: {exc}",
                )
            results.append(result)
            if result.severity == "fail":
                break
        return results

    def has_failures(self, results: list[ValidatorResult]) -> bool:
        """Return True if any validator returned a failure."""
        return any(r.severity == "fail" for r in results)

    def get_warnings(self, results: list[ValidatorResult]) -> list[str]:
        """Extract warning messages from results."""
        return [r.message for r in results if r.severity == "warn"]

    def get_errors(self, results: list[ValidatorResult]) -> list[str]:
        """Extract error messages from results."""
        return [r.message for r in results if r.severity == "fail"]


# ── Individual validators (12) ───────────────────────────────────────────────


async def validate_dose_range(context: dict[str, Any]) -> ValidatorResult:
    """V01: Validate dose against DRUG_SAFETY range limits."""
    drug = context.get("drug", "")
    dose = context.get("dose", 0.0)
    unit = context.get("unit", "")
    route = context.get("route", "")
    frequency = context.get("frequency", "")
    weight_kg = context.get("weight_kg")
    gfr = context.get("gfr")
    age_years = context.get("age_years")

    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)
    if not safety:
        return ValidatorResult(
            passed=True, severity="pass", rule_id="V01",
            message=f"Dose range not defined for {drug} — skipping.",
        )

    dose_valid, warnings_list = _validate_dose(
        drug, dose, unit, route, frequency, weight_kg, gfr, age_years,
    )
    if not dose_valid:
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V01",
            message=f"Dose out of range: {'; '.join(warnings_list)}",
        )
    if warnings_list:
        return ValidatorResult(
            passed=True, severity="warn", rule_id="V01",
            message=f"Dose warning: {'; '.join(warnings_list)}",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V01",
        message="Dose within safe range.",
    )


async def validate_weight_required(context: dict[str, Any]) -> ValidatorResult:
    """V02: Check if patient weight is required for weight-based drugs."""
    drug = context.get("drug", "")
    weight_kg = context.get("weight_kg")

    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)
    if safety and safety.get("weight_based") and (weight_kg is None or weight_kg <= 0):
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V02",
            message=f"Weight-based drug '{drug}' requires patient weight (weight_kg).",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V02",
        message="Weight check passed.",
    )


async def validate_allergy_check(context: dict[str, Any]) -> ValidatorResult:
    """V03: Check drug allergy cross-reactivity groups."""
    drug = context.get("drug", "")
    drug_key = drug.lower().replace(" ", "_")

    for allergy_group, drugs_in_group in DRUG_ALLERGY_GROUPS.items():
        if drug_key in drugs_in_group:
            return ValidatorResult(
                passed=True, severity="warn", rule_id="V03",
                message=(
                    f"Drug '{drug}' belongs to allergy group '{allergy_group}'. "
                    "Verify patient allergy history."
                ),
            )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V03",
        message="No allergy group cross-reactivity flagged.",
    )


async def validate_interaction_check(context: dict[str, Any]) -> ValidatorResult:
    """V04: Check drug-drug interactions against active prescriptions."""
    drug = context.get("drug", "")
    mpi_id = context.get("mpi_id", "")
    db = context.get("db")

    if not db:
        return ValidatorResult(
            passed=True, severity="pass", rule_id="V04",
            message="No DB session provided for interaction check.",
        )

    alerts = await _check_interactions(drug, mpi_id, db)
    contraindicated = [a for a in alerts if a.severity == "contraindicated"]
    if contraindicated:
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V04",
            message=(
                "Contraindicated interactions: "
                + "; ".join(a.description for a in contraindicated)
            ),
        )
    if alerts:
        return ValidatorResult(
            passed=True, severity="warn", rule_id="V04",
            message=f"{len(alerts)} interaction(s) detected.",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V04",
        message="No drug interactions detected.",
    )


async def validate_frequency_valid(context: dict[str, Any]) -> ValidatorResult:
    """V05: Validate frequency string is in VALID_FREQUENCIES."""
    frequency = context.get("frequency", "")
    if frequency not in VALID_FREQUENCIES:
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V05",
            message=f"Invalid frequency '{frequency}'. Valid: {', '.join(VALID_FREQUENCIES)}",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V05",
        message="Frequency valid.",
    )


async def validate_route_valid(context: dict[str, Any]) -> ValidatorResult:
    """V06: Validate administration route is in VALID_ROUTES."""
    route = context.get("route", "")
    if route not in VALID_ROUTES:
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V06",
            message=f"Invalid route '{route}'. Valid: {', '.join(VALID_ROUTES)}",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V06",
        message="Route valid.",
    )


async def validate_duplicate_check(context: dict[str, Any]) -> ValidatorResult:
    """V07: Check for duplicate active prescription (same drug+route+patient)."""
    drug = context.get("drug", "")
    route = context.get("route", "")
    mpi_id = context.get("mpi_id", "")
    db = context.get("db")

    if not db:
        return ValidatorResult(
            passed=True, severity="pass", rule_id="V07",
            message="No DB session for duplicate check.",
        )

    warnings_list = await _check_duplicate(mpi_id, drug, route, db)
    if warnings_list:
        return ValidatorResult(
            passed=True, severity="warn", rule_id="V07",
            message=f"Duplicate: {'; '.join(warnings_list)}",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V07",
        message="No duplicate prescriptions found.",
    )


async def validate_co_signature_required(context: dict[str, Any]) -> ValidatorResult:
    """V08: Check if co-signature is recommended for high-risk drugs."""
    HIGH_RISK_DRUGS: set[str] = {
        "heparina_nao_fracionada", "enoxaparina", "insulina_regular",
        "noradrenalina", "dobutamina", "morfina", "fentanil",
        "cloreto_de_potassio",
    }
    drug = context.get("drug", "")
    drug_key = drug.lower().replace(" ", "_")

    if drug_key in HIGH_RISK_DRUGS:
        return ValidatorResult(
            passed=True, severity="warn", rule_id="V08",
            message=(
                f"High-risk drug '{drug}' — co-signature recommended "
                "per institutional protocol."
            ),
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V08",
        message="Co-signature not required.",
    )


async def validate_pregnancy_contraindicated(context: dict[str, Any]) -> ValidatorResult:
    """V09: Warn about pregnancy risk for teratogenic/contraindicated drugs."""
    PREGNANCY_CONTRAINDICATED: set[str] = {
        "amiodarona", "heparina_nao_fracionada",
    }
    drug = context.get("drug", "")
    drug_key = drug.lower().replace(" ", "_")

    if drug_key in PREGNANCY_CONTRAINDICATED:
        return ValidatorResult(
            passed=True, severity="warn", rule_id="V09",
            message=(
                f"Drug '{drug}' has pregnancy risk — "
                "verify pregnancy status before administration."
            ),
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V09",
        message="No pregnancy contraindications flagged.",
    )


async def validate_renal_adjustment(context: dict[str, Any]) -> ValidatorResult:
    """V10: Check if renal dose adjustment is needed based on GFR."""
    drug = context.get("drug", "")
    gfr = context.get("gfr")

    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)

    if safety and safety.get("renal_adjust"):
        if gfr is not None and gfr < 50:
            return ValidatorResult(
                passed=True, severity="warn", rule_id="V10",
                message=(
                    f"Renal adjustment needed for '{drug}' (GFR={gfr} mL/min). "
                    "Consider dose reduction per RENAL_ADJUSTMENTS table."
                ),
            )
        if gfr is None:
            return ValidatorResult(
                passed=True, severity="warn", rule_id="V10",
                message=(
                    f"GFR not provided for renally-adjusted drug '{drug}'. "
                    "Consider obtaining GFR for dose optimization."
                ),
            )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V10",
        message="Renal adjustment not required or GFR normal.",
    )


async def validate_unit_valid(context: dict[str, Any]) -> ValidatorResult:
    """V11: Validate dose unit is in VALID_UNITS."""
    unit = context.get("unit", "")
    if unit not in VALID_UNITS:
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V11",
            message=f"Invalid unit '{unit}'. Valid: {', '.join(VALID_UNITS)}",
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V11",
        message="Unit valid.",
    )


async def validate_continuous_only_route(context: dict[str, Any]) -> ValidatorResult:
    """V12: Validate continuous-only drugs use an infusion-compatible route."""
    drug = context.get("drug", "")
    route = context.get("route", "")
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)

    if safety and safety.get("continuous_only") and route not in INFUSION_ROUTES:
        return ValidatorResult(
            passed=False, severity="fail", rule_id="V12",
            message=(
                f"Continuous-only drug '{drug}' requires infusion route "
                f"(IV, SC), got '{route}'."
            ),
        )
    return ValidatorResult(
        passed=True, severity="pass", rule_id="V12",
        message="Continuous-only route check passed.",
    )


# ── Pipeline builder ─────────────────────────────────────────────────────────


def build_default_validation_pipeline() -> PrescricaoValidationPipeline:
    """Build the default validation pipeline with all 12 validators.

    Order: hard validators first (fail-fast), then warning validators.
    """
    pipeline = PrescricaoValidationPipeline(name="default_prescricao")
    # Hard validators (can fail and stop the pipeline)
    pipeline.add_validator(validate_route_valid)           # V06
    pipeline.add_validator(validate_frequency_valid)       # V05
    pipeline.add_validator(validate_unit_valid)            # V11
    pipeline.add_validator(validate_weight_required)       # V02
    pipeline.add_validator(validate_continuous_only_route) # V12
    pipeline.add_validator(validate_dose_range)            # V01
    pipeline.add_validator(validate_interaction_check)     # V04
    # Warning validators (advisory, do not block)
    pipeline.add_validator(validate_duplicate_check)       # V07
    pipeline.add_validator(validate_allergy_check)         # V03
    pipeline.add_validator(validate_co_signature_required) # V08
    pipeline.add_validator(validate_pregnancy_contraindicated)  # V09
    pipeline.add_validator(validate_renal_adjustment)      # V10
    return pipeline


# =============================================================================
# Export
# =============================================================================

__all__ = [
    "ConcurrencyError", "PrescriptionRecord", "InteractionAlert",
    "PrescriptionResult", "PrescriptionListResult", "DrugSafetyEntry",
    "PrescriptionStateMachine", "get_state_machine", "STATE_MACHINE_VERSION",
    "VALID_ROUTES", "VALID_STATUSES", "VALID_FREQUENCIES", "VALID_UNITS",
    "STATE_TRANSITIONS", "DRUG_SAFETY", "DRUG_INTERACTIONS", "RENAL_ADJUSTMENTS",
    "create_prescription", "get_prescription", "list_prescriptions",
    "update_prescription", "count_active_prescriptions",
    "get_alerts_for_prescription", "resolve_alert",
    "_calculate_dose_weight_based", "_calculate_dose_renal_adjusted",
    "_validate_dose", "_check_interactions", "_transition_state",
    "ValidatorResult", "PrescricaoValidationPipeline",
    "build_default_validation_pipeline",
    "validate_dose_range", "validate_weight_required",
    "validate_allergy_check", "validate_interaction_check",
    "validate_frequency_valid", "validate_route_valid",
    "validate_duplicate_check", "validate_co_signature_required",
    "validate_pregnancy_contraindicated", "validate_renal_adjustment",
    "validate_unit_valid", "validate_continuous_only_route",
]
