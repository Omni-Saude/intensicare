"""
Fluid Balance domain — RATIFIED per WAVE 2B (P1 rules).
Implements the 07:00-07:00 nursing day boundary, fluid balance computation,
intake/output aggregation, temperature maxima, and 2-hour time-bucketing.

RATIFIED thresholds per RATIFICATION.md:
  - RAT-BALANCO-HIDRICO-03 (RULE-006): 24h fluid balance = intake - output over 07:00-07:00
  - RAT-BALANCO-HIDRICO-04 (RULE-007): Ganhos (intake) summed over 07:00-07:00 nursing day
  - RAT-BALANCO-HIDRICO-05 (RULE-008): Diureses (urine output) summed over 07:00-07:00 nursing day
  - RAT-BALANCO-HIDRICO-06 (RULE-010): Maximum temperature over 07:00-07:00 nursing day
  - RAT-BALANCO-HIDRICO-08 (RULE-013): 2-hour time-bucketing with corrected 22:00-00:00 wrap
  - RAT-BALANCO-HIDRICO-09 (RULE-016): tempo_criacao with total_seconds()

Design decisions ratified 2026-07-04:
  - Nursing day: 07:00-07:00 (America/Sao_Paulo)
  - Fluid balance = intake_sum - output_sum (0 is a valid balance, never coerced to None)
  - Urine output tipos: {diurese_espontanea, diurese_sonda}
  - Temperature aggregate: MAX (not last)
  - 2h bucket anchor: 08:00 with corrected 22:00-00:00 wrap
  - tempo_criacao: corrected from timedelta.seconds to total_seconds()
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pytz

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Nursing day cutoff: 07:00 local time
NURSING_DAY_HOUR = 7
NURSING_DAY_TZ = "America/Sao_Paulo"

# Valid urine output tipos
URINE_OUTPUT_TIPOS = {"diurese_espontanea", "diurese_sonda"}

# 2-hour bucket labels (08:00 start)
BUCKET_LABELS = [
    "08:00-10:00",
    "10:00-12:00",
    "12:00-14:00",
    "14:00-16:00",
    "16:00-18:00",
    "18:00-20:00",
    "20:00-22:00",
    "22:00-00:00",
    "00:00-02:00",
    "02:00-04:00",
    "04:00-06:00",
    "06:00-08:00",
]

# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass
class NursingDayWindow:
    """A 07:00-07:00 nursing day window in local time."""

    start: datetime
    end: datetime
    nursing_date: str  # YYYY-MM-DD of the day this window belongs to


@dataclass
class FluidBalanceResult:
    """Result of fluid balance computation for a nursing day."""

    nursing_date: str
    total_intake_ml: float = 0.0
    total_output_ml: float = 0.0
    net_balance_ml: float = 0.0
    urine_output_ml: float = 0.0
    max_temperature_c: float | None = None
    bucket_intake: dict[str, float] = field(default_factory=dict)
    bucket_output: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Nursing day window computation
# ---------------------------------------------------------------------------


def get_nursing_day_window(reference: datetime | None = None) -> NursingDayWindow:
    """Compute the 07:00-07:00 nursing day window containing `reference`.

    If reference is None, uses the current time in America/Sao_Paulo.

    Rules:
      - If reference.hour < 7: window spans from previous day 07:00 to today 07:00
      - If reference.hour >= 7: window spans from today 07:00 to next day 07:00

    The nursing_date is the date of the day that starts the window (i.e., the date
    at 07:00). Pre-07:00 entries on a given date belong to the previous nursing day.
    """
    tz = pytz.timezone(NURSING_DAY_TZ)

    if reference is None:
        reference = datetime.now(tz)

    # Normalize to local timezone
    if reference.tzinfo is None:
        reference = tz.localize(reference)
    else:
        reference = reference.astimezone(tz)

    # Determine which day's 07:00 starts the window
    if reference.hour < NURSING_DAY_HOUR:
        # Reference is in early morning (00:00-06:59) — belongs to previous nursing day
        start_date = reference.date() - timedelta(days=1)
    else:
        start_date = reference.date()

    start = tz.localize(
        datetime(start_date.year, start_date.month, start_date.day, NURSING_DAY_HOUR, 0, 0)
    )
    end = start + timedelta(hours=24)

    return NursingDayWindow(
        start=start,
        end=end,
        nursing_date=start_date.isoformat(),
    )


# ---------------------------------------------------------------------------
# tempo_criacao — corrected from timedelta.seconds to total_seconds()
# ---------------------------------------------------------------------------


def tempo_criacao(created_at: datetime, reference: datetime | None = None) -> float:
    """Hours elapsed since a record was created.

    CORRECTED from timedelta.seconds (0..86399 intra-day only) to total_seconds().
    This fixes the recency window guard defect where records >24h old could
    spuriously pass "< N hours" checks (RAT-BALANCO-HIDRICO-09).
    """
    if reference is None:
        reference = datetime.now(timezone.utc)

    # Normalize: if naive, assume UTC
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)

    delta = reference - created_at
    return delta.total_seconds() / 3600.0


# ---------------------------------------------------------------------------
# Fluid balance computation
# ---------------------------------------------------------------------------


def compute_24h_fluid_balance(
    entradas: list[dict[str, Any]],
    saidas: list[dict[str, Any]],
    window: NursingDayWindow | None = None,
    reference: datetime | None = None,
) -> FluidBalanceResult:
    """Compute 24h fluid balance over the 07:00-07:00 nursing day.

    Args:
        entradas: List of intake records, each with 'quantidade' (float) and 'data_hora' (datetime).
        saidas: List of output records, each with 'quantidade' (float), 'tipo' (str), and 'data_hora' (datetime).
        window: Pre-computed nursing day window. If None, computes from `reference`.
        reference: Reference datetime for window computation.

    Returns:
        FluidBalanceResult with computed values. 0 is a valid balance value, never coerced to None.
        Missing sums default to 0.0.

    RATIFIED per RAT-BALANCO-HIDRICO-03/04/05/06.
    """
    if window is None:
        window = get_nursing_day_window(reference)

    # Filter entries within the window
    total_intake = 0.0
    for e in entradas:
        dt = _safe_datetime(e.get("data_hora"))
        if dt is not None and window.start <= dt < window.end:
            qtd = _safe_float(e.get("quantidade"), 0.0)
            total_intake += qtd

    total_output = 0.0
    urine_output = 0.0
    for s in saidas:
        dt = _safe_datetime(s.get("data_hora"))
        if dt is not None and window.start <= dt < window.end:
            qtd = _safe_float(s.get("quantidade"), 0.0)
            total_output += qtd
            # Urine output: filtered by tipo
            tipo = s.get("tipo", "")
            if tipo in URINE_OUTPUT_TIPOS:
                urine_output += qtd

    net_balance = total_intake - total_output

    return FluidBalanceResult(
        nursing_date=window.nursing_date,
        total_intake_ml=total_intake,
        total_output_ml=total_output,
        net_balance_ml=net_balance,
        urine_output_ml=urine_output,
    )


def compute_ganhos(
    entradas: list[dict[str, Any]],
    window: NursingDayWindow | None = None,
    reference: datetime | None = None,
) -> float:
    """Sum of all fluid-intake quantities (Entrada.quantidade, no type filter)
    over the 07:00-07:00 nursing day.

    RATIFIED per RAT-BALANCO-HIDRICO-04.
    0 is a valid sum, never coerced to None.
    """
    if window is None:
        window = get_nursing_day_window(reference)

    total = 0.0
    for e in entradas:
        dt = _safe_datetime(e.get("data_hora"))
        if dt is not None and window.start <= dt < window.end:
            qtd = _safe_float(e.get("quantidade"), 0.0)
            total += qtd

    return total


def compute_diureses(
    saidas: list[dict[str, Any]],
    window: NursingDayWindow | None = None,
    reference: datetime | None = None,
) -> float:
    """Sum of urine-output quantities (Saida with tipo in {diurese_espontanea, diurese_sonda})
    over the 07:00-07:00 nursing day.

    RATIFIED per RAT-BALANCO-HIDRICO-05.
    0 is a valid sum, never coerced to None.
    """
    if window is None:
        window = get_nursing_day_window(reference)

    total = 0.0
    for s in saidas:
        dt = _safe_datetime(s.get("data_hora"))
        if dt is not None and window.start <= dt < window.end:
            tipo = s.get("tipo", "")
            if tipo in URINE_OUTPUT_TIPOS:
                qtd = _safe_float(s.get("quantidade"), 0.0)
                total += qtd

    return total


def compute_max_temperature(
    sinais_vitais: list[dict[str, Any]],
    window: NursingDayWindow | None = None,
    reference: datetime | None = None,
) -> float | None:
    """Maximum body temperature over the 07:00-07:00 nursing day.

    Takes the MAX of per-window maxima. None-stripping applied.
    Returns None if no valid temperature measurements exist.

    RATIFIED per RAT-BALANCO-HIDRICO-06.
    """
    if window is None:
        window = get_nursing_day_window(reference)

    max_temp = None
    for sv in sinais_vitais:
        dt = _safe_datetime(sv.get("data_hora"))
        if dt is not None and window.start <= dt < window.end:
            temp = sv.get("temperatura")
            if temp is not None:
                try:
                    t = float(temp)
                    if max_temp is None or t > max_temp:
                        max_temp = t
                except (ValueError, TypeError):
                    pass

    return max_temp


# ---------------------------------------------------------------------------
# 2-hour time-bucketing (visao-geral grid)
# ---------------------------------------------------------------------------


def compute_2h_buckets(
    entradas: list[dict[str, Any]],
    saidas: list[dict[str, Any]],
    reference: datetime | None = None,
) -> dict[str, dict[str, float]]:
    """Build fluid-balance overview grid: sum quantidade into twelve fixed 2-hour buckets.

    Bucket labels/edges start at 08:00 and wrap through 06:00-08:00, using
    America/Sao_Paulo local time.

    CORRECTED: The [22:00, 00:00] bucket now properly wraps. Previously the SQL
    BETWEEN 22:00:00 and 00:00:00 produced a degenerate/empty range.

    RATIFIED per RAT-BALANCO-HIDRICO-08.
    """
    tz = pytz.timezone(NURSING_DAY_TZ)

    if reference is None:
        reference = datetime.now(tz)
    if reference.tzinfo is None:
        reference = tz.localize(reference)
    else:
        reference = reference.astimezone(tz)

    # The grid anchor date: if before 08:00, use previous day
    if reference.hour < 8:
        anchor_date = reference.date() - timedelta(days=1)
    else:
        anchor_date = reference.date()

    # Build 12 two-hour bucket edges starting at 08:00 on anchor_date
    bucket_edges: list[tuple[datetime, datetime, str]] = []
    for i in range(12):
        start_hour = (8 + 2 * i) % 24
        end_hour = (start_hour + 2) % 24

        # Determine dates for start and end (handle day wrap)
        if start_hour == 22 and end_hour == 0:
            # 22:00-00:00 — end is on NEXT day
            start_dt = tz.localize(
                datetime(anchor_date.year, anchor_date.month, anchor_date.day, 22, 0, 0)
            )
            end_dt = start_dt + timedelta(hours=2)  # 00:00 next day
        elif start_hour >= 8:
            # 08:00-10:00, 10:00-12:00, ..., 20:00-22:00
            start_dt = tz.localize(
                datetime(anchor_date.year, anchor_date.month, anchor_date.day, start_hour, 0, 0)
            )
            end_dt = start_dt + timedelta(hours=2)
        elif start_hour < 8:
            # 00:00-02:00, 02:00-04:00, 04:00-06:00, 06:00-08:00 — next day
            next_date = anchor_date + timedelta(days=1)
            start_dt = tz.localize(
                datetime(next_date.year, next_date.month, next_date.day, start_hour, 0, 0)
            )
            end_dt = start_dt + timedelta(hours=2)
        else:
            raise ValueError(f"Unexpected start_hour: {start_hour}")

        bucket_edges.append((start_dt, end_dt, BUCKET_LABELS[i]))

    # Initialize buckets
    buckets: dict[str, dict[str, float]] = {}
    for _, _, label in bucket_edges:
        buckets[label] = {"intake": 0.0, "output": 0.0}

    # Fill intake buckets
    for e in entradas:
        dt = _safe_datetime(e.get("data_hora"))
        if dt is not None:
            qtd = _safe_float(e.get("quantidade"), 0.0)
            for start_dt, end_dt, label in bucket_edges:
                if start_dt <= dt < end_dt:
                    buckets[label]["intake"] += qtd
                    break

    # Fill output buckets
    for s in saidas:
        dt = _safe_datetime(s.get("data_hora"))
        if dt is not None:
            qtd = _safe_float(s.get("quantidade"), 0.0)
            for start_dt, end_dt, label in bucket_edges:
                if start_dt <= dt < end_dt:
                    buckets[label]["output"] += qtd
                    break

    return buckets


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_datetime(value: Any) -> datetime | None:
    """Coerce a value to datetime, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
    return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Coerce a value to float, returning default on failure."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _is_finite(value: float) -> bool:
    """Check if a float is finite (not NaN, not inf)."""
    return math.isfinite(value)
