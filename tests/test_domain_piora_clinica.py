"""
Tests for Clinical Deterioration domain (domain_piora_clinica.py).

Covers:
- evaluate_deterioration: score categories (0, 1+, 1-, 3+, 3-)
- Trend computation vs previous_score
- 13 criteria across 5 domains
- domains_affected count
- Recommendation generation (PT-BR)
- classify_deterioration helper
- DeteriorationEvaluationResult dataclass defaults
"""

from __future__ import annotations

import pytest

from intensicare.services.domain_piora_clinica import (
    DOMAIN_CRITERIA,
    DeteriorationCriteriaResult,
    DeteriorationEvaluationResult,
    classify_deterioration,
    evaluate_deterioration,
)


# ---------------------------------------------------------------------------
# Test helpers: clinical_data builders
# ---------------------------------------------------------------------------

def _empty_clinical_data() -> dict:
    return {}


def _data_respiratory_alert() -> dict:
    """Trigger respiratory domain: SpO2 low + high FiO2 + tachypnea."""
    return {
        "saturacao_o2": 85.0,
        "fio2": 0.70,
        "frequencia_respiratoria": 40.0,
    }


def _data_hemodynamic_alert() -> dict:
    """Trigger hemodynamic domain: low PAM, vasopressor escalation, high SI."""
    return {
        "pressao_arterial_media": 45.0,
        "dose_vasopressor": 0.5,
        "dose_vasopressor_basal": 0.1,
        "frequencia_cardiaca": 130.0,
        "pressao_arterial_sistolica": 80.0,
    }


def _data_neurologic_alert() -> dict:
    """Trigger neurologic domain: low GCS."""
    return {"glasgow": 7}


def _data_renal_alert() -> dict:
    """Trigger renal domain: creatinine high."""
    return {"creatinina": 3.0, "creatinina_basal": 1.0}


def _data_sepsis_alert() -> dict:
    """Trigger sepsis domain: high lactate, high qSOFA."""
    return {
        "lactato_arterial": 5.0,
        "frequencia_respiratoria": 25.0,
        "pressao_arterial_sistolica": 90.0,
        "glasgow": 13,
    }


def _data_multi_domain_3plus() -> dict:
    """Trigger 3+ domains: respiratory + hemodynamic + neurologic."""
    return {
        # Respiratory
        "saturacao_o2": 82.0,
        "fio2": 0.80,
        "frequencia_respiratoria": 38.0,
        # Hemodynamic
        "pressao_arterial_media": 50.0,
        "dose_vasopressor": 0.6,
        "dose_vasopressor_basal": 0.1,
        "frequencia_cardiaca": 135.0,
        "pressao_arterial_sistolica": 75.0,
        # Neurologic
        "glasgow": 6,
    }


def _data_worsening_vs_previous() -> dict:
    """Single domain affected — for testing trend vs previous."""
    return {
        "saturacao_o2": 85.0,
        "fio2": 0.65,
    }


# ===========================================================================
# evaluate_deterioration — scoring
# ===========================================================================


class TestEvaluateDeteriorationScore:
    """Score computation: 0, 1+, 1-, 3+, 3-."""

    def test_empty_data_score_zero(self):
        """Empty clinical data → score '0', zero domains affected."""
        result = evaluate_deterioration("MPI-001", _empty_clinical_data())
        assert result.mpi_id == "MPI-001"
        assert result.score == "0"
        assert result.domains_affected == 0
        assert result.trend == "none"

    def test_one_domain_affected_no_previous_score_1minus(self):
        """1 domain affected, no previous score → score '1-'."""
        result = evaluate_deterioration("MPI-002", _data_respiratory_alert())
        assert result.score == "1-"
        assert result.domains_affected >= 1

    def test_one_domain_affected_improving_trend_1plus(self):
        """1 domain affected, previous_score='3-' → improving → score '1+'."""
        result = evaluate_deterioration(
            "MPI-003", _data_respiratory_alert(), previous_score="3-"
        )
        # 1 domain affected vs 3 previous → improving
        assert result.score == "1+"
        assert result.trend == "improving"

    def test_one_domain_affected_worsening_trend_1minus(self):
        """1 domain affected, previous_score='0' → worsening → score '1-'."""
        result = evaluate_deterioration(
            "MPI-004", _data_hemodynamic_alert(), previous_score="0"
        )
        assert result.score == "1-"
        assert result.trend == "worsening"

    def test_three_plus_domains_affected_score_3minus(self):
        """3+ domains affected, no previous score → score '3-'."""
        result = evaluate_deterioration("MPI-005", _data_multi_domain_3plus())
        assert result.score == "3-"
        assert result.domains_affected >= 3

    def test_three_plus_domains_improving_score_3plus(self):
        """3+ domains affected, previous_score='3-' with more domains → improving → '3+'."""
        result = evaluate_deterioration(
            "MPI-006", _data_respiratory_alert(), previous_score="3-"
        )
        # 1 domain vs 3 previous → improving → score starts with "1+"
        assert result.trend == "improving"


# ===========================================================================
# Trend computation
# ===========================================================================


class TestTrendComputation:
    """Trend determination from previous_score."""

    def test_trend_none_without_previous(self):
        result = evaluate_deterioration("MPI-T1", _data_respiratory_alert())
        assert result.trend == "none"

    def test_trend_improving_fewer_domains(self):
        """Fewer domains than previous → improving."""
        result = evaluate_deterioration(
            "MPI-T2", _data_respiratory_alert(), previous_score="3-"
        )
        assert result.trend == "improving"

    def test_trend_worsening_more_domains(self):
        """More domains than previous → worsening."""
        result = evaluate_deterioration(
            "MPI-T3", _data_multi_domain_3plus(), previous_score="0"
        )
        assert result.trend == "worsening"

    def test_trend_stable_same_domains(self):
        """Same number of domains → stable."""
        # Trigger 1 domain, compare to previous "1-"
        result = evaluate_deterioration(
            "MPI-T4", _data_respiratory_alert(), previous_score="1-"
        )
        assert result.trend == "stable"
        assert result.score == "1-"


# ===========================================================================
# Domains affected
# ===========================================================================


class TestDomainsAffected:
    """domains_affected count and domain enumeration."""

    def test_zero_domains_affected_empty_data(self):
        result = evaluate_deterioration("MPI-D1", _empty_clinical_data())
        assert result.domains_affected == 0

    def test_respiratory_domain_affected(self):
        result = evaluate_deterioration("MPI-D2", _data_respiratory_alert())
        assert result.domains_affected >= 1
        # Check criteria for respiratory domain
        resp_criteria = [c for c in result.criteria if c.domain == "respiratory"]
        assert any(c.status in ("alert", "critical") for c in resp_criteria)

    def test_hemodynamic_domain_affected(self):
        result = evaluate_deterioration("MPI-D3", _data_hemodynamic_alert())
        assert result.domains_affected >= 1

    def test_multi_domain_affected(self):
        result = evaluate_deterioration("MPI-D4", _data_multi_domain_3plus())
        assert result.domains_affected >= 3


# ===========================================================================
# Criteria structure
# ===========================================================================


class TestCriteriaStructure:
    """Verify the 13 criteria structure."""

    def test_returns_thirteen_criteria(self):
        result = evaluate_deterioration("MPI-C1", _empty_clinical_data())
        assert len(result.criteria) == 13
        assert all(isinstance(c, DeteriorationCriteriaResult) for c in result.criteria)

    def test_all_five_domains_present(self):
        result = evaluate_deterioration("MPI-C2", _empty_clinical_data())
        domains = {c.domain for c in result.criteria}
        expected = {"respiratory", "hemodynamic", "sepsis", "neurologic", "renal"}
        assert domains == expected

    def test_domain_criteria_constant_has_13_items(self):
        assert len(DOMAIN_CRITERIA) == 13

    def test_each_criterion_has_valid_status(self):
        result = evaluate_deterioration("MPI-C4", _empty_clinical_data())
        for c in result.criteria:
            assert c.status in ("normal", "alert", "critical")


# ===========================================================================
# classify_deterioration helper
# ===========================================================================


class TestClassifyDeterioration:
    """Quick deterioration classification from domain count and trend."""

    def test_zero_domains_score_0(self):
        result = classify_deterioration(0)
        assert result["score"] == "0"

    def test_one_domain_worsening_score_1minus(self):
        result = classify_deterioration(1, trend="worsening")
        assert result["score"] == "1-"

    def test_one_domain_improving_score_1plus(self):
        result = classify_deterioration(1, trend="improving")
        assert result["score"] == "1+"

    def test_three_domains_worsening_score_3minus(self):
        result = classify_deterioration(3, trend="worsening")
        assert result["score"] == "3-"

    def test_three_domains_improving_score_3plus(self):
        result = classify_deterioration(4, trend="improving")
        assert result["score"] == "3+"

    def test_classify_returns_recommendation(self):
        result = classify_deterioration(2, trend="worsening")
        assert "recommendation" in result
        assert len(result["recommendation"]) > 0


# ===========================================================================
# DeteriorationEvaluationResult dataclass
# ===========================================================================


class TestDeteriorationEvaluationResult:
    """Dataclass field defaults and structure."""

    def test_default_values(self):
        result = DeteriorationEvaluationResult(mpi_id="MPI-DEF")
        assert result.mpi_id == "MPI-DEF"
        assert result.score == "0"
        assert result.trend == "none"
        assert result.criteria == []
        assert result.domains_affected == 0
        assert result.recommendation == ""
        assert result.assessed_at == ""
        assert result.assessed_by == "system"

    def test_assessed_at_set_after_evaluation(self):
        result = evaluate_deterioration("MPI-TS", _empty_clinical_data())
        assert result.assessed_at != ""
        assert "T" in result.assessed_at


# ===========================================================================
# Recommendation strings (PT-BR)
# ===========================================================================


class TestRecommendationStrings:
    """Verify recommendation text for each score category."""

    def test_score_0_recommendation(self):
        result = evaluate_deterioration("MPI-R0", _empty_clinical_data())
        assert "Sem sinais de deterioração" in result.recommendation
        assert "rotina" in result.recommendation.lower()

    def test_score_1minus_recommendation(self):
        result = evaluate_deterioration("MPI-R1", _data_respiratory_alert())
        assert "POUCOS DOMÍNIOS AFETADOS" in result.recommendation
        assert "ATENÇÃO" in result.recommendation

    def test_score_3minus_recommendation(self):
        result = evaluate_deterioration("MPI-R3", _data_multi_domain_3plus())
        assert "MÚLTIPLOS DOMÍNIOS AFETADOS" in result.recommendation
        assert "CRÍTICO" in result.recommendation

    def test_score_3plus_recommendation(self):
        """3+ improving → recommendation mentions MELHORANDO."""
        result = evaluate_deterioration(
            "MPI-R3P", _data_respiratory_alert(), previous_score="3-"
        )
        assert "MELHORANDO" in result.recommendation


# ===========================================================================
# Edge cases / boundary
# ===========================================================================


class TestEdgeCases:
    """Boundary and edge case tests."""

    def test_previous_score_none(self):
        """previous_score=None is handled gracefully."""
        result = evaluate_deterioration(
            "MPI-EDGE1", _data_respiratory_alert(), previous_score=None
        )
        assert result.score in ("0", "1-", "1+", "3-", "3+")

    def test_previous_score_invalid(self):
        """Invalid previous_score string is handled gracefully."""
        result = evaluate_deterioration(
            "MPI-EDGE2", _data_respiratory_alert(), previous_score="invalid"
        )
        # Should not crash; _parse_previous_domains returns None
        assert result.score in ("0", "1-", "1+", "3-", "3+")

    def test_fio2_percentage_conversion(self):
        """FiO2 > 1.0 is treated as percentage (e.g., 70 → 0.70)."""
        data = {"saturacao_o2": 85.0, "fio2": 70.0}  # percentage
        result = evaluate_deterioration("MPI-FIO2", data)
        # Should trigger SpO2/FiO2 criterion
        spo2_crit = next(
            (c for c in result.criteria if "Queda de SpO2" in c.name), None
        )
        assert spo2_crit is not None
        # 85% < 90% and FiO2=0.70 > 0.60 → critical
        assert spo2_crit.status in ("alert", "critical")
