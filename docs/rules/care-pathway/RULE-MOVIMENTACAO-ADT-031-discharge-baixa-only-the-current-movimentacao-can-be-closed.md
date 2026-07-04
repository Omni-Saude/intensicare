# RULE-MOVIMENTACAO-ADT-031 — Discharge (baixa) - only the current movimentacao can be closed; frees the bed

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Closing a movimentacao is permitted only if it is the current one; it records discharge fields (motivo_baixa, data_saida, encerrado_por), deactivates the movimentacao (atual=False), and frees the bed (leito.ocupado=False). Test-asserted: POST baixa returns 200 and sets data_saida; also the create-side of the occupancy lifecycle (creating a movimentacao marks the bed ocupado=True) is asserted by the same test.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| movimentacao | pk, uuid |  |  |
| motivo_baixa | string |  |  |
| data_saida | date |  |  |
| encerrado_por | Usuario |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| closed movimentacao + freed bed | side-effect |  |

## Logic
```text
movimentacao = get_object_or_404(Movimentacao, pk)
if movimentacao.atual:
    set motivo_baixa, data_saida, encerrado_por; atual=False; save
else:
    raise ValidationError({"ultima_movimentacao":"a movimentacao enviada nao e a ultima movimentacao"})
leito = movimentacao.leito; leito.ocupado=False; leito.save()

# test-asserted lifecycle (test_movimentacao.py:537-558):
# before create: leito.ocupado == False
# after POST /movimentacoes/: mov.leito.ocupado == True
# after POST /movimentacoes/{id}/baixa/ {data_saida, motivo_baixa}: leito.ocupado == False, data_saida set, status 200
```

## Edge cases (as implemented)
404 if movimentacao not found. Freeing the bed re-triggers Leito.save alert recomputation (alerta set to None when not ocupado). Discharge endpoint returns 200 (not 201); data_saida becomes non-null after baixa.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/use_cases/movimentacao/baixa_movimentacao.py | 23-48 | 8166c07e | primary |
| ahlabs-trilhas | core/tests/test_movimentacao.py | 537-558 | 8166c07e | duplicate |
- Merged from: RULE-movimentacao-BE-04-035, RULE-CAREPATH-BE-12-027
- Related rules: RULE-MOVIMENTACAO-ADT-032, RULE-MOVIMENTACAO-ADT-055, RULE-MOVIMENTACAO-ADT-022

## Notes
Constructor param misspelled "movito_baixa"; behavior unaffected. Test source (test_movimentacao.py:537-558) is a duplicate capture that asserts BOTH the free-on-discharge half (this rule) AND the occupy-on-admission half (implemented by RULE-032); its occupy half is documented here in the logic block and cross-referenced to RULE-032.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
