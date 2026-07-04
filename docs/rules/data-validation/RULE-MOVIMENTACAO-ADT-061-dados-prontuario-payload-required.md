# RULE-MOVIMENTACAO-ADT-061 — dados_prontuario payload required

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The request must contain a dados_prontuario key.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.data | dict |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valid \| ValidationError | bool |  |

## Logic
```text
if "dados_prontuario" not in request.data:
    raise {"dados_prontuario": "O envio de dados_prontuario e obrigatorio"}
```

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/validators/dados_prontuario.py` | 9-13 | `8166c07e` | primary |

- Merged from: RULE-validation-BE-04-044
- Related rules: RULE-MOVIMENTACAO-ADT-062

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
