# RULE-SEDACAO-020 — Sedation manual C6 - severity without sedation

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Flags absence of sedative while patient has poor P/F (<200) or SHIC or PCR-24h or EME.

## Inputs

| name | type |
|---|---|
| sedativos_present | boolean |
| relacao_po2_fio2 | float |
| shic | boolean |
| eme | boolean |
| pcr_24h | boolean |

## Outputs

| name | type |
|---|---|
| criterio_6 | boolean |

## Logic

```text
criterio_6 = all([
  not verificar_existencia_sedativos,
  any([
    0 < relacao_po2_fio2 < 200,
    shic, verificar_pcr_nas_ultimas_24hr(), eme,
  ]),
])
```

## Edge cases (as implemented)

If any sedative exists -> False regardless.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published guideline defines this exact composite ("no sedative AND (P/F<200 OR SHIC OR PCR<24h OR EME)"). Embedded anchor: P/F<200 = Berlin moderate ARDS (ARDS Definition Task Force, JAMA 2012;307:2526-2533). ([source](https://jamanetwork.com/journals/jama/fullarticle/1160659))

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
| sedative_present=false; pf=150; shic=false; pcr24=false; eme=false | true (severity P/F<200 without sedation) | true (not-sedative True; 0<150<200 True) | yes |
| sedative_present=true; pf=150; shic=false; pcr24=false; eme=false | false (sedative present) | false (first all() term 'not sedative' False) | yes |
| sedative_present=false; pf=250; shic=false; pcr24=false; eme=false | false (P/F>=200, no other severity marker) | false (any([0<250<200 False, all others False])) | yes |
| sedative_present=false; pf=; shic=false; pcr24=false; eme=true | true (EME severity marker, no sedation) | true (any([...,eme True])) | yes |

**Verifier notes**

Proprietary care-pathway composite; embedded P/F<200 anchor matches Berlin moderate-ARDS boundary. Code (line 165) and current _REGRAS (line 27) both use "<200"; _ANTIGAS_REGRAS text (line 16) said "<150" but is the superseded variant, so current code and current rule text agree. Status OK preserved.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 159-172 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-016`

**Related rules:**

- [RULE-SEDACAO-019](RULE-SEDACAO-019-sedation-manual-c5-poor-oxygenation-with-light-absent-sedati.md)
- [RULE-SEDACAO-021](../alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)
- [RULE-SEDACAO-022](RULE-SEDACAO-022-cardiac-arrest-within-last-24h-pcr-24h-helper-manual-model.md)

## Notes

_REGRAS text says "PO2/FiO2 < 200" while _ANTIGAS_REGRAS said "< 150" - code uses < 200 (matches current _REGRAS). Uses PCR helper RULE-SEDACAO-022. Test test_trilha_sedacao.py:148-168.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
