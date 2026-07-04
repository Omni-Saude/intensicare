# RULE-CLINICAL-SCORING-013 — Glasgow Coma Scale valid range (3-15)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
GCS total score constrained to the inclusive range 3..15 across the homecare neurological model (backend) and two frontend capture forms.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| escala_coma_glasgow / glasgow | int | points | 3-15 |

## Outputs

| name | type | unit |
|---|---|---|
| validated GCS | int | points |

## Logic

```text
Backend (trilha_homecare neurologica.escala_coma_glasgow):
  IntegerField(validators=[MinValueValidator(3), MaxValueValidator(15)])  # null/blank allowed
Frontend movimentacao (dados_prontuario.glasgow):
  { label: "Glasgow", type: "interval", min: 3, max: 15 }
Frontend physician neuro (avaliacao_neurologica.escala_coma_glasgow):
  { label: "ESCALA GLASGOW", type: "number", min: 3, max: 15 }
# inclusive bounds 3 (deep coma) .. 15 (fully alert); total GCS only (no E/V/M sub-scores)
```

## Edge cases (as implemented)

Inclusive bounds 3 and 15. Backend allows null (blank/null True). Total GCS only; component E/V/M sub-scores not modeled.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Teasdale G, Jennett B. Assessment of coma and impaired consciousness: a practical scale. Lancet. 1974;2(7872):81-84. Total GCS = eye(1-4) + verbal(1-5) + motor(1-6), inclusive range 3 (deep coma) to 15 (fully alert). ([source](https://pubmed.ncbi.nlm.nih.gov/4136544/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| glasgow=3 | valid (minimum, deep coma) | accepted (>=3) | yes |
| glasgow=15 | valid (maximum, fully alert) | accepted (<=15) | yes |
| glasgow=2 | invalid (below 3, impossible total GCS) | rejected (MinValueValidator 3) | yes |
| glasgow=16 | invalid (above 15) | rejected (MaxValueValidator 15) | yes |

**Verifier notes**

Inclusive 3..15 bounds match the Teasdale-Jennett total-GCS range exactly across backend model and both frontend capture forms. Total-score-only modeling (no E/V/M sub-scores) is a common valid design choice, not a reference deviation; the form-type descriptor difference (interval vs number vs IntegerField) is cosmetic. Note: the trilha_manual dados_prontuario.glasgow field (consumed by SOFA RULE-006) had no range validator captured in this cluster, so the 3-15 guard applies to the homecare/physician neuro path, not necessarily to the ICU SOFA input.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/formularios/avaliacoes/neurologica.py` | 19-24 | `8166c07eae` | primary |
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 43-48 | `f9656be266` | frontend-copy |
| trilhas-frontend | `src/utils/dataForms/dataFormFormularioMedico.ts` | 462-476 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-neuro-BE-06-001`
- `RULE-scoring-FE-01-019`
- `RULE-scoring-FE-01-037`

**Related rules:**

- [RULE-CLINICAL-SCORING-006](RULE-CLINICAL-SCORING-006-sofa-cns-sub-score-glasgow.md)

## Notes

Values reconcile exactly (3-15 inclusive) across all three; status OK. Only the form-type descriptor differs (movimentacao "interval" vs physician "number" vs backend IntegerField) — cosmetic, no clinical divergence. The two frontend captures target different backend fields: movimentacao->dados_prontuario.glasgow (trilha_manual/ICU), physician neuro->avaliacao_neurologica.escala_coma_glasgow (trilha_homecare, the merged backend validator here). No trilha_manual dados_prontuario.glasgow range validator was captured in this cluster.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
