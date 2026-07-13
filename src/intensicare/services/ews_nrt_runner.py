"""
EWS NRT Runner — Event-driven early-warning score computation and alerting.

Hooks into the vital_sign ingestion pipeline to evaluate the 4 EWS alert
definitions from early-warning-scores.yaml:

- ALERT-EWS-NEWS2-DETERIORATION-01  (edge-triggered NEWS2 >=7 crossing / red parameter)
- ALERT-EWS-TREND-RISING-02         (NEWS2/MEWS delta >=3 across window)
- ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03 (ΔSOFA >=2 from 24h baseline)
- ALERT-EWS-DISCHARGE-READINESS-04  (composite stability → step-down readiness)

NRT p95 budget: score compute <30s, alert fire <5s.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.alert import Alert
from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.vital_sign import VitalSign
from intensicare.services.mews import calculate_mews
from intensicare.services.news2 import (
    calculate_news2,
    score_consciousness,
    score_heart_rate,
    score_respiratory_rate,
    score_spo2,
    score_systolic_bp,
    score_temperature,
)
from intensicare.services.qsofa import calculate_qsofa
from intensicare.services.sofa import calculate_sofa

# ---------------------------------------------------------------------------
# Score snapshot — holds all 4 EWS scores + prior values for edge/trend evaluation
# ---------------------------------------------------------------------------


@dataclass
class EWSScoreSnapshot:
    """Aggregated EWS scores computed from a vital_sign record."""

    mpi_id: str
    vital_sign_id: int

    # Current scores
    mews_score: int = 0
    news2_score: int = 0
    news2_components: dict[str, int] = field(default_factory=dict)
    qsofa_score: int = 0
    sofa_total: int = 0

    # Previous values (fetched from clinical_score history)
    news2_score_prev: int | None = None
    mews_score_prev: int | None = None
    sofa_total_baseline_24h: int | None = None  # most recent SOFA within 24h

    # NEWS2 individual parameter scores
    news2_rr_score: int = 0
    news2_spo2_score: int = 0
    news2_sbp_score: int = 0
    news2_hr_score: int = 0
    news2_cons_score: int = 0
    news2_temp_score: int = 0

    # Previous red-parameter state (from prior measurement)
    news2_red_params_prev: set[str] = field(default_factory=set)

    # Windowed scores for trend detection
    news2_at_window_start: int | None = None
    mews_at_window_start: int | None = None

    # Discharge-readiness inputs
    gcs: int | None = None
    map_value: float | None = None
    vasopressor_dose: float | None = None
    mechanical_ventilation: bool = False
    spo2: int | None = None
    supplemental_o2: bool | None = None

    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Helper queries
# ---------------------------------------------------------------------------


async def _fetch_previous_score(
    db: AsyncSession,
    mpi_id: str,
    score_type: str,
    before: datetime,
    *,
    window: timedelta | None = None,
) -> tuple[int | None, datetime | None]:
    """Fetch the most recent score of a given type before a timestamp.

    Args:
        db: Async database session.
        mpi_id: Patient MPI ID.
        score_type: e.g. 'MEWS', 'NEWS2', 'SOFA'.
        before: Reference timestamp (exclusive upper bound).
        window: Optional time window; if provided, only consider scores
                within this window of ``before``.

    Returns:
        Tuple of (score_value, calculated_at) or (None, None).
    """
    stmt = (
        select(ClinicalScore.score_value, ClinicalScore.calculated_at)
        .where(
            ClinicalScore.mpi_id == mpi_id,
            ClinicalScore.score_type == score_type,
            ClinicalScore.calculated_at < before,
        )
        .order_by(ClinicalScore.calculated_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        return None, None

    if window is not None:
        age = before - row.calculated_at
        if age > window:
            return None, None

    return row.score_value, row.calculated_at


async def _fetch_scores_in_window(
    db: AsyncSession,
    mpi_id: str,
    score_type: str,
    since: datetime,
    before: datetime,
) -> list[ClinicalScore]:
    """Fetch all scores of a given type within a window."""
    stmt = (
        select(ClinicalScore)
        .where(
            ClinicalScore.mpi_id == mpi_id,
            ClinicalScore.score_type == score_type,
            ClinicalScore.calculated_at >= since,
            ClinicalScore.calculated_at < before,
        )
        .order_by(ClinicalScore.calculated_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _fetch_previous_news2_components(
    db: AsyncSession,
    mpi_id: str,
    before: datetime,
) -> dict[str, int]:
    """Fetch NEWS2 component scores from the most recent prior score."""
    stmt = (
        select(ClinicalScore.components)
        .where(
            ClinicalScore.mpi_id == mpi_id,
            ClinicalScore.score_type == "NEWS2",
            ClinicalScore.calculated_at < before,
        )
        .order_by(ClinicalScore.calculated_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None or row.components is None:
        return {}
    return {k: v for k, v in row.components.items() if isinstance(v, int)}


# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------


def _compute_ews_scores(vs: VitalSign) -> EWSScoreSnapshot:
    """Compute all 4 EWS scores from a VitalSign record (no DB access)."""
    snapshot = EWSScoreSnapshot(
        mpi_id=vs.mpi_id,
        vital_sign_id=vs.id if vs.id else 0,
    )

    # MEWS
    mews_score, _ = calculate_mews(
        heart_rate=vs.heart_rate,
        systolic_bp=vs.systolic_bp,
        respiratory_rate=vs.respiratory_rate,
        temperature=vs.temperature,
        avpu=vs.avpu,
    )
    snapshot.mews_score = mews_score

    # NEWS2
    news2_result = calculate_news2(
        respiratory_rate=vs.respiratory_rate,
        spo2=vs.spo2,
        hypercapnic=False,
        supplemental_o2=vs.supplemental_o2,
        systolic_bp=vs.systolic_bp,
        heart_rate=vs.heart_rate,
        avpu=vs.avpu,
        temperature=vs.temperature,
    )
    snapshot.news2_score = news2_result.total_score

    # Individual NEWS2 parameter scores
    snapshot.news2_rr_score = score_respiratory_rate(vs.respiratory_rate)
    snapshot.news2_spo2_score = score_spo2(vs.spo2, hypercapnic=bool(vs.supplemental_o2))
    snapshot.news2_sbp_score = score_systolic_bp(vs.systolic_bp)
    snapshot.news2_hr_score = score_heart_rate(vs.heart_rate)
    snapshot.news2_cons_score = score_consciousness(vs.avpu)
    snapshot.news2_temp_score = score_temperature(vs.temperature)

    # qSOFA
    qsofa_result = calculate_qsofa(
        respiratory_rate=vs.respiratory_rate,
        systolic_bp=vs.systolic_bp,
        gcs=vs.gcs,
    )
    snapshot.qsofa_score = qsofa_result.total_score

    # SOFA
    sofa_result = calculate_sofa(
        pao2_fio2=vs.pao2_fio2,
        mechanical_ventilation=vs.mechanical_ventilation,
        platelets=vs.platelets,
        bilirubin=vs.bilirubin,
        map_value=vs.map_value,
        vasopressor_type=vs.vasopressor_type,
        vasopressor_dose_mcg_kg_min=vs.vasopressor_dose_mcg_kg_min,
        gcs=vs.gcs,
        creatinine=vs.creatinine,
        urine_output_ml_day=vs.urine_output_ml_day,
    )
    snapshot.sofa_total = sofa_result.total_score

    # Discharge-readiness fields
    snapshot.gcs = vs.gcs
    snapshot.map_value = vs.map_value
    snapshot.vasopressor_dose = vs.vasopressor_dose_mcg_kg_min
    snapshot.mechanical_ventilation = vs.mechanical_ventilation
    snapshot.spo2 = vs.spo2
    snapshot.supplemental_o2 = vs.supplemental_o2

    return snapshot


# ---------------------------------------------------------------------------
# Alert evaluation
# ---------------------------------------------------------------------------


def _get_red_params(snapshot: EWSScoreSnapshot) -> set[str]:
    """Return the set of NEWS2 parameter names that score 3 (red)."""
    red: set[str] = set()
    if snapshot.news2_rr_score == 3:
        red.add("respiratory_rate")
    if snapshot.news2_spo2_score == 3:
        red.add("spo2")
    if snapshot.news2_sbp_score == 3:
        red.add("systolic_bp")
    if snapshot.news2_hr_score == 3:
        red.add("heart_rate")
    if snapshot.news2_cons_score == 3:
        red.add("consciousness")
    if snapshot.news2_temp_score == 3:
        red.add("temperature")
    return red


# ── ALERT-EWS-NEWS2-DETERIORATION-01 ───────────────────────────────────


def evaluate_ews_deterioration_01(
    snapshot: EWSScoreSnapshot,
) -> tuple[bool, str]:
    """Edge-triggered NEWS2 deterioration.

    Fires when:
    - NEWS2 crosses >=7 from below (new crossing), OR
    - A single NEWS2 parameter scores 3 (red) and was NOT red at the
      previous measurement.

    Edge-triggered only — persistent high state does NOT re-fire.
    """
    reasons: list[str] = []

    # Edge trigger: NEWS2 crossing into >=7
    if snapshot.news2_score >= 7:
        if snapshot.news2_score_prev is None or snapshot.news2_score_prev < 7:
            reasons.append(
                f"NEWS2 edge crossing: {snapshot.news2_score_prev} -> {snapshot.news2_score}"
            )
        # else: persistent high — suppressed

    # Single red parameter: newly red
    current_red = _get_red_params(snapshot)
    new_red = current_red - snapshot.news2_red_params_prev
    if new_red:
        reasons.append(f"New red parameter(s): {', '.join(sorted(new_red))} scored 3")

    if reasons:
        return True, "; ".join(reasons)
    return False, ""


# ── ALERT-EWS-TREND-RISING-02 ──────────────────────────────────────────


def evaluate_ews_trend_rising_02(
    snapshot: EWSScoreSnapshot,
) -> tuple[bool, str]:
    """Sustained rising trend in NEWS2 or MEWS.

    Fires when:
    - NEWS2 delta >= 3 from window start (8h), OR
    - MEWS delta >= 3 from window start (8h),
    - With >=2 consecutive scorings in the window.
    """
    reasons: list[str] = []

    # NEWS2 trend
    if (
        snapshot.news2_at_window_start is not None
        and snapshot.news2_score - snapshot.news2_at_window_start >= 3
    ):
        delta = snapshot.news2_score - snapshot.news2_at_window_start
        reasons.append(
            f"NEWS2 rising: {snapshot.news2_at_window_start} -> {snapshot.news2_score} (Δ+{delta})"
        )

    # MEWS trend
    if (
        snapshot.mews_at_window_start is not None
        and snapshot.mews_score - snapshot.mews_at_window_start >= 3
    ):
        delta = snapshot.mews_score - snapshot.mews_at_window_start
        reasons.append(
            f"MEWS rising: {snapshot.mews_at_window_start} -> {snapshot.mews_score} (Δ+{delta})"
        )

    if reasons:
        return True, "; ".join(reasons)
    return False, ""


# ── ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03 ──────────────────────────


def evaluate_ews_sofa_organ_dysfunction_03(
    snapshot: EWSScoreSnapshot,
) -> tuple[bool, str]:
    """Acute SOFA rise >=2 from 24h baseline (Sepsis-3 organ dysfunction)."""
    if snapshot.sofa_total_baseline_24h is None:
        return False, ""

    delta = snapshot.sofa_total - snapshot.sofa_total_baseline_24h
    if delta >= 2:
        return True, (
            f"SOFA acute rise: {snapshot.sofa_total_baseline_24h} -> "
            f"{snapshot.sofa_total} (Δ+{delta})"
        )
    return False, ""


# ── ALERT-EWS-DISCHARGE-READINESS-04 ───────────────────────────────────


def evaluate_ews_discharge_readiness_04(
    snapshot: EWSScoreSnapshot,
    *,
    has_active_deterioration: bool = False,
) -> tuple[bool, str]:
    """Composite step-down readiness signal.

    All criteria must be met:
    - GCS >= 14
    - Vasopressor dose == 0 mcg/kg/min
    - MAP >= 65 mmHg
    - NOT on mechanical ventilation
    - SpO2 >= 92% on room air or low-flow O2
    - No active deterioration alert

    Note: admitted_gt_24h and lactate are checked by the caller via DB.
    """
    failures: list[str] = []

    if has_active_deterioration:
        failures.append("active deterioration alert present")

    if snapshot.gcs is not None and snapshot.gcs < 14:
        failures.append(f"GCS {snapshot.gcs} < 14")
    elif snapshot.gcs is None:
        failures.append("GCS unavailable")

    if snapshot.vasopressor_dose is not None and snapshot.vasopressor_dose > 0:
        failures.append(f"vasopressor dose {snapshot.vasopressor_dose} > 0")

    if snapshot.map_value is not None and snapshot.map_value < 65:
        failures.append(f"MAP {snapshot.map_value} < 65")

    if snapshot.mechanical_ventilation:
        failures.append("mechanical ventilation active")

    if snapshot.spo2 is not None and snapshot.spo2 < 92 and not snapshot.supplemental_o2:
        failures.append(f"SpO2 {snapshot.spo2} < 92% on room air")

    if failures:
        return False, "; ".join(failures)
    return True, "all stability criteria met"


# ---------------------------------------------------------------------------
# Main NRT pipeline — called from vitals ingestion (post-insert hook)
# ---------------------------------------------------------------------------


async def process_ews_nrt(
    db: AsyncSession,
    vs: VitalSign,
    *,
    tenant_id: str | None = None,
    unit: str | None = None,
    # --- Discharge-readiness extra flags (looked up by caller) ---
    admitted_gt_24h: bool = False,
    lactate_arterial: float | None = None,
    has_active_deterioration: bool = False,
) -> list[Alert]:
    """Event-driven EWS NRT pipeline.

    Computes all 4 EWS scores, evaluates the 4 alert definitions from
    early-warning-scores.yaml, and creates Alerts for any that fire.

    Designed to be called from ``ingest_vitals()`` (vitals.py) after the
    vital_sign record has been flushed and scores persisted.

    Args:
        db: Async database session.
        vs: The newly-inserted VitalSign record (must have an id).
        tenant_id: Tenant identifier.
        unit: Unit identifier.
        admitted_gt_24h: Whether the patient has been admitted >24h.
        lactate_arterial: Most recent arterial lactate in mmol/L.
        has_active_deterioration: Whether an active EWS deterioration
            alert (01/02/03) exists for this patient.

    Returns:
        List of Alert objects created (may be empty).
    """
    now = datetime.now(timezone.utc)

    # 1. Compute current scores
    snapshot = _compute_ews_scores(vs)

    # 2. Fetch previous scores for edge/trend/baseline
    snapshot.news2_score_prev, _ = await _fetch_previous_score(
        db,
        vs.mpi_id,
        "NEWS2",
        now,
    )
    snapshot.mews_score_prev, _ = await _fetch_previous_score(
        db,
        vs.mpi_id,
        "MEWS",
        now,
    )

    # SOFA 24h baseline
    sofa_prev_val, _ = await _fetch_previous_score(
        db,
        vs.mpi_id,
        "SOFA",
        now,
        window=timedelta(hours=24),
    )
    if sofa_prev_val is not None:
        snapshot.sofa_total_baseline_24h = sofa_prev_val

    # Previous NEWS2 red parameters
    prev_news2_comps = await _fetch_previous_news2_components(
        db,
        vs.mpi_id,
        now,
    )
    snapshot.news2_red_params_prev = {
        name for name, score in prev_news2_comps.items() if score == 3
    }

    # Window-start scores for trend (8h window)
    window_ago = now - timedelta(hours=8)
    snapshot.news2_at_window_start, _ = await _fetch_previous_score(
        db,
        vs.mpi_id,
        "NEWS2",
        now,
        window=timedelta(hours=8),
    )
    # If we have a recent enough score within window, use it as baseline
    # Otherwise, the earliest score in the window becomes the reference
    news2_in_window = await _fetch_scores_in_window(
        db,
        vs.mpi_id,
        "NEWS2",
        window_ago,
        now,
    )
    if news2_in_window:
        snapshot.news2_at_window_start = news2_in_window[0].score_value

    mews_in_window = await _fetch_scores_in_window(
        db,
        vs.mpi_id,
        "MEWS",
        window_ago,
        now,
    )
    if mews_in_window:
        snapshot.mews_at_window_start = mews_in_window[0].score_value

    # 3. Evaluate each alert definition
    alerts: list[Alert] = []

    # ── ALERT-EWS-NEWS2-DETERIORATION-01 ──
    fired_01, reason_01 = evaluate_ews_deterioration_01(snapshot)
    if fired_01:
        alerts.append(
            _build_alert(
                alert_id="ALERT-EWS-NEWS2-DETERIORATION-01",
                name="Deterioração clínica — NEWS2 alto (novo cruzamento >=7 ou parâmetro vermelho)",
                severity="urgent",
                snapshot=snapshot,
                reason=reason_01,
                tenant_id=tenant_id,
                unit=unit,
            )
        )

    # ── ALERT-EWS-TREND-RISING-02 ──
    fired_02, reason_02 = evaluate_ews_trend_rising_02(snapshot)
    if fired_02:
        alerts.append(
            _build_alert(
                alert_id="ALERT-EWS-TREND-RISING-02",
                name="Tendência de piora — escore de alerta precoce em elevação",
                severity="watch",
                snapshot=snapshot,
                reason=reason_02,
                tenant_id=tenant_id,
                unit=unit,
            )
        )

    # ── ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03 ──
    fired_03, reason_03 = evaluate_ews_sofa_organ_dysfunction_03(snapshot)
    if fired_03:
        alerts.append(
            _build_alert(
                alert_id="ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03",
                name="Disfunção orgânica aguda — aumento de SOFA >=2",
                severity="urgent",
                snapshot=snapshot,
                reason=reason_03,
                tenant_id=tenant_id,
                unit=unit,
            )
        )

    # ── ALERT-EWS-DISCHARGE-READINESS-04 ──
    # The discharge-readiness check requires extra context:
    # - admitted_gt_24h
    # - lactate_arterial < 2 mmol/L
    # - no active deterioration
    fired_04 = False
    reason_04 = ""
    if admitted_gt_24h and (lactate_arterial is None or lactate_arterial < 2.0):
        fired_04, reason_04 = evaluate_ews_discharge_readiness_04(
            snapshot,
            has_active_deterioration=has_active_deterioration,
        )

    if fired_04:
        alerts.append(
            _build_alert(
                alert_id="ALERT-EWS-DISCHARGE-READINESS-04",
                name="Prontidão para alta/step-down da UTI",
                severity="normal",
                snapshot=snapshot,
                reason=reason_04,
                tenant_id=tenant_id,
                unit=unit,
            )
        )

    # 4. Persist alerts
    for alert in alerts:
        db.add(alert)
    if alerts:
        await db.flush()

    return alerts


# ---------------------------------------------------------------------------
# Alert builder
# ---------------------------------------------------------------------------


def _build_alert(
    *,
    alert_id: str,
    name: str,
    severity: str,
    snapshot: EWSScoreSnapshot,
    reason: str,
    tenant_id: str | None = None,
    unit: str | None = None,
) -> Alert:
    """Build an Alert ORM object from evaluation results."""
    now = datetime.now(timezone.utc)

    title = f"[{alert_id}] {name}"
    body_lines = [
        f"Patient: {snapshot.mpi_id}",
        f"Alert: {alert_id} — {name}",
        f"Severity: {severity}",
        f"Reason: {reason}",
        "",
        "Scores:",
        f"  MEWS:  {snapshot.mews_score}",
        f"  NEWS2: {snapshot.news2_score}",
        f"  qSOFA: {snapshot.qsofa_score}",
        f"  SOFA:  {snapshot.sofa_total}",
    ]
    if snapshot.news2_score_prev is not None:
        body_lines.append(f"  NEWS2 prev: {snapshot.news2_score_prev}")
    if snapshot.sofa_total_baseline_24h is not None:
        body_lines.append(f"  SOFA 24h baseline: {snapshot.sofa_total_baseline_24h}")
    if tenant_id:
        body_lines.append(f"Tenant: {tenant_id}")
    if unit:
        body_lines.append(f"Unit: {unit}")

    return Alert(
        mpi_id=snapshot.mpi_id,
        score_id=snapshot.vital_sign_id,
        severity=severity,
        status="active",
        title=title,
        body="\n".join(body_lines),
        created_at=now,
    )


# ---------------------------------------------------------------------------
# Convenience: hook into the existing vitals ingestion pipeline
# ---------------------------------------------------------------------------


async def process_ews_after_vital_insert(
    db: AsyncSession,
    vs: VitalSign,
    *,
    tenant_id: str | None = None,
    unit: str | None = None,
    admitted_gt_24h: bool = False,
    lactate_arterial: float | None = None,
) -> list[Alert]:
    """Call this from ingest_vitals() after scores are persisted.

    Checks for active deterioration alerts before evaluating discharge
    readiness.
    """
    # Check for active deterioration alerts
    has_active_det = await _has_active_deterioration(db, vs.mpi_id)

    return await process_ews_nrt(
        db=db,
        vs=vs,
        tenant_id=tenant_id,
        unit=unit,
        admitted_gt_24h=admitted_gt_24h,
        lactate_arterial=lactate_arterial,
        has_active_deterioration=has_active_det,
    )


async def _has_active_deterioration(
    db: AsyncSession,
    mpi_id: str,
) -> bool:
    """Check if the patient has an active EWS deterioration alert (01/02/03)."""
    stmt = select(Alert).where(
        Alert.mpi_id == mpi_id,
        Alert.status == "active",
        Alert.title.like("%EWS-NEWS2-DETERIORATION%")
        | Alert.title.like("%EWS-TREND-RISING%")
        | Alert.title.like("%EWS-SOFA-ACUTE-ORGAN%"),
    )
    result = await db.execute(stmt)
    return result.first() is not None
