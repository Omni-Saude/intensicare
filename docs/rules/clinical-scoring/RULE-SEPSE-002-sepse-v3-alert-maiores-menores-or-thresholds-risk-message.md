# RULE-SEPSE-002 — SEPSE v3 alert maiores/menores (OR thresholds) + risk message

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
SEPSE v3 alert from 11 major (criterio_1..11) and 9 minor (criterio_12..20) criteria; VERMELHO when either major>=3 OR minor>=4; AMARELO when major>=2 OR minor>=3. Also emits a risk message.

## Inputs

- criterio_1..11 (maiores) (boolean)
- criterio_12..20 (menores) (boolean)

## Outputs

- alerta (enum {VERMELHO, AMARELO, NEUTRO})
- mensagem (string)

## Logic

```text
maiores = [criterio_1..criterio_11].count(True)
menores = [criterio_12..criterio_20].count(True)
if maiores >= 3 or menores >= 4: alerta = "VERMELHO"
elif maiores >= 2 or menores >= 3: alerta = "AMARELO"
else: alerta = "NEUTRO"
mensagem = "" if NEUTRO else ("Moderado risco para SEPSE." if AMARELO else "Alto risco para SEPSE.")
# save(): if alerta == "NEUTRO": assistido = False
```

## Edge cases (as implemented)

count(True) only counts boolean True. Group boundary changed vs v1.

## Divergence

v1 (RULE-SEPSE-001) requires maiores AND menores (>=3 AND >=4 -> VERMELHO; >=2 AND >=3 -> AMARELO); v3 uses OR (maiores>=3 OR menores>=4 -> VERMELHO; >=2 OR >=3 -> AMARELO) and shifts the major group to 11 criteria (criterio_11 moved from minor to major).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** No external reference for the aggregation. The flagged discrepancy is INTERNAL (v3 vs v1). External screening context: Singer M et al. Sepsis-3, JAMA 2016;315(8):801-810; Evans L et al. Surviving Sepsis Campaign: International Guidelines 2021, Crit Care Med 2021;49(11):e1063-e1143. ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff-INTERNAL: v3 uses OR (maiores>=3 OR menores>=4 -> VERMELHO; >=2 OR >=3 -> AMARELO) whereas v1/manual (RULE-SEPSE-001/004) use AND, and v3 regroups criterio_11 from minor to major (11 major / 9 minor). Confirmed by hand-trace of trilha_sepse.py:187-231. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| maiores=3; menores=0 | v1/manual (AND) -> NEUTRO | VERMELHO (mensagem: 'Alto risco para SEPSE.') | no |
| maiores=0; menores=4 | v1/manual (AND) -> NEUTRO | VERMELHO | no |
| maiores=2; menores=0 | v1/manual (AND) -> NEUTRO | AMARELO (mensagem: 'Moderado risco para SEPSE.') | no |
| maiores=1; menores=1 | NEUTRO (both approaches) | NEUTRO | yes |

**Verifier notes**

CONFIRMED (internal cross-version discrepancy, extraction flag upheld). The aggregation math has no authoritative external reference, so it is not "wrong" against published literature; however the v3 OR-logic materially diverges from the v1/manual AND-logic for the SAME nominal sepsis screen. Effect: OR-logic fires on either axis alone, so v3 flags substantially MORE patients than v1 (higher sensitivity, lower specificity). This is the safer direction for sepsis (a missed sepsis is high-harm), and OR/pooled logic is actually closer to SIRS/qSOFA "any-N" screening than v1's dual-AND. Impact moderate because the two shipped pathways classify the identical patient differently. save(): when alerta=='NEUTRO' the record sets assistido=False.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 187-231 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-100`

**Related rules:**

- [RULE-SEPSE-001](RULE-SEPSE-001-sepse-v1-alert-maiores-menores-dual-threshold.md)
- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)
- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)
- [RULE-SEPSE-058](../alert-threshold/RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)
- [RULE-SEPSE-007](../alert-threshold/RULE-SEPSE-007-sepse-v3-criterio-1-fever-without-vasopressor.md)
- [RULE-SEPSE-008](../alert-threshold/RULE-SEPSE-008-sepse-v3-criterio-2-tachypnea-hypoxemia-without-vasopressor.md)
- [RULE-SEPSE-009](../alert-threshold/RULE-SEPSE-009-sepse-v3-criterio-3-respiratory-failure-prescription.md)
- [RULE-SEPSE-010](../alert-threshold/RULE-SEPSE-010-sepse-v3-criterio-4-newly-started-vasopressor.md)
- [RULE-SEPSE-011](../alert-threshold/RULE-SEPSE-011-sepse-v3-criterio-5-hypotension-without-vasopressor.md)
- [RULE-SEPSE-012](../alert-threshold/RULE-SEPSE-012-sepse-v3-criterio-6-thrombocytopenia-without-vasopressor.md)
- [RULE-SEPSE-013](../alert-threshold/RULE-SEPSE-013-sepse-v3-criterio-7-hyperlactatemia-without-vasopressor.md)
- [RULE-SEPSE-014](../physiological-calculation/RULE-SEPSE-014-sepse-v3-criterio-8-oliguria-without-vasopressor-dialysis.md)
- [RULE-SEPSE-015](../alert-threshold/RULE-SEPSE-015-sepse-v3-criterio-9-acute-kidney-injury-without-vasopressor.md)
- [RULE-SEPSE-016](../alert-threshold/RULE-SEPSE-016-sepse-v3-criterio-10-acute-encephalopathy-delirium.md)
- [RULE-SEPSE-017](../alert-threshold/RULE-SEPSE-017-sepse-v3-criterio-11-hyperbilirubinemia-jaundice-incomplete.md)
- [RULE-SEPSE-018](../alert-threshold/RULE-SEPSE-018-sepse-v3-criterio-12-hypothermia-minor.md)
- [RULE-SEPSE-019](../alert-threshold/RULE-SEPSE-019-sepse-v3-criterio-13-tachycardia-minor-wrong-column.md)
- [RULE-SEPSE-020](../alert-threshold/RULE-SEPSE-020-sepse-v3-criterio-14-respiratory-alkalosis-hypoxemia-spontan.md)
- [RULE-SEPSE-021](../alert-threshold/RULE-SEPSE-021-sepse-v3-criterio-15-leukocytosis-leukopenia-bandemia-crp-mi.md)
- [RULE-SEPSE-022](../alert-threshold/RULE-SEPSE-022-sepse-v3-criterio-16-prolonged-capillary-refill-minor-new-on.md)
- [RULE-SEPSE-023](../alert-threshold/RULE-SEPSE-023-sepse-v3-criterio-17-enteral-tube-with-adequate-gcs-minor.md)
- [RULE-SEPSE-024](../alert-threshold/RULE-SEPSE-024-sepse-v3-criterio-18-central-line-7-days-minor.md)
- [RULE-SEPSE-025](../alert-threshold/RULE-SEPSE-025-sepse-v3-criterio-19-femoral-central-line-5-days-minor.md)
- [RULE-SEPSE-026](../alert-threshold/RULE-SEPSE-026-sepse-v3-criterio-20-recent-abdominal-surgery-minor.md)

## Notes

DISCREPANCY vs v1 (RULE-sepse-BE-03-014): v1 required maiores AND menores; v3 uses OR and also shifts the major group to 11 criteria (criterio_11 moved from minor to major). Numbered 100 to cross-reference the 20 v3 criteria below.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
