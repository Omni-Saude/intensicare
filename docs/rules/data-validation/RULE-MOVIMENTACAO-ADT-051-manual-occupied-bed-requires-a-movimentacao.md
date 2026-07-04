# RULE-MOVIMENTACAO-ADT-051 — Manual occupied bed requires a movimentacao

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
For manual beds, an occupied bed with no movimentacao is an error; an empty bed returns only the bed payload.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| leito.tipo | str |  |  |
| leito.ocupado | bool |  |  |
| movimentacao | Movimentacao \| None |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| payload | dict |  |

## Logic
```text
if leito.tipo == 'manual':
  if leito.ocupado:
      if movimentacao: return movimentacao.get_payload()
      else: raise ParseError("...leito ocupado sem movimentacao")
  else: return {'id': leito.pk, 'leito': leito.get_payload()}
return OcupacaoSerializer(leito).data
```

## Edge cases (as implemented)
Retrieve of a non-existent Movimentacao falls back to Leito lookup (automatica/homecare micro-indicators) else ParseError "Movimentacao nao existe".

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/api/v1/views/ocupacoes.py` | 30-48,99-142 | `8166c07e` | primary |

- Merged from: RULE-op-BE-10-065
- Related rules: RULE-MOVIMENTACAO-ADT-024, RULE-MOVIMENTACAO-ADT-002

## Notes
retrieve() also triggers dados_prontuario.atualizar_trilhas() and surfaces micro-indicadores (tempo_internacao, vm, dva, sedacao).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
