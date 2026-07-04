# RULE-OPERACIONAL-INFRA-060 — TasyModel Oracle database routing (reads and writes forced to the 'oracle' connection)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Any model mixing in the abstract TasyModel is force-routed to the legacy Oracle 'Tasy' EMR database. Its default manager (TasyModelManager) appends .using("oracle") in get_queryset() so all reads hit Oracle, and TasyModel.save() forces kwargs["using"]="oracle" so all writes hit Oracle, instead of the default Postgres connection. A second manager, objects_without_request, is a plain models.Manager() without the Oracle routing.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| model mixing in TasyModel | Django model | - | - |
| db alias | string | - | 'oracle' (Tasy) vs default (Postgres) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| read/write connection | db alias | - |

## Logic

```text
class TasyModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("oracle")    # reads -> oracle

class TasyModel(models.Model):
    objects = TasyModelManager()                          # default manager -> oracle
    objects_without_request = models.Manager()            # plain manager (no forced oracle)
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        kwargs["using"] = "oracle"                        # writes -> oracle (overrides caller)
        super().save(*args, **kwargs)
```

## Edge cases (as implemented)

save() unconditionally overwrites kwargs["using"] with "oracle", so even a caller explicitly passing using="default" is silently redirected to Oracle. Reads via the default `objects` manager go to Oracle; the `objects_without_request` manager bypasses the routing and uses the default database. Being abstract, this applies to every concrete model that inherits TasyModel.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/models.py` | 263-277 | `8166c07e` | primary |

- Merged from: RULE-gap6-07
- Related rules: RULE-OPERACIONAL-INFRA-017, RULE-OPERACIONAL-INFRA-018, RULE-OPERACIONAL-INFRA-053

## Notes

Sibling mixins in the same file (ParanoiaMixin soft-delete 193-243, SetUpModel 245-261, uniqueness mixins 46-157) are captured as RULE-OPERACIONAL-INFRA-017/018/053/054, but this Oracle-routing convention had no corresponding rule.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
