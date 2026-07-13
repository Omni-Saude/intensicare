"""Deterministic deterioration-trend projection (lead-time estimate).

Dim E audit finding (dedução -8): "zero capacidade preditiva/lead-time;
Epic EDI ~24h, CLEW 8h FDA-cleared". This module closes that gap with a
deliberately *simple, explainable, deterministic* alternative to ML/black-box
prediction: ordinary least-squares linear regression over the patient's real
persisted ``clinical_score`` history (MEWS/NEWS2), projecting forward to the
next ratified alert threshold (``threshold_config`` — see migration 0038 /
ADR-0024's conceptual precedent, ``domain_piora_clinica``).

Design goals (explicitly NOT a ML model):
  * stdlib-only least-squares regression (no numpy/sklearn) — every number
    in the output can be recomputed by hand from the returned ``points``.
  * every projection carries the raw (timestamp, score) points it was fit
    on, so a clinician can audit the math directly (EXPLICABILIDADE).
  * confidence is reported honestly (``low``/``moderate``) from R² *and*
    sample size — a "perfect" 3-point fit is never over-trusted.
  * projections beyond a 24h horizon, or when the score is not worsening,
    are reported as ``None`` rather than a speculative number.

This is intentionally *not* a substitute for validated clinical prediction
tools (CLEW, Epic Deterioration Index) — see ``disclaimer`` on every result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.patient_cache import PatientCache
from intensicare.services.threshold_resolver import resolve_threshold

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Trend window: only scores from the last N hours are considered.
WINDOW_HOURS = 12.0

#: Minimum number of points required to fit a regression at all. Below this,
#: there is no statistically meaningful trend — "sem dado, sem previsão".
MIN_POINTS = 3

#: A regression can only ever be called "moderate" confidence with at least
#: this many points — 3 points is the bare minimum to fit a line at all and
#: is never, by itself, enough to trust a lead-time estimate.
MIN_POINTS_FOR_MODERATE_CONFIDENCE = 4

#: R² floor for "moderate" confidence (below this: "low", regardless of n).
R_SQUARED_MODERATE_FLOOR = 0.6

#: Lead-time projections beyond this horizon are not reported (too
#: speculative to be clinically actionable) — reported as ``None`` instead.
MAX_HOURS_TO_THRESHOLD = 24.0

#: Fallback watch/urgent/critical thresholds — identical to the migration
#: 0038 seed values (Subbe et al. 2001 for MEWS; RCP NEWS2 2017) — used when
#: threshold_config has no row for a tenant/score_type. Mirrors the same
#: fallback pattern already used by services/dashboard.py.
FALLBACK_THRESHOLDS: dict[str, tuple[int, int, int]] = {
    "MEWS": (3, 4, 5),
    "NEWS2": (3, 5, 7),
}

DISCLAIMER = (
    "Projeção linear determinística baseada em tendência recente; não substitui julgamento clínico."
)


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TrendPoint:
    """A single (timestamp, score) observation used to fit the trend."""

    timestamp: datetime
    score: int


@dataclass(frozen=True)
class TrendProjection:
    """Deterministic deterioration-trend projection for one score_type."""

    score_type: str
    current_score: int
    slope_per_hour: float
    r_squared: float
    n_points: int
    window_hours: float
    projected_threshold: int | None
    hours_to_threshold: float | None
    confidence: str  # "low" | "moderate"
    disclaimer: str
    points: list[TrendPoint] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Least-squares regression (stdlib only — no numpy/sklearn)
# ---------------------------------------------------------------------------


def _least_squares(x: list[float], y: list[float]) -> tuple[float, float, float]:
    """Fit ``y = intercept + slope * x`` by ordinary least squares.

    Returns ``(slope, intercept, r_squared)``. Pure stdlib arithmetic — no
    external numerical libraries — so every value is reproducible by hand.
    """
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    s_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y, strict=True))
    s_xx = sum((xi - mean_x) ** 2 for xi in x)

    if s_xx == 0:
        # All points share the same timestamp (degenerate window) — no time
        # variance to fit a slope against.
        return 0.0, mean_y, 0.0

    slope = s_xy / s_xx
    intercept = mean_y - slope * mean_x

    ss_tot = sum((yi - mean_y) ** 2 for yi in y)
    if ss_tot == 0:
        # Perfectly flat series (zero variance) — nothing left for slope to
        # explain; treat as a perfect (degenerate) fit.
        r_squared = 1.0
    else:
        y_hat = [intercept + slope * xi for xi in x]
        ss_res = sum((yi - yhi) ** 2 for yi, yhi in zip(y, y_hat, strict=True))
        r_squared = 1.0 - ss_res / ss_tot

    return slope, intercept, r_squared


def _next_threshold(current_score: int, thresholds: tuple[int, int, int]) -> int | None:
    """Return the smallest ratified threshold strictly above the current score.

    ``thresholds`` is ``(watch, urgent, critical)``. Returns ``None`` when the
    current score has already reached/passed the highest (critical) tier —
    there is no "next" tier left to project a lead time towards.
    """
    candidates = [t for t in thresholds if t > current_score]
    return min(candidates) if candidates else None


async def _resolve_thresholds(
    db: AsyncSession, mpi_id: str, score_type: str
) -> tuple[int, int, int]:
    """Resolve (watch, urgent, critical) thresholds for a patient's score_type.

    Tries the patient's real bed/unit/tenant-scoped ``threshold_config`` row
    (bed ≻ unit ≻ tenant resolution) and falls back to the ratified
    migration-0038 defaults when no patient/config row is found.
    """
    fallback = FALLBACK_THRESHOLDS.get(score_type, (3, 4, 5))

    patient = (
        await db.execute(select(PatientCache).where(PatientCache.mpi_id == mpi_id))
    ).scalar_one_or_none()
    if patient is None:
        return fallback

    config = await resolve_threshold(
        db,
        tenant_id=patient.tenant_id,
        score_type=score_type,
        unit=patient.unit,
        bed_id=patient.bed_id,
    )
    if config is None:
        return fallback

    return (config.watch_threshold, config.urgent_threshold, config.critical_threshold)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def compute_deterioration_trend(
    db: AsyncSession,
    mpi_id: str,
    now: datetime,
    score_type: str = "MEWS",
) -> TrendProjection | None:
    """Compute a deterministic lead-time projection for a patient's score trend.

    Fits an ordinary-least-squares line over the patient's ``clinical_score``
    history for ``score_type`` in the last :data:`WINDOW_HOURS` hours, then
    (if the trend is worsening) estimates the number of hours until the score
    crosses the next ratified alert threshold.

    Returns ``None`` when fewer than :data:`MIN_POINTS` scores exist in the
    window — "sem dado, sem previsão" — never a speculative projection from
    insufficient data.
    """
    window_start = now - timedelta(hours=WINDOW_HOURS)
    stmt = (
        select(ClinicalScore)
        .where(
            ClinicalScore.mpi_id == mpi_id,
            ClinicalScore.score_type == score_type,
            ClinicalScore.calculated_at >= window_start,
            ClinicalScore.calculated_at <= now,
        )
        .order_by(ClinicalScore.calculated_at.asc())
    )
    rows = (await db.execute(stmt)).scalars().all()

    if len(rows) < MIN_POINTS:
        return None

    points = [TrendPoint(timestamp=row.calculated_at, score=row.score_value) for row in rows]

    t0 = points[0].timestamp
    x = [(p.timestamp - t0).total_seconds() / 3600.0 for p in points]
    y = [float(p.score) for p in points]

    slope, _intercept, r_squared = _least_squares(x, y)
    n_points = len(points)
    current_score = points[-1].score  # most recent *observed* score — not fitted

    confidence = (
        "moderate"
        if r_squared >= R_SQUARED_MODERATE_FLOOR and n_points >= MIN_POINTS_FOR_MODERATE_CONFIDENCE
        else "low"
    )

    projected_threshold: int | None = None
    hours_to_threshold: float | None = None
    if slope > 0:
        thresholds = await _resolve_thresholds(db, mpi_id, score_type)
        next_threshold = _next_threshold(current_score, thresholds)
        if next_threshold is not None:
            hours = (next_threshold - current_score) / slope
            if hours <= MAX_HOURS_TO_THRESHOLD:
                projected_threshold = next_threshold
                hours_to_threshold = round(hours, 2)
            # else: beyond the 24h horizon — reported as None (too
            # speculative), per spec cap.

    return TrendProjection(
        score_type=score_type,
        current_score=current_score,
        slope_per_hour=round(slope, 4),
        r_squared=round(r_squared, 4),
        n_points=n_points,
        window_hours=WINDOW_HOURS,
        projected_threshold=projected_threshold,
        hours_to_threshold=hours_to_threshold,
        confidence=confidence,
        disclaimer=DISCLAIMER,
        points=points,
    )
