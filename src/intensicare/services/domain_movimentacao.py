"""Domain service: MOVIMENTACAO-ADT cluster — UNVERIFIABLE RATIFY rules.

RATIFIED 2026-07-04 per RATIFICATION-DECISIONS.md ASK-2:
  Recommended defaults across groups:
    GRP-ADT-B-LOS: A (keep as-is)
    GRP-ADT-B-LOOKUP-KEY: C (keep as-is)
    GRP-ADT-B-MORTALITY-SCORE: B (keep as-is)
    GRP-ADT-B-PAYLOAD-SHAPE: C (keep as-is)
    GRP-ADT-B-SERIALIZER-DELEGATION: C (keep as-is)

Member rules (9 UNVERIFIABLE RATIFY):
  RULE-MOVIMENTACAO-ADT-001 through 003, 005 through 008, 010, 011

All rules confirmed verbatim per drafter recommendations under owner delegation.
Provenance: ahlabs-trilhas @ 8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-001: Length-of-stay (tempo de permanencia)
# Category: physiological-calculation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/movimentacao.py:73-103 @8166c07
# Logic:
#   tempo_permanencia = diferenca_dias(data_entrada.date())
#   where diferenca_dias(entrada) = (timezone.now().date() - entrada).days
# ═════════════════════════════════════════════════════════════════════════════


def diferenca_dias(entrada: datetime) -> int:
    """Calculate whole days between now and a given date.

    Used by RULE-MOVIMENTACAO-ADT-001.
    Truncates to whole-day difference (date-based, not hour-based).

    Args:
        entrada: The admission date.

    Returns:
        Number of whole days elapsed.
    """
    return (datetime.now(timezone.utc).date() - entrada.date()).days


def tempo_permanencia(data_entrada: datetime) -> int:
    """Length of stay in days since admission.

    RULE-MOVIMENTACAO-ADT-001 (RATIFIED, UNVERIFIABLE).

    Args:
        data_entrada: Admission datetime.

    Returns:
        Days elapsed since admission (whole days).
        Raises AttributeError if data_entrada is None (matches legacy behavior).
    """
    return diferenca_dias(data_entrada)


def buscar_dias_internacao(data_entrada: datetime | None) -> int:
    """Safe length-of-stay with None guard.

    RULE-MOVIMENTACAO-ADT-001 variant (RATIFIED).
    Returns 0 if data_entrada is None (unlike tempo_permanencia which raises).

    Args:
        data_entrada: Admission datetime or None.

    Returns:
        Days elapsed or 0 if data_entrada is None.
    """
    if data_entrada is None:
        return 0
    return diferenca_dias(data_entrada)


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-002: Bed/movimentacao micro-indicators payload
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/movimentacao.py @8166c07
# Builds micro-indicator payload with VM (mechanical ventilation),
# noradrenalina, and other clinical signals for a bed/movimentacao.
# ═════════════════════════════════════════════════════════════════════════════

def build_micro_indicators_payload(
    vm: bool = False,
    noradrenalina: bool = False,
    dialise: bool = False,
    sedacao: bool = False,
    droga_vasoativa: bool = False,
    antibiotico: bool = False,
    tempo_internacao: int = 0,
    mortalidade_esperada: float | None = None,
) -> dict[str, object]:
    """Build micro-indicator payload for bed/movimentacao.

    RULE-MOVIMENTACAO-ADT-002 (RATIFIED, UNVERIFIABLE).
    Returns a dict with clinical micro-indicator flags.

    Args:
        vm: Mechanical ventilation in use.
        noradrenalina: Noradrenaline in use.
        dialise: Dialysis in use.
        sedacao: Sedation in use.
        droga_vasoativa: Any vasoactive drug in use.
        antibiotico: Antibiotic in use.
        tempo_internacao: Length of stay in days.
        mortalidade_esperada: Expected mortality score (optional).

    Returns:
        Dict with micro-indicator payload keys.
    """
    payload: dict[str, object] = {
        "vm": vm,
        "noradrenalina": noradrenalina,
        "dialise": dialise,
        "sedacao": sedacao,
        "droga_vasoativa": droga_vasoativa,
        "antibiotico": antibiotico,
        "tempo_internacao": tempo_internacao,
    }
    if mortalidade_esperada is not None:
        payload["mortalidade_esperada"] = mortalidade_esperada
    return payload


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-003: Expected-mortality score
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/movimentacao.py @8166c07
# Surface mortalidade_esperada without recomputation.
# ═════════════════════════════════════════════════════════════════════════════

def surface_expected_mortality(
    mortalidade_esperada: float | None,
    with_label: bool = True,
) -> dict[str, object]:
    """Surface the expected mortality score in the ADT payload.

    RULE-MOVIMENTACAO-ADT-003 (RATIFIED, UNVERIFIABLE).
    Surfaces the pre-computed mortalidade_esperada value without recomputation.
    Includes an optional PT-BR label.

    Args:
        mortalidade_esperada: The expected mortality value (or None).
        with_label: Include a human-readable label.

    Returns:
        Dict with 'value' and optionally 'label'.
    """
    result: dict[str, object] = {"value": mortalidade_esperada}
    if with_label:
        result["label"] = "Mortalidade Esperada (TLP)"
    return result


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-005: Bed micro-indicator lookup key
# Category: physiological-calculation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/movimentacao.py @8166c07
# Lookup key collapses nr_atendimento + bed name into compound key format.
# ═════════════════════════════════════════════════════════════════════════════

def build_bed_lookup_key(nr_atendimento: str, bed_name: str) -> str:
    """Build compound lookup key from attendance number + bed name.

    RULE-MOVIMENTACAO-ADT-005 (RATIFIED, UNVERIFIABLE).
    Format: "{nr_atendimento}:{bed_name}"

    Args:
        nr_atendimento: Attendance/encounter number.
        bed_name: Bed/leito name.

    Returns:
        Compound lookup key string.
    """
    return f"{nr_atendimento}:{bed_name}"


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-006: Bed patient snapshot defaults to empty dict
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/serializers/leito.py @8166c07
# When bed is unassigned (no patient), snapshot defaults to {}.
# ═════════════════════════════════════════════════════════════════════════════

def bed_patient_snapshot(
    patient_data: dict[str, object] | None,
) -> dict[str, object]:
    """Return patient snapshot or empty dict for unassigned beds.

    RULE-MOVIMENTACAO-ADT-006 (RATIFIED, UNVERIFIABLE).

    Args:
        patient_data: Patient data dict or None.

    Returns:
        Patient data or empty dict if None.
    """
    return patient_data if patient_data is not None else {}


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-007: Patient basic name/age computed fields
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/serializers/movimentacao.py @8166c07
# Computes basic patient display fields: nome_completo, idade.
# ═════════════════════════════════════════════════════════════════════════════

def patient_basic_fields(
    nome: str | None = None,
    sobrenome: str | None = None,
    data_nascimento: datetime | None = None,
) -> dict[str, str | int | None]:
    """Compute basic patient name and age display fields.

    RULE-MOVIMENTACAO-ADT-007 (RATIFIED, UNVERIFIABLE).

    Args:
        nome: Patient first name.
        sobrenome: Patient last name.
        data_nascimento: Patient birth date.

    Returns:
        Dict with 'nome_completo' and 'idade' (or None if insufficient data).
    """
    nome_completo: str | None = None
    if nome:
        nome_completo = nome.strip()
        if sobrenome:
            nome_completo = f"{nome_completo} {sobrenome.strip()}"

    idade: int | None = None
    if data_nascimento is not None:
        today = datetime.now(timezone.utc).date()
        idade = (
            today.year
            - data_nascimento.year
            - (
                (today.month, today.day)
                < (data_nascimento.month, data_nascimento.day)
            )
        )

    return {"nome_completo": nome_completo, "idade": idade}


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-008: Precomputed vinculo lookup dict
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/views/leito.py @8166c07
# A precomputed vinculo (patient-bed relationship) lookup dict built but
# never consumed in the current code path. Preserved for downstream consumers.
# ═════════════════════════════════════════════════════════════════════════════

def build_vinculo_lookup(
    movimentacoes: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    """Build a precomputed vinculo lookup dict from movimentacoes.

    RULE-MOVIMENTACAO-ADT-008 (RATIFIED, UNVERIFIABLE).
    Built but may not be consumed by all code paths. Preserved for downstream.

    Args:
        movimentacoes: List of movimentacao dicts with 'leito_id' and 'paciente_id'.

    Returns:
        Dict keyed by leito_id mapping to {leito_id, paciente_id, nr_atendimento}.
    """
    return {
        str(m["leito_id"]): {
            "leito_id": m.get("leito_id"),
            "paciente_id": m.get("paciente_id"),
            "nr_atendimento": m.get("nr_atendimento"),
        }
        for m in movimentacoes
        if m.get("leito_id") is not None
    }


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-010: Live camera RTSP URL construction
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/serializers/leito.py @8166c07
# Constructs RTSP URL for live bed camera stream from camera config.
# ═════════════════════════════════════════════════════════════════════════════

def build_camera_rtsp_url(
    camera_ip: str,
    username: str | None = None,
    password: str | None = None,
    channel: int = 1,
    subtype: int = 0,
) -> str:
    """Build RTSP URL for live bed camera.

    RULE-MOVIMENTACAO-ADT-010 (RATIFIED, UNVERIFIABLE).
    Format: rtsp://{user}:{pass}@{ip}/cam/realmonitor?channel={ch}&subtype={st}

    Credentials resolved from env var RTSP_CREDENTIALS (format
    "user:pass"), falling back to RTSP_USER / RTSP_PASS.
    """
    import os

    if username is None or password is None:
        creds = os.getenv("RTSP_CREDENTIALS", "")
        if ":" in creds:
            username, password = creds.split(":", 1)
        else:
            username = os.getenv("RTSP_USER", "intensicare_cam")
            password = os.getenv("RTSP_PASS", "")
    return (
        f"rtsp://{username}:{password}@{camera_ip}"
        f"/cam/realmonitor?channel={channel}&subtype={subtype}"
    )


# ═════════════════════════════════════════════════════════════════════════════
# RULE-MOVIMENTACAO-ADT-011: Bed 'assistido' flag
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/leito.py @8166c07
# Delegated to a model property: leito.assistido reports whether the bed
# currently has an active care-pathway being attended.
# ═════════════════════════════════════════════════════════════════════════════

def compute_assistido_flag(
    has_active_pathway: bool = False,
    has_attended_flag: bool = False,
) -> bool:
    """Compute the 'assistido' (attended) flag for a bed.

    RULE-MOVIMENTACAO-ADT-011 (RATIFIED, UNVERIFIABLE).
    A bed is 'assistido' if it has an active care pathway being attended.

    Args:
        has_active_pathway: Whether the bed has an active care pathway.
        has_attended_flag: Whether the pathway is currently being attended.

    Returns:
        True if the bed is being assisted/attended.
    """
    return has_active_pathway and has_attended_flag


# ═════════════════════════════════════════════════════════════════════════════
# NOVOS ENDPOINTS: MovementRecord, BedRecord, register_movement, get_bed_grid
# In-memory implementation (no DB — API router connects later)
# ═════════════════════════════════════════════════════════════════════════════

# ── In-memory storage ──────────────────────────────────────────────────────

_movements_store: list[dict[str, Any]] = []
_beds_store: dict[str, dict[str, Any]] = {}
_next_movement_id: int = 1


def _init_default_beds() -> None:
    """Initialize a default bed grid if the store is empty."""
    if not _beds_store:
        default_units = ["UTI-A", "UTI-B", "Enfermaria-1", "Enfermaria-2"]
        for unit in default_units:
            for i in range(1, 6):
                bed_id = f"{unit}-LEITO-{i:02d}"
                _beds_store[bed_id] = {
                    "id": bed_id,
                    "unit": unit,
                    "status": "free",
                    "current_patient_mpi_id": None,
                    "current_patient_name": None,
                    "occupied_since": None,
                    "last_cleaned_at": None,
                    "notes": None,
                }


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class MovementRecord:
    id: int | None = None
    mpi_id: str = ""
    type: str = ""  # admission, transfer, discharge
    from_unit: str | None = None
    to_unit: str | None = None
    from_bed: str | None = None
    to_bed: str | None = None
    timestamp: str = ""
    notes: str | None = None
    registered_by: str | None = None
    created_at: str = ""


@dataclass
class BedRecord:
    id: str = ""
    unit: str = ""
    status: str = "free"  # free, occupied, blocked, cleaning
    current_patient_mpi_id: str | None = None
    current_patient_name: str | None = None
    occupied_since: str | None = None
    last_cleaned_at: str | None = None
    notes: str | None = None


@dataclass
class BedGridResult:
    beds: list[BedRecord] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)


@dataclass
class MovementListResult:
    movements: list[MovementRecord] = field(default_factory=list)
    total: int = 0


# ── Internal helpers ────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bed_from_dict(d: dict[str, Any]) -> BedRecord:
    return BedRecord(
        id=d["id"],
        unit=d["unit"],
        status=d["status"],
        current_patient_mpi_id=d.get("current_patient_mpi_id"),
        current_patient_name=d.get("current_patient_name"),
        occupied_since=d.get("occupied_since"),
        last_cleaned_at=d.get("last_cleaned_at"),
        notes=d.get("notes"),
    )


def _movement_from_dict(d: dict[str, Any]) -> MovementRecord:
    return MovementRecord(
        id=d.get("id"),
        mpi_id=d.get("mpi_id", ""),
        type=d.get("type", ""),
        from_unit=d.get("from_unit"),
        to_unit=d.get("to_unit"),
        from_bed=d.get("from_bed"),
        to_bed=d.get("to_bed"),
        timestamp=d.get("timestamp", ""),
        notes=d.get("notes"),
        registered_by=d.get("registered_by"),
        created_at=d.get("created_at", ""),
    )


# ── Validation ──────────────────────────────────────────────────────────────

def _validate_movement(mpi_id: str, movement_type: str, from_bed: str | None,
                       to_bed: str | None) -> None:
    """Validate movement rules: bed availability, patient state consistency.

    Raises ValueError for invalid types, non-existent beds, occupied beds,
    and patients already admitted elsewhere.
    """
    _init_default_beds()

    valid_types = {"admission", "transfer", "discharge"}
    if movement_type not in valid_types:
        raise ValueError(
            f"Invalid movement type '{movement_type}'. "
            f"Must be one of: {sorted(valid_types)}."
        )

    if not mpi_id or not mpi_id.strip():
        raise ValueError("mpi_id is required.")

    # Admission: target bed must exist and be free
    if movement_type == "admission":
        if not to_bed:
            raise ValueError("to_bed is required for admission.")
        if to_bed not in _beds_store:
            raise ValueError(f"Bed '{to_bed}' not found.")
        bed = _beds_store[to_bed]
        if bed["status"] != "free":
            raise ValueError(
                f"Bed '{to_bed}' is not free (current status: {bed['status']})."
            )
        # Check patient is not already admitted to another bed
        for b in _beds_store.values():
            if b["current_patient_mpi_id"] == mpi_id and b["status"] == "occupied":
                raise ValueError(
                    f"Patient '{mpi_id}' is already admitted to bed '{b['id']}'."
                )

    # Transfer: from_bed must be occupied by this patient, to_bed must be free
    elif movement_type == "transfer":
        if not from_bed:
            raise ValueError("from_bed is required for transfer.")
        if not to_bed:
            raise ValueError("to_bed is required for transfer.")
        if from_bed not in _beds_store:
            raise ValueError(f"Source bed '{from_bed}' not found.")
        if to_bed not in _beds_store:
            raise ValueError(f"Target bed '{to_bed}' not found.")
        source = _beds_store[from_bed]
        if source["status"] != "occupied" or source["current_patient_mpi_id"] != mpi_id:
            raise ValueError(
                f"Patient '{mpi_id}' is not occupying bed '{from_bed}'."
            )
        target = _beds_store[to_bed]
        if target["status"] != "free":
            raise ValueError(
                f"Target bed '{to_bed}' is not free (current status: {target['status']})."
            )

    # Discharge: from_bed must be occupied by this patient
    elif movement_type == "discharge":
        if not from_bed:
            raise ValueError("from_bed is required for discharge.")
        if from_bed not in _beds_store:
            raise ValueError(f"Bed '{from_bed}' not found.")
        source = _beds_store[from_bed]
        if source["status"] != "occupied" or source["current_patient_mpi_id"] != mpi_id:
            raise ValueError(
                f"Patient '{mpi_id}' is not occupying bed '{from_bed}'."
            )


# ── Public API ──────────────────────────────────────────────────────────────

def register_movement(mpi_id: str, movement_type: str, from_unit: str | None = None,
                     to_unit: str | None = None, from_bed: str | None = None,
                     to_bed: str | None = None, timestamp: str = "",
                     notes: str | None = None, registered_by: str = "system") -> MovementRecord:
    """Register a patient movement (admission, transfer, discharge).

    Validates bed availability, handles discharge (frees bed), handles admission
    (occupies bed). Raises ValueError for conflicts (occupied bed, patient
    already admitted, etc.).

    Args:
        mpi_id: Patient MPI identifier.
        movement_type: One of 'admission', 'transfer', 'discharge'.
        from_unit: Unit the patient is moving from.
        to_unit: Unit the patient is moving to.
        from_bed: Bed the patient is moving from.
        to_bed: Bed the patient is moving to.
        timestamp: ISO timestamp of the movement (default: now).
        notes: Optional notes.
        registered_by: Who registered the movement (default: 'system').

    Returns:
        MovementRecord with the registered movement.
    """
    _init_default_beds()
    global _next_movement_id

    _validate_movement(mpi_id, movement_type, from_bed, to_bed)

    ts = timestamp or _now_iso()
    created_at = _now_iso()

    movement_id = _next_movement_id
    _next_movement_id += 1

    # Update bed state based on movement type
    if movement_type == "admission":
        bed = _beds_store[to_bed]  # type: ignore[index]
        bed["status"] = "occupied"
        bed["current_patient_mpi_id"] = mpi_id
        bed["current_patient_name"] = None
        bed["occupied_since"] = ts

    elif movement_type == "transfer":
        source = _beds_store[from_bed]  # type: ignore[index]
        target = _beds_store[to_bed]  # type: ignore[index]
        # Free source
        source["status"] = "free"
        source["current_patient_mpi_id"] = None
        source["current_patient_name"] = None
        source["occupied_since"] = None
        # Occupy target
        target["status"] = "occupied"
        target["current_patient_mpi_id"] = mpi_id
        target["current_patient_name"] = None
        target["occupied_since"] = ts

    elif movement_type == "discharge":
        source = _beds_store[from_bed]  # type: ignore[index]
        source["status"] = "free"
        source["current_patient_mpi_id"] = None
        source["current_patient_name"] = None
        source["occupied_since"] = None

    record_dict: dict[str, Any] = {
        "id": movement_id,
        "mpi_id": mpi_id,
        "type": movement_type,
        "from_unit": from_unit,
        "to_unit": to_unit,
        "from_bed": from_bed,
        "to_bed": to_bed,
        "timestamp": ts,
        "notes": notes,
        "registered_by": registered_by,
        "created_at": created_at,
    }
    _movements_store.append(record_dict)

    return _movement_from_dict(record_dict)


def get_patient_movements(mpi_id: str, movement_type: str | None = None,
                         limit: int = 50, offset: int = 0) -> MovementListResult:
    """Get movement history for a patient with optional type filter.

    Args:
        mpi_id: Patient MPI identifier.
        movement_type: Optional filter by movement type.
        limit: Maximum number of results (default: 50).
        offset: Pagination offset (default: 0).

    Returns:
        MovementListResult with movements list and total count.
    """
    _init_default_beds()

    filtered = [
        m for m in _movements_store
        if m["mpi_id"] == mpi_id
        and (movement_type is None or m["type"] == movement_type)
    ]

    # Sort by timestamp descending (most recent first)
    filtered.sort(key=lambda m: str(m.get("timestamp", "")), reverse=True)

    total = len(filtered)
    page = filtered[offset:offset + limit]

    return MovementListResult(
        movements=[_movement_from_dict(m) for m in page],
        total=total,
    )


def get_bed_grid(unit: str | None = None, status: str | None = None) -> BedGridResult:
    """Get bed grid with summary counts, optional filters.

    Args:
        unit: Optional filter by unit name.
        status: Optional filter by bed status (free, occupied, blocked, cleaning).

    Returns:
        BedGridResult with list of BedRecord and summary dict.
    """
    _init_default_beds()

    beds = list(_beds_store.values())

    if unit is not None:
        beds = [b for b in beds if b["unit"] == unit]
    if status is not None:
        beds = [b for b in beds if b["status"] == status]

    # Compute summary
    summary: dict[str, int] = {"total": 0, "free": 0, "occupied": 0, "blocked": 0, "cleaning": 0}
    for b in beds:
        summary["total"] += 1
        st = str(b.get("status", "free"))
        if st in summary:
            summary[st] += 1

    return BedGridResult(
        beds=[_bed_from_dict(b) for b in beds],
        summary=summary,
    )


def update_bed_status(bed_id: str, status: str, notes: str | None = None) -> BedRecord:
    """Update bed status (free, occupied, blocked, cleaning).

    Raises ValueError if trying to free a bed that has a patient, if the
    bed does not exist, or if the status value is invalid.

    Args:
        bed_id: Bed identifier.
        status: New status (free, occupied, blocked, cleaning).
        notes: Optional notes about the status change.

    Returns:
        BedRecord with updated bed data.
    """
    _init_default_beds()

    valid_statuses = {"free", "occupied", "blocked", "cleaning"}
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {sorted(valid_statuses)}."
        )

    if bed_id not in _beds_store:
        raise ValueError(f"Bed '{bed_id}' not found.")

    bed = _beds_store[bed_id]

    # Prevent freeing a bed that has a patient
    if status == "free" and bed.get("current_patient_mpi_id") is not None:
        raise ValueError(
            f"Cannot free bed '{bed_id}' — it has patient "
            f"'{bed['current_patient_mpi_id']}'. "
            f"Discharge or transfer the patient first."
        )

    bed["status"] = status
    if notes is not None:
        bed["notes"] = notes

    if status == "cleaning":
        bed["last_cleaned_at"] = _now_iso()

    return _bed_from_dict(bed)
