# RULE-MOVIMENTACAO-ADT-052 — Bed/company monitoring-modality enumeration (manual|automatica|homecare)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Each bed (Ocupacao.Filter.tipo, Ocupacao.Leito.tipo) and each company (Usuario.Empresa.tipo) is classified into exactly one of three care/monitoring modalities - manual data entry, automatic (device-integrated) monitoring, or homecare.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | string enum: manual \| automatica \| homecare |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| tipo | string enum |  |

## Logic
```text
LeitoTipo = "manual" | "automatica" | "homecare"
```

## Edge cases (as implemented)
None beyond the closed 3-value set.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Ocupacao.d.ts` | 107-107 | `f9656be2` | primary |

- Merged from: RULE-ocupacao-FE-07-002
- Related rules: RULE-MOVIMENTACAO-ADT-026, RULE-MOVIMENTACAO-ADT-021, RULE-MOVIMENTACAO-ADT-018

## Notes
Identical literal union independently redeclared at Models.Usuario.Empresa.tipo (src/@types/models/User.d.ts line 31, RULE-usuario-FE-07-002 out of cluster). Also referenced by the dedicated homecare feed endpoint.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
