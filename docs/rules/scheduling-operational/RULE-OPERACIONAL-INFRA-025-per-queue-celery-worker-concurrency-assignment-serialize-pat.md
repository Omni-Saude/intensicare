# RULE-OPERACIONAL-INFRA-025 — Per-queue Celery worker concurrency assignment (serialize pathway-mutating queues)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Across demo/homol/prod uwsgi configs, the following queues are consistently run with worker concurrency forced to 1 (-c 1): atualizar_trilhas, executar_trilhas, estabelecimento_setor_leito, prescricoes, prescricao_continua, etl_dados_brutos, callprocedure. The remaining queues (log, mensagens, etl, notificacoes, amhdocs) run with default (unrestricted) concurrency.

## Outputs

| Name | Type | Unit |
|---|---|---|
| worker concurrency per queue | 1 (serialized) or default | - |

## Logic

```text
concurrency_1_queues = {atualizar_trilhas, executar_trilhas, estabelecimento_setor_leito,
                         prescricoes, prescricao_continua, etl_dados_brutos, callprocedure}
FOR queue IN all_queues:
  IF queue IN concurrency_1_queues:
    attach-daemon = "celery -A trilhas worker -n <env>-trilhas@<queue> -c 1 -E -Q <env>.trilhas.<queue>"
  ELSE:
    attach-daemon = "celery -A trilhas worker -n <env>-trilhas@<queue> -E -Q <env>.trilhas.<queue>"   # no -c
```

## Edge cases (as implemented)

Consistent across uwsgi-demo.ini, uwsgi-homol.ini, and uwsgi-prod.ini (uwsgi-old.ini has all celery lines commented out and is not an active config).

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `uwsgi/uwsgi-demo.ini, uwsgi/uwsgi-homol.ini, uwsgi/uwsgi-prod.ini` | uwsgi-demo.ini:21-32; uwsgi-homol.ini:19-30; uwsgi-prod.ini:20-33 | `8166c07e` | primary |

- Merged from: RULE-ops-BE-11-067
- Related rules: RULE-OPERACIONAL-INFRA-046, RULE-OPERACIONAL-INFRA-047, RULE-OPERACIONAL-INFRA-026

## Notes

Serializing these specific queues (all of which mutate shared Trilha/Leito rows) suggests an intentional avoidance of race conditions on pathway-state updates; recorded as an operational business rule for the rebuild's task-queue design.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
