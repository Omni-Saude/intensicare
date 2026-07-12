"""Ventilation Monitoring domain service.
Expands domain_respiratory.py with ventilation parameter extraction and trend analysis.

Provides:
  - extract_ventilation_params: extract ventilation parameters from clinical data
  - compute_ventilation_trend: 24h trend with min/max/avg/direction/change_pct
  - evaluate_ventilation: unified entry point (current params + trend)
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from intensicare.services.domain_respiratory import (
    _compute_pf_ratio,
    _ensure_fio2_fraction,
)
from intensicare.services.domain_respiratory import (
    evaluate_all as evaluate_respiratory,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dataclasses matching OpenAPI schemas (docs/contracts/ventilation-openapi.yaml)
# ---------------------------------------------------------------------------


@dataclass
class VentilationParameters:
    """Current ventilation parameters (single reading)."""

    id: int | None = None
    mpi_id: str = ""
    mode: str | None = None
    FiO2: float | None = None
    PEEP: float | None = None
    VC: float | None = None
    FR: int | None = None
    Pplat: float | None = None
    driving_pressure: float | None = None
    PaO2_FiO2_ratio: float | None = None
    SpO2: int | None = None
    tidal_volume_per_kg_pbw: float | None = None
    spontaneous_rate: int | None = None
    collected_at: str = ""
    source: str = "prontuario"


@dataclass
class ParameterTrend:
    """Trend data for a single parameter over the analysis window."""

    current: float | None = None
    min: float | None = None
    max: float | None = None
    avg: float | None = None
    direction: str = "stable"  # "rising", "falling", "stable"
    change_pct: float | None = None
    series: list[dict] = field(default_factory=list)


@dataclass
class VentilationTrend:
    """24-hour trend for all ventilation parameters."""

    period_hours: int = 24
    start_time: str = ""
    end_time: str = ""
    parameters: dict[str, ParameterTrend] = field(default_factory=dict)


@dataclass
class VentilationResult:
    """Complete ventilation evaluation result."""

    parameters: VentilationParameters = field(default_factory=VentilationParameters)
    trend: VentilationTrend = field(default_factory=VentilationTrend)
    collected_at: str = ""


# ---------------------------------------------------------------------------
# Mapping from raw field names → trend parameter keys
# ---------------------------------------------------------------------------

# Direct fields: trend param key → raw field name (or None for computed)
_TREND_PARAM_MAP: dict[str, str | None] = {
    "FiO2": "fio2",
    "PEEP": "peep",
    "VC": "volume_corrente",
    "FR": "frequencia_respiratoria",
    "Pplat": "pplat",
    "driving_pressure": None,  # computed: Pplat - PEEP
    "PaO2_FiO2_ratio": None,  # computed: PaO2 / FiO2
}

# Parameters to track in trend analysis (order preserved for stable iteration)
_TREND_PARAM_KEYS = [
    "FiO2",
    "PEEP",
    "VC",
    "FR",
    "Pplat",
    "driving_pressure",
    "PaO2_FiO2_ratio",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_float(v: Any) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _to_int(v: Any) -> int | None:
    """Safely convert a value to int, returning None on failure."""
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def _parse_iso_datetime(v: Any) -> datetime | None:
    """Parse an ISO-8601 datetime string. Returns None on failure."""
    if not v or not isinstance(v, str):
        return None
    try:
        # Handle both 'Z' suffix and +00:00 offset
        s = v.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _extract_param_value(entry: dict[str, Any], param_key: str) -> float | None:
    """Extract a numeric value from a history entry for a given trend parameter key.

    For computed parameters (driving_pressure, PaO2_FiO2_ratio), derive from
    raw fields within the entry.
    """
    raw_field = _TREND_PARAM_MAP.get(param_key)

    if raw_field is not None:
        # Direct field mapping
        return _to_float(entry.get(raw_field))

    # --- Computed parameters ---
    if param_key == "driving_pressure":
        pplat = _to_float(entry.get("pplat"))
        peep = _to_float(entry.get("peep"))
        if pplat is not None and peep is not None:
            return pplat - peep
        return None

    if param_key == "PaO2_FiO2_ratio":
        pao2 = entry.get("pao2")
        fio2 = entry.get("fio2")
        return _compute_pf_ratio(pao2, fio2)

    return None


def _determine_direction(values: list[float], threshold_pct: float = 5.0) -> str:
    """Determine trend direction from a time-ordered list of values.

    Args:
        values: list of numeric values in chronological order (oldest → newest).
        threshold_pct: minimum percent change to consider trending (default 5%).

    Returns:
        "rising", "falling", or "stable".
    """
    if len(values) < 2:
        return "stable"

    first = values[0]
    last = values[-1]

    if first == 0:
        # Avoid division by zero; use absolute difference
        if last > 0:
            return "rising"
        if last < 0:
            return "falling"
        return "stable"

    change_pct = ((last - first) / abs(first)) * 100

    if change_pct >= threshold_pct:
        return "rising"
    if change_pct <= -threshold_pct:
        return "falling"
    return "stable"


def _compute_change_pct(values: list[float]) -> float | None:
    """Compute percentage change from first to last value."""
    if len(values) < 2:
        return None
    first = values[0]
    last = values[-1]
    if first == 0:
        return None
    return ((last - first) / abs(first)) * 100


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_ventilation_params(patient_data: dict[str, Any]) -> VentilationParameters:
    """Extract ventilation parameters from patient clinical data.

    Reads raw clinical fields (Portuguese naming convention) and maps them
    to the OpenAPI VentilationParameters schema. Uses domain_respiratory helpers
    for FiO2 fraction enforcement and ratio computation.

    Args:
        patient_data: dict with clinical fields (fio2, peep, volume_corrente,
            frequencia_respiratoria, pplat, pao2, saturacao_o2, etc.)

    Returns:
        VentilationParameters with all extractable fields populated.
    """
    params = VentilationParameters()

    params.mpi_id = str(patient_data.get("mpi_id", ""))
    params.id = _to_int(patient_data.get("id"))
    params.mode = patient_data.get("modo_ventilatorio")

    # FiO2 — enforce fraction via domain_respiratory helper
    params.FiO2 = _ensure_fio2_fraction(patient_data.get("fio2"))

    params.PEEP = _to_float(patient_data.get("peep"))
    params.VC = _to_float(patient_data.get("volume_corrente"))
    params.FR = _to_int(patient_data.get("frequencia_respiratoria"))
    params.Pplat = _to_float(patient_data.get("pplat"))

    # Driving pressure = Pplat - PEEP (only when both available)
    if params.Pplat is not None and params.PEEP is not None:
        params.driving_pressure = params.Pplat - params.PEEP

    # PaO2/FiO2 ratio via domain_respiratory helper
    pao2 = patient_data.get("pao2")
    if pao2 is not None and params.FiO2 is not None:
        params.PaO2_FiO2_ratio = _compute_pf_ratio(pao2, params.FiO2)

    params.SpO2 = _to_int(patient_data.get("saturacao_o2"))
    params.tidal_volume_per_kg_pbw = _to_float(patient_data.get("vc_por_kg_pbw"))
    params.spontaneous_rate = _to_int(patient_data.get("fr_espontanea"))

    params.collected_at = str(
        patient_data.get("collected_at", datetime.now(timezone.utc).isoformat())
    )
    params.source = str(patient_data.get("source", "prontuario"))

    return params


def compute_ventilation_trend(
    mpi_id: str,
    history: list[dict[str, Any]],
    trend_hours: int = 24,
) -> VentilationTrend:
    """Compute trend analysis from ventilation history data.

    For each ventilation parameter (FiO2, PEEP, VC, FR, Pplat, driving_pressure,
    PaO2_FiO2_ratio), computes min, max, avg, direction, and percentage change
    over the specified time window.

    Args:
        mpi_id: patient identifier (for logging only).
        history: list of dicts with ventilation readings, each containing
            a ``collected_at`` timestamp and raw clinical fields.
        trend_hours: analysis window in hours (default 24).

    Returns:
        VentilationTrend with per-parameter trend data and time series.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=trend_hours)

    trend = VentilationTrend(
        period_hours=trend_hours,
        start_time=cutoff.isoformat(),
        end_time=now.isoformat(),
        parameters={},
    )

    if not history:
        logger.debug("compute_ventilation_trend: empty history for mpi_id=%s", mpi_id)
        return trend

    # --- Filter to time window and sort chronologically ---
    window_entries: list[dict[str, Any]] = []
    for entry in history:
        ts = _parse_iso_datetime(entry.get("collected_at"))
        if ts is None:
            continue
        if ts >= cutoff:
            window_entries.append(entry)

    if not window_entries:
        logger.debug("compute_ventilation_trend: no entries in window for mpi_id=%s", mpi_id)
        return trend

    # Sort oldest → newest
    window_entries.sort(
        key=lambda e: (
            _parse_iso_datetime(e.get("collected_at")) or datetime.min.replace(tzinfo=timezone.utc)
        )
    )

    # Update actual window bounds from data
    first_ts = _parse_iso_datetime(window_entries[0].get("collected_at"))
    last_ts = _parse_iso_datetime(window_entries[-1].get("collected_at"))
    if first_ts:
        trend.start_time = first_ts.isoformat()
    if last_ts:
        trend.end_time = last_ts.isoformat()

    # --- Compute trend for each parameter ---
    for param_key in _TREND_PARAM_KEYS:
        series: list[dict] = []
        values: list[float] = []

        for entry in window_entries:
            val = _extract_param_value(entry, param_key)
            collected = entry.get("collected_at", "")
            if val is not None:
                series.append({"value": val, "collected_at": collected})
                values.append(val)

        if not values:
            # No data for this parameter in the window
            trend.parameters[param_key] = ParameterTrend(direction="stable")
            continue

        current = values[-1] if values else None
        param_min = min(values)
        param_max = max(values)
        param_avg = sum(values) / len(values)
        direction = _determine_direction(values)
        change_pct = _compute_change_pct(values)

        trend.parameters[param_key] = ParameterTrend(
            current=current,
            min=param_min,
            max=param_max,
            avg=round(param_avg, 2),
            direction=direction,
            change_pct=round(change_pct, 2) if change_pct is not None else None,
            series=series,
        )

    return trend


def evaluate_ventilation(
    mpi_id: str,
    current_data: dict[str, Any],
    history: list[dict[str, Any]] | None = None,
    trend_hours: int = 24,
) -> VentilationResult:
    """Main entry point: evaluate ventilation parameters + trend.

    Extracts current ventilation parameters from ``current_data`` and computes
    a 24-hour trend from ``history``. Combines both into a single
    ``VentilationResult``.

    Args:
        mpi_id: patient identifier.
        current_data: dict with the latest clinical readings (same fields as
            ``extract_ventilation_params``).
        history: optional list of historical ventilation readings for trend
            analysis. If None or empty, trend will have no series data.
        trend_hours: analysis window in hours (default 24).

    Returns:
        VentilationResult with both current parameters and trend.
    """
    params = extract_ventilation_params(current_data)
    params.mpi_id = mpi_id

    if history is None:
        history = []

    trend = compute_ventilation_trend(
        mpi_id=mpi_id,
        history=history,
        trend_hours=trend_hours,
    )

    return VentilationResult(
        parameters=params,
        trend=trend,
        collected_at=params.collected_at,
    )


# ---------------------------------------------------------------------------
# Convenience: re-export respiratory evaluator for callers that want both
# ---------------------------------------------------------------------------

__all__ = [
    "ParameterTrend",
    "VentilationParameters",
    "VentilationResult",
    "VentilationTrend",
    "compute_ventilation_trend",
    "evaluate_respiratory",
    "evaluate_ventilation",
    "extract_ventilation_params",
]
