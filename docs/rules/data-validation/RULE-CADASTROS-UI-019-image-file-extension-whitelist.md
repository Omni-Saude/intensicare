# RULE-CADASTROS-UI-019 — Image-file extension whitelist

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Determines whether a filename is an image (drives inline preview vs generic file icon) by lowercase-insensitive... (actually case-sensitive) extension membership.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| nameFile | string |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| isImage | boolean |  |

## Logic

```text
extension = nameFile.substring(nameFile.lastIndexOf(".") + 1)
return [tif, tiff, bmp, jpg, jpeg, gif, png, eps, raw, cr2, nef, orf, sr2, ico, svg].includes(extension)
```

## Edge cases (as implemented)

Case-SENSITIVE: "PNG"/"JPG" (uppercase) are NOT matched. A filename with no dot yields the whole string as "extension" (lastIndexOf -1 -> substring(0)). Includes RAW camera formats (cr2/nef/orf/sr2) and vector svg/eps but not webp/heic.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/isImage.ts` | 1-23 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-02-007`

**Related rules:** _none_

## Notes

Case sensitivity is a likely latent bug (uppercase extensions excluded) but recorded verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
