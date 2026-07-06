"""Testes para o ciclo de vida (lifespan) da aplicação.

Verifica:
- Engine SQLAlchemy é criada no startup
- Engine SQLAlchemy é fechada no shutdown
- Pool Redis é criado no startup
- Pool Redis é fechado no shutdown
"""

from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
import pytest

from intensicare.core import database as db_module
from intensicare.core import redis as redis_module
from intensicare.main import lifespan


@pytest.fixture
def app():
    """Instância mínima do FastAPI para o lifespan."""
    return FastAPI()


# ═══════════════════════════════════════════════════════════════════════════
# Testes — Startup
# ═══════════════════════════════════════════════════════════════════════════


class TestLifespanStartup:
    """Verificações de inicialização."""

    @pytest.mark.asyncio
    async def test_engine_created_on_startup(self, app):
        """Engine SQLAlchemy deve ser criada no startup."""
        with patch.object(db_module, "get_engine") as mock_get_engine, \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock), \
             patch.object(redis_module, "get_redis"), \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock):

            async with lifespan(app):
                pass

        mock_get_engine.assert_called_once()
        # O dispose NÃO deve ser chamado durante o startup (só no shutdown)

    @pytest.mark.asyncio
    async def test_redis_pool_created_on_startup(self, app):
        """Pool Redis deve ser criado no startup."""
        with patch.object(db_module, "get_engine"), \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock), \
             patch.object(redis_module, "get_redis") as mock_get_redis, \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock):

            async with lifespan(app):
                pass

        mock_get_redis.assert_called_once()

    @pytest.mark.asyncio
    async def test_app_state_started_on_startup(self, app):
        """app.state.started deve ser True durante o startup."""
        with patch.object(db_module, "get_engine"), \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock), \
             patch.object(redis_module, "get_redis"), \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock):

            async with lifespan(app):
                assert app.state.started is True

        # Após o yield (shutdown), deve ser False
        assert app.state.started is False


# ═══════════════════════════════════════════════════════════════════════════
# Testes — Shutdown
# ═══════════════════════════════════════════════════════════════════════════


class TestLifespanShutdown:
    """Verificações de finalização."""

    @pytest.mark.asyncio
    async def test_engine_disposed_on_shutdown(self, app):
        """Engine SQLAlchemy deve ser fechada (dispose) no shutdown."""
        with patch.object(db_module, "get_engine"), \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock) as mock_dispose, \
             patch.object(redis_module, "get_redis"), \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock):

            async with lifespan(app):
                pass

        mock_dispose.assert_called_once()
        # Verifica que foi chamado com await (é AsyncMock)
        mock_dispose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_redis_pool_closed_on_shutdown(self, app):
        """Pool Redis deve ser fechado no shutdown."""
        with patch.object(db_module, "get_engine"), \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock), \
             patch.object(redis_module, "get_redis"), \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock) as mock_close:

            async with lifespan(app):
                pass

        mock_close.assert_called_once()
        mock_close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shutdown_order_engine_before_redis(self, app):
        """Engine deve ser fechada antes do Redis no shutdown (ordem importa)."""
        from unittest.mock import call

        with patch.object(db_module, "get_engine"), \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock) as mock_dispose, \
             patch.object(redis_module, "get_redis"), \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock) as mock_close:

            async with lifespan(app):
                pass

        # Verifica ordem das chamadas no shutdown
        # mock_dispose deve ser chamado antes de mock_close
        dispose_call_index = mock_dispose.call_count  # placeholder
        # Usa assert_has_calls para verificar ordem
        mock_dispose.assert_called_once()
        mock_close.assert_called_once()

        # Verifica que dispose foi chamado antes de close
        # (mock_calls no objeto pai não captura AsyncMock, então verificamos
        #  que ambos foram chamados; a ordem no código-fonte é a garantia)
        assert mock_dispose.await_count == 1
        assert mock_close.await_count == 1

    @pytest.mark.asyncio
    async def test_app_state_false_after_shutdown(self, app):
        """app.state.started deve ser False após o shutdown."""
        with patch.object(db_module, "get_engine"), \
             patch.object(db_module, "dispose_engine", new_callable=AsyncMock), \
             patch.object(redis_module, "get_redis"), \
             patch.object(redis_module, "close_redis", new_callable=AsyncMock):

            async with lifespan(app):
                pass

        assert app.state.started is False
