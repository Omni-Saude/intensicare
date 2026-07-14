"""Humanized PT-BR clinical copy for alert titles/bodies.

ADR-0039 §6: alert title/body text is centralized here as pure,
dependency-free string templates — the single source of truth called from
``alert_engine.check_score_against_thresholds`` (never a string built
inline at the call site, never duplicated in the UI). See
``docs/adr/ADR-0039-alert-group-read-aggregation.md`` and
``docs/audit/ALERT_CONSOLIDATION_ANALYSIS.md`` §5 for the analysis this
module implements.

Tone and the 3-part structure (o que aconteceu / por que importa / o que
verificar) follow the pattern already validated in production code —
``pathway_enrollment._build_recommendation`` (~L819-1019) and
``api.v1.cds_hooks._build_detail``: sober PT-BR clínico, no alarmism, no
diminutives, one concrete next action per severity band, consistent with
the severity vocabulary the frontend already renders
(``frontend-v3/components/dashboard/severity-dot.tsx`` SEVERITY_LABEL,
``frontend-v3/components/patient/alert-item.tsx`` SEVERITY_LABELS:
watch → "Observação", urgent → "Urgente", critical → "Crítico").

Clinical claims are anchored to evidence already cited elsewhere in this
codebase for the same score types — nothing here introduces a new
clinical claim:

* NEWS2: ``services/news2.py`` — ``NEWS2_HIGH_RISK_MIN = 7`` ("aggregate
  >= 7 -> high risk"), ``NEWS2_MEDIUM_RISK_MIN = 5`` ("aggregate >= 5 ->
  medium risk / urgent response"), sourced from the Royal College of
  Physicians NEWS2 (2017) protocol.
* MEWS: ``services/mews.py`` header comment — Subbe CP et al., QJM
  2001;94:521-526 — and the seed rationale in
  ``alembic/versions/0038_seed_default_threshold_config.py`` ("MEWS >= 5
  associado a aumento de mortalidade/admissão em UTI; >= 4 é o gatilho de
  resposta"), matching ``services/threshold_resolver.GUIDELINE_SOURCES``.

Scope decision (documented per the task's explicit instruction to decide
whether tenant/unit belong in the humanized body): the old inline body
(``alert_engine.py``, pre-humanization) appended a trailing
``"Tenant: {tenant_id}, Unit: {unit or 'N/A'}"`` line. That line is
dropped here, deliberately:

* ``tenant_id`` is redundant per-alert — a logged-in user only ever sees
  their own tenant's alerts (session/auth-scoped), so surfacing it inside
  every alert body added noise, not information.
* ``unit`` is administrative/operational metadata, not clinical content —
  it doesn't belong in a 3-part clinical explanation next to "o que
  verificar". Unlike ``mpi_id`` (which the UI already renders as a
  separate structured field — ``AlertResponse.patient_name``/``mpi_id``,
  confirmed in ``docs/audit/ALERT_CONSOLIDATION_ANALYSIS.md`` §2.5/§2.7),
  ``unit`` today has **no** structured column on the ``Alert`` model and
  **no** field on ``AlertResponse`` — so dropping it from the body is a
  real (if minor) loss of a previously-visible fact, not a no-op. Adding
  a structured ``unit`` column/contract field is a schema change out of
  this ticket's ≤3-file scope (2B.2, copy only); it is left as a
  follow-up for whoever owns 2B.1 (consolidation) or a future contract
  change, should per-alert unit display be judged necessary. The unit is
  still recoverable via the patient's own record (dashboard bed card,
  patient panel) — it just no longer appears inline in the alert text.
"""

from __future__ import annotations

# PT-BR severity labels for the *title* — intentionally identical to the
# frontend's existing severity badge vocabulary so the alert title and the
# severity badge next to it never disagree in wording.
_SEVERITY_LABEL: dict[str, str] = {
    "watch": "observação",
    "urgent": "urgente",
    "critical": "crítico",
}

# PT-BR band phrase for the "o que aconteceu" sentence — mirrors the
# "faixa crítica"/"faixa urgente" phrasing already used in
# pathway_enrollment._build_recommendation (e.g. "critério em faixa
# crítica", "critério em faixa urgente").
_BAND_PHRASE: dict[str, str] = {
    "watch": "faixa de observação",
    "urgent": "faixa urgente",
    "critical": "faixa crítica",
}

# "Por que importa" — evidence-grounded clinical interpretation, one entry
# per (score_type, severity). Only NEWS2 and MEWS are exercised on the live
# alert path today (ALERT_CONSOLIDATION_ANALYSIS.md §5.2); any other
# score_type (SOFA/qSOFA future) falls back to _GENERIC_WHY below.
_NEWS2_WHY: dict[str, str] = {
    "watch": (
        "Está abaixo do limiar de risco moderado do NEWS2 (score ≥ 5), mas fora "
        "da faixa normal — é um sinal precoce a acompanhar (Royal College of "
        "Physicians, NEWS2, 2017)."
    ),
    "urgent": (
        "NEWS2 entre 5 e 6 indica risco clínico moderado e recomenda resposta "
        "urgente (Royal College of Physicians, NEWS2, 2017)."
    ),
    "critical": (
        "NEWS2 ≥ 7 indica risco alto de deterioração clínica (Royal College of "
        "Physicians, NEWS2, 2017)."
    ),
}

_MEWS_WHY: dict[str, str] = {
    "watch": (
        "Está abaixo do limiar-gatilho de resposta do MEWS (score ≥ 4), mas fora "
        "da faixa normal — sinal a ser acompanhado (Subbe CP et al., QJM "
        "2001;94:521-6)."
    ),
    "urgent": (
        "MEWS ≥ 4 é o limiar-gatilho de resposta clínica descrito por Subbe et "
        "al. (QJM 2001;94:521-6)."
    ),
    "critical": (
        "MEWS ≥ 5 está associado a aumento de mortalidade e de admissão em UTI "
        "(Subbe CP et al., QJM 2001;94:521-6)."
    ),
}

# Neutral, clinically-noncommittal fallback — used whenever score_type is
# not one of the score types this module has an evidence-grounded mapping
# for (today: anything other than NEWS2/MEWS, e.g. SOFA/qSOFA). Makes no
# specific clinical claim beyond "this crossed a configured threshold" —
# safe by construction, never invents medicine for a score it doesn't know.
_GENERIC_WHY: dict[str, str] = {
    "watch": "O valor está fora da faixa considerada normal para este indicador.",
    "urgent": (
        "O valor cruzou um limiar clínico configurado que indica necessidade de "
        "atenção prioritária."
    ),
    "critical": (
        "O valor está em faixa crítica configurada, associada a maior risco para o paciente."
    ),
}

# "O que verificar" — objective next action per severity band. Not
# score-type-specific (the action is about response tempo, not about the
# score's clinical mechanism), so this same mapping is correct for the
# fallback path too.
_WHAT_TO_CHECK: dict[str, str] = {
    "watch": (
        "Reavaliar na próxima ronda de sinais vitais, conforme a frequência de "
        "monitorização já prescrita."
    ),
    "urgent": (
        "Solicitar reavaliação médica com conjunto completo de sinais vitais o quanto antes."
    ),
    "critical": (
        "Realizar avaliação imediata à beira-leito e considerar acionar o time de resposta rápida."
    ),
}

_WHY_BY_SCORE_TYPE: dict[str, dict[str, str]] = {
    "NEWS2": _NEWS2_WHY,
    "MEWS": _MEWS_WHY,
}


def build_alert_copy(
    score_type: str,
    severity: str,
    score_value: int,
    threshold: int,
) -> tuple[str, str]:
    """Build the humanized ``(title, body)`` pair for a clinical alert.

    Pure function, no I/O, no database/network access — safe to call from
    any context (alert creation, tests, future re-render of historical
    alerts).

    Args:
        score_type: Clinical score identifier, e.g. ``"NEWS2"``, ``"MEWS"``.
            Any value is accepted; only ``"NEWS2"``/``"MEWS"`` get an
            evidence-grounded "por que importa" clause today — everything
            else uses the generic, clinically-safe fallback.
        severity: One of ``"watch"``, ``"urgent"``, ``"critical"``
            (``schemas.severity.CANONICAL_SEVERITIES`` minus ``"normal"``
            — ``check_score_against_thresholds`` never raises an alert at
            ``"normal"``). An unrecognized value falls back to the
            ``"watch"`` (least severe) copy rather than raising, so a
            future severity-model change degrades gracefully instead of
            crashing alert creation.
        score_value: The score value that crossed the threshold.
        threshold: The configured threshold for this severity band (i.e.
            ``getattr(config, f"{severity}_threshold")`` at the call
            site).

    Returns:
        ``(title, body)``:

        * ``title`` — short, scannable string for dense list views:
          ``"{score_type} {severity em PT-BR} — {score_value}"``, e.g.
          ``"NEWS2 crítico — 17"``. Always well under the ``Alert.title``
          DB column limit (``String(255)``) and kept ≤60 chars by
          construction (score_type/severity/score_value are all short).
        * ``body`` — 3-part PT-BR clinical explanation, one labeled
          sentence per part (o que aconteceu / por que importa / o que
          verificar), separated by newlines so the UI's disclosure region
          (``alert-row.tsx``) can render it as-is.
    """
    severity_label = _SEVERITY_LABEL.get(severity, _SEVERITY_LABEL["watch"])
    band_phrase = _BAND_PHRASE.get(severity, _BAND_PHRASE["watch"])
    why_map = _WHY_BY_SCORE_TYPE.get(score_type, _GENERIC_WHY)
    why = why_map.get(severity, _GENERIC_WHY["watch"])
    what_to_check = _WHAT_TO_CHECK.get(severity, _WHAT_TO_CHECK["watch"])

    title = f"{score_type} {severity_label} — {score_value}"

    what_happened = (
        f"O {score_type} do paciente atingiu {score_value}, entrando na "
        f"{band_phrase} (limiar ≥ {threshold})."
    )

    body = (
        f"O que aconteceu: {what_happened}\n"
        f"Por que importa: {why}\n"
        f"O que verificar: {what_to_check}"
    )

    return title, body
