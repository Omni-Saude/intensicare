"""Pydantic schemas para API v1."""

from intensicare.schemas.clinical_forms import (
    ClinicalFormResponse,
    ClinicalFormSubmission,
)
from intensicare.schemas.dashboard import (
    DashboardResponse,
    PatientBedSummary,
    PatientDetailResponse,
    ScoreHistoryPoint,
    VitalsHistoryPoint,
)
from intensicare.schemas.patients import (
    FHIREnrichment,
    PatientStatusResponse,
    ScoreSummary,
    TrendSummary,
    VitalSignSummary,
)
from intensicare.schemas.severity import (
    CANONICAL_SEVERITIES,
    SeverityLevel,
    TripleEncoder,
    highest_severity,
    max_severity,
)
from intensicare.schemas.thresholds import (
    ThresholdConfigBase,
    ThresholdConfigCreate,
    ThresholdConfigResponse,
    ThresholdConfigUpdate,
)
from intensicare.schemas.vitals import (
    VitalSignCreate,
    VitalSignResponse,
)

__all__ = [
    "CANONICAL_SEVERITIES",
    "ClinicalFormResponse",
    "ClinicalFormSubmission",
    "DashboardResponse",
    "FHIREnrichment",
    "PatientBedSummary",
    "PatientDetailResponse",
    "PatientStatusResponse",
    "ScoreHistoryPoint",
    "ScoreSummary",
    "SeverityLevel",
    "ThresholdConfigBase",
    "ThresholdConfigCreate",
    "ThresholdConfigResponse",
    "ThresholdConfigUpdate",
    "TrendSummary",
    "TripleEncoder",
    "VitalSignCreate",
    "VitalSignResponse",
    "VitalSignSummary",
    "VitalsHistoryPoint",
    "highest_severity",
    "max_severity",
]
