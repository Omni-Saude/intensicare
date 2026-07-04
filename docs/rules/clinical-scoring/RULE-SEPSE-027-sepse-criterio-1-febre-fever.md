# RULE-SEPSE-027 — Sepse criterio_1 - Febre (fever)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Sepsis screening major criterion 1 fires when the most recent vital-sign temperature exceeds 38 C and was recorded within the last 24 hours.

## Inputs

- sinais_vitais.temperatura (float, Celsius)
- sinais_vitais.tempo_criacao() (float, hours)

## Outputs

- criterio_1 (boolean)

## Logic

```text
temperatura = sinais_vitais.temperatura if sinais_vitais else None
if temperatura:                      # falsy guard: None OR 0.0 -> return False
    return temperatura > 38 if sinais_vitais.tempo_criacao() <= 24 else False
return False
```

## Edge cases (as implemented)

temperatura == 0.0 is falsy and yields False. Strict > 38 (38.0 exactly does NOT fire). tempo_criacao() uses timedelta.seconds (see RULE-balanco-BE-06-006) so it is always < 24, making the "<= 24" window guard effectively always true.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ACCP/SCCM Consensus SIRS criteria (Bone RC et al., Chest 1992;101(6):1644-55): body temperature > 38 C (or < 36 C). Fever component threshold > 38 C strict. ([source](https://emedicine.medscape.com/article/168943-overview))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok (Celsius, matches SIRS) |
| ranges | ok |
| rounding | n/a (direct > comparison, no rounding) |
| cutoffs | ok (strict > 38 C matches SIRS fever cutoff) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| temperatura=38.5; tempo_criacao_h=2 | fever True (>38) | True (38.5>38, window ok) | yes |
| temperatura=38.0; tempo_criacao_h=2 | False (SIRS strict >38; 38.0 not fever) | False (38.0>38 is False) | yes |
| temperatura=37.5; tempo_criacao_h=2 | False | False | yes |
| temperatura=0.0; tempo_criacao_h=2 | n/a (non-physiologic) | False (0.0 falsy guard) | yes |

**Verifier notes**

Strict >38 C matches classic SIRS fever cutoff. Some sepsis screens (ILAS Brazil / SSC surgical) use >38.3 C; legacy's >38 C is the more sensitive standard SIRS value - acceptable. Companion hypothermia (<36 C) is a separate 'menor' criterion. tempo_criacao() 24h window guard is effectively always-true (timedelta.seconds bug per catalog) but is a data-recency gate, not the clinical threshold - no impact. temp==0.0 falsy guard is non-physiologic, no clinical impact.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 105-112 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-001`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

One of 7 "maiores" criteria. Paired with hypothermia criterio_8 (<36) which is a "menor".

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
