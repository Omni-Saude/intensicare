"""
Tests for Hemodynamics domain (WO-028) — 6 alerts, 34 test vectors.

Covers:
- ALERT-HEMO-SHOCK-INDEX-01: Shock index screening (5 vectors)
- ALERT-HEMO-LACTATE-CLEARANCE-02: Lactate clearance failure (6 vectors)
- ALERT-HEMO-VASO-ESCALATION-03: Vasopressor escalation (6 vectors)
- ALERT-HEMO-REFRACTORY-SHOCK-04: Refractory shock (6 vectors)
- ALERT-HEMO-FLUID-NONRESPONSIVE-05: Fluid non-responsiveness (5 vectors)
- ALERT-HEMO-ANTIHTN-CONFLICT-06: Antihypertensive conflict (6 vectors)

Total: 34 vectors, exactly matching hemodynamics.yaml.
All vasopressor dosing canonical mcg/kg/min.
"""

from __future__ import annotations

from intensicare.schemas.severity import SeverityLevel
from intensicare.services.domain_hemo import (
    HEMO_ALERT_DEFINITIONS,
    HemoAlertResult,
    evaluate_all,
    evaluate_antihtn_conflict,
    evaluate_fluid_nonresponsive,
    evaluate_lactate_clearance,
    evaluate_refractory_shock,
    evaluate_shock_index,
    evaluate_stability_crt_noradrenaline,
    evaluate_stability_dobutamine_high_norad,
    evaluate_stability_high_norad_without_adjuncts,
    evaluate_stability_lactate_sepsis,
    evaluate_stability_refractory_triple,
    evaluate_stability_vaso_negative_balance,
    evaluate_vaso_escalation,
    should_auto_resolve,
)

# ===========================================================================
# ALERT-HEMO-SHOCK-INDEX-01 — 5 test vectors
# ===========================================================================


class TestShockIndex:
    """TV-1 through TV-5 from hemodynamics.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — SI=1.2 (>0.9) with lactate 3.1 (>2) → fire
    # ------------------------------------------------------------------
    def test_tv1_si_elevated_with_lactate_corroborator(self):
        """TV-1: SI=1.2 (>0.9) sustained with lactate>2 — fire."""
        inputs = {
            "frequencia_cardiaca": 120,
            "pressao_arterial_sistolica": 100,
            "indice_choque": 1.2,
            "lactato_arterial": 3.1,
        }
        result = evaluate_shock_index(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: fire — MSI=110/78=1.41 (>1.3) with TEC 4s (>3) → fire
    # ------------------------------------------------------------------
    def test_tv2_msi_elevated_with_tec_corroborator(self):
        """TV-2: MSI=110/78=1.41 (>1.3) with TEC 4s (>3) — MSI branch + TEC."""
        inputs = {
            "frequencia_cardiaca": 110,
            "pressao_arterial_media": 78,
            "lactato_arterial": 1.5,
            "tempo_enchimento_capilar": 4.0,
        }
        result = evaluate_shock_index(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-3: no-fire — SI elevated but NO perfusion corroborator
    # ------------------------------------------------------------------
    def test_tv3_si_elevated_no_corroborator(self):
        """TV-3: SI=1.2 but lactate<2 and TEC<3 — suppressed."""
        inputs = {
            "frequencia_cardiaca": 120,
            "pressao_arterial_sistolica": 100,
            "indice_choque": 1.2,
            "lactato_arterial": 1.4,
            "tempo_enchimento_capilar": 2.0,
        }
        result = evaluate_shock_index(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: boundary — SI exactly 0.90 NOT >0.9 (strict) → no-fire
    # ------------------------------------------------------------------
    def test_tv4_boundary_si_exact_threshold(self):
        """TV-4: SI=0.90 is NOT >0.9 (strict) — no fire even with high lactate."""
        inputs = {
            "frequencia_cardiaca": 90,
            "pressao_arterial_sistolica": 100,
            "indice_choque": 0.9,
            "lactato_arterial": 3.0,
        }
        result = evaluate_shock_index(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: boundary — SI=0.91 (>0.9) with lactate 2.01 (>2) → fire
    # ------------------------------------------------------------------
    def test_tv5_boundary_si_just_above(self):
        """TV-5: SI=0.91 (>0.9) with lactate 2.01 (>2) both just above — fires."""
        inputs = {
            "frequencia_cardiaca": 91,
            "pressao_arterial_sistolica": 100,
            "indice_choque": 0.91,
            "lactato_arterial": 2.01,
        }
        result = evaluate_shock_index(inputs)
        assert result.fired is True


# ===========================================================================
# ALERT-HEMO-LACTATE-CLEARANCE-02 — 6 test vectors
# ===========================================================================


class TestLactateClearance:
    """TV-1 through TV-6 from hemodynamics.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — clearance 5% (<10%) at 2h during active resuscitation
    # ------------------------------------------------------------------
    def test_tv1_clearance_5_percent_2h(self):
        """TV-1: baseline 4.0, clearance 5% (<10%) with fluid bolus — fire."""
        inputs = {
            "lactato_inicial": 4.0,
            "lactato_2h": 3.8,
            "clearance_lactato_2h": 5.0,
            "fluid_bolus_given": True,
        }
        result = evaluate_lactate_clearance(inputs)
        assert result.fired is True
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL

    # ------------------------------------------------------------------
    # TV-2: fire — lactate 2.6 > 2 at 6h despite vasopressor → fire
    # ------------------------------------------------------------------
    def test_tv2_persistent_lactate_6h(self):
        """TV-2: lactate 2.6 > 2 at 6h with active vasopressor — persistence branch."""
        inputs = {
            "lactato_inicial": 3.0,
            "lactato_6h": 2.6,
            "dose_vasopressor": 0.2,
        }
        result = evaluate_lactate_clearance(inputs)
        assert result.fired is True
        assert result.band == "critical"

    # ------------------------------------------------------------------
    # TV-3: no-fire — adequate clearance (30%) and 6h lactate normal
    # ------------------------------------------------------------------
    def test_tv3_adequate_clearance(self):
        """TV-3: clearance 30% (>=10%) and 6h lactate <2 — adequate response."""
        inputs = {
            "lactato_inicial": 4.0,
            "lactato_2h": 2.8,
            "clearance_lactato_2h": 30.0,
            "lactato_6h": 1.8,
            "fluid_bolus_given": True,
        }
        result = evaluate_lactate_clearance(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: no-fire — poor clearance but NO active resuscitation
    # ------------------------------------------------------------------
    def test_tv4_poor_clearance_no_resuscitation(self):
        """TV-4: poor clearance but no active resuscitation — gate not met."""
        inputs = {
            "lactato_inicial": 4.0,
            "lactato_2h": 3.8,
            "clearance_lactato_2h": 5.0,
            "dose_vasopressor": 0,
            "fluid_bolus_given": False,
        }
        result = evaluate_lactate_clearance(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: boundary — clearance 10% NOT <10 AND lactate 2.0 NOT >2 → no-fire
    # ------------------------------------------------------------------
    def test_tv5_boundary_exact_thresholds(self):
        """TV-5: clearance=10.0 is NOT <10 (strict) AND lactate 2.0 is NOT >2 (strict)."""
        inputs = {
            "lactato_inicial": 2.0,
            "lactato_2h": 1.8,
            "clearance_lactato_2h": 10.0,
            "lactato_6h": 2.0,
            "fluid_bolus_given": True,
        }
        result = evaluate_lactate_clearance(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-6: boundary — baseline exactly 2.0 (>=2 inclusive) with clearance 9% → fires
    # ------------------------------------------------------------------
    def test_tv6_boundary_baseline_2_clearance_9(self):
        """TV-6: baseline exactly 2.0 (>=2 inclusive) with clearance 9% (<10) — fires."""
        inputs = {
            "lactato_inicial": 2.0,
            "lactato_2h": 1.82,
            "clearance_lactato_2h": 9.0,
            "fluid_bolus_given": True,
        }
        result = evaluate_lactate_clearance(inputs)
        assert result.fired is True
        assert result.band == "critical"


# ===========================================================================
# ALERT-HEMO-VASO-ESCALATION-03 — 6 test vectors
# ===========================================================================


class TestVasoEscalation:
    """TV-1 through TV-6 from hemodynamics.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — NE 0.20->0.35 = 75% increase (>50%) → fire
    # ------------------------------------------------------------------
    def test_tv1_dose_75_percent_increase(self):
        """TV-1: NE 0.20->0.35 = 75% increase (>50%) in 2h."""
        inputs = {
            "dose_vasopressor": 0.35,
            "dose_vasopressor_2h_atras": 0.20,
        }
        result = evaluate_vaso_escalation(inputs)
        assert result.fired is True
        assert result.band == "urgent"
        assert result.severity == SeverityLevel.URGENT

    # ------------------------------------------------------------------
    # TV-2: fire — vasopressin 0.03 U/min while NE active → 2nd agent
    # ------------------------------------------------------------------
    def test_tv2_vasopressin_second_agent(self):
        """TV-2: vasopressin 0.03 U/min newly added while NE active — 2nd-agent branch."""
        inputs = {
            "dose_vasopressor": 0.30,
            "dose_vasopressor_2h_atras": 0.28,
            "dose_vasopressina": 0.03,
        }
        result = evaluate_vaso_escalation(inputs)
        assert result.fired is True
        assert result.band == "urgent"

    # ------------------------------------------------------------------
    # TV-3: no-fire — NE 0.20->0.22 = 10% increase (<50%), no 2nd agent
    # ------------------------------------------------------------------
    def test_tv3_normal_titration_no_fire(self):
        """TV-3: 10% increase (<50%), no 2nd agent — normal titration."""
        inputs = {
            "dose_vasopressor": 0.22,
            "dose_vasopressor_2h_atras": 0.20,
        }
        result = evaluate_vaso_escalation(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: no-fire — dobutamine present but NO active norepinephrine
    # ------------------------------------------------------------------
    def test_tv4_dobutamine_only_no_ne(self):
        """TV-4: dobutamine but dose_vasopressor=0 — gate not met (inotrope-only)."""
        inputs = {
            "dose_vasopressor": 0,
            "dose_vasopressor_2h_atras": 0,
            "dose_dobutamina": 5.0,
        }
        result = evaluate_vaso_escalation(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: boundary — exactly 50% increase → no-fire (strict >)
    # ------------------------------------------------------------------
    def test_tv5_boundary_exact_50_percent(self):
        """TV-5: NE 0.30 = exactly 1.5x0.20 = exactly 50% — NOT >50% (strict) → no-fire."""
        inputs = {
            "dose_vasopressor": 0.30,
            "dose_vasopressor_2h_atras": 0.20,
        }
        result = evaluate_vaso_escalation(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-6: boundary — 0.301 just above 1.5x0.20 (>50%) → fires
    # ------------------------------------------------------------------
    def test_tv6_boundary_just_above_50_percent(self):
        """TV-6: 0.301 > 1.5*0.20 (>50%) — fires."""
        inputs = {
            "dose_vasopressor": 0.301,
            "dose_vasopressor_2h_atras": 0.20,
        }
        result = evaluate_vaso_escalation(inputs)
        assert result.fired is True


# ===========================================================================
# ALERT-HEMO-REFRACTORY-SHOCK-04 — 6 test vectors
# ===========================================================================


class TestRefractoryShock:
    """TV-1 through TV-6 from hemodynamics.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — MAP 58 (<65) on NE 1.4 (>1.0) → fire
    # ------------------------------------------------------------------
    def test_tv1_map58_ne14_adjuncts_absent(self):
        """TV-1: MAP 58 (<65) on NE 1.4 (>1.0); adjuncts absent → rescue recommended."""
        inputs = {
            "pressao_arterial_media": 58,
            "dose_vasopressor": 1.4,
            "dose_vasopressina": 0,
            "hidrocortisona_ativa": False,
        }
        result = evaluate_refractory_shock(inputs)
        assert result.fired is True
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL
        assert result.metadata["adjuncts_absent"] is True

    # ------------------------------------------------------------------
    # TV-2: no-fire — MAP <65 but NE 0.4 (<=1.0) → hypotensive but not maximal
    # ------------------------------------------------------------------
    def test_tv2_hypotensive_not_maximal_dose(self):
        """TV-2: MAP<65 but NE 0.4 (<=1.0) — hypotensive but not on maximal vasopressor."""
        inputs = {
            "pressao_arterial_media": 58,
            "dose_vasopressor": 0.4,
        }
        result = evaluate_refractory_shock(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-3: no-fire — MAP 72 (>=65) on high-dose NE → pressure target met
    # ------------------------------------------------------------------
    def test_tv3_pressure_target_met(self):
        """TV-3: MAP 72 (>=65) even with NE 1.5 — pressure target met, not refractory."""
        inputs = {
            "pressao_arterial_media": 72,
            "dose_vasopressor": 1.5,
        }
        result = evaluate_refractory_shock(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: boundary — MAP exactly 65 NOT <65 (strict) → no-fire
    # ------------------------------------------------------------------
    def test_tv4_boundary_map_exact_65(self):
        """TV-4: MAP=65 is NOT <65 (strict) — target met."""
        inputs = {
            "pressao_arterial_media": 65,
            "dose_vasopressor": 1.5,
        }
        result = evaluate_refractory_shock(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: boundary — dose exactly 1.0 NOT >1.0 (strict) → no-fire
    # ------------------------------------------------------------------
    def test_tv5_boundary_dose_exact_1(self):
        """TV-5: dose=1.0 is NOT >1.0 (strict); MAP<65 but not on maximal dose."""
        inputs = {
            "pressao_arterial_media": 64,
            "dose_vasopressor": 1.0,
        }
        result = evaluate_refractory_shock(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-6: boundary — MAP 64 (<65) with dose 1.01 (>1.0) → fires
    # ------------------------------------------------------------------
    def test_tv6_boundary_just_past_thresholds(self):
        """TV-6: MAP 64 (<65) with dose 1.01 (>1.0) both just past — fires."""
        inputs = {
            "pressao_arterial_media": 64,
            "dose_vasopressor": 1.01,
        }
        result = evaluate_refractory_shock(inputs)
        assert result.fired is True
        assert result.band == "critical"


# ===========================================================================
# ALERT-HEMO-FLUID-NONRESPONSIVE-05 — 5 test vectors
# ===========================================================================


class TestFluidNonresponsive:
    """TV-1 through TV-5 from hemodynamics.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — PPV 6% (<10) + SV change 4% (<10) + balance +3800 mL
    # ------------------------------------------------------------------
    def test_tv1_ppv_low_sv_poor_balance_positive(self):
        """TV-1: PPV 6% (<10) + SV change 4% (<10) + 24h balance +3800 (>3000) — fire."""
        inputs = {
            "ppv": 6,
            "delta_sv_pos_fluid": 4,
            "balanco_hidrico_24h": 3800,
        }
        result = evaluate_fluid_nonresponsive(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: fire — fallback: fluid challenge, MAP change 3 (<5), lact change 2% (<5)
    # ------------------------------------------------------------------
    def test_tv2_fallback_fluid_challenge(self):
        """TV-2: fluid challenge with MAP change 3 (<5) and lact change 2% (<5), balance +3500."""
        inputs = {
            "fluid_challenge_realizado": True,
            "delta_map_pos_fluid": 3,
            "delta_lactato_pos_fluid": 2,
            "balanco_hidrico_24h": 3500,
        }
        result = evaluate_fluid_nonresponsive(inputs)
        assert result.fired is True
        assert result.band == "watch"

    # ------------------------------------------------------------------
    # TV-3: no-fire — PPV 15% (>=10) and SV rose 18% (>=10) → fluid-responsive
    # ------------------------------------------------------------------
    def test_tv3_fluid_responsive_no_fire(self):
        """TV-3: PPV 15% (>=10) and SV rose 18% (>=10) — fluid-responsive, no alert."""
        inputs = {
            "ppv": 15,
            "delta_sv_pos_fluid": 18,
            "balanco_hidrico_24h": 3800,
        }
        result = evaluate_fluid_nonresponsive(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: no-fire — non-responsive but balance only +1500 (<=3000)
    # ------------------------------------------------------------------
    def test_tv4_nonresponsive_low_balance(self):
        """TV-4: non-responsive but 24h balance only +1500 (<=3000) — not overloaded."""
        inputs = {
            "ppv": 6,
            "delta_sv_pos_fluid": 4,
            "balanco_hidrico_24h": 1500,
        }
        result = evaluate_fluid_nonresponsive(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: boundary — PPV=10 NOT <10 AND balance=3000 NOT >3000 → no-fire
    # ------------------------------------------------------------------
    def test_tv5_boundary_exact_thresholds(self):
        """TV-5: PPV=10 is NOT <10 (strict) AND balance=3000 is NOT >3000 (strict)."""
        inputs = {
            "ppv": 10,
            "delta_sv_pos_fluid": 9,
            "balanco_hidrico_24h": 3000,
        }
        result = evaluate_fluid_nonresponsive(inputs)
        assert result.fired is False


# ===========================================================================
# ALERT-HEMO-ANTIHTN-CONFLICT-06 — 6 test vectors
# ===========================================================================


class TestAntihtnConflict:
    """TV-1 through TV-6 from hemodynamics.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — branch A: antihypertensive active + vasopressor → fire
    # ------------------------------------------------------------------
    def test_tv1_antihtn_with_vasopressor(self):
        """TV-1: scheduled antihypertensive active + vasopressor 0.15 — deprescribe."""
        inputs = {
            "antihipertensivo_agendado_ativo": True,
            "dose_vasopressor": 0.15,
            "pressao_arterial_sistolica": 88,
        }
        result = evaluate_antihtn_conflict(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: fire — branch A: recurrent hypotension + active antihypertensive
    # ------------------------------------------------------------------
    def test_tv2_recurrent_hypotension_with_antihtn(self):
        """TV-2: SBP 82 (<90) AND DBP 55 (<60) with active antihypertensive."""
        inputs = {
            "antihipertensivo_agendado_ativo": True,
            "dose_vasopressor": 0,
            "pressao_arterial_sistolica": 82,
            "pressao_arterial_diastolica": 55,
        }
        result = evaluate_antihtn_conflict(inputs)
        assert result.fired is True

    # ------------------------------------------------------------------
    # TV-3: fire — branch B: uncontrolled HTN off pressor, no permissive indication
    # ------------------------------------------------------------------
    def test_tv3_uncontrolled_htn_off_pressor(self):
        """TV-3: SBP 168 (>155) AND DBP 98 (>90) off vasopressor, no permissive HTN."""
        inputs = {
            "dose_vasopressor": 0,
            "antihipertensivo_agendado_ativo": False,
            "pressao_arterial_sistolica": 168,
            "pressao_arterial_diastolica": 98,
            "permissive_htn_indication": False,
        }
        result = evaluate_antihtn_conflict(inputs)
        assert result.fired is True

    # ------------------------------------------------------------------
    # TV-4: no-fire — uncontrolled HTN but permissive HTN window active
    # ------------------------------------------------------------------
    def test_tv4_permissive_htn_suppression(self):
        """TV-4: recurrent HTN but permissive-HTN indication — exclusion suppresses."""
        inputs = {
            "dose_vasopressor": 0,
            "antihipertensivo_agendado_ativo": False,
            "pressao_arterial_sistolica": 168,
            "pressao_arterial_diastolica": 98,
            "permissive_htn_indication": True,
        }
        result = evaluate_antihtn_conflict(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: no-fire — hypotensive on vasopressor but NO antihypertensive
    # ------------------------------------------------------------------
    def test_tv5_hypotensive_vasopressor_no_antihtn(self):
        """TV-5: hypotensive on vasopressor but no antihypertensive scheduled — nothing to deprescribe."""
        inputs = {
            "antihipertensivo_agendado_ativo": False,
            "dose_vasopressor": 0.15,
            "pressao_arterial_sistolica": 88,
        }
        result = evaluate_antihtn_conflict(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-6: boundary — SBP=90 NOT <90 AND DBP=60 NOT <60 → no-fire
    # ------------------------------------------------------------------
    def test_tv6_boundary_exact_thresholds(self):
        """TV-6: SBP=90 is NOT <90 (strict) AND DBP=60 is NOT <60 (strict) — no hypotension reading."""
        inputs = {
            "antihipertensivo_agendado_ativo": True,
            "dose_vasopressor": 0,
            "pressao_arterial_sistolica": 90,
            "pressao_arterial_diastolica": 60,
        }
        result = evaluate_antihtn_conflict(inputs)
        assert result.fired is False


# ===========================================================================
# Unified evaluate_all
# ===========================================================================


class TestEvaluateAll:
    """Integration: evaluate_all returns all 12 results (6 original + 6 WAVE 2B stability)."""

    def test_all_twelve_results_returned(self):
        """evaluate_all should return dict with 12 keys."""
        inputs = {
            "frequencia_cardiaca": 120,
            "pressao_arterial_sistolica": 100,
            "pressao_arterial_media": 58,
            "indice_choque": 1.2,
            "lactato_arterial": 3.1,
            "lactato_inicial": 4.0,
            "lactato_2h": 3.8,
            "clearance_lactato_2h": 5.0,
            "fluid_bolus_given": True,
            "dose_vasopressor": 1.4,
            "dose_vasopressor_2h_atras": 0.20,
            "ppv": 6,
            "delta_sv_pos_fluid": 4,
            "balanco_hidrico_24h": 3800,
            "antihipertensivo_agendado_ativo": True,
            "dose_vasopressina": 0,
            "hidrocortisona_ativa": False,
        }
        results = evaluate_all(inputs)
        expected_ids = {
            "ALERT-HEMO-SHOCK-INDEX-01",
            "ALERT-HEMO-LACTATE-CLEARANCE-02",
            "ALERT-HEMO-VASO-ESCALATION-03",
            "ALERT-HEMO-REFRACTORY-SHOCK-04",
            "ALERT-HEMO-FLUID-NONRESPONSIVE-05",
            "ALERT-HEMO-ANTIHTN-CONFLICT-06",
            "ALERT-HEMO-STABILITY-VASO-BALANCE-07",
            "ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08",
            "ALERT-HEMO-STABILITY-HIGH-NORAD-09",
            "ALERT-HEMO-STABILITY-REFRACTORY-10",
            "ALERT-HEMO-STABILITY-DOBUTAMINE-11",
            "ALERT-HEMO-STABILITY-CRT-NORAD-12",
        }
        assert set(results.keys()) == expected_ids
        # Verify some expected results
        assert results["ALERT-HEMO-SHOCK-INDEX-01"].fired is True
        assert results["ALERT-HEMO-REFRACTORY-SHOCK-04"].fired is True
        assert results["ALERT-HEMO-VASO-ESCALATION-03"].fired is True

    def test_all_no_fire_normal(self):
        """Normal inputs → all no-fire."""
        inputs = {
            "frequencia_cardiaca": 70,
            "pressao_arterial_sistolica": 120,
            "pressao_arterial_media": 85,
            "lactato_arterial": 1.0,
            "lactato_inicial": 1.0,
            "dose_vasopressor": 0,
            "balanco_hidrico_24h": 500,
            "antihipertensivo_agendado_ativo": False,
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
        """CRIT alert should never auto-resolve even with fresh/stale data."""
        result = HemoAlertResult(
            alert_id="ALERT-HEMO-REFRACTORY-SHOCK-04",
            name="test",
            fired=True,
            severity=SeverityLevel.CRITICAL,
        )
        assert should_auto_resolve(result, {}, is_stale=False) is False
        assert should_auto_resolve(result, {}, is_stale=True) is False

    def test_watch_auto_resolves_on_stale(self):
        """Watch alert may auto-resolve on stale data."""
        result = HemoAlertResult(
            alert_id="ALERT-HEMO-SHOCK-INDEX-01",
            name="test",
            fired=True,
            severity=SeverityLevel.WATCH,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True
        assert should_auto_resolve(result, {}, is_stale=False) is False

    def test_urgent_auto_resolves_on_stale(self):
        """Urgent alert may auto-resolve on stale data."""
        result = HemoAlertResult(
            alert_id="ALERT-HEMO-VASO-ESCALATION-03",
            name="test",
            fired=True,
            severity=SeverityLevel.URGENT,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True


# ===========================================================================
# WAVE 3A: Stability (ESTABILIDADE) RATIFY alerts — 6 new evaluators
# ===========================================================================


class TestStabilityVasoBalance:
    """ALERT-HEMO-STABILITY-VASO-BALANCE-07: Vasopressor with negative balance."""

    def test_fire_negative_balance_no_bolus(self):
        """Noradrenaline started 6h + balance -2500 + no bolus -> fire."""
        inputs = {
            "noradrenalina_iniciada_ultimas_6h": True,
            "balanco_hidrico_cumulativo": -2500,
            "bolus_cristaloide_500ml_ultimas_4h": False,
        }
        result = evaluate_stability_vaso_negative_balance(inputs)
        assert result.fired is True
        assert result.band == "urgent"

    def test_no_fire_norad_not_started(self):
        """Noradrenaline not started -> no fire."""
        inputs = {
            "noradrenalina_iniciada_ultimas_6h": False,
            "balanco_hidrico_cumulativo": -3000,
            "bolus_cristaloide_500ml_ultimas_4h": False,
        }
        result = evaluate_stability_vaso_negative_balance(inputs)
        assert result.fired is False

    def test_no_fire_balance_not_negative_enough(self):
        """Balance -1500 (not below -2000) -> no fire."""
        inputs = {
            "noradrenalina_iniciada_ultimas_6h": True,
            "balanco_hidrico_cumulativo": -1500,
            "bolus_cristaloide_500ml_ultimas_4h": False,
        }
        result = evaluate_stability_vaso_negative_balance(inputs)
        assert result.fired is False

    def test_no_fire_bolus_given(self):
        """Bolus already given -> suppressed."""
        inputs = {
            "noradrenalina_iniciada_ultimas_6h": True,
            "balanco_hidrico_cumulativo": -3000,
            "bolus_cristaloide_500ml_ultimas_4h": True,
        }
        result = evaluate_stability_vaso_negative_balance(inputs)
        assert result.fired is False


class TestStabilityLactateSepsis:
    """ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08: Lactate + sepsis therapy."""

    def test_fire_lactate_high_atb_no_norad_no_vm(self):
        """Lactate 3 + ATB + no norad + no VM -> fire (early shock)."""
        inputs = {
            "lactato_arterial": 3.0,
            "antibiotico_prescrito_24h": True,
            "noradrenalina_presente_4h": False,
            "ventilacao_mecanica_24h": False,
        }
        result = evaluate_stability_lactate_sepsis(inputs)
        assert result.fired is True
        assert result.band == "watch"

    def test_no_fire_norad_present(self):
        """Noradrenaline present -> suppressed (not early shock)."""
        inputs = {
            "lactato_arterial": 3.0,
            "antibiotico_prescrito_24h": True,
            "noradrenalina_presente_4h": True,
            "ventilacao_mecanica_24h": False,
        }
        result = evaluate_stability_lactate_sepsis(inputs)
        assert result.fired is False

    def test_no_fire_lactate_below_threshold(self):
        """Lactate 1.5 -> no fire."""
        inputs = {
            "lactato_arterial": 1.5,
            "antibiotico_prescrito_24h": True,
            "noradrenalina_presente_4h": False,
            "ventilacao_mecanica_24h": False,
        }
        result = evaluate_stability_lactate_sepsis(inputs)
        assert result.fired is False


class TestStabilityHighNorad:
    """ALERT-HEMO-STABILITY-HIGH-NORAD-09: High-dose norad without adjuncts."""

    def test_fire_high_norad_no_adjuncts(self):
        """NE 0.6 + no vasopressin + no hydrocortisone -> fire CRITICAL."""
        inputs = {
            "dose_noradrenalina": 0.6,
            "dose_vasopressina": 0,
            "hidrocortisona_prescrita": False,
        }
        result = evaluate_stability_high_norad_without_adjuncts(inputs)
        assert result.fired is True
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL

    def test_no_fire_both_adjuncts_present(self):
        """Both vasopressin and hydrocortisone present -> no fire."""
        inputs = {
            "dose_noradrenalina": 0.8,
            "dose_vasopressina": 0.04,
            "hidrocortisona_prescrita": True,
        }
        result = evaluate_stability_high_norad_without_adjuncts(inputs)
        assert result.fired is False

    def test_no_fire_low_dose(self):
        """NE 0.3 (below 0.5) -> no fire."""
        inputs = {
            "dose_noradrenalina": 0.3,
            "dose_vasopressina": 0,
            "hidrocortisona_prescrita": False,
        }
        result = evaluate_stability_high_norad_without_adjuncts(inputs)
        assert result.fired is False


class TestStabilityRefractoryTriple:
    """ALERT-HEMO-STABILITY-REFRACTORY-10: Refractory shock triple therapy."""

    def test_fire_norad_vaso_no_adr(self):
        """NE 0.6 + vasopressin 0.04 + no epinephrine -> fire."""
        inputs = {
            "dose_noradrenalina": 0.6,
            "dose_vasopressina": 0.04,
            "dose_adrenalina": 0,
        }
        result = evaluate_stability_refractory_triple(inputs)
        assert result.fired is True

    def test_no_fire_epinephrine_present(self):
        """Epinephrine already running -> no fire."""
        inputs = {
            "dose_noradrenalina": 0.7,
            "dose_vasopressina": 0.04,
            "dose_adrenalina": 0.1,
        }
        result = evaluate_stability_refractory_triple(inputs)
        assert result.fired is False


class TestStabilityDobutamine:
    """ALERT-HEMO-STABILITY-DOBUTAMINE-11: Dobutamine with high norad."""

    def test_fire_with_tachycardia(self):
        """NE 0.6 + dobutamine 5 + FC 140 -> fire URGENT."""
        inputs = {
            "dose_noradrenalina": 0.6,
            "dose_dobutamina": 5,
            "frequencia_cardiaca": 140,
        }
        result = evaluate_stability_dobutamine_high_norad(inputs)
        assert result.fired is True
        assert result.band == "urgent"

    def test_fire_without_tachycardia(self):
        """NE 0.6 + dobutamine 5 + FC 100 -> fire WATCH only."""
        inputs = {
            "dose_noradrenalina": 0.6,
            "dose_dobutamina": 5,
            "frequencia_cardiaca": 100,
        }
        result = evaluate_stability_dobutamine_high_norad(inputs)
        assert result.fired is True
        assert result.band == "watch"

    def test_no_fire_no_dobutamine(self):
        """NE only, no dobutamine -> no fire."""
        inputs = {
            "dose_noradrenalina": 0.8,
            "dose_dobutamina": 0,
        }
        result = evaluate_stability_dobutamine_high_norad(inputs)
        assert result.fired is False


class TestStabilityCrtNorad:
    """ALERT-HEMO-STABILITY-CRT-NORAD-12: CRT > 3s on noradrenaline."""

    def test_fire_crt_4_norad_active(self):
        """CRT 4s + active noradrenaline -> fire."""
        inputs = {
            "tempo_enchimento_capilar": 4,
            "noradrenalina_ativa": True,
        }
        result = evaluate_stability_crt_noradrenaline(inputs)
        assert result.fired is True
        assert result.band == "watch"

    def test_no_fire_crt_3_boundary(self):
        """CRT exactly 3 (NOT > 3) -> no fire (ANDROMEDA-SHOCK strict)."""
        inputs = {
            "tempo_enchimento_capilar": 3.0,
            "noradrenalina_ativa": True,
        }
        result = evaluate_stability_crt_noradrenaline(inputs)
        assert result.fired is False

    def test_no_fire_no_norad(self):
        """CRT high but no noradrenaline -> no fire."""
        inputs = {
            "tempo_enchimento_capilar": 5,
            "noradrenalina_ativa": False,
            "dose_noradrenalina": 0,
        }
        result = evaluate_stability_crt_noradrenaline(inputs)
        assert result.fired is False


# ===========================================================================
# Alert definitions seeding
# ===========================================================================


class TestHemoAlertDefinitions:
    """Verify HEMO_ALERT_DEFINITIONS are well-formed."""

    def test_six_definitions(self):
        """Should have 6 alert definitions."""
        assert len(HEMO_ALERT_DEFINITIONS) == 6

    def test_all_have_definition_version(self):
        """Each definition must have a definition_version starting with alert ID."""
        expected_prefixes = [
            "ALERT-HEMO-SHOCK-INDEX-01",
            "ALERT-HEMO-LACTATE-CLEARANCE-02",
            "ALERT-HEMO-VASO-ESCALATION-03",
            "ALERT-HEMO-REFRACTORY-SHOCK-04",
            "ALERT-HEMO-FLUID-NONRESPONSIVE-05",
            "ALERT-HEMO-ANTIHTN-CONFLICT-06",
        ]
        for d, expected in zip(HEMO_ALERT_DEFINITIONS, expected_prefixes, strict=False):
            assert d["definition_version"].startswith(expected)
            assert d["semver"] == "1.0.0"
            assert len(d["spec_hash"]) == 16
            assert d["description"]


# ===========================================================================
# Evaluate all (12 alerts)
# ===========================================================================


class TestEvaluateAll12:
    """Verify evaluate_all returns all 12 alert results."""

    def test_returns_12_alerts(self):
        """evaluate_all should return 12 alert results."""
        results = evaluate_all({"dose_noradrenalina": 0.0})
        assert len(results) == 12

    def test_all_have_alert_ids(self):
        """All results should have non-empty alert_ids."""
        results = evaluate_all({})
        for alert_id, result in results.items():
            assert alert_id
            assert isinstance(result, HemoAlertResult)
