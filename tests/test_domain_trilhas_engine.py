"""Tests for Care Pathways (Trilhas Engine) domain.

Covers:
- get_pathway_catalog / get_pathway_by_id: catalog structure
- check_pathway_eligibility: eligibility rules per pathway (Rules 5, 15-18)
- enroll_patient: enrollment flows (Rules 3, 4, 6)
- evaluate_criteria: criteria evaluation, state transitions, severity (Rules 7-10)
- get_patient_pathways: patient pathway listing (Rule 13)
- get_pathway_progress: progress, trends, recommendations (Rules 11, 12, 14)
"""

from __future__ import annotations

import pytest

from intensicare.services.domain_trilhas_engine import (
    PATHWAY_SEEDS,
    CriteriaEvaluationResult,
    PathwayEligibilityResult,
    PathwayEnrollmentResult,
    PathwayProgressResult,
    _reset_stores,
    check_pathway_eligibility,
    enroll_patient,
    evaluate_criteria,
    get_pathway_by_id,
    get_pathway_catalog,
    get_patient_pathways,
    get_pathway_progress,
)


# ── Shared fixture for a clean in-memory store before each test ─────────────────
@pytest.fixture(autouse=True)
def _clean_stores() -> None:
    """Reset in-memory stores before every test to avoid cross-test pollution."""
    _reset_stores()


# =============================================================================
# Pathway Catalog
# =============================================================================


class TestPathwayCatalog:
    """get_pathway_catalog and get_pathway_by_id."""

    def test_catalog_returns_twelve_pathways(self) -> None:
        """active_only=True must return all 12 YAML-persisted pathways."""
        catalog = get_pathway_catalog(active_only=True)
        assert len(catalog) == 12
        slugs = {p["slug"] for p in catalog}
        assert slugs == {
            "antimicrobiano",
            "delirium",
            "desmame",
            "equilibrio",
            "estabilidade",
            "nutricao",
            "profilaxia",
            "renal",
            "respiratorio",
            "sedacao",
            "sepse",
            "ventilacao",
        }

    def test_catalog_active_only_false_also_returns_twelve(self) -> None:
        """active_only=False returns all pathways (all are active by default)."""
        catalog = get_pathway_catalog(active_only=False)
        assert len(catalog) == 12

    def test_catalog_is_copy_not_reference(self) -> None:
        """Returns a copy; mutating it does not mutate PATHWAY_SEEDS."""
        catalog = get_pathway_catalog()
        original_length = len(PATHWAY_SEEDS)
        catalog.append({"id": 999, "name": "fake", "slug": "fake"})
        assert len(PATHWAY_SEEDS) == original_length

        # Mutating a nested list inside the copy also doesn't change seeds
        first_copy = catalog[0]
        first_seed = PATHWAY_SEEDS[0]
        assert first_copy["states"] is not first_seed["states"]

    def test_get_pathway_by_id_valid(self) -> None:
        """get_pathway_by_id with a valid ID returns the pathway."""
        pathway = get_pathway_by_id(1)
        assert pathway is not None
        assert pathway["name"] == "Ventilação Mecânica"
        assert pathway["slug"] == "ventilacao"
        assert len(pathway["states"]) >= 2
        assert len(pathway["criteria"]) >= 2

    def test_get_pathway_by_id_invalid_returns_none(self) -> None:
        """Non-existent pathway ID returns None."""
        assert get_pathway_by_id(999) is None
        assert get_pathway_by_id(0) is None
        assert get_pathway_by_id(-1) is None

    def test_each_pathway_has_states_and_criteria(self) -> None:
        """Every pathway in the catalog must have states and criteria."""
        for p in PATHWAY_SEEDS:
            assert "id" in p
            assert "name" in p
            assert "slug" in p
            assert "active" in p
            assert "states" in p and len(p["states"]) >= 2
            assert "criteria" in p and len(p["criteria"]) >= 3
            # Check each state has required fields
            for s in p["states"]:
                assert "id" in s
                assert "name" in s
                assert "order" in s
                assert "is_terminal" in s
            # Check each criterion has required fields
            for c in p["criteria"]:
                assert "id" in c
                assert "name" in c
                assert "category" in c
                assert "description" in c

    def test_pathway_slugs_are_unique(self) -> None:
        """Each pathway slug must be unique."""
        slugs = [p["slug"] for p in PATHWAY_SEEDS]
        assert len(slugs) == len(set(slugs))

    def test_each_pathway_has_exactly_one_terminal_state(self) -> None:
        """Rule 3: each pathway must have exactly one terminal state."""
        for p in PATHWAY_SEEDS:
            terminal_states = [s for s in p["states"] if s.get("is_terminal")]
            assert len(terminal_states) == 1, (
                f"Pathway {p['slug']} has {len(terminal_states)} terminal states, expected 1"
            )


# =============================================================================
# Pathway Eligibility
# =============================================================================


class TestPathwayEligibility:
    """check_pathway_eligibility — Rules 5, 15-18."""

    def test_eligibility_valid_ventilacao(self) -> None:
        """Rule 15: patient with ventilation/O₂ data is eligible."""
        result = check_pathway_eligibility(
            "MPI-001",
            pathway_id=1,
            patient_data={"oxigenacao": {"pf_ratio": 280}, "peep": 8, "vc": 7},
        )
        assert result.eligible is True
        assert "Ventilação Mecânica" in result.reason
        assert len(result.matching_criteria) > 0

    def test_eligibility_valid_sepse_qsofa(self) -> None:
        """Rule 16: patient with qSOFA data is eligible for Sepse."""
        result = check_pathway_eligibility(
            "MPI-002",
            pathway_id=2,
            patient_data={"qsofa": 2, "lactato": 3.5},
        )
        assert result.eligible is True
        assert "Sepse" in result.reason

    def test_eligibility_valid_desmame(self) -> None:
        """Rule 17: patient with weaning readiness data is eligible."""
        result = check_pathway_eligibility(
            "MPI-003",
            pathway_id=3,
            patient_data={"nif": -30, "rsbi": 80, "glasgow": 12},
        )
        assert result.eligible is True
        assert "desmame" in result.reason

    def test_eligibility_valid_nutricao(self) -> None:
        """Rule 18: patient with nutritional screening data is eligible."""
        result = check_pathway_eligibility(
            "MPI-004",
            pathway_id=4,
            patient_data={"nrs": 4, "calorias": 70},
        )
        assert result.eligible is True
        assert "nutricional" in result.reason

    def test_eligibility_no_data_defaults_eligible(self) -> None:
        """Without patient_data, eligibility defaults to True (requires manual review)."""
        result = check_pathway_eligibility("MPI-005", pathway_id=1)
        assert result.eligible is True
        assert "Elegibilidade presumida" in result.reason

    def test_eligibility_insufficient_data_ventilacao(self) -> None:
        """Rule 15: insufficient ventilation data returns not eligible."""
        result = check_pathway_eligibility(
            "MPI-006",
            pathway_id=1,
            patient_data={"heart_rate": 90},  # irrelevant data
        )
        assert result.eligible is False
        assert "insuficientes" in result.reason.lower()

    def test_eligibility_insufficient_data_nutricao(self) -> None:
        """Rule 18: insufficient nutritional data returns not eligible."""
        result = check_pathway_eligibility(
            "MPI-007",
            pathway_id=4,
            patient_data={"glasgow": 14},  # irrelevant
        )
        assert result.eligible is False
        assert "insuficientes" in result.reason.lower()

    def test_eligibility_invalid_pathway(self) -> None:
        """Non-existent pathway returns not eligible."""
        result = check_pathway_eligibility("MPI-008", pathway_id=999)
        assert result.eligible is False
        assert "não encontrado" in result.reason

    def test_eligibility_already_enrolled_active(self) -> None:
        """Rule 4: already enrolled (active) → not eligible."""
        # Enroll first
        enroll_result = enroll_patient("MPI-009", pathway_id=1)
        assert enroll_result.error == ""

        # Now check eligibility — should be ineligible
        result = check_pathway_eligibility("MPI-009", pathway_id=1)
        assert result.eligible is False
        assert "já está inscrito" in result.reason


# =============================================================================
# Pathway Enrollment
# =============================================================================


class TestPathwayEnrollment:
    """enroll_patient — Rules 3, 4, 6."""

    def test_enroll_patient_success(self) -> None:
        """Enroll a patient successfully."""
        result = enroll_patient("MPI-100", pathway_id=1)
        assert result.error == ""
        assert result.patient_pathway_id is not None
        assert result.mpi_id == "MPI-100"
        assert result.pathway_id == 1
        assert result.status == "active"
        assert result.current_state == "initial"
        assert result.severity == "normal"
        assert result.enrolled_at != ""

    def test_enroll_patient_sets_initial_state(self) -> None:
        """Rule 6: enrollment always starts at 'initial' state."""
        for pw_id in [1, 2, 3, 4]:
            result = enroll_patient(f"MPI-{pw_id}", pathway_id=pw_id)
            assert result.current_state == "initial", f"Expected 'initial' for pathway {pw_id}"
            assert result.patient_pathway_id is not None

    def test_enroll_patient_duplicate_returns_error(self) -> None:
        """Rule 4: duplicate active enrollment returns error."""
        first = enroll_patient("MPI-101", pathway_id=1)
        assert first.error == ""

        second = enroll_patient("MPI-101", pathway_id=1)
        assert second.error != ""
        assert "já está inscrito" in second.error

    def test_enroll_patient_invalid_pathway(self) -> None:
        """Enrolling in a non-existent pathway returns error."""
        result = enroll_patient("MPI-102", pathway_id=999)
        assert result.error != ""
        assert "não encontrado" in result.error
        assert result.patient_pathway_id is None

    def test_enroll_with_initial_criteria(self) -> None:
        """Enrollment accepts initial_criteria and populates criteria_data."""
        result = enroll_patient(
            "MPI-103",
            pathway_id=1,
            initial_criteria=[
                {"id": "crit-vent-pf", "met": True, "value": 320},
                {"id": "crit-vent-peep", "met": True, "value": 8},
            ],
        )
        assert result.error == ""
        assert result.patient_pathway_id is not None

        # Verify criteria data via patient pathways
        pathways = get_patient_pathways("MPI-103")
        assert len(pathways) == 1
        criteria = pathways[0]["criteria_data"]
        pf_crit = next(c for c in criteria if c["id"] == "crit-vent-pf")
        assert pf_crit["met"] is True
        assert pf_crit["value"] == 320
        peep_crit = next(c for c in criteria if c["id"] == "crit-vent-peep")
        assert peep_crit["met"] is True
        assert peep_crit["value"] == 8

        # Criteria not specified should default to met=False
        vc_crit = next(c for c in criteria if c["id"] == "crit-vent-vc")
        assert vc_crit["met"] is False

    def test_enroll_patient_increments_ids(self) -> None:
        """Each enrollment gets a unique auto-increment ID."""
        r1 = enroll_patient("MPI-200", pathway_id=1)
        r2 = enroll_patient("MPI-201", pathway_id=2)
        assert r1.patient_pathway_id is not None
        assert r2.patient_pathway_id is not None
        assert r2.patient_pathway_id == r1.patient_pathway_id + 1


# =============================================================================
# Criteria Evaluation
# =============================================================================


class TestCriteriaEvaluation:
    """evaluate_criteria — Rules 7, 8, 9, 10."""

    def _enroll_and_get_id(self, mpi_id: str, pathway_id: int = 1) -> int:
        """Helper: enroll a patient and return the pp_id."""
        result = enroll_patient(mpi_id, pathway_id=pathway_id)
        assert result.error == ""
        assert result.patient_pathway_id is not None
        return result.patient_pathway_id

    def test_update_criteria_met(self) -> None:
        """Rule 7: criteria update marks individual criterion as met."""
        pp_id = self._enroll_and_get_id("MPI-300")
        result = evaluate_criteria(
            "MPI-300",
            patient_pathway_id=pp_id,
            criteria_updates=[
                {"id": "crit-vent-pf", "met": True, "value": 310},
            ],
        )
        assert result.patient_pathway_id == pp_id
        assert result.state_changed is False  # Only 1 of 5 met
        # Check the criterion is marked met
        pf_crit = next(c for c in result.criteria if c["id"] == "crit-vent-pf")
        assert pf_crit["met"] is True
        assert pf_crit["value"] == 310
        assert pf_crit["evaluated_at"] is not None

    def test_update_criteria_not_met(self) -> None:
        """Criteria can be explicitly marked as not met."""
        pp_id = self._enroll_and_get_id("MPI-301")
        result = evaluate_criteria(
            "MPI-301",
            patient_pathway_id=pp_id,
            criteria_updates=[
                {"id": "crit-vent-pf", "met": False, "value": 150},
            ],
        )
        pf_crit = next(c for c in result.criteria if c["id"] == "crit-vent-pf")
        assert pf_crit["met"] is False
        assert pf_crit["value"] == 150

    def test_criteria_triggers_state_transition(self) -> None:
        """Rule 8: when ALL criteria are met, auto-transition to next state."""
        pp_id = self._enroll_and_get_id("MPI-302")

        # Mark ALL 5 ventilacao criteria as met
        updates = [
            {"id": "crit-vent-pf", "met": True, "value": 320},
            {"id": "crit-vent-peep", "met": True, "value": 8},
            {"id": "crit-vent-vc", "met": True, "value": 7},
            {"id": "crit-vent-plat", "met": True, "value": 25},
            {"id": "crit-vent-drive", "met": True, "value": 12},
        ]
        result = evaluate_criteria("MPI-302", patient_pathway_id=pp_id, criteria_updates=updates)
        assert result.state_changed is True
        assert result.new_state == "otimizacao"  # Next state after 'initial'
        assert "Avançando" in result.transition_reason
        assert result.severity == "normal"  # All 5 met → 100%

    def test_criteria_state_transition_to_terminal(self) -> None:
        """Rule 3: reaching terminal state completes the pathway (status=completed)."""
        pp_id = self._enroll_and_get_id("MPI-303", pathway_id=3)  # Desmame has 6 criteria

        # Mark ALL 6 criteria met
        updates = [
            {"id": "crit-des-frvt", "met": True, "value": 80},
            {"id": "crit-des-nif", "met": True, "value": -30},
            {"id": "crit-des-glasgow", "met": True, "value": 13},
            {"id": "crit-des-tosse", "met": True, "value": "presente"},
            {"id": "crit-des-secrecao", "met": True, "value": "adequado"},
            {"id": "crit-des-gasometria", "met": True, "value": "estável"},
        ]
        result = evaluate_criteria("MPI-303", patient_pathway_id=pp_id, criteria_updates=updates)
        assert result.state_changed is True
        # Desmame has 4 states: initial → tps → extubacao → alta (terminal)
        assert result.new_state == "tps"

        # Check that the enrollment is still active (not yet terminal after one transition)
        pathways = get_patient_pathways("MPI-303")
        assert len(pathways) == 1
        assert pathways[0]["status"] == "active"
        assert pathways[0]["current_state"] == "tps"

    def test_criteria_reaching_terminal_completes_pathway(self) -> None:
        """Rule 3: reaching terminal state sets status=completed and completed_at."""
        pp_id = self._enroll_and_get_id("MPI-304", pathway_id=4)  # Nutrição has 6 criteria

        # First transition: mark all 6 → move to "progressao"
        updates = [
            {"id": "crit-nut-triagem", "met": True, "value": 4},
            {"id": "crit-nut-calorias", "met": True, "value": 85},
            {"id": "crit-nut-proteinas", "met": True, "value": 1.4},
            {"id": "crit-nut-residuo", "met": True, "value": 100},
            {"id": "crit-nut-albumina", "met": True, "value": 3.2},
            {"id": "crit-nut-diarreia", "met": True, "value": 0},
        ]
        r1 = evaluate_criteria("MPI-304", patient_pathway_id=pp_id, criteria_updates=updates)
        assert r1.state_changed is True
        assert r1.new_state == "progressao"

        # Second transition: all criteria still met → move to "meta"
        r2 = evaluate_criteria("MPI-304", patient_pathway_id=pp_id, criteria_updates=[])
        assert r2.state_changed is True
        assert r2.new_state == "meta"

        # Third transition: all criteria still met → move to "alta" (terminal)
        r3 = evaluate_criteria("MPI-304", patient_pathway_id=pp_id, criteria_updates=[])
        assert r3.state_changed is True
        assert r3.new_state == "alta"

        # Check pathway is now completed
        pathways = get_patient_pathways("MPI-304", status_filter="completed")
        assert len(pathways) == 1
        assert pathways[0]["status"] == "completed"
        assert pathways[0]["completed_at"] is not None

    def test_criteria_unknown_patient_pathway(self) -> None:
        """Evaluating criteria for unknown pp_id returns empty result."""
        result = evaluate_criteria(
            "MPI-399",
            patient_pathway_id=9999,
            criteria_updates=[{"id": "crit-vent-pf", "met": True}],
        )
        assert result.patient_pathway_id == 9999
        assert result.state_changed is False
        # Criteria passed back as-is (no matching enrollment)
        assert result.criteria == [{"id": "crit-vent-pf", "met": True}]

    def test_severity_normal_from_all_met(self) -> None:
        """Rule 10: 100% met → severity 'normal'."""
        pp_id = self._enroll_and_get_id("MPI-305")
        updates = [
            {"id": f"crit-vent-{s}", "met": True, "value": 1}
            for s in ["pf", "peep", "vc", "plat", "drive"]
        ]
        result = evaluate_criteria("MPI-305", patient_pathway_id=pp_id, criteria_updates=updates)
        assert result.severity == "normal"

    def test_severity_watch_from_partial_met(self) -> None:
        """Rule 10: 3 of 5 met (60%) → severity 'watch'."""
        pp_id = self._enroll_and_get_id("MPI-306")
        updates = [
            {"id": "crit-vent-pf", "met": True},
            {"id": "crit-vent-peep", "met": True},
            {"id": "crit-vent-vc", "met": True},
        ]
        result = evaluate_criteria("MPI-306", patient_pathway_id=pp_id, criteria_updates=updates)
        assert result.severity == "watch"

    def test_severity_critical_from_few_met(self) -> None:
        """Rule 10: 0 of 5 met (0%) → severity 'critical'."""
        pp_id = self._enroll_and_get_id("MPI-307")
        # No criteria met — just mark one as not met explicitly
        result = evaluate_criteria(
            "MPI-307",
            patient_pathway_id=pp_id,
            criteria_updates=[{"id": "crit-vent-pf", "met": False}],
        )
        # 0 met out of 5 → < 40% → critical
        assert result.severity == "critical"

    def test_transition_is_logged_in_history(self) -> None:
        """Rule 9: every state transition is logged."""
        pp_id = self._enroll_and_get_id("MPI-308")

        updates = [
            {"id": "crit-vent-pf", "met": True, "value": 320},
            {"id": "crit-vent-peep", "met": True, "value": 8},
            {"id": "crit-vent-vc", "met": True, "value": 7},
            {"id": "crit-vent-plat", "met": True, "value": 25},
            {"id": "crit-vent-drive", "met": True, "value": 12},
        ]
        evaluate_criteria("MPI-308", patient_pathway_id=pp_id, criteria_updates=updates)

        progress = get_pathway_progress("MPI-308", patient_pathway_id=pp_id)
        assert len(progress.state_history) >= 1
        transition = progress.state_history[0]
        assert transition["from_state"] == "initial"
        assert transition["to_state"] == "otimizacao"
        assert "Avançando" in transition["reason"]
        assert transition["changed_at"] is not None


# =============================================================================
# Patient Pathways
# =============================================================================


class TestPatientPathways:
    """get_patient_pathways — Rule 13."""

    def test_get_patient_pathways_active(self) -> None:
        """Returns active pathways for an enrolled patient."""
        enroll_patient("MPI-400", pathway_id=1)
        enroll_patient("MPI-400", pathway_id=2)
        pathways = get_patient_pathways("MPI-400")
        assert len(pathways) == 2
        slugs = {p["pathway_slug"] for p in pathways}
        assert slugs == {"ventilacao", "sepse"}
        for pw in pathways:
            assert pw["status"] == "active"

    def test_get_patient_pathways_empty(self) -> None:
        """Unknown MPI returns an empty list."""
        pathways = get_patient_pathways("MPI-NOEXIST")
        assert pathways == []

    def test_get_patient_pathways_completed_filter(self) -> None:
        """status_filter='completed' returns only completed pathways."""
        pp_id = enroll_patient("MPI-401", pathway_id=4).patient_pathway_id
        assert pp_id is not None

        # Complete the pathway through all states
        updates = [
            {"id": "crit-nut-triagem", "met": True, "value": 4},
            {"id": "crit-nut-calorias", "met": True, "value": 85},
            {"id": "crit-nut-proteinas", "met": True, "value": 1.4},
            {"id": "crit-nut-residuo", "met": True, "value": 100},
            {"id": "crit-nut-albumina", "met": True, "value": 3.2},
            {"id": "crit-nut-diarreia", "met": True, "value": 0},
        ]
        evaluate_criteria("MPI-401", patient_pathway_id=pp_id, criteria_updates=updates)
        evaluate_criteria("MPI-401", patient_pathway_id=pp_id, criteria_updates=[])
        evaluate_criteria("MPI-401", patient_pathway_id=pp_id, criteria_updates=[])

        # Now active filter returns empty
        active = get_patient_pathways("MPI-401", status_filter="active")
        assert active == []

        # Completed filter returns it
        completed = get_patient_pathways("MPI-401", status_filter="completed")
        assert len(completed) == 1
        assert completed[0]["status"] == "completed"

    def test_get_patient_pathways_all_statuses(self) -> None:
        """status_filter='all' returns pathways regardless of status."""
        # Enroll and complete one pathway
        pp_id = enroll_patient("MPI-402", pathway_id=4).patient_pathway_id
        assert pp_id is not None

        updates = [
            {"id": "crit-nut-triagem", "met": True, "value": 4},
            {"id": "crit-nut-calorias", "met": True, "value": 85},
            {"id": "crit-nut-proteinas", "met": True, "value": 1.4},
            {"id": "crit-nut-residuo", "met": True, "value": 100},
            {"id": "crit-nut-albumina", "met": True, "value": 3.2},
            {"id": "crit-nut-diarreia", "met": True, "value": 0},
        ]
        evaluate_criteria("MPI-402", patient_pathway_id=pp_id, criteria_updates=updates)
        evaluate_criteria("MPI-402", patient_pathway_id=pp_id, criteria_updates=[])
        evaluate_criteria("MPI-402", patient_pathway_id=pp_id, criteria_updates=[])

        # Enroll in another pathway (active)
        enroll_patient("MPI-402", pathway_id=1)

        all_pathways = get_patient_pathways("MPI-402", status_filter="all")
        assert len(all_pathways) == 2
        statuses = {p["status"] for p in all_pathways}
        assert statuses == {"active", "completed"}


# =============================================================================
# Pathway Progress
# =============================================================================


class TestPathwayProgress:
    """get_pathway_progress — Rules 11, 12, 14."""

    def test_progress_has_criteria_summary(self) -> None:
        """Rule 14: progress includes criteria_summary with total/met/not_met/pending."""
        pp_id = enroll_patient("MPI-500", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        progress = get_pathway_progress("MPI-500", patient_pathway_id=pp_id)
        summary = progress.criteria_summary
        assert summary["total"] == 5  # ventilacao has 5 criteria
        assert summary["met"] == 0
        assert summary["not_met"] == 5
        assert summary["pending"] == 0

    def test_progress_after_criteria_updates(self) -> None:
        """Criteria summary updates correctly after evaluation."""
        pp_id = enroll_patient("MPI-501", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        evaluate_criteria(
            "MPI-501",
            patient_pathway_id=pp_id,
            criteria_updates=[
                {"id": "crit-vent-pf", "met": True, "value": 300},
                {"id": "crit-vent-peep", "met": True, "value": 8},
            ],
        )

        progress = get_pathway_progress("MPI-501", patient_pathway_id=pp_id)
        assert progress.criteria_summary["met"] == 2
        assert progress.criteria_summary["not_met"] == 3
        assert progress.criteria_summary["total"] == 5

    def test_progress_trend_none_without_transitions(self) -> None:
        """Rule 11: trend is 'none' when no state transitions have occurred."""
        pp_id = enroll_patient("MPI-502", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        progress = get_pathway_progress("MPI-502", patient_pathway_id=pp_id)
        assert progress.trend == "none"
        assert progress.state_history == []

    def test_progress_trend_improving_after_transition(self) -> None:
        """Rule 11: trend becomes 'improving' after forward state transitions."""
        pp_id = enroll_patient("MPI-503", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        updates = [
            {"id": "crit-vent-pf", "met": True, "value": 320},
            {"id": "crit-vent-peep", "met": True, "value": 8},
            {"id": "crit-vent-vc", "met": True, "value": 7},
            {"id": "crit-vent-plat", "met": True, "value": 25},
            {"id": "crit-vent-drive", "met": True, "value": 12},
        ]
        evaluate_criteria("MPI-503", patient_pathway_id=pp_id, criteria_updates=updates)

        progress = get_pathway_progress("MPI-503", patient_pathway_id=pp_id)
        assert progress.trend == "improving"
        assert len(progress.state_history) >= 1

        # Second transition: mark all criteria met again
        evaluate_criteria("MPI-503", patient_pathway_id=pp_id, criteria_updates=[])

        progress2 = get_pathway_progress("MPI-503", patient_pathway_id=pp_id)
        assert progress2.trend == "improving"
        assert len(progress2.state_history) >= 2

    def test_progress_has_recommendation_pt_br(self) -> None:
        """Rule 12: progress includes a PT-BR recommendation string."""
        pp_id = enroll_patient("MPI-504", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        progress = get_pathway_progress("MPI-504", patient_pathway_id=pp_id)
        assert progress.recommendation != ""
        assert "Dentro das metas" in progress.recommendation
        # Should be in Portuguese
        assert any(
            word in progress.recommendation.lower()
            for word in ["parâmetros", "avaliação", "acompanhamento", "adequados", "ventilação"]
        )

    def test_progress_recommendation_changes_with_severity(self) -> None:
        """Recommendation reflects severity level."""
        pp_id = enroll_patient("MPI-505", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        # Default severity (0 met out of 5) → critical
        evaluate_criteria(
            "MPI-505",
            patient_pathway_id=pp_id,
            criteria_updates=[{"id": "crit-vent-pf", "met": False}],
        )
        progress = get_pathway_progress("MPI-505", patient_pathway_id=pp_id)
        assert "CRÍTICO" in progress.recommendation

        # Mark 3 met (60%) → watch
        evaluate_criteria(
            "MPI-505",
            patient_pathway_id=pp_id,
            criteria_updates=[
                {"id": "crit-vent-pf", "met": True},
                {"id": "crit-vent-peep", "met": True},
                {"id": "crit-vent-vc", "met": True},
            ],
        )
        progress2 = get_pathway_progress("MPI-505", patient_pathway_id=pp_id)
        assert "Acompanhar" in progress2.recommendation
        assert "CRÍTICO" not in progress2.recommendation

    def test_progress_unknown_patient_pathway(self) -> None:
        """get_pathway_progress for unknown pp_id returns empty/fallback result."""
        progress = get_pathway_progress("MPI-999", patient_pathway_id=9999)
        assert progress.patient_pathway_id == 9999
        assert progress.pathway_name == "Desconhecido"
        assert progress.current_state == ""
        assert progress.criteria_summary == {"total": 0, "met": 0, "not_met": 0, "pending": 0}
        assert progress.criteria == []
        assert progress.state_history == []
        assert progress.trend == "none"
        assert "não localizada" in progress.recommendation

    def test_progress_respects_mpi_id(self) -> None:
        """get_pathway_progress validates mpi_id matches enrollment."""
        pp_id = enroll_patient("MPI-506", pathway_id=1).patient_pathway_id
        assert pp_id is not None

        # Wrong mpi_id should return empty/fallback
        progress = get_pathway_progress("MPI-WRONG", patient_pathway_id=pp_id)
        assert progress.pathway_name == "Desconhecido"
        assert "não localizada" in progress.recommendation


# =============================================================================
# TrilhasEngine Integration (M4 — new stateless engine)
# =============================================================================


class TestTrilhasEngineIntegration:
    """Tests for the new stateless TrilhasEngine (YAML-based).

    Validates that the new engine:
    - Loads YAML pathway definitions
    - Provides get_pathways() / get_pathway() API
    - Converts correctly to the flat dict format expected by the API
    - Falls back gracefully when YAML dirs are missing
    """

    def test_engine_loads_pathways(self) -> None:
        """TrilhasEngine loads at least 4 pathways from _work/alerts/pathways/."""
        from intensicare.services.trilhas_engine import TrilhasEngine

        engine = TrilhasEngine()
        pathways = engine.get_pathways()
        assert len(pathways) >= 4, (
            f"Expected at least 4 pathways loaded, got {len(pathways)}"
        )
        slugs = {p.slug for p in pathways}
        assert slugs >= {"ventilacao", "sepse", "desmame", "nutricao"}

    def test_engine_get_pathway_by_id(self) -> None:
        """get_pathway returns correct PathwayDefinition for ID 1."""
        from intensicare.services.trilhas_engine import TrilhasEngine

        engine = TrilhasEngine()
        p = engine.get_pathway(1)
        assert p is not None
        assert p.name == "Ventilação Mecânica"
        assert p.slug == "ventilacao"
        assert len(p.states) >= 2
        assert len(p.criteria) >= 2  # YAML-based: 2+ criteria

    def test_engine_get_pathway_returns_none_for_invalid(self) -> None:
        """get_pathway returns None for non-existent IDs."""
        from intensicare.services.trilhas_engine import TrilhasEngine

        engine = TrilhasEngine()
        assert engine.get_pathway(999) is None
        assert engine.get_pathway(0) is None

    def test_pathway_definition_to_flat_dict(self) -> None:
        """_pathway_def_to_flat_dict produces a dict compatible with _to_pathway_schema."""
        from intensicare.api.v1.pathways import _pathway_def_to_flat_dict
        from intensicare.services.trilhas_engine import TrilhasEngine

        engine = TrilhasEngine()
        pdef = engine.get_pathway(1)
        assert pdef is not None

        flat = _pathway_def_to_flat_dict(pdef)
        assert isinstance(flat, dict)
        assert flat["id"] == 1
        assert flat["name"] == "Ventilação Mecânica"
        assert flat["slug"] == "ventilacao"
        assert flat["active"] is True
        assert "states" in flat
        assert "criteria" in flat
        assert len(flat["states"]) >= 2
        assert len(flat["criteria"]) >= 2  # YAML-based: 2+ criteria

        # Verify flat criteria have expected fields
        for c in flat["criteria"]:
            assert "id" in c
            assert "name" in c
            assert "category" in c
            assert "unit" in c  # extracted from predicate

        # Verify flat states have expected fields
        for s in flat["states"]:
            assert "id" in s
            assert "name" in s
            assert "order" in s
            assert "is_terminal" in s

    def test_engine_patient_pathways_delegates_to_legacy(self) -> None:
        """engine.get_patient_pathways delegates to legacy store and returns results."""
        from intensicare.services.trilhas_engine import TrilhasEngine

        engine = TrilhasEngine()

        # Enroll via legacy to prime the store
        enroll_patient("MPI-ENG-001", pathway_id=1)

        # Query via engine (should find the enrollment)
        pathways = engine.get_patient_pathways("MPI-ENG-001")
        assert len(pathways) == 1
        assert pathways[0]["pathway_id"] == 1
        assert pathways[0]["mpi_id"] == "MPI-ENG-001"

    def test_engine_respects_patient_pathway_status(self) -> None:
        """Completed pathways visible via engine.get_patient_pathways."""
        from intensicare.services.trilhas_engine import TrilhasEngine

        engine = TrilhasEngine()

        pp_id = enroll_patient("MPI-ENG-002", pathway_id=4).patient_pathway_id
        assert pp_id is not None

        # Complete via legacy
        updates = [
            {"id": "crit-nut-triagem", "met": True, "value": 4},
            {"id": "crit-nut-calorias", "met": True, "value": 85},
            {"id": "crit-nut-proteinas", "met": True, "value": 1.4},
            {"id": "crit-nut-residuo", "met": True, "value": 100},
            {"id": "crit-nut-albumina", "met": True, "value": 3.2},
            {"id": "crit-nut-diarreia", "met": True, "value": 0},
        ]
        evaluate_criteria("MPI-ENG-002", patient_pathway_id=pp_id, criteria_updates=updates)
        evaluate_criteria("MPI-ENG-002", patient_pathway_id=pp_id, criteria_updates=[])
        evaluate_criteria("MPI-ENG-002", patient_pathway_id=pp_id, criteria_updates=[])

        pathways = engine.get_patient_pathways("MPI-ENG-002")
        assert len(pathways) == 1
        assert pathways[0]["status"] == "completed"

    def test_domain_re_exports_engine(self) -> None:
        """domain_trilhas_engine re-exports TrilhasEngine and PathwayDefinition."""
        from intensicare.services.domain_trilhas_engine import (
            PathwayDefinition,
            TrilhasEngine,
        )
        # Just verify they import without error
        assert TrilhasEngine is not None
        assert PathwayDefinition is not None

    def test_domain_re_exports_legacy(self) -> None:
        """domain_trilhas_engine still re-exports legacy PathwayStore types."""
        from intensicare.services.domain_trilhas_engine import (
            PATHWAY_SEEDS,
            PathwayStore,
            PatientPathwayDict,
            create_pathway_store,
            get_pathway_by_id,
            get_pathway_catalog,
        )
        assert PATHWAY_SEEDS is not None
        assert PathwayStore is not None
        assert PatientPathwayDict is not None
        assert create_pathway_store is not None
        assert get_pathway_by_id is not None
        assert get_pathway_catalog is not None
