"""Testes de integração para a API principal."""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verifica se o endpoint legado /health redireciona e permanece alcançável.

    /health agora é um 307 redirect para /api/v1/health (main.py:160-162,
    backward compat). A intenção original — health check acessível pela
    rota legada — é preservada seguindo o redirect até o destino real.
    """
    response = await client.get("/health", follow_redirects=True)

    assert len(response.history) == 1
    assert response.history[0].status_code == 307
    assert response.request.url.path == "/api/v1/health"
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded", "unhealthy")
    assert data["version"] == "0.1.0"
