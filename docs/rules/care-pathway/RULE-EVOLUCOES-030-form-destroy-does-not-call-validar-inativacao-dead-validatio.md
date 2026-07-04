# RULE-EVOLUCOES-030 — Form destroy() does not call validar_inativacao (dead validation)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
destroy() marks a Formulario as inactive (status="inativo") and logs an AcaoHomecare audit entry, but never calls self.validar_inativacao(instance) (RULE-formulario-BE-08-017). As written, a form with status "liberado" CAN be inactivated through this endpoint, contradicting the intent expressed by validar_inativacao's docstring/message.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.status |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| instance.status [set to 'inativo'] |  |  |
| AcaoHomecare audit record |  |  |

## Logic
```text
def destroy(request):
    instance = self.get_object()
    # NOTE: self.validar_inativacao(instance) is NOT called here
    instance.status = "inativo"
    instance.save()
    criar_acao_homecare(tipo="evolucao", acoes=["inativar"], leito=request.leito,
                         setor=request.setor, evolucao=instance, realizado_por=request.user)
    return Response(status=204)
```

## Edge cases (as implemented)
No exception is raised even if instance.status == "liberado" prior to this call.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_base.py` | 151-169 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-018
- Related rules: RULE-EVOLUCOES-055

## Notes
Recorded verbatim per ground rules; validar_inativacao (lines 142-149) appears unused/dead in this file.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
