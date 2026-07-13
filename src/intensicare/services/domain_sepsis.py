"""Domain service for Sepsis alerts — hybrid NRT+micro-batch evaluation.

WO-024: Implements 6 sepsis alerts (31 vectors) via the alert compiler.

Architecture:
- Hybrid runner: NRT (Near Real-Time) qSOFA/screening evaluation
  + micro-batch lab confirmation (lactate, PCT, cultures)
- All evaluations via AlertCompiler (definitions loaded, test vectors checked)
- Explicit per-alert evaluation functions for clinical precision
- SSC-2021 screening pathway: qSOFA >=2 + suspected infection -> lactate
  confirmation -> hour-1 bundle (CLINICALLY RATIFIED v3.0.0, RAT-SEPSE-01/02)

Alerts:
  ALERT-SEPSIS-SCREEN-01  — SSC-2021 qSOFA/SIRS screening with infection gate (v3.0.0)
  ALERT-SEPSIS-ORGAN-02    — qSOFA >=2 + elevated/rising lactate (v3.0.0)
  ALERT-SEPSIS-SHOCK-03    — Septic shock: lactate >=4 or refractory MAP<65 (v3.0.0)
  ALERT-SEPSIS-BUNDLE-OVERDUE-04 — Hour-1 bundle compliance timer (v3.0.0)
  ALERT-SEPSIS-PCT-RISING-05     — PCT rising (treatment failure) (v3.0.0)
  ALERT-SEPSIS-PCT-DEESC-06      — PCT-guided de-escalation (v3.0.0)
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any, TypedDict

from intensicare.services.alert_compiler import (
    AlertCompiler,
    AlertDefinition,
    compile_alert_registry,
)
from intensicare.services.news2 import (
    score_heart_rate,
    score_respiratory_rate,
    score_spo2,
    score_systolic_bp,
    score_temperature,
)
from intensicare.services.qsofa import calculate_qsofa

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEPSIS_ALERT_IDS = [
    "ALERT-SEPSIS-SCREEN-01",
    "ALERT-SEPSIS-ORGAN-02",
    "ALERT-SEPSIS-SHOCK-03",
    "ALERT-SEPSIS-BUNDLE-OVERDUE-04",
    "ALERT-SEPSIS-PCT-RISING-05",
    "ALERT-SEPSIS-PCT-DEESC-06",
]

# ---------------------------------------------------------------------------
# SSC-2021 RATIFIED screening constants (RAT-SEPSE-01/02 — CLINICALLY RATIFIED)
# ---------------------------------------------------------------------------
# SSC-2021 screening pathway: qSOFA >= 2 + suspected infection → lactate
# confirmation → hour-1 bundle. All sepsis alert definitions are v3.0.0.
SEPSIS_DEFINITION_VERSION: str = "3.0.0"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class SepsisClinicalInputs(TypedDict, total=False):
    """All 32 clinical input fields used by sepsis alert evaluation.

    Fields are typed according to their clinical semantics.
    total=False means all fields are optional — partial data is accepted.
    """

    # Vital signs
    temperatura: float
    frequencia_cardiaca: float
    frequencia_respiratoria: float
    pressao_arterial_sistolica: float
    pressao_arterial_media: float
    saturacao_o2: float
    nivel_consciencia: str
    glasgow: float

    # Lab values
    leucocitos: float
    bastonetes: float
    paco2_arterial: float
    lactato_arterial: float
    lactato_arterial_anterior: float
    lactate_delta_hours: float
    procalcitonina: float
    procalcitonina_anterior: float
    pico_pct: float

    # Infection / treatment flags
    cultura_positiva: bool
    atb_iniciado_ultimas_24h: bool
    suspeita_infeccao_documentada: bool
    atb_ativa_horas: float

    # qSOFA
    qsofa: float

    # Shock / hemodynamic
    dose_vasopressor: float
    fluid_bolus_given: bool

    # Bundle compliance
    protocol_active: bool
    item_checked: bool
    item_pacote: str
    minutes_since_accept: float

    # PCT de-escalation
    patient_unstable: bool

    # Pain scales
    escala_dor_numerica: float
    escala_dor_comportamental: float

    # COPD flag
    dpoc_diagnosticado: bool


@dataclass
class SepsisAlertResult:
    """Result of evaluating a single sepsis alert."""

    alert_id: str
    alert_name: str
    severity: str
    fired: bool
    inputs_used: dict[str, Any] = field(default_factory=dict)
    missing_inputs: list[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class SepsisEvaluationResult:
    """Result of evaluating all sepsis alerts for a patient."""

    patient_id: str
    alerts: list[SepsisAlertResult]
    n_fired: int
    n_total: int
    mode: str  # "nrt", "micro-batch", "hybrid"
    evaluation_time: str = ""
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helper functions — used across alert evaluations
# ---------------------------------------------------------------------------


def _num(v: Any) -> float | None:
    """Safely convert a value to float."""
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _bool(v: Any) -> bool:
    """Safely convert a value to bool."""
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v > 0
    if isinstance(v, str):
        return v.lower() in ("true", "1", "yes", "sim")
    return bool(v)


def _infection_present(inputs: SepsisClinicalInputs) -> bool:
    """Derive infection_present from infection evidence flags."""
    return (
        _bool(inputs.get("cultura_positiva"))
        or _bool(inputs.get("atb_iniciado_ultimas_24h"))
        or _bool(inputs.get("suspeita_infeccao_documentada"))
    )


def _compute_sirs_count(inputs: SepsisClinicalInputs) -> int:
    """Compute SIRS count (0-4) from clinical inputs.

    Criteria:
    1. Temperature > 38.0 °C or < 36.0 °C
    2. Heart rate > 90 bpm
    3. Respiratory rate > 20 rpm (or PaCO2 < 32 mmHg as alternative)
    4. WBC > 12 x10^3/uL or < 4 x10^3/uL (or bands > 10% as alternative)
    """
    count = 0
    # Criterion 1: Temperature
    t = _num(inputs.get("temperatura"))
    if t is not None and (t > 38.0 or t < 36.0):
        count += 1

    # Criterion 2: Heart rate
    hr = _num(inputs.get("frequencia_cardiaca"))
    if hr is not None and hr > 90:
        count += 1

    # Criterion 3: Respiratory rate or PaCO2
    rr = _num(inputs.get("frequencia_respiratoria"))
    if rr is not None and rr > 20:
        count += 1
    else:
        paco2 = _num(inputs.get("paco2_arterial"))
        if paco2 is not None and paco2 < 32:
            count += 1

    # Criterion 4: WBC or bands
    leuc = _num(inputs.get("leucocitos"))
    if leuc is not None and (leuc > 12 or leuc < 4):
        count += 1
    else:
        bast = _num(inputs.get("bastonetes"))
        if bast is not None and bast > 10:
            count += 1

    return count


def _compute_qsofa_points(inputs: SepsisClinicalInputs) -> int:
    """Compute qSOFA points (0-3) from clinical inputs.

    Delegates to the canonical ``calculate_qsofa()`` engine in qsofa.py.
    Portuguese field names are mapped to the English names the canonical
    engine expects via the adapter below.

    Note: if "qsofa" is directly provided as a pre-computed score, use it.
    """
    # If qsofa score is explicitly provided, use it
    qs = _num(inputs.get("qsofa"))
    if qs is not None:
        return int(qs)

    # Map Portuguese field names → canonical English field names
    rr = _num(inputs.get("frequencia_respiratoria"))
    sbp = _num(inputs.get("pressao_arterial_sistolica"))
    gcs = _num(inputs.get("glasgow"))
    result = calculate_qsofa(
        respiratory_rate=int(rr) if rr is not None else None,
        systolic_bp=int(sbp) if sbp is not None else None,
        gcs=int(gcs) if gcs is not None else None,
    )
    return result.total_score


# ---------------------------------------------------------------------------
# Per-alert evaluation functions
# ---------------------------------------------------------------------------


def _eval_screen_01(inputs: SepsisClinicalInputs) -> tuple[bool, str]:
    """ALERT-SEPSIS-SCREEN-01: SSC-2021 qSOFA/SIRS screening with infection gate.

    SSC-2021 RATIFIED (RAT-SEPSE-01/02): infection_present AND
    (qsofa >= 2 OR sirs_count >= 2) -> positive screen triggers
    lactate measurement -> hour-1 bundle.
    """
    infection = _infection_present(inputs)
    if not infection:
        return False, "No infection evidence (cultura/ATB/suspeita)"

    qsofa = _compute_qsofa_points(inputs)
    sirs = _compute_sirs_count(inputs)

    if qsofa >= 2:
        return True, f"qSOFA={qsofa} >= 2 with infection evidence"
    if sirs >= 2:
        return True, f"SIRS={sirs} >= 2 with infection evidence"

    return False, f"qSOFA={qsofa} < 2 and SIRS={sirs} < 2"


def _eval_organ_02(inputs: SepsisClinicalInputs) -> tuple[bool, str]:
    """ALERT-SEPSIS-ORGAN-02 (v3.0.0): qSOFA >=2 + elevated/rising lactate.

    Logic: qsofa >= 2 AND (lactato_arterial > 2 OR delta_lactato > 0.5/h over 6h)

    Delta lactate: per-hour rate over the lookback window (default 6h per PT6H).
    Use ``lactate_delta_hours`` input to specify actual interval between measurements.
    """
    qsofa = _compute_qsofa_points(inputs)
    if qsofa < 2:
        return False, f"qSOFA={qsofa} < 2 (gate not met)"

    lactate = _num(inputs.get("lactato_arterial"))
    if lactate is not None and lactate > 2.0:
        return True, f"qSOFA={qsofa} >= 2, lactate={lactate} > 2 mmol/L"

    # Delta lactate trend: per-hour rate > 0.5 mmol/L/h
    lactate_prev = _num(inputs.get("lactato_arterial_anterior"))
    if lactate is not None and lactate_prev is not None:
        delta_raw = lactate - lactate_prev
        # Default to 6h window (PT6H), override via lactate_delta_hours
        delta_hours = _num(inputs.get("lactate_delta_hours"))
        if delta_hours is None or delta_hours <= 0:
            delta_hours = 6.0
        delta_per_hour = delta_raw / delta_hours
        if delta_per_hour > 0.5:
            return True, (
                f"qSOFA={qsofa} >= 2, delta_lactato={delta_raw:.2f} mmol/L "
                f"over {delta_hours:.1f}h ({delta_per_hour:.2f}/h) > 0.5/h"
            )

    return False, (f"qSOFA={qsofa} >= 2, lactate={lactate}, neither lactate>2 nor delta>0.5/h met")


def _eval_shock_03(inputs: SepsisClinicalInputs) -> tuple[bool, str]:
    """ALERT-SEPSIS-SHOCK-03 (v3.0.0): Septic shock — lactate >=4 or refractory MAP<65.

    Logic: lactato_arterial >= 4
           OR (MAP < 65 AND (fluid_bolus OR dose_vasopressor > 0))
    """
    lactate = _num(inputs.get("lactato_arterial"))
    if lactate is not None and lactate >= 4.0:
        return True, f"Lactate={lactate} >= 4 mmol/L (septic shock marker)"

    map_val = _num(inputs.get("pressao_arterial_media"))
    vasopressor = _num(inputs.get("dose_vasopressor"))
    fluid_bolus = _bool(inputs.get("fluid_bolus_given"))

    if map_val is not None and map_val < 65:
        if (vasopressor is not None and vasopressor > 0) or fluid_bolus:
            return True, (
                f"MAP={map_val} < 65 mmHg with "
                f"{'vasopressor' if vasopressor and vasopressor > 0 else 'fluid bolus'}"
            )
        return False, f"MAP={map_val} < 65 but no vasopressor/fluid bolus"

    return False, (f"Lactate={lactate} < 4 and MAP={map_val} >= 65 or no refractory state")


def _eval_bundle_overdue_04(inputs: SepsisClinicalInputs) -> tuple[bool, str]:
    """ALERT-SEPSIS-BUNDLE-OVERDUE-04 (v3.0.0): Hour-1 bundle compliance timer.

    Logic: protocol_active AND NOT item_checked AND now > due_at
    where item.due_at = accept_time + 60min (primeira_hora) or + 180min (reavaliacao)
    """
    active = _bool(inputs.get("protocol_active"))
    if not active:
        return False, "Protocol not active"

    checked = _bool(inputs.get("item_checked"))
    if checked:
        return False, "Item already checked"

    pacote = inputs.get("item_pacote", "primeira_hora")
    if isinstance(pacote, str):
        pacote = pacote.strip().lower()

    minutes_since_accept = _num(inputs.get("minutes_since_accept"))
    if minutes_since_accept is None:
        # Try alternative: protocol_accept_time + now computation
        return False, "No minutes_since_accept provided"

    if pacote in ("primeira_hora", "1h", "hora-1"):
        due_minutes = 60
        pkg_label = "primeira_hora (60 min)"
    elif pacote in ("reavaliacao", "reavaliação", "3h", "reassessment"):
        due_minutes = 180
        pkg_label = "reavaliacao (180 min)"
    else:
        due_minutes = 60
        pkg_label = f"{pacote} (default 60 min)"

    if minutes_since_accept > due_minutes:
        return True, (
            f"Item {pkg_label} unchecked, "
            f"{minutes_since_accept} min elapsed > {due_minutes} min due"
        )

    return False, (
        f"Item {pkg_label} not yet overdue: {minutes_since_accept} min <= {due_minutes} min"
    )


def _eval_pct_rising_05(inputs: SepsisClinicalInputs) -> tuple[bool, str]:
    """ALERT-SEPSIS-PCT-RISING-05 (v3.0.0): PCT rising — treatment failure.

    Logic: procalcitonina > procalcitonina_anterior
           AND delta_pct > 0.25 ng/mL over PT24H
           AND atb_ativa_horas >= 48
    """
    pct = _num(inputs.get("procalcitonina"))
    pct_prev = _num(inputs.get("procalcitonina_anterior"))
    atb_hours = _num(inputs.get("atb_ativa_horas"))

    if atb_hours is None or atb_hours < 48:
        return False, f"ATB active only {atb_hours}h (< 48h) — too early"

    if pct is None or pct_prev is None:
        return False, "Missing PCT values"

    if pct <= pct_prev:
        return False, f"PCT {pct} <= previous {pct_prev} (not rising)"

    delta = pct - pct_prev
    if delta > 0.25:
        return True, (
            f"PCT rising: {pct_prev} → {pct} (delta={delta:.2f} > 0.25 ng/mL), ATB={atb_hours}h"
        )

    return False, (f"PCT rising but delta={delta:.2f} <= 0.25 ng/mL")


def _eval_pct_deesc_06(inputs: SepsisClinicalInputs) -> tuple[bool, str]:
    """ALERT-SEPSIS-PCT-DEESC-06 (v3.0.0): PCT-guided de-escalation.

    Logic: (PCT < 0.25 OR >80% drop from peak) AND ATB >= 48h AND NOT patient_unstable
    """
    unstable = _bool(inputs.get("patient_unstable"))
    if unstable:
        return False, "Patient unstable — stability gate suppresses de-escalation"

    atb_hours = _num(inputs.get("atb_ativa_horas"))
    if atb_hours is None or atb_hours < 48:
        return False, f"ATB only {atb_hours}h (< 48h)"

    pct = _num(inputs.get("procalcitonina"))
    if pct is None:
        return False, "Missing PCT value"

    # Branch A: PCT < 0.25 ng/mL
    if pct < 0.25:
        return True, f"PCT={pct} < 0.25 ng/mL, ATB={atb_hours}h, patient stable"

    # Branch B: >80% drop from peak
    peak = _num(inputs.get("pico_pct"))
    if peak is not None and peak > 0 and pct < peak:
        drop_ratio = (peak - pct) / peak
        if drop_ratio > 0.80:
            return True, (
                f"PCT dropped {drop_ratio:.0%} from peak {peak} → {pct} "
                f"(>80%), ATB={atb_hours}h, stable"
            )

    return False, (f"PCT={pct} not <0.25 and no >80% drop from peak, or ATB too early")


# Map alert_id -> evaluation function
_ALERT_EVALUATORS = {
    "ALERT-SEPSIS-SCREEN-01": _eval_screen_01,
    "ALERT-SEPSIS-ORGAN-02": _eval_organ_02,
    "ALERT-SEPSIS-SHOCK-03": _eval_shock_03,
    "ALERT-SEPSIS-BUNDLE-OVERDUE-04": _eval_bundle_overdue_04,
    "ALERT-SEPSIS-PCT-RISING-05": _eval_pct_rising_05,
    "ALERT-SEPSIS-PCT-DEESC-06": _eval_pct_deesc_06,
}


# ---------------------------------------------------------------------------
# Domain service
# ---------------------------------------------------------------------------


class SepsisDomainService:
    """Hybrid domain service for sepsis alert evaluation.

    Modes:
    - NRT (Near Real-Time): qSOFA evaluation on every vital-sign update
    - micro-batch: Lab confirmation (lactate, PCT, cultures) on scheduled polls
    - hybrid: NRT screening fires → triggers micro-batch lab confirmation

    Usage::

        service = SepsisDomainService()
        result = service.evaluate("P-001", patient_data, mode="hybrid")
        for alert_result in result.alerts:
            if alert_result.fired:
                print(f"ALERT: {alert_result.alert_id} severity={alert_result.severity}")
    """

    def __init__(self, repo_root: Path | None = None):
        if repo_root is None:
            repo_root = self._find_repo_root()
        self._repo_root = repo_root
        self._compiler: AlertCompiler | None = None
        self._definitions: dict[str, AlertDefinition] = {}

    @staticmethod
    def _find_repo_root() -> Path:
        return Path(__file__).resolve().parents[3]

    def _ensure_loaded(self) -> None:
        """Lazy-load alert definitions from catalog YAMLs."""
        if self._definitions:
            return
        definitions, compiler = compile_alert_registry(self._repo_root)
        self._compiler = compiler
        self._definitions = definitions

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        patient_id: str,
        inputs: SepsisClinicalInputs,
        *,
        mode: str = "hybrid",
        alert_ids: list[str] | None = None,
    ) -> SepsisEvaluationResult:
        """Evaluate all (or specified) sepsis alerts for a patient.

        Args:
            patient_id: Patient MPI identifier.
            inputs: Dict of clinical data (vitals, labs, flags).
            mode: Evaluation mode — "nrt", "micro-batch", or "hybrid".
            alert_ids: Specific alert IDs to evaluate (default: all 6).

        Returns:
            SepsisEvaluationResult with per-alert results.
        """
        self._ensure_loaded()

        target_ids = alert_ids or SEPSIS_ALERT_IDS
        results: list[SepsisAlertResult] = []
        errors: list[str] = []

        # Filter by mode
        if mode == "nrt":
            nrt_ids = {
                aid
                for aid in target_ids
                if aid in ("ALERT-SEPSIS-SCREEN-01", "ALERT-SEPSIS-SHOCK-03")
            }
            target_ids = [aid for aid in target_ids if aid in nrt_ids]
        elif mode == "micro-batch":
            mb_ids = {
                aid
                for aid in target_ids
                if aid not in ("ALERT-SEPSIS-SCREEN-01", "ALERT-SEPSIS-SHOCK-03")
            }
            target_ids = [aid for aid in target_ids if aid in mb_ids]

        for alert_id in target_ids:
            try:
                result = self._evaluate_single(alert_id, inputs)
                results.append(result)
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                errors.append(f"{alert_id}: {exc}")
                results.append(
                    SepsisAlertResult(
                        alert_id=alert_id,
                        alert_name=alert_id,
                        severity="unknown",
                        fired=False,
                        reason=f"Error: {exc}",
                    )
                )

        n_fired = sum(1 for r in results if r.fired)

        return SepsisEvaluationResult(
            patient_id=patient_id,
            alerts=results,
            n_fired=n_fired,
            n_total=len(results),
            mode=mode,
            evaluation_time=datetime.now(timezone.utc).isoformat(),
            errors=errors,
        )

    def evaluate_screening_only(
        self,
        patient_id: str,
        inputs: SepsisClinicalInputs,
    ) -> SepsisAlertResult:
        """NRT screening evaluation — only SCREEN-01."""
        return self._evaluate_single("ALERT-SEPSIS-SCREEN-01", inputs)

    def evaluate_organ_only(
        self,
        patient_id: str,
        inputs: SepsisClinicalInputs,
    ) -> SepsisAlertResult:
        """Organ dysfunction evaluation — only ORGAN-02."""
        return self._evaluate_single("ALERT-SEPSIS-ORGAN-02", inputs)

    def evaluate_shock_only(
        self,
        patient_id: str,
        inputs: SepsisClinicalInputs,
    ) -> SepsisAlertResult:
        """Shock evaluation — only SHOCK-03."""
        return self._evaluate_single("ALERT-SEPSIS-SHOCK-03", inputs)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _evaluate_single(
        self,
        alert_id: str,
        inputs: SepsisClinicalInputs,
    ) -> SepsisAlertResult:
        """Evaluate a single alert definition against provided inputs.

        Uses the explicit per-alert evaluation function if available,
        falling back to the compiler's test-vector-based evaluation.
        """
        self._ensure_loaded()

        ad = self._definitions.get(alert_id)
        if ad is None:
            return SepsisAlertResult(
                alert_id=alert_id,
                alert_name=alert_id,
                severity="unknown",
                fired=False,
                reason=f"Alert definition not found: {alert_id}",
            )

        # Use explicit evaluator if available
        evaluator = _ALERT_EVALUATORS.get(alert_id)
        if evaluator is not None:
            fired, reason = evaluator(inputs)
            declared_names = {i.name for i in ad.inputs}
            available = {k: v for k, v in inputs.items() if k in declared_names}
            missing = sorted(declared_names - set(inputs.keys()))
            return SepsisAlertResult(
                alert_id=alert_id,
                alert_name=ad.name,
                severity=ad.severity,
                fired=fired,
                inputs_used=available,
                missing_inputs=missing,
                reason=reason,
            )

        # Fallback to compiler evaluation
        assert self._compiler is not None  # ensured by _ensure_loaded() above
        fired = self._compiler.evaluate_alert_definition(alert_id, inputs)  # type: ignore[arg-type]
        reason = f"Fired: {ad.name}" if fired else "Not fired. Criteria not met."
        return SepsisAlertResult(
            alert_id=alert_id,
            alert_name=ad.name,
            severity=ad.severity,
            fired=fired,
            reason=reason,
        )


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


def evaluate_sepsis(
    patient_id: str,
    inputs: SepsisClinicalInputs,
    *,
    mode: str = "hybrid",
) -> SepsisEvaluationResult:
    """Convenience: evaluate all sepsis alerts for a patient."""
    service = SepsisDomainService()
    return service.evaluate(patient_id, inputs, mode=mode)


def evaluate_sepsis_nrt(
    patient_id: str,
    qsofa_score: int,
    rr: int | None = None,
    sbp: int | None = None,
    gcs: int | None = None,
    **extra_inputs: Any,
) -> SepsisAlertResult:
    """NRT qSOFA evaluation — screening + shock only."""
    inputs: dict[str, Any] = {
        "qsofa": qsofa_score,
        **extra_inputs,
    }
    if rr is not None:
        inputs["frequencia_respiratoria"] = rr
    if sbp is not None:
        inputs["pressao_arterial_sistolica"] = sbp
    if gcs is not None:
        inputs["glasgow"] = gcs

    service = SepsisDomainService()
    result = service.evaluate(patient_id, inputs, mode="nrt")  # type: ignore[arg-type]
    for severity in ("critical", "urgent", "watch", "normal"):
        for ar in result.alerts:
            if ar.fired and ar.severity == severity:
                return ar
    for ar in result.alerts:
        if ar.alert_id == "ALERT-SEPSIS-SCREEN-01":
            return ar
    return (
        result.alerts[0]
        if result.alerts
        else SepsisAlertResult(
            alert_id="ALERT-SEPSIS-SCREEN-01",
            alert_name="Triagem de sepse",
            severity="urgent",
            fired=False,
            reason="No alerts evaluated",
        )
    )


def evaluate_sepsis_micro_batch(
    patient_id: str,
    inputs: SepsisClinicalInputs,
) -> SepsisEvaluationResult:
    """Micro-batch lab confirmation — organ, bundle, PCT alerts."""
    service = SepsisDomainService()
    return service.evaluate(patient_id, inputs, mode="micro-batch")


# ══════════════════════════════════════════════════════════════
# WAVE 3A: Clinical Worsening (PIORA) RATIFY Evaluation
# ══════════════════════════════════════════════════════════════


# ---------------------------------------------------------------------------
# Clinical worsening sub-scoring — individual criterion evaluations
# ---------------------------------------------------------------------------


def _piora_score_respiratoria(fr: float | None) -> tuple[int, str]:
    """criterio_1: Frequência respiratória graded sub-score.

    Delegates to canonical NEWS2 ``score_respiratory_rate``.
    Returns (score, label).
    """
    if fr is None:
        return (0, "sem dados")
    score = score_respiratory_rate(int(fr))
    if score == 3:
        label = "bradipneia grave" if fr <= 8 else "taquipneia grave"
    elif score == 2:
        label = "taquipneia moderada"
    elif score == 1:
        label = "bradipneia leve"
    else:
        label = "normal"
    return (score, label)


def _piora_score_temperatura(t: float | None) -> tuple[int, str]:
    """criterio_2: Temperatura axilar sub-score.

    Aligned to canonical NEWS2 ``score_temperature``.
    """
    if t is None:
        return (0, "sem dados")
    score = score_temperature(t)
    if score == 3:
        label = "hipotermia grave"
    elif score == 2:
        label = "febre alta"
    elif score == 1:
        # Could be hypothermia mild (35.1-36.0) or fever mild (38.1-39.0)
        label = "hipotermia leve" if t <= 36.0 else "febre leve"
    else:
        label = "normal"
    return (score, label)


def _piora_score_pas(pas: float | None) -> tuple[int, str]:
    """criterio_3: Pressão arterial sistólica graded sub-score.

    Delegates to canonical NEWS2 ``score_systolic_bp``.
    """
    if pas is None:
        return (0, "sem dados")
    score = score_systolic_bp(int(pas))
    if score == 3:
        label = "hipotensão grave" if pas <= 90 else "hipertensão grave"
    elif score == 2:
        label = "hipotensão moderada"
    elif score == 1:
        label = "hipotensão leve"
    else:
        label = "normal"
    return (score, label)


def _piora_score_fc(fc: float | None) -> tuple[int, str]:
    """criterio_4: Frequência cardíaca graded sub-score.

    Delegates to canonical NEWS2 ``score_heart_rate``.
    """
    if fc is None:
        return (0, "sem dados")
    score = score_heart_rate(int(fc))
    if score == 3:
        label = "bradicardia grave" if fc <= 40 else "taquicardia grave"
    elif score == 2:
        label = "taquicardia moderada"
    elif score == 1:
        label = "bradicardia leve" if fc <= 50 else "taquicardia leve"
    else:
        label = "normal"
    return (score, label)


def _piora_score_consciencia(nivel: str | None) -> tuple[int, str]:
    """criterio_5: Nível de consciência graded sub-score (AVDI).

    A=Alerta=0, V=Responde a voz=1, D=Responde a dor=2, I=Inconsciente=3.
    """
    if nivel is None:
        return (0, "sem dados")
    nivel_upper = nivel.strip().upper()
    if nivel_upper == "A" or nivel_upper.startswith("ALERT"):
        return (0, "alerta")
    if nivel_upper == "V" or nivel_upper.startswith("VOZ"):
        return (1, "responde a voz")
    if nivel_upper == "D" or nivel_upper.startswith("DOR"):
        return (2, "responde a dor")
    if nivel_upper == "I" or nivel_upper.startswith("INCONSCI"):
        return (3, "inconsciente")
    return (0, f"não classificado: {nivel}")


def _piora_score_dor_nrs(dor: float | None) -> tuple[int, str]:
    """criterio_6: Dor (escala numérica 0-10) graded sub-score.

    RATIFIED per rat-piora-clinica-04 (P0, recommended default B):
    Corrected compound-comparison bug: 7 <= dor <= 10 -> 3+ (severe).
    2-3 -> 1+ (mild), 4-6 -> 2+ (moderate), 7-10 -> 3+ (severe).

    NRS 0-10, Boonstra AM et al., Front Psychol 2016.
    """
    if dor is None:
        return (0, "sem dor / sem dados")
    if dor <= 1:
        return (0, "sem dor")
    if dor <= 3:
        return (1, "dor leve")
    if dor <= 6:
        return (2, "dor moderada")
    # RATIFIED: corrected from legacy bug `7 <= dor > 10`
    if dor <= 10:
        return (3, "dor intensa")
    return (0, "fora do intervalo")


def _piora_score_dor_bps(sinais: float | None) -> tuple[int, str]:
    """criterio_7: Dor (escala comportamental 3-12) graded sub-score.

    RATIFIED per rat-piora-clinica-05 (P0, recommended default B):
    Corrected compound-comparison bug: 10 <= sinais <= 12 -> 3+.
    5-6 -> 1+, 7-9 -> 2+, 10-12 -> 3+.

    Behavioral Pain Scale, Payen JF et al., Crit Care Med 2001.
    """
    if sinais is None:
        return (0, "sem dor / sem dados")
    if sinais <= 4:
        return (0, "sem dor")
    if sinais <= 6:
        return (1, "dor leve")
    if sinais <= 9:
        return (2, "dor moderada")
    # RATIFIED: corrected from legacy bug `10 <= sinais > 12`
    if sinais <= 12:
        return (3, "dor intensa")
    return (0, "fora do intervalo")


def _piora_score_sato2_regular(spo2: float | None) -> tuple[int, str]:
    """criterio_8: SatO2 (paciente regular / não-DPOC) graded sub-score.

    Delegates to canonical NEWS2 ``score_spo2`` (Scale 1, non-hypercapnic).
    """
    if spo2 is None:
        return (0, "sem dados")
    score = score_spo2(int(spo2), hypercapnic=False)
    if score == 3:
        label = "hipoxemia grave"
    elif score == 2:
        label = "hipoxemia moderada"
    elif score == 1:
        label = "hipoxemia leve"
    else:
        label = "normal"
    return (score, label)


def _piora_score_sato2_dpoc(spo2: float | None) -> tuple[int, str]:
    """criterio_9: SatO2 (paciente DPOC/COPD) graded sub-score.

    RATIFIED per rat-piora-clinica-07 (P1, recommended default A):
    NEWS2 Scale 2: target 88-92%, penalize both over and under oxygenation.

    Scale 2: <= 83 = 3, 84-85 = 2, 86-87 = 1, 88-92 = 0,
             93-94 on O2 = 1, 95-96 = 2, >= 97 = 3.
    """
    if spo2 is None:
        return (0, "sem dados")
    if spo2 <= 83:
        return (3, "hipoxemia grave")
    if spo2 <= 85:
        return (2, "hipoxemia moderada")
    if spo2 <= 87:
        return (1, "hipoxemia leve")
    if spo2 <= 92:
        return (0, "alvo (88-92%)")
    if spo2 <= 94:
        return (1, "hiperóxia leve")
    if spo2 <= 96:
        return (2, "hiperóxia moderada")
    return (3, "hiperóxia grave")


# ---------------------------------------------------------------------------
# PIORA aggregate clinical worsening alert
# (rat-piora-clinica-08, RULE-PIORA-CLINICA-010, P0 RATIFY)
# ---------------------------------------------------------------------------


@dataclass
class PioraClinicaResult:
    """Result of clinical worsening evaluation."""

    fired: bool
    severity: str  # "NEUTRO", "AMARELO", "VERMELHO"
    aggregate_score: int
    max_single_score: int
    criteria_scores: dict[str, tuple[int, str]]
    recommendation: str


def evaluate_clinical_worsening(inputs: SepsisClinicalInputs) -> PioraClinicaResult:
    """Evaluate clinical worsening (PIORA) aggregate track-and-trigger.

    RATIFIED per rat-piora-clinica-08 (P0, recommended default B):
    NEWS2/MEWS-style two-tier logic:
    1. ANY single criterion at grade 3 -> VERMELHO (no downgrade)
    2. ANY at grade 2 -> at least AMARELO
    3. Aggregate sum drives graded bands (with sign/magnitude preserved)

    Fixes legacy bugs:
    - Last-writer-wins overwrite (no more)
    - int(criterio[0]) sign-discarding sum (now counts magnitude)
    - Dead 15-21 sum band (now reachable)
    """
    # Evaluate all 9 criteria sub-scores
    criterios: dict[str, tuple[int, str]] = {}

    criterios["c1_fr"] = _piora_score_respiratoria(_num(inputs.get("frequencia_respiratoria")))
    criterios["c2_temp"] = _piora_score_temperatura(_num(inputs.get("temperatura")))
    criterios["c3_pas"] = _piora_score_pas(_num(inputs.get("pressao_arterial_sistolica")))
    criterios["c4_fc"] = _piora_score_fc(_num(inputs.get("frequencia_cardiaca")))
    criterios["c5_cons"] = _piora_score_consciencia(inputs.get("nivel_consciencia"))

    # Pain: use whichever scale has data
    dor_nrs = _num(inputs.get("escala_dor_numerica"))
    dor_bps = _num(inputs.get("escala_dor_comportamental"))
    if dor_bps is not None:
        criterios["c6_dor"] = _piora_score_dor_bps(dor_bps)
    elif dor_nrs is not None:
        criterios["c6_dor"] = _piora_score_dor_nrs(dor_nrs)
    else:
        criterios["c6_dor"] = (0, "sem dados")

    # If BPS already used for pain, use it; otherwise use NRS
    if dor_bps is not None:
        criterios["c7_dor"] = _piora_score_dor_bps(dor_bps)
    elif dor_nrs is not None:
        criterios["c7_dor"] = _piora_score_dor_nrs(dor_nrs)
    else:
        criterios["c7_dor"] = (0, "sem dados")

    # SatO2: DPOC vs regular
    is_dpoc = inputs.get("dpoc_diagnosticado", False)
    spo2 = _num(inputs.get("saturacao_o2"))
    if is_dpoc:
        criterios["c8_sato2"] = _piora_score_sato2_dpoc(spo2)
        criterios["c9_sato2"] = _piora_score_sato2_dpoc(spo2)
    else:
        criterios["c8_sato2"] = _piora_score_sato2_regular(spo2)
        criterios["c9_sato2"] = _piora_score_sato2_regular(spo2)

    # Compute aggregate (sum of absolute scores) and max single score
    scores = [s for s, _ in criterios.values()]
    aggregate = sum(abs(s) for s in scores)
    max_single = max(scores)

    # RATIFIED NEWS2 two-tier logic
    severity = "NEUTRO"
    recommendation = ""

    if max_single >= 3:
        severity = "VERMELHO"
        recommendation = (
            "Alto risco de piora clínica — avaliação médica imediata (NEWS2 ≥ 3 em parâmetro único)"
        )
    elif max_single >= 2 or aggregate >= 5:
        severity = "AMARELO"
        recommendation = "Risco moderado de piora clínica — reavaliar em 1h e notificar plantonista"
    elif aggregate >= 3:
        severity = "AMARELO"
        recommendation = "Risco baixo-moderado — vigilância e reavaliação em 2-4h"
    else:
        severity = "NEUTRO"
        recommendation = "Sem sinais de piora clínica — manter rotina de avaliação"

    return PioraClinicaResult(
        fired=(severity != "NEUTRO"),
        severity=severity,
        aggregate_score=aggregate,
        max_single_score=max_single,
        criteria_scores=criterios,
        recommendation=recommendation,
    )
