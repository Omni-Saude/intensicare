# RULE-OPERACIONAL-INFRA-044 — Assistido flag reset - 1-minute update window

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Celery task that clears the "assistido" (attended) flag on automatic trilhas that were updated in the last minute but not themselves assisted in the last minute.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| dt_atualizacao | datetime |  |  |
| assistido_em | datetime |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| assistido / assistido_por / assistido_em reset | fields |  |

## Logic

```text
now = datetime.now().astimezone()
For each trilha in Leito.get_trilhas_automaticas_v2():
  rows = trilha.objects
    .exclude(assistido_em__gte = now - 1 minute)
    .filter(dt_atualizacao__gte = now - 1 minute, dt_atualizacao__lte = now)
  rows.update(assistido=False, assistido_por=None, assistido_em=None)
limpar_todos_os_assistidos(): over Leito.get_trilhas_automaticas() (v1 set) resets ALL rows
  unconditionally.
```

## Edge cases (as implemented)

Window is exactly timedelta(minutes=1), timezone-aware (astimezone()). Boundary uses >= for lower bound and <= for upper. Uses v2 trilha set for the windowed reset but the v1 set for the full wipe.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/tasks/atualizar_assistido.py` | 12-34 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ops-BE-01-022`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-045](RULE-OPERACIONAL-INFRA-045-interactive-sepsis-overdue-item-auto-check-and-alert-message.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
