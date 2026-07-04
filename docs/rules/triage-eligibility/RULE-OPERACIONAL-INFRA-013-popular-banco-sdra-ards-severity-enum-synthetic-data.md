# RULE-OPERACIONAL-INFRA-013 — popular_banco SDRA (ARDS) severity enum (synthetic data)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | scoring |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

The synthetic test-data generator draws a random ARDS/SDRA (Síndrome do Desconforto Respiratório Agudo) severity classification from 3 categories: mild, moderate, severe.

## Outputs

| Name | Type | Unit |
|---|---|---|
| sdra | string | - |

## Logic

```text
sdra_choices = ["leve", "moderada", "grave"]
sdra = sdra_choices[randint(0, 2)]
```

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: ARDS Definition Task Force; Ranieri VM, Rubenfeld GD, Thompson BT, et al. Acute respiratory distress syndrome: the Berlin Definition. JAMA. 2012;307(23):2526-2533. Berlin stratifies ARDS into three mutually exclusive severity categories by PaO2/FiO2 (on PEEP/CPAP >=5 cmH2O): mild (200 < P/F <= 300), moderate (100 < P/F <= 200), severe (P/F <= 100).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/popular_banco.py` | 72, 135 | `8166c07e` | primary |

- Merged from: RULE-seed-BE-11-033
- Related rules: RULE-OPERACIONAL-INFRA-012, RULE-OPERACIONAL-INFRA-055, RULE-OPERACIONAL-INFRA-032

## Notes

Same provenance caveat as RULE-seed-BE-11-032: sourced from the test-data generator, not the authoritative model definition (out of BE-11 scope). Matches the standard 3-tier Berlin-definition-style ARDS severity naming (mild/moderate/severe), used verbatim here without correction.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
