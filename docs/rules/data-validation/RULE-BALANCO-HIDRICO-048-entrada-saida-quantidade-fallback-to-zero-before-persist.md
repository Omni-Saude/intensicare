# RULE-BALANCO-HIDRICO-048 — Entrada/Saida quantidade fallback to zero before persist

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
If, after the dieta_enteral default is applied, quantidade is still falsy, it is forced to 0 before persisting (so the field is never null/blank in storage).

## Inputs

- quantidade (mL (assumed))

## Outputs

- quantidade (mL (assumed))

## Logic

```text
if not validated_data.quantidade:
    validated_data.quantidade = 0
```

## Edge cases (as implemented)

Runs after the dieta_enteral-specific default, so it only affects other tipos.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/entradas.py` | 98-99 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/saidas.py` | 109-110 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-07-002`
- `RULE-balanco-BE-07-010`

**Related rules:**

- [RULE-BALANCO-HIDRICO-020](../physiological-calculation/RULE-BALANCO-HIDRICO-020-default-volume-for-enteral-diet-intake-entry.md)

## Notes

Same pattern duplicated in saidas.py (RULE-balanco-BE-07-010).
Identical validation in entradas.py:98-99 and saidas.py:109-110: `if not validated_data.quantidade: validated_data.quantidade = 0`. Runs AFTER the type-specific volume defaults (dieta_enteral=200 for Entrada; presenca_espontanea/presenca mappings for Saida), so it only affects tipos without a specific default. No divergence -> OK.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
