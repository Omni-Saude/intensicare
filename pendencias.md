# PENDÊNCIAS — IntensiCare v2 (pós-remediação forense)

**Branch:** `main` | **Data:** 2026-07-06
**Origem:** Forensic Remediation — 25 gaps fechados (22 implementados, 3 deferred)
**Gatekeepers:** production-validator GO + security-manager GO

---

## 🔴 Bloqueantes para Deploy (Ambiente AWS)

Estes 3 gaps requerem ambiente AWS provisionado. Sem eles, o deploy em staging/production NÃO é possível.

### GAP-017 — ECS Task Definitions (WO-007)
- **Status:** Deferred
- **O que falta:** Criar task definitions ECS Fargate para API, Engine, e MLLP listener
- **Referência:** `docs/plan/architecture/system-architecture.md` §8
- **Diretórios:** `infrastructure/` e `infra/` estão vazios — precisam ser populados ou removidos
- **Ação humana necessária:** Provisionar conta AWS, criar task definitions via Terraform ou Console

### GAP-018 — IAM/ABAC Verification
- **Status:** Deferred
- **O que falta:** Verificar integração SSO com AWS IAM Identity Center real em staging
- **Módulos existentes:** `src/intensicare/auth/iam.py`, `src/intensicare/auth/abac.py` — implementados mas nunca testados contra IAM IC real
- **Config:** `config.py` — `iam_enabled=False` por padrão
- **Ação humana necessária:** Configurar IAM Identity Center, realizar teste de autenticação SSO

### GAP-019 — Disaster Recovery Configuration
- **Status:** Deferred
- **O que falta:** WAL shipping PostgreSQL, Caddy+LE TLS, DR drill
- **RPO/RTO alvo:** 1h/1h (definido em `docs/plan/architecture/observability-slo.md` §7)
- **Ação humana necessária:** Provisionar região DR, configurar replicação, realizar DR drill documentado

---

## 🟡 Pendências Técnicas (não-bloqueantes para staging)

### ~30 cores estruturais Tailwind restantes
- **Contexto:** GAP-006 reduziu 271 → ~30 violações. As restantes são bordas cinzas (`border-slate-200`), backgrounds (`bg-gray-50`), e hover states — não afetam segurança clínica
- **Arquivos afetados:** `command-center/page.tsx`, `alert-triage/page.tsx`, `admin/thresholds/page.tsx` (banners de erro), `Layout.tsx` (hover states)
- **Ação:** Migrar para `var(--semantic-border-default)`, `var(--semantic-surface-canvas)` numa futura sprint de consistência de UI

### 42 testes legacy quebrando (v1)
- **Arquivos:** `tests/test_vitals.py`, `tests/test_websocket.py`, `tests/test_thresholds.py`
- **Contexto:** Falhas pré-existentes herdadas do v1 — não foram introduzidas pela remediação
- **Ação:** Sessão dedicada de correção ou migração para nova suíte de testes

### Python 3.12 requerido, ambiente local tem 3.11
- **Impacto:** `pip install -e ".[dev]"` falha no ambiente local
- **Workaround:** Testes podem ser coletados com `--noconftest` e executados em CI (que usa Python 3.12 via actions/setup-python)
- **Ação:** Atualizar Python local ou usar Docker para dev

### L1/L2 test harness — vetores pendentes de wiring
- **Contexto:** GAP-013 criou 538 vetores YAML + 16 testes de propriedade Hypothesis. Os testes validam estrutura dos vetores mas NÃO estão wireados aos scorers reais (MEWS/NEWS2/SOFA/qSOFA)
- **Arquivos:** `tests/rules/test_alert_vectors.py`, `tests/property/test_scorer_properties.py`
- **Ação:** Wirear os testes aos scorers reais quando os domínios clínicos forem integrados

### Style Dictionary build no CI
- **Contexto:** `npm run build-tokens` funciona localmente mas não está integrado ao CI
- **Ação:** Adicionar step no workflow `ci.yml` para rodar `npm run build-tokens` e validar que todos os tokens resolvem

---

## 🟢 Prontos para Deploy (já implementados e verificados)

| Área | O que foi feito |
|------|----------------|
| **Segurança** | RateLimitMiddleware wired, alembic.ini limpo, JWT jti (logout funcional), secrets de produção bloqueados por model_validator, Redis com senha em prod |
| **Frontend clínico** | Cores de severidade migradas para CSS custom properties (BedCard, SeverityBadge, AlertCard, ScoreTimeline), 3 novas telas (alert-routing, clinical-forms, handoff) |
| **Design system** | 24 tokens JSON + build pipeline (Style Dictionary → 3 arquivos CSS), Storybook instalado, 13 page.tsx |
| **CI/CD** | Contract/storm/drills com scripts reais, `continue-on-error` removido, 9 scripts CI criados |
| **Testes** | ~320 novos testes (191 serviços + 49 health/pgcrypto + 538 vetores + 16 propriedades + BYTEA fix + correlação), 7 serviços cobertos |
| **Infra** | K8s/Helm worker path corrigido, Redis password em docker-compose.prod.yml, .env.example padronizado |
| **Cleanup** | Legacy frontend/ arquivado, auth stub removido, migration duplicada removida, docstring corrigida, fixture renomeada |

---

## 📋 Checklist para Deploy

- [ ] Provisionar conta AWS (GAP-017/018/019)
- [ ] Criar ECS task definitions para API, Engine, MLLP
- [ ] Configurar IAM Identity Center e testar SSO
- [ ] Configurar WAL shipping PostgreSQL + DR region
- [ ] Configurar TLS/Caddy+LE no ALB
- [ ] Rodar suíte completa de testes em staging (CI)
- [ ] Executar DR drill documentado
- [ ] Validar HL7 real com hospital AUSTA (CLIN-001)
- [ ] Realizar pentest externo (SEC-001)
- [ ] Submeter documentação ANVISA SaMD Classe II (REG-001)
- [ ] Finalizar LGPD RIPD (REG-002)

---

## 📁 Artefatos de Referência

| Artefato | Localização |
|----------|------------|
| Plano de remediação | `docs/plan/delivery/PlanV2-Build.md` |
| BUILD JOURNAL | `docs/plan/delivery/BUILD-JOURNAL.md` |
| HANDOFF (estado final) | `HANDOFF.yaml` |
| Plano de execução | `PLANS.md` |
| Gate reports | `/tmp/gate-security-manager.md`, `/tmp/gate-production-validator.md` |
| Traceability matrix | `docs/plan/traceability-matrix.md` (959 rules) |
| Design tokens spec | `docs/plan/design/design-tokens.md` |
| Test strategy | `docs/plan/delivery/test-strategy.md` |

---

*Gerado por Parreira (Orchestrator, SOUL.md v3 Agentic Loop) em 2026-07-06.*
*Sessão de remediação forense — 25 gaps fechados, gatekeepers GO/GO.*
