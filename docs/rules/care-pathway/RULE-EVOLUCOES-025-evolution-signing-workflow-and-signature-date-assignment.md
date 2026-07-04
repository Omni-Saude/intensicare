# RULE-EVOLUCOES-025 — Evolution signing workflow and signature-date assignment

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
When an evolution document is signed, the system validates the signer has a registered CPF+PIN, generates the signed PDF via the Cryptocubo integration, and stamps the document's "dt_assinatura" (signature date) — but with the record's dt_registro (registration timestamp) rather than the actual signature timestamp produced by the signing service.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formulario.preenchido_por (cpf, pin) |  |  |  |
| formulario.pdf |  |  |  |
| formulario.dt_registro |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| formulario.pdf_assinado |  |  |
| formulario.dt_assinatura |  |  |

## Logic
```text
def assinar(formulario, assinar):
    if assinar:
        validar_assinatura(formulario.preenchido_por)  # requires cpf AND pin
        assinatura = assinar_pdf_cryptocubo(formulario.pdf, formulario.preenchido_por)
        dt_registro = formulario.dt_registro
        pdf_assinado = assinatura.get_pdf_assinado()
        formulario.pdf_assinado = pdf_assinado
        if formulario.pdf_assinado:
            formulario.dt_assinatura = dt_registro   # <-- uses dt_registro, not the signature's own timestamp
            acoes.append("assinar")
            enviar_arquivo_amhdocs.apply_async(args=[formulario.nr_atendimento, get_amhdocs_data(...)])
```

## Edge cases (as implemented)
The `assinatura` object returned by assinar_pdf_cryptocubo presumably carries its own true signing timestamp (used elsewhere, e.g. EntradaSerializer.get_data_assinatura reads instance.assinatura.data_assinatura), but this method discards it in favor of dt_registro. If dt_registro is set at document-creation time and signing happens later (e.g. on update()), dt_assinatura will misrepresent the actual signing moment.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 193-210 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-003
- Related rules: RULE-EVOLUCOES-026, RULE-EVOLUCOES-027, RULE-EVOLUCOES-054

## Notes
Flagged DISCREPANCY because within the same codebase (entradas.py/saidas.py/ sinais_vitais.py) the true "data_assinatura" is clearly available on the assinatura object and used directly elsewhere, suggesting this dt_registro substitution is unintentional rather than a deliberate design choice.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
