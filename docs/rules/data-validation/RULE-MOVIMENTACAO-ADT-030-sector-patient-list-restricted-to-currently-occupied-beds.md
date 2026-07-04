# RULE-MOVIMENTACAO-ADT-030 — Sector patient list restricted to currently-occupied beds

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
SetorPacienteViewSet.get_queryset only returns patients whose leito matches the given setor__pk AND whose leito is currently occupied (ocupado=True).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.setor__pk | uuid |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Paciente |  |

## Logic
```text
return Paciente.objects.filter(leito__setor__pk=setor, leito__ocupado=True)
```

## Edge cases (as implemented)
A patient linked to a bed that has since been vacated (ocupado=False) disappears from this list even if a UsuarioSetorPaciente link still exists for them.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/paciente.py | 40-42 | 8166c07e | primary |
- Merged from: RULE-paciente-BE-05-001
- Related rules: RULE-MOVIMENTACAO-ADT-042, RULE-MOVIMENTACAO-ADT-044

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
