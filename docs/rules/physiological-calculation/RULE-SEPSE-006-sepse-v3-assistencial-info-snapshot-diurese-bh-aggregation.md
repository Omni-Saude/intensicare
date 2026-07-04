# RULE-SEPSE-006 — SEPSE v3 assistencial info snapshot (diurese/BH aggregation)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Confidence | medium |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Builds a clinical snapshot including 24h urine output and 24h fluid balance from summed balance fields.

## Inputs

- balanco.qt_vol_espontanea/svd/cistostomia, qt_vol_ganhos, qt_vol_perdas (float, mL)

## Outputs

- diurese_24h (float, mL)
- balanco_hidrico_24h (float, mL)

## Logic

```text
diurese_24h = Sum(qt_vol_espontanea + qt_vol_svd + qt_vol_cistostomia) over balancos(dt>=now-24h)
balanco_hidrico_24h = Sum(qt_vol_ganhos + qt_vol_perdas) over balancos(dt>=now-24h)
# delirium/noradrenalina rendered as "Presente"/"Ausente" via presenca map on bool(value)
```

## Edge cases (as implemented)

balanco_hidrico_24h ADDS ganhos + perdas (does not subtract) - net balance would normally be ganhos - perdas; here perdas is expected pre-signed or this yields a sum, not a net.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** Fluid balance is definitionally net = intake (ganhos) - output (perdas); 24h urine output is the sum of all urine sources. No proprietary published equation governs this internal snapshot aggregation. General reference: standard ICU fluid-balance charting (intake minus output). ([source](https://www.ncbi.nlm.nih.gov/books/NBK541123/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | ok |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_espontanea=1000; qt_vol_svd=0; qt_vol_cistostomia=0 | diurese_24h = 1000 mL (sum of urine sources) | diurese_24h = 1000 + 0 + 0 = 1000 mL | yes |
| qt_vol_ganhos=2000; qt_vol_perdas=1500 | net balanco_hidrico = ganhos - perdas = +500 mL (if perdas is an unsigned volume) | balanco_hidrico_24h = 2000 + 1500 = 3500 mL (ADDS, does not subtract) | no |
| qt_vol_ganhos=2000; qt_vol_perdas=-1500 | net balanco_hidrico = +500 mL | balanco_hidrico_24h = 2000 + (-1500) = 500 mL | yes |

**Verifier notes**

diurese_24h (urine output sum) is correct and matches the standard definition. balanco_hidrico_24h ADDS ganhos + perdas rather than subtracting; correctness depends entirely on the internal data convention for the sign of qt_vol_perdas (if losses are stored pre-signed negative the sum equals net balance; if stored as positive volumes the result is a gross total, not a net balance). This is an internal aggregation with no authoritative published equation to adjudicate the sign convention, hence UNVERIFIABLE. Additionally the method is not wired into get_detalhe (call commented out at line 301), so it is inert in production. Flag for internal review of the perdas sign convention.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 121-177 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-122`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)

## Notes

Method currently not wired into get_detalhe (call commented out at line 301).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
