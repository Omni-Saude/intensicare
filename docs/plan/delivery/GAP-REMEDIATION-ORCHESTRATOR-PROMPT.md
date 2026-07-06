# Orchestrator Prompt — IntensiCare v2 Forensic Remediation (100% Gap Closure)

> **Paste this entire document** into a fresh orchestrator session (Hermes profile `parreira`)
> on branch `build/v2-fase-0` in `/Users/familia/intensicare`.
> **Mission:** Close ALL 25 gaps found by the 2026-07-06 forensic audit. Achieve 100% gap closure
> with formal gatekeeper sign-off on every milestone.

---

## ═══════════════════════════════════════════════════════════
## TASK ENVELOPE (OBRIGATÓRIO — SOUL.md §Envelope)
## ═══════════════════════════════════════════════════════════

| Campo | Valor |
|-------|-------|
| **Goal** | Fechar 100% dos 25 gaps identificados pela auditoria forense de 2026-07-06 no branch `build/v2-fase-0`, alcançando GO definitivo dos gatekeepers `production-validator` e `security-manager`. |
| **Context** | IntensiCare v2 — plataforma SaMD Classe II de suporte à decisão para UTI. Stack: Python 3.12+ FastAPI, PostgreSQL 16/TimescaleDB 2.18, Redis 7, Next.js 15 App Router, Radix UI, Tailwind v4. 507 arquivos alterados, 68,746+ inserções. 24/40 WOs verificadas, 31 migrations, 1.743 testes (94.8% passing), RATIFY 204→0. Branch: `build/v2-fase-0`. |
| **Constraints** | Não quebrar CI verde existente. Não regredir os 1.653 testes que passam. Manter compatibilidade com K8s/Helm. Usar CSS custom properties (não Tailwind hardcoded) para cores clínicas. Seguir estritamente SOUL.md agentic-loop. |
| **Done When** | (1) Todos os 25 gaps fechados com evidência em disco, (2) `production-validator` emite GO, (3) `security-manager` emite GO, (4) `check_tokens.py --strict` PASS, (5) `check_dispositions.py` PASS, (6) Suíte de testes ≥94.8% passing sem novas regressões, (7) BUILD-JOURNAL.md atualizado com todos os milestones, (8) HANDOFF.yaml atualizado sem blocked items críticos. |
| **Risk Level** | **L2** — mutação com escala. Alterações em auth (JWT), rate limiting (middleware), frontend clínico (cores de severidade), CI/CD (contract/storm/drills), e K8s/Helm (worker path). |
| **Scope Boundary** | NÃO alterar: schemas de banco de dados (migrations 0001-0030 são imutáveis), lógica de scoring clínico (MEWS/NEWS2/SOFA/qSOFA), 7 serviços de domínio já testados, RATIFY dispositions (371 ADOPT, 57 ADOPT-CORRECTED, 223 ADAPT, 242 RETIRE, 66 SUPERSEDE). NÃO fazer deploy. NÃO processar dados reais de pacientes. |

---

## ═══════════════════════════════════════════════════════════
## PERSISTENCE FILES — CONTEXT MAP
## ═══════════════════════════════════════════════════════════

### Primary (read first, in order)

| # | File | What It Contains |
|---|------|-----------------|
| 1 | `docs/plan/delivery/PlanV2-Build.md` | CANONICAL GAP LIST — 25 gaps com severidade, file:line, remediação, fases A→D |
| 2 | `docs/plan/delivery/BUILD-JOURNAL.md` | Claims da build original — Entry 0-4. Subestima realidade (41→60 testes, 20→31 migrations, 27→36 serviços) |
| 3 | `HANDOFF.yaml` | Blocked items (AUDIT-*, TECH-*, REG-*, CLIN-*, SEC-*), build_state (fase_0..4 status), infrastructure flags, known_issues |
| 4 | `docs/plan/traceability-matrix.md` | 959 rules, RATIFY: 0, ADOPT: 371, ADOPT-CORRECTED: 57 |

### Gate Reports (formal GO/NO-GO verdicts)

| # | File | Key Findings |
|---|------|-------------|
| 5 | `/tmp/gate-security-manager.md` | 🔴 CONDITIONAL-GO. C1: Wire rate limit. C2: Remove alembic.ini creds. C3-C4: Replace SecretStr defaults. C5: Redis password. C6: Remove auth stub. **JWT jti not emitted — logout broken.** **before_state/after_state not encrypted.** |
| 6 | `/tmp/gate-production-validator.md` | 🟡 CONDITIONAL-GO. W1: Remove auth stub. W2: Production secrets. W3-W6: Low/cosmetic. 0 blocking issues found. |

### Audit Reports (6 specialist agents)

| # | File | Scope | Key Gaps Found |
|---|------|-------|---------------|
| 7 | `/tmp/audit-2a-wo-verification.md` | WO-by-WO (40 WOs) | WO-023 DIVERGENT (design-tokens), WO-007/022/034/035 PARTIAL |
| 8 | `/tmp/audit-2b-migration-chain.md` | 31 migrations DAG | ⚠️ WARN: duplicate 0023, docstring 0013 wrong, 13 leaf branches |
| 9 | `/tmp/audit-2c-test-suite.md` | 1.743 tests | 2 code bugs (correlation fixture, alert BYTEA), 5 missing deps, 7 services 0% coverage, 37 infra-dependent failures |
| 10 | `/tmp/audit-2d-frontend.md` | frontend-v2/ | 10/12 pages, 7/7 components, BUILD_ID exists, legacy not archived |
| 11 | `/tmp/audit-2e-design-spec.md` | Design tokens + colors | Severity colors ✅ match spec hex, 271 hardcoded Tailwind violations, design-tokens 45% complete |
| 12 | `/tmp/audit-2f-infrastructure.md` | K8s, Helm, CI, Docker | K8s 21 manifests ✅, Helm 18 templates ✅, Rate limit not wired ❌, K8s worker path wrong |

---

## ═══════════════════════════════════════════════════════════
## THE 25 GAPS — COMPLETE LIST WITH REMEDIATION INSTRUCTIONS
## ═══════════════════════════════════════════════════════════

### PHASE A: 🔴 CRITICAL (Blocks Any Deployment) — 5 gaps, ~2 horas

#### GAP-001 | 🔴 CRITICAL | Rate Limiting Dead Code
- **Source:** Security Manager C1, Production Validator R2
- **Finding:** `RateLimitMiddleware` (200 LOC, `src/intensicare/core/rate_limit.py`) implementado com token bucket Redis + Lua scripting + buckets `auth`(5/min) e `api`(100/min). Mas **nunca registrado** no `main.py`.
- **File:** `src/intensicare/main.py:73`
- **Fix:** Adicionar 2 linhas após `CORSMiddleware`:
  ```python
  from intensicare.core.rate_limit import RateLimitMiddleware
  app.add_middleware(RateLimitMiddleware)
  ```
- **Verify:** `grep -n "RateLimitMiddleware" src/intensicare/main.py` deve retornar 2 ocorrências (import + add_middleware)
- **Test:** `curl -v http://localhost:8000/api/v1/health` deve mostrar headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- **Agent:** `tdd-london-swarm` (mid, 1 arquivo, 2 linhas)
- **Skill:** `tdd-london-swarm`

#### GAP-002 | 🔴 CRITICAL | Credenciais Hardcoded no alembic.ini
- **Source:** Security Manager C2 (único gatekeeper que detectou — NÃO estava nos relatórios de auditoria)
- **Finding:** `alembic.ini:8` contém `sqlalchemy.url = postgresql+asyncpg://intensicare:intensicare_dev@localhost:5432/intensicare` versionado em texto plano.
- **File:** `alembic.ini:8`
- **Fix:** Substituir por:
  ```ini
  sqlalchemy.url = %(DATABASE_URL)s
  ```
  E garantir que `DATABASE_URL` esteja no `.env.example` e seja injetado pelo `docker-compose`.
- **Verify:** `grep "intensicare_dev" alembic.ini` deve retornar 0. `grep "DATABASE_URL" alembic.ini` deve retornar 1.
- **Agent:** `tdd-london-swarm` (cheap, 1 arquivo, 1 linha)
- **Skill:** `tdd-london-swarm`

#### GAP-003 | 🔴 CRITICAL | JWT Logout Quebrado (jti não emitido)
- **Source:** Security Manager §3.3 (único gatekeeper que detectou)
- **Finding:** `create_access_token()` não emite claim `jti`. Sem `jti`, o blacklist via Redis nunca funciona — tokens continuam válidos após logout até expirarem naturalmente.
- **File:** `src/intensicare/auth/dependencies.py` (ou onde `create_access_token` estiver definido)
- **Fix:** Adicionar ao payload do token:
  ```python
  from uuid import uuid4
  payload = {..., "jti": str(uuid4())}
  ```
  E verificar que `is_token_blacklisted(jti)` é chamado em `get_current_user`.
- **Verify:** Inspecionar um token JWT gerado (decode base64 payload) — deve conter campo `jti`. Teste de logout deve invalidar o token.
- **Agent:** `tdd-london-swarm` (strong, auth-critical)
- **Skill:** `tdd-london-swarm` + `security-manager`

#### GAP-004 | 🔴 CRITICAL | BedCard.tsx — Cores Clínicas Hardcoded
- **Source:** Audit 2E GAP-2E-01, Production Validator (implied)
- **Finding:** 22 violações em `BedCard.tsx:9-75`. Usa `bg-red-500`, `text-red-600`, `bg-green-400`, `bg-yellow-500` para indicadores clínicos de severidade em vez de `var(--clinical-severity-*-fill/signal/wash)`.
- **File:** `frontend-v2/components/BedCard.tsx:9-75`
- **Fix:** Migrar para CSS custom properties seguindo o padrão de `SeverityBadge.tsx` (já 100% token-compliant). Exemplo:
  ```tsx
  // ❌ Antes
  <span className="bg-red-500 animate-pulse" />
  // ✅ Depois
  <span style={{ backgroundColor: 'var(--clinical-severity-critical-signal)' }} className="animate-pulse" />
  ```
- **Verify:** `grep -c "bg-red-500\|bg-green-400\|bg-yellow-500\|text-red-600" frontend-v2/components/BedCard.tsx` deve retornar 0. `check_tokens.py --strict` deve continuar PASS.
- **Agent:** `tdd-london-swarm` (mid, 1 arquivo, substituição mecânica)
- **Skill:** `tdd-london-swarm`

#### GAP-005 | 🔴 CRITICAL | admin/thresholds — Severity Band Map Hardcoded
- **Source:** Audit 2E GAP-2E-02
- **Finding:** `admin/thresholds/page.tsx:401-403` define mapa de bandas com classes Tailwind:
  ```tsx
  watch: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  urgent: 'bg-orange-50 border-orange-200 text-orange-800',
  critical: 'bg-red-50 border-red-200 text-red-800',
  ```
- **File:** `frontend-v2/app/admin/thresholds/page.tsx:401-403`
- **Fix:** Substituir por CSS custom properties:
  ```tsx
  watch: { backgroundColor: 'var(--clinical-severity-watch-wash)', borderColor: 'var(--clinical-severity-watch-signal)', color: 'var(--clinical-severity-watch-on-fill)' },
  ```
- **Verify:** `grep "bg-yellow-50\|bg-orange-50\|bg-red-50" frontend-v2/app/admin/thresholds/page.tsx` deve retornar 0.
- **Agent:** `tdd-london-swarm` (mid, 1 arquivo)
- **Skill:** `tdd-london-swarm`

### PHASE B: 🟠 HIGH (Blocks Pilot) — 5 gaps, ~3-5 dias

#### GAP-006 | 🟠 HIGH | 271 Hardcoded Tailwind Violations (14 arquivos)
- **Source:** Audit 2E §2.4
- **Files (ordered by violation count):**
  1. `app/patient/[id]/page.tsx` — 50 violações
  2. `app/admin/users/page.tsx` — 44
  3. `app/dashboard/page.tsx` — 39
  4. `app/admin/thresholds/page.tsx` — 28
  5. `app/admin/page.tsx` — 27
  6. `components/BedCard.tsx` — 22 (CRITICAL — já tratado no GAP-004)
  7. `components/Layout.tsx` — 21
  8. `app/register/page.tsx` — 13
  9. `app/login/page.tsx` — 11
  10. `app/command-center/page.tsx` — 6
  11. `app/alert-triage/page.tsx` — 5
  12. `components/AlertCard.tsx` — 3
  13. `components/ScoreTimeline.tsx` — 1
  14. `components/VitalsChart.tsx` — 1
- **Fix:** Migração sistemática em 3 sub-fases:
  - **B1:** Componentes clínicos (BedCard, AlertCard, ScoreTimeline, VitalsChart) — ~1 dia
  - **B2:** Páginas admin (users, thresholds, admin) — ~1.5 dias
  - **B3:** Páginas gerais (dashboard, patient, login, register, Layout) — ~1.5 dias
- **Verify (após cada sub-fase):** `check_tokens.py --strict` deve continuar PASS. `grep -c "bg-[a-z]*-[0-9]00\|text-[a-z]*-[0-9]00" <arquivo>` deve mostrar redução.
- **Agent:** `tdd-london-swarm` (mid, 14 arquivos, trabalho mecânico mas volumoso)
- **Skill:** `tdd-london-swarm`

#### GAP-007 | 🟠 HIGH | design-tokens/ 45% Complete
- **Source:** Audit 2E §2.2
- **Missing files (11 itens):**
  - `primitives/z-index.json`
  - `primitives/motion.json`
  - `primitives/type.json`
  - `primitives/elevation.json`
  - `primitives/breakpoints.json`
  - `brand/brand.schema.json`
  - `brand/brand.default.json`
  - `semantic/action.json`
  - `semantic/feedback.json`
  - `build/` directory (populado via `style-dictionary build`)
  - Style Dictionary config no local correto (`config/style-dictionary.config.js`)
- **Fix:** Criar cada arquivo JSON seguindo o schema definido em `design-tokens.md` §1. Rodar `npm run build-tokens` para popular `build/`.
- **Verify:** `find design-tokens -type f | wc -l` deve ser ≥20. `npm run build-tokens` deve sair com exit code 0.
- **Agent:** `tdd-london-swarm` (cheap, criação mecânica de JSON a partir de spec)
- **Skill:** `tdd-london-swarm`

#### GAP-008 | 🟠 HIGH | 3 Clinical Screens Missing
- **Source:** Audit 2A WO-034
- **Missing screens:**
  1. **alert-routing** — Configuração de roteamento por severidade (critical→RRT+SMS, urgent→push, watch→badge)
  2. **clinical-forms** — Formulários estruturados de beira-leito (RASS, CAM-ICU, BPS/NRS)
  3. **handoff** — Relatório de passagem de plantão
- **Spec reference:** `docs/plan/design/screens/` (canonical truth)
- **Fix:** Implementar cada tela como página Next.js App Router com:
  - CSS custom properties (não Tailwind hardcoded)
  - `aria-label` em todos elementos interativos
  - Suporte a `data-theme="dark"` e `data-theme="light"`
  - Componentes reutilizáveis do `frontend-v2/components/`
- **Verify:** 3 novos `page.tsx` existem. `check_tokens.py --strict` PASS para novas páginas. `axe-core` scan reporta 0 violations nos novos componentes.
- **Agent:** `tdd-london-swarm` (mid, 3 novas páginas)
- **Skill:** `tdd-london-swarm`

#### GAP-009 | 🟠 HIGH | CI Contract/Storm/Drills Placeholder
- **Source:** Audit 2A WO-035, Audit 2F
- **Finding:** 3 jobs no `ci.yml` estão em draft-mode com `continue-on-error: true`:
  - `contract` (L534-572): Só valida schema OpenAPI, não executa testes contratuais reais
  - `storm` (L614-683): Shell vazio
  - `drills` (L686-708): Contém `⚠️ Chaos drills são placeholder`
- **Fix:**
  - **contract:** Implementar testes reais contra `api/openapi.yaml` e `asyncapi.yaml` + mocks Athena/Gold + HL7 fixtures (`test-strategy.md` §4)
  - **storm:** Implementar L6 ≥500 alertas/min com p95<30s zero-loss (`test-strategy.md` §5)
  - **drills:** Implementar 6 L7 chaos drills: DRILL-AUDIT-TAMPER, DRILL-CROSS-TENANT-DECRYPT, DRILL-PHI-EGRESS-SCRUB, DRILL-VERSION-PIN, DRILL-POLLER-KILL, DRILL-NOTIFICATION-BLACKHOLE, DRILL-DUPLICATE-REPLAY (`test-strategy.md` §6)
  - Remover `continue-on-error: true` de todos os 3 jobs
- **Verify:** CI deve falhar (red) se contract/storm/drills falharem. `grep "continue-on-error.*true" .github/workflows/ci.yml` deve retornar 0 para esses jobs.
- **Agent:** `ops-cicd-github` (strong, CI/CD crítico) + QA agents para implementar os testes
- **Skill:** `ops-cicd-github` + `test-strategy.md` reference

#### GAP-010 | 🟠 HIGH | Legacy frontend/ Not Archived
- **Source:** Audit 2D §5
- **Finding:** Diretório `frontend/` (Vite SPA, ~300MB com node_modules e dist/) ainda no disco. Não referenciado por docker-compose ou CI, mas ocupa espaço e causa confusão.
- **Fix:**
  ```bash
  git mv frontend/ _legacy_frontend/
  echo "_legacy_frontend/node_modules/" >> .gitignore
  git add .gitignore
  git commit -m "chore: archive legacy Vite frontend to _legacy_frontend/"
  ```
- **Verify:** `ls frontend/` deve retornar "No such file". `ls _legacy_frontend/` deve existir. `grep -r "frontend/" docker-compose.yml docker-compose.prod.yml .github/workflows/ci.yml` não deve mostrar referências ao legacy.
- **Agent:** Coordinator (git mv é operação simples) — ou delegar para `tdd-london-swarm`
- **Skill:** N/A (git operation)

### PHASE C: 🟡 MEDIUM (Fix Before Production) — 15 gaps, ~1-2 semanas

#### GAP-011 | 🟡 MEDIUM | Style Dictionary Not Installed
- **Fix:** `cd frontend-v2 && npm install --save-dev style-dictionary`
- **Agent:** `tdd-london-swarm` (cheap)

#### GAP-012 | 🟡 MEDIUM | Storybook Not Installed
- **Fix:** `cd frontend-v2 && npx storybook@latest init --builder webpack5`
- **Agent:** `tdd-london-swarm` (mid)

#### GAP-013 | 🟡 MEDIUM | L1/L2 Test Harness Incomplete
- **Fix:** Expandir `tests/rules/test_alert_vectors.py` com 266 vetores YAML-driven. Expandir `tests/property/test_scorer_properties.py` com Hypothesis strategies.
- **Agent:** QA agents (cheap — tests-from-vectors)

#### GAP-014 | 🟡 MEDIUM | K8s/Helm Worker Module Path Wrong
- **Fix:** Atualizar `k8s/base/deployment-worker.yaml` e `helm/intensicare/templates/deployment-worker.yaml`: `intensicare.worker.settings.WorkerSettings` → `src.intensicare.services.notification_worker.WorkerSettings`
- **Agent:** `ops-containers-k8s` (mid)

#### GAP-015 | 🟡 MEDIUM | Duplicate Migration 0023
- **Fix:** `rm src/intensicare/db/migrations/0023_activate_clinical_ratify.py`. Se diretório `db/migrations/` inteiro for legado, remover tudo.
- **Agent:** `tdd-london-swarm` (cheap)

#### GAP-016 | 🟡 MEDIUM | .env.example Naming Mismatches
- **Fix:** Padronizar `SECRET_KEY`→`JWT_SECRET_KEY`, `KMS_CMK_ARN`→`ENCRYPTION_KEY_ARN`. Adicionar `ARQ_CONCURRENCY`, `ARQ_POLL_INTERVAL`.
- **Agent:** `tdd-london-swarm` (cheap)

#### GAP-017 | 🟡 MEDIUM | ECS Task Definitions / Empty Dirs
- **Fix:** Criar ECS task defs para API, Engine, MLLP em `infrastructure/` OU remover diretórios vazios.
- **Agent:** `ops-cloud-provisioning` (mid)

#### GAP-018 | 🟡 MEDIUM | IAM/ABAC Not Verified
- **Fix:** Verificar integração SSO em staging com IAM Identity Center real. (Se ambiente AWS não disponível, documentar como "verified in staging" e marcar como deferred com HANDOFF entry.)
- **Agent:** `security-manager` (strong)

#### GAP-019 | 🟡 MEDIUM | DR Not Configured
- **Fix:** Configurar WAL shipping PostgreSQL, Caddy+LE TLS, DR drill.
- **Agent:** `ops-iac-terraform` + `ops-cloud-provisioning` (strong)

#### GAP-020 | 🟡 MEDIUM | Migration Docstring Wrong (0013)
- **Fix:** Corrigir `Revises: 0008_driver_idempotency` → `Revises: 0012` em `alembic/versions/0013_seed_domain_definitions.py:3`
- **Agent:** `tdd-london-swarm` (cheap, 1 linha)

#### GAP-021 | 🟡 MEDIUM | Correlation Engine Fixture Collision (53 tests dead)
- **Fix:** Renomear fixture `engine` → `corr_engine` em `tests/test_correlation_engine.py`
- **Agent:** `tdd-london-swarm` (cheap, rename operação)

#### GAP-022 | 🟡 MEDIUM | Alert Engine BYTEA Bug (1 test fail)
- **Fix:** Aplicar `encrypt_text()` no helper `create_patient` antes de inserir `display_name` na `patient_cache`
- **Agent:** `tdd-london-swarm` (mid, requer entender pgcrypto)

#### GAP-023 | 🟡 MEDIUM | 7 Services Zero Coverage
- **Fix:** Criar testes para: `auth.py`, `rate_limit.py`, `secrets.py`, `telemetry.py`, `arq_settings.py`, `domain_fluid_balance.py`, `domain_pharmaco_delirium.py`. Target ≥80% coverage.
- **Agent:** QA agents (cheap, tests-from-spec)

#### GAP-024 | 🟡 MEDIUM | 5 Missing Test Dependencies
- **Fix:** Adicionar `jsonschema`, `hypothesis`, `pytz` ao `pyproject.toml` [dev] dependencies. Resolver import `maezo` (repo externo).
- **Agent:** `tdd-london-swarm` (cheap)

#### GAP-025 | 🟡 MEDIUM | Missing test_health.py + test_pgcrypto.py
- **Fix:** Criar ambos os arquivos de teste conforme WO-004 e WO-002 acceptance criteria.
- **Agent:** QA agents (cheap)

### ADDITIONAL GATEKEEPER-ONLY FINDINGS (not in PlanV2-Build.md)

#### GATE-SEC-01 | 🟡 MEDIUM | Config.py SecretStr Defaults
- **Source:** Security Manager C3, C4; Production Validator W2
- **Finding:** `config.py:26` `secret_key = SecretStr("change-me-in-production")` e `config.py:94` `postgres_password = SecretStr("intensicare_dev")`. Mitigado por sobreposição via `.env` em produção, mas defaults existem.
- **Fix:** Adicionar validação: `if settings.environment == "production" and "change-me" in settings.secret_key.get_secret_value(): raise ValueError(...)` . Ou usar `SecretStr(default=None)` e exigir env var.
- **Agent:** `tdd-london-swarm` (mid)

#### GATE-SEC-02 | 🟡 MEDIUM | Redis Sem Senha em Produção
- **Source:** Security Manager C5
- **Finding:** `config.py:133` `redis_password = SecretStr("")`. `docker-compose.prod.yml` não configura `requirepass`.
- **Fix:** Adicionar `REDIS_PASSWORD` ao `.env.example` e `docker-compose.prod.yml`. Configurar `requirepass` no Redis de produção.
- **Agent:** `ops-containers-k8s` (mid)

#### GATE-PROD-01 | 🟡 MEDIUM | Auth Stub Removal
- **Source:** Production Validator W1, Security Manager C6
- **Finding:** `src/intensicare/auth.py` (stub de dev) coexiste com pacote `auth/`. Python prioriza pacote, mas coexistência confunde scanners.
- **Fix:** `rm src/intensicare/auth.py` ou mover para `src/intensicare/auth/_dev_stub.py` com comentário explícito.
- **Agent:** `tdd-london-swarm` (cheap)

#### GATE-PROD-02 | ⚪ LOW | _check_config.py Debug Script
- **Source:** Production Validator W6
- **Fix:** Mover para `scripts/dev/_check_config.py` ou remover.
- **Agent:** `tdd-london-swarm` (cheap)

---

## ═══════════════════════════════════════════════════════════
## AGENTIC-LOOP OPERATING RULES (SOUL.md — MANDATORY)
## ═══════════════════════════════════════════════════════════

### Rule 0: Qualidade > Velocidade
O objetivo é 100% de fechamento de gaps com GO dos gatekeepers. Custo de token é investimento.

### Rule 1: Envelope First
Cada gap já tem envelope completo neste documento (Finding, File, Fix, Verify, Agent, Skill). NÃO execute sem revisar o envelope do gap.

### Rule 2: Plan Before Edit
Antes de iniciar cada fase (A/B/C), atualize `PLANS.md` no workspace com:
- Milestones da fase (cada gap = 1 milestone)
- Ordem de delegação
- Dependências entre milestones
- Gatekeepers requeridos por milestone

### Rule 3: Pre-load Skills Before EVERY delegate_task
**NUNCA dispare `delegate_task` sem `skill_view()` antes.**

| Gap Category | Skills to Pre-load |
|-------------|-------------------|
| Python backend (GAP-001, 002, 003, 020, 021, 022, GATE-SEC-01) | `tdd-london-swarm`, `security-manager` |
| Frontend (GAP-004, 005, 006, 007, 008, 011, 012) | `tdd-london-swarm` |
| CI/CD (GAP-009) | `ops-cicd-github` |
| K8s/Helm (GAP-014, GATE-SEC-02) | `ops-containers-k8s` |
| Infra/AWS (GAP-017, 018, 019) | `ops-cloud-provisioning`, `ops-iac-terraform`, `security-manager` |
| Testing (GAP-013, 023, 024, 025) | `tdd-london-swarm` |
| Migrations/Cleanup (GAP-015, 016, 020, GATE-PROD-01, GATE-PROD-02) | `tdd-london-swarm` |

### Rule 4: Delegate with the Right Tool

| Complexity | Tool |
|-----------|------|
| 1 arquivo, ≤10 min, 1 skill | `delegate_task` |
| 3+ arquivos, >10 min, 2+ skills, qualidade crítica | `hermes chat -q -s <skill1> -s <skill2> -w` |

**Para este prompt:**
- GAP-001, 002, 004, 005, 020, 021, GATE-PROD-01, GATE-PROD-02 → `delegate_task` (simples, 1-2 arquivos)
- GAP-003, 006, 007, 008, 009 → `hermes chat -q -s` (complexos, multi-arquivo, segurança crítica)
- GAP-010 → Coordinator (git mv) ou `delegate_task`

### Rule 5: VERIFY → GATE Cycle (NUNCA pular)

Após CADA milestone:
```
1. generate-or-update-tests  → escrever/atualizar teste
2. run-targeted-checks       → rodar apenas os testes do milestone
3. evaluate                  → passou? próximo. falhou? continua
4. summarize-failure         → documentar falha
5. repair                    → corrigir causa raiz
6. rerun                     → reexecutar
7. GATEKEEPER                → spawn production-validator OU security-manager
```

### Rule 6: Gatekeepers Are Independent & Mandatory
- **Reviewer ≠ Implementer** — gatekeeper é agente DIFERENTE, contexto LIMPO
- **Gatekeeper NUNCA é opcional** — mesmo para gaps "simples"
- **Se gatekeeper falhar (timeout), RE-DISPATCH com escopo menor**

### Rule 7: State on Filesystem, Not Conversation
- `PLANS.md` → milestones + progresso
- `RUNBOOK.md` → log de cada milestone durante execução longa
- `CHECKPOINT.md` → ao final de cada milestone
- `HANDOFF.yaml` → atualizar blocked items conforma gaps fecham
- `BUILD-JOURNAL.md` → append entry ao final de cada fase

### Rule 8: Flywheel After Every Phase
Após cada fase (A/B/C):
```
1. Registrar trace   → comandos, decisões, falhas, custo, duração
2. Diagnosticar      → o que deu certo? errado? por quê?
3. Classificar       → erro de contexto? ferramenta errada? agente errado?
4. Converter         → se falha recorrente: skill patch, regra AGENTS.md, hook, eval
5. Alimentar learner → reasoningbank-learner
```

---

## ═══════════════════════════════════════════════════════════
## EXECUTION ORDER (MAX PARALLELISM)
## ═══════════════════════════════════════════════════════════

### Phase A Execution Plan (5 gaps, ~2 horas)

```
PLAN: PLANS.md — Fase A milestones

WAVE A1 (parallel — sem dependências entre si):
├── delegate_task: GAP-001 (rate limit wiring, 2 linhas)
├── delegate_task: GAP-002 (alembic.ini creds, 1 linha)
├── delegate_task: GAP-004 (BedCard cores, 1 arquivo)
├── delegate_task: GAP-005 (admin/thresholds band map, 1 arquivo)
└── delegate_task: GAP-003 (JWT jti, auth crítico)

AFTER ALL COMPLETE:
├── VERIFY: Rodar test suite, check_tokens.py, grep verification
├── GATE: Spawn production-validator (focado em rate limit + auth)
├── GATE: Spawn security-manager (focado em alembic.ini + JWT jti)
└── DOCUMENT: Atualizar BUILD-JOURNAL.md Entry 5a, HANDOFF.yaml
```

### Phase B Execution Plan (5 gaps, ~3-5 dias)

```
WAVE B1 (parallel):
├── hermes chat: GAP-007 (design-tokens completion, 11 JSON files)
├── hermes chat: GAP-008 (3 clinical screens, 3 new page.tsx)
├── delegate_task: GAP-010 (legacy archive, git mv)
└── delegate_task: GAP-006-B1 (componentes clínicos: BedCard, AlertCard, ScoreTimeline, VitalsChart)

WAVE B2 (parallel — após B1):
├── delegate_task: GAP-006-B2 (páginas admin: users, thresholds, admin)
└── delegate_task: GAP-006-B3 (páginas gerais: dashboard, patient, login, register, Layout)

WAVE B3 (sequential — após B1/B2):
└── hermes chat: GAP-009 (CI contract/storm/drills, 3 jobs, critical path)

AFTER ALL COMPLETE:
├── VERIFY: Full test suite, check_tokens.py --strict, CI dry-run
├── GATE: Spawn production-validator (full scan)
├── GATE: Spawn security-manager (full scan)
└── DOCUMENT: BUILD-JOURNAL.md Entry 5b, HANDOFF.yaml
```

### Phase C Execution Plan (15 gaps, ~1-2 semanas)

```
WAVE C1 (parallel — independentes):
├── GAP-011: npm install style-dictionary
├── GAP-015: rm duplicate migration
├── GAP-020: fix migration docstring (1 linha)
├── GAP-021: rename correlation fixture
├── GAP-024: add test dependencies to pyproject.toml
└── GATE-PROD-02: remove/move _check_config.py

WAVE C2 (parallel — dependem de C1 para contexto):
├── hermes chat: GAP-013 (L1/L2 test harness, 266 vectors + Hypothesis)
├── delegate_task: GAP-016 (.env.example naming standardization)
├── delegate_task: GAP-022 (alert engine BYTEA fix)
├── delegate_task: GAP-023 (7 services zero coverage tests)
└── delegate_task: GAP-025 (test_health.py + test_pgcrypto.py)

WAVE C3 (parallel — infra, podem correr em paralelo):
├── delegate_task: GAP-012 (Storybook init + configure)
├── delegate_task: GAP-014 (K8s/Helm worker path fix)
├── delegate_task: GATE-SEC-02 (Redis password production)
└── delegate_task: GATE-PROD-01 (auth stub removal)

WAVE C4 (sequential/semi-parallel — requerem ambiente):
├── GAP-017: ECS task definitions (se AWS disponível)
├── GAP-018: IAM/ABAC verification (se AWS disponível)
└── GAP-019: DR configuration (se AWS disponível)

AFTER ALL COMPLETE:
├── VERIFY: Full test suite (target ≥95% passing), coverage ≥80%
├── GATE: Spawn production-validator (FULL, definitive)
├── GATE: Spawn security-manager (FULL, definitive)
├── DOCUMENT: BUILD-JOURNAL.md Entry 5c (FINAL), HANDOFF.yaml
└── LEARN: Feed reasoningbank-learner with full trajectory
```

---

## ═══════════════════════════════════════════════════════════
## SKILL PRE-LOADING TABLE
## ═══════════════════════════════════════════════════════════

Antes de CADA `delegate_task` ou `hermes chat`, carregue estas skills via `skill_view()`:

| Agent | Skills to Pre-load | When |
|-------|-------------------|------|
| `tdd-london-swarm` | `tdd-london-swarm` | Todo gap de código (Python ou TypeScript) |
| `ops-cicd-github` | `ops-cicd-github` | GAP-009 (CI/CD) |
| `ops-containers-k8s` | `ops-containers-k8s` | GAP-014, GATE-SEC-02 |
| `ops-cloud-provisioning` | `ops-cloud-provisioning` | GAP-017 |
| `ops-iac-terraform` | `ops-iac-terraform` | GAP-019 |
| `security-manager` | `security-manager` | GAP-003, GAP-018, todos os gate checks |
| `production-validator` | `production-validator` | Todos os gate checks |
| `ops-compliance-gate` | `ops-compliance-gate` | GAP-009 (contract tests LGPD/ANS) |

---

## ═══════════════════════════════════════════════════════════
## VERIFICATION COMMANDS (Run After Every Milestone)
## ═══════════════════════════════════════════════════════════

```bash
# === PHASE A VERIFICATION ===

# GAP-001: Rate limit wired
grep -n "RateLimitMiddleware" src/intensicare/main.py
# Esperado: 2 ocorrências (import + add_middleware)

# GAP-002: alembic.ini clean
grep "intensicare_dev" alembic.ini
# Esperado: 0 matches

# GAP-003: JWT jti
python3 -c "
import sys; sys.path.insert(0,'src')
from intensicare.auth.dependencies import create_access_token
token = create_access_token({'sub':'test'})
import base64, json
payload = json.loads(base64.urlsafe_b64decode(token.split('.')[1] + '=='))
assert 'jti' in payload, 'JTI MISSING!'
print('JTI PRESENT:', payload['jti'])
"

# GAP-004: BedCard clinical colors
grep -c "bg-red-500\|bg-green-400\|bg-yellow-500\|text-red-600" frontend-v2/components/BedCard.tsx
# Esperado: 0

# GAP-005: admin/thresholds band map
grep "bg-yellow-50\|bg-orange-50\|bg-red-50" frontend-v2/app/admin/thresholds/page.tsx
# Esperado: 0 matches

# === CROSS-CUTTING ===
cd /Users/familia/intensicare
python3 scripts/check_tokens.py --strict
# Esperado: PASS, 0 unresolved

python3 docs/plan/_work/scripts/check_dispositions.py
# Esperado: PASS (14/0/0)

python3 -m pytest tests/ -x --tb=short -q --ignore=tests/test_vitals.py --ignore=tests/test_websocket.py --ignore=tests/test_thresholds.py 2>&1 | tail -5
# Esperado: ≥94.8% passing

# === PHASE B ADDITIONAL ===
grep "continue-on-error.*true" .github/workflows/ci.yml
# Esperado: 0 matches for contract/storm/drills jobs

ls frontend/ 2>&1
# Esperado: "No such file or directory"

ls _legacy_frontend/
# Esperado: diretório existe

find design-tokens -type f | wc -l
# Esperado: ≥20

# === PHASE C ADDITIONAL ===
python3 -m pytest tests/test_correlation_engine.py --co -q 2>&1 | tail -3
# Esperado: 53 tests collected (não 0)

python3 -m pytest tests/ --cov=src/intensicare --cov-report=term-missing 2>&1 | grep "TOTAL"
# Esperado: ≥80% coverage

helm lint helm/intensicare/
# Esperado: 0 errors

kubectl --dry-run=client -k k8s/overlays/staging/ 2>&1 | head -3
# Esperado: sem erros de parsing
```

---

## ═══════════════════════════════════════════════════════════
## ANTI-PATTERNS (STRICTLY AVOID)
## ═══════════════════════════════════════════════════════════

| ❌ Anti-Pattern | ✅ Correct |
|----------------|-----------|
| Orquestrador codando diretamente | **DELEGATE** para specialist agent |
| `delegate_task` sem `skill_view()` prévio | **PRE-LOAD** skills e passar no `context` |
| Aceitar claim de agente sem verificação | **VERIFY** cada output contra disco |
| Prosseguir antes do gatekeeper retornar | **WAIT** for formal GO/NO-GO |
| Pular flywheel após milestones | **TRACE → DIAGNOSE → CLASSIFY → CONVERT → LEARN** |
| Usar `delegate_task` para 3+ skills | **`hermes chat -q -s`** para complexidade |
| Gatekeeper = implementer | **DIFFERENT agent, CLEAN context** |
| Fazer broad grep manual | **search_files + execute_code** programático |
| Criar arquivos MD de status temporários | **PLANS.md, RUNBOOK.md, HANDOFF.yaml** apenas |
| Deploy ou dados reais de pacientes | **NUNCA** — este é um prompt de remediação apenas |

---

## ═══════════════════════════════════════════════════════════
## DEFINITION OF DONE (FINAL)
## ═══════════════════════════════════════════════════════════

- [ ] Todos os 25 gaps fechados com evidência em disco
- [ ] `production-validator` emite **GO** (não CONDITIONAL-GO)
- [ ] `security-manager` emite **GO** (não CONDITIONAL-GO)
- [ ] `check_tokens.py --strict` **PASS** (0 unresolved)
- [ ] `check_dispositions.py` **PASS** (14/0/0)
- [ ] Suíte de testes ≥94.8% passing (sem novas regressões)
- [ ] Cobertura de código ≥80% global (≥95% scorers/engine)
- [ ] `helm lint` **PASS** (0 errors)
- [ ] K8s manifests parseiam sem erros
- [ ] CI contract/storm/drills jobs **não** são draft-mode
- [ ] `grep "continue-on-error.*true" .github/workflows/ci.yml` retorna 0 para contract/storm/drills
- [ ] Legacy `frontend/` não existe mais no disco
- [ ] `design-tokens/` tem ≥20 arquivos
- [ ] `npm run build-tokens` sai com exit code 0
- [ ] `frontend-v2/` tem ≥13 page.tsx (10 originais + 3 novas)
- [ ] BUILD-JOURNAL.md atualizado com Entry 5a, 5b, 5c
- [ ] HANDOFF.yaml sem blocked items 🔴 CRITICAL
- [ ] Flywheel executado para todas as 3 fases

---

## ═══════════════════════════════════════════════════════════
## KICKOFF CHECKLIST (Execute Before Any Code)
## ═══════════════════════════════════════════════════════════

1. [ ] `git status` — deve estar limpo no `build/v2-fase-0`
2. [ ] Ler `PlanV2-Build.md` para confirmar os 25 gaps
3. [ ] Ler `/tmp/gate-security-manager.md` — anotar C1-C6
4. [ ] Ler `/tmp/gate-production-validator.md` — anotar W1-W6
5. [ ] Criar `PLANS.md` com milestones da Fase A
6. [ ] Pre-load skills: `tdd-london-swarm`, `security-manager`, `production-validator`
7. [ ] Spawnar Wave A1 (5 gaps em paralelo)

---

*Prompt compilado em 2026-07-06 a partir de: 6 auditorias de agente + 2 rodadas de gatekeeper + cross-validation do coordenador. Autoridade: SOUL.md v3 Enhanced — Modern Agentic Loop.*
