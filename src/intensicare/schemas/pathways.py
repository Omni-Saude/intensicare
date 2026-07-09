"""Pydantic schemas for Care Pathways API."""
from datetime import datetime
from pydantic import BaseModel, Field

class PathwayStateSchema(BaseModel):
    id: str = Field(..., description="State identifier (ex: 'initial')")
    name: str = Field(..., description="Human-readable state name")
    order: int = Field(..., ge=0, description="Sequential order")
    description: str | None = None
    is_terminal: bool = False

class PathwayCriteriaSchema(BaseModel):
    id: str = Field(..., description="Criteria ID (ex: 'crit-pf-ratio')")
    name: str = Field(..., description="Criteria name")
    category: str = Field(..., description="Clinical category")
    description: str | None = None
    unit: str | None = None
    normal_range: str | None = None
    alert_threshold: str | None = None
    met: bool | None = None
    value: str | None = None
    evaluated_at: datetime | None = None

class PathwaySchema(BaseModel):
    id: int
    name: str
    description: str | None = None
    slug: str
    active: bool = True
    states: list[PathwayStateSchema] = []
    criteria: list[PathwayCriteriaSchema] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

class PatientPathwaySchema(BaseModel):
    id: int
    mpi_id: str
    encounter_id: str = Field(..., description="Admission identifier from AMH Gold")
    bed_id: str | None = Field(None, description="Current bed at time of enrollment")
    unit: str | None = Field(None, description="Current unit at time of enrollment")
    pathway: PathwaySchema
    current_state: PathwayStateSchema
    criteria: list[PathwayCriteriaSchema] = []
    status: str = "active"
    severity: str | None = None
    enrolled_at: datetime
    enrolled_by: str | None = None
    completed_at: datetime | None = None
    updated_at: datetime | None = None

class PatientPathwayListResponse(BaseModel):
    items: list[PatientPathwaySchema]
    total: int

class PathwayListResponse(BaseModel):
    items: list[PathwaySchema]
    total: int

class EnrollPatientRequest(BaseModel):
    pathway_id: int = Field(..., description="Pathway ID to enroll patient in")
    encounter_id: str = Field(..., description="Admission identifier from AMH Gold")
    bed_id: str | None = Field(None, description="Current bed at time of enrollment")
    unit: str | None = Field(None, description="Current unit at time of enrollment")
    initial_criteria: list[dict] | None = None

class UpdateCriteriaRequest(BaseModel):
    criteria: list[dict]  # [{id: str, met: bool, value: str}]

class PathwayProgressSchema(BaseModel):
    patient_pathway_id: int
    mpi_id: str
    pathway_name: str
    current_state: PathwayStateSchema
    criteria_summary: dict  # {total, met, not_met, pending}
    criteria: list[PathwayCriteriaSchema] = []
    state_history: list[dict] = []
    trend: str = "none"  # improving, stable, worsening, none
    last_evaluated_at: datetime | None = None
    recommendation: str | None = None
