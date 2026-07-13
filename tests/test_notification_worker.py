"""Tests for the notification worker — retry, DLQ, dedup.

Covers:
- DRILL-NOTIFICATION-BLACKHOLE: retries exhausted → DLQ + operational alert
- Exponential backoff timing (Retry.defer matches BACKOFF_SCHEDULE)
- Client-side deduplication on dedup_key
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

from arq.worker import Retry
import pytest

from intensicare.services.notification_worker import (
    BACKOFF_SCHEDULE,
    DLQ_ALERT_CHANNEL,
    DLQ_KEY,
    MAX_RETRIES,
    _check_dedup,
    _move_to_dlq,
    send_alert_notification,
)

# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _make_ctx(
    redis_client: object,
    *,
    job_id: str = "test-job-001",
    job_try: int = 1,
) -> dict[str, object]:
    """Build an ARQ worker context dict for direct job-function calls."""
    return {
        "redis": redis_client,
        "job_id": job_id,
        "job_try": job_try,
        "enqueue_time": None,
        "score": 0,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Deduplication tests (uses real Redis via conftest fixtures)
# ═══════════════════════════════════════════════════════════════════════════


class TestDedup:
    """Client-side deduplication on ``dedup_key``."""

    @pytest.mark.asyncio
    async def test_first_call_proceeds(self):
        """First call with a dedup_key should NOT be suppressed."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()
        ctx = _make_ctx(redis_client, job_id="dedup-test-1")

        with patch(
            "intensicare.services.notification_worker._dispatch_notification",
            new_callable=AsyncMock,
        ):
            result = await send_alert_notification(
                ctx,
                alert_id="alert-001",
                channels=["ws"],
                dedup_key="key-abc",
            )

        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_second_call_is_duplicate(self):
        """Second call with the same dedup_key should be suppressed."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()
        dedup_key = "key-dup-test"

        # First call — should proceed
        ctx1 = _make_ctx(redis_client, job_id="dedup-test-2a")
        with patch(
            "intensicare.services.notification_worker._dispatch_notification",
            new_callable=AsyncMock,
        ):
            result1 = await send_alert_notification(
                ctx1, alert_id="alert-001", channels=["ws"], dedup_key=dedup_key
            )

        assert result1["status"] == "sent"

        # Second call — should be deduplicated
        ctx2 = _make_ctx(redis_client, job_id="dedup-test-2b")
        result2 = await send_alert_notification(
            ctx2, alert_id="alert-001", channels=["ws"], dedup_key=dedup_key
        )

        assert result2["status"] == "deduplicated"
        assert result2["dedup_key"] == dedup_key

    @pytest.mark.asyncio
    async def test_no_dedup_key_passes_through(self):
        """Without a dedup_key, every call should proceed normally."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()

        ctx1 = _make_ctx(redis_client, job_id="nodup-1")
        ctx2 = _make_ctx(redis_client, job_id="nodup-2")

        with patch(
            "intensicare.services.notification_worker._dispatch_notification",
            new_callable=AsyncMock,
        ):
            r1 = await send_alert_notification(ctx1, alert_id="alert-001", channels=["ws"])
            r2 = await send_alert_notification(ctx2, alert_id="alert-001", channels=["ws"])

        assert r1["status"] == "sent"
        assert r2["status"] == "sent"

    @pytest.mark.asyncio
    async def test_check_dedup_helper_atomic(self):
        """_check_dedup should be atomic: first call sets, second finds it."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()
        key = "atomic-key"

        is_dup_1 = await _check_dedup(redis_client, key, "job-1")
        assert is_dup_1 is False  # first occurrence

        is_dup_2 = await _check_dedup(redis_client, key, "job-2")
        assert is_dup_2 is True  # duplicate


# ═══════════════════════════════════════════════════════════════════════════
# Retry / exponential backoff tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRetryBackoff:
    """Exponential backoff: each retry matches BACKOFF_SCHEDULE."""

    @pytest.mark.asyncio
    async def test_raises_retry_with_correct_defer(self):
        """On failure, the job should raise Retry with the correct backoff delay."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()

        for try_idx, expected_delay in enumerate(BACKOFF_SCHEDULE, start=1):
            ctx = _make_ctx(redis_client, job_id=f"retry-test-{try_idx}", job_try=try_idx)

            with (
                patch(
                    "intensicare.services.notification_worker._dispatch_notification",
                    side_effect=ConnectionError("simulated failure"),
                ),
                pytest.raises(Retry) as exc_info,
            ):
                await send_alert_notification(ctx, alert_id="alert-retry", channels=["ws"])

            assert exc_info.value.defer_score == expected_delay * 1000, (
                f"job_try={try_idx}: expected defer={expected_delay}s, "
                f"got {exc_info.value.defer_score}ms"
            )

    @pytest.mark.asyncio
    async def test_backoff_schedule_length(self):
        """BACKOFF_SCHEDULE should have exactly MAX_RETRIES entries."""
        assert len(BACKOFF_SCHEDULE) == MAX_RETRIES
        # Verify exponential growth: each entry is 2× the previous
        for i in range(1, len(BACKOFF_SCHEDULE)):
            assert BACKOFF_SCHEDULE[i] == BACKOFF_SCHEDULE[i - 1] * 2


# ═══════════════════════════════════════════════════════════════════════════
# Dead-letter queue (DLQ) tests — DRILL-NOTIFICATION-BLACKHOLE
# ═══════════════════════════════════════════════════════════════════════════


class TestDeadLetterQueue:
    """DRILL-NOTIFICATION-BLACKHOLE: when retries are exhausted → DLQ."""

    @pytest.mark.asyncio
    async def test_exhausted_retries_moves_to_dlq(self):
        """After MAX_RETRIES attempts, job goes to dead-letter queue."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()
        exhausted_try = MAX_RETRIES + 1
        ctx = _make_ctx(redis_client, job_id="dlq-test-001", job_try=exhausted_try)

        with patch(
            "intensicare.services.notification_worker._dispatch_notification",
            side_effect=RuntimeError("channel unreachable"),
        ):
            result = await send_alert_notification(
                ctx,
                alert_id="alert-dlq",
                channels=["sms"],
                dedup_key="dlq-dedup",
            )

        # ── Assertions ──────────────────────────────────────────────────
        assert result["status"] == "dead_letter"
        assert result["alert_id"] == "alert-dlq"
        assert result["try"] == exhausted_try
        assert "RuntimeError" in result["error"]

        # DLQ entry should exist in Redis list
        dlq_items = await redis_client.lrange(DLQ_KEY, 0, -1)
        assert len(dlq_items) >= 1, "DLQ list should contain at least one entry"

        dlq_entry = json.loads(dlq_items[-1])
        assert dlq_entry["alert_id"] == "alert-dlq"
        assert dlq_entry["channels"] == ["sms"]
        assert dlq_entry["dedup_key"] == "dlq-dedup"
        assert dlq_entry["max_retries"] == MAX_RETRIES
        assert "RuntimeError" in dlq_entry["error"]
        assert "exhausted_at" in dlq_entry

    @pytest.mark.asyncio
    async def test_dlq_publishes_operational_alert(self):
        """Moving to DLQ should publish on the operational-alert channel."""
        import redis.asyncio as aioredis

        from intensicare.config import settings

        # We need a separate subscriber connection because the pub/sub
        # model requires a dedicated connection for listening.
        sub = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        pubsub = sub.pubsub()
        await pubsub.subscribe(DLQ_ALERT_CHANNEL)

        # Give Redis a moment to register the subscription
        import asyncio

        await asyncio.sleep(0.05)

        try:
            from intensicare.core.redis import get_redis

            redis_client = get_redis()
            exhausted_try = MAX_RETRIES + 1
            ctx = _make_ctx(redis_client, job_id="dlq-pub-001", job_try=exhausted_try)

            with patch(
                "intensicare.services.notification_worker._dispatch_notification",
                side_effect=RuntimeError("channel unreachable"),
            ):
                await send_alert_notification(
                    ctx,
                    alert_id="alert-dlq-pub",
                    channels=["ws", "sms"],
                )

            # Read the published message (non-blocking with short timeout)
            await pubsub.get_message(timeout=2.0)
            # The first message is the subscription confirmation; the second
            # is the actual publish.
            messages: list[dict[str, object]] = []
            while True:
                msg = await pubsub.get_message(timeout=0.5)
                if msg is None:
                    break
                messages.append(msg)

            # Find the actual data message (type == "message")
            data_messages = [m for m in messages if m.get("type") == "message"]
            assert len(data_messages) >= 1, (
                f"Expected at least one pub/sub message on {DLQ_ALERT_CHANNEL}, got {messages}"
            )

            payload = json.loads(str(data_messages[0]["data"]))
            assert payload["alert_id"] == "alert-dlq-pub"
        finally:
            await pubsub.unsubscribe(DLQ_ALERT_CHANNEL)
            await pubsub.aclose()
            await sub.aclose()

    @pytest.mark.asyncio
    async def test_move_to_dlq_helper(self):
        """Unit test for _move_to_dlq helper."""
        mock_redis = AsyncMock()
        mock_redis.rpush = AsyncMock()
        mock_redis.publish = AsyncMock()

        await _move_to_dlq(
            mock_redis,
            alert_id="alert-helper",
            channels=["ws"],
            dedup_key="key-helper",
            error="TestError: boom",
        )

        # Assert rpush was called with DLQ_KEY and a JSON entry
        mock_redis.rpush.assert_called_once()
        call_args = mock_redis.rpush.call_args
        assert call_args[0][0] == DLQ_KEY
        entry = json.loads(call_args[0][1])
        assert entry["alert_id"] == "alert-helper"
        assert entry["error"] == "TestError: boom"

        # Assert publish was called for operational alert
        mock_redis.publish.assert_called_once()
        pub_args = mock_redis.publish.call_args
        assert pub_args[0][0] == DLQ_ALERT_CHANNEL


# ═══════════════════════════════════════════════════════════════════════════
# Integration: full happy-path
# ═══════════════════════════════════════════════════════════════════════════


class TestHappyPath:
    """Notification succeeds on first try."""

    @pytest.mark.asyncio
    async def test_successful_notification(self):
        """A successful dispatch returns status=sent with metadata."""
        from intensicare.core.redis import get_redis

        redis_client = get_redis()
        ctx = _make_ctx(redis_client, job_id="happy-001", job_try=1)

        with patch(
            "intensicare.services.notification_worker._dispatch_notification",
            new_callable=AsyncMock,
        ) as mock_dispatch:
            result = await send_alert_notification(
                ctx,
                alert_id="alert-happy",
                channels=["ws", "mobile"],
            )

        assert result["status"] == "sent"
        assert result["alert_id"] == "alert-happy"
        assert result["channels"] == ["ws", "mobile"]
        assert result["try"] == 1
        mock_dispatch.assert_called_once_with("alert-happy", ["ws", "mobile"])
