# RULE-SEPSE-001 — SEPSE v1 alert maiores/menores dual threshold

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
SEPSE v1 alert from two criterion groups: 9 major (criterio_1..9) and 11 minor (criterio_10..20). Requires simultaneous major AND minor thresholds.

## Inputs

- criterio_1..9 (maiores) (int flag (1))
- criterio_10..20 (menores) (int flag (1))

## Outputs

- alerta (enum {VERMELHO, AMARELO, NEUTRO})

## Logic

```text
maiores = [criterio_1..criterio_9].count(1)
menores = [criterio_10..criterio_20].count(1)
if maiores >= 3 and menores >= 4: return "VERMELHO"
elif maiores >= 2 and menores >= 3: return "AMARELO"
else: return "NEUTRO"
```

## Edge cases (as implemented)

Uses AND between groups (both must clear). Contrast with v3 which uses OR (RULE-sepse-BE-03-100).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published reference defines the specific "N maiores AND M menores" aggregation. Closest external standards for the underlying screening concept: Bone RC et al. ACCP/SCCM Consensus (SIRS, "any >=2 of 4" pooled criteria), Chest 1992; Singer M et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3), JAMA 2016;315(8):801-810 (qSOFA "any >=2 of 3"); ILAS (Instituto Latino Americano de Sepse) screening protocol 2018. ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff-vs-external: proprietary. Published sepsis screening (SIRS/qSOFA) pools criteria and fires on "any >=2"; there is no authoritative source for a dual-axis (both groups must clear) threshold, nor for the specific values maiores>=3 & menores>=4 / >=2 & >=3. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| maiores=3; menores=4 | n/a (no external aggregation reference) | VERMELHO | n/a - matches rule logic |
| maiores=2; menores=3 | n/a | AMARELO | n/a - matches rule logic |
| maiores=5; menores=0 | SIRS/qSOFA would flag (>=5 pooled criteria); dual-AND logic does not | NEUTRO | n/a - proprietary divergence documented |
| maiores=2; menores=4 | n/a | AMARELO | n/a - >=3 majors needed for VERMELHO even with 4 minors |

**Verifier notes**

Internal business rule. count(1) counts int 1 (Python True==1 also counts). Logic hand-traced against legacy trilha4.py:139-174 and matches the catalog pseudocode exactly. The dual-axis AND aggregation is an institutional design choice with no published validation; flag for internal clinical review. Boundary {5,0}->NEUTRO: a patient meeting 5 of 9 major criteria but no minor criterion is not alerted, which is more conservative (lower sensitivity) than pooled SIRS/qSOFA screening. Structurally identical to RULE-SEPSE-004 (manual pathway); diverges from RULE-SEPSE-002 (v3) which uses OR.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilha4.py` | 139-174 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-014`

**Related rules:**

- [RULE-SEPSE-002](RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)
- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

v3 counterpart (TrilhaSepseV3Model.calcular_alerta) changed AND to OR - see notes on RULE-sepse-BE-03-100.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
