# RULE-COMUNICACAO-045 — FilePicker only reconciles local file list on removal

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The multi-file chat picker's onChange handler updates the locally tracked file list only when the new fileList is shorter than the current one (i.e. a file was removed); additions are otherwise assumed to already be reflected via the separate customRequest upload handler.

## Inputs

| name | type |
|---|---|
| files (antd Upload fileList on change) | Models.LocalFile[] |

## Outputs

| name | type |
|---|---|
| customFileList (state) | Models.LocalFile[] |

## Logic

```text
handleChange(files):
  if files.length < customFileList.length:
    setCustomFileList(files)
  // else: no-op, even if files.length > customFileList.length
```

## Edge cases (as implemented)

If antd's onChange ever fires with a same-length but reordered/replaced list (e.g. a replace-in-place edit), this guard silently drops that update since length is unchanged; only pure removals are reconciled through this path.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FilePicker/FilePicker.tsx` | 48-52,79-82 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-upload-FE-05-003`

**Related rules:** _none_

## Notes

Ambiguous whether this is an intentional dedup guard (additions always go through handleB64Upload/customRequest so re-adding them here would double them) or an incomplete handler; recorded as observed without correcting it.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
