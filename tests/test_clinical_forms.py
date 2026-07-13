"""Tests for POST /api/clinical-forms — clinical assessment form submissions.

Covers:
- Valid submissions for all three form types (RASS, CAM-ICU, BPS-NRS)
- Invalid form_type → 422
- Missing required field (mpiId) → 422
- Unauthenticated request → 401

Contract note: ClinicalFormSubmission (src/intensicare/schemas/clinical_forms.py)
declares validation_alias="formId"/"mpiId" WITHOUT populate_by_name=True, so the
snake_case field names (form_type/patient_mpi_id) are rejected as input — only
the camelCase aliases are accepted. This is a deliberate, self-documented
contract (see the schema's own docstring) matching frontend JS/TS conventions;
no consumer (frontend-v3, legacy frontend, docs/contracts/) posts snake_case to
this endpoint, so the payloads below use the camelCase contract rather than
adding populate_by_name=True.
"""

from __future__ import annotations

import uuid

from httpx import AsyncClient
import pytest

VALID_RASS_PAYLOAD = {
    "formId": "rass",
    "mpiId": "MPI-001",
    "data": {"score": -1, "description": "Drowsy"},
}

VALID_CAM_ICU_PAYLOAD = {
    "formId": "cam-icu",
    "mpiId": "MPI-002",
    "data": {"feature_1": True, "feature_2": False, "feature_3": True, "feature_4": False},
}

VALID_BPS_NRS_PAYLOAD = {
    "formId": "bps-nrs",
    "mpiId": "MPI-003",
    "data": {"behavioral_score": 1, "nrs_score": 3},
}


# ─── Valid submissions ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_valid_rass(client: AsyncClient, user_headers: dict[str, str]):
    """POST /api/clinical-forms with valid RASS data → 201 with id/status/recorded_at."""
    response = await client.post(
        "/api/clinical-forms",
        json=VALID_RASS_PAYLOAD,
        headers=user_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "recorded"
    assert "recorded_at" in data
    # id must be a valid UUID
    uuid.UUID(data["id"])


@pytest.mark.asyncio
async def test_submit_valid_cam_icu(client: AsyncClient, user_headers: dict[str, str]):
    """POST /api/clinical-forms with valid CAM-ICU data → 201."""
    response = await client.post(
        "/api/clinical-forms",
        json=VALID_CAM_ICU_PAYLOAD,
        headers=user_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "recorded"


@pytest.mark.asyncio
async def test_submit_valid_bps_nrs(client: AsyncClient, user_headers: dict[str, str]):
    """POST /api/clinical-forms with valid BPS-NRS data → 201."""
    response = await client.post(
        "/api/clinical-forms",
        json=VALID_BPS_NRS_PAYLOAD,
        headers=user_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "recorded"


# ─── Invalid submissions ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_invalid_form_type(client: AsyncClient, user_headers: dict[str, str]):
    """POST /api/clinical-forms with invalid formId → 422."""
    response = await client.post(
        "/api/clinical-forms",
        json={
            "formId": "invalid",
            "mpiId": "MPI-001",
            "data": {},
        },
        headers=user_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_submit_missing_patient_mpi_id(client: AsyncClient, user_headers: dict[str, str]):
    """POST /api/clinical-forms without mpiId → 422."""
    response = await client.post(
        "/api/clinical-forms",
        json={
            "formId": "rass",
            "data": {},
        },
        headers=user_headers,
    )

    assert response.status_code == 422


# ─── Authentication ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_unauthenticated(client: AsyncClient):
    """POST /api/clinical-forms without auth → 401."""
    response = await client.post(
        "/api/clinical-forms",
        json=VALID_RASS_PAYLOAD,
    )

    assert response.status_code == 401
