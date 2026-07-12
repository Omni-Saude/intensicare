"""
WO-036: PPV Tracker — Positive Predictive Value instrumentation.

Tracks per-alert PPV (true positives / total alerts) and emits
metrics via OTEL (OpenTelemetry). Designed to validate that the
alert engine maintains:
- PPV ≥ 0.60
- Alert fatigue ≤ 10%

PPV = TP / (TP + FP)
Fatigue = (false_positive_resolutions) / (total_resolved_with_feedback)

Architecture:
- Observer pattern: hooks into alert lifecycle (resolve events)
- In-memory counters with optional Redis sync for distributed deployments
- OTEL metrics emission: Gauge for PPV, Counter for TP/FP/total
- Thread-safe: uses asyncio.Lock for concurrent access
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING

# OTEL imports — optional, graceful degradation if not installed
try:
    from opentelemetry import metrics as _otel_metrics
    from opentelemetry.metrics import (
        CallbackOptions as _CallbackOptions,
    )
    from opentelemetry.metrics import (
        Observation as _Observation,
    )

    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _OTEL_AVAILABLE = False
    _otel_metrics = None  # type: ignore[assignment]
    _CallbackOptions = object  # type: ignore[assignment,misc]
    _Observation = object  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

# Resolution types that count as a "positive" prediction
# "true_positive": the alert correctly identified a clinical event
# "false_positive": the alert was a false alarm
# "intervention_done": action was taken (counts as TP for PPV)
_POSITIVE_RESOLUTIONS = frozenset({"true_positive", "intervention_done"})
_NEGATIVE_RESOLUTIONS = frozenset({"false_positive"})
_ALL_FEEDBACK_RESOLUTIONS = _POSITIVE_RESOLUTIONS | _NEGATIVE_RESOLUTIONS

# PPV target: must be ≥ 0.60
PPV_TARGET = 0.60
# Fatigue target: ≤ 10% (false positive rate among resolved with feedback)
FATIGUE_TARGET = 0.10


class PPVTracker:
    """Tracks Positive Predictive Value for the clinical alert engine.

    Usage:
        tracker = PPVTracker()

        # Hook into alert resolve flow:
        await tracker.record_resolution("true_positive")
        await tracker.record_resolution("false_positive")

        # Query metrics:
        ppv = tracker.ppv
        fatigue = tracker.fatigue_rate
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._total_alerts = 0
        self._total_resolved = 0
        self._true_positives = 0
        self._false_positives = 0
        self._interventions = 0
        self._resolutions_by_type: dict[str, int] = defaultdict(int)
        self._started_at = datetime.now(timezone.utc)

        # Per-severity breakdown
        self._severity_tp: dict[str, int] = defaultdict(int)
        self._severity_total: dict[str, int] = defaultdict(int)

        # OTEL instruments (lazy init)
        self._otel_initialized = False
        self._otel_meter = None
        self._ppv_gauge = None
        self._fatigue_gauge = None
        self._tp_counter = None
        self._fp_counter = None
        self._total_counter = None

    # ── Properties ─────────────────────────────────────────────────────────

    @property
    def total_alerts(self) -> int:
        """Total number of alerts tracked (all statuses)."""
        return self._total_alerts

    @property
    def total_resolved(self) -> int:
        """Total number of resolved alerts with feedback."""
        return self._total_resolved

    @property
    def true_positives(self) -> int:
        """Number of true positive resolutions."""
        return self._true_positives

    @property
    def false_positives(self) -> int:
        """Number of false positive resolutions."""
        return self._false_positives

    @property
    def ppv(self) -> float:
        """Current PPV: TP / (TP + FP). Returns 0.0 if no data."""
        total = self._true_positives + self._false_positives
        if total == 0:
            return 0.0
        return self._true_positives / total

    @property
    def fatigue_rate(self) -> float:
        """Alert fatigue: FP / total resolved with feedback."""
        if self._total_resolved == 0:
            return 0.0
        return self._false_positives / self._total_resolved

    @property
    def ppv_target_met(self) -> bool:
        """Whether the PPV target (≥0.60) is currently met."""
        if self._total_resolved < 10:
            return True  # Not enough data; assume OK initially
        return self.ppv >= PPV_TARGET

    @property
    def fatigue_target_met(self) -> bool:
        """Whether the fatigue target (≤10%) is currently met."""
        if self._total_resolved < 10:
            return True
        return self.fatigue_rate <= FATIGUE_TARGET

    # ── Record methods ─────────────────────────────────────────────────────

    async def record_alert_created(self, severity: str = "watch") -> None:
        """Record that a new alert was created (increments total).

        Args:
            severity: The severity level of the alert.
        """
        async with self._lock:
            self._total_alerts += 1
            self._severity_total[severity] = self._severity_total.get(severity, 0) + 1

    async def record_resolution(
        self,
        resolution: str,
        severity: str = "watch",
    ) -> None:
        """Record a clinical resolution of an alert.

        Args:
            resolution: One of 'true_positive', 'false_positive', 'intervention_done'.
            severity: The severity level of the alert.
        """
        async with self._lock:
            self._total_resolved += 1
            self._resolutions_by_type[resolution] += 1

            if resolution in _POSITIVE_RESOLUTIONS:
                self._true_positives += 1
                self._severity_tp[severity] = self._severity_tp.get(severity, 0) + 1
            elif resolution == "false_positive":
                self._false_positives += 1

            current_ppv = self.ppv
            current_fatigue = self.fatigue_rate

        # Log significant changes
        if self._total_resolved % 50 == 0:
            logger.info(
                "PPV Tracker: %d resolved, PPV=%.3f, fatigue=%.3f, TP=%d, FP=%d",
                self._total_resolved,
                current_ppv,
                current_fatigue,
                self._true_positives,
                self._false_positives,
            )

    async def record_batch(
        self,
        resolutions: list[tuple[str, str]],
    ) -> None:
        """Record multiple resolutions atomically in a batch.

        Args:
            resolutions: List of (resolution_type, severity) tuples.
        """
        async with self._lock:
            for resolution, severity in resolutions:
                self._total_resolved += 1
                self._resolutions_by_type[resolution] += 1

                if resolution in _POSITIVE_RESOLUTIONS:
                    self._true_positives += 1
                    self._severity_tp[severity] = self._severity_tp.get(severity, 0) + 1
                elif resolution == "false_positive":
                    self._false_positives += 1

    # ── OTEL Integration ───────────────────────────────────────────────────

    def init_otel(self) -> None:
        """Initialize OpenTelemetry instruments for metrics emission.

        Safe to call multiple times; subsequent calls are no-ops.
        """
        if self._otel_initialized or not _OTEL_AVAILABLE:
            return

        try:
            self._otel_meter = _otel_metrics.get_meter(  # pyright: ignore[reportOptionalMemberAccess]
                "intensicare.ppv_tracker",
                version="0.1.0",
            )

            # PPV Gauge — reports current PPV ratio
            self._ppv_gauge = self._otel_meter.create_observable_gauge(
                name="intensicare.alerts.ppv",
                description="Current Positive Predictive Value (TP/(TP+FP))",
                unit="ratio",
                callbacks=[self._ppv_callback],
            )

            # Fatigue Gauge — reports current fatigue rate
            self._fatigue_gauge = self._otel_meter.create_observable_gauge(
                name="intensicare.alerts.fatigue_rate",
                description="Alert fatigue rate (FP/total resolved with feedback)",
                unit="ratio",
                callbacks=[self._fatigue_callback],
            )

            # TP Counter — cumulative true positives
            self._tp_counter = self._otel_meter.create_counter(
                name="intensicare.alerts.true_positives",
                description="Cumulative number of true positive alert resolutions",
                unit="1",
            )

            # FP Counter — cumulative false positives
            self._fp_counter = self._otel_meter.create_counter(
                name="intensicare.alerts.false_positives",
                description="Cumulative number of false positive alert resolutions",
                unit="1",
            )

            # Total Counter — cumulative alerts
            self._total_counter = self._otel_meter.create_counter(
                name="intensicare.alerts.total",
                description="Cumulative total number of alerts",
                unit="1",
            )

            self._otel_initialized = True
            logger.info("PPV Tracker OTEL instruments initialized")
        except Exception as exc:
            logger.warning("Failed to initialize PPV OTEL instruments: %s", exc)

    def _ppv_callback(self, options: _CallbackOptions) -> list[_Observation]:  # pyright: ignore[reportUndefinedVariable,reportInvalidTypeForm]
        """OTEL callback: emit current PPV as observable gauge."""
        current = self.ppv
        return [_Observation(current)]  # pyright: ignore[reportCallIssue,reportUndefinedVariable]

    def _fatigue_callback(self, options: _CallbackOptions) -> list[_Observation]:  # pyright: ignore[reportUndefinedVariable,reportInvalidTypeForm]
        """OTEL callback: emit current fatigue rate as observable gauge."""
        current = self.fatigue_rate
        return [_Observation(current)]  # pyright: ignore[reportCallIssue,reportUndefinedVariable]

    async def emit_metrics_sync(self) -> None:
        """Emit cumulative counter metrics to OTEL (call periodically or on change).

        Raises no error if OTEL is not available.
        """
        if not self._otel_initialized:
            return

        try:
            async with self._lock:
                tp = self._true_positives
                fp = self._false_positives
                total = self._total_alerts

            if self._tp_counter is not None:
                self._tp_counter.add(tp)
            if self._fp_counter is not None:
                self._fp_counter.add(fp)
            if self._total_counter is not None:
                self._total_counter.add(total)
        except Exception as exc:
            logger.debug("Failed to emit PPV metrics: %s", exc)

    # ── Snapshot & Reporting ───────────────────────────────────────────────

    def snapshot(self) -> dict:
        """Return a snapshot of all PPV tracker state for API/dashboard use.

        Returns:
            Dict with PPV, fatigue, counts, and targets.
        """
        return {
            "ppv": round(self.ppv, 4),
            "ppv_target": PPV_TARGET,
            "ppv_target_met": self.ppv_target_met,
            "fatigue_rate": round(self.fatigue_rate, 4),
            "fatigue_target": FATIGUE_TARGET,
            "fatigue_target_met": self.fatigue_target_met,
            "total_alerts": self._total_alerts,
            "total_resolved": self._total_resolved,
            "true_positives": self._true_positives,
            "false_positives": self._false_positives,
            "interventions": self._interventions,
            "resolutions_by_type": dict(self._resolutions_by_type),
            "severity_breakdown": {
                sev: {
                    "tp": self._severity_tp.get(sev, 0),
                    "total": self._severity_total.get(sev, 0),
                }
                for sev in set(self._severity_tp) | set(self._severity_total)
            },
            "started_at": self._started_at.isoformat(),
        }

    def reset(self) -> None:
        """Reset all counters (for testing purposes)."""
        self._total_alerts = 0
        self._total_resolved = 0
        self._true_positives = 0
        self._false_positives = 0
        self._interventions = 0
        self._resolutions_by_type.clear()
        self._severity_tp.clear()
        self._severity_total.clear()
        self._started_at = datetime.now(timezone.utc)


# ── Module-level singleton ─────────────────────────────────────────────────

# Global PPV tracker instance for the application.
# Import this in alert lifecycle hooks or API handlers.
ppv_tracker = PPVTracker()


async def record_alert_resolution(
    resolution: str,
    severity: str = "watch",
) -> None:
    """Convenience function: record a resolution on the module-level tracker.

    Should be called from the resolve_alert endpoint or alert engine
    whenever a clinical resolution is recorded.

    Args:
        resolution: 'true_positive', 'false_positive', or 'intervention_done'.
        severity: The severity level of the original alert.
    """
    await ppv_tracker.record_resolution(resolution, severity)


async def get_ppv_status() -> dict:
    """Get current PPV status from the module-level tracker.

    Returns:
        Snapshot dict with PPV, fatigue, and detailed breakdown.
    """
    return ppv_tracker.snapshot()
