# RULE-TENANCY-ORGANIZACAO-016 — Processing-mode (tipo) enumeration for company/bed/sector/establishment

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The `tipo` field ("manual"/"automatica"/"homecare"/"") selects which pathway engine and alert logic apply to a bed/sector/establishment/company.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | string |  | manual\|automatica\|homecare\|'' (Não informado) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| processing_mode | string |  |

## Logic

```text
EmpresaChoices.tipo() -> (manual, automatica, homecare, "").
Downstream branching (Leito.save / get_alerta_leito / get_paciente_instance):
  tipo=="automatica" -> use automatic pathway set + alerta_nao_assistido_automatico
  tipo=="homecare"   -> use homecare pathway set + alerta_nao_assistido_homecare
  tipo=="manual"     -> alerta computed from stored movimentacao trilhas (no auto engine)
Defaults: Estabelecimento/Setor/Leito default "manual"; Empresa.tipo default "".
```

## Edge cases (as implemented)
get_alerta_leito raises ValidationError for any tipo other than homecare/automatica when computing bed alert; get_trilha raises "Tipo de leito inválido" for tipo not in {automatica,homecare}.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/choices/empresa.py` | 14-21 | `8166c07e` | primary |

- Merged from: `RULE-empresa-BE-04-003`
- Related rules: RULE-TENANCY-ORGANIZACAO-025, RULE-TENANCY-ORGANIZACAO-026, RULE-TENANCY-ORGANIZACAO-027, RULE-TENANCY-ORGANIZACAO-028, RULE-TENANCY-ORGANIZACAO-029, RULE-TENANCY-ORGANIZACAO-030, RULE-TENANCY-ORGANIZACAO-034, RULE-TENANCY-ORGANIZACAO-035, RULE-TENANCY-ORGANIZACAO-036, RULE-TENANCY-ORGANIZACAO-038

## Notes
Leito.tipo reuses EmpresaChoices.tipo but max_length=64; Estabelecimento/Setor use max_length=65. Same enum reused across four models.
 | Reconciliation: this is the single canonical definition of the shared `tipo` enum and its downstream engine-selection semantics; all tipo-branching decision rules elsewhere in this cluster (FE gating rules, estabelecimento/setor tipo-branch formulas) are separate rules that consume this enum and are cross-referenced here rather than merged, since each implements a distinct decision (different button, different aggregation) rather than restating this same enum definition.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
