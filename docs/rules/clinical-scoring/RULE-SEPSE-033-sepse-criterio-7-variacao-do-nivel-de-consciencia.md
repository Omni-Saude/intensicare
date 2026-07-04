# RULE-SEPSE-033 — Sepse criterio_7 - Variacao do nivel de consciencia

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Major criterion 7 compares previous vs current consciousness level via a numeric severity hierarchy and returns True when the PREVIOUS severity rank is greater than the current rank.

## Inputs

- sinais_vitais.nv_consciencia (current) (enum, acordado|sonolencia|agitacao|convulsao|reage_verbal|reage_tatil|coma)
- sinais_vitais.anterior(nr_atendimento).nv_consciencia (previous) (enum, same)

## Outputs

- criterio_7 (boolean)

## Logic

```text
H = {acordado:1, sonolencia:2, agitacao:3, convulsao:3, reage_verbal:4, reage_tatil:5, coma:6}
anterior = H.get(previous.nv_consciencia)      # None if no previous reading
atual    = H.get(current.nv_consciencia)
if anterior and atual is not None:
    return anterior > atual                    # fires when previous rank > current rank
return False
```

## Edge cases (as implemented)

Guard uses `if anterior and atual is not None`. anterior truthiness excludes rank None; note rank 0 impossible so fine. Requires at least 2 readings (anterior via index [1]).

## Divergence

DISCREPANCY: In hierarquia_consciencia higher number = worse (coma=6, acordado=1). Returning `anterior > atual` (previous worse than current) fires on clinical IMPROVEMENT, not deterioration. A worsening-detection criterion would expect `atual > anterior`. Recorded verbatim; direction appears inverted.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Sepsis-3 (Singer M et al., JAMA 2016) & qSOFA - altered mental status / DECLINE in level of consciousness (e.g. GCS < 15) is a marker of sepsis-associated organ dysfunction; the deterioration is the signal to detect. ([source](https://jamanetwork.com/journals/jama/fullarticle/2492881))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| previous_nv=acordado; current_nv=coma | deterioration (1->6) -> worsening consciousness should FIRE = True | anterior(1) > atual(6)? False -> returns False | no |
| previous_nv=coma; current_nv=acordado | improvement (6->1) -> should NOT fire = False | anterior(6) > atual(1)? True -> returns True | no |
| previous_nv=sonolencia; current_nv=sonolencia | no change -> False | 2 > 2? False -> False | yes |
| previous_nv=; current_nv=coma | single reading, cannot compute delta | anterior None -> guard fails -> False | yes |

**Verifier notes**

Confirms the extraction-flagged inversion. In hierarquia_consciencia higher rank = worse (coma=6, acordado=1). Legacy returns `anterior > atual`, i.e. it fires when the PREVIOUS state was worse than the current - clinical IMPROVEMENT - and stays silent on true deterioration. A worsening level of consciousness, which Sepsis-3/qSOFA treat as a key organ-dysfunction sign, will NOT trigger this MAJOR criterion, while a recovering patient spuriously will. Impact moderate rather than high because the homecare alert requires >2 majors (RULE-SEPSE-003), partially mitigating one inverted criterion. The ordinal hierarchy itself is institutional (no published scale), so only the comparison DIRECTION is judged against the reference intent.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 229-254 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-007`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)
- [RULE-SEPSE-005](RULE-SEPSE-005-sepse-hierarquia-de-nivel-de-consciencia.md)

## Notes

DISCREPANCY: In hierarquia_consciencia higher number = worse (coma=6, acordado=1). Returning `anterior > atual` (previous worse than current) fires on clinical IMPROVEMENT, not deterioration. A worsening-detection criterion would expect `atual > anterior`. Recorded verbatim; direction appears inverted.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
