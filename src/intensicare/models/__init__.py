"""Modelos SQLAlchemy — tabelas do banco de dados."""
from intensicare.models.alert import Alert
from intensicare.models.alert_definition_version import AlertDefinitionVersion
from intensicare.models.alert_routing import AlertRoutingRule
from intensicare.models.algorithm_registry import AlgorithmRegistry
from intensicare.models.antimicrobial import AntimicrobialAssessment
from intensicare.models.audit_trail import AuditTrail
from intensicare.models.clinical_form import ClinicalFormSubmission, FormDefinition
from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.correlation_event import CorrelationEvent
from intensicare.models.deterioration import DeteriorationAssessment
from intensicare.models.documentacao import Documentacao
from intensicare.models.evolucao import Evolucao, EvolucaoSection, EvolucaoTemplate
from intensicare.models.lab_result import LabResult
from intensicare.models.medication import MedicationAdministration, MedicationOrder
from intensicare.models.movimentacao import AdmissionEpisode, Bed, PatientMovement
from intensicare.models.patient_cache import PatientCache
from intensicare.models.pathway import (
    Pathway,
    PathwayCriteria,
    PathwayStateTransition,
    PatientPathway,
)
from intensicare.models.prescricao import (
    AgendaPrescricao,
    AuditoriaPrescricao,
    InteracaoAlerta,
    Prescricao,
)
from intensicare.models.prophylaxis import ProphylaxisAssessment
from intensicare.models.ratification_event import RatificationEvent
from intensicare.models.sedacao import SedationAssessment
from intensicare.models.stability import StabilityAssessment
from intensicare.models.threshold_config import ThresholdConfig
from intensicare.models.user import User
from intensicare.models.vital_sign import VitalSign

__all__ = [
    "AdmissionEpisode",
    "AgendaPrescricao",
    "Alert",
    "AlertDefinitionVersion",
    "AlertRoutingRule",
    "AlgorithmRegistry",
    "AntimicrobialAssessment",
    "AuditTrail",
    "AuditoriaPrescricao",
    "Bed",
    "ClinicalScore",
    "ClinicalFormSubmission",
    "CorrelationEvent",
    "DeteriorationAssessment",
    "Documentacao",
    "Evolucao",
    "EvolucaoSection",
    "EvolucaoTemplate",
    "FormDefinition",
    "InteracaoAlerta",
    "LabResult",
    "MedicationAdministration",
    "MedicationOrder",
    "Pathway",
    "PathwayCriteria",
    "PathwayStateTransition",
    "PatientCache",
    "PatientMovement",
    "PatientPathway",
    "Prescricao",
    "ProphylaxisAssessment",
    "RatificationEvent",
    "SedationAssessment",
    "StabilityAssessment",
    "ThresholdConfig",
    "User",
    "VitalSign",
]
