"""Tests for Efficiency & Stewardship domain — 12+ tests.

Covers:
- assess_efficiency with complete data
- 12 transfusion criteria defined in catalog
- Hb pre/post documentation check
- Restraint >4h detection
- Frailty CFS scoring 1-9 categories
- LOS outlier detection (>1.5x expected)
- Recommendation generation in PT-BR
- Empty data → safe behavior for all evaluators
"""

from __future__ import annotations

import pytest

from intensicare.services.domain_eficiencia import (
    CATEGORY_LABELS,
    TRANSFUSION_CRITERIA,
    EfficiencyAssessment,
    FrailtyScale,
    RestraintStatus,
    TransfusionCriterionResult,
    _build_recommendation,
    assess_efficiency,
    evaluate_frailty,
    evaluate_los,
    evaluate_restraint,
    evaluate_transfusion_criteria,
    get_transfusion_categories,
    get_transfusion_criteria_catalog,
)


# ============================================================================
# Transfusion Criteria Catalog — 12 items
# ============================================================================


class TestTransfusionCriteriaCatalog:
    """Verify the 12-item transfusion criteria catalog."""

    def test_catalog_has_12_criteria(self):
        """Exactly 12 transfusion-appropriateness criteria defined."""
        assert len(TRANSFUSION_CRITERIA) == 12

    def test_all_criteria_have_code_description_category_detail(self):
        """Every criterion has the four required fields."""
        for c in TRANSFUSION_CRITERIA:
            assert "code" in c
            assert "description" in c
            assert "category" in c
            assert "detail" in c
            assert isinstance(c["code"], str)
            assert isinstance(c["description"], str)
            assert isinstance(c["category"], str)
            assert isinstance(c["detail"], str)

    def test_criteria_codes_follow_tf_pattern(self):
        """All criteria codes use the TF-NNN pattern."""
        for c in TRANSFUSION_CRITERIA:
            assert c["code"].startswith("TF-")
            num = int(c["code"].split("-")[1])
            assert 1 <= num <= 12

    def test_distinct_categories_present(self):
        """Catalog spans multiple clinical categories."""
        categories = {c["category"] for c in TRANSFUSION_CRITERIA}
        assert len(categories) >= 4  # hb_threshold, symptomatic_anemia, etc.

    def test_get_transfusion_criteria_catalog_returns_copy(self):
        """Catalog helper returns a list of new dicts (not a reference)."""
        catalog = get_transfusion_criteria_catalog()
        assert len(catalog) == 12
        # Mutating the returned list must not affect the original
        catalog.append({"code": "TF-999", "description": "fake"})
        assert len(TRANSFUSION_CRITERIA) == 12

    def test_get_transfusion_categories_returns_label_map(self):
        """Categories helper returns the label map."""
        labels = get_transfusion_categories()
        assert isinstance(labels, dict)
        assert "hb_threshold" in labels
        assert labels["hb_threshold"] == "Limiar de Hb"


# ============================================================================
# evaluate_transfusion_criteria
# ============================================================================


class TestEvaluateTransfusionCriteria:
    """Tests for evaluate_transfusion_criteria()."""

    def test_empty_inputs_all_not_met(self):
        """With no inputs, most criteria are unmet → appropriate=False.

        TF-003 (single-unit, units defaults to 0) and TF-006 (no reaction)
        happen to be met by default, but overall it's still not appropriate.
        """
        result = evaluate_transfusion_criteria(None)
        assert result["total"] == 12
        assert result["met_count"] == 2  # TF-003 and TF-006 default to met
        assert result["appropriate"] is False
        assert len(result["criteria"]) == 12

    def test_hb_documentation_check_tf001(self):
        """TF-001: Hb pre-transfusional documentation — met when hb_pre provided."""
        result = evaluate_transfusion_criteria({"hb_pre": 8.5})
        tf001 = next(c for c in result["criteria"] if c["code"] == "TF-001")
        assert tf001["met"] is True
        assert "8.5" in tf001["detail"]

    def test_hb_post_documentation_tf005(self):
        """TF-005: Hb post-transfusional documentation — met when hb_post provided."""
        result = evaluate_transfusion_criteria({"hb_pre": 7.2, "hb_post": 9.1})
        tf005 = next(c for c in result["criteria"] if c["code"] == "TF-005")
        assert tf005["met"] is True
        assert "9.1" in tf005["detail"]

    def test_hb_threshold_restrictive_tf002(self):
        """TF-002: Met when Hb >= 7.0 (restrictive trigger respected)."""
        result = evaluate_transfusion_criteria({"hb_pre": 7.5})
        tf002 = next(c for c in result["criteria"] if c["code"] == "TF-002")
        assert tf002["met"] is True

    def test_single_unit_strategy_tf003(self):
        """TF-003: Single-unit transfusion strategy — met when ≤1 unit."""
        result = evaluate_transfusion_criteria({"hb_pre": 6.8, "units": 1})
        tf003 = next(c for c in result["criteria"] if c["code"] == "TF-003")
        assert tf003["met"] is True

    def test_infusion_time_within_4h_tf012(self):
        """TF-012: Infusion ≤ 240 minutes is met."""
        result = evaluate_transfusion_criteria({"infusion_time_min": 180})
        tf012 = next(c for c in result["criteria"] if c["code"] == "TF-012")
        assert tf012["met"] is True

    def test_infusion_time_exceeds_4h_tf012(self):
        """TF-012: Infusion > 240 minutes is NOT met."""
        result = evaluate_transfusion_criteria({"infusion_time_min": 300})
        tf012 = next(c for c in result["criteria"] if c["code"] == "TF-012")
        assert tf012["met"] is False

    def test_all_criteria_met_count(self):
        """With all optimal inputs, ≥8 of 12 criteria are met → appropriate=True."""
        result = evaluate_transfusion_criteria({
            "hb_pre": 7.5,
            "hb_post": 9.0,
            "units": 1,
            "reassessed_6h": True,
            "reaction": False,
            "indication_documented": True,
            "consent_signed": True,
            "patient_id_checked": True,
            "abo_rh_confirmed": True,
            "cold_chain_ok": True,
            "infusion_time_min": 120,
        })
        assert result["met_count"] >= 8
        assert result["appropriate"] is True

    def test_empty_dict_same_as_none(self):
        """Empty dict {} behaves identically to None."""
        r1 = evaluate_transfusion_criteria(None)
        r2 = evaluate_transfusion_criteria({})
        assert r1["met_count"] == r2["met_count"]
        assert r1["appropriate"] == r2["appropriate"]


# ============================================================================
# evaluate_restraint
# ============================================================================


class TestEvaluateRestraint:
    """Tests for evaluate_restraint()."""

    def test_no_restraint_returns_none_status(self):
        """When not active, status is NONE and duration check is met."""
        result = evaluate_restraint({"active": False})
        assert result["active"] is False
        assert result["status"] == RestraintStatus.NONE.value

    def test_restraint_within_4h(self):
        """Restraint active ≤ 4h — duration_within_limit is True."""
        result = evaluate_restraint({
            "active": True,
            "duration_hours": 3.5,
            "reassessed_today": True,
        })
        assert result["active"] is True
        assert result["criteria_met"]["duration_within_limit"] is True
        assert result["criteria_met"]["daily_reassessment"] is True

    def test_restraint_exceeds_4h_detection(self):
        """Restraint active > 4h — duration_within_limit is False."""
        result = evaluate_restraint({
            "active": True,
            "duration_hours": 6.0,
            "reassessed_today": False,
        })
        assert result["active"] is True
        assert result["duration_hours"] == 6.0
        assert result["criteria_met"]["duration_within_limit"] is False
        assert result["criteria_met"]["daily_reassessment"] is False

    def test_restraint_empty_inputs_safe(self):
        """Empty inputs → active=False, duration=0, safe defaults."""
        result = evaluate_restraint(None)
        assert result["active"] is False
        assert result["duration_hours"] == 0.0
        assert result["criteria_met"]["duration_within_limit"] is True
        assert result["criteria_met"]["daily_reassessment"] is False


# ============================================================================
# evaluate_frailty — CFS 1-9
# ============================================================================


class TestEvaluateFrailty:
    """Tests for evaluate_frailty() CFG scoring."""

    def test_frailty_not_assessed_returns_none(self):
        """When cfs_score is None, assessed=False and category indicates not assessed."""
        result = evaluate_frailty(None)
        assert result["cfs_score"] is None
        assert result["assessed"] is False
        assert result["category"] == "não avaliada"

    def test_cfs_1_to_3_robusto(self):
        """CFS 1-3 → 'Robusto'."""
        for score in (1, 2, 3):
            result = evaluate_frailty({"cfs_score": score})
            assert result["cfs_score"] == score
            assert result["category"] == "Robusto"
            assert result["assessed"] is True

    def test_cfs_4_vulneravel(self):
        """CFS 4 → 'Vulnerável'."""
        result = evaluate_frailty({"cfs_score": 4})
        assert result["category"] == "Vulnerável"

    def test_cfs_5_to_6_fragil(self):
        """CFS 5-6 → 'Frágil'."""
        for score in (5, 6):
            result = evaluate_frailty({"cfs_score": score})
            assert result["category"] == "Frágil"

    def test_cfs_7_to_8_muito_fragil(self):
        """CFS 7-8 → 'Muito frágil'."""
        for score in (7, 8):
            result = evaluate_frailty({"cfs_score": score})
            assert result["category"] == "Muito frágil"

    def test_cfs_9_terminal(self):
        """CFS 9 → 'Terminal'."""
        result = evaluate_frailty({"cfs_score": 9})
        assert result["category"] == "Terminal"

    def test_cfs_with_scale_override(self):
        """Custom scale (e.g., mFI) is preserved."""
        result = evaluate_frailty({"cfs_score": 5, "scale": "mFI"})
        assert result["scale"] == "mFI"
        assert result["cfs_score"] == 5


# ============================================================================
# evaluate_los — ICU LOS outlier detection
# ============================================================================


class TestEvaluateLOS:
    """Tests for evaluate_los() benchmarking."""

    def test_los_within_expected_range(self):
        """5 days vs expected 7 → not an outlier (5 ≤ 10.5)."""
        result = evaluate_los({"days": 5, "expected_days": 7})
        assert result["is_outlier"] is False

    def test_los_exceeds_1_5x_expected(self):
        """12 days vs expected 7 → outlier (12 > 10.5)."""
        result = evaluate_los({"days": 12, "expected_days": 7})
        assert result["is_outlier"] is True

    def test_los_boundary_exact_1_5x_not_outlier(self):
        """Exactly 1.5x expected is NOT an outlier (> is strict)."""
        result = evaluate_los({"days": 10.5, "expected_days": 7})
        assert result["is_outlier"] is False

    def test_los_boundary_just_above_1_5x_is_outlier(self):
        """Just above 1.5x → outlier."""
        result = evaluate_los({"days": 10.5001, "expected_days": 7})
        assert result["is_outlier"] is True

    def test_los_no_benchmark_defaults_to_14_days(self):
        """Without expected_days, >14 days → outlier."""
        result = evaluate_los({"days": 15})
        assert result["is_outlier"] is True

    def test_los_no_benchmark_under_14_not_outlier(self):
        """Without expected_days, ≤14 days → not outlier."""
        result = evaluate_los({"days": 10})
        assert result["is_outlier"] is False

    def test_los_empty_inputs_safe(self):
        """Empty inputs → days=0, not outlier."""
        result = evaluate_los(None)
        assert result["days"] == 0.0
        assert result["is_outlier"] is False


# ============================================================================
# _build_recommendation — PT-BR
# ============================================================================


class TestBuildRecommendation:
    """Tests for _build_recommendation() PT-BR output."""

    def test_recommendation_transfusion_appropriate(self):
        """When transfusion is appropriate, recommendation says 'dentro dos critérios'."""
        rec = _build_recommendation(
            transfusion_appropriate=True,
            restraint_active=False,
            restraint_duration_hours=0,
            cfs_score=None,
            los_is_outlier=False,
        )
        assert "dentro dos critérios" in rec
        assert "Manter monitorização" in rec

    def test_recommendation_transfusion_not_appropriate(self):
        """When transfusion is NOT appropriate, recommendation calls for audit."""
        rec = _build_recommendation(
            transfusion_appropriate=False,
            restraint_active=False,
            restraint_duration_hours=0,
            cfs_score=None,
            los_is_outlier=False,
        )
        assert "Revisar protocolo transfusional" in rec
        assert "critérios de adequação não atendidos" in rec

    def test_recommendation_restraint_over_4h(self):
        """Active restraint > 4h triggers re-evaluation recommendation."""
        rec = _build_recommendation(
            transfusion_appropriate=True,
            restraint_active=True,
            restraint_duration_hours=5.5,
            cfs_score=None,
            los_is_outlier=False,
        )
        assert "reavaliar necessidade" in rec
        assert "5.5h" in rec

    def test_recommendation_restraint_active_under_4h(self):
        """Active restraint ≤ 4h → programar reavalição."""
        rec = _build_recommendation(
            transfusion_appropriate=True,
            restraint_active=True,
            restraint_duration_hours=2.0,
            cfs_score=None,
            los_is_outlier=False,
        )
        assert "programar reavaliação em 4h" in rec

    def test_recommendation_frailty_cfs_high(self):
        """CFS ≥ 5 → fragility warning."""
        rec = _build_recommendation(
            transfusion_appropriate=True,
            restraint_active=False,
            restraint_duration_hours=0,
            cfs_score=6,
            los_is_outlier=False,
        )
        assert "paciente frágil" in rec
        assert "CFS 6" in rec

    def test_recommendation_frailty_cfs_low(self):
        """CFS < 5 → within expected range."""
        rec = _build_recommendation(
            transfusion_appropriate=True,
            restraint_active=False,
            restraint_duration_hours=0,
            cfs_score=3,
            los_is_outlier=False,
        )
        assert "dentro do esperado" in rec

    def test_recommendation_los_outlier(self):
        """LOS outlier → review barriers."""
        rec = _build_recommendation(
            transfusion_appropriate=True,
            restraint_active=False,
            restraint_duration_hours=0,
            cfs_score=None,
            los_is_outlier=True,
        )
        assert "Tempo de permanência na UTI acima do benchmark" in rec
        assert "Revisar barreiras de alta" in rec

    def test_recommendation_combined_all_flags(self):
        """All flags active → comprehensive recommendation."""
        rec = _build_recommendation(
            transfusion_appropriate=False,
            restraint_active=True,
            restraint_duration_hours=7.0,
            cfs_score=7,
            los_is_outlier=True,
        )
        assert "Revisar protocolo transfusional" in rec
        assert "Contenção mecânica ativa" in rec
        assert "CFS 7" in rec
        assert "acima do benchmark" in rec


# ============================================================================
# assess_efficiency — full integration
# ============================================================================


class TestAssessEfficiency:
    """Integration tests for assess_efficiency()."""

    def test_assess_efficiency_with_complete_data(self):
        """Full assessment with all domains populated returns complete result."""
        result = assess_efficiency(
            mpi_id="PAT-001",
            transfusion_inputs={
                "hb_pre": 7.5,
                "hb_post": 9.0,
                "units": 1,
                "reassessed_6h": True,
                "reaction": False,
                "indication_documented": True,
                "consent_signed": True,
                "patient_id_checked": True,
                "abo_rh_confirmed": True,
                "cold_chain_ok": True,
                "infusion_time_min": 180,
            },
            restraint_inputs={
                "active": False,
                "duration_hours": 0,
                "reassessed_today": True,
            },
            frailty_inputs={"cfs_score": 3},
            los_inputs={"days": 5, "expected_days": 7},
        )

        assert isinstance(result, EfficiencyAssessment)
        assert result.mpi_id == "PAT-001"
        assert result.transfusion["total"] == 12
        assert result.transfusion["appropriate"] is True
        assert result.restraint["active"] is False
        assert result.frailty["cfs_score"] == 3
        assert result.frailty["category"] == "Robusto"
        assert result.los["is_outlier"] is False
        assert isinstance(result.recommendation, str)
        assert len(result.recommendation) > 0
        assert result.assessed_at is not None
        # PT-BR content check
        assert "dentro dos critérios" in result.recommendation

    def test_assess_efficiency_empty_data_safe(self):
        """Full assessment with no inputs does not crash and returns safe defaults.

        TF-003 and TF-006 default to met even with empty inputs, giving met_count=2.
        """
        result = assess_efficiency(mpi_id="PAT-NODATA")
        assert result.mpi_id == "PAT-NODATA"
        assert result.transfusion["appropriate"] is False
        assert result.transfusion["met_count"] == 2  # TF-003, TF-006 default met
        assert result.restraint["active"] is False
        assert result.frailty["assessed"] is False
        assert result.los["is_outlier"] is False
        assert isinstance(result.recommendation, str)

    def test_assess_efficiency_outlier_los(self):
        """LOS outlier scenario via assess_efficiency."""
        result = assess_efficiency(
            mpi_id="PAT-OUTLIER",
            los_inputs={"days": 20, "expected_days": 7},
        )
        assert result.los["is_outlier"] is True
        assert "acima do benchmark" in result.recommendation

    def test_assess_efficiency_restraint_alert(self):
        """Restraint > 4h detected in full assessment."""
        result = assess_efficiency(
            mpi_id="PAT-RESTRAINT",
            restraint_inputs={
                "active": True,
                "duration_hours": 8,
                "reassessed_today": False,
            },
        )
        assert result.restraint["active"] is True
        assert result.restraint["duration_hours"] == 8.0
        assert result.restraint["criteria_met"]["duration_within_limit"] is False
        assert "reavaliar necessidade" in result.recommendation

    def test_assess_efficiency_frailty_terminal(self):
        """CFS 9 (Terminal) via full assessment."""
        result = assess_efficiency(
            mpi_id="PAT-FRAIL",
            frailty_inputs={"cfs_score": 9},
        )
        assert result.frailty["category"] == "Terminal"
        assert result.frailty["assessed"] is True


# ============================================================================
# Dataclass tests
# ============================================================================


class TestEfficiencyAssessmentDataclass:
    """Verify EfficiencyAssessment defaults and construction."""

    def test_default_assessed_at_is_set(self):
        """assessed_at is auto-populated to current UTC time."""
        obj = EfficiencyAssessment(mpi_id="TEST")
        assert obj.assessed_at is not None
        assert "T" in obj.assessed_at  # ISO 8601

    def test_explicit_assessed_at_respected(self):
        """assessed_at can be passed explicitly."""
        ts = "2025-01-01T00:00:00Z"
        obj = EfficiencyAssessment(mpi_id="TEST", assessed_at=ts)
        assert obj.assessed_at == ts


class TestTransfusionCriterionResult:
    """Verify TransfusionCriterionResult dataclass."""

    def test_construction(self):
        crit = TransfusionCriterionResult(
            code="TF-001",
            description="Hb documentada",
            met=True,
            detail="Hb = 8.0 g/dL",
        )
        assert crit.code == "TF-001"
        assert crit.met is True
        assert crit.detail == "Hb = 8.0 g/dL"

    def test_detail_defaults_to_none(self):
        crit = TransfusionCriterionResult(
            code="TF-999",
            description="Test",
            met=False,
        )
        assert crit.detail is None
