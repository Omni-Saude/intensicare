# RULE-COMUNICACAO-006 — Firebase unread-count decrement when an observation checagem is checked off

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
When a ChecagemObservacao is updated and its 'checado' field becomes truthy, and reduzir_qtd(observacao) confirms the shared unread-count was decremented, a Firebase update is pushed asynchronously to zero out the pending/unread flags for the observation's setor+responsavel.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| validated_data.checado | boolean | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| firebase_update | async task call | — |

## Logic
```text
instance = super().update(instance, validated_data)
observacao = instance.observacao
if validated_data.get("checado") and reduzir_qtd(observacao):
    send_qtd_mensagens_to_firebase.apply_async(
        args=[observacao.setor.get_pk, observacao.responsavel.get_pk, False, True]
    )
return instance
```

## Edge cases (as implemented)
If checado is falsy in this update call, or reduzir_qtd returns falsy, no Firebase call is made.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/checagem_observacao.py | 28-43 | 8166c07e | primary |
- Merged from: RULE-checagem-BE-05-001
- Related rules: RULE-COMUNICACAO-004, RULE-COMUNICACAO-005, RULE-COMUNICACAO-033, RULE-COMUNICACAO-014

## Notes
reduzir_qtd/send_qtd_mensagens_to_firebase implementations are in utils.firebase, out of scope; the extra two positional args (False, True) vs. the 2-arg call in RULE-observacao-BE-05-004 suggest a different call signature/overload - flagged for a verifier to confirm against utils.firebase source.

---

RECONCILED: verified against utils/firebase.py — send_qtd_mensagens_to_firebase's real signature is (setor, usuario_pk, is_reacao=False, reduzir_qtd=False). The apply_async(args=[setor_pk, responsavel_pk, False, True]) call here maps positionally to is_reacao=False, reduzir_qtd=True — the SAME function/signature as RULE-COMUNICACAO-004 and RULE-COMUNICACAO-007's 2-arg calls, just invoked with different trailing arguments for a different scenario. The 'different call signature/overload' concern flagged by Phase-1 is resolved: there is only one function, called with 2, 3, or 4 positional args depending on branch — no discrepancy.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
