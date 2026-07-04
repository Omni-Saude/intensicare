# RULE-OPERACIONAL-INFRA-037 — ListChoiceField.to_representation — context-dependent representation switch

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A DRF ChoiceField subclass whose representation behavior depends on whether the serializer was instantiated WITH a context: if there is NO context, values are mapped through the choices dict directly (handling both list-of-values and single-value cases); if there IS a context, it defers entirely to the standard DRF ChoiceField.to_representation.

## Inputs

| name | type | unit |
|---|---|---|
| obj | value or list of values |  |

## Outputs

| name | type | unit |
|---|---|---|
| representation | mapped label(s) or standard DRF representation |  |

## Logic

```text
to_representation(obj):
  IF NOT self.context:
    IF obj:
      IF isinstance(obj, list):
        RETURN [self.choices.get(v) FOR v IN obj]
      ELSE:
        RETURN self.choices.get(obj)
    # implicit: returns None if obj is falsy and there's no context
  ELSE:
    RETURN super().to_representation(obj)
```

## Edge cases (as implemented)

If context is falsy AND obj is falsy, the function implicitly returns None (no explicit return statement executed).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/serializer.py` | 4-16 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ser-BE-11-071`

**Related rules:** _none_

## Notes

AMBIGUOUS: the intent of switching representation strictly on context PRESENCE (not on any specific context key/value) is not evident from this file alone; likely used to render human-readable labels in one serialization path (e.g. admin/read views without request context) vs raw values in another (e.g. API responses with request context). Flag for verifier with visibility into call sites (out of BE-11 scope).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
