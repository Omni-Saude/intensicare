# RULE-MOVIMENTACAO-ADT-053 — Invasive-procedure type enumeration (10 values)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Invasive procedures tracked per bed occupancy are restricted to a fixed catalog of 10 procedure types spanning central-venous-catheter placements (mono/duplo/triplo lumen; by puncture or for hemodialysis; or portocath), airway procedures (orotracheal intubation, tracheostomy), and indwelling urinary catheterization (2-way or 3-way).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | string enum, 10 literal values |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| tipo | string enum |  |

## Logic
```text
ProcedimentoInvasivoTipo =
  puncao_de_acesso_venoso_central_mono_lumen |
  puncao_de_acesso_venoso_central_duplo_lumen |
  puncao_de_acesso_venoso_central_triplo_lumen |
  implante_de_cateter_venoso_central_por_puncao_cvc |
  implante_de_cateter_venoso_central_para_hemodialise |
  colocacao_de_cateter_venoso_central_ou_portocath |
  intubacao_orotraqueal |
  traqueostomia |
  passagem_de_sonda_vesical_de_demora_2_vias |
  passagem_de_sonda_vesical_de_demora_3_vias
```

## Edge cases (as implemented)
None beyond the closed 10-value set; each ProcedimentoInvasivo also carries a free-text "nome" alongside the constrained "tipo".

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Ocupacao.d.ts` | 35-45 | `f9656be2` | primary |

- Merged from: RULE-ocupacao-FE-07-003
- Related rules: RULE-MOVIMENTACAO-ADT-016

## Notes
One enum value ("colocacao_de_cateter_venoso_central_ou_portocath") contains diacritics (cedilla, tilde) in the source while sibling literals use ASCII-only snake_case - an inconsistent naming convention recorded verbatim.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
