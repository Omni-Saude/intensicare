# RULE-ESTABILIDADE-010 — Estabilidade v3 criterio_10 - antihypertensive with active vasopressor (VERMELHO, wired)

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | drug-dosing |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Noradrenaline > 50ml/h in last 4h AND any scheduled antihypertensive prescribed. WIRED (contributes to VERMELHO alert).

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| cpoe antihypertensives (checked, 16): monocordil, nifedipino, losartan, captopril, enalapril, sustrate, nitroglicerina, nitroprussiato, clonidina, hidralazina, propranolol, bisoprolol, carvedilol, atenolol, metildopa, minoxidil | float |  |

## Outputs

| name | type |
|---|---|
| criterio_10 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(qt_vol_nora__gt=50).exists(),
  any([ get_number(cpoe.<each of the 16 antihypertensives above>) > 0 ]),
]) if (ultima_cpoe and balanco_4h) else False
```

## Edge cases (as implemented)

Docstring lists 18 antihypertensives (additionally anlodipino and metoprolol) but the code's any([...]) checks only 16 — a patient on ONLY anlodipino or metoprolol would not trigger.

## Divergence

Code vs docstring: documented 18-drug antihypertensive list, code checks 16 (omits anlodipino and metoprolol from the any([]) evaluation).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published clinical score/guideline defines a "scheduled antihypertensive present WITH active vasopressor" conflict alert or its specific drug enumeration — this is an internal medication-safety business rule (TASY drug list). SSC-2021 concept of avoiding agents that lower MAP during shock resuscitation is directionally supportive but does not specify a list. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_mlh=60; losartan=1 | internal intent: antihypertensive + active vasopressor -> FLAG (losartan is in both the 18-drug docstring and the 16-drug code list) | nora>50 T, any([losartan>0 T]) T -> True | yes |
| qt_vol_nora_mlh=60; anlodipino=1 | docstring lists anlodipino (amlodipine) as an antihypertensive -> should FLAG | code any([]) has NO anlodipino key -> no clause True -> False (missed alert) | no |
| qt_vol_nora_mlh=60; metoprolol=1 | docstring lists metoprolol -> should FLAG | code any([]) has NO metoprolol key -> False (missed alert) | no |
| qt_vol_nora_mlh=50; losartan=1 | boundary: nora exactly 50 is not >50 | balanco_4h.filter(qt_vol_nora__gt=50) empty (strict) -> False | yes |

**Verifier notes**

No external authoritative reference governs this rule's drug enumeration or its ml/h vasopressor threshold — it is a proprietary medication-conflict safety rule; flagged for internal review, not treated as wrong. However the extraction-flagged DISCREPANCY is CONFIRMED by direct source read (lines 544-590): the docstring enumerates 18 antihypertensives (…anlodipino…metoprolol…) but the any([...]) evaluates only 16, omitting anlodipino (amlodipine) and metoprolol. Consequence: a patient on active high-dose vasopressor whose ONLY prescribed antihypertensive is amlodipine or metoprolol would NOT trigger this WIRED VERMELHO alert (vectors 2-3). Amlodipine and metoprolol are common agents, so the gap is clinically relevant as a missed-safety-alert, but because no published source mandates the list, impact is recorded n/a and the finding is routed to internal review. The ml/h cutoff (>50) is likewise institution-specific and unverifiable against published anchors.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 544-590 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-070`

**Related rules:**

- [RULE-ESTABILIDADE-014](../alert-threshold/RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)
- [RULE-ESTABILIDADE-021](../care-pathway/RULE-ESTABILIDADE-021-estabilidade-manual-c5-antihypertensive-with-adequate-pressu.md)

## Notes

Status upgraded OK->DISCREPANCY: Phase-1 identified the 16-vs-18 drug-list gap in notes but left status OK. Facade text counterpart = criterio_10 'Uso de Noradrenalina e presenca de anti-hipertensivos na prescricao'.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
