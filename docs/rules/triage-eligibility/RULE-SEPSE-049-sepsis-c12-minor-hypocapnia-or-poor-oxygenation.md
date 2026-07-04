# RULE-SEPSE-049 — Sepsis C12 (minor) - hypocapnia or poor oxygenation

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Minor criterion - (PaCO2<32 AND no VM) OR P/F ratio < 300.

## Inputs

- paco2 (float, mmHg, 0-150)
- ventilacao_mecanica_exists (bool)
- relacao_po2_fio2 (float)

## Outputs

- criterio_12 (bool)

## Logic

```text
any([
  all([(paco2 < 32) if paco2 else False, not verificar_objeto_existe(dp,'ventilacao_mecanica')]),
  (relacao_po2_fio2 < 300) if (po2 and fio2) else False])
```

## Edge cases (as implemented)

paco2 falsy excluded. Ratio path requires po2 and fio2 present. Strict <32 and <300. Test paco2=31->True; ratio 300->False, 299->True.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** SIRS respiratory criterion PaCO2 < 32 mmHg (ACCP/SCCM 1992, Chest 1992;101:1644-1655); PaO2/FiO2 < 300 = arterial hypoxemia / mild ARDS organ dysfunction (Surviving Sepsis Campaign severe-sepsis criteria; Berlin ARDS mild = P/F <= 300). ([source](https://pubmed.ncbi.nlm.nih.gov/1303622/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | PaCO2 32 mmHg and P/F 300 match references |
| units | PaCO2 mmHg correct; P/F ratio uses PaO2(mmHg)/FiO2(fraction) per verificar_relacao_po2_fio2 |
| ranges | paco2 0-150 plausible |
| rounding | n/a |
| cutoffs | strict PaCO2 < 32 and P/F < 300 (Berlin is <=300; 1-point difference at exactly 300) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| paco2=31; ventilacao_mecanica_exists=false | true | true | yes |
| paco2=31; ventilacao_mecanica_exists=true | false | false | yes |
| relacao_po2_fio2=299; po2=90; fio2=0.3 | true | true | yes |
| relacao_po2_fio2=300; po2=90; fio2=0.3 | false | false | yes |

**Verifier notes**

Minor criterion combining SIRS hypocapnia (PaCO2<32, gated on absence of mechanical ventilation to avoid vent-driven hypocapnia) OR hypoxemic organ dysfunction (P/F<300). Both cutoffs match published references; strict <300 vs Berlin's <=300 differs only at exactly 300 (negligible). P/F requires both po2 and fio2 present. Assumes FiO2 stored as fraction; not flagged as a unit bug in extraction. Legacy confirmed at trilha_sepse.py:366-383.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 366-383 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-037`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:203-217.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
