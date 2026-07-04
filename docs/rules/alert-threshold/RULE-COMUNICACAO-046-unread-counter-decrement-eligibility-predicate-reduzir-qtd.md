# RULE-COMUNICACAO-046 — Unread-counter decrement eligibility predicate (reduzir_qtd)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule

Predicate that decides whether the per-user unread-alert/notification badge counter should be decremented. It returns True only when the observation, after the triggering change, has zero reactions, zero checked confirmations (checagens with checado=True), and zero other replies (excluding the given resposta pk). Gates send_qtd_mensagens_to_firebase(reduzir_qtd=True) from Reacao.save, the ChecagemObservacao serializer and the Observacao serializer.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| observacao | Observacao | - | reacoes / checagens / observacoes_respondidas |
| resposta | pk|null | - | reply excluded from the 'other replies' count |

## Outputs

| Name | Type | Unit |
|---|---|---|
| decrement? | bool | - |

## Logic

```text
def reduzir_qtd(observacao, resposta=None):
    return all([
        not observacao.reacoes.count(),
        not observacao.checagens.filter(checado=True).exists(),
        not observacao.observacoes_respondidas.exclude(pk=resposta).count(),
    ])
```

## Edge cases (as implemented)

All three conditions must hold (all([...])) for a True result. With resposta=None, exclude(pk=None) excludes nothing, so ANY existing reply blocks the decrement. checagens are only counted when checado=True (unchecked confirmations do not block). A True result means the observation has become fully un-engaged (no reactions, no checks, no other replies).

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/firebase.py` | 77-84 | `8166c07e` | primary |

- Merged from: RULE-gap6-05
- Related rules: RULE-COMUNICACAO-004, RULE-COMUNICACAO-037

## Notes

Only lines 19-75 of utils/firebase.py (RULE-COMUNICACAO-004, the counter fanout) were previously cited; this decrement-eligibility predicate itself was uncovered. It is the gate that decides when RULE-COMUNICACAO-004 is invoked with reduzir_qtd=True.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
