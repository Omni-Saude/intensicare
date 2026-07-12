"""
Tests for Antimicrobial Stewardship domain.

Covers:
- evaluate_assessment: scoring and severity bands (NEUTRO, AMARELO, VERMELHO)
- get_criteria_catalog: 12 criteria returned
- get_categories: 7 category labels
- Criterion IDs: crit-001..crit-012 match frontend
- Recommendation generation PT-BR
"""

from __future__ import annotations

from intensicare.services.domain_antimicrobiano import (
    ANTIMICROBIAL_CRITERIA,
    AntimicrobialAssessmentResult,
    evaluate_assessment,
    evaluate_criterion,
    get_categories,
    get_criteria_by_category,
    get_criteria_catalog,
)

# ===========================================================================
# evaluate_assessment — scoring and severity bands
# ===========================================================================


class TestEvaluateAssessment:
    """Score → severity band and recommendation correctness."""

    # ------------------------------------------------------------------
    # NEUTRO band (0-3 criteria)
    # ------------------------------------------------------------------

    def test_zero_criteria_met_neutro(self):
        """0 criteria met → score 0 → NEUTRO."""
        result = evaluate_assessment("MPI-001", criteria_met=[])
        assert result.mpi_id == "MPI-001"
        assert result.score == 0
        assert result.severity == "NEUTRO"
        assert "dentro dos parâmetros adequados" in result.recommendation
        assert len(result.criteria) == 12
        assert all(c.met is False for c in result.criteria)

    def test_three_criteria_met_neutro_boundary(self):
        """3 criteria met (boundary) → score 3 → NEUTRO."""
        criteria = ["crit-001", "crit-002", "crit-003"]
        result = evaluate_assessment("MPI-002", criteria_met=criteria)
        assert result.score == 3
        assert result.severity == "NEUTRO"
        met_ids = {c.id for c in result.criteria if c.met}
        assert met_ids == set(criteria)

    # ------------------------------------------------------------------
    # AMARELO band (4-7 criteria)
    # ------------------------------------------------------------------

    def test_four_criteria_met_amarelo_entry(self):
        """4 criteria met (entry) → score 4 → AMARELO."""
        criteria = ["crit-001", "crit-002", "crit-003", "crit-004"]
        result = evaluate_assessment("MPI-003", criteria_met=criteria)
        assert result.score == 4
        assert result.severity == "AMARELO"
        assert "Recomenda-se revisão estruturada" in result.recommendation

    def test_seven_criteria_met_amarelo_boundary(self):
        """7 criteria met (boundary) → score 7 → AMARELO."""
        criteria = [f"crit-{i:03d}" for i in range(1, 8)]
        result = evaluate_assessment("MPI-004", criteria_met=criteria)
        assert result.score == 7
        assert result.severity == "AMARELO"

    # ------------------------------------------------------------------
    # VERMELHO band (8-12 criteria)
    # ------------------------------------------------------------------

    def test_eight_criteria_met_vermelho_entry(self):
        """8 criteria met (entry) → score 8 → VERMELHO."""
        criteria = [f"crit-{i:03d}" for i in range(1, 9)]
        result = evaluate_assessment("MPI-005", criteria_met=criteria)
        assert result.score == 8
        assert result.severity == "VERMELHO"
        assert "INTERVENÇÃO IMEDIATA" in result.recommendation

    def test_twelve_criteria_met_vermelho_max(self):
        """12 criteria met (max) → score 12 → VERMELHO."""
        criteria = [f"crit-{i:03d}" for i in range(1, 13)]
        result = evaluate_assessment("MPI-006", criteria_met=criteria)
        assert result.score == 12
        assert result.severity == "VERMELHO"
        assert "stewardship" in result.recommendation.lower()

    # ------------------------------------------------------------------
    # Defaults and edge cases
    # ------------------------------------------------------------------

    def test_default_assessed_by_is_system(self):
        """When assessed_by not provided, defaults to 'system'."""
        result = evaluate_assessment("MPI-007")
        assert result.assessed_by == "system"

    def test_custom_assessed_by_preserved(self):
        """Custom assessed_by value is preserved."""
        result = evaluate_assessment("MPI-008", assessed_by="dr-house")
        assert result.assessed_by == "dr-house"

    def test_criteria_met_none_defaults_empty(self):
        """criteria_met=None behaves like empty list → score 0."""
        result = evaluate_assessment("MPI-009", criteria_met=None)
        assert result.score == 0
        assert result.severity == "NEUTRO"

    def test_duplicate_criteria_met_counted_once(self):
        """Duplicate criterion IDs in the met list are deduplicated."""
        criteria = ["crit-001", "crit-001", "crit-002", "crit-002"]
        result = evaluate_assessment("MPI-010", criteria_met=criteria)
        assert result.score == 2  # Only 2 unique, not 4


# ===========================================================================
# Recommendation strings (PT-BR)
# ===========================================================================


class TestRecommendationStrings:
    """Verify recommendation text for each severity band."""

    def test_neutro_recommendation_text(self):
        result = evaluate_assessment("MPI-R1", criteria_met=[])
        assert result.recommendation.startswith(
            "Prescrição antimicrobiana dentro dos parâmetros adequados"
        )
        assert "reavaliar em 72h" in result.recommendation

    def test_amarelo_recommendation_text(self):
        result = evaluate_assessment(
            "MPI-R2",
            criteria_met=["crit-001", "crit-002", "crit-003", "crit-004"],
        )
        assert "Recomenda-se revisão estruturada" in result.recommendation
        assert "24-48h" in result.recommendation

    def test_vermelho_recommendation_text(self):
        result = evaluate_assessment(
            "MPI-R3",
            criteria_met=[f"crit-{i:03d}" for i in range(1, 9)],
        )
        assert "INTERVENÇÃO IMEDIATA" in result.recommendation
        assert "12h" in result.recommendation


# ===========================================================================
# Criteria catalog: get_criteria_catalog
# ===========================================================================


class TestCriteriaCatalog:
    """Verify the criteria catalog structure and contents."""

    def test_catalog_has_twelve_criteria(self):
        """get_criteria_catalog must return 12 criteria."""
        catalog = get_criteria_catalog()
        assert len(catalog) == 12

    def test_catalog_is_copy_not_reference(self):
        """get_criteria_catalog returns a copy, not the original list."""
        catalog = get_criteria_catalog()
        assert catalog is not ANTIMICROBIAL_CRITERIA
        # Mutating the copy must not affect the original
        catalog.append({"id": "crit-999", "name": "fake"})
        assert len(ANTIMICROBIAL_CRITERIA) == 12

    def test_catalog_ids_match_frontend(self):
        """All criterion IDs are crit-001 through crit-012."""
        catalog = get_criteria_catalog()
        ids = {c["id"] for c in catalog}
        expected_ids = {f"crit-{i:03d}" for i in range(1, 13)}
        assert ids == expected_ids

    def test_each_criterion_has_required_fields(self):
        """Every criterion must have id, name, category, description."""
        for crit in get_criteria_catalog():
            for field in ("id", "name", "category", "description"):
                assert field in crit, f"Missing field '{field}' in {crit['id']}"
                assert isinstance(crit[field], str)
                assert crit[field]  # non-empty


# ===========================================================================
# Categories: get_categories
# ===========================================================================


class TestCategories:
    """Verify the category label map."""

    def test_categories_returns_seven_labels(self):
        """get_categories must return 7 category entries."""
        categories = get_categories()
        assert len(categories) == 7

    def test_category_keys_match_catalog_categories(self):
        """Category keys in catalog must be a subset of the label map."""
        categories = get_categories()
        catalog_categories = {c["category"] for c in get_criteria_catalog()}
        assert catalog_categories.issubset(set(categories.keys()))

    def test_all_categories_have_non_empty_label(self):
        """Every category must have a non-empty human-readable label."""
        for key, label in get_categories().items():
            assert label, f"Category '{key}' has empty label"


# ===========================================================================
# get_criteria_by_category
# ===========================================================================


class TestCriteriaByCategory:
    """Filter criteria by category."""

    def test_filter_duracao(self):
        """duracao category should return crit-001 and crit-010."""
        results = get_criteria_by_category("duracao")
        ids = {c["id"] for c in results}
        assert ids == {"crit-001", "crit-010"}

    def test_filter_espectro(self):
        """espectro category should return crit-002, crit-008, crit-009."""
        results = get_criteria_by_category("espectro")
        ids = {c["id"] for c in results}
        assert ids == {"crit-002", "crit-008", "crit-009"}

    def test_filter_unknown_category_returns_empty(self):
        """Unknown category returns an empty list."""
        results = get_criteria_by_category("nonexistent")
        assert results == []

    def test_each_result_is_copy(self):
        """Each dict returned is a copy, not a reference to the original."""
        results = get_criteria_by_category("duracao")
        results[0]["extra"] = "mutated"
        original = get_criteria_catalog()
        has_extra = any("extra" in c for c in original)
        assert not has_extra


# ===========================================================================
# AntimicrobialAssessmentResult dataclass
# ===========================================================================


class TestAssessmentResultDataclass:
    """Tests for the dataclass fields and defaults."""

    def test_default_values(self):
        """Default values for a freshly constructed result."""
        result = AntimicrobialAssessmentResult()
        assert result.id is None
        assert result.mpi_id == ""
        assert result.criteria == []
        assert result.score == 0
        assert result.severity == "NEUTRO"
        assert result.recommendation == ""
        assert result.assessed_by == ""
        assert result.assessed_at is not None  # auto-populated

    def test_assessed_at_is_utc_aware(self):
        """assessed_at must be timezone-aware (UTC)."""
        result = AntimicrobialAssessmentResult()
        assert result.assessed_at is not None
        assert result.assessed_at.tzinfo is not None


# ===========================================================================
# evaluate_criterion (placeholder)
# ===========================================================================


class TestEvaluateCriterion:
    """Tests for the single-criterion evaluator (placeholder)."""

    def test_no_inputs_returns_not_met(self):
        """Without inputs, criterion is not met."""
        crit_def = {"id": "crit-001", "name": "Test", "category": "duracao", "description": "Desc"}
        result = evaluate_criterion(crit_def)
        assert result.met is False
        assert result.id == "crit-001"

    def test_with_empty_inputs_returns_not_met(self):
        """With empty inputs dict, criterion is still not met."""
        crit_def = {"id": "crit-002", "name": "Test", "category": "espectro", "description": "Desc"}
        result = evaluate_criterion(crit_def, inputs={})
        assert result.met is False


# ===========================================================================
# ANTIMICROBIAL_CRITERIA constant
# ===========================================================================


class TestAntimicrobialCriteriaConstant:
    """Verify the module-level constant."""

    def test_constant_is_list_of_dicts(self):
        assert isinstance(ANTIMICROBIAL_CRITERIA, list)
        assert all(isinstance(c, dict) for c in ANTIMICROBIAL_CRITERIA)

    def test_constant_has_twelve_items(self):
        assert len(ANTIMICROBIAL_CRITERIA) == 12

    def test_constant_is_immutable_export(self):
        """The constant should not be mutated by external callers (best effort)."""
        length_before = len(ANTIMICROBIAL_CRITERIA)
        # get_criteria_catalog returns a copy; the constant itself is unchanged
        catalog_copy = get_criteria_catalog()
        catalog_copy.clear()
        assert len(ANTIMICROBIAL_CRITERIA) == length_before
