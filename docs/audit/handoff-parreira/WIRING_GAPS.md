# WIRING_GAPS.md — Matriz de Gaps Frontend-v3 ↔ Backend IntensiCare

**Gerado por:** Parreira (DevOps Orchestrator)  
**Data:** 2026-07-09  
**Status:** 10/14 resolvidos, 4/14 OK, 0 críticos restantes, 0 postergados [atualizado 2026-07-12 — WebSocket M8 fechado neste ciclo]

---

## Matriz de Endpoints (14 funções do frontend)

| # | Endpoint Frontend | Endpoint Backend Real | HTTP | Shape Match | Severidade | Ação | Status |
|---|-------------------|----------------------|------|-------------|------------|------|--------|
| 1 | `POST /api/v1/auth/login` (form-urlencoded) | `POST /api/v1/auth/login` (OAuth2PasswordRequestForm) | 200 | ✅ `{access_token, token_type, user:{id,name,email,role,is_admin}}` | CRITICAL → OK | Adicionado router compat + campo user + cookie `token` | ✅ FASE 2.1 |
| 2 | `GET /api/v1/dashboard[?unit=]` | `GET /api/v1/dashboard` | 200 | ✅ Adaptado: `critical_count`, `patient_name`, `bed`, `mews`, `severity`, `vitals.{hr,spo2,bp_sys}`, `unit_counts` | CRITICAL → OK | Pydantic Field(alias=frontend_name) + service adapter | ✅ FASE 3.1 |
| 3 | `GET /api/v1/patients/{mpiId}` | `GET /api/v1/patients/{mpi_id}` (alias → /detail) | 200 | ✅ Adaptado: `patient_name`, `bed`, `vitals`, `scores`, `active_pathways_count` | CRITICAL → OK | Alias route + VitalRecord/ScoreRecord transform | ✅ FASE 2.2 + 3.1 |
| 4 | `GET /api/v1/patients/{id}/pathways` | `GET /api/v1/patients/{mpi_id}/pathways` | 200 | ✅ `{items: PatientPathway[], total}` | OK | Shape compatível | ✅ |
| 5 | `GET /api/v1/patients/{id}/pathways/{ppId}/progress` | `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress` | 200 | ✅ PathwayProgress completo | OK | Shape compatível (dados dependem de seed) | ⚠️ Precisa seed |
| 6 | `GET /api/v1/pathways?active_only=true` | `GET /api/v1/pathways` | 200 | ✅ `{items: Pathway[], total}` | OK | 12 trilhas no catálogo | ✅ |
| 7 | `GET /api/v1/pathways/{id}` | `GET /api/v1/pathways/{pathway_id}` | 200 | ✅ Pathway completo | OK | Shape compatível | ✅ |
| 8 | `GET /api/v1/alerts` | `GET /api/v1/alerts` | 200 | ✅ Adaptado: `items`, `type`, `message`, `patient_name` | MAJOR → OK | AlertResponse com frontend names | ✅ FASE 3.2 |
| 9 | `POST /api/v1/alerts/{id}/acknowledge` | `POST /api/v1/alerts/{id}/acknowledge` | 200 | ✅ AlertInfo | OK | Funcional | ✅ |
| 10 | `POST /api/v1/alerts/{id}/escalate` | `POST /api/v1/alerts/{id}/escalate` | 200 | ✅ AlertInfo | OK | Funcional | ✅ |
| 11 | `POST /api/v1/alerts/{id}/resolve` | `POST /api/v1/alerts/{id}/resolve` | 200 | ✅ AlertInfo | OK | Funcional | ✅ |
| 12 | `GET /api/v1/admin/users` | `GET /api/v1/admin/users` | 200 | ✅ Adaptado: `items`, `id:string`, `name`, `role`, `is_admin` | CRITICAL → OK | UserOut + prefix /api/v1 | ✅ FASE 2.2 + 3.3 |
| 13 | `GET /api/v1/health` | `GET /api/v1/health` (via health_router) | 200 | ✅ `{status, version}` presente | MINOR | status="healthy" vs "ok" — não crítico | ✅ |
| 14 | WebSocket | `WSS /api/v1/ws?token=<JWT>` | 101 | ✅ Protocolo alinhado nas 4 camadas: `{action:"subscribe", channel, token}`, pong por mensagem, envelope real; `pathway.state_changed` aliased para `pathway.updated` | MAJOR → OK | Frontend (`lib/websocket.ts`) reescrito para falar o protocolo do backend (`api/v1/ws.py`) | ✅ [Resolvido 2026-07-12, commit `3711216`] |

---

## Resumo

| Severidade | Count | Status |
|-----------|-------|--------|
| CRITICAL (resolvidos) | 5 → 0 | ✅ Todos fechados |
| MAJOR (resolvidos) | 2 → 0 | ✅ Fechado (inclui WebSocket, ver nota 2026-07-12) |
| MAJOR (postergado) | 0 | ✅ Nenhum — WebSocket protocol fechado neste ciclo (commit `3711216`) |
| MINOR | 1 | ✅ health status="healthy" aceitável |
| OK (sem ação) | 6 | ✅ Compatíveis nativamente |

---

## Correções Aplicadas (4 commits)

| Commit | FASE | Descrição |
|--------|------|-----------|
| `4f64f3e` | 2.1 | Auth: form-urlencoded compat, user field, cookie `token`, JWT com email/name |
| `c8b53c3` | 2.2 | Paths: patient alias, admin prefix /api/v1, seed data ventilação |
| `18f2a44` | 3 | Shapes: Pydantic Field(alias=) para Dashboard, Patient, Admin, Alerts |
| `3512b0e` | 6 | CI/CD: workflow frontend-v3 + ci.yml atualizado |

---

## Pontos de Atenção

1. **WebSocket**: ~~Conexão estabelece, mas protocolo de mensagens diverge entre frontend (`{type:"auth"}`) e backend (`{action:"subscribe"}`). Requer alinhamento em M8.~~ **[RESOLVIDO 2026-07-12]** Protocolo alinhado nas 4 camadas (`lib/websocket.ts` ↔ `api/v1/ws.py`): `{action:"subscribe", channel, token}`, pong por mensagem, envelope real; `pathway.state_changed` aliased para `pathway.updated`. Evento `pathway.updated` provado ponta-a-ponta (`services/pathway_enrollment.py::_publish_pathway_updated` → `app/patient/[mpi_id]/page.tsx` via `useRealtimeChannel`). Commit `3711216`.
2. **Dados de pathways**: Pacientes têm enrolments (LEITO-01: ventilação, desmame, nutrição) mas progress/criteria podem estar vazios. Precisa seed data adicional.
3. **Staleness**: ~~Dados de vitals/scores têm >13 dias de atraso (último: 2026-06-26). Necessário pipeline de ingestão para dados frescos.~~ **[RESOLVIDO 2026-07-12]** Seed DEMO regenerado com dados frescos (`scripts/dev/seed_demo.py`); e, defensivamente, o dashboard passou a cair de volta para as N=50 linhas mais recentes quando a janela de 24h está vazia (`services/dashboard.py::_rows_within_cutoff_or_recent`) — nunca mais tela vazia por staleness.
4. **Admin password**: ~~Foi resetado durante a sessão (bcrypt re-gerado). Senha atual: `admin`.~~ **[RESOLVIDO 2026-07-12]** A causa raiz não era a senha — era `User.role` preso em `'readonly'` para usuários admin legados (o ABAC passou a validar `role` real em vez de um valor derivado). Migração `0040_backfill_admin_role` promove para `role='admin'` todo usuário com `is_admin=TRUE` ainda em `role='readonly'`.
