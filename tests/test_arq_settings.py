"""Testes para arq_settings — configuração Redis do ARQ worker."""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestArqRedisSettings:
    """Testa get_arq_redis_settings."""

    def test_returns_redis_settings(self):
        """Deve retornar um objeto RedisSettings válido."""
        from intensicare.services.arq_settings import get_arq_redis_settings

        with patch("intensicare.services.arq_settings.get_redis_connection_kwargs") as mock_kwargs:
            mock_kwargs.return_value = {
                "host": "localhost",
                "port": 6379,
                "database": 0,
            }
            settings = get_arq_redis_settings()
            assert settings is not None
            assert settings.host == "localhost"  # type: ignore[attr-defined]
            assert settings.port == 6379  # type: ignore[attr-defined]


class TestNotificationDefaults:
    """Testa as constantes de configuração do worker de notificação."""

    def test_queue_name(self):
        from intensicare.services.arq_settings import NOTIFICATION_QUEUE_NAME

        assert NOTIFICATION_QUEUE_NAME == "arq:notification"

    def test_max_tries(self):
        from intensicare.services.arq_settings import NOTIFICATION_MAX_TRIES

        assert NOTIFICATION_MAX_TRIES == 7

    def test_job_timeout(self):
        from intensicare.services.arq_settings import NOTIFICATION_JOB_TIMEOUT

        assert NOTIFICATION_JOB_TIMEOUT == 30

    def test_poll_delay(self):
        from intensicare.services.arq_settings import NOTIFICATION_POLL_DELAY

        assert NOTIFICATION_POLL_DELAY == 0.2

    def test_keep_result(self):
        from intensicare.services.arq_settings import NOTIFICATION_KEEP_RESULT

        assert NOTIFICATION_KEEP_RESULT == 600

    def test_max_tries_exceeds_one(self):
        """Deve ter pelo menos 1 tentativa inicial para permitir retries."""
        from intensicare.services.arq_settings import NOTIFICATION_MAX_TRIES

        assert NOTIFICATION_MAX_TRIES > 1

    def test_poll_delay_positive(self):
        """Poll delay deve ser positivo."""
        from intensicare.services.arq_settings import NOTIFICATION_POLL_DELAY

        assert NOTIFICATION_POLL_DELAY > 0
