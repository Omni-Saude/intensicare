# RULE-SEPSE-067 — Sepsis / infection-source screening flags (movimentacao)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Boolean flags capturing time-windowed infection/device exposures and vasoactive/steroid use, forming sepsis and device-associated-infection screening criteria.

## Inputs

- antibiotico_em_24hrs (boolean)
- presenca_cvc_cdl_svd_10_dias (boolean)
- cvc_regiao_femoral_7_dias (boolean)
- hidrocortisona / vasopressina / anti_hipertensivo / delirium (boolean)

## Outputs

- screening flags (boolean set)

## Logic

```text
antibiotico_em_24hrs: "Antibiótico iniciado nas últimas 24h?"
presenca_cvc_cdl_svd_10_dias: "CVC, CDL ou SVD nos últimos 10 dias?"
cvc_regiao_femoral_7_dias: "CVC na região femoral nos últimos 7 dias?"
hidrocortisona, vasopressina (adjunct sepsis therapy), anti_hipertensivo, delirium: booleans.
```

## Edge cases (as implemented)

The 10-day (any central line/urinary catheter) and 7-day (femoral CVC) windows are device-associated-infection surveillance thresholds.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 67-71,100-109,213-232 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepsis-FE-01-026`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)
- [RULE-SEPSE-066](RULE-SEPSE-066-sepsis-pathway-disabled-legacy-criteria-v-old-27-vs-current.md)
- [RULE-SEPSE-068](../data-validation/RULE-SEPSE-068-urea-field-encodes-an-unbounded-value-under-a-threshold-name.md)

## Notes

These booleans plus RULE-024 labs are classic inputs for a sepsis/CLABSI/CAUTI screening engine.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
