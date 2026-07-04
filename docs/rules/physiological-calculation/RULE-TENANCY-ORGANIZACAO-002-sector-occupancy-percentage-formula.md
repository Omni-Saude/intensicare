# RULE-TENANCY-ORGANIZACAO-002 — Sector occupancy percentage formula

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
SetorStatusSerializer.get_ocupacao computes bed occupancy percentage as (occupied active beds / total active beds) * 100, rounded to 2 decimals; returns integer 0 (division-by-zero guard) when there are no active beds.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| total_leitos | integer |  | >= 0 |
| total_leitos_ocupados | integer |  | >= 0 |

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
total_leitos == 0 returns int 0 (not float 0.0), a minor type inconsistency vs. the rounded-float branch. This exact formula/guard is duplicated in EstabelecimentoStatusSerializer.get_ocupacao (RULE-estabelecimento-BE-05-001).

## Verification
- Verdict: VERIFIED, impact: none
- Reference: WHO European Health Information Gateway, Bed Occupancy Rate (%); BOR = (occupied active beds / total active beds) x 100.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 142-148 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-006`
- Related rules: RULE-TENANCY-ORGANIZACAO-001

## Notes
Reconciliation: cross-hierarchy variant of the identical formula/guard at establishment scope (see related). Kept separate per variant-preservation rule; no divergence in the formula itself was found between the two levels.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
