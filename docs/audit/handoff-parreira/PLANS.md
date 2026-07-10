# PLANS.md — Wiring Frontend v3 ↔ Backend IntensiCare

**Orquestrador:** Parreira  
**Origem:** PROMPT_WIRING.md (Niemeyer)  
**Data:** 2026-07-09  
**Status:** EM EXECUÇÃO

---

## 1. Objetivo

Conectar o frontend-v3 (50 componentes, 14 funções de API) com o backend FastAPI rodando em localhost:8000. Fechar gaps de wiring (path mismatch, shape mismatch, auth flow, CORS) e preparar M7 (trilhas restantes) e M8 (produção).

## 2. Descobertas do Recon (Fase 0)

| # | Descoberta | Severidade |
|---|-----------|------------|
| D1 | Backend `/auth/login` SEM prefixo `/api/v1` — router prefix é `/auth` | **CRITICAL** |
| D2 | Backend patient detail em `/patients/{mpi_id}/detail`, frontend chama `/patients/{mpiId}` | **CRITICAL** |
| D3 | next.config.ts já tem proxy rewrites + CSP + WebSocket proxy | ✅ OK |
| D4 | Backend health retorna `{status:"healthy"}` vs frontend espera `{status:"ok"}` | MINOR |
| D5 | Backend tem 12 YAMLs de trilhas (inclui antimicrobiano, desmame, estabilidade) | INFO |
| D6 | Backend `/api/v1/alerts` expõe acknowledge/resolve/escalate — rotas batem | ✅ OK |
| D7 | Backend pathways tem `/patients/{mpi_id}/pathways/{pp_id}/progress` | ✅ OK |
| D8 | Backend ws.py existe — verificar se endpoint `/ws` está registrado | MAJOR |
| D9 | Backend `/admin/users` SEM prefixo `/api/v1` — router prefix é `/admin` | CRITICAL |
| D10 | CORS precisa ser verificado — backend pode bloquear origin:3000 | MAJOR |

## 3. Milestones

### FASE 1: Gap Analysis (1 agente)
**M1.1** — Produzir WIRING_GAPS.md completo batendo em cada endpoint real
- Agente: `delegate_task` com contexto detalhado das descobertas do recon
- Duração: ≤30 min
- Verificação: arquivo existe, tabela completa (14 endpoints × status/shape/severidade)

### FASE 2: Auth + Path Fixes (2 agentes paralelos)
**M2.1** — Alinhar autenticação
- Corrigir path do login: frontend chama `/api/v1/auth/login` → backend expõe `/auth/login`
- Solução: adicionar rota `/api/v1/auth/login` no backend OU ajustar next.config.ts rewrite
- Verificar JWT claims (is_admin, role, sub, exp)
- Testar fluxo completo: POST /login → token → GET /dashboard

**M2.2** — Corrigir path mismatches (Patient + Admin + CORS)
- `/patients/{mpiId}` → `/patients/{mpi_id}/detail`
- `/admin/users` → precisa do prefixo `/api/v1` (backend router é `/admin`)
- Verificar CORS no backend (CORSMiddleware)
- Health check de integração: frontend→proxy→backend

### FASE 3: API Shape Validation (3 agentes paralelos)
**M3.1** — Dashboard + Patient Detail shapes
**M3.2** — Pathways + Alerts shapes (CRÍTICO)
**M3.3** — Admin + Health shapes

### FASE 4: M7 — Validação de Trilhas (2 agentes paralelos)
**M4.1** — renal, respiratório, ventilação, equilíbrio
**M4.2** — nutrição, profilaxia, sedação, delirium (+antimicrobiano, desmame, estabilidade)

### FASE 5: WebSocket (1 agente)
**M5.1** — Verificar/implementar ws://localhost:8000/ws

### FASE 6: CI/CD (1 agente)
**M6.1** — Pipeline de build/deploy frontend-v3

### FASE 7: Gate Final
- Atualizar HANDOFF.yaml
- Produzir RUNBOOK.md final
- Gatekeepers: production-validator + security-manager

## 4. Dependências

```
FASE 1 (RECON) ──→ FASE 2 (Auth+Paths) ──→ FASE 3 (Shapes) ──→ FASE 4 (Trilhas)
                                                                    │
                                                                    └──→ FASE 5 (WS)
                                                                          │
                                                                    FASE 6 (CI/CD)
                                                                          │
                                                                    FASE 7 (GATE)
```

Fases 5 e 6 podem rodar em paralelo após FASE 4.

## 5. Riscos

| Risco | Prob | Impacto | Mitigação |
|-------|------|---------|-----------|
| Auth path mismatch requer refactor backend | Alta | Alto | Adicionar rota alias, não refatorar |
| CORS bloqueando | Média | Alto | Verificar antes de qualquer teste |
| WebSocket não implementado | Média | Médio | Fallback para polling (ADR-0034) |
| Schema drift banco → models | Baixa | Alto | Verificar com health check |
| Phantom path (subagente escreve em /Users/familia/docs/) | Média | Médio | Verificar após cada batch |

## 6. Rollback Plan

Cada milestone commitado separadamente (wave-based commits):
- `git revert <commit>` por milestone
- Rollback máximo: restaurar branch do estado pré-wiring

## 7. Gatekeepers por Fase

| Fase | Gatekeeper |
|------|-----------|
| FASE 2 (Auth) | security-manager |
| FASE 3 (Shapes) | production-validator |
| FASE 7 (Gate) | production-validator + security-manager + ops-compliance-gate |

## 8. Ordem de Delegação

```
FASE 1: 1 agente (gap-analysis)
FASE 2: 2 agentes paralelos (auth + paths/CORS)
FASE 3: 3 agentes paralelos (dashboard/patient + pathways/alerts + admin/health)
FASE 4: 2 agentes paralelos (trilhas 2-5 + trilhas 6-9+)
FASE 5: 1 agente (websocket)
FASE 6: 1 agente (CI/CD)
FASE 7: Orquestrador (gate)
```

## 9. Estimativa

- FASE 1: S (30 min)
- FASE 2: M (2h paralelo)
- FASE 3: L (3h paralelo)
- FASE 4: L (4h paralelo)
- FASE 5: M (2h)
- FASE 6: M (2h)
- FASE 7: S (30 min)

**Total:** ~14h agente, ~6-7h wall clock com paralelismo.
