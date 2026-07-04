# RULE-MOVIMENTACAO-ADT-007 — Patient basic name/age computed fields

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
PacienteSimplesSerializer.get_nome and get_idade delegate to model properties nome_fracionado and idade_paciente respectively; nome_extendido maps directly to the model's nome_abreviado field.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.nome_fracionado | string |  |  |
| instance.idade_paciente | integer |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| nome | string |  |
| idade | integer |  |
| nome_extendido | string |  |

## Logic
```text
def get_nome(instance): return instance.nome_fracionado
def get_idade(instance): return instance.idade_paciente
nome_extendido = CharField(source="nome_abreviado", read_only=True)
```

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference exists. Internal field mapping (PacienteSimplesSerializer: get_nome->nome_fracionado, get_idade->idade_paciente, nome_extendido<-nome_abreviado). Verified against legacy source only.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/paciente.py | 7-26 | 8166c07e | primary |
- Merged from: RULE-paciente-BE-05-004
- Related rules: RULE-MOVIMENTACAO-ADT-006, RULE-MOVIMENTACAO-ADT-020

## Notes
nome_fracionado/idade_paciente/nome_abreviado are model properties in core/models, out of partition - only the field-mapping rule is captured.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
