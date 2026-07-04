# RULE-TENANCY-ORGANIZACAO-048 — Company field constraints (primary color length, refresh interval)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Company primary color must be 6 chars (hex without

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| cor_primaria | string |  | exactly 6 characters (MinLengthValidator(6), max_length=6) |
| tempo_atualizacao | integer | seconds | >=0 (PositiveIntegerField), default 300 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid_company | bool |  |

## Logic
```text
cor_primaria = CharField(max_length=6, validators=[MinLengthValidator(6)]) -> must be length 6.
tempo_atualizacao = PositiveIntegerField(default=300).
```

## Edge cases (as implemented)
MinLengthValidator only enforced via full_clean/serializers; no '#' or hex-format check.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/empresa.py | 29-35 | 8166c07e | primary |

- Merged from: RULE-empresa-BE-04-011
- Related rules: RULE-TENANCY-ORGANIZACAO-043, RULE-TENANCY-ORGANIZACAO-044

## Notes
tempo_atualizacao likely the client refresh cadence for bed/alert polling. | Reconciliation: tempo_atualizacao (this rule's field-level constraint: PositiveIntegerField default 300) is the origin of the value consumed by the two auto-refresh polling rules (empresa-FE-08-002/003); cross-referenced via related.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
