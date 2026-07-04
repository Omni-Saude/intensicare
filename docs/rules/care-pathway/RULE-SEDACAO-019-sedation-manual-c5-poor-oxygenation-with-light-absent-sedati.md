# RULE-SEDACAO-019 — Sedation manual C5 - poor oxygenation with light/absent sedation

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
Flags P/F<200 combined with light RASS (>= -2) or no sedative.

## Inputs

| name | type |
|---|---|
| relacao_po2_fio2 | float |
| rass | str enum |
| sedativos_present | boolean |

## Outputs

| name | type |
|---|---|
| criterio_5 | boolean |

## Logic

```text
criterio_5 = all([
  0 < relacao_po2_fio2 < 200,
  any([
    rass in ['-2','-1','0','+1','+2','+3','+4'],
    not verificar_existencia_sedativos,
  ]),
])
```

## Edge cases (as implemented)

Requires ratio strictly in (0,200). relacao==False excluded (0<False<200 is False).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published guideline defines this exact composite ("P/F<200 AND (RASS>=-2 OR no sedative)"). Embedded anchors: P/F<200 = Berlin moderate ARDS (ARDS Definition Task Force, JAMA 2012;307:2526); RASS scale -5..+4 with light-sedation target 0 to -2 (Sessler et al. Am J Respir Crit Care Med 2002;166:1338; SCCM PADIS Guidelines, Crit Care Med 2018;46:e825). ([source](https://jamanetwork.com/journals/jama/fullarticle/1160659))

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
| pf=150; rass=-1; sedative_present=true | true (moderate ARDS P/F<200 with light sedation RASS>=-2 = potential undersedation) | true (0<150<200 True; rass in light list True) | yes |
| pf=150; rass=-4; sedative_present=true | false (deep RASS -4, adequately sedated) | false (rass not in light list; sedative present so not-absent False) | yes |
| pf=250; rass=-1; sedative_present=true | false (P/F>=200 not <200) | false (0<250<200 False) | yes |
| pf=; rass=-1; sedative_present=false | false (no valid P/F) | false (0<False<200 False) | yes |

**Verifier notes**

Proprietary care-pathway composite; embedded numeric anchors are correct — P/F<200 matches Berlin moderate-ARDS boundary, RASS light-sedation enumeration matches the Sessler scale / PADIS light-target band. No code-vs-text discrepancy: both code (line 148) and current _REGRAS (line 26) use "<200" (_ANTIGAS_REGRAS had used <150 historically; superseded). Status OK preserved.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sedacao.py` | 145-157 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-10-015`

**Related rules:**

- [RULE-SEDACAO-020](RULE-SEDACAO-020-sedation-manual-c6-severity-without-sedation.md)
- [RULE-SEDACAO-021](../alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md)

## Notes

Test test_trilha_sedacao.py:134-146.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
