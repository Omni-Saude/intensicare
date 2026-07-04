# RULE-ALERTAS-026 — Record lifecycle status to icon/color mapping (handleIconByStatus)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps a record status string to an icon and color: "salvo" (saved) -> green check-circle, "liberado" (released/finalized) -> blue check-all, "inativo" (inactive) -> red cancel, empty string or anything else -> gray info icon.

## Inputs

- status (salvo | liberado | inativo | '' | other)

## Outputs

- icon (mdi path string)
- color (hex string)

## Logic

```text
switch(status):
  "salvo":    { icon: mdiCheckCircleOutline, color: "#258a10" }   # green
  "liberado": { icon: mdiCheckAll,           color: "#1890ff" }   # blue
  "inativo":  { icon: mdiCancel,             color: "#ff1633" }   # red
  "":         { icon: mdiInformation,        color: "#bababa" }   # gray
  default:    { icon: mdiInformation,        color: "#bababa" }   # gray
```

## Edge cases (as implemented)

Empty string and default both fall to gray info. The status enum (salvo/liberado/inativo) encodes the clinical-record lifecycle: draft-saved vs released/signed vs deactivated.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/handleIconByStatus.ts` | 8-21 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-status-FE-02-002`

**Related rules:** _none_

## Notes

Record-lifecycle status indicator (NOT alert severity); a generic UI helper. Kept in alertas as a status-enum sibling of the alert-color rules rather than misrouted, since no single other cluster is a clear owner. The domain rule is the status enumeration and its lifecycle meaning; icons/colors are presentation.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
