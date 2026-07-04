# RULE-MOVIMENTACAO-ADT-042 — Patient-user-sector link diff-sync (vinculo bulk action)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The 'vinculo' action on SetorPacienteViewSet syncs which patients a given user is linked to within a sector: it computes the difference between the submitted pacientes_id list and the currently-linked patient ids for that (usuario, setor) pair, bulk-deletes links for patients no longer listed, and bulk-creates links for newly listed patients.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.data.pacientes_id | array of uuid |  |  |
| kwargs.setor__pk | uuid |  |  |
| kwargs.usuario__pk | uuid |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| UsuarioSetorPaciente links | set |  |

## Logic
```text
pacientes_enviados_id = request.data.pop("pacientes_id")
pacientes_atuais_id = list(UsuarioSetorPaciente.objects.filter(usuario=usuario, setor=setor).values_list("paciente", flat=True))
pacientes_adicionados = [p for p in pacientes_enviados_id if p not in pacientes_atuais_id]
pacientes_removidos = [p for p in pacientes_atuais_id if p not in pacientes_enviados_id]
if pacientes_removidos:
    UsuarioSetorPaciente.objects.filter(setor=setor, usuario=usuario, paciente__in=pacientes_removidos).delete()
if pacientes_adicionados:
    bulk_create UsuarioSetorPaciente(setor_id=setor, usuario_id=usuario, paciente_id=p) for p in pacientes_adicionados
return Response(status=200)
```

## Edge cases (as implemented)
Sending an empty pacientes_id list removes ALL existing links for that (usuario, setor) pair (full-clear operation), unlike the grupos_acessos empty-list edge case which is NOT clearable via empty array.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/paciente.py` | 65-105 | `8166c07e` | primary |

- Merged from: RULE-paciente-BE-05-003
- Related rules: RULE-MOVIMENTACAO-ADT-043, RULE-MOVIMENTACAO-ADT-008, RULE-MOVIMENTACAO-ADT-045

## Notes
Distinct route from the single-item SetorPacienteVinculoViewSet (RULE-043); this is the bulk-diff form. The submitted pacientes_id comes from the frontend GestaoPaciente screen selection (RULE-045).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
