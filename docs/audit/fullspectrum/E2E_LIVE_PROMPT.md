# PROMPT — Verificação End-to-End Ao Vivo da Plataforma IntensiCare (Browser Real)
## Do "passa nos testes" ao "funciona nas mãos do intensivista"

**De:** Orquestração de correção pós-auditoria (Claude Fable 5)
**Para:** Novo Orquestrador (hive-mind queen) — sessão de verificação de runtime
**Data:** 2026-07-13
**Tipo:** Execução local + interação real em Chrome + correção de bugs reais (ciclo fechado)
**Objetivo:** Subir a plataforma IntensiCare inteira localmente (backend + frontend + Postgres/Timescale + Redis), dirigir a jornada real do intensivista em um navegador Chrome de verdade, capturar comportamento/erros/bugs verdadeiros que só aparecem em runtime, e CORRIGIR o que estiver quebrado — cada correção verificada de novo no browser.

---

## ═══════ ENVELOPE ═══════

| Campo | Valor |
|-------|-------|
| **Goal** | Provar (ou refutar) que a plataforma funciona de verdade nas mãos de um usuário, num navegador real, na jornada completa Dashboard → Patient → Pathway → Ação — e corrigir todo bug real encontrado, com re-verificação no browser. |
| **Context** | IntensiCare no `main` pós-ciclo-de-correção (veredito GO-WITH-ISSUES 79.25). Backend FastAPI + Postgres/TimescaleDB + Redis; frontend Next.js 16 (frontend-v3). Repo: `/Users/familia/intensicare/`. |
| **Constraints** | Ambiente LOCAL apenas. Pode modificar código para corrigir bugs (diferente da auditoria original, que era read-only). Cada fix por agente especialista (≤3 arquivos), verificado. Sem deploy, sem cloud. |
| **Done When** | Relatório `E2E_LIVE_REPORT.md` com: matriz de fluxos testados (PASS/FAIL com screenshot), lista de bugs reais encontrados+corrigidos (antes/depois), bugs não-corrigíveis localmente (com razão), e veredito de runtime: a jornada do intensivista funciona ponta a ponta em Chrome? |
| **Risk Level** | L2 — sobe serviços locais, altera código de bug-fix, roda migrações no DB de dev. Sem produção. |

---

## ═══════ REGRAS DE OURO (aprendidas nesta base — LEIA) ═══════

1. **Você orquestra, agentes executam.** Hive-mind queen: NÃO code diretamente. Delegue a agentes especialistas (não-genéricos) com contexto pré-carregado. Roteamento inteligente: Haiku para fixes mecânicos/verificações, Sonnet para diagnóstico/implementação, você (o modelo principal) para síntese e adjudicação.
2. **Paralelismo máximo seguro.** Fluxos e fixes sem colisão de arquivos rodam em paralelo. Agentes que escrevem código usam **git worktrees isolados** (`git worktree add <scratchpad>/wt-X origin/main -b fix/X`) — NUNCA troque de branch no checkout principal com múltiplos agentes ativos (o stash é global entre worktrees e engole trabalho alheio — isso quebrou nesta sessão).
3. **NUNCA confie em self-report.** Após CADA agente: `git diff --stat` + `grep` + re-execução do comando de verificação você mesmo. Relatórios de agentes contêm fabricações ocasionais (já pegamos hex de hash inventado e "8 falhas pré-existentes" que eram 7+1 regressão). Verifique no filesystem/browser.
4. **Gatekeeper ≠ implementador.** Quem revisa não é quem escreveu.
5. **A prova é o BROWSER, não o teste.** Testes verdes não bastam — o objetivo é runtime real. Toda alegação de "funciona" precisa de screenshot ou trace de interação real no Chrome.
6. **Boot fresco, não `--reload` stale.** VERIFICAÇÃO DE BOOT = `PYTHONPATH=src .venv/bin/python -c "from intensicare.main import app"`. O `uvicorn --reload` MASCARA erros de import-time (serve código velho após reload falhado silenciosamente) — já nos enganou uma vez (NameError de import que "não existia" no server rodando).
7. **Estado no filesystem.** Relatórios em `docs/audit/fullspectrum/`. Handoff em `E2E_HANDOFF.yaml`.

---

## ═══════ FASE 0 — RECON + SUBIR O AMBIENTE (você + 1 agente de infra) ═══════

### 0.1 — Leia antes de agir
- `docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md` (+ ADENDO 2) — o que foi corrigido e o que ficou pendente.
- `docs/audit/fullspectrum/DIM_B_REAUDIT.md` e `DIM_D_REAUDIT.md` — achados de UX/integração mais recentes.
- `README.md` §Quick Start, `docker-compose.yml`, `Makefile`, `frontend-v3/package.json`, `.env` / `.env.local`.

### 0.2 — Suba a stack (delegue a um agente de infra, verifique você)
Ordem e armadilhas conhecidas:
1. **Postgres/TimescaleDB + Redis**: `docker compose up -d` (ou o container `intensicare-postgres` que já existe local). Confirme extensões: TimescaleDB, pgcrypto.
2. **Migrações**: `.venv/bin/alembic upgrade head` — **ARMADILHA CONHECIDA**: a cadeia tem `revision 0002` duplicada e `0016` que trunca `SODIUM_CORRECTION` em `VARCHAR(16)`, fazendo `upgrade head` from-scratch QUEBRAR antes das migrações novas. Se falhar, aplique até onde der e reporte; o dev DB atual já está em `0040`. NÃO conserte a cadeia antiga sem necessidade (fora de escopo — anote).
3. **venv**: pode estar recriado via `uv` (Python 3.12) SEM deps de teste. Se faltar pytest/ruff: `uv pip install pytest pytest-asyncio pytest-cov pytest-timeout httpx anyio ruff mypy`.
4. **Seed de dados**: `make seed-demo` (ou `.venv/bin/python scripts/dev/seed_demo.py`) — cria 5 pacientes `MPI-DEMO-001..005` com vitais frescos e enrollments (DEMO-001 sepse crítica, DEMO-002 sedação urgente). **Idempotente.** Sem isso, o dashboard fica vazio e nada é navegável.
5. **Backend**: `.venv/bin/uvicorn intensicare.main:app --port 8000 --app-dir src` (foreground OU background monitorado). Health: `curl localhost:8000/api/v1/health` → 200.
6. **Frontend**: `cd frontend-v3 && npm ci && npm run dev` (porta 3000). Se `npm ci` falhar por peer-deps: `--legacy-peer-deps`.
7. **Credenciais**: `admin` / `admin` (form-urlencoded no login; o cookie `token` HttpOnly é setado pelo backend).

**Output FASE 0:** `docs/audit/fullspectrum/E2E_HANDOFF.yaml` com estado dos serviços (up/down + versão), URL de cada um, e qualquer armadilha encontrada ao subir.

---

## ═══════ FASE 1 — DRIVER DE BROWSER (você define a ferramenta) ═══════

Você PRECISA de um Chrome real dirigível. Opções (escolha a que o ambiente suporta, teste antes de fanar out):
- **Playwright** (já é devDependency do frontend-v3; `npx playwright test` funciona; `chromium` instalável via `npx playwright install chromium`). PREFERIDO — os smoke tests em `frontend-v3/e2e/` já usam.
- Chrome headless via CDP (`--headless=new` + `Network.setCookie` para injetar o cookie `token`) — usado nesta sessão para screenshots autenticados.
- **ARMADILHA CRÍTICA CONHECIDA**: o JWT vive SÓ em memória no frontend; o middleware só checa PRESENÇA do cookie. Para navegar autenticado, faça login REAL pela UI (preencher form + submit) OU injete o cookie `token` via CDP. Um hard-reload/deep-link agora restaura sessão via `/auth/refresh` (cookie HttpOnly) — CONFIRME que isso funciona (foi corrigido neste ciclo, valide que sobreviveu).

Escreva um harness de interação reutilizável (Playwright spec ou script CDP) que os agentes de fluxo vão estender.

---

## ═══════ FASE 2 — FLUXOS REAIS (swarm, 1 agente por fluxo) ═══════

Cada agente dirige UM fluxo no Chrome, captura screenshots em cada passo, e reporta PASS/FAIL + qualquer erro de console/rede/render. Rode em paralelo onde não colidem (a maioria é read-only de navegação).

**F1 — Login + sessão:** carregar `/` sem cookie → redireciona `/login`; login admin/admin → dashboard; **F5 (reload) → CONTINUA logado** (bug de sessão foi corrigido — valide); deep-link direto `/patient/MPI-DEMO-001` em aba nova → carrega; logout → volta a `/login` e NÃO ressuscita sessão no reload seguinte.

**F2 — Dashboard:** grid de leitos renderiza os 5 DEMO + leitos legados; cada card tem cor de severidade (NENHUM sem borda — bug corrigido); DEMO-001 critical, DEMO-004 normal; contador "críticos" mostra Nº DE PACIENTES críticos (~5), não total de alertas (~53) — bug corrigido, valide; MEWS/NEWS2 visíveis; tooltips (hover) mostram texto clínico; atalhos `g a`/`g d`/`g t` navegam; `?` abre overlay de ajuda.

**F3 — Patient Detail:** clicar num leito → `/patient/{mpi}`; breadcrumb mostra NOME do paciente (não ID); vitais + scores + timeline renderizam; todas as trilhas ativas aparecem; paciente com dados velhos (LEITO legado) mostra os N mais recentes, não tela vazia.

**F4 — Pathway View (o coração):** de Patient → clicar numa trilha → `/patient/{mpi}/pathway/{pp}`; breadcrumb "Paciente → {nome} → Trilha → {nome trilha}"; estado atual, critérios com severidade por banda, recomendações SSC-2021, histórico de transições — tudo numa tela; DEMO-001 sepse deve mostrar critérios reais (PAM 58 → crítico). Jornada Dashboard→Pathway em ≤2 cliques.

**F5 — Alertas:** `/alerts` lista alertas; filtros funcionam; acknowledge/resolve/escalate — **resolve exige enum** (`false_positive`/`true_positive`/`intervention_done`) via as 3 opções da UI (texto livre foi removido — valide que resolve retorna 200, não 422); acknowledge não explode (bug de eager-load foi corrigido — valide 200 com nome do paciente).

**F6 — Admin:** `/admin` — usuário admin entra; **crie um usuário não-admin** (role `medico` via a UI, que agora aceita role) e prove que ele é REDIRECIONADO ao tentar `/admin` (guard cliente corrigido). Lista de usuários carrega.

**F7 — Tempo real (WebSocket):** com o dashboard aberto, dispare uma mudança no backend (ex: `PUT /patients/MPI-DEMO-001/pathways/{pp}/criteria` ou nova ingestão de vitais via `POST /api/v1/vitals`) e observe se a UI atualiza sem reload (WS `pathway.updated`/`bed_grid.updated`). Se cair para polling, valide que o polling (30s) atualiza. Indicador de conexão (WifiOff) coerente.

**F8 — Features novas do uplift (valide que funcionam de verdade):**
- **Deterioration trend**: `GET /api/v1/patients/MPI-DEMO-001/deterioration-trend` → projeção com slope fisiológico, R², pontos auditáveis, disclaimer.
- **CDS Hooks**: `GET /cds-services` (discovery) e `POST /cds-services/intensicare-pathway-alerts` com `{"hook":"patient-view","context":{"patientId":"MPI-DEMO-001"}}` → card critical de sepse.
- **Auto-avaliação**: ingira um vital com PAM<65 para DEMO-001 via `POST /api/v1/vitals` e confirme que o critério `crit-sep-pam` do enrollment foi avaliado automaticamente (sem PUT manual).

**F9 — Acessibilidade real:** `npx @axe-core/cli http://localhost:3000/login` → 0 violations (corrigido); rode axe também no dashboard autenticado; navegação por teclado (Tab/Enter/Esc) na jornada core.

**Para cada fluxo o agente reporta:** passos executados, screenshots (no scratchpad), erros de console do browser (capture `page.on('console')` e `page.on('pageerror')`), respostas de rede com status ≥400, e veredito PASS/FAIL/DEGRADED.

---

## ═══════ FASE 3 — TRIAGEM + CORREÇÃO (você adjudica, swarm corrige) ═══════

Para cada bug real encontrado nos fluxos:
1. **Você triagem**: reproduzível? é bug de runtime real ou dado/ambiente? severidade (bloqueia jornada clínica = CRITICAL)?
2. **Delegue o fix** a um agente especialista em worktree isolado (≤3 arquivos), com o bug pré-carregado (passos de repro + screenshot/trace). Roteamento: mecânico→Haiku, lógico→Sonnet.
3. **Regra anti-workaround**: corrija a RAIZ, não o sintoma. Sem mascarar, sem `try/except` que engole, sem desabilitar teste.
4. **Gatekeeper diferente re-verifica NO BROWSER** — o bug sumiu na interação real, não só no teste.
5. **Cuidado com defeitos pré-existentes conhecidos** (não introduzidos por você, podem aparecer): cadeia alembic 0002/0016; `ventilacao.yaml` é stub incompleto; wiring de `session-encryption-key` ausente (PHI cai em fallback "—" em DB cifrado); suíte de testes completa tem ~falhas pré-existentes fora do escopo. Decida caso a caso: corrigir se destrava a jornada, documentar se é dívida estrutural.

---

## ═══════ FASE 4 — SÍNTESE + VEREDITO DE RUNTIME (você) ═══════

**Output:** `docs/audit/fullspectrum/E2E_LIVE_REPORT.md` com:
1. **Matriz de fluxos** (F1–F9): PASS/FAIL/DEGRADED + screenshot + observações.
2. **Bugs reais** encontrados: tabela (fluxo, sintoma, causa raiz, fix aplicado + commit, ou "não-corrigível local + razão"), antes/depois.
3. **Console/rede**: erros de browser residuais (mesmo que não-bloqueantes).
4. **Veredito de runtime**: a jornada do intensivista funciona ponta a ponta em Chrome real? SIM / SIM-COM-RESSALVAS / NÃO — com evidência (não intuição).
5. **Diff de PRs**: se corrigiu bugs, abra PR(s) para `main` (branch protection exige review humana de code-owner — deixe pronto, não force merge; o CI required é Lint & Type Check + Security Scan + Frontend — Lint & Build).
6. Atualize a memória do projeto (`fullspectrum-fix-cycle-complete` e crie um `e2e-live-verification` se houver achados duráveis).

---

## ═══════ ANTI-PATTERNS (NÃO REPETIR — custaram tempo nesta sessão) ═══════

- ❌ Orquestrador codando direto — delegue.
- ❌ Trocar branch no checkout principal com agentes ativos — use worktrees.
- ❌ Confiar em self-report — verifique no browser/filesystem.
- ❌ `git stash` num worktree com outros agentes ativos — o stash é global, engole trabalho alheio.
- ❌ "Funciona" baseado em teste verde — a prova é o Chrome.
- ❌ Verificar boot só pelo server `--reload` rodando — faça import fresco.
- ❌ Forçar merge com `--admin` por cima de review humana — é gate legítimo; deixe o PR pronto e pare.
- ❌ Gatekeeper = implementador.
- ❌ Um agente com >3 arquivos ou escopo grande demais.

---

## ═══════ REFERÊNCIAS RÁPIDAS ═══════

- Login: `POST /api/v1/auth/login` form-urlencoded `username=admin&password=admin`
- Seed: `make seed-demo` (5 pacientes MPI-DEMO-*)
- Boot fresco: `PYTHONPATH=src .venv/bin/python -c "from intensicare.main import app"`
- Drift/contratos: `PYTHONPATH=src .venv/bin/python scripts/ci/check_openapi_drift.py`
- Pathways engine gate: `.venv/bin/python scripts/validate_alerts.py --gate B`
- Frontend e2e: `cd frontend-v3 && npx playwright test e2e/smoke.spec.ts` (E2E_BACKEND=1 para os testes que exigem backend)
- Pacientes-chave: DEMO-001 (sepse critical), DEMO-002 (sedação urgent), DEMO-004 (controle normal), LEITO-06 (MEWS 13 — dados legados/stale)
