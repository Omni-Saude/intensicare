# RULE-AUTH-USUARIOS-004 — Partner-required permission predicate

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | access-control |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Grants access only when the request is associated with a (non-null) partner.

## Inputs

| name | type | range |
|---|---|---|
| request.partner | object\|null | None => denied |

## Outputs

| name | type |
|---|---|
| has_permission | boolean |

## Logic

```text
class HasPartnerPermission:
    def has_permission(request, view): return request.partner is not None
```

## Edge cases (as implemented)

Strict is-not-None check.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/permissions.py` | 9-11 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ACCESS-BE-12-016`

**Related rules:** _none_

## Notes

request.partner presumably set by an API-key/partner auth middleware.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
