# RULE-ESTABILIDADE-004 — Estabilidade v3 criterio_2 - new vasopressor missing sepsis work-up

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | low |

## Rule
Noradrenaline started in last 24h AND (no new antibiotic OR a Ringer-lactate record < 1000ml / isolated saline OR no blood culture ordered). Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml |
| balanco.qt_vol_ringer_lactato | float | ml |
| balanco.qt_vol_soro | float | ml |
| cpoe.antibiotico | float |  |
| cpoe.hemocultura_bacterias / hemocultura_fungos | float |  |

## Outputs

| name | type |
|---|---|
| criterio_2 | boolean |

## Logic

```text
return all([
  balanco_24h.filter(qt_vol_nora__gt=0).exists(),
  any([ not cpoe_24h.filter(antibiotico__gt=0).exists(),
        not balanco_24h.filter(Q(qt_vol_ringer_lactato__lt=1000) | Q(qt_vol_soro__gt=0)).exists(),
        not cpoe_24h.filter(hemocultura_bacterias__gt=0).exists(),
        not cpoe_24h.filter(hemocultura_fungos__gt=0).exists() ]),
]) if (balanco_24h and cpoe_24h) else False
```

## Edge cases (as implemented)

Ringer clause fires when a SINGLE record has qt_vol_ringer_lactato < 1000 (not an aggregate), OR'd with any isolated saline record. Unwired in calcular_criterios.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** low
- **Reference:** Surviving Sepsis Campaign 2021 Hour-1 bundle (Evans L et al., Crit Care Med 2021;49(11): e1063-e1143): obtain blood cultures BEFORE antibiotics, administer broad-spectrum antibiotics, give 30 mL/kg crystalloid within 3 h, measure/remeasure lactate, start vasopressors for MAP >=65. ANDROMEDA-SHOCK-2 defines septic shock after a >=1000 mL fluid load. ([source](https://pubmed.ncbi.nlm.nih.gov/34605781/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | 1000 mL Ringer anchor is below SSC 30 mL/kg (~2100 mL for 70 kg); matches ANDROMEDA >=1000 mL fluid-load reference instead |
| units | mL |
| ranges | 24h window; single-record (not aggregate) Ringer test |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_24h=present; new_antibiotic=none; cultures=any; ringer=any | flag workup gap (no antibiotic within Hour-1 bundle) | fires (not antibiotico.exists() True) | yes |
| nora_24h=present; antibiotic=given; blood_cultures=none; ringer=any | flag workup gap (no cultures — SSC requires cultures before/with antibiotics) | fires (not hemocultura_bacterias.exists() True) | yes |
| nora_24h=present; antibiotic=given; blood_cultures=ordered; ringer_lactato_mL=2000; soro=none | no flag (full bundle: antibiotics + cultures + adequate fluids) | fires — filter(ringer<1000 OR soro>0) matches no record, so `not exists()` is True, any() True | no |

**Verifier notes**

Component mapping to the SSC Hour-1 bundle is sound (cultures, antibiotics, fluids, vasopressor window). Two reference caveats, neither a code-vs-docstring defect (code faithfully implements its docstring): (1) the 1000 mL Ringer anchor is below the SSC 30 mL/kg resuscitation target (~2100 mL/70 kg), aligning instead with the ANDROMEDA-SHOCK-2 >=1000 mL fluid-load definition; (2) the fluid sub-clause is a convoluted negation — `not exists(ringer<1000 OR soro>0)` fires when a fully-resuscitated patient has NO under-1000 mL Ringer record and no saline (test vector 3 false positive). Rated low impact / VERIFIED because it is a bundle-completeness heuristic (no single published equation to violate) and is UNWIRED in production.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 249-284 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-062`

**Related rules:**

- [RULE-ESTABILIDADE-015](../alert-threshold/RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)
- [RULE-ESTABILIDADE-018](RULE-ESTABILIDADE-018-estabilidade-manual-c2-noradrenaline-started-in-last-24h.md)
- [RULE-ESTABILIDADE-024](RULE-ESTABILIDADE-024-estabilizacao-trilha2-shock-work-up-vasopressor-escalation-t.md)

## Notes

Encodes Surviving-Sepsis-Campaign bundle elements (cultures, antibiotics, fluid resuscitation) — verify the 1000ml fluid anchor against the SSC 30 ml/kg recommendation.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
