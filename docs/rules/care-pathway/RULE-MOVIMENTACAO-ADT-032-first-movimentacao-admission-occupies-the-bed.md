# RULE-MOVIMENTACAO-ADT-032 — First movimentacao - admission occupies the bed

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
First admission creates the prontuario and optional clinical sub-records, assembles the SOFA score inputs, marks the bed occupied, then creates pathways and updates the alert.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dados_prontuario | dict, may include noradrenalina/parada/sedativos/ventilacao |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| DadosProntuario + SOFA + occupied bed + trilhas | side-effect |  |

## Logic
```text
order: get_atributos -> create DadosProntuario (serializer)
  -> if noradrenalina: create; if parada: create; for each sedativo: create; if ventilacao: create
  -> __criar_escore_sofa
  -> alterar_status_leito: leito.ocupado=True; save   (triggers Leito.save alert recompute)
  -> CriarTrilhas(prontuario) -> atualizar_alerta_movimentacao(movimentacao.pk)
```

## Edge cases (as implemented)
Sub-records created only if truthy payload present. Bed occupancy set BEFORE pathway/alert creation.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/use_cases/movimentacao/cadastrar_primeira_movimentacao.py | 50-168 | 8166c07e | primary |
- Merged from: RULE-movimentacao-BE-04-037
- Related rules: RULE-MOVIMENTACAO-ADT-031, RULE-MOVIMENTACAO-ADT-033, RULE-MOVIMENTACAO-ADT-025

## Notes
SOFA scoring (__criar_escore_sofa) runs out of partition. The occupy-on-admission behavior is also asserted by test_movimentacao.py:537-558 (see RULE-031).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
