# RULE-SEPSE-035 — Sepse criterio_9 - Taquicardia

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Minor criterion 9 fires when heart rate > 110 bpm on the latest reading within a 12-hour window.

## Inputs

- sinais_vitais.frequencia_cardiaca (int, bpm)
- sinais_vitais.tempo_criacao() (float, hours)

## Outputs

- criterio_9 (boolean)

## Logic

```text
fc = sinais_vitais.frequencia_cardiaca if sinais_vitais else None
if fc:
    return fc > 110 if sinais_vitais.tempo_criacao() <= 12 else False
return False
```

## Edge cases (as implemented)

Strict > 110. The 12-hour guard is a real filter here (unlike the 24h guards) because tempo_criacao() returns 0..~24 via timedelta.seconds/3600; readings whose creation seconds-of-day/3600 exceed 12 fail. See RULE-balanco-BE-06-006 for the seconds-vs-total_seconds caveat.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** SIRS criteria (ACCP/SCCM Consensus, Bone 1992; Sepsis-2) - tachycardia = heart rate > 90 bpm. (NEWS2 scores HR 111-130 as 2 points.) ([source](https://reference.medscape.com/calculator/522/sirs-criteria-systemic-inflammatory-response-syndrome))

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
| frequencia_cardiaca=95; window_h=6 | 95 > 90 -> SIRS tachycardia True | 95>110 False -> False | no |
| frequencia_cardiaca=115; window_h=6 | 115 > 90 -> True | 115>110 True (window<=12) -> True | yes |
| frequencia_cardiaca=110; window_h=6 | 110 > 90 -> True | 110>110 False -> False | no |
| frequencia_cardiaca=0 | n/a invalid/absent | fc falsy -> False | yes |

**Verifier notes**

Correct column (frequencia_cardiaca, bpm) - no fc/fr swap here, unlike the v3 counterpart RULE-SEPSE-019. Threshold differs from SIRS: legacy fires only at HR>110, whereas the SIRS tachycardia cutoff is >90 bpm; HR 91-110 (SIRS-positive) will not fire this criterion. The 110 cutoff instead aligns with a higher-acuity band (NEWS2 111-130 = 2 pts). Impact low: it is a MINOR criterion within a multi-criterion screen, so the higher threshold reduces sensitivity but is a deliberate specificity choice rather than a unit error. Also uses a 12h window (vs 24h elsewhere), a real filter given tempo_criacao() seconds/3600 behavior; institutional, not a reference dimension.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 264-268 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-009`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

Minor criterion. 12h threshold (vs 24h for others).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
