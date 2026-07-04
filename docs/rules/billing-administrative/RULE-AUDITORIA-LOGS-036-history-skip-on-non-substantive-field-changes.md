# RULE-AUDITORIA-LOGS-036 — History-skip on non-substantive field changes

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When saving an automatic trilha record, no history/audit snapshot is created if the only changed (dirty) fields are within a whitelist of non-substantive fields; any change touching a field outside that set records history normally.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| dirty_fields | set[string] |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| skip_history_when_saving | boolean |  |

## Logic

```text
fields_exclude_historico = {"dt_atualizacao", "assistido", "assistido_por", "assistido_em", "dt_referencia"}
if len(set(dirty_fields) - fields_exclude_historico) == 0:
    self.skip_history_when_saving = True     # -> no history record
super().save(...)
```

## Edge cases (as implemented)

Uses django-dirtyfields get_dirty_fields(). If a pre-existing skip_history_when_saving attr is present it is deleted first. When some dirty field is outside the whitelist, history is recorded even if whitelist fields also changed.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models_tasy/trilha_tasy_header.py` | 70-87 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-audit-BE-02-007`

**Related rules:** _none_

## Notes

The consumer of skip_history_when_saving (django-simple-history or similar) is outside this partition; effect inferred from the flag name and whitelist. get_version() is hardcoded "v2".

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
