"""
Tests for AKI domain (WO-025) — 3 KDIGO alerts, 17 test vectors.

Covers:
- ALERT-AKI-KDIGO-STAGE-01: KDIGO staging (7 vectors)
- ALERT-AKI-PROGRESSION-02: Stage progression (5 vectors)
- ALERT-AKI-NEPHROTOXIN-03: Nephrotoxic risk (5 vectors)
- Boundary: Cr=1.5x inclusive; UO <0.5 strict
- KDIGO stage 1/2/3 correct
- CRIT never auto-resolves
"""

from __future__ import annotations

import pytest

from intensicare.schemas.severity import SeverityLevel
from intensicare.services.domain_aki import (
    AkiAlertResult,
    AKI_ALERT_DEFINITIONS,
    _check_nephrotoxic_combo,
    compute_kdigo_stage,
    evaluate_all,
    evaluate_kdigo_stage,
    evaluate_nephrotoxin,
    evaluate_progression,
    should_auto_resolve,
)


# ===========================================================================
# ALERT-AKI-KDIGO-STAGE-01 — 7 test vectors
# ===========================================================================


class TestKdigoStage:
    """TV-1 through TV-7 from aki.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — Cr 1.6x baseline → stage 1 → watch
    # ------------------------------------------------------------------
    def test_tv1_creatinine_ratio_stage_1(self):
        """TV-1: Cr 1.6 = 1.6x baseline (>=1.5x) → stage 1 → watch."""
        inputs = {
            "creatinina": 1.6,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.9,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 1
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: fire — Cr 2.2x baseline → stage 2 → urgent
    # ------------------------------------------------------------------
    def test_tv2_creatinine_ratio_stage_2(self):
        """TV-2: Cr 2.2x baseline → stage 2 → urgent."""
        inputs = {
            "creatinina": 2.2,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.9,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 2
        assert result.band == "urgent"
        assert result.severity == SeverityLevel.URGENT

    # ------------------------------------------------------------------
    # TV-3: fire — UO 0.25 mL/kg/h (<0.3) → stage_uo 3 → critical
    # ------------------------------------------------------------------
    def test_tv3_urine_output_stage_3(self):
        """TV-3: UO 0.25 < 0.3 → stage_uo 3 → critical (max of axes)."""
        inputs = {
            "creatinina": 1.0,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.25,
            "peso": 70,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 3
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL

    # ------------------------------------------------------------------
    # TV-4: no-fire — Cr 1.1x baseline, UO normal → stage 0
    # ------------------------------------------------------------------
    def test_tv4_normal_no_fire(self):
        """TV-4: Cr 1.1x baseline (<1.5x), delta 0.1<0.3, UO normal → stage 0."""
        inputs = {
            "creatinina": 1.1,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.9,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is False
        assert result.kdigo_stage == 0
        assert result.band is None
        assert result.severity is None

    # ------------------------------------------------------------------
    # TV-5: boundary — Cr exactly 1.5x baseline → fire (inclusive)
    #         UO exactly 0.5 → does NOT fire (<0.5 strict)
    # ------------------------------------------------------------------
    def test_tv5_boundary_cr_ratio_inclusive(self):
        """TV-5: Cr exactly 1.5x → stage 1 (>=1.5x inclusive);
        UO exactly 0.5 does NOT fire (<0.5 strict)."""
        inputs = {
            "creatinina": 1.5,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.5,
            "peso": 70,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 1
        assert result.band == "watch"
        # Verify it's from Cr axis, not UO axis
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-6: boundary — delta 0.29 < 0.3, 1.29x < 1.5x, UO exactly 0.5
    #         not <0.5 → stage 0
    # ------------------------------------------------------------------
    def test_tv6_boundary_sub_threshold_no_fire(self):
        """TV-6: delta 0.29<0.3, 1.29x<1.5x, UO exactly 0.5 not <0.5 → stage 0."""
        inputs = {
            "creatinina": 1.29,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.5,
            "peso": 70,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is False
        assert result.kdigo_stage == 0

    # ------------------------------------------------------------------
    # TV-7: fire — Cr 4.2 >= 4.0 with acute rise 0.6 >= 0.5 → stage 3
    # ------------------------------------------------------------------
    def test_tv7_high_creatinine_with_acute_rise_stage_3(self):
        """TV-7: Cr 4.2>=4.0 with acute rise 0.6>=0.5 → stage 3 → critical."""
        inputs = {
            "creatinina": 4.2,
            "creatinina_basal": 3.9,
            "delta_cr_48h": 0.6,
            "terapia_renal_substitutiva": False,
        }
        result = evaluate_kdigo_stage(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 3
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL


# ===========================================================================
# compute_kdigo_stage — additional stage logic tests
# ===========================================================================


class TestComputeKdigoStage:
    """Additional tests for KDIGO stage computation logic."""

    def test_stage_3_cr_triple_baseline(self):
        """Cr >= 3.0 * baseline → stage 3."""
        assert compute_kdigo_stage({"creatinina": 3.0, "creatinina_basal": 1.0}) == 3

    def test_stage_3_rrt_active(self):
        """RRT active → stage 3 regardless of Cr."""
        assert (
            compute_kdigo_stage({
                "creatinina": 1.0,
                "creatinina_basal": 1.0,
                "terapia_renal_substitutiva": True,
            })
            == 3
        )

    def test_stage_2_cr_double_baseline(self):
        """Cr >= 2.0 * baseline → stage 2."""
        assert compute_kdigo_stage({"creatinina": 2.0, "creatinina_basal": 1.0}) == 2

    def test_stage_1_delta_cr(self):
        """delta_cr_48h >= 0.3 → stage 1."""
        assert (
            compute_kdigo_stage({
                "creatinina": 1.3,
                "creatinina_basal": 1.0,
                "delta_cr_48h": 0.3,
            })
            == 1
        )

    def test_stage_uo_3(self):
        """UO < 0.3 → stage_uo 3."""
        assert (
            compute_kdigo_stage({
                "debito_urinario_horario": 0.2,
            })
            == 3
        )

    def test_stage_uo_1(self):
        """UO < 0.5 but >= 0.3 → stage_uo 1."""
        assert (
            compute_kdigo_stage({
                "debito_urinario_horario": 0.4,
            })
            == 1
        )

    def test_max_of_axes(self):
        """max(stage_cr=2, stage_uo=3) → 3."""
        assert (
            compute_kdigo_stage({
                "creatinina": 2.2,
                "creatinina_basal": 1.0,
                "debito_urinario_horario": 0.25,
            })
            == 3
        )

    def test_stage_0_no_inputs(self):
        """No inputs → stage 0."""
        assert compute_kdigo_stage({}) == 0


# ===========================================================================
# ALERT-AKI-PROGRESSION-02 — 5 test vectors
# ===========================================================================


class TestProgression:
    """TV-1 through TV-5 for progression alert."""

    # ------------------------------------------------------------------
    # TV-1: fire — stage 1 → 2 → urgent
    # ------------------------------------------------------------------
    def test_tv1_progression_1_to_2(self):
        """TV-1: stage 1 → 2 within 24h → urgent."""
        inputs = {"kdigo_stage_now": 2, "kdigo_stage_24h_ago": 1}
        result = evaluate_progression(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 2
        assert result.band == "urgent"
        assert result.severity == SeverityLevel.URGENT

    # ------------------------------------------------------------------
    # TV-2: fire — stage 1 → 3 → critical (escalation)
    # ------------------------------------------------------------------
    def test_tv2_progression_1_to_3_critical(self):
        """TV-2: stage 1 → 3 → critical (new stage == 3)."""
        inputs = {"kdigo_stage_now": 3, "kdigo_stage_24h_ago": 1}
        result = evaluate_progression(inputs)
        assert result.fired is True
        assert result.kdigo_stage == 3
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL

    # ------------------------------------------------------------------
    # TV-3: no-fire — static stage 2
    # ------------------------------------------------------------------
    def test_tv3_static_stage_no_fire(self):
        """TV-3: no increase (static stage 2) → staging alert owns this."""
        inputs = {"kdigo_stage_now": 2, "kdigo_stage_24h_ago": 2}
        result = evaluate_progression(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: boundary — null prior stage → no-fire
    # ------------------------------------------------------------------
    def test_tv4_null_prior_stage_boundary(self):
        """TV-4: no prior stage (null) → first detection is staging alert's job."""
        inputs = {"kdigo_stage_now": 1, "kdigo_stage_24h_ago": None}
        result = evaluate_progression(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: no-fire — improving (2 → 1)
    # ------------------------------------------------------------------
    def test_tv5_improving_no_fire(self):
        """TV-5: improving (2 → 1) → no progression alert."""
        inputs = {"kdigo_stage_now": 1, "kdigo_stage_24h_ago": 2}
        result = evaluate_progression(inputs)
        assert result.fired is False


# ===========================================================================
# ALERT-AKI-NEPHROTOXIN-03 — 5 test vectors
# ===========================================================================


class TestNephrotoxin:
    """TV-1 through TV-5 for nephrotoxin alert."""

    # ------------------------------------------------------------------
    # TV-1: fire — rising_cr AND vanco+aminoglycoside
    # ------------------------------------------------------------------
    def test_tv1_vanco_amino_rising_cr(self):
        """TV-1: rising_cr (1.3 > 1.0+0.2) AND vanco+aminoglycoside → watch."""
        inputs = {
            "creatinina": 1.3,
            "creatinina_basal": 1.0,
            "vancomicina_ativa": True,
            "aminoglicosideo_ativo": True,
        }
        result = evaluate_nephrotoxin(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: fire — rising_cr AND ACEi/ARB + volume depletion
    # ------------------------------------------------------------------
    def test_tv2_ieca_hypovolemia_rising_cr(self):
        """TV-2: rising_cr AND ACEi/ARB + volume depletion branch."""
        inputs = {
            "creatinina": 1.4,
            "creatinina_basal": 1.0,
            "ieca_bra_ativo": True,
            "hipovolemia": True,
        }
        result = evaluate_nephrotoxin(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-3: no-fire — combo present but Cr <= baseline+0.2
    # ------------------------------------------------------------------
    def test_tv3_combo_present_but_no_renal_signal(self):
        """TV-3: combo present but Cr 1.15 <= baseline+0.2 → no renal signal."""
        inputs = {
            "creatinina": 1.15,
            "creatinina_basal": 1.0,
            "vancomicina_ativa": True,
            "aminoglicosideo_ativo": True,
        }
        result = evaluate_nephrotoxin(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: boundary — Cr exactly baseline+0.2 → no-fire (strict >)
    # ------------------------------------------------------------------
    def test_tv4_boundary_exact_plus_02_no_fire(self):
        """TV-4: Cr exactly baseline+0.2 (1.2) NOT > 0.2 rise (strict) → no-fire."""
        inputs = {
            "creatinina": 1.2,
            "creatinina_basal": 1.0,
            "vancomicina_ativa": True,
            "aminoglicosideo_ativo": True,
        }
        result = evaluate_nephrotoxin(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: no-fire — rising_cr true but only one nephrotoxin
    # ------------------------------------------------------------------
    def test_tv5_single_nephrotoxin_no_combo(self):
        """TV-5: rising_cr true but only vancomycin alone → combo false → no-fire."""
        inputs = {
            "creatinina": 1.5,
            "creatinina_basal": 1.0,
            "vancomicina_ativa": True,
            "aminoglicosideo_ativo": False,
            "contraste_iodado": False,
        }
        result = evaluate_nephrotoxin(inputs)
        assert result.fired is False


# ===========================================================================
# Nephrotoxic combo helper tests
# ===========================================================================


class TestNephrotoxicCombo:
    """Unit tests for the combo checker."""

    def test_vanco_amino(self):
        assert _check_nephrotoxic_combo({
            "vancomicina_ativa": True, "aminoglicosideo_ativo": True
        })

    def test_vanco_contraste(self):
        assert _check_nephrotoxic_combo({
            "vancomicina_ativa": True, "contraste_iodado": True
        })

    def test_amino_aine(self):
        assert _check_nephrotoxic_combo({
            "aminoglicosideo_ativo": True, "aine_ativo": True
        })

    def test_ieca_hipovolemia(self):
        assert _check_nephrotoxic_combo({
            "ieca_bra_ativo": True, "hipovolemia": True
        })

    def test_no_combo_single_drug(self):
        assert not _check_nephrotoxic_combo({
            "vancomicina_ativa": True,
        })

    def test_no_combo_wrong_pairs(self):
        assert not _check_nephrotoxic_combo({
            "vancomicina_ativa": True,
            "aine_ativo": True,
        })


# ===========================================================================
# Unified evaluate_all
# ===========================================================================


class TestEvaluateAll:
    """Integration: evaluate_all returns all 3 results."""

    def test_all_three_results_returned(self):
        """evaluate_all should return dict with 3 keys."""
        inputs = {
            "creatinina": 1.6,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.9,
            "kdigo_stage_now": 1,
            "kdigo_stage_24h_ago": 0,
            "vancomicina_ativa": True,
            "aminoglicosideo_ativo": True,
        }
        results = evaluate_all(inputs)
        assert set(results.keys()) == {
            "ALERT-AKI-KDIGO-STAGE-01",
            "ALERT-AKI-PROGRESSION-02",
            "ALERT-AKI-NEPHROTOXIN-03",
        }
        assert results["ALERT-AKI-KDIGO-STAGE-01"].fired is True
        assert results["ALERT-AKI-PROGRESSION-02"].fired is True
        assert results["ALERT-AKI-NEPHROTOXIN-03"].fired is True

    def test_all_no_fire(self):
        """Normal inputs → all no-fire."""
        inputs = {
            "creatinina": 1.0,
            "creatinina_basal": 1.0,
            "debito_urinario_horario": 0.9,
            "kdigo_stage_now": 0,
            "kdigo_stage_24h_ago": 0,
        }
        results = evaluate_all(inputs)
        for r in results.values():
            assert r.fired is False


# ===========================================================================
# CRIT non-auto-resolve guard
# ===========================================================================


class TestCritNonAutoResolve:
    """CRIT alerts must NEVER auto-resolve."""

    def test_crit_never_auto_resolves(self):
        """CRIT alert should never auto-resolve even with fresh data."""
        result = AkiAlertResult(
            alert_id="ALERT-AKI-KDIGO-STAGE-01",
            name="test",
            fired=True,
            severity=SeverityLevel.CRITICAL,
        )
        assert should_auto_resolve(result, {}, is_stale=False) is False
        assert should_auto_resolve(result, {}, is_stale=True) is False

    def test_watch_auto_resolves_on_stale(self):
        """Watch alert may auto-resolve on stale data."""
        result = AkiAlertResult(
            alert_id="ALERT-AKI-NEPHROTOXIN-03",
            name="test",
            fired=True,
            severity=SeverityLevel.WATCH,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True
        assert should_auto_resolve(result, {}, is_stale=False) is False

    def test_urgent_auto_resolves_on_stale(self):
        """Urgent alert may auto-resolve on stale data."""
        result = AkiAlertResult(
            alert_id="ALERT-AKI-PROGRESSION-02",
            name="test",
            fired=True,
            severity=SeverityLevel.URGENT,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True


# ===========================================================================
# Alert definitions seeding
# ===========================================================================


class TestAlertDefinitions:
    """Verify AKI_ALERT_DEFINITIONS are well-formed."""

    def test_three_definitions(self):
        """Should have 3 alert definitions."""
        assert len(AKI_ALERT_DEFINITIONS) == 3

    def test_all_have_definition_version(self):
        """Each definition must have a definition_version starting with alert ID."""
        for d in AKI_ALERT_DEFINITIONS:
            assert d["definition_version"]
            assert "-" in d["definition_version"]
            assert d["semver"] == "1.0.0"
            assert len(d["spec_hash"]) == 16
            assert d["description"]
