# RULE-TENANCY-ORGANIZACAO-045 — Access-group exactly-one-scope constraint (three_xor)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
A GrupoAcesso (access group) must be attached to exactly one organizational scope - one and only one of empresa, estabelecimento, or setor may be set; zero or two+ is invalid.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| a (empresa set) | boolean | - | true\|false |
| b (estabelecimento set) | boolean | - | true\|false |
| c (setor set) | boolean | - | true\|false |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid | boolean | - |

## Logic
```text
def three_xor(a, b, c):
    return (not a and (b ^ c)) or (a and not (b or c))
# truth table: True IFF exactly one of a,b,c is True
# usage (core/models/grupo_acesso.py:117):
#   if not three_xor(bool(empresa), bool(estabelecimento), bool(setor)):
#       raise ValidationError({"data": "Inconsistencia de dados!"})
```

## Edge cases (as implemented)
Returns True only for exactly-one-set. All-false -> False (invalid). Any two or all three set -> False (invalid). Caller raises ValidationError when three_xor is False.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/utils.py | 145-146 | 8166c07e | primary |

- Merged from: RULE-VALIDATION-BE-12-014
- Related rules: RULE-TENANCY-ORGANIZACAO-046

## Notes
Verified truth table = XOR-exactly-one. Enforced in GrupoAcesso.save (core/models/grupo_acesso.py:108-119, outside partition). | Reconciliation: cross-referenced with grupo-FE-06-029, the frontend UI that lets an admin attach sectors/users to a GrupoAcesso's single organizational scope; the frontend rule documents the client-side query parameters, this rule documents the backend invariant they must satisfy.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
