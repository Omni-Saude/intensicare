# RULE-TRILHAS-ENGINE-001 — Automatic-bed pathway composition (v3 + v2 model sets)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Which automatic care-pathway models are evaluated for an automatic bed = the v3 set followed by the v2 set; several legacy v2 pathways are commented out.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| none (static composition) |  |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| pathway model list | list[Model] |  |

## Logic
```text
get_trilhas_automaticas() = get_trilhas_automaticas_v3() + get_trilhas_automaticas_v2()
v3 = [TrilhaSedacaoV3Model, TrilhaEficienciaV3Model, TrilhaEstabilidadeV3Model,
      TrilhaSepseV3Model, TrilhaProfilaxiaV3Model]
v2 = [TrilhaVentilacaoModel, TrilhaAntimicrobianoModel, TrilhaNutricaoModel,
      TrilhaEquilibrioModel, TrilhaGlozaZeroModel]
# commented out in v2: TrilhaSedacaoModel, TrilhaEstabilizacaoModel, TrilhaSEPSEModel, TrilhaProfilaxiasModel
```

## Edge cases (as implemented)
Order matters for first-match patient derivation (RULE-paciente-BE-04-020). v3 sedacao/estabilidade/sepse/profilaxia supersede their commented-out v2 equivalents.

## Divergence
v2/v3 duplication: get_trilhas_automaticas returns the v3 set plus the v2 set, but the v2 counterparts of sedacao / estabilizacao / sepse / profilaxias are commented out — leaving the v3 variants (TrilhaSedacaoV3, TrilhaEstabilidadeV3, TrilhaSepseV3, TrilhaProfilaxiaV3) canonical while their disabled v2 models still exist in trilha_automatica.models. Engineers must treat the v3 variants as canonical.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 134-163 | `8166c07e` | primary |

- Merged from: `RULE-trilha-BE-04-016`
- Related rules: RULE-TRILHAS-ENGINE-002, RULE-TRILHAS-ENGINE-003, RULE-TRILHAS-ENGINE-009, RULE-TRILHAS-ENGINE-010, RULE-TRILHAS-ENGINE-012

## Notes
Pathway models live in trilha_automatica.models (out of partition). v3 5-set mirrors the bootstrap set in RULE-TRILHAS-ENGINE-012 (AtualizarTrilhasV3).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
