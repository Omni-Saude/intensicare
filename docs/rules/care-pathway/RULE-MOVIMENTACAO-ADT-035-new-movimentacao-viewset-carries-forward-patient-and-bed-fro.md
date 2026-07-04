# RULE-MOVIMENTACAO-ADT-035 — New movimentacao viewset carries forward patient and bed from the previous record

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
MovimentacaoNovaViewSet.create resolves the PREVIOUS Movimentacao from movimentacoes__pk, then forces the new record's paciente and leito to match that previous record (this route does not change beds - it records a subsequent movimentacao entry on the SAME bed/patient), links ultima_movimentacao to the previous pk, forces atualizado_por to the current user, then hands off to NovaMovimentacao.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.movimentacoes__pk | uuid |  |  |
| request.data.dados_prontuario | object |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| movimentacao | object |  |

## Logic
```text
ultima_movimentacao = get_object_or_404(Movimentacao, pk=kwargs["movimentacoes__pk"])
request.data["ultima_movimentacao"] = str(ultima_movimentacao.pk)
request.data["paciente"] = ultima_movimentacao.paciente.pk
request.data["leito"] = ultima_movimentacao.leito.pk
request.data["atualizado_por"] = request.user.pk
movimentacao = super().create(request, *args, **kwargs)
dados_prontuario["ultima_movimentacao"] = str(ultima_movimentacao.pk)
dados_prontuario["movimentacao"] = movimentacao.data["id"]
NovaMovimentacao(dados_prontuario)
return movimentacao
```

## Edge cases (as implemented)
@transaction.atomic wraps the whole operation. permission_trilhas=('can_add_movimentacao',), no exceto_metodo.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/movimentacao.py` | 133-162 | `8166c07e` | primary |

- Merged from: RULE-movimentacao-BE-05-004
- Related rules: RULE-MOVIMENTACAO-ADT-034, RULE-MOVIMENTACAO-ADT-056

## Notes
NovaMovimentacao use case (RULE-034) is a distinct layer; this rule captures the view-layer field-injection/orchestration.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
