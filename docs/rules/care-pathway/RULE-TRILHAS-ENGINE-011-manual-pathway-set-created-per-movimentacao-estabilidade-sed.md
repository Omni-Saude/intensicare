# RULE-TRILHAS-ENGINE-011 — Manual pathway set created per movimentacao (Estabilidade/Sedacao/Sepse/Ventilacao)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Each prontuario (dados_prontuario) spawns exactly four manual care pathways — TrilhaEstabilidade, TrilhaSedacao, TrilhaSepse, TrilhaVentilacao — created in order.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dados_prontuario | DadosProntuario |  | may include noradrenalina, sedativos, ventilacao_mecanica, parada_cardiorrespiratoria, labs, etc. |

## Outputs

| Name | Type | Unit |
|---|---|---|
| 4 pathway rows (trilha_estabilidade/trilha_sedacao/trilha_sepse/trilha_ventilacao) | side-effect |  |

## Logic
```text
trilhas = [TrilhaEstabilidade, TrilhaSedacao, TrilhaSepse, TrilhaVentilacao]
for trilha in trilhas: trilha.objects.create(dados_prontuario=dados_prontuario)
  on ValidationError -> raise {"<trilha>": "Ocorreu um erro na criação da <trilha>: ..."}
# Effect confirmed by test: after create, movimentacao.dados_prontuario has attributes
#   trilha_estabilidade, trilha_sedacao, trilha_sepse, trilha_ventilacao
#   (plus stored noradrenalina, parada_cardiorrespiratoria, sedativos, ventilacao_mecanica)
```

## Edge cases (as implemented)
Antimicrobiano/Nutricao/Equilibrio/etc are NOT created here (those are automatic-bed pathways). Ordered creation. Trilhas are generated even from a minimal prontuario; each movimentacao gets its own prontuario/trilhas (a chained movimentacao's prontuario differs from the prior one).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/trilhas/criar_trilhas.py` | 24-38 | `8166c07e` | primary |
| ahlabs-trilhas | `core/tests/test_movimentacao.py` | 155-165,288-295 | `8166c07e` | duplicate |

- Merged from: `RULE-trilha-BE-04-039`, `RULE-CAREPATH-BE-12-028`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-012

## Notes
Merge of the use_case code (criar_trilhas.py, primary) and the test that observes its effect (test_movimentacao.py). Confirmed same four pathways, same order. Pathway models live in trilha_manual.models. Terminology note: the test/Phase-1 label called these "automatic ICU pathways" but the code creates the MANUAL set (trilha_manual.models) via the CriarTrilhas use case — no logic divergence, only loose naming.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
