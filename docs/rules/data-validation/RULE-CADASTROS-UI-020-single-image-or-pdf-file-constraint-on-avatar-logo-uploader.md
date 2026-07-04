# RULE-CADASTROS-UI-020 — Single image-or-PDF file constraint on avatar/logo uploader

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The generic base64 file-upload control (used for user photos and company logos) only accepts a single file at a time and restricts the file picker to images or PDF documents.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| uploaded file | File |  | MIME type image/* or application/pdf |

## Outputs

| name | type |
|---|---|
| onChange({ b64, nome }) | { b64: string; nome: string } |

## Logic

```text
Upload.Dragger:
  multiple = false
  maxCount = 1
  accept = "image/*,application/pdf"
on upload -> getBase64(file) -> onChange({ b64, nome: file.name })
```

## Edge cases (as implemented)

No explicit file-size limit is enforced client-side (only mime-type/count constraints); a progress percentage is faked via setInterval incrementing 5% every 300ms and force-cleared after 8000ms regardless of actual completion, so the progress bar does not reflect real upload/conversion progress.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FileB64Convert/FileB64Convert.tsx` | 78-93 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-upload-FE-05-001`

**Related rules:**

- [RULE-CADASTROS-UI-019](RULE-CADASTROS-UI-019-image-file-extension-whitelist.md)

## Notes

Also renders a disabled prop pass-through used by FormEmpresa/FormUsuario for edit-mode locking.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
