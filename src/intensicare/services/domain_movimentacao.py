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
    username: str = "admin",
    password: str = "admin",
    channel: int = 1,
    subtype: int = 0,
) -> str:
    """Build RTSP URL for live bed camera.

    RULE-MOVIMENTACAO-ADT-010 (RATIFIED, UNVERIFIABLE).
    Format: rtsp://{user}:{pass}@{ip}/cam/realmonitor?channel={ch}&subtype={st}

    Args:
        camera_ip: Camera IP address.
        username: RTSP username (default: admin).
        password: RTSP password (default: admin).
        channel: Camera channel (default: 1).
        subtype: Stream subtype (default: 0).

    Returns:
        RTSP URL string.
    """
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
