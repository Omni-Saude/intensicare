# RULE-MOVIMENTACAO-ADT-033 — First admission (Primeira Movimentacao) viewset - forced fields and downstream workflow

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
MovimentacaoViewSet.create runs MovimentacaoValidation first, then forces registrado_por to the current user and leito to the leitos__pk URL kwarg (server-side, ignoring client values), resolves/creates the patient via CadastrarPaciente, creates the Movimentacao row, and hands dados_prontuario (tagged with the new movimentacao id) to the PrimeiraMovimentacao use case.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.leitos__pk | uuid |  |  |
| request.data.paciente | object |  |  |
| request.data.dados_prontuario | object |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| movimentacao | object |  |

## Logic
```text
MovimentacaoValidation(request, kwargs).validate()
request.data["registrado_por"] = request.user.pk
request.data["leito"] = kwargs.get("leitos__pk")
request.data["paciente"] = CadastrarPaciente(request.data.get("paciente")).create()
movimentacao = super().create(request, *args, **kwargs)
dados_prontuario = request.data.pop("dados_prontuario")
dados_prontuario["movimentacao"] = movimentacao.data["id"]
PrimeiraMovimentacao(dados_prontuario)
return movimentacao
```

## Edge cases (as implemented)
Entire operation wrapped in @transaction.atomic. permission_trilhas=('can_create_paciente',) with exceto_metodo='GET' (list/retrieve bypass the permission check).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/movimentacao.py` | 43-66 | `8166c07e` | primary |

- Merged from: RULE-movimentacao-BE-05-002
- Related rules: RULE-MOVIMENTACAO-ADT-032, RULE-MOVIMENTACAO-ADT-041, RULE-MOVIMENTACAO-ADT-062

## Notes
MovimentacaoValidation, CadastrarPaciente, and PrimeiraMovimentacao live in core/use_cases; this rule captures the view-layer orchestration/field-injection (distinct layer from RULE-032).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
