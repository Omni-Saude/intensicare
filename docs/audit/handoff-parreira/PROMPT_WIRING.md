# PROMPT — Parreira: Wiring do Frontend v3 com Backend IntensiCare

**De:** Niemeyer (System Architect)  
**Para:** Parreira (DevOps Team Orchestrator)  
**Data:** 2026-07-09  
**Objetivo:** Spawn e coordenar agentes especializados para conectar o novo frontend (v3, construído por Ive) com o backend existente, resolver gaps de API, e preparar o ambiente para M7 (8 trilhas restantes) e M8 (produção).

---

## Contexto

Ive (Product-Design-Orchestrator) concluiu M0-M6 do rebuild do frontend. O código está em `/Users/familia/intensicare/frontend-v3/`. São **50 componentes React**, **403 linhas de API client** (`lib/api.ts`), **14 funções de endpoint**, middleware de auth, AppShell com sidebar.

O frontend está **pronto visualmente**, mas **não conectado ao backend real**. As funções em `lib/api.ts` chamam `/api/v1/*` — esses endpoints precisam existir, responder com os shapes corretos, e estar acessíveis via proxy do Next.js.

Seu papel: **orquestrar agentes especializados para fechar todos os gaps de wiring, infra, e dados.**

---

## Regras de Ouro (Agentic Loop — Parreira)

1. **RECON antes de agir.** Ler cada arquivo relevante. Não assumir shapes de API.
2. **`delegate_task` com skills.** Cada tarefa de wiring vai para um agente especializado com skills específicas carregadas via `skill_view()`.
3. **Gatekeeper ≠ Implementador.** Você orquestra e revisa. Agentes diferentes implementam e testam.
4. **Estado no filesystem.** Atualizar `HANDOFF.yaml` e produzir `RUNBOOK.md` com decisões.
5. **Flywheel.** Após cada batch: o que funcionou? o que quebrou? Atualizar skills.
6. **Max 3 `delegate_task` concorrentes.** Paralelize onde possível.

---

## Fase 1 — RECON: Análise de Gaps (1 agente, ≤ 30 min)

Spawn um agente com `delegate_task` para analisar e produzir a matriz de gaps:

```
delegate_task(
  goal="Produzir matriz de gaps entre frontend-v3 API client e backend endpoints reais",
  context="""
Frontend: /Users/familia/intensicare/frontend-v3/lib/api.ts (403 linhas, 14 funções de endpoint)
Backend: /Users/familia/intensicare/ (monorepo, serviços de domínio)

Para cada função em lib/api.ts:
1. Verificar se o endpoint existe no backend (rota registrada)
2. Verificar se o shape da resposta do backend casa com o tipo TypeScript esperado
3. Verificar autenticação (JWT Bearer vs cookie)
4. Verificar CORS/CSP
5. Classificar severidade: CRITICAL (ausente), MAJOR (shape diferente), MINOR (campo opcional faltando)

Output: arquivo /Users/familia/intensicare/docs/audit/handoff-parreira/WIRING_GAPS.md com tabela de gaps
""",
  toolsets=["terminal", "file", "web"]
)
```

**Entregável:** `docs/audit/handoff-parreira/WIRING_GAPS.md` — tabela com endpoint, status, shape match, severidade, ação necessária.

---

## Fase 2 — Batch 1: Auth & Infra (2 agentes paralelos, ≤ 2h)

### Agente 2.1 — Alinhamento de Autenticação

```
delegate_task(
  goal="Alinhar fluxo de autenticação entre frontend-v3 e backend",
  context="""
Frontend espera:
  POST /api/v1/auth/login (form-urlencoded: username + password)
  Response: { access_token, token_type, user: { id, name, email, role, is_admin } }
  API calls: Authorization: Bearer {token} header
  Middleware: lê cookie 'token' para proteger rotas. Se ausente, redirect /login.

Backend atual (verificar):
  /auth/login existe? Retorna access_token?
  JWT contém claims: is_admin, role, sub, exp?
  Cookie vs Bearer: o backend seta cookie HttpOnly ou espera Authorization header?
  CORS: permite origin do frontend?

Tarefas:
1. Verificar endpoint de login do backend e documentar contrato real
2. Se houver mismatch: corrigir NO BACKEND (não no frontend) para casar com o contrato esperado
3. Garantir que JWT contém claims: sub, is_admin, role, exp
4. Alinhar estratégia de token: se backend usa cookie HttpOnly, frontend middleware já funciona. Se backend usa Bearer, middleware precisa ser ajustado OU backend precisa setar cookie também.
5. Testar fluxo completo: POST /login → recebe token → GET /dashboard com Authorization header
""",
  toolsets=["terminal", "file", "web"]
)
```

### Agente 2.2 — Proxy & Infra (paralelo com 2.1)

```
delegate_task(
  goal="Configurar proxy reverso, CSP, CORS e next.config.js para frontend-v3",
  context="""
Frontend está em /Users/familia/intensicare/frontend-v3/
Backend roda em localhost:8000 (verificar porta real)

Tarefas:
1. Criar/verificar next.config.ts com rewrites:
   async rewrites() {
     return [{ source: '/api/v1/:path*', destination: 'http://localhost:8000/api/v1/:path*' }]
   }

2. Configurar CSP headers (injetar no next.config.ts ou middleware):
   Content-Security-Policy: "default-src 'self'; connect-src 'self' ws://localhost:8000 wss://localhost:8000; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-eval'"

3. Verificar CORS no backend: permitir origin http://localhost:3000 (dev) e origin de produção
   Se o backend usa FastAPI/Starlette: CORSMiddleware com origins corretos
   Se não configurado: ADICIONAR (não é opcional — frontend não funciona sem)

4. Verificar porta do backend: 8000? 8080? Outra?
   Documentar em WIRING_GAPS.md

5. Health check: GET /api/v1/health deve retornar { status: "ok", version: "..." }
""",
  toolsets=["terminal", "file", "web"]
)
```

---

## Fase 3 — Batch 2: API Shape Validation (3 agentes paralelos, ≤ 3h)

### Agente 3.1 — Dashboard + Patient Detail

```
delegate_task(
  goal="Validar e corrigir shapes dos endpoints Dashboard e Patient Detail",
  context="""
Frontend espera (lib/api.ts):

GET /api/v1/dashboard[?unit=]
  Response: DashboardResponse {
    patients: PatientBedSummary[] {
      mpi_id, patient_name, bed, unit, mews?, news2?,
      severity: 'normal'|'watch'|'urgent'|'critical',
      last_vital_at?, active_pathways?: {slug, severity}[],
      vitals?: { hr?, spo2?, bp_sys?, bp_dia? }
    },
    total: number,
    critical_count: number,
    unit_counts?: Record<string, number>
  }

GET /api/v1/patients/{mpiId}
  Response: PatientDetailResponse {
    mpi_id, patient_name, bed, unit,
    vitals: VitalRecord[] { name, value, unit, measured_at, severity? },
    scores: ScoreRecord[] { name, value, measured_at, trend? },
    active_pathways_count: number
  }

Tarefas:
1. Para cada endpoint, bater no backend real e comparar response shape com o tipo TypeScript
2. Listar campos faltantes, divergentes, ou com tipos errados
3. Se backend não tem o endpoint: criar (preferir adicionar ao serviço existente)
4. Se backend tem mas com shape diferente: criar adapter OU ajustar backend
5. Testar com curl e documentar resultado
""",
  toolsets=["terminal", "file", "web"]
)
```

### Agente 3.2 — Pathways + Alerts

```
delegate_task(
  goal="Validar e corrigir shapes dos endpoints de Pathways e Alerts",
  context="""
Frontend espera (lib/api.ts):

GET /api/v1/patients/{mpiId}/pathways?status=active
  Response: { items: PatientPathway[], total: number }
  PatientPathway: { id, mpi_id, pathway: Pathway, current_state: PathwayState,
    criteria?: PathwayCriteria[], status: 'active'|'completed'|'archived',
    severity?: SeverityLevel, enrolled_at, enrolled_by?, completed_at?, updated_at? }

GET /api/v1/patients/{mpiId}/pathways/{ppId}/progress
  Response: PathwayProgress {
    patient_pathway_id, mpi_id, pathway_name, current_state: PathwayState,
    criteria_summary: { total, met, not_met, pending },
    criteria?: PathwayCriteria[], state_history?: StateTransition[],
    trend: 'improving'|'stable'|'worsening'|'none',
    last_evaluated_at?, recommendation? }

GET /api/v1/pathways?active_only=true → { items: Pathway[], total }
GET /api/v1/pathways/{id} → Pathway
GET /api/v1/alerts → AlertListResponse { items: AlertInfo[], total }
POST /api/v1/alerts/{id}/acknowledge → AlertInfo
POST /api/v1/alerts/{id}/escalate → AlertInfo
POST /api/v1/alerts/{id}/resolve { resolution } → AlertInfo

⚠️ CRÍTICO: Estes são os endpoints NOVOS que o frontend v3 mais depende.
Se não existirem, o Patient Detail (ActivePathways) e o Pathway View ficam vazios.

Tarefas:
1. Bater em cada endpoint e comparar response shape
2. Prioridade #1: /patients/{mpiId}/pathways e /patients/{mpiId}/pathways/{ppId}/progress
   Se não existirem, CRIAR no backend (trilhas_engine.py deve expor esses endpoints)
3. Validar que o endpoint de progress retorna dados REAIS para a trilha de sepse
4. Testar acknowledge/escalate/resolve nos alertas
5. Documentar resultado em WIRING_GAPS.md
""",
  toolsets=["terminal", "file", "web"]
)
```

### Agente 3.3 — Admin + Health (paralelo)

```
delegate_task(
  goal="Validar endpoints de Admin e Health",
  context="""
GET /api/v1/admin/users → { items: UserInfo[], total }
  UserInfo: { id, name, email, role, is_admin }

GET /api/v1/health → { status: string, version: string }

Tarefas:
1. Verificar se /admin/users existe e retorna lista de usuários com is_admin
2. Se não existe: criar endpoint mínimo (pode ser mock inicialmente)
3. Verificar /health (essencial para monitoramento)
4. Documentar
""",
  toolsets=["terminal", "file", "web"]
)
```

---

## Fase 4 — Batch 3: M7 — 8 Trilhas Restantes (2 agentes paralelos, ≤ 4h)

O frontend já tem componentes genéricos (StateFlow, CriteriaList, etc.). O que falta é **o backend servir dados reais** para cada trilha.

### Agente 4.1 — Validar YAMLs e endpoints (trilhas 2-5)

```
delegate_task(
  goal="Validar e garantir dados para trilhas: renal, respiratório, ventilação, equilíbrio",
  context="""
As trilhas são definidas em /Users/familia/intensicare/_work/alerts/pathways/*.yaml

Trilhas a validar:
2. renal.yaml — KDIGO, creatinina, débito urinário
3. respiratorio.yaml — SpO₂/FiO₂, FR, gasometria
4. ventilacao.yaml — Parâmetros VM, desmame, extubação
5. equilibrio.yaml — Na⁺, K⁺, Ca²⁺, Mg²⁺, pH

Para cada trilha:
1. Verificar se o YAML é válido (parseável)
2. Verificar se o endpoint GET /patients/{mpiId}/pathways/{ppId}/progress retorna dados
3. Verificar se criteria_summary, criteria[], state_history, recommendation estão preenchidos
4. Se vazio: carregar dados de teste reais no banco para pelo menos 1 paciente
5. Testar: resposta do endpoint contém todos os campos que o PathwayProgress TypeScript espera
""",
  toolsets=["terminal", "file", "web"]
)
```

### Agente 4.2 — Validar YAMLs e endpoints (trilhas 6-9)

```
delegate_task(
  goal="Validar e garantir dados para trilhas: nutrição, profilaxia, sedação, delirium",
  context="""
Trilhas a validar:
6. nutricao.yaml — TNE, ingestão calórica, proteica
7. profilaxia.yaml — TEV, úlcera de estresse, cabeceira
8. sedacao.yaml — RASS, sedoanalgesia
9. delirium.yaml — CAM-ICU, rastreio, manejo

Mesmo processo do agente 4.1: validar YAML, verificar endpoint, carregar dados de teste, testar shape.
""",
  toolsets=["terminal", "file", "web"]
)
```

---

## Fase 5 — Batch 4: WebSocket & Real-time (1 agente, ≤ 2h)

```
delegate_task(
  goal="Implementar ou configurar WebSocket para atualização em tempo real do frontend",
  context="""
ADR-0034 define WebSocket como mecanismo primário com fallback para polling.
O frontend atualmente usa SWR com polling (sem WebSocket).

Tarefas:
1. Verificar se backend tem endpoint WebSocket (ex: ws://localhost:8000/ws)
2. Se não tem: criar endpoint mínimo que emite eventos:
   - bed_grid.updated (Dashboard)
   - alert.raised, alert.updated (Dashboard + Patient)
   - vitals.updated (Patient Detail)
   - pathway.updated (Patient Detail)
   - pathway.state_changed (Pathway View)
3. Configurar CSP para permitir ws:// (dev) e wss:// (prod)
4. Se WebSocket for complexo demais para agora: melhorar polling (15s Dashboard, 30s Patient)
5. Documentar status: funcional / postergado / fallback-only
""",
  toolsets=["terminal", "file", "web"]
)
```

---

## Fase 6 — Batch 5: Deploy & CI/CD (1 agente, ≤ 2h)

```
delegate_task(
  goal="Configurar pipeline de build e deploy para frontend-v3",
  context="""
Repositório: /Users/familia/intensicare/
Frontend: frontend-v3/ (Next.js 16, build com `npm run build`)

Tarefas:
1. Criar/atualizar GitHub Actions workflow para frontend-v3:
   - on push to feature/frontend-v3: lint + build + typecheck
   - on merge to main: build + deploy

2. Configurar variáveis de ambiente:
   - NEXT_PUBLIC_API_URL (se necessário — atualmente usa proxy /api/v1)
   - NODE_ENV

3. Verificar se `npm run build` passa no ambiente de CI
   (atualmente passa localmente: 2.6s compile, TypeScript OK)

4. Definir estratégia de deploy:
   - Dev: next dev (localhost:3000)
   - Staging: next start (porta 3000) atrás de Nginx
   - Prod: mesma coisa, com HTTPS

5. Script de cleanup pós-M8:
   mv frontend-v2 frontend-v2-archive
   mv frontend-v3 frontend-v2
   Atualizar CI/CD para apontar para frontend-v2/ (que será o v3 promovido)
""",
  toolsets=["terminal", "file", "web"]
)
```

---

## Fase 7 — Gate: Verificação e Signoff

Após todos os batches concluídos:

1. **Atualizar HANDOFF.yaml:**
   - M7: status → `completed` (se 8 trilhas funcionando)
   - M8: depende de testes E2E + a11y + performance que Ive precisa rodar

2. **Atualizar WIRING_GAPS.md** com resumo final:
   - Endpoints OK
   - Endpoints com adapter
   - Endpoints postergados
   - WebSocket status

3. **Produzir RUNBOOK.md** com:
   - Decisões tomadas
   - Comandos para dev, staging, prod
   - Rollback plan

---

## Ordem de Execução (Resumo)

```
FASE 1: RECON (1 agente, 30 min)
  └── WIRING_GAPS.md

FASE 2: Auth + Infra (2 agentes paralelos, 2h)
  ├── 2.1: Alinhar autenticação
  └── 2.2: Proxy, CSP, CORS, next.config.js

FASE 3: API Shape Validation (3 agentes paralelos, 3h)
  ├── 3.1: Dashboard + Patient Detail
  ├── 3.2: Pathways + Alerts ⚠️ CRÍTICO
  └── 3.3: Admin + Health

FASE 4: M7 — 8 Trilhas (2 agentes paralelos, 4h)
  ├── 4.1: renal, respiratório, ventilação, equilíbrio
  └── 4.2: nutrição, profilaxia, sedação, delirium

FASE 5: WebSocket (1 agente, 2h)

FASE 6: Deploy & CI/CD (1 agente, 2h)

FASE 7: Gate — atualizar HANDOFF.yaml + RUNBOOK.md
```

**Tempo total estimado:** ~14h de trabalho de agente (pode rodar em ~6h com paralelismo).

---

## Anti-Patterns (Específicos para Wiring)

- ❌ **Modificar o frontend para casar com backend quebrado.** O backend é que deve servir o contrato que o frontend espera. Os tipos em `lib/api.ts` são o contrato.
- ❌ **Criar mock no frontend.** Se o endpoint não existe, CRIE no backend. Mock no frontend = dívida.
- ❌ **Deixar CORS/CSP para depois.** Sem isso, nada funciona. É pré-requisito da Fase 2.
- ❌ **Commitar sem testar `npm run build`.** Ive já garantiu que build passa. Não quebre.
- ❌ **Ignorar os gatekeeper scores do M3.** DS 92%, UX 6.3/10 — os issues de UX (logout CRITICAL) precisam ser corrigidos no frontend (Ive) ou no backend (auth flow).

---

## Referências

- Frontend v3: `/Users/familia/intensicare/frontend-v3/`
- API client: `frontend-v3/lib/api.ts` (403 linhas, 14 funções)
- API contracts: `docs/contracts/pathways-openapi.yaml`
- YAMLs das trilhas: `_work/alerts/pathways/*.yaml`
- ADRs: `docs/adr/ADR-0030` a `ADR-0034`
- Handoff state: `docs/audit/handoff-product-designer/HANDOFF.yaml`
