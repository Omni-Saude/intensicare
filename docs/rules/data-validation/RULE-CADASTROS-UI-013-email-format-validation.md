# RULE-CADASTROS-UI-013 — Email format validation

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
E-mail fields must match emailPattern regex; error message "E-mail invalido!".

## Inputs

| name | type | unit | range |
|---|---|---|---|
| email | string |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| valid | boolean |  |

## Logic

```text
emailFormRules = [ { pattern: emailPattern, message: "E-mail inválido!" } ]
emailPattern = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
```

## Edge cases (as implemented)

Local part allows many special chars; each domain label limited to 1-63 chars; TLD not required to be alphabetic; anchored full-string match.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/emailFormRules.ts` | 1-5 | `f9656be266` | primary |
| trilhas-frontend | `src/utils/constants.ts` | 7-8 | `f9656be266` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-01-002`
- `RULE-validation-FE-02-001`

**Related rules:**

- [RULE-CADASTROS-UI-011](RULE-CADASTROS-UI-011-formusuario-required-fields-only-enforced-in-modal-creation.md)

## Notes

The regex literal itself lives in src/utils/constants.ts:7-9 (outside partition FE-01); reproduced here from that source for completeness.

Merged with RULE-validation-FE-02-001 (constants.ts definition of emailPattern, lines 7-8): confirms the regex is identical to the one wrapped by emailFormRules.ts. That entry's edge_cases additionally note the final dotted domain group is optional in the regex, so a bare "user@host" (no TLD) also passes validation. The same constants.ts file also defines UI breakpoints collapseRule=1260 / collapseRuleMobile=800 (cosmetic, not captured here) and urlEnv detection (tracked separately as RULE-ops-FE-02-001 in the source misroute set, not part of this batch).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
