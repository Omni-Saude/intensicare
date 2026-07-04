# RULE-MOVIMENTACAO-ADT-062 — Movimentacao creation composite validation

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Movimentacao creation runs bed, prontuario, patient, and (conditionally) entry-date validations together.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request, kwargs | leitos__pk) (mixed |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| aggregated validation | side-effect |  |

## Logic
```text
validations = [
  LeitoValidation(kwargs["leitos__pk"]),          # RULE-025
  DadosProntuarioValidation(request),             # RULE-061
  PacienteValidation(request),                    # RULE-060
]
if "data_entrada" in request.data:
  validations.append(DataValidation(request.data["data_entrada"], "%Y-%m-%dT%H:%M:%S"))  # RULE-059
ValidationComposite(validations).validate()
```

## Edge cases (as implemented)
DataValidation only added when data_entrada present (else defaults to timezone.now on the model).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/validators/movimentacao.py` | 10-33 | `8166c07e` | primary |

- Merged from: RULE-validation-BE-04-045
- Related rules: RULE-MOVIMENTACAO-ADT-025, RULE-MOVIMENTACAO-ADT-059, RULE-MOVIMENTACAO-ADT-060, RULE-MOVIMENTACAO-ADT-061, RULE-MOVIMENTACAO-ADT-033

## Notes
Composite pattern via utils.composite (out of partition).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
