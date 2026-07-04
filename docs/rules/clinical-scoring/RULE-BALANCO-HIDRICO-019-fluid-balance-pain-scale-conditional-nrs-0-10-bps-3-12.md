# RULE-BALANCO-HIDRICO-019 — Fluid-balance pain-scale conditional (NRS 0-10 / BPS 3-12)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | AMBIGUOUS |
| Verification | VERIFIED, impact: none |
| Confidence | medium |
| Cluster | balanco-hidrico |

## Rule
Pain assessment branches by patient report; a verbal complaint triggers a 0-10 numeric rating scale, whereas observed pain signs trigger a 3-12 scored scale.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dor | — | — | — |
| escala_dor | — | score | — |
| sinais_dor | — | score | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| pain score | — | score |

## Logic
```text
dor options { ausente, queixa, sinais }
  queixa -> escala_dor required, min 0, max 10
  sinais -> sinais_dor required, min 3, max 12
```

## Edge cases (as implemented)
Boundaries inclusive (min/max). Empty branch for "ausente".

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Numeric Rating Scale (NRS) for pain intensity: integer 0-10 (0=no pain, 10=worst imaginable). Behavioral Pain Scale (BPS), Payen et al., Crit Care Med 2001;29(12):2258-2263 — sum of 3 subscales (facial expression, upper-limb movements, compliance with mechanical ventilation), each scored 1-4, total range 3-12. (https://pubmed.ncbi.nlm.nih.gov/16198570/)
- Test vectors: 5/5 match
- Extraction status was AMBIGUOUS only because the scale names are not labelled in code; against the published
references the enforced bounds are exactly canonical: queixa (verbal complaint) -> 0-10 = NRS; sinais (observed
signs, non-verbal/ventilated patient) -> 3-12 = Payen BPS (3 subscales x 1-4). Boundaries inclusive on both ends,
matching both scales. No score is computed here (front-end input-range gate only), so equation/units are n/a.
Ranges and band cutoffs VERIFIED.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormBalancoHidrico.ts | 582-622 | f9656be2 | primary |
- Merged from: RULE-fluidbalance-FE-01-015
- Related rules: RULE-BALANCO-HIDRICO-059

## Notes
0-10 range is consistent with the Numeric Rating Scale; the 3-12 range is consistent with the Behavioral Pain Scale (BPS). Scale identities are inferred, not labelled in code -> AMBIGUOUS.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
