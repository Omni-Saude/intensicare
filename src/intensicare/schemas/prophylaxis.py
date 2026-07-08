"""Pydantic schemas for the Prophylaxis Bundles API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BundleCriterionSchema(BaseModel):
    """A single criterion within a prophylaxis bundle."""

    id: str
    label: str
    met: bool
    na: bool = False


class ProphylaxisBundleResponse(BaseModel):
    """Response schema for a single prophylaxis bundle assessment."""

    id: str
    name: str
    status: str  # complete, partial, pending, na
    score: int = Field(ge=0, le=100)
    criteria: list[BundleCriterionSchema] = Field(default_factory=list)
    assessed_at: datetime | None = None
    assessed_by: str | None = None


class ProphylaxisBundlesListResponse(BaseModel):
    """Response schema for the list of all 5 prophylaxis bundles."""

    bundles: list[ProphylaxisBundleResponse] = Field(default_factory=list)
    overall_status: str = "all_pending"  # all_complete, partial, all_pending
    overall_score: int = Field(default=0, ge=0, le=100)


class BundleCatalogResponse(BaseModel):
    """Response schema for the static bundle criteria catalog endpoint."""

    bundle_id: str
    bundle_name: str
    criteria: list[dict[str, Any]] = Field(default_factory=list)


class ProphylaxisBundleUpdateRequest(BaseModel):
    """Request schema for updating a bundle's criteria."""

    mpi_id: str
    criteria: list[BundleCriterionUpdate] = Field(default_factory=list)


class BundleCriterionUpdate(BaseModel):
    """A single criterion update within a PUT request."""

    id: str
    met: bool
