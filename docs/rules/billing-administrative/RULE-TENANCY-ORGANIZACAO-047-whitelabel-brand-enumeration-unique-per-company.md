# RULE-TENANCY-ORGANIZACAO-047 — Whitelabel brand enumeration (unique per company)

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Company whitelabel/brand identifier, unique across all companies.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| whitelabel | string |  | americashealth\|ficticia\|homecare\|outras |

## Outputs

| Name | Type | Unit |
|---|---|---|
| brand | string |  |

## Logic
```text
EmpresaChoices.whitelabel() -> (americashealth, ficticia, homecare, outras).
Empresa.whitelabel = CharField(max_length=25, unique=True) -> at most one company per brand slug.
```

## Edge cases (as implemented)
unique=True enforced at DB level.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/choices/empresa.py | 4-12 | 8166c07e | primary |

- Merged from: RULE-empresa-BE-04-004

## Notes
Model field constraint in core/models/empresa.py line 12-14.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
