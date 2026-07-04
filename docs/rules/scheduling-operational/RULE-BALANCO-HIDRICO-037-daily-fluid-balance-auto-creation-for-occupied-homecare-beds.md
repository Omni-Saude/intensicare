# RULE-BALANCO-HIDRICO-037 — Daily fluid-balance auto-creation for occupied homecare beds

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Scheduled task that creates one BalancoHidrico per day for every occupied homecare bed that has an attendance number, unless one already exists for that attendance and day.

## Inputs

- (none - reads current date and Leito table)

## Outputs

- BalancoHidrico records created

## Logic

```text
data = now(localtime).date()
leitos = Leito where nr_atendimento IS NOT NULL AND ocupado == True AND tipo == "homecare"
for leito in leitos:
    if not BalancoHidrico.exists(nr_atendimento == leito.nr_atendimento, dia == data):
        BalancoHidrico.create(nr_atendimento=leito.nr_atendimento, leito=leito, dia=data)
```

## Edge cases (as implemented)

Only beds with tipo == "homecare", ocupado == True, and non-null nr_atendimento qualify. Any creation error is re-raised wrapped as Exception (aborts the loop). Idempotent per (attendance, day).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/tasks.py` | 51-71 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balancohidrico-BE-09-009`

**Related rules:**

- [RULE-BALANCO-HIDRICO-036](../care-pathway/RULE-BALANCO-HIDRICO-036-balanco-hidrico-auto-provisioning-no-direct-write-endpoints.md)

## Notes

Celery shared_task criar_balancos_diario, routing key <ENV>.trilhas.prescricoes.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
