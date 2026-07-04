# RULE-OPERACIONAL-INFRA-045 — Interactive sepsis - overdue item auto-check and alert message

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
Celery task scanning interactive sepsis trilhas for overdue checklist items and emitting a delay observation message from the system user.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| trilha.leito.ocupado | bool |  |  |
| finalizado / aceito flags | bool |  |  |
| item.atraso_item_interativa | bool |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| observacao message | string |  |

## Logic

```text
For each TrilhaInterativaSpese WHERE trilha.leito.ocupado = True
    AND finalizado = False AND aceito = True:
  For each item in itens_trilha_interativa:
    checagem_envio_automatico(item)   # out-of-scope: computes atraso flag
    IF item.atraso_item_interativa:
      message = f"A checagem do item {item.nome_item} esta atrasada"
      enviar_observacao_trilha_interativa(message, tipo_trilha="sepse",
        trilha_interativa=item.trilha_interativa,
        responsavel=Usuario(username="sistema").get_pk)
```

## Edge cases (as implemented)

Only occupied beds and accepted, non-finalized interactive trilhas are scanned. The overdue predicate itself (atraso_item_interativa / checagem_envio_automatico) is computed in core.utils (out of scope). tipo_trilha hard-coded to "sepse".

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/tasks/checagem_trilha_interativa.py` | 12-28 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ops-BE-01-023`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-044](RULE-OPERACIONAL-INFRA-044-assistido-flag-reset-1-minute-update-window.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
