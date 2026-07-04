# RULE-SEPSE-023 — SEPSE v3 criterio_17 - enteral tube with adequate GCS (minor)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
No invasive vent AND GCS>=13 AND nasoenteral tube prescription in last 12h.

## Inputs

- evolucao.diurna_glasgow, diurna_ventilacao (float / string, GCS)
- cpoe.passagem_sonda_naso, cpoe.vent_mecanica_invasiva (float)

## Outputs

- criterio_17 (boolean)

## Logic

```text
return all([
  any([ not get_number(cpoe.vent_mecanica_invasiva),
        (not evolucao.diurna_ventilacao.strip().lower() in get_ventilacao("ventilacao_mecanica_invasiva")) if evolucao.diurna_ventilacao else False ]),
  get_number(evolucao.diurna_glasgow) >= 13,
  cpoe_12h.filter(passagem_sonda_naso__gt=0).exists(),
]) if ultima_cpoe and ultima_evolucao else False
```

## Edge cases (as implemented)

Note this is the only sepse minor with no noradrenaline gate.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published guideline defines 'nasoenteral tube prescription + GCS>=13 + no invasive ventilation' as a sepsis screening criterion. GCS 13-15 = mild impairment is standard (Teasdale & Jennett 1974), but the composite is an internal institutional risk indicator (enteral device as potential infection/aspiration source in a patient with adequate consciousness). ([source](https://www.glasgowcomascale.org/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a — GCS>=13 aligns with standard mild-GCS band but the composite criterion has no published source |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a — institutional |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| invasive_vent=false; glasgow=14; sne_prescribed_12h=true | per self-documented algorithm -> fires | True — no invasive vent, GCS 14>=13, SNE prescription in 12h | yes |
| invasive_vent=false; glasgow=12; sne_prescribed_12h=true | per algorithm -> does not fire (GCS<13) | False — get_number(12) not >=13 | yes |
| invasive_vent=false; glasgow=13; sne_prescribed_12h=true | boundary GCS=13 -> fires | True — 13>=13 | yes |

**Verifier notes**

Internal business rule; no primary clinical reference sets this composite as a sepsis marker. Logic is internally consistent with its own docstring (verified by trace). GCS>=13 boundary and the invasive-vent exclusion behave as documented. Flag for internal clinical review, not a defect. This is the only sepse minor criterion with no noradrenaline gate (noted in extraction).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 944-978 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-117`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
