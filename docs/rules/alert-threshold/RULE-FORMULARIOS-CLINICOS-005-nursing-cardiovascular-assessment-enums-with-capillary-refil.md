# RULE-FORMULARIOS-CLINICOS-005 — Nursing cardiovascular assessment enums with capillary-refill (TEC) > 5 s alert

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | alert-threshold |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Cardiovascular exam enums plus a boolean capillary-refill (TEC) > 5 s perfusion alert.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_cardiologica.tec_maior_5s | boolean |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| cardiovascular assessment | object |  |

## Logic

```text
pressao_arterial {normotenso, hipotensao, hipertensao, instavel (Instável Hemodinamicamente)}
frequencia_cardiaca {normocardio, bradicardico, taquicardio}
ritmo_cardiaco {ritmo_sinusal, arritmia, marcapasso, sopro_cardiaco}
tec_maior_5s(boolean) "Tempo de Enchimento Capilar maior que 5 segundos?"
```

## Edge cases (as implemented)

TEC > 5 s is a peripheral-perfusion alert (capillary refill time).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Capillary refill time (CRT). Standard reference: normal CRT <2 s (adults; up to ~3 s in elderly); prolonged/abnormal >2-3 s indicates impaired peripheral perfusion. Sepsis resuscitation literature (ANDROMEDA-SHOCK, Hernandez et al. JAMA 2019) uses CRT >3 s as the abnormal target. StatPearls, Capillary Refill Time. ([source](https://www.ncbi.nlm.nih.gov/books/NBK557753/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| crt_seconds=1.5 | normal (<2 s), no perfusion alert | tec_maior_5s = false (no alert) | yes |
| crt_seconds=2.5 | prolonged/abnormal (>2 s) -> perfusion concern | tec_maior_5s = false (NO alert; under-triggers) | no |
| crt_seconds=4.0 | prolonged (>3 s), abnormal by sepsis-resuscitation criteria | tec_maior_5s = false (NO alert; under-triggers) | no |
| crt_seconds=6.0 | markedly prolonged, abnormal | tec_maior_5s = true (alert) | yes |

**Verifier notes**

The capillary-refill (TEC) alert boolean fires only at >5 s, which is substantially more lenient than the published abnormal threshold (>2-3 s; sepsis literature uses >3 s). Consequently it does NOT flag the 3-5 s prolonged-refill window that reference standards already consider abnormal/hypoperfused -> under-triggering. Impact assessed LOW rather than moderate because this is a manual nursing screening flag, not an automatic clinical-decision gate, and the same cardiovascular block independently captures hemodynamic instability (pressao_arterial 'instavel'/'hipotensao'); a delayed refill in the 3-5 s range would rarely be the sole perfusion signal. Still a genuine threshold-leniency discrepancy of the exact kind this audit targets. Note: no single published scale defines a '>5 s' CRT cutoff, but the reference standard for abnormal CRT is well established, so this is characterizable (not UNVERIFIABLE).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 424-472 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-nursing-FE-01-043`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-010](../data-validation/RULE-FORMULARIOS-CLINICOS-010-physician-physical-exam-enums-and-conditional-reveals.md)
- [RULE-FORMULARIOS-CLINICOS-032](../data-validation/RULE-FORMULARIOS-CLINICOS-032-physiotherapy-neuro-cardio-respiratory-assessment-enums.md)

## Notes

pressao_arterial / frequencia_cardiaca categorical enums are reused in the Fisioterapeuta and Farmaceutico cardio sections (RULE-FORMULARIOS-CLINICOS-032). verify=true: alert-threshold carrying a plausible published clinical anchor (capillary refill time).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
