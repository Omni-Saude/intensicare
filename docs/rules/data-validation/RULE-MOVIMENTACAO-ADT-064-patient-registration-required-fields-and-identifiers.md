# RULE-MOVIMENTACAO-ADT-064 — Patient registration required fields and identifiers

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Patient record requires attendance number, name, birth date and CPF; CPF is masked to Brazilian format; gender constrained to M/F/O.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| numero_atendimento | number |  |  |
| paciente.nome | string |  |  |
| paciente.data_nascimento | date, no time |  |  |
| paciente.cpf | masked string |  |  |
| paciente.genero | enum M\|F\|O |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid patient record | boolean |  |

## Logic
```text
required: numero_atendimento(number), paciente.nome(string), paciente.data_nascimento(date, showTime=false), paciente.cpf
cpf.mask = "000.000.000-00"
genero.options = { Masculino:"M", Feminino:"F", Outro:"O" }
paciente.codigo(number) and paciente.observacao(string) optional
```

## Edge cases (as implemented)
CPF mask enforces 11 digits in NNN.NNN.NNN-NN layout but no check-digit validation. Birth date has no time component.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormPaciente.ts` | 1-55 | `f9656be2` | primary |

- Merged from: RULE-patient-FE-01-005
- Related rules: RULE-MOVIMENTACAO-ADT-060, RULE-MOVIMENTACAO-ADT-054, RULE-MOVIMENTACAO-ADT-041

## Notes
Frontend gender enum here is M/F/O; the gender icon mapping (RULE-054) handles only M/F with a default fallback.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
