# RULE-OPERACIONAL-INFRA-050 — next/image remote image domain whitelist

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
next.config.js restricts Next.js's built-in Image Optimization (`next/image`) to only fetch/optimize remote images whose host is "firebasestorage.googleapis.com" or "omni-pub-bkt.s3.amazonaws.com". Any other remote image domain is rejected by the framework at request time.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| image_src_hostname | string | n/a | firebasestorage.googleapis.com \| omni-pub-bkt.s3.amazonaws.com |

## Outputs

| name | type | unit |
|---|---|---|
| image_optimization_allowed | boolean | n/a |

## Logic

```text
ALLOWED_DOMAINS = ["firebasestorage.googleapis.com", "omni-pub-bkt.s3.amazonaws.com"]
IF request.image_hostname NOT IN ALLOWED_DOMAINS:
  REJECT (next/image throws/blocks optimization)
```

## Edge cases (as implemented)

Any future image source (e.g. a new CDN or a different S3 bucket) must be added to this list or images from it will fail to render via next/image. This is a security/allow-list control (mitigates SSRF-style abuse of the image-proxy) as well as a functional dependency on exactly two storage backends (Firebase Storage and an "omni-pub-bkt" S3 bucket), consistent with the `firebase` dependency in package.json.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `next.config.js` | 25-30 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-DATA-FE-09-004`

**Related rules:** _none_

## Notes

Verbatim as coded.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
