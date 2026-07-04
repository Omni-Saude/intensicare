# RULE-OPERACIONAL-INFRA-042 — PWA app identity and installed-app display behavior

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
public/manifest.json declares the installable web-app identity for the product: short_name/name = "teleUTI" (i.e. the product's actual name is "teleUTI" — a tele-ICU product), start_url "/", scope "/", display mode "standalone" (launches without browser chrome), background_color #FFFFFF, theme_color #000000, and an icon set spanning 36x36 through 512x512 plus a 192x192 "maskable" icon for adaptive Android icons.

## Inputs

_None._

## Outputs

| name | type | unit | range |
|---|---|---|---|
| installed_app_name | string | n/a | teleUTI |
| display_mode | string | n/a | standalone |

## Logic

```text
manifest = {
  name: "teleUTI", short_name: "teleUTI",
  start_url: "/", scope: "/",
  display: "standalone",
  background_color: "#FFFFFF", theme_color: "#000000",
  icons: [36,48,72,96,144,192,512 px PNGs + 192px maskable],
  shortcuts: []
}
```

## Edge cases (as implemented)

"shortcuts": [] means no PWA app-shortcuts (e.g. quick actions from a long-press on the home-screen icon) are configured despite the field being present.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `public/manifest.json` | 1-55 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-PWA-FE-09-006`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-038](RULE-OPERACIONAL-INFRA-038-pwa-service-worker-generation-disabled-only-in-local-develop.md)

## Notes

Verbatim as coded.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
