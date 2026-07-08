"""Tests for Clinical Forms domain service — scoring engines for SOFA, RASS,
CAM-ICU, Glasgow, BPS/NRS.
"""
from __future__ import annotations

import pytest

from intensicare.services.domain_formularios import (
    FORM_DEFINITIONS,
    FormListResult,
    FormSubmissionResult,
    FormTypeInfo,
    SubmissionListResult,
    calculate_score,
    get_form_types,
    list_submissions,
    submit_form,
)


# ============================================================================
# get_form_types
# ============================================================================


class TestGetFormTypes:
    """Tests for get_form_types()."""

    def test_returns_5_form_types(self):
        """get_form_types should return exactly 5 clinical form types."""
        result = get_form_types()

        assert isinstance(result, FormListResult)
        assert result.total == 5
        assert len(result.items) == 5

    def test_form_types_have_required_fields(self):
        """Every form type should have id, name, description."""
        result = get_form_types()

        for item in result.items:
            assert isinstance(item, FormTypeInfo)
            assert item.id
            assert item.name
            assert item.description
            assert item.active is True
            assert item.version == "1.0.0"

    def test_form_types_ids_match_definitions(self):
        """Returned form type IDs should match FORM_DEFINITIONS keys."""
        result = get_form_types()
        ids = {item.id for item in result.items}

        expected = {"rass", "cam-icu", "bps-nrs", "glasgow", "sofa"}
        assert ids == expected


# ============================================================================
# submit_form
# ============================================================================


class TestSubmitForm:
    """Tests for submit_form()."""

    def test_submit_rass(self):
        """Submit a RASS form with valid score."""
        result = submit_form(
            mpi_id="P001",
            form_id="f-rass-01",
            form_type="rass",
            data={"nivel": -2},
            submitted_by="enfermeiro",
        )

        assert isinstance(result, FormSubmissionResult)
        assert result.mpi_id == "P001"
        assert result.form_type == "rass"
        assert result.score == -2.0
        assert result.severity == "Sedação leve"
        assert result.submitted_by == "enfermeiro"
        assert result.submitted_at  # ISO timestamp

    def test_submit_cam_icu_positive(self):
        """CAM-ICU should be positive when inicio_agudo + desatencao +
        pensamento_desorganizado are present."""
        result = submit_form(
            mpi_id="P002",
            form_id="f-cam-01",
            form_type="cam-icu",
            data={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": False,
            },
        )

        assert result.score == 1.0
        assert result.severity == "delirium_positivo"

    def test_submit_cam_icu_negative(self):
        """CAM-ICU should be negative when desatencao is False."""
        result = submit_form(
            mpi_id="P003",
            form_id="f-cam-02",
            form_type="cam-icu",
            data={
                "inicio_agudo": True,
                "desatencao": False,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": True,
            },
        )

        assert result.score == 0.0
        assert result.severity == "delirium_negativo"

    def test_submit_glasgow_max(self):
        """Glasgow max score (ocular=4, verbal=5, motora=6) → 15."""
        result = submit_form(
            mpi_id="P004",
            form_id="f-gcs-01",
            form_type="glasgow",
            data={"ocular": 4, "verbal": 5, "motora": 6},
        )

        assert result.score == 15.0
        assert result.severity == "leve"

    def test_submit_glasgow_min(self):
        """Glasgow min score (each component at minimum) → 3."""
        result = submit_form(
            mpi_id="P005",
            form_id="f-gcs-02",
            form_type="glasgow",
            data={"ocular": 1, "verbal": 1, "motora": 1},
        )

        assert result.score == 3.0
        assert result.severity == "muito_grave"

    def test_submit_bps_pain(self):
        """BPS pain score from facial, membros, ventilacao indicators."""
        result = submit_form(
            mpi_id="P006",
            form_id="f-pain-01",
            form_type="bps-nrs",
            data={
                "tipo": "bps",
                "expressao_facial": 3,
                "membros_superiores": 2,
                "ventilacao_mecanica_indicador": 1,
            },
        )

        assert result.score == 6.0
        assert result.severity == "dor_leve"

    def test_submit_nrs_pain(self):
        """NRS self-reported pain 0-10."""
        result = submit_form(
            mpi_id="P007",
            form_id="f-pain-02",
            form_type="bps-nrs",
            data={"tipo": "nrs", "nrs": 8},
        )

        assert result.score == 8.0
        assert result.severity == "dor_intensa"

    def test_submit_invalid_form_type_raises(self):
        """Submitting an unknown form_type must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown form_type"):
            submit_form(
                mpi_id="P008",
                form_id="f-bad",
                form_type="nonexistent",
                data={},
            )


# ============================================================================
# calculate_score — SOFA edge cases
# ============================================================================


class TestCalculateScoreSOFA:
    """Tests for calculate_score with SOFA form type."""

    def test_sofa_zero_all_normal(self):
        """SOFA = 0 when all organ systems are normal."""
        data = {
            "respiratorio": {"pao2_fio2": 500},
            "coagulacao": {"plaquetas": 200},
            "hepatico": {"bilirrubina": 0.8},
            "cardiovascular": {"pam": 80},
            "neurologico": {"glasgow": 15},
            "renal": {"creatinina": 0.9, "debito_urinario_24h": 1500},
        }
        score, severity = calculate_score("sofa", data)

        assert score == 0.0
        assert severity == "baixo_risco"

    def test_sofa_maximum_24(self):
        """SOFA = 24 (max possible) with worst scores in all 6 systems."""
        data = {
            "respiratorio": {
                "pao2_fio2": 50,
                "ventilacao_mecanica": True,
            },
            "coagulacao": {"plaquetas": 10},
            "hepatico": {"bilirrubina": 15.0},
            "cardiovascular": {
                "pam": 50,
                "vasopressor": "norepinefrina",
                "dose_vasopressor": 0.5,
            },
            "neurologico": {"glasgow": 3},
            "renal": {"creatinina": 6.0, "debito_urinario_24h": 100},
        }
        score, severity = calculate_score("sofa", data)

        assert score == 24.0
        assert severity == "risco_muito_alto"

    def test_sofa_respiratory_no_vent(self):
        """SOFA respiratory capped at 2 without mechanical ventilation."""
        data = {
            "respiratorio": {"pao2_fio2": 150},
            "coagulacao": {"plaquetas": 200},
            "hepatico": {"bilirrubina": 0.5},
            "cardiovascular": {"pam": 80},
            "neurologico": {"glasgow": 15},
            "renal": {"creatinina": 0.8, "debito_urinario_24h": 2000},
        }
        score, _ = calculate_score("sofa", data)

        # Only respiratory should contribute (pao2_fio2 150 → score 2 without vent)
        assert score == 2.0

    def test_sofa_with_vasopressor_dopamine(self):
        """Dopamine dosing influences SOFA cardiovascular score."""
        data = {
            "cardiovascular": {
                "pam": 55,
                "vasopressor": "dopamina",
                "dose_vasopressor": 10,
            },
        }
        score, _ = calculate_score("sofa", data)

        # dopamine <=15 → 3
        assert score == 3.0


# ============================================================================
# list_submissions
# ============================================================================


class TestListSubmissions:
    """Tests for list_submissions()."""

    def test_list_filter_by_mpi_id(self):
        """list_submissions should only return records for the given patient."""
        # Submit for two patients
        submit_form("P-A", "f1", "rass", {"nivel": 0})
        submit_form("P-A", "f2", "rass", {"nivel": -1})
        submit_form("P-B", "f3", "rass", {"nivel": 2})

        result = list_submissions("P-A")

        assert isinstance(result, SubmissionListResult)
        assert result.total == 2
        assert all(item.mpi_id == "P-A" for item in result.items)

    def test_list_pagination(self):
        """list_submissions should respect limit and offset."""
        for i in range(5):
            submit_form("P-C", f"f-pag-{i}", "rass", {"nivel": i - 2})

        result = list_submissions("P-C", limit=2, offset=1)

        assert len(result.items) == 2
        assert result.total == 5


# ============================================================================
# calculate_score — edge cases
# ============================================================================


class TestCalculateScoreEdgeCases:
    """Edge case tests for calculate_score dispatcher."""

    def test_invalid_form_type_raises(self):
        """Unknown form_type must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown form_type"):
            calculate_score("invalid", {})

    def test_cam_icu_positive_via_altered_consciousness(self):
        """CAM-ICU positive via nivel_consciencia_alterado instead of
        pensamento_desorganizado."""
        data = {
            "inicio_agudo": True,
            "desatencao": True,
            "pensamento_desorganizado": False,
            "nivel_consciencia_alterado": True,
        }
        score, severity = calculate_score("cam-icu", data)

        assert score == 1.0
        assert severity == "delirium_positivo"

    def test_rass_clamped_to_range(self):
        """RASS values outside -5..+4 are clamped."""
        score, severity = calculate_score("rass", {"nivel": 10})
        assert score == 4.0

        score, severity = calculate_score("rass", {"nivel": -10})
        assert score == -5.0

    def test_nrs_out_of_range_clamped(self):
        """NRS values outside 0-10 are clamped."""
        score, severity = calculate_score("bps-nrs", {"tipo": "nrs", "nrs": 20})
        assert score == 10.0
        assert severity == "dor_intensa"

        score, severity = calculate_score("bps-nrs", {"tipo": "nrs", "nrs": -5})
        assert score == 0.0
        assert severity == "sem_dor"

    def test_bps_missing_components_default_min(self):
        """Missing BPS components default to 1 each (score = 3)."""
        score, severity = calculate_score("bps-nrs", {
            "tipo": "bps",
            "expressao_facial": 1,
            "membros_superiores": 1,
            "ventilacao_mecanica_indicador": 1,
        })
        assert score == 3.0
        assert severity == "sem_dor"

    def test_bps_all_components_none_returns_none(self):
        """When all BPS components are None, returns (None, None)."""
        score, severity = calculate_score("bps-nrs", {"tipo": "bps"})
        assert score is None
        assert severity is None
