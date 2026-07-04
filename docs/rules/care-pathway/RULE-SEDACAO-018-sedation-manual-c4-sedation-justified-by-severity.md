# RULE-SEDACAO-018 — Sedation manual C4 - sedation justified by severity

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Flags patient on a sedative who ALSO has P/F>=200 or EME or SHIC or PCR in last 24h.

## Inputs

| name | type |
|---|---|
| sedativos_present | boolean |
| relacao_po2_fio2 | float |
| eme | boolean |
| shic | boolean |
| pcr_24h | boolean |

## Outputs

| name | type |
|---|---|
| criterio_4 | boolean |

## Logic

```text
criterio_4 = all([
  verificar_existencia_sedativos,
  any([
    0 < relacao_po2_fio2 >= 200,   # chained: (0 < ratio) and (ratio >= 200)
    eme, shic, verificar_pcr_nas_ultimas_24hr(),
  ]),
])
```

## Edge cases (as implemented)

`0 < relacao >= 200` is a Python chained comparison meaning ratio>0 AND ratio>=200, i.e. ratio>=200. relacao==False -> 0<False is False.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published guideline defines this exact composite boolean ("sedative present AND (P/F>=200 OR EME OR SHIC OR PCR<24h)"). The only citable embedded anchor is the P/F 200 cutoff = Berlin Definition of ARDS boundary (moderate ARDS PaO2/FiO2 100-200; >200 = mild/none). ARDS Definition Task Force, JAMA 2012;307(23):2526-2533. ([source](https://jamanetwork.com/journals/jama/fullarticle/1160659))

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
| sedative_present=true; pf=250; eme=false; shic=false; pcr24=false | true (P/F>200, on sedative) | true (0<250>=200 -> True) | yes |
| sedative_present=true; pf=200; eme=false; shic=false; pcr24=false | false per _REGRAS text 'P/F>200' (200 not >200) | true (0<200>=200 -> 200>=200 True) | no |
| sedative_present=false; pf=300; eme=false; shic=false; pcr24=false | false (no sedative -> criterion N/A) | false (first all() term False) | yes |
| sedative_present=true; pf=; eme=true; shic=false; pcr24=false | true (EME severity marker) | true (any([0<False..., eme=True])) | yes |

**Verifier notes**

Proprietary care-pathway composite; flag for internal review, not treated as wrong. The chained comparison `0 < ratio >= 200` makes code effectively P/F>=200, whereas the model's own _REGRAS descriptive text (line 24) says "PO2/FiO2 > 200" — a one-value boundary inconsistency at exactly P/F=200 (this is the extraction-flagged AMBIGUOUS item). If severe-ARDS numeric intent is <200 boundary, the >=200 vs >200 divergence affects only the knife-edge P/F=200; clinically low. Embedded P/F 200 anchor itself matches the Berlin moderate-ARDS boundary. relacao==False (no PO2/FiO2) yields 0<False -> criterion false via that branch.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 130-143 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-014`

**Related rules:**

- [RULE-SEDACAO-021](../alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)
- [RULE-SEDACAO-022](RULE-SEDACAO-022-cardiac-arrest-within-last-24h-pcr-24h-helper-manual-model.md)

## Notes

AMBIGUOUS vs _REGRAS text "PO2/FiO2 > 200" - code effectively uses >=200 via the chained comparison. _ANTIGAS_REGRAS worded criterion 4 differently (ausencia de SDRA/EME/PCR/SHIC). Uses PCR helper RULE-SEDACAO-022. Test test_trilha_sedacao.py:96-125. Preserved verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
