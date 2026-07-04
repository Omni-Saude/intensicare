# RULE-DOCUMENTACAO-FATURAMENTO-010 — Digital-signature eligibility - user must have CPF and PIN

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
A clinical document (SinaisVitais / Entrada / Saida etc.) is digitally signed via Cryptocubo only if the acting user has both a CPF and a PIN. Otherwise signing is skipped and a warning is logged; the object is left unsigned.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| user | User (needs .cpf and .pin) |  |  |
| objeto | model instance to sign |  |  |
| tipo | string (document type tag) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| objeto.assinatura | AssinaturaCryptocubo or unchanged |  |

## Logic
```text
if user.cpf and user.pin:
    data = vars(objeto).copy(); data.pop("_state")
    assinatura = assinar_xml_cryptocubo({tipo: data}, user)   # xml-escaped dict2xml, single-line
    if not assinatura.get_error():
        objeto.assinatura = AssinaturaCryptocubo.create(
            documento_assinado=sign_response, assinado_por=user,
            data_assinatura=now(), tipo=tipo, documento_original=xml_original)
    # on ValidationError: log warning, leave unsigned
else:
    log warning "usuario nao possui cpf ou pin"; leave unsigned
```

## Edge cases (as implemented)
Both cpf AND pin required (either missing -> no signature, warning only, no exception raised to caller). Signature generation failure (ValidationError from assinar_xml_cryptocubo) is caught and logged, not propagated. Object._state is stripped before serialising to XML.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 462-483 | 8166c07e | primary |
- Merged from: RULE-assinatura-BE-09-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-007, RULE-DOCUMENTACAO-FATURAMENTO-008, RULE-DOCUMENTACAO-FATURAMENTO-009, RULE-DOCUMENTACAO-FATURAMENTO-002

## Notes
assinar_xml_cryptocubo (utils.py 441-459) is the plumbing helper it calls. Signature metadata (assinado_por CPF, conselho, numero_conselho, estado_conselho, data_assinatura, "Valido") is rendered on the balanco/prescription PDFs.


Confirmed: validar_realizar_assinatura_cryptocubo (trilha_homecare/utils.py:456-483) is the caller of assinar_xml_cryptocubo, which constructs utils.cryptocubo.DocumentosCryptocubo (formato="xml") — the class whose internals are RULE-DOCUMENTACAO-FATURAMENTO-007/008/009.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
