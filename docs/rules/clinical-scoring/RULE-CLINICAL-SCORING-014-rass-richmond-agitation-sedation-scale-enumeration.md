# RULE-CLINICAL-SCORING-014 — RASS (Richmond Agitation-Sedation Scale) enumeration

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
RASS sedation/agitation classification enumerating levels +4 (combative) to -5, stored as strings and consumed by sedation/ventilation criteria. Defined three times (trilha_manual, trilha_homecare, frontend) with divergent labels.

## Inputs

| name | type | range |
|---|---|---|
| rass | str enum | +4,+3,+2,+1,0,-1,-2,-3,-4,-5 and '' (see divergence) |

## Outputs

| name | type |
|---|---|
| label | str |

## Logic

```text
Canonical value -> label (trilha_manual RassChoices.definicao() and frontend select):
  +4 Combativo, +3 Muito agitado, +2 Agitado, +1 Inquieto, 0 Alerta e calmo,
  -1 Torporoso, -2 Sedado leve, -3 Sedado moderado, -4 Sedado profundamente, -5 Coma,
  '' Nao informado
# values stored as strings ("+4".."-5","0",""); classification only, no aggregation
```

## Edge cases (as implemented)

Sedation C2 uses ['-2','-3','-4','-5'] (deep); Sedation C5 uses ['-2','-1','0','+1','+2','+3','+4']; RASS -2 appears in BOTH sets (boundary overlap). Ventilacao C4/C8 parse int(rass) so '-2'->-2; '' would raise ValueError (guarded by `if rass`). The homecare enum omits '' so its consumers never see the empty sentinel.

## Divergence

Same logical scale defined in two backend modules + frontend, with divergent labels. trilha_manual (choices/indicadores.py RassChoices.definicao) and the frontend select agree EXACTLY on all 11 options including '' "Nao informado". trilha_homecare (choices/avaliacao_neurologica.rass) diverges: -1 = "Sonolento" (vs "Torporoso"), -4 = "Sedacao Intensa" (vs "Sedado profundamente"), -5 = "Nao desperta" (vs "Coma"), and OMITS the '' "Nao informado" option (10 options vs 11). Levels +4,+3,+2,+1,0,-2,-3 labels are identical across all three. Numeric scale identical everywhere.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Sessler CN, Gosnell MS, Grap MJ, et al. The Richmond Agitation-Sedation Scale: validity and reliability in adult intensive care unit patients. Am J Respir Crit Care Med. 2002;166(10):1338-1344. 10-point scale: +4 Combative, +3 Very agitated, +2 Agitated, +1 Restless, 0 Alert and calm, -1 Drowsy, -2 Light sedation, -3 Moderate sedation, -4 Deep sedation, -5 Unarousable. ([source](https://pubmed.ncbi.nlm.nih.gov/12421743/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| rass=+4 | Combative | manual/frontend 'Combativo', homecare 'Combativo' — consistent, matches reference intent | yes |
| rass=-1 | Drowsy | manual/frontend 'Torporoso' vs homecare 'Sonolento' — internal label divergence (same numeric -1) | no |
| rass=-5 | Unarousable | manual/frontend 'Coma' vs homecare 'Nao desperta' — internal label divergence | no |
| rass= | not a RASS level (sentinel) | manual/frontend include '' 'Nao informado'; homecare OMITS it (10 vs 11 options) | no |

**Verifier notes**

The numeric RASS scale (+4..-5, 10 levels) matches Sessler 2002 exactly in all three definitions, and downstream logic keys on the numeric string (int(rass) in ventilacao C4/C8; membership sets in sedation), so scoring behavior is reference-correct. The extracted DISCREPANCY is an intra-codebase label divergence, NOT a deviation of the numeric scale from the reference: trilha_homecare relabels -1 Sonolento / -4 Sedacao Intensa / -5 Nao desperta and omits '' Nao informado, while trilha_manual and the frontend agree on all 11 options. Clinical impact low: labels are display-only, the two enums feed different pathways (homecare -> neuro assessment; manual/frontend -> sedation/ventilation) and are never compared at runtime; homecare -1 'Sonolento' is arguably closer to the reference 'Drowsy' than manual 'Torporoso'. The load-bearing numeric anchors are correct everywhere.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/choices/indicadores.py` | 4-19 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_homecare/models/choices/avaliacao_neurologica.py` | 63-76 | `8166c07eae` | duplicate |
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 49-66 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-choice-BE-10-069`
- `RULE-neuro-BE-06-002`
- `RULE-scoring-FE-01-020`

**Related rules:**

- [RULE-CLINICAL-SCORING-006](RULE-CLINICAL-SCORING-006-sofa-cns-sub-score-glasgow.md)

## Notes

trilha_manual RassChoices.descricao() (indicadores.py:21-34) builds a malformed nested tuple (cosmetic; not used in logic) and adds per-level clinical descriptions. -1 "Torporoso" is a localization choice. Homecare RASS feeds the neurological assessment; manual/frontend RASS feeds sedation/ventilation.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
