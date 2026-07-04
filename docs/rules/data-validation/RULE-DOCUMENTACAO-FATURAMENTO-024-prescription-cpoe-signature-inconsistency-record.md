# RULE-DOCUMENTACAO-FATURAMENTO-024 — Prescription/CPOE signature-inconsistency record

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | documentacao-faturamento |

## Rule
An "Inconsistência de Assinatura" (signature inconsistency) record cross-references an item as tracked in Trilhas ("item") against its corresponding item in the CPOE (Computerized Physician Order Entry) system ("item_cpoe") for a given patient/bed and date, implying a data-integrity reconciliation check between the two systems, though the actual mismatch-detection algorithm is computed server-side and not present in this partition.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| item | string |  |  |
| item_cpoe | string |  |  |
| data_item | string (date) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Inconsistencia.Assinatura | object |  |

## Logic
```text
Inconsistencia.Assinatura = {
  id: number, leito: string, data_item: string,
  ds_item: string, ds_paciente: string, ds_profissional: string,
  item: string, item_cpoe: string
}
// presumed: a mismatch/pending-signature discrepancy exists whenever item and item_cpoe
// disagree for the same data_item/leito/profissional; exact comparison logic not present here.
```

## Edge cases (as implemented)
No client-side comparison of item vs item_cpoe is performed in this partition — the frontend only lists/reports already-flagged inconsistencies (via GET .../inconsistencias/ and a PDF report endpoint).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/@types/models/Inconsistencia.d.ts | 4-14 | f9656be2 | primary |
- Merged from: RULE-inconsistencia-FE-07-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-025, RULE-DOCUMENTACAO-FATURAMENTO-002

## Notes
A verifier should check the backend partition for the actual reconciliation algorithm between Trilhas prescription items and CPOE order-entry items.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
