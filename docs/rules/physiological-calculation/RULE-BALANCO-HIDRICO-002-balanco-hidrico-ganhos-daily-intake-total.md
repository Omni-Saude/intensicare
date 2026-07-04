# RULE-BALANCO-HIDRICO-002 — Balanco Hidrico ganhos (daily intake total)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Total fluid intake for this balance day = sum of non-deleted entrada quantities.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| entradas.quantidade | — | mL | this balance, deletado_em is null |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ganhos | — | mL |

## Logic
```text
entradas_qs = self.entradas.filter(deletado_em__isnull=True)
entradas = entradas_qs.aggregate(total=Sum("quantidade")).get("total", 0) if entradas_qs.exists() else 0
return entradas or 0
```

## Edge cases (as implemented)
Returns 0 when no entries. `or 0` coerces a None Sum to 0.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: ADQI/Malbrain 2014 fluid-balance framework: daily fluid intake (gains) = sum of all recorded intake volumes over the accounting period. Elementary aggregation. (https://pmc.ncbi.nlm.nih.gov/articles/PMC10133509/)
- Test vectors: 3/3 match
- Trivial summation of intake volumes; matches the "total intake" component of fluid balance. The
`or 0` idiom correctly coerces a None Sum (all-null quantidade) to 0, so this helper is robust where
RULE-001 is not. No unit or coefficient concerns (single homogeneous mL field). Confirmed at
balanco.py:61-71.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/balanco.py | 61-71 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-002
- Related rules: RULE-BALANCO-HIDRICO-001, RULE-BALANCO-HIDRICO-003, RULE-BALANCO-HIDRICO-007, RULE-BALANCO-HIDRICO-014

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
