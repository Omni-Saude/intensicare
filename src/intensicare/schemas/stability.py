"""Pydantic schemas for Hemodynamic Stability API."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class StabilityCriterionSchema(BaseModel):
    name: str
    value: str
    threshold: str
    status: str = Field(..., description="normal, warning, critical")
    category: str = Field(
        ..., description="vasopressor, perfusion, cardiac_output, fluid_balance, lactate, combined"
    )
    alert_id: str | None = None


class StabilityStatusSchema(BaseModel):
    mpi_id: str
    score: int = Field(..., ge=0, le=27, description="Number of criteria in warning/critical")
    severity: str = Field(..., description="estavel, atencao, critico")
    criteria: list[StabilityCriterionSchema] = []
    recommendation: str | None = None
    assessed_at: datetime


class StabilityTrendPointSchema(BaseModel):
    date: date
    score: int = Field(..., ge=0, le=27)
    severity: str
    criteria_triggered: int


class StabilityTrendSchema(BaseModel):
    mpi_id: str
    current: StabilityStatusSchema
    trend: list[StabilityTrendPointSchema] = []
    direction: str = "stable"  # improving, stable, worsening
    delta_7d: int = 0
