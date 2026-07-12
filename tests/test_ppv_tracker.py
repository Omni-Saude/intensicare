"""
WO-036: Tests for PPV Tracker instrumentation.

Validates:
- PPV calculation: TP/(TP+FP)
- Fatigue calculation: FP/total_resolved
- Target thresholds: PPV ≥ 0.60, fatigue ≤ 10%
- Batch recording
- Snapshot correctness
- Reset behavior
- OTEL integration (mock)
"""

from __future__ import annotations

import asyncio

import pytest

from intensicare.services.ppv_tracker import (
    PPVTracker,
    get_ppv_status,
    ppv_tracker,
    record_alert_resolution,
)


class TestPPVTrackerCore:
    """Core PPV calculation and lifecycle tests."""

    def test_initial_state(self):
        """New tracker should have zero counts and zero PPV."""
        tracker = PPVTracker()
        assert tracker.total_alerts == 0
        assert tracker.total_resolved == 0
        assert tracker.true_positives == 0
        assert tracker.false_positives == 0
        assert tracker.ppv == 0.0
        assert tracker.fatigue_rate == 0.0

    def test_ppv_target_met_initially_true(self):
        """With no data (<10 resolutions), target should be met by default."""
        tracker = PPVTracker()
        assert tracker.ppv_target_met is True
        assert tracker.fatigue_target_met is True

    @pytest.mark.asyncio
    async def test_single_true_positive(self):
        """One TP should give PPV = 1.0."""
        tracker = PPVTracker()
        await tracker.record_resolution("true_positive", "watch")
        assert tracker.total_resolved == 1
        assert tracker.true_positives == 1
        assert tracker.false_positives == 0
        assert tracker.ppv == 1.0
        assert tracker.fatigue_rate == 0.0

    @pytest.mark.asyncio
    async def test_single_false_positive(self):
        """One FP should give PPV = 0.0, fatigue = 1.0."""
        tracker = PPVTracker()
        await tracker.record_resolution("false_positive", "critical")
        assert tracker.total_resolved == 1
        assert tracker.true_positives == 0
        assert tracker.false_positives == 1
        assert tracker.ppv == 0.0
        assert tracker.fatigue_rate == 1.0

    @pytest.mark.asyncio
    async def test_mixed_resolutions(self):
        """8 TP, 2 FP → PPV = 0.8, fatigue = 0.2."""
        tracker = PPVTracker()
        for _ in range(8):
            await tracker.record_resolution("true_positive", "watch")
        for _ in range(2):
            await tracker.record_resolution("false_positive", "watch")
        assert tracker.total_resolved == 10
        assert tracker.ppv == 0.8
        assert tracker.fatigue_rate == 0.2

    @pytest.mark.asyncio
    async def test_intervention_counts_as_tp(self):
        """Intervention_done should count towards TP."""
        tracker = PPVTracker()
        await tracker.record_resolution("intervention_done", "critical")
        await tracker.record_resolution("true_positive", "urgent")
        await tracker.record_resolution("false_positive", "watch")
        # TP = 2 (1 intervention + 1 tp), FP = 1
        assert tracker.true_positives == 2
        assert tracker.false_positives == 1
        assert tracker.ppv == 2 / 3

    @pytest.mark.asyncio
    async def test_ppv_target_60(self):
        """PPV exactly at 0.60 should pass the target."""
        tracker = PPVTracker()
        for _ in range(6):
            await tracker.record_resolution("true_positive", "watch")
        for _ in range(4):
            await tracker.record_resolution("false_positive", "watch")
        # 6/10 = 0.60
        assert tracker.ppv == 0.60
        assert tracker.ppv_target_met is True

    @pytest.mark.asyncio
    async def test_ppv_target_below_60(self):
        """PPV below 0.60 should fail the target when enough data."""
        tracker = PPVTracker()
        for _ in range(5):
            await tracker.record_resolution("true_positive", "watch")
        for _ in range(5):
            await tracker.record_resolution("false_positive", "watch")
        # 5/10 = 0.50 < 0.60
        assert tracker.ppv == 0.50
        assert tracker.ppv_target_met is False

    @pytest.mark.asyncio
    async def test_fatigue_target_10(self):
        """Fatigue at exactly 10% should pass."""
        tracker = PPVTracker()
        for _ in range(9):
            await tracker.record_resolution("true_positive", "watch")
        await tracker.record_resolution("false_positive", "watch")
        # 1/10 = 0.10
        assert tracker.fatigue_rate == 0.10
        assert tracker.fatigue_target_met is True

    @pytest.mark.asyncio
    async def test_fatigue_above_10(self):
        """Fatigue above 10% should fail."""
        tracker = PPVTracker()
        for _ in range(8):
            await tracker.record_resolution("true_positive", "watch")
        for _ in range(2):
            await tracker.record_resolution("false_positive", "watch")
        # 2/10 = 0.20 > 0.10
        assert tracker.fatigue_rate == 0.20
        assert tracker.fatigue_target_met is False


class TestPPVTrackerBatch:
    """Batch recording and concurrency tests."""

    @pytest.mark.asyncio
    async def test_batch_recording(self):
        """Batch should atomically record multiple resolutions."""
        tracker = PPVTracker()
        resolutions = [
            ("true_positive", "watch"),
            ("false_positive", "urgent"),
            ("true_positive", "critical"),
            ("intervention_done", "watch"),
            ("false_positive", "normal"),
        ]
        await tracker.record_batch(resolutions)
        assert tracker.total_resolved == 5
        assert tracker.true_positives == 3  # 2 TP + 1 intervention
        assert tracker.false_positives == 2
        assert tracker.ppv == 3 / 5

    @pytest.mark.asyncio
    async def test_concurrent_recording(self):
        """Concurrent resolves should not corrupt state (lock safety)."""
        tracker = PPVTracker()
        n_per_worker = 50

        async def worker():
            for i in range(n_per_worker):
                if i % 3 == 0:
                    await tracker.record_resolution("false_positive", "watch")
                else:
                    await tracker.record_resolution("true_positive", "watch")

        # 4 concurrent workers
        await asyncio.gather(*[worker() for _ in range(4)])

        total = n_per_worker * 4
        expected_fp = (n_per_worker // 3 + (1 if n_per_worker % 3 > 0 else 0)) * 4
        # Actually: i % 3 == 0 for i=0,3,6,... so exactly ceil(50/3)=17 × 4 = 68

        # Recalculate precisely
        fp_per_worker = sum(1 for i in range(n_per_worker) if i % 3 == 0)
        expected_fp = fp_per_worker * 4  # 17 × 4 = 68
        expected_tp = total - expected_fp  # 200 - 68 = 132

        assert tracker.total_resolved == total
        assert tracker.true_positives == expected_tp
        assert tracker.false_positives == expected_fp


class TestPPVTrackerSnapshot:
    """Snapshot and reporting tests."""

    @pytest.mark.asyncio
    async def test_snapshot_structure(self):
        """Snapshot should contain all required fields."""
        tracker = PPVTracker()
        await tracker.record_resolution("true_positive", "watch")
        await tracker.record_resolution("false_positive", "critical")

        snap = tracker.snapshot()
        assert "ppv" in snap
        assert "fatigue_rate" in snap
        assert "ppv_target" in snap
        assert "ppv_target_met" in snap
        assert "fatigue_target" in snap
        assert "fatigue_target_met" in snap
        assert "total_alerts" in snap
        assert "total_resolved" in snap
        assert "true_positives" in snap
        assert "false_positives" in snap
        assert "resolutions_by_type" in snap
        assert "severity_breakdown" in snap
        assert "started_at" in snap

    @pytest.mark.asyncio
    async def test_snapshot_severity_breakdown(self):
        """Severity breakdown tracks per-severity TP from resolutions."""
        tracker = PPVTracker()
        # Record alert creations to populate severity_total
        await tracker.record_alert_created("critical")
        await tracker.record_alert_created("urgent")
        await tracker.record_alert_created("watch")
        await tracker.record_alert_created("critical")

        # Record resolutions
        await tracker.record_resolution("true_positive", "critical")
        await tracker.record_resolution("true_positive", "urgent")
        await tracker.record_resolution("false_positive", "watch")
        await tracker.record_resolution("true_positive", "critical")

        snap = tracker.snapshot()
        breakdown = snap["severity_breakdown"]

        assert "critical" in breakdown
        assert breakdown["critical"]["tp"] == 2
        assert breakdown["critical"]["total"] == 2
        assert "urgent" in breakdown
        assert breakdown["urgent"]["tp"] == 1
        assert "watch" in breakdown
        assert breakdown["watch"]["tp"] == 0
        assert breakdown["watch"]["total"] == 1

    def test_reset_clears_all(self):
        """Reset should return tracker to initial state."""
        tracker = PPVTracker()
        tracker._total_alerts = 100
        tracker._total_resolved = 50
        tracker._true_positives = 30
        tracker._false_positives = 20

        tracker.reset()

        assert tracker.total_alerts == 0
        assert tracker.total_resolved == 0
        assert tracker.true_positives == 0
        assert tracker.false_positives == 0
        assert tracker.ppv == 0.0
        assert tracker.fatigue_rate == 0.0


class TestPPVTrackerAlertCreation:
    """Alert creation tracking tests."""

    @pytest.mark.asyncio
    async def test_record_alert_created(self):
        """Recording alert creation should increment total_alerts."""
        tracker = PPVTracker()
        await tracker.record_alert_created("critical")
        await tracker.record_alert_created("watch")
        await tracker.record_alert_created("watch")
        assert tracker.total_alerts == 3

        snap = tracker.snapshot()
        breakdown = snap["severity_breakdown"]
        assert breakdown.get("critical", {}).get("total", 0) == 1
        assert breakdown.get("watch", {}).get("total", 0) == 2


class TestModuleLevelSingleton:
    """Tests for the module-level ppv_tracker singleton and helpers."""

    def test_singleton_exists(self):
        """Module-level ppv_tracker should be importable."""
        assert ppv_tracker is not None
        assert isinstance(ppv_tracker, PPVTracker)

    @pytest.mark.asyncio
    async def test_record_alert_resolution_helper(self):
        """record_alert_resolution() should delegate to singleton."""
        ppv_tracker.reset()
        await record_alert_resolution("true_positive", "critical")
        await record_alert_resolution("false_positive", "watch")
        assert ppv_tracker.total_resolved == 2
        assert ppv_tracker.true_positives == 1
        assert ppv_tracker.false_positives == 1

    @pytest.mark.asyncio
    async def test_get_ppv_status(self):
        """get_ppv_status() should return snapshot dict."""
        ppv_tracker.reset()
        await record_alert_resolution("true_positive", "watch")
        await record_alert_resolution("true_positive", "watch")
        await record_alert_resolution("false_positive", "watch")

        status = await get_ppv_status()
        assert isinstance(status, dict)
        assert status["ppv"] == pytest.approx(2 / 3, abs=0.01)
        assert status["total_resolved"] == 3


class TestPPVEdgeCases:
    """Edge case and boundary tests."""

    @pytest.mark.asyncio
    async def test_no_resolutions_no_data(self):
        """PPV of 0.0 with no data is expected."""
        tracker = PPVTracker()
        assert tracker.ppv == 0.0
        assert tracker.fatigue_rate == 0.0

    @pytest.mark.asyncio
    async def test_all_false_positives(self):
        """All FP → PPV = 0.0, fatigue = 1.0."""
        tracker = PPVTracker()
        for _ in range(10):
            await tracker.record_resolution("false_positive", "watch")
        assert tracker.ppv == 0.0
        assert tracker.fatigue_rate == 1.0

    @pytest.mark.asyncio
    async def test_all_true_positives(self):
        """All TP → PPV = 1.0, fatigue = 0.0."""
        tracker = PPVTracker()
        for _ in range(100):
            await tracker.record_resolution("true_positive", "critical")
        assert tracker.ppv == 1.0
        assert tracker.fatigue_rate == 0.0

    @pytest.mark.asyncio
    async def test_large_volume(self):
        """Large volume should maintain precision."""
        tracker = PPVTracker()
        tp_count = 75_000
        fp_count = 25_000
        for _ in range(tp_count):
            await tracker.record_resolution("true_positive", "watch")
        for _ in range(fp_count):
            await tracker.record_resolution("false_positive", "watch")
        expected_ppv = tp_count / (tp_count + fp_count)
        assert tracker.ppv == expected_ppv
        assert tracker.total_resolved == tp_count + fp_count

    @pytest.mark.asyncio
    async def test_invalid_resolution_does_not_corrupt(self):
        """Invalid resolution strings should still be recorded (no validation)."""
        tracker = PPVTracker()
        await tracker.record_resolution("unknown_resolution_type", "watch")
        # Recorded but not counted as TP or FP
        assert tracker.total_resolved == 1
        assert tracker.true_positives == 0
        assert tracker.false_positives == 0
