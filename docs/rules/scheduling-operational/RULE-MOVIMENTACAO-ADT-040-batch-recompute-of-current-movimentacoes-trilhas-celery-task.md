# RULE-MOVIMENTACAO-ADT-040 — Batch recompute of current movimentacoes' trilhas (Celery task)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Celery task recomputes all manual pathways for current (atual=True) movimentacoes and then all automatic/homecare trilhas.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| Movimentacao.filter | atual=True) (queryset |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| side-effect | saved trilhas + alerts |  |

## Logic
```text
manuais: ids = current movimentacoes; for Trilha in [Sepse,Sedacao,Estabilidade,Ventilacao]:
           for t in Trilha.filter(dados_prontuario__in=ids): t.save()
         for id in ids: atualizar_alerta_movimentacao(id)
automaticas: for Trilha in Leito.get_trilhas_automaticas_v2(): resave all; then resave leitos tipo in [automatica,homecare]
```

## Edge cases (as implemented)
Runs as shared_task with exchange 'trilhas'; routing key prefixed by ENVIRONMENT env var.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/tasks.py` | 18-61 | `8166c07e` | primary |

- Merged from: RULE-op-BE-10-066
- Related rules: RULE-MOVIMENTACAO-ADT-038, RULE-MOVIMENTACAO-ADT-012

## Notes
SOFA is not resaved in the manual loop (only the 4 trilhas), so escore_sofa can lag unless the prontuario is saved.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
