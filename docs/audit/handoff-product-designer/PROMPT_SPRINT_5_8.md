# PROMPT.md — Product-Design-Orchestrator (Sprint 5-8 Core Critical UI)

> **De:** Niemeyer → **Para:** product-design-orchestrator
> **Data:** 2026-07-07
> **Baseline:** `docs/audit/PLANS_SPRINT_5_8.md`
> **Stack:** Next.js 15, React 19, TypeScript strict, Tailwind 4, Storybook 8

---

## Mission

Projetar e implementar as UIs para os **4 domínios críticos** do IntensiCare. O mais importante: **trilhas-engine** — o care pathway engine que define o produto. Este é o design mais complexo do projeto: um paradigma de interação completamente novo (protocolos clínicos interativos).

## Context

Sprint 1-2 e 3-4 entregaram 12 domínios. Agora avançamos para o core do produto. O backend será construído por parreira em paralelo — usar mock data inicialmente, swappar quando APIs estiverem prontas.

## Domínios (Ordem de Prioridade)

### 1. Trilhas-Engine — `/care-pathways` ⭐⭐⭐⭐⭐

**O design mais importante do projeto.** Care pathways são protocolos clínicos interativos com:
- Motor de elegibilidade (paciente elegível para pathway X pelo tipo de leito?)
- Estados do pathway (não iniciado → screening → ativo → completado → descontinuado)
- Critérios de entrada/saída por estado
- Tracking de adesão (quais critérios foram atendidos?)
- Alertas de não-conformidade

**Layout sugerido:**
```
┌─────────────────────────────────────────────────────┐
│ Care Pathways                           [Unit: UTI 1 ▼] │
├────────────────────┬────────────────────────────────┤
│ Patient List       │ Pathway Board (selected patient) │
│ ┌────────────────┐ │ ┌──────────────────────────────┐ │
│ │ Leito 01 ●     │ │ │ Pathway: Sepse               │ │
│ │  → Sepse       │ │ │ Status: ████████░░ 80%       │ │
│ │ Leito 02 ●     │ │ │                              │ │
│ │  → Profilaxia  │ │ │ ☑ Screening (qSOFA≥2)       │ │
│ │ Leito 03 ○     │ │ │ ☑ Lactate confirmation      │ │
│ │  → Nenhum      │ │ │ ☑ Cultures collected        │ │
│ │ ...            │ │ │ ☐ Hour-1 Bundle started     │ │
│ └────────────────┘ │ │ ☐ Bundle completed (60 min)  │ │
│                    │ └──────────────────────────────┘ │
│                    │ ┌──────────────────────────────┐ │
│                    │ │ Active Alerts                │ │
│                    │ │ ⚠ Bundle overdue (12 min)    │ │
│                    │ └──────────────────────────────┘ │
└────────────────────┴────────────────────────────────┘
```

**Componentes novos:**
- `PathwayBoard` — visualização do estado atual do pathway com progresso
- `PathwayTimeline` — timeline de estados percorridos (baseado no ClinicalTimeline do Sprint 1-2)
- `PathwayCriteriaPanel` — checklist de critérios por estado (baseado no CriteriaChecklist)
- `PathwayEligibilityBadge` — indicador de elegibilidade

### 2. Ventilacao — `/ventilation`

Painel de parâmetros ventilatorios em tempo real:
- Modo ventilatório atual + FiO₂, PEEP, VC, FR
- Gráfico de tendência (PaO₂/FiO₂ nas últimas 24h)
- Driving pressure e Pplat
- Alertas de parâmetros fora do range

**Componentes:** VentilatorParameterCard, VentilationTrendChart (Recharts)

### 3. Estabilidade — `/stability`

Dashboard de estabilidade hemodinâmica:
- 27 critérios de instabilidade
- Mapa de calor (quais critérios estão alterados?)
- Tendência temporal

**Componentes:** StabilityHeatmap, StabilityCriteriaList

### 4. Piora-Clinica — `/clinical-deterioration`

Detector de deterioração clínica com scoring graduado:
- Score atual + tendência (melhorando/estável/piorando)
- Critérios que contribuíram para o score
- Timeline de eventos de deterioração

**Componentes:** DeteriorationScoreGauge, DeteriorationTimeline

## Regras

- Reutilizar componentes base do Sprint 1-2: CriteriaChecklist, ClinicalTimeline, SeverityBadge
- Tokens novos: `--clinical-pathway-*`, `--clinical-ventilation-*`, `--clinical-stability-*`, `--clinical-deterioration-*`
- WCAG AA obrigatório
- Mock data → API real quando parreira entregar
- Stories para todo componente novo
