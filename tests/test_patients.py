"""Testes para o serviço de consulta de status do paciente (patients.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from intensicare.services.patients import (
    _fhir_data_to_enrichment,
    _enrich_from_fhir,
)

# ---------------------------------------------------------------------------
# _fhir_data_to_enrichment
# ---------------------------------------------------------------------------


class FakeFHIRData:
    """Fake FHIRPatientData for testing."""
    mpi_id: str = "P-001"
    display_name: str | None = "João Silva"
    gender: str | None = "male"
    birth_date = None
    marital_status: str | None = None
    phone: str | None = None
    address: str | None = None
    primary_condition: str | None = None
    condition_list: list[str] = []
    allergy_list: list[str] = []
    latest_observations: dict = {}


def test_fhir_data_to_enrichment_basic():
    """Deve converter FHIRPatientData para FHIREnrichment."""
    data = FakeFHIRData()
    data.display_name = "Maria"
    data.gender = "female"
    enrichment = _fhir_data_to_enrichment(data)
    assert enrichment.display_name == "Maria"
    assert enrichment.gender == "female"
    assert enrichment.phone is None


def test_fhir_data_to_enrichment_allergy_list():
    """Deve preservar allergy_list na conversão."""
    data = FakeFHIRData()
    data.allergy_list = ["penicilina", "sulfa"]
    enrichment = _fhir_data_to_enrichment(data)
    assert enrichment.allergy_list == ["penicilina", "sulfa"]


# ---------------------------------------------------------------------------
# _enrich_from_fhir
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_enrich_from_fhir_not_configured():
    """Deve retornar None quando FHIR não está configurado."""
    with patch("intensicare.services.patients.settings") as mock_settings:
        mock_settings.fhir_base_url = ""
        result = await _enrich_from_fhir("P-001")
        assert result is None


@pytest.mark.asyncio
async def test_enrich_from_fhir_client_returns_none():
    """Deve retornar None quando o cliente FHIR retorna None."""
    with patch("intensicare.services.patients.settings") as mock_settings:
        mock_settings.fhir_base_url = "http://fhir.example.com"
        with patch("intensicare.services.patients.get_fhir_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_patient = AsyncMock(return_value=None)
            mock_get_client.return_value = mock_client
            result = await _enrich_from_fhir("P-001")
            assert result is None


@pytest.mark.asyncio
async def test_enrich_from_fhir_graceful_error():
    """Deve retornar None e loggar exception em caso de erro."""
    with patch("intensicare.services.patients.settings") as mock_settings:
        mock_settings.fhir_base_url = "http://fhir.example.com"
        with patch("intensicare.services.patients.get_fhir_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_patient = AsyncMock(side_effect=RuntimeError("FHIR down"))
            mock_get_client.return_value = mock_client
            result = await _enrich_from_fhir("P-001")
            assert result is None


@pytest.mark.asyncio
async def test_enrich_from_fhir_empty_data_returns_none():
    """Deve retornar None quando os dados FHIR só têm mpi_id."""
    with patch("intensicare.services.patients.settings") as mock_settings:
        mock_settings.fhir_base_url = "http://fhir.example.com"
        with patch("intensicare.services.patients.get_fhir_client") as mock_get_client:
            empty_data = FakeFHIRData()
            empty_data.display_name = None
            empty_data.gender = None
            empty_data.condition_list = []
            mock_client = AsyncMock()
            mock_client.get_patient = AsyncMock(return_value=empty_data)
            mock_get_client.return_value = mock_client
            result = await _enrich_from_fhir("P-001")
            assert result is None
