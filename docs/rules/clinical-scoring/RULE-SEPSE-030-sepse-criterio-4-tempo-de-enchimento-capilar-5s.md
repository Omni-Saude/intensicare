# RULE-SEPSE-030 — Sepse criterio_4 - Tempo de enchimento capilar > 5s

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Major criterion 4 fires when the linked nursing evolution's physical exam lists 'tec_5s' (capillary refill time > 5 seconds).

## Inputs

- evolucao.exame_fisico.tipos_exame (array[enum])

## Outputs

- criterio_4 (boolean)

## Logic

```text
tipos_exames = evolucao.exame_fisico.tipos_exame if (evolucao and hasattr(evolucao, "exame_fisico")) else []
if tipos_exames:
    return "tec_5s" in tipos_exames
return False
```

## Edge cases (as implemented)

Returns False if no evolucao, no exame_fisico relation, or empty list.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Capillary refill time (CRT): normal <= 3 s; CRT > 3 s is the perfusion-abnormality / hypoperfusion target used in ANDROMEDA-SHOCK (Hernandez G et al., JAMA 2019;321(7):654-664) and the ANDROMEDA-SHOCK-2 protocol. Legacy fires only at CRT > 5 s. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC9345585/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok (seconds) |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff (legacy fires at >5 s; published abnormal/hypoperfusion cutoff is >3 s) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| tipos_exame=["tec_5s"] | abnormal perfusion True (>3 s reference; certainly abnormal at >5 s) | True ('tec_5s' in list) | yes |
| tipos_exame=["tec_3s"] | abnormal True per ANDROMEDA-SHOCK (>3 s) | False ('tec_5s' not in list) | no |
| tipos_exame=[] | False (normal perfusion) | False | yes |
| evolucao= | n/a (no data) | False (no exame_fisico relation) | yes |

**Verifier notes**

Legacy fires this major criterion only at CRT > 5 s, whereas the published perfusion-abnormality threshold is > 3 s (ANDROMEDA-SHOCK). Patients with moderately prolonged CRT (3-5 s), an evidence-based marker of hypoperfusion, do NOT trigger the criterion, potentially missing early tissue-hypoperfusion signal. Impact LOW because (a) it is one of several major criteria feeding the aggregate alert and (b) a stricter >5 s cutoff for a MAJOR criterion is a defensible specificity trade-off (the exame choice label is literally 'TEC > 5s'). Documented as a threshold difference vs the reference; not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 168-176 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-004`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

The 'tec_5s' choice is defined in FormularioChoices.tipo_exame() with label "TEC > 5s".

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
