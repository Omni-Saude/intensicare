"""Tests for Sedation domain service — RASS labels, CAM-ICU algorithm,
deep sedation gate, BPS/NRS validators.
"""

from __future__ import annotations

import pytest

from intensicare.services.domain_sedacao import (
    CAMICUFeatures,
    SedationRecord,
    _calculate_rass_label,
    _evaluate_cam_icu,
    _validate_bps,
    _validate_nrs,
    _validate_rass,
    assess_sedation_pure,
    assess_sedation_sync,
    evaluate_cam_icu_batch,
)

# ============================================================================
# _calculate_rass_label
# ============================================================================


class TestRassLabel:
    """Tests for _calculate_rass_label()."""

    @pytest.mark.parametrize(
        "score,expected",
        [
            (-5, "Não despertável"),
            (-4, "Sedação profunda"),
            (-3, "Sedação moderada"),
            (-2, "Sedação leve"),
            (-1, "Sonolento"),
            (0, "Alerta e calmo"),
            (1, "Inquieto"),
            (2, "Agitado"),
            (3, "Muito agitado"),
            (4, "Combativo"),
        ],
    )
    def test_rass_labels_full_range(self, score, expected):
        """Every RASS score from -5 to +4 maps to the correct label."""
        assert _calculate_rass_label(score) == expected

    def test_rass_label_out_of_range_returns_desconhecido(self):
        """Scores outside -5..+4 return 'Desconhecido'."""
        assert _calculate_rass_label(-6) == "Desconhecido"
        assert _calculate_rass_label(5) == "Desconhecido"
        assert _calculate_rass_label(100) == "Desconhecido"


# ============================================================================
# _evaluate_cam_icu
# ============================================================================


class TestEvaluateCamICU:
    """Tests for _evaluate_cam_icu()."""

    def test_positive_all_features_true(self):
        """CAM-ICU positive when all features are True."""
        is_pos, features = _evaluate_cam_icu(
            {
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": True,
            }
        )

        assert is_pos is True
        assert isinstance(features, CAMICUFeatures)
        assert features.inicio_agudo is True
        assert features.desatencao is True

    def test_positive_via_feature_3_altered_loc(self):
        """CAM-ICU positive with feature 1+2+3 (no feature 4)."""
        is_pos, _ = _evaluate_cam_icu(
            {
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": False,
                "nivel_consciencia_alterado": True,
            }
        )

        assert is_pos is True

    def test_positive_via_feature_4_disorganized(self):
        """CAM-ICU positive with feature 1+2+4 (no feature 3)."""
        is_pos, _ = _evaluate_cam_icu(
            {
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": False,
            }
        )

        assert is_pos is True

    def test_negative_missing_feature_1(self):
        """CAM-ICU negative when feature 1 (inicio_agudo) is False."""
        is_pos, _ = _evaluate_cam_icu(
            {
                "inicio_agudo": False,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": True,
            }
        )

        assert is_pos is False

    def test_negative_missing_feature_2(self):
        """CAM-ICU negative when feature 2 (desatencao) is False."""
        is_pos, _ = _evaluate_cam_icu(
            {
                "inicio_agudo": True,
                "desatencao": False,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": True,
            }
        )

        assert is_pos is False

    def test_negative_missing_features_3_and_4(self):
        """CAM-ICU negative when both feature 3 and 4 are False
        (required: at least one of 3 or 4 must be True)."""
        is_pos, _ = _evaluate_cam_icu(
            {
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": False,
                "nivel_consciencia_alterado": False,
            }
        )

        assert is_pos is False

    def test_default_missing_keys_are_false(self):
        """Missing CAM-ICU feature keys default to False."""
        is_pos, _ = _evaluate_cam_icu({})

        assert is_pos is False

    def test_accepts_camicu_features_dataclass(self):
        """_evaluate_cam_icu should also accept a CAMICUFeatures dataclass."""
        features = CAMICUFeatures(
            inicio_agudo=True,
            desatencao=True,
            pensamento_desorganizado=True,
            nivel_consciencia_alterado=False,
        )
        is_pos, result_features = _evaluate_cam_icu(features)

        assert is_pos is True
        assert result_features is features  # same object returned


# ============================================================================
# Deep sedation gate — assess_sedation_pure / assess_sedation_sync
# ============================================================================


class TestDeepSedationGate:
    """Tests for the deep sedation gate (RASS <= -4 → CAM-ICU unassessable)."""

    def test_deep_sedation_cam_icu_none(self):
        """When RASS <= -4, CAM-ICU should not be assessable (result = None)."""
        record = assess_sedation_sync(
            mpi_id="P-DEEP",
            rass_score=-4,
            cam_icu_features={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": True,
            },
        )

        assert record.cam_icu_positive is None
        assert record.rass_label == "Sedação profunda"

    def test_deep_sedation_rass_minus5(self):
        """RASS -5 (não despertável) also blocks CAM-ICU assessment."""
        record = assess_sedation_sync(
            mpi_id="P-NODES",
            rass_score=-5,
            cam_icu_features={"inicio_agudo": True, "desatencao": True},
        )

        assert record.cam_icu_positive is None
        assert record.rass_label == "Não despertável"

    def test_rass_minus3_allows_cam_icu(self):
        """RASS -3 (moderate sedation) still allows CAM-ICU assessment."""
        record = assess_sedation_sync(
            mpi_id="P-MOD",
            rass_score=-3,
            cam_icu_features={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": False,
            },
        )

        assert record.cam_icu_positive is True
        assert record.rass_label == "Sedação moderada"

    def test_pure_assess_returns_sedation_record(self):
        """assess_sedation_pure returns a fully populated SedationRecord."""
        record = assess_sedation_pure(
            mpi_id="P-PURE",
            rass_score=0,
            bps_score=5,
            nrs_score=3,
            cam_icu_features={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": False,
            },
            current_sedation="Propofol 20 mL/h",
            assessed_by="medico",
            notes="Paciente estável",
        )

        assert isinstance(record, SedationRecord)
        assert record.mpi_id == "P-PURE"
        assert record.rass_score == 0
        assert record.rass_label == "Alerta e calmo"
        assert record.bps_score == 5
        assert record.nrs_score == 3
        assert record.cam_icu_positive is True
        assert record.current_sedation == "Propofol 20 mL/h"
        assert record.assessed_by == "medico"
        assert record.notes == "Paciente estável"
        assert record.assessed_at  # ISO timestamp


# ============================================================================
# Validation — RASS, BPS, NRS
# ============================================================================


class TestValidators:
    """Tests for _validate_rass, _validate_bps, _validate_nrs."""

    @pytest.mark.parametrize("score", [-5, -3, 0, 2, 4])
    def test_validate_rass_valid(self, score):
        """Valid RASS scores (-5 to +4) pass validation."""
        assert _validate_rass(score) is True

    @pytest.mark.parametrize("score", [-6, -10, 5, 10])
    def test_validate_rass_invalid(self, score):
        """Invalid RASS scores (outside -5..+4) fail validation."""
        assert _validate_rass(score) is False

    @pytest.mark.parametrize("score", [3, 5, 8, 12])
    def test_validate_bps_valid(self, score):
        """Valid BPS scores (3-12) pass validation."""
        assert _validate_bps(score) is True

    @pytest.mark.parametrize("score", [0, 1, 2, 13, 20])
    def test_validate_bps_invalid(self, score):
        """Invalid BPS scores (outside 3-12) fail validation."""
        assert _validate_bps(score) is False

    @pytest.mark.parametrize("score", [0, 3, 7, 10])
    def test_validate_nrs_valid(self, score):
        """Valid NRS scores (0-10) pass validation."""
        assert _validate_nrs(score) is True

    @pytest.mark.parametrize("score", [-1, -5, 11, 20])
    def test_validate_nrs_invalid(self, score):
        """Invalid NRS scores (outside 0-10) fail validation."""
        assert _validate_nrs(score) is False


# ============================================================================
# Validation errors in assess_sedation_sync
# ============================================================================


class TestAssessSedationValidationErrors:
    """Tests for ValueError raised on invalid score ranges."""

    def test_rass_out_of_range_raises(self):
        """RASS outside -5..+4 must raise ValueError."""
        with pytest.raises(ValueError, match="RASS score"):
            assess_sedation_sync("P-ERR", rass_score=10)

    def test_bps_out_of_range_raises(self):
        """BPS outside 3-12 must raise ValueError."""
        with pytest.raises(ValueError, match="BPS score"):
            assess_sedation_sync("P-ERR", bps_score=20)

    def test_nrs_out_of_range_raises(self):
        """NRS outside 0-10 must raise ValueError."""
        with pytest.raises(ValueError, match="NRS score"):
            assess_sedation_sync("P-ERR", nrs_score=15)


# ============================================================================
# evaluate_cam_icu_batch
# ============================================================================


class TestEvaluateCamICUBatch:
    """Tests for evaluate_cam_icu_batch()."""

    def test_batch_deep_sedation_gate(self):
        """Batch evaluation returns unassessable when RASS <= -4."""
        result = evaluate_cam_icu_batch(
            features={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": True,
            },
            rass_score=-5,
        )

        assert result["cam_icu_positive"] is None
        assert result["cam_icu_assessable"] is False
        assert "sedado" in result["recommendation"].lower()

    def test_batch_hiperativo_delirium(self):
        """Hyperactive delirium recommendation when CAM-ICU+ with RASS >= 0."""
        result = evaluate_cam_icu_batch(
            features={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": False,
            },
            rass_score=2,
        )

        assert result["cam_icu_positive"] is True
        assert result["cam_icu_assessable"] is True
        assert "hiperativo" in result["recommendation"].lower()

    def test_batch_hipoativo_delirium(self):
        """Hypoactive delirium recommendation when CAM-ICU+ with RASS < 0."""
        result = evaluate_cam_icu_batch(
            features={
                "inicio_agudo": True,
                "desatencao": True,
                "pensamento_desorganizado": True,
                "nivel_consciencia_alterado": False,
            },
            rass_score=-1,
        )

        assert result["cam_icu_positive"] is True
        assert result["cam_icu_assessable"] is True
        assert "hipoativo" in result["recommendation"].lower()

    def test_batch_negative_no_recommendation(self):
        """CAM-ICU negative returns no recommendation."""
        result = evaluate_cam_icu_batch(
            features={
                "inicio_agudo": False,
                "desatencao": False,
                "pensamento_desorganizado": False,
                "nivel_consciencia_alterado": False,
            },
            rass_score=0,
        )

        assert result["cam_icu_positive"] is False
        assert result["cam_icu_assessable"] is True
        assert result["recommendation"] is None
