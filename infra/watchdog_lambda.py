"""
Dead-man's switch watchdog — CloudWatch scheduled Lambda (INV-5).

Deploy as a per-minute CloudWatch Events trigger. This Lambda:
1. Pings /api/v1/health on the Intensicare API.
2. Writes a custom CloudWatch metric ``WatchdogPing`` (value 1 on success, 0 on failure).
3. A CloudWatch Alarm on ``WatchdogPing ≤ 0 for 2 datapoints`` pages ops.

Also emits a staleness metric: ``StalenessMinutes`` per (unit, domain) so a
separate alarm can fire when no scores arrive for > staleness_alert_minutes.

Configuration via environment variables:
- INTENSICARE_HEALTH_URL (default: http://localhost:8000/api/v1/health)
- WATCHDOG_TIMEOUT_SECONDS (default: 30)
- CLOUDWATCH_NAMESPACE  (default: "Intensicare/Watchdog")

Dependencies (Lambda layer or bundled):
- boto3
- requests
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import boto3  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ── Config ───────────────────────────────────────────────────────────────────

HEALTH_URL: str = os.environ.get(
    "INTENSICARE_HEALTH_URL", "http://localhost:8000/api/v1/health"
)
TIMEOUT: int = int(os.environ.get("WATCHDOG_TIMEOUT_SECONDS", "30"))
NAMESPACE: str = os.environ.get("CLOUDWATCH_NAMESPACE", "Intensicare/Watchdog")

cloudwatch = boto3.client("cloudwatch")


# ── Helpers ──────────────────────────────────────────────────────────────────


def _put_metric(name: str, value: float, unit: str = "Count", **dimensions: str) -> None:
    """Publish a single CloudWatch metric datapoint."""
    try:
        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[
                {
                    "MetricName": name,
                    "Value": value,
                    "Unit": unit,
                    "Timestamp": datetime.now(timezone.utc),
                    "Dimensions": [
                        {"Name": k, "Value": v} for k, v in dimensions.items()
                    ],
                }
            ],
        )
    except Exception:
        logger.exception("Failed to publish metric %s", name)


# ── Main handler ─────────────────────────────────────────────────────────────


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:  # noqa: ARG001
    """CloudWatch scheduled Lambda entry point.

    event: CloudWatch Events scheduled event (not used).
    context: Lambda context (not used directly).
    """
    import requests  # noqa: PLC0415  # deferred import; may be bundled or in layer

    overall_success = False
    checks_detail: dict[str, str] = {}
    staleness_metrics: list[dict[str, Any]] = []

    try:
        t0 = time.monotonic()
        resp = requests.get(HEALTH_URL, timeout=TIMEOUT)
        elapsed = (time.monotonic() - t0) * 1000
        resp.raise_for_status()
        body = resp.json()

        # ── Record per-component checks ──────────────────────────────────
        for name, check in body.get("checks", {}).items():
            status = check.get("status", "unknown")
            checks_detail[name] = status
            # Emit OK=1 / Error=0 metric per component
            _put_metric(f"Component_{name}", 1 if status == "ok" else 0, "Count")

        # ── Staleness metrics ────────────────────────────────────────────
        staleness: dict[str, dict[str, dict[str, Any]]] = body.get("staleness", {})
        for unit_name, domains in staleness.items():
            for domain_name, entry in domains.items():
                minutes = entry.get("minutes_stale")
                if minutes is not None:
                    staleness_metrics.append(
                        {
                            "unit": unit_name,
                            "domain": domain_name,
                            "minutes_stale": minutes,
                        }
                    )
                    _put_metric(
                        "StalenessMinutes",
                        float(minutes),
                        "Seconds",
                        Unit=unit_name,
                        Domain=domain_name,
                    )

        # ── Overall status ───────────────────────────────────────────────
        status = body.get("status", "unknown")
        overall_success = status in ("healthy", "degraded")

        logger.info(
            "Watchdog ping OK: status=%s elapsed=%.0fms checks=%s staleness=%s",
            status,
            elapsed,
            checks_detail,
            staleness_metrics,
        )

    except Exception:
        logger.exception("Watchdog ping FAILED — health endpoint unreachable")
        overall_success = False
        # Emit error metrics for all expected components so alarms fire.
        for comp in ("postgresql", "redis", "arq", "athena"):
            _put_metric(f"Component_{comp}", 0, "Count")

    # ── Global watchdog heartbeat ────────────────────────────────────────
    _put_metric("WatchdogPing", 1 if overall_success else 0, "Count")

    return {
        "statusCode": 200 if overall_success else 500,
        "body": json.dumps(
            {
                "success": overall_success,
                "checks": checks_detail,
                "staleness": staleness_metrics,
            }
        ),
    }
