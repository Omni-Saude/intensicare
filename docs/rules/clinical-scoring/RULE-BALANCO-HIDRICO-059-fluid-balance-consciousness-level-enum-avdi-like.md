# RULE-BALANCO-HIDRICO-059 — Fluid-balance consciousness level enum (AVDI-like)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | clinical-scoring |
| Type | validation |
| Status | OK |
| Confidence | medium |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Level-of-consciousness captured as an ordered enum of alertness states.

## Inputs

- nv_consciencia

## Outputs

- consciousness level

## Logic

```text
options: acordado(Mantido ou acordado), sonolencia(Sonolência), agitacao(Agitação ou confusão),
reage_verbal(Reage/responde ao estímulo verbal), reage_tatil(Reage/responde ao estímulo tátil),
coma(Não reage/responde (coma)), convulsao(Convulsão (pós ictal))
```

## Edge cases (as implemented)

Not a numeric score; ordinal severity implied by ordering.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** AVPU scale (Alert, Voice, Pain, Unresponsive) — closest standard reactivity ladder; see McNarry AF, Goldhill DR. Simple bedside assessment of level of consciousness: comparison of two simple assessment scales with the Glasgow Coma Scale. Anaesthesia. 2004;59(1):34-37. AVPU/AVDI defines only 4 ordinal states. ([source](https://onlinelibrary.wiley.com/doi/10.1111/j.1365-2044.2004.03526.x))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nv_consciencia=acordado | Nearest AVPU state = Alert; accepted as a valid alertness level | Accepted (option value 'acordado' = 'Mantido ou acordado') | yes |
| nv_consciencia=reage_verbal | Nearest AVPU state = Voice (responds to verbal stimulus); accepted | Accepted (option value 'reage_verbal' = 'Reage ou responde ao estímulo verbal') | yes |
| nv_consciencia=coma | Nearest AVPU state = Unresponsive; accepted | Accepted (option value 'coma' = 'Não reage ou responde (coma)') | yes |
| nv_consciencia=convulsao | No AVPU/AVDI equivalent — post-ictal seizure is not a level-of-consciousness state in the standard scale | Accepted (option value 'convulsao' = 'Convulsão (pós ictal)'); custom 7th enum member | no |
| nv_consciencia=agitacao | No direct AVPU/AVDI level — agitation/confusion is a qualitative state absent from the 4-point ladder | Accepted (option value 'agitacao' = 'Agitação ou confusão'); custom enum member | no |

**Verifier notes**

RULE-BALANCO-HIDRICO-059 is a categorical UI select enum (nv_consciencia) with 7 discrete
alertness states, NOT a numeric score, calculator, or weighted scale. Source confirmed at
trilhas-frontend src/utils/dataForms/dataFormBalancoHidrico.ts:547-581 (commit f9656be);
the 7 enum values match the catalog exactly: acordado, sonolencia, agitacao, reage_verbal,
reage_tatil, coma, convulsao. Labels differ trivially from the catalog transcription
("Reage ou responde..." in source vs "Reage/responde..." in catalog) — no behavioral impact.

No authoritative published reference defines this exact 7-item ladder. It loosely resembles
the AVPU/AVDI reactivity ladder (Alert/Voice→verbal, Pain→tactile, Unresponsive→coma) but
diverges: AVPU/AVDI has only 4 ordinal states, whereas this enum inserts non-AVPU states
(sonolencia, agitacao) and appends convulsao (post-ictal), which is a clinical event rather
than a consciousness level. There is no equation, coefficient, unit, numeric range, rounding,
or scored cutoff to verify against a primary source. It is an internal data-capture
vocabulary (proprietary nursing enum), so it is flagged UNVERIFIABLE for internal review
rather than DISCREPANCY — the legacy behavior (accept these 7 values) is internally consistent
and correct as implemented. The catalog status OK is not contradicted; there is simply no
external standard against which correctness can be adjudicated. No unit-mismatch or
calculation risk exists because no computation is performed on this field within this rule.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 547-581 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-fluidbalance-FE-01-016`

**Related rules:**

- [RULE-BALANCO-HIDRICO-019](RULE-BALANCO-HIDRICO-019-fluid-balance-pain-scale-conditional-nrs-0-10-bps-3-12.md)
- [RULE-BALANCO-HIDRICO-032](../care-pathway/RULE-BALANCO-HIDRICO-032-fluid-balance-vital-sign-ventilation-conditional.md)

## Notes

Resembles AVPU/AVDI reactivity ladder; not explicitly named.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
