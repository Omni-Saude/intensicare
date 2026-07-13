"""Domain service: ALERTAS cluster — UNVERIFIABLE RATIFY rules.

RATIFIED 2026-07-04 per RATIFICATION-DECISIONS.md ASK-2:
  - GRP-ALERT-B-COUNTING: Recommended default A (keep as-is)
  - RULE-ALERTAS-001: Count triggered criteria (contar_qtd_criterios_alerta)
  - RULE-ALERTAS-002: Aggregate alert counts across movimentacoes

All rules confirmed verbatim per drafter recommendations under owner delegation.
Provenance: ahlabs-trilhas @ 8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.
"""

from __future__ import annotations

__version__ = "3.0.0"

from typing import Any

# ── RULE-ALERTAS-001: Count triggered criteria ─────────────────────────────
# Cluster: alertas | Type: formula | Status: OK | Verdict: UNVERIFIABLE
# Confidence: high | Clinical impact: n/a
#
# Legacy source: trilha_automatica/utils.py:8-13, core/utils.py:18-23 @8166c07
# Byte-identical implementations in both locations; no divergence.
#
# Logic:
#   acc = 0
#   for criterio in trilha["criterios"]:
#       if criterio["esta_alerta"] == 1:
#           acc += 1
#   return acc
#
# Edge cases: only exact ==1 increments; empty criterios -> 0.


def contar_qtd_criterios_alerta(criterios: list[dict[str, Any]]) -> int:
    """Count how many criteria in a trilha have esta_alerta == 1.

    RULE-ALERTAS-001 (RATIFIED, UNVERIFIABLE).
    This is a generic business-rule counter — not a validated clinical score.
    Only exact ==1 increments; empty list returns 0.

    Args:
        criterios: List of criterion dicts, each with 'esta_alerta' in {0,1}.

    Returns:
        Integer count of criteria with esta_alerta == 1.

    Test vectors (from rule audit):
        [{'esta_alerta':1},{'esta_alerta':1},{'esta_alerta':0}] -> 2
        [] -> 0
        [{'esta_alerta':1},{'esta_alerta':2},{'esta_alerta':None},{'esta_alerta':0}] -> 1
    """
    acc = 0
    for criterio in criterios:
        if criterio.get("esta_alerta") == 1:
            acc += 1
    return acc


# ── RULE-ALERTAS-002: Aggregate alert counts across movimentacoes ──────────
# Cluster: alertas | Type: scoring | Status: OK | Verdict: UNVERIFIABLE
# Confidence: high | Clinical impact: n/a
#
# Legacy source: core/models/leito.py:709-736 @8166c07
#
# Logic:
#   for each movimentacao's tuple of
#       (trilha_sepse.alerta, trilha_ventilacao.alerta,
#        trilha_sedacao.alerta, trilha_estabilidade.alerta):
#     if "VERMELHO" in tuple: VERMELHO += 1
#     elif "AMARELO" in tuple: AMARELO += 1
#     else: NEUTRO += 1


def _worst_alert_color(alert_tuple: tuple[str | None, ...]) -> str:
    """Determine the worst alert color with VERMELHO > AMARELO > NEUTRO precedence.

    Implements RULE-ALERTAS-002 precedence logic.
    """
    if "VERMELHO" in alert_tuple:
        return "VERMELHO"
    if "AMARELO" in alert_tuple:
        return "AMARELO"
    return "NEUTRO"


def aggregate_alert_counts(
    movimentacao_alerts: list[tuple[str | None, str | None, str | None, str | None]],
) -> dict[str, int]:
    """Aggregate alert counts across movimentacoes by worst manual-pathway alert.

    RULE-ALERTAS-002 (RATIFIED, UNVERIFIABLE).
    Counts beds/movimentacoes by worst manual-pathway alert among:
      (trilha_sepse, trilha_ventilacao, trilha_sedacao, trilha_estabilidade)
    with VERMELHO precedence.

    Args:
        movimentacao_alerts: List of 4-tuples (sepse, ventilacao, sedacao, estabilidade).
            Each element may be 'VERMELHO', 'AMARELO', 'NEUTRO', or None.

    Returns:
        Dict with counts keyed by {'VERMELHO', 'AMARELO', 'NEUTRO'}.

    Test vectors (from rule audit):
        [('VERMELHO','NEUTRO','AMARELO','NEUTRO')] -> {'VERMELHO':1,'AMARELO':0,'NEUTRO':0}
        [('NEUTRO','AMARELO','NEUTRO',None)] -> {'VERMELHO':0,'AMARELO':1,'NEUTRO':0}
        [(None,None,None,None)] -> {'VERMELHO':0,'AMARELO':0,'NEUTRO':1}
    """
    counts: dict[str, int] = {"VERMELHO": 0, "AMARELO": 0, "NEUTRO": 0}
    for alert_tuple in movimentacao_alerts:
        counts[_worst_alert_color(alert_tuple)] += 1
    return counts
