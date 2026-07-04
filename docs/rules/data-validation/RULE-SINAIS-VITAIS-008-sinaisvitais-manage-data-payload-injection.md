# RULE-SINAIS-VITAIS-008 — SinaisVitais manage_data payload injection

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Parent balanco id injected from the route kwarg; the 'assinar' (sign) flag is passed through only if present in the payload.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| balancos__pk (URL kwarg) | string (uuid) |  |  |
| assinar (payload field) | boolean/any truthy |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| data["balanco"] | string (uuid) |  |
| data["assinar"] | same as input |  |

## Logic
```text
if isinstance(balanco, str): data["balanco"] = balanco
assinar = data.pop("assinar", None)
if assinar: data["assinar"] = assinar
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/sinais_vitais.py` | 54-65 | `8166c07e` | primary |

- Merged from: RULE-sinal-BE-08-050
- Related rules: RULE-SINAIS-VITAIS-006, RULE-SINAIS-VITAIS-007

## Notes
Identical pattern to entrada/saida manage_data (balanco-hidrico cluster: RULE-entrada-BE-08-012 / RULE-saida-BE-08-047).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
