# RULE-MOVIMENTACAO-ADT-058 — Automatic-type bed rejects movimentacao lacking data_entrada

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | movimentacao-adt |

## Rule
Posting a movimentacao to a bed whose tipo is 'automatica' with an empty data_entrada is rejected (400).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| leito.tipo | string, automatica |  |  |
| data_entrada | empty, "" |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| http_status | int |  |

## Logic
```text
leito.tipo = "automatica"; POST with data_entrada="" , dados_prontuario={} -> 400
```

## Edge cases (as implemented)
Test sets tipo='automatica' AND empty data_entrada simultaneously.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/tests/test_movimentacao.py` | 580-601 | `8166c07e` | primary |

- Merged from: RULE-VALIDATION-BE-12-030
- Related rules: RULE-MOVIMENTACAO-ADT-057, RULE-MOVIMENTACAO-ADT-025

## Notes
AMBIGUOUS - the 400 is fully explained by the empty-string data_entrada rule (RULE-057), which returns 400 for a MANUAL bed too. Cannot confirm from tests alone whether 'automatica' beds impose an additional data_entrada requirement; the test name signals that intent but the confound (empty string) makes it unverifiable. Kept separate (not merged into RULE-057) because the automatica-specific intent cannot be confirmed or ruled out.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
