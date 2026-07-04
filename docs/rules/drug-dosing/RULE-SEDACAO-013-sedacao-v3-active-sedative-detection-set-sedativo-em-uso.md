# RULE-SEDACAO-013 — Sedacao v3 active-sedative detection (set_sedativo_em_uso)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Sets DS_SEDATIVO_CRITERIO_1 to the first non-zero sedative in a fixed priority order.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_mid/pro/fen/cet/dex | float | ml/h |

## Outputs

| name | type |
|---|---|
| DS_SEDATIVO_CRITERIO_1 | string enum {Midazolam, Propofol, Fentanil, Cetamina, Precedex} |

## Logic

```text
order = [(qt_vol_mid,"Midazolam"), (qt_vol_pro,"Propofol"), (qt_vol_fen,"Fentanil"),
         (qt_vol_cet,"Cetamina"), (qt_vol_dex,"Precedex")]
for key, label in order:
  if getattr(balanco, key, 0):
    DS_SEDATIVO_CRITERIO_1 = label
    break
```

## Edge cases (as implemented)

First-match wins by dict insertion order; Precedex label maps to qt_vol_dex (dexmedetomidina).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published reference. This is an internal UI/labeling business rule: pick the first non-zero continuous sedative in a fixed vendor-defined priority order (midazolam -> propofol -> fentanil -> cetamina -> dexmedetomidina/"Precedex") to populate the active-drug label DS_SEDATIVO_CRITERIO_1. No clinical guideline prescribes a drug-labeling precedence order. ([source](n/a))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_mid=5; qt_vol_pro=10 | Midazolam (first non-zero by dict order) | Midazolam | yes |
| qt_vol_mid=0; qt_vol_pro=8; qt_vol_dex=3 | Propofol (first non-zero) | Propofol | yes |
| qt_vol_dex=15; others=0 | Precedex (dex label) | Precedex | yes |

**Verifier notes**

Confirmed at source (trilha_sedacao.py:293-309): iterates a fixed-order dict and sets the label to the first drug with a non-zero infusion, then breaks (first-match wins). Behavior is internally self-consistent and deterministic, but there is no external clinical/published anchor for the precedence order or the "Precedex" trade-name mapping - it is proprietary business logic. Flagged for internal review; not treated as an error. Feeds the crit1 recommendation text (RULE-SEDACAO-025).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 293-309 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-041`

**Related rules:**

- [RULE-SEDACAO-005](RULE-SEDACAO-005-sedacao-v3-criterio-1-excessive-continuous-sedation-infusion.md)
- [RULE-SEDACAO-025](RULE-SEDACAO-025-sedative-specific-reduction-recommendation-criterio-1-free-t.md)
- [RULE-SEDACAO-026](RULE-SEDACAO-026-sedative-drug-enumeration-sedativo-nome-sedativo-choices.md)

## Notes

Called from criterio_1 (RULE-SEDACAO-005). Feeds the crit1 recommendation text (RULE-SEDACAO-025).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
