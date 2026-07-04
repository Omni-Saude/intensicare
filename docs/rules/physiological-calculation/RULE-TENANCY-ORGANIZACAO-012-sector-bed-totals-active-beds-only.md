# RULE-TENANCY-ORGANIZACAO-012 — Sector bed totals (active beds only)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
SetorSerializer.get_leitos returns the total count of active (ativo=True) beds in the sector and, of those, how many are currently occupied.

## Inputs

| Name | Type | Unit |
|---|---|---|
| obj | Setor |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total | integer |  |
| ocupados | integer |  |

## Logic

```text
queryset = Leito.objects.filter(setor=obj, ativo=True)
return {"total": queryset.count(), "ocupados": queryset.filter(ocupado=True).count()}
```

## Edge cases (as implemented)
'ocupados' is a strict subset of 'total' since it filters the already ativo=True queryset - unlike the analogous SetorStatusSerializer methods (RULE-setor-BE-05-007), there is no ativo mismatch here.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal/proprietary business logic: SetorSerializer.get_leitos counts active beds (ativo=True) and the occupied subset (ocupado=True) within that active set. This is bed-inventory bookkeeping, not a clinical calculator; general ICU-occupancy definition (occupied/available beds) is the only conceptual anchor and it is not a coefficient/cutoff-bearing published equation.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 81-92 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-004`
- Related rules: RULE-TENANCY-ORGANIZACAO-002, RULE-TENANCY-ORGANIZACAO-004

## Notes
Reconciliation: distinct from the SetorStatusSerializer bed-count methods (RULE-TENANCY-ORGANIZACAO for setor-BE-05-006/007) which use the same ativo/ocupado filters but live in a different serializer class and (in the -007 case) drop the ativo constraint from the numerator. This SetorSerializer.get_leitos method scopes both total and ocupados to ativo=True consistently (no discrepancy here).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
