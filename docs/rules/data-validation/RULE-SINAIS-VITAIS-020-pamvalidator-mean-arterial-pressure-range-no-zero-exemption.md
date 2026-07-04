# RULE-SINAIS-VITAIS-020 — PAMValidator — mean arterial pressure range, no zero exemption (validator defined but disabled on field)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
PAM (mean arterial pressure) validator requires 0-200 inclusive. The validator class is defined but its application on the model field is COMMENTED OUT (pam field and import both disabled in dados_prontuario.py), so no PAM is stored/validated at present.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pam | number | mmHg | 0-200 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| validity | raises ValidationError otherwise |  |

## Logic
```text
IF NOT (0 <= pam <= 200): RAISE ValidationError(f"{pam} deve estar entre 0 e 200")
```

## Edge cases (as implemented)
No zero exemption. Application disabled: dados_prontuario.py:84-85 field commented out and import at line 16 commented out. Dead test: test_pad_entre_0_e_200 sets a non-field attribute pam=205 which is NOT validated.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 176-185 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 84-85 (commented) | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-017

## Notes
Standalone (no separate BE-10 rule captured; the disabled-application detail was recorded in the PADValidator capture's note). Left OK (validator definition is well-formed); the disabled state is documented rather than flagged.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
