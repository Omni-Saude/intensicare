# RULE-MOVIMENTACAO-ADT-043 — SetorPacienteVinculoViewSet forces all link fields from the URL and hard-deletes

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
SetorPacienteVinculoViewSet.manage_data always overwrites 'paciente', 'setor', and 'usuario' from the corresponding URL kwargs (a client cannot set these via the body); get_queryset triple-scopes to the exact (setor, usuario, paciente) combination; deletion is a hard delete (force_delete=True), not soft-delete.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.paciente__pk | uuid |  |  |
| kwargs.setor__pk | uuid |  |  |
| kwargs.usuario__pk | uuid |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| UsuarioSetorPaciente | object |  |

## Logic
```text
def get_queryset():
    return UsuarioSetorPaciente.objects.filter(setor=kwargs["setor__pk"], usuario=kwargs["usuario__pk"], paciente=kwargs["paciente__pk"])
def manage_data(request, *a, **kw):
    data = super().manage_data(request, *a, **kw)
    data["paciente"] = kwargs["paciente__pk"]
    data["setor"] = kwargs["setor__pk"]
    data["usuario"] = kwargs["usuario__pk"]
    return data
def perform_destroy(instance):
    instance.delete(force_delete=True)
```

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/usuario_setor_paciente.py` | 23-45 | `8166c07e` | primary |

- Merged from: RULE-vinculo-BE-05-001
- Related rules: RULE-MOVIMENTACAO-ADT-042

## Notes
Distinct viewset/route from the 'vinculo' action on SetorPacienteViewSet (RULE-042) - both manage UsuarioSetorPaciente rows but via different URL shapes and single-item vs bulk-diff semantics.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
