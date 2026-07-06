"""Testes para o serviço de dashboard (dashboard.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from intensicare.services.dashboard import (
    NEWS2_HIGH_RISK_THRESHOLD,
    NEWS2_MEDIUM_RISK_THRESHOLD,
)


class TestNews2RiskThresholds:
    """Testa as constantes de threshold de risco NEWS2."""

    def test_high_risk_threshold(self):
        """NEWS2_HIGH_RISK_THRESHOLD deve ser 7."""
        assert NEWS2_HIGH_RISK_THRESHOLD == 7

    def test_medium_risk_threshold(self):
        """NEWS2_MEDIUM_RISK_THRESHOLD deve ser 5."""
        assert NEWS2_MEDIUM_RISK_THRESHOLD == 5

    def test_risk_categories_are_ordered(self):
        """Categorias devem estar em ordem crescente de severidade."""
        assert NEWS2_MEDIUM_RISK_THRESHOLD < NEWS2_HIGH_RISK_THRESHOLD


# ---------------------------------------------------------------------------
# Testes do get_dashboard (com mock de DB)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_dashboard_empty_patients():
    """Deve retornar resposta vazia quando não há pacientes ativos."""
    from intensicare.services.dashboard import get_dashboard

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_dashboard(mock_db)
    assert response.total == 0
    assert response.patients == []
    assert response.active_alerts_total == 0


@pytest.mark.asyncio
async def test_get_dashboard_with_unit_filter():
    """Deve filtrar por unidade quando unit é fornecido."""
    from intensicare.services.dashboard import get_dashboard

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_dashboard(mock_db, unit="UTI-A")
    assert response.total == 0


# ---------------------------------------------------------------------------
# Testes do get_patient_detail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_patient_detail_not_found():
    """Deve retornar None quando o paciente não existe."""
    from intensicare.services.dashboard import get_patient_detail

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_patient_detail(mock_db, "P-NOEXIST")
    assert response is None
