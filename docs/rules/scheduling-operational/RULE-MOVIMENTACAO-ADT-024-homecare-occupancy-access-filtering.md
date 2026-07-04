# RULE-MOVIMENTACAO-ADT-024 — Homecare occupancy access filtering

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
For homecare establishments, an occupancy list only returns occupied beds whose patient is assigned to the requesting user; automatic type returns only occupied beds; others return all sector beds.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| estabelecimento.empresa.tipo | enum {homecare, automatica, manual, ...} |  |  |
| UsuarioSetorPaciente | setor, usuario) (relation |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset of Leito |  |  |

## Logic
```text
tipo = setor.estabelecimento.empresa.tipo
if tipo == 'homecare':
    ids_pacientes = UsuarioSetorPaciente.filter(setor=setor, usuario=request.user).values_list('paciente_id')
    return qs.filter(setor=setor, paciente_id__in=ids_pacientes, ocupado=True).order_by('codigo')
qs = qs.filter(setor=setor)
return qs.filter(ocupado=True).order_by('codigo') if tipo in ['homecare','automatica'] else qs
```

## Edge cases (as implemented)
setor missing -> raises "Setor deve ser enviado na rota". homecare additionally scopes to the user's assigned patients.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_manual/api/v1/views/ocupacoes.py | 50-75 | 8166c07e | primary |
- Merged from: RULE-op-BE-10-064
- Related rules: RULE-MOVIMENTACAO-ADT-021, RULE-MOVIMENTACAO-ADT-051

## Notes
'homecare' branch handled before the final ternary (which also lists homecare) so the ternary's homecare arm is unreachable.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
