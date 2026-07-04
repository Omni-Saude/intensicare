# RULE-SEPSE-034 — Sepse criterio_8 - Hipotermia

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
Minor criterion 8 fires when temperature < 36 C on the latest reading within 24h.

## Inputs

- sinais_vitais.temperatura (float, Celsius)

## Outputs

- criterio_8 (boolean)

## Logic

```text
temperatura = sinais_vitais.temperatura if sinais_vitais else None
if temperatura:
    return temperatura < 36 if sinais_vitais.tempo_criacao() <= 24 else False
return False
```

## Edge cases (as implemented)

Strict < 36. temperatura falsy (None/0.0) -> False. tempo_criacao <= 24 effectively always true.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** SIRS criteria (ACCP/SCCM Consensus, Bone 1992; Sepsis-2) - hypothermia = core temperature < 36 C. ([source](https://reference.medscape.com/calculator/522/sirs-criteria-systemic-inflammatory-response-syndrome))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| temperatura=35.5 | 35.5 < 36 -> hypothermia True | 35.5<36 True (window<=24) -> True | yes |
| temperatura=36.0 | boundary, strict <36 not met -> False | 36<36 False -> False | yes |
| temperatura=37.0 | not hypothermic -> False | 37<36 False -> False | yes |
| temperatura=0.0 | n/a invalid/absent | temperatura falsy -> False | yes |

**Verifier notes**

criterio_8 hypothermia matches the SIRS hypothermia threshold (<36 C) exactly, including strict inequality and Celsius units. Symmetric with criterio_1 fever (>38 C, RULE-SEPSE-027) which likewise matches SIRS >38 C. The 0.0-is-falsy edge and always-true tempo_criacao()<=24 window are documented elsewhere and do not affect agreement with the reference.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 256-262 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-008`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

One of 4 "menores" criteria.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
