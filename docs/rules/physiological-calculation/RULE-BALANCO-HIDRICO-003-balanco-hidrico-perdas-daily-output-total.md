# RULE-BALANCO-HIDRICO-003 — Balanco Hidrico perdas (daily output total)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Total fluid output for this balance day = sum of non-deleted saida quantities.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| saidas.quantidade | — | mL | this balance, deletado_em is null |

## Outputs
| Name | Type | Unit |
|---|---|---|
| perdas | — | mL |

## Logic
```text
saidas_qs = self.saidas.filter(deletado_em__isnull=True)
saidas = saidas_qs.aggregate(total=Sum("quantidade")).get("total", 0) if saidas_qs.exists() else 0
return saidas or 0
```

## Edge cases (as implemented)
Returns 0 when no outputs. `or 0` coerces a None Sum to 0.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: ADQI/Malbrain 2014 fluid-balance framework: daily fluid output (losses) = sum of all recorded output volumes over the accounting period. Elementary aggregation. (https://pmc.ncbi.nlm.nih.gov/articles/PMC10133509/)
- Test vectors: 3/3 match
- Mirror of RULE-002 for outputs; matches the "total output" component of the standard definition.
Applies NO tipo filter (all outputs counted), correct for a gross output total. `or 0` handles the
empty/None case robustly. Confirmed at balanco.py:73-85.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/balanco.py | 73-85 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-003
- Related rules: RULE-BALANCO-HIDRICO-001, RULE-BALANCO-HIDRICO-002, RULE-BALANCO-HIDRICO-015

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
