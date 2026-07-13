# DIM D — Auditoria de Integração Frontend ↔ Backend

**Data:** 2026-07-12 · **Auditor:** agente independente (somente leitura)
**Frontend:** `frontend-v3` (Next.js, dev em `localhost:3000`) · **Backend:** FastAPI em `localhost:8000`
**Baseline re-verificada:** `docs/audit/handoff-parreira/WIRING_GAPS.md` (2026-07-09, autodeclarava 13/14 OK + 1 MAJOR postergado)

> Metodologia: todos os endpoints batidos com `curl` autenticado (`admin/admin`), tipos TS extraídos de
> `frontend-v3/lib/api.ts` (403 linhas), comparação campo-a-campo com o JSON real. WebSocket testado ao vivo
> com `python websockets` (script em scratchpad). POSTs de mutação de alertas NÃO foram executados
> (auditoria read-only) — shape auditado por código (`src/intensicare/api/v1/alerts.py`).

---

## 1. SHAPE MATCHING — Matriz dos 14 endpoints

Classificação: **FULL_MATCH** (todos os campos esperados presentes com tipo certo) /
**PARTIAL** (campo esperado ausente/null onde o tipo TS não permite) /
**MISMATCH** (tipo/nome errado com impacto de runtime) / **BROKEN** (500/404 estrutural).

| # | Função TS (`lib/api.ts`) | Endpoint | HTTP | Shape | Severidade |
|---|---|---|---|---|---|
| 1 | `login()` | `POST /api/v1/auth/login` (form-urlencoded) | 200 | **MISMATCH** | **MAJOR** |
| 2 | `logout()` | (local apenas — limpa token em memória; não chama `POST /auth/logout` do backend) | n/a | **PARTIAL** | MINOR |
| 3 | `fetchDashboard()` | `GET /api/v1/dashboard` | 200 | **PARTIAL** | **MAJOR** |
| 4 | `fetchPatientDetail()` | `GET /api/v1/patients/{mpi_id}` | 200 | FULL_MATCH | — |
| 5 | `fetchPatientPathways()` | `GET /api/v1/patients/{mpi_id}/pathways?status=` | 200 | FULL_MATCH¹ | — |
| 6 | `fetchPathwayProgress()` | `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress` | 404² | FULL_MATCH (por código)² | — |
| 7 | `fetchPathways()` | `GET /api/v1/pathways?active_only=` | 200 | FULL_MATCH | — |
| 8 | `fetchPathway()` | `GET /api/v1/pathways/{id}` | 200 | FULL_MATCH | — |
| 9 | `fetchAlerts()` | `GET /api/v1/alerts` | 200 | FULL_MATCH | — |
| 10 | `acknowledgeAlert()` | `POST /api/v1/alerts/{id}/acknowledge` | não testado (mutação) | FULL_MATCH (por código: `AlertResponse` = shape do GET) | — |
| 11 | `escalateAlert()` | `POST /api/v1/alerts/{id}/escalate` | não testado (mutação) | FULL_MATCH (por código) | — |
| 12 | `resolveAlert()` | `POST /api/v1/alerts/{id}/resolve` | não testado (mutação) | FULL_MATCH (por código; body `{resolution}` aceito) | — |
| 13 | `fetchUsers()` | `GET /api/v1/admin/users` | 200 | FULL_MATCH³ | — |
| 14 | `fetchHealth()` | `GET /api/v1/health` | 200 | FULL_MATCH (extras benignos) | — |

**Contagem: 10 FULL_MATCH · 3 PARTIAL⁴ · 1 MISMATCH · 0 BROKEN** (+ WebSocket BROKEN, seção 3 — não é endpoint REST da matriz).

### Evidência célula-a-célula

**#1 login — MISMATCH (MAJOR).** TS `LoginResponse.user: UserInfo {id: string, name, email, role, is_admin}`.
Resposta real (curl 200):
```json
"user": {"id": 2, "username": "admin", "email": "admin@intensicare.io",
         "display_name": "Administrador", "is_admin": true, "is_active": true}
```
- `user.name` → **AUSENTE** (backend manda `display_name`) → `auth.tsx` grava `user.name = undefined`; o AppShell renderiza `{user.name}` em branco após login.
- `user.role` → **AUSENTE** (backend `UserResponse` em `api/v1/auth.py` não inclui `role`) → sidebar mostra role vazio; qualquer futura lógica `user.role` quebra na sessão pós-login (só funciona após reload, quando `auth.tsx` re-decodifica o JWT, que TEM `role`).
- `user.id`: número (`2`) vs TS `string` — tolerado em runtime, mas viola o contrato.
- Extras não tipados: `refresh_token` (ignorado pelo frontend — nenhum fluxo de refresh existe no cliente), `is_active`, cookies `token`/`access_token` setados pelo backend (é isso que satisfaz o middleware).

**#2 logout — PARTIAL (MINOR).** `logout()` do frontend só zera o token em memória. Não chama `POST /auth/logout` (blacklist Redis) e **não limpa os cookies `token`/`access_token`** (HttpOnly, só o backend poderia). Consequência: após "Sair", o middleware ainda vê cookie válido por até 30 min — rotas server-side continuam acessíveis; token não é blacklistado.

**#3 dashboard — PARTIAL (MAJOR).** Top-level bate: `{patients, total: 7, critical_count: 2, unit_counts: {"UTI-ADULTO": 6, "UTI-CORONARIANA": 1}}`.
Item por item vs `PatientBedSummary`:
- `severity: SeverityLevel` no TS é **obrigatório e não-nulo**; o backend retorna `"severity": null` em 5 de 7 pacientes. Em `bed-card.tsx` linha 57, `SEVERITY_BORDER[severity]` → `undefined` → cartão sem borda de severidade. Pior: **LEITO-06 tem MEWS 13 / NEWS2 19 com `severity: null`** — paciente gravíssimo renderiza sem cor de severidade (dissonância clínica).
- `mews`/`news2`/`last_vital_at`/`vitals` opcionais — OK (null aceito).
- Extras não tipados (benignos): `news2_risk`, `mews_trend`, `news2_trend`, `active_alerts_count`, `highest_alert_encoding`, `vitals.respiratory_rate/temperature/recorded_at`.
- `active_pathways`: `[]` em TODOS os pacientes (ver seção 4).

**#4 patient detail — FULL_MATCH.** `{"mpi_id":"LEITO-01","bed":"LEITO-01","patient_name":"Maria Silva","unit":"UTI-ADULTO","vitals":[],"scores":[],"active_pathways_count":0}` — todos os campos do TS presentes com tipo certo. `vitals`/`scores` vazios é problema de dado, não de shape.

**#5 patient pathways — FULL_MATCH¹.** `{"items":[],"total":0}` (200) para todos os leitos e todos os status (`active|completed|archived` varridos nos 8 leitos + MPI-001: **zero enrolments no banco**). Envelope bate; shape do item validado estaticamente: `PatientPathwaySchema` (`schemas/pathways.py:35`) cobre todos os campos do TS `PatientPathway` (extras `encounter_id/bed_id/unit` benignos). ¹Item nunca observado ao vivo por ausência de dados.

**#6 progress — FULL_MATCH por código².** Sem enrolment não há `pp_id` real; `GET .../pathways/999/progress` → 404 `{"detail":"Inscrição de pathway 999 não encontrada..."}` (comportamento correto). `PathwayProgressSchema` (`schemas/pathways.py:69`) espelha o TS `PathwayProgress` campo a campo (`patient_pathway_id, mpi_id, pathway_name, current_state, criteria_summary{total,met,not_met,pending}, criteria[], state_history[], trend, last_evaluated_at, recommendation`). ²Não verificado ao vivo.

**#7/#8 pathways catálogo — FULL_MATCH.** 12 pathways; keys do item: `active, created_at, criteria, description, id, name, slug, states, updated_at`; state: `description, id, is_terminal, name, order`; criteria: `alert_threshold, category, description, evaluated_at, id, met, name, normal_range, unit, value` — 1:1 com `Pathway/PathwayState/PathwayCriteria` do TS.

**#9 alerts — FULL_MATCH.** `{"items":[...], "total": 2}`; keys do item = exatamente os 13 campos de `AlertInfo` (`acknowledged_at, created_at, id, message, mpi_id, pathway_name, patient_name, resolution, resolved_at, resolved_by, severity, title, type`).

**#13 admin/users — FULL_MATCH³.** 200 com `{items:[{id:"2" (string ✓), name, email, role, is_admin, + extras username/display_name/is_active/created_at}], total:4}`. ³Nota: aqui `id` É string e `name`/`role` existem — o backend do admin usa um serializer diferente do login, evidenciando a inconsistência do #1.

---

## 2. FLUXO DE AUTENTICAÇÃO

**2.1 Login shape** — ver #1 acima: `access_token` ✓, `token_type: "bearer"` ✓, `user` **incompleto** (`name` e `role` ausentes; `id` numérico). **Reprovado no campo-a-campo.**

**2.2 JWT decodificado:**
```json
{"sub":"admin","user_id":2,"is_admin":true,"role":"readonly","name":"Administrador",
 "email":"admin@intensicare.io","exp":1783876548,"type":"access","jti":"..."}
```
`sub` ✓ `is_admin` ✓ `role` ✓ `exp` ✓ (+ name/email/user_id/jti).
**`role:"readonly"` no admin — impacto no frontend: cosmético, não funcional.** Evidência: grep completo em `app/` e `components/` — `user.role` é usado APENAS para exibição (`app-shell.tsx:145` mostra "readonly" na sidebar; `user-manager.tsx:332` idem na tabela). Nenhum guard usa `role`; `is_admin` também não é usado em guard algum (só como badge em `user-manager.tsx:336`). No backend, `require_admin` (`auth/dependencies.py:92-96`) checa `is_admin`, e `_has_role()` dá bypass a admin — por isso `GET /admin/users` retorna 200 mesmo com `role:"readonly"`. **Achado real: dado inconsistente (admin com role "readonly", 3 de 4 usuários "readonly") + UX enganosa (sidebar do admin exibe "readonly").**

**2.3 middleware.ts** — funciona:
- `GET /` sem cookie → **307 → /login** ✓ · `GET /patient/LEITO-01` sem cookie → **307 → /login** ✓
- `GET /` com `Cookie: token=<jwt>` → **200** ✓ · `GET /login` sem cookie → **200** ✓
- Ressalva: o middleware só testa **presença** do cookie, não validade/expiração (cookie lixo passa; a página então falha no fetch).
- Nota de latência: nas primeiras tentativas o dev server levou >20 s (compilação sob demanda); depois, 75 ms.

**2.4 Token inválido/expirado → 401?** **Parcialmente NÃO:**
- Sem token → `401 {"detail":"Not authenticated"}` ✓
- JWT bem-formado expirado/assinatura inválida → `401` ✓
- **Bearer malformado (`invalid.token.here`) → `500 Internal Server Error`** (reproduzido 2×). Causa raiz: `is_token_blacklisted()` em `auth/jwt.py:45` chama `jwt.get_unverified_claims(token)` fora do try/except — `JWTError` não tratado. **Impacto no frontend:** `request<T>()` (`api.ts:245-252`) só limpa token + redireciona `/login` em **401**; um 500 vira `ApiError(500, "Internal Server Error")` → usuário fica preso numa tela de erro em vez de re-logar.
- Tratamento 401 no frontend: `clearToken()` + `window.location.href='/login'` + throw `ApiError(401,'Não autorizado')` — correto, porém **não apaga os cookies** (HttpOnly), então o middleware deixa a navegação passar e cada página refaz o ciclo fetch→401→redirect.

**2.5 Admin guard no frontend: NÃO EXISTE.** `app/admin/page.tsx` não verifica `is_admin` nem `role` (é só UI de tabs); `middleware.ts` não distingue `/admin`; o item "Admin" do menu (`app-shell.tsx:26`) aparece para **todos** os usuários autenticados. Um não-admin (ex.: `medico1`, `is_admin:false`, visto em `/admin/users`) navega até `/admin` e vê a página inteira; a proteção real é só o 403 do backend nos fetches (auditado por código — não testei login de não-admin para não disparar lockout de conta de terceiros). **Defesa em profundidade ausente no cliente.**

**2.6 Lockout observado:** primeira tentativa de login da auditoria retornou `429 "Account temporarily locked..."` (resíduo de tentativas anteriores; chave Redis `lockout:failed:admin` expirou em ~15 min e o login passou). O frontend `login()` exibe o `detail` do 429 corretamente.

---

## 3. WEBSOCKET — **BROKEN (protocolo E rota) — pior que a baseline**

Teste ao vivo (script python/websockets no scratchpad):

| Teste | Resultado |
|---|---|
| `ws://localhost:8000/api/v1/ws?token=<jwt>` | **CONECTA** ✓ |
| Enviar `{"action":"subscribe","channel":"bed_grid.updated","token":...}` | aceito (sem ack — servidor não confirma) |
| Enviar `{"type":"auth","token":...}` (protocolo do frontend) | `{"type":"error","message":"Unknown action. Use: subscribe, unsubscribe, pong."}` |
| `ws://localhost:8000/api/v1/ws` sem token | rejeitado HTTP 403 ✓ |
| `ws://localhost:8000/ws` (destino do rewrite do Next) | **HTTP 403 — rota não existe no backend** |
| `ws://localhost:3000/ws` (o que o frontend realmente abre) | **timeout no handshake** via proxy dev |

**Quatro camadas de incompatibilidade** entre `frontend-v3/lib/websocket.ts` e `src/intensicare/api/v1/ws.py`:
1. **URL errada:** frontend abre `//host/ws` (linha 60) e `next.config.ts` reescreve `/ws → ${API_URL}/ws`; o backend só expõe **`/api/v1/ws`** (`ws.py:242`). 403/timeout garantido.
2. **Auth errada:** backend exige `?token=` na query (`ws.py:245`); frontend nunca anexa token à URL — espera um handshake `auth_required → {type:"auth"} → subscribed` que o backend não implementa.
3. **Protocolo de mensagens:** frontend fala `{type: auth|ping|...}`; backend fala `{action: subscribe|unsubscribe|pong, token}` **com JWT obrigatório em cada mensagem**. O mismatch `{type:"auth"}` vs `{action:"subscribe"}` da baseline **persiste e foi confirmado ao vivo** (erro "Unknown action").
4. **Envelope de eventos:** backend publica `{"type":"<canal>","data":...,"payload":...}`; frontend só processa `msg.type === 'event'` com `msg.channel` — nunca entregaria eventos mesmo conectado. Além disso, frontend assina `pathway.updated`/`pathway.state_changed`, canais que o backend **não publica** (publica `alert.raised/alert.updated/bed_grid.updated/presence.updated/vitals.updated`).

**Fallback de polling: FUNCIONAL (é o que salva o produto).** O `WS_TIMEOUT` de 5 s (`websocket.ts:63,192-199`) dispara `setStatus('fallback')` + `startAllPolling()`; cada assinatura re-chama `mutate()` do SWR a cada 30 s (`fallbackInterval: 30_000` no dashboard `app/page.tsx:22-23`, alerts, patient detail com 60 s para alertas). A página de alertas ainda tem `refreshInterval: 30_000` nativo do SWR. O indicador do topo mostra WifiOff/"Modo polling" — honesto. **Na prática, todo usuário vive permanentemente em modo polling; "tempo real" não existe.**

---

## 4. CONSISTÊNCIA DE DADOS

- **Dashboard:** 7 pacientes (`total:7` = len(patients) ✓): LEITO-01..06 + MPI-001 ("Paciente Teste MPI-001" — **paciente de teste vazando para a UI clínica**). Severidades: `critical` (LEITO-02), `urgent` (LEITO-03), **`null` ×5** — enquanto `critical_count:2` (bate com os alertas critical=1 + contagem interna). Dissonância grave: LEITO-04 (MEWS 9/NEWS2 17) e LEITO-06 (MEWS 13/NEWS2 19) com `severity: null` → renderizam como leitos "sem severidade". Vitals congelados em `2026-06-26T15:00` (16 dias stale, confirmado pelo `/health`: `minutes_stale: 23095`).
- **Trilhas por paciente:** `GET /patients/{id}/pathways` → `{"items":[],"total":0}` para TODOS os leitos em TODOS os status. O catálogo tem 12 pathways ativos, mas **zero enrolments** — contradiz a nota do recon ("enrolments existem"). Consequência em cascata: `active_pathways: []` no dashboard (sem chips de trilha nos cartões), `active_pathways_count: 0` no detalhe, e o **Pathway View (`/patient/{id}/pathway/{pp_id}`) é código morto navegacional** — não há link possível até ele; acessado direto daria 404 tratado. `progress` não pode retornar criteria populados nem vazios: não há inscrição alguma. **Dissonância produto-dado: a feature central ("pathway-centric rebuild") não tem um único dado real para exibir.**
- **Alertas:** `GET /alerts` → 2 itens (MEWS 7 crítico LEITO-02; AKI Stage 2 urgente LEITO-03), `total:2`, criados 2026-07-10, nunca acknowledged. Shape 100% compatível com o que a AlertTable/`AlertInfo` espera (inclui `patient_name`/`mpi_id` para exibição). Consistente com `critical_count` e `active_alerts_count`/`highest_alert_encoding` do dashboard ✓.

---

## 5. TRATAMENTO DE ERROS

**lib/api.ts (`request<T>`, linhas 229-271):** 401 → clearToken + redirect `/login` + throw; demais não-2xx → `throw new ApiError(status, body.detail || statusText)` (classe tipada com `status` e `detail`, mensagem via `detail` do FastAPI); 204 → `undefined`. Sem retry, sem tratamento especial para 500 (aceitável) — mas ver 2.4: o 500-em-vez-de-401 do backend furando o redirect é a combinação ruim.

**Páginas core (6/6 têm error state — nenhuma tela branca):**
| Página | Error state |
|---|---|
| `/` dashboard | `BedGrid` recebe `error` + `onRetry`; renderiza "Erro ao carregar dashboard" + `error.message` + botão "Tentar novamente" (`bed-grid.tsx:59-102`) ✓ |
| `/alerts` | toast global de erro + `error.message` na tabela + estado empty separado (`alerts/page.tsx:147-166`) ✓ |
| `/patient/[mpi_id]` | erro full-page para o paciente (linha 116) + erros por seção via `getErrorMessage` ✓ |
| `/patient/.../pathway/[pp_id]` | `if (error && !progress)` → mensagem com `getErrorMessage(error)` (linhas 118-126) ✓ |
| `/pathways` | `pathway-grid.tsx:167-175`: mensagem de erro + empty state ✓ |
| `/admin` | `user-manager.tsx:113-139`: bloco de erro com `(error as Error).message` ✓ |
| `/login` | exibe `err.message` do `ApiError` (inclui detail de 401/429 do backend) ✓ |

**Qualidade das mensagens:** boas — o `detail` do backend (frequentemente já em pt-BR, ex. o 404 do progress) chega ao usuário. Lacunas: (a) 401 lança `'Não autorizado'` mas o redirect imediato torna a mensagem invisível — aceitável; (b) o 500 de token malformado mostra "Internal Server Error" cru; (c) nenhuma página distingue 403 (relevante para não-admins em `/admin`).

---

## 6. SCORING — **72/100**

Base 100; cada dedução mapeada a um achado desta auditoria:

| Δ | Achado | Ref |
|---|---|---|
| −10 | **WS-1 (MAJOR):** WebSocket totalmente quebrado — rota, auth, protocolo e envelope incompatíveis (mismatch da baseline confirmado + 3 camadas extras não reportadas). Só não é −20 porque o fallback de polling é robusto e o indicador de status é honesto | §3 |
| −7 | **AUTH-1 (MAJOR):** `LoginResponse.user` sem `name`/`role` (e `id` number) — contrato de login violado; UI de usuário fica em branco na sessão pós-login | §1#1, §2.1 |
| −6 | **DASH-1 (MAJOR):** `severity: null` em 5/7 pacientes contra tipo TS não-nulo; pacientes MEWS 13 renderizam sem severidade (risco clínico de leitura) | §1#3, §4 |
| −5 | **AUTH-2 (MAJOR):** backend 500 (não 401) para Bearer malformado (`jwt.py:45` fora do try) neutraliza o auto-redirect do frontend | §2.4 |
| −4 | **AUTH-3 (MAJOR):** nenhum admin guard no cliente — `/admin` acessível/visível a qualquer autenticado; proteção só no backend | §2.5 |
| −3 | **DATA-1:** zero enrolments — Pathway View/progress inalcançáveis; feature central sem dado (dissonância produto-dado; parcialmente ambiente) | §4 |
| −2 | **AUTH-4:** logout não invalida token (não chama `/auth/logout`) nem cookies HttpOnly — sessão residual ≤30 min no middleware | §1#2 |
| −1 | **DATA-2:** paciente de teste `MPI-001` no dashboard clínico; dado de usuários inconsistente (admin `role:"readonly"`) | §4, §2.2 |

Pontos fortes que seguram a nota: 10/14 endpoints FULL_MATCH verificados ao vivo; middleware de rota correto; `ApiError` tipado com `detail` do backend propagado; 6/6 páginas com error/empty/loading states e retry; fallback de polling que de fato mantém o produto funcional sem WS.

**Veredito vs baseline:** o self-report "13/14 OK, 1 MAJOR postergado" é **otimista**. O MAJOR do WebSocket é maior do que descrito (4 camadas, não 1), e existem 3 MAJORs não reportados (login user shape, severity null, 500-em-vez-de-401) + ausência de admin guard.
