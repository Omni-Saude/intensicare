# RULE-MOVIMENTACAO-ADT-004 — Bed-level assistencial information clinical panel (vitals / neuro scores / labs)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | validation |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Each bed's Trilha exposes an assistencial-data panel combining vitals (BP systolic/diastolic/mean, temperature), neuro scores (RASS, Glasgow), delirium status, fluid balance (24h diuresis, 24h fluid balance), vasopressor/hemodialysis-catheter status, and a laboratory panel (WBC, platelets, CRP, lactate, pH, bicarbonate, pO2, pCO2, P/F ratio, creatinine, urea, bilirubin).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pressao_arterial.sistolica/diastolica/media | string, mmHg presumed |  |  |
| rass | number; clinically -5..+4, not enforced |  |  |
| glasgow | number; clinically 3..15, not enforced |  |  |
| delirium | enum Ausente\|Presente |  |  |
| noradrenalina | enum Ausente\|Presente |  |  |
| diurese_24h / balanco_hidrico_24h | number, mL presumed |  |  |
| leucocitos/plaquetas/pcr/lactato/ph/bicarbonato/po2/pco2/pf/creatinina/ureia/bilirrubinas | number |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| InformacoesAssistenciais | object |  |

## Logic
```text
InformacoesAssistenciais = {
  pressao_arterial: { sistolica: string, diastolica: string, media: string },
  rass: number, glasgow: number,
  delirium: "Ausente" | "Presente",
  diurese_24h: number, balanco_hidrico_24h: number, temperatura: number,
  noradrenalina: "Ausente" | "Presente",
  cateter_de_hemodialise: string,
  leucocitos: number, plaquetas: number, pcr: number, lactato: number,
  ph: number, bicarbonato: number, po2: number, pco2: number, pf: number,
  creatinina: number, ureia: number, bilirrubinas: number
}
```

## Edge cases (as implemented)
Blood-pressure sub-fields are typed as string (not number) unlike every other numeric lab value in this panel - an internal type inconsistency recorded verbatim. No numeric range validation present in this partition for any field.

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Composite assistencial panel. The two range-bearing scales it declares are verifiable: RASS (Sessler et al., Am J Respir Crit Care Med 2002;166:1338-44) spans +4 (combative) to -5 (unarousable); GCS total (Teasdale & Jennett, Lancet 1974) spans 3-15. All other fields (BP, temp, diuresis, labs: WBC, platelets, CRP, lactate, pH, HCO3, pO2, pCO2, P/F, creatinine, urea, bilirubin) are raw measured values, not scored - no formula/coefficients apply.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/@types/models/Ocupacao.d.ts | 109-135 | f9656be2 | primary |
- Merged from: RULE-ocupacao-FE-07-006
- Related rules: RULE-MOVIMENTACAO-ADT-002

## Notes
Cross-model note (other side out of this cluster): RASS here is number while Models.DadosProntuario.rass is string (RULE-prontuario-FE-07-002) - a cross-model type discrepancy not reconcilable within this cluster.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
