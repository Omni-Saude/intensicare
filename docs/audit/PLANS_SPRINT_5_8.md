# PLANS.md — Sprint 5-8 Core Critical

> **Fase:** Core Critical — os domínios que definem o produto
> **Data:** 2026-07-07
> **Pré-requisito:** Sprint 1-2 ✅ (UI Quick Wins) + Sprint 3-4 ✅ (Backend Novos + UI Parciais)
> **Agentes:** Niemeyer (contratos/governança), Parreira (backend), Product-Designer (UI)

---

## O Que Já Foi Entregue (12 domínios)

| Sprint | Domínios | Status |
|--------|----------|--------|
| 1-2 | sepse, antimicrobiano, profilaxia | ✅ Frontend + Backend |
| 3-4 | nutricao, fluid-balance, comunicacao, tenancy, auditoria | ✅ Frontend (parcial backend) |
| — | sinais-vitais, auth-usuarios, clinical-scoring, alertas, operacional-infra | ✅ Já existiam |

---

## O Que Falta (15 domínios)

| Prioridade | Domínios | Regras | Impacto |
|------------|----------|--------|---------|
| 🔴 **CORE** | trilhas-engine, ventilacao, estabilidade, piora-clinica | 85 | Define o produto |
| 🟠 **ALTA** | movimentacao-adt, prescricao, evolucoes | 198 | Operação da UTI |
| 🟡 **MÉDIA** | documentacao-faturamento, formularios-clinicos, sedacao, cadastros-ui, indicadores-etl, eficiencia | 207 | Qualidade/suporte |

---

## Sprint 5-8: Core Critical (4 domínios, 85 regras)

### Domínios

| # | Domínio | Regras | Complexidade | Por que é crítico |
|---|---------|--------|-------------|-------------------|
| 1 | **trilhas-engine** | 18 | ⭐⭐⭐⭐⭐ | **O produto.** Care pathway engine com motor de elegibilidade e protocolos interativos. Sem isso, IntensiCare é só um sistema de alertas. |
| 2 | **ventilacao** | 27 | ⭐⭐⭐⭐ | Parâmetros ventilatorios em tempo real. Essencial para UTI. |
| 3 | **estabilidade** | 27 | ⭐⭐⭐⭐ | Detecção de instabilidade hemodinâmica. 27 critérios. |
| 4 | **piora-clinica** | 13 | ⭐⭐⭐ | Deterioração clínica com scoring graduado. Complementa estabilidade. |

### Divisão de Trabalho

```
FASE 0 — Design Review (Niemeyer + Product-Designer, 1 dia)
├─ ADRs para cada domínio
├─ Wireframes de alto nível para trilhas-engine
└─ Contratos OpenAPI para todos os 4 domínios

FASE 1 — Backend (Parreira, 2-3 semanas)
├─ domain_trilhas_engine.py (care pathway engine)
├─ domain_ventilacao.py (já tem domain_respiratory.py — expandir)
├─ domain_estabilidade.py
├─ domain_piora_clinica.py
└─ APIs REST para todos

FASE 2 — Frontend (Product-Designer, 2-3 semanas)
├─ /care-pathways (trilhas-engine UI — a mais complexa)
├─ /ventilation (painel de parâmetros ventilatorios)
├─ /stability (dashboard de estabilidade hemodinâmica)
└─ /clinical-deterioration (detecção de piora clínica)
```

### Marcos (Milestones)

| M# | O que | Quem | Depende de |
|----|-------|------|-----------|
| M0 | ADRs + Contratos | Niemeyer | — |
| M1 | Backend trilhas-engine | Parreira | M0 |
| M2 | Backend ventilacao + estabilidade + piora | Parreira | M0 |
| M3 | Frontend trilhas-engine | Product-Designer | M1 |
| M4 | Frontend ventilacao + estabilidade | Product-Designer | M2 |
| M5 | Frontend piora-clinica | Product-Designer | M2 |
| M6 | Integração + GATE | Niemeyer | M3, M4, M5 |
