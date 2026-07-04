# RULE-MOVIMENTACAO-ADT-056 — Movimentacao requires patient unless it chains a prior movimentacao

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
Creating an initial bed movimentacao (admission) requires a paciente payload; a follow-up movimentacao created via the /nova/ endpoint against an ultima_movimentacao does not require paciente (it is inherited from the chain).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| paciente | object\|absent; required for initial POST |  |  |
| ultima_movimentacao | id\|empty; presence relaxes paciente requirement |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| http_status | int |  |

## Logic
```text
POST /leitos/{id}/movimentacoes/ without paciente            -> 400 (test_post_paciente_faltando)
POST /leitos/{id}/movimentacoes/ without paciente & no ultima -> 400 (test_post_sem_paciente_sem_ultima_movimentacao)
POST /leitos/{id}/movimentacoes/{ultima}/nova/ without paciente, with ultima -> 201 (test_post_sem_paciente_com_ultima_movimentacao)
```

## Edge cases (as implemented)
Initial admission must carry paciente; chained (nova) movimentacao inherits patient identity.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/tests/test_movimentacao.py` | 386-467 | `8166c07e` | primary |

- Merged from: RULE-VALIDATION-BE-12-025
- Related rules: RULE-MOVIMENTACAO-ADT-060, RULE-MOVIMENTACAO-ADT-035, RULE-MOVIMENTACAO-ADT-033

## Notes
Test-asserted behavioral contract. The initial "paciente required" side is implemented by PacienteValidation (RULE-060); the chained relaxation is a property of the /nova/ route (RULE-035, which forces paciente from the previous record). Kept as its own rule since the chained-relaxation nuance is not captured elsewhere.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
