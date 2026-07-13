"""
Tests for Fluid Balance domain — RATIFIED per WAVE 2B.
Covers the 07:00-07:00 nursing day boundary, fluid balance computation,
intake/output aggregation, temperature maxima, and 2-hour time-bucketing.

RATIFIED rules tested:
  - RAT-BALANCO-HIDRICO-03 (RULE-006): 24h fluid balance
  - RAT-BALANCO-HIDRICO-04 (RULE-007): Ganhos (intake)
  - RAT-BALANCO-HIDRICO-05 (RULE-008): Diureses (urine output)
  - RAT-BALANCO-HIDRICO-06 (RULE-010): Maximum temperature
  - RAT-BALANCO-HIDRICO-08 (RULE-013): 2-hour time-bucketing
  - RAT-BALANCO-HIDRICO-09 (RULE-016): tempo_criacao
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
import pytz

from intensicare.services.domain_fluid_balance import (
    FluidBalanceResult,
    NursingDayWindow,
    compute_2h_buckets,
    compute_24h_fluid_balance,
    compute_diureses,
    compute_ganhos,
    compute_max_temperature,
    get_nursing_day_window,
    tempo_criacao,
)

SP_TZ = pytz.timezone("America/Sao_Paulo")


# ===========================================================================
# Nursing day window tests
# ===========================================================================


class TestNursingDayWindow:
    """Tests for 07:00-07:00 nursing day window computation."""

    def test_midday_reference_returns_today_window(self):
        """At 14:00 on 2026-07-06, window should be 2026-07-06 07:00 to 2026-07-07 07:00."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 14, 0, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2026-07-06"
        assert w.start == SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0))
        assert w.end == SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0))

    def test_early_morning_reference_returns_previous_day_window(self):
        """At 03:00 on 2026-07-06, window should be 2026-07-05 07:00 to 2026-07-06 07:00."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 3, 0, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2026-07-05"
        assert w.start == SP_TZ.localize(datetime(2026, 7, 5, 7, 0, 0))
        assert w.end == SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0))

    def test_exactly_at_0700_returns_same_day_window(self):
        """At exactly 07:00, window starts at 07:00 same day."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2026-07-06"
        assert w.start == SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0))

    def test_exactly_at_0659_returns_previous_day_window(self):
        """At 06:59, window belongs to previous nursing day."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 6, 59, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2026-07-05"

    def test_month_boundary_midday(self):
        """At 14:00 on 2026-07-31, window spans into August correctly."""
        ref = SP_TZ.localize(datetime(2026, 7, 31, 14, 0, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2026-07-31"
        assert w.start == SP_TZ.localize(datetime(2026, 7, 31, 7, 0, 0))
        assert w.end == SP_TZ.localize(datetime(2026, 8, 1, 7, 0, 0))

    def test_month_boundary_early_morning(self):
        """At 03:00 on 2026-08-01, window spans last day of July."""
        ref = SP_TZ.localize(datetime(2026, 8, 1, 3, 0, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2026-07-31"
        assert w.start == SP_TZ.localize(datetime(2026, 7, 31, 7, 0, 0))
        assert w.end == SP_TZ.localize(datetime(2026, 8, 1, 7, 0, 0))

    def test_year_boundary(self):
        """At 14:00 on 2025-12-31, window spans into 2026."""
        ref = SP_TZ.localize(datetime(2025, 12, 31, 14, 0, 0))
        w = get_nursing_day_window(ref)
        assert w.nursing_date == "2025-12-31"
        assert w.end == SP_TZ.localize(datetime(2026, 1, 1, 7, 0, 0))


# ===========================================================================
# tempo_criacao tests — corrected total_seconds()
# ===========================================================================


class TestTempoCriacao:
    """Tests for tempo_criacao — RAT-BALANCO-HIDRICO-09."""

    def test_recent_record_less_than_1_hour(self):
        """Record created 30 minutes ago should return ~0.5 hours."""
        now = datetime(2026, 7, 6, 14, 30, 0, tzinfo=timezone.utc)
        created = datetime(2026, 7, 6, 14, 0, 0, tzinfo=timezone.utc)
        t = tempo_criacao(created, now)
        assert t == pytest.approx(0.5, rel=0.01)

    def test_record_older_than_24h_uses_total_seconds(self):
        """Record created 30 hours ago must return ~30, not 6 (old timedelta.seconds bug)."""
        now = datetime(2026, 7, 7, 14, 0, 0, tzinfo=timezone.utc)
        created = datetime(2026, 7, 6, 8, 0, 0, tzinfo=timezone.utc)
        t = tempo_criacao(created, now)
        # 30 hours = 30 * 3600 total seconds
        assert t == pytest.approx(30.0, rel=0.01)
        # Old bug would have returned ~6 (30 % 24 = 6)

    def test_record_exactly_48_hours(self):
        """Record created exactly 48 hours ago returns 48."""
        now = datetime(2026, 7, 8, 12, 0, 0, tzinfo=timezone.utc)
        created = datetime(2026, 7, 6, 12, 0, 0, tzinfo=timezone.utc)
        t = tempo_criacao(created, now)
        assert t == pytest.approx(48.0, rel=0.01)

    def test_naive_datetimes_assume_utc(self):
        """Naive datetimes are treated as UTC."""
        now = datetime(2026, 7, 6, 14, 30, 0)
        created = datetime(2026, 7, 6, 14, 0, 0)
        t = tempo_criacao(created, now)
        assert t == pytest.approx(0.5, rel=0.01)


# ===========================================================================
# Fluid balance computation tests
# ===========================================================================


class TestFluidBalance:
    """Tests for 24h fluid balance — RAT-BALANCO-HIDRICO-03."""

    def _make_entry(
        self, quantidade: float, horas: int, minutos: int = 0, tipo: str | None = None, dia: int = 6
    ) -> dict:
        """Helper to create an entry dict within the 2026-07-06 SP timezone."""
        dt = SP_TZ.localize(datetime(2026, 7, dia, horas, minutos, 0))
        entry = {"quantidade": quantidade, "data_hora": dt}
        if tipo is not None:
            entry["tipo"] = tipo
        return entry

    def test_balance_positive(self):
        """Intake > output → positive balance."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [
            self._make_entry(500, 8),
            self._make_entry(1000, 12),
            self._make_entry(500, 16),
        ]
        saidas = [
            self._make_entry(300, 10, tipo="diurese_sonda"),
            self._make_entry(200, 14, tipo="diurese_espontanea"),
        ]
        result = compute_24h_fluid_balance(entradas, saidas, window)
        assert result.total_intake_ml == 2000.0
        assert result.total_output_ml == 500.0
        assert result.net_balance_ml == 1500.0
        assert result.urine_output_ml == 500.0

    def test_balance_negative(self):
        """Output > intake → negative balance."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [self._make_entry(500, 9)]
        saidas = [
            self._make_entry(800, 10, tipo="diurese_sonda"),
            self._make_entry(300, 14, tipo="diurese_espontanea"),
        ]
        result = compute_24h_fluid_balance(entradas, saidas, window)
        assert result.net_balance_ml == -600.0

    def test_zero_balance_is_valid(self):
        """Zero balance is a real value, NOT None (RATIFIED)."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [self._make_entry(500, 9)]
        saidas = [self._make_entry(500, 10, tipo="diurese_espontanea")]
        result = compute_24h_fluid_balance(entradas, saidas, window)
        assert result.net_balance_ml == 0.0
        assert result.net_balance_ml is not None

    def test_entries_before_window_excluded(self):
        """Entries before 07:00 are excluded (belong to previous nursing day)."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [
            self._make_entry(1000, 5),  # Before 07:00 — excluded
            self._make_entry(500, 8),  # In window
        ]
        saidas = [
            self._make_entry(200, 6, tipo="diurese_sonda"),  # Before 07:00 — excluded
        ]
        result = compute_24h_fluid_balance(entradas, saidas, window)
        assert result.total_intake_ml == 500.0
        assert result.total_output_ml == 0.0
        assert result.net_balance_ml == 500.0

    def test_entries_after_window_excluded(self):
        """Entries at/after next day 07:00 are excluded."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [
            self._make_entry(500, 23, dia=6),  # Night of 6th — in window
            self._make_entry(300, 7, dia=7),  # Exactly at end — excluded
        ]
        saidas = []
        result = compute_24h_fluid_balance(entradas, saidas, window)
        # Entry at 2026-07-06 23:00 is in window; at 2026-07-07 07:00 is excluded
        assert result.total_intake_ml == 500.0

    def test_urine_output_only_counts_diurese_tipos(self):
        """Only diurese_espontanea and diurese_sonda count as urine output."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        saidas = [
            self._make_entry(300, 10, tipo="diurese_sonda"),
            self._make_entry(200, 12, tipo="diurese_espontanea"),
            self._make_entry(150, 14, tipo="evacuacao"),  # Not urine
            self._make_entry(100, 16, tipo="vomito"),  # Not urine
        ]
        entradas = []
        result = compute_24h_fluid_balance(entradas, saidas, window)
        assert result.urine_output_ml == 500.0
        assert result.total_output_ml == 750.0

    def test_missing_quantidade_defaults_to_zero(self):
        """Missing quantidade field defaults to 0 (safe)."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [{"data_hora": SP_TZ.localize(datetime(2026, 7, 6, 10, 0, 0))}]
        saidas = []
        result = compute_24h_fluid_balance(entradas, saidas, window)
        assert result.total_intake_ml == 0.0


# ===========================================================================
# Ganhos (intake) tests
# ===========================================================================


class TestGanhos:
    """Tests for Ganhos (fluid intake sum) — RAT-BALANCO-HIDRICO-04."""

    def test_ganhos_sums_all_entradas_no_type_filter(self):
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        entradas = [
            {"quantidade": 500, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 8, 0, 0))},
            {"quantidade": 300, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 12, 0, 0))},
            {"quantidade": 200, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 16, 0, 0))},
        ]
        total = compute_ganhos(entradas, window)
        assert total == 1000.0

    def test_ganhos_zero_is_valid(self):
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        total = compute_ganhos([], window)
        assert total == 0.0
        assert total is not None


# ===========================================================================
# Diureses (urine output) tests
# ===========================================================================


class TestDiureses:
    """Tests for Diureses (urine output) — RAT-BALANCO-HIDRICO-05."""

    def test_diureses_filters_by_tipos(self):
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        saidas = [
            {
                "quantidade": 400,
                "tipo": "diurese_sonda",
                "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 10, 0, 0)),
            },
            {
                "quantidade": 300,
                "tipo": "diurese_espontanea",
                "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 14, 0, 0)),
            },
            {
                "quantidade": 200,
                "tipo": "evacuacao",
                "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 16, 0, 0)),
            },
        ]
        total = compute_diureses(saidas, window)
        assert total == 700.0

    def test_diureses_zero_is_valid(self):
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        total = compute_diureses([], window)
        assert total == 0.0


# ===========================================================================
# Maximum temperature tests
# ===========================================================================


class TestMaxTemperature:
    """Tests for maximum temperature — RAT-BALANCO-HIDRICO-06."""

    def test_max_temperature_returns_highest(self):
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        sv = [
            {"temperatura": 36.5, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 8, 0, 0))},
            {"temperatura": 38.2, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 14, 0, 0))},
            {"temperatura": 37.1, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 20, 0, 0))},
        ]
        max_temp = compute_max_temperature(sv, window)
        assert max_temp == 38.2

    def test_max_temperature_none_stripped(self):
        """Records with None temperatura are ignored."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        sv = [
            {"temperatura": 37.0, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 8, 0, 0))},
            {"temperatura": None, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 12, 0, 0))},
        ]
        max_temp = compute_max_temperature(sv, window)
        assert max_temp == 37.0

    def test_no_temperature_records_returns_none(self):
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        max_temp = compute_max_temperature([], window)
        assert max_temp is None

    def test_temperature_outside_window_excluded(self):
        """Temperature recorded before 07:00 excluded."""
        window = NursingDayWindow(
            start=SP_TZ.localize(datetime(2026, 7, 6, 7, 0, 0)),
            end=SP_TZ.localize(datetime(2026, 7, 7, 7, 0, 0)),
            nursing_date="2026-07-06",
        )
        sv = [
            {"temperatura": 36.0, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 6, 0, 0))},
            {"temperatura": 37.5, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 10, 0, 0))},
        ]
        max_temp = compute_max_temperature(sv, window)
        assert max_temp == 37.5


# ===========================================================================
# 2-hour bucket tests — RAT-BALANCO-HIDRICO-08
# ===========================================================================


class Test2HBuckets:
    """Tests for 2-hour time-bucketing."""

    def test_buckets_distribute_entries_correctly(self):
        """Entries should land in the correct bucket."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 15, 0, 0))  # After 08:00 on July 6
        entradas = [
            {"quantidade": 100, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 8, 30, 0))},
            {"quantidade": 200, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 10, 15, 0))},
        ]
        saidas = [
            {"quantidade": 50, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 9, 0, 0))},
        ]
        buckets = compute_2h_buckets(entradas, saidas, ref)
        assert buckets["08:00-10:00"]["intake"] == 100.0
        assert buckets["08:00-10:00"]["output"] == 50.0
        assert buckets["10:00-12:00"]["intake"] == 200.0
        assert buckets["12:00-14:00"]["intake"] == 0.0

    def test_bucket_2200_0000_wraps_correctly(self):
        """22:00-00:00 bucket should capture entries in that range (was buggy)."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 15, 0, 0))
        saidas = [
            {"quantidade": 300, "data_hora": SP_TZ.localize(datetime(2026, 7, 6, 23, 0, 0))},
        ]
        entradas = []
        buckets = compute_2h_buckets(entradas, saidas, ref)
        assert buckets["22:00-00:00"]["output"] == 300.0

    def test_bucket_0000_0200_wraps_to_next_day(self):
        """00:00-02:00 bucket on next day."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 15, 0, 0))  # Antes das 08:00 -> anchor 06
        entradas = [
            {"quantidade": 150, "data_hora": SP_TZ.localize(datetime(2026, 7, 7, 1, 30, 0))},
        ]
        saidas = []
        buckets = compute_2h_buckets(entradas, saidas, ref)
        assert buckets["00:00-02:00"]["intake"] == 150.0

    def test_all_buckets_present(self):
        """All 12 bucket labels must be present."""
        ref = SP_TZ.localize(datetime(2026, 7, 6, 15, 0, 0))
        buckets = compute_2h_buckets([], [], ref)
        expected_labels = [
            "08:00-10:00",
            "10:00-12:00",
            "12:00-14:00",
            "14:00-16:00",
            "16:00-18:00",
            "18:00-20:00",
            "20:00-22:00",
            "22:00-00:00",
            "00:00-02:00",
            "02:00-04:00",
            "04:00-06:00",
            "06:00-08:00",
        ]
        for label in expected_labels:
            assert label in buckets
            assert "intake" in buckets[label]
            assert "output" in buckets[label]


# ===========================================================================
# Additional edge-case tests (GAP-023 coverage enhancement)
# ===========================================================================


class TestFluidBalanceResult:
    """Tests for FluidBalanceResult dataclass."""

    def test_result_creation(self):
        """Should create a valid FluidBalanceResult."""

        result = FluidBalanceResult(
            nursing_date="2026-07-06",
            total_intake_ml=1000.0,
            total_output_ml=500.0,
            net_balance_ml=500.0,
            urine_output_ml=300.0,
            max_temperature_c=37.5,
        )
        assert result.total_intake_ml == 1000.0
        assert result.total_output_ml == 500.0
        assert result.urine_output_ml == 300.0
        assert result.net_balance_ml == 500.0

    def test_result_with_none_temperature(self):
        """Temperature can be None when no readings."""

        result = FluidBalanceResult(
            nursing_date="2026-07-06",
            total_intake_ml=0.0,
            total_output_ml=0.0,
            net_balance_ml=0.0,
            urine_output_ml=0.0,
            max_temperature_c=None,
        )
        assert result.max_temperature_c is None


class TestNursingDayWindowModel:
    """Tests for NursingDayWindow dataclass."""

    def test_window_creation(self):
        from datetime import datetime, timezone

        from intensicare.services.domain_fluid_balance import NursingDayWindow

        w = NursingDayWindow(
            start=datetime(2026, 7, 6, 7, 0, 0, tzinfo=timezone.utc),
            end=datetime(2026, 7, 7, 7, 0, 0, tzinfo=timezone.utc),
            nursing_date="2026-07-06",
        )
        assert w.nursing_date == "2026-07-06"
        # NursingDayWindow has no duration_hours() helper — compute the span
        # directly from start/end (the "nursing day is 24h" invariant).
        assert (w.end - w.start).total_seconds() / 3600.0 == 24.0


class TestFluidBalanceEmptyEntries:
    """Edge cases with empty entries lists."""

    def test_empty_entries_return_zero_balance(self):
        """No entries at all should return zero balance."""
        from datetime import datetime, timezone

        from intensicare.services.domain_fluid_balance import (
            NursingDayWindow,
            compute_24h_fluid_balance,
        )

        window = NursingDayWindow(
            start=datetime(2026, 7, 6, 7, 0, 0, tzinfo=timezone.utc),
            end=datetime(2026, 7, 7, 7, 0, 0, tzinfo=timezone.utc),
            nursing_date="2026-07-06",
        )
        result = compute_24h_fluid_balance([], [], window)
        assert result.total_intake_ml == 0.0
        assert result.total_output_ml == 0.0
        assert result.net_balance_ml == 0.0
        assert result.urine_output_ml == 0.0

    def test_negative_quantidade_is_accepted(self):
        """Negative quantities should be summed (correction entries)."""
        from datetime import datetime, timezone

        from intensicare.services.domain_fluid_balance import (
            NursingDayWindow,
            compute_24h_fluid_balance,
        )

        window = NursingDayWindow(
            start=datetime(2026, 7, 6, 7, 0, 0, tzinfo=timezone.utc),
            end=datetime(2026, 7, 7, 7, 0, 0, tzinfo=timezone.utc),
            nursing_date="2026-07-06",
        )
        entradas = [
            {"quantidade": 500, "data_hora": datetime(2026, 7, 6, 8, 0, 0, tzinfo=timezone.utc)},
            {"quantidade": -100, "data_hora": datetime(2026, 7, 6, 9, 0, 0, tzinfo=timezone.utc)},
        ]
        result = compute_24h_fluid_balance(entradas, [], window)
        assert result.total_intake_ml == 400.0

    def test_null_handling_in_compute_max_temperature(self):
        """compute_max_temperature with no readings returns None."""
        from intensicare.services.domain_fluid_balance import compute_max_temperature

        result = compute_max_temperature([])
        assert result is None

    def test_max_temperature_with_multiple_readings(self):
        """Should return the maximum temperature."""
        from datetime import datetime, timezone

        from intensicare.services.domain_fluid_balance import (
            NursingDayWindow,
            compute_max_temperature,
        )

        window = NursingDayWindow(
            start=datetime(2026, 7, 6, 7, 0, 0, tzinfo=timezone.utc),
            end=datetime(2026, 7, 7, 7, 0, 0, tzinfo=timezone.utc),
            nursing_date="2026-07-06",
        )
        temps = [
            {"temperatura": 37.0, "data_hora": datetime(2026, 7, 6, 8, 0, 0, tzinfo=timezone.utc)},
            {"temperatura": 38.5, "data_hora": datetime(2026, 7, 6, 12, 0, 0, tzinfo=timezone.utc)},
            {"temperatura": 37.2, "data_hora": datetime(2026, 7, 6, 16, 0, 0, tzinfo=timezone.utc)},
        ]
        result = compute_max_temperature(temps, window)
        assert result == 38.5


class TestFluidBalanceComputeFunctions:
    """Tests for individual compute functions used by the domain."""

    def test_compute_ganhos_sums_intake(self):
        """compute_ganhos should sum all intake entries in the window."""
        from datetime import datetime, timezone

        from intensicare.services.domain_fluid_balance import (
            NursingDayWindow,
            compute_ganhos,
        )

        window = NursingDayWindow(
            start=datetime(2026, 7, 6, 7, 0, 0, tzinfo=timezone.utc),
            end=datetime(2026, 7, 7, 7, 0, 0, tzinfo=timezone.utc),
            nursing_date="2026-07-06",
        )
        entradas = [
            {"quantidade": 250, "data_hora": datetime(2026, 7, 6, 8, 0, 0, tzinfo=timezone.utc)},
            {"quantidade": 250, "data_hora": datetime(2026, 7, 6, 20, 0, 0, tzinfo=timezone.utc)},
        ]
        result = compute_ganhos(entradas, window)
        assert result == 500.0

    def test_compute_diureses_sums_urine_only(self):
        """compute_diureses should sum only urine-related output."""
        from datetime import datetime, timezone

        from intensicare.services.domain_fluid_balance import (
            NursingDayWindow,
            compute_diureses,
        )

        window = NursingDayWindow(
            start=datetime(2026, 7, 6, 7, 0, 0, tzinfo=timezone.utc),
            end=datetime(2026, 7, 7, 7, 0, 0, tzinfo=timezone.utc),
            nursing_date="2026-07-06",
        )
        saidas = [
            {
                "quantidade": 300,
                "data_hora": datetime(2026, 7, 6, 10, 0, 0, tzinfo=timezone.utc),
                "tipo": "diurese_sonda",
            },
            {
                "quantidade": 200,
                "data_hora": datetime(2026, 7, 6, 12, 0, 0, tzinfo=timezone.utc),
                "tipo": "evacuacao",
            },
        ]
        result = compute_diureses(saidas, window)
        assert result == 300.0
