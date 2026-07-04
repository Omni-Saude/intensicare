# RULE-VENTILACAO-006 — Ventilation C2/C3 previous-version FiO2->PEEP table (peep_old_table)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | DISCREPANCY, impact: none |
| Confidence | medium |
| Cluster | ventilacao |

## Rule

The prior (inactive) version compared PEEP against a single expected value per FiO2 bucket.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| fio2 bucket (str) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| expected_peep (int, cmH2O) | | |

## Logic

```text
peep_old_table = {"0.0":5,"0.1":5,"0.2":5,"0.3":5,"0.4":5,"0.5":8,"0.6":10,
                  "0.7":10,"0.8":14,"0.9":14,"1.0":16}
# previous logic checked if the actual PEEP was LESS than the expected value.
```

## Edge cases (as implemented)

Defined in both criterio_2 and criterio_3 but never read (dead code).

## Verification

- Verdict: DISCREPANCY (clinical impact: none)
- Reference: ARDSNet ARMA trial (NEJM 2000) lower PEEP/FiO2 titration table; LITFL CCC summary of the ARDSNet strategy

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_ventilacao.py` | 147-159,190-202 | `8166c07e` | variant |

- Merged from: RULE-vent-BE-10-049b
- Related rules: RULE-VENTILACAO-004, RULE-VENTILACAO-005

## Notes

Version variant of the ARDSnet-style FiO2xPEEP table; superseded by peep_new_table (list-of-allowed per bucket). Kept as a SEPARATE variant per policy (do not merge variants). verify=true to check the historical table values against ARDSnet.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
