# RULE-TENANCY-ORGANIZACAO-001 — Establishment occupancy percentage formula

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
EstabelecimentoStatusSerializer.get_ocupacao computes bed occupancy percentage as (occupied beds / total beds) * 100 rounded to 2 decimals across all the establishment's sectors the user belongs to; returns int 0 if there are no beds.

## Inputs

| Name | Type | Unit |
|---|---|---|
| total_leitos | integer |  |
| total_leitos_ocupados | integer |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| ocupacao | float \| integer | % |

## Logic

```text
total_leitos = self.get_total_leitos(instance)
return round((self.get_total_leitos_ocupados(instance) / total_leitos) * 100, 2) if total_leitos else 0
```

## Edge cases (as implemented)
Same 0-guard int/float type inconsistency as RULE-setor-BE-05-006.

## Verification
- Verdict: VERIFIED, impact: none
- Reference: WHO European Health Information Gateway, "Bed occupancy rate (%), acute care hospitals only"; standard Bed Occupancy Rate (BOR) = (occupied beds / available beds) x 100. Point-prevalence form corroborated by PA Dept. of Health "Occupancy Rates in Health Facilities".

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 87-93 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-001`
- Related rules: RULE-TENANCY-ORGANIZACAO-002

## Notes
Identical formula duplicated at sector level (RULE-setor-BE-05-006). | Reconciliation: cross-hierarchy variant of the identical formula/guard at sector scope (see related). No merge performed — establishment- and sector-level occupancy are distinct computed values over different querysets, per the audit's variant-preservation rule; kept as separate rules, cross-referenced.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
