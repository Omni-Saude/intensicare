# RULE-EVOLUCOES-026 — Auto sign-and-release on create when status is "liberado"

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When a new evolution document is created with status == "liberado", the system automatically generates the PDF and attempts both signing and release in the same request (rather than requiring separate explicit sign/release actions).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| validated_data.status [rascunho | liberado | inativo (inferred)] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| formulario.pdf, pdf_assinado, dt_assinatura, dt_liberacao |  |  |

## Logic
```text
def create(validated_data):
    ...
    formulario = super().create(validated_data)
    criar_campos_evolucao(formulario, campos_formulario)
    liberar = validated_data.get("status", False) == "liberado"
    evolucao = gerar_pdf_assinar_liberar(formulario, assinar=liberar, liberar=liberar)
    criar_acao_homecare()
    return evolucao
```

## Edge cases (as implemented)
assinar and liberar are always passed the SAME boolean (derived only from status=="liberado") — there is no way via this code path to sign without also attempting release, or vice versa, at creation time.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 238-255 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-005
- Related rules: RULE-EVOLUCOES-027, RULE-EVOLUCOES-025

## Notes
Same status=="liberado" gate reused identically in update() (RULE-evolucao-BE-07-011). RECONCILED with backend model: Formulario.status field default='salvo', choices=('salvo','liberado','inativo') (models/choices/formulario.py:46-51; models/formularios/formulario.py:26-29). This confirms the frontend status enum; the Phase-1 draft-state guess 'rascunho' is incorrect — the draft value is 'salvo'.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
