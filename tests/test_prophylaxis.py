"""Unit tests for Prophylaxis Bundles domain logic."""

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


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def _c(id_: str, met: bool = False, na: bool = False) -> CriterionResult:
    """Shorthand to build a CriterionResult."""
    return CriterionResult(id=id_, label=id_, met=met, na=na)


def _br(id_: str, status: str, score: int) -> BundleResult:
    """Shorthand to build a BundleResult."""
    return BundleResult(id=id_, name=id_, status=status, score=score)


# ════════════════════════════════════════════════════════════════════════════
# compute_score_and_status
# ════════════════════════════════════════════════════════════════════════════


class TestComputeScoreAndStatus:
    def test_all_met_complete(self):
        """All applicable criteria met → score 100, status complete."""
        criteria = [
            _c("a", met=True),
            _c("b", met=True),
            _c("c", met=True),
        ]
        score, status = compute_score_and_status(criteria)
        assert score == 100
        assert status == "complete"

    def test_half_met_partial(self):
        """Half met → score 50, status partial."""
        criteria = [
            _c("a", met=True),
            _c("b", met=False),
            _c("c", met=True),
            _c("d", met=False),
        ]
        score, status = compute_score_and_status(criteria)
        assert score == 50
        assert status == "partial"

    def test_none_met_pending(self):
        """No criteria met → score 0, status pending."""
        criteria = [
            _c("a", met=False),
            _c("b", met=False),
        ]
        score, status = compute_score_and_status(criteria)
        assert score == 0
        assert status == "pending"

    def test_all_na_returns_na(self):
        """All criteria na → score 0, status na."""
        criteria = [
            _c("a", na=True),
            _c("b", na=True),
            _c("c", na=True),
        ]
        score, status = compute_score_and_status(criteria)
        assert score == 0
        assert status == "na"

    def test_mixed_na_and_met(self):
        """Mixed na + met: na are excluded, score based on applicable only."""
        criteria = [
            _c("a", met=True),       # applicable, met
            _c("b", na=True),          # excluded
            _c("c", met=False),        # applicable, not met
            _c("d", na=True),          # excluded
        ]
        # applicable = a + c (2); met = a (1) → 1/2 = 50%
        score, status = compute_score_and_status(criteria)
        assert score == 50
        assert status == "partial"

    def test_single_met_rounding(self):
        """Score should be rounded to nearest integer."""
        # 1 met out of 3 applicable → 33.33... → rounds to 33
        criteria = [
            _c("a", met=True),
            _c("b", met=False),
            _c("c", met=False),
        ]
        score, status = compute_score_and_status(criteria)
        assert score == 33
        assert status == "partial"

    def test_two_of_three_rounding(self):
        """2/3 = 66.67 → rounds to 67."""
        criteria = [
            _c("a", met=True),
            _c("b", met=True),
            _c("c", met=False),
        ]
        score, status = compute_score_and_status(criteria)
        assert score == 67
        assert status == "partial"

    def test_single_applicable_met(self):
        """One applicable criterion, met → 100, complete."""
        criteria = [_c("a", met=True)]
        score, status = compute_score_and_status(criteria)
        assert score == 100
        assert status == "complete"

    def test_single_applicable_not_met(self):
        """One applicable criterion, not met → 0, pending."""
        criteria = [_c("a", met=False)]
        score, status = compute_score_and_status(criteria)
        assert score == 0
        assert status == "pending"

    def test_empty_list(self):
        """Empty criteria list → 0, na (no applicable criteria)."""
        score, status = compute_score_and_status([])
        assert score == 0
        assert status == "na"


# ════════════════════════════════════════════════════════════════════════════
# compute_overall
# ════════════════════════════════════════════════════════════════════════════


class TestComputeOverall:
    def test_all_complete(self):
        """All bundles at 100 → overall all_complete."""
        bundles = [
            _br("a", "complete", 100),
            _br("b", "complete", 100),
            _br("c", "complete", 100),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "all_complete"
        assert overall_score == 100

    def test_all_pending(self):
        """All bundles at 0 → overall all_pending."""
        bundles = [
            _br("a", "pending", 0),
            _br("b", "pending", 0),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "all_pending"
        assert overall_score == 0

    def test_mixed_partial(self):
        """Mixed scores → overall partial."""
        bundles = [
            _br("a", "complete", 100),
            _br("b", "pending", 0),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "partial"
        assert overall_score == 50

    def test_empty_list(self):
        """Empty list → all_pending, 0."""
        overall_status, overall_score = compute_overall([])
        assert overall_status == "all_pending"
        assert overall_score == 0

    def test_partial_with_na_bundle(self):
        """Partial scores including some at 0 and some at 100 → partial."""
        bundles = [
            _br("a", "complete", 100),
            _br("b", "na", 0),         # na bundles score 0
            _br("c", "partial", 50),
        ]
        overall_status, overall_score = compute_overall(bundles)
        assert overall_status == "partial"
        assert overall_score == 50  # (100+0+50)/3 = 50

    def test_average_rounding(self):
        """Overall score averages and rounds correctly."""
        bundles = [
            _br("a", "partial", 33),
            _br("b", "partial", 33),
        ]
        _, overall_score = compute_overall(bundles)
        assert overall_score == 33  # (33+33)/2 = 33 exactly

        bundles2 = [
            _br("a", "partial", 50),
            _br("b", "partial", 33),
        ]
        _, overall_score2 = compute_overall(bundles2)
        assert overall_score2 == 42  # (50+33)/2 = 41.5 → rounds to 42


# ════════════════════════════════════════════════════════════════════════════
# build_default_criteria
# ════════════════════════════════════════════════════════════════════════════


class TestBuildDefaultCriteria:
    def test_lamgd_criteria_count(self):
        criteria = build_default_criteria("lamgd")
        assert len(criteria) == 4
        for c in criteria:
            assert c.met is False
            assert c.na is False

    def test_tev_criteria_count(self):
        criteria = build_default_criteria("tev")
        assert len(criteria) == 5
        for c in criteria:
            assert c.met is False
            assert c.na is False

    def test_hiperglicemia_criteria_count(self):
        criteria = build_default_criteria("hiperglicemia")
        assert len(criteria) == 3
        for c in criteria:
            assert c.met is False
            assert c.na is False

    def test_mobilizacao_criteria_count(self):
        criteria = build_default_criteria("mobilizacao")
        assert len(criteria) == 3
        for c in criteria:
            assert c.met is False
            assert c.na is False

    def test_dispositivos_na_defaults(self):
        """Dispositivos criteria all have na_default=True."""
        criteria = build_default_criteria("dispositivos")
        assert len(criteria) == 5
        for c in criteria:
            assert c.met is False
            assert c.na is True

    def test_invalid_bundle_id_raises_valueerror(self):
        with pytest.raises(ValueError, match="Unknown bundle_id"):
            build_default_criteria("nonexistent")


# ════════════════════════════════════════════════════════════════════════════
# evaluate_bundle
# ════════════════════════════════════════════════════════════════════════════


class TestEvaluateBundle:
    def test_valid_bundle_returns_bundle_result(self):
        result = evaluate_bundle("lamgd")
        assert isinstance(result, BundleResult)
        assert result.id == "lamgd"
        assert result.name == BUNDLE_CATALOG["lamgd"]["name"]
        assert result.status == "pending"  # all met=False → 0%
        assert result.score == 0
        assert len(result.criteria) == 4

    def test_invalid_bundle_id_raises_valueerror(self):
        with pytest.raises(ValueError, match="Unknown bundle_id"):
            evaluate_bundle("invalid_bundle")

    def test_with_criteria_overrides(self):
        """Override some criteria as met → score updates accordingly."""
        inputs = [
            {"id": "lamgd-vm", "met": True},
            {"id": "lamgd-coag", "met": True},
        ]
        result = evaluate_bundle("lamgd", criteria_inputs=inputs)
        # 2 met out of 4 applicable → 50%
        assert result.score == 50
        assert result.status == "partial"

        # Verify the actual criteria states
        vm = next(c for c in result.criteria if c.id == "lamgd-vm")
        assert vm.met is True
        coag = next(c for c in result.criteria if c.id == "lamgd-coag")
        assert coag.met is True
        cortico = next(c for c in result.criteria if c.id == "lamgd-cortico")
        assert cortico.met is False

    def test_with_na_overrides(self):
        """Override na flag on criteria."""
        inputs = [
            {"id": "lamgd-vm", "met": True, "na": False},
            {"id": "lamgd-coag", "na": True},       # mark as N/A
            {"id": "lamgd-choque", "met": True},
            {"id": "lamgd-cortico", "met": False},
        ]
        result = evaluate_bundle("lamgd", criteria_inputs=inputs)
        # Applicable: lamgd-vm, lamgd-choque, lamgd-cortico (3)
        # lamgd-coag is na → excluded
        # met: lamgd-vm, lamgd-choque (2) → 2/3 = 67%
        assert result.score == 67
        assert result.status == "partial"

        # Verify na is set correctly
        coag = next(c for c in result.criteria if c.id == "lamgd-coag")
        assert coag.na is True

    def test_unknown_criteria_id_ignored(self):
        """Overrides with unknown criterion IDs are silently ignored."""
        inputs = [
            {"id": "nonexistent-crit", "met": True},
        ]
        result = evaluate_bundle("lamgd", criteria_inputs=inputs)
        # Should still be pending (all default met=False)
        assert result.score == 0
        assert result.status == "pending"

    def test_all_met_via_overrides_complete(self):
        """All criteria overridden to met → 100, complete."""
        bundle_def = BUNDLE_CATALOG["lamgd"]
        inputs = [{"id": c["id"], "met": True} for c in bundle_def["criteria"]]
        result = evaluate_bundle("lamgd", criteria_inputs=inputs)
        assert result.score == 100
        assert result.status == "complete"

    def test_dispositivos_default_na(self):
        """Dispositivos with no overrides: all na → status na, score 0."""
        result = evaluate_bundle("dispositivos")
        assert result.status == "na"
        assert result.score == 0
        for c in result.criteria:
            assert c.na is True
            assert c.met is False

    def test_dispositivos_with_overrides(self):
        """Dispositivos: unset na and mark some met."""
        inputs = [
            {"id": "disp-cvc-barreira", "na": False, "met": True},
            {"id": "disp-cvc-curativo", "na": False, "met": True},
            {"id": "disp-cvc-revisao", "na": False, "met": False},
            {"id": "disp-svd", "na": False, "met": False},
            {"id": "disp-tot", "na": False, "met": False},
        ]
        result = evaluate_bundle("dispositivos", criteria_inputs=inputs)
        # 2 met out of 5 applicable → 40%
        assert result.score == 40
        assert result.status == "partial"

    def test_none_inputs_uses_defaults(self):
        """criteria_inputs=None → uses all catalog defaults."""
        result = evaluate_bundle("hiperglicemia", criteria_inputs=None)
        assert result.score == 0
        assert result.status == "pending"
        assert len(result.criteria) == 3


# ════════════════════════════════════════════════════════════════════════════
# evaluate_all_bundles
# ════════════════════════════════════════════════════════════════════════════


class TestEvaluateAllBundles:
    def test_returns_five_bundles(self):
        result = evaluate_all_bundles()
        assert isinstance(result, BundlesResult)
        assert len(result.bundles) == 5
        bundle_ids = {b.id for b in result.bundles}
        assert bundle_ids == {"lamgd", "tev", "hiperglicemia", "mobilizacao", "dispositivos"}

    def test_default_overall_status(self):
        """With defaults (all met=False): pending for non-na, na for dispositivos."""
        result = evaluate_all_bundles()
        # lamgd, tev, hiperglicemia, mobilizacao → pending (score 0)
        # dispositivos → na (score 0)
        # all scores are 0 → all_pending
        assert result.overall_status == "all_pending"
        assert result.overall_score == 0

    def test_with_overrides_partial_overall(self):
        """Override some bundles to be complete → overall partial."""
        lamgd_inputs = [{"id": c["id"], "met": True} for c in BUNDLE_CATALOG["lamgd"]["criteria"]]
        bundle_inputs = {
            "lamgd": lamgd_inputs,
        }
        result = evaluate_all_bundles(bundle_inputs=bundle_inputs)
        # lamgd = 100, others = 0, dispositivos = na (0)
        # avg = 100/5 = 20
        assert result.overall_status == "partial"
        assert result.overall_score == 20

        # Verify individual bundle
        lamgd = next(b for b in result.bundles if b.id == "lamgd")
        assert lamgd.score == 100
        assert lamgd.status == "complete"

    def test_all_complete_overall(self):
        """All non-na bundles at 100 → overall all_complete
        (dispositivos stays na but score 0, so overall won't be all_complete
        unless we override dispositivos too)."""
        # Override all 5 bundles to be complete
        bundle_inputs = {}
        for bid, bdef in BUNDLE_CATALOG.items():
            bundle_inputs[bid] = [
                {"id": c["id"], "met": True, "na": False}
                for c in bdef["criteria"]
            ]
        result = evaluate_all_bundles(bundle_inputs=bundle_inputs)
        assert result.overall_status == "all_complete"
        assert result.overall_score == 100

    def test_empty_inputs_dict(self):
        """Passing an empty dict → same as no inputs (all defaults)."""
        result = evaluate_all_bundles(bundle_inputs={})
        assert len(result.bundles) == 5
        assert result.overall_status == "all_pending"


# ════════════════════════════════════════════════════════════════════════════
# get_bundle_catalog
# ════════════════════════════════════════════════════════════════════════════


class TestGetBundleCatalog:
    def test_single_bundle_structure(self):
        result = get_bundle_catalog("lamgd")
        assert isinstance(result, dict)
        assert result["bundle_id"] == "lamgd"
        assert "bundle_name" in result
        assert "criteria" in result
        assert len(result["criteria"]) == 4

        # Each criterion has id, label, na_default
        for c in result["criteria"]:
            assert "id" in c
            assert "label" in c
            assert "na_default" in c

    def test_invalid_bundle_id_raises_valueerror(self):
        with pytest.raises(ValueError, match="Unknown bundle_id"):
            get_bundle_catalog("not_a_bundle")

    def test_all_bundles(self):
        """Without bundle_id → returns dict of all bundles."""
        result = get_bundle_catalog()
        assert isinstance(result, dict)
        assert len(result) == 5
        for bid in ["lamgd", "tev", "hiperglicemia", "mobilizacao", "dispositivos"]:
            assert bid in result
            assert result[bid]["bundle_id"] == bid

    def test_dispositivos_na_defaults_in_catalog(self):
        result = get_bundle_catalog("dispositivos")
        for c in result["criteria"]:
            assert c["na_default"] is True

    def test_tev_criteria_structure(self):
        result = get_bundle_catalog("tev")
        assert result["bundle_id"] == "tev"
        assert result["bundle_name"] == BUNDLE_CATALOG["tev"]["name"]
        assert len(result["criteria"]) == 5


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE_CATALOG constant
# ════════════════════════════════════════════════════════════════════════════


class TestBundleCatalogConstant:
    def test_has_five_bundles(self):
        assert len(BUNDLE_CATALOG) == 5

    def test_all_bundles_have_name_and_criteria(self):
        for bid, bdef in BUNDLE_CATALOG.items():
            assert "name" in bdef
            assert "criteria" in bdef
            assert isinstance(bdef["criteria"], list)
            assert len(bdef["criteria"]) > 0

    def test_criteria_have_required_keys(self):
        for bdef in BUNDLE_CATALOG.values():
            for c in bdef["criteria"]:
                assert "id" in c
                assert "label" in c
                assert "na_default" in c
