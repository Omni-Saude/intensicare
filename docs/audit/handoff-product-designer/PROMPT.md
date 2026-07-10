# PROMPT.md — IntensiCare Frontend v3 Rebuild

**Instrução:** Este prompt é autocontido. Pode ser colado como primeira mensagem em uma sessão nova do Product-Design-Orchestrator. Leia completamente antes de agir.

---

## Tarefa

Construir o frontend do IntensiCare **100% do zero**. Nada é copiado do frontend v2.

O backend tem 9 trilhas clínicas definidas em YAML (`_work/alerts/pathways/`), um motor de avaliação, e um motor de alertas. O frontend v2 tem 33 páginas com erro de UX: domínios isolados que não respondem à jornada real do intensivista.

A jornada correta é: **Dashboard (visão geral) → Patient Detail (todos os riscos) → Pathway View (estado + critérios + ação)**.

Você vai construir 6 páginas core. A trilha de **Sepse** é o MVP benchmark — as outras 8 replicam o mesmo padrão sem código novo.

## Princípios de UX (Imutáveis)

1. **Cada componente responde a uma pergunta da jornada.** "Isso ajuda o intensivista a decidir?" Se não, não existe.
2. **Densidade com clareza.** Muita informação em pouco espaço. Severidade = cor + posição + movimento.
3. **≤2 cliques para qualquer informação crítica.**
4. **Modo escuro como padrão.** UTI 24h. Luzes baixas à noite.
5. **Severidade é o atributo visual primário.** normal/watch/urgent/critical → verde/âmbar/laranja/vermelho.

## Regras de Ouro (Agentic Loop)

1. **Envelope antes de tudo.** Validar Goal, Context, Constraints, Done When de cada milestone.
2. **RECON antes de agir.** Ler o milestone no HANDOFF.yaml. Entender o schema OpenAPI. Só então produzir.
3. **PLANS.md local.** Para cada milestone, criar mini-plano com: o que gerar, rollback.
4. **`delegate_task` com skills.** Para implementação, usar `delegate_task`. Pré-carregar skills via `skill_view()`.
5. **Verificar cada output.** `npm run build`, `npm run lint`, testar no browser.
6. **Gatekeeper ≠ Implementador.** Review é feito por outro agente ou humano.
7. **Estado no filesystem.** HANDOFF.yaml é fonte canônica. Atualizar após cada milestone.
8. **Flywheel.** Após cada milestone: o que funcionou? o que falhou? Atualizar skills.

## Anti-Patterns (Específicos)

- ❌ **Copiar qualquer coisa do frontend-v2.** Nem componentes, nem tokens, nem API client, nem CSS. NADA.
- ❌ **Criar página standalone de domínio.** Toda informação clínica vive no Patient Detail ou Pathway View.
- ❌ **Componente específico por trilha.** StateFlow, CriteriaList, RecommendationsPanel são genéricos.
- ❌ **Pular acessibilidade.** WCAG 2.1 AA desde o M0.
- ❌ **Hardcodar dados de trilha.** Tudo vem da API. Nada de mock no componente.
- ❌ **Componente sem pergunta da jornada.** "Este componente é bonito" não é justificativa.

## Fontes de Verdade (ÚNICAS)

1. **`docs/contracts/pathways-openapi.yaml`** — schemas, endpoints, tipos
2. **`_work/alerts/pathways/sepse.yaml`** — estrutura de trilha benchmark
3. **`FRONTEND_REBUILD_PLAN.md` § 1** — jornada do intensivista

## Setup Inicial (M0)

```bash
# 1. Criar projeto DO ZERO
npx create-next-app@latest frontend-v3 --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"

# 2. Dependências
cd frontend-v3
npm install @radix-ui/react-slot class-variance-authority clsx tailwind-merge lucide-react recharts react-syntax-highlighter swr
npx shadcn@latest init

# 3. Estrutura de diretórios (criar do zero)
mkdir -p lib components/ui app/{patient,alerts,pathways,admin,auth}
```

## Design System (M0 — Construir do Zero)

```css
/* app/globals.css — Sistema de severidade */
:root[data-theme='dark'] {
  --severity-normal: #2DD269;
  --severity-watch: #F2B90D;
  --severity-urgent: #F96F06;
  --severity-critical: #FF3B4A;

  --severity-normal-wash: color-mix(in srgb, var(--severity-normal) 12%, transparent);
  --severity-watch-wash: color-mix(in srgb, var(--severity-watch) 12%, transparent);
  --severity-urgent-wash: color-mix(in srgb, var(--severity-urgent) 14%, transparent);
  --severity-critical-wash: color-mix(in srgb, var(--severity-critical) 16%, transparent);

  --surface-canvas: #0a0e14;
  --surface-raised: #141b22;
  --surface-overlay: #1c2530;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --border-default: #30363d;
}

@keyframes pulse-critical {
  0%, 100% { box-shadow: 0 0 0 0 var(--severity-critical-wash); }
  50% { box-shadow: 0 0 8px 2px var(--severity-critical); }
}
.severity-critical-pulse {
  animation: pulse-critical 2s infinite;
}
```

## API Client (M0 — Derivado dos Schemas OpenAPI)

```typescript
// lib/api.ts — Tipos derivados de pathways-openapi.yaml
// NÃO copiar do v2. Escrever a partir dos schemas.

type SeverityLevel = 'normal' | 'watch' | 'urgent' | 'critical';

interface Pathway { /* schema: pathways-openapi.yaml § Pathway */ }
interface PathwayState { /* schema: pathways-openapi.yaml § PathwayState */ }
interface PatientPathway { /* schema: pathways-openapi.yaml § PatientPathway */ }
interface PathwayProgress { /* schema: pathways-openapi.yaml § PathwayProgress */ }
interface EvaluatedCriterion { /* critério COM avaliação */ }
interface StateTransition { /* schema: pathways-openapi.yaml § state_history */ }

// Funções — só as que o frontend realmente consome
async function fetchDashboard(unit?: string): Promise<DashboardResponse>;
async function fetchPatientDetail(mpiId: string): Promise<PatientDetailResponse>;
async function fetchPatientPathways(mpiId: string): Promise<{ items: PatientPathway[]; total: number }>;
async function fetchPathwayProgress(mpiId: string, ppId: number): Promise<PathwayProgress>;
async function fetchPathways(): Promise<{ items: Pathway[]; total: number }>;
async function fetchPathway(id: number): Promise<Pathway>;
async function fetchAlerts(params?: AlertFilters): Promise<AlertListResponse>;
async function acknowledgeAlert(id: number): Promise<AlertInfo>;
async function escalateAlert(id: number): Promise<AlertInfo>;
async function resolveAlert(id: number, resolution: string): Promise<AlertInfo>;
```

## Ordem de Execução

```
M0 (Foundation: 2d)
├── M1 (Dashboard: 3d) ─────────────────────────────────────┐
├── M2 (Patient Detail: 3d) ──► M3 (Pathway Sepse: 4d) ──► M7 (8 trilhas: 6d)
├── M4 (Alert Triage: 3d) ───────────────────────────────────┤
├── M5 (Pathway Catalog: 2d) ────────────────────────────────┤
└── M6 (Admin: 2d) ──────────────────────────────────────────┘
                                                            │
                                              M8 (Integração: 3d)
                                              ├── E2E, a11y, performance
                                              └── Cleanup: v2 → archive, v3 → v2
```

**M1, M2, M4, M5, M6 podem ser paralelizados** (só dependem de M0).  
**M3 requer M2** (precisa do Patient Detail para navegação).  
**M7 requer M3** (componentes genéricos precisam existir).

## Para Cada Milestone

1. Ler `HANDOFF.yaml` → milestone atual, status, deliverables
2. Ler `DESIGN_BRIEF.yaml` → domínio, componentes, props, data contracts
3. Criar mini-plano local
4. Implementar com `delegate_task` (pré-carregar skills relevantes)
5. Verificar: `npm run build`, `npm run lint`, `npx tsc --noEmit`, teste manual
6. Atualizar `HANDOFF.yaml`: `status: "completed"`
7. **M0 e M3:** parar para review do gate (G0/G1)

## Verificações Obrigatórias

```bash
npm run build        # zero erros
npm run lint         # zero warnings
npx tsc --noEmit     # tipos OK
```

## Quando Parar e Escalar

- Endpoint retorna 500/404/422 → reportar ao Parreira. Não fazer workaround no frontend.
- `GET /patients/{mpi_id}/pathways` não existe → **bloqueia M2 e M3**. Escalar imediatamente.
- WebSocket não conecta → usar fallback de polling (30s Dashboard, 60s Patient). Reportar CSP.
- Dúvida sobre jornada do usuário → consultar FRONTEND_REBUILD_PLAN.md § 1.

## Cleanup do v2 (último passo do M8, após G2 aprovado)

```bash
cd /Users/familia/intensicare
mv frontend-v2 frontend-v2-archive   # arquivar v2 antigo
mv frontend-v3 frontend-v2           # promover v3 como canônico
git add -A
git commit -m "feat: substitui frontend-v2 pelo v3 (pathway-centric rebuild)"
```

O `frontend-v2-archive/` fica no repo para consulta. Remover manualmente após 30 dias se não houver rollback.

## Referências

1. `HANDOFF.md` — envelope e fases
2. `DESIGN_BRIEF.yaml` — especificações de componentes e contratos
3. `PLANS.md` — milestones e dependências
4. `HANDOFF.yaml` — estado canônico (atualize após cada milestone!)
5. `FRONTEND_REBUILD_PLAN.md` — blueprint completo com jornada do intensivista
6. `docs/adr/ADR-0030` a `ADR-0034` — decisões de arquitetura
7. `docs/contracts/pathways-openapi.yaml` — API schemas

**Construa do zero. Siga a jornada. Boa sorte.**
