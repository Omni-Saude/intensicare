# RULE-EVOLUCOES-027 — Auto sign-and-release on update when status is "liberado", gated by edit-eligibility

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Updating an evolution document first validates that it is editable at all (not inactive, and edited only by its original author), then — if the submitted status is "liberado" — re-runs the same sign+release logic as on create.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.status |  |  |  |
| instance.preenchido_por |  |  |  |
| requesting user |  |  |  |
| validated_data.status |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| formulario.pdf, pdf_assinado, dt_assinatura, dt_liberacao |  |  |

## Logic
```text
def update(instance, validated_data):
    validar_atualizacao(instance, usuario)  # validar_status + validar_usuario
    formulario = super().update(instance, validated_data)
    atualizar_campos_evolucao(campos_formulario)
    liberado = validated_data.get("status", False) == "liberado"
    evolucao = gerar_pdf_assinar_liberar(formulario, assinar=liberado, liberar=liberado)
    criar_acao_homecare()
    return evolucao
```

## Edge cases (as implemented)
If validar_atualizacao raises, the update never proceeds to the sign/release step.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 257-274 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-006
- Related rules: RULE-EVOLUCOES-026, RULE-EVOLUCOES-051, RULE-EVOLUCOES-052

## Notes
Composes RULE-evolucao-BE-07-007 (validar_status) and RULE-evolucao-BE-07-008 (validar_usuario).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
