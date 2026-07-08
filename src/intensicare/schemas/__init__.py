"""Pydantic schemas para API v1."""

from intensicare.schemas.alert_routing import (
    AlertRoutingRuleCreate,
    AlertRoutingRuleResponse,
    AlertRoutingRulesListResponse,
    AlertRoutingRuleUpdate,
)
from intensicare.schemas.antimicrobial import (
    AntimicrobialAssessmentListResponse,
    AntimicrobialAssessmentResponse,
    AntimicrobialCriteriaCatalogResponse,
    AntimicrobialCriterionSchema,
    CreateAntimicrobialAssessmentSchema,
)
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
from intensicare.schemas.deterioration import (
    DeteriorationCriteriaSchema,
    DeteriorationHistoryResponse,
    DeteriorationScoreSchema,
)
from intensicare.schemas.patients import (
    FHIREnrichment,
    PatientStatusResponse,
    ScoreSummary,
    TrendSummary,
    VitalSignSummary,
)
from intensicare.schemas.pathways import (
    EnrollPatientRequest,
    PathwayListResponse,
    PathwayProgressSchema,
    PathwaySchema,
    PatientPathwayListResponse,
    PatientPathwaySchema,
    UpdateCriteriaRequest,
)
from intensicare.schemas.prophylaxis import (
    BundleCatalogResponse,
    BundleCriterionSchema,
    ProphylaxisBundleResponse,
    ProphylaxisBundlesListResponse,
    ProphylaxisBundleUpdateRequest,
)
from intensicare.schemas.severity import (
    CANONICAL_SEVERITIES,
    SeverityLevel,
    TripleEncoder,
    highest_severity,
    max_severity,
)
from intensicare.schemas.stability import (
    StabilityCriterionSchema,
    StabilityStatusSchema,
    StabilityTrendPointSchema,
    StabilityTrendSchema,
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
    "AlertRoutingRuleCreate",
    "AlertRoutingRuleResponse",
    "AlertRoutingRulesListResponse",
    "AlertRoutingRuleUpdate",
    "AntimicrobialAssessmentListResponse",
    "AntimicrobialAssessmentResponse",
    "AntimicrobialCriteriaCatalogResponse",
    "AntimicrobialCriterionSchema",
    "BundleCatalogResponse",
    "BundleCriterionSchema",
    "CANONICAL_SEVERITIES",
    "ClinicalFormResponse",
    "ClinicalFormSubmission",
    "CreateAntimicrobialAssessmentSchema",
    "DashboardResponse",
    "DeteriorationCriteriaSchema",
    "DeteriorationHistoryResponse",
    "DeteriorationScoreSchema",
    "EnrollPatientRequest",
    "FHIREnrichment",
    "PatientBedSummary",
    "PatientDetailResponse",
    "PatientPathwayListResponse",
    "PatientPathwaySchema",
    "PatientStatusResponse",
    "PathwayListResponse",
    "PathwayProgressSchema",
    "PathwaySchema",
    "ProphylaxisBundleResponse",
    "ProphylaxisBundlesListResponse",
    "ProphylaxisBundleUpdateRequest",
    "ScoreHistoryPoint",
    "ScoreSummary",
    "SeverityLevel",
    "StabilityCriterionSchema",
    "StabilityStatusSchema",
    "StabilityTrendPointSchema",
    "StabilityTrendSchema",
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
