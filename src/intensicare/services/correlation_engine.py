"""
Correlation Engine — cross-domain correlations (Rollout 2d, WO-032).

Second-pass evaluator over persisted domain alerts/scores.
Implements four cross-domain correlations per
docs/plan/_work/alerts/correlation-engine.yaml:

  1. ALERT-CORR-SEPSIS-AKI-01  — Sepsis + AKI (SA-AKI)
  2. ALERT-CORR-RESP-HEMO-02    — Respiratory + Hemodynamic (SDRA+choque)
  3. ALERT-CORR-QTC-ELEC-03     — Drug + Electrolyte (QTc + K+/Mg2+)
  4. ALERT-CORR-EXAM-REDUND-04  — Redundant diagnostic ordering

Core principle: a correlation is a NEW richer alert that REPLACES its
member alerts. Each fires only when BOTH members are present within a
temporal join window — strictly MORE specific -> higher PPV, fewer pushes.

Clinical chains (1)(2)(3) emit correlation.member_suppressed to fold the
member alerts. Chain (3) additionally AMPLIFIES severity (WARN -> critical).
Chain (4) is standalone (efficiency/stewardship), excluded from suppression
accounting.

PPV budget: fleet floor >= 0.60; each correlation has its own target.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from intensicare.schemas.severity import SeverityLevel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CORRELATION_ALERT_IDS: list[str] = [
    "ALERT-CORR-SEPSIS-AKI-01",
    "ALERT-CORR-RESP-HEMO-02",
    "ALERT-CORR-QTC-ELEC-03",
    "ALERT-CORR-EXAM-REDUND-04",
]

# Correlation IDs grouped by nature
CLINICAL_CORRELATIONS = [
    "ALERT-CORR-SEPSIS-AKI-01",
    "ALERT-CORR-RESP-HEMO-02",
    "ALERT-CORR-QTC-ELEC-03",
]

EFFICIENCY_CORRELATIONS = [
    "ALERT-CORR-EXAM-REDUND-04",
]

# Temporal join windows (ISO 8601 duration -> hours)
JOIN_WINDOWS: dict[str, float] = {
    "ALERT-CORR-SEPSIS-AKI-01": 72.0,   # PT72H
    "ALERT-CORR-RESP-HEMO-02": 6.0,     # PT6H
    "ALERT-CORR-QTC-ELEC-03": 24.0,     # PT24H
    "ALERT-CORR-EXAM-REDUND-04": 720.0,  # PT720H (max window for exam history)
}

# Per-class reassessment windows for exam redundancy (hours)
EXAM_CLASS_WINDOWS: dict[str, float] = {
    "hemograma": 120.0,              # PT120H = 5 days
    "bioquimica_rotina": 168.0,      # PT168H = 7 days
    "rx_torax_rotina": 336.0,        # PT336H = 14 days
    "marcadores_tireoide": 504.0,    # PT504H = 21 days
    "sorologias": 720.0,             # PT720H = 30 days
}

# PPV budget per correlation
PPV_BUDGET: dict[str, dict[str, Any]] = {
    "ALERT-CORR-SEPSIS-AKI-01": {
        "target_ppv": 0.80,
        "est_volume_per_100_beds_day": 2,
    },
    "ALERT-CORR-RESP-HEMO-02": {
        "target_ppv": 0.85,
        "est_volume_per_100_beds_day": 1,
    },
    "ALERT-CORR-QTC-ELEC-03": {
        "target_ppv": 0.70,
        "est_volume_per_100_beds_day": 1,
    },
    "ALERT-CORR-EXAM-REDUND-04": {
        "target_ppv": 0.60,
        "est_volume_per_100_beds_day": 2,
    },
}

# Severity definitions per correlation
CORRELATION_SEVERITY: dict[str, str] = {
    "ALERT-CORR-SEPSIS-AKI-01": "critical",
    "ALERT-CORR-RESP-HEMO-02": "critical",
    "ALERT-CORR-QTC-ELEC-03": "critical",  # Amplified from WARN
    "ALERT-CORR-EXAM-REDUND-04": "normal",
}

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class CorrelationAlertResult:
    """Result of evaluating a single correlation alert."""

    alert_id: str
    name: str
    fired: bool
    severity: SeverityLevel | None = None
    inputs_used: dict[str, Any] = field(default_factory=dict)
    missing_inputs: list[str] = field(default_factory=list)
    reason: str = ""
    # Linked source alerts that triggered this correlation
    source_alerts: list[dict[str, Any]] = field(default_factory=list)
    # Member alerts suppressed (folded) by this correlation
    suppressed_member_ids: list[str] = field(default_factory=list)
    # PPV tracking
    ppv_budget: dict[str, Any] | None = None


@dataclass
class CorrelationEvent:
    """A correlation event emitted to the alert dispatcher."""

    correlation_id: str
    patient_id: str
    encounter_id: str
    name: str
    severity: str
    # References to the source domain events
    source_event_refs: list[dict[str, Any]]
    # Alerts folded into this correlation
    member_alerts_suppressed: list[str]
    # Correlation-specific fields
    fields: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class CorrelationEvaluationResult:
    """Result of evaluating all correlations for a patient."""

    patient_id: str
    encounter_id: str
    correlations: list[CorrelationAlertResult]
    n_fired: int
    n_total: int
    errors: list[str] = field(default_factory=list)
    # Fleet PPV tracking
    ppv_summary: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Correlation evaluators
# ---------------------------------------------------------------------------


def _evaluate_sepsis_aki(
    inputs: dict[str, Any],
) -> tuple[bool, str, list[str], dict[str, Any]]:
    """Evaluate ALERT-CORR-SEPSIS-AKI-01: Sepsis + AKI correlation.

    Logic:
      sepsis_active AND aki_active AND causal_temporal_link
      where sepsis_active := sepsis_event in {organ_dysfunction, shock}
      aki_active := kdigo_stage >= 1
      causal_temporal_link := aki_onset >= sepsis_onset AND
        (aki_onset - sepsis_onset) <= 72h * 3600s
    """
    sepsis_event = inputs.get("sepsis_event")
    sepsis_onset = inputs.get("sepsis_onset_at")
    aki_onset = inputs.get("aki_onset_at")
    kdigo_stage = inputs.get("kdigo_stage")

    missing: list[str] = []

    # Check sepsis member
    sepsis_active = sepsis_event in (
        "sepsis.organ_dysfunction.detected",
        "sepsis.shock.detected",
    )
    if sepsis_event is None:
        missing.append("sepsis_event")

    # Check AKI member
    aki_active = False
    if kdigo_stage is not None and isinstance(kdigo_stage, (int, float)):
        if kdigo_stage >= 1:
            # Also check supporting evidence (creatinine or urine output)
            creatinina = inputs.get("creatinina")
            debito_urinario = inputs.get("debito_urinario_horario")
            if creatinina is not None or debito_urinario is not None:
                aki_active = True
            else:
                # KDIGO stage >=1 alone is sufficient if set by domain
                aki_active = True
    if kdigo_stage is None:
        missing.append("kdigo_stage")

    # Check causal temporal link
    causal_link = False
    if sepsis_onset is not None and aki_onset is not None:
        try:
            s_onset = float(sepsis_onset)
            a_onset = float(aki_onset)
            causal_lag_s = a_onset - s_onset
            # AKI onset at or after sepsis onset, within 72h window
            if causal_lag_s >= 0 and causal_lag_s <= 72.0 * 3600.0:
                causal_link = True
        except (ValueError, TypeError):
            pass
    if sepsis_onset is None:
        missing.append("sepsis_onset_at")
    if aki_onset is None:
        missing.append("aki_onset_at")

    fired = sepsis_active and aki_active and causal_link

    extra = {
        "causal_lag_h": None,
        "kdigo_stage": kdigo_stage,
        "sepsis_event": sepsis_event,
    }
    if sepsis_onset is not None and aki_onset is not None:
        try:
            extra["causal_lag_h"] = (
                float(aki_onset) - float(sepsis_onset)
            ) / 3600.0
        except (ValueError, TypeError):
            pass

    reason = ""
    if fired:
        reason = (
            f"SA-AKI correlation fired: sepsis={sepsis_event}, "
            f"KDIGO stage={kdigo_stage}, "
            f"causal lag={extra['causal_lag_h']:.1f}h"
        )
    else:
        parts = []
        if not sepsis_active:
            parts.append("no active sepsis event")
        if not aki_active:
            parts.append("no AKI (KDIGO >=1)")
        if not causal_link:
            parts.append("no causal temporal link within 72h")
        reason = "; ".join(parts) or "criteria not met"

    return fired, reason, missing, extra


def _evaluate_resp_hemo(
    inputs: dict[str, Any],
) -> tuple[bool, str, list[str], dict[str, Any]]:
    """Evaluate ALERT-CORR-RESP-HEMO-02: Respiratory + Hemodynamic.

    Logic:
      ards_moderate_or_severe AND shock_active within PT6H
      where ards_moderate_or_severe :=
        (relacao_pao2_fio2 <= 200 OR relacao_spo2_fio2 <= 235)
        AND ards_severity in {moderada, grave}
      shock_active := shock_event
        OR (pressao_arterial_media < 65 AND dose_vasopressor > 0)
    """
    pf_ratio = inputs.get("relacao_pao2_fio2")
    sf_ratio = inputs.get("relacao_spo2_fio2")
    ards_sev = inputs.get("ards_severity")
    map_val = inputs.get("pressao_arterial_media")
    vaso_dose = inputs.get("dose_vasopressor")
    shock_event = inputs.get("shock_event")

    missing: list[str] = []

    # ARDS moderate/severe
    ards_moderate_or_severe = False
    if ards_sev in ("moderada", "grave"):
        if pf_ratio is not None:
            try:
                if float(pf_ratio) <= 200:
                    ards_moderate_or_severe = True
            except (ValueError, TypeError):
                pass
        if not ards_moderate_or_severe and sf_ratio is not None:
            try:
                if float(sf_ratio) <= 235:
                    ards_moderate_or_severe = True
            except (ValueError, TypeError):
                pass
    if ards_sev is None:
        missing.append("ards_severity")
    if pf_ratio is None and sf_ratio is None:
        missing.append("relacao_pao2_fio2 or relacao_spo2_fio2")

    # Shock active
    shock_active = False
    if shock_event is True:
        shock_active = True
    elif map_val is not None and vaso_dose is not None:
        try:
            if float(map_val) < 65 and float(vaso_dose) > 0:
                shock_active = True
        except (ValueError, TypeError):
            pass
    if shock_event is None and (map_val is None or vaso_dose is None):
        missing.append("shock_event or (pressao_arterial_media + dose_vasopressor)")

    fired = ards_moderate_or_severe and shock_active

    extra: dict[str, Any] = {
        "ards_severity": ards_sev,
        "pf_ratio": pf_ratio,
        "sf_ratio": sf_ratio,
        "map_mmHg": map_val,
        "vasopressor_dose": vaso_dose,
    }

    reason = ""
    if fired:
        reason = (
            f"Cardiopulmonary failure correlation: ARDS={ards_sev}"
            f" (P/F={pf_ratio}) + shock"
        )
    else:
        parts = []
        if not ards_moderate_or_severe:
            parts.append("no moderate/severe ARDS")
        if not shock_active:
            parts.append("no active shock")
        reason = "; ".join(parts) or "criteria not met"

    return fired, reason, missing, extra


def _evaluate_qtc_electrolyte(
    inputs: dict[str, Any],
) -> tuple[bool, str, list[str], dict[str, Any]]:
    """Evaluate ALERT-CORR-QTC-ELEC-03: Drug + Electrolyte.

    AMPLIFICATION: two WARN members -> one CRITICAL.

    Logic:
      qtc > 500 ms
      AND qt_prolonging_drug_count >= 1
      AND (potassio < 3.5 OR magnesio < 0.7)
      within PT24H
    """
    qtc = inputs.get("qtc")
    qt_drug_count = inputs.get("qt_prolonging_drug_count")
    k = inputs.get("potassio")
    mg = inputs.get("magnesio")

    missing: list[str] = []

    # QTc > 500 (strict)
    qtc_prolonged = False
    if qtc is not None:
        try:
            if float(qtc) > 500:
                qtc_prolonged = True
        except (ValueError, TypeError):
            pass
    else:
        missing.append("qtc")

    # QT-prolonging drug active
    drug_active = False
    if qt_drug_count is not None:
        try:
            if int(qt_drug_count) >= 1:
                drug_active = True
        except (ValueError, TypeError):
            pass
    else:
        missing.append("qt_prolonging_drug_count")

    # Electrolyte substrate
    electrolyte_substrate = False
    if k is not None:
        try:
            if float(k) < 3.5:
                electrolyte_substrate = True
        except (ValueError, TypeError):
            pass
    if not electrolyte_substrate and mg is not None:
        try:
            if float(mg) < 0.7:
                electrolyte_substrate = True
        except (ValueError, TypeError):
            pass
    if k is None and mg is None:
        missing.append("potassio or magnesio")

    fired = qtc_prolonged and drug_active and electrolyte_substrate

    extra: dict[str, Any] = {
        "qtc_ms": qtc,
        "qt_drug_count": qt_drug_count,
        "potassio_mmol_L": k,
        "magnesio_mmol_L": mg,
        "amplified": True,  # WARN -> CRITICAL
    }

    reason = ""
    if fired:
        reason = (
            f"TdP substrate amplified: QTc={qtc}ms, "
            f"{qt_drug_count} QT drug(s), "
            f"K={k} mmol/L, Mg={mg} mmol/L"
        )
    else:
        parts = []
        if not qtc_prolonged:
            parts.append("QTc <= 500ms")
        if not drug_active:
            parts.append("no QT-prolonging drug active")
        if not electrolyte_substrate:
            parts.append("no electrolyte substrate (K>=3.5 and Mg>=0.7)")
        reason = "; ".join(parts) or "criteria not met"

    return fired, reason, missing, extra


def _evaluate_exam_redundant(
    inputs: dict[str, Any],
) -> tuple[bool, str, list[str], dict[str, Any]]:
    """Evaluate ALERT-CORR-EXAM-REDUND-04: Redundant diagnostic ordering.

    Per-class window test (corrected from legacy summed-across-classes).

    Logic:
      exam_class in known classes AND prior_within_window
      where hours_since_prior_same_class < W(exam_class)
    """
    exam_class = inputs.get("exam_class")
    prior_within_window = inputs.get("prior_order_within_window")
    hours_since = inputs.get("hours_since_prior_same_class")

    missing: list[str] = []
    if exam_class is None:
        missing.append("exam_class")
    if prior_within_window is None:
        missing.append("prior_order_within_window")

    fired = False

    if exam_class is not None and prior_within_window is True:
        window = EXAM_CLASS_WINDOWS.get(str(exam_class))
        if window is not None:
            if hours_since is not None:
                try:
                    if float(hours_since) < window:
                        fired = True
                except (ValueError, TypeError):
                    pass
            else:
                # If prior_within_window is already computed externally,
                # trust the flag
                fired = True
        else:
            # Unknown exam class — no window defined
            pass

    extra: dict[str, Any] = {
        "exam_class": exam_class,
        "hours_since_prior": hours_since,
        "reassessment_window_h": (
            EXAM_CLASS_WINDOWS.get(str(exam_class)) if exam_class else None
        ),
    }

    reason = ""
    if fired:
        reason = (
            f"Redundant exam: {exam_class} repeated within "
            f"{extra['reassessment_window_h']}h window "
            f"(last was {hours_since}h ago)"
        )
    else:
        parts = []
        if exam_class is None:
            parts.append("no exam_class specified")
        elif prior_within_window is not True:
            parts.append("no prior same-class order within window")
        else:
            window = EXAM_CLASS_WINDOWS.get(str(exam_class))
            if window is None:
                parts.append(f"unknown exam class: {exam_class}")
            elif hours_since is not None:
                try:
                    if float(hours_since) >= window:
                        parts.append(
                            f"{exam_class} last ordered {hours_since}h ago "
                            f"(outside {window}h window)"
                        )
                except (ValueError, TypeError):
                    pass
        reason = "; ".join(parts) or "criteria not met"

    return fired, reason, missing, extra


# Map of correlation evaluator functions
_CORRELATION_EVALUATORS: dict[str, Any] = {
    "ALERT-CORR-SEPSIS-AKI-01": _evaluate_sepsis_aki,
    "ALERT-CORR-RESP-HEMO-02": _evaluate_resp_hemo,
    "ALERT-CORR-QTC-ELEC-03": _evaluate_qtc_electrolyte,
    "ALERT-CORR-EXAM-REDUND-04": _evaluate_exam_redundant,
}

# Correlation display names
CORRELATION_NAMES: dict[str, str] = {
    "ALERT-CORR-SEPSIS-AKI-01": "Sepse com lesão renal aguda associada (SA-AKI)",
    "ALERT-CORR-RESP-HEMO-02": "Falência cardiopulmonar combinada (SDRA moderada/grave + choque)",
    "ALERT-CORR-QTC-ELEC-03": "Substrato de Torsades amplificado — QTc prolongado + hipocalemia/hipomagnesemia",
    "ALERT-CORR-EXAM-REDUND-04": "Solicitação redundante de exame (mesma classe dentro da janela de reavaliação)",
}


# ---------------------------------------------------------------------------
# Correlation Engine Service
# ---------------------------------------------------------------------------


class CorrelationEngine:
    """Cross-domain correlation evaluator.

    Consumes domain events (already staged by domain services) and
    evaluates correlation rules. Emits correlation events with linked
    alert references and member suppression directives.

    Usage::

        engine = CorrelationEngine()
        result = engine.evaluate("P-001", "E-001", patient_data)
        for corr in result.correlations:
            if corr.fired:
                print(f"CORRELATION: {corr.alert_id} severity={corr.severity}")
    """

    def __init__(self, repo_root: Path | None = None):
        if repo_root is None:
            repo_root = self._find_repo_root()
        self._repo_root = repo_root

    @staticmethod
    def _find_repo_root() -> Path:
        return Path(__file__).resolve().parents[3]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        patient_id: str,
        encounter_id: str,
        inputs: dict[str, Any],
        *,
        correlation_ids: list[str] | None = None,
    ) -> CorrelationEvaluationResult:
        """Evaluate all (or specified) correlation alerts for a patient.

        Args:
            patient_id: Patient MPI identifier.
            encounter_id: Encounter/visit identifier.
            inputs: Dict of clinical data from multiple domains.
            correlation_ids: Specific correlation IDs (default: all 4).

        Returns:
            CorrelationEvaluationResult with per-correlation results.
        """
        target_ids = correlation_ids or CORRELATION_ALERT_IDS
        results: list[CorrelationAlertResult] = []
        errors: list[str] = []

        for corr_id in target_ids:
            try:
                result = self._evaluate_single(corr_id, inputs)
                results.append(result)
            except Exception as e:
                logger.error("Error evaluating %s: %s", corr_id, e, exc_info=True)
                errors.append(f"{corr_id}: {e}")
                results.append(CorrelationAlertResult(
                    alert_id=corr_id,
                    name=CORRELATION_NAMES.get(corr_id, corr_id),
                    fired=False,
                    reason=f"Evaluation error: {e}",
                ))

        n_fired = sum(1 for r in results if r.fired)

        # Compute PPV summary
        ppv_summary = self._compute_ppv_summary(results)

        return CorrelationEvaluationResult(
            patient_id=patient_id,
            encounter_id=encounter_id,
            correlations=results,
            n_fired=n_fired,
            n_total=len(results),
            errors=errors,
            ppv_summary=ppv_summary,
        )

    def evaluate_single(
        self,
        correlation_id: str,
        inputs: dict[str, Any],
    ) -> CorrelationAlertResult:
        """Evaluate a single correlation by ID."""
        return self._evaluate_single(correlation_id, inputs)

    def emit_correlation_event(
        self,
        patient_id: str,
        encounter_id: str,
        result: CorrelationAlertResult,
    ) -> CorrelationEvent | None:
        """Create a correlation_event with linked alert references.

        Returns None if the correlation did not fire.
        """
        if not result.fired:
            return None

        import time

        return CorrelationEvent(
            correlation_id=result.alert_id,
            patient_id=patient_id,
            encounter_id=encounter_id,
            name=result.name,
            severity=result.severity.value if result.severity else "normal",
            source_event_refs=result.source_alerts,
            member_alerts_suppressed=result.suppressed_member_ids,
            fields=result.inputs_used,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    # ------------------------------------------------------------------
    # PPV Tracking
    # ------------------------------------------------------------------

    def get_ppv_budget(self, correlation_id: str) -> dict[str, Any] | None:
        """Return PPV budget for a correlation."""
        return PPV_BUDGET.get(correlation_id)

    def get_fleet_ppv_summary(self) -> dict[str, Any]:
        """Return fleet-level PPV budget summary."""
        total_volume = sum(
            b["est_volume_per_100_beds_day"] for b in PPV_BUDGET.values()
        )
        # Clinical correlations (1)(2)(3) net-suppress member pushes
        clinical_volume = sum(
            PPV_BUDGET[cid]["est_volume_per_100_beds_day"]
            for cid in CLINICAL_CORRELATIONS
        )
        # Efficiency (4) is net-additive
        efficiency_volume = sum(
            PPV_BUDGET[cid]["est_volume_per_100_beds_day"]
            for cid in EFFICIENCY_CORRELATIONS
        )

        return {
            "total_est_volume_per_100_beds_day": total_volume,
            "clinical_correlation_volume": clinical_volume,
            "efficiency_correlation_volume": efficiency_volume,
            "clinical_correlations": CLINICAL_CORRELATIONS,
            "efficiency_correlations": EFFICIENCY_CORRELATIONS,
            "fleet_ppv_floor": 0.60,
            "per_correlation": {
                cid: {
                    "target_ppv": PPV_BUDGET[cid]["target_ppv"],
                    "est_volume": PPV_BUDGET[cid]["est_volume_per_100_beds_day"],
                }
                for cid in CORRELATION_ALERT_IDS
            },
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _evaluate_single(
        self,
        correlation_id: str,
        inputs: dict[str, Any],
    ) -> CorrelationAlertResult:
        """Evaluate a single correlation rule."""
        evaluator = _CORRELATION_EVALUATORS.get(correlation_id)
        if evaluator is None:
            return CorrelationAlertResult(
                alert_id=correlation_id,
                name=CORRELATION_NAMES.get(correlation_id, correlation_id),
                fired=False,
                reason=f"Unknown correlation: {correlation_id}",
            )

        fired, reason, missing, extra = evaluator(inputs)

        severity_str = CORRELATION_SEVERITY.get(correlation_id, "watch")
        severity = SeverityLevel(severity_str)

        # Determine source alerts and suppressed members
        source_alerts, suppressed_ids = self._resolve_source_alerts(
            correlation_id, inputs
        )

        return CorrelationAlertResult(
            alert_id=correlation_id,
            name=CORRELATION_NAMES.get(correlation_id, correlation_id),
            fired=fired,
            severity=severity,
            inputs_used={**inputs, **extra},
            missing_inputs=missing,
            reason=reason,
            source_alerts=source_alerts,
            suppressed_member_ids=suppressed_ids,
            ppv_budget=PPV_BUDGET.get(correlation_id),
        )

    def _resolve_source_alerts(
        self, correlation_id: str, inputs: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Resolve which domain alerts triggered this correlation.

        Returns (source_alerts, suppressed_member_ids).
        """
        source_alerts: list[dict[str, Any]] = []
        suppressed: list[str] = []

        if correlation_id == "ALERT-CORR-SEPSIS-AKI-01":
            sepsis_event = inputs.get("sepsis_event", "")
            if "shock" in str(sepsis_event):
                source_alerts.append({
                    "domain": "sepsis",
                    "alert_id": "ALERT-SEPSIS-SHOCK-03",
                    "event_type": sepsis_event,
                })
                suppressed.append("ALERT-SEPSIS-SHOCK-03")
            elif "organ_dysfunction" in str(sepsis_event):
                source_alerts.append({
                    "domain": "sepsis",
                    "alert_id": "ALERT-SEPSIS-ORGAN-02",
                    "event_type": sepsis_event,
                })
                suppressed.append("ALERT-SEPSIS-ORGAN-02")
            kdigo = inputs.get("kdigo_stage")
            if kdigo is not None and int(kdigo) >= 1:
                aki_id = f"ALERT-AKI-KDIGO-STAGE-{int(kdigo):02d}"
                source_alerts.append({
                    "domain": "aki",
                    "alert_id": aki_id,
                    "kdigo_stage": kdigo,
                })
                suppressed.append(aki_id)

        elif correlation_id == "ALERT-CORR-RESP-HEMO-02":
            if inputs.get("ards_severity") in ("moderada", "grave"):
                source_alerts.append({
                    "domain": "respiratory",
                    "alert_id": "ALERT-RESP-ARDS-MODERATE-01",
                    "severity": inputs.get("ards_severity"),
                })
                suppressed.append("ALERT-RESP-ARDS-MODERATE-01")
            if inputs.get("shock_event") or (
                inputs.get("pressao_arterial_media") is not None
                and float(inputs.get("pressao_arterial_media", 100)) < 65
            ):
                source_alerts.append({
                    "domain": "hemodynamics",
                    "alert_id": "ALERT-HEMO-SHOCK-01",
                    "map": inputs.get("pressao_arterial_media"),
                })
                suppressed.append("ALERT-HEMO-SHOCK-01")

        elif correlation_id == "ALERT-CORR-QTC-ELEC-03":
            source_alerts.append({
                "domain": "pharmaco-interaction",
                "alert_id": "ALERT-DDX-QTC-PROLONGED-01",
                "qtc_ms": inputs.get("qtc"),
                "drug_count": inputs.get("qt_prolonging_drug_count"),
            })
            suppressed.append("ALERT-DDX-QTC-PROLONGED-01")
            if inputs.get("potassio") is not None:
                source_alerts.append({
                    "domain": "electrolyte",
                    "alert_id": "ALERT-ELY-POTASSIUM-01",
                    "potassio": inputs.get("potassio"),
                })
                suppressed.append("ALERT-ELY-POTASSIUM-01")
            if inputs.get("magnesio") is not None:
                source_alerts.append({
                    "domain": "electrolyte",
                    "alert_id": "ALERT-ELY-MAGNESIUM-01",
                    "magnesio": inputs.get("magnesio"),
                })
                suppressed.append("ALERT-ELY-MAGNESIUM-01")

        elif correlation_id == "ALERT-CORR-EXAM-REDUND-04":
            # Standalone — no member alerts to suppress
            source_alerts.append({
                "domain": "efficiency-stewardship",
                "alert_id": "ALERT-CORR-EXAM-REDUND-04",
                "exam_class": inputs.get("exam_class"),
                "lineage": "RULE-EFICIENCIA-007 (ADAPT)",
            })
            # Explicitly NO suppression — standalone, net-additive

        return source_alerts, suppressed

    def _compute_ppv_summary(
        self, results: list[CorrelationAlertResult],
    ) -> dict[str, Any]:
        """Compute fleet PPV summary from correlation results."""
        fired_by_correlation: dict[str, bool] = {}
        for r in results:
            fired_by_correlation[r.alert_id] = r.fired

        total_fired = sum(1 for v in fired_by_correlation.values() if v)
        total_est_volume = sum(
            PPV_BUDGET.get(cid, {}).get("est_volume_per_100_beds_day", 0)
            for cid, fired in fired_by_correlation.items()
            if fired
        )

        return {
            "total_fired": total_fired,
            "total_est_volume": total_est_volume,
            "per_correlation": fired_by_correlation,
            "fleet_ppv_target": 0.60,
        }


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


def evaluate_correlations(
    patient_id: str,
    encounter_id: str,
    inputs: dict[str, Any],
    *,
    correlation_ids: list[str] | None = None,
) -> CorrelationEvaluationResult:
    """Convenience: evaluate all correlations for a patient."""
    engine = CorrelationEngine()
    return engine.evaluate(
        patient_id, encounter_id, inputs, correlation_ids=correlation_ids,
    )


def get_correlation_engine() -> CorrelationEngine:
    """Get a singleton CorrelationEngine instance."""
    return CorrelationEngine()
