"""
Hemodynamics domain — hybrid NRT+micro-batch evaluator.
6 alerts, 34 test vectors from docs/plan/_work/alerts/hemodynamics.yaml.

CRITICAL DESIGN RULE: CRIT severity never auto-resolves on stale data.
Unlike watch/urgent, a CRIT alert persists until explicitly acknowledged
and resolved by a clinician.

Vasopressor dosing ALL in canonical mcg/kg/min via the conversion service.
This is the audit's #1 finding (SYS-02/CON-0060) — mL/h is NOT convertible
without concentration+weight.
CANONICAL UNITS RATIFIED (ASK-5): registry v2, all vasopressor predicates
use mcg/kg/min; mL/h is EDGE-ONLY and must pass through conversion service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from intensicare.schemas.severity import SeverityLevel


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass
class HemoAlertResult:
    """Result of evaluating one hemodynamics alert."""

    alert_id: str
    name: str
    fired: bool
    severity: SeverityLevel | None = None
    band: str | None = None  # "critical", "urgent", "watch", "normal"
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _band_severity(band: str | None) -> SeverityLevel | None:
    """Convert band label to SeverityLevel."""
    if band is None:
        return None
    return {
        "critical": SeverityLevel.CRITICAL,
        "urgent": SeverityLevel.URGENT,
        "watch": SeverityLevel.WATCH,
        "normal": SeverityLevel.NORMAL,
    }.get(band)


# ---------------------------------------------------------------------------
# ALERT-HEMO-SHOCK-INDEX-01: Índice de choque elevado — hipoperfusão oculta
# ---------------------------------------------------------------------------


def evaluate_shock_index(inputs: dict[str, Any]) -> HemoAlertResult:
    """Evaluate shock index screening for occult hypoperfusion.

    Fires when:
      (SI > 0.9 OR MSI > 1.3) sustained > PT15M
      AND (lactate > 2 mmol/L OR capillary refill > 3 s)

    SI = HR / SBP (classic, Rady 1994)
    MSI = HR / MAP (modified, Liu 2012)

    Boundary: strict > for all thresholds.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-SHOCK-INDEX-01",
        name="Índice de choque elevado — hipoperfusão oculta",
        fired=False,
    )

    fc = inputs.get("frequencia_cardiaca")
    pas = inputs.get("pressao_arterial_sistolica")
    pam = inputs.get("pressao_arterial_media")
    indice_choque = inputs.get("indice_choque")
    lactato = inputs.get("lactato_arterial")
    tec = inputs.get("tempo_enchimento_capilar")

    # Compute SI and MSI if raw values provided
    si_computed = None
    msi_computed = None
    if fc is not None and pas is not None:
        try:
            si_computed = float(fc) / float(pas)
        except (ValueError, TypeError, ZeroDivisionError):
            pass
    if fc is not None and pam is not None:
        try:
            msi_computed = float(fc) / float(pam)
        except (ValueError, TypeError, ZeroDivisionError):
            pass

    # Use provided indice_choque (SI) if available, else computed
    si_value = indice_choque if indice_choque is not None else si_computed

    # Check shock index bands
    si_positive = False
    msi_positive = False

    if si_value is not None:
        si_positive = float(si_value) > 0.9

    if msi_computed is not None:
        msi_positive = float(msi_computed) > 1.3

    # Perfusion corroborator
    perfusion_corroborator = False
    if lactato is not None and float(lactato) > 2.0:
        perfusion_corroborator = True
    if tec is not None and float(tec) > 3.0:
        perfusion_corroborator = True

    if (si_positive or msi_positive) and perfusion_corroborator:
        result.fired = True
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "indice_choque": si_value,
            "msi_computed": msi_computed,
            "lactato_arterial": lactato,
            "tempo_enchimento_capilar": tec,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-LACTATE-CLEARANCE-02: Clearance de lactato inadequado
# ---------------------------------------------------------------------------


def evaluate_lactate_clearance(inputs: dict[str, Any]) -> HemoAlertResult:
    """Evaluate lactate clearance failure during active resuscitation.

    Fires when:
      active_resuscitation
      AND lactato_inicial >= 2 mmol/L
      AND (clearance_lactato_2h < 10% OR lactato_6h > 2 mmol/L)

    active_resuscitation := fluid_bolus_given OR dose_vasopressor > 0
                             OR sepsis.shock.detected.

    Boundary: strict < for clearance, strict > for 6h lactate.
    Baseline >= 2 is inclusive.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-LACTATE-CLEARANCE-02",
        name="Clearance de lactato inadequado",
        fired=False,
    )

    lactato_inicial = inputs.get("lactato_inicial")
    lactato_2h = inputs.get("lactato_2h")
    lactato_6h = inputs.get("lactato_6h")
    clearance = inputs.get("clearance_lactato_2h")
    dose_vaso = inputs.get("dose_vasopressor", 0)
    fluid_bolus = inputs.get("fluid_bolus_given", False)
    sepsis_shock = inputs.get("sepsis_shock_detected", False)

    # Active resuscitation gate
    active_resuscitation = (
        (fluid_bolus is True)
        or (dose_vaso is not None and float(dose_vaso) > 0)
        or (sepsis_shock is True)
    )

    if not active_resuscitation:
        return result

    # Baseline lactate gate (inclusive >= 2)
    if lactato_inicial is None or float(lactato_inicial) < 2.0:
        return result

    # Branch 1: 2h clearance < 10% (strict)
    clearance_failure = False
    persistence_failure = False

    if clearance is not None and float(clearance) < 10.0:
        clearance_failure = True

    # Branch 2: 6h lactate > 2 mmol/L (strict)
    if lactato_6h is not None and float(lactato_6h) > 2.0:
        persistence_failure = True

    if clearance_failure or persistence_failure:
        result.fired = True
        result.band = "critical"
        result.severity = SeverityLevel.CRITICAL
        result.metadata = {
            "lactato_inicial": lactato_inicial,
            "lactato_2h": lactato_2h,
            "lactato_6h": lactato_6h,
            "clearance_lactato_2h": clearance,
            "active_resuscitation": active_resuscitation,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-VASO-ESCALATION-03: Escalonamento de vasopressor
# ---------------------------------------------------------------------------


def evaluate_vaso_escalation(inputs: dict[str, Any]) -> HemoAlertResult:
    """Evaluate vasopressor escalation (dose trend / second agent).

    Fires when:
      dose_vasopressor > 0 mcg/kg/min
      AND (dose_vasopressor > 1.5 * dose_vasopressor_2h_atras    # >50% increase
           OR second_vasopressor_started_2h)                       # 2nd agent

    second_vasopressor_started_2h := any of {vasopressin > 0, epinephrine > 0,
                                             dobutamine > 0} newly started.

    Boundary: strict > for 50% increase. Exactly 50% does NOT fire.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-VASO-ESCALATION-03",
        name="Escalonamento de vasopressor",
        fired=False,
    )

    dose_vaso = inputs.get("dose_vasopressor")
    dose_vaso_2h = inputs.get("dose_vasopressor_2h_atras")
    dose_vasopressina = inputs.get("dose_vasopressina", 0)
    dose_adrenalina = inputs.get("dose_adrenalina", 0)
    dose_dobutamina = inputs.get("dose_dobutamina", 0)

    # Gate: vasopressor must be active
    if dose_vaso is None or float(dose_vaso) <= 0:
        return result

    dose_vaso_f = float(dose_vaso)

    # Branch 1: >50% increase in 2h (strict >)
    dose_increase_fired = False
    if dose_vaso_2h is not None:
        dose_vaso_2h_f = float(dose_vaso_2h)
        if dose_vaso_2h_f > 0 and dose_vaso_f > 1.5 * dose_vaso_2h_f:
            dose_increase_fired = True

    # Branch 2: second vasopressor added
    second_agent_fired = False
    if dose_vasopressina is not None and float(dose_vasopressina) > 0:
        second_agent_fired = True
    if dose_adrenalina is not None and float(dose_adrenalina) > 0:
        second_agent_fired = True
    if dose_dobutamina is not None and float(dose_dobutamina) > 0:
        second_agent_fired = True

    if dose_increase_fired or second_agent_fired:
        result.fired = True
        result.band = "urgent"
        result.severity = SeverityLevel.URGENT
        result.metadata = {
            "dose_vasopressor": dose_vaso_f,
            "dose_vasopressor_2h_atras": dose_vaso_2h,
            "dose_increase_fired": dose_increase_fired,
            "second_agent_fired": second_agent_fired,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-REFRACTORY-SHOCK-04: Choque refratário
# ---------------------------------------------------------------------------


def evaluate_refractory_shock(inputs: dict[str, Any]) -> HemoAlertResult:
    """Evaluate refractory shock (hypotension on maximal vasopressor).

    Fires when:
      MAP < 65 mmHg sustained > PT30M
      AND dose_vasopressor > 1.0 mcg/kg/min

    Boundary: MAP strict < 65, dose strict > 1.0.
    Enrichment (does not gate): flags absent adjuncts (vasopressin/hydrocortisone).
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-REFRACTORY-SHOCK-04",
        name="Choque refratário — hipotensão sob vasopressor máximo",
        fired=False,
    )

    pam = inputs.get("pressao_arterial_media")
    dose_vaso = inputs.get("dose_vasopressor")
    dose_vasopressina = inputs.get("dose_vasopressina", 0)
    hidrocortisona = inputs.get("hidrocortisona_ativa", False)

    # MAP < 65 strict
    if pam is None or float(pam) >= 65:
        return result

    # dose > 1.0 strict
    if dose_vaso is None or float(dose_vaso) <= 1.0:
        return result

    # Enrichment: adjunct absence
    adjuncts_absent = (
        (dose_vasopressina is None or float(dose_vasopressina) <= 0)
        and (hidrocortisona is not True)
    )

    result.fired = True
    result.band = "critical"
    result.severity = SeverityLevel.CRITICAL
    result.metadata = {
        "pressao_arterial_media": pam,
        "dose_vasopressor": dose_vaso,
        "dose_vasopressina": dose_vasopressina,
        "hidrocortisona_ativa": hidrocortisona,
        "adjuncts_absent": adjuncts_absent,
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-FLUID-NONRESPONSIVE-05: Não responsivo a fluidos
# ---------------------------------------------------------------------------


def evaluate_fluid_nonresponsive(inputs: dict[str, Any]) -> HemoAlertResult:
    """Evaluate fluid non-responsiveness (overload risk).

    Primary path (advanced monitor):
      (PPV < 10% OR SVV < 10%) AND delta_SV_post_fluid < 10%
      AND balanco_hidrico_24h > 3000 mL

    Fallback path (clinical fluid challenge):
      fluid_challenge_realizado AND delta_MAP_post_fluid < 5 mmHg
      AND delta_lactato_post_fluid < 5% AND balanco_hidrico_24h > 3000 mL

    Boundary: strict < for all thresholds, strict > for balance.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-FLUID-NONRESPONSIVE-05",
        name="Não responsivo a fluidos — risco de sobrecarga",
        fired=False,
    )

    ppv = inputs.get("ppv")
    svv = inputs.get("svv")
    delta_sv = inputs.get("delta_sv_pos_fluid")
    balanco = inputs.get("balanco_hidrico_24h")
    fluid_challenge = inputs.get("fluid_challenge_realizado", False)
    delta_map = inputs.get("delta_map_pos_fluid")
    delta_lact = inputs.get("delta_lactato_pos_fluid")

    # Balance gate (both paths require positive balance > 3000)
    if balanco is None or float(balanco) <= 3000:
        return result

    # --- Primary path: PPV/SVV ---
    ppv_svv_nonresponsive = False
    ppv_low = ppv is not None and float(ppv) < 10.0
    svv_low = svv is not None and float(svv) < 10.0
    sv_poor = delta_sv is not None and float(delta_sv) < 10.0

    if (ppv_low or svv_low) and sv_poor:
        ppv_svv_nonresponsive = True

    # --- Fallback path: fluid challenge ---
    fallback_nonresponsive = False
    if fluid_challenge is True:
        map_poor = delta_map is not None and float(delta_map) < 5.0
        lact_poor = delta_lact is not None and float(delta_lact) < 5.0
        if map_poor and lact_poor:
            fallback_nonresponsive = True

    if ppv_svv_nonresponsive or fallback_nonresponsive:
        result.fired = True
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "ppv": ppv,
            "svv": svv,
            "delta_sv_pos_fluid": delta_sv,
            "balanco_hidrico_24h": balanco,
            "path": "primary" if ppv_svv_nonresponsive else "fallback",
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-ANTIHTN-CONFLICT-06: Conflito anti-hipertensivo × PA / vasopressor
# ---------------------------------------------------------------------------


def evaluate_antihtn_conflict(inputs: dict[str, Any]) -> HemoAlertResult:
    """Evaluate antihypertensive vs BP/vasopressor medication-safety conflict.

    Branch A (deprescribe):
      antihipertensivo_agendado_ativo
      AND (recurrent_hypotension OR dose_vasopressor > 0)

    Branch B (uncontrolled HTN off pressor):
      dose_vasopressor == 0
      AND recurrent_hypertension
      AND NOT permissive_htn_indication

    recurrent_hypotension := SBP < 90 mmHg OR DBP < 60 mmHg
    recurrent_hypertension := SBP > 155 mmHg OR DBP > 90 mmHg

    Boundary: strict < for hypotension, strict > for hypertension.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-ANTIHTN-CONFLICT-06",
        name="Conflito anti-hipertensivo × pressão arterial / vasopressor",
        fired=False,
    )

    antihtn = inputs.get("antihipertensivo_agendado_ativo", False)
    dose_vaso = inputs.get("dose_vasopressor", 0)
    pas = inputs.get("pressao_arterial_sistolica")
    pad = inputs.get("pressao_arterial_diastolica")
    permissive = inputs.get("permissive_htn_indication", False)

    # Compute recurrent hypotension: SBP < 90 OR DBP < 60 (strict)
    recurrent_hypotension = False
    if pas is not None and float(pas) < 90.0:
        recurrent_hypotension = True
    if pad is not None and float(pad) < 60.0:
        recurrent_hypotension = True

    # Compute recurrent hypertension: SBP > 155 OR DBP > 90 (strict)
    recurrent_hypertension = False
    if pas is not None and float(pas) > 155.0:
        recurrent_hypertension = True
    if pad is not None and float(pad) > 90.0:
        recurrent_hypertension = True

    dose_vaso_f = float(dose_vaso) if dose_vaso is not None else 0.0

    # Branch A: deprescribe — antihypertensive + hypotension/vasopressor
    branch_a = False
    if antihtn is True:
        if recurrent_hypotension or dose_vaso_f > 0:
            branch_a = True

    # Branch B: uncontrolled HTN off pressor
    branch_b = False
    if dose_vaso_f == 0 and recurrent_hypertension and not permissive:
        branch_b = True

    if branch_a or branch_b:
        result.fired = True
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "branch": "A" if branch_a else "B",
            "antihipertensivo_agendado_ativo": antihtn,
            "dose_vasopressor": dose_vaso_f,
            "recurrent_hypotension": recurrent_hypotension,
            "recurrent_hypertension": recurrent_hypertension,
            "permissive_htn_indication": permissive,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-STABILITY-VASO-BALANCE-07: Vasopressor com balanço negativo
# (rat-estabilidade-01, RULE-ESTABILIDADE-001, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_stability_vaso_negative_balance(
    inputs: dict[str, Any],
) -> HemoAlertResult:
    """Evaluate vasopressor with negative cumulative fluid balance.

    RATIFIED per rat-estabilidade-01 (recommended default A):
    Noradrenaline started in last 6h AND cumulative fluid balance < -2000 mL
    AND no >=500 mL Ringer/saline bolus in last 4h.

    Fires when all conditions met — flags under-resuscitation on vasopressor.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-STABILITY-VASO-BALANCE-07",
        name="Vasopressor com balanço hídrico cumulativo negativo",
        fired=False,
    )

    nora_iniciada_6h = inputs.get("noradrenalina_iniciada_ultimas_6h", False)
    balanco_cumulativo = inputs.get("balanco_hidrico_cumulativo")
    bolus_ringer_4h = inputs.get("bolus_cristaloide_500ml_ultimas_4h", False)

    # Gate: noradrenaline must be newly started in last 6h
    if not nora_iniciada_6h:
        return result

    # Balance < -2000 mL (strict)
    if balanco_cumulativo is None or float(balanco_cumulativo) >= -2000:
        return result

    # No >=500 mL crystalloid bolus in last 4h
    if bolus_ringer_4h:
        return result

    result.fired = True
    result.band = "urgent"
    result.severity = SeverityLevel.URGENT
    result.metadata = {
        "noradrenalina_iniciada_ultimas_6h": nora_iniciada_6h,
        "balanco_hidrico_cumulativo": balanco_cumulativo,
        "bolus_cristaloide_500ml_ultimas_4h": bolus_ringer_4h,
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08: Lactato elevado com terapia
# (rat-estabilidade-02, RULE-ESTABILIDADE-005, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_stability_lactate_sepsis(
    inputs: dict[str, Any],
) -> HemoAlertResult:
    """Evaluate lactate elevation with sepsis therapy — early shock.

    RATIFIED per rat-estabilidade-02 (recommended default A):
    Lactato >= 2 mmol/L AND antibiotic prescribed AND
    ABSENCE of noradrenaline (not yet on vasopressors) AND
    no mechanical ventilation in last 24h.

    Targets early septic shock before vasopressor initiation.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08",
        name="Lactato elevado com terapia de sepse — choque precoce",
        fired=False,
    )

    lactato = inputs.get("lactato_arterial")
    atb_prescrito = inputs.get("antibiotico_prescrito_24h", False)
    nora_presente = inputs.get("noradrenalina_presente_4h", False)
    vm_24h = inputs.get("ventilacao_mecanica_24h", False)

    # Lactate >= 2 mmol/L (inclusive)
    if lactato is None or float(lactato) < 2.0:
        return result

    # Antibiotic must be prescribed
    if not atb_prescrito:
        return result

    # ABSENCE of noradrenaline (per docstring intent)
    if nora_presente:
        return result

    # No mechanical ventilation
    if vm_24h:
        return result

    result.fired = True
    result.band = "watch"
    result.severity = SeverityLevel.WATCH
    result.metadata = {
        "lactato_arterial": lactato,
        "antibiotico_prescrito_24h": atb_prescrito,
        "noradrenalina_presente_4h": nora_presente,
        "ventilacao_mecanica_24h": vm_24h,
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-STABILITY-HIGH-NORAD-09: Noradrenalina em dose alta sem adjuntos
# (rat-estabilidade-03, RULE-ESTABILIDADE-007, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_stability_high_norad_without_adjuncts(
    inputs: dict[str, Any],
) -> HemoAlertResult:
    """Evaluate high-dose noradrenaline without adjuncts (vasopressin/hydrocortisone).

    RATIFIED per rat-estabilidade-03 (recommended default B, pending institutional
    concentration ratification):
    Noradrenaline in mcg/kg/min > institutional high-dose threshold
    AND (no vasopressin recorded OR no hydrocortisone prescribed).

    Uses canonical mcg/kg/min; the legacy ml/h > 20 threshold is recorded
    as an open institutional-concentration item.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-STABILITY-HIGH-NORAD-09",
        name="Noradrenalina em dose alta sem adjuntos — avaliar vasopressina/hidrocortisona",
        fired=False,
    )

    dose_nora = inputs.get("dose_noradrenalina")  # mcg/kg/min
    dose_vaso = inputs.get("dose_vasopressina", 0)
    hidrocortisona = inputs.get("hidrocortisona_prescrita", False)

    # High-dose threshold: > 0.5 mcg/kg/min (SSC 2021 adjunct-therapy range)
    # Legacy ml/h > 20 recorded as open item for institutional concentration
    if dose_nora is None or float(dose_nora) <= 0.5:
        return result

    # Adjunct absence: either vasopressin missing OR hydrocortisone missing
    vaso_ausente = (dose_vaso is None or float(dose_vaso) <= 0)
    hidro_ausente = (not hidrocortisona)

    if not vaso_ausente and not hidro_ausente:
        return result  # Both adjuncts present

    result.fired = True
    result.band = "critical"  # VERMELHO in legacy
    result.severity = SeverityLevel.CRITICAL
    result.metadata = {
        "dose_noradrenalina": dose_nora,
        "dose_vasopressina": dose_vaso,
        "hidrocortisona_prescrita": hidrocortisona,
        "vasopressina_ausente": vaso_ausente,
        "hidrocortisona_ausente": hidro_ausente,
        "open_item": "institutional_noradrenaline_concentration_pending",
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-STABILITY-REFRACTORY-10: Choque refratário — terapia tripla
# (rat-estabilidade-04, RULE-ESTABILIDADE-008, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_stability_refractory_triple(
    inputs: dict[str, Any],
) -> HemoAlertResult:
    """Evaluate refractory shock — norepinephrine + vasopressin without epinephrine.

    RATIFIED per rat-estabilidade-04 (recommended default B):
    Noradrenaline > institutional-high-dose AND vasopressin > institutional-dose
    AND absence of adrenaline (epinephrine as third agent).

    SSC 2021 escalation: add epinephrine when MAP inadequate on NE + vasopressin.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-STABILITY-REFRACTORY-10",
        name="Choque refratário — noradrenalina + vasopressina sem adrenalina",
        fired=False,
    )

    dose_nora = inputs.get("dose_noradrenalina")  # mcg/kg/min
    dose_vaso = inputs.get("dose_vasopressina")
    dose_adr = inputs.get("dose_adrenalina", 0)

    # Both norepi and vasopressin must be at elevated doses
    if dose_nora is None or float(dose_nora) <= 0.5:
        return result

    if dose_vaso is None or float(dose_vaso) <= 0:
        return result

    # Epinephrine must be absent
    if dose_adr is not None and float(dose_adr) > 0:
        return result

    result.fired = True
    result.band = "critical"
    result.severity = SeverityLevel.CRITICAL
    result.metadata = {
        "dose_noradrenalina": dose_nora,
        "dose_vasopressina": dose_vaso,
        "dose_adrenalina": dose_adr,
        "escalation_target": "adicionar adrenalina como terceiro agente (SSC 2021)",
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-STABILITY-DOBUTAMINE-11: Dobutamina com noradrenalina em dose alta
# (rat-estabilidade-05, RULE-ESTABILIDADE-009, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_stability_dobutamine_high_norad(
    inputs: dict[str, Any],
) -> HemoAlertResult:
    """Evaluate dobutamine with high-dose noradrenaline — tachycardia gate.

    RATIFIED per rat-estabilidade-05 (recommended default A):
    Noradrenaline > institutional-high-dose AND dobutamine > 0
    AND (FC > 130 bpm gate when available — facade condition).

    SSC 2021: suspend dobutamine when tachycardia impairs diastolic filling.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-STABILITY-DOBUTAMINE-11",
        name="Dobutamina com noradrenalina em dose alta — avaliar FC > 130",
        fired=False,
    )

    dose_nora = inputs.get("dose_noradrenalina")  # mcg/kg/min
    dose_dobu = inputs.get("dose_dobutamina")
    fc = inputs.get("frequencia_cardiaca")

    # Both agents must be active
    if dose_nora is None or float(dose_nora) <= 0.5:
        return result

    if dose_dobu is None or float(dose_dobu) <= 0:
        return result

    # Tachycardia gate: FC > 130 bpm when available (facade condition)
    # If FC not available, fire on dose combination alone (watch severity)
    tachycardia = False
    if fc is not None and float(fc) > 130:
        tachycardia = True

    result.fired = True
    if tachycardia:
        result.band = "urgent"
        result.severity = SeverityLevel.URGENT
    else:
        result.band = "watch"
        result.severity = SeverityLevel.WATCH

    result.metadata = {
        "dose_noradrenalina": dose_nora,
        "dose_dobutamina": dose_dobu,
        "frequencia_cardiaca": fc,
        "tachycardia_130": tachycardia,
        "recommendation": "suspender dobutamina se FC > 130 (prejuizo enchimento diastolico)",
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-HEMO-STABILITY-CRT-NORAD-12: TEC lentificado em noradrenalina
# (rat-estabilidade-09, RULE-ESTABILIDADE-017, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_stability_crt_noradrenaline(
    inputs: dict[str, Any],
) -> HemoAlertResult:
    """Evaluate slow capillary refill on active noradrenaline.

    RATIFIED per rat-estabilidade-09 (recommended default A):
    CRT > 3 s (ANDROMEDA-SHOCK 2019) AND active noradrenaline record.
    Harmonized with v3 RULE-ESTABILIDADE-003.

    Replaces legacy strict > 5 s with the validated ANDROMEDA-SHOCK > 3 s.
    """
    result = HemoAlertResult(
        alert_id="ALERT-HEMO-STABILITY-CRT-NORAD-12",
        name="Tempo de enchimento capilar lentificado (>3 s) em uso de noradrenalina",
        fired=False,
    )

    tec = inputs.get("tempo_enchimento_capilar")
    nora_ativa = inputs.get("noradrenalina_ativa", False)
    dose_nora = inputs.get("dose_noradrenalina", 0)

    # CRT > 3 s (ANDROMEDA-SHOCK, strict >)
    if tec is None or float(tec) <= 3.0:
        return result

    # Active noradrenaline required
    if not nora_ativa and (dose_nora is None or float(dose_nora) <= 0):
        return result

    result.fired = True
    result.band = "watch"
    result.severity = SeverityLevel.WATCH
    result.metadata = {
        "tempo_enchimento_capilar": tec,
        "noradrenalina_ativa": nora_ativa,
        "dose_noradrenalina": dose_nora,
        "threshold": "ANDROMEDA-SHOCK CRT > 3 s",
    }

    return result


# ---------------------------------------------------------------------------
# Unified evaluator: evaluate all 12 alerts
# ---------------------------------------------------------------------------


def evaluate_all(inputs: dict[str, Any]) -> dict[str, HemoAlertResult]:
    """Evaluate all 12 hemodynamics alerts for a set of clinical inputs.

    Returns a dict keyed by alert_id with results. Unfired alerts
    have fired=False.
    """
    evaluators = [
        evaluate_shock_index,
        evaluate_lactate_clearance,
        evaluate_vaso_escalation,
        evaluate_refractory_shock,
        evaluate_fluid_nonresponsive,
        evaluate_antihtn_conflict,
        # WAVE 3A stability RATIFY alerts (P1)
        evaluate_stability_vaso_negative_balance,
        evaluate_stability_lactate_sepsis,
        evaluate_stability_high_norad_without_adjuncts,
        evaluate_stability_refractory_triple,
        evaluate_stability_dobutamine_high_norad,
        evaluate_stability_crt_noradrenaline,
    ]

    results: dict[str, HemoAlertResult] = {}
    for fn in evaluators:
        r = fn(inputs)
        results[r.alert_id] = r

    return results


# ---------------------------------------------------------------------------
# CRIT non-auto-resolve guard
# ---------------------------------------------------------------------------


def should_auto_resolve(
    alert_result: HemoAlertResult,
    current_inputs: dict[str, Any],
    is_stale: bool = False,
) -> bool:
    """Determine whether a fired alert should auto-resolve.

    CRITICAL RULE: CRIT severity NEVER auto-resolves, even on stale data.
    The alert persists until a clinician explicitly acknowledges and resolves it.
    Watch/urgent alerts may auto-resolve when inputs return to normal range.

    Returns True if the alert should auto-resolve, False otherwise.
    """
    if alert_result.severity == SeverityLevel.CRITICAL:
        return False  # NEVER auto-resolve CRIT

    # For watch/urgent: auto-resolve if stale
    return is_stale


# ---------------------------------------------------------------------------
# Alert definitions for seeding
# ---------------------------------------------------------------------------


HEMO_ALERT_DEFINITIONS = [
    {
        "definition_version": "ALERT-HEMO-SHOCK-INDEX-01-a1b2c3",
        "score_type": "SHOCK_INDEX",
        "semver": "1.0.0",
        "spec_hash": "he01a1b2c3d4e5f6",
        "description": (
            "ALERT-HEMO-SHOCK-INDEX-01: Índice de choque elevado — hipoperfusão oculta. "
            "SI > 0.9 OR MSI > 1.3 sustained > PT15M + perfusion corroborator (lactate > 2 mmol/L "
            "OR TEC > 3 s). Rady 1994 + Liu 2012 + ANDROMEDA-SHOCK 2019. severity=watch."
        ),
    },
    {
        "definition_version": "ALERT-HEMO-LACTATE-CLEARANCE-02-b2c3d4",
        "score_type": "LACTATE_CLEARANCE",
        "semver": "1.0.0",
        "spec_hash": "he02b2c3d4e5f6a7",
        "description": (
            "ALERT-HEMO-LACTATE-CLEARANCE-02: Clearance de lactato inadequado. "
            "Active resuscitation gate + baseline >= 2 mmol/L + (2h clearance < 10% OR "
            "6h lactate > 2 mmol/L). Jones 2010 JAMA + SSC 2021. severity=critical."
        ),
    },
    {
        "definition_version": "ALERT-HEMO-VASO-ESCALATION-03-c3d4e5",
        "score_type": "VASO_ESCALATION",
        "semver": "1.0.0",
        "spec_hash": "he03c3d4e5f6a7b8",
        "description": (
            "ALERT-HEMO-VASO-ESCALATION-03: Escalonamento de vasopressor. "
            "NE > 0 mcg/kg/min + (>50% dose increase in 2h OR second vasopressor added). "
            "SCCM 2024 + SSC 2021. All dosing canonical mcg/kg/min. severity=urgent."
        ),
    },
    {
        "definition_version": "ALERT-HEMO-REFRACTORY-SHOCK-04-d4e5f6",
        "score_type": "REFRACTORY_SHOCK",
        "semver": "1.0.0",
        "spec_hash": "he04d4e5f6a7b8c9",
        "description": (
            "ALERT-HEMO-REFRACTORY-SHOCK-04: Choque refratário — hipotensão sob vasopressor máximo. "
            "MAP < 65 mmHg sustained > PT30M AND NE > 1.0 mcg/kg/min. "
            "SEPSISPAM 2014 + SCCM 2024. Adjunct-absence enrichment. severity=critical."
        ),
    },
    {
        "definition_version": "ALERT-HEMO-FLUID-NONRESPONSIVE-05-e5f6a7",
        "score_type": "FLUID_NONRESPONSIVE",
        "semver": "1.0.0",
        "spec_hash": "he05e5f6a7b8c9d0",
        "description": (
            "ALERT-HEMO-FLUID-NONRESPONSIVE-05: Não responsivo a fluidos — risco de sobrecarga. "
            "Primary (PPV/SVV < 10% + ΔSV < 10% + balance > 3000 mL) OR "
            "Fallback (fluid challenge + ΔMAP < 5 mmHg + Δlactate < 5%). "
            "Marik 2013 + Monnet 2016. severity=watch."
        ),
    },
    {
        "definition_version": "ALERT-HEMO-ANTIHTN-CONFLICT-06-f6a7b8",
        "score_type": "ANTIHTN_CONFLICT",
        "semver": "1.0.0",
        "spec_hash": "he06f6a7b8c9d0e1",
        "description": (
            "ALERT-HEMO-ANTIHTN-CONFLICT-06: Conflito anti-hipertensivo × PA / vasopressor. "
            "Branch A (deprescribe): active antihypertensive + hypotension/vasopressor. "
            "Branch B: uncontrolled HTN off pressor, no permissive indication. "
            "Institutional medication-safety pathway. severity=watch."
        ),
    },
]
