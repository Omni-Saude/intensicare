# RULE-CLINICAL-SCORING-012 — SOFA score input assembly (first movimentacao)

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
Builds the input set for the SOFA organ-dysfunction score from prontuario data plus the noradrenaline dose, on first admission (use-case layer).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| fio2 | number | fraction/percent |  |
| po2 | number | mmHg |  |
| plaquetas | number | x10^3/uL |  |
| bilirrubinas | number | mg/dL |  |
| pam | number | mmHg |  |
| dobutamina | number | dose |  |
| glasgow | integer | GCS points | 3-15 (not enforced here) |
| debito_urinario_24h | number | mL/24h |  |
| creatinina | number | mg/dL |  |
| noradrenalina | number | dose (quantidade) |  |

## Outputs

| name | type |
|---|---|
| SOFA record | model |

## Logic

```text
dados = {}
if prontuario has noradrenalina: dados["noradrenalina"] = prontuario.noradrenalina.quantidade
for item in [fio2, po2, plaquetas, bilirrubinas, pam, dobutamina, glasgow, debito_urinario_24h, creatinina]:
    dados[item] = serializer.data.get(item)
SOFA.objects.create(dados_prontuario=prontuario.instance, **dados)
# on ValidationError -> raise {"escore_sofa": "...erro na criacao do escore sofa..."}
```

## Edge cases (as implemented)

The actual SOFA point computation happens inside the SOFA model save (RULE-011). This rule captures WHICH variables feed SOFA and that the noradrenaline dose is included only when a noradrenalina record exists.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Vincent JL, Moreno R, Takala J, et al. The SOFA score. Intensive Care Med. 1996;22(7):707-710. Six organ systems: respiratory (PaO2/FiO2), coagulation (platelets), hepatic (bilirubin), cardiovascular (MAP + vasopressors), neurological (GCS), renal (creatinine / urine output). ([source](https://pubmed.ncbi.nlm.nih.gov/8844239/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| assembled=fio2,po2 | respiratory organ covered by PaO2/FiO2 | fio2 + po2 collected | yes |
| assembled=pam,dobutamina,noradrenalina | cardiovascular = MAP + vasopressor requirement | pam, dobutamina, and (conditionally) noradrenalina.quantidade collected | yes |
| assembled=creatinina,debito_urinario_24h | renal = creatinine OR 24h urine output | creatinina + debito_urinario_24h collected | yes |

**Verifier notes**

Input-assembly workflow. All six SOFA organ systems from Vincent 1996 are represented by the collected variables and mapped to the correct organs; the noradrenaline dose is included only when a Noradrenalina record exists, matching RULE-011. This rule does not compute points, so the unit hazards flagged elsewhere (FiO2 fraction-vs-percent RULE-008; noradrenalina in ml RULE-005) are inherited downstream, not introduced here. Assembly is faithful to the reference.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/movimentacao/cadastrar_primeira_movimentacao.py` | 132-159 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-04-038`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)
- [RULE-CLINICAL-SCORING-011](RULE-CLINICAL-SCORING-011-sofa-attribute-sourcing-from-prontuario-model-save.md)

## Notes

SOFA components implied: PaO2/FiO2 (po2,fio2), platelets, bilirubin, MAP+vasopressors (pam, dobutamina, noradrenalina), GCS (glasgow), renal (creatinina, debito_urinario_24h). NovaMovimentacao instead clones+recalculates the prior SOFA via atualizar_atributos_sofa (RULE-011).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
