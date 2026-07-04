# RULE-MOVIMENTACAO-ADT-041 — Patient creation wrapper (CadastrarPaciente)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
CadastrarPaciente validates and creates a Paciente, returning its pk; invalid input raises a domain error.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| paciente | dict |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| paciente_pk | uuid string |  |

## Logic
```text
try: create via PacienteSerializer
except ValidationError: raise {"paciente":"paciente deve ser um dicionario com os dados do paciente"}
return str(instance.pk)
```

## Edge cases (as implemented)
Thin wrapper; validation delegated to PacienteSerializer.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/paciente/cadastrar_paciente.py` | 7-18 | `8166c07e` | primary |

- Merged from: RULE-paciente-BE-04-040
- Related rules: RULE-MOVIMENTACAO-ADT-020, RULE-MOVIMENTACAO-ADT-033, RULE-MOVIMENTACAO-ADT-060

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
