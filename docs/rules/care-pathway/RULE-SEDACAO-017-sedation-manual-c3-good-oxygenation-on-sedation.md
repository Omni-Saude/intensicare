# RULE-SEDACAO-017 — Sedation manual C3 - good oxygenation on sedation

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Flags patient with P/F > 200 who is still on a sedative (candidate to lighten sedation).

## Inputs

| name | type | unit |
|---|---|---|
| relacao_po2_fio2 | float | ratio |
| sedativos_present | boolean |  |

## Outputs

| name | type |
|---|---|
| criterio_3 | boolean |

## Logic

```text
criterio_3 = all([
  verificar_relacao_po2_fio2 > 200,
  verificar_existencia_sedativos,
])
```

## Edge cases (as implemented)

relacao is False when no po2/fio2 -> False>200 -> False. Strict >200.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ARDS Definition Task Force (Ranieri VM et al.). Acute Respiratory Distress Syndrome: The Berlin Definition. JAMA 2012;307(23):2526-2533. Severity by PaO2/FiO2: mild 200<P/F<=300, moderate 100<P/F<=200, severe P/F<=100. P/F>200 => oxygenation is mild-ARDS-or-better (adequate), supporting sedation lightening per PADIS 2018 light-sedation goal. ([source](https://pubmed.ncbi.nlm.nih.gov/22797452/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| relacao_po2_fio2=250; sedative_present=true | true | true | yes |
| relacao_po2_fio2=200; sedative_present=true | false | false | yes |
| relacao_po2_fio2=180; sedative_present=true | false | false | yes |
| relacao_po2_fio2=false; sedative_present=true | false | false | yes |

**Verifier notes**

Confirmed at source (trilha_manual/models/trilha_sedacao.py:122-128). The strict >200 cutoff coincides exactly with the Berlin mild-ARDS lower bound (mild = 200<P/F<=300); P/F=200 correctly falls in the moderate band and is excluded, matching the reference boundary semantics. Units are a dimensionless ratio, consistent. No divergence on any checked dimension.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 122-128 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-013`

**Related rules:**

- [RULE-SEDACAO-018](RULE-SEDACAO-018-sedation-manual-c4-sedation-justified-by-severity.md)
- [RULE-SEDACAO-021](../alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)

## Notes

Test test_trilha_sedacao.py:75-85.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
