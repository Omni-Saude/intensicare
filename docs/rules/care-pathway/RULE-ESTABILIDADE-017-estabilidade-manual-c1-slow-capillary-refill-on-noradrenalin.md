# RULE-ESTABILIDADE-017 — Estabilidade manual C1 - slow capillary refill on noradrenaline

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Flags capillary refill time > 5s together with an active (persisted) noradrenaline record.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tec | int | seconds | 0 or 3-20 |
| noradrenalina_exists | bool |  |  |

## Outputs

| name | type |
|---|---|
| criterio_1 | bool |

## Logic

```text
bool(tec > 5 AND verificar_objeto_existe(dados_prontuario, 'noradrenalina'))
```

## Edge cases (as implemented)

tec strict > 5 (tec == 5 -> False). Requires a persisted Noradrenalina (hasattr AND instance.pk truthy). Test tec=6 with noradrenaline -> True; delete noradrenaline -> False.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** ANDROMEDA-SHOCK (Hernandez et al., JAMA 2019;321:654) and Surviving Sepsis Campaign perfusion-targeted resuscitation: capillary refill time (CRT) > 3 seconds is the validated abnormal/hypoperfusion threshold in septic shock (measured on distal phalanx, 10 s pressure). ([source](https://pubmed.ncbi.nlm.nih.gov/24811942/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| tec=4; noradrenalina_exists=true | CRT 4s > 3s = abnormal hypoperfusion on vasopressor -> should flag | 4 > 5 False -> criterio_1 = False (does NOT flag) | no |
| tec=6; noradrenalina_exists=true | CRT 6s > 3s = abnormal -> flag | 6 > 5 True AND noradrenaline persisted True -> criterio_1 = True | yes |
| tec=5; noradrenalina_exists=true | CRT 5s > 3s = abnormal -> should flag | 5 > 5 False (strict >) -> criterio_1 = False (does NOT flag) | no |
| tec=3; noradrenalina_exists=true | CRT exactly 3s = upper limit of normal (ANDROMEDA >3 abnormal) -> do not flag | 3 > 5 False -> criterio_1 = False | yes |

**Verifier notes**

Manual C1 uses CRT strict > 5 s, whereas the validated septic-shock reference (ANDROMEDA-SHOCK) defines abnormal peripheral perfusion as CRT > 3 s (the v3 counterpart RULE-003 correctly uses >3). The 3-5 s abnormal band (patients with genuine hypoperfusion on noradrenaline) is missed -> reduced sensitivity/delayed escalation. Impact moderate: under-detection of hypoperfusion in a patient already on vasopressor; direction is conservative (fewer alerts) but clinically under-sensitive.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 109-111 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-019`

**Related rules:**

- [RULE-ESTABILIDADE-003](../alert-threshold/RULE-ESTABILIDADE-003-estabilidade-v3-criterio-1-hypoperfusion-on-vasopressor.md)
- [RULE-ESTABILIDADE-023](../alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

Variant of v3 criterio_1 (RULE-003): manual uses TEC>5 + noradrenaline presence (no lactate branch), v3 uses TEC>3 OR lactate>=2 with a 6h vasopressor window. verificar_objeto_existe checks hasattr AND pk. Unit test test_trilha_estabilidade.py:34-48.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
