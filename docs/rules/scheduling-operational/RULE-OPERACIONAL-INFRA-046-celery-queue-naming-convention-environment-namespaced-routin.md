# RULE-OPERACIONAL-INFRA-046 — Celery queue naming convention — environment-namespaced routing keys

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
Every Celery queue/routing-key in the project is namespaced by the ENVIRONMENT variable (e.g. 'prod.trilhas.amhdocs', 'demo.trilhas.etl'), so the same RabbitMQ broker can host isolated queues per deployment environment (demo/homol/prod) without collision. 12 queues are declared: atualizar_trilhas, log, mensagens, etl, executar_trilhas, estabelecimento_setor_leito, etl_dados_brutos, prescricoes, prescricao_continua, notificacoes, callprocedure, amhdocs.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| ENVIRONMENT | string |  | e.g. demo \| homol \| prod \| '' (default) |

## Outputs

| name | type | unit |
|---|---|---|
| Queue/routing_key | string |  |

## Logic

```text
FOR queue_name IN [atualizar_trilhas, log, mensagens, etl, executar_trilhas,
                   estabelecimento_setor_leito, etl_dados_brutos, prescricoes,
                   prescricao_continua, notificacoes, callprocedure, amhdocs]:
  Queue(
    name = f"{os.environ.get('ENVIRONMENT','')}.trilhas.{queue_name}",
    routing_key = f"{os.environ.get('ENVIRONMENT','')}.trilhas.{queue_name}",
  )
task_default_exchange = "trilhas"; task_default_exchange_type = "direct"; task_default_queue = "default"
```

## Edge cases (as implemented)

If ENVIRONMENT is unset, queue names begin with a leading '.' (e.g. '.trilhas.log') since the empty-string default is still concatenated with the '.' separator.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/celery.py` | 21-71 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-ops-BE-11-066`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-025](RULE-OPERACIONAL-INFRA-025-per-queue-celery-worker-concurrency-assignment-serialize-pat.md)
- [RULE-OPERACIONAL-INFRA-047](RULE-OPERACIONAL-INFRA-047-celery-beat-scheduler-databasescheduler-with-a-duplicate-bea.md)

## Notes

Matches the -Q flags seen in the uwsgi ini attach-daemon lines (RULE-ops-BE-11-067) and the routing_key in utils/integracoes.py's enviar_arquivo_amhdocs task.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
