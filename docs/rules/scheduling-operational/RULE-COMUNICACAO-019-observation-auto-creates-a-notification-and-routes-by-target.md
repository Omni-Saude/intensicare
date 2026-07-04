# RULE-COMUNICACAO-019 — Observation auto-creates a notification and routes by target

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
A newly created Observacao with a sector spawns a Notificacao; its websocket message type is "leito" if bound to a bed, else "setor".

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| setor | Setor FK | — | — |
| leito | Leito FK\|null | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Notificacao + tipo_mensagem | side-effect/string | — |

## Logic
```text
@transaction.atomic save():
  if (not exists) and setor is not None:
      Notificacao(observacao=self).save()   # triggers RULE-027
  super().save()
tipo_mensagem = "leito" if self.leito else "setor"
Meta.ordering = ["-criado_em"] (newest first)
```

## Edge cases (as implemented)
No notification if setor is None or on update. Observacao also stores paciente_automatica/paciente_homecare JSON snapshots and a conteudo JSON array.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/observacao.py | 72-108 | 8166c07e | primary |
- Merged from: RULE-observacao-BE-04-028
- Related rules: RULE-COMUNICACAO-017, RULE-COMUNICACAO-011, RULE-COMUNICACAO-039

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
