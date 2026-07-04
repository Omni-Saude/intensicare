# RULE-COMUNICACAO-013 — Observation dual-mode movimentacao/leito resolution

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
try_set_movimentacao resolves the URL kwarg 'ocupacoes__pk' as EITHER a Movimentacao pk (manual bed occupation) or, if no such Movimentacao exists, as a Leito pk directly (automatica/homecare beds don't use per-admission Movimentacao records for this purpose). If the kwarg is entirely absent, nothing is set (general setor-level observation, no leito attached).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.ocupacoes__pk | uuid \| null | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| request.data.movimentacao_id | uuid | — |
| request.data.leito_id | uuid | — |
| request.data.paciente_id / paciente_automatica | uuid \| object | — |
| request.data.alerta_observacao | string enum (VERMELHO\|AMARELO\|NEUTRO) | — |

## Logic
```text
ocupacao = kwargs.get("ocupacoes__pk")
if ocupacao:
    try:
        movimentacao = Movimentacao.objects.get(pk=ocupacao)
        request.data["movimentacao_id"] = movimentacao.id
        request.data["leito_id"] = movimentacao.leito.id
        request.data["paciente_id"] = movimentacao.paciente.id
        request.data["alerta_observacao"] = movimentacao.alerta_movimentacao
    except Movimentacao.DoesNotExist:
        leito = get_object_or_404(Leito, pk=ocupacao)
        request.data["leito_id"] = leito.pk
        request.data["paciente_automatica"] = (
            leito.paciente.get_payload() if leito.paciente else leito.get_paciente_automatica
        )
        request.data["alerta_observacao"] = leito.get_alerta_leito
```

## Edge cases (as implemented)
If ocupacao is falsy (None), the method is a no-op (no leito/movimentacao association at all).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/observacao.py | 59-81 | 8166c07e | primary |
- Merged from: RULE-observacao-BE-05-007
- Related rules: RULE-COMUNICACAO-012

## Notes
Same 'ocupacoes__pk means Movimentacao-or-Leito' overload pattern appears in views/assistido.py (RULE-assistido-BE-05-003).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
