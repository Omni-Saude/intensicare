# RULE-PROFILAXIA-005 — Prophylaxis v3 criterio_1 - GI stress-ulcer (LAMGD) prophylaxis indicated but absent (AMARELO)

| Field | Value |
|---|---|
| Cluster | profilaxia |
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
criterio_1 predicate: no PPI/cimetidine prescribed AND at least one stress-ulcer prophylaxis indication present (noradrenaline in balance; OR mechanical ventilation >48h; OR platelets <= 50000; OR no enteral/oral diet logged >24h; OR high-risk admission diagnosis).

## Inputs

| name | type | unit |
|---|---|---|
| cpoe.omeprazol/pantoprazol/esomeprazol/cimetidina; balanco.qt_vol_nora, qt_vol_dieta; evolucao.diurna_plaquetas, diurna_ventilacao, diag_inter_1..4 | float / string |  |

## Outputs

| name | type | unit |
|---|---|---|
| criterio_1 | boolean |  |

## Logic

```text
diagnosticos_intern = [
  "Traumatismo cranio-encefalico - TCE",
  "Acidente vascular cerebral isquemico - AVCi",
  "Acidente vascular cerebral hemorragico" "Grande queimado",   # implicit-concat bug -> single fused string
  "SEPSE",
  "Pos- operatorio recente de cirurgia abdominal",
  "Cirrose hepatica",
  "Hemorragia digestiva alta - HDA",
]
return any([
  all([ not get_number(cpoe.omeprazol), not get_number(cpoe.pantoprazol),
        not get_number(cpoe.esomeprazol), not get_number(cpoe.cimetidina),
        get_number(balanco.qt_vol_nora) ]),
  evolucao(dt_atualizacao >= now - 50h).annotate(vent=Lower(diurna_ventilacao))
        .filter(vent in ventilacao_mecanica | ventilacao_mecanica_invasiva),
  get_number(evolucao.diurna_plaquetas) <= 50000,
  not balanco(dt_atualizacao >= now - 26h).filter(qt_vol_dieta__gt=0).exists(),
  list(filter(lambda x: x in diagnosticos_intern,
       vars(ultima_evolucao).fromkeys(("diag_inter_1","diag_inter_2","diag_inter_3","diag_inter_4")))),  # inert
]) if (ultima_prescricao and ultimo_balanco and ultima_evolucao
       and evolucao_50h and balanco_26h) else False
```

## Edge cases (as implemented)

Documented "48h" ventilation window is implemented as now-50h; documented "24h" diet window is implemented as now-26h. The high-risk-diagnosis list membership check is non-functional: dict.fromkeys(("diag_inter_1"...)) iterates the literal KEY NAMES, never the evolucao field VALUES, so no real diagnosis is ever matched (per systemic finding RULE-systemic-BE-03-001). One list entry is a Python implicit-string-concatenation bug: "Acidente vascular cerebral hemorragico" "Grande queimado" fuse into a single string "Acidente vascular cerebral hemorragicoGrande queimado", merging two distinct diagnoses into one unmatchable entry.

## Divergence

Intent (docstring) vs implementation divergence: (1) docstring "ventilacao mecanica ha mais de 48h" but code uses timedelta(hours=50); (2) docstring "dieta ... ha mais de 24h" but code uses timedelta(hours=26); (3) the diagnosis-of-admission branch is inert (fromkeys iterates key names, not values) so that entire OR-clause never contributes; (4) string-concat bug fuses "hemorragico"+"Grande queimado". The PPI-absence+noradrenaline branch and the platelets<=50000 branch are sound and functional.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Cook DJ et al. "Risk Factors for Gastrointestinal Bleeding in Critically Ill Patients." N Engl J Med 1994;330:377-381 (Canadian Critical Care Trials Group). Two independent risk factors for clinically important GI bleeding: respiratory failure = mechanical ventilation >48h (OR 15.6) and coagulopathy = platelet count <50,000/mm3 OR INR >1.5 OR PTT >2x ULN (OR 4.3). ASPEN/ASHP stress-ulcer prophylaxis guidance adds high-risk conditions (TBI, extensive burns, sepsis, hepatic failure, GI bleed) as accepted additional indications. ([source](https://www.nejm.org/doi/full/10.1056/NEJM199402103300601))

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
| ventilation=invasive MV documented in an evolucao 60h old but updated within last 50h; PPI=absent; plaquetas=200000; dieta=logged; nora=absent | MV >48h present -> stress-ulcer prophylaxis indicated -> criterio_1 TRUE | branch2 (evolucao within now-50h with ventilation mode in MV set) contributes -> any() TRUE | yes |
| plaquetas=50000; ventilation=none; PPI=absent; dieta=logged; nora=absent; diag=none | Cook coagulopathy = platelets <50,000; exactly 50,000 is NOT coagulopathy -> criterio_1 FALSE | branch3 get_number(diurna_plaquetas) <= 50000 -> 50000<=50000 TRUE -> any() TRUE | no |
| diag_inter_1=Grande queimado; ventilation=none; plaquetas=200000; PPI=absent; dieta=logged; nora=absent | extensive burn is an accepted additional SUP indication -> criterio_1 TRUE | branch5 iterates dict.fromkeys(('diag_inter_1',...)) = the KEY NAME strings, never the field VALUES, so 'Grande queimado' is never tested; additionally the string-concat bug fuses 'Acidente vascular cerebral hemorragico'+'Grande queimado' into one unmatchable entry. Branch inert -> any() FALSE | no |
| ventilation=invasive MV but only evolucao is 52h old (outside now-50h window); everything else negative= | still ventilated >48h -> indication present -> TRUE | evolucao__mais_que_48hrs (dt >= now-50h) queryset empty; also empty queryset fails the guard 'and evolucao__mais_que_48hrs' -> predicate returns False | no |

**Verifier notes**

Confirmed against Cook 1994 verbatim. Four intent-vs-implementation divergences: (1) Ventilation window: reference/docstring "48h" but code uses timedelta(hours=50) - 2h looser; low impact on its own. (2) Platelet cutoff: code uses <=50000 while Cook's coagulopathy is platelets <50,000; at exactly 50,000 the legacy over-triggers by one boundary unit - none/low impact (arguably clinically conservative). (3) Diet-absence window: documented "24h" implemented as now-26h; the enteral- nutrition-absence branch has no single published cutoff (institutional), so this is an intent-vs-code divergence rather than a reference contradiction. (4) High-risk admission-diagnosis OR-clause is fully INERT: dict.fromkeys( ("diag_inter_1"..)) iterates the literal key-name strings, never the evolucao field values, so TBI/AVC/sepsis/burn/cirrhosis/HDA never contribute; compounded by a Python implicit-string-concat bug fusing "...hemorragico"+"Grande queimado" into one unmatchable string. This is the driver of the MODERATE rating: an entire recognized indication class (ASPEN/ASHP additional SUP conditions) is silently unable to raise the AMARELO alert, causing under-detection for patients who qualify ONLY via admission diagnosis. Mitigating factors keeping it below high: this is an advisory alert (not an order), and the two evidence-strongest Cook branches - PPI-absence+noradrenaline, and platelets<=50000 - remain sound and functional. Per-audit policy the legacy is documented, not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_profilaxia.py` | 192-281 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profilaxia-BE-03-092`

**Related rules:** _none_

## Notes

AMARELO criterion. Verified verbatim against source (concat bug at line 207; 50h at line 217; 26h at line 220; <=50000 at line 257). verify=true because it is an eligibility predicate with published clinical anchors (stress-ulcer prophylaxis indications: mechanical ventilation >48h and coagulopathy platelets<=50000). Recommendation/action text for this criterio_1 lives in the v3 facade RULE-PROFILAXIA-008; the v1 facade equivalent is criterio_1 in RULE-PROFILAXIA-007.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
