# RULE-OPERACIONAL-INFRA-055 — popular_banco gender enum (synthetic data)

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The synthetic test-data generator draws a random patient gender code from 4 categories: M (male), F (female), O (other), N (not informed).

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| genero | string |  |

## Logic

```text
genero_choices = ["M", "F", "O", "N"]
genero = genero_choices[randint(0, 3)]
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/popular_banco.py` | 73, 129 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-seed-BE-11-034`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-032](RULE-OPERACIONAL-INFRA-032-popular-banco-valores-maximos-atributos-vital-sign-reference.md)
- [RULE-OPERACIONAL-INFRA-012](../clinical-scoring/RULE-OPERACIONAL-INFRA-012-popular-banco-rass-enum-values-synthetic-data.md)
- [RULE-OPERACIONAL-INFRA-013](../triage-eligibility/RULE-OPERACIONAL-INFRA-013-popular-banco-sdra-ards-severity-enum-synthetic-data.md)

## Notes

Same provenance caveat as RULE-seed-BE-11-032/033. Meaning of 'O' and 'N' inferred (Other / Não informado) from context, not stated explicitly in code.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
