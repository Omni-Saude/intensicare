# RULE-EVOLUCOES-001 — Medical-record clinical parameter panel with pre-computed SOFA score

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
The full patient-record clinical dataset (DadosProntuario) includes a single numeric "escore_sofa" (SOFA score) field alongside its likely component labs/vitals (creatinine, bilirubin, platelets, MAP-adjacent fields via pas/pad, Glasgow, temperature, heart rate, PaO2/FiO2-adjacent fields), implying the SOFA score itself is computed server-side; no computation formula is present in this frontend partition.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| creatinina, bilirrubinas, plaquetas, glasgow, pas, pad, po2, paco2, fio2, temperatura, frequencia_cardiaca |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| escore_sofa [clinically 0-24 (not enforced in this file)] |  |  |

## Logic
```text
DadosProntuario.escore_sofa: number   // opaque pre-computed value; component inputs present
// in the same object but no SOFA sub-score formula (respiratory/coagulation/liver/
// cardiovascular/CNS/renal) is implemented in this frontend partition.
```

## Edge cases (as implemented)
Unknown rounding/derivation; not computed client-side.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Vincent JL, Moreno R, Takala J, Willatts S, De Mendonca A, Bruining H, et al. The SOFA (Sepsis-related Organ Failure Assessment) score to describe organ dysfunction/failure. On behalf of the Working Group on Sepsis-Related Problems of the ESICM. Intensive Care Med. 1996;22(7):707-710. Six organ systems (respiratory, coagulation, hepatic, cardiovascular, CNS, renal), each 0-4, total 0-24.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/Prontuario.d.ts` | 19-63 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-07-001
- Related rules: RULE-EVOLUCOES-002

## Notes
A verifier should check the backend partition for the actual SOFA sub-score computation. DadosProntuario additionally tracks eme, shic, tec, vasopressina, hidrocortisona, anti_hipertensivo, covid_19, volume_corrente, dpoc, baixa_aceitacao_dieta_vo, historico_cirurgia_abdominal_recente, antibiotico_em_24hrs, presenca_cvc_cdl_7_dias, cvc_cdl_femoral_5_dias as boolean/numeric risk-factor flags whose exact clinical abbreviation is not spelled out in code and is therefore not asserted here.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
