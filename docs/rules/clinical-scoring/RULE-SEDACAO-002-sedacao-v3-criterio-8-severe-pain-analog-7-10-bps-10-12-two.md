# RULE-SEDACAO-002 — Sedacao v3 criterio_8 - severe pain (analog 7-10 / BPS 10-12), two consecutive

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Pain score 7-10 on the VISUAL analog scale OR 10-12 on the COMPORTAMENTAL (BPS, sedated adult) scale, present in BOTH of the last two consecutive fluid-balance records. VERMELHO criterion in the wired v3 alert (calcular_alerta_v2).

## Inputs

| name | type | unit | values |
|---|---|---|---|
| balanco.escala_dor | string |  | VISUAL \| COMPORTAMENTAL |
| balanco.ponto_dor | float | pain points |  |

## Outputs

| name | type |
|---|---|
| criterio_8 | boolean |

## Logic

```text
def paind(b):
  return (b.escala_dor == "VISUAL"        and 7  <= get_number(b.ponto_dor) <= 10) or \
         (b.escala_dor == "COMPORTAMENTAL" and 10 <= get_number(b.ponto_dor) <= 12)
return all([ any([paind(ultimo_balanco)]),
             any([paind(balanco_anterior)]) ]) if ultimo_balanco and balanco_anterior else False
```

## Edge cases (as implemented)

VISUAL range 7-10 abuts criterio_7's 4-6 at the value 7 (both inclusive). Both balances required.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Numeric/Visual Analog pain bands (7-10 severe) per SCCM PADIS 2018 pain-assessment standard; BPS total range 3-12 (Payen 2001), top of range = maximal observed pain. ([source](https://www.weguide.health/instruments/behavioral-pain-scale-bps))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | VISUAL 7-10 matches standard NRS severe band; BPS 10-12 is institutional top sub-band within valid 3-12 range |
| units | ok |
| ranges | ok - 10-12 is the upper third of BPS 3-12; 7-10 upper third of NRS 0-10 |
| rounding | n/a |
| cutoffs | VISUAL 7-10 matches reference severe band; BPS 10-12 institutional but consistent |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| escala_dor=VISUAL; ponto_dor=7; both_balances=true | severe (lower bound) -> True | 7<=7<=10 True -> True | yes |
| escala_dor=VISUAL; ponto_dor=10; both_balances=true | severe (max) -> True | True | yes |
| escala_dor=COMPORTAMENTAL; ponto_dor=12; both_balances=true | BPS max = severe -> True | 10<=12<=12 True -> True | yes |
| escala_dor=COMPORTAMENTAL; ponto_dor=9; both_balances=true | belongs to moderate band (crit_7), not severe | 9 not in 10-12 -> False | yes |

**Verifier notes**

VISUAL 7-10 matches the published NRS severe band exactly and abuts crit_7's 4-6 cleanly (6|7 boundary, no overlap - the edge_cases note wording is imprecise but the intervals are disjoint). BPS 10-12 is an institutional top sub-band, within valid range and consistent. Both consecutive balances required. Verified against source lines 634-685.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 634-685 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-049`

**Related rules:**

- [RULE-SEDACAO-001](RULE-SEDACAO-001-sedacao-v3-criterio-7-moderate-pain-analog-4-6-bps-7-9-two-c.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)
- [RULE-SEDACAO-024](../drug-dosing/RULE-SEDACAO-024-sedation-analgesia-pathway-recommendation-catalog-facade-tex.md)

## Notes

VERMELHO criterion (wired). Verified against source.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
