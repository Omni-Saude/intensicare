# RULE-SEDACAO-009 — Sedacao v3 criterio_5 - no morning sedation reduction (>=1/2)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Sedative present at the latest balance AND no reduction of at least half between the 06:00 and 10:00 balances (for midazolam/propofol/cetamina/dexmedetomidina). Wired AMARELO criterion.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_mid/pro/cet/dex at 06:00 and last<=10:00, plus latest | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_5 | boolean |

## Logic

```text
balanco_range = balancos(06:00 <= dt <= 10:00 today, local tz) order by dt asc
primeiro       = balanco_range.first()
ultimo_ate_10  = balanco_range.last()
ultimo         = balancos.first()
per drug D in {mid, pro, cet, dex}:
  cond_D = get_number(ultimo.D) and not (get_number(primeiro.D) - get_number(ultimo_ate_10.D)) <= get_number(primeiro.D)/2
return all([ any([cond_mid, cond_pro, cond_cet, cond_dex]) ]) if ultimo and ultimo_ate_10 and primeiro else False
```

## Edge cases (as implemented)

Operator-precedence sensitive: "X and not (A - B) <= C" parses as X and (not ((A-B) <= C)); a reduction strictly greater than half flags true, and "reduced to exactly half" is NOT a failure. Uses local today 06:00-10:00 window via datetime.combine(...).astimezone().

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Devlin JW et al. PADIS Guidelines. Crit Care Med 2018 (daily awakening trials / spontaneous awakening trials, target light sedation). Kress JP et al. Daily interruption of sedative infusions. NEJM 2000;342:1471-1477. ([source](https://pubmed.ncbi.nlm.nih.gov/30113379/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff - implemented reduction test is logically inverted vs its documented intent |
| coefficients | n/a (reduction threshold 'half' is an institutional protocol value, no published numeric anchor) |
| units | ok - all volumes ml/h, same drug compared across the 06:00-10:00 window |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff - operator precedence makes the alert fire on the OPPOSITE condition (see notes/vectors) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| drug=midazolam; primeiro_06h=10; ultimo_ate_10h=10; ultimo_latest=10 | Docstring example: 10 ml/h at 06h still 10 ml/h later, NO reduction -> should FLAG (AMARELO: sedation not weaned) | reduction=10-10=0; not(0<=10/2=5)=not True=False; cond = 10 and False = False -> criterio_5=False (does NOT flag) | no |
| drug=midazolam; primeiro_06h=10; ultimo_ate_10h=4; ultimo_latest=4 | Reduced 10->4 (below half, adequate weaning) -> should NOT flag | reduction=6; not(6<=5)=not False=True; cond = 4 and True = True -> criterio_5=True (FLAGS a well-weaned patient) | no |
| drug=midazolam; primeiro_06h=10; ultimo_ate_10h=5; ultimo_latest=5 | Reduced exactly to half (adequate) -> should NOT flag | reduction=5; not(5<=5)=not True=False; cond=5 and False=False -> criterio_5=False (agrees only by boundary coincidence) | yes |

**Verifier notes**

WIRED AMARELO criterion (calcular_alerta_v2 amarelo=[criterio_5, criterio_7]; criterio_5 IS computed by calcular_criterios), so the defect is live, not inert. Per Python precedence the per-drug clause parses as `present and (not ((primeiro - ultimo_ate_10) <= primeiro/2))` = present AND (reduction > half). Intended alert ('ausencia de reducao >=1/2' -> flag when the drug was NOT reduced by at least half) is reduction < half. The implementation is INVERTED: it stays silent when there was no reduction (the exact case it should catch, vector 1) and fires when the infusion was appropriately reduced by more than half (vector 2). The 'reduce by half by 06h' threshold itself is an institutional protocol value (no published numeric anchor), but the daily-sedation-reduction concept aligns with PADIS daily awakening trials / Kress 2000. Impact moderate: as a wired advisory yellow alert the inversion causes missed 'not-weaned' alerts and false alarms on well-managed patients; it prompts clinician review rather than triggering automated dosing. Extraction status AMBIGUOUS is here characterized as a directional inversion of a wired alert.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 447-537 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-046`

**Related rules:**

- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

AMARELO criterion (wired). Convoluted logic; boundary and precedence flagged AMBIGUOUS. Preserved verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
