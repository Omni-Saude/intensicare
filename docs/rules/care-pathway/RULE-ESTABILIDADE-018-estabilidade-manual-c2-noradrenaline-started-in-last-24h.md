# RULE-ESTABILIDADE-018 — Estabilidade manual C2 - noradrenaline started in last 24h

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
True if any Noradrenalina in the patient's lookback chain has horario_inicio within the last 24h.

## Inputs

| name | type |
|---|---|
| buscar_ultimos_dados | list[pk] |
| Noradrenalina.horario_inicio | datetime |

## Outputs

| name | type |
|---|---|
| criterio_2 | bool |

## Logic

```text
horario = now - 24h
Noradrenalina.objects.filter(pk__in=dados_prontuario.buscar_ultimos_dados,
                             horario_inicio__gt=horario).exists()
```

## Edge cases (as implemented)

Strict > (started exactly 24h ago excluded). Searches across chained prontuarios (same pk space as dados_prontuario).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_estabilidade.py` | 91-99,113-114 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estab-BE-10-020`

**Related rules:**

- [RULE-ESTABILIDADE-004](RULE-ESTABILIDADE-004-estabilidade-v3-criterio-2-new-vasopressor-missing-sepsis-wo.md)
- [RULE-ESTABILIDADE-023](../alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md)

## Notes

Temporal vasopressor-initiation check; no numeric clinical anchor -> verify:false. Unit test test_trilha_estabilidade.py:58-74.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
