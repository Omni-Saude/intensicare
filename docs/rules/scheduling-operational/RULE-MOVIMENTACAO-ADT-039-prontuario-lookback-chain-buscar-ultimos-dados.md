# RULE-MOVIMENTACAO-ADT-039 — Prontuario lookback chain (buscar_ultimos_dados)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
Builds the set of prontuario PKs to search for 12h/24h historical criteria by walking the ultima_movimentacao chain.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| movimentacao.ultima_movimentacao chain | linked list |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| list of dados_prontuario PKs | as str) (list[str] |  |

## Logic
```text
ultimos = [self.pk]
obj = self
while True:
  if ultima_movimentacao lacks get_pk: break
  if ultima_movimentacao has dados_prontuario:
      append prev dados_prontuario.pk; obj = that prontuario
return ultimos
```

## Edge cases (as implemented)
Potential infinite loop if a movimentacao has ultima_movimentacao.get_pk but no dados_prontuario (obj is not advanced -> while True never breaks). Terminates only when the chain end lacks get_pk or the loop advances.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 163-175,299-311 | `8166c07e` | primary |

- Merged from: RULE-mov-BE-10-063
- Related rules: RULE-MOVIMENTACAO-ADT-034, RULE-MOVIMENTACAO-ADT-009

## Notes
Two variants - buscar_ultimos_dados (pks) and buscar_ultimos_dados_objetos (objects). Underpins sepse C6/C8/C10/C11/C14/C15/C17 and estabilidade C2. A sibling chain-walk (buscar_ultimas_movimentacoes) exists in core/models/movimentacao.py:90-100.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
