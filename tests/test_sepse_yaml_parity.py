"""Golden-vector parity tests: declarative ``sepse.yaml`` v4 vs. ``domain_sepsis.py``.

Sprint 3 sepsis governance (branch ``fix/sprint-3-sepsis-governance``): the rich,
imperative sepsis logic in :mod:`intensicare.services.domain_sepsis` (SIRS
scoring, PCT stewardship, SSC-2021 bundle timers — validated by 31 test
vectors in ``tests/test_domain_sepsis.py``) has been ported to the declarative
Trilhas Engine model (``_work/alerts/pathways/sepse.yaml`` v4.0.0). This module
is the differential parity harness: for every one of the 31 vectors it

  1. Computes the domain_sepsis "oracle" verdict by calling the exact same
     ``_eval_*`` function ``test_domain_sepsis.py`` asserts against (the rich
     implementation is NOT touched by this port — it remains the reference).
  2. Adapts the vector's raw (domain-shaped) inputs into the new declarative
     input vocabulary (``qsofa_score``, ``sirs_count``, ``lactato``, ...) that
     ``sepse.yaml`` v4 and ``sepsis_input_provider.build_sepsis_inputs`` speak.
  3. Runs the REAL ``TrilhasEngine`` (loading the actual
     ``_work/alerts/pathways/`` directory — no fixture YAML) against the
     adapted inputs and reads whether the mapped criterion fired.
  4. Asserts both verdicts agree.

Alert -> criterion map (see ``_work/alerts/pathways/sepse.yaml`` v4.0.0):
  ALERT-SEPSIS-SCREEN-01          -> crit-sep-screen
  ALERT-SEPSIS-ORGAN-02           -> crit-sep-organ           (lactate>2 branch only)
  ALERT-SEPSIS-SHOCK-03           -> crit-sep-shock
  ALERT-SEPSIS-BUNDLE-OVERDUE-04  -> crit-sep-bundle-atb-1h    (item_pacote="primeira_hora")
  ALERT-SEPSIS-BUNDLE-OVERDUE-04  -> crit-sep-bundle-reaval-3h (item_pacote="reavaliacao")
  ALERT-SEPSIS-PCT-RISING-05      -> crit-sep-pct-rising
  ALERT-SEPSIS-PCT-DEESC-06       -> crit-sep-pct-deesc

Non-portable vector (documented xfail, strict — see module docstring of
``ALERT-SEPSIS-ORGAN-02``'s TV-6 below): the declarative v4 input vocabulary
has no "previous lactate" / "lactate delta over N hours" input (only the
current ``lactato`` value — see ``sepsis_input_provider.py``'s documented data
gaps), so the delta-lactate-trend branch of ORGAN-02 cannot be evaluated
declaratively. This is 1 of a maximum of 3 allowed xfails.

Suppression: ``sepse.yaml``'s ``suppression`` block (15 min cooldown, 6/hour
rate limit) is irrelevant to these tests — they assert predicate LOGIC, not
dedup behaviour. It is neutralized two ways, belt-and-braces: (1) the
session/function-scoped ``_isolate_redis`` autouse fixture in
``tests/conftest.py`` flushes the test Redis DB before/after every single
parametrized test item, so no cooldown/rate-limit key can ever survive across
vectors; (2) each vector additionally uses a unique ``mpi_id`` (derived from
its name), so even without the Redis flush, no vector could ever collide with
another's suppression state (first-ever firing for that identity always
passes the cooldown/rate-limit check).
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from intensicare.services.domain_sepsis import (
    _eval_bundle_overdue_04,
    _eval_organ_02,
    _eval_pct_deesc_06,
    _eval_pct_rising_05,
    _eval_screen_01,
    _eval_shock_03,
    _compute_qsofa_points,
    _compute_sirs_count,
    _infection_present,
)
from intensicare.services.trilhas_engine import TrilhasEngine

SEPSE_PATHWAY_ID = 2

OracleFn = Callable[[dict[str, Any]], tuple[bool, str]]
AdapterFn = Callable[[dict[str, Any]], dict[str, Any]]


# ---------------------------------------------------------------------------
# Fixture: real TrilhasEngine over the real _work/alerts/pathways/ directory
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def trilhas_engine() -> TrilhasEngine:
    """The production TrilhasEngine, loading the real pathway YAML directory.

    Not named ``engine`` to avoid any confusion with the unrelated
    session-scoped SQLAlchemy ``engine`` fixture in ``tests/conftest.py``
    (different fixture, different purpose — this test module needs no DB).
    """
    return TrilhasEngine()


async def _get_criterion_met(
    trilhas_engine: TrilhasEngine,
    mpi_id: str,
    criterion_id: str,
    patient_data: dict[str, Any],
) -> bool:
    """Run the declarative engine and report whether ``criterion_id`` fired.

    ``TrilhasEvaluator.evaluate_pathway`` (which ``TrilhasEngine.evaluate``
    delegates to) only returns criteria that are MET — a criterion absent
    from the firings list means either it evaluated to ``met=False`` or one
    of its referenced inputs was missing from ``patient_data`` (KeyError,
    caught and skipped per-criterion). Both cases correctly mean "not met"
    for this test's purposes.
    """
    alerts = await trilhas_engine.evaluate(mpi_id, patient_data)
    for alert in alerts:
        if alert.pathway_id != SEPSE_PATHWAY_ID:
            continue
        for firing in alert.firings:
            if firing.criterion_id == criterion_id and not firing.suppressed:
                return True
    return False


# ---------------------------------------------------------------------------
# Adapters: domain_sepsis-shaped raw vector inputs -> sepse.yaml v4 inputs
#
# Note on composite predicates: PredicateCompiler's AND/OR/NOT nodes do NOT
# short-circuit (all sub_predicates are evaluated unconditionally, mirroring
# how graded/threshold classification always runs). A KeyError from ANY
# sub_predicate propagates out of the WHOLE criterion evaluation (caught only
# at the pathway level, which then skips the entire criterion — not just the
# offending branch). domain_sepsis's imperative evaluators, by contrast, use
# ``_num()``/``_bool()`` + early returns that treat a missing field as a
# harmless "not applicable" 0/False/None and keep evaluating other branches.
# To reproduce that same graceful behaviour without inventing a "missing
# input" affordance the compiler doesn't have, these adapters always supply
# every input referenced anywhere in the target criterion's predicate tree,
# filling in clinically-neutral defaults (e.g. PAM=999 "clearly not <65",
# vasopressor/peak-drop=0/False) whenever the raw vector itself omits them.
# ---------------------------------------------------------------------------


def _adapt_screen(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "qsofa_score": _compute_qsofa_points(raw),
        "sirs_count": _compute_sirs_count(raw),
        "infeccao_suspeita": _infection_present(raw),
    }


def _adapt_organ(raw: dict[str, Any]) -> dict[str, Any]:
    # Only the lactate>2 branch is portable (see module docstring) — the
    # delta-lactate-trend branch has no declarative equivalent input.
    return {
        "qsofa_score": _compute_qsofa_points(raw),
        "lactato": raw.get("lactato_arterial", -1.0),
    }


def _adapt_shock(raw: dict[str, Any]) -> dict[str, Any]:
    dose = raw.get("dose_vasopressor")
    fluid_bolus = raw.get("fluid_bolus_given", False)
    vasopressor_ativo = bool(dose and dose > 0) or bool(fluid_bolus)
    return {
        "lactato": raw.get("lactato_arterial", -1.0),
        # Default well above 65 so an unspecified PAM never spuriously
        # satisfies the "PAM < 65" branch (mirrors domain's `map_val is
        # not None` guard, which simply skips the branch when PAM is
        # unmeasured).
        "pam": raw.get("pressao_arterial_media", 999.0),
        "vasopressor_ativo": vasopressor_ativo,
    }


def _adapt_bundle_atb(raw: dict[str, Any]) -> dict[str, Any]:
    """BUNDLE-OVERDUE-04, item_pacote="primeira_hora" -> crit-sep-bundle-atb-1h."""
    return {
        "atb_status": bool(raw.get("item_checked", False)),
        "minutes_since_accept_atb": raw.get("minutes_since_accept", 0),
    }


def _adapt_bundle_reaval(raw: dict[str, Any]) -> dict[str, Any]:
    """BUNDLE-OVERDUE-04, item_pacote="reavaliacao" -> crit-sep-bundle-reaval-3h."""
    return {
        "culturas_status": bool(raw.get("item_checked", False)),
        "minutes_since_accept_culturas": raw.get("minutes_since_accept", 0),
    }


def _adapt_pct_rising(raw: dict[str, Any]) -> dict[str, Any]:
    pct = raw.get("procalcitonina")
    pct_prev = raw.get("procalcitonina_anterior")
    delta = (pct - pct_prev) if (pct is not None and pct_prev is not None) else -1.0
    return {
        "atb_ativa_horas": raw.get("atb_ativa_horas", 0),
        "delta_pct_24h": delta,
    }


def _adapt_pct_deesc(raw: dict[str, Any]) -> dict[str, Any]:
    pct = raw.get("procalcitonina")
    peak = raw.get("pico_pct")
    pct_queda_pct = 0.0
    if peak is not None and peak > 0 and pct is not None and pct < peak:
        pct_queda_pct = (peak - pct) / peak * 100.0
    return {
        "atb_ativa_horas": raw.get("atb_ativa_horas", 0),
        "paciente_estavel_48h": not bool(raw.get("patient_unstable", False)),
        "pct": pct if pct is not None else 999.0,
        "pct_queda_pct": pct_queda_pct,
    }


# ---------------------------------------------------------------------------
# Golden vectors — 1:1 port of the 31 test vectors in tests/test_domain_sepsis.py
# ---------------------------------------------------------------------------


class Vector:
    """One golden vector: a domain_sepsis input dict + its declarative mapping."""

    def __init__(
        self,
        name: str,
        criterion_id: str,
        raw: dict[str, Any],
        oracle: OracleFn,
        adapter: AdapterFn,
    ) -> None:
        self.name = name
        self.criterion_id = criterion_id
        self.raw = raw
        self.oracle = oracle
        self.adapter = adapter


GOLDEN_VECTORS: list[Vector] = [
    # ── ALERT-SEPSIS-SCREEN-01 -> crit-sep-screen (5 vectors) ──────────────
    Vector(
        "screen-tv1-fire-qsofa-infection", "crit-sep-screen",
        {
            "qsofa": 2, "frequencia_respiratoria": 24,
            "pressao_arterial_sistolica": 96, "glasgow": 14,
            "suspeita_infeccao_documentada": True,
        },
        _eval_screen_01, _adapt_screen,
    ),
    Vector(
        "screen-tv2-fire-sirs-atb", "crit-sep-screen",
        {
            "temperatura": 38.6, "frequencia_cardiaca": 112,
            "leucocitos": 15.2, "qsofa": 0,
            "atb_iniciado_ultimas_24h": True,
        },
        _eval_screen_01, _adapt_screen,
    ),
    Vector(
        "screen-tv3-no-fire-sirs-no-infection", "crit-sep-screen",
        {
            "temperatura": 38.6, "frequencia_cardiaca": 112,
            "leucocitos": 15.2, "qsofa": 0,
            "cultura_positiva": False, "atb_iniciado_ultimas_24h": False,
            "suspeita_infeccao_documentada": False,
        },
        _eval_screen_01, _adapt_screen,
    ),
    Vector(
        "screen-tv4-boundary-exact-no-fire", "crit-sep-screen",
        {
            "frequencia_cardiaca": 90, "temperatura": 37.4,
            "frequencia_respiratoria": 20, "leucocitos": 12.0,
            "suspeita_infeccao_documentada": True,
        },
        _eval_screen_01, _adapt_screen,
    ),
    Vector(
        "screen-tv5-boundary-just-above-fires", "crit-sep-screen",
        {
            "frequencia_cardiaca": 91, "temperatura": 38.1,
            "frequencia_respiratoria": 20, "leucocitos": 12.0,
            "qsofa": 0, "cultura_positiva": True,
        },
        _eval_screen_01, _adapt_screen,
    ),

    # ── ALERT-SEPSIS-ORGAN-02 -> crit-sep-organ (6 vectors, TV-6 xfail) ────
    Vector(
        "organ-tv1-fire-qsofa-lactate-high", "crit-sep-organ",
        {"qsofa": 2, "lactato_arterial": 2.4},
        _eval_organ_02, _adapt_organ,
    ),
    Vector(
        "organ-tv2-no-fire-lactate-below-trend-weak", "crit-sep-organ",
        {"qsofa": 2, "lactato_arterial": 1.8, "lactato_arterial_anterior": 1.2},
        _eval_organ_02, _adapt_organ,
    ),
    Vector(
        "organ-tv3-no-fire-qsofa-low", "crit-sep-organ",
        {"qsofa": 1, "lactato_arterial": 5.0},
        _eval_organ_02, _adapt_organ,
    ),
    Vector(
        "organ-tv4-boundary-lactate-2-0-no-fire", "crit-sep-organ",
        {"qsofa": 2, "lactato_arterial": 2.0},
        _eval_organ_02, _adapt_organ,
    ),
    Vector(
        "organ-tv5-boundary-lactate-2-01-fires", "crit-sep-organ",
        {"qsofa": 2, "lactato_arterial": 2.01},
        _eval_organ_02, _adapt_organ,
    ),
    Vector(
        "organ-tv6-fire-delta-lactato-trend-XFAIL", "crit-sep-organ",
        {
            "qsofa": 2, "lactato_arterial": 1.9,
            "lactato_arterial_anterior": 1.0, "lactate_delta_hours": 1.0,
        },
        _eval_organ_02, _adapt_organ,
    ),

    # ── ALERT-SEPSIS-SHOCK-03 -> crit-sep-shock (5 vectors) ─────────────────
    Vector(
        "shock-tv1-fire-lactate-4-2", "crit-sep-shock",
        {"lactato_arterial": 4.2},
        _eval_shock_03, _adapt_shock,
    ),
    Vector(
        "shock-tv2-fire-map-low-on-vasopressor", "crit-sep-shock",
        {"pressao_arterial_media": 58, "dose_vasopressor": 0.2, "lactato_arterial": 3.1},
        _eval_shock_03, _adapt_shock,
    ),
    Vector(
        "shock-tv3-no-fire-map-low-no-vasopressor", "crit-sep-shock",
        {
            "pressao_arterial_media": 58, "dose_vasopressor": 0,
            "fluid_bolus_given": False, "lactato_arterial": 2.5,
        },
        _eval_shock_03, _adapt_shock,
    ),
    Vector(
        "shock-tv4-boundary-lactate-4-0-fires", "crit-sep-shock",
        {"lactato_arterial": 4.0, "pressao_arterial_media": 70},
        _eval_shock_03, _adapt_shock,
    ),
    Vector(
        "shock-tv5-boundary-map-65-no-fire", "crit-sep-shock",
        {"pressao_arterial_media": 65, "dose_vasopressor": 0.3, "lactato_arterial": 3.0},
        _eval_shock_03, _adapt_shock,
    ),

    # ── ALERT-SEPSIS-BUNDLE-OVERDUE-04 (5 vectors) ──────────────────────────
    # item_pacote="primeira_hora" -> crit-sep-bundle-atb-1h
    Vector(
        "bundle-tv1-fire-overdue-primeira-hora", "crit-sep-bundle-atb-1h",
        {
            "protocol_active": True, "item_checked": False,
            "item_pacote": "primeira_hora", "minutes_since_accept": 75,
        },
        _eval_bundle_overdue_04, _adapt_bundle_atb,
    ),
    Vector(
        "bundle-tv2-no-fire-item-already-checked", "crit-sep-bundle-atb-1h",
        {
            "protocol_active": True, "item_checked": True,
            "item_pacote": "primeira_hora", "minutes_since_accept": 75,
        },
        _eval_bundle_overdue_04, _adapt_bundle_atb,
    ),
    Vector(
        "bundle-tv4-boundary-exactly-60-min-no-fire", "crit-sep-bundle-atb-1h",
        {
            "protocol_active": True, "item_checked": False,
            "item_pacote": "primeira_hora", "minutes_since_accept": 60,
        },
        _eval_bundle_overdue_04, _adapt_bundle_atb,
    ),
    # item_pacote="reavaliacao" -> crit-sep-bundle-reaval-3h
    Vector(
        "bundle-tv3-no-fire-reavaliacao-not-yet-due", "crit-sep-bundle-reaval-3h",
        {
            "protocol_active": True, "item_checked": False,
            "item_pacote": "reavaliacao", "minutes_since_accept": 120,
        },
        _eval_bundle_overdue_04, _adapt_bundle_reaval,
    ),
    Vector(
        "bundle-tv5-boundary-181-min-fires", "crit-sep-bundle-reaval-3h",
        {
            "protocol_active": True, "item_checked": False,
            "item_pacote": "reavaliacao", "minutes_since_accept": 181,
        },
        _eval_bundle_overdue_04, _adapt_bundle_reaval,
    ),

    # ── ALERT-SEPSIS-PCT-RISING-05 -> crit-sep-pct-rising (5 vectors) ──────
    Vector(
        "pct-rising-tv1-fire-atb-60h", "crit-sep-pct-rising",
        {"procalcitonina": 1.2, "procalcitonina_anterior": 0.8, "atb_ativa_horas": 60},
        _eval_pct_rising_05, _adapt_pct_rising,
    ),
    Vector(
        "pct-rising-tv2-no-fire-atb-too-early", "crit-sep-pct-rising",
        {"procalcitonina": 1.2, "procalcitonina_anterior": 0.8, "atb_ativa_horas": 24},
        _eval_pct_rising_05, _adapt_pct_rising,
    ),
    Vector(
        "pct-rising-tv3-no-fire-pct-falling", "crit-sep-pct-rising",
        {"procalcitonina": 0.9, "procalcitonina_anterior": 1.5, "atb_ativa_horas": 72},
        _eval_pct_rising_05, _adapt_pct_rising,
    ),
    Vector(
        "pct-rising-tv4-boundary-delta-0-25-no-fire", "crit-sep-pct-rising",
        {"procalcitonina": 1.05, "procalcitonina_anterior": 0.80, "atb_ativa_horas": 48},
        _eval_pct_rising_05, _adapt_pct_rising,
    ),
    Vector(
        "pct-rising-tv5-boundary-delta-0-26-fires", "crit-sep-pct-rising",
        {"procalcitonina": 1.06, "procalcitonina_anterior": 0.80, "atb_ativa_horas": 48},
        _eval_pct_rising_05, _adapt_pct_rising,
    ),

    # ── ALERT-SEPSIS-PCT-DEESC-06 -> crit-sep-pct-deesc (5 vectors) ────────
    Vector(
        "pct-deesc-tv1-fire-pct-low-stable", "crit-sep-pct-deesc",
        {"procalcitonina": 0.18, "atb_ativa_horas": 60, "patient_unstable": False},
        _eval_pct_deesc_06, _adapt_pct_deesc,
    ),
    Vector(
        "pct-deesc-tv2-fire-pct-drop-85-percent", "crit-sep-pct-deesc",
        {"procalcitonina": 0.9, "pico_pct": 6.0, "atb_ativa_horas": 72, "patient_unstable": False},
        _eval_pct_deesc_06, _adapt_pct_deesc,
    ),
    Vector(
        "pct-deesc-tv3-no-fire-unstable-patient", "crit-sep-pct-deesc",
        {"procalcitonina": 0.18, "atb_ativa_horas": 60, "patient_unstable": True},
        _eval_pct_deesc_06, _adapt_pct_deesc,
    ),
    Vector(
        "pct-deesc-tv4-boundary-pct-0-25-no-fire", "crit-sep-pct-deesc",
        {"procalcitonina": 0.25, "atb_ativa_horas": 60, "patient_unstable": False},
        _eval_pct_deesc_06, _adapt_pct_deesc,
    ),
    Vector(
        "pct-deesc-tv5-boundary-pct-0-24-fires", "crit-sep-pct-deesc",
        {"procalcitonina": 0.24, "atb_ativa_horas": 48, "patient_unstable": False},
        _eval_pct_deesc_06, _adapt_pct_deesc,
    ),
]

assert len(GOLDEN_VECTORS) == 31, f"Expected 31 golden vectors, got {len(GOLDEN_VECTORS)}"

# Non-portable vectors — maximum 3 allowed (see module docstring). Reason is
# surfaced in the xfail report; ``strict=True`` means an unexpected PASS here
# fails the suite (keeps this list honest as sepse.yaml evolves).
_XFAIL_REASONS: dict[str, str] = {
    "organ-tv6-fire-delta-lactato-trend-XFAIL": (
        "ALERT-SEPSIS-ORGAN-02's delta-lactate-trend branch (rate of change "
        "over a lookback window) has no declarative equivalent in sepse.yaml "
        "v4 — the input vocabulary only carries the current 'lactato' value, "
        "not a previous reading or lookback interval (see "
        "sepsis_input_provider.py's documented data gaps: no persisted "
        "lactate history is read there either). crit-sep-organ only ports "
        "the lactate>2 absolute-value branch."
    ),
}
assert len(_XFAIL_REASONS) <= 3, "Max 3 xfails allowed — port is incomplete, rework the YAML."


def _to_param(vector: Vector) -> Any:
    reason = _XFAIL_REASONS.get(vector.name)
    marks = [pytest.mark.xfail(reason=reason, strict=True)] if reason else []
    return pytest.param(vector, id=vector.name, marks=marks)


@pytest.mark.parametrize("vector", [_to_param(v) for v in GOLDEN_VECTORS])
async def test_golden_vector_parity(
    trilhas_engine: TrilhasEngine, vector: Vector
) -> None:
    """Declarative sepse.yaml v4 criterion.met must match domain_sepsis's verdict."""
    oracle_fired, oracle_reason = vector.oracle(vector.raw)
    patient_data = vector.adapter(vector.raw)
    mpi_id = f"GOLDEN-{vector.name}"

    declarative_met = await _get_criterion_met(
        trilhas_engine, mpi_id, vector.criterion_id, patient_data,
    )

    assert declarative_met == oracle_fired, (
        f"Parity mismatch for {vector.name!r}: "
        f"declarative criterion {vector.criterion_id!r} met={declarative_met}, "
        f"domain_sepsis fired={oracle_fired} ({oracle_reason}); "
        f"raw={vector.raw!r} adapted={patient_data!r}"
    )


# ---------------------------------------------------------------------------
# Sanity checks on the pathway wiring itself
# ---------------------------------------------------------------------------


def test_sepse_pathway_is_active_and_v4(trilhas_engine: TrilhasEngine) -> None:
    """sepse.yaml v4 must compile cleanly (no criterion deactivates the pathway)."""
    pdef = trilhas_engine.get_pathway(SEPSE_PATHWAY_ID)
    assert pdef is not None
    assert pdef.active is True, (
        f"sepse pathway inactive — compile failures: {trilhas_engine.load_failures}"
    )
    assert pdef.version == "4.0.0"


def test_sepse_pathway_has_all_expected_criteria(trilhas_engine: TrilhasEngine) -> None:
    """All 7 preserved v3 criteria + 8 new v4 criteria are present."""
    pdef = trilhas_engine.get_pathway(SEPSE_PATHWAY_ID)
    assert pdef is not None
    ids = {c["id"] for c in pdef.criteria}
    expected = {
        # preserved from v3
        "crit-sep-qsofa", "crit-sep-lactato", "crit-sep-pct", "crit-sep-pam",
        "crit-sep-culturas", "crit-sep-atb", "crit-sep-fluid",
        # new in v4
        "crit-sep-screen", "crit-sep-organ", "crit-sep-shock",
        "crit-sep-bundle-atb-1h", "crit-sep-bundle-reaval-3h",
        "crit-sep-culturas-antes-atb", "crit-sep-pct-rising", "crit-sep-pct-deesc",
    }
    assert ids == expected
