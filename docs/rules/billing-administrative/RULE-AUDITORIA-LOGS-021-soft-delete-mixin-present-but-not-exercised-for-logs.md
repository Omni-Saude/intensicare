# RULE-AUDITORIA-LOGS-021 — Soft-delete mixin present but not exercised for logs

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
LogModel inherits SetUpModel -> ParanoiaMixin, which provides a 'deletado_em' soft-delete column, an instance .delete() override that soft-deletes by default, and both an unfiltered 'objects' manager and a filtered 'objects_without_deleted' manager. Nothing in the log app ever calls .delete() on an individual LogModel instance, and the only bulk deletion (RULE-012's limpar_logs) uses QuerySet.delete() which does not go through the instance override, so it hard-deletes regardless. All log queries in views/log.py use the plain 'objects' manager, which returns rows regardless of deletado_em.

## Inputs

_None._

## Outputs

_None._

## Logic

```text
# ParanoiaMixin (utils/models.py):
objects = models.Manager()                 # unfiltered — used everywhere in log/views
objects_without_deleted = ParanoiaManager()  # filters deletado_em__isnull=True — never used by log app
def delete(self, **kwargs):
    ... soft-delete path (sets deletado_em) unless force_delete/admin-path ...
# LogModel/log app never calls instance .delete(); only bulk .filter().delete() (RULE-012) is used, which
# bypasses this override entirely (hard delete).
```

## Edge cases (as implemented)

If any LogModel row were ever individually soft-deleted (deletado_em set) through some code path outside this partition, it would still show up in every dashboard/list/detail view in log/views/log.py because they all query LogModel.objects (unfiltered), not objects_without_deleted.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/models/log.py` | 1-13 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-013`

**Related rules:**

- [RULE-AUDITORIA-LOGS-005](RULE-AUDITORIA-LOGS-005-log-retention-purge-threshold-2-weeks-hard-delete.md)

## Notes

AMBIGUOUS: inherited soft-delete machinery appears to be dead weight for this model given how it's actually used (only ever hard-deleted in bulk by age); best interpretation is that soft-delete was inherited automatically via SetUpModel and simply never leveraged for logs. Supporting mixin code is in utils/models.py (outside log/*), cited only for evidence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
