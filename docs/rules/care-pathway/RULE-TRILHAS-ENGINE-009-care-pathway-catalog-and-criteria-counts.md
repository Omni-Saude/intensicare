# RULE-TRILHAS-ENGINE-009 — Care-pathway catalog and criteria counts

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
The platform defines nine automatic care pathways (trilhas), each bound to a v3 Tasy source model, a local target model, and a fixed number of clinical criteria (quantidade_criterios) that drives pathway evaluation/completion in the shared novo_etl_schema engine.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha_number | integer |  | 1-9 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| quantidade_criterios | integer |  |

## Logic
```text
novo_etl_schema(TrilhaSedacaoTasyModel,        TrilhaSedacaoModel,        quantidade_criterios=12)  # Trilha 1 - Sedacao
novo_etl_schema(TrilhaEstabilizacaoTasyModel,  TrilhaEstabilizacaoModel,  quantidade_criterios=6)   # Trilha 2 - Estabilizacao
novo_etl_schema(TrilhaVentilacaoTasyModel,     TrilhaVentilacaoModel,     quantidade_criterios=10)  # Trilha 3 - Ventilacao
novo_etl_schema(TrilhaSEPSETasyModel,          TrilhaSEPSEModel,          quantidade_criterios=10)  # Trilha 4 - SEPSE
novo_etl_schema(TrilhaAntimicrobianoTasyModel, TrilhaAntimicrobianoModel, quantidade_criterios=14)  # Trilha 5 - Antimicrobiano
novo_etl_schema(TrilhaNutricaoTasyModel,       TrilhaNutricaoModel,       quantidade_criterios=10)  # Trilha 6 - Nutricao
novo_etl_schema(TrilhaEquilibrioTasyModel,     TrilhaEquilibrioModel,     quantidade_criterios=10)  # Trilha 7 - Equilibrio (balanco hidrico)
novo_etl_schema(TrilhaProfilaxiasTasyModel,    TrilhaProfilaxiasModel,    quantidade_criterios=11)  # Trilha 8 - Profilaxias
novo_etl_schema(TrilhaGlozaZeroTasyModel,      TrilhaGlozaZeroModel,      quantidade_criterios=16)  # Trilha 9 - Glosa Zero
```

## Edge cases (as implemented)
quantidade_criterios is consumed by novo_etl_schema (module `utils`, OUTSIDE this partition) which contains the actual per-criterion scoring/aggregation logic; the counts here are the contract only.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/etl/trilha5.py` | 1-8 | `8166c07e` | primary |

- Merged from: `RULE-trilha-BE-02-006`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-010

## Notes
One rule per file: trilha1.py:15 (12), trilha2.py:7 (6), trilha3.py:7 (10), trilha4.py:7 (10), trilha5.py:7 (14), trilha6.py:7 (10), trilha7.py:7 (10), trilha8.py:7 (11), trilha9.py:7 (16). VERSION VARIANTS: commented-out legacy calls use the old etl_schema with different counts (trilha1 v1=6, trilha3 v1=7, trilha4 v1=6, trilha6 v1=6, trilha7 v1=7, trilha8 v1=6). The active code uses the "novo"/v3 models with the counts above. Verify criterion definitions in utils.novo_etl_schema.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
