# RULE-CADASTROS-UI-001 — FilterLeitos tri-state occupancy filter sent as literal string

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The Leitos list filter offers a 3-way "Ocupação" select - "Sem preferencia" (value "unknown", default), "Sim" (value "true"), "Não" (value "false") - and passes whichever string value is chosen straight through to onFilter with no transformation.

## Inputs

| name | type | range |
|---|---|---|
| ocupado | 'unknown' \| 'true' \| 'false' | enum: unknown (default) \| true \| false |

## Outputs

| name | type |
|---|---|
| onFilter({ ocupado, ... }) | Partial<Models.Leito> |

## Logic

```text
Select(name="ocupado", defaultValue="unknown"):
  Option("unknown") -> "Sem preferencia"
  Option("true")    -> "Sim"
  Option("false")   -> "Não"
onFinish = onFilter directly (values passed through unmodified)
```

## Edge cases (as implemented)

Unlike FilterOcupacoes (RULE-filtro-FE-05-004), the "no preference" sentinel ("unknown") is NOT converted to undefined here - it is sent to onFilter/the backend as the literal string "unknown", so the caller/API must know to special-case that value as "no filter", or bed filtering silently breaks for the default option.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FilterLeitos/FilterLeitos.tsx` | 13-45 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-filtro-FE-05-003`

**Related rules:** _none_

## Notes

Flagged AMBIGUOUS because the analogous FilterOcupacoes component explicitly maps its "no filter" sentinel ("todos") to undefined before calling onFilter, while this component does not - a verifier should check whether the "ocupado" query param backing FilterLeitos actually treats the string "unknown" as "no filter" server-side, or whether this is a latent bug that leaves the default filter state broken.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
