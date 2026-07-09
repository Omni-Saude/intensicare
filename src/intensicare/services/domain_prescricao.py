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
"""

from __future__ import annotations

__version__ = "3.0.0"

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

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
# Backward-compatible wrapper for _check_interactions
# =============================================================================


def _check_interactions(drug: str, mpi_id: str) -> list[InteractionAlert]:
    """R17-R26: Check drug-drug/duplicate interactions (backward-compatible wrapper).

    Maintains the original 2-argument signature expected by existing test suites.
    Internally delegates to the refactored version in drug_interactions.py.
    """
    active_rx_list = list(_prescriptions.values())
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
# In-memory store (to be replaced by DB via API router)
# =============================================================================

_prescriptions: dict[int, PrescriptionRecord] = {}
_alerts: dict[int, list[InteractionAlert]] = {}
_next_id: int = 1


def _generate_id() -> int:
    """Generate next sequential prescription ID."""
    global _next_id
    pid = _next_id
    _next_id += 1
    return pid


def _now_iso() -> str:
    """Return current UTC timestamp as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


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
# Rule R11-R16: Duplicate and conflict detection
# =============================================================================


def _check_duplicate(mpi_id: str, drug: str, route: str) -> list[str]:
    """R11: Check for duplicate active prescription for same drug+route+patient."""
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    for rx in _prescriptions.values():
        if (
            rx.mpi_id == mpi_id
            and rx.drug.lower().replace(" ", "_") == drug_key
            and rx.route == route
            and rx.status == "active"
        ):
            warnings.append(
                f"R11: Paciente {mpi_id} já possui prescrição ativa de {drug} "
                f"via {route} (ID: {rx.id}). Verificar duplicidade."
            )
    return warnings


def _check_same_class_duplicate(mpi_id: str, drug: str) -> list[str]:
    """R12: Check for duplicate therapeutic class."""
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    new_class = DRUG_CLASSES.get(drug_key)
    if not new_class:
        return warnings

    for rx in _prescriptions.values():
        if rx.mpi_id == mpi_id and rx.status == "active":
            rx_key = rx.drug.lower().replace(" ", "_")
            rx_class = DRUG_CLASSES.get(rx_key)
            if rx_class and rx_class == new_class and rx_key != drug_key:
                warnings.append(
                    f"R12: Duplicação de classe terapêutica '{new_class}': "
                    f"{drug} + {rx.drug} já ativos para o paciente {mpi_id}."
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


def _validate_prescription_limits(mpi_id: str) -> list[str]:
    """R15-R16: Prescription safety limits.

    R15: Maximum active prescriptions per patient (15).
    R16: Polypharmacy alert threshold (8 active drugs).
    """
    warnings: list[str] = []
    active_count = count_active_prescriptions(mpi_id)

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
# Public API — Main functions
# =============================================================================


def create_prescription(
    mpi_id: str,
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
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
    5. Create record in in-memory store

    Args:
        mpi_id: Patient identifier (MPI — Master Patient Index).
        drug: Drug name (e.g., 'Meropenem', 'vancomicina').
        dose: Numeric dose value.
        unit: Dose unit (mg, g, mcg, UI, mEq, etc.).
        route: Administration route (IV, PO, SC, etc.).
        frequency: Dosing frequency (8/8h, QID, continuous, etc.).
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
    dup_warnings = _check_duplicate(mpi_id, drug, route)
    dup_warnings += _check_same_class_duplicate(mpi_id, drug)
    dup_warnings += _validate_temporal_constraints(start_time)
    dup_warnings += _validate_prescription_limits(mpi_id)

    # Step 3: Check drug interactions
    alerts = _check_interactions(drug, mpi_id)

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

    # Step 5: Create prescription record
    now = _now_iso()
    record = PrescriptionRecord(
        id=_generate_id(),
        mpi_id=mpi_id,
        drug=drug,
        dose=dose,
        unit=unit,
        route=route,
        frequency=frequency,
        start_time=start_time or now,
        status="active",
        version=1,
        notes=notes,
        prescribed_by=prescribed_by,
        created_at=now,
        updated_at=now,
    )

    # Store in memory (id is guaranteed set by _generate_id above)
    assert record.id is not None
    _prescriptions[record.id] = record
    _alerts[record.id] = alerts

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


def get_prescription(prescription_id: int) -> PrescriptionRecord | None:
    """Get a single prescription by ID from in-memory store."""
    return _prescriptions.get(prescription_id)


def list_prescriptions(
    mpi_id: str,
    status: str = "active",
    limit: int = 50,
    offset: int = 0,
) -> PrescriptionListResult:
    """R42: List prescriptions for a patient with optional status filter.

    Args:
        mpi_id: Patient identifier. If empty string, returns all patients.
        status: Filter by status. Use 'all' to include all statuses.
        limit: Max prescriptions to return.
        offset: Pagination offset.

    Returns:
        PrescriptionListResult with prescriptions and total count.
    """
    # Filter by patient
    if mpi_id:
        candidates = [rx for rx in _prescriptions.values() if rx.mpi_id == mpi_id]
    else:
        candidates = list(_prescriptions.values())

    # Filter by status
    if status and status != "all":
        candidates = [rx for rx in candidates if rx.status == status]

    # Sort by created_at descending (newest first)
    candidates.sort(key=lambda rx: rx.created_at, reverse=True)

    total = len(candidates)

    # Paginate
    paginated = candidates[offset : offset + limit]

    return PrescriptionListResult(prescriptions=paginated, total=total)


def update_prescription(
    prescription_id: int,
    updates: dict[str, Any],
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
        changed_by: Clinician executing the update.

    Returns:
        Updated PrescriptionRecord.

    Raises:
        ValueError: On validation errors, invalid transitions, or version mismatch.
        KeyError: If prescription_id not found.
    """
    record = _prescriptions.get(prescription_id)
    if record is None:
        raise KeyError(f"Prescrição {prescription_id} não encontrada.")

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

    # Apply value updates
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

    logger.info(
        "Prescription updated: id=%s, fields=%s, by=%s",
        prescription_id, list(updates.keys()), changed_by,
    )

    return record


def count_active_prescriptions(mpi_id: str) -> int:
    """Count active prescriptions for a patient."""
    return sum(
        1 for rx in _prescriptions.values()
        if rx.mpi_id == mpi_id and rx.status == "active"
    )


def get_alerts_for_prescription(prescription_id: int) -> list[InteractionAlert]:
    """Get all interaction alerts for a prescription."""
    return _alerts.get(prescription_id, [])


def resolve_alert(
    prescription_id: int,
    alert_index: int,
) -> InteractionAlert | None:
    """Mark an interaction alert as resolved."""
    alerts = _alerts.get(prescription_id, [])
    if not alerts or alert_index < 0 or alert_index >= len(alerts):
        return None
    alerts[alert_index].resolved = True
    return alerts[alert_index]


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
]
