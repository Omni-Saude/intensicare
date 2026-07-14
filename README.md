# Intensicare 🏥⚡

**Plataforma de monitoramento contínuo para UTI — FastAPI + TimescaleDB + Redis + Next.js**

> **Status: em hardening pós-auditoria — 2026-07**
>
> Backend **Python 3.12 + FastAPI + SQLAlchemy (async) + PostgreSQL/TimescaleDB + Redis**; frontend **Next.js 16 + React 19 + Tailwind v4** (`frontend-v3/`). Quatro engines de scoring clínico (MEWS, NEWS2, SOFA, qSOFA), **12 trilhas clínicas declarativas** com enrollment persistente e auto-avaliação na ingestão, alertas com **consolidação anti-fadiga e linguagem humanizada** ([ADR-0039](docs/adr/ADR-0039-alert-group-read-aggregation.md)), ingestão HL7 v2 via MLLP, tempo real via WebSocket, CDS Hooks 2.0 e projeção de deterioração.
>
> Ciclos de auditoria e correção (2026-07): full-spectrum → E2E ao vivo em Chrome real → estabilização da suíte (**2975 passed / 0 failed / 0 errors**) → remediação responsiva/a11y (axe 0 violations multi-viewport) → consolidação de alertas. Relatórios em [`docs/audit/`](docs/audit/). **Pendência regulatória central: validação clínica independente formal** (ver [SECURITY.md](SECURITY.md) e `docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md`).

---

## 📋 Navegação Rápida

| Para | Vá para |
|------|---------|
| **Visão do produto** | [`docs/product/vision.md`](docs/product/vision.md) |
| **Documentação da API** | [`docs/api/overview.md`](docs/api/overview.md) + contratos OpenAPI em [`docs/contracts/`](docs/contracts/) (28 arquivos) |
| **Política de segurança** | [`SECURITY.md`](SECURITY.md) |
| **Decisões de arquitetura (ADRs)** | [`docs/adr/`](docs/adr/) (ADR-001, ADR-0030…ADR-0039 + série 0001–0029 de frontend/design) |
| **Auditorias e vereditos** | [`docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md`](docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md) · [`E2E_LIVE_REPORT.md`](docs/audit/fullspectrum/E2E_LIVE_REPORT.md) · [`RESPONSIVE_FIX_REPORT.md`](docs/audit/RESPONSIVE_FIX_REPORT.md) |
| **Catálogo de regras clínicas** | [`docs/rules/README.md`](docs/rules/README.md) (959 regras, 27 clusters) |

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+ · Docker e Docker Compose · Node.js 20+ · Git

### Subida de desenvolvimento (caminho verificado)

```bash
git clone https://github.com/Omni-Saude/intensicare.git
cd intensicare

# 1) Infra (Postgres/TimescaleDB + Redis) via Docker
docker compose up -d postgres redis

# 2) Backend local (venv)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head          # ver nota de migrações abaixo
make seed-demo                # 5 pacientes MPI-DEMO-001..005 com vitais e trilhas
.venv/bin/uvicorn intensicare.main:app --port 8000 --app-dir src

# 3) Frontend (Next.js, em outro terminal)
cd frontend-v3 && npm ci && npm run dev   # http://localhost:3000

# 4) Saúde
curl -L http://localhost:8000/health      # /health responde 307 → /api/v1/health
```

> **Notas honestas de ambiente**
> - **Swagger/Redoc (`/docs`, `/redoc`) só existem com `DEBUG=true`** no `.env` — com `DEBUG=false` retornam 404 (default de produção). A fonte de verdade dos contratos é `docs/contracts/`.
> - **`docker compose up` completo hoje NÃO sobe o frontend atual**: o serviço `frontend-dev` monta `./frontend-v2`, que não existe mais (o frontend vivo é `frontend-v3/`). Use o passo 3 acima. (Dívida rastreada.)
> - **Migrações from-scratch**: a cadeia alembic tem defeitos históricos (revisão `0002` duplicada; `0016` truncando enum) que podem quebrar `upgrade head` num banco 100% virgem — o ambiente de dev corrente está em `0040`. Dívida documentada em `docs/audit/fullspectrum/`.
> - **Credenciais de dev**: `admin` / `admin`. O bootstrap do primeiro admin **não é scriptado** (`make seed-demo` cria pacientes, não usuários) — em banco novo, crie-o manualmente antes do primeiro login. Dívida rastreada.

**Serviços (nomes reais do `docker-compose.yml`: `api`, `arq-worker`, `frontend-dev`, `postgres`, `redis`, `tests`):**

| Serviço | URL/porta | Descrição |
|---------|-----------|-----------|
| **API** | http://localhost:8000 | REST + WebSocket (FastAPI) |
| **Frontend (Next.js)** | http://localhost:3000 | Dashboard clínico (`frontend-v3/`) |
| **PostgreSQL** | localhost:5432 | `timescale/timescaledb` (pg16) |
| **Redis** | localhost:6379 | `redis:7-alpine` — cache/pub-sub/rate-limit |
| **MLLP Listener** | TCP 2575 | HL7 v2 — **módulo standalone**, não é serviço do compose (ver §MLLP) |

---

## 📖 API — exemplos verificados

Todos os endpoints clínicos exigem **JWT Bearer** (RBAC/ABAC por role clínica). Rate-limit real: 5/min no login, 100/min nos demais.

```bash
# Login (form-urlencoded — a rota /api/v1/auth/login NÃO aceita JSON; a rota legada /auth/login aceita)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=admin' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# Ingestão de vitais (calcula MEWS+NEWS2+SOFA+qSOFA na resposta; recorded_at é OPCIONAL — default now())
curl -X POST http://localhost:8000/api/v1/vitals \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"mpi_id":"MPI-DEMO-004","heart_rate":88,"systolic_bp":125,"diastolic_bp":80,
       "temperature":37.0,"spo2":97,"respiratory_rate":16,"avpu":"A",
       "supplemental_o2":false,"source_system":"philips_monitor"}'

# Detalhe do paciente (vitais 24h com fallback aos N mais recentes, scores, trilhas ativas)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/patients/MPI-DEMO-001/detail
# (/status existe mas está DEPRECATED — 200 null-safe, sem auth, com headers Deprecation/Sunset)

# Dashboard de leitos (unidades reais do seed: UTI-DEMO, UTI-ADULTO, UTI-CORONARIANA)
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/dashboard?unit=UTI-DEMO"

# Alertas — consolidação anti-fadiga por (paciente, sinal) + títulos humanizados (ADR-0039)
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/alerts?group_by=signal"
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/alerts?status=all&severity=critical"

# Projeção de deterioração (regressão linear com R², pontos auditáveis, disclaimer clínico)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/patients/MPI-DEMO-001/deterioration-trend

# CDS Hooks 2.0 (discovery é público; o serviço exige auth + hookInstance)
curl http://localhost:8000/cds-services
```

### WebSocket (tempo real)

```bash
# URL real (o /ws sem prefixo NÃO existe — 403):
wscat -c "ws://localhost:8000/api/v1/ws?token=<JWT>"

# Protocolo: assinatura por CANAL (não por paciente), token em cada mensagem:
# → {"action":"subscribe","channel":"bed_grid.updated","token":"<JWT>"}
# → {"action":"subscribe","channel":"alert.raised","token":"<JWT>"}
# O SERVIDOR envia {"type":"ping"} a cada 30s; o cliente responde {"action":"pong","token":"<JWT>"}.
# Canais publicados: alert.raised, bed_grid.updated, pathway.updated (alert.updated/vitals.updated:
# declarados no contrato, publishers em backlog).
```

### Endpoints principais (87 operações; contrato completo em `docs/contracts/`, drift-check `0 órfãos` no CI)

| Grupo | Rotas |
|-------|-------|
| Saúde | `GET /api/v1/health` (e `GET /health` → 307) |
| Auth | `POST /api/v1/auth/login` (form) · `/logout` · `/refresh` (cookie HttpOnly) · `POST /auth/register` (admin) |
| Admin | `GET/POST /api/v1/admin/users` · `PUT /api/v1/admin/users/{id}` |
| Vitais | `POST /api/v1/vitals` (idempotência por `X-Idempotency-Key` e por chave natural `mpi+recorded_at+source`) |
| Pacientes | `GET /api/v1/patients/{mpi}/detail` · `/deterioration-trend` · `/status` (deprecated) |
| Dashboard | `GET /api/v1/dashboard` (`unit_counts` sempre completo) |
| Alertas | `GET /api/v1/alerts` (`status` incl. `all`, `severity`, `group_by=signal`) · `POST .../{id}/acknowledge|escalate|resolve` (resolve exige enum) · `GET .../{id}/trace` |
| Trilhas | `GET /api/v1/pathways` (12) · `GET /api/v1/patients/{mpi}/pathways` · `.../pathways/{pp}/progress` · `PUT .../criteria` |
| Thresholds | CRUD `GET/POST/PUT/DELETE /api/v1/thresholds` (admin) |
| CDS Hooks | `GET /cds-services` · `POST /cds-services/intensicare-pathway-alerts` |
| Domínios | `stability`, `sedation`, `ventilation`, `movements`, `prescriptions`, `evolucoes`, `clinical-forms`, `documentacao`, `efficiency`, `indicators`, `antimicrobial`, `prophylaxis`, `registry`, `alert-routing`, `events` |
| Tempo real | `WS /api/v1/ws` |

---

## 🧪 Scores Clínicos

| Score | Versão viva | Referência |
|-------|--------|-----------|
| **MEWS** | `MEWS-v3.0.0` | Subbe CP et al., QJM 2001;94(10):521-6 |
| **NEWS2** | `NEWS2-v3.0.0` | Royal College of Physicians, 2017 |
| **SOFA** | `SOFA-v2.0.0` | Vincent et al. |
| **qSOFA** | `qSOFA-v1.0` | Sepsis-3 |

Calculados **sincronamente** a cada ingestão; cada `ClinicalScore` carrega `algorithm_version` (registry versionado — múltiplas versões coexistem para rastreabilidade). A ingestão também dispara a **auto-avaliação das trilhas enroladas** do paciente (~200ms, síncrona) e publica `bed_grid.updated`/`alert.raised` no WebSocket.

---

## 🧬 Inteligência Clínica

> **959 regras clínicas** extraídas do sistema legado (de 1.030 extrações brutas), organizadas em **27 clusters de domínio** ([catálogo completo](docs/rules/README.md)) — distintos dos **24 serviços de domínio** em `services/domain_*.py` — e **12 trilhas declarativas** (YAML content-addressed em `_work/alerts/pathways/`, executadas pelo `TrilhasEngine`, com enrollment **persistente em Postgres** e espelhamento a cada boot via `pathway_definitions_sync.py`).

### Trilhas Clínicas (12)

`sepse` · `estabilidade` · `respiratorio` · `ventilacao`¹ · `sedacao` · `delirium` · `nutricao` · `profilaxia` · `antimicrobiano` · `renal` · `equilibrio` · `desmame`

Cada trilha define estados, critérios com bandas de severidade e recomendações (ex.: SSC-2021 na sepse). A avaliação acontece automaticamente na ingestão de dados; o resumo por critério distingue `met`/`not_met`/`pending` (critérios nunca avaliados não contam como falha). ¹`ventilacao.yaml` é stub incompleto (dívida documentada).

### Alertas — consolidação e humanização ([ADR-0039](docs/adr/ADR-0039-alert-group-read-aggregation.md))

- **Agregação na leitura** por `(paciente, sinal)`: `group_by=signal` — a fonte de verdade nunca é fundida; todo alerta original permanece auditável. Escalação **nunca** é suprimida (flag `escalating` + destaque na UI).
- **Linguagem humanizada em 3 partes** (o que aconteceu / por que importa / o que verificar), com referências clínicas: ex. título `NEWS2 crítico — 17`, corpo citando RCP 2017 / Subbe 2001.
- **Anti-burst**: cooldown por threshold (seed demo: 15 min; fallback de código: 5 min) + rate-limit por hora.
- Ack de grupo = N acks individuais auditáveis, com confirmação de contagem; resolve é sempre individual e exige enum (`false_positive`/`true_positive`/`intervention_done`).

---

## 🛠️ Stack

| Componente | Tecnologia | Versão (pin real) |
|-----------|------------|--------|
| Linguagem | Python | ≥3.12 (CI: 3.12 e 3.13) |
| API | FastAPI | ≥0.115,<1.0 |
| ORM | SQLAlchemy (async) | ≥2.0,<3.0 |
| Banco | PostgreSQL + TimescaleDB | timescale/timescaledb pg16 |
| Cache/filas | Redis (servidor 7; client py `redis` ≥5,<6) + arq | — |
| Auth | JWT (python-jose) + **bcrypt direto** (sem passlib) | access 30 min · refresh 7 dias (cookie HttpOnly) |
| HL7 | hl7apy | ≥1.3,<2.0 |
| Frontend | Next.js / React / Tailwind / SWR | 16.2 / 19.2 / 4 / 2.4 |
| Qualidade | Ruff · MyPy (`strict = true`) · pytest | ≥0.4 · ≥1.10,<2.0 · **≥9.0,<10.0** |
| Migrações | Alembic | ≥1.13,<2.0 (43 revisões) |
| E2E | Playwright (`frontend-v3/e2e/`) + axe-core | — |

---

## 🧪 Testes

```bash
make test                          # ou:
PYTHONPATH=src .venv/bin/python -m pytest tests/ -q
make test-cov                      # com cobertura
cd frontend-v3 && npx tsc --noEmit && npm run lint && npx playwright test e2e/smoke.spec.ts
```

**Estado da suíte (2026-07-13): 2975 passed · 1 xfailed · 0 failed · 0 errors** (94 arquivos de teste, incluindo `tests/contract/`, `tests/property/`, `tests/rules/`, `tests/drills/`, `tests/storm/`). Exclusões documentadas no `pyproject.toml` (testes dos módulos `maezo`/`prescricao` pré-v3.2.0 — reescrita em backlog). O job **Test — Python (3.12/3.13)** roda no CI; required checks: Lint & Type Check, Security Scan, Frontend — Lint & Build.

---

## 📂 Estrutura (resumo real)

```
intensicare/
├── src/intensicare/
│   ├── main.py                  # FastAPI + lifespan (sync de pathways no boot)
│   ├── config.py                # pydantic-settings (.env — sem comentários inline!)
│   ├── mllp_listener.py         # Servidor TCP MLLP (HL7 v2) — standalone
│   ├── api/                     # vitals, patients, thresholds, clinical_forms, reference_ranges
│   │   └── v1/                  # 24 routers: auth, admin, alerts, dashboard, pathways, ws,
│   │                            #   cds_hooks, deterioration, registry, domínios clínicos…
│   ├── auth/                    # jwt, dependencies (RBAC), abac, iam
│   ├── core/                    # database, redis, websocket, rate_limit, security_headers,
│   │                            #   secrets, telemetry, metrics
│   ├── models/                  # 26 módulos de modelo (43 classes: vitals, scores, alerts,
│   │                            #   pathways, audit_trail…)
│   ├── schemas/                 # Pydantic (contratos espelhados em docs/contracts/)
│   └── services/                # engines de score, alert_engine + alert_copy (humanização),
│                                #   pathway_enrollment/TrilhasEngine, dashboard, 24× domain_*
├── tests/                       # 94 arquivos (unit, contract, property, rules, drills, storm)
├── frontend-v3/                 # Next.js 16 (App Router) — frontend VIVO
├── frontend-v2-archive/         # legado arquivado (não usar)
├── alembic/versions/            # 43 migrações
├── _work/alerts/pathways/       # 12 trilhas YAML (content-addressed)
├── docs/                        # contracts/ (28 OpenAPI), adr/, audit/, rules/, product/
├── docker-compose.yml           # api, arq-worker, frontend-dev*, postgres, redis, tests
└── Makefile                     # 44 targets (make help)
```

---

## 🏥 Integração Hospitalar (MLLP)

Listener HL7 v2 ORU-R01 (framing `<VT>…<FS><CR>`, ACK AA/AE/AR, LOINC → vitais, idempotência por `MSH-10`). **Não é um serviço do docker-compose** — rode como módulo:

```bash
python -m intensicare.mllp_listener --host 0.0.0.0 --port 2575 --api-url http://localhost:8000/api/v1
```

LOINC suportados: `8867-4` (FC), `8480-6`/`8462-4` (PA), `8310-5` (temp), `2708-6`/`59408-5` (SpO₂), `9279-1` (FR), `11488-4` (AVPU) + aliases (`HR`, `SBP`, `TEMP`…).

---

## 🔐 Autenticação e RBAC

- Login: `POST /api/v1/auth/login` **form-urlencoded**; sessão sobrevive a F5/deep-link via `POST /auth/refresh` (cookie HttpOnly); logout blacklista access+refresh no Redis.
- Roles clínicas (ABAC): `admin`, `medico`, `enfermeiro`, `fisioterapeuta`, `farmacia`, `nutricao`, `readonly` — aplicadas nos routers clínicos.
- Gestão de usuários: UI em `/admin` (criação com role) ou `GET/POST /api/v1/admin/users`.
- PHI: `display_name` cifrado com pgcrypto no banco; descriptografia controlada na leitura.

## ⚙️ Thresholds

```bash
curl -X POST http://localhost:8000/api/v1/thresholds \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"tenant_id":"austa","unit":"UTI-DEMO","score_type":"MEWS",
       "watch_threshold":3,"urgent_threshold":4,"critical_threshold":5,
       "rate_limit_per_hour":10,"cooldown_minutes":15}'
```

---

## 🔒 Segurança e Compliance

| Dimensão | Status |
|----------|--------|
| **ANVISA SaMD** | Classe II — análise preliminar; **validação clínica independente formal PENDENTE** (bloqueador de produção) |
| **LGPD** | Conformidade por design (PHI cifrada, audit trail imutável via trigger); RIPD pendente |
| **CFM** | Resolução 1.821/07 (prontuário eletrônico) |

Práticas implementadas: bcrypt · JWT 30min/7d + blacklist Redis · CSP com nonce por request · headers de segurança · rate-limit (login 5/min, API 100/min) · trilha de auditoria append-only (hypertable + trigger) · idempotência de ingestão · a11y WCAG 2.1/2.2 AA verificada por axe em runtime.

---

## 🤝 Contribuindo

```bash
pip install -e ".[dev]" && pre-commit install --hook-type pre-commit --hook-type commit-msg
make check          # lint (ruff check+format, mypy strict) + testes
```

Regras da casa: contratos OpenAPI regenerados do `app.openapi()` (drift-check no CI); mudanças de UI verificadas com axe em runtime (lint estático de JSX produz falso-positivos); prova de correção = comportamento real (browser/curl), não só teste verde.

## ⚠️ Dívidas conhecidas (honestidade > marketing)

- `docker-compose.yml` → `frontend-dev` monta `./frontend-v2` (inexistente); usar `frontend-v3/` local.
- Bootstrap do primeiro usuário admin não é scriptado.
- Cadeia alembic quebra `upgrade head` em banco virgem (0002 duplicada / 0016).
- `ventilacao.yaml` stub; publishers WS `alert.updated`/`vitals.updated` pendentes; campo `unit` não estruturado em `Alert`.
- Suíte de `prescricao`/`maezo` excluída aguardando reescrita (ignores documentados no `pyproject.toml`).

## 📜 Licença

Proprietária. Todos os direitos reservados.

---

<div align="center">

**Desenvolvido pela equipe Intensicare — tecnologia que salva vidas na UTI**

</div>
