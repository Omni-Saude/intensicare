# RECON_MAP.md — IntensiCare Frontend↔Backend Territory Map

> **FASE 0 — Reconnaissance Complete**
> **Data:** 2026-07-07
> **Agente:** Niemeyer (System Architect)

---

## 1. Catálogo de Clusters YAML (27 clusters, 989 regras)

| # | Cluster | Regras | Linhas | Domain Service | API Coverage |
|---|---------|--------|--------|---------------|-------------|
| 1 | alertas | 29 | 1,420 | domain_alertas.py | ✅ alerts API |
| 2 | antimicrobiano | 3 | 160 | — | ❌ |
| 3 | auditoria-logs | 37 | 1,388 | domain_operacional.py (?) | ❌ |
| 4 | auth-usuarios | 68 | 3,077 | domain_tenancy.py (?) | ✅ auth API |
| 5 | balanco-hidrico | 64 | 2,670 | domain_fluid_balance.py | ❌ |
| 6 | cadastros-ui | 35 | 862 | — | ❌ |
| 7 | clinical-scoring | 18 | 942 | serviços de scoring | ✅ dashboard API |
| 8 | comunicacao | 47 | 2,180 | domain_comunicacao.py | ❌ |
| 9 | documentacao-faturamento | 40 | 1,803 | — | ❌ |
| 10 | eficiencia | 12 | 623 | — | ❌ |
| 11 | equilibrio | 4 | 224 | — | ❌ |
| 12 | estabilidade | 27 | 1,253 | domain_hemo.py (?) | ❌ |
| 13 | evolucoes | 81 | 2,687 | — | ❌ |
| 14 | formularios-clinicos | 49 | 2,205 | domain_pharmaco_delirium.py (?) | ✅ clinical-forms API |
| 15 | indicadores-etl | 31 | 1,277 | — | ❌ |
| 16 | movimentacao-adt | 74 | 2,832 | domain_movimentacao.py | ❌ |
| 17 | nutricao | 11 | 565 | — | ❌ |
| 18 | operacional-infra | 64 | 2,900 | domain_operacional.py | ❌ |
| 19 | piora-clinica | 13 | 549 | domain_hemo.py (?) | ❌ |
| 20 | prescricao | 43 | 1,825 | — | ❌ |
| 21 | profilaxia | 8 | 382 | — | ❌ |
| 22 | sedacao | 28 | 1,153 | domain_pharmaco_delirium.py | ❌ |
| 23 | sepse | 101 | 4,333 | domain_sepsis.py | ✅ alerts API |
| 24 | sinais-vitais | 44 | 1,587 | vitals.py (service) | ✅ vitals API |
| 25 | tenancy-organizacao | 53 | 2,032 | domain_tenancy.py | ✅ admin API |
| 26 | trilhas-engine | 18 | 909 | — | ❌ |
| 27 | ventilacao | 27 | 1,073 | domain_respiratory.py | ❌ |
| **TOTAL** | | **989** | **48,735** | **12 services** | **~30% com API** |

---

## 2. Domain Services (12 arquivos em `src/intensicare/services/`)

| # | Service | Linhas | Domínios Mapeados |
|---|---------|--------|-------------------|
| 1 | domain_sepsis.py | 948 | sepse (101 rules) |
| 2 | domain_respiratory.py | — | ventilacao (27 rules) |
| 3 | domain_aki.py | — | N/A (novo domínio clínico) |
| 4 | domain_pharmaco_delirium.py | — | sedacao (28), formularios-clinicos (49) |
| 5 | domain_hemo.py | — | estabilidade (27), piora-clinica (13) |
| 6 | domain_fluid_balance.py | — | balanco-hidrico (64) |
| 7 | domain_electrolyte.py | — | N/A (novo domínio clínico) |
| 8 | domain_movimentacao.py | — | movimentacao-adt (74) |
| 9 | domain_comunicacao.py | — | comunicacao (47) |
| 10 | domain_operacional.py | — | operacional-infra (64), auditoria-logs (37) |
| 11 | domain_tenancy.py | — | tenancy-organizacao (53), auth-usuarios (68) |
| 12 | domain_alertas.py | — | alertas (29) |

---

## 3. API Endpoints Expostos (backend)

| Arquivo | Prefix | Endpoints |
|---------|--------|-----------|
| api/v1/alerts.py | `/api/v1/alerts` | GET /alerts, POST /{id}/acknowledge, POST /{id}/resolve, POST /{id}/escalate, GET /{id}/trace |
| api/v1/auth.py | `/auth` | POST /login, POST /logout |
| api/v1/admin.py | — | GET/POST /admin/users, PUT /admin/users/{id} |
| api/v1/dashboard.py | `/api/v1` | GET /dashboard |
| api/v1/health.py | — | GET /health |
| api/v1/ws.py | `/api/v1` | WS /ws, SSE /events/stream |
| api/vitals.py | — | POST /api/v1/vitals |
| api/patients.py | — | GET /api/v1/patients/{mpi_id}/status |
| api/thresholds.py | — | GET/POST /api/v1/thresholds, PUT /api/v1/thresholds/{id} |
| api/reference_ranges.py | — | GET /api/reference-ranges |
| api/clinical_forms.py | — | POST /api/v1/clinical-forms |

**Total: ~25 endpoints REST + 1 WebSocket + 1 SSE**

---

## 4. Frontend Pages (16 em `frontend-v2/app/`)

| # | Rota | Arquivo | API Consumida |
|---|------|---------|---------------|
| 1 | `/` | app/page.tsx | ? (landing) |
| 2 | `/login` | app/login/page.tsx | POST /auth/login |
| 3 | `/register` | app/register/page.tsx | POST /auth/register |
| 4 | `/dashboard` | app/dashboard/page.tsx | GET /api/v1/dashboard, WS |
| 5 | `/command-center` | app/command-center/page.tsx | GET /api/v1/dashboard, WS |
| 6 | `/alert-triage` | app/alert-triage/page.tsx | GET /api/v1/alerts, WS, POST /alerts/{id}/* |
| 7 | `/alert-routing` | app/alert-routing/page.tsx | ? |
| 8 | `/clinical-forms` | app/clinical-forms/page.tsx | POST /api/v1/clinical-forms |
| 9 | `/patient/[id]` | app/patient/[id]/page.tsx | GET /api/v1/patients/{id}/detail |
| 10 | `/handoff` | app/handoff/page.tsx | ? |
| 11 | `/admin` | app/admin/page.tsx | GET /admin/users, GET /api/v1/thresholds |
| 12 | `/admin/users` | app/admin/users/page.tsx | GET/POST/PUT /admin/users |
| 13 | `/admin/thresholds` | app/admin/thresholds/page.tsx | GET/POST/PUT /api/v1/thresholds |

---

## 5. Frontend API Client (`lib/api.ts`)

Chamadas definidas (evidência: leitura do arquivo):
- `loginApi` → POST /auth/login
- `registerApi` → POST /auth/register ⚠️ (não encontrado no backend!)
- `logoutApi` → POST /auth/logout
- `fetchDashboard` → GET /api/v1/dashboard
- `fetchPatientDetail` → GET /api/v1/patients/{mpiId}/detail ⚠️ (backend tem /status!)
- `fetchAlerts` → GET /api/v1/alerts
- `acknowledgeAlert` → POST /api/v1/alerts/{id}/acknowledge
- `resolveAlert` → POST /api/v1/alerts/{id}/resolve
- `escalateAlert` → POST /api/v1/alerts/{id}/escalate
- `fetchUsers` → GET /admin/users
- `createUser` → POST /admin/users
- `updateUser` → PUT /admin/users/{id}
- `fetchThresholds` → GET /api/v1/thresholds
- `updateThreshold` → PUT /api/v1/thresholds/{id}
- `createThreshold` → POST /api/v1/thresholds
- `fetchAdminStats` → GET /api/v1/alerts (aggregate)
- `fetchHealth` → GET /health

## 6. WebSocket / Realtime (`lib/websocket.ts`)

Eventos assinados: alert.raised, alert.updated, bed_grid.updated, presence.updated, vitals.updated
Transport: WS `/api/v1/ws?token=...` com fallback SSE `/api/v1/events/stream`

---

## 7. Gaps Preliminares Identificados no RECON

| Gap | Severidade | Descrição |
|-----|-----------|-----------|
| GAP-R01 | ⚠️ MAJOR | Frontend chama `/api/v1/patients/{id}/detail` — backend expõe `/api/v1/patients/{mpi_id}/status` |
| GAP-R02 | ⚠️ MAJOR | `registerApi` definido no frontend — endpoint `/auth/register` NÃO encontrado no backend |
| GAP-R03 | ⚠️ MAJOR | 16 clusters YAML (489 regras) sem domain service dedicado |
| GAP-R04 | 🔴 BLOCKER | 20+ clusters sem qualquer exposição via API REST |
| GAP-R05 | ⚠️ MAJOR | GET `/api/v1/alerts/{id}/trace` exposto no backend — sem consumidor frontend |
| GAP-R06 | ⚠️ MAJOR | GET `/api/reference-ranges` exposto — sem consumidor frontend |
| GAP-R07 | ⚠️ MAJOR | Domínios clínicos críticos (AKI, electrolyte, respiratory) com service mas sem endpoints API dedicados |
| GAP-R08 | 🔴 BLOCKER | Trilhas-engine (18 regras) — mecanismo de care pathways sem qualquer exposição |
