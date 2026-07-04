# RULE-PRESCRICAO-022 — Horario prescricao manage_data payload injection

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
On write, the parent continuous-prescription id and the leito id are injected into the payload from nested-route kwargs when present as strings.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| prescricoes__pk (URL kwarg) | string (uuid) |  |  |
| ocupacoes__pk (URL kwarg) | string (uuid) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| data["prescricao_continua"] | string (uuid) |  |
| data["leito"] | string (uuid) |  |

## Logic

```text
if isinstance(prescricao, str): data["prescricao_continua"] = prescricao
if isinstance(leito, str): data["leito"] = leito
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/horario_prescricao.py` | 36-48 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-08-033

**Related rules:**

- RULE-PRESCRICAO-033

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
