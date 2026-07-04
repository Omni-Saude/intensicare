# RULE-ESTABILIDADE-005 — Estabilidade v3 criterio_3 - lactate elevation with sepsis therapy

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Lactate >= 2 mmol/L AND antibiotic prescribed AND noradrenaline present in last 4h AND no mechanical ventilation in last 24h. The docstring documents ABSENCE of noradrenaline but the code checks PRESENCE. Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| evolucao.diurna_lactato | float | mmol/L |
| cpoe.antibiotico | float |  |
| evolucao.diurna_ventilacao | string |  |

## Outputs

| name | type |
|---|---|
| criterio_3 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(qt_vol_nora__gt=0).exists(),               # docstring: "ausencia de noradrenalina"
  get_number(evolucao.diurna_lactato) >= 2,
  get_number(cpoe.antibiotico),
  not evolucao_24h.filter(diurna_ventilacao__in=get_ventilacao("ventilacao_mecanica")).exists(),
]) if (ultimo_balanco and ultima_cpoe and ultima_evolucao and evolucao_24h) else False
```

## Edge cases (as implemented)

Presence-vs-documented-absence of noradrenaline. Lactate inclusive >= 2. Unwired.

## Divergence

Code checks noradrenaline PRESENCE (qt_vol_nora__gt=0 exists) while the docstring specifies ABSENCE ("ausencia de noradrenalina ... nas ultimas 4h"). Kept AMBIGUOUS (not DISCREPANCY) because the criterion is unwired, leaving true intent undetermined.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Sepsis-3 (Singer M et al., JAMA 2016;315(8):801-810) — hyperlactatemia >2 mmol/L; concept of cryptic/occult septic shock = hyperlactatemia WITHOUT hypotension/vasopressor requirement (normotensive hyperlactatemia). Facade alert text (RULE-015 criterio_3) states "Lactato >2mmol/L sem DVA e VM. Choque oculto?" (i.e. occult shock = ABSENCE of vasopressor). ([source](https://pubmed.ncbi.nlm.nih.gov/26903338/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | mmol/L (lactate) — correct |
| ranges | 4h vasopressor window, 24h MV window |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| diurna_lactato=3.0; antibiotico=>0; nora_4h=absent; mecanica_vent_24h=absent | flag occult shock (high lactate, on antibiotics, NO vasopressor, no MV) | no fire (requires nora_4h.exists(); nora absent -> False) | no |
| diurna_lactato=3.0; antibiotico=>0; nora_4h=present; mecanica_vent_24h=absent | no flag (patient ON vasopressor = overt, not occult, shock) | fires (nora_4h.exists() True, lactate 3>=2, antibiotic, no MV) | no |
| diurna_lactato=2.0; antibiotico=>0; nora_4h=absent; mecanica_vent_24h=absent | flag boundary occult shock (lactate at threshold, no vasopressor) | no fire (nora absent blocks; also lactate>=2 inclusive vs Sepsis-3 strict >2) | no |

**Verifier notes**

Lactate anchor (>=2 mmol/L) matches Sepsis-3 (minor inclusive-vs-strict boundary at 2.0). The load-bearing discrepancy is the noradrenaline direction: the code requires vasopressor PRESENCE (`balanco_4h.filter(qt_vol_nora__gt=0).exists()`, line 308) while both the docstring ("ausencia de noradrenalina ... nas ultimas 4h") AND the facade alert text ("sem DVA ... Choque oculto?") and the published cryptic/occult-shock concept require vasopressor ABSENCE. The code thus flags the exact opposite population (patients already on vasopressors) from the intended occult-shock cohort. Extraction kept this AMBIGUOUS because the criterion is unwired; characterized here as a DISCREPANCY since two independent documentation layers plus the clinical concept agree the check is inverted. Impact moderate on logic; none in production (UNWIRED).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 286-319 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-063`

**Related rules:**

- [RULE-ESTABILIDADE-015](RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)

## Notes

Facade criterio_3 alert = 'Lactato >2mmol/L sem DVA e VM. Choque oculto?' (occult shock).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
