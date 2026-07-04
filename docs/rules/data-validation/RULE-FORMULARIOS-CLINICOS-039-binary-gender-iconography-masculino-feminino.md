# RULE-FORMULARIOS-CLINICOS-039 — Binary gender iconography (Masculino/Feminino)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | formularios-clinicos |

## Rule
Two dedicated icon components exist for gender/sex representation: Masculino.jsx (Male) and Feminino.jsx (Female). No third/non-binary or 'unspecified' gender icon exists within this partition's scope.

## Outputs

| Name | Type | Unit |
|---|---|---|
| gender_icon | string | n/a |

## Logic

```text
GENDER_ICON = { "M": Masculino.jsx, "F": Feminino.jsx }
```

## Edge cases (as implemented)

AMBIGUOUS: the icon set alone does not prove the data model restricts gender/sex to a strict binary - the actual field validation lives outside this partition. DISCREPANCY (verbatim): unlike Feminino.jsx (fn 'Feminino'), Masculino.jsx internally names its component generic 'Icon'.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/icons/Masculino.jsx | 1-41 | f9656be2 | primary |

- Merged from: RULE-CLINICAL-FE-09-012
- Related rules: RULE-FORMULARIOS-CLINICOS-037

## Notes

Cross-referenced with src/icons/Feminino.jsx lines 1-45.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
