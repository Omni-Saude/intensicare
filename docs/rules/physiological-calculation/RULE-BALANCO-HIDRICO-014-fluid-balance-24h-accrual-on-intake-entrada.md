# RULE-BALANCO-HIDRICO-014 — Fluid balance 24h accrual on intake (entrada)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Creating an Entrada (intake) record incrementally adds its quantidade to the parent BalancoHidrico's running balanco_24h total (rather than recomputing the sum from all entradas/saidas).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| balanco.balanco_24h | mL (assumed) | — | — |
| quantidade | mL (assumed) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco.balanco_24h | mL (assumed) | — |

## Logic
```text
balanco.balanco_24h = balanco.balanco_24h + validated_data.quantidade
balanco.save()
```

## Edge cases (as implemented)
Incremental accumulator, not a recompute: EntradaSerializer.update() (lines 120-135) never adjusts balanco.balanco_24h even when quantidade changes on an edit, and there is no corresponding decrement on delete visible in this file — editing/deleting an intake record after creation does not correct the running 24h balance shown in BalancoHidricoSerializer.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Standard nursing/ICU fluid-balance sign convention: Fluid Balance = total intake - total output; intake (oral, IV, tube feeds, TPN, flushes) INCREASES the balance, and when intake exceeds output the balance is POSITIVE (net gain). Nurseslabs, "Monitoring Fluid Intake and Output (I&O)". (https://nurseslabs.com/monitoring-fluid-intake-and-output-io/)
- Test vectors: 3/3 match
- The accrual direction/sign matches the textbook fluid-balance definition: intake increments the running 24h balance (positive = net fluid gain), units are mL added to mL. VERIFIED on all checkable dimensions. One data-integrity caveat (documented in the rule's edge_cases, NOT a formula discrepancy): the accumulator is incremental, so EntradaSerializer.update() does not re-adjust balanco_24h when quantidade is edited and there is no decrement on delete — editing/deleting an intake after creation leaves the running total stale. This is an update-consistency gap, not a wrong equation; flag for internal review if edit/delete of intake records is a supported workflow.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/entradas.py | 100-101 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-07-003
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-015, RULE-BALANCO-HIDRICO-038

## Notes
Mirror/opposite of RULE-balanco-BE-07-011 (Saida subtracts instead of adds). The apparent lack of balance correction on update is flagged as an edge case rather than a full DISCREPANCY because no update-time recomputation code exists at all to contradict — it is simply absent.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
