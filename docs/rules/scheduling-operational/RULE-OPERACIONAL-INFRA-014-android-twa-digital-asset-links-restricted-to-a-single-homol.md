# RULE-OPERACIONAL-INFRA-014 — Android TWA Digital Asset Links restricted to a single homol package

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | eligibility |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

public/.well-known/assetlinks.json grants "delegate_permission/common.handle_all_urls" (full-URL App Links / Trusted Web Activity verification, enabling a chromeless installed Android app experience) to exactly one Android package: "co.omnisaude.trilhas.homol.twa", identified by a single SHA256 cert fingerprint. No entries exist for a "prod" or "demo" TWA package, even though package.json/ecosystem.config.js define three parallel deploy targets (prod/homol/demo) that appear to share this same public/ directory and codebase.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| android_package_name | string | n/a | co.omnisaude.trilhas.homol.twa |
| sha256_cert_fingerprint | string | n/a | A8:27:...:A9 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| url_handling_delegated | boolean | n/a |

## Logic

```text
IF requesting_android_package == "co.omnisaude.trilhas.homol.twa"
   AND cert_fingerprint == "A8:27:34:65:C8:23:B3:F5:30:7B:9B:18:FD:96:21:BF:F0:F8:E1:00:9A:4E:0B:ED:F9:D8:E8:88:E1:A1:24:A9":
  DELEGATE handle_all_urls permission (verified App Link / full TWA mode)
ELSE:
  deny (link opens in regular browser, not the installed TWA app)
```

## Edge cases (as implemented)

DISCREPANCY (verbatim, not corrected): if a prod or demo Android TWA app exists, it would not be App-Link-verified under this assetlinks.json content — either each deploy target must serve its own distinct public/.well-known/assetlinks.json (not evidenced anywhere in this partition, which contains only one such file) or only the homol/staging Android app is actually verified, and any production/demo Android TWA would fall back to ordinary browser-chrome behavior rather than a full native-feeling app experience.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `public/.well-known/assetlinks.json` | 1-13 | `f9656be2` | primary |

- Merged from: RULE-DEPLOY-FE-09-007
- Related rules: RULE-OPERACIONAL-INFRA-039, RULE-OPERACIONAL-INFRA-040

## Notes

Only one assetlinks.json exists in this checkout; cannot confirm whether prod/demo branches/servers substitute a different file at deploy time.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
