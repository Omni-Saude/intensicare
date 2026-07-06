"""Tests for Sepsis domain service (WO-024) — 6 alerts, 31 test vectors.

Validates:
- All 31 vectors from docs/plan/_work/alerts/sepsis.yaml pass
- Hybrid mode: NRT qSOFA + micro-batch lab confirmation
- Explicit per-alert evaluation functions for clinical precision
- PPV budget tracking (>=0.60 fleet floor)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from intensicare.services.domain_sepsis import (
    SEPSIS_ALERT_IDS,
    SEPSIS_DEFINITION_VERSION,
    SepsisDomainService,
    SepsisEvaluationResult,
    evaluate_sepsis,
    evaluate_sepsis_nrt,
    evaluate_sepsis_micro_batch,
    _compute_sirs_count,
    _compute_qsofa_points,
    _infection_present,
    _eval_screen_01,
    _eval_organ_02,
    _eval_shock_03,
    _eval_bundle_overdue_04,
    _eval_pct_rising_05,
    _eval_pct_deesc_06,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def sepsis_service() -> SepsisDomainService:
    """Module-scoped service instance (definitions loaded once)."""
    return SepsisDomainService(_repo_root())


# ---------------------------------------------------------------------------
# Helper function unit tests
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    """Unit tests for helper/computation functions."""

    def test_sirs_count_all_four(self):
        """All 4 SIRS criteria met."""
        count = _compute_sirs_count({
            "temperatura": 38.6,
            "frequencia_cardiaca": 112,
            "frequencia_respiratoria": 24,
            "leucocitos": 15.2,
        })
        assert count == 4

    def test_sirs_count_two(self):
        """2 SIRS criteria: temp + HR."""
        count = _compute_sirs_count({
            "temperatura": 38.6,
            "frequencia_cardiaca": 112,
            "frequencia_respiratoria": 18,
            "leucocitos": 10.0,
        })
        assert count == 2

    def test_sirs_count_none(self):
        """No criteria met."""
        count = _compute_sirs_count({
            "temperatura": 37.0,
            "frequencia_cardiaca": 80,
            "frequencia_respiratoria": 16,
            "leucocitos": 10.0,
        })
        assert count == 0

    def test_sirs_boundary_exact(self):
        """Exact threshold values should NOT count."""
        count = _compute_sirs_count({
            "temperatura": 38.0,  # NOT > 38.0
            "frequencia_cardiaca": 90,  # NOT > 90
            "frequencia_respiratoria": 20,  # NOT > 20
            "leucocitos": 12.0,  # NOT > 12
        })
        assert count == 0

    def test_sirs_boundary_just_above(self):
        """Just above thresholds should count."""
        count = _compute_sirs_count({
            "temperatura": 38.1,
            "frequencia_cardiaca": 91,
        })
        assert count == 2

    def test_qsofa_from_vitals(self):
        """Compute qSOFA from raw vitals."""
        pts = _compute_qsofa_points({
            "frequencia_respiratoria": 24,  # >= 22 -> 1
            "pressao_arterial_sistolica": 96,  # <= 100 -> 1
            "glasgow": 14,  # < 15 -> 1
        })
        assert pts == 3

    def test_qsofa_explicit_score(self):
        """Pre-computed qSOFA score takes precedence."""
        pts = _compute_qsofa_points({"qsofa": 2})
        assert pts == 2

    def test_qsofa_none(self):
        """No data -> 0."""
        pts = _compute_qsofa_points({})
        assert pts == 0

    def test_infection_present_all_sources(self):
        """Infection from cultura/ATB/suspeita."""
        assert _infection_present({"cultura_positiva": True})
        assert _infection_present({"atb_iniciado_ultimas_24h": True})
        assert _infection_present({"suspeita_infeccao_documentada": True})
        assert not _infection_present({
            "cultura_positiva": False,
            "atb_iniciado_ultimas_24h": False,
            "suspeita_infeccao_documentada": False,
        })


# ---------------------------------------------------------------------------
# ALERT-SEPSIS-SCREEN-01 — 5 test vectors
# ---------------------------------------------------------------------------


class TestSepsisScreen01:
    """Screening layer: infection-gated SIRS/qSOFA."""

    def test_tv1_fire_qsofa_infection(self):
        """TV-1: qSOFA>=2 with documented infection suspicion."""
        fired, reason = _eval_screen_01({
            "qsofa": 2,
            "frequencia_respiratoria": 24,
            "pressao_arterial_sistolica": 96,
            "glasgow": 14,
            "suspeita_infeccao_documentada": True,
        })
        assert fired, f"TV-1 should fire: {reason}"

    def test_tv2_fire_sirs_atb(self):
        """TV-2: 3 SIRS criteria with antimicrobial started <24h."""
        fired, reason = _eval_screen_01({
            "temperatura": 38.6,
            "frequencia_cardiaca": 112,
            "leucocitos": 15.2,
            "qsofa": 0,
            "atb_iniciado_ultimas_24h": True,
        })
        assert fired, f"TV-2 should fire: {reason}"

    def test_tv3_no_fire_sirs_no_infection(self):
        """TV-3: 3 SIRS criteria but NO infection evidence."""
        fired, reason = _eval_screen_01({
            "temperatura": 38.6,
            "frequencia_cardiaca": 112,
            "leucocitos": 15.2,
            "qsofa": 0,
            "cultura_positiva": False,
            "atb_iniciado_ultimas_24h": False,
            "suspeita_infeccao_documentada": False,
        })
        assert not fired, f"TV-3 should NOT fire: {reason}"

    def test_tv4_boundary_exact_thresholds_no_fire(self):
        """TV-4: exact thresholds — no criterion met, no fire."""
        fired, reason = _eval_screen_01({
            "frequencia_cardiaca": 90,
            "temperatura": 37.4,
            "frequencia_respiratoria": 20,
            "leucocitos": 12.0,
            "suspeita_infeccao_documentada": True,
        })
        assert not fired, f"TV-4 should NOT fire: {reason}"

    def test_tv5_boundary_just_above_fires(self):
        """TV-5: boundary — HR=91 (>90) + temp=38.1 (>38.0) => sirs=2, fires."""
        fired, reason = _eval_screen_01({
            "frequencia_cardiaca": 91,
            "temperatura": 38.1,
            "frequencia_respiratoria": 20,
            "leucocitos": 12.0,
            "qsofa": 0,
            "cultura_positiva": True,
        })
        assert fired, f"TV-5 should fire: {reason}"


# ---------------------------------------------------------------------------
# ALERT-SEPSIS-ORGAN-02 — 6 test vectors
# ---------------------------------------------------------------------------


class TestSepsisOrgan02:
    """Organ dysfunction: qSOFA>=2 + lactate elevation/trend."""

    def test_tv1_fire_qsofa_lactate_high(self):
        """TV-1: qSOFA>=2 with lactate >2 mmol/L."""
        fired, reason = _eval_organ_02({"qsofa": 2, "lactato_arterial": 2.4})
        assert fired, f"TV-1 should fire: {reason}"

    def test_tv2_no_fire_lactate_below_trend_weak(self):
        """TV-2: qSOFA>=2 but lactate <2 and trend too weak (0.1/h < 0.5/h)."""
        fired, reason = _eval_organ_02({
            "qsofa": 2,
            "lactato_arterial": 1.8,
            "lactato_arterial_anterior": 1.2,
        })
        assert not fired, f"TV-2 should NOT fire: {reason}"

    def test_tv3_no_fire_qsofa_low(self):
        """TV-3: high lactate but qSOFA<2 — gate not met."""
        fired, reason = _eval_organ_02({"qsofa": 1, "lactato_arterial": 5.0})
        assert not fired, f"TV-3 should NOT fire: {reason}"

    def test_tv4_boundary_lactate_2_0_no_fire(self):
        """TV-4: boundary — lactate=2.0 is NOT >2 (strict)."""
        fired, reason = _eval_organ_02({"qsofa": 2, "lactato_arterial": 2.0})
        assert not fired, f"TV-4 should NOT fire: {reason}"

    def test_tv5_boundary_lactate_2_01_fires(self):
        """TV-5: boundary — lactate just above 2 fires."""
        fired, reason = _eval_organ_02({"qsofa": 2, "lactato_arterial": 2.01})
        assert fired, f"TV-5 should fire: {reason}"

    def test_tv6_fire_delta_lactato_trend(self):
        """TV-6: delta 0.9 mmol/L over 1h lookback = 0.9 mmol/L/h > 0.5/h.

        The test vector note specifies a 1h lookback between measurements.
        """
        fired, reason = _eval_organ_02({
            "qsofa": 2,
            "lactato_arterial": 1.9,
            "lactato_arterial_anterior": 1.0,
            "lactate_delta_hours": 1.0,  # per note: "1h lookback"
        })
        assert fired, f"TV-6 should fire: {reason}"


# ---------------------------------------------------------------------------
# ALERT-SEPSIS-SHOCK-03 — 5 test vectors
# ---------------------------------------------------------------------------


class TestSepsisShock03:
    """Septic shock: lactate >=4 or refractory MAP <65."""

    def test_tv1_fire_lactate_4_2(self):
        """TV-1: lactate >=4 mmol/L."""
        fired, reason = _eval_shock_03({"lactato_arterial": 4.2})
        assert fired, f"TV-1 should fire: {reason}"

    def test_tv2_fire_map_low_on_vasopressor(self):
        """TV-2: MAP<65 on active vasopressor."""
        fired, reason = _eval_shock_03({
            "pressao_arterial_media": 58,
            "dose_vasopressor": 0.2,
            "lactato_arterial": 3.1,
        })
        assert fired, f"TV-2 should fire: {reason}"

    def test_tv3_no_fire_map_low_no_vasopressor(self):
        """TV-3: MAP<65 but no fluid bolus and no vasopressor yet."""
        fired, reason = _eval_shock_03({
            "pressao_arterial_media": 58,
            "dose_vasopressor": 0,
            "fluid_bolus_given": False,
            "lactato_arterial": 2.5,
        })
        assert not fired, f"TV-3 should NOT fire: {reason}"

    def test_tv4_boundary_lactate_4_0_fires(self):
        """TV-4: boundary — lactate=4.0 is >=4 (inclusive) => fires."""
        fired, reason = _eval_shock_03({
            "lactato_arterial": 4.0,
            "pressao_arterial_media": 70,
        })
        assert fired, f"TV-4 should fire (inclusive >=): {reason}"

    def test_tv5_boundary_map_65_no_fire(self):
        """TV-5: boundary — MAP=65 is NOT <65 (strict)."""
        fired, reason = _eval_shock_03({
            "pressao_arterial_media": 65,
            "dose_vasopressor": 0.3,
            "lactato_arterial": 3.0,
        })
        assert not fired, f"TV-5 should NOT fire: {reason}"


# ---------------------------------------------------------------------------
# ALERT-SEPSIS-BUNDLE-OVERDUE-04 — 5 test vectors
# ---------------------------------------------------------------------------


class TestSepsisBundleOverdue04:
    """Hour-1 bundle compliance timer."""

    def test_tv1_fire_overdue_primeira_hora(self):
        """TV-1: primeira_hora item unchecked 75 min after accept."""
        fired, reason = _eval_bundle_overdue_04({
            "protocol_active": True,
            "item_checked": False,
            "item_pacote": "primeira_hora",
            "minutes_since_accept": 75,
        })
        assert fired, f"TV-1 should fire: {reason}"

    def test_tv2_no_fire_item_already_checked(self):
        """TV-2: item already checked — no overdue."""
        fired, reason = _eval_bundle_overdue_04({
            "protocol_active": True,
            "item_checked": True,
            "item_pacote": "primeira_hora",
            "minutes_since_accept": 75,
        })
        assert not fired, f"TV-2 should NOT fire: {reason}"

    def test_tv3_no_fire_reavaliacao_not_yet_due(self):
        """TV-3: reavaliacao item due at 180 min, only 120 elapsed."""
        fired, reason = _eval_bundle_overdue_04({
            "protocol_active": True,
            "item_checked": False,
            "item_pacote": "reavaliacao",
            "minutes_since_accept": 120,
        })
        assert not fired, f"TV-3 should NOT fire: {reason}"

    def test_tv4_boundary_exactly_60_min_no_fire(self):
        """TV-4: boundary — at exactly 60 min, not yet overdue (strict >)."""
        fired, reason = _eval_bundle_overdue_04({
            "protocol_active": True,
            "item_checked": False,
            "item_pacote": "primeira_hora",
            "minutes_since_accept": 60,
        })
        assert not fired, f"TV-4 should NOT fire: {reason}"

    def test_tv5_boundary_181_min_fires(self):
        """TV-5: boundary — reavaliacao 1 min past 180 deadline fires."""
        fired, reason = _eval_bundle_overdue_04({
            "protocol_active": True,
            "item_checked": False,
            "item_pacote": "reavaliacao",
            "minutes_since_accept": 181,
        })
        assert fired, f"TV-5 should fire: {reason}"


# ---------------------------------------------------------------------------
# ALERT-SEPSIS-PCT-RISING-05 — 5 test vectors
# ---------------------------------------------------------------------------


class TestSepsisPctRising05:
    """Procalcitonin rising — treatment failure trend."""

    def test_tv1_fire_pct_rising_atb_60h(self):
        """TV-1: PCT rising, delta > 0.25, ATB >=48h."""
        fired, reason = _eval_pct_rising_05({
            "procalcitonina": 1.2,
            "procalcitonina_anterior": 0.8,
            "atb_ativa_horas": 60,
        })
        assert fired, f"TV-1 should fire: {reason}"

    def test_tv2_no_fire_atb_too_early(self):
        """TV-2: rising but ATB only 24h (<48h) — too early."""
        fired, reason = _eval_pct_rising_05({
            "procalcitonina": 1.2,
            "procalcitonina_anterior": 0.8,
            "atb_ativa_horas": 24,
        })
        assert not fired, f"TV-2 should NOT fire: {reason}"

    def test_tv3_no_fire_pct_falling(self):
        """TV-3: PCT falling — responding to therapy."""
        fired, reason = _eval_pct_rising_05({
            "procalcitonina": 0.9,
            "procalcitonina_anterior": 1.5,
            "atb_ativa_horas": 72,
        })
        assert not fired, f"TV-3 should NOT fire: {reason}"

    def test_tv4_boundary_delta_0_25_no_fire(self):
        """TV-4: boundary — delta=0.25 is NOT >0.25 (strict)."""
        fired, reason = _eval_pct_rising_05({
            "procalcitonina": 1.05,
            "procalcitonina_anterior": 0.80,
            "atb_ativa_horas": 48,
        })
        assert not fired, f"TV-4 should NOT fire: {reason}"

    def test_tv5_boundary_delta_0_26_fires(self):
        """TV-5: boundary — delta 0.26 > 0.25, ATB exactly 48h fires."""
        fired, reason = _eval_pct_rising_05({
            "procalcitonina": 1.06,
            "procalcitonina_anterior": 0.80,
            "atb_ativa_horas": 48,
        })
        assert fired, f"TV-5 should fire: {reason}"


# ---------------------------------------------------------------------------
# ALERT-SEPSIS-PCT-DEESC-06 — 5 test vectors
# ---------------------------------------------------------------------------


class TestSepsisPctDeesc06:
    """Procalcitonin-guided de-escalation."""

    def test_tv1_fire_pct_low_stable(self):
        """TV-1: PCT <0.25 ng/mL, ATB >=48h, patient stable."""
        fired, reason = _eval_pct_deesc_06({
            "procalcitonina": 0.18,
            "atb_ativa_horas": 60,
            "patient_unstable": False,
        })
        assert fired, f"TV-1 should fire: {reason}"

    def test_tv2_fire_pct_drop_85_percent(self):
        """TV-2: >80% drop from peak (6.0->0.9), stable patient."""
        fired, reason = _eval_pct_deesc_06({
            "procalcitonina": 0.9,
            "pico_pct": 6.0,
            "atb_ativa_horas": 72,
            "patient_unstable": False,
        })
        assert fired, f"TV-2 should fire: {reason}"

    def test_tv3_no_fire_unstable_patient(self):
        """TV-3: PCT low but patient unstable — stability gate suppresses."""
        fired, reason = _eval_pct_deesc_06({
            "procalcitonina": 0.18,
            "atb_ativa_horas": 60,
            "patient_unstable": True,
        })
        assert not fired, f"TV-3 should NOT fire: {reason}"

    def test_tv4_boundary_pct_0_25_no_fire(self):
        """TV-4: boundary — PCT=0.25 is NOT <0.25 (strict)."""
        fired, reason = _eval_pct_deesc_06({
            "procalcitonina": 0.25,
            "atb_ativa_horas": 60,
            "patient_unstable": False,
        })
        assert not fired, f"TV-4 should NOT fire: {reason}"

    def test_tv5_boundary_pct_0_24_fires(self):
        """TV-5: boundary — PCT 0.24 <0.25, ATB >=48h, stable fires."""
        fired, reason = _eval_pct_deesc_06({
            "procalcitonina": 0.24,
            "atb_ativa_horas": 48,
            "patient_unstable": False,
        })
        assert fired, f"TV-5 should fire: {reason}"


# ---------------------------------------------------------------------------
# Hybrid mode tests
# ---------------------------------------------------------------------------


class TestHybridMode:
    """Hybrid mode: NRT screening fires → lab confirmation via micro-batch."""

    def test_hybrid_screening_fires_triggers_lab(self, sepsis_service):
        """NRT qSOFA screening fires, then micro-batch confirms organ dysfunction."""
        patient_id = "P-HYBRID-001"

        # Step 1: NRT screening — qSOFA high, infection present
        nrt_inputs = {
            "qsofa": 2,
            "frequencia_respiratoria": 24,
            "pressao_arterial_sistolica": 96,
            "glasgow": 14,
            "suspeita_infeccao_documentada": True,
        }
        nrt_result = sepsis_service.evaluate(patient_id, nrt_inputs, mode="nrt")
        screen_fired = any(
            r.alert_id == "ALERT-SEPSIS-SCREEN-01" and r.fired
            for r in nrt_result.alerts
        )
        assert screen_fired, "NRT screening should fire on qSOFA>=2 + infection"

        # Step 2: Micro-batch lab confirmation — add lactate > 2
        lab_inputs = {
            "qsofa": 2,
            "lactato_arterial": 2.4,
        }
        lab_result = sepsis_service.evaluate(patient_id, lab_inputs, mode="micro-batch")
        organ_fired = any(
            r.alert_id == "ALERT-SEPSIS-ORGAN-02" and r.fired
            for r in lab_result.alerts
        )
        assert organ_fired, "Micro-batch should confirm organ dysfunction with lactate >2"

    def test_hybrid_full_flow(self, sepsis_service):
        """Complete hybrid flow: screening → organ → shock."""
        patient_id = "P-HYBRID-002"
        all_inputs = {
            "qsofa": 2,
            "frequencia_respiratoria": 24,
            "pressao_arterial_sistolica": 96,
            "glasgow": 14,
            "suspeita_infeccao_documentada": True,
            "lactato_arterial": 4.2,
        }
        result = sepsis_service.evaluate(patient_id, all_inputs, mode="hybrid")
        fired_ids = {r.alert_id for r in result.alerts if r.fired}
        assert "ALERT-SEPSIS-SCREEN-01" in fired_ids, "Screen should fire"
        assert "ALERT-SEPSIS-ORGAN-02" in fired_ids, "Organ should fire"
        assert "ALERT-SEPSIS-SHOCK-03" in fired_ids, "Shock should fire"

    def test_hybrid_no_infection_no_cascade(self, sepsis_service):
        """Without infection evidence, screening should NOT fire, and cascade stops."""
        patient_id = "P-HYBRID-003"
        all_inputs = {
            "qsofa": 2,
            "frequencia_respiratoria": 24,
            "pressao_arterial_sistolica": 96,
            "glasgow": 14,
            "cultura_positiva": False,
            "atb_iniciado_ultimas_24h": False,
            "suspeita_infeccao_documentada": False,
            "lactato_arterial": 3.5,
        }
        result = sepsis_service.evaluate(patient_id, all_inputs, mode="hybrid")
        screen = next(r for r in result.alerts if r.alert_id == "ALERT-SEPSIS-SCREEN-01")
        assert not screen.fired, "Screen should NOT fire without infection"

    def test_hybrid_convenience_functions(self):
        """Convenience functions evaluate_sepsis, evaluate_sepsis_nrt, evaluate_sepsis_micro_batch."""
        # NRT convenience
        result = evaluate_sepsis_nrt("P-001", qsofa_score=0)
        assert result.alert_id == "ALERT-SEPSIS-SCREEN-01"

        result_fire = evaluate_sepsis_nrt(
            "P-002", qsofa_score=2,
            suspeita_infeccao_documentada=True,
        )
        assert result_fire.fired

        # Micro-batch convenience
        mb_result = evaluate_sepsis_micro_batch("P-003", {
            "qsofa": 2,
            "lactato_arterial": 2.4,
        })
        organ = next(
            r for r in mb_result.alerts
            if r.alert_id == "ALERT-SEPSIS-ORGAN-02"
        )
        assert organ.fired

        # Full convenience
        full_result = evaluate_sepsis("P-004", {
            "qsofa": 0,
            "procalcitonina": 0.18,
            "atb_ativa_horas": 60,
            "patient_unstable": False,
        })
        deesc = next(
            r for r in full_result.alerts
            if r.alert_id == "ALERT-SEPSIS-PCT-DEESC-06"
        )
        assert deesc.fired


# ---------------------------------------------------------------------------
# PPV budget tracking
# ---------------------------------------------------------------------------


class TestPpvBudget:
    """PPV budget verification: fleet floor >= 0.60."""

    def test_ppv_targets_all_above_fleet_floor(self, sepsis_service):
        """Every sepsis alert must have PPV target >= 0.60 except PCT-RISING-05."""
        allowed_below = {"ALERT-SEPSIS-PCT-RISING-05"}
        sepsis_service._ensure_loaded()
        for aid in SEPSIS_ALERT_IDS:
            ad = sepsis_service._definitions.get(aid)
            assert ad is not None, f"Missing definition: {aid}"
            target = ad.ppv_budget.get("target_ppv", 0)
            if aid in allowed_below:
                assert target >= 0.58, (
                    f"{aid}: PPV target {target} below documented floor 0.58"
                )
            else:
                assert target >= 0.60, (
                    f"{aid}: PPV target {target} below fleet floor 0.60"
                )

    def test_ppv_all_budgets_present(self, sepsis_service):
        """Every sepsis alert must have a ppv_budget block."""
        sepsis_service._ensure_loaded()
        for aid in SEPSIS_ALERT_IDS:
            ad = sepsis_service._definitions.get(aid)
            assert ad is not None, f"Missing definition: {aid}"
            budget = ad.ppv_budget
            assert budget, f"{aid}: missing ppv_budget"
            assert "target_ppv" in budget, f"{aid}: missing target_ppv"
            assert "est_volume_per_100_beds_day" in budget, (
                f"{aid}: missing est_volume_per_100_beds_day"
            )
            assert "rationale" in budget, f"{aid}: missing rationale"


# ---------------------------------------------------------------------------
# Service interface
# ---------------------------------------------------------------------------


class TestSepsisDomainService:
    """Domain service interface and convenience functions."""

    def test_all_6_alerts_loaded(self, sepsis_service):
        """All 6 sepsis alert definitions must be loaded."""
        sepsis_service._ensure_loaded()
        assert len(sepsis_service._definitions) >= 6
        for aid in SEPSIS_ALERT_IDS:
            assert aid in sepsis_service._definitions, (
                f"Missing definition: {aid}"
            )

    def test_screening_only(self, sepsis_service):
        """evaluate_screening_only returns SCREEN-01 result."""
        result = sepsis_service.evaluate_screening_only("P-001", {"qsofa": 0})
        assert result.alert_id == "ALERT-SEPSIS-SCREEN-01"
        assert not result.fired

        result2 = sepsis_service.evaluate_screening_only("P-002", {
            "qsofa": 2,
            "suspeita_infeccao_documentada": True,
        })
        assert result2.fired

    def test_organ_only(self, sepsis_service):
        """evaluate_organ_only returns ORGAN-02 result."""
        result = sepsis_service.evaluate_organ_only("P-001", {
            "qsofa": 2,
            "lactato_arterial": 2.4,
        })
        assert result.fired
        assert result.alert_id == "ALERT-SEPSIS-ORGAN-02"

    def test_shock_only(self, sepsis_service):
        """evaluate_shock_only returns SHOCK-03 result."""
        result = sepsis_service.evaluate_shock_only("P-001", {
            "lactato_arterial": 4.2,
        })
        assert result.fired
        assert result.alert_id == "ALERT-SEPSIS-SHOCK-03"

    def test_mode_nrt_only_evaluates_screen_and_shock(self, sepsis_service):
        """NRT mode only evaluates screening and shock alerts."""
        result = sepsis_service.evaluate("P-001", {
            "qsofa": 2,
            "suspeita_infeccao_documentada": True,
            "lactato_arterial": 4.5,
        }, mode="nrt")
        nrt_ids = {r.alert_id for r in result.alerts}
        assert "ALERT-SEPSIS-SCREEN-01" in nrt_ids
        assert "ALERT-SEPSIS-SHOCK-03" in nrt_ids
        assert "ALERT-SEPSIS-ORGAN-02" not in nrt_ids
        assert "ALERT-SEPSIS-BUNDLE-OVERDUE-04" not in nrt_ids

    def test_mode_micro_batch_excludes_nrt(self, sepsis_service):
        """Micro-batch mode excludes screening and shock."""
        result = sepsis_service.evaluate("P-001", {"qsofa": 2}, mode="micro-batch")
        mb_ids = {r.alert_id for r in result.alerts}
        assert "ALERT-SEPSIS-SCREEN-01" not in mb_ids
        assert "ALERT-SEPSIS-SHOCK-03" not in mb_ids

    def test_empty_inputs_no_fire(self, sepsis_service):
        """Empty inputs should not fire any alert."""
        result = sepsis_service.evaluate("P-001", {})
        assert result.n_fired == 0

    def test_missing_inputs_reported(self, sepsis_service):
        """Missing inputs should be reported in the result."""
        result = sepsis_service._evaluate_single("ALERT-SEPSIS-SCREEN-01", {})
        assert len(result.missing_inputs) > 0
        assert not result.fired


# ---------------------------------------------------------------------------
# Sepsis definition version (RAT-SEPSE-01/02 — CLINICALLY RATIFIED v3.0.0)
# ---------------------------------------------------------------------------


class TestSepsisDefinitionVersion:
    """Version tracking — all sepsis alerts CLINICALLY RATIFIED v3.0.0."""

    def test_definition_version_is_3_0_0(self):
        """Sepsis definition version must be '3.0.0' (RATIFIED)."""
        assert SEPSIS_DEFINITION_VERSION == "3.0.0", (
            f"Expected '3.0.0' RATIFIED version, got '{SEPSIS_DEFINITION_VERSION}'"
        )

    def test_definition_version_is_valid_semver(self):
        """Version must be valid semver."""
        parts = SEPSIS_DEFINITION_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)
        major = int(parts[0])
        assert major >= 3, "RATIFIED version must be >= 3.x.x"
