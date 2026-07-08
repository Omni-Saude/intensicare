# PLANS.md — PASSO 2.1 + 2.2: Backend Restante

> **Orquestrador:** Parreira | **Data:** 2026-07-08
> **Fonte:** PROMPT_PASSO_2_3_4.md | **Pré-requisito:** Sprint 5-8 ✅

## Status
| Wave | Descrição | Status |
|------|-----------|--------|
| 2.1-W1 | Models+Schemas (mov, presc, evol) | ✅ Complete |
| 2.1-W2 | Domain Services (3 agents) | 🔄 Running |
| 2.2-W1 | Models+Schemas (doc, form, sed) | 🔄 Running |
| 2.1-W3 | API Routers (mov, presc, evol) | ⬜ Pending |
| 2.2-W2 | Domain Services (doc, form, sed) | ⬜ Pending |
| 2.2-W3 | API Routers (doc, form, sed) | ⬜ Pending |
| W4 | Migration + Tests + Wiring | ⬜ Pending |
| W5 | Gatekeepers | ⬜ Pending |

## PASSO 2.1 (movimentacao-adt, prescricao, evolucoes)
- 11 endpoints total (4+4+3)
- 3 domain services, 3 models, 3 schemas
- movimentacao: expand domain_movimentacao.py existente

## PASSO 2.2 (documentacao, formularios-clinicos, sedacao)
- 7 endpoints total (2+3+2)
- 3 domain services, 3 models, 3 schemas
- formularios: expand api/clinical_forms.py existente
- sedacao: expand domain_pharmaco_delirium.py existente
