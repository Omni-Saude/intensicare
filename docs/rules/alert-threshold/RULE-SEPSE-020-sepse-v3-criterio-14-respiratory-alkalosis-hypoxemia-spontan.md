# RULE-SEPSE-020 — SEPSE v3 criterio_14 - respiratory alkalosis/hypoxemia spontaneous vent (minor)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
No noradrenaline (6h) AND spontaneous ventilation AND (PaCO2<32 OR PaO2/FiO2<300).

## Inputs

- evolucao.diurna_pco2, diurna_po2, diurna_fio2, diurna_ventilacao (float / string, mmHg / ratio)

## Outputs

- criterio_14 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  (evolucao.diurna_ventilacao.strip().lower() in get_ventilacao("ventilacao_espontanea")) if evolucao.diurna_ventilacao else False,
  any([ get_number(diurna_pco2) < 32,
        (get_number(diurna_po2) / get_number(diurna_fio2) < 300) if get_number(diurna_fio2) > 0 else False ]),
]) if balanco_6h else False
```

## Edge cases (as implemented)

Division guarded by fio2>0. P/F uses raw diurna_po2/diurna_fio2 (fio2 as fraction vs percent not normalized).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** SIRS PaCO2 criterion (ACCP/SCCM 1992): PaCO2 < 32 mmHg. Respiratory dysfunction PaO2/FiO2 < 300: SOFA respiratory component (Vincent 1996, P/F<300 = 2pts) and ARDS Berlin Definition (JAMA 2012;307:2526). P/F ratio = PaO2 (mmHg) / FiO2 as a DECIMAL FRACTION (0.21-1.0); if FiO2 is a percentage it must be divided by 100 first. ([source](https://jamanetwork.com/journals/jama/fullarticle/1160659))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | diff |
| ranges | diff |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| paco2_mmhg=28; pao2=95; fio2=0.21 | fire (PaCO2 28 < 32) | fire (get_number(28) < 32 True) | yes |
| paco2_mmhg=40; pao2=90; fio2=0.21 | no-fire (PaCO2 40 not<32; P/F=428 not<300) | no-fire (40<32 False; 90/0.21=428 not<300) | yes |
| paco2_mmhg=40; pao2=250; fio2_as_percent=60 | no-fire (FiO2 0.60 -> P/F = 250/0.60 = 417, not<300) | fire (250/60 = 4.17 < 300 True) -- FALSE POSITIVE from unnormalized percent FiO2 | no |
| paco2_mmhg=blank/missing; pao2=95; fio2=0.21 | no-fire (no PaCO2 datum; P/F=452 normal) | fire (get_number("")=0, and 0 < 32 True) -- FALSE POSITIVE from missing-data coercion | no |

**Verifier notes**

Independent verdict overrides extraction status OK: the equation form and both cutoffs (PaCO2<32 mmHg, P/F<300) match the references, BUT two reference-relevant computation defects exist. (1) PaCO2 branch: handlers.get_number(blank)=0, and 0<32 is True, so an absent/blank PaCO2 spuriously satisfies the criterion; combined with the spontaneous-vent gate (many spontaneously breathing patients have no ABG), this can fire broadly on missing data. (2) P/F branch: PaO2/FiO2 is computed on the raw stored diurna_fio2 with NO fraction-vs-percent normalization (confirmed: get_number only float-casts). If FiO2 is stored as a percentage (e.g. 40 or 60, common in Brazilian charting), the ratio is understated ~100x and is almost always < 300 -> systematic false positive; if stored as a fraction the math is correct (data-convention dependent). This is exactly the fraction/percent FiO2 unit hazard the audit targets. Impact moderate: criterio_14 is a minor criterion, but both defects push toward over-firing (over-triggering sepsis alerts), not under-detection.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 803-842 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-114`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

Guard uses only balanco_6h truthiness; ultima_evolucao may be None (AttributeError risk if no evolucao but balanco exists).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
