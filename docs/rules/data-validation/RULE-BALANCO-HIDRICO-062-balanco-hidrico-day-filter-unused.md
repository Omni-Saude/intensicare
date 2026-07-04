# RULE-BALANCO-HIDRICO-062 — Balanco hidrico day filter (unused)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A FilterSet restricting BalancoHidrico queryset to an exact-match 'dia' (day) field exists but is not attached to any viewset (BalancoHidricoViewSet has its filter_class commented out).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| dia | date |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| filtered queryset | queryset |  |

## Logic

```text
class BalancoHidricoFilter(FilterSet):
    class Meta:
        model = BalancoHidrico
        fields = ("dia",)
```

## Edge cases (as implemented)

Not referenced by any view in scope; dead code as of this commit.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/filters/balanco_hidrico.py` | 6-9 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-filtro-BE-08-002`

**Related rules:**

- [RULE-BALANCO-HIDRICO-023](../physiological-calculation/RULE-BALANCO-HIDRICO-023-default-clinical-day-cutoff-07-00-for-balanco-hidrico.md)

## Notes

BalancoHidricoViewSet.get_queryset() implements its own day-cutoff logic manually (see RULE-BALANCO-HIDRICO-023, the 07:00 clinical-day default from RULE-balanco-BE-08-005) instead of using this filter. Routed here from cadastros-ui: fluid-balance domain logic (and dead/unwired code), not a registration/CRUD concern.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
