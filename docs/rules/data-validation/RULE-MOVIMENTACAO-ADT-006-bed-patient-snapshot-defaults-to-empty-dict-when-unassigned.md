# RULE-MOVIMENTACAO-ADT-006 — Bed patient snapshot defaults to empty dict when unassigned

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
OcupacaoSerializer.get_paciente returns a flattened patient info dict (id, nome, nome_extendido, idade, genero) when instance.paciente is set, or an empty dict {} (not null) when no patient is assigned to the bed.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.paciente | object \| null |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| paciente | object |  |

## Logic
```text
return ({
    "id": instance.paciente.get_pk, "nome": instance.paciente.nome_fracionado,
    "nome_extendido": instance.paciente.nome_abreviado, "idade": instance.paciente.idade_paciente,
    "genero": instance.paciente.genero,
} if instance.paciente else {})
```

## Edge cases (as implemented)
Returns {} rather than None when unassigned - contrast with ObservacaoSerializer.get_paciente which implicitly returns None when there is no leito.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference exists. Internal serializer contract (OcupacaoSerializer.get_paciente returns flattened patient dict, or {} when bed unassigned). Verified against legacy source only.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/leito.py | 101-116 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-003
- Related rules: RULE-MOVIMENTACAO-ADT-007

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
