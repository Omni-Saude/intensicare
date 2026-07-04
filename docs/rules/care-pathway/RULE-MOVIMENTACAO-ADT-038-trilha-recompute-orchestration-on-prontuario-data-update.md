# RULE-MOVIMENTACAO-ADT-038 — Trilha recompute orchestration on prontuario data update

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Saving prontuario data re-saves all four pathways (each recomputes its criteria) then re-aggregates the bed alert.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dados_prontuario | DadosProntuario |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| recomputed trilhas + bed alert | side-effect |  |

## Logic
```text
atualizar_trilhas():
  trilha_sedacao.save(); trilha_estabilidade.save(); trilha_ventilacao.save(); trilha_sepse.save()
  atualizar_alerta_movimentacao(str(movimentacao.pk))
```

## Edge cases (as implemented)
Ordering - sedacao, estabilidade, ventilacao, sepse, then aggregation. SOFA is NOT re-saved here (recomputed only on its own save).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 205-212 | `8166c07e` | primary |

- Merged from: RULE-mov-BE-10-062
- Related rules: RULE-MOVIMENTACAO-ADT-012, RULE-MOVIMENTACAO-ADT-040

## Notes
Invoked by OcupacaoViewSet.retrieve (ocupacoes.py:103) before building the payload.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
