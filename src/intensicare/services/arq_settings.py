"""ARQ configuration — Redis connection settings and worker defaults.

Provides:
- get_arq_redis_settings(): build RedisSettings from application config
- get_worker_defaults(): sensible defaults for the notification worker
"""

from arq.connections import RedisSettings

from intensicare.core.redis import get_redis_connection_kwargs


def get_arq_redis_settings() -> RedisSettings:
    """Build ARQ RedisSettings from the application's Redis configuration."""
    kwargs = get_redis_connection_kwargs()
    return RedisSettings(**kwargs)


# ── Notification worker defaults ────────────────────────────────────────────
# These are passed to Worker() and can be overridden per deployment.

NOTIFICATION_QUEUE_NAME = "arq:notification"
NOTIFICATION_MAX_TRIES = 7  # 1 initial + 6 retries (matches BACKOFF_SCHEDULE)
NOTIFICATION_JOB_TIMEOUT = 30  # seconds — each notification attempt
NOTIFICATION_POLL_DELAY = 0.2  # seconds between queue polls
NOTIFICATION_KEEP_RESULT = 600  # seconds to keep job results in Redis
