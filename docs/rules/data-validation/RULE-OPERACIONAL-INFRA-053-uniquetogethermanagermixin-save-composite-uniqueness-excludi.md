# RULE-OPERACIONAL-INFRA-053 — UniqueTogetherManagerMixin.save — composite uniqueness excluding soft-deleted rows

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
Before saving, for each unique-together field-combo declared in a model's `UniqueTogether.value` (which may be a single flat tuple of field names, or a tuple of such tuples for multiple constraints — depth-detected), builds a Q-filter requiring ALL present (truthy) field values to match, excludes the current row (by pk) and soft-deleted rows (deletado_em__isnull=True); if an `except_has` condition (key or key/value pair) matches the current instance, the check is bypassed entirely for that combo. If a matching non-deleted row exists for a combo where every field produced a truthy filter value, raises ValidationError with a default or custom message.

## Inputs

| name | type | unit |
|---|---|---|
| self.UniqueTogether.value | tuple of field names, or tuple of tuples |  |
| self.UniqueTogether.except_has | tuple of (key) or (key, value) bypass conditions |  |

## Outputs

| name | type | unit |
|---|---|---|
| validity | raises ValidationError otherwise |  |

## Logic

```text
FOR unique IN (UniqueTogether.value if nested else [UniqueTogether.value]):
  args_to_check = []
  FOR param IN unique:
    value = getattr(self, param, None)
    IF value: args_to_check.append(Q(**{param: value}))
  IF len(unique) == len(args_to_check):    # every field in the combo had a truthy value
    qs = Klass.objects.filter(~Q(pk=self.get_pk), Q(deletado_em__isnull=True), *args_to_check)
    FOR except_param IN except_has:
      (key, value) = except_param if tuple/list else (except_param, None)
      IF getattr(self, key) == value (when value given): qs = Klass.objects.none(); BREAK
    IF qs.exists(): RAISE ValidationError(message OR default "Os campos <unique> devem ser únicos")
```

## Edge cases (as implemented)

If ANY field in a combo is falsy (None/empty) on self, that field is omitted from the filter and, because len(unique) != len(args_to_check), the ENTIRE combo check is skipped — a unique-together constraint with any blank component is not enforced at all for that row.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/models.py` | 46-113 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-model-BE-11-055`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-054](RULE-OPERACIONAL-INFRA-054-uniquemanagermixin-save-single-field-uniqueness-excluding-so.md)

## Notes

Soft-deleted rows (deletado_em not null) are always excluded from the uniqueness check, i.e. a soft-deleted record does not block re-creating a 'duplicate'. Compare RULE-model-BE-11-058 (SetUpModel) which overrides delete() but this mixin's own save() logic is shared by any model class combining it.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
