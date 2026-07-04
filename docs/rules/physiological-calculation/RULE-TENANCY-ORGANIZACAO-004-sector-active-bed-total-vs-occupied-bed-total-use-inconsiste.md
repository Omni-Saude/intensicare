# RULE-TENANCY-ORGANIZACAO-004 — Sector active-bed total vs. occupied-bed total use inconsistent ativo scoping

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
get_total_leitos filters leitos.filter(ativo=True) (the occupancy-percentage denominator), but get_total_leitos_ocupados filters leitos.filter(ocupado=True) with NO ativo constraint (the numerator). If any leito has ocupado=True but ativo=False, it inflates the numerator without being counted in the denominator, which can push the RULE-setor-BE-05-006 occupancy percentage above 100%.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.leitos | related manager of Leito |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_leitos | integer |  |
| total_leitos_ocupados | integer |  |

## Logic

```text
def get_total_leitos(instance):
    return instance.leitos.filter(ativo=True).count()
def get_total_leitos_ocupados(instance):
    return instance.leitos.filter(ocupado=True).count()   # no ativo=True filter
```

## Edge cases (as implemented)
Only manifests when an inactive bed is simultaneously marked ocupado=True; whether that combination is reachable in practice depends on Leito's own state-transition rules (out of this partition's scope).

## Verification
- Verdict: DISCREPANCY, impact: low
- Reference: WHO / standard BOR: occupied beds subset of available beds, BOR <=100%. Same authority as RULE-003.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 150-156 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-007`
- Related rules: RULE-TENANCY-ORGANIZACAO-003

## Notes
Identical asymmetry pattern also present in EstabelecimentoStatusSerializer (RULE-estabelecimento-BE-05-002) - both should be checked together by a verifier. | Reconciliation: identical ativo-scoping asymmetry pattern also present at establishment scope (see related, status also DISCREPANCY there). Kept as separate rules (different entity/queryset), not merged.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
