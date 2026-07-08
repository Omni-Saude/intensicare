# EXECUTION_GUIDE.md — IntensiCare Complete Build Sequence

> **Autor:** Niemeyer (System Architect) — Deep Think Re-evaluation
> **Data:** 2026-07-07
> **Propósito:** Guia passo a passo para execução completa por AI agents, com paralelismo maximizado e dependências explícitas.
> **Status atual:** 17/27 domínios cobertos. 10 domínios + fixes restantes.

---

## Arquitetura de Execução

```
                  ┌─────────────────────────────────┐
                  │     NIEMEYER (Governança)        │
                  │     ADRs + Contratos + Gates     │
                  │     delegate_task: max 3 paral   │
                  └──────────┬──────────────────────┘
                             │ Contratos OpenAPI
                  ┌──────────┴──────────┐
                  │                     │
    ┌─────────────┴──────────┐  ┌──────┴─────────────────┐
    │   PARREIRA (Backend)   │  │ PRODUCT-DESIGNER (UI)  │
    │   domain services +    │  │ Figma → Tokens → Pages │
    │   APIs + migrations    │  │ delegate_task: max 3   │
    │   delegate_task: 3     │  │                        │
    └────────────┬───────────┘  └──────────┬──────────────┘
                 │                         │
                 └──────────┬──────────────┘
                            │
                 ┌──────────┴──────────────┐
                 │   NIEMEYER (GATE)       │
                 │   Cross-validation      │
                 │   Drift detection       │
                 │   Final verdict         │
                 └─────────────────────────┘
```

---

## REGRA FUNDAMENTAL

**Parreira (backend) e Product-Designer (UI) para o MESMO domínio rodam EM PARALELO.**
A UI começa com mock data. Quando o backend fica pronto, swappa-se o mock pela API real.
O ÚNICO pré-requisito compartilhado é o contrato OpenAPI do Niemeyer.

---

## PASSO 0 — Niemeyer: Contratos Universais (1 sessão, BLOQUEANTE)

**Por que primeiro:** Sem contratos, ninguém avança. Este passo destrava TUDO.

**O que fazer:**

### Sub-passo 0.1 — ADRs (3 em paralelo via delegate_task)

| Agente | ADRs |
|--------|------|
| Sub 1 | ADR-020 (trilhas-engine architecture) + ADR-021 (pathway data model) |
| Sub 2 | ADR-022 (ventilacao: unify vs separate) + ADR-023 (estabilidade scoring) |
| Sub 3 | ADR-024 (piora-clinica) + ADR-025 (movimentacao-adt) |

**Output:** `docs/adr/ADR-020*.md` até `ADR-025*.md`

### Sub-passo 0.2 — Contratos OpenAPI (3 em paralelo via delegate_task)

| Agente | Contratos |
|--------|-----------|
| Sub 1 | `docs/contracts/pathways-openapi.yaml` + `ventilation-openapi.yaml` |
| Sub 2 | `docs/contracts/stability-openapi.yaml` + `deterioration-openapi.yaml` |
| Sub 3 | `docs/contracts/movimentacao-openapi.yaml` + `prescricao-openapi.yaml` |

**Output:** 6 contratos OpenAPI

### Sub-passo 0.3 — Contratos Restantes (3 em paralelo via delegate_task)

| Agente | Contratos |
|--------|-----------|
| Sub 1 | `docs/contracts/evolucoes-openapi.yaml` + `documentacao-openapi.yaml` |
| Sub 2 | `docs/contracts/formularios-clinicos-openapi.yaml` + `sedacao-openapi.yaml` |
| Sub 3 | `docs/contracts/cadastros-ui-openapi.yaml` + `indicadores-openapi.yaml` + `eficiencia-openapi.yaml` |

**Output:** 7 contratos OpenAPI

### Sub-passo 0.4 — TDDs (para domínios complexos)

| Agente | TDDs |
|--------|------|
| Sub 1 | `docs/tdd/tdd-trilhas-engine.md` (completo) |
| Sub 2 | `docs/tdd/tdd-movimentacao-adt.md` |

**Output:** 2 TDDs

**Tempo estimado:** 1 sessão (30-60 min com 3 batches de delegate_task)
**Gate:** Todos os contratos validados com Spectral linting

---

## PASSO 1 — Core Critical (Parreira ∥ Product-Designer, 3 batches)

**Pré-requisito:** PASSO 0 concluído (contratos prontos)
**Paralelismo:** Parreira e Product-Designer executam SIMULTANEAMENTE

### Batch 1.1 — Parreira: Backend Core (3 agentes em paralelo)

| Agente | Domínio | Entregáveis |
|--------|---------|-------------|
| P1 | **trilhas-engine** | `domain_trilhas_engine.py`, `models/pathway.py`, `api/v1/pathways.py`, migration, testes |
| P2 | **ventilacao** | `domain_ventilacao.py` (expandir `domain_respiratory.py`), `api/v1/ventilation.py`, testes |
| P3 | **estabilidade** | `domain_estabilidade.py`, `models/stability.py`, `api/v1/stability.py`, migration, testes |

**Prompt:** `docs/audit/handoff-parreira/PROMPT_SPRINT_5_8.md`
**Verificação:** `pytest tests/test_domain_trilhas_engine.py tests/test_domain_ventilacao.py tests/test_domain_estabilidade.py`

### Batch 1.2 — Product-Designer: UI Core (3 agentes em paralelo)

| Agente | Domínio | Entregáveis |
|--------|---------|-------------|
| D1 | **trilhas-engine** | `app/care-pathways/page.tsx`, `components/PathwayBoard.tsx`, tokens `--clinical-pathway-*`, stories |
| D2 | **ventilacao** | `app/ventilation/page.tsx`, `components/VentilatorParameterCard.tsx`, tokens, stories |
| D3 | **estabilidade** | `app/stability/page.tsx`, `components/StabilityHeatmap.tsx`, tokens, stories |

**Prompt:** `docs/audit/handoff-product-designer/PROMPT_SPRINT_5_8.md`
**Dados:** Mock (contratos OpenAPI como referência)
**Verificação:** `npx tsc --noEmit` por domínio

### Batch 1.3 — Parreira + Product-Designer: Piora-Clinica + Fixes

| Agente | Tarefa | Entregáveis |
|--------|--------|-------------|
| P4 (Parreira) | **piora-clinica** backend | `domain_piora_clinica.py`, `api/v1/deterioration.py`, testes |
| D4 (Product-Designer) | **piora-clinica** UI | `app/clinical-deterioration/page.tsx`, tokens, stories |
| D5 (Product-Designer) | **Swap mocks → real** | `antimicrobial-stewardship` + `prophylaxis-bundles` migram para API real |

**Gate PASSO 1:** `ux-review-agent-loop` + `accessibility-review-agent-loop` em todas as novas páginas. `security-manager` em novos endpoints.

---

## PASSO 2 — Large Modules (Parreira ∥ Product-Designer, 2 batches)

### Batch 2.1 — Backend + UI Lote 1 (6 agentes: 3 Parreira ∥ 3 Product-Designer)

| Agente | Domínio | Camada |
|--------|---------|--------|
| P5 | **movimentacao-adt** | Backend: `domain_movimentacao.py` (expandir), `api/v1/movimentacao.py` |
| P6 | **prescricao** | Backend: `domain_prescricao.py`, `models/prescricao.py`, `api/v1/prescricao.py` |
| P7 | **evolucoes** | Backend: `domain_evolucoes.py`, `models/evolucao.py`, `api/v1/evolucoes.py` |
| D6 | **movimentacao-adt** | UI: `app/patient-movement/page.tsx`, tokens, stories |
| D7 | **prescricao** | UI: `app/prescription/page.tsx`, tokens, stories |
| D8 | **evolucoes** | UI: `app/clinical-notes/page.tsx`, tokens, stories |

### Batch 2.2 — Backend + UI Lote 2 (6 agentes: 3 Parreira ∥ 3 Product-Designer)

| Agente | Domínio | Camada |
|--------|---------|--------|
| P8 | **documentacao-faturamento** | Backend: `domain_documentacao.py`, `api/v1/documentacao.py` |
| P9 | **formularios-clinicos** | Backend: expandir `api/clinical_forms.py` |
| P10 | **sedacao** | Backend: expandir `domain_pharmaco_delirium.py`, `api/v1/sedation.py` |
| D9 | **documentacao-faturamento** | UI: `app/documentation/page.tsx` |
| D10 | **formularios-clinicos** | UI: expandir `app/clinical-forms/page.tsx` |
| D11 | **sedacao** | UI: `app/sedation/page.tsx` |

**Gate PASSO 2:** Gatekeepers independentes nos novos endpoints e páginas.

---

## PASSO 3 — Backlog Final (Parreira ∥ Product-Designer, 1 batch)

### Batch 3.1 — Últimos 3 domínios (6 agentes)

| Agente | Domínio | Camada |
|--------|---------|--------|
| P11 | **cadastros-ui** | Backend: `api/v1/registry.py` |
| P12 | **indicadores-etl** | Backend: `api/v1/indicators.py` |
| P13 | **eficiencia** | Backend: `domain_eficiencia.py`, `api/v1/efficiency.py` |
| D12 | **cadastros-ui** | UI: expandir `app/admin/` |
| D13 | **indicadores-etl** | UI: `app/indicators/page.tsx` |
| D14 | **eficiencia** | UI: `app/efficiency/page.tsx` |

---

## PASSO 4 — Correções de Gap Pendentes (Parreira)

**O que:** 6 missing-consumer endpoints + 4 mocked features → real + 3 path mismatches

### Batch 4.1

| Agente | Correção |
|--------|----------|
| P14 | `GET /api/v1/alerts/{id}/trace` — documentar / expor frontend consumer |
| P15 | Unificar `patients/{id}/status` → `patients/{id}/detail` |
| P16 | Criar `POST/GET /api/v1/alert-routing` (substitui mock) |

### Batch 4.2

| Agente | Correção |
|--------|----------|
| P17 | Corrigir `POST /api/clinical-forms` schema (mpiId/formId → form_type) |
| P18 | Adicionar `GET /api/v1/thresholds/{id}` consumer no frontend |
| P19 | Implementar SSE `/api/v1/events/stream` ou remover fallback |

---

## PASSO 5 — Niemeyer: GATE Final (1 sessão, BLOQUEANTE)

**O que:** Verificação completa de todos os 27 domínios.

### Sub-passo 5.1 — Cross-Validation (3 agentes em paralelo)

| Agente | Escopo |
|--------|--------|
| Sub 1 | Validar todos os backend services × contratos OpenAPI (drift detection) |
| Sub 2 | Validar todas as páginas frontend × contratos OpenAPI (API calls conferem?) |
| Sub 3 | A11y re-scan automatizado em TODAS as páginas novas |

### Sub-passo 5.2 — Build + Integração

| Ação | Comando |
|------|---------|
| Backend | `pytest` — todos os testes |
| Backend | `alembic upgrade head` — todas as migrations |
| Frontend | `npx tsc --noEmit` — zero erros |
| Frontend | `npm run build` — build completo |

### Sub-passo 5.3 — Veredito Final

Produzir `docs/audit/GOVERNANCE_FINAL_VERDICT.md` com:
- Matriz 27×27 (domínio × backend × API × frontend) — todos COBERTOS?
- Scorecard de qualidade arquitetural
- Recomendações para produção

---

## MAPA DE PARALELISMO (Visual)

```
TEMPO →
─────────────────────────────────────────────────────────────────────────

PASSO 0 (Niemeyer — 1 sessão, BLOQUEANTE)
  [ADR batch 1 ∥ ADR batch 2 ∥ ADR batch 3]
  [Contracts batch 1 ∥ Contracts batch 2 ∥ Contracts batch 3]
  [TDD batch 1]
  ════════════════════════════════════════════ GATE: Contratos validados

PASSO 1 (Parreira ∥ Product-Designer — PARALELO)
  [P1: trilhas-engine BE ∥ P2: ventilacao BE ∥ P3: estabilidade BE]
  [D1: trilhas-engine UI ∥ D2: ventilacao UI ∥ D3: estabilidade UI]
  [P4: piora-clinica BE + D4: piora-clinica UI + D5: swap mocks→real]
  ════════════════════════════════════════════ GATE: UX + A11y + Security

PASSO 2 (Parreira ∥ Product-Designer — PARALELO)
  [P5: movimentacao ∥ P6: prescricao ∥ P7: evolucoes]
  [D6: movimentacao ∥ D7: prescricao ∥ D8: evolucoes]
  [P8: documentacao ∥ P9: formularios ∥ P10: sedacao]
  [D9: documentacao ∥ D10: formularios ∥ D11: sedacao]
  ════════════════════════════════════════════ GATE

PASSO 3 (Parreira ∥ Product-Designer — PARALELO)
  [P11 ∥ P12 ∥ P13] ∥ [D12 ∥ D13 ∥ D14]
  ════════════════════════════════════════════ GATE

PASSO 4 (Parreira — CORREÇÕES)
  [P14 ∥ P15 ∥ P16] → [P17 ∥ P18 ∥ P19]

PASSO 5 (Niemeyer — GATE FINAL)
  [Cross-val ∥ A11y scan ∥ Build check] → VERDICT
─────────────────────────────────────────────────────────────────────────
```

---

## RESUMO: O QUE VOCÊ (HUMANO) PRECISA FAZER

### Sessão 1 — Disparar PASSO 0
```
1. Abrir chat com Niemeyer
2. Colar: "Execute docs/audit/PROMPT_NIEMEYER_SPRINT_5_8.md"
3. Aguardar contratos + ADRs + TDDs
4. VERIFICAR: todos os arquivos em docs/contracts/ e docs/adr/
```

### Sessão 2 — Disparar PASSO 1 (2 chats em paralelo)
```
1. Abrir chat com Parreira
   → "Execute docs/audit/handoff-parreira/PROMPT_SPRINT_5_8.md"
2. Abrir OUTRO chat com Product-Design-Orchestrator
   → "Execute docs/audit/handoff-product-designer/PROMPT_SPRINT_5_8.md"
3. Aguardar ambos completarem
```

### Sessão 3 — Disparar PASSO 2 + 3 + 4 (2 chats em paralelo)
```
1. Chat Parreira:
   → "Continue com docs/audit/handoff-parreira/PROMPT_SPRINT_5_8.md — Batch 2.1"
   → depois: "Batch 2.2, depois Batch 3.1, depois PASSO 4"
2. Chat Product-Designer:
   → "Continue com docs/audit/handoff-product-designer/PROMPT_SPRINT_5_8.md — Batch 2.1"
   → depois: "Batch 2.2, depois Batch 3.1"
```

### Sessão 4 — Disparar PASSO 5 (GATE FINAL)
```
1. Chat Niemeyer:
   → "Execute GATE final: cross-validation de todos os 27 domínios"
   → Output: GOVERNANCE_FINAL_VERDICT.md
```

---

## MÉTRICAS DE PROGRESSO

| PASSO | Domínios | Backend | Frontend | Duração Estimada |
|-------|----------|---------|----------|-----------------|
| 0 | 13 (contratos) | — | — | 1 sessão |
| 1 | 4 core | 4 services | 4 pages | 2-3 sessões |
| 2 | 6 large | 6 services | 6 pages | 2-3 sessões |
| 3 | 3 backlog | 3 services | 3 pages | 1 sessão |
| 4 | fixes | correções | — | 1 sessão |
| 5 | gate | verificação | verificação | 1 sessão |
| **TOTAL** | **13 novos + 14 existentes = 27** | **completo** | **completo** | **6-9 sessões** |
