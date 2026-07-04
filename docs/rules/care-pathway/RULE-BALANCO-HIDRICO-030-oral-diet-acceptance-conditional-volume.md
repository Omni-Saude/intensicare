# RULE-BALANCO-HIDRICO-030 — Oral-diet acceptance conditional volume

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
For an oral-diet intake, acceptance level determines whether a volume is required.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| aceitacao | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| quantidade | — | ml |

## Logic
```text
aceitacao required.
  aceitou  -> quantidade(ml) required
  reduzida -> quantidade(ml) required
  recusou  -> no volume field (patient refused; implicit 0)
```

## Edge cases (as implemented)
The recusou branch intentionally collects no volume.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormBalancoHidrico.ts | 53-92 | f9656be2 | primary |
- Merged from: RULE-fluidbalance-FE-01-008
- Related rules: RULE-BALANCO-HIDRICO-029

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
