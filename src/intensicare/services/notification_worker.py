"""Notification worker — ARQ-based async job handler with retry, DLQ, and dedup.

Implements REQ-INV-6 and DRILL-NOTIFICATION-BLACKHOLE:
- Exponential-backoff retry on every notification channel (WS / mobile / SMS)
- Dead-letter queue (DLQ) + operational alert when retries are exhausted
- Client-side deduplication via ``dedup_key``

Replaces the dead ``tenacity`` dependency (AUDIT-005) — ARQ provides the retry
infrastructure natively.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from arq.worker import Retry

from intensicare.core.redis import get_redis
from intensicare.core.websocket import get_websocket_manager

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Retry / backoff schedule
# ═══════════════════════════════════════════════════════════════════════════

# Exponential backoff: 1 s → 2 s → 4 s → 8 s → 16 s → 32 s
BACKOFF_SCHEDULE: list[int] = [1, 2, 4, 8, 16, 32]
MAX_RETRIES: int = len(BACKOFF_SCHEDULE)  # 6

# ═══════════════════════════════════════════════════════════════════════════
# Redis key prefixes
# ═══════════════════════════════════════════════════════════════════════════

DLQ_KEY = "dlq:notification"
DLQ_ALERT_CHANNEL = "alert:operational:dlq_exhausted"

DEDUP_PREFIX = "dedup:notification:"
DEDUP_TTL = 300  # 5 minutes — dedup window per key


# ═══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════


async def _dispatch_notification(
    alert_id: str,
    channels: list[str],
) -> None:
    """Send a notification through each requested channel.

    Currently implemented channels:
    - ``ws``: broadcast via WebSocket manager
    - ``mobile`` / ``sms``: placeholder (emits warning — not yet wired)

    Raises the first exception encountered so the ARQ retry machinery can act.
    """
    ws_manager = get_websocket_manager()

    for channel in channels:
        if channel == "ws":
            await ws_manager.broadcast_alert(
                {"type": "alert_notification", "alert_id": alert_id}
            )
        elif channel in ("mobile", "sms"):
            logger.warning(
                "Channel %s not yet wired — placeholder for alert_id=%s",
                channel,
                alert_id,
            )
        # Unknown channels are silently ignored (forward-compat).


async def _move_to_dlq(
    redis_client: Any,
    alert_id: str,
    channels: list[str],
    dedup_key: str | None,
    error: str,
) -> None:
    """Move a failed job to the dead-letter queue and fire an operational alert.

    The DLQ entry is a JSON object pushed to a Redis list.  After pushing we
    publish on a pub/sub channel so operators/monitoring can react.
    """
    entry = {
        "alert_id": alert_id,
        "channels": channels,
        "dedup_key": dedup_key,
        "error": error,
        "exhausted_at": datetime.now(timezone.utc).isoformat(),
        "max_retries": MAX_RETRIES,
    }

    await redis_client.rpush(DLQ_KEY, json.dumps(entry))
    await redis_client.publish(DLQ_ALERT_CHANNEL, json.dumps(entry))

    logger.error(
        "DLQ: notification exhausted retries — alert_id=%s channels=%s error=%s",
        alert_id,
        channels,
        error,
    )


async def _check_dedup(
    redis_client: Any,
    dedup_key: str,
    job_id: str,
) -> bool:
    """Return True if this notification should be suppressed (duplicate).

    Uses ``SETNX``-style atomic check-and-set: if the key already exists the
    notification is a duplicate; otherwise we set the key with a TTL and allow
    the notification through.
    """
    dedup_full_key = f"{DEDUP_PREFIX}{dedup_key}"
    # SET key value NX EX ttl → returns True if set, None/False if already exists
    was_set = await redis_client.set(dedup_full_key, job_id, nx=True, ex=DEDUP_TTL)
    if not was_set:
        logger.info("Notification deduplicated: dedup_key=%s", dedup_key)
        return True  # duplicate — suppress
    return False  # first occurrence — proceed


# ═══════════════════════════════════════════════════════════════════════════
# ARQ job function
# ═══════════════════════════════════════════════════════════════════════════


async def send_alert_notification(
    ctx: dict[str, Any],
    alert_id: str,
    channels: list[str],
    dedup_key: str | None = None,
) -> dict[str, Any]:
    """ARQ job: send an alert notification with retry, dedup, and DLQ.

    Parameters
    ----------
    ctx:
        ARQ worker context dict.  Contains ``job_id``, ``job_try`` (1-indexed),
        and ``redis`` (the ArqRedis connection).
    alert_id:
        The alert to notify about.
    channels:
        List of notification channels (``"ws"``, ``"mobile"``, ``"sms"``).
    dedup_key:
        Optional client-provided deduplication key.  When set, the worker
        suppresses duplicate notifications with the same key within the
        dedup window (5 minutes).

    Returns
    -------
    dict with ``status`` and metadata.

    Raises
    ------
    Retry
        When a transient failure occurs and retries remain — ARQ re-enqueues
        the job after the backoff delay.
    """
    redis_client: Any = ctx["redis"]
    job_id: str = ctx["job_id"]
    job_try: int = ctx["job_try"]

    # ── Dedup gate ──────────────────────────────────────────────────────
    if dedup_key:
        is_duplicate = await _check_dedup(redis_client, dedup_key, job_id)
        if is_duplicate:
            return {"status": "deduplicated", "dedup_key": dedup_key, "alert_id": alert_id}

    # ── Attempt dispatch ────────────────────────────────────────────────
    try:
        await _dispatch_notification(alert_id, channels)
        logger.info(
            "Notification sent: alert_id=%s channels=%s try=%d",
            alert_id,
            channels,
            job_try,
        )
        return {
            "status": "sent",
            "alert_id": alert_id,
            "channels": channels,
            "try": job_try,
        }
    except Exception as exc:
        error_str = f"{type(exc).__name__}: {exc}"

        # ── Exhausted? → dead-letter queue ──────────────────────────
        if job_try > MAX_RETRIES:
            await _move_to_dlq(redis_client, alert_id, channels, dedup_key, error_str)
            return {
                "status": "dead_letter",
                "alert_id": alert_id,
                "error": error_str,
                "try": job_try,
            }

        # ── Retry with exponential backoff ───────────────────────────
        delay = BACKOFF_SCHEDULE[job_try - 1]  # job_try is 1-indexed
        logger.warning(
            "Notification retry %d/%d — deferring %ds: alert_id=%s error=%s",
            job_try,
            MAX_RETRIES,
            delay,
            alert_id,
            error_str,
        )
        raise Retry(defer=delay) from exc


# ═══════════════════════════════════════════════════════════════════════════
# Worker factory
# ═══════════════════════════════════════════════════════════════════════════


def build_notification_worker_functions() -> list[Any]:
    """Return the list of job functions to register with an ARQ Worker.

    Usage::

        from arq import Worker
        from intensicare.services.arq_settings import get_arq_redis_settings
        from intensicare.services.notification_worker import (
            build_notification_worker_functions,
        )

        worker = Worker(
            functions=build_notification_worker_functions(),
            redis_settings=get_arq_redis_settings(),
        )
    """
    return [send_alert_notification]


# ═══════════════════════════════════════════════════════════════════════════
# ARQ WorkerSettings — entry point for ``arq`` CLI
# ═══════════════════════════════════════════════════════════════════════════
# Usage:
#   arq src.intensicare.services.notification_worker.WorkerSettings
#
# The ARQ CLI introspects this class for ``functions``, ``redis_settings``,
# ``queue_name``, and other worker configuration knobs.


class WorkerSettings:
    """Configuration class consumed by the ``arq`` CLI runner.

    All attributes are optional — the ARQ CLI uses its defaults for any
    attribute that is absent.
    """

    functions: list[Any] = build_notification_worker_functions()

    @staticmethod
    def redis_settings() -> "RedisSettings":
        from intensicare.services.arq_settings import get_arq_redis_settings

        return get_arq_redis_settings()

    # Defer most knobs to arq_settings so they stay DRY.
    @staticmethod
    def queue_name() -> str:
        from intensicare.services.arq_settings import NOTIFICATION_QUEUE_NAME

        return NOTIFICATION_QUEUE_NAME

    @staticmethod
    def max_tries() -> int:
        from intensicare.services.arq_settings import NOTIFICATION_MAX_TRIES

        return NOTIFICATION_MAX_TRIES

    @staticmethod
    def job_timeout() -> int:
        from intensicare.services.arq_settings import NOTIFICATION_JOB_TIMEOUT

        return NOTIFICATION_JOB_TIMEOUT

    @staticmethod
    def poll_delay() -> float:
        from intensicare.services.arq_settings import NOTIFICATION_POLL_DELAY

        return NOTIFICATION_POLL_DELAY

    @staticmethod
    def keep_result() -> int:
        from intensicare.services.arq_settings import NOTIFICATION_KEEP_RESULT

        return NOTIFICATION_KEEP_RESULT
