# RULE-DOCUMENTACAO-FATURAMENTO-015 — Auto-post released evolution to Tasy (lancamento code 501)

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | documentacao-faturamento |

## Rule
When an evolution is liberated, a Celery task calls the Tasy Oracle stored procedure amh_gerar_lancamento_auto to auto-generate a billing/record posting for the attendance, using a fixed procedure/lancamento code 501 and origin "TasyApp". Target DB depends on environment.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| cpf | string |  |  |
| nr_atendimento | string |  |  |
| codigo_evolucao | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Oracle stored-proc call (side-effect) | side-effect |  |

## Logic
```text
env = ENVIRONMENT
connection = "oracle" if env == "prod" else "homol-oracle"
cursor.callproc("amh_gerar_lancamento_auto",
  [ nr_atendimento, None, 501, "TasyApp", None, None, None, None, None, None,
    cpf, codigo_evolucao, now(localtime) ])
# ConnectionError is swallowed (pass)
```

## Edge cases (as implemented)
Fixed positional args: index2 = 501 (constant code), index3 = "TasyApp". Routes to production Oracle only when ENVIRONMENT == "prod", else homologation DB. ConnectionError is caught and ignored (silent failure -> posting may be dropped). Timestamp is localtime-aware now().

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 405-438 | 8166c07e | primary |
- Merged from: RULE-billing-BE-09-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-002

## Notes
AMBIGUOUS: the meaning of the magic constant 501 and the seven None positional params of amh_gerar_lancamento_auto is not derivable from this repo (Tasy stored proc). Recorded verbatim. Celery shared_task liberar_evolucao, routing key <ENV>.trilhas.callprocedure.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
