"""Tests for Ventilation Monitoring domain."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from intensicare.services.domain_ventilacao import (
    ParameterTrend,
    VentilationParameters,
    VentilationResult,
    VentilationTrend,
    compute_ventilation_trend,
    evaluate_ventilation,
    extract_ventilation_params,
)


# ============================================================================
# extract_ventilation_params
# ============================================================================


class TestExtractVentilationParams:
    """Tests for extract_ventilation_params()."""

    def test_extract_full_params(self):
        """All ventilation parameters extracted correctly."""
        data = {
            "mpi_id": "PAT-001",
            "id": 42,
            "modo_ventilatorio": "VCV",
            "fio2": 0.50,
            "peep": 8,
            "volume_corrente": 450,
            "frequencia_respiratoria": 16,
            "pplat": 24,
            "pao2": 90,
            "saturacao_o2": 96,
            "vc_por_kg_pbw": 6.5,
            "fr_espontanea": 18,
            "collected_at": "2025-01-01T12:00:00Z",
            "source": "prontuario",
        }
        result = extract_ventilation_params(data)

        assert result.mpi_id == "PAT-001"
        assert result.id == 42
        assert result.mode == "VCV"
        assert result.FiO2 == 0.50
        assert result.PEEP == 8.0
        assert result.VC == 450.0
        assert result.FR == 16
        assert result.Pplat == 24.0
        assert result.driving_pressure == pytest.approx(16.0)  # 24 - 8
        assert result.PaO2_FiO2_ratio == pytest.approx(180.0)  # 90 / 0.50
        assert result.SpO2 == 96
        assert result.tidal_volume_per_kg_pbw == pytest.approx(6.5)
        assert result.spontaneous_rate == 18
        assert result.collected_at == "2025-01-01T12:00:00Z"
        assert result.source == "prontuario"

    def test_driving_pressure_computed(self):
        """Pplat - PEEP = driving pressure."""
        data = {
            "pplat": 30,
            "peep": 10,
            "fio2": 0.40,
        }
        result = extract_ventilation_params(data)
        assert result.driving_pressure == pytest.approx(20.0)

    def test_driving_pressure_none_when_missing(self):
        """Driving pressure is None when Pplat or PEEP missing."""
        data_missing_pplat = {"peep": 10, "fio2": 0.40}
        result = extract_ventilation_params(data_missing_pplat)
        assert result.driving_pressure is None

        data_missing_peep = {"pplat": 30, "fio2": 0.40}
        result = extract_ventilation_params(data_missing_peep)
        assert result.driving_pressure is None

    def test_pf_ratio_computed(self):
        """PaO2/FiO2 ratio computed when both available."""
        data = {"pao2": 100, "fio2": 0.50}
        result = extract_ventilation_params(data)
        assert result.PaO2_FiO2_ratio == pytest.approx(200.0)

    def test_pf_ratio_none_when_pao2_missing(self):
        """PaO2/FiO2 ratio is None when PaO2 is missing."""
        data = {"fio2": 0.50}
        result = extract_ventilation_params(data)
        assert result.PaO2_FiO2_ratio is None

    def test_fio2_percentage_converted(self):
        """FiO2 60% → 0.60 fraction (via _ensure_fio2_fraction)."""
        data = {"fio2": 60, "pao2": 90}
        result = extract_ventilation_params(data)
        assert result.FiO2 == 0.60
        # P/F ratio should use 0.60: 90 / 0.60 = 150
        assert result.PaO2_FiO2_ratio == pytest.approx(150.0)

    def test_missing_data_handled(self):
        """None/absent values for optional fields are handled gracefully."""
        data: dict = {}  # completely empty
        result = extract_ventilation_params(data)
        assert result.mpi_id == ""
        assert result.id is None
        assert result.mode is None
        assert result.FiO2 is None
        assert result.PEEP is None
        assert result.VC is None
        assert result.FR is None
        assert result.Pplat is None
        assert result.driving_pressure is None
        assert result.PaO2_FiO2_ratio is None
        assert result.SpO2 is None
        assert result.tidal_volume_per_kg_pbw is None
        assert result.spontaneous_rate is None

    def test_invalid_numeric_values(self):
        """Non-numeric strings become None for numeric fields."""
        data = {
            "peep": "invalid",
            "pplat": "not_a_number",
            "frequencia_respiratoria": "abc",
        }
        result = extract_ventilation_params(data)
        assert result.PEEP is None
        assert result.Pplat is None
        assert result.FR is None

    def test_default_collected_at(self):
        """When collected_at is absent, a default is generated."""
        data = {"fio2": 0.21}
        result = extract_ventilation_params(data)
        # Should have a non-empty isoformat timestamp
        assert result.collected_at != ""
        # Should be parseable
        datetime.fromisoformat(result.collected_at)


# ============================================================================
# compute_ventilation_trend
# ============================================================================


class TestVentilationTrend:
    """Tests for compute_ventilation_trend()."""

    @staticmethod
    def _make_history(
        entries: list[tuple[float, float, float]],
    ) -> list[dict]:
        """Build history dicts from list of (time_delta_hours, peep, pplat).

        Each entry gets: fio2=0.50, volume_corrente=450, frequencia_respiratoria=16,
        peep and pplat as given, and a timestamp relative to now.
        Entries should be ordered chronologically (oldest first).
        """
        now = datetime.now(timezone.utc)
        history = []
        for i, (hours_ago, peep, pplat) in enumerate(entries):
            ts = now - timedelta(hours=hours_ago)
            history.append(
                {
                    "fio2": 0.50,
                    "peep": peep,
                    "volume_corrente": 450,
                    "frequencia_respiratoria": 16,
                    "pplat": pplat,
                    "collected_at": ts.isoformat(),
                }
            )
        return history

    def test_trend_computes_min_max_avg(self):
        """Trend computes min, max, avg for each parameter."""
        history = self._make_history(
            [
                (2.0, 8, 24),
                (1.0, 10, 26),
                (0.5, 12, 28),
            ]
        )
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)

        peep = trend.parameters["PEEP"]
        assert peep.current == 12.0
        assert peep.min == 8.0
        assert peep.max == 12.0
        assert peep.avg == pytest.approx(10.0)

        pplat = trend.parameters["Pplat"]
        assert pplat.current == 28.0
        assert pplat.min == 24.0
        assert pplat.max == 28.0
        assert pplat.avg == pytest.approx(26.0)

    def test_trend_direction_rising(self):
        """Trend direction 'rising' when values increase >= 5%."""
        history = self._make_history(
            [
                (2.0, 8, 20),  # PEEP=8
                (1.0, 9, 22),  # PEEP=9
                (0.5, 10, 24),  # PEEP=10  (+25% from 8)
            ]
        )
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        assert trend.parameters["PEEP"].direction == "rising"

    def test_trend_direction_falling(self):
        """Trend direction 'falling' when values decrease >= 5%."""
        history = self._make_history(
            [
                (2.0, 14, 30),
                (1.0, 12, 28),
                (0.5, 10, 26),  # PEEP 10, -28.6% from 14
            ]
        )
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        assert trend.parameters["PEEP"].direction == "falling"

    def test_trend_direction_stable(self):
        """Trend direction 'stable' when change is less than 5%."""
        history = self._make_history(
            [
                (2.0, 8, 24),
                (1.0, 8.2, 24.1),  # very small change
            ]
        )
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        # 8 → 8.2 is 2.5%, under 5% threshold
        assert trend.parameters["PEEP"].direction == "stable"

    def test_trend_empty_history(self):
        """Empty history returns a VentilationTrend with empty parameters dict."""
        trend = compute_ventilation_trend("PAT-001", [], trend_hours=24)
        assert isinstance(trend, VentilationTrend)
        assert trend.period_hours == 24
        # No entries → no parameters computed
        assert trend.parameters == {}

    def test_trend_respects_hours_window(self):
        """Entries older than trend_hours are excluded."""
        history = self._make_history(
            [
                (30.0, 5, 18),  # 30h ago — OUTSIDE 24h window
                (2.0, 12, 28),  # 2h ago — inside window
            ]
        )
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        # Only the 2h-old entry is inside the window
        peep = trend.parameters["PEEP"]
        assert peep.current == 12.0  # from the 2h entry
        assert peep.min == 12.0
        assert peep.max == 12.0
        assert len(peep.series) == 1

    def test_trend_computes_change_pct(self):
        """Trend computes change_pct from first to last value."""
        history = self._make_history(
            [
                (2.0, 10, 25),
                (0.5, 12, 30),
            ]
        )
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        # PEEP 10→12 = +20%
        assert trend.parameters["PEEP"].change_pct == pytest.approx(20.0)

    def test_trend_driving_pressure_computed(self):
        """Trend computes driving_pressure from Pplat - PEEP in each entry."""
        history = [
            {
                "pplat": 28,
                "peep": 8,
                "collected_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            },
            {
                "pplat": 32,
                "peep": 10,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        dp = trend.parameters["driving_pressure"]
        # 28-8=20, 32-10=22, so values are [20, 22]
        assert dp.current == 22.0
        assert dp.min == 20.0
        assert dp.max == 22.0
        # 20→22 = +10%
        assert dp.change_pct == pytest.approx(10.0)
        assert dp.direction == "rising"

    def test_trend_single_value_direction_stable(self):
        """A single value in the window produces 'stable' direction."""
        history = self._make_history([(0.5, 10, 25)])
        trend = compute_ventilation_trend("PAT-001", history, trend_hours=24)
        assert trend.parameters["PEEP"].direction == "stable"
        assert trend.parameters["PEEP"].change_pct is None


# ============================================================================
# evaluate_ventilation
# ============================================================================


class TestEvaluateVentilation:
    """Tests for evaluate_ventilation()."""

    def test_evaluate_combines_params_and_trend(self):
        """evaluate_ventilation returns VentilationResult with both params and trend."""
        now = datetime.now(timezone.utc)
        current = {
            "mpi_id": "PAT-001",
            "modo_ventilatorio": "PCV",
            "fio2": 0.40,
            "peep": 8,
            "volume_corrente": 500,
            "frequencia_respiratoria": 14,
            "pplat": 22,
            "pao2": 95,
            "collected_at": now.isoformat(),
        }
        history = [
            {
                "fio2": 0.40,
                "peep": 10,
                "pplat": 24,
                "collected_at": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "fio2": 0.50,
                "peep": 8,
                "pplat": 22,
                "collected_at": (now - timedelta(hours=1)).isoformat(),
            },
        ]

        result = evaluate_ventilation("PAT-001", current, history, trend_hours=24)

        assert isinstance(result, VentilationResult)
        assert result.parameters.mpi_id == "PAT-001"
        assert result.parameters.FiO2 == 0.40
        assert result.parameters.PEEP == 8.0
        assert result.parameters.driving_pressure == pytest.approx(14.0)  # 22-8
        assert result.parameters.PaO2_FiO2_ratio == pytest.approx(237.5)  # 95/0.40

        # Trend should have computed from history
        assert isinstance(result.trend, VentilationTrend)
        peep_trend = result.trend.parameters["PEEP"]
        # history PEEP: 10, 8 → falling
        assert peep_trend.current == 8.0
        assert peep_trend.min == 8.0
        assert peep_trend.max == 10.0
        assert peep_trend.direction == "falling"

    def test_evaluate_no_history(self):
        """evaluate_ventilation with no history still returns params with empty trend."""
        current = {
            "fio2": 0.30,
            "peep": 5,
        }
        result = evaluate_ventilation("PAT-002", current)

        assert result.parameters.FiO2 == 0.30
        assert result.parameters.PEEP == 5.0
        # Trend exists but has no parameter entries (empty history → empty params dict)
        assert isinstance(result.trend, VentilationTrend)
        assert result.trend.parameters == {}

    def test_evaluate_default_history_none(self):
        """evaluate_ventilation handles history=None gracefully."""
        current = {"fio2": 0.21}
        result = evaluate_ventilation("PAT-003", current, history=None)
        assert result.parameters.FiO2 == 0.21
        assert isinstance(result.trend, VentilationTrend)
        # No history → empty parameters dict
        assert result.trend.parameters == {}

    def test_evaluate_collected_at_propagated(self):
        """evaluate_ventilation propagates collected_at from params to result."""
        current = {
            "fio2": 0.21,
            "collected_at": "2025-06-15T08:00:00Z",
        }
        result = evaluate_ventilation("PAT-004", current)
        assert result.collected_at == "2025-06-15T08:00:00Z"
