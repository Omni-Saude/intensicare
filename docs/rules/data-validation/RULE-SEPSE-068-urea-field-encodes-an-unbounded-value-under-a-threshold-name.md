# RULE-SEPSE-068 — Urea field encodes an unbounded value under a threshold name

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The urea input is stored as a plain number with no bounds although its field key implies a ">50 in 24h" threshold.

## Inputs

- ureia_maior_50_24hrs (number, mg/dL)

## Outputs

- urea value (number, mg/dL)

## Logic

```text
label "Uréia"; nome ["dados_prontuario","ureia_maior_50_24hrs"]; type number; NO min/max.
```

## Edge cases (as implemented)

Field name suggests a boolean threshold (urea > 50 within 24h) but the input is a free numeric value with no validation.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 180-184 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepsis-FE-01-027`

**Related rules:**

- [RULE-SEPSE-067](../triage-eligibility/RULE-SEPSE-067-sepsis-infection-source-screening-flags-movimentacao.md)

## Notes

AMBIGUOUS = key vs type mismatch; a downstream consumer may (mis)interpret whether this holds a raw value or a >50 flag.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
