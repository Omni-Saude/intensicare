"""
Tests for Respiratory domain (WO-029) — 5 alerts, 24 test vectors.

Covers:
- ALERT-RESP-ARDS-STAGING-01: Berlin ARDS staging (6 vectors)
- ALERT-RESP-DETERIORATION-02: Ventilatory deterioration (4 vectors)
- ALERT-RESP-ASYNCHRONY-03: Patient-ventilator asynchrony (4 vectors)
- ALERT-RESP-WEANING-READY-04: Weaning readiness (5 vectors)
- ALERT-RESP-PROLONGED-INTUB-05: Prolonged intubation (5 vectors)

Total: 24 vectors, exactly matching respiratory.yaml.
FiO2 FRACTION enforced at every computation boundary (CANON_PINS).
"""

from __future__ import annotations

import pytest

from intensicare.schemas.severity import SeverityLevel
from intensicare.services.domain_respiratory import (
    RespiratoryAlertResult,
    RESPIRATORY_ALERT_DEFINITIONS,
    _ensure_fio2_fraction,
    _compute_sf_ratio,
    _compute_pf_ratio,
    evaluate_all,
    evaluate_ards_staging,
    evaluate_deterioration,
    evaluate_asynchrony,
    evaluate_weaning_ready,
    evaluate_prolonged_intubation,
    # WAVE 3A ventilation RATIFY
    evaluate_high_pplat_tidal,
    evaluate_peep_fio2_moderate,
    evaluate_peep_fio2_severe,
    evaluate_prolonged_covid_intubation,
    evaluate_extubation_readiness_bundle,
    evaluate_pain_assessment,
    should_auto_resolve,
)


# ===========================================================================
# FiO2 fraction enforcement tests (CANON_PINS)
# ===========================================================================


class TestFio2Fraction:
    """FiO2 fraction enforcement (CANON_PINS from WO-009)."""

    def test_fraction_passthrough(self):
        """0.50 should pass through as 0.50."""
        assert _ensure_fio2_fraction(0.50) == 0.50

    def test_percentage_conversion(self):
        """60 should be converted to 0.60."""
        assert _ensure_fio2_fraction(60) == 0.60
        assert _ensure_fio2_fraction(100) == 1.0

    def test_none_returns_none(self):
        """None input → None."""
        assert _ensure_fio2_fraction(None) is None

    def test_out_of_range_returns_none(self):
        """Values over 100% (after conversion) → None."""
        # 200 would be 2.0 after /100, which is > 1.0
        assert _ensure_fio2_fraction(200) is None

    def test_negative_returns_none(self):
        """Negative values → None."""
        assert _ensure_fio2_fraction(-0.1) is None

    def test_sf_ratio_with_percentage_fio2(self):
        """S/F with FiO2=60 should treat it as 0.60."""
        sf = _compute_sf_ratio(90, 60)
        assert sf == pytest.approx(90 / 0.60)

    def test_pf_ratio_with_fraction_fio2(self):
        """P/F with FiO2=0.50."""
        pf = _compute_pf_ratio(75, 0.50)
        assert pf == pytest.approx(150.0)


# ===========================================================================
# ALERT-RESP-ARDS-STAGING-01 — 6 test vectors
# ===========================================================================


class TestArdsStaging:
    """TV-1 through TV-6 from respiratory.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — S/F = 90/0.60 = 150 → moderada (urgent)
    # ------------------------------------------------------------------
    def test_tv1_moderada_urgent(self):
        """TV-1: S/F = 90/0.60 = 150 → moderada (URGENT); gate satisfied."""
        inputs = {
            "saturacao_o2": 90,
            "fio2": 0.60,
            "peep": 8,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "moderada"
        assert result.band == "urgent"
        assert result.severity == SeverityLevel.URGENT

    # ------------------------------------------------------------------
    # TV-2: fire — S/F = 88/0.90 = 97.8 <= 148 → grave (critical)
    # ------------------------------------------------------------------
    def test_tv2_grave_critical(self):
        """TV-2: S/F = 88/0.90 = 97.8 <=148 → grave (CRITICAL)."""
        inputs = {
            "saturacao_o2": 88,
            "fio2": 0.90,
            "peep": 12,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "grave"
        assert result.band == "critical"
        assert result.severity == SeverityLevel.CRITICAL

    # ------------------------------------------------------------------
    # TV-3: boundary — S/F = 94.5/0.30 = 315 exactly → leve (fires)
    #         leve: S/F <= 315 AND > 235 → 315 is <=315 so fires
    # ------------------------------------------------------------------
    def test_tv3_boundary_sf_315_leve(self):
        """TV-3: S/F = 94.5/0.30 = 315 exactly; leve requires S/F<=315 AND >235 — fires leve."""
        inputs = {
            "saturacao_o2": 94.5,
            "fio2": 0.30,
            "peep": 5,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "leve"
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-4: no-fire — S/F=150 but no bilateral infiltrates → gate fails
    # ------------------------------------------------------------------
    def test_tv4_no_infiltrates_gate_fails(self):
        """TV-4: S/F=150 but no bilateral infiltrates → Berlin gate fails → suppressed."""
        inputs = {
            "saturacao_o2": 90,
            "fio2": 0.60,
            "peep": 8,
            "infiltrado_bilateral": False,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: no-fire — S/F = 97/0.21 = 462 > 315 → no ARDS band
    # ------------------------------------------------------------------
    def test_tv5_normal_no_ards(self):
        """TV-5: S/F = 97/0.21 = 462 > 315 → no ARDS band."""
        inputs = {
            "saturacao_o2": 97,
            "fio2": 0.21,
            "peep": 5,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-6: fire — ABG present: P/F = 75/0.50 = 150 → moderada; PF authoritative
    # ------------------------------------------------------------------
    def test_tv6_pf_authoritative_override(self):
        """TV-6: ABG present: P/F = 75/0.50 = 150 → moderada; PF overrides S/F=184."""
        inputs = {
            "saturacao_o2": 92,
            "fio2": 0.50,
            "pao2": 75,
            "peep": 10,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        # P/F = 75/0.50 = 150 → moderada (between 100 and 200)
        assert result.stage == "moderada"
        assert result.band == "urgent"


# ===========================================================================
# ALERT-RESP-DETERIORATION-02 — 4 test vectors
# ===========================================================================


class TestDeterioration:
    """TV-1 through TV-4 from respiratory.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — ΔS/F = -60 = -25% of 240 (<= -20%) → fire
    # ------------------------------------------------------------------
    def test_tv1_sf_drop_25_percent(self):
        """TV-1: ΔS/F = -60 = -25% of 240 (<= -20%) → fire."""
        inputs = {
            "relacao_spo2_fio2": 180,
            "relacao_spo2_fio2_6h_ago": 240,
        }
        result = evaluate_deterioration(inputs)
        assert result.fired is True
        assert result.band == "urgent"
        assert result.severity == SeverityLevel.URGENT

    # ------------------------------------------------------------------
    # TV-2: fire — FiO2 0.70 > 1.30*0.50=0.65 AND SpO2 not improved
    # ------------------------------------------------------------------
    def test_tv2_fio2_escalation_no_spo2_improvement(self):
        """TV-2: FiO2 0.70 > 1.30*0.50=0.65 AND SpO2 92 <= 94 — escalating O2 demand."""
        inputs = {
            "fio2": 0.70,
            "fio2_6h_ago": 0.50,
            "saturacao_o2": 92,
            "saturacao_o2_6h_ago": 94,
        }
        result = evaluate_deterioration(inputs)
        assert result.fired is True
        assert result.band == "urgent"

    # ------------------------------------------------------------------
    # TV-3: boundary — ΔS/F = -48 = exactly -20% of 240 → fires (<= -20%)
    # ------------------------------------------------------------------
    def test_tv3_boundary_exact_negative_20_percent(self):
        """TV-3: ΔS/F = -48 = -20% of 240; rule is <= -20% so -20% FIRES."""
        inputs = {
            "relacao_spo2_fio2": 192,
            "relacao_spo2_fio2_6h_ago": 240,
        }
        result = evaluate_deterioration(inputs)
        assert result.fired is True

    # ------------------------------------------------------------------
    # TV-4: no-fire — FiO2 up but SpO2 improved (97>93) → not deterioration
    # ------------------------------------------------------------------
    def test_tv4_fio2_up_spo2_improved(self):
        """TV-4: FiO2 up but SpO2 improved (97>93) → not deterioration; also 0.60 < 0.65 threshold."""
        inputs = {
            "fio2": 0.60,
            "fio2_6h_ago": 0.50,
            "saturacao_o2": 97,
            "saturacao_o2_6h_ago": 93,
        }
        result = evaluate_deterioration(inputs)
        assert result.fired is False


# ===========================================================================
# ALERT-RESP-ASYNCHRONY-03 — 4 test vectors
# ===========================================================================


class TestAsynchrony:
    """TV-1 through TV-4 from respiratory.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — spont RR 32 > set 16 AND plateau 34 > 30 → fire
    # ------------------------------------------------------------------
    def test_tv1_asynchrony_fire(self):
        """TV-1: spont RR 32 > set 16 AND plateau 34 > 30 → fire."""
        inputs = {
            "frequencia_respiratoria": 32,
            "frequencia_respiratoria_programada": 16,
            "pressao_plato": 34,
        }
        result = evaluate_asynchrony(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: no-fire — RR high but plateau 26 <= 30 → no fire
    # ------------------------------------------------------------------
    def test_tv2_high_rr_low_plateau(self):
        """TV-2: RR high but plateau 26 <= 30 → no fire."""
        inputs = {
            "frequencia_respiratoria": 32,
            "frequencia_respiratoria_programada": 16,
            "pressao_plato": 26,
        }
        result = evaluate_asynchrony(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-3: boundary — spont RR 17 > set 16 (strict >) AND plateau 31 > 30 → fire
    # ------------------------------------------------------------------
    def test_tv3_boundary_rr_just_above_set(self):
        """TV-3: spont RR 17 > set 16 (strict >) AND plateau 31 > 30 → fire."""
        inputs = {
            "frequencia_respiratoria": 17,
            "frequencia_respiratoria_programada": 16,
            "pressao_plato": 31,
        }
        result = evaluate_asynchrony(inputs)
        assert result.fired is True

    # ------------------------------------------------------------------
    # TV-4: no-fire — plateau absent → insufficient data, no fire
    # ------------------------------------------------------------------
    def test_tv4_plateau_absent(self):
        """TV-4: plateau absent → insufficient data, no fire on RR alone."""
        inputs = {
            "frequencia_respiratoria": 32,
            "frequencia_respiratoria_programada": 16,
            "pressao_plato": None,
        }
        result = evaluate_asynchrony(inputs)
        assert result.fired is False


# ===========================================================================
# ALERT-RESP-WEANING-READY-04 — 5 test vectors
# ===========================================================================


class TestWeaningReady:
    """TV-1 through TV-5 from respiratory.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — all criteria met sustained 2h → ready
    # ------------------------------------------------------------------
    def test_tv1_all_criteria_met(self):
        """TV-1: all criteria met, sustained 2h → ready."""
        inputs = {
            "relacao_spo2_fio2": 350,
            "peep": 5,
            "fio2": 0.30,
            "indice_respiracao_rapida_superficial": 80,
            "rass": -1,
            "glasgow": 14,
            "dose_vasopressor": 0.0,
            "dias_em_ventilacao_mecanica": 3,
        }
        result = evaluate_weaning_ready(inputs)
        assert result.fired is True
        assert result.band == "normal"
        assert result.severity == SeverityLevel.NORMAL

    # ------------------------------------------------------------------
    # TV-2: no-fire — RSBI 120 >= 105 → not ready (rapid shallow breathing)
    # ------------------------------------------------------------------
    def test_tv2_rsbi_high(self):
        """TV-2: RSBI 120 >= 105 → not ready (rapid shallow breathing)."""
        inputs = {
            "relacao_spo2_fio2": 350,
            "peep": 5,
            "fio2": 0.30,
            "indice_respiracao_rapida_superficial": 120,
            "rass": -1,
            "glasgow": 14,
            "dose_vasopressor": 0.0,
            "dias_em_ventilacao_mecanica": 3,
        }
        result = evaluate_weaning_ready(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-3: boundary — every criterion at its exact boundary → fire
    # ------------------------------------------------------------------
    def test_tv3_boundary_all_exact_criteria(self):
        """TV-3: S/F 316 (>315), PEEP 8 (<=8), FiO2 0.40 (<=0.40),
        RSBI 104 (<105), RASS -2 (>= -2), GCS 10 (>=10),
        vasopressor 0.2 (<=0.2), days 1 (>=1) → fire."""
        inputs = {
            "relacao_spo2_fio2": 316,
            "peep": 8,
            "fio2": 0.40,
            "indice_respiracao_rapida_superficial": 104,
            "rass": -2,
            "glasgow": 10,
            "dose_vasopressor": 0.2,
            "dias_em_ventilacao_mecanica": 1,
        }
        result = evaluate_weaning_ready(inputs)
        assert result.fired is True

    # ------------------------------------------------------------------
    # TV-4: no-fire — RASS -4 (deep sedation) AND GCS 6 → not arousable
    # ------------------------------------------------------------------
    def test_tv4_deep_sedation_not_arousable(self):
        """TV-4: RASS -4 (< -2) deep sedation AND GCS 6 (<=8) → not arousable."""
        inputs = {
            "relacao_spo2_fio2": 350,
            "peep": 5,
            "fio2": 0.30,
            "indice_respiracao_rapida_superficial": 80,
            "rass": -4,
            "glasgow": 6,
            "dose_vasopressor": 0.0,
            "dias_em_ventilacao_mecanica": 3,
        }
        result = evaluate_weaning_ready(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: no-fire — vasopressor 0.5 > 0.2 → hemodynamically unfit
    # ------------------------------------------------------------------
    def test_tv5_high_vasopressor_not_ready(self):
        """TV-5: vasopressor 0.5 > 0.2 mcg/kg/min → hemodynamically unfit for weaning."""
        inputs = {
            "relacao_spo2_fio2": 350,
            "peep": 5,
            "fio2": 0.30,
            "indice_respiracao_rapida_superficial": 80,
            "rass": -1,
            "glasgow": 14,
            "dose_vasopressor": 0.5,
            "dias_em_ventilacao_mecanica": 3,
        }
        result = evaluate_weaning_ready(inputs)
        assert result.fired is False


# ===========================================================================
# ALERT-RESP-PROLONGED-INTUB-05 — 5 test vectors
# ===========================================================================


class TestProlongedIntubation:
    """TV-1 through TV-5 from respiratory.yaml."""

    # ------------------------------------------------------------------
    # TV-1: fire — TOT 12 days > 10 (non-COVID) → fire
    # ------------------------------------------------------------------
    def test_tv1_tot_12_days(self):
        """TV-1: TOT 12 days > 10 (non-COVID) → fire."""
        inputs = {
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 12,
            "covid19_ativo": False,
        }
        result = evaluate_prolonged_intubation(inputs)
        assert result.fired is True
        assert result.band == "watch"
        assert result.severity == SeverityLevel.WATCH

    # ------------------------------------------------------------------
    # TV-2: no-fire — already tracheostomized (TQT) → excluded
    # ------------------------------------------------------------------
    def test_tv2_already_tracheostomized(self):
        """TV-2: already tracheostomized (TQT) → excluded from intubation timer."""
        inputs = {
            "dispositivo_via_aerea": "TQT",
            "dias_em_ventilacao_mecanica": 20,
            "covid19_ativo": False,
        }
        result = evaluate_prolonged_intubation(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-3: boundary — exactly 10 days → no-fire (strict >)
    # ------------------------------------------------------------------
    def test_tv3_boundary_exact_10_days(self):
        """TV-3: exactly 10 days; rule is strict >10 so day 10 no-fire, day 11 fires."""
        inputs = {
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 10,
            "covid19_ativo": False,
        }
        result = evaluate_prolonged_intubation(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-4: no-fire — active COVID 12 days < 14 → deferred
    # ------------------------------------------------------------------
    def test_tv4_covid_12_days_deferred(self):
        """TV-4: active COVID uses >=14d threshold (RAT-VENTILACAO-05); 12 < 14 → deferred."""
        inputs = {
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 12,
            "covid19_ativo": True,
        }
        result = evaluate_prolonged_intubation(inputs)
        assert result.fired is False

    # ------------------------------------------------------------------
    # TV-5: fire — active COVID at 14 days (>=14) → fire
    # ------------------------------------------------------------------
    def test_tv5_covid_14_days_fires(self):
        """TV-5: active COVID at 14 days (>=14) → fire."""
        inputs = {
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 14,
            "covid19_ativo": True,
        }
        result = evaluate_prolonged_intubation(inputs)
        assert result.fired is True


# ===========================================================================
# Additional ARDS boundary tests
# ===========================================================================


class TestArdsBoundaries:
    """Additional boundary tests for ARDS staging."""

    def test_sf_316_no_ards(self):
        """S/F=316 > 315 — above leve threshold, should not fire."""
        inputs = {
            "saturacao_o2": 94.8,
            "fio2": 0.30,
            "peep": 5,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        # S/F = 94.8 / 0.30 = 316.0, should NOT fire
        result = evaluate_ards_staging(inputs)
        assert result.fired is False

    def test_pf_300_leve(self):
        """P/F = 300, PEEP 5 with ABG — should stage leve (<=300 AND >200)."""
        inputs = {
            "saturacao_o2": 92,
            "fio2": 0.30,
            "pao2": 90,
            "peep": 5,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        # P/F = 90/0.30 = 300 — leve (<=300 inclusive)
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "leve"

    def test_pf_100_grave(self):
        """P/F = 100 exactly → grave (<=100 inclusive)."""
        inputs = {
            "saturacao_o2": 88,
            "fio2": 0.50,
            "pao2": 50,
            "peep": 10,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        # P/F = 50/0.50 = 100 — grave (<=100 inclusive)
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "grave"
        assert result.severity == SeverityLevel.CRITICAL

    def test_sf_148_grave(self):
        """S/F = 148 exactly → grave (<=148 inclusive)."""
        inputs = {
            "saturacao_o2": 74,
            "fio2": 0.50,
            "peep": 10,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        # S/F = 74/0.50 = 148 — grave (<=148 inclusive)
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "grave"

    def test_gate_peep_lt_5(self):
        """PEEP < 5 → gate fails → no fire."""
        inputs = {
            "saturacao_o2": 90,
            "fio2": 0.60,
            "peep": 3,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is False

    def test_gate_edema_not_excluded(self):
        """Cardiogenic edema NOT excluded → gate fails."""
        inputs = {
            "saturacao_o2": 90,
            "fio2": 0.60,
            "peep": 8,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": False,
        }
        result = evaluate_ards_staging(inputs)
        assert result.fired is False

    def test_fio2_percentage_like_60(self):
        """FiO2=60 (percentage) treated as fraction 0.60."""
        inputs = {
            "saturacao_o2": 90,
            "fio2": 60,  # percentage
            "peep": 8,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
        }
        # S/F = 90/0.60 = 150 → moderada
        result = evaluate_ards_staging(inputs)
        assert result.fired is True
        assert result.stage == "moderada"


# ===========================================================================
# Unified evaluate_all
# ===========================================================================


class TestEvaluateAll:
    """Integration: evaluate_all returns all 11 results (5 original + 6 RATIFIED)."""

    def test_all_eleven_results_returned(self):
        """evaluate_all should return dict with 11 keys."""
        inputs = {
            "saturacao_o2": 90,
            "fio2": 0.60,
            "peep": 8,
            "infiltrado_bilateral": True,
            "edema_cardiogenico_excluido": True,
            "relacao_spo2_fio2": 180,
            "relacao_spo2_fio2_6h_ago": 240,
            "frequencia_respiratoria": 32,
            "frequencia_respiratoria_programada": 16,
            "pressao_plato": 34,
            "indice_respiracao_rapida_superficial": 80,
            "rass": -1,
            "glasgow": 14,
            "dose_vasopressor": 0.0,
            "dias_em_ventilacao_mecanica": 12,
            "dispositivo_via_aerea": "TOT",
            "covid19_ativo": False,
        }
        results = evaluate_all(inputs)
        expected_ids = {
            "ALERT-RESP-ARDS-STAGING-01",
            "ALERT-RESP-DETERIORATION-02",
            "ALERT-RESP-ASYNCHRONY-03",
            "ALERT-RESP-WEANING-READY-04",
            "ALERT-RESP-PROLONGED-INTUB-05",
            "ALERT-RESP-HIGH-PPLAT-06",
            "ALERT-RESP-PEEP-FIO2-MODERATE-07",
            "ALERT-RESP-PEEP-FIO2-SEVERE-08",
            "ALERT-RESP-PROLONGED-COVID-09",
            "ALERT-RESP-EXTUBATION-BUNDLE-10",
            "ALERT-RESP-PAIN-ASSESS-11",
        }
        assert set(results.keys()) == expected_ids
        assert results["ALERT-RESP-ARDS-STAGING-01"].fired is True
        assert results["ALERT-RESP-DETERIORATION-02"].fired is True
        assert results["ALERT-RESP-ASYNCHRONY-03"].fired is True

    def test_all_no_fire_normal(self):
        """Normal inputs → all no-fire."""
        inputs = {
            "saturacao_o2": 98,
            "fio2": 0.21,
            "peep": 5,
            "infiltrado_bilateral": False,
            "edema_cardiogenico_excluido": False,
            "relacao_spo2_fio2": 450,
            "relacao_spo2_fio2_6h_ago": 440,
            "frequencia_respiratoria": 14,
            "frequencia_respiratoria_programada": 14,
            "rass": 0,
            "glasgow": 15,
            "dose_vasopressor": 0.0,
            "dias_em_ventilacao_mecanica": 0,
            "dispositivo_via_aerea": "MNA",
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
        result = RespiratoryAlertResult(
            alert_id="ALERT-RESP-ARDS-STAGING-01",
            name="test",
            fired=True,
            severity=SeverityLevel.CRITICAL,
        )
        assert should_auto_resolve(result, {}, is_stale=False) is False
        assert should_auto_resolve(result, {}, is_stale=True) is False

    def test_watch_auto_resolves_on_stale(self):
        """Watch alert may auto-resolve on stale data."""
        result = RespiratoryAlertResult(
            alert_id="ALERT-RESP-ASYNCHRONY-03",
            name="test",
            fired=True,
            severity=SeverityLevel.WATCH,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True
        assert should_auto_resolve(result, {}, is_stale=False) is False

    def test_urgent_auto_resolves_on_stale(self):
        """Urgent alert may auto-resolve on stale data."""
        result = RespiratoryAlertResult(
            alert_id="ALERT-RESP-DETERIORATION-02",
            name="test",
            fired=True,
            severity=SeverityLevel.URGENT,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True

    def test_normal_auto_resolves_on_stale(self):
        """Normal alert may auto-resolve on stale data."""
        result = RespiratoryAlertResult(
            alert_id="ALERT-RESP-WEANING-READY-04",
            name="test",
            fired=True,
            severity=SeverityLevel.NORMAL,
        )
        assert should_auto_resolve(result, {}, is_stale=True) is True


# ===========================================================================
# WAVE 3A: Ventilation (VENTILACAO) RATIFY alerts — 5 new evaluators
# ===========================================================================


class TestHighPplatTidal:
    """ALERT-RESP-HIGH-PPLAT-06: High plateau pressure / tidal volume."""

    def test_fire_pplat_high(self):
        """Pplat 32 > 30 -> fire."""
        result = evaluate_high_pplat_tidal({"pressao_plato": 32})
        assert result.fired is True
        assert result.band == "watch"

    def test_no_fire_pplat_normal(self):
        """Pplat 28 -> no fire."""
        result = evaluate_high_pplat_tidal({"pressao_plato": 28})
        assert result.fired is False

    def test_fire_vc_high_pbw(self):
        """VC 500 + altura 160cm male -> PBW=56.9, VC/PBW=8.78 > 8 -> fire."""
        result = evaluate_high_pplat_tidal({
            "volume_corrente": 500,
            "altura_cm": 160,
            "sexo": "M",
        })
        assert result.fired is True

    def test_no_fire_vc_normal_pbw(self):
        """VC 400 + altura 170cm female -> PBW=61.5, VC/PBW=6.50 < 8 -> no fire."""
        result = evaluate_high_pplat_tidal({
            "volume_corrente": 400,
            "altura_cm": 170,
            "sexo": "F",
        })
        assert result.fired is False


class TestPeepFio2Moderate:
    """ALERT-RESP-PEEP-FIO2-MODERATE-07: Moderate FiO2xPEEP mismatch."""

    def test_fire_moderate_mismatch(self):
        """P/F 250 (moderate), FiO2 0.5, PEEP 5 (too low) -> fire."""
        result = evaluate_peep_fio2_moderate({
            "pao2": 125,  # 125/0.5 = 250
            "fio2": 0.50,
            "peep": 5,
        })
        assert result.fired is True
        assert result.band == "watch"

    def test_no_fire_adequate_peep(self):
        """P/F 250, FiO2 0.5, PEEP 8 (adequate) -> no fire."""
        result = evaluate_peep_fio2_moderate({
            "pao2": 125,
            "fio2": 0.50,
            "peep": 8,
        })
        assert result.fired is False


class TestPeepFio2Severe:
    """ALERT-RESP-PEEP-FIO2-SEVERE-08: Severe FiO2xPEEP mismatch."""

    def test_fire_severe_mismatch(self):
        """P/F 150 (severe), FiO2 0.7, PEEP 8 (too low) -> fire."""
        result = evaluate_peep_fio2_severe({
            "pao2": 105,  # 105/0.7 = 150
            "fio2": 0.70,
            "peep": 8,
        })
        assert result.fired is True
        assert result.band == "urgent"

    def test_no_fire_not_severe(self):
        """P/F 250 (not severe) -> no fire."""
        result = evaluate_peep_fio2_severe({
            "pao2": 100,
            "fio2": 0.40,
            "peep": 5,
        })
        assert result.fired is False


class TestProlongedCovidIntubation:
    """ALERT-RESP-PROLONGED-COVID-09: Prolonged COVID intubation."""

    def test_fire_covid_14_days(self):
        """COVID patient, TOT, 14 days -> fire."""
        result = evaluate_prolonged_covid_intubation({
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 14,
            "covid19_ativo": True,
        })
        assert result.fired is True

    def test_no_fire_covid_12_days(self):
        """COVID patient, TOT, 12 days (< 14) -> no fire."""
        result = evaluate_prolonged_covid_intubation({
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 12,
            "covid19_ativo": True,
        })
        assert result.fired is False

    def test_no_fire_non_covid(self):
        """Non-COVID patient -> this alert should not fire."""
        result = evaluate_prolonged_covid_intubation({
            "dispositivo_via_aerea": "TOT",
            "dias_em_ventilacao_mecanica": 15,
            "covid19_ativo": False,
        })
        assert result.fired is False


class TestExtubationBundle:
    """ALERT-RESP-EXTUBATION-BUNDLE-10: Extubation readiness bundle."""

    def test_fire_all_criteria_met(self):
        """All 5 criteria met -> fire (ready for SBT)."""
        result = evaluate_extubation_readiness_bundle({
            "fio2": 0.35,
            "peep": 5,
            "pao2": 90,  # 90/0.35 = 257 >= 150
            "glasgow": 14,
            "dose_vasopressor": 0,
        })
        assert result.fired is True
        assert result.band == "normal"

    def test_no_fire_fio2_too_high(self):
        """FiO2 0.50 > 0.40 -> no fire."""
        result = evaluate_extubation_readiness_bundle({
            "fio2": 0.50,
            "peep": 5,
            "pao2": 100,
            "glasgow": 14,
            "dose_vasopressor": 0,
        })
        assert result.fired is False

    def test_no_fire_pf_too_low(self):
        """P/F 120 < 150 -> no fire."""
        result = evaluate_extubation_readiness_bundle({
            "fio2": 0.30,
            "peep": 5,
            "pao2": 36,  # 36/0.30 = 120
            "glasgow": 14,
            "dose_vasopressor": 0,
        })
        assert result.fired is False


# ===========================================================================
# Evaluate all (10 alerts)
# ===========================================================================


class TestEvaluateAll10:
    """Verify evaluate_all returns all 10 alert results."""

    def test_returns_10_alerts(self):
        """evaluate_all should return 10 alert results (5 base + 5 WAVE 3A)."""
        results = evaluate_all({})
        assert len(results) >= 10


# ===========================================================================
# Alert definitions seeding
# ===========================================================================


class TestRespiratoryAlertDefinitions:
    """Verify RESPIRATORY_ALERT_DEFINITIONS are well-formed."""

    def test_definitions_count(self):
        """Should have 6 alert definitions (base 5 + pain assessment)."""
        assert len(RESPIRATORY_ALERT_DEFINITIONS) >= 6

    def test_all_have_definition_version(self):
        """Each definition must have a definition_version starting with alert ID."""
        expected_prefixes = [
            "ALERT-RESP-ARDS-STAGING-01",
            "ALERT-RESP-DETERIORATION-02",
            "ALERT-RESP-ASYNCHRONY-03",
            "ALERT-RESP-WEANING-READY-04",
            "ALERT-RESP-PROLONGED-INTUB-05",
        ]
        for d, expected in zip(RESPIRATORY_ALERT_DEFINITIONS, expected_prefixes):
            assert d["definition_version"].startswith(expected)
            assert d["semver"] == "3.0.0"
            assert len(d["spec_hash"]) == 16
            assert d["description"]
