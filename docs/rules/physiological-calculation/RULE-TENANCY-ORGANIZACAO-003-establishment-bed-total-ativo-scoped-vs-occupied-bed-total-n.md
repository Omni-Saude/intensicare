# RULE-TENANCY-ORGANIZACAO-003 — Establishment bed total (ativo-scoped) vs occupied-bed total (no ativo scoping)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
get_total_leitos requires both setor.usuarios=request.user AND leitos.ativo=True (denominator); get_total_leitos_ocupados requires setor.usuarios=request.user AND leitos.ocupado=True but NOT ativo=True (numerator) - an inactive-but-occupied bed inflates occupancy above what the denominator accounts for, mirroring the same asymmetry found at the sector level.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.setores | related manager of Setor |  |
| request.user | object |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_leitos | integer |  |
| total_leitos_ocupados | integer |  |

## Logic

```text
def get_total_leitos(instance):
    return instance.setores.filter(usuarios=request.user, leitos__ativo=True).aggregate(total_leitos=Count("leitos")).get("total_leitos", 0)
def get_total_leitos_ocupados(instance):
    return instance.setores.filter(leitos__ocupado=True, usuarios=request.user).aggregate(total_leitos_ocupados=Count("leitos")).get("total_leitos_ocupados", 0)
```

## Edge cases (as implemented)
Both are scoped to setores where request.user is a member (setor.usuarios=user), unlike the analogous Setor-level methods which operate directly on a single already-resolved Setor instance.

## Verification
- Verdict: DISCREPANCY, impact: low
- Reference: WHO / standard BOR definition: occupied beds is a strict subset of available beds, therefore BOR is bounded at <=100%. PA Dept. of Health "Occupancy Rates in Health Facilities" states the numerator (occupied) must be drawn from the same available-bed denominator.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 95-112 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-002`
- Related rules: RULE-TENANCY-ORGANIZACAO-004

## Notes
Cross-reference RULE-setor-BE-05-007 for the identical inconsistency pattern at sector scope. | Reconciliation: identical ativo-scoping asymmetry pattern also present at sector scope (see related, status also DISCREPANCY there). Kept as separate rules (different entity/queryset), not merged.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
