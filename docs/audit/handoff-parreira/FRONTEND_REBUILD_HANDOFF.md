# HANDOFF — Refatoração Arquitetural do Frontend IntensiCare v2

**De:** Parreira (DevOps Orchestrator)  
**Para:** Niemeyer (System Architect)  
**Data:** 2026-07-09  
**Assunto:** Plano de reconstrução do frontend orientado a trilhas clínicas  

---

## 1. Problema Encontrado

### 1.1 Diagnóstico

O frontend atual (`frontend-v2`) tem **33 páginas**, mas foi construído com o modelo mental errado:

```
MODELO ATUAL (ERRADO):  1 domínio clínico = 1 página independente

  /ventilation        Página isolada de ventilação
  /sedation           Página isolada de sedação
  /nutrition          Página isolada de nutrição
  /stability          Página isolada de estabilidade
  /fluid-balance      Página isolada de balanço hídrico
  /prophylaxis-bundles Página isolada de profilaxia
  /antimicrobial-stewardship Página isolada de antimicrobiano
  /clinical-deterioration    Página isolada de piora clínica
  ... (17 páginas neste padrão)
```

Cada página busca seus próprios dados, renderiza seus próprios componentes, e **não se comunica com as outras**. O intensivista precisa navegar entre 17 páginas diferentes para entender o estado de um único paciente — o oposto de um "centro de comando clínico".

### 1.2 Causa raiz

O frontend ignorou a arquitetura do backend. O backend é organizado em torno de **trilhas clínicas (care pathways)** — fluxos estruturados que avaliam critérios, calculam scores, cruzam thresholds e geram alertas. O frontend tratou cada trilha como se fosse um aplicativo independente.

### 1.3 Evidência

| Indicador | Valor |
|-----------|-------|
| Páginas totais no frontend | 33 |
| Páginas que servem à missão | ~8 (24%) |
| Páginas que são domínios desconexos | 17 (52%) |
| Páginas admin/sistema | 8 (24%) |
| Endpoints que retornam 500 | 3+ (stability, ventilation) |
| Endpoints que retornam 404 | 5+ (handoff, shifts, ventilation/history) |
| Endpoints que retornam 422 | 1+ (prophylaxis/bundles) |

---

## 2. O Que Está Certo (Backend)

O backend **não precisa ser refeito**. Ele tem a arquitetura correta e deve servir como **spec canônica** para o novo frontend:

### 2.1 Motor de Trilhas (`trilhas_engine.py`)

```
Pipeline: YAML definitions → Compiler → Predicate AST → Evaluator → Alert instances
```

- **Stateless**: cada avaliação é independente
- **Declarativo**: trilhas definidas em YAML, não em código
- **Rastreável**: cada alerta gerado referencia o critério, threshold e versão da definição

### 2.2 Nove Trilhas Clínicas (`_work/alerts/pathways/`)

| # | Trilha | Arquivo | Descrição |
|---|--------|---------|-----------|
| 1 | Sepse | `sepse.yaml` | Identificação precoce, lactato, PAM, antibiótico |
| 2 | Renal | `renal.yaml` | AKI, KDIGO, débito urinário, creatinina |
| 3 | Respiratório | `respiratorio.yaml` | Insuficiência respiratória, SpO₂/FiO₂ |
| 4 | Ventilação | `ventilacao.yaml` | Parâmetros de VM, desmame, extubação |
| 5 | Equilíbrio | `equilibrio.yaml` | Na⁺, K⁺, Ca²⁺, Mg²⁺, ácido-base |
| 6 | Nutrição | `nutricao.yaml` | TNE, ingestão calórica, proteica |
| 7 | Profilaxia | `profilaxia.yaml` | TEV, úlcera de estresse, cabeceira |
| 8 | Sedação | `sedacao.yaml` | RASS, sedoanalgesia, delirium |
| 9 | Delirium | `delirium.yaml` | CAM-ICU, rastreio, manejo |

### 2.3 Serviços de Domínio (54 serviços)

Cada domínio clínico tem um serviço que **alimenta** as trilhas:
- `domain_sepsis.py`, `domain_aki.py`, `domain_respiratory.py`, `domain_ventilacao.py`, `domain_electrolyte.py`, `domain_fluid_balance.py`, `domain_profilaxia.py`, `domain_sedacao.py`, `domain_pharmaco_delirium.py`

### 2.4 Motor de Alertas (`alert_engine.py`)

- Scores clínicos (MEWS, NEWS2, SOFA, qSOFA) → thresholds configuráveis → alertas com severidade
- Rate limiting via Redis
- Rastreabilidade completa (score → threshold → alert)

---

## 3. Arquitetura-Alvo do Frontend

### 3.1 Princípio organizador

> **A trilha (pathway) é a unidade organizadora central.** Toda informação clínica é apresentada no contexto da trilha que a gerou.

### 3.2 Modelo de navegação

```
┌─────────────────────────────────────────────────────────┐
│  DASHBOARD (todos os pacientes)                         │
│  Grid de leitos com scores, alertas, status das trilhas │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ Leito 1 │ │ Leito 2 │ │ Leito 3 │ │ Leito 4 │      │
│  │ MEWS 4  │ │ MEWS 2  │ │ MEWS 6  │ │ MEWS 1  │      │
│  │ ⚠️ 2    │ │ ✅ 0    │ │ 🔴 3    │ │ ✅ 0    │      │
│  └────┬────┘ └─────────┘ └────┬────┘ └─────────┘      │
│       │                       │                         │
│       ▼                       ▼                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │         PATIENT DETAIL (1 paciente)              │    │
│  │  ┌──────────────────────────────────────────┐   │    │
│  │  │  TRILHAS ATIVAS                          │   │    │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐       │   │    │
│  │  │  │ Sepse  │ │ Renal  │ │ Resp.  │ ...   │   │    │
│  │  │  │ ⚠️     │ │ ✅     │ │ 🔴     │       │   │    │
│  │  │  └───┬────┘ └────────┘ └────────┘       │   │    │
│  │  │      │                                     │   │    │
│  │  │      ▼                                     │   │    │
│  │  │  ┌────────────────────────────────────┐   │   │    │
│  │  │  │  TRILHA DETAIL (1 pathway)         │   │   │    │
│  │  │  │  • Estado atual da trilha          │   │   │    │
│  │  │  │  • Critérios (✅ met / ⏳ pend / ❌)│   │   │    │
│  │  │  │  • Scores e tendências             │   │   │    │
│  │  │  │  • Alertas desta trilha            │   │   │    │
│  │  │  │  • Recomendações clínicas          │   │   │    │
│  │  │  └────────────────────────────────────┘   │   │    │
│  │  └──────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  ALERT TRIAGE (todos os alertas)                │    │
│  │  Filtrar por severidade, unidade, tipo          │    │
│  │  └── Alert Detail → Patient → Trilha            │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  CARE PATHWAYS (definições das trilhas)          │    │
│  │  Visualizar/editar YAML, testar contra pacientes │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Páginas do novo frontend (6 páginas core)

| # | Página | Rota | Descrição |
|---|--------|------|-----------|
| 1 | **Dashboard** | `/` | Grid de leitos, scores ao vivo, alertas ativos, filtro por unidade |
| 2 | **Patient Detail** | `/patient/[mpi_id]` | Visão completa: scores, trilhas ativas, alertas, vitais, evoluções |
| 3 | **Pathway View** | `/patient/[mpi_id]/pathway/[pathway_id]` | Uma trilha específica: estados, critérios, recomendações |
| 4 | **Alert Triage** | `/alerts` | Lista de todos os alertas com filtros, acknowledge/escalate/resolve |
| 5 | **Care Pathways** | `/pathways` | Catálogo das trilhas, definições YAML, teste contra paciente |
| 6 | **Admin** | `/admin` | Usuários, thresholds, tenancy, registro |

### 3.4 O que NÃO existirá mais

As 17 páginas de domínio standalone serão **abolidas**. Seus componentes serão **reaproveitados** como seções dentro do Pathway View:

| Página abolida | Vira componente em |
|---------------|-------------------|
| `/ventilation` | `PathwayView` (trilha ventilação) |
| `/sedation` | `PathwayView` (trilha sedação) |
| `/nutrition` | `PathwayView` (trilha nutrição) |
| `/stability` | `PatientDetail` (indicador calculado) |
| `/fluid-balance` | `PathwayView` (trilha equilíbrio) |
| `/prophylaxis-bundles` | `PathwayView` (trilha profilaxia) |
| `/antimicrobial-stewardship` | `PathwayView` (trilha sepse) |
| `/clinical-deterioration` | `PatientDetail` (indicador calculado) |
| `/clinical-forms` | `PatientDetail` (modal/form) |
| `/clinical-notes` | `PatientDetail` (seção) |
| `/communication` | Feature no `PatientDetail` |
| `/documentation` | `PatientDetail` (seção) |
| `/prescription` | `PatientDetail` (seção) |
| `/patient-movement` | `CommandCenter` (modal) |
| `/efficiency` | `Admin` |
| `/handoff` | Feature no `PatientDetail` |
| `/sepse-dashboard` | `PathwayView` (trilha sepse) |

---

## 4. Estratégia de Implementação (Draft)

### 4.1 FASE 0 — Foundation (1-2 dias)

- [ ] Novo projeto Next.js 15 com App Router
- [ ] Stack de UI: Tailwind CSS + shadcn/ui + Recharts
- [ ] Design tokens (já existem em `design-tokens/`)
- [ ] Middleware de auth (aproveitar `middleware.ts` atual)
- [ ] Lib de API (`lib/api.ts`) — aproveitar e expandir
- [ ] Tipos TypeScript alinhados com schemas do backend (Pydantic → TypeScript)

### 4.2 FASE 1 — Dashboard (2-3 dias)

- [ ] Componente `BedGrid`: grid de leitos com scores, alertas, status de trilhas
- [ ] Componente `PatientCard`: card resumido com MEWS/NEWS2/SOFA, alertas ativos, trilhas
- [ ] Filtro por unidade (UTI-ADULTO, UTI-CORONARIANA, etc.)
- [ ] WebSocket para atualização em tempo real (corrigir CSP!)
- [ ] API: `GET /api/v1/dashboard`

### 4.3 FASE 2 — Patient Detail (3-4 dias)

- [ ] Componente `PatientHeader`: identificação, leito, unidade, scores em tempo real
- [ ] Componente `ActivePathways`: cards das trilhas ativas com status e alertas
- [ ] Componente `VitalsChart`: gráfico de sinais vitais (aproveitar Recharts)
- [ ] Componente `ScoreTimeline`: timeline de MEWS/NEWS2/SOFA
- [ ] Componente `AlertsList`: alertas deste paciente
- [ ] Componente `EvolucoesList`: evoluções clínicas
- [ ] API: `GET /api/v1/patients/{mpi_id}/detail`, `GET /api/v1/patients/{mpi_id}/pathways`

### 4.4 FASE 3 — Pathway View (3-4 dias)

- [ ] Componente `PathwayStateMachine`: visualização do estado atual e transições
- [ ] Componente `CriteriaPanel`: lista de critérios com status (met/pending/violated)
- [ ] Componente `CriteriaDetail`: evidência e valores que geraram violação
- [ ] Componente `PathwayRecommendations`: recomendações baseadas no estado atual
- [ ] Componente `PathwayHistory`: histórico de transições de estado
- [ ] API: `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress`

### 4.5 FASE 4 — Alert Triage (2-3 dias)

- [ ] Componente `AlertTable`: tabela filtrável com severidade, paciente, trilha, data
- [ ] Ações: acknowledge, escalate, resolve (já existem no backend)
- [ ] Componente `AlertTrace`: rastreabilidade (score → threshold → alert)
- [ ] API: `GET /api/v1/alerts`, `POST .../acknowledge`, `POST .../escalate`, `POST .../resolve`

### 4.6 FASE 5 — Care Pathways Catalog (2 dias)

- [ ] Componente `PathwayCatalog`: lista de trilhas com status, versão, hash
- [ ] Componente `PathwayDefinition`: visualização da definição YAML formatada
- [ ] Componente `PathwayTest`: testar trilha contra dados de paciente
- [ ] API: `GET /api/v1/pathways`, `GET /api/v1/pathways/{id}`

### 4.7 FASE 6 — Admin (2 dias)

- [ ] Gestão de usuários
- [ ] Configuração de thresholds
- [ ] Tenancy (empresas, estabelecimentos)
- [ ] API: existente (`/admin/*`, `/api/v1/thresholds/*`, `/api/v1/registry/*`)

---

## 5. Migração do Frontend Atual

### 5.1 O que APROVEITAR (não jogar fora)

| Artefato | Localização | Reuso |
|----------|------------|-------|
| Design tokens | `design-tokens/` | ✅ Integral — 24 arquivos, build pipeline funcional |
| `lib/api.ts` | `lib/api.ts` | ✅ Expandir — 1029 linhas de tipos e funções |
| `lib/auth.ts` | `lib/auth.ts` | ✅ Integral |
| `middleware.ts` | `middleware.ts` | ✅ Integral (já validado) |
| `components/SeverityBadge` | `components/` | ✅ Reaproveitar |
| `components/ClinicalTooltip` | `components/` | ✅ Reaproveitar |
| `components/Layout` | `components/Layout.tsx` | 🔄 Refatorar sidebar |
| `lib/clinical-severity` | `lib/` | ✅ Integral |
| `lib/websocket` | `lib/` | 🔄 Corrigir CSP + JWT |
| `hooks/useRole` | `hooks/` | ✅ Integral |

### 5.2 O que DESCARTAR

- Todas as 17 páginas de domínio standalone (seus componentes internos podem ser extraídos e reaproveitados)
- O modelo de sidebar atual (18 itens planos → substituir por agrupamento hierárquico)

### 5.3 Estratégia de branch

```
main (atual)
  └── feature/frontend-v3 (novo projeto)
       ├── FASE 0: foundation
       ├── FASE 1: dashboard
       ├── FASE 2: patient-detail
       ├── FASE 3: pathway-view
       ├── FASE 4: alert-triage
       ├── FASE 5: pathway-catalog
       └── FASE 6: admin
```

Manter `frontend-v2` como referência durante a construção. Ao final, substituir.

---

## 6. Riscos e Dependências

| Risco | Mitigação |
|-------|-----------|
| Endpoints do backend com bugs (500, 404, 422) | Corrigir durante FASE 0 como pré-requisito |
| JWT sem claims de `is_admin` e `role` | Corrigir no backend (adicionar claims) ou criar endpoint `/api/v1/me` |
| WebSocket bloqueado por CSP | Adicionar `ws://localhost:8000` ao CSP header OU mudar para wss:// |
| Perda de funcionalidade durante migração | Construir em paralelo, não modificar `frontend-v2` |
| Complexidade do Pathway View | Começar com a trilha de sepse (mais madura) como MVP |

---

## 7. Métricas de Sucesso

- [ ] Dashboard carrega em <2s com 20+ pacientes
- [ ] Navegação Dashboard → Patient → Pathway em ≤2 cliques
- [ ] Intensivista consegue ver todas as trilhas de um paciente em uma única tela
- [ ] Zero páginas standalone de domínio clínico
- [ ] Zero endpoints 500 nas trilhas core (sepse, renal, respiratório)
- [ ] Alertas são rastreáveis até o critério e threshold que os gerou
- [ ] WebSocket funcional com atualização em tempo real

---

*Documento preparado para refinamento por Niemeyer (System Architect).*  
*Próximo passo: Niemeyer transforma este draft em plano completo com milestones, responsáveis, e estimativas.*
