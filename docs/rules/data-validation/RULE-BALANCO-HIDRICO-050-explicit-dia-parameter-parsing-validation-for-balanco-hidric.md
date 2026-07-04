# RULE-BALANCO-HIDRICO-050 — Explicit 'dia' parameter parsing/validation for balanco hidrico

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When a 'dia' query parameter is supplied, it must parse as 'YYYY-MM-DD'; otherwise a 400 validation error with a Portuguese message is raised.

## Inputs

- dia (query param)

## Outputs

- dia_param

## Logic

```text
try:
    dia_param = datetime.strptime(dia_param, "%Y-%m-%d").date()
except ValueError:
    raise ValidationError("Formato de data inválido para o parâmetro 'dia'. Use o formato 'YYYY-MM-DD'.")
```

## Edge cases (as implemented)

Only ValueError is caught; any other parsing exception would propagate uncaught.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/balanco_hidrico.py` | 38-42 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-08-006`

**Related rules:**

- [RULE-BALANCO-HIDRICO-023](../physiological-calculation/RULE-BALANCO-HIDRICO-023-default-clinical-day-cutoff-07-00-for-balanco-hidrico.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
