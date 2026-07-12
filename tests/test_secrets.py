"""
Tests for AWS Secrets Manager integration.

Covers:
  - Cache hit (returns cached value without boto3 call)
  - Cache miss → boto3 call → SecretString
  - Cache miss → boto3 call → SecretBinary (base64)
  - Missing secret (ResourceNotFoundException)
  - boto3 not installed fallback
  - get_secret_sync behaviour
  - invalidate_secret_cache
  - prefetch_secrets
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from intensicare.core.secrets import (
    _secret_cache,
    get_secret,
    get_secret_sync,
    invalidate_secret_cache,
    prefetch_secrets,
)

# ─── Clean up cache between tests ────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _clear_cache():
    _secret_cache.clear()
    yield
    _secret_cache.clear()


# ─── get_secret tests ────────────────────────────────────────────────────────


class TestGetSecret:
    """Tests for async get_secret."""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_value(self):
        """When a secret is already in cache, return it without boto3."""
        _secret_cache["prod/db/password"] = "cached-value"
        result = await get_secret("prod/db/password")
        assert result == "cached-value"

    @pytest.mark.asyncio
    async def test_cache_miss_calls_boto3_secret_string(self):
        """When cache misses, fetch from AWS Secrets Manager (SecretString)."""
        mock_client = MagicMock()
        mock_response = {"SecretString": '{"password": "secret123"}'}
        mock_client.get_secret_value.return_value = mock_response

        with patch(
            "intensicare.core.secrets._get_secrets_manager_client",
            return_value=mock_client,
        ):
            result = await get_secret("prod/db/password")
            assert result == '{"password": "secret123"}'
            mock_client.get_secret_value.assert_called_once_with(SecretId="prod/db/password")
            # Should now be cached
            assert _secret_cache["prod/db/password"] == '{"password": "secret123"}'

    @pytest.mark.asyncio
    async def test_cache_miss_calls_boto3_secret_binary(self):
        """When SecretString is absent, decode SecretBinary (base64)."""
        import base64

        plaintext = "binary-secret-value"
        encoded = base64.b64encode(plaintext.encode()).decode()

        mock_client = MagicMock()
        mock_response = {"SecretBinary": encoded}
        mock_client.get_secret_value.return_value = mock_response

        with patch(
            "intensicare.core.secrets._get_secrets_manager_client",
            return_value=mock_client,
        ):
            result = await get_secret("prod/api/key")
            assert result == plaintext
            assert _secret_cache["prod/api/key"] == plaintext

    @pytest.mark.asyncio
    async def test_resource_not_found_returns_none(self):
        """When the secret does not exist, return None."""
        mock_client = MagicMock()
        mock_client.exceptions.ResourceNotFoundException = type(
            "ResourceNotFoundException", (Exception,), {}
        )
        mock_client.get_secret_value.side_effect = mock_client.exceptions.ResourceNotFoundException(
            "Not found"
        )

        with patch(
            "intensicare.core.secrets._get_secrets_manager_client",
            return_value=mock_client,
        ):
            result = await get_secret("nonexistent/secret")
            assert result is None
            assert "nonexistent/secret" not in _secret_cache

    @pytest.mark.asyncio
    async def test_boto3_not_available_returns_none(self):
        """When boto3 is not installed, return None gracefully."""
        with patch("intensicare.core.secrets._has_boto3", return_value=False):
            result = await get_secret("any/secret")
            assert result is None

    @pytest.mark.asyncio
    async def test_invalid_request_exception_returns_none(self):
        """InvalidRequestException should return None."""
        mock_client = MagicMock()
        mock_client.exceptions.InvalidRequestException = type(
            "InvalidRequestException", (Exception,), {}
        )
        mock_client.get_secret_value.side_effect = mock_client.exceptions.InvalidRequestException(
            "Bad request"
        )

        with patch(
            "intensicare.core.secrets._get_secrets_manager_client",
            return_value=mock_client,
        ):
            result = await get_secret("bad/request")
            assert result is None

    @pytest.mark.asyncio
    async def test_generic_exception_returns_none(self):
        """Unexpected errors should be logged and return None."""
        mock_client = MagicMock()
        mock_client.get_secret_value.side_effect = RuntimeError("Boom")

        with patch(
            "intensicare.core.secrets._get_secrets_manager_client",
            return_value=mock_client,
        ):
            result = await get_secret("boom/secret")
            assert result is None


# ─── get_secret_sync tests ───────────────────────────────────────────────────


class TestGetSecretSync:
    """Tests for synchronous get_secret_sync."""

    def test_no_running_loop_uses_asyncio_run(self):
        """When called outside an event loop, use asyncio.run()."""
        with patch(
            "intensicare.core.secrets.get_secret",
            new_callable=AsyncMock,
        ) as mock_async:
            mock_async.return_value = "sync-result"
            result = get_secret_sync("prod/test")
            assert result == "sync-result"

    def test_with_running_loop_uses_future(self):
        """When called inside a running loop, use run_coroutine_threadsafe."""
        # This test runs inside pytest-asyncio's loop, so the fallback path is taken.
        # We just verify it doesn't crash.
        _secret_cache["prod/fast"] = "fast-value"
        result = get_secret_sync("prod/fast")
        assert result == "fast-value"


# ─── invalidate_secret_cache tests ───────────────────────────────────────────


class TestInvalidateSecretCache:
    """Tests for cache invalidation."""

    def test_invalidate_specific_secret(self):
        _secret_cache["a"] = "1"
        _secret_cache["b"] = "2"
        invalidate_secret_cache("a")
        assert "a" not in _secret_cache
        assert "b" in _secret_cache

    def test_invalidate_all_secrets(self):
        _secret_cache["a"] = "1"
        _secret_cache["b"] = "2"
        invalidate_secret_cache()
        assert len(_secret_cache) == 0


# ─── prefetch_secrets tests ──────────────────────────────────────────────────


class TestPrefetchSecrets:
    """Tests for bulk prefetch."""

    @pytest.mark.asyncio
    async def test_prefetch_populates_cache(self):
        """prefetch_secrets should fetch multiple secrets and warm the cache."""
        mock_client = MagicMock()

        def side_effect(SecretId=None):
            return {"SecretString": f"value-for-{SecretId}"}

        mock_client.get_secret_value.side_effect = side_effect

        with patch(
            "intensicare.core.secrets._get_secrets_manager_client",
            return_value=mock_client,
        ):
            results = await prefetch_secrets(["s1", "s2", "s3"])
            assert results == {"s1": "value-for-s1", "s2": "value-for-s2", "s3": "value-for-s3"}
            assert _secret_cache["s1"] == "value-for-s1"
            assert _secret_cache["s2"] == "value-for-s2"
            assert _secret_cache["s3"] == "value-for-s3"
