# PLANS.md — Sprint 3-4 (Domínios Parciais)

> **Orquestrador:** Ive (Product Design Orchestrator)
> **Data:** 2026-07-07
> **RECON:** Completo ✅

## RECON Summary

| Artefato | Status | Notas |
|----------|--------|-------|
| Componentes Sprint 1-2 | 10 componentes com stories ✅ | CriteriaChecklist, BundleCard, ClinicalTimeline, StewardshipScoreBadge, AlertCard, SeverityBadge, ClinicalTooltip, Layout, DrawerBuilder, ErrorBoundary |
| Tokens existentes | 3 domínios ✅ | sepsis(5), antimicrobial(3), prophylaxis(4) — cada com 7 sub-tokens |
| API client | 8 endpoints ✅ | auth, dashboard, patient, alerts, admin/users, thresholds, stats, health |
| Backend domain_fluid_balance | 425 linhas ✅ | Nursing day, I/O aggregation, 2h buckets |
| Backend domain_comunicacao | 262 linhas ✅ | Reaction aggregation, observations |
| Backend domain_tenancy | 423 linhas ✅ | Estabelecimento/setor indicators |
| Backend AuditTrail | Model SQLAlchemy ✅ | TimescaleDB hypertable |
| Backend Nutrition | ❌ Nenhum | Mock data + zod schema |
| Antimicrobial contract | 164 linhas ✅ | 3 endpoints: assessments GET/POST, criteria GET |
| Prophylaxis contract | 165 linhas ✅ | 4 endpoints: bundles GET, bundle GET/PUT, criteria GET |
| Antimicrobial page | Mock data ⚠️ | lib/antimicrobial-types.ts com MOCK_PATIENTS |
| Prophylaxis page | Mock data ⚠️ | lib/prophylaxis-types.ts com PROPHYLAXIS_BUNDLES |

---

## Milestones (8 fases)

### FASE 0 — Token Expansion (PRÉ-REQUISITO)
**Agente:** Token Manager (design-token-management-loop)
**Arquivos:** `app/tokens-generated.css`, `design-tokens/`
**Tokens novos:**
- `--clinical-nutrition-*` (3 variants: optimal, at-risk, critical)
- `--clinical-fluid-balance-*` (3 variants: positive, negative, neutral)
- `--clinical-communication-*` (2 variants: unread, read)
- `--admin-tenancy-*` (3 variants: organization, establishment, sector)

**Gate:** `npm run build-tokens` passa

### FASE 1 — Nutricao (`/nutrition`) [L0]
**Agente:** FE Implementer (design-to-code-agent-loop)
**Backend:** ❌ (mock)
**Arquivos:** 3 novos
1. `lib/nutrition-types.ts` — tipos + mock data + zod schema
2. `components/NutritionalAssessmentForm.tsx` — formulário (altura, peso, IMC, metas)
3. `app/nutrition/page.tsx` — página com Layout + states
**Reusar:** CriteriaChecklist, Layout, ErrorBoundary
**Tokens:** `--clinical-nutrition-*` (da Fase 0)
**Estados:** empty, partial, complete, loading, error

### FASE 2 — Fluid Balance (`/fluid-balance`) [L1]
**Agente:** FE Implementer (design-to-code-agent-loop)
**Backend:** `domain_fluid_balance.py` ✅
**Arquivos:** 3 novos
1. `lib/fluid-balance-types.ts` — tipos + API types
2. `components/FluidBalanceChart.tsx` — Recharts I/O acumulado
3. `app/fluid-balance/page.tsx` — dashboard com Summary + Chart
**API:** `lib/api.ts` — `fetchFluidBalance(mpiId)`, `fetchFluidBalanceTrend(mpiId, days)`
**Reusar:** Layout, ErrorBoundary, ClinicalTimeline
**Tokens:** `--clinical-fluid-balance-*`
**Estados:** 24h view, 7d trend, loading, empty, error

### FASE 3 — Comunicacao (`/communication`) [L1]
**Agente:** FE Implementer (design-to-code-agent-loop)
**Backend:** `domain_comunicacao.py` ✅
**Arquivos:** 3 novos
1. `lib/communication-types.ts` — tipos + API types
2. `components/HandoffMessageCard.tsx` — card de mensagem SBAR
3. `app/communication/page.tsx` — lista + formulário de handoff
**API:** `lib/api.ts` — `fetchHandoffMessages()`, `createHandoffMessage()`, `addReaction()`
**Reusar:** Layout, ErrorBoundary, DrawerBuilder
**Tokens:** `--clinical-communication-*`
**Estados:** message list, new message, loading, empty, error

### FASE 4 — Tenancy (`/admin/tenancy`) [L1]
**Agente:** FE Implementer (design-to-code-agent-loop)
**Backend:** `domain_tenancy.py` ✅
**Arquivos:** 2 novos
1. `lib/tenancy-types.ts` — tipos + API types
2. `app/admin/tenancy/page.tsx` — hierarchy tree + config
**API:** `lib/api.ts` — `fetchOrganizations()`, `fetchEstablishments()`, `fetchSectors()`
**Reusar:** Layout, ErrorBoundary, DrawerBuilder
**Tokens:** `--admin-tenancy-*`
**Estados:** tree view, edit mode, loading, empty, error

### FASE 5 — Auditoria (`/admin/audit-log`) [L1]
**Agente:** FE Implementer (design-to-code-agent-loop)
**Backend:** Model `AuditTrail` ✅
**Arquivos:** 2 novos
1. `lib/audit-types.ts` — tipos + API types
2. `app/admin/audit-log/page.tsx` — TanStack Table + filtros
**API:** `lib/api.ts` — `fetchAuditLogs(filter)`, `fetchAuditLogDetail(id)`
**Reusar:** Layout, ErrorBoundary, DrawerBuilder
**Tokens:** usar existentes (semantic-surface, semantic-text, feedback-*)
**Estados:** filtered list, detail drawer, loading, empty, error

### FASE 6 — Mock → API Swap [L2]
**Agente:** FE Implementer (design-to-code-agent-loop)
**Pré-requisito:** parreira entrega endpoints
**Arquivos afetados:**
1. `lib/api.ts` — `fetchAntimicrobialAssessments()`, `createAntimicrobialAssessment()`, `fetchProphylaxisBundles()`, `updateProphylaxisBundle()`
2. `lib/antimicrobial-types.ts` — remover MOCK_PATIENTS, manter DEFAULT_CRITERIA e helpers
3. `lib/prophylaxis-types.ts` — remover PROPHYLAXIS_BUNDLES mock, manter helpers
4. `app/antimicrobial-stewardship/page.tsx` — buscar dados da API
5. `app/prophylaxis-bundles/page.tsx` — buscar dados da API
**Contratos:** `docs/contracts/antimicrobial-openapi.yaml`, `docs/contracts/prophylaxis-openapi.yaml`

### FASE 7 — Gatekeeping & Stories [L2]
**Agentes (3 em paralelo):**
- **A11y Reviewer** — axe-core scan em todas as 5 novas páginas + 2 alteradas
- **UX Reviewer** — revisão heurística de fluxos, estados, affordance
- **Storybook Keeper** — stories para todos os novos componentes + 7 state variants

### FASE 8 — Cross-Validation & Build
- `npx tsc --noEmit` — type check
- `npm run build` — production build
- `npm run build-tokens` — token validation
- HANDOFF.yaml atualizado

---

## Paralelização

```
FASE 0 (Tokens) ──┬── FASE 1 (Nutricao)
                  ├── FASE 2 (Fluid Balance)    }── TODAS em paralelo
                  ├── FASE 3 (Comunicacao)       }   (sem dependências
                  ├── FASE 4 (Tenancy)           }    entre si)
                  └── FASE 5 (Audit)
                           │
                    FASE 6 (Mock→API) [aguarda parreira]
                           │
                    FASE 7 (Gatekeeping)
                           │
                    FASE 8 (Cross-Validation)
```

## Dependências

| Milestone | Depende de | Bloqueia |
|-----------|-----------|----------|
| FASE 0 | nada | todas as fases 1-5 |
| FASE 1-5 | FASE 0 | nada (independentes) |
| FASE 6 | parreira entregar endpoints | nada |
| FASE 7 | FASE 1-6 completas | FASE 8 |
| FASE 8 | FASE 7 completa | conclusão |

## Rollback Plan

| Milestone | Rollback |
|-----------|----------|
| FASE 0 | `git checkout HEAD -- app/tokens-generated.css` |
| FASE 1-5 | `git checkout HEAD -- app/{nutrition,fluid-balance,communication,admin/tenancy,admin/audit-log}/ lib/{nutrition,fluid-balance,communication,tenancy,audit}-types.ts components/{NutritionalAssessmentForm,FluidBalanceChart,HandoffMessageCard}.tsx` |
| FASE 6 | `git checkout HEAD -- lib/api.ts lib/antimicrobial-types.ts lib/prophylaxis-types.ts app/antimicrobial-stewardship/ app/prophylaxis-bundles/` |

## Estimativa

| Fase | Tamanho | Arquivos | Agentes |
|------|---------|----------|---------|
| FASE 0 | S | 1-2 | 1 |
| FASE 1-5 | M (cada) | 2-3 por fase | 1 por fase (5 em paralelo) |
| FASE 6 | M | 5 | 1 |
| FASE 7 | M | 3 reviews | 3 em paralelo |
| **Total** | **XL** | ~20 arquivos | máx 5 concorrentes |
