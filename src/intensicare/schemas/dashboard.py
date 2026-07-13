"""Pydantic schemas for the clinical dashboard.

Shape adapters: field names match the frontend contract (what gets serialized).
Backend-internal names are provided as Field(alias=...) so the service layer
can construct objects with the internal names via populate_by_name=True.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TripleEncodingMeta(BaseModel):
    """Triple-encoded severity metadata for frontend rendering."""

    color: str
    icon: str
    shape: str
    label: str
    description: str


class VitalRecord(BaseModel):
    """Single vital sign record — shape expected by frontend."""

    name: str
    value: float
    unit: str
    measured_at: str
    severity: str | None = None  # normal, watch, urgent, critical


class ScoreRecord(BaseModel):
    """Single score record — shape expected by frontend."""

    name: str
    value: float
    measured_at: str
    trend: str | None = None


class LatestVitals(BaseModel):
    """Most recent vital signs snapshot for a patient.

    Field names use the frontend contract (hr, bp_sys, bp_dia).
    Backend-internal names (heart_rate, systolic_bp, diastolic_bp)
    are provided as aliases for construction via populate_by_name=True.
    """

    model_config = {"populate_by_name": True}

    heart_rate: int | None = Field(default=None, alias="hr")
    systolic_bp: int | None = Field(default=None, alias="bp_sys")
    diastolic_bp: int | None = Field(default=None, alias="bp_dia")
    spo2: int | None = None
    respiratory_rate: int | None = None
    temperature: float | None = None
    recorded_at: str | None = None


class PatientBedSummary(BaseModel):
    """Summary of a patient for the bed grid dashboard.

    Field names match the frontend contract. Backend-internal names
    (bed_id, display_name, latest_mews, etc.) are aliases.
    """

    model_config = {"populate_by_name": True}

    mpi_id: str
    bed_id: str | None = Field(default=None, alias="bed")
    display_name: str = Field(alias="patient_name")
    unit: str | None = None
    latest_mews: int | None = Field(default=None, alias="mews")
    latest_news2: int | None = Field(default=None, alias="news2")
    news2_risk: str | None = None  # low, medium, high
    mews_trend: str | None = None  # increasing, decreasing, stable
    news2_trend: str | None = None
    active_alerts_count: int = 0
    # AUDIT-008 resolved: canonical severity model (normal/watch/urgent/critical)
    highest_alert_severity: str | None = Field(default=None, alias="severity")
    highest_alert_encoding: TripleEncodingMeta | None = None
    latest_vitals: LatestVitals | None = Field(default=None, alias="vitals")
    last_updated: str | None = Field(default=None, alias="last_vital_at")
    active_pathways: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Active pathways with slug and severity for frontend rendering",
    )


class DashboardResponse(BaseModel):
    """Dashboard response with list of patient bed summaries.

    Field name critical_count matches frontend contract.
    Backend-internal name active_alerts_total is an alias.
    """

    model_config = {"populate_by_name": True}

    patients: list[PatientBedSummary] = Field(default_factory=list)
    total: int = 0
    active_alerts_total: int = Field(default=0, alias="critical_count")
    unit_counts: dict[str, int] = Field(default_factory=dict)


class VitalsHistoryPoint(BaseModel):
    """A single vitals data point for charting (internal representation)."""

    recorded_at: str
    heart_rate: int | None = None
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    temperature: float | None = None
    spo2: int | None = None
    respiratory_rate: int | None = None
    avpu: str | None = None
    supplemental_o2: bool | None = None


class ScoreHistoryPoint(BaseModel):
    """A single score data point for charting (internal representation)."""

    calculated_at: str
    score_type: str
    score_value: int
    trend: str | None = None


class PatientDetailResponse(BaseModel):
    """Detailed patient view with vitals history and scores.

    Field names match the frontend contract. Backend-internal names
    (bed_id, display_name) are aliases.

    Internal-only fields (vitals_history, mews_history, news2_history,
    active_alerts) are excluded from serialization.
    """

    model_config = {"populate_by_name": True}

    mpi_id: str
    bed_id: str | None = Field(default=None, alias="bed")
    display_name: str = Field(alias="patient_name")
    unit: str | None = None

    # Internal fields — used by service, excluded from serialization
    vitals_history: list[VitalsHistoryPoint] = Field(default_factory=list, exclude=True)
    mews_history: list[ScoreHistoryPoint] = Field(default_factory=list, exclude=True)
    news2_history: list[ScoreHistoryPoint] = Field(default_factory=list, exclude=True)
    active_alerts: list[dict[str, Any]] = Field(default_factory=list, exclude=True)

    # Frontend-facing fields
    vitals: list[VitalRecord] = Field(default_factory=list)
    scores: list[ScoreRecord] = Field(default_factory=list)
    active_pathways_count: int = 0
