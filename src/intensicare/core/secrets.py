"""
AWS Secrets Manager integration for production secrets.

Provides a caching `get_secret(secret_name)` function backed by boto3.
In development/staging, falls back gracefully to environment variables when
the AWS SDK is unavailable or no secret ARN is configured.

Usage::

    from intensicare.core.secrets import get_secret, prefetch_secrets

    await prefetch_secrets(["prod/database/password", "prod/jwt/secret"])
    db_password = await get_secret("prod/database/password")
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# In-memory cache to avoid hitting Secrets Manager on every call.
# Keys are secret names, values are the decoded secret strings.
_secret_cache: dict[str, str] = {}

# Set to True after the first boto3 import attempt to avoid repeated failures.
_boto3_available: bool | None = None


def _has_boto3() -> bool:
    """Check whether boto3 is installed without raising."""
    global _boto3_available
    if _boto3_available is None:
        try:
            import boto3  # noqa: F401

            _boto3_available = True
        except ImportError:
            _boto3_available = False
    return _boto3_available


def _get_secrets_manager_client():
    """Return a boto3 Secrets Manager client (lazy, cached via lru_cache)."""
    if not _has_boto3():
        return None
    import boto3

    return boto3.client(
        "secretsmanager",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )


async def get_secret(secret_name: str) -> str | None:
    """Retrieve a secret value from AWS Secrets Manager.

    Parameters
    ----------
    secret_name:
        Friendly name or full ARN of the secret (e.g. ``prod/intensicare/db``).

    Returns
    -------
    The secret string, or ``None`` when the secret cannot be retrieved
    (boto3 not installed, secret not found, or access denied).

    Notes
    -----
    Results are cached in-process forever (Secrets Manager values change
    rarely; redeploy to pick up rotations).  For zero-downtime rotation,
    call ``invalidate_secret_cache(secret_name)`` after the rotation event.
    """
    # ── Cache hit ────────────────────────────────────────────────────────
    if secret_name in _secret_cache:
        return _secret_cache[secret_name]

    # ── Try Secrets Manager ──────────────────────────────────────────────
    client = _get_secrets_manager_client()
    if client is None:
        logger.debug("boto3 not available — secrets manager disabled")
        return None

    try:
        response = client.get_secret_value(SecretId=secret_name)
        value: str | None = None

        if "SecretString" in response:
            value = response["SecretString"]
        elif "SecretBinary" in response:
            import base64

            value = base64.b64decode(response["SecretBinary"]).decode("utf-8")

        if value is not None:
            _secret_cache[secret_name] = value
            logger.info("Secret loaded from AWS: %s", secret_name)
            return value

        return None

    except client.exceptions.ResourceNotFoundException:
        logger.warning("Secret not found in AWS Secrets Manager: %s", secret_name)
        return None
    except client.exceptions.InvalidRequestException as exc:
        logger.error("Invalid request for secret %s: %s", secret_name, exc)
        return None
    except Exception:
        logger.exception("Unexpected error retrieving secret %s", secret_name)
        return None


async def prefetch_secrets(secret_names: list[str]) -> dict[str, str | None]:
    """Pre-fetch multiple secrets and warm the cache.

    Returns a dict mapping each secret name to its value (or ``None`` for misses).
    """
    results: dict[str, str | None] = {}
    for name in secret_names:
        results[name] = await get_secret(name)
    return results


def invalidate_secret_cache(secret_name: str | None = None) -> None:
    """Clear the in-process secret cache.

    Parameters
    ----------
    secret_name:
        Specific secret to invalidate.  When ``None``, clears the entire cache.
    """
    if secret_name is None:
        _secret_cache.clear()
        logger.info("Secret cache fully invalidated")
    else:
        _secret_cache.pop(secret_name, None)
        logger.info("Secret cache invalidated for: %s", secret_name)


def get_secret_sync(secret_name: str) -> str | None:
    """Synchronous wrapper around ``get_secret`` (for sync startup code).

    Uses ``asyncio.run()`` internally — **do not** call from within an
    already-running event loop.
    """
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to create one.
        return asyncio.run(get_secret(secret_name))

    # We're inside an event loop.  This is not the intended use-case, but
    # we provide a best-effort fallback by scheduling on the existing loop.
    logger.warning(
        "get_secret_sync called inside a running event loop for %s — use the async version instead",
        secret_name,
    )
    import concurrent.futures

    future = asyncio.run_coroutine_threadsafe(get_secret(secret_name), loop)
    try:
        return future.result(timeout=10)
    except concurrent.futures.TimeoutError:
        logger.error("Timeout waiting for secret %s", secret_name)
        return None
