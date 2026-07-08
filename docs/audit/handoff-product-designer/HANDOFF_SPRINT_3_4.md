# HANDOFF.md — Product-Design-Orchestrator (Sprint 3-4)

> **De:** Niemeyer (System Architect) → **Para:** product-design-orchestrator
> **Data:** 2026-07-07
> **Projeto:** IntensiCare v2 — Sprint 3-4 (Domínios Parciais)
> **Risk Level:** L2 (frontend-v2/ only)
> **Pré-requisito:** Sprint 1-2 concluído ✅

---

## Envelope de Missão

### Goal
Projetar e implementar as UIs para **5 domínios com backend parcial**, expandindo componentes base do Sprint 1-2 e cobrindo gaps de UX identificados. Adicionalmente: **swappar mock data por APIs reais** nos 2 domínios do Sprint 1-2 assim que parreira entregar os endpoints.

### Context
O Sprint 1-2 entregou 3 domínios (Sepse ✅, Antimicrobiano ⚠️ mock, Profilaxia ⚠️ mock). O Sprint 3-4 avança para 5 domínios onde o backend JÁ EXISTE parcialmente mas não tem frontend:

| Domínio | Regras | Backend | Gap de UI |
|---------|--------|---------|-----------|
| **Nutricao** | 11 | ❌ Nenhum | NOVO — formulário de avaliação nutricional + IMC + metas |
| **Equilibrio** | 4 | `domain_fluid_balance.py` (parcial) | EXPANDIR — dashboard de balanço hídrico com pathway Equilibrio |
| **Comunicacao** | 47 | `domain_comunicacao.py` ✅ | NOVO — handoff messages, comunicação entre turnos |
| **Tenancy** | 53 | `domain_tenancy.py` ✅ | NOVO — gestão de organizações/estabelecimentos/setores |
| **Auditoria** | 37 | Modelo `AuditTrail` ✅ | NOVO — log viewer com filtros e export |

O backend para estes domínios já tem services implementados — o trabalho é majoritariamente **UI + integrar com APIs existentes**.

### Constraints (mesmas do Sprint 1-2)
- Stack: Next.js 15, React 19, TypeScript strict, Tailwind 4, Storybook 8, Lucide Icons
- Design tokens: sistema existente em `tokens-generated.css` — estender, nunca substituir
- Componentes base do Sprint 1-2: CriteriaChecklist, ClinicalTimeline, BundleCard, StewardshipScoreBadge — REUTILIZAR
- Componentes originais: AlertCard, SeverityBadge, ClinicalTooltip, Layout, DrawerBuilder, ErrorBoundary — REUTILIZAR
- API client: `lib/api.ts` com `request<T>()` — NUNCA fetch direto
- WebSocket: `lib/websocket.ts` com `useRealtimeChannel()`
- WCAG AA obrigatório

### Done When
- [ ] 5 novas páginas implementadas e integradas com APIs reais (ou mock → real quando pronto)
- [ ] Componentes reutilizáveis novos (máx 3) com stories
- [ ] Design tokens novos registrados
- [ ] Antimicrobiano e Profilaxia migrados de mock → API real (assim que parreira entregar)
- [ ] A11y re-scan: ≥95% em todos os componentes
- [ ] `npx tsc --noEmit` + `npm run build` passam
- [ ] `HANDOFF.yaml` atualizado

### Scope Boundary
- ✅ DENTRO: `frontend-v2/app/{nutrition,fluid-balance,communication,tenancy,audit-log}/`, novos componentes, tokens
- ✅ DENTRO: Swappar `lib/antimicrobial-types.ts` mock → `lib/api.ts` real, idem profilaxia
- ❌ FORA: `src/intensicare/`, contratos OpenAPI

---

## Domínios (Ordem de Prioridade)

### 1. Nutricao (`/nutrition`)
- **11 regras** do legado
- **Novo design:** formulário de avaliação nutricional
- **Componentes:** NutritionalAssessmentForm (altura, peso, IMC calculado, metas calóricas/proteicas)
- **Estados:** empty, partial, complete, loading, error
- **Tokens:** `--clinical-nutrition-*`

### 2. Equilibrio / Fluid Balance (`/fluid-balance`)
- **4 regras** do legado (pathway Equilibrio) + 64 regras balanco-hidrico
- **Expandir:** domain_fluid_balance.py já existe
- **Novo design:** dashboard de balanço hídrico com gráfico I/O acumulado
- **Componentes:** FluidBalanceChart (Recharts), FluidBalanceSummary (entradas/saídas/balanço)
- **Estados:** 24h view, 7d trend, loading, empty, error
- **Tokens:** `--clinical-fluid-balance-*`

### 3. Comunicacao (`/communication`)
- **47 regras** do legado
- **Novo design:** handoff messages entre turnos, comunicação estruturada (SBAR)
- **Componentes:** HandoffMessageCard, ShiftHandoffForm (template SBAR)
- **Estados:** message list, new message, loading, empty, error
- **Tokens:** `--clinical-communication-*`

### 4. Tenancy (`/admin/tenancy`)
- **53 regras** do legado
- **Novo design:** gestão de organizações (empresa → estabelecimento → setor)
- **Componentes:** OrgHierarchyTree, TenancyConfigForm
- **Estados:** tree view, edit mode, loading, empty, error
- **Tokens:** `--admin-tenancy-*`

### 5. Auditoria (`/admin/audit-log`)
- **37 regras** do legado
- **Novo design:** visualizador de logs de auditoria com filtros
- **Componentes:** AuditLogTable (TanStack Table), AuditLogFilters
- **Estados:** filtered list, detail drawer, loading, empty, error
- **Tokens:** usar existentes (não precisa de tokens específicos)

---

## Tarefa Extra: Swap Mock → API Real

Assim que parreira entregar os endpoints de Antimicrobiano e Profilaxia:
1. Substituir `MOCK_ASSESSMENTS` em `lib/antimicrobial-types.ts` por chamadas a `lib/api.ts`
2. Substituir `PROPHYLAXIS_BUNDLES` em `lib/prophylaxis-types.ts` por chamadas a `lib/api.ts`
3. Adicionar funções no `lib/api.ts`: `fetchAntimicrobialAssessments()`, `createAntimicrobialAssessment()`, `fetchProphylaxisBundles()`, `updateProphylaxisBundle()`
4. Atualizar páginas para usar dados reais com loading/error states
5. Contratos: `docs/contracts/antimicrobial-openapi.yaml`, `docs/contracts/prophylaxis-openapi.yaml`

---

## Regras de Ouro (Agentic-Loop)

1. **RECON primeiro.** Revisar o que o Sprint 1-2 produziu — componentes, tokens, padrões.
2. **PLANS.md antes de codar.** Milestones ≤3 arquivos. 5 páginas = 5 milestones independentes (paralelizáveis).
3. **Reutilizar componentes.** CriteriaChecklist, BundleCard, ClinicalTimeline do Sprint 1-2. Não recriar.
4. **Delegate com skills.** Pré-carregar `design-to-code-agent-loop`, `ux-review-agent-loop`, `accessibility-review-agent-loop`.
5. **Gatekeeper ≠ implementador.** Revisores independentes por milestone.
6. **Estado no HANDOFF.yaml.** Não criar MDs temporários.
7. **Swappar mocks assim que APIs reais disponíveis.** Prioridade: Antimicrobiano → Profilaxia → Novos domínios.

## Anti-Patterns
- ❌ Recriar CriteriaChecklist para Nutricao (já existe — reutilizar)
- ❌ Criar tokens fora do sistema
- ❌ fetch() direto — usar `lib/api.ts`
- ❌ Componente sem story
- ❌ >3 arquivos por agente
