# RULE-EVOLUCOES-047 — Previous-form-indicators carry-forward endpoint

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
For any evolution-form route, a dedicated endpoint retrieves the "anterior_indicadores" (previous indicators) for the same bed occupation, allowing a new form entry to reference/pre-populate values from the most recent prior submission of the same form type for that patient encounter.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| route |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| previous indicators |  |  |

## Logic
```text
GET empresas/{idEmpresa}/estabelecimentos/{idEstabelecimento}/setores/{idSetor}
    /ocupacoes/{idOcupacao}/{route}/anterior_indicadores/
```

## Edge cases (as implemented)
Return type is untyped (`any`) in this partition; actual merge/pre-fill behavior into the new form is not present here.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/networking/evolucao.ts` | 48-68 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-07-003
- Related rules: RULE-EVOLUCOES-029

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
