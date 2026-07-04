# RULE-OPERACIONAL-INFRA-012 — popular_banco RASS enum values (synthetic data)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

The synthetic test-data generator draws a random RASS (Richmond Agitation-Sedation Scale) value from the fixed set of 10 standard RASS levels, -5 through +4.

## Outputs

| Name | Type | Unit |
|---|---|---|
| rass | string | - |

## Logic

```text
rass_choices = ["-5", "-4", "-3", "-2", "-1", "0", "+1", "+2", "+3", "+4"]
rass = rass_choices[randint(0, 9)]
```

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: Sessler CN, Gosnell MS, Grap MJ, et al. The Richmond Agitation-Sedation Scale: validity and reliability in adult intensive care unit patients. Am J Respir Crit Care Med. 2002;166(10):1338-1344. Also Ely EW et al. JAMA 2003;289(22):2983-2991. Standard RASS is a 10-point ordinal scale from -5 (unarousable) through 0 (alert and calm) to +4 (combative).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/popular_banco.py` | 71, 134 | `8166c07e` | primary |

- Merged from: RULE-seed-BE-11-032
- Related rules: RULE-OPERACIONAL-INFRA-013, RULE-OPERACIONAL-INFRA-055, RULE-OPERACIONAL-INFRA-032

## Notes

Sourced from a developer test-data generator, not from an authoritative model field/serializer choices= in this partition (the actual model with choices likely lives in trilha_manual, out of BE-11 scope). Included as provisional evidence that the system's RASS domain is the standard 10-point -5..+4 scale.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
