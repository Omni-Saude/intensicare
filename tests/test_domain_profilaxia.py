"""
Tests for Prophylaxis Bundles domain.

Covers:
- evaluate_all_bundles: overall_status (all_complete, partial, all_pending)
- evaluate_bundle: individual bundle status (complete, partial, pending, na)
- get_bundle_catalog: returns correct criteria for each bundle
- BUNDLE_CATALOG: has 5 bundles with correct structure
- compute_score_and_status: edge cases
- compute_overall: aggregate scoring
"""

from __future__ import annotations

import pytest

from intensicare.services.domain_profilaxia import (
    BUNDLE_CATALOG,
    BundleResult,
    BundlesResult,
    CriterionResult,
    build_default_criteria,
    compute_overall,
    compute_score_and_status,
    evaluate_all_bundles,
    evaluate_bundle,
    get_bundle_catalog,
)

# ===========================================================================
# BUNDLE_CATALOG constant
# ===========================================================================


class TestBundleCatalogConstant:
    """Verify the module-level BUNDLE_CATALOG constant."""

    def test_catalog_has_five_bundles(self):
        """BUNDLE_CATALOG must contain exactly 5 bundles."""
        assert len(BUNDLE_CATALOG) == 5

    def test_expected_bundle_ids_present(self):
        """All 5 expected bundle IDs must be present."""
        expected_ids = {"lamgd", "tev", "hiperglicemia", "mobilizacao", "dispositivos"}
        assert set(BUNDLE_CATALOG.keys()) == expected_ids

    def test_each_bundle_has_name_and_criteria(self):
        """Every bundle must have a name field and a criteria list."""
        for bid, bdef in BUNDLE_CATALOG.items():
            assert "name" in bdef, f"Missing 'name' in bundle {bid}"
            assert "criteria" in bdef, f"Missing 'criteria' in bundle {bid}"
            assert isinstance(bdef["criteria"], list)
            assert len(bdef["criteria"]) > 0

    def test_lamgd_has_four_criteria(self):
        """LAMGD bundle must have 4 criteria."""
        assert len(BUNDLE_CATALOG["lamgd"]["criteria"]) == 4

    def test_tev_has_five_criteria(self):
        """TEV bundle must have 5 criteria."""
        assert len(BUNDLE_CATALOG["tev"]["criteria"]) == 5

    def test_hiperglicemia_has_three_criteria(self):
        """Hiperglicemia bundle must have 3 criteria."""
        assert len(BUNDLE_CATALOG["hiperglicemia"]["criteria"]) == 3

    def test_mobilizacao_has_three_criteria(self):
        """Mobilizacao bundle must have 3 criteria."""
        assert len(BUNDLE_CATALOG["mobilizacao"]["criteria"]) == 3

    def test_dispositivos_has_five_criteria(self):
        """Dispositivos bundle must have 5 criteria."""
        assert len(BUNDLE_CATALOG["dispositivos"]["criteria"]) == 5

    def test_each_criterion_has_id_label_and_na_default(self):
        """Every criterion must have id, label, and na_default fields."""
        for bid, bdef in BUNDLE_CATALOG.items():
            for crit in bdef["criteria"]:
                assert "id" in crit, f"Missing 'id' in {bid} criterion"
                assert "label" in crit, f"Missing 'label' in {bid} criterion"
                assert "na_default" in crit, f"Missing 'na_default' in {bid} criterion"
                assert isinstance(crit["na_default"], bool)

    def test_dispositivos_criteria_all_na_default_true(self):
        """All 'dispositivos' criteria have na_default=True."""
        for crit in BUNDLE_CATALOG["dispositivos"]["criteria"]:
            assert crit["na_default"] is True, f"{crit['id']} should be na_default=True"

    def test_other_bundles_na_default_false(self):
        """All non-dispositivos bundles have na_default=False."""
        for bid in ("lamgd", "tev", "hiperglicemia", "mobilizacao"):
            for crit in BUNDLE_CATALOG[bid]["criteria"]:
                assert crit["na_default"] is False, (
                    f"{crit['id']} in {bid} should be na_default=False"
                )


# ===========================================================================
# build_default_criteria
# ===========================================================================


class TestBuildDefaultCriteria:
    """Verify default criteria builder from catalog."""

    def test_lamgd_defaults(self):
        """LAMGD should return 4 criteria, all met=False, na=False."""
        criteria = build_default_criteria("lamgd")
        assert len(criteria) == 4
        for c in criteria:
            assert c.met is False
            assert c.na is False

    def test_dispositivos_defaults_all_na(self):
        """Dispositivos should have all criteria na=True by default."""
        criteria = build_default_criteria("dispositivos")
        assert len(criteria) == 5
        for c in criteria:
            assert c.na is True

    def test_unknown_bundle_id_raises(self):
        """Unknown bundle_id must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown bundle_id"):
            build_default_criteria("invalid_bundle")


# ===========================================================================
# evaluate_bundle — individual bundle evaluation
# ===========================================================================


class TestEvaluateBundle:
    """Test individual bundle evaluation with various inputs."""

    # ------------------------------------------------------------------
    # complete (100%)
    # ------------------------------------------------------------------

    def test_lamgd_all_met_complete(self):
        """When all LAMGD criteria are met → status 'complete'."""
        inputs = [
            {"id": "lamgd-vm", "met": True},
            {"id": "lamgd-coag", "met": True},
            {"id": "lamgd-choque", "met": True},
            {"id": "lamgd-cortico", "met": True},
        ]
        result = evaluate_bundle("lamgd", inputs)
        assert result.status == "complete"
        assert result.score == 100

    # ------------------------------------------------------------------
    # partial (>0% <100%)
    # ------------------------------------------------------------------

    def test_lamgd_partial_two_of_four(self):
        """2 of 4 LAMGD criteria met → status 'partial'."""
        inputs = [
            {"id": "lamgd-vm", "met": True},
            {"id": "lamgd-coag", "met": True},
            {"id": "lamgd-choque", "met": False},
            {"id": "lamgd-cortico", "met": False},
        ]
        result = evaluate_bundle("lamgd", inputs)
        assert result.status == "partial"
        assert result.score == 50

    def test_tev_partial_one_of_five(self):
        """1 of 5 TEV criteria met → status 'partial'."""
        inputs = [
            {"id": "tev-heparina", "met": True},
        ]
        result = evaluate_bundle("tev", inputs)
        assert result.status == "partial"
        assert result.score == 20  # 1/5 = 20%

    # ------------------------------------------------------------------
    # pending (0%)
    # ------------------------------------------------------------------

    def test_no_override_pending(self):
        """Without any inputs, all met=False → status 'pending'."""
        result = evaluate_bundle("lamgd")
        assert result.status == "pending"
        assert result.score == 0
        assert all(c.met is False for c in result.criteria)

    def test_all_explicitly_false_pending(self):
        """All criteria explicitly met=False → status 'pending'."""
        inputs = [
            {"id": "lamgd-vm", "met": False},
            {"id": "lamgd-coag", "met": False},
            {"id": "lamgd-choque", "met": False},
            {"id": "lamgd-cortico", "met": False},
        ]
        result = evaluate_bundle("lamgd", inputs)
        assert result.status == "pending"
        assert result.score == 0

    # ------------------------------------------------------------------
    # na (all criteria set to na)
    # ------------------------------------------------------------------

    def test_all_na_status_is_na(self):
        """When all applicable criteria are marked na → status 'na'."""
        inputs = [
            {"id": "lamgd-vm", "na": True},
            {"id": "lamgd-coag", "na": True},
            {"id": "lamgd-choque", "na": True},
            {"id": "lamgd-cortico", "na": True},
        ]
        result = evaluate_bundle("lamgd", inputs)
        assert result.status == "na"

    def test_dispositivos_default_na_status_is_na(self):
        """Dispositivos with default na=True for all criteria → 'na'."""
        result = evaluate_bundle("dispositivos")
        assert result.status == "na"

    # ------------------------------------------------------------------
    # Mixed na + met (partial)
    # ------------------------------------------------------------------

    def test_partial_with_some_na(self):
        """Some criteria na, some met → score based on applicable only."""
        inputs = [
            {"id": "lamgd-vm", "met": True},
            {"id": "lamgd-coag", "met": False},
            {"id": "lamgd-choque", "na": True},
            {"id": "lamgd-cortico", "na": True},
        ]
        result = evaluate_bundle("lamgd", inputs)
        # Applicable: lamgd-vm (met), lamgd-coag (not met) → 1/2 = 50%
        assert result.status == "partial"
        assert result.score == 50

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_unknown_criterion_in_inputs_ignored(self):
        """Unknown criterion IDs in inputs are silently ignored."""
        inputs = [
            {"id": "nonexistent-crit", "met": True},
        ]
        result = evaluate_bundle("lamgd", inputs)
        assert result.status == "pending"
        assert result.score == 0

    def test_input_without_id_ignored(self):
        """Input dict without 'id' key is ignored."""
        inputs = [
            {"met": True},
        ]
        result = evaluate_bundle("lamgd", inputs)
        assert result.status == "pending"

    def test_result_name_matches_catalog(self):
        """BundleResult.name should match the catalog definition."""
        result = evaluate_bundle("tev")
        assert result.name == BUNDLE_CATALOG["tev"]["name"]

    def test_unknown_bundle_id_raises(self):
        """Unknown bundle_id must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown bundle_id"):
            evaluate_bundle("invalid_bundle")


# ===========================================================================
# evaluate_all_bundles — aggregate evaluation
# ===========================================================================


class TestEvaluateAllBundles:
    """Test the evaluate_all_bundles function with different combinations."""

    # ------------------------------------------------------------------
    # all_complete
    # ------------------------------------------------------------------

    def test_all_bundles_full_met_all_complete(self):
        """When every criterion in every bundle is met → all_complete."""
        bundle_inputs = {}
        for bid, bdef in BUNDLE_CATALOG.items():
            bundle_inputs[bid] = [
                {"id": c["id"], "met": True, "na": c.get("na_default", False)}
                for c in bdef["criteria"]
            ]
        # For dispositivos, na_default=True, so even if met=False, let's set met=True too
        # and ensure na stays True — that makes it "na" not "complete"
        # Actually for all_complete we need non-dispositivos complete
        # Let's override dispositivos to have na=False and met=True
        bundle_inputs["dispositivos"] = [
            {"id": c["id"], "met": True, "na": False}
            for c in BUNDLE_CATALOG["dispositivos"]["criteria"]
        ]
        result = evaluate_all_bundles(bundle_inputs)
        assert result.overall_status == "all_complete"
        assert result.overall_score == 100
        assert len(result.bundles) == 5

    def test_all_bundles_met_except_dispositivos_na(self):
        """Non-na bundles all complete, dispositivos is na → overall partial."""
        bundle_inputs = {}
        for bid in ("lamgd", "tev", "hiperglicemia", "mobilizacao"):
            bundle_inputs[bid] = [
                {"id": c["id"], "met": True} for c in BUNDLE_CATALOG[bid]["criteria"]
            ]
        # dispositivos stays default (all na)
        result = evaluate_all_bundles(bundle_inputs)
        # 4 complete + 1 na → not all_complete (na has score 0)
        assert result.overall_status == "partial"

    # ------------------------------------------------------------------
    # all_pending
    # ------------------------------------------------------------------

    def test_no_inputs_all_pending(self):
        """With no inputs, all bundles have score 0 → all_pending."""
        result = evaluate_all_bundles()
        assert result.overall_status == "all_pending"
        assert result.overall_score == 0
        for b in result.bundles:
            if b.id == "dispositivos":
                assert b.status == "na"  # dispositivos defaults to na
            else:
                assert b.status == "pending"

    def test_all_explicitly_met_false_all_pending(self):
        """All criteria explicitly met=False (non-na bundles) → all_pending."""
        bundle_inputs = {}
        for bid in ("lamgd", "tev", "hiperglicemia", "mobilizacao"):
            bundle_inputs[bid] = [
                {"id": c["id"], "met": False} for c in BUNDLE_CATALOG[bid]["criteria"]
            ]
        # For dispositivos, force na=False too (otherwise it's "na", not "pending")
        bundle_inputs["dispositivos"] = [
            {"id": c["id"], "met": False, "na": False}
            for c in BUNDLE_CATALOG["dispositivos"]["criteria"]
        ]
        result = evaluate_all_bundles(bundle_inputs)
        assert result.overall_status == "all_pending"
        assert result.overall_score == 0

    # ------------------------------------------------------------------
    # partial
    # ------------------------------------------------------------------

    def test_mixed_complete_and_pending_partial(self):
        """Some bundles complete, some pending → partial."""
        bundle_inputs = {
            "lamgd": [{"id": c["id"], "met": True} for c in BUNDLE_CATALOG["lamgd"]["criteria"]],
        }
        result = evaluate_all_bundles(bundle_inputs)
        assert result.overall_status == "partial"

    def test_one_bundle_partial_others_pending(self):
        """One bundle at 50%, others 0% → partial."""
        bundle_inputs = {
            "tev": [
                {"id": "tev-heparina", "met": True},
                {"id": "tev-deamb", "met": True},
            ],
        }
        result = evaluate_all_bundles(bundle_inputs)
        assert result.overall_status == "partial"
        # TEV: 2/5 = 40%, others: 0% → avg = 40/5 = 8
        assert result.overall_score == 8

    # ------------------------------------------------------------------
    # Edge cases with empty inputs
    # ------------------------------------------------------------------

    def test_empty_dict_inputs(self):
        """Empty bundle_inputs dict → same as None."""
        result = evaluate_all_bundles({})
        assert len(result.bundles) == 5

    def test_partial_bundle_inputs_only_some(self):
        """Only providing inputs for some bundles, others default."""
        bundle_inputs = {
            "lamgd": [
                {"id": "lamgd-vm", "met": True},
            ],
        }
        result = evaluate_all_bundles(bundle_inputs)
        lamgd = next(b for b in result.bundles if b.id == "lamgd")
        assert lamgd.status == "partial"
        assert lamgd.score == 25  # 1/4


# ===========================================================================
# compute_score_and_status — unit-level
# ===========================================================================


class TestComputeScoreAndStatus:
    """Direct tests for the scoring helper."""

    def test_all_met_complete(self):
        criteria = [
            CriterionResult(id="a", label="A", met=True),
            CriterionResult(id="b", label="B", met=True),
        ]
        score, status = compute_score_and_status(criteria)
        assert status == "complete"
        assert score == 100

    def test_none_met_pending(self):
        criteria = [
            CriterionResult(id="a", label="A", met=False),
            CriterionResult(id="b", label="B", met=False),
        ]
        score, status = compute_score_and_status(criteria)
        assert status == "pending"
        assert score == 0

    def test_some_met_partial(self):
        criteria = [
            CriterionResult(id="a", label="A", met=True),
            CriterionResult(id="b", label="B", met=False),
        ]
        score, status = compute_score_and_status(criteria)
        assert status == "partial"
        assert score == 50

    def test_all_na_status_is_na(self):
        """When all criteria are na, status is 'na'."""
        criteria = [
            CriterionResult(id="a", label="A", met=True, na=True),
            CriterionResult(id="b", label="B", met=True, na=True),
            CriterionResult(id="c", label="C", met=False, na=True),
        ]
        score, status = compute_score_and_status(criteria)
        assert status == "na"
        assert score == 0  # no applicable criteria

    def test_rounding_down(self):
        """Score should round to nearest integer (round half to even)."""
        # 1 met out of 3 applicable → 33.33... → round = 33
        criteria = [
            CriterionResult(id="a", label="A", met=True),
            CriterionResult(id="b", label="B", met=False),
            CriterionResult(id="c", label="C", met=False),
        ]
        score, _status = compute_score_and_status(criteria)
        assert score == 33

    def test_rounding_up(self):
        """2 met out of 3 applicable → 66.67 → round = 67."""
        criteria = [
            CriterionResult(id="a", label="A", met=True),
            CriterionResult(id="b", label="B", met=True),
            CriterionResult(id="c", label="C", met=False),
        ]
        score, _status = compute_score_and_status(criteria)
        assert score == 67

    def test_mixed_na_with_met(self):
        """Some na, one met → 100% on applicable."""
        criteria = [
            CriterionResult(id="a", label="A", met=True),
            CriterionResult(id="b", label="B", met=False, na=True),
            CriterionResult(id="c", label="C", met=False, na=True),
        ]
        score, status = compute_score_and_status(criteria)
        assert status == "complete"
        assert score == 100  # 1 applicable, 1 met


# ===========================================================================
# compute_overall — aggregate
# ===========================================================================


class TestComputeOverall:
    """Direct tests for the overall scoring helper."""

    def test_all_complete(self):
        bundles = [
            BundleResult(id="lamgd", name="LAMGD", status="complete", score=100),
            BundleResult(id="tev", name="TEV", status="complete", score=100),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "all_complete"
        assert overall_score == 100

    def test_all_pending(self):
        bundles = [
            BundleResult(id="lamgd", name="LAMGD", status="pending", score=0),
            BundleResult(id="tev", name="TEV", status="pending", score=0),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "all_pending"
        assert overall_score == 0

    def test_partial_mixed(self):
        bundles = [
            BundleResult(id="lamgd", name="LAMGD", status="complete", score=100),
            BundleResult(id="tev", name="TEV", status="pending", score=0),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "partial"
        assert overall_score == 50

    def test_empty_bundles_list(self):
        """Empty list → all_pending, score 0."""
        overall_status, overall_score = compute_overall([])
        assert overall_status == "all_pending"
        assert overall_score == 0

    def test_five_bundles_average(self):
        """Average of 5 bundle scores."""
        bundles = [
            BundleResult(id="lamgd", name="LAMGD", status="complete", score=100),
            BundleResult(id="tev", name="TEV", status="partial", score=50),
            BundleResult(id="hiperglicemia", name="HG", status="pending", score=0),
            BundleResult(id="mobilizacao", name="MOB", status="complete", score=100),
            BundleResult(id="dispositivos", name="DISP", status="na", score=0),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "partial"
        # (100+50+0+100+0)/5 = 250/5 = 50
        assert overall_score == 50


# ===========================================================================
# get_bundle_catalog
# ===========================================================================


class TestGetBundleCatalog:
    """Verify the catalog helper function."""

    def test_get_all_returns_five_bundles(self):
        """get_bundle_catalog() without bundle_id returns all 5 bundles."""
        catalog = get_bundle_catalog()
        assert len(catalog) == 5
        assert set(catalog.keys()) == set(BUNDLE_CATALOG.keys())

    def test_get_specific_bundle(self):
        """get_bundle_catalog(bundle_id='lamgd') returns correct definition."""
        result = get_bundle_catalog("lamgd")
        assert result["bundle_id"] == "lamgd"
        assert result["bundle_name"] == "LAMGD — Úlcera de Estresse"
        assert len(result["criteria"]) == 4

    def test_all_bundle_keys_present_in_specific_result(self):
        """A specific bundle result must have bundle_id, bundle_name, criteria."""
        for bid in BUNDLE_CATALOG:
            result = get_bundle_catalog(bid)
            for key in ("bundle_id", "bundle_name", "criteria"):
                assert key in result, f"Missing '{key}' in {bid}"

    def test_unknown_bundle_raises_error(self):
        """Requesting an unknown bundle must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown bundle_id"):
            get_bundle_catalog("unknown_bundle")

    def test_get_all_returns_copy_not_reference(self):
        """Catalog dict from get_bundle_catalog is a copy."""
        catalog = get_bundle_catalog()
        # Mutating should not affect the original
        catalog["fake"] = {}
        assert "fake" not in BUNDLE_CATALOG


# ===========================================================================
# BundleResult and BundlesResult dataclasses
# ===========================================================================


class TestBundleResultDataclass:
    """Verify BundleResult dataclass defaults."""

    def test_default_criteria_empty(self):
        result = BundleResult(id="test", name="Test", status="pending")
        assert result.criteria == []

    def test_default_score_zero(self):
        result = BundleResult(id="test", name="Test", status="pending")
        assert result.score == 0


class TestBundlesResultDataclass:
    """Verify BundlesResult dataclass defaults."""

    def test_default_bundles_empty(self):
        result = BundlesResult()
        assert result.bundles == []

    def test_default_overall_status_all_pending(self):
        result = BundlesResult()
        assert result.overall_status == "all_pending"

    def test_default_overall_score_zero(self):
        result = BundlesResult()
        assert result.overall_score == 0
