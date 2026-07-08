# HANDOFF.md — Product-Design-Orchestrator

> **De:** Niemeyer (System Architect) → **Para:** product-design-orchestrator
> **Data:** 2026-07-07
> **Projeto:** IntensiCare v2 — Sprint 1-2 Quick Wins (Design de UI)
> **Baseline:** `docs/audit/BACKEND_FRONTEND_GAP_MAP.md`
> **Risk Level:** L2 (design/código frontend — não afeta backend em produção)

---

## Envelope de Missão

### Goal
Projetar e implementar as interfaces de usuário para **3 domínios clínicos prioritários** (Quick Wins do gap audit), seguindo o pipeline Figma → Design Tokens → Componentes → Storybook → Páginas Next.js, com contratos de API definidos e validação WCAG AA.

### Context
O gap audit (`docs/audit/BACKEND_FRONTEND_GAP_MAP.md`) revelou que:
- **Sepse** (101 regras): backend completo (`domain_sepsis.py` + 5 endpoints REST), mas frontend só tem lista genérica de alertas — falta dashboard dedicado com visualização de critérios maiores/menores e timeline de confirmação
- **Antimicrobiano** (3 regras): ZERO backend, ZERO frontend — precisa de design completo (stewardship, catálogo de 12 critérios, scoring VERMELHO/AMARELO/NEUTRO)
- **Profilaxia** (8 regras): ZERO backend, ZERO frontend — bundles de prevenção (LAMGD, TEV, hiperglicemia, mobilização, dispositivos invasivos)

Backend expõe APIs genéricas (`/api/v1/alerts`, `/api/v1/dashboard`, `/api/v1/patients/{id}/detail`) que já cobrem parcialmente sepse. Antimicrobiano e profilaxia precisarão de novos endpoints — os contratos OpenAPI serão fornecidos por Niemeyer.

### Constraints
1. **Stack:** Next.js 15+ (App Router), React 19, TypeScript strict, Tailwind CSS 4, Storybook 8, Lucide Icons
2. **Design tokens:** Sistema existente em `app/tokens-generated.css` + `app/globals.css` — NUNCA criar tokens fora do sistema; usar `design-token-management-loop`
3. **Componentes existentes:** `AlertCard`, `SeverityBadge`, `ClinicalTooltip`, `Layout`, `DrawerBuilder`, `ErrorBoundary` — reutilizar sempre que possível
4. **WCAG AA:** Obrigatório para todos os componentes clínicos (ANVISA)
5. **Form engine:** `lib/form-engine/` já provê renderização de formulários — usar para clinical forms
6. **API client:** `lib/api.ts` com `request<T>()` wrapper (JWT, error handling) — NUNCA usar fetch direto
7. **WebSocket:** `lib/websocket.ts` com `useRealtimeChannel()` — usar para updates em tempo real
8. **Severity model:** `lib/clinical-severity.ts` com `getSeverityStyle()`, `getMEWSSeverity()`, `getSeverityFromAlert()`
9. **Storybook:** Todo componente novo DEVE ter `.stories.tsx`
10. **NÃO modificar** `src/intensicare/` (backend) — escopo é apenas `frontend-v2/`

### Done When
- [ ] Sepse Dashboard com timeline de confirmação, visualização de critérios maiores/menores, e integração com API de alertas existente — publicado no Storybook
- [ ] Antimicrobiano Stewardship UI com catálogo de 12 critérios, scoring, e mock de API (contrato OpenAPI definido por Niemeyer em paralelo)
- [ ] Profilaxia Bundles UI com checklists interativos para 5 bundles, scoring — publicado no Storybook
- [ ] Todos os componentes passam `npx tsc --noEmit` sem erros
- [ ] `npm run build` passa sem erros
- [ ] Design tokens novos registrados e versionados via `design-token-management-loop`
- [ ] Accessibility review via `accessibility-review-agent-loop` — score WCAG AA ≥ 95%
- [ ] Visual regression tests via `visual-regression-agent-loop` — zero regressões nos componentes existentes
- [ ] `HANDOFF.yaml` atualizado com status de cada domínio
- [ ] `docs/audit/handoff-product-designer/COMPLETION_REPORT.md` com evidência de cada milestone

### Risk Level
**L2** — Modifica apenas `frontend-v2/`. Backend e produção não são afetados. Rollback via `git checkout` dos arquivos modificados.

### Scope Boundary
- ✅ **DENTRO:** `frontend-v2/app/sepse-dashboard/`, `frontend-v2/app/antimicrobial-stewardship/`, `frontend-v2/app/prophylaxis-bundles/`, novos componentes em `frontend-v2/components/`, novas stories, design tokens
- ✅ **DENTRO:** Arquivos de handoff em `docs/audit/handoff-product-designer/`
- ❌ **FORA:** `src/intensicare/` (backend), `docs/rules/` (catálogo legado), `docs/audit/` (relatório final — somente leitura)

---

## Regras de Ouro (Agentic-Loop — Adaptado para Design-to-Code)

1. **Envelope validado.** Goal, Context, Constraints, Done When, Risk Level, Scope Boundary acima. Se algo estiver ambíguo, clarificar ANTES de começar.
2. **RECON antes de desenhar.** Carregar `figma-intake-agent-loop` e inspecionar design tokens existentes (`app/tokens-generated.css`, `app/globals.css`), componentes existentes (`components/`), e API client (`lib/api.ts`). NUNCA desenhar sem conhecer o que já existe.
3. **PLANS.md antes de codar.** Milestones de ≤3 arquivos cada, com dependências entre componentes mapeadas. Rollback por milestone.
4. **Delegate com skills pré-carregadas.** Subagentes NÃO carregam skills sozinhos. O orquestrador DEVE pré-carregar via `skill_view()` e passar no `context`. Skills deste plano: `figma-intake-agent-loop`, `design-token-management-loop`, `component-mapping-loop`, `design-to-code-agent-loop`, `ux-review-agent-loop`, `accessibility-review-agent-loop`, `visual-regression-agent-loop`, `storybook-sync-agent-loop`, `design-system-governance-loop`.
5. **Verificar cada milestone.** `npx tsc --noEmit`, `npm run build`, `npm run storybook -- --smoke-test` (ou `npx storybook dev --no-open` para verificar). Subagente DIFERENTE faz cross-validation.
6. **Gatekeeper ≠ implementador.** `ux-review-agent-loop` + `accessibility-review-agent-loop` + `visual-regression-agent-loop` são gatekeepers independentes ao final de cada fase. NUNCA usar o mesmo agente.
7. **Estado no filesystem.** `PLANS.md`, `HANDOFF.yaml`, `docs/audit/handoff-product-designer/`. NUNCA criar MDs temporários; usar `memory` para contexto entre sessões.
8. **Flywheel.** Após conclusão: `storybook-sync-agent-loop`, `design-system-governance-loop`. Converter descobertas em regras de design system.

---

## Anti-Patterns (Design-to-Code Específicos)

| Anti-Pattern | Correção |
|---|---|
| ❌ Orquestrador codando componente diretamente | DELEGAR para `design-to-code-agent-loop` + subagentes |
| ❌ Criar token CSS fora do sistema (`var(--minha-cor)`) | Usar `design-token-management-loop` e versionar em `tokens-generated.css` |
| ❌ Componente sem Storybook story | Todo componente → `.stories.tsx` com variantes de estado |
| ❌ Pular acessibilidade | `accessibility-review-agent-loop` em TODO componente clínico |
| ❌ fetch() direto em vez de `lib/api.ts` | Usar `request<T>()` wrapper — JWT, error handling, tipagem |
| ❌ Ignorar componentes existentes (recriar AlertCard, SeverityBadge) | RECON primeiro — ver `components/` e `lib/` |
| ❌ Um agente cobrindo >3 componentes | Máximo 3 componentes por subagente |
| ❌ Confiar em self-report | `git diff --stat` + `npx tsc --noEmit` após cada subagente |
| ❌ Gatekeeper = implementador | Revisor SEMPRE diferente |
| ❌ MDs temporários para estado | `HANDOFF.yaml` como fonte canônica |
| ❌ Design sem contrato de API | Todo componente que consome API precisa do contrato OpenAPI |

---

## Fases de Execução

### FASE 0 — RECON + Design Token Audit (1 agente, BLOQUEANTE)

**Objetivo:** Mapear o design system existente ANTES de qualquer design novo.

| Tarefa | Ferramenta | Output |
|--------|-----------|--------|
| Auditar todos os design tokens em `tokens-generated.css` e `globals.css` | `read_file` | Catálogo de tokens existentes |
| Listar todos os componentes em `components/` com seus props e stories | `search_files` + `read_file` | Catálogo de componentes reutilizáveis |
| Listar todas as funções exportadas em `lib/api.ts` e tipos | `read_file` | Catálogo de API consumers |
| Verificar pages existentes em `app/` para evitar duplicação de rotas | `search_files(pattern='page.tsx')` | Catálogo de rotas |
| Produzir `RECON_DESIGN_SYSTEM.md` | Agente `figma-intake-agent-loop` | Baseline para FASE 1 |

**Gate FASE 0:** `RECON_DESIGN_SYSTEM.md` com todos os tokens, componentes, APIs e rotas existentes catalogados.

---

### FASE 1 — Design Tokens + Componentes Base (2 agentes em paralelo)

**Objetivo:** Criar tokens de design para os novos domínios E componentes base reutilizáveis.

#### Agente 1A — Design Tokens

| Domínio | Tokens Necessários |
|---------|-------------------|
| Sepse | `--clinical-sepsis-*` (critério maior/menor, confirmado/suspeito, hour-1 bundle status) |
| Antimicrobiano | `--clinical-antimicrobial-*` (espectro, duração, stewardship score) |
| Profilaxia | `--clinical-prophylaxis-*` (bundle completo/pendente/ausente, risco TEV) |

**Skills:** `design-token-management-loop`
**Output:** Tokens adicionados em `tokens-generated.css`, validados via `design-system-governance-loop`

#### Agente 1B — Componentes Base

| Componente | Props | Domínio |
|-----------|-------|---------|
| `CriteriaChecklist` | `{items: Criterion[], domain: string, onToggle: fn}` | Sepse (maiores/menores) + Antimicrobiano (12 critérios) |
| `ClinicalTimeline` | `{events: TimelineEvent[], domain: string}` | Sepse (confirmação: qSOFA→lactato→culturas→bundle) |
| `BundleCard` | `{bundle: Bundle, status: 'complete'\|'partial'\|'pending'}` | Profilaxia (LAMGD, TEV, hiperglicemia, etc.) |
| `StewardshipScoreBadge` | `{score: number, criteria: Criterion[]}` | Antimicrobiano (scoring VERMELHO/AMARELHO/NEUTRO) |

**Skills:** `component-mapping-loop` → `design-to-code-agent-loop`
**Output:** Componentes em `components/` com `.stories.tsx`, usando tokens existentes + novos

**Gate FASE 1:** `ux-review-agent-loop` + `accessibility-review-agent-loop` em todos os componentes. GO somente se WCAG AA ≥ 95% e zero regressões.

---

### FASE 2 — Páginas (3 agentes em paralelo, 1 por domínio)

**Objetivo:** Montar as páginas completas usando os componentes base + API client.

#### Agente 2A — Sepse Dashboard (`app/sepse-dashboard/page.tsx`)

**Dados disponíveis (API):**
- `GET /api/v1/alerts?type=sepse` — lista de alertas de sepse
- `GET /api/v1/patients/{mpiId}/detail` — vitals + scores + alertas do paciente
- `POST /api/v1/alerts/{id}/acknowledge|resolve|escalate` — ações em alertas

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Sepse Dashboard                        [Filter: Unit ▼] │
├──────────────────────┬──────────────────────────────┤
│ Patient List (leito) │ Patient Detail (selected)      │
│ ┌──────────────────┐ │ ┌────────────────────────────┐ │
│ │ Leito 01 ● critic│ │ │ qSOFA: 2 ▲  Lactate: 3.2 ▲ │ │
│ │ Leito 02 ● watch │ │ │ ┌────────────────────────┐ │ │
│ │ Leito 03 ○ normal│ │ │ │ Criteria:              │ │ │
│ │ Leito 04 ● critic│ │ │ │ ☑ Major: hypotension   │ │ │
│ │ ...              │ │ │ │ ☑ Major: lactate > 2   │ │ │
│ └──────────────────┘ │ │ │ ☑ Major: altered mental │ │ │
│                      │ │ │ ☐ Minor: tachycardia    │ │ │
│                      │ │ │ ...                     │ │ │
│                      │ │ └────────────────────────┘ │ │
│                      │ │ ┌────────────────────────┐ │ │
│                      │ │ │ Timeline:              │ │ │
│                      │ │ │ 14:30 qSOFA=2 (screen) │ │ │
│                      │ │ │ 14:45 Lactate=3.2 (conf)│ │ │
│                      │ │ │ 15:00 Cultures collected│ │ │
│                      │ │ │ 15:30 Bundle started    │ │ │
│                      │ │ └────────────────────────┘ │ │
│                      │ └────────────────────────────┘ │
└──────────────────────┴──────────────────────────────┘
```

**Skills:** `design-to-code-agent-loop`
**Output:** `app/sepse-dashboard/page.tsx` + `app/sepse-dashboard/layout.tsx`

#### Agente 2B — Antimicrobiano Stewardship (`app/antimicrobial-stewardship/page.tsx`)

**API:** Mock inicial (contrato OpenAPI será provido por Niemeyer). Usar `lib/api.ts` com endpoint temporário `/api/v1/antimicrobial`.

**Dados mock:**
```typescript
interface AntimicrobialCriterion {
  id: string;
  name: string;         // ex: "Duração > 7 dias"
  category: string;     // "duração" | "espectro" | "dose" | "CVC" | "cultura"
  status: boolean;      // critério atendido?
  alertTriggered: boolean;
}

interface AntimicrobialAssessment {
  patientMpiId: string;
  criteria: AntimicrobialCriterion[];
  score: number;        // 0-12
  severity: 'VERMELHO' | 'AMARELO' | 'NEUTRO';
  recommendation: string;
}
```

**Skills:** `design-to-code-agent-loop`
**Output:** `app/antimicrobial-stewardship/page.tsx` + mock data types em `lib/antimicrobial-types.ts`

#### Agente 2C — Profilaxia Bundles (`app/prophylaxis-bundles/page.tsx`)

**API:** Mock inicial (contrato OpenAPI será provido por Niemeyer).

**Bundles:**
1. **LAMGD** — Úlcera de estresse (4 critérios)
2. **TEV** — Tromboembolismo venoso (5 critérios + ajuste renal/IMC)
3. **Hiperglicemia** — Controle glicêmico (3 critérios)
4. **Mobilização Precoce** — (3 critérios)
5. **Dispositivos Invasivos** — Bundles de inserção (5 critérios)

**Skills:** `design-to-code-agent-loop`
**Output:** `app/prophylaxis-bundles/page.tsx` + mock data types em `lib/prophylaxis-types.ts`

**Gate FASE 2:** `ux-review-agent-loop` + `accessibility-review-agent-loop` + `visual-regression-agent-loop` em cada página. GO somente se zero regressões nos componentes existentes.

---

### FASE 3 — Integração + GATE Final (1 agente, sequencial)

**Objetivo:** Integrar as páginas na navegação, atualizar Storybook, validar build completo.

| Tarefa | Output |
|--------|--------|
| Adicionar links no `Layout` (sidebar) para as novas páginas | Navegação integrada |
| `storybook-sync-agent-loop` para todas as novas stories | Storybook atualizado |
| `npm run build` — verificar build completo | Build sem erros |
| `design-system-governance-loop` — validar tokens não-duplicados | Tokens consistentes |
| Atualizar `docs/audit/handoff-product-designer/HANDOFF.yaml` | Status final |
| Produzir `COMPLETION_REPORT.md` com evidência de cada milestone | Relatório final |

**Gate FASE 3:** `visual-regression-agent-loop` final + `ux-review-agent-loop` final. GO somente se build passa e zero regressões.

---

## Dependências Entre Fases

```
FASE 0 (RECON Design System)
 │
 ▼
FASE 1A (Tokens) ──┐  PARALELO
FASE 1B (Componentes) ─┘
 │
 ▼
FASE 2A (Sepse Dashboard) ──┐
FASE 2B (Antimicrobiano)  ──┤  PARALELO (3 agentes)
FASE 2C (Profilaxia)       ──┘
 │
 ▼
FASE 3 (Integração + GATE)
```

---

## Métricas de Sucesso

| Artefato | Critério |
|----------|----------|
| `RECON_DESIGN_SYSTEM.md` | Todos os tokens, componentes, APIs e rotas catalogados |
| Novos design tokens | Registrados em `tokens-generated.css`, zero duplicações, governados |
| 4 componentes base | Cada um com `.stories.tsx` (≥3 variantes por story), WCAG AA ≥ 95% |
| 3 páginas | Cada uma funcional, integrada com API (real ou mock), navegável |
| `npx tsc --noEmit` | Zero erros |
| `npm run build` | Zero erros |
| Visual regression | Zero regressões em componentes existentes |
| `COMPLETION_REPORT.md` | Evidência de cada milestone concluído |
| `HANDOFF.yaml` | Status completo dos 3 domínios |

---

## Apêndice A: Dados do Gap Audit Relevantes

Ver `docs/audit/BACKEND_FRONTEND_GAP_MAP.md` para o relatório completo. Resumo dos 3 domínios:

| Domínio | Regras | Backend | API | Frontend Atual | Esforço |
|---------|--------|---------|-----|---------------|---------|
| Sepse | 101 | `domain_sepsis.py` ✅ | 5 endpoints REST ✅ | Apenas alert-triage genérico | L |
| Antimicrobiano | 3 | — | — | — | L |
| Profilaxia | 8 | — | — | — | L |

---

## Apêndice B: Design Tokens Existentes (Referência Rápida)

```css
/* Clinical Severity (já existente) */
--clinical-severity-normal-on-surface / -wash / -signal
--clinical-severity-watch-on-surface / -wash / -signal
--clinical-severity-urgent-on-surface / -wash / -signal
--clinical-severity-critical-on-surface / -wash / -signal

/* Clinical Status (já existente) */
--clinical-status-attended-color / -on-color
--clinical-status-pending-color / -on-color

/* Spacing, Radius, Elevation, Motion */
--spacing-{0..16}, --radius-{sm,md,lg,xl,full}
--elevation-{none,sm,md,lg}
--motion-duration-{instant,fast,normal,slow,gentle}
```

---
**Pronto para execução.** O orquestrador deve carregar este arquivo como prompt base e seguir as fases na ordem especificada.
