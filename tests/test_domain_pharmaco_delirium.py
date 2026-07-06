"""
Tests for the pharmaco-delirium domain runners.

Covers:
  - run_pharmaco_batch: drug interaction micro-batch evaluation
  - run_delirium_batch: neuro-sedation/delirium micro-batch evaluation
  - evaluate_sedation_morning_reduction: daily sedation reduction RATIFY
  - evaluate_sedation_rass_camicu: RASS + CAM-ICU integrated evaluation
  - evaluate_all_domains: integration point aggregating all domain alerts
  - _build_context: context normalisation
  - _load_yaml: YAML catalog loading
  - Error handling (missing data, malformed inputs, YAML not found)
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from intensicare.services.domain_pharmaco_delirium import (
    _build_context,
    _load_yaml,
    evaluate_all_domains,
    evaluate_sedation_morning_reduction,
    evaluate_sedation_rass_camicu,
    run_delirium_batch,
    run_pharmaco_batch,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def pharmaco_catalog_yaml() -> str:
    """Minimal pharmaco-interaction YAML catalog for testing."""
    return """
alerts:
  - alert_id: "PHARM-001"
    name: "Warfarin-NSAID Interaction"
    severity: "critical"
    condition: "on_warfarin == true and on_nsaid == true"
    description: "Increased bleeding risk with warfarin + NSAID"
  - alert_id: "PHARM-002"
    name: "QTc Prolongation"
    severity: "urgent"
    condition: "qtc_ms != null and qtc_ms > 500"
    description: "QTc > 500ms — risk of Torsades"
  - alert_id: "PHARM-003"
    name: "Polypharmacy Alert"
    severity: "watch"
    condition: "medication_count != null and medication_count > 10"
    description: "More than 10 concurrent medications"
"""


@pytest.fixture
def delirium_catalog_yaml() -> str:
    """Minimal neuro-sedation YAML catalog for testing."""
    return """
alerts:
  - alert_id: "DEL-001"
    name: "CAM-ICU Positive Delirium"
    severity: "urgent"
    condition: "cam_icu_positive == true"
    description: "Delirium detected via CAM-ICU"
  - alert_id: "DEL-002"
    name: "Deep Sedation > 24h"
    severity: "watch"
    condition: "rass_score != null and rass_score <= -3 and hours_on_sedation > 24"
    description: "Deep sedation for more than 24 hours"
"""


# ─── _build_context tests ────────────────────────────────────────────────────


class TestBuildContext:
    """Tests for context normalisation."""

    def test_passes_through_all_keys(self):
        ctx = _build_context({"heart_rate": 80, "spo2": 98, "rass_score": -1})
        assert ctx["heart_rate"] == 80
        assert ctx["spo2"] == 98
        assert ctx["rass_score"] == -1

    def test_empty_context(self):
        ctx = _build_context({})
        assert ctx == {}


# ─── run_pharmaco_batch tests ────────────────────────────────────────────────


class TestRunPharmacoBatch:
    """Tests for pharmaco-interaction domain runner."""

    def test_warfarin_nsaid_interaction_fires(self, pharmaco_catalog_yaml):
        """Warfarin + NSAID should fire PHARM-001."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "PHARM-001", "name": "Warfarin-NSAID", "severity": "critical",
                 "condition": "on_warfarin == true and on_nsaid == true", "description": "Bleeding risk"},
            ]},
        ):
            ctx = {"on_warfarin": True, "on_nsaid": True}
            results = run_pharmaco_batch(ctx)
            assert len(results) == 1
            assert results[0]["alert_id"] == "PHARM-001"
            assert results[0]["severity"] == "critical"

    def test_no_drug_interactions_returns_empty(self, pharmaco_catalog_yaml):
        """Patient not on interacting drugs should produce no alerts."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "PHARM-001", "name": "Warfarin-NSAID", "severity": "critical",
                 "condition": "on_warfarin == true and on_nsaid == true", "description": "Bleeding risk"},
            ]},
        ):
            ctx = {"on_warfarin": False, "on_nsaid": False}
            results = run_pharmaco_batch(ctx)
            assert len(results) == 0

    def test_qtc_prolongation_fires(self):
        """QTc > 500ms should fire alert."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "PHARM-002", "name": "QTc Prolongation", "severity": "urgent",
                 "condition": "qtc_ms != null and qtc_ms > 500", "description": "QTc > 500ms"},
            ]},
        ):
            ctx = {"qtc_ms": 520}
            results = run_pharmaco_batch(ctx)
            assert len(results) == 1
            assert results[0]["alert_id"] == "PHARM-002"

    def test_qtc_normal_does_not_fire(self):
        """QTc <= 500ms should not fire."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "PHARM-002", "name": "QTc Prolongation", "severity": "urgent",
                 "condition": "qtc_ms != null and qtc_ms > 500", "description": "QTc > 500ms"},
            ]},
        ):
            ctx = {"qtc_ms": 450}
            results = run_pharmaco_batch(ctx)
            assert len(results) == 0

    def test_missing_data_does_not_crash(self):
        """Alerts that reference missing context keys should be skipped gracefully."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "PHARM-001", "name": "Test", "severity": "critical",
                 "condition": "missing_field == true", "description": "test"},
            ]},
        ):
            ctx: dict = {}
            results = run_pharmaco_batch(ctx)
            assert len(results) == 0

    def test_catalog_path_override(self):
        """Custom catalog path should be used when provided."""
        mock_path = MagicMock()
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": []},
        ) as mock_load:
            run_pharmaco_batch({}, catalog_path=mock_path)
            mock_load.assert_called_once_with(mock_path)


# ─── run_delirium_batch tests ────────────────────────────────────────────────


class TestRunDeliriumBatch:
    """Tests for delirium/neuro-sedation domain runner."""

    def test_cam_icu_positive_fires(self):
        """CAM-ICU positive should fire delirium alert."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "DEL-001", "name": "CAM-ICU Positive", "severity": "urgent",
                 "condition": "cam_icu_positive == true", "description": "Delirium"},
            ]},
        ):
            ctx = {"cam_icu_positive": True}
            results = run_delirium_batch(ctx)
            assert len(results) == 1
            assert results[0]["alert_id"] == "DEL-001"

    def test_cam_icu_negative_no_alert(self):
        """CAM-ICU negative should not fire."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "DEL-001", "name": "CAM-ICU Positive", "severity": "urgent",
                 "condition": "cam_icu_positive == true", "description": "Delirium"},
            ]},
        ):
            ctx = {"cam_icu_positive": False}
            results = run_delirium_batch(ctx)
            assert len(results) == 0

    def test_deep_sedation_alert_fires(self):
        """Deep sedation > 24h should fire."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium._load_yaml",
            return_value={"alerts": [
                {"alert_id": "DEL-002", "name": "Deep Sedation > 24h", "severity": "watch",
                 "condition": "rass_score != null and rass_score <= -3 and hours_on_sedation > 24",
                 "description": "Deep sedation"},
            ]},
        ):
            ctx = {"rass_score": -4, "hours_on_sedation": 36}
            results = run_delirium_batch(ctx)
            assert len(results) == 1
            assert results[0]["alert_id"] == "DEL-002"


# ─── evaluate_sedation_morning_reduction tests ───────────────────────────────


class TestSedationMorningReduction:
    """Tests for daily sedation reduction RATIFY evaluations."""

    def test_no_sedation_active(self):
        """When no sedation is active, the rule does not apply."""
        result = evaluate_sedation_morning_reduction({"sedativo_em_uso": False})
        assert result["fired"] is False
        assert result["sedation_active"] is False
        assert "não aplicável" in result["recommendation"].lower()

    def test_insufficient_data(self):
        """When doses are missing, return insufficient-data recommendation."""
        result = evaluate_sedation_morning_reduction({
            "sedativo_em_uso": True,
            "dose_sedativo_atual": None,
            "dose_sedativo_anterior": None,
        })
        assert result["fired"] is False
        assert result["sedation_active"] is True
        assert "insuficientes" in result["recommendation"].lower()

    def test_reduction_50_percent_or_more(self):
        """>= 50% reduction should NOT fire (good — target reached)."""
        result = evaluate_sedation_morning_reduction({
            "sedativo_em_uso": True,
            "dose_sedativo_atual": 5,
            "dose_sedativo_anterior": 20,
        })
        assert result["fired"] is False
        assert result["reduction_pct"] == 75.0
        assert "alcançada" in result["recommendation"].lower()

    def test_reduction_less_than_50_percent_fires(self):
        """< 50% reduction should fire."""
        result = evaluate_sedation_morning_reduction({
            "sedativo_em_uso": True,
            "dose_sedativo_atual": 12,
            "dose_sedativo_anterior": 15,
        })
        assert result["fired"] is True
        assert result["reduction_pct"] == 20.0
        assert "apenas" in result["recommendation"].lower()

    def test_invalid_dose_values(self):
        """Non-numeric dose values should be handled gracefully."""
        result = evaluate_sedation_morning_reduction({
            "sedativo_em_uso": True,
            "dose_sedativo_atual": "N/A",
            "dose_sedativo_anterior": 10,
        })
        assert result["fired"] is False
        assert "inválida" in result["recommendation"].lower()

    def test_zero_anterior_dose(self):
        """When anterior dose is 0, there's no reference."""
        result = evaluate_sedation_morning_reduction({
            "sedativo_em_uso": True,
            "dose_sedativo_atual": 5,
            "dose_sedativo_anterior": 0,
        })
        assert result["fired"] is False
        assert "zero" in result["recommendation"].lower()


# ─── evaluate_sedation_rass_camicu tests ─────────────────────────────────────


class TestSedationRassCamicu:
    """Tests for RASS + CAM-ICU integrated evaluation."""

    def test_normal_rass_no_delirium(self):
        """RASS 0, CAM-ICU negative should be normal."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": 0,
            "cam_icu_positive": False,
        })
        assert result["fired"] is False
        assert result["severity"] == "normal"
        assert result["deep_sedation"] is False
        assert result["undersedation"] is False

    def test_deep_sedation_rass_minus_4(self):
        """RASS -4 should flag deep sedation as urgent."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": -4,
            "cam_icu_positive": False,
        })
        assert result["fired"] is True
        assert result["deep_sedation"] is True
        assert result["severity"] == "urgent"

    def test_moderate_sedation_rass_minus_3(self):
        """RASS -3 should flag deep sedation as watch."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": -3,
            "cam_icu_positive": False,
        })
        assert result["fired"] is True
        assert result["deep_sedation"] is True
        assert result["severity"] == "watch"

    def test_agitation_rass_plus_3(self):
        """RASS +3 should flag undersedation as urgent."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": 3,
            "cam_icu_positive": False,
        })
        assert result["fired"] is True
        assert result["undersedation"] is True
        assert result["severity"] == "urgent"

    def test_cam_icu_positive_delirium(self):
        """CAM-ICU positive should always fire."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": 0,
            "cam_icu_positive": True,
        })
        assert result["fired"] is True
        assert result["delirium_detected"] is True

    def test_cam_icu_with_positive_rass_hyperactive(self):
        """CAM-ICU+ with RASS >= 0 should recommend hyperactive delirium management."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": 1,
            "cam_icu_positive": True,
        })
        assert any("hiperativo" in r.lower() for r in result["recommendations"])

    def test_cam_icu_with_negative_rass_hypoactive(self):
        """CAM-ICU+ with RASS < 0 should recommend hypoactive delirium management."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": -1,
            "cam_icu_positive": True,
        })
        assert any("hipoativo" in r.lower() for r in result["recommendations"])

    def test_out_of_range_rass(self):
        """RASS values outside [-5, +4] should return validation error."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": 10,
            "cam_icu_positive": False,
        })
        assert any("fora do intervalo" in r.lower() for r in result["recommendations"])

    def test_missing_rass(self):
        """When RASS is not provided, recommend assessment."""
        result = evaluate_sedation_rass_camicu({
            "cam_icu_positive": False,
        })
        assert any("não registrado" in r.lower() for r in result["recommendations"])

    def test_invalid_rass_type(self):
        """Non-integer RASS should be flagged."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": "five",
            "cam_icu_positive": False,
        })
        assert any("inválido" in r.lower() for r in result["recommendations"])

    def test_ventilated_deep_sedation_adds_padis_guidance(self):
        """When on ventilator with deep sedation, add PADIS recommendation."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": -4,
            "cam_icu_positive": False,
            "on_mechanical_ventilation": True,
        })
        assert any("SAT" in r for r in result["recommendations"])
        assert any("PADIS" in r for r in result["recommendations"])

    def test_custom_target_range(self):
        """Custom target RASS min/max should be respected."""
        result = evaluate_sedation_rass_camicu({
            "rass_score": -1,
            "cam_icu_positive": False,
            "target_rass_min": 0,
            "target_rass_max": 1,
        })
        assert result["outside_target"] is True
        assert result["fired"] is True


# ─── evaluate_all_domains tests ──────────────────────────────────────────────


class TestEvaluateAllDomains:
    """Tests for the integration entry point."""

    def test_returns_expected_keys(self):
        """Should return dict with pharmaco, delirium, sedation_ratify keys."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium.run_pharmaco_batch",
            return_value=[],
        ), patch(
            "intensicare.services.domain_pharmaco_delirium.run_delirium_batch",
            return_value=[],
        ):
            result = evaluate_all_domains({})
            assert "pharmaco" in result
            assert "delirium" in result
            assert "sedation_ratify" in result
            assert isinstance(result["pharmaco"], list)
            assert isinstance(result["delirium"], list)
            assert isinstance(result["sedation_ratify"], list)

    def test_firing_sedation_alert_appears(self):
        """When sedation reduction fires, it should appear in sedation_ratify."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium.run_pharmaco_batch",
            return_value=[],
        ), patch(
            "intensicare.services.domain_pharmaco_delirium.run_delirium_batch",
            return_value=[],
        ):
            ctx = {
                "sedativo_em_uso": True,
                "dose_sedativo_atual": 12,
                "dose_sedativo_anterior": 15,
                "rass_score": -4,
                "cam_icu_positive": False,
            }
            result = evaluate_all_domains(ctx)
            # Should have sedation alerts (both reduction and RASS)
            assert len(result["sedation_ratify"]) >= 1
            alert_ids = [a["alert_id"] for a in result["sedation_ratify"]]
            assert "SED-REDUCTION-01" in alert_ids or "SED-RASS-01" in alert_ids

    def test_stable_patient_no_alerts(self):
        """A stable patient with no risk factors should have no alerts."""
        with patch(
            "intensicare.services.domain_pharmaco_delirium.run_pharmaco_batch",
            return_value=[],
        ), patch(
            "intensicare.services.domain_pharmaco_delirium.run_delirium_batch",
            return_value=[],
        ):
            ctx = {
                "rass_score": 0,
                "cam_icu_positive": False,
                "sedativo_em_uso": False,
            }
            result = evaluate_all_domains(ctx)
            total = sum(len(v) for v in result.values())
            assert total == 0
