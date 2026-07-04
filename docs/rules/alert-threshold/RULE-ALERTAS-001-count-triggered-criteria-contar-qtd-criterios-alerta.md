# RULE-ALERTAS-001 — Count triggered criteria (contar_qtd_criterios_alerta)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Counts how many criteria in a trilha have esta_alerta == 1; this count is the input to define_tipo_alerta (RULE-ALERTAS-003).

## Inputs

- trilha.criterios (list; each element has esta_alerta in {0,1})

## Outputs

- acc (integer count)

## Logic

```text
acc = 0
for criterio in trilha["criterios"]:
    if criterio["esta_alerta"] == 1:
        acc += 1
return acc
```

## Edge cases (as implemented)

Only exact ==1 increments; empty criterios -> 0.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published clinical reference. This is an internal business rule: a generic counter (contar_qtd_criterios_alerta) that tallies how many criteria in a trilha have esta_alerta == 1. It is not a validated clinical score, equation, or guideline-defined cutoff (Sepsis-3, KDIGO, ASPEN, ARDSNet, MDCalc, etc. do not define this counting primitive).

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a - input criterio['esta_alerta'] is a domain {0,1} flag; only ==1 increments |
| rounding | n/a - integer accumulator (acc = int(0)), no rounding |
| cutoffs | n/a - no score bands; produces a raw count consumed downstream by define_tipo_alerta (RULE-ALERTAS-003) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| criterios=[{esta_alerta:1},{esta_alerta:1},{esta_alerta:0}] | n/a (no clinical reference) - internal-consistency expectation = 2 | 2 | yes |
| criterios=[] (empty) | n/a - internal-consistency expectation = 0 | 0 | yes |
| criterios=[{esta_alerta:1},{esta_alerta:2},{esta_alerta:None},{esta_alerta:0}] | n/a - internal-consistency expectation = 1 (strict ==1; values 2/None/0 excluded) | 1 | yes |

**Verifier notes**

Legacy source verified byte-for-byte @8166c07 in both trilha_automatica/utils.py:8-13 and core/utils.py:18-23 - identical implementations, no divergence. Logic is a strict-equality (==1) counter over a criterios list; no unit, equation, or coefficient surface to audit against a published source. Flagged for internal review only: the count semantics (which criteria carry esta_alerta==1, and how many trigger a color) are governed by the per-trilha _CRITERIOS_ALERTA thresholds in RULE-ALERTAS-003 (already DISCREPANCY-flagged for a latent dead-zone and under-counting of criterio ranges), not by this primitive. This counter itself is behaviorally correct for its stated contract. Not treated as wrong.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/utils.py` | 8-13 | `8166c07eae` | primary |
| ahlabs-trilhas | `core/utils.py` | 18-23 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ALERT-BE-12-009`

**Related rules:**

- [RULE-ALERTAS-003](RULE-ALERTAS-003-criteria-count-alert-color-mapping-define-tipo-alerta-per-mo.md)
- [RULE-ALERTAS-004](RULE-ALERTAS-004-single-criterion-alert-flag-esta-alerta.md)

## Notes

Byte-identical implementation exists in both trilha_automatica/utils.py and core/utils.py (verified @8166c07). No behavioral divergence between the two copies.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
