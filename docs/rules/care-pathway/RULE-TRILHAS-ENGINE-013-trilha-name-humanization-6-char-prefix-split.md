# RULE-TRILHAS-ENGINE-013 — Trilha name humanization (6-char prefix split)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | trilhas-engine |

## Rule
Formats an internal trilha (care-pathway) identifier for display by splitting it at a FIXED 6-character boundary, capitalizing each part and joining with a space. This assumes trilha identifiers are of the form "trilha"+suffix (the literal 6-char prefix "trilha").

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilhaName | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| humanized | string |  |

## Logic
```text
firstWord = trilhaName.substring(0,6)     # first 6 chars, e.g. "trilha"
lastWord  = trilhaName.substring(6)       # remainder
return capitalize(firstWord) + " " + capitalize(lastWord)   # lodash capitalize (first letter up, rest lower)
```

## Edge cases (as implemented)
Hard-coded 6-char split assumes every trilha name begins with the 6-letter token "trilha". lodash capitalize lowercases the rest, so a mixed-case suffix like "Sepse" -> "Sepse" but "SEPSE" -> "Sepse". Names shorter than 6 chars yield an empty lastWord and a trailing space.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/trilhaHumanize.ts` | 3-10 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-02-001`
- Related rules: RULE-TRILHAS-ENGINE-018, RULE-TRILHAS-ENGINE-005

## Notes
AMBIGUOUS: the magic number 6 encodes an assumption about the "trilha<Name>" naming convention that a verifier should confirm against actual trilha slugs (e.g. sepse vs sepse_v3 variants handled elsewhere / out of partition).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
