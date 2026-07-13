# AUDIT_PLAN — Auditoria Full-Spectrum IntensiCare

**Orquestrador:** Claude (Fable 5) — sessão de auditoria autônoma
**Data:** 2026-07-12
**Base:** `AUDIT_PROMPT.md` (Niemeyer, 2026-07-10)
**Modo:** Somente leitura/análise/teste. Zero modificação de código de produto.

---

## 1. Recon — Estado Verificado (FASE 0)

| Item | Estado verificado |
|------|-------------------|
| Backend localhost:8000 | ✅ UP — `/api/v1/health` → 200 |
| Frontend localhost:3000 | ✅ UP — `/` → 307 (redirect p/ login, middleware ativo) |
| Auth | ✅ `POST /api/v1/auth/login` (form-urlencoded, admin/admin) retorna access_token JWT com claims `sub, user_id, is_admin, role, name, email, exp, type, jti` |
| Trilhas YAML | **12** em `_work/alerts/pathways/` (antimicrobiano, delirium, desmame, equilibrio, estabilidade, nutricao, profilaxia, renal, respiratorio, sedacao, sepse, ventilacao) — prompt fala em "9+" |
| Contratos OpenAPI | **15** em `docs/contracts/` |
| Frontend v3 | 7 rotas page.tsx: `/`, `/login`, `/alerts`, `/pathways`, `/admin`, `/patient/[mpi_id]`, `/patient/[mpi_id]/pathway/[pp_id]` |
| lib/api.ts | 403 linhas confirmadas |
| Auditoria anterior | `audit-results/CONSOLIDATED_FORENSIC_AUDIT.md` (2026-07-09): veredito 🟡 ~85% aligned; 7 CRITICAL, 15 HIGH, 12 MEDIUM, 4 LOW. **Nota:** `docs/audit/FORENSICS_SYNTHESIS.md` citado no prompt NÃO existe — o equivalente real é o consolidado em `audit-results/`. |
| WIRING_GAPS.md | 14 endpoints: 13 ✅, 1 ⚠️ (WebSocket protocol mismatch, postergado M8). Staleness de dados >13 dias (último 2026-06-26 — hoje 16 dias). Senha admin = `admin`. |
| HANDOFF.yaml (product-designer) | M0–M8 todos `completed`. Gaps declarados: WCAG 88/100, stories 3/42, WS protocol pendente |

### Divergências detectadas no recon (a validar pelos agentes)
1. Prompt fala em "9 trilhas", existem **12** YAMLs — verificar quais estão ativas/completas.
2. Prompt fala em "6 páginas core / 8 rotas", existem **7** page.tsx — contar rotas de build.
3. `FORENSICS_SYNTHESIS.md` não existe no caminho citado — fonte substituta: `audit-results/CONSOLIDATED_FORENSIC_AUDIT.md`.
4. JWT do admin tem `role: "readonly"` com `is_admin: true` — possível incoerência RBAC (validar em Dim C/D).
5. Dados stale (>16 dias) — impacto em Dim B (telas vazias?) e Dim C (motor não validável sem pathways ativos?).

---

## 2. Mapa de Auditoria por Dimensão

| Dim | Pergunta central | Fontes de verdade | Agente | Output |
|-----|------------------|-------------------|--------|--------|
| **A — Rastreabilidade** (15%) | O que foi construído corresponde ao problema do usuário? | `docs/plan/`, `docs/adr/` (0001–0034), `docs/tdd/`, `docs/contracts/` (15), `audit-results/CONSOLIDATED_FORENSIC_AUDIT.md`, git history | 1 agente especializado (produto/spec) | `DIM_A_TRACEABILITY.md` |
| **B — UX/Jornada** (30%) | Intensivista decide em ≤2 cliques? | `frontend-v3/app/**`, `frontend-v3/components/**`, navegação real via curl/HTML render, `FRONTEND_REBUILD_PLAN.md`, HANDOFF.yaml metrics, tokens CSS | 1 agente (UX/a11y) | `DIM_B_UX.md` |
| **C — Backend** (25%) | Fórmulas/thresholds/critérios corretos e completos? | `_work/alerts/pathways/*.yaml` (12), motor de trilhas (`services/`), scoring MEWS/NEWS2/SOFA/qSOFA, endpoints reais com JWT, literatura (SSC-2021, KDIGO, CAM-ICU) | 1 agente (clínico/backend) | `DIM_C_BACKEND.md` |
| **D — Integração** (20%) | Contratos frontend↔backend íntegros? | `frontend-v3/lib/api.ts` (14 funções), curl campo-a-campo vs tipos TS, auth flow, WebSocket, `WIRING_GAPS.md` como baseline | 1 agente (integração) | `DIM_D_INTEGRATION.md` |
| **E — Inovação** (10%) | Genuinamente inovador ou dashboard genérico? | ADRs, YAMLs, motor declarativo, comparação com estado da arte CDS (Epic DI, Philips, etc. — pesquisa web) | 1 agente (pesquisa/produto) | `DIM_E_INNOVATION.md` |

## 3. Ordem de Execução

```
FASE 0  ✅ RECON (este documento)
BATCH 1 (3 agentes concorrentes — teto de 3 respeitado):
  ├── Dim A — Rastreabilidade
  ├── Dim C — Backend
  └── Dim E — Inovação
BATCH 2 (2 agentes, após liberação de slots):
  ├── Dim B — UX (backend+frontend UP confirmados)
  └── Dim D — Integração
FASE 6  Síntese (orquestrador) → FULLSPECTRUM_VERDICT.md
```

## 4. Regras aplicadas aos agentes
- Todo achado cita arquivo:linha, endpoint+resposta, ou comando+output.
- Nenhum agente corrige nada — bugs são REPORTADOS.
- Scoring 0–100 derivado de tabela de achados (cada ponto perdido tem achado correspondente).
- Cross-validation na síntese: convergência entre dimensões eleva severidade.
- Credenciais de teste: `admin`/`admin` via form-urlencoded (evidência: WIRING_GAPS.md §Pontos de Atenção #4).
