# RULE-COMUNICACAO-012 — Patient snapshot in observation branches by leito type

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
get_paciente (identical in ObservacaoSerializer and ObservacaoRespostaSerializer) resolves which patient payload to return for an observation based on the linked leito's tipo: 'manual' uses the real Paciente record (nested serializer); 'automatica' uses a stored JSON snapshot (paciente_automatica); anything else (i.e. 'homecare') uses paciente_homecare JSON snapshot.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.leito.tipo | string enum (manual\|automatica\|homecare) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| paciente | object \| null | — |

## Logic
```text
def get_paciente(instance):
    if instance.leito:
        if instance.leito.tipo == "manual":
            return PacienteSimplesSerializer(instance.paciente).data
        elif instance.leito.tipo == "automatica":
            return instance.paciente_automatica
        else:
            return instance.paciente_homecare
    # implicit: returns None if instance.leito is falsy
```

## Edge cases (as implemented)
If instance.leito is None (e.g. a setor-level general observation not tied to a bed), the method returns None implicitly (no explicit else/return at the outer level).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/observacao.py | 62-70, 173-181 | 8166c07e | primary |
- Merged from: RULE-observacao-BE-05-001
- Related rules: RULE-COMUNICACAO-013, RULE-COMUNICACAO-034

## Notes
Duplicated verbatim between ObservacaoRespostaSerializer.get_paciente and ObservacaoSerializer.get_paciente.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
