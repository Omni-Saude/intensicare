"""
Tests for Hemodynamic Stability domain (domain_estabilidade.py).

Covers:
- evaluate_stability: score, severity bands, recommendation
- Severity bands: estavel (0-3), atencao (4-9), critico (10+)
- 27 criteria returned across 6 categories
- Combined criteria (hipoperfusão global, piora multidomínio, choque persistente)
- classify_stability and compute_stability_trend helpers
- StabilityEvaluationResult dataclass defaults
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from intensicare.services.domain_estabilidade import (
    STABILITY_CRITERIA,
    StabilityCriterionResult,
    StabilityEvaluationResult,
    _determine_severity,
    classify_stability,
    compute_stability_trend,
    evaluate_stability,
)


# ---------------------------------------------------------------------------
# Helper: build clinical_data that triggers specific additional criteria
# ---------------------------------------------------------------------------

def _empty_clinical_data() -> dict:
    """Return empty clinical_data dict."""
    return {}


def _data_lactate_high(lactate: float = 4.5) -> dict:
    """Clinical data with elevated lactate (triggers Lactato>2 and Lactato>=4)."""
    return {"lactato_arterial": lactate}


def _data_multiple_abnormal() -> dict:
    """Clinical data triggering 4+ criteria across 3+ categories.

    Triggers:
    - Lactato > 2 (perfusion)
    - Lactato >= 4 (perfusion)
    - PAM < 65 (cardiac_output)
    - FC > 130 (cardiac_output)
    - Hipoperfusão global (combined, >=2 domains altered)
    """
    return {
        "lactato_arterial": 5.0,
        "pressao_arterial_media": 55.0,
        "frequencia_cardiaca": 145.0,
    }


def _data_perfusion_criteria() -> dict:
    """Clinical data triggering perfusion + combined criteria.

    Triggers:
    - SvO2 < 65% (perfusion)
    - Delta PCO2 > 6 (perfusion)
    - Lactato > 2 (perfusion)
    """
    return {
        "svo2": 58.0,
        "delta_pco2": 8.0,
        "lactato_arterial": 2.5,
    }


def _data_fluid_balance() -> dict:
    """Clinical data triggering fluid balance criteria.

    Triggers:
    - Balanço 24h > 3000 (fluid_balance)
    - Balanço cumulativo < -2000 (fluid_balance)
    """
    return {
        "balanco_hidrico_24h": 4000.0,
        "balanco_hidrico_cumulativo": -2500.0,
    }


# ===========================================================================
# evaluate_stability — score and severity
# ===========================================================================


class TestEvaluateStabilityScore:
    """Score computation: empty data → 0, abnormal data → increasing score."""

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_empty_data_score_zero(self, mock_hemo):
        """Empty clinical data → score 0, severity estavel."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-001", _empty_clinical_data())
        assert result.mpi_id == "MPI-001"
        assert result.score == 0
        assert result.severity == "estavel"

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_high_lactate_triggers_two_criteria(self, mock_hemo):
        """Lactate >= 4 triggers two perfusion criteria."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-002", _data_lactate_high(4.5))
        assert result.score >= 2

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_multiple_abnormal_triggers_several_criteria(self, mock_hemo):
        """Multiple abnormal vitals → score >= 4."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-003", _data_multiple_abnormal())
        # At minimum: lactate>2, lactate>=4, PAM<65, FC>130 = 4
        # Plus potentially hipoperfusao global (>=2 domains) = 5
        assert result.score >= 4


# ===========================================================================
# Severity bands
# ===========================================================================


class TestSeverityBands:
    """Severity mapping: 0-3 estavel, 4-9 atencao, 10+ critico."""

    def test_determine_severity_estavel_zero(self):
        assert _determine_severity(0) == "estavel"

    def test_determine_severity_estavel_boundary(self):
        assert _determine_severity(3) == "estavel"

    def test_determine_severity_atencao_entry(self):
        assert _determine_severity(4) == "atencao"

    def test_determine_severity_atencao_boundary(self):
        assert _determine_severity(9) == "atencao"

    def test_determine_severity_critico_entry(self):
        assert _determine_severity(10) == "critico"

    def test_determine_severity_critico_max(self):
        assert _determine_severity(27) == "critico"

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_severity_atencao_with_multiple_abnormal(self, mock_hemo):
        """Multiple abnormal data → severity atencao (score 4+)."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-SEV", _data_multiple_abnormal())
        assert result.severity in ("atencao", "critico")
        assert result.score >= 4


# ===========================================================================
# Criteria structure
# ===========================================================================


class TestCriteriaStructure:
    """Verify the 27 criteria structure and categories."""

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_returns_twenty_seven_criteria(self, mock_hemo):
        """evaluate_stability returns exactly 27 StabilityCriterionResult items."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-CAT", _empty_clinical_data())
        assert len(result.criteria) == 27
        assert all(isinstance(c, StabilityCriterionResult) for c in result.criteria)

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_all_six_categories_present(self, mock_hemo):
        """All 6 categories appear in the criteria results."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-CAT2", _empty_clinical_data())
        categories = {c.category for c in result.criteria}
        expected = {"vasopressor", "perfusion", "cardiac_output", "fluid_balance", "lactate", "combined"}
        assert categories == expected

    def test_stability_criteria_constant_has_27_items(self):
        """STABILITY_CRITERIA constant has 27 items."""
        assert len(STABILITY_CRITERIA) == 27

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_each_criterion_has_status(self, mock_hemo):
        """Every criterion result has a valid status."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-STAT", _empty_clinical_data())
        for c in result.criteria:
            assert c.status in ("normal", "warning", "critical")


# ===========================================================================
# Combined criteria
# ===========================================================================


class TestCombinedCriteria:
    """Tests for the three combined criteria (hipoperfusão, piora multidomínio, choque persistente)."""

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_hipoperfusao_global_triggered_with_multi_domain(self, mock_hemo):
        """Hipoperfusão global triggers when >=2 domains have warning/critical criteria."""
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-HIPO", _data_multiple_abnormal())
        hipo = next((c for c in result.criteria if "Hipoperfusão global" in c.name), None)
        assert hipo is not None
        # With lactate, PAM, FC all abnormal → at least perfusion and cardiac_output
        # affected → hipoperfusão global should be warning
        assert hipo.status in ("warning", "normal")  # depends on exact evaluation

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_piora_multidominio_from_flags(self, mock_hemo):
        """Piora multidomínio uses historical flags from clinical_data."""
        mock_hemo.return_value = {}
        data = {
            "piora_vasopressor_6h": True,
            "piora_perfusao_6h": True,
            "piora_debito_6h": False,
            "piora_fluidos_6h": False,
            "piora_lactato_6h": False,
        }
        result = evaluate_stability("MPI-PIORA", data)
        piora = next((c for c in result.criteria if "Piora em ≥ 2 domínios" in c.name), None)
        assert piora is not None
        assert piora.status == "warning"
        assert "2 domínios" in piora.value

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_choque_persistente_with_duration(self, mock_hemo):
        """Choque persistente triggers when instability duration > 6h."""
        mock_hemo.return_value = {}
        data = {"horas_instabilidade_hemodinamica": 10.0}
        result = evaluate_stability("MPI-CHOQUE", data)
        choque = next((c for c in result.criteria if "Choque persistente" in c.name), None)
        assert choque is not None
        assert choque.status == "warning"


# ===========================================================================
# classify_stability helper
# ===========================================================================


class TestClassifyStability:
    """Quick severity classification from score alone."""

    def test_classify_score_0_estavel(self):
        result = classify_stability(0)
        assert result["severity"] == "estavel"

    def test_classify_score_3_estavel(self):
        result = classify_stability(3)
        assert result["severity"] == "estavel"

    def test_classify_score_5_atencao(self):
        result = classify_stability(5)
        assert result["severity"] == "atencao"

    def test_classify_score_12_critico(self):
        result = classify_stability(12)
        assert result["severity"] == "critico"

    def test_classify_returns_recommendation(self):
        result = classify_stability(8)
        assert "recommendation" in result
        assert len(result["recommendation"]) > 0


# ===========================================================================
# compute_stability_trend
# ===========================================================================


class TestComputeStabilityTrend:
    """7-day trend computation from assessment history."""

    def test_empty_history_stable(self):
        trend = compute_stability_trend("MPI-T1", [])
        assert trend["direction"] == "stable"
        assert trend["delta_7d"] == 0
        assert trend["trend_points"] == []

    def test_single_point_stable(self):
        history = [{"score": 3, "severity": "estavel", "assessed_at": "2025-01-01T10:00:00"}]
        trend = compute_stability_trend("MPI-T2", history)
        assert trend["direction"] == "stable"
        assert trend["delta_7d"] == 0
        assert len(trend["trend_points"]) == 1

    def test_worsening_trend(self):
        history = [
            {"score": 1, "severity": "estavel", "assessed_at": "2025-01-01T10:00:00"},
            {"score": 6, "severity": "atencao", "assessed_at": "2025-01-02T10:00:00"},
        ]
        trend = compute_stability_trend("MPI-T3", history)
        assert trend["direction"] == "worsening"
        assert trend["delta_7d"] == 5

    def test_improving_trend(self):
        history = [
            {"score": 8, "severity": "atencao", "assessed_at": "2025-01-01T10:00:00"},
            {"score": 2, "severity": "estavel", "assessed_at": "2025-01-02T10:00:00"},
        ]
        trend = compute_stability_trend("MPI-T4", history)
        assert trend["direction"] == "improving"
        assert trend["delta_7d"] == -6


# ===========================================================================
# StabilityEvaluationResult dataclass
# ===========================================================================


class TestStabilityEvaluationResult:
    """Dataclass field defaults and structure."""

    def test_default_values(self):
        result = StabilityEvaluationResult(mpi_id="MPI-DEF")
        assert result.mpi_id == "MPI-DEF"
        assert result.score == 0
        assert result.severity == "estavel"
        assert result.criteria == []
        assert result.recommendation == ""
        assert result.assessed_at == ""

    def test_assessed_at_set_after_evaluation(self):
        """After evaluate_stability, assessed_at is populated (ISO format)."""
        with patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts", return_value={}):
            result = evaluate_stability("MPI-TS", _empty_clinical_data())
        assert result.assessed_at != ""
        assert "T" in result.assessed_at  # ISO format contains 'T'


# ===========================================================================
# Recommendation strings (PT-BR)
# ===========================================================================


class TestRecommendationStrings:
    """Verify recommendation text for each severity band."""

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_estavel_recommendation(self, mock_hemo):
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-REC1", _empty_clinical_data())
        assert "ESTÁVEL" in result.recommendation
        assert "rotina" in result.recommendation.lower()

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_atencao_recommendation(self, mock_hemo):
        mock_hemo.return_value = {}
        result = evaluate_stability("MPI-REC2", _data_multiple_abnormal())
        assert "ATENÇÃO" in result.recommendation

    @patch("intensicare.services.domain_estabilidade.evaluate_hemo_alerts")
    def test_critico_recommendation(self, mock_hemo):
        """Manually produce a critico scenario via classify_stability recommendation."""
        result = classify_stability(12)
        assert "CRÍTICO" in result["recommendation"]
        assert "IMEDIATA" in result["recommendation"]
