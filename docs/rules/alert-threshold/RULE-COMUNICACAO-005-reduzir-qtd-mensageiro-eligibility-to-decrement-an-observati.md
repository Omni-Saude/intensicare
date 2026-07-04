# RULE-COMUNICACAO-005 — reduzir_qtd (mensageiro) — eligibility to decrement an observation's unread badge

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
An observation's unread-count contribution is only eligible to be decremented if it has NO reactions, NO checked confirmations (checagens with checado=True), and NO other replies to it (excluding a given reply pk).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| observacao | Observacao instance | — | — |
| resposta | pk of a reply to exclude from the check | — | optional, default None |

## Outputs
| Name | Type | Unit |
|---|---|---|
| pode_reduzir | boolean | — |

## Logic
```text
RETURN ALL([
  observacao.reacoes.count() == 0,
  NOT observacao.checagens.filter(checado=True).exists(),
  observacao.observacoes_respondidas.exclude(pk=resposta).count() == 0,
])
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/mensageiro.py | 77-84 | 8166c07e | primary |
- Merged from: RULE-msg-BE-11-046
- Related rules: RULE-COMUNICACAO-004, RULE-COMUNICACAO-006, RULE-COMUNICACAO-007, RULE-COMUNICACAO-037

## Notes
Function name is identical to the `reduzir_qtd` PARAMETER of send_qtd_mensagens_to_firebase (RULE-msg-BE-11-045) but they are different things: this one COMPUTES eligibility, that one CONSUMES a boolean flag with that name. Not shown in this partition is the call site that feeds this function's result into that parameter.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
