# Plano de Reconstrução do Frontend IntensiCare v3
## Arquitetura Orientada à Jornada do Intensivista (UX-First, Pathway-Centric)

**Autor:** Niemeyer (System Architect)  
**Data:** 2026-07-09  
**Versão:** 2.0.0  
**Status:** Draft → Aguardando aprovação  
**Princípio:** UX precede design. A jornada completa do intensivista é o fator organizador principal.  

---

## Sumário Executivo

O frontend atual (v2) tem 33 páginas, mas 17 delas tratam domínios clínicos como aplicativos independentes. **O erro não foi técnico — foi de UX.** Páginas bonitas e isoladas que não resolvem a jornada do intensivista: "este paciente está bem? Quais riscos ele apresenta agora? O que eu preciso fazer?"

O backend tem a arquitetura correta — **9 trilhas clínicas (YAML) → motor de avaliação → scores → alertas**. O backend é a spec canônica.

**A solução:** construir um frontend **100% novo, do zero**, onde cada decisão de interface responde a uma pergunta da jornada do intensivista. A trilha clínica é o frame natural porque o médico pensa em termos de "este paciente está na trilha de sepse, em tratamento ativo, com PAM crítica — preciso agir".

**Nada do frontend v2 é reaproveitado.** Design tokens, componentes, API client — tudo é reconstruído a partir da especificação do backend e da jornada do usuário.

---

## 0. Princípios Fundamentais (Imutáveis)

> **1. UX precede Design.** Nenhum componente é desenhado antes de responder: "que pergunta do intensivista este componente responde?"
>
> **2. A jornada completa é o fator organizador principal.** Dashboard → Patient → Pathway → Ação. Não existem páginas isoladas.
>
> **3. O backend é a única spec canônica.** Endpoints, schemas OpenAPI, definições YAML das trilhas — tudo que o frontend renderiza vem de lá.
>
> **4. Densidade de informação com clareza visual.** UTI não é dashboard de marketing. O intensivista precisa ver MUITA informação em POUCO espaço, com severidade codificada por cor e posição.
>
> **5. Zero clicks desnecessários.** Se a informação existe no backend e é clinicamente relevante, ela está a ≤2 cliques de distância.
>
> **6. Segurança e privacidade por design.** PHI, JWT in-memory, CSP, RBAC — desde a primeira linha de código.

---

## 1. A Jornada do Intensivista (Fio Condutor)

```
MANHÃ — ROUND MULTIDISCIPLINAR (desktop, tela grande)

  1. "Quantos pacientes tenho na UTI hoje? Algum crítico?"
     → DASHBOARD: grid de leitos, scores (MEWS/NEWS2), badges de severidade

  2. "Este paciente específico — quais riscos ele apresenta?"
     → PATIENT DETAIL: vitais, scores, timeline, e TODAS as trilhas ativas

  3. "A trilha de sepse está em qual estado? Quais critérios estão violados?"
     → PATHWAY VIEW: estado atual, critérios com severidade, recomendações

  4. "Preciso agir. Qual a recomendação baseada em evidência?"
     → RECOMMENDATIONS: guideline SSC-2021, ação sugerida

NOITE — PLANTÃO (tablet, troca de turno)

  5. "Quais alertas estão ativos agora em todas as UTIs?"
     → ALERT TRIAGE: todos os alertas, filtráveis, acionáveis

  6. "O que mudou desde meu último plantão?"
     → PATHWAY HISTORY: transições de estado, tendências (melhorando/piorando)

AÇÃO IMEDIATA — CÓDIGO AZUL (qualquer dispositivo)

  7. "Alerta crítico! De onde veio? Qual critério disparou?"
     → ALERT TRACE: rastreabilidade reversa (alerta ← threshold ← score ← critério)
```

**Cada página, cada componente, cada rota responde a uma dessas perguntas.** Se não responder, não existe.

---

## 2. Diagnóstico do Erro Atual

### 2.1 O erro de UX (não técnico)

```
JORNADA REAL DO INTENSIVISTA:

  "Preciso entender o paciente do leito 3."
  → Abre /dashboard
  → Clica no paciente
  → Vê vitals e scores (ok)
  → "Ele está na trilha de sepse? E de ventilação? E renal?"
  → NÃO EXISTE UMA PÁGINA QUE MOSTRE ISSO JUNTO
  → Abre /sepse-dashboard em outra aba
  → Abre /ventilation em outra aba
  → Abre /renal... (não existe)
  → Abre /stability
  → Abre /antimicrobial-stewardship
  → 5 abas abertas para 1 paciente
  → "Isso não é um centro de comando. É um quebra-cabeça."
```

### 2.2 Evidência quantitativa

| Indicador | Valor |
|-----------|-------|
| Páginas totais | 33 |
| Páginas de domínio standalone | 17 (52%) |
| Páginas que respondem a perguntas da jornada | ~8 (24%) |
| Cliques para ver todas as trilhas de 1 paciente | 5+ (5 abas diferentes) |
| Cliques na arquitetura correta | 2 (Dashboard → Patient → Pathway) |

---

## 3. Arquitetura-Alvo

### 3.1 Modelo de Navegação (6 páginas, 2 cliques de profundidade)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD  (/)                                │
│  "Quantos pacientes? Algum crítico?"                             │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Leito 1  │ │ Leito 2  │ │ Leito 3  │ │ Leito 4  │           │
│  │ MEWS 4   │ │ MEWS 2   │ │ MEWS 6 🔴│ │ MEWS 1   │           │
│  │ ⚠️ S R V │ │ ✅ S R V │ │ 🔴 S R V │ │ ✅ S R V │           │
│  └────┬─────┘ └──────────┘ └────┬─────┘ └──────────┘           │
│       │                         │                                │
│       ▼                         ▼                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         PATIENT DETAIL  (/patient/[mpi_id])               │   │
│  │  "Quais riscos este paciente apresenta?"                   │   │
│  │                                                            │   │
│  │  ┌─ Header: nome, leito, MEWS/NEWS2 ao vivo ──────────┐   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │  ┌─ Vitals (HR, BP, SpO₂, Temp, RR) ──────────────────┐   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │  ┌─ TRILHAS ATIVAS ────────────────────────────────────┐   │   │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │   │   │
│  │  │  │ Sepse  │ │ Renal  │ │ Resp.  │ │ Vent.  │ ...   │   │   │
│  │  │  │ ⚠️ urg │ │ ✅ norm│ │ 🔴 crit│ │ ✅ norm│       │   │   │
│  │  │  │ 4/7    │ │ 5/5    │ │ 2/4    │ │ 6/6    │       │   │   │
│  │  │  └───┬────┘ └────────┘ └────────┘ └────────┘       │   │   │
│  │  └──────┼──────────────────────────────────────────────┘   │   │
│  │         │                                                    │   │
│  │         ▼                                                    │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  PATHWAY VIEW  (/patient/[mpi_id]/pathway/[id])      │   │   │
│  │  │  "Qual o estado? Quais critérios? O que fazer?"      │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌─ State Machine ───────────────────────────────┐   │   │   │
│  │  │  │  initial → confirmacao → tratamento → estab   │   │   │   │
│  │  │  │                                    ↑ ATUAL    │   │   │   │
│  │  │  └──────────────────────────────────────────────┘   │   │   │
│  │  │  ┌─ Critérios (com severidade) ─────────────────┐   │   │   │
│  │  │  │  🔴 PAM 58 mmHg      threshold: ≥65          │   │   │   │
│  │  │  │  ⚠️ Lactato 3.2       threshold: <2.0         │   │   │   │
│  │  │  │  ✅ qSOFA 1           threshold: ≥2           │   │   │   │
│  │  │  │  ❌ ATB 1h            não administrado        │   │   │   │
│  │  │  └──────────────────────────────────────────────┘   │   │   │
│  │  │  ┌─ Recomendações ──────────────────────────────┐   │   │   │
│  │  │  │  SSC-2021: Cristaloide 30 mL/kg em 3h        │   │   │   │
│  │  │  │  SSC-2021: Reavaliar volemia em 6h           │   │   │   │
│  │  │  └──────────────────────────────────────────────┘   │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    ALERT TRIAGE  (/alerts)                                │   │
│  │    "Quais alertas estão ativos?" → filtrar, agir, auditar │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    PATHWAY CATALOG  (/pathways)                           │   │
│  │    "Quais trilhas existem? Como são definidas?"           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    ADMIN  (/admin)                                        │   │
│  │    Usuários, thresholds, tenancy                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Seis Páginas (cada uma responde a perguntas da jornada)

| # | Rota | Pergunta que responde | Fonte de Dados |
|---|------|----------------------|----------------|
| 1 | `/` | "Quantos pacientes? Algum crítico?" | `GET /api/v1/dashboard` |
| 2 | `/patient/[mpi_id]` | "Quais riscos este paciente apresenta?" | `GET /api/v1/patients/{mpi_id}/detail` + `GET .../pathways` |
| 3 | `/patient/[mpi_id]/pathway/[pp_id]` | "Qual estado? Quais critérios violados? O que fazer?" | `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress` |
| 4 | `/alerts` | "Quais alertas ativos? De onde vieram?" | `GET /api/v1/alerts` + POST actions |
| 5 | `/pathways` | "Quais trilhas existem? Como são definidas?" | `GET /api/v1/pathways` + `GET .../{id}` |
| 6 | `/admin` | "Quem acessa? Quais thresholds?" | `/admin/*` |

---

## 4. Arquitetura de Componentes

### 4.1 Árvore Completa (tudo novo, nada do v2)

```
<AppShell>                              ← shell: sidebar hierárquica + breadcrumb + tenant
├── <TenantProvider>                    ← contexto de tenant (hospital/UTI)
├── <ErrorBoundary>                     ← graceful degradation
│
├── [Dashboard] /
│   ├── <UnitFilter>                    ← "UTI-ADULTO", "UTI-CORONARIANA", "Todas"
│   ├── <StatsBar>                      ← totais: pacientes, alertas, críticos, MEWS≥5
│   ├── <BedGrid>                       ← grid responsivo de leitos
│   │   └── <BedCard>[]                 ← card de leito
│   │       ├── <SeverityDot>           ← bolinha verde/âmbar/laranja/vermelha pulsante
│   │       ├── <PatientIdentity>       ← nome, leito, unidade
│   │       ├── <ScorePair>             ← MEWS + NEWS2 lado a lado
│   │       ├── <PathwayBadges>         ← mini-badges das trilhas ativas (S R V N...)
│   │       └── <VitalsInline>          ← HR, SpO₂, BP em uma linha
│   └── <EmptyState>                    ← "Nenhum paciente internado"
│
├── [Patient Detail] /patient/[mpi_id]
│   ├── <PatientHeader>                 ← nome, MPI, leito, unidade, scores, WS status
│   ├── <VitalsPanel>                   ← última aferição com severidade por threshold
│   │   └── <VitalReadout>[]            ← HR, BP, SpO₂, Temp, RR, AVPU, O₂
│   ├── <ScoreTimeline>                 ← MEWS + NEWS2 históricos (gráfico sparkline + tabela)
│   │   └── <ScorePoint>[]              ← data, valor, tendência
│   ├── <ActivePathways>                ← ⬅ CORAÇÃO DA PÁGINA
│   │   └── <PathwayCard>[]             ← nome, estado, severidade, progresso (n/m)
│   │       ├── <SeverityGlow>          ← borda colorida pulsante se critical
│   │       ├── <StateLabel>            ← "Tratamento Ativo" / "Estabilização"
│   │       └── <MiniProgress>          ← barra: 4/7 critérios OK
│   ├── <AlertsPanel>                   ← alertas ativos deste paciente
│   │   └── <AlertItem>[]               ← severidade, título, data, ação rápida
│   └── <Timeline>                      ← vitais + evoluções em linha do tempo
│
├── [Pathway View] /patient/[mpi_id]/pathway/[pp_id]
│   ├── <PathwayHeader>                 ← "Sepse — Paciente X — Tratamento Ativo"
│   ├── <StateFlow>                     ← máquina de estados visual
│   │   └── <StatePill>[]               ← cada estado: cor, label, status (past/current/future)
│   ├── <CriteriaList>                  ← lista de critérios com severidade
│   │   └── <CriteriaRow>[]             ← expansível
│   │       ├── <SeverityIcon>          ← 🔴⚠️✅❌
│   │       ├── <CriteriaValue>         ← "PAM: 58 mmHg"
│   │       ├── <ThresholdMarker>       ← "limiar: ≥65 mmHg"
│   │       └── <CriteriaEvidence>      ← expandido: guideline, banda, histórico
│   ├── <RecommendationsPanel>          ← extraído do YAML (evidence.recommendations)
│   │   └── <RecommendationCard>[]      ← guideline + ação específica
│   └── <TransitionHistory>             ← histórico de mudanças de estado
│       └── <TransitionRow>[]           ← from → to, timestamp, motivo
│
├── [Alert Triage] /alerts
│   ├── <FilterBar>                     ← severidade, unidade, trilha, status, período
│   ├── <AlertTable>                    ← tabela densa e escaneável
│   │   └── <AlertRow>[]                ← expandível
│   │       ├── <SeverityBadge>
│   │       ├── <PatientLink>           ← link para Patient Detail
│   │       ├── <PathwayLink>           ← link para Pathway View
│   │       └── <QuickActions>          ← acknowledge / escalate / resolve
│   └── <AlertTrace>                    ← rastreabilidade: alerta ← threshold ← score ← critério
│
├── [Pathway Catalog] /pathways
│   ├── <PathwayGrid>                   ← cards das 9 trilhas
│   │   └── <PathwayDefCard>[]          ← nome, descrição, versão, nº critérios/estados
│   ├── <YamlViewer>                    ← definição YAML com syntax highlight
│   └── <PathwayTester>                 ← testar trilha contra paciente real
│
└── [Admin] /admin
    ├── <UserManager>                   ← CRUD usuários
    ├── <ThresholdEditor>               ← thresholds por score/unidade
    ├── <TenantConfig>                  ← empresas, estabelecimentos
    └── <AuditLog>                      ← registro de ações
```

### 4.2 Zero reaproveitamento — tudo nasce da spec

Nenhum componente do v2 é copiado. Cada componente é projetado a partir de:
1. **A pergunta da jornada que ele responde** (Seção 1)
2. **O schema OpenAPI do endpoint que ele consome** (`docs/contracts/pathways-openapi.yaml`)
3. **A definição YAML da trilha** que ele renderiza (`_work/alerts/pathways/sepse.yaml`)

---

## 5. Modelo de Dados (TypeScript — derivado dos schemas OpenAPI)

### 5.1 Schemas core (extraídos de `pathways-openapi.yaml`)

```typescript
// ── Trilha (definição) ──

interface Pathway {
  id: number;
  name: string;            // "Sepse"
  slug: string;            // "sepse"
  description: string;     // "Acompanhamento conforme SSC-2021..."
  active: boolean;
  states: PathwayState[];
  criteria: PathwayCriteriaDef[];
  evidence?: {
    guideline: string;     // "Surviving Sepsis Campaign 2021"
    doi: string;
    recommendations: string[];
  };
}

interface PathwayState {
  id: string;              // "confirmacao"
  name: string;            // "Confirmação Diagnóstica"
  order: number;           // 1
  description: string;
  is_terminal: boolean;
}

interface PathwayCriteriaDef {
  id: string;              // "crit-sep-lactato"
  name: string;            // "Lactato Sérico"
  category: string;        // "laboratorial"
  description: string;
  unit: string;            // "mmol/L"
  normal_range: string;    // "< 2.0"
  alert_threshold: string; // "> 2.0"
}

// ── Paciente na Trilha ──

interface PatientPathway {
  id: number;
  mpi_id: string;
  pathway: Pathway;
  current_state: PathwayState;
  criteria: EvaluatedCriterion[];  // critérios COM avaliação
  status: 'active' | 'completed' | 'archived';
  severity: 'normal' | 'watch' | 'urgent' | 'critical';
  enrolled_at: string;
}

interface EvaluatedCriterion extends PathwayCriteriaDef {
  met: boolean | null;
  value: string | null;
  severity: 'normal' | 'watch' | 'urgent' | 'critical' | null;
  evaluated_at: string | null;
}

// ── Progresso Detalhado ──

interface PathwayProgress {
  patient_pathway_id: number;
  mpi_id: string;
  pathway_name: string;
  current_state: PathwayState;
  criteria_summary: {
    total: number; met: number; not_met: number; pending: number;
  };
  criteria: EvaluatedCriterion[];
  state_history: StateTransition[];
  trend: 'improving' | 'stable' | 'worsening' | 'none';
  last_evaluated_at: string | null;
  recommendation: string | null;
}

interface StateTransition {
  from_state: string | null;
  to_state: string;
  changed_at: string;
  reason: string | null;
}
```

### 5.2 Sistema de Severidade (4 níveis — derivado do YAML)

| Severidade | Cor (dark theme) | Significado | Ação |
|-----------|-----------------|-------------|------|
| `normal` | `#2DD269` verde | Dentro do esperado | Nenhuma |
| `watch` | `#F2B90D` âmbar | Alteração relevante | < 2h |
| `urgent` | `#F96F06` laranja | Deterioração | < 30 min |
| `critical` | `#FF3B4A` vermelho | Risco iminente | < 5 min |

---

## 6. Estratégia de Construção (do zero)

### 6.1 Stack

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Framework | Next.js 15 (App Router) | SSR opcional, RSC, routing baseado em filesystem |
| Estilização | Tailwind CSS 4 + CSS custom properties | Utility-first + tokens de severidade como variáveis CSS |
| Componentes base | shadcn/ui | Headless, acessível, tree-shakeable |
| Visualização de dados | Recharts | Gráficos de scores e tendências |
| Syntax highlighting | react-syntax-highlighter | YAML viewer no catálogo |
| Ícones | Lucide React | Consistente, acessível, leve |
| State management | React Context + SWR | Cache de API com revalidação |

### 6.2 Construção limpa (sem dependência do v2)

O projeto é inicializado com `npx create-next-app@latest`. Nenhum arquivo do v2 é copiado. Tudo é construído a partir de:

1. **Especificações do backend:** schemas OpenAPI em `docs/contracts/pathways-openapi.yaml`
2. **Definições YAML:** `_work/alerts/pathways/sepse.yaml` (e demais)
3. **Jornada do usuário:** Seção 1 deste documento
4. **Princípios de UX:** Seção 0 deste documento

### 6.3 Fases de Implementação

| Fase | Dias | O que constrói | APIs |
|------|------|---------------|------|
| **M0 — Foundation** | 2 | Projeto Next.js, sistema de design (tokens CSS), API client, middleware auth, AppShell | `/auth/*` |
| **M1 — Dashboard** | 3 | BedGrid, BedCard, ScorePair, PathwayBadges, WebSocket, UnitFilter | `GET /dashboard` |
| **M2 — Patient Detail** | 3 | PatientHeader, VitalsPanel, ScoreTimeline, ActivePathways, AlertsPanel | `GET /patients/{id}/detail`, `GET /patients/{id}/pathways` |
| **M3 — Pathway View (Sepse)** | 4 | StateFlow, CriteriaList, RecommendationsPanel, TransitionHistory | `GET /patients/{id}/pathways/{pp_id}/progress` |
| **M4 — Alert Triage** | 3 | FilterBar, AlertTable, QuickActions, AlertTrace | `GET /alerts`, POST actions |
| **M5 — Pathway Catalog** | 2 | PathwayGrid, YamlViewer, PathwayTester | `GET /pathways` |
| **M6 — Admin** | 2 | UserManager, ThresholdEditor, TenantConfig, AuditLog | `/admin/*` |
| **M7 — 8 Trilhas Restantes** | 6 | Replicar M3 para renal, resp, ventilação, equilíbrio, nutrição, profilaxia, sedação, delirium | `GET .../progress` |
| **M8 — Integração** | 3 | Testes E2E, WCAG 2.1 AA, performance, responsividade, **substituição do v2** | — |

### 6.4 MVP: Trilha Sepse como Benchmark

A trilha de Sepse é o MVP porque:
- É a mais madura (v3.0.0, guideline SSC-2021 com recomendações explícitas)
- 7 critérios cobrindo todos os tipos de predicate (graded bands + boolean)
- 5 estados lineares — máquina de estados didática
- Tem suppression config, dedup, evidence

**M3 entrega componentes genéricos.** M7 é só configuração — sem novos componentes.

### 6.5 Cleanup do Frontend v2 (parte do M8)

Ao final do M8, com todas as métricas de sucesso atingidas e o gate G2 aprovado:

1. **Arquivar v2:** `frontend-v2/` → `frontend-v2-archive/` (mantido como referência histórica, não servido)
2. **Promover v3:** `frontend-v3/` → `frontend-v2/` (assume o lugar canônico no monorepo)
3. **Atualizar CI/CD:** apontar pipelines para o novo diretório
4. **Limpar branches:** remover branches de feature do v3 após merge (`fase-0-foundation` a `fase-8-integracao`)
5. **Deploy:** build de produção do novo frontend substitui o antigo

```bash
# Script de cleanup (executado APÓS G2 aprovado)
cd /Users/familia/intensicare
mv frontend-v2 frontend-v2-archive
mv frontend-v3 frontend-v2
git add -A
git commit -m "feat: substitui frontend-v2 pelo v3 (pathway-centric rebuild)

- 6 páginas core orientadas a trilhas clínicas
- 9 trilhas com componentes genéricos data-driven
- UX-first: jornada do intensivista como fator organizador
- Zero páginas standalone de domínio
- v2 arquivado em frontend-v2-archive/"
```

O diretório `frontend-v2-archive/` permanece no repositório para consulta, mas não é mais servido. Pode ser removido manualmente após 30 dias se nenhum rollback for necessário.

---

## 7. APIs e Contratos

### 7.1 Endpoints consumidos (todos definidos em OpenAPI)

| Endpoint | Schema de resposta | Usado em |
|----------|-------------------|----------|
| `GET /api/v1/dashboard` | `DashboardResponse` | M1 |
| `GET /api/v1/patients/{mpi_id}/detail` | `PatientDetailResponse` | M2 |
| `GET /api/v1/patients/{mpi_id}/pathways` | `{ items: PatientPathway[] }` | M2 |
| `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress` | `PathwayProgress` | M3, M7 |
| `GET /api/v1/pathways` | `{ items: Pathway[] }` | M5 |
| `GET /api/v1/pathways/{id}` | `Pathway` | M5 |
| `GET /api/v1/alerts` | `AlertListResponse` | M4 |
| `POST /api/v1/alerts/{id}/acknowledge` | `AlertInfo` | M4 |
| `POST /api/v1/alerts/{id}/escalate` | `AlertInfo` | M4 |
| `POST /api/v1/alerts/{id}/resolve` | `AlertInfo` | M4 |

**Contratos:** `docs/contracts/pathways-openapi.yaml` — 510 linhas, schemas completos.

### 7.2 Pré-requisitos do Backend

| Item | Ação |
|------|------|
| JWT claims (`is_admin`, `role`) | Adicionar ao token ou criar `GET /api/v1/me` |
| WebSocket CSP | `connect-src 'self' wss://` em prod, `ws://localhost:8000` em dev |
| Endpoint `GET /patients/{mpi_id}/pathways` | **Validar antes do M2** — é o endpoint mais crítico |
| Endpoints 500 (stability, ventilation) | Corrigir antes do M7 |

---

## 8. Métricas de Sucesso

- [ ] Dashboard carrega em < 2s com 20+ pacientes
- [ ] **Jornada completa:** Dashboard → Patient → Pathway → Ação em ≤ 2 cliques
- [ ] **Todas as trilhas de um paciente visíveis em UMA tela** (Patient Detail)
- [ ] Zero páginas standalone de domínio clínico
- [ ] Zero endpoints 500 nas trilhas core
- [ ] 100% dos alertas rastreáveis (AlertTrace)
- [ ] WebSocket funcional com fallback para polling
- [ ] WCAG 2.1 AA (contraste, teclado, leitores de tela)
- [ ] Responsivo: tablet (plantão noturno) e desktop (round)

---

## 9. Riscos

| Risco | P×I | Mitigação |
|-------|-----|-----------|
| `GET /patients/{mpi_id}/pathways` não implementado | M×A | Validar antes do M2. Se ausente, priorizar no backend. |
| StateFlow visual complexo | A×M | v1: lista horizontal de pills. v2: diagrama de transições. |
| Performance com 20+ pacientes no Dashboard | M×M | Server-side data fetching (RSC). Cliente só hidrata. |
| WebSocket bloqueado por firewall hospitalar | M×A | Fallback automático para polling 30s. |
| Tempo de construção (28 dias) | M×M | M1, M2, M4, M5, M6 são paralelizáveis (só dependem de M0). |

---

*Documento gerado por Niemeyer (System Architect) v2.0 — UX-First, Zero Reaproveitamento.*
