"""Sepsis computed-input provider — pre-computes relative inputs for sepse.yaml v4.

WO-024 follow-up (Sprint 3 sepsis governance): ``domain_sepsis.py`` already
operates on PRE-COMPUTED relative inputs (``sirs_count``, ``qsofa``,
``atb_ativa_horas``, ``delta_pct_24h``, ``minutes_since_accept``, ...) — its
31-vector-validated evaluators never look at absolute timestamps themselves.
This module is the missing bridge: it reads whatever is *actually persisted*
for a patient (``VitalSign``, ``LabResult``, ``StabilityAssessment``,
``PatientPathway``) and reduces it to that same relative-input vocabulary,
so the declarative ``sepse.yaml`` v4 pathway can consume it directly.

Design contract (approved):
- ``now`` is injected by the caller (never ``datetime.now()`` internally) —
  every relative/duration input is computed against this single reference
  instant, making the provider deterministic and testable.
- **Missing input = pending criterion.** If a value cannot be derived from
  data this codebase actually ingests/persists today, the corresponding key
  is OMITTED from the returned dict (never guessed, never defaulted to a
  clinically-meaningful sentinel like 0 or False) — the declarative
  evaluator's own "missing input" handling is the correct, intentional
  behavior. The one deliberate exception is ``sirs_count``/``qsofa_score``:
  ``domain_sepsis._compute_sirs_count``/``_compute_qsofa_points`` are reused
  verbatim (not reimplemented) and, by their own validated design, treat an
  unmeasured *component* as contributing 0 points rather than blocking the
  whole score — that is inherited canonical behavior, not invented here.
- SIRS/qSOFA/PCT arithmetic is never re-derived — it is imported from
  ``domain_sepsis`` (the canonical, 31-vector-validated source) and reused
  as-is.

Known data gaps as of this writing (documented, not papered over):
- No persisted antibiotic-administration-confirmation signal exists
  (``Prescricao`` records orders with a free-text ``medication`` string and
  no therapeutic-class tagging; there is no administration-confirmation
  timestamp joined to a "this is the sepsis empiric antibiotic" concept).
  Therefore ``atb_ativa_horas`` and ``culturas_antes_atb`` are always
  omitted today — deliberately, per the missing-input contract above, not a
  bug in this provider.
- No blood-culture/hemocultura persistence exists anywhere in this
  codebase (no model, no ingestion path) — ``culturas_antes_atb`` is
  therefore always omitted for the same reason.
- No persisted "infection suspected" flag exists (``cultura_positiva`` /
  ``atb_iniciado_ultimas_24h`` / ``suspeita_infeccao_documentada`` — the
  three signals ``domain_sepsis._infection_present`` derives from — have no
  storage today), so ``infeccao_suspeita`` is always omitted.
- No fluid-balance persistence exists (``domain_fluid_balance.py`` operates
  on caller-supplied dataclasses, not an ORM table), so ``fluid_volume`` is
  always omitted.
- ``minutes_since_accept_atb`` / ``minutes_since_accept_culturas`` are both
  derived from the same persisted clock — ``PatientPathway.enrolled_at`` for
  the patient's sepse-pathway enrollment (there is no distinct "bundle
  timer accepted" timestamp separate from enrollment in this schema) — so
  the two values are currently identical. They are kept as two separate
  keys because sepse.yaml v4 gates the ATB bundle item and the cultures
  bundle item independently, and a future, more granular "accept" timestamp
  per bundle item should only require a change inside this function.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.lab_result import LabResult
from intensicare.models.pathway import Pathway, PatientPathway
from intensicare.models.stability import StabilityAssessment
from intensicare.models.vital_sign import VitalSign
from intensicare.services.domain_sepsis import (
    SepsisClinicalInputs,
    _compute_qsofa_points,
    _compute_sirs_count,
)

logger = logging.getLogger(__name__)

__all__ = ["build_sepsis_inputs"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEPSE_PATHWAY_SLUG = "sepse"

# How far back to look for lab results feeding SIRS components (leucocitos,
# bastonetes, paco2), lactate, and the *current* PCT reading.
_RECENT_LABS_WINDOW = timedelta(hours=72)

# How far back to search for a prior PCT reading / PCT peak (procalcitonin
# kinetics are followed over days, not hours, in SSC-2021 de-escalation).
_PCT_HISTORY_WINDOW = timedelta(days=14)

# Target lookback for "the PCT value from ~24h ago" plus tolerance either
# side — a real prior sample rarely lands on exactly T-24h00m.
_PCT_DELTA_TARGET_HOURS = 24.0
_PCT_DELTA_TOLERANCE_HOURS = 6.0

_LEUCOCITOS_ANALYTES = {"leucocitos", "leucograma", "leukocytes", "wbc", "white_blood_cells"}
_BASTONETES_ANALYTES = {"bastonetes", "bands", "neutrofilos_bastonetes"}
_PACO2_ANALYTES = {"paco2", "paco2_arterial", "pco2", "pco2_arterial"}
_LACTATE_ANALYTES = {"lactate", "lactato", "lactato_arterial", "acido_lactico"}
_PCT_ANALYTES = {"procalcitonina", "pct", "procalcitonin"}

# Stability window for "clinically stable for 48h" — see paciente_estavel_48h.
_STABILITY_WINDOW = timedelta(hours=48)


def _normalize_analyte(name: str | None) -> str:
    return (name or "").strip().lower().replace(" ", "_").replace("-", "_")


def _compute_map(systolic: float | None, diastolic: float | None) -> float | None:
    """MAP = DBP + (SBP - DBP) / 3. Same formula used in api/v1/stability.py."""
    if systolic is None or diastolic is None:
        return None
    return diastolic + (systolic - diastolic) / 3.0


# ---------------------------------------------------------------------------
# Persistence reads
# ---------------------------------------------------------------------------


async def _fetch_latest_vital(db: AsyncSession, mpi_id: str) -> VitalSign | None:
    stmt = (
        select(VitalSign)
        .where(VitalSign.mpi_id == mpi_id)
        .order_by(desc(VitalSign.recorded_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _fetch_labs_since(
    db: AsyncSession, mpi_id: str, since: datetime, *, limit: int = 200
) -> list[LabResult]:
    stmt = (
        select(LabResult)
        .where(LabResult.mpi_id == mpi_id)
        .where(LabResult.collected_at >= since)
        .order_by(desc(LabResult.collected_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def _latest_matching(labs: list[LabResult], analyte_names: set[str]) -> LabResult | None:
    """Most recent lab result (labs is already sorted desc) matching any of the names."""
    for lab in labs:
        if _normalize_analyte(lab.analyte) in analyte_names and lab.value_num is not None:
            return lab
    return None


async def _fetch_sepse_pathway_id(db: AsyncSession) -> int | None:
    stmt = select(Pathway.id).where(Pathway.slug == SEPSE_PATHWAY_SLUG)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _fetch_latest_sepse_enrollment(
    db: AsyncSession, mpi_id: str, pathway_id: int
) -> PatientPathway | None:
    """Most recent sepse enrollment for this patient (active preferred, else latest)."""
    stmt = (
        select(PatientPathway)
        .where(PatientPathway.mpi_id == mpi_id, PatientPathway.pathway_id == pathway_id)
        .order_by(desc(PatientPathway.enrolled_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _fetch_stability_assessments(
    db: AsyncSession, mpi_id: str, since: datetime
) -> list[StabilityAssessment]:
    stmt = (
        select(StabilityAssessment)
        .where(StabilityAssessment.mpi_id == mpi_id)
        .where(StabilityAssessment.assessed_at >= since)
        .order_by(desc(StabilityAssessment.assessed_at))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _build_sirs_qsofa_inputs(vital: VitalSign | None, labs: list[LabResult]) -> dict[str, Any]:
    """SIRS + qSOFA — reuse domain_sepsis's canonical, validated math verbatim.

    Builds a SepsisClinicalInputs-shaped dict from whatever is available;
    both compute functions tolerate missing components (they contribute 0
    points rather than blocking the score — inherited behavior, see the
    module docstring), so these two keys are always present.
    """
    clinical: SepsisClinicalInputs = {}
    if vital is not None:
        if vital.temperature is not None:
            clinical["temperatura"] = float(vital.temperature)
        if vital.heart_rate is not None:
            clinical["frequencia_cardiaca"] = float(vital.heart_rate)
        if vital.respiratory_rate is not None:
            clinical["frequencia_respiratoria"] = float(vital.respiratory_rate)
        if vital.systolic_bp is not None:
            clinical["pressao_arterial_sistolica"] = float(vital.systolic_bp)
        if vital.gcs is not None:
            clinical["glasgow"] = float(vital.gcs)

    leuco = _latest_matching(labs, _LEUCOCITOS_ANALYTES)
    if leuco is not None:
        clinical["leucocitos"] = leuco.value_num  # type: ignore[typeddict-item]
    bast = _latest_matching(labs, _BASTONETES_ANALYTES)
    if bast is not None:
        clinical["bastonetes"] = bast.value_num  # type: ignore[typeddict-item]
    paco2 = _latest_matching(labs, _PACO2_ANALYTES)
    if paco2 is not None:
        clinical["paco2_arterial"] = paco2.value_num  # type: ignore[typeddict-item]

    return {
        "sirs_count": _compute_sirs_count(clinical),
        "qsofa_score": _compute_qsofa_points(clinical),
    }


def _build_lab_snapshot_inputs(
    labs: list[LabResult], pct_history: list[LabResult]
) -> dict[str, Any]:
    """Current lactate + PCT values — from LabResult, omitted if never persisted."""
    out: dict[str, Any] = {}
    lactate_lab = _latest_matching(labs, _LACTATE_ANALYTES)
    if lactate_lab is not None:
        out["lactato"] = lactate_lab.value_num

    pct_lab = _latest_matching(pct_history, _PCT_ANALYTES)
    if pct_lab is not None:
        out["pct"] = pct_lab.value_num
    return out


def _build_pam_input(vital: VitalSign | None) -> dict[str, Any]:
    """PAM — prefer the persisted map_value, else derive from SBP/DBP."""
    if vital is None:
        return {}
    pam: float | None = None
    if vital.map_value is not None:
        pam = float(vital.map_value)
    elif vital.systolic_bp is not None and vital.diastolic_bp is not None:
        pam = _compute_map(float(vital.systolic_bp), float(vital.diastolic_bp))
    return {"pam": pam} if pam is not None else {}


def _build_vasopressor_input(vital: VitalSign | None) -> dict[str, Any]:
    """Vasopressor in use — only asserted when the persisted signal is explicit.

    VitalSign.vasopressor_dose_mcg_kg_min/vasopressor_type are nullable
    ("not measured"), unlike e.g. mechanical_ventilation which defaults to
    False ("measured, and it's off"). We only assert True/False when at
    least one of the two fields is explicitly populated; otherwise the key
    is omitted rather than guessing "not on vasopressor".
    """
    if vital is None:
        return {}
    if vital.vasopressor_dose_mcg_kg_min is None and not vital.vasopressor_type:
        return {}
    dose = (
        float(vital.vasopressor_dose_mcg_kg_min)
        if vital.vasopressor_dose_mcg_kg_min is not None
        else 0.0
    )
    return {"vasopressor_ativo": dose > 0 or bool(vital.vasopressor_type)}


async def _build_bundle_timer_inputs(
    db: AsyncSession, mpi_id: str, now: datetime
) -> dict[str, Any]:
    """minutes_since_accept_{atb,culturas} — both derived from the same persisted
    clock (PatientPathway.enrolled_at for the sepse enrollment) — see module
    docstring "Known data gaps" for why they are not yet independently timed.
    """
    sepse_pathway_id = await _fetch_sepse_pathway_id(db)
    if sepse_pathway_id is None:
        return {}
    enrollment = await _fetch_latest_sepse_enrollment(db, mpi_id, sepse_pathway_id)
    if enrollment is None:
        return {}
    elapsed_minutes = (now - enrollment.enrolled_at).total_seconds() / 60.0
    return {
        "minutes_since_accept_atb": elapsed_minutes,
        "minutes_since_accept_culturas": elapsed_minutes,
    }


def _build_pct_kinetics_inputs(pct_history: list[LabResult]) -> dict[str, Any]:
    """delta_pct_24h, pct_queda_pct — PCT trend/peak-drop over the history window."""
    pct_readings = [
        (lab.collected_at, lab.value_num)
        for lab in pct_history
        if _normalize_analyte(lab.analyte) in _PCT_ANALYTES and lab.value_num is not None
    ]  # already sorted desc by collected_at (pct_history query order)
    if not pct_readings:
        return {}

    out: dict[str, Any] = {}
    current_ts, current_val = pct_readings[0]

    # Prior reading closest to "24h before the current PCT sample".
    target_ts = current_ts - timedelta(hours=_PCT_DELTA_TARGET_HOURS)
    prior_candidates = [
        (ts, val)
        for ts, val in pct_readings[1:]
        if abs((ts - target_ts).total_seconds()) / 3600.0 <= _PCT_DELTA_TOLERANCE_HOURS
    ]
    if prior_candidates:
        _, prior_val = min(
            prior_candidates, key=lambda item: abs((item[0] - target_ts).total_seconds())
        )
        out["delta_pct_24h"] = current_val - prior_val

    # Peak PCT over the lookback window (includes the current reading).
    peak_val = max(val for _, val in pct_readings)
    if peak_val > 0:
        out["pct_queda_pct"] = (peak_val - current_val) / peak_val * 100.0
    return out


async def _build_stability_input(db: AsyncSession, mpi_id: str, now: datetime) -> dict[str, Any]:
    """paciente_estavel_48h — from persisted StabilityAssessment history."""
    stability_rows = await _fetch_stability_assessments(db, mpi_id, now - _STABILITY_WINDOW)
    if not stability_rows:
        return {}
    return {
        "paciente_estavel_48h": all(row.severity == "estavel" for row in stability_rows),
    }


async def build_sepsis_inputs(db: AsyncSession, mpi_id: str, now: datetime) -> dict[str, Any]:
    """Build the full set of pre-computed relative inputs sepse.yaml v4 consumes.

    Reads persisted ``VitalSign``, ``LabResult``, ``PatientPathway`` and
    ``StabilityAssessment`` rows for ``mpi_id`` and reduces them to the
    relative-input vocabulary ``domain_sepsis.py``'s evaluators already
    expect. Every duration/delta is computed against ``now`` (injected by
    the caller — never ``datetime.now()``), so this function is
    deterministic and safe to unit-test with a fixed clock.

    Keys are OMITTED (not set to ``None``) whenever the underlying signal is
    not currently persisted anywhere this codebase writes to — see the
    module docstring's "Known data gaps" section. This lets the declarative
    pathway evaluator treat "no data" as "criterion pending", which is the
    correct, intentional behavior, rather than silently inventing a
    clinically-meaningful default. Two keys are never omitted:
    ``sirs_count``/``qsofa_score`` (see ``_build_sirs_qsofa_inputs``).

    Not computed at all (see module docstring "Known data gaps" — no
    persisted source exists anywhere in this codebase today):
    ``fluid_volume``, ``infeccao_suspeita``, ``atb_ativa_horas``,
    ``culturas_antes_atb``.

    Returns:
        Dict with any subset of: ``sirs_count``, ``qsofa_score``,
        ``lactato``, ``pct``, ``pam``, ``vasopressor_ativo``,
        ``minutes_since_accept_atb``, ``minutes_since_accept_culturas``,
        ``delta_pct_24h``, ``pct_queda_pct``, ``paciente_estavel_48h``.
    """
    vital = await _fetch_latest_vital(db, mpi_id)
    labs = await _fetch_labs_since(db, mpi_id, now - _RECENT_LABS_WINDOW)
    pct_history = await _fetch_labs_since(db, mpi_id, now - _PCT_HISTORY_WINDOW)

    inputs: dict[str, Any] = {}
    inputs.update(_build_sirs_qsofa_inputs(vital, labs))
    inputs.update(_build_lab_snapshot_inputs(labs, pct_history))
    inputs.update(_build_pam_input(vital))
    inputs.update(_build_vasopressor_input(vital))
    inputs.update(await _build_bundle_timer_inputs(db, mpi_id, now))
    inputs.update(_build_pct_kinetics_inputs(pct_history))
    inputs.update(await _build_stability_input(db, mpi_id, now))
    return inputs
