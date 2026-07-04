# RULE-CADASTROS-UI-015 — Brazilian federative-unit (UF) enumeration

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
The 27 Brazilian states/federal district (UF code -> name) used for address/council registration state selection.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| uf | string |  | AC,AL,AP,AM,BA,CE,DF,ES,GO,MA,MT,MS,MG,PA,PB,PR,PE,PI,RJ,RN,RS,RO,RR,SC,SP,SE,TO |

## Outputs

| name | type | unit |
|---|---|---|
| label | string |  |

## Logic

```text
Standard IBGE two-letter UF codes mapped to full state names (27 entries).
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/choicesEstados.ts` | 1-110 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-02-003`

**Related rules:** _none_

## Notes

Complete set of 26 states + DF. Low domain weight but constrains council/address forms.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
