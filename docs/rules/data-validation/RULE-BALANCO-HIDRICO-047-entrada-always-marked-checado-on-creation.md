# RULE-BALANCO-HIDRICO-047 — Entrada always marked checado on creation

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
Every Entrada created through this serializer is forced to checado=True regardless of client input, and preenchido_por is always set to the requesting user.

## Inputs

- checado

## Outputs

- checado

## Logic

```text
validated_data.checado = True
validated_data.preenchido_por = request.user
```

## Edge cases (as implemented)

No client-supplied checado value can override this; there is no equivalent forced-True in SinaisVitais.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/entradas.py` | 92-93 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-07-005`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
