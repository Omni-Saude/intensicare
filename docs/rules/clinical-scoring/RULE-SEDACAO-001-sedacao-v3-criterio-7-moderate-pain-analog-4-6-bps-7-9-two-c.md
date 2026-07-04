# RULE-SEDACAO-001 — Sedacao v3 criterio_7 - moderate pain (analog 4-6 / BPS 7-9), two consecutive

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
Pain score 4-6 on the VISUAL analog scale OR 7-9 on the COMPORTAMENTAL (BPS, sedated adult) scale, present in BOTH of the last two consecutive fluid-balance records. AMARELO criterion in the wired v3 alert (calcular_alerta_v2).

## Inputs

| name | type | unit | values |
|---|---|---|---|
| balanco.escala_dor | string |  | VISUAL \| COMPORTAMENTAL |
| balanco.ponto_dor | float | pain points |  |

## Outputs

| name | type |
|---|---|
| criterio_7 | boolean |

## Logic

```text
def paind(b):
  return (b.escala_dor == "VISUAL"        and 4 <= get_number(b.ponto_dor) <= 6) or \
         (b.escala_dor == "COMPORTAMENTAL" and 7 <= get_number(b.ponto_dor) <= 9)
return all([ any([paind(ultimo_balanco)]),
             any([paind(balanco_anterior)]) ]) if ultimo_balanco and balanco_anterior else False
```

## Edge cases (as implemented)

Requires the condition true in BOTH consecutive balances (balancos[0] and balancos[1]). Inclusive bounds. Wired via calcular_criterios.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Numeric/Visual Analog pain bands (0-3 none/mild, 4-6 moderate, 7-10 severe) per SCCM PADIS 2018 guideline pain-assessment standard; Behavioral Pain Scale (BPS) total range 3-12 (Payen JL et al. Crit Care Med 2001), significant/unacceptable pain cutoff >5. ([source](https://www.weguide.health/instruments/behavioral-pain-scale-bps))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | VISUAL 4-6 matches standard NRS moderate band; BPS 7-9 is an institutional sub-band (BPS has no published moderate/severe sub-bands, only cutoff >5) |
| units | ok (pain points; VISUAL=NRS 0-10, COMPORTAMENTAL=BPS 3-12) |
| ranges | ok - 7-9 lies within valid BPS range 3-12; 4-6 within NRS 0-10 |
| rounding | n/a |
| cutoffs | VISUAL 4-6 matches reference moderate band exactly; BPS 7-9 institutional but clinically consistent (all >5 cutoff) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| escala_dor=VISUAL; ponto_dor=4; both_balances=true | moderate pain -> True | 4<=4<=6 True in both -> True | yes |
| escala_dor=VISUAL; ponto_dor=6; both_balances=true | moderate (upper bound) -> True | True | yes |
| escala_dor=VISUAL; ponto_dor=7; both_balances=true | severe not moderate -> False here | 7 not in 4-6 -> False | yes |
| escala_dor=COMPORTAMENTAL; ponto_dor=8; both_balances=true | BPS 8 >5 = significant pain -> plausibly moderate True | 7<=8<=9 True -> True | yes |
| escala_dor=COMPORTAMENTAL; ponto_dor=6; both_balances=true | BPS 6 >5 = pain present (institutional split puts it below moderate band) | 6 not in 7-9 -> False | yes |

**Verifier notes**

VISUAL band 4-6 matches the published NRS moderate band exactly. The COMPORTAMENTAL (BPS) sub-band 7-9 is an institutional subdivision of the validated 3-12 BPS scale; BPS itself only publishes a single actionable cutoff (>5). The 7-9 band is internally consistent (all values exceed the >5 cutoff) and within range, so no reference conflict. Requires condition True in both consecutive balances; inclusive bounds confirmed against source lines 581-632.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 581-632 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-048`

**Related rules:**

- [RULE-SEDACAO-002](RULE-SEDACAO-002-sedacao-v3-criterio-8-severe-pain-analog-7-10-bps-10-12-two.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)
- [RULE-SEDACAO-024](../drug-dosing/RULE-SEDACAO-024-sedation-analgesia-pathway-recommendation-catalog-facade-tex.md)

## Notes

AMARELO criterion (wired). VISUAL 4-6 / COMPORTAMENTAL 7-9. Verified against source.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
