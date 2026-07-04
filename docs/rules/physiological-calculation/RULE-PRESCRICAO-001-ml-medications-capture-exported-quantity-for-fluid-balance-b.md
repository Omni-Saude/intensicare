# RULE-PRESCRICAO-001 — ml medications capture exported quantity for fluid balance (balanco hidrico)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | validation |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
When a medication is being marked administered AND its unit of measure is "ml", the modal shows a required numeric "Quantidade em ml" field whose value (qtd_exportada) is explicitly used for the patient fluid-balance (balanco hidrico) calculation.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| check (administrado radio == true) | boolean |  |  |
| unidadeMedida | string |  |  |
| qtd_exportada | number | ml |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| qtd_exportada | number | ml |

## Logic

```text
if (check === true && unidadeMedida === "ml"):
  render required InputNumber "Quantidade em ml" (name=qtd_exportada)
  caption: "* Valor em ml utilizado para o calculo de balanco hidrico"
else if (!check):
  render required "Motivo" select (see RULE-presc-FE-04-008)
# If administered but unit != "ml", no quantity input is shown; qtd_exportada falls back to quantidade.
```

## Edge cases (as implemented)
For non-ml administered meds no ml input is shown and qtd_exportada defaults to the prescribed quantidade (RULE-presc-FE-04-006). The actual balanco hidrico summation is done elsewhere (BalancoHidricoItens / backend), out of this partition.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. This is an internal UI/data-capture business rule governing whether the medication-check modal renders a required 'Quantidade em ml' input for meds whose unit of measure is 'ml', for later fluid-balance (balanco hidrico) charting. Fluid balance (intake/output charting) is a general nursing concept with no equation, coefficient, or score-band; there is no calculator or guideline (Sepsis-3/KDIGO/ASPEN/etc.) that governs conditional form-field rendering.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/CheckModalContent/CheckModalContent.tsx` | 117-132 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-007

**Related rules:**

- RULE-PRESCRICAO-025
- RULE-PRESCRICAO-004

## Notes
Category physiological-calculation: qtd_exportada feeds the balanco hidrico (fluid-balance) summation, done elsewhere (BalancoHidricoItens/backend, out of partition).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
