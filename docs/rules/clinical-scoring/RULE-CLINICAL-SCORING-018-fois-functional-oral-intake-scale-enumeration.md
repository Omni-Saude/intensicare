# RULE-CLINICAL-SCORING-018 — FOIS (Functional Oral Intake Scale) enumeration

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Functional Oral Intake Scale captured as a 7-level select with the standard level descriptions.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_fonoaudiologica.fois | enum | level | nivel1-nivel7 |

## Outputs

| name | type | unit |
|---|---|---|
| fois level | enum | level |

## Logic

```text
fois options:
  nivel1 Nada por via oral
  nivel2 Dependente de via alternativa e minima via oral de algum alimento/liquido
  nivel3 Dependente de via alternativa com consistente via oral de alimento/liquido
  nivel4 Via oral total de uma unica consistencia
  nivel5 Via oral total com multiplas consistencias, com preparo especial/compensacoes
  nivel6 Via oral total com multiplas consistencias, sem preparo especial mas com restricoes
  nivel7 Via oral total sem restricoes
```

## Edge cases (as implemented)

Ordinal 1(worst)->7(best); labels match published FOIS.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Crary MA, Mann GDC, Groher ME. Initial psychometric assessment of a functional oral intake scale for dysphagia in stroke patients. Arch Phys Med Rehabil. 2005;86(8):1516-1520. Seven ordinal levels: 1 nothing by mouth; 2 tube dependent with minimal/inconsistent oral intake; 3 tube dependent with consistent oral intake; 4 total oral intake of a single consistency; 5 total oral intake of multiple consistencies requiring special preparation; 6 total oral intake with no special preparation but must avoid specific foods/liquids; 7 total oral intake with no restrictions. ([source](https://pubmed.ncbi.nlm.nih.gov/16084801/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| fois=nivel1 | FOIS 1: No oral intake / nothing by mouth | 'Nada por via oral' | yes |
| fois=nivel3 | FOIS 3: tube dependent with consistent oral intake of food/liquid | 'Dependente de via alternativa com consistente via oral de alimento/liquido' | yes |
| fois=nivel4 | FOIS 4: total oral intake of a single consistency | 'Via oral total de uma unica consistencia' | yes |
| fois=nivel6 | FOIS 6: total oral, multiple consistencies, no special prep but with restrictions | 'Via oral total com multiplas consistencias, sem preparo especial mas com restricoes' | yes |
| fois=nivel7 | FOIS 7: total oral intake with no restrictions | 'Via oral total sem restricoes' | yes |

**Verifier notes**

All seven level labels and their ordinal direction (1 = worst / nothing by mouth, 7 = best / unrestricted) match the published Crary et al. 2005 FOIS. Non-oral tiers (levels 1-3) and total-oral tiers (levels 4-7) are correctly partitioned. Only cosmetic issue is a source typo in the level-6 label ("oucompensacoes" / concatenation), which does not change the clinical meaning. Frontend-only capture; no backend copy in this cluster.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFonoaudiologo.ts` | 146-181 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-scoring-FE-01-063`

**Related rules:** _none_

## Notes

Standard 7-point FOIS (Crary et al.). Level-6 label has a typo in source ("oucompensacoes"). Frontend-only capture; no backend copy found in this cluster.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
