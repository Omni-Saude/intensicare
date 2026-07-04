# RULE-BALANCO-HIDRICO-015 — Fluid balance 24h accrual on output (saida)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Creating a Saida (output) record incrementally subtracts its quantidade from the parent BalancoHidrico's running balanco_24h total.

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
balanco.balanco_24h = balanco.balanco_24h - validated_data.quantidade
balanco.save()
```

## Edge cases (as implemented)
Same incremental-accumulator caveat as RULE-balanco-BE-07-003: SaidaSerializer.update() (lines 129-143) never adjusts balanco.balanco_24h even if quantidade is edited.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Standard nursing/ICU fluid-balance sign convention: Fluid Balance = total intake - total output; output (urine, stool, emesis, drainage, blood loss) DECREASES the balance, and when output exceeds intake the balance is NEGATIVE (net loss). Nurseslabs, "Monitoring Fluid Intake and Output (I&O)". (https://nurseslabs.com/monitoring-fluid-intake-and-output-io/)
- Test vectors: 3/3 match
- Mirror of RULE-BALANCO-HIDRICO-014. The accrual direction/sign matches the textbook fluid-balance definition: output decrements the running 24h balance (negative = net fluid loss), units are mL subtracted from mL. VERIFIED on all checkable dimensions. Same incremental-accumulator caveat (documented, not a formula discrepancy): SaidaSerializer.update() does not re-adjust balanco_24h when a saida's quantidade is edited, and no increment-back on delete is visible — editing/deleting an output after creation leaves the running total stale. Update-consistency gap, not a wrong equation; flag for internal review.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/saidas.py | 111-112 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-07-011
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-014, RULE-BALANCO-HIDRICO-039

## Notes
Mirror/opposite of RULE-balanco-BE-07-003.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
