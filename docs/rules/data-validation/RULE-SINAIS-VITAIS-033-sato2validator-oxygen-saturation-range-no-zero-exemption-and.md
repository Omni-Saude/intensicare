# RULE-SINAIS-VITAIS-033 — SatO2Validator — oxygen saturation range, no zero exemption AND disabled on the model field

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule

SpO2/SatO2 validator requires min_value=21 to max_value=100 inclusive with NO zero exemption (unlike the structurally identical FiO2Validator). Moreover the validator is DISABLED on the model field: sato2 = PositiveIntegerField(...) with validators=[SatO2Validator()] commented out (and the import commented out), so SatO2 is effectively unvalidated.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| sato2 | int | percent | 21-100 (per definition) / unvalidated (as applied) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| validity | raises ValidationError if enabled; no validation as applied | |

## Logic

```text
# validator definition (utils/validators.py):
min_value = 21; max_value = 100
IF NOT (min_value <= sato2 <= max_value): RAISE ValidationError(f"{sato2} deve estar entre {min_value} e {max_value}")
# model field application (dados_prontuario.py): validators=[SatO2Validator()] is COMMENTED OUT
sato2 = PositiveIntegerField(null=True, blank=True)  # any positive integer accepted
```

## Edge cases (as implemented)

As defined, sato2==0 is REJECTED (no sentinel exemption), whereas the structurally identical FiO2Validator (also 21-100) exempts 0 — an internal inconsistency. As applied, the validator is disabled so any positive integer is accepted. Sepse C2 uses <96; ventilacao C10 uses >96 and >92.

## Divergence

Two-facet ambiguity: (1) definition inconsistency — SatO2Validator (21-100) has no zero-exemption while FiO2Validator (RULE-SINAIS-VITAIS-010, same 21-100 bound) exempts 0; (2) the validator is defined but its field application is commented out, so no bound is enforced at runtime. Whether the missing zero-exemption and the disabled state are intentional is unresolved.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/validators.py | 371-386 | 8166c07e | primary |
| ahlabs-trilhas | trilha_manual/models/dados_prontuario.py | 147-151 | 8166c07e | duplicate |

- Merged from: RULE-vitais-BE-11-030, RULE-val-BE-10-093
- Related rules: RULE-SINAIS-VITAIS-010, RULE-SINAIS-VITAIS-005

## Notes

Merges the validator-definition capture (BE-11-030, range 21-100, no zero-exempt) with the model-field capture (BE-10-093, validator commented out / disabled). Physician form SpO2 is also unbounded (RULE-SINAIS-VITAIS-005), consistent with the disabled backend validator.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
