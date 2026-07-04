# RULE-BALANCO-HIDRICO-044 — Fluid-balance module navigation/state routes

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The fluid-balance (balanço hídrico) module for a given bed occupation is organized into exactly four navigable sub-routes/states, each backed by a distinct record type (intake, output, vital signs, and an aggregate overview).

## Inputs

- route

## Outputs

- SendValues

## Logic

```text
ItemRoute = "entrada" | "saida" | "sinais-vitais" | "visao-geral"
SendValues = Entrada | Saida | SinaisVitais   // one payload shape per route (excl. visao-geral which is read-only aggregate)
```

## Edge cases (as implemented)

visao-geral has no corresponding SendValues member — it is read-only (VisaoGeral interface with entradas/saidas/horarios arrays), consistent with useGetBalancoHidricoVisaoGeral being a GET-only endpoint.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/BalancoHidrico.d.ts` | 97-103 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-07-001`

**Related rules:**

- [RULE-BALANCO-HIDRICO-013](../physiological-calculation/RULE-BALANCO-HIDRICO-013-fluid-balance-visao-geral-2-hour-time-bucketing-08-00-start.md)
- [RULE-BALANCO-HIDRICO-045](RULE-BALANCO-HIDRICO-045-fluid-balance-record-signing-deletion-lifecycle.md)

## Notes

Endpoint plumbing implementing these routes is in src/hooks/networking/balancoHidrico.ts (generic parametrized CRUD, marked rule_bearing:no there — the domain rule lives in the type model).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
