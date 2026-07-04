# RULE-OPERACIONAL-INFRA-054 — UniqueManagerMixin.save — single-field uniqueness excluding soft-deleted rows

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Before saving, for each field name in a model's `Unique.value`, checks independently (not combined) whether another non-deleted row has the same value for that field (excluding self by pk); raises ValidationError if so, unless an `except_has` bypass condition matches.

## Inputs

| name | type | unit |
|---|---|---|
| self.Unique.value | tuple of field names, each checked independently |  |
| self.Unique.except_has | tuple of (key) or (key, value) bypass conditions |  |

## Outputs

| name | type | unit |
|---|---|---|
| validity | raises ValidationError otherwise |  |

## Logic

```text
FOR param IN self.Unique.value:
  value = getattr(self, param, None)
  IF value:
    qs = Klass.objects.filter(~Q(pk=self.get_pk), Q(deletado_em__isnull=True), Q(**{param: value}))
    FOR except_param IN except_has:
      (key, value) = except_param if tuple/list else (except_param, None)
      IF getattr(self, key) == value (when value given): qs = Klass.objects.none(); BREAK
    IF qs.exists(): RAISE ValidationError(message OR default "O campo <param> deve ser único")
```

## Edge cases (as implemented)

A falsy field value (None/empty) is simply never checked for uniqueness (silently skipped), unlike UniqueTogetherManagerMixin where a falsy field skips the WHOLE combo — here each field is independent so only that one field's check is skipped.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/models.py` | 116-157 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-model-BE-11-056`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-053](RULE-OPERACIONAL-INFRA-053-uniquetogethermanagermixin-save-composite-uniqueness-excludi.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
