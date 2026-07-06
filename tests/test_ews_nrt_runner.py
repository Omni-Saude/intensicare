"""Testes para o EWS NRT Runner — computação de scores e avaliação de alertas.

Cobre as funções standalone (sem DB) de ews_nrt_runner.py.
"""

from __future__ import annotations

import pytest

from intensicare.services.ews_nrt_runner import (
    EWSScoreSnapshot,
    _get_red_params,
    evaluate_ews_deterioration_01,
    evaluate_ews_discharge_readiness_04,
    evaluate_ews_sofa_organ_dysfunction_03,
    evaluate_ews_trend_rising_02,
)


# ---------------------------------------------------------------------------
# _get_red_params
# ---------------------------------------------------------------------------


def test_get_red_params_no_reds():
    """Snapshot sem scores vermelhos deve retornar conjunto vazio."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    assert _get_red_params(snap) == set()


def test_get_red_params_respiratory_rate_red():
    """RR score 3 deve aparecer como red."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_rr_score = 3
    assert "respiratory_rate" in _get_red_params(snap)


def test_get_red_params_multiple_reds():
    """Múltiplos scores 3 devem todos aparecer."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_rr_score = 3
    snap.news2_sbp_score = 3
    reds = _get_red_params(snap)
    assert "respiratory_rate" in reds
    assert "systolic_bp" in reds
    assert "heart_rate" not in reds


# ---------------------------------------------------------------------------
# evaluate_ews_deterioration_01
# ---------------------------------------------------------------------------


def test_deterioration_01_news2_crossing_threshold():
    """NEWS2 cruzando >=7 deve disparar alerta."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_score = 8
    snap.news2_score_prev = 5
    fired, reason = evaluate_ews_deterioration_01(snap)
    assert fired
    assert "edge crossing" in reason


def test_deterioration_01_persistent_high_suppressed():
    """NEWS2 persistentemente alto NÃO deve re-disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_score = 8
    snap.news2_score_prev = 8
    snap.news2_red_params_prev = set()
    fired, _ = evaluate_ews_deterioration_01(snap)
    assert not fired


def test_deterioration_01_new_red_parameter():
    """Novo parâmetro vermelho deve disparar alerta."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_score = 4
    snap.news2_rr_score = 3  # red
    snap.news2_red_params_prev = set()  # nothing was red before
    fired, reason = evaluate_ews_deterioration_01(snap)
    assert fired
    assert "respiratory_rate" in reason


def test_deterioration_01_same_red_suppressed():
    """Parâmetro que já estava vermelho NÃO deve re-disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_score = 4
    snap.news2_rr_score = 3
    snap.news2_red_params_prev = {"respiratory_rate"}
    snap.news2_score_prev = 5  # below threshold
    fired, _ = evaluate_ews_deterioration_01(snap)
    assert not fired


# ---------------------------------------------------------------------------
# evaluate_ews_trend_rising_02
# ---------------------------------------------------------------------------


def test_trend_rising_02_news2_delta():
    """NEWS2 com delta >=3 deve disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_score = 7
    snap.news2_at_window_start = 3
    fired, reason = evaluate_ews_trend_rising_02(snap)
    assert fired
    assert "NEWS2 rising" in reason


def test_trend_rising_02_no_baseline():
    """Sem baseline de janela, não deve disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.news2_score = 7
    snap.news2_at_window_start = None
    snap.mews_at_window_start = None
    fired, _ = evaluate_ews_trend_rising_02(snap)
    assert not fired


def test_trend_rising_02_mews_delta():
    """MEWS com delta >=3 deve disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.mews_score = 6
    snap.mews_at_window_start = 2
    snap.news2_at_window_start = None
    fired, reason = evaluate_ews_trend_rising_02(snap)
    assert fired
    assert "MEWS rising" in reason


# ---------------------------------------------------------------------------
# evaluate_ews_sofa_organ_dysfunction_03
# ---------------------------------------------------------------------------


def test_sofa_organ_dysfunction_delta_2():
    """ΔSOFA >=2 deve disparar alerta."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.sofa_total = 5
    snap.sofa_total_baseline_24h = 3
    fired, reason = evaluate_ews_sofa_organ_dysfunction_03(snap)
    assert fired
    assert "Δ+2" in reason


def test_sofa_organ_dysfunction_no_baseline():
    """Sem baseline de 24h, não deve disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.sofa_total = 5
    snap.sofa_total_baseline_24h = None
    fired, _ = evaluate_ews_sofa_organ_dysfunction_03(snap)
    assert not fired


def test_sofa_organ_dysfunction_delta_below_2():
    """ΔSOFA <2 NÃO deve disparar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.sofa_total = 4
    snap.sofa_total_baseline_24h = 3
    fired, _ = evaluate_ews_sofa_organ_dysfunction_03(snap)
    assert not fired


# ---------------------------------------------------------------------------
# evaluate_ews_discharge_readiness_04
# ---------------------------------------------------------------------------


def test_discharge_readiness_all_criteria_met():
    """Todos os critérios OK → readiness confirmada."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.gcs = 15
    snap.vasopressor_dose = 0
    snap.map_value = 80
    snap.mechanical_ventilation = False
    snap.spo2 = 96
    snap.supplemental_o2 = False
    fired, reason = evaluate_ews_discharge_readiness_04(
        snap, has_active_deterioration=False,
    )
    assert fired
    assert "all stability criteria met" in reason


def test_discharge_readiness_gcs_too_low():
    """GCS <14 deve falhar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.gcs = 10
    snap.vasopressor_dose = 0
    snap.map_value = 80
    snap.mechanical_ventilation = False
    snap.spo2 = 96
    snap.supplemental_o2 = False
    fired, reason = evaluate_ews_discharge_readiness_04(
        snap, has_active_deterioration=False,
    )
    assert not fired
    assert "GCS" in reason


def test_discharge_readiness_active_deterioration():
    """Deterioração ativa deve bloquear readiness."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.gcs = 15
    snap.vasopressor_dose = 0
    snap.map_value = 80
    snap.mechanical_ventilation = False
    snap.spo2 = 96
    snap.supplemental_o2 = False
    fired, reason = evaluate_ews_discharge_readiness_04(
        snap, has_active_deterioration=True,
    )
    assert not fired
    assert "active deterioration" in reason


def test_discharge_readiness_ventilation_active():
    """Ventilação mecânica ativa deve falhar."""
    snap = EWSScoreSnapshot(mpi_id="P-001", vital_sign_id=1)
    snap.gcs = 15
    snap.vasopressor_dose = 0
    snap.map_value = 80
    snap.mechanical_ventilation = True
    snap.spo2 = 96
    snap.supplemental_o2 = False
    fired, reason = evaluate_ews_discharge_readiness_04(
        snap, has_active_deterioration=False,
    )
    assert not fired
    assert "mechanical ventilation" in reason
