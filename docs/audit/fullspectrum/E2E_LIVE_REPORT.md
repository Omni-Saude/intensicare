# E2E LIVE REPORT — Verificação End-to-End Ao Vivo em Chrome Real
## IntensiCare — do "passa nos testes" ao "funciona nas mãos do intensivista"

**Data:** 2026-07-13
**Base:** `main` @ `0f98392` (pós-ciclo GO-WITH-ISSUES 79.25)
**Branch de correção:** `fix/e2e-live-runtime` (13 fixes, cada um em worktree isolado, integrados com 13 merges limpos)
**Método:** stack local completa (Postgres/TimescaleDB + Redis + FastAPI + Next.js 16) + Chromium real via Playwright; 9 agentes de fluxo + 13 agentes de fix + 2 gatekeepers independentes (implementador ≠ revisor); toda alegação de "funciona" tem screenshot ou trace de rede/WS; evidências-chave re-verificadas pelo orquestrador.
**Artefatos:** harness + scripts + ~100 screenshots + reports JSON no scratchpad da sessão (`e2e-live/artifacts/{smoke,f1..f9,gk1,gk2,gk2b}/`). Estado da stack em [E2E_HANDOFF.yaml](E2E_HANDOFF.yaml).

---

## 1. VEREDITO DE RUNTIME

# **SIM-COM-RESSALVAS** — a jornada do intensivista funciona ponta a ponta em Chrome real.

**O que foi provado com interação real** (não testes verdes):
- Login → Dashboard → Patient → Pathway → Ação em ≤2 cliques, com dados clínicos reais renderizados em cada tela.
- Sessão sobrevive a F5 e deep-link em aba nova (`/auth/refresh` via cookie HttpOnly) — o fix crítico B-C2 do ciclo anterior está vivo.
- **Auto-avaliação de ponta a ponta**: `POST /vitals` com PAM 52 → motor avalia `crit-sep-pam` em ~206ms síncrono → UI mostra o valor novo — sem nenhum PUT manual. Fecha com prova viva o gap histórico A#1/A-N2.
- **Realtime real**: push WebSocket `bed_grid.updated` em ~585ms e `alert.raised` em ~721ms após ingestão, DOM atualizando sem reload; deep-link conecta o WS após bootstrap de sessão.
- Acessibilidade: axe = 0 violations em `/login` E no dashboard autenticado; jornada core 100% operável por teclado.
- 14 bugs reais de runtime encontrados; **13 corrigidos na raiz e re-verificados no browser por gatekeepers que não os implementaram**; 1 documentado como dívida de contrato.

**As ressalvas** (por que não "SIM" pleno):
1. Os fixes estão em PR aguardando review humana de code-owner (branch protection) — o `main` ainda contém os 14 bugs.
2. Defeitos pré-existentes conhecidos permanecem (fora de escopo, §5): `ventilacao.yaml` stub, `session-encryption-key` não wired, MPI-001 vazando no dashboard, leitos legados sem enrollment, ~18 falhas pré-existentes em `test_alerts.py` (ABAC/field drift) e outras suítes.
3. Validação clínica independente formal continua ausente (bloqueador regulatório já registrado no verdict — não é endereçável por engenharia).

---

## 2. MATRIZ DE FLUXOS (F1–F9)

| Fluxo | Veredito na 1ª passada | Bugs achados | Estado pós-fix (gatekeeper) |
|---|---|---|---|
| F1 Login+Sessão | FAIL (1/9 passos) | BUG-F1-01 logout | FIXED — GK-1 |
| F2 Dashboard | FAIL (3/23) | BUG-F2-01 abas colapsam; erro "[object Object]" | FIXED — GK-1 |
| F3 Patient Detail | PASS (c/ achado) | BUG-F3-01 staleness invisível; BUG-F3-02 erro ilegível | FIXED — GK-1 |
| F4 Pathway View | DEGRADED | BUG-F4-01 severidade contraditória; BUG-F4-03 nome hardcoded; F4-02 banda por critério (dívida) | FIXED — GK-2 (F4-02 documentado) |
| F5 Alertas | DEGRADED | BUG-F5-01 filtros no-op; BUG-F5-02 alerta some sem volta | FIXED — GK-2 |
| F6 Admin+RBAC | FAIL (1/12) | Ausência de UI de criação de usuário | FIXED — GK-2 |
| F7 WebSocket | FAIL | BUG-F7-02/03/04/05 (cadeia de 4 defeitos) | FIXED — GK-2 (+GK2-NEW-01 achado e corrigido) |
| F8 Uplift | PASS | BUG-F8-01 pending sempre 0; window_hours (cosmético, dívida) | FIXED — GK-2 |
| F9 A11y | FAIL | BUG-F9-01 sem h1; BUG-F9-02 tablist sem teclado | FIXED — GK-1 (axe dashboard: 0 violations) |

**Fixes do ciclo anterior re-validados em browser real (nenhuma regressão):** sessão pós-F5/deep-link (B-C2), breadcrumb com nome (B-M3 nos 2 níveis), contador "5 críticos" = pacientes críticos (DASH-2), severity nunca-null com LEITO-04/06 critical (DASH-1), fallback "N mais recentes" (LEITO-06 não-vazio), resolve por enum retorna 200, acknowledge 200 com nome (eager-load), PHI descriptografada nas listas, guard client-side + 403 server-side de /admin, atalhos `g d`/`g a`/`g t` + `?`, tooltips clínicos, axe /login = 0, CDS Hooks conforme spec 2.0, deterioration-trend com regressão re-calculada independentemente (match exato slope/R²).

---

## 3. BUGS REAIS ENCONTRADOS E CORRIGIDOS (14)

| # | Bug (sintoma → causa raiz) | Severidade | Fix (branch, commit) | Re-verificação |
|---|---|---|---|---|
| 1 | **BUG-F1-01** Logout não navega; grid com PHI fica na tela indefinidamente (sessão servidor morta, cliente não navega nem limpa SWR) → `lib/auth.tsx` sem navegação | ALTA (PHI em terminal compartilhado) | `fix/e2e-logout-nav` `f07f08c` — `window.location.assign('/login')` fail-closed (destrói realm JS + cache SWR) | GK-1 FIXED |
| 2 | **BUG-F2-01** Filtrar unidade faz as outras abas sumirem → backend devolvia `unit_counts` filtrado; front deriva abas dele | MAIOR | `fix/e2e-unit-counts` `22cb725` — agregação GROUP BY independente do filtro | GK-1 FIXED |
| 3 | **BUG-F3-01** Vitais de 17 dias renderizados como atuais (só HH:MM, sem data/aviso) | ALTA (risco clínico) | `fix/e2e-staleness-indicator` `eb4bb54` — banner `role=alert` + data nos tiles + `lib/vitals-staleness.ts` compartilhado com bed-card | GK-1 FIXED |
| 4 | **BUG-F3-02/F2-02** 422 Pydantic (array) renderiza "[object Object],[object Object]" → `lib/api.ts` usa `body.detail` cru | BAIXA | `fix/e2e-api-error-msg` `4060bad` — `normalizeApiDetail()` nas 2 ocorrências | GK-1 FIXED ("username: Field required; password: …") |
| 5 | **BUG-F4-01** Badge "Crítico" contradiz backend "urgent" na mesma tela → página recalculava severidade por notMetRatio | MAIOR (contradição clínica) | `fix/e2e-pathway-severity` `39ea960` — usa severity do backend (mesma chave SWR do paciente); ratio vira fallback documentado | GK-2 FIXED |
| 6 | **BUG-F4-03** Header "Paciente: Paciente MPI-DEMO-002" → `patientName` hardcoded | BAIXA | idem `39ea960` — nome real da mesma fonte do breadcrumb | GK-2 FIXED |
| 7 | **BUG-F9-01** Dashboard sem `<h1>` (única página; axe page-has-heading-one) | MODERADA | `fix/e2e-a11y-dashboard` `52a76c7` — `<h1 class="sr-only">Dashboard</h1>` | GK-1 FIXED (axe 0 violations) |
| 8 | **BUG-F9-02** Tablist de unidades sem handler de setas — 3 de 4 unidades inalcançáveis por teclado (WCAG 2.1.1) | ALTA (a11y) | idem `52a76c7` — padrão APG completo (setas/Home/End, ativação manual p/ não disparar N fetches) | GK-1 FIXED |
| 9 | **F6-GAP** Painel admin sem UI de criação de usuário (backend suportava; UI nunca existiu) | MAIOR (bloqueia onboarding) | `fix/e2e-admin-create-ui` `96771a6` — dialog acessível, roles de `CLINICAL_ROLES`, acoplamento is_admin×role no cliente (mitiga C-N1) | GK-2 FIXED (criou `e2e-enfermeiro-live` via UI) |
| 10 | **BUG-F8-01** Critérios nunca avaliados contados como "não atendidos"; `pending` sempre 0; card CDS "15 de 15 avaliados" enganoso | ALTA (confiança clínica) | `fix/e2e-criteria-pending` `fb492a6` — `evaluated_at` define met/not_met vs pending; textos verdadeiros; PROVA de que summary não alimenta transição/severidade | GK-2 FIXED ("3 de 15 avaliados", 12 pendentes, UI==API) |
| 11 | **BUG-F5-01** Filtros de alertas no-op silencioso → front enviava params que o backend não declara | MAIOR | `fix/e2e-alert-filters-backend` `d0b120b` (status enum + severity + contrato + drift 87/87) e `fix/e2e-alert-filters-frontend` `756adb9` (UI mapeia status, opção "Escalados" nova) | GK-2 FIXED (563/571/572 revisitáveis por filtro) |
| 12 | **BUG-F5-02** Alerta processado some da UI sem caminho de volta (perda de rastro de auditoria) | MAIOR | idem #11 — "Todos status"/filtros por estado devolvem visibilidade | GK-2 FIXED |
| 13 | **BUG-F7** (cadeia realtime): backend só publicava 1 evento em todo o repo (docstring prometia 5 canais); mismatch `pp_id`≠`patient_pathway_id`; race de token em deep-link (WS nunca tentava); watchdog de 5s órfão sobrescrevia o status do socket vivo | CRÍTICA (refuta "FUNCTIONAL" da re-auditoria D) | `fix/e2e-ws-publishers` `9716838` (publishers `bed_grid.updated`+`alert.raised`, não-fatais) + `fix/e2e-ws-client` `7c0007c` (campo alinhado; `onTokenAvailable`→conecta pós-bootstrap; `clearTimeout` no onclose) | GK-2 FIXED (push 585/721ms, DOM sem reload, deep-link conecta, indicador honesto) |
| 14 | **GK2-NEW-01** (achado pelo gatekeeper) "há X min" congelado: `last_vital_at` vinha de `synced_at`, que a ingestão nunca atualiza — card recém-atualizado rotulado "há 1.1h" | ALTA (indicador de frescor mente) | `fix/e2e-last-vital-at` `eb7280e` — deriva do `recorded_at` mais novo (mesma fonte de `vitals`); fallback synced_at; LEITO-06 preservado | API provada pelo orquestrador; browser: ver §3.1 |

### 3.1 Verificação final GK2-NEW-01 (browser — GK-2b)
**FIXED.** Baseline "há 10 min" → `POST /vitals` (201) → frame `bed_grid.updated` em **T+487ms** → rótulo do card "há 0 min" em **T+490ms**, com **zero reload** (0 eventos `load`, 0 navegações no main frame; detector armado antes do POST). Staleness legítimo preservado: LEITO-06 segue "há 16 dias" na cor `--severity-critical` exata (probe DOM). Varredura dos 12 pacientes: `last_vital_at == recorded_at` do vital mais novo em todos; MPI-001 (sem vitais) usa o fallback `synced_at` documentado. Screenshots em `artifacts/gk2b/01..03`.

**Não corrigidos nesta sessão (dívida documentada, decisão de triagem):**
- **BUG-F4-02** — banda de severidade por critério não exposta (schema/contrato + motor + UI; estoura escopo ≤3 arquivos e o gate de drift; não é regressão). Nota: `criteria-row.tsx` chama `SeverityIcon` com `severity={null}` hardcoded.
- **window_hours** do deterioration-trend reporta a janela de lookback (12h), não o span real dos dados (5.9h) — cosmético; sugerido renomear para `lookback_window_hours`.
- **alert.updated / vitals.updated** — canais WS documentados sem publisher; ack/resolve/escalate têm 3 call-sites sem ponto de convergência (exigiria refactor da camada de rotas).
- Nota UX menor: campo "Justificativa" (note) do resolve não é persistido no backend.

---

## 4. CONSOLE/REDE — ERROS RESIDUAIS (pós-fix, sessões dos gatekeepers)

- **pageErrors: 0** em todas as sessões (nenhuma exceção JS não tratada).
- Esperados/benignos (documentados): `401 POST /auth/refresh` em páginas sem sessão (bootstrap by-design); 1ª tentativa de WS falha e reconecta em ~1s (double-mount do React StrictMode em dev — estado estável = conectado).
- **Hydration mismatch em `/login`** (2× console error): pré-existente, possivelmente ligado ao nonce CSP por request; não bloqueou nenhum fluxo. Não corrigido (fora de triagem — sem impacto funcional observado).
- Corrida de hidratação do form de login sob carga (fill pré-hidratação → 422): artefato de automação/dev-server; usuário real não digita em <300ms. Mitigado no harness; o sintoma de UI associado (mensagem ilegível) foi corrigido (#4).

---

## 5. DEFEITOS PRÉ-EXISTENTES CONFIRMADOS (não são regressões; fora de escopo)

Encontrados pelos fluxos e deliberadamente NÃO tocados (rastreados nas re-auditorias):
- Cadeia alembic 0002 duplicada / 0016 VARCHAR(16) — quebra `upgrade head` from-scratch (dev DB já em 0040).
- `ventilacao.yaml` stub — description vazia; repr interno `graded(...)` vaza na API/UI.
- `session-encryption-key` não wired — PHI cai em fallback (o seed emitiu o warning de schema legacy nesta sessão).
- "Paciente Teste MPI-001" vaza no dashboard clínico (DATA-2); leitos legados LEITO-01..06 sem enrollment (DATA-1).
- Logout não limpa cookies HttpOnly (AUTH-4 residual — mitigado na prática pelo fix #1; sessão servidor é invalidada).
- Suíte de testes: 18 falhas pré-existentes em `test_alerts.py` (Users sem role pós-RBAC + assert `alerts` vs campo `items`), 7 em `test_vitals.py`/`test_alert_engine.py`, ~8 em `test_domain_trilhas_engine.py` (motor depreciado) — conjuntos idênticos antes/depois dos fixes, verificados em worktree baseline.
- `POST /admin/users` aceita is_admin×role incoerente (C-N1) — agora mitigado no cliente pela UI nova (#9), backend permanece.

---

## 6. OPERAÇÃO (para a memória institucional)

- **Armadilhas pré-mapeadas que se confirmaram**: servidores stale nas portas 8000/3000 (incluindo `uvicorn --reload` de sessão anterior — Regra 6 aplicada: kill + boot fresco); `make seed-demo` obrigatório (pp_ids novos 31/32/33 — docs antigos citavam 22); JWT só em memória (login real pela UI no harness).
- **Regra 3 rendeu**: a re-auditoria D dizia WS "FUNCTIONAL ~130ms" — a verificação ao vivo mostrou canal sem publishers; a premissa "UI de criação aceita role" era só backend; um "19º teste falhando" era contenção de DB entre agentes concorrentes, não regressão (isolado e provado).
- **Gatekeeper ≠ implementador rendeu**: GK-2 achou GK2-NEW-01 (last_vital_at congelado) ao verificar o fix do realtime — 14º bug, corrigido no mesmo ciclo.
- **Mutações de dado desta sessão** (dev DB): alertas 563→resolved/571→escalated/572→acknowledged/570→acknowledged (MPI-DEMO-003); vitais extras em DEMO-001/004/005; usuários criados: `e2e-medico-live` (API, id 10) e `e2e-enfermeiro-live` (via UI nova). Mantidos como evidência; remover se incomodarem.
- Harness reutilizável (login hydration-safe, captura de console/rede/WS frames) no scratchpad — replicável para ciclos futuros.

## 7. CONCLUSÃO E PRÓXIMOS PASSOS

1. **PR** `fix/e2e-live-runtime` → `main` aberto e pronto; branch protection exige review humana de code-owner (gate legítimo — não forçado). CI required: Lint & Type Check + Security Scan + Frontend Lint & Build (tsc limpo, drift 87/87, ruff/mypy nos arquivos tocados).
2. Dívidas priorizadas para o próximo ciclo: banda por critério (F4-02), `alert.updated`/`vitals.updated` publishers, hydration mismatch do /login, persistir `note` do resolve.
3. Pendências de dono humano (inalteradas): sign-off clínico formal; review dos PRs; roadmap preditivo/CDC.
