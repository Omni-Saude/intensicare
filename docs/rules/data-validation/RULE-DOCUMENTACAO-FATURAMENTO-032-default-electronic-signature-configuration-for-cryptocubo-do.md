# RULE-DOCUMENTACAO-FATURAMENTO-032 — Default electronic-signature configuration for CryptoCubo document signing

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule

DocumentosCryptocubo.__init__ hardcodes the default electronic-signature configuration used to legally sign clinical documents (evolutions/forms) through the CryptoCubo integration: tipo="advanced", formato="pdf", perfil="adrb", icpbr=False. These defaults are interpolated into the sign/verify request URLs (sign/{tipo}/{formato}?profile={perfil}&icpbr={icpbr}) and thus determine the legal signature strength/profile applied to every document signed on this path (invoked from utils/evolucoes.py:86-104 assinar_pdf_cryptocubo).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | string (default) | - | 'advanced' (not 'qualified') |
| formato | string (default) | - | 'pdf' |
| perfil | string (default) | - | 'adrb' |
| icpbr | bool (default) | - | False (ICP-Brasil root chain off) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| __SIGN_URL / __VERIFY_URL | string | - |

## Logic

```text
def __init__(self, documentos, usuario,
             tipo="advanced", formato="pdf", perfil="adrb", icpbr=False):
    self.__SIGN_URL   = CRYPTOCUBO_HOST + CRYPTOCUBO_ELETRONIC_SIGNATURE + \
                        f"sign/{tipo}/{formato}?profile={perfil}&icpbr={icpbr}"
    self.__VERIFY_URL = CRYPTOCUBO_HOST + CRYPTOCUBO_ELETRONIC_SIGNATURE + \
                        f"verify/{tipo}/{formato}?profile={perfil}&icpbr={icpbr}"
    # tipo="advanced" (NOT "qualified"); perfil="adrb"; icpbr=False (ICP-Brasil root chain off)
```

## Edge cases (as implemented)

All four signature parameters are keyword defaults, so unless a caller overrides them every document is signed with tipo=advanced (advanced, not qualified, signature), profile=adrb and icpbr=False (the ICP-Brasil root chain is not applied). The values flow verbatim into the CryptoCubo sign/verify URL query string.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/cryptocubo.py` | 18-27 | `8166c07e` | primary |

- Merged from: RULE-gap6-04
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-007, RULE-DOCUMENTACAO-FATURAMENTO-008, RULE-AUTH-USUARIOS-063

## Notes

COMPLIANCE-RELEVANT DEFAULT: the deployment default legally signs medical documents with an 'advanced' (not 'qualified') CryptoCubo profile and with ICP-Brasil (icpbr) disabled, which affects the legal weight/validity of the signature under Brazilian e-signature norms (MP 2.200-2/ICP-Brasil). Extracted as-is; NOT corrected. Only lines 44-47, 74-82 and 164-180 of this file were previously cited. Flag for legal/compliance review of the intended signature strength.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
