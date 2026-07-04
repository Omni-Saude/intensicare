# RULE-AUTH-USUARIOS-054 — CPFValidator — Brazilian CPF check-digit validation

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Validates a Brazilian CPF taxpayer-ID string using the standard two-check-digit algorithm after stripping '-' and '.' separators. Rejects empty/short (<11 char) values and values where all characters are identical. Computes two check digits from the first 9 digits with descending weights and modulo-11, then compares the reconstructed 11-digit number to the input.

## Inputs

| name | type | range |
|---|---|---|
| cpf | string | 11 digits after stripping '.' and '-' |

## Outputs

| name | type |
|---|---|
| validity | raises ValidationError('CPF invalido') if invalid; returns nothing otherwise |

## Logic

```text
cpf = cpf.replace("-", "").replace(".", "")
IF NOT cpf OR len(cpf) < 11: RAISE Invalid
IF cpf == cpf[0] * len(cpf): RAISE Invalid            # all-identical-digit CPFs rejected
inteiros = [int(c) for c in cpf]
novo = inteiros[:9]
WHILE len(novo) < 11:
  r = sum((len(novo) + 1 - i) * v for i, v in enumerate(novo)) % 11
  f = 11 - r IF r > 1 ELSE 0
  novo.append(f)
IF novo != inteiros: RAISE Invalid
```

## Edge cases (as implemented)

CPF strings longer than 11 digits after stripping separators pass the length check but always fail the final novo==inteiros comparison (novo is fixed at 11 elements), so they are still rejected, just not via an explicit upper-bound message. Non-numeric characters raise via int() conversion (unhandled here, propagates as a ValueError rather than ValidationError).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 7-29 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cpf-BE-11-005`

**Related rules:**

- [RULE-AUTH-USUARIOS-031](RULE-AUTH-USUARIOS-031-auto-hash-plaintext-password-on-user-save.md)

## Notes

Verified against the standard published CPF algorithm (weights 10..2 then 11..2 over the digits, modulo 11, remainder<2 -> check digit 0 else 11-remainder): implementation matches; status OK, not a discrepancy.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
