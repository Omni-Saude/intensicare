# RULE-SEPSE-083 — Interactive sepsis trail filtered by bed

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
TrilhaInterativaViewSet.get_queryset returns TrilhaSepseV3Model rows whose leito matches the 'ocupacoes__pk' URL kwarg directly (treated as a Leito pk).

## Inputs

- kwargs.ocupacoes__pk (uuid)

## Outputs

- queryset (queryset of TrilhaSepseV3Model)

## Logic

```text
return TrilhaSepseV3Model.objects.filter(leito=kwargs.get("ocupacoes__pk"))
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/trilha_interativa.py` | 19-20 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-trilhainterativa-BE-05-001`

**Related rules:**

- [RULE-SEPSE-071](RULE-SEPSE-071-sepse-v3-interactive-protocol-creation-gate-can-criar-novo-p.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
