# RULE-SEPSE-005 — Sepse - Hierarquia de nivel de consciencia

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Ordinal severity mapping of consciousness levels used to detect changes between successive readings.

## Inputs

- nv_consciencia (enum, acordado|sonolencia|agitacao|convulsao|reage_verbal|reage_tatil|coma)

## Outputs

- rank (int)

## Logic

```text
{ "acordado":1, "sonolencia":2, "agitacao":3, "convulsao":3, "reage_verbal":4, "reage_tatil":5, "coma":6 }
```

## Edge cases (as implemented)

"agitacao" and "convulsao" share rank 3. The "coma" consciousness value from BalancoChoices.consciencia() is present; the value "reage_verbal"/"reage_tatil" map to 4/5. Values not in the map return None via .get().

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published ordinal scale matches this exact 6-level consciousness map. Closest external referents: AVPU scale (Alert/Verbal/Pain/Unresponsive) and the Glasgow Coma Scale (Teasdale & Jennett, Lancet 1974;2(7872):81-84). This is a custom institutional severity ordering, not a validated scale. ([source](https://pubmed.ncbi.nlm.nih.gov/4136544/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ordinal ranks acordado=1 < sonolencia=2 < agitacao=3 = convulsao=3 < reage_verbal=4 < reage_tatil=5 < coma=6. Monotonic and internally consistent (increasing severity); agitacao and convulsao intentionally tie at 3. |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nv_consciencia=acordado | lowest severity (AVPU 'Alert') | 1 | n/a - ordinally consistent |
| nv_consciencia=coma | highest severity (AVPU 'Unresponsive') | 6 | n/a - ordinally consistent |
| nv_consciencia=agitacao | n/a | 3 | n/a - tied with convulsao |
| nv_consciencia=convulsao | n/a | 3 | n/a - tied with agitacao |
| nv_consciencia=xyz_unmapped | n/a | None | n/a - .get() returns None for unknown key |

**Verifier notes**

Internal ordinal mapping used only to detect direction of change between successive consciousness readings (consumed by RULE-SEPSE-033). Hand-traced against trilha_homecare/models/sepse.py:229-239; matches the catalog exactly. Not a published/validated scale, so UNVERIFIABLE; the ordering is monotonic and clinically plausible (wakefulness lowest, coma highest). The agitacao/convulsao tie at 3 means a transition between those two states registers no rank change - flag for internal review if unintended.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 229-239 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-012`

**Related rules:**

- [RULE-SEPSE-033](RULE-SEPSE-033-sepse-criterio-7-variacao-do-nivel-de-consciencia.md)

## Notes

Consumed by RULE-sepse-BE-06-007. Note BalancoChoices.consciencia has a "mantido ou acordado" key "acordado".

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
