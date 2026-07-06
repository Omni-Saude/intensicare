"""Fhir R4 client module — queries HAPI FHIR server for patient enrichment."""

from intensicare.fhir.client import (
    FHIRClient,
    FHIRLabResult,
    FHIRMedicationAdministration,
    FHIRMedicationOrder,
    FHIRPatientContext,
    FHIRPatientData,
    get_fhir_client,
)

__all__ = [
    "FHIRClient",
    "FHIRLabResult",
    "FHIRMedicationAdministration",
    "FHIRMedicationOrder",
    "FHIRPatientContext",
    "FHIRPatientData",
    "get_fhir_client",
]
