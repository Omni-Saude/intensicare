# RULE-SINAIS-VITAIS-004 — Capillary refill time (TEC) range and >5s threshold — inconsistent encodings

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Capillary refill time (TEC) is captured three different ways across the frontend: as a number bounded 3-20 s (movimentacao), as a boolean ">5s?" (enfermagem), and as an exam checkbox "TEC > 5s" (physician). The numeric field's lower bound of 3s also conflicts with physiologically-normal refill (<2-3s).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tec | number | seconds | 3-20 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| tec value / alert | number|boolean | seconds |

## Logic
```text
movimentacao:      tec number, min 3, max 20
enfermagem:        tec_maior_5s boolean ("Tempo de Enchimento Capilar maior que 5 segundos?")
formulario_medico: exame_fisico option tec_5s "TEC > 5s"
```

## Edge cases (as implemented)
Lower bound of 3s excludes physiologically-normal refill (<2s), so normal-perfusion patients cannot record a true TEC on the numeric field. Same concept encoded three different ways (number 3-20, boolean >5s, checkbox >5s) across forms.

## Divergence
Three divergent encodings of the same clinical concept coexist: numeric 3-20s (movimentacao) vs boolean ">5s" (enfermagem dataFormEnfermagem.ts:462-465) vs checkbox "TEC > 5s" (formulario_medico dataFormFormularioMedico.ts:149). The numeric 3-20 bound also matches backend TecValidator (RULE-SINAIS-VITAIS-013, 0 or 3-20) but the >5s boolean/checkbox is a separate derived alert threshold not present in the backend range. The 3s floor conflicts with the published normal capillary-refill cutoff (~<2-3s).

## Verification
- Verdict: DISCREPANCY (clinical impact: moderate)
- Reference: Capillary refill time (CRT). Normal CRT in adults is <=2 s; a value >2-3 s indicates impaired peripheral perfusion. The 3 s cutoff is the perfusion target adopted in the ANDROMEDA-SHOCK / ANDROMEDA-SHOCK-2 septic-shock RCTs (Hernandez et al. JAMA 2019; Kattan/Hernandez 2023). CRT >5 s is a markedly- prolonged severity level, not the normal/abnormal boundary.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 93-99 | `f9656be2` | primary |
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 462-465 | `f9656be2` | variant |
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 149 | `f9656be2` | variant |

- Merged from: RULE-vitals-FE-01-022
- Related rules: RULE-SINAIS-VITAIS-013

## Notes
verify=true: capillary refill time has a published clinical anchor (normal <2-3s; abnormal >3s used in perfusion/shock assessment) against which the 3s floor and >5s alert should be checked.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
