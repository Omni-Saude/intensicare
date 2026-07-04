# RULE-SEPSE-022 — SEPSE v3 criterio_16 - prolonged capillary refill (minor, new onset)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
No noradrenaline (6h) AND TEC>3s in last 24h AND not TEC>3s before 24h (new onset).

## Inputs

- evolucao.tempo_enchimento_capilar (float, seconds)
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_16 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  evolucao_24h(dt>=now-24h).filter(tempo_enchimento_capilar__gt=3).exists(),
  not evolucao_mais_24h(dt<now-24h).filter(tempo_enchimento_capilar__gt=3).exists(),
]) if balanco_6h and evolucao_24h else False
```

## Edge cases (as implemented)

tempo_enchimento_capilar is CharField; DB __gt=3 comparison backend-dependent.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ANDROMEDA-SHOCK trial (Hernandez G et al., JAMA 2019) and ANDROMEDA-SHOCK-2 (JAMA 2025): capillary refill time (CRT) >3 seconds defined as abnormal peripheral perfusion in septic shock. ([source](https://jamanetwork.com/journals/jama/fullarticle/2840823))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok — TEC >3s abnormal threshold matches ANDROMEDA-SHOCK definition |
| units | ok — seconds |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok — strict __gt=3 matches '>3 seconds' (3.0s exactly not abnormal). Note the 'new onset' gate (present <24h AND absent >24h) is an institutional refinement, not part of the CRT reference |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_6h=absent; tec_last24h=4; tec_before24h=none | abnormal CRT present -> fires | True — TEC>3 in 24h exists, none before 24h | yes |
| nora_6h=absent; tec_last24h=2; tec_before24h=none | normal CRT (<3s) -> does not fire | False — 2 not >3 | yes |
| nora_6h=absent; tec_last24h=3; tec_before24h=none | boundary — 3.0s is not >3s, not abnormal -> does not fire | False — __gt=3 excludes 3.0 | yes |
| nora_6h=absent; tec_last24h=4; tec_before24h=4 | pure CRT-abnormal reference would still flag (CRT abnormal) | False — new-onset gate: prior TEC>3 exists so 'not exists' is False | no |

**Verifier notes**

TEC>3s threshold and strict comparison match the ANDROMEDA-SHOCK reference. The additional 'new onset' requirement (abnormal within 24h AND not abnormal before 24h) is an intentional institutional design choice to capture acute-onset hypoperfusion and is not a discrepancy against the perfusion reference (last test vector reflects that design, not a threshold error). CharField __gt=3 comparison is backend-dependent (noted in extraction) but does not affect the reference-cutoff verdict.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 915-942 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-116`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
