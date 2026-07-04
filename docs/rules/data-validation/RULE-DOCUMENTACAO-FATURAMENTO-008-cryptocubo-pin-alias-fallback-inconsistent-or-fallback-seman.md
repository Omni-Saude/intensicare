# RULE-DOCUMENTACAO-FATURAMENTO-008 — Cryptocubo PIN/ALIAS fallback — inconsistent 'or'-fallback semantics, unencoded fallback PIN

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
In the constructor, __ALIAS falls back to a plain environment default when usuario.cpf is falsy: `usuario.cpf or os.environ.get('CRYPTOCUBO_ALIAS')` — this works as intended for any falsy cpf (None or ''). __PIN instead first COMPUTES a derived value (base64-encoding usuario.pin) and only THEN applies 'or' against the environment default: `base64.b64encode(usuario.pin.encode('utf-8')).decode('utf-8') or os.environ.get('CRYPTOCUBO_PIN')`. If usuario.pin is None, `.encode()` raises an unhandled AttributeError before the fallback can ever apply. If usuario.pin is an empty string, the base64 encoding of empty bytes decodes to an empty string (falsy), so the fallback DOES trigger — but the fallback value taken directly from the environment is NOT base64-encoded, unlike every other code path's PIN value, which is always base64-encoded.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| usuario.cpf | string |  |  |
| usuario.pin | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| __ALIAS | string |  |
| __PIN | base64 string (intended) or raw env value (fallback path) |  |

## Logic
```text
__ALIAS = usuario.cpf OR os.environ.get("CRYPTOCUBO_ALIAS")
__PIN = base64.b64encode(usuario.pin.encode("utf-8")).decode("utf-8") OR os.environ.get("CRYPTOCUBO_PIN")
```

## Edge cases (as implemented)
usuario.pin is None -> unhandled AttributeError (crash), not a graceful fallback. usuario.pin == '' -> falls back to CRYPTOCUBO_PIN env value used AS-IS (not base64-encoded), while the Cryptocubo API payload builder (__get_cryptocubo_sign_data) always sends whatever is in self.__PIN as the 'pin' field, so this fallback path sends a differently-encoded PIN value than the normal path.

## Divergence
Within the same DocumentosCryptocubo.__init__ (utils/cryptocubo.py:44-47), __ALIAS and __PIN use the same 'or env-default' fallback idiom but behave inconsistently: __ALIAS = usuario.cpf or os.environ.get('CRYPTOCUBO_ALIAS') falls back safely for ANY falsy cpf (None or ''). __PIN = base64.b64encode(usuario.pin.encode('utf-8')).decode('utf-8') or os.environ.get('CRYPTOCUBO_PIN') instead computes the base64 encoding FIRST: if usuario.pin is None, '.encode()' raises an unhandled AttributeError before any fallback can apply (ALIAS has no equivalent crash risk); if usuario.pin == '', the base64 encoding of empty bytes decodes to '' (falsy), so the fallback DOES trigger, but the fallback value taken directly from CRYPTOCUBO_PIN is NOT base64-encoded — unlike every other code path's PIN value, which always is, and unlike ALIAS's fallback, which needs no such encoding step. __get_cryptocubo_sign_data() (utils/cryptocubo.py:95-113) sends self.__PIN verbatim as the API's 'pin' field regardless of which path set it, so the empty-pin fallback silently submits a differently-encoded PIN than every other case.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | utils/cryptocubo.py | 44-47 | 8166c07e | primary |
- Merged from: RULE-sign-BE-11-052
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-007, RULE-DOCUMENTACAO-FATURAMENTO-009, RULE-DOCUMENTACAO-FATURAMENTO-010

## Notes
DISCREPANCY recorded verbatim: the PIN fallback both risks an unhandled crash (None case) and produces an inconsistently-encoded value (empty-string case) compared to the ALIAS fallback in the same constructor, which behaves safely and consistently.

Confirmed: __get_cryptocubo_sign_data() (utils/cryptocubo.py:95-113) sends self.__PIN verbatim as the 'pin' field for every request, so the empty-string fallback's un-encoded value really does reach the Cryptocubo API differently-encoded than the normal path.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
