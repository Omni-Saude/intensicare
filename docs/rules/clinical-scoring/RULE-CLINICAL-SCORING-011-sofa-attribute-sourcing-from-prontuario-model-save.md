# RULE-CLINICAL-SCORING-011 — SOFA attribute sourcing from prontuario (model.save)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
On save, SOFA copies raw values from the linked DadosProntuario before scoring; noradrenaline dose is read from the related Noradrenalina object; all six sub-scores and the total are recomputed every save().

## Inputs

| name | type |
|---|---|
| dados_prontuario | DadosProntuario |

## Outputs

| name | type |
|---|---|
| sofa fields | mixed |

## Logic

```text
fio2=dp.fio2; po2=dp.po2; plaquetas=dp.plaquetas; bilirrubinas=dp.bilirrubinas
pam = ((2*dp.pad)+dp.pas)/3 if (dp.pad and dp.pas) else 0
dobutamina = dp.dobutamina
if hasattr(dp,'noradrenalina'): noradrenalina = dp.noradrenalina.quantidade   # else stays previous/0
glasgow=dp.glasgow; debito_urinario_24h=dp.debito_urinario_24h; creatinina=dp.creatinina
then recompute pontos_criterio_1..6 and escore_sofa on every save()
```

## Edge cases (as implemented)

If no Noradrenalina relation exists, sofa.noradrenalina is NOT reset (keeps prior/default 0). Recomputed every save().

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Vincent JL, Moreno R, Takala J, et al. The SOFA (Sepsis-related Organ Failure Assessment) score to describe organ dysfunction/failure. Intensive Care Med. 1996;22(7):707-710. Standard MAP = (SBP + 2*DBP)/3. ([source](https://pubmed.ncbi.nlm.nih.gov/8844239/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| pad=80; pas=120 | 93.33 | 93.33 | yes |
| pad=60; pas=90 | 70.0 | 70.0 | yes |
| pad=0; pas=120 | MAP undefined (missing DBP) | 0 | yes |

**Verifier notes**

Workflow rule; the only closed-form clinical calculation is the embedded MAP expression, which matches the standard SOFA MAP formula exactly (algebraically identical to DBP+1/3(SBP-DBP)). All six organ inputs are sourced consistent with Vincent 1996. The FiO2 percentage-vs-fraction hazard and the noradrenalina-in-ml (not mcg/kg/min) sourcing are documented and adjudicated in RULE-008 and RULE-005 respectively and are not re-adjudicated here. The not-reset-when-no-Noradrenalina- relation behavior is an implementation quirk, not a reference deviation.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 40-67 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-003`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)
- [RULE-CLINICAL-SCORING-008](../physiological-calculation/RULE-CLINICAL-SCORING-008-pao2-fio2-ratio-relacao-po2-fio2.md)
- [RULE-CLINICAL-SCORING-009](../physiological-calculation/RULE-CLINICAL-SCORING-009-mean-arterial-pressure-pam-from-pas-pad.md)
- [RULE-CLINICAL-SCORING-012](RULE-CLINICAL-SCORING-012-sofa-score-input-assembly-first-movimentacao.md)

## Notes

noradrenaline dose here is Noradrenalina.quantidade (in ml), not a mcg/kg/min rate. The embedded MAP expression is catalogued as the reusable formula RULE-009.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
