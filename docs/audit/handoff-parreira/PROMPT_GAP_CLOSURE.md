PROMPT PARA PARREIRA — Fechamento de 100% dos Gaps Forenses (v2 — 38 gaps)
=====================================================================================

## ═══════ GOAL ═══════

Fechar TODOS os 38 gaps identificados nas 4 auditorias forenses (Niemeyer + Parreira + Agent 1 + Agent 2 + Agent 3)
até atingir 100% de compliance. Nenhum gap deve permanecer aberto sem documentação.

## ═══════ CONTEXT ═══════

### Baseline reports (leia ANTES de qualquer ação — ordem recomendada)

1. `/Users/familia/intensicare/audit-results/CONSOLIDATED_FORENSIC_AUDIT.md` (183 linhas) — **síntese unificada** de 4 auditores
2. `/Users/familia/intensicare/docs/audit/FORENSICS_SYNTHESIS.md` (134 linhas) — Niemeyer+Parreira synthesis
3. `/Users/familia/intensicare/audit-results/FORENSIC_AUDIT_REPORT.md` (463 linhas) — Parreira deep analysis
4. `/Users/familia/intensicare/audit-results/forensic-tdd-gap-analysis.md` (389 linhas) — Agent 1: TDD gap detalhado
5. `/Users/familia/intensicare/audit-results/forensic-adr-compliance.md` (545 linhas) — Agent 2: ADR compliance estrito
6. `/Users/familia/intensicare/audit-results/forensic-rules-security.md` (531 linhas) — Agent 3: Regras + Segurança

### Current state (2026-07-09)

- **29/29 ADRs ratificados** ✅ — Niemeyer batch 2026-07-09 (status files atualizados)
- **24 domain services** com cobertura de testes ✅
- **15 contratos OpenAPI** (14 com API router correspondente) ✅
- **Frontend-v2**: 33 páginas Next.js, Style Dictionary instalado, build zero-erros
- **JWT**: production-grade (jti, blacklist, logout funcional)
- **Middlewares**: todos wired (no CVE-4 inactive guards)
- **eval()-free**: compilador usa `operator` module
- **Infra existe**: Docker, K8s, Helm, 34 Alembic migrations, CI scripts
- **Overall score atual**: ~78% → meta: 100% (ou todos BLOCKED documentados)

### GAP INVENTORY COMPLETO (38 gaps de 4 fontes independentes)

#### 🔴 CRITICAL (7 — must fix before production)

| ID | Gap | Domain | Fonte | Detalhe |
|----|-----|--------|-------|---------|
| C1 | **CDC consumer ADT não construído** | Movimentacao | All 4 | Materialized view (ADR-0025) requer Kafka/MSK; AWS-dependente |
| C2 | **3 de 5 tabelas ADT ausentes** | Movimentacao | Agent 1 | `admission_episode`, `patient_location_current`, `discharge_summary` — não existem em `models/movimentacao.py` |
| C3 | **Storage in-memory em 3 domínios** | Trilhas/Prescricao/Forms | Agent 1 | Dados em Python dicts, voláteis — perdem-se no restart |
| C4 | **`encounter_id` ausente no PatientPathway** | Trilhas Engine | Agent 1 | Sem encounter_id, readmissions são indetectáveis; ADR-021 exige escopo por admissão |
| C5 | **Sem content-addressing (SHA-256)** | Trilhas Engine | Agent 1 | TDD §3.1 exige `definition_version_id` como SHA-256; modelo atual é mutável |
| C6 | **ECS Task Definitions não criadas** | DevOps | All 4 | `infrastructure/` e `infra/` vazios; AWS-dependente |
| C7 | **RBAC binário (admin/não-admin)** | Security | Agent 3 | Sem granularidade por papel clínico (médico, enfermeiro, fisioterapeuta, etc.) |

#### 🟡 HIGH (15)

| ID | Gap | Domain | Fonte |
|----|-----|--------|-------|
| H1 | 8 de 12 pathway YAML definitions não escritos | Trilhas Engine | All 4 |
| H2 | 74 regras DMN de movimentação não implementadas (9/74) | Movimentacao | All 4 |
| H3 | Rotas da API de Prescricao divergem do contrato | Prescricao | Agent 1 |
| H4 | Sem pipeline de validação composable (43 regras) | Prescricao | Agent 1 |
| H5 | Sem integração com base ANVISA de medicamentos (ADR-026) | Prescricao | Agent 1 |
| H6 | IAM Identity Center não testado contra SSO real | Auth | Parreira |
| H7 | DR não configurado (RPO/RTO 1h) | Infrastructure | Parreira |
| H8 | Sem cross-field validation rules (RASS=-5 → CAM-ICU) | Formularios | Agent 1 |
| H9 | Sem form versioning / schema sync (ADR-0029) | Formularios | Agent 1 |
| H10 | Sem pre-population do MovimentacaoStateStore (dep. C1) | Evolucoes | Agent 1 |
| H11 | 14 clinical role templates não populados | Evolucoes | Agent 1 |
| H12 | Per-tenant white-label não implementado (ADR-0004) | Frontend | Agent 2 |
| H13 | Neumorphic elevation tokens não implementados visualmente (ADR-0007) | Frontend | Agent 2 |
| H14 | Sem query timeout na API layer (T-09) | Security | Parreira |
| H15 | Sem account lockout após N falhas (F-08) | Security | Parreira |

#### 🟠 MEDIUM (12)

| ID | Gap | Domain | Fonte |
|----|-----|--------|-------|
| M1 | ~30 tailwind core color violations | Frontend | Parreira |
| M2 | 42 legacy tests quebrados (v1) | Testing | Parreira |
| M3 | Test coverage em 31.2% (meta: 80%+) | Quality | Parreira |
| M4 | Style Dictionary build não no CI pipeline | DevOps | Parreira |
| M5 | L1/L2 test harness não wired a scorers reais | Testing | Parreira |
| M6 | SBOM não gerado no CI (F-10) | Security | Parreira |
| M7 | WebSocket per-message auth não implementado (F-09) | Security | Parreira |
| M8 | Sem offline-first submission (ADR-0029 spec) | Formularios | Agent 1 |
| M9 | Sem drawer-in-drawer overlay stack manager (ADR-0010) | Frontend | Agent 2 |
| M10 | Sem breadcrumb component (ADR-0009) | Frontend | Agent 2 |
| M11 | `admin:admin` hardcoded no RTSP URL builder | Security | Consolidated |
| M12 | SEPSE C1-C20 legacy criteria; v3 usa 6 SSC-2021 alerts | Rules | Agent 1 |

#### 🟢 LOW (4)

| ID | Gap | Domain | Fonte |
|----|-----|--------|-------|
| L1 | `--color-sidebar-hover` falha contraste (verify.py) | Design | Parreira |
| L2 | Python 3.12 required mas local env 3.11 | DevEx | Parreira |
| L3 | Sem políticas formais OPA/Rego compliance | Compliance | Consolidated |
| L4 | Phantom path `/Users/familia/docs/` stale directories | Ops | Parreira |

### Project structure (paths absolutos)
```
/Users/familia/intensicare/
├── src/intensicare/
│   ├── api/v1/              ← 22 API routers
│   ├── services/             ← 24 domain services + utilities
│   ├── models/               ← 27 SQLAlchemy models
│   ├── schemas/              ← 20 Pydantic schemas
│   ├── auth/                 ← JWT (jwt.py), ABAC (abac.py), deps, IAM
│   ├── core/                 ← database.py, redis.py, rate_limit.py, security_headers.py, telemetry.py
│   └── main.py               ← FastAPI app (157 linhas, todos middlewares wired)
├── frontend-v2/              ← Next.js 15 + Radix UI + Tailwind v4
│   ├── app/                  ← 33 pages (todas page.tsx)
│   ├── app/globals.css       ← CSS custom properties + data-theme
│   ├── lib/form-engine/      ← FormEngine.tsx, types.ts, renderers/
│   ├── config/forms/         ← 6 JSON form definitions
│   ├── design-tokens/        ← Style Dictionary pipeline (23 tokens)
│   ├── STACK_DECISION.md     ← Ratificação Radix+Tailwind
│   └── package.json          ← React 19, Next.js 15, Radix, Tailwind v4
├── docs/
│   ├── adr/                  ← 29 ADRs (todos ratificados 2026-07-09)
│   ├── contracts/            ← 15 OpenAPI 3.1.0 YAML specs
│   ├── tdd/                  ← 5 TDDs
│   ├── rules/                ← 279 regras YAML (50 arquivos em extraction/phase3/)
│   ├── audit/                ← Forensics reports + handoffs
│   └── security/threat-model.md
├── tests/                    ← 93 test files
├── _work/alerts/pathways/    ← 4 YAML pathway definitions (8 missing)
├── k8s/                      ← base/ + overlays/staging/ + overlays/production/
├── helm/intensicare/         ← Helm chart completo
├── docker-compose.yml + docker-compose.prod.yml
├── alembic/                  ← 34 migrations
├── scripts/ci/               ← contract-tests.sh, drills/, storm-test.py
└── pyproject.toml            ← 5,471 bytes, pinned deps
```

## ═══════ CONSTRAINTS ═══════

1. **READ-ONLY primeiro**: RECON antes de qualquer edição. Mapear território, validar existência de arquivos.
2. **PLANS.md antes de cada milestone** (≤3 arquivos por milestone, dependências mapeadas, rollback).
3. **Gatekeeper ≠ implementador**: após cada milestone, agente DIFERENTE faz cross-validation.
4. **Estado no filesystem**: HANDOFF.yaml, PLANS.md. NUNCA na conversa.
5. **Máximo paralelismo**: agentes sem shared files rodam em paralelo via `delegate_task`.
6. **Verificar com comandos reais**: `npm run build`, `npx tsc --noEmit`, `pytest`, `wc -l`, `grep -c`.
7. **Path ABSOLUTO sempre**: `/Users/familia/intensicare/...` — NUNCA paths relativos.
8. **Self-report NÃO confiável**: verificar com `ls -la`, `wc -l`, `grep -c` após cada batch.
9. **AWS gaps (C1, C2, C6)**: se AWS account indisponível, documentar em `docs/audit/BLOCKERS.md` e pular.

## ═══════ PHASES ═══════

### FASE 0 — RECON & PLAN (você, sem subagentes)

1. Ler os 6 relatórios listados no CONTEXT (ordem recomendada).
2. Validar o gap inventory contra o filesystem atual.
3. Produzir `/Users/familia/intensicare/docs/audit/GAP_CLOSURE_PLAN.md` com:
   - Tabela dos 38 gaps com status atual (OPEN/IN_PROGRESS/BLOCKED/DONE)
   - Ordem de execução (dependências primeiro: C1→C2→H2→H10, C4→C5, etc.)
   - Milestones de ≤3 arquivos cada
   - Estimativa de esforço por milestone
4. **GATE**: confirmar que o PLAN cobre 38/38 gaps.

### FASE 1 — Data Model Criticals (C2, C3, C4, C5 — ≤4h)

**Milestone 1.1: Corrigir modelo PatientPathway (C4)**
- Adicionar `encounter_id VARCHAR(64) NOT NULL` ao model `PatientPathway` em `models/pathway.py`
- Adicionar `bed_id VARCHAR(32)`, `unit VARCHAR(64)`, `current_state_id VARCHAR(32)`
- Criar migration Alembic: `alembic revision --autogenerate -m "add_encounter_id_to_patient_pathway"`
- Atualizar `schemas/pathways.py` com os novos campos
- Atualizar `services/domain_trilhas_engine.py` para usar `encounter_id`
- Gatekeeper: `grep 'encounter_id' models/pathway.py` deve retornar a definição da coluna

**Milestone 1.2: Content-addressing (C5)**
- Adicionar `definition_version_id VARCHAR(128)` e `definition_hash VARCHAR(128)` ao model `PathwayDefinition`
- Implementar SHA-256 hashing em `services/trilhas_compiler.py` (canonicalize YAML → hash)
- Atualizar `_work/alerts/schema/pathway.schema.json` se necessário
- Gatekeeper: `python -c "from intensicare.services.trilhas_compiler import compute_hash; print(compute_hash)"` deve funcionar

**Milestone 1.3: Migrar in-memory → PostgreSQL (C3)**
- **Trilhas**: mover `_enrollments` dict → tabela `patient_pathways` (já existe, usar query)
- **Prescricao**: mover `_prescriptions` dict → queries em `models/prescricao.py` (já existe tabela)
- **Formularios**: mover armazenamento → queries em `models/clinical_form.py`
- Gatekeeper para cada domínio: `grep -c '= {}' services/domain_*.py` deve ser 0 (ou próximo)

### FASE 2 — Movimentação ADT (C1, C2, H2 — parcialmente AWS-dependente)

**Milestone 2.1: Criar 3 tabelas ADT faltantes (C2)**
- Adicionar a `models/movimentacao.py`: `AdmissionEpisode`, `PatientLocationCurrent`, `DischargeSummary`
- Colunas conforme TDD §3.2 (ver `/Users/familia/intensicare/docs/tdd/tdd-movimentacao-adt.md` linhas 140-235)
- Criar migration Alembic
- Gatekeeper: `grep -c 'class.*Table' models/movimentacao.py` deve retornar ≥6

**Milestone 2.2: CDC Consumer ADT + DMN Engine (C1, H2)**
- Se AWS account DISPONÍVEL: construir `src/intensicare/consumers/cdc_adt.py`
- Implementar 74-rule DMN engine em `services/domain_movimentacao.py`
- Se AWS account NÃO DISPONÍVEL: documentar em `docs/audit/BLOCKERS.md` e pular

### FASE 3 — Pathway YAMLs + Domain Services (H1, H7 original) — ≤2h

**Milestone 3.1: 8 pathway YAML definitions (H1)**
- Criar em `_work/alerts/pathways/`: `estabilidade.yaml`, `sedacao.yaml`, `profilaxia.yaml`, `antimicrobiano.yaml`, `equilibrio.yaml`, `renal.yaml`, `delirium.yaml`, `respiratorio.yaml`
- Validar contra `_work/alerts/schema/pathway.schema.json`
- Gatekeeper: `ls _work/alerts/pathways/*.yaml | wc -l` deve retornar 12

**Milestone 3.2: 3 domain services faltantes (original H07)**
- Criar `services/domain_clinical_scoring.py` (18 regras de clinical-scoring YAML)
- Criar `services/domain_indicadores.py` (6 regras indicadores-etl)
- Criar `services/domain_nutricao.py` (5 regras nutricao)
- Cada um com: dataclasses, pelo menos 1 test file
- Gatekeeper: `ls services/domain_{clinical_scoring,indicadores,nutricao}.py`

### FASE 4 — Prescricao Gaps (H3, H4, H5) — ≤3h

**Milestone 4.1: Alinhar rotas da API com contrato (H3)**
- Rotas atuais divergem do TDD. Alinhar `api/v1/prescricao.py` com `docs/contracts/prescricao-openapi.yaml`
- Adicionar endpoint `POST /api/v1/prescricao/{id}/state` (state transition dedicado)
- Gatekeeper: diff entre contrato e router deve ser zero

**Milestone 4.2: Pipeline de validação composable (H4)**
- Implementar `PrescricaoValidationPipeline` em `services/domain_prescricao.py`
- 43 regras como validators chainable (pass/fail/warn)
- Gatekeeper: `grep -c 'def validate_' services/domain_prescricao.py` ≥ 20

**Milestone 4.3: Integração ANVISA drug database (H5)**
- Verificar se `services/drug_interactions.py` já tem base ANVISA local
- Se não: implementar cache local + fallback para API externa (ADR-026)
- Gatekeeper: `grep -c 'ANVISA\|anvisa' services/drug_interactions.py` ≥ 1

### FASE 5 — Formularios & Evolucoes (H8, H9, H10, H11, M8) — ≤3h

**Milestone 5.1: Cross-field validation (H8)**
- Implementar regra RASS=-5 → CAM-ICU bloqueado em `services/domain_formularios.py`
- Client-side: Zod `.refine()` no `FormEngine.tsx`
- Server-side: Pydantic validator
- Gatekeeper: test case `test_rass_minus5_blocks_cam_icu`

**Milestone 5.2: Form versioning / schema sync (H9)**
- Adicionar `definition_version` a `models/clinical_form.py`
- Build-time schema generation de FormConfig → Pydantic (ADR-0029)
- Gatekeeper: `grep 'definition_version' models/clinical_form.py`

**Milestone 5.3: Evolucoes gaps (H10, H11)**
- Pre-population do MovimentacaoStateStore — depende de C1; se bloqueado, stub com mock data
- Popular 14 clinical role templates em `services/domain_evolucoes.py`
- Gatekeeper: `grep -c 'role' services/domain_evolucoes.py` ≥ 14

**Milestone 5.4: Offline-first submission (M8)**
- IndexedDB queue no `FormEngine.tsx`
- Background Sync API registration
- Server-side: aceitar `submitted_offline=true` flag
- Gatekeeper: service worker registrado no build

### FASE 6 — Frontend ADR Gaps (H12, H13, M9, M10, M1) — ≤3h

**Milestone 6.1: Per-tenant white-label (H12)**
- Resolver token de cor primária antes do first paint (ADR-0004)
- CSS custom properties com namespace por tenant em `globals.css`
- Gatekeeper: `grep 'tenant' frontend-v2/app/globals.css`

**Milestone 6.2: Neumorphic elevation (H13)**
- Implementar escala de shadow tokens com dual-shadow neumórfico (ADR-0007)
- Adicionar a `design-tokens/primitives/elevation.json`
- Gatekeeper: build-tokens gera CSS shadows

**Milestone 6.3: Drawer + Breadcrumb (M9, M10)**
- Implementar overlay-stack manager com nesting, Esc/back, focus trapping (ADR-0010)
- Implementar breadcrumb component full-depth (ADR-0009)
- Gatekeeper: `find frontend-v2 -name 'OverlayStack*' -o -name 'Breadcrumb*'`

**Milestone 6.4: Tailwind color violations (M1)**
- Corrigir ~30 violações de core colors
- Rodar `python3 audit-results/verify.py` — zero color errors
- Gatekeeper: verify.py passa

### FASE 7 — Security Hardening (C7, H14, H15, M6, M7, M11) — ≤3h

**Milestone 7.1: Query timeout + Account lockout (H14, H15)**
- `statement_timeout = 30000` em `core/database.py`
- Account lockout: Redis, 5 falhas → 15min em `auth/dependencies.py`
- Gatekeeper: `pytest tests/test_auth_dependencies.py -v`

**Milestone 7.2: RBAC granular (C7)**
- Adicionar roles: `medico`, `enfermeiro`, `fisioterapeuta`, `farmacia`, `nutricao`, `admin`, `readonly`
- Atualizar `auth/abac.py` com policy por role
- Gatekeeper: `grep -c 'class.*Role' auth/abac.py` ≥ 7

**Milestone 7.3: WS auth + SBOM + RTSP fix (M6, M7, M11)**
- WebSocket per-message auth: JWT validation em `api/v1/ws.py`
- SBOM: `cyclonedx-py` em `scripts/ci/`
- RTSP: substituir `admin:admin` por env var `RTSP_CREDENTIALS`
- Gatekeeper: `grep 'admin:admin' services/domain_movimentacao.py` deve retornar 0

**Milestone 7.4: IAM Identity Center SSO Test (H6)**
- Teste de integração com IdP externo em `tests/test_auth.py`
- Verificar IAM IC config em `auth/iam.py`
- Se IdP NÃO disponível: documentar em `BLOCKERS.md`
- Gatekeeper: `pytest tests/test_auth.py -v -k iam`

### FASE 8 — Testing & Quality (M2, M3, M4, M5) — ≤4h

**Milestone 8.1: Corrigir 42 legacy tests (M2)**
- Rodar `pytest tests/ --tb=line -q`
- Corrigir falhas (provavelmente imports, APIs deprecated, auth fixtures)
- Gatekeeper: `pytest tests/ --tb=line -q` deve ter zero failures

**Milestone 8.2: Rule traceability tests**
- `tests/traceability/test_prescricao_rules.py` — 43 test cases
- `tests/traceability/test_evolucoes_rules.py` — 81 test cases
- `tests/traceability/test_formularios_rules.py` — 49 test cases
- Gatekeeper: `pytest tests/traceability/ -v` — todos passam

**Milestone 8.3: Test coverage 80%+ (M3)**
- `pytest --cov=src/intensicare --cov-report=term --cov-fail-under=80`
- Identificar módulos <80% e adicionar testes
- Gatekeeper: coverage report ≥80%

**Milestone 8.4: CI pipeline (M4, M5)**
- Integrar `npm run build-tokens` ao `scripts/ci/`
- Integrar `cyclonedx-py` SBOM ao CI
- Wire L1/L2 test harness vectors
- Gatekeeper: CI scripts executam sem erro

### FASE 9 — Infra & DR (C6, H7) — AWS-dependente

**Milestone 9.1: ECS Task Definitions (C6)**
- Se AWS account DISPONÍVEL: criar `infrastructure/ecs/task-definition.json`
- Se NÃO: documentar em `BLOCKERS.md`

**Milestone 9.2: DR Configuration (H7)**
- WAL shipping no `docker-compose.prod.yml`
- Documentar restore em `docs/ops/disaster-recovery.md`
- RPO 1h, RTO 1h

### FASE 10 — Polish (L1, L2, L3, L4, M12) — ≤2h

**Milestone 10.1: Contrast + Python + Phantom (L1, L2, L4)**
- Corrigir `--color-sidebar-hover` contraste
- Verificar `pyproject.toml` requires-python; documentar se 3.11 é aceitável
- Limpar `/Users/familia/docs/` stale directories
- Gatekeeper: `python3 audit-results/verify.py` zero failures

**Milestone 10.2: Documentação (L3, M12)**
- Documentar transição SEPSE C1-C20 → 6 SSC-2021 alerts
- Criar `docs/compliance/opa-policies/` com Rego policies iniciais

## ═══════ AGENTIC-LOOP PERSISTENCE ═══════

### Regra Máxima: REPETIR ATÉ 100%

Após cada milestone:
1. Rodar TODOS os gatekeepers do milestone
2. Se QUALQUER gatekeeper falhar:
   a. Diagnosticar (NÃO pular)
   b. Corrigir com agente DIFERENTE do implementador
   c. Re-rodar gatekeeper
   d. Repetir até PASSAR
3. Atualizar `docs/audit/GAP_CLOSURE_PLAN.md` com progresso
4. Se gap BLOCKED: documentar em `docs/audit/BLOCKERS.md` com:
   - O que falta
   - Bloqueador específico
   - Plano de desbloqueio
   - Owner
5. O loop NÃO termina até que: 38/38 gaps estejam DONE ou BLOCKED (com plano)

### HANDOFF.yaml por milestone

```yaml
# /Users/familia/intensicare/docs/audit/handoff-parreira/HANDOFF.yaml
milestone: "M1.1"
gaps_closed: ["C4"]
status: DONE | BLOCKED | IN_PROGRESS
files_changed: ["models/pathway.py", "schemas/pathways.py", "..."]
gatekeeper_passed: true | false
gatekeeper_output: "..."
next_milestone: "M1.2"
```

### Verificação Cruzada (antes de declarar DONE)

```bash
ls -la /Users/familia/intensicare/<paths>
wc -l /Users/familia/intensicare/<paths>
grep -c '<pattern>' /Users/familia/intensicare/<paths>
pytest /Users/familia/intensicare/tests/<test_file>.py -v --tb=short
cd /Users/familia/intensicare/frontend-v2 && npm run build
cd /Users/familia/intensicare/frontend-v2 && npx tsc --noEmit
```

## ═══════ DONE WHEN ═══════

- [ ] `docs/audit/GAP_CLOSURE_PLAN.md` cobre 38/38 gaps
- [ ] C4: `encounter_id` no PatientPathway + migration
- [ ] C5: Content-addressing SHA-256 implementado
- [ ] C3: In-memory storage migrado para PostgreSQL (3 domínios)
- [ ] C2: 3 tabelas ADT criadas + migration
- [ ] C1: CDC consumer ADT construído ou BLOCKED documentado
- [ ] C6: ECS Task Definitions criadas ou BLOCKED documentado
- [ ] C7: RBAC granular com 7+ clinical roles
- [ ] H1: 12/12 pathway YAML definitions (8 novos)
- [ ] H2: 74 DMN rules implementadas ou BLOCKED
- [ ] H3: Rotas prescricao alinhadas com contrato
- [ ] H4: Pipeline de validação composable (43 regras)
- [ ] H5: ANVISA drug database integrado
- [ ] H6: IAM SSO testado ou BLOCKED
- [ ] H7: DR configurado e documentado
- [ ] H8: Cross-field validation (RASS=-5 → CAM-ICU)
- [ ] H9: Form versioning implementado
- [ ] H10: Pre-population MovimentacaoStateStore (ou stub)
- [ ] H11: 14 clinical role templates populados
- [ ] H12: Per-tenant white-label implementado
- [ ] H13: Neumorphic elevation tokens visuais
- [ ] H14: `statement_timeout` PostgreSQL
- [ ] H15: Account lockout implementado
- [ ] M1: Zero tailwind color violations
- [ ] M2: Zero legacy test failures
- [ ] M3: Test coverage ≥80%
- [ ] M4: Style Dictionary build no CI
- [ ] M5: L1/L2 harness wired
- [ ] M6: SBOM no CI pipeline
- [ ] M7: WebSocket per-message auth
- [ ] M8: Offline-first submission
- [ ] M9: Drawer overlay stack manager
- [ ] M10: Breadcrumb component
- [ ] M11: `admin:admin` removido do RTSP builder
- [ ] M12: SEPSE migration documentado
- [ ] L1: Contraste corrigido (verify.py passa)
- [ ] L2: Python version documentado/resolvido
- [ ] L3: OPA/Rego policies iniciais
- [ ] L4: Phantom paths limpos
- [ ] `docs/audit/GAP_CLOSURE_FINAL.md` — relatório final
- [ ] `docs/audit/BLOCKERS.md` — gaps AWS-dependentes (se aplicável)
- [ ] Overall score = 100% (ou todos restantes BLOCKED com plano)

## ═══════ ANTI-PATTERNS ═══════

- ❌ Pular gatekeeper porque "é só um detalhe"
- ❌ Mesmo agente implementa E revisa
- ❌ Subagente com >3 arquivos no escopo
- ❌ Path relativo — SEMPRE `/Users/familia/intensicare/...`
- ❌ Confiar em self-report de subagente sem `ls -la` + `wc -l`
- ❌ Deixar gap aberto sem documentar em BLOCKERS.md
- ❌ Parar na primeira falha — loop persiste até resolver
- ❌ Ignorar dependências entre gaps (ex: corrigir C4 antes de C5)
- ❌ Fazer deploy sem testar (sempre rodar `pytest` + `npm run build`)

## ═══════ DEPENDENCY MAP ═══════

```
C1 (CDC consumer) ──► C2 (ADT tables) ──► H2 (DMN rules) ──► H10 (pre-population)
C4 (encounter_id) ──► C5 (content-addressing)
C3 (in-memory→PG) ──► independent
C6 (ECS) ──► AWS blocker
C7 (RBAC) ──► independent
H1 (YAMLs) ──► independent
H3, H4, H5 (prescricao) ──► H4 depends on H3
H8, H9 (forms) ──► independent
H12, H13 (frontend) ──► independent
M2 (legacy tests) ──► independent (run early)
M3 (coverage) ──► after M2 + rule traceability
```

## ═══════ REFERENCE ═══════

- Niemeyer SOUL.md: `/Users/familia/.hermes/profiles/niemeyer/SOUL.md`
- Consolidated audit: `/Users/familia/intensicare/audit-results/CONSOLIDATED_FORENSIC_AUDIT.md`
- TDD specs: `/Users/familia/intensicare/docs/tdd/`
- OpenAPI contracts: `/Users/familia/intensicare/docs/contracts/`
- ADRs: `/Users/familia/intensicare/docs/adr/`
- Rules YAML: `/Users/familia/intensicare/docs/rules/extraction/phase3/`
- Threat model: `/Users/familia/intensicare/docs/security/threat-model.md`
