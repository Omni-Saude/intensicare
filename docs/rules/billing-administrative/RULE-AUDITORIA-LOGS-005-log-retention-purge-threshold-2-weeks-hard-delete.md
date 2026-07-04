# RULE-AUDITORIA-LOGS-005 — Log retention / purge threshold (2 weeks, hard delete)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A scheduled Celery task permanently deletes LogModel rows older than 2 weeks (14 days) from criado_em, using a queryset bulk .delete() — which performs a real SQL DELETE, bypassing the model's soft-delete override entirely.
 Cadence: no celery-beat schedule entry for limpar_logs was found in-repo by either capture; trigger frequency is not determinable from code alone.

## Inputs

| name | type | unit |
|---|---|---|
| LogModel.criado_em | datetime | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| deleted_rows | n/a | n/a |

## Logic

```text
def limpar_logs():
    LogModel.objects.filter(
        criado_em__lt=timezone.now() - timezone.timedelta(weeks=2)
    ).delete()   # QuerySet.delete() => bulk hard delete, not soft-delete
```

## Edge cases (as implemented)

No scheduling/celery-beat entry for limpar_logs was found anywhere in the repo (grep for the task name only matches its own definition), so it is unclear from the code what triggers this purge or how often it runs. Strict less-than (records exactly 2 weeks old to the microsecond are kept). Cadence set by celery beat elsewhere.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/tasks.py` | 47-54 | `8166c07eae` | primary |
| ahlabs-trilhas | `core/tasks.py` | 47-54 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-012`
- `RULE-SCHED-BE-12-020`

**Related rules:**

- [RULE-AUDITORIA-LOGS-021](RULE-AUDITORIA-LOGS-021-soft-delete-mixin-present-but-not-exercised-for-logs.md)

## Notes

core/tasks.py is OUTSIDE the log/* file enumeration for this partition, but it is the only retention rule that exists for LogModel data and the task brief explicitly calls out 'audit-logging retention rules' as in-scope, so it is included here with its true source path for traceability. This is the definitive retention policy for the audit log: 14 days, then hard delete. | Duplicate capture reconciled: RULE-SCHED-BE-12-020 (partition BE-12) independently captured the identical function (core/tasks.py limpar_logs, same commit) under name 'Log retention - purge logs older than 2 weeks', category 'scheduling-operational'. Its extra detail: 'Cadence set by celery beat elsewhere.' and the sibling-task note ('Sibling task limpar_historicos_duplicados runs clean_duplicate_history --auto, no explicit threshold in-file') are folded in here without loss.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
