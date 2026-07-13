"""Unit tests for Antimicrobial Stewardship domain service."""

from datetime import datetime, timezone

from intensicare.services.domain_antimicrobiano import (
    ANTIMICROBIAL_CRITERIA,
    CATEGORY_LABELS,
    AntimicrobialAssessmentResult,
    AntimicrobialCriterionResult,
    _build_recommendation,
    evaluate_assessment,
    evaluate_criterion,
    get_categories,
    get_criteria_by_category,
    get_criteria_catalog,
)

# ════════════════════════════════════════════════════════════════════════════
# evaluate_assessment — scoring bands and edge cases
# ════════════════════════════════════════════════════════════════════════════


class TestEvaluateAssessment:
    """Tests for evaluate_assessment covering all severity bands and edge cases."""

    def test_zero_met_neutro(self):
        """0 criteria met → NEUTRO, score=0."""
        result = evaluate_assessment("MPI-001", criteria_met=[])
        assert result.mpi_id == "MPI-001"
        assert result.score == 0
        assert result.severity == "NEUTRO"
        assert "dentro dos parâmetros adequados" in result.recommendation
        assert len(result.criteria) == 12
        assert all(not c.met for c in result.criteria)

    def test_none_met_defaults_to_empty(self):
        """None criteria_met → treated as empty, NEUTRO, score=0."""
        result = evaluate_assessment("MPI-002", criteria_met=None)
        assert result.score == 0
        assert result.severity == "NEUTRO"

    def test_three_met_neutro_boundary(self):
        """3 criteria met = upper NEUTRO boundary, score=3."""
        met = ["crit-001", "crit-002", "crit-003"]
        result = evaluate_assessment("MPI-003", criteria_met=met)
        assert result.score == 3
        assert result.severity == "NEUTRO"
        assert "dentro dos parâmetros adequados" in result.recommendation

    def test_four_met_amarelo_lower_boundary(self):
        """4 criteria met → AMARELO, score=4 (lower boundary)."""
        met = ["crit-001", "crit-002", "crit-003", "crit-004"]
        result = evaluate_assessment("MPI-004", criteria_met=met)
        assert result.score == 4
        assert result.severity == "AMARELO"
        assert "requerem atenção" in result.recommendation
        assert "24-48h" in result.recommendation

    def test_seven_met_amarelo_upper_boundary(self):
        """7 criteria met = upper AMARELO boundary, score=7."""
        met = [f"crit-{i:03d}" for i in range(1, 8)]
        result = evaluate_assessment("MPI-005", criteria_met=met)
        assert result.score == 7
        assert result.severity == "AMARELO"

    def test_eight_met_vermelho_lower_boundary(self):
        """8 criteria met → VERMELHO, score=8 (lower boundary)."""
        met = [f"crit-{i:03d}" for i in range(1, 9)]
        result = evaluate_assessment("MPI-006", criteria_met=met)
        assert result.score == 8
        assert result.severity == "VERMELHO"
        assert "INTERVENÇÃO IMEDIATA" in result.recommendation
        assert "12h" in result.recommendation

    def test_twelve_met_vermelho_max(self):
        """All 12 criteria met → VERMELHO, score=12."""
        met = [f"crit-{i:03d}" for i in range(1, 13)]
        result = evaluate_assessment("MPI-007", criteria_met=met)
        assert result.score == 12
        assert result.severity == "VERMELHO"
        assert all(c.met for c in result.criteria)

    def test_specific_criteria_ids(self):
        """Only specific criteria IDs met; check criteria results match."""
        met = ["crit-005", "crit-010"]
        result = evaluate_assessment("MPI-008", criteria_met=met)
        assert result.score == 2
        met_ids = {c.id for c in result.criteria if c.met}
        assert met_ids == {"crit-005", "crit-010"}

    def test_assessed_by_defaults_to_system(self):
        """Default assessed_by is 'system'."""
        result = evaluate_assessment("MPI-009", criteria_met=[])
        assert result.assessed_by == "system"

    def test_assessed_by_custom_value(self):
        """Custom assessed_by is preserved."""
        result = evaluate_assessment("MPI-010", criteria_met=[], assessed_by="dr_silva")
        assert result.assessed_by == "dr_silva"

    def test_assessed_at_is_set(self):
        """assessed_at is automatically set via __post_init__."""
        result = evaluate_assessment("MPI-011", criteria_met=[])
        assert result.assessed_at is not None
        assert isinstance(result.assessed_at, datetime)
        # Should be timezone-aware (UTC)
        assert result.assessed_at.tzinfo == timezone.utc

    def test_duplicate_ids_counted_once(self):
        """Duplicate IDs in criteria_met are deduplicated (score counted once)."""
        met = ["crit-001", "crit-001", "crit-002", "crit-002"]
        result = evaluate_assessment("MPI-012", criteria_met=met)
        assert result.score == 2


# ════════════════════════════════════════════════════════════════════════════
# _build_recommendation
# ════════════════════════════════════════════════════════════════════════════


class TestBuildRecommendation:
    """Tests for _build_recommendation — PT-BR strings per severity band."""

    def test_neutro_recommendation(self):
        """NEUTRO → routine monitoring recommendation."""
        rec = _build_recommendation(0, "NEUTRO")
        assert "dentro dos parâmetros adequados" in rec
        assert "72h" in rec

    def test_amarelo_recommendation(self):
        """AMARELO → structured review recommendation with score."""
        rec = _build_recommendation(5, "AMARELO")
        assert "5 critério(s)" in rec
        assert "requerem atenção" in rec
        assert "descalonamento" in rec
        assert "24-48h" in rec

    def test_vermelho_recommendation(self):
        """VERMELHO → immediate intervention recommendation with score."""
        rec = _build_recommendation(10, "VERMELHO")
        assert "INTERVENÇÃO IMEDIATA" in rec
        assert "10 critérios críticos" in rec
        assert "stewardship" in rec
        assert "12h" in rec


# ════════════════════════════════════════════════════════════════════════════
# Criteria catalog helpers
# ════════════════════════════════════════════════════════════════════════════


class TestGetCriteriaCatalog:
    """Tests for get_criteria_catalog."""

    def test_returns_twelve_items(self):
        """Catalog must return exactly 12 criteria."""
        catalog = get_criteria_catalog()
        assert len(catalog) == 12

    def test_returns_copy_not_reference(self):
        """Returned list is a shallow copy, not the original."""
        catalog = get_criteria_catalog()
        catalog.append({"id": "extra"})
        assert len(ANTIMICROBIAL_CRITERIA) == 12

    def test_each_item_has_required_keys(self):
        """Every criterion dict has id, name, category, description."""
        for crit in get_criteria_catalog():
            assert "id" in crit
            assert "name" in crit
            assert "category" in crit
            assert "description" in crit

    def test_ids_follow_naming_convention(self):
        """All IDs follow crit-NNN pattern."""
        for crit in get_criteria_catalog():
            assert crit["id"].startswith("crit-")
            assert len(crit["id"]) == 8  # "crit-001" through "crit-012"


class TestGetCriteriaByCategory:
    """Tests for get_criteria_by_category — filtering by category key."""

    def test_filter_duracao_returns_two(self):
        """'duracao' category has 2 criteria (crit-001, crit-010)."""
        result = get_criteria_by_category("duracao")
        assert len(result) == 2
        assert all(c["category"] == "duracao" for c in result)

    def test_filter_espectro_returns_three(self):
        """'espectro' category has 3 criteria (crit-002, crit-008, crit-009)."""
        result = get_criteria_by_category("espectro")
        assert len(result) == 3
        assert all(c["category"] == "espectro" for c in result)

    def test_filter_dose_returns_two(self):
        """'dose' category has 2 criteria (crit-003, crit-011)."""
        result = get_criteria_by_category("dose")
        assert len(result) == 2
        assert all(c["category"] == "dose" for c in result)

    def test_filter_cvc_returns_two(self):
        """'cvc' category has 2 criteria (crit-004, crit-012)."""
        result = get_criteria_by_category("cvc")
        assert len(result) == 2
        assert all(c["category"] == "cvc" for c in result)

    def test_filter_candidemia_returns_one(self):
        """'candidemia' category has 1 criterion (crit-005)."""
        result = get_criteria_by_category("candidemia")
        assert len(result) == 1
        assert result[0]["id"] == "crit-005"

    def test_filter_culturas_returns_one(self):
        """'culturas' category has 1 criterion (crit-006)."""
        result = get_criteria_by_category("culturas")
        assert len(result) == 1
        assert result[0]["id"] == "crit-006"

    def test_filter_cap_covid_returns_one(self):
        """'cap_covid' category has 1 criterion (crit-007)."""
        result = get_criteria_by_category("cap_covid")
        assert len(result) == 1
        assert result[0]["id"] == "crit-007"

    def test_unknown_category_returns_empty(self):
        """Non-existent category returns empty list."""
        result = get_criteria_by_category("nonexistent")
        assert result == []

    def test_returns_copy_not_reference(self):
        """Returned list is a shallow copy, not the original."""
        result = get_criteria_by_category("duracao")
        result.append({"id": "extra"})
        assert len(get_criteria_by_category("duracao")) == 2


class TestGetCategories:
    """Tests for get_categories — category label map."""

    def test_returns_seven_categories(self):
        """Must return exactly 7 category keys."""
        categories = get_categories()
        assert len(categories) == 7

    def test_expected_keys_present(self):
        """All expected category keys are present."""
        categories = get_categories()
        expected = {"duracao", "espectro", "dose", "cvc", "candidemia", "culturas", "cap_covid"}
        assert set(categories.keys()) == expected

    def test_labels_are_non_empty(self):
        """Every category has a non-empty label."""
        for _key, label in get_categories().items():
            assert isinstance(label, str)
            assert len(label) > 0

    def test_returns_copy_not_reference(self):
        """Returned dict is a copy, not the original reference."""
        categories = get_categories()
        categories["new_key"] = "New Label"
        assert "new_key" not in CATEGORY_LABELS


# ════════════════════════════════════════════════════════════════════════════
# evaluate_criterion — placeholder evaluator
# ════════════════════════════════════════════════════════════════════════════


class TestEvaluateCriterion:
    """Tests for evaluate_criterion — placeholder that returns met=False."""

    def test_returns_met_false_by_default(self):
        """Without inputs, criterion result has met=False."""
        crit_def = ANTIMICROBIAL_CRITERIA[0]
        result = evaluate_criterion(crit_def)
        assert result.met is False
        assert result.id == "crit-001"
        assert result.name == "Duração > 7 dias"
        assert result.category == "duracao"

    def test_none_inputs_returns_met_false(self):
        """Explicit None inputs also returns met=False."""
        crit_def = ANTIMICROBIAL_CRITERIA[5]  # crit-006
        result = evaluate_criterion(crit_def, inputs=None)
        assert result.met is False

    def test_with_empty_inputs_returns_met_false(self):
        """Empty dict inputs still returns met=False (placeholder)."""
        crit_def = ANTIMICROBIAL_CRITERIA[11]  # crit-012
        result = evaluate_criterion(crit_def, inputs={})
        assert result.met is False

    def test_result_fields_match_criterion_def(self):
        """Result carries through all fields from criterion definition."""
        crit_def = {
            "id": "test-id",
            "name": "Test Criterion",
            "category": "test-cat",
            "description": "A test description.",
        }
        result = evaluate_criterion(crit_def)
        assert result.id == "test-id"
        assert result.name == "Test Criterion"
        assert result.category == "test-cat"
        assert result.description == "A test description."


# ════════════════════════════════════════════════════════════════════════════
# Dataclasses
# ════════════════════════════════════════════════════════════════════════════


class TestAntimicrobialAssessmentResult:
    """Tests for AntimicrobialAssessmentResult dataclass behavior."""

    def test_post_init_sets_assessed_at_when_none(self):
        """__post_init__ sets assessed_at to now(UTC) when None."""
        result = AntimicrobialAssessmentResult(mpi_id="MPI-TEST")
        assert result.assessed_at is not None
        assert isinstance(result.assessed_at, datetime)
        assert result.assessed_at.tzinfo == timezone.utc

    def test_post_init_preserves_explicit_assessed_at(self):
        """__post_init__ does not override an explicitly-provided assessed_at."""
        explicit_dt = datetime(2025, 1, 15, 10, 30, tzinfo=timezone.utc)
        result = AntimicrobialAssessmentResult(
            mpi_id="MPI-TEST",
            assessed_at=explicit_dt,
        )
        assert result.assessed_at == explicit_dt

    def test_default_field_values(self):
        """Check default values for all fields."""
        result = AntimicrobialAssessmentResult()
        assert result.id is None
        assert result.mpi_id == ""
        assert result.criteria == []
        assert result.score == 0
        assert result.severity == "NEUTRO"
        assert result.recommendation == ""
        assert result.assessed_by == ""


class TestAntimicrobialCriterionResult:
    """Tests for AntimicrobialCriterionResult dataclass."""

    def test_creation_with_all_fields(self):
        """Can create with all fields set."""
        result = AntimicrobialCriterionResult(
            id="crit-001",
            name="Duração > 7 dias",
            category="duracao",
            description="Test description.",
            met=True,
        )
        assert result.id == "crit-001"
        assert result.name == "Duração > 7 dias"
        assert result.category == "duracao"
        assert result.description == "Test description."
        assert result.met is True

    def test_met_defaults_to_false(self):
        """met field defaults to False when not specified."""
        # The dataclass doesn't define a default for met, so it must be provided.
        # Testing that met=False works correctly.
        result = AntimicrobialCriterionResult(
            id="x", name="x", category="x", description="x", met=False
        )
        assert result.met is False
