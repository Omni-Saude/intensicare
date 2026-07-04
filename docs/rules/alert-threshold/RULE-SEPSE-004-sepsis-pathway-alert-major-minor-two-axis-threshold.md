# RULE-SEPSE-004 — Sepsis pathway alert (major/minor two-axis threshold)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Sepsis alert requires simultaneous counts of "major" (C1-9) and "minor" (C10-20) criteria.

## Inputs

- maiores (int, count of C1..C9 True, 0-9)
- menores (int, count of C10..C20 True, 0-11)

## Outputs

- alerta (str enum {VERMELHO,AMARELO,NEUTRO})

## Logic

```text
maiores = count(True in [c1..c9]); menores = count(True in [c10..c20])
if maiores >= 3 and menores >= 4: 'VERMELHO'
elif maiores >= 2 and menores >= 3: 'AMARELO'
else: 'NEUTRO'
```

## Edge cases (as implemented)

BOTH axes must clear the bar simultaneously; e.g. many majors but 0 minors -> NEUTRO. AMARELO band requires maiores>=2 AND menores>=3.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published reference defines the "N maiores AND M menores" aggregation. External context: Bone RC et al. ACCP/SCCM (SIRS), Chest 1992; Singer M et al. Sepsis-3, JAMA 2016;315(8):801-810; ILAS screening protocol 2018. ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff-vs-external: proprietary dual-axis AND thresholds (maiores>=3 & menores>=4 -> VERMELHO; >=2 & >=3 -> AMARELO). Identical structure to v1 RULE-SEPSE-001. No authoritative source. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| maiores=3; menores=4 | n/a (legacy test test_trilha_sepse.py:337-360 expects VERMELHO) | VERMELHO | n/a - matches rule logic and legacy test |
| maiores=2; menores=3 | n/a (legacy test expects AMARELO) | AMARELO | n/a - matches rule logic and legacy test |
| maiores=5; menores=0 | SIRS/qSOFA would flag; dual-AND does not | NEUTRO | n/a - proprietary divergence documented |
| maiores=2; menores=2 | n/a | NEUTRO | n/a - needs menores>=3 for AMARELO |

**Verifier notes**

Internal business rule; aggregation identical to v1 (RULE-SEPSE-001). Hand-traced against trilha_manual/models/trilha_sepse.py:526-561; matches the catalog pseudocode and the shipped unit test (2 major+3 minor->AMARELO; 3 major+4 minor->VERMELHO). count(True) counts booleans. Flag for internal clinical review to reconcile the AND-vs-OR divergence with the v3 pathway (RULE-SEPSE-002).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 526-561 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-046`

**Related rules:**

- [RULE-SEPSE-001](../clinical-scoring/RULE-SEPSE-001-sepse-v1-alert-maiores-menores-dual-threshold.md)
- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-003](RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)
- [RULE-SEPSE-066](../triage-eligibility/RULE-SEPSE-066-sepsis-pathway-disabled-legacy-criteria-v-old-27-vs-current.md)
- [RULE-SEPSE-038](../triage-eligibility/RULE-SEPSE-038-sepsis-c1-major-fever.md)
- [RULE-SEPSE-039](../triage-eligibility/RULE-SEPSE-039-sepsis-c2-major-spontaneous-respiratory-distress.md)
- [RULE-SEPSE-040](../triage-eligibility/RULE-SEPSE-040-sepsis-c3-major-recent-start-of-mechanical-ventilation.md)
- [RULE-SEPSE-041](../triage-eligibility/RULE-SEPSE-041-sepsis-c4-major-noradrenaline-started-in-last-24h.md)
- [RULE-SEPSE-042](../triage-eligibility/RULE-SEPSE-042-sepsis-c5-major-slow-capillary-refill.md)
- [RULE-SEPSE-043](../triage-eligibility/RULE-SEPSE-043-sepsis-c6-major-hypotension-pas-90-or-pad-90-in-24h.md)
- [RULE-SEPSE-044](../triage-eligibility/RULE-SEPSE-044-sepsis-c7-major-oliguria-or-rising-creatinine.md)
- [RULE-SEPSE-045](../triage-eligibility/RULE-SEPSE-045-sepsis-c8-major-glasgow-drop-or-delirium.md)
- [RULE-SEPSE-046](../triage-eligibility/RULE-SEPSE-046-sepsis-c9-major-hyperbilirubinemia.md)
- [RULE-SEPSE-047](../triage-eligibility/RULE-SEPSE-047-sepsis-c10-minor-hypothermia-in-last-24h.md)
- [RULE-SEPSE-048](../triage-eligibility/RULE-SEPSE-048-sepsis-c11-minor-tachycardia.md)
- [RULE-SEPSE-049](../triage-eligibility/RULE-SEPSE-049-sepsis-c12-minor-hypocapnia-or-poor-oxygenation.md)
- [RULE-SEPSE-050](../triage-eligibility/RULE-SEPSE-050-sepsis-c13-minor-elevated-arterial-lactate.md)
- [RULE-SEPSE-051](../triage-eligibility/RULE-SEPSE-051-sepsis-c14-minor-leukocytosis-in-last-24h.md)
- [RULE-SEPSE-052](../triage-eligibility/RULE-SEPSE-052-sepsis-c15-minor-thrombocytopenia-in-last-24h.md)
- [RULE-SEPSE-053](../triage-eligibility/RULE-SEPSE-053-sepsis-c16-minor-poor-oral-intake-with-preserved-consciousne.md)
- [RULE-SEPSE-054](../triage-eligibility/RULE-SEPSE-054-sepsis-c17-minor-depressed-consciousness-in-last-12h.md)
- [RULE-SEPSE-055](../triage-eligibility/RULE-SEPSE-055-sepsis-c18-minor-central-line-7-days.md)
- [RULE-SEPSE-056](../triage-eligibility/RULE-SEPSE-056-sepsis-c19-minor-femoral-central-line-5-days.md)
- [RULE-SEPSE-057](../triage-eligibility/RULE-SEPSE-057-sepsis-c20-minor-recent-abdominal-surgery.md)

## Notes

Distinct from the other three pathways (which use a single count). Major set = criterio_1..9, minor set = criterio_10..20. Test test_trilha_sepse.py:337-360 (2 major+3 minor->AMARELO; 3 major+4 minor->VERMELHO).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
