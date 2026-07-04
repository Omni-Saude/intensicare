# RULE-MOVIMENTACAO-ADT-012 — Bed/movimentacao alert aggregation + new-alert notification

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Rolls the 4 pathway alerts into a single bed alert and fires a notification when a bed newly turns red or its red content changed.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| trilha alertas | sepse, ventilacao, sedacao, estabilidade) (list[str] |  |  |
| alerta_antigo | str |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| movimentacao.alerta_movimentacao | str enum {VERMELHO,AMARELO,NEUTRO} |  |

## Logic
```text
trilhas = [sepse.alerta, ventilacao.alerta, sedacao.alerta, estabilidade.alerta]
if 'VERMELHO' in trilhas:
    alerta = 'VERMELHO'
    if alerta_antigo != 'VERMELHO': send observacao (Mensageiro)
    else:
        conteudo_atual = conteudo_trilha_criterios(mov)
        conteudo_anterior = last Observacao(leito, texto is null, conteudo != []) by -criado_em
        if conteudo_anterior and conteudo_anterior.conteudo != conteudo_atual: send observacao
elif 'AMARELO' in trilhas: alerta = 'AMARELO'
else: alerta = 'NEUTRO'
movimentacao.save()
```

## Edge cases (as implemented)
Priority VERMELHO > AMARELO > NEUTRO. Notification only on red transition or changed red content.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_manual/facade/atualizar_alerta_movimentacao.py | 9-79 | 8166c07e | primary |
- Merged from: RULE-mov-BE-10-060
- Related rules: RULE-MOVIMENTACAO-ADT-014, RULE-MOVIMENTACAO-ADT-038, RULE-MOVIMENTACAO-ADT-040

## Notes
Called by DadosProntuario.atualizar_trilhas and by the batch task. Mensageiro/Observacao live in core (out of partition).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
