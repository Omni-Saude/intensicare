# Intensicare 🏥⚡

**Plataforma de monitoramento contínuo para UTI — FastAPI + TimescaleDB + Redis**

> **Status: MVP Funcional — `v0.1.0-alpha` (Junho 2026)**
>
> Stack implementada: **Python 3.12 + FastAPI + SQLAlchemy (async) + PostgreSQL/TimescaleDB + Redis**.
> Quatro engines de scoring clínico (MEWS, NEWS2, SOFA, qSOFA), ingestão HL7 v2 via MLLP,
> alertas em tempo real via WebSocket, e dashboard clínico React.

---

## 📋 Navegação Rápida

| Para | Vá para |
|------|---------|
| **Status do projeto** | [`PROJECT_STATUS.md`](PROJECT_STATUS.md) |
| **Visão do produto** | [`docs/product/vision.md`](docs/product/vision.md) |
| **Documentação da API** | [`docs/api/overview.md`](docs/api/overview.md) |
| **Política de segurança** | [`SECURITY.md`](SECURITY.md) |
| **Fila regulatória** | [`docs/review-queue.md`](docs/review-queue.md) |
| **Plano de implementação** | [`docs/implementation-plan.md`](docs/implementation-plan.md) |
| **Arquitetura (ADR)** | [`docs/architecture/adr/ADR-001-amh-data-platform-consumer.md`](docs/architecture/adr/ADR-001-amh-data-platform-consumer.md) |

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Git

### Iniciar o ambiente de desenvolvimento

```bash
# Clonar o repositório
git clone https://github.com/Omni-Saude/intensicare.git
cd intensicare

# Subir banco + Redis + API + frontend
docker compose up -d

# Verificar saúde da API
curl http://localhost:8000/health

# Acessar documentação interativa (Swagger)
open http://localhost:8000/docs
```

**Serviços disponíveis:**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **API** | http://localhost:8000 | API REST + WebSocket |
| **Swagger UI** | http://localhost:8000/docs | Documentação interativa OpenAPI |
| **Redoc** | http://localhost:8000/redoc | Documentação alternativa |
| **MLLP Listener** | TCP port 2575 | Ingestão HL7 v2 |
| **Frontend (React)** | http://localhost:3000 | Dashboard clínico |
| **PostgreSQL** | localhost:5432 | Banco (TimescaleDB) |
| **Redis** | localhost:6379 | Cache / rate limiting |

### Ingestão de sinais vitais

```bash
# Enviar sinais vitais para a API
curl -X POST http://localhost:8000/api/v1/vitals \
  -H "Content-Type: application/json" \
  -d '{
    "mpi_id": "MPI-00012345",
    "recorded_at": "2026-06-26T10:00:00Z",
    "heart_rate": 88,
    "systolic_bp": 125,
    "diastolic_bp": 80,
    "temperature": 37.0,
    "spo2": 97,
    "respiratory_rate": 16,
    "avpu": "A",
    "supplemental_o2": false,
    "source_system": "philips_monitor"
  }'

# Resposta inclui MEWS, NEWS2, SOFA e qSOFA calculados automaticamente
```

### Consultar status do paciente

```bash
# Status agregado com score + tendência
curl http://localhost:8000/api/v1/patients/MPI-00012345/status
```

### Dashboard (leitos)

```bash
# Grid de leitos com scores e alertas
curl http://localhost:8000/api/v1/dashboard

# Filtrar por unidade
curl "http://localhost:8000/api/v1/dashboard?unit=UTI-A"
```

### WebSocket (alertas em tempo real)

```bash
# Conectar via wscat ou ferramenta similar
wscat -c ws://localhost:8000/ws

# No WebSocket:
# {"action": "subscribe", "patient_id": "MPI-00012345"}
# {"action": "ping"}
```

---

## 📖 Documentação da API

A documentação interativa completa está disponível em:

- **Swagger UI:** http://localhost:8000/docs
- **Redoc:** http://localhost:8000/redoc

### Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/auth/login` | Login (retorna JWT) |
| `POST` | `/auth/register` | Registro (admin-only) |
| `POST` | `/auth/logout` | Logout (blacklist token) |
| `POST` | `/api/v1/vitals` | Ingerir sinais vitais (calcula MEWS + NEWS2 + SOFA + qSOFA) |
| `GET` | `/api/v1/patients/{mpi_id}/status` | Status do paciente |
| `GET` | `/api/v1/patients/{mpi_id}/detail` | Detalhes do paciente (24h) |
| `GET` | `/api/v1/dashboard` | Dashboard de leitos |
| `GET` | `/api/v1/alerts` | Listar alertas |
| `POST` | `/api/v1/alerts/{id}/acknowledge` | Confirmar alerta |
| `GET` | `/api/v1/alerts/{id}/trace` | Rastrear alerta |
| `GET` | `/api/v1/thresholds` | Listar thresholds (admin) |
| `POST` | `/api/v1/thresholds` | Criar threshold (admin) |
| `PUT` | `/api/v1/thresholds/{id}` | Atualizar threshold (admin) |
| `DELETE` | `/api/v1/thresholds/{id}` | Remover threshold (admin) |
| `WS` | `/ws` | WebSocket para alertas em tempo real |

> Documentação completa de cada endpoint com exemplos: [`docs/api/overview.md`](docs/api/overview.md)

---

## 🧪 Scores Clínicos Implementados

| Score | Engine | Versão | Validação |
|-------|--------|--------|-----------|
| **MEWS** | Modified Early Warning Score | `MEWS-v3.0.0` (Subbe CP et al., QJM 2001;94(10):521-6) | ✅ Testes unitários + integração |
| **NEWS2** | National Early Warning Score 2 | `NEWS2-v3.0.0` | ✅ Testes unitários + integração |
| **SOFA** | Sequential Organ Failure Assessment | `SOFA-v2.0.0` | ✅ Testes unitários |
| **qSOFA** | Quick SOFA (Sepsis Screening) | `qSOFA-v1.0` | ✅ Testes unitários |

Todos os scores são calculados **sincronamente** após cada ingestão de sinais vitais.
Cada ClinicalScore registrado inclui `algorithm_version` para rastreabilidade completa.

---

## 🧬 Inteligência Clínica — Motor de Regras

> **188 regras clínicas** extraídas do sistema legado (463 arquivos TypeScript + 153
> LESS), organizadas em **25 clusters de regras legadas** (taxonomia da extração — ver
> tabela abaixo; distinta dos **24 serviços de domínio** em `services/domain_*.py`) e
> **12 trilhas declarativas** (YAML
> content-addressed em `_work/alerts/pathways/`, executadas pelo `TrilhasEngine` e
> espelhadas em Postgres a cada boot via `pathway_definitions_sync.py`).
>
> API: **82 endpoints** com contrato OpenAPI correspondente em `docs/contracts/` (0
> órfãos — `scripts/ci/check_openapi_drift.py`). Early warning score: **MEWS v3.0.0**
> (Subbe CP et al., QJM 2001;94(10):521-6).
>
> Ciclo de correção pós-auditoria (2026-07-12): ver [`docs/audit/fullspectrum/`](docs/audit/fullspectrum/).

### 📊 Domínios Clínicos (25 clusters de regras)

| # | Domínio | Escopo | Batches |
|---|---------|--------|---------|
| 1 | **Sepse** | 13 batches, 20 critérios (≥3 maiores + ≥4 menores = 🔴 Crítico). Lactato, PAM, PAS, PAD, noradrenalina | 13 |
| 2 | **Estabilidade Hemodinâmica** | Vasopressores (noradrenalina mcg/kg/min), choque oculto/séptico, balanço negativo, bicarbonato, enchimento capilar >5s | 4 |
| 3 | **Balanço Hídrico** | Ganhos/perdas, diurese (KDIGO oligúria), balanço acumulado, reposição volêmica | 7 |
| 4 | **Ventilação Mecânica** | Desmame, FiO₂, PEEP, drive pressórico, relação P/F | 3 |
| 5 | **Sedação** | RASS, CAM-ICU (delirium), BPS/NRS (dor), infusão contínua | 5 |
| 6 | **Piora Clínica** | Escore de alerta precoce composto (deterioração multissistêmica) | 3 |
| 7 | **Clinical Scoring** | MEWS (≥5 crítico), NEWS2 (≥7 crítico), SOFA (0-24 bandas), qSOFA | 4 |
| 8 | **Nutrição** | Tolerância, VRG >500mL/6h, diarreia, NPT, hiperglicemia | 1 |
| 9 | **Profilaxia** | Úlcera de estresse (IBP/cimetidina), TEV, sangramento GI | 1 |
| 10 | **Antimicrobiano** | Escalonamento, tempo de antibiótico, culturas | 1 |
| 11 | **Prescrição** | Conciliação medicamentosa, reconciliação de admissão | 1 |
| 12 | **Movimentação ADT** | Admissão/transferência/alta, tempo de permanência em UTI | 3 |
| 13 | **Evoluções** | Documentação clínica diária obrigatória | 1 |
| 14 | **Sinais Vitais** | Frequência de coleta, thresholds por vital, completude | 1 |
| 15 | **Comunicação** | Passagem de plantão estruturada, handoff sheet | 1 |
| 16 | **Equilíbrio Hidroeletrolítico** | Eletrólitos (Na, K, Mg, Ca, P), bandas KDIGO para fosfato | 1 |
| 17 | **Eficiência Operacional** | Tempo de resposta a alertas, tempo de resolução | 2 |
| 18 | **Indicadores ETL** | Métricas de qualidade UTI, dashboards de gestão | 2 |
| 19 | **Formulários Clínicos** | RASS, CAM-ICU, BPS-NRS, documentação estruturada | 2 |
| 20 | **Auditoria & Logs** | Trilha de auditoria imutável para compliance regulatório | 1 |
| 21 | **Auth & Usuários** | Perfis clínicos, permissões ABAC, MFA | 1 |
| 22 | **Tenancy & Organização** | Multi-tenant, white-label por hospital, hierarquia empresa/estabelecimento/setor | 4 |
| 23 | **Documentação & Faturamento** | AIH, procedimentos, codificação | 1 |
| 24 | **Operacional & Infra** | Watchdog, health checks, Redis, telemetria | 3 |
| 25 | **Trilhas Engine** | Motor de execução das trilhas clínicas | 1 |

### 🚨 Alertas Críticos

| Alerta | Severidade | Gatilho |
|--------|-----------|---------|
| MEWS CRITICAL | 🔴 Critical | MEWS ≥ 5 |
| NEWS2 CRITICAL | 🔴 Critical | NEWS2 ≥ 7 |
| SEPSE VERMELHO | 🔴 Critical | ≥3 critérios maiores + ≥4 menores simultâneos |
| SEPSE AMARELO | 🟡 Watch | ≥2 maiores + ≥3 menores |
| Choque Séptico | 🔴 Critical | Noradrenalina + lactato > 2 mmol/L |
| Choque Oculta | 🟠 Urgent | Lactato > 2 sem hipotensão |
| IRA KDIGO | 🟠 Urgent | Diurese < 0.5 mL/kg/h por 6h |
| Delirium CAM-ICU+ | 🟡 Watch | CAM-ICU positivo |
| Balanço Negativo | 🟡 Watch | Balanço < −2000mL com vasopressor |
| VRG Elevado | 🟡 Watch | Volume residual gástrico > 500mL/6h |

### 🔄 Trilhas Clínicas (Care Pathways)

Cada trilha é um **pipeline de avaliação contínua** executado a cada novo dado
(vital, exame, balanço) que gera recomendações e alertas para a equipe:

| Trilha | Domínios | O que avalia |
|--------|----------|-------------|
| **Trilha Sepse** | Sepse + Estabilidade | Screening contínuo (20 critérios), classificação dual-threshold, alerta automático com gravidade |
| **Trilha Estabilidade** | Estabilidade + Balanço Hídrico | Monitoramento hemodinâmico (vasopressores, perfusão, choque, balanço) |
| **Trilha Ventilação** | Ventilação + Sinais Vitais | Desmame ventilatório, parâmetros de drive pressórico, P/F |
| **Trilha Sedação** | Sedação + Delirium | RASS diário, CAM-ICU, BPS/NRS, interrupção diária da sedação |
| **Trilha Nutrição** | Nutrição + Profilaxia | Tolerância, VRG, progressão de dieta, profilaxia de úlcera/TEV |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│  Fontes de Dados                                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ Monitores│  │ HL7 (MLLP)│  │  AMH Data     │  │
│  │ Philips  │  │ TCP:2575  │  │  Platform     │  │
│  └────┬─────┘  └─────┬─────┘  └──────┬───────┘  │
└───────┼──────────────┼───────────────┼───────────┘
        │              │               │
        ▼              ▼               ▼
┌─────────────────────────────────────────────────┐
│              Intensicare API (FastAPI)            │
│  ┌─────────────┐  ┌──────────────┐              │
│  │ Vitals      │  │ Alert Engine │              │
│  │ Ingestion   │  │ (Redis RL)   │              │
│  └──────┬──────┘  └──────┬───────┘              │
│         │                │                       │
│  ┌──────▼────────────────▼───────┐              │
│  │     Scoring Engines           │              │
│  │  MEWS | NEWS2 | SOFA | qSOFA  │              │
│  └──────────────┬────────────────┘              │
│                 │                                │
│  ┌──────────────▼────────────────┐              │
│  │     WebSocket Manager          │              │
│  │     (broadcast em tempo real)  │              │
│  └───────────────────────────────┘              │
└──────────┬──────────────────┬───────────────────┘
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│ PostgreSQL 16    │  │ Redis 7          │
│ + TimescaleDB    │  │ cache / pubsub   │
│ (dados + scores) │  │ / rate limiting  │
└──────────────────┘  └──────────────────┘
```

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia | Versão |
|-----------|------------|--------|
| **Linguagem** | Python | 3.12+ |
| **Framework API** | FastAPI | 0.115+ |
| **ORM** | SQLAlchemy (async) | 2.0+ |
| **Banco** | PostgreSQL + TimescaleDB | 16 / 2.x |
| **Cache / Queue** | Redis | 7 |
| **Autenticação** | JWT (python-jose) + bcrypt | — |
| **HL7 Parser** | hl7apy | 1.0+ |
| **Linter** | Ruff | 0.4+ |
| **Type Checker** | MyPy (strict) | 1.10+ |
| **Testes** | pytest + pytest-asyncio | 8.2+ |
| **Migrations** | Alembic | 1.13+ |
| **Container** | Docker Compose | v2+ |

---

## 🧪 Testes

```bash
# Executar todos os testes
docker compose exec api pytest tests/ -v

# Ou com o ambiente local:
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=src/intensicare --cov-report=term-missing
```

Cobertura de testes inclui:
- `test_mews.py` — Validação do algoritmo MEWS
- `test_news2.py` — Todos os 7 parâmetros do NEWS2
- `test_sofa.py` — 6 sistemas orgânicos do SOFA
- `test_qsofa.py` — 3 critérios binários do qSOFA
- `test_vitals.py` — Ingestão, idempotência, status do paciente
- `test_auth.py` — Login, registro, JWT
- `test_alerts.py` — CRUD de alertas, acknowledge
- `test_alert_engine.py` — Thresholds, rate limiting, cooldown
- `test_thresholds.py` — CRUD de thresholds
- `test_websocket.py` — WebSocket connect/subscribe/broadcast
- `test_mllp_listener.py` — MLLP framing, parsing HL7
- `test_main.py` — Health check

---

## 📂 Estrutura do Repositório

```
intensicare/
├── src/intensicare/
│   ├── main.py              # Aplicação FastAPI + lifespan
│   ├── config.py            # Configuração centralizada (pydantic-settings)
│   ├── auth.py              # Dependências de autenticação
│   ├── mllp_listener.py     # Servidor TCP MLLP (HL7 v2)
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py      # POST /auth/login, /auth/register, /auth/logout
│   │   │   ├── alerts.py    # GET/POST /api/v1/alerts
│   │   │   ├── dashboard.py # GET /api/v1/dashboard, /patients/{id}/detail
│   │   │   └── __init__.py
│   │   ├── vitals.py        # POST /api/v1/vitals
│   │   ├── patients.py      # GET /api/v1/patients/{id}/status
│   │   └── thresholds.py    # CRUD /api/v1/thresholds
│   ├── auth/
│   │   ├── jwt.py           # Criação/verificação de tokens JWT
│   │   └── dependencies.py  # get_current_user, require_admin
│   ├── core/
│   │   ├── database.py      # Engine SQLAlchemy async + session
│   │   ├── redis.py         # Cliente Redis (lazy init)
│   │   └── websocket.py     # WebSocket Manager
│   ├── models/              # SQLAlchemy models (6 tabelas)
│   │   ├── vital_sign.py
│   │   ├── clinical_score.py
│   │   ├── alert.py
│   │   ├── threshold_config.py
│   │   ├── patient_cache.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Lógica de negócio
│       ├── vitals.py        # Ingestão + idempotência
│       ├── mews.py          # Engine MEWS
│       ├── news2.py         # Engine NEWS2
│       ├── sofa.py          # Engine SOFA
│       ├── qsofa.py         # Engine qSOFA
│       ├── alert_engine.py  # Verificação de thresholds + rate limiting
│       ├── patients.py      # Consulta de status
│       └── dashboard.py     # Agregação do dashboard
├── tests/                   # 12 arquivos de teste
├── frontend/                # Dashboard React + TypeScript + Vite
│   ├── src/
│   │   ├── components/      # BedGrid, PatientDetail, AlertPanel, etc.
│   │   ├── hooks/           # useAuth
│   │   ├── api/             # Cliente HTTP
│   │   └── types/           # Tipos TypeScript
│   └── Dockerfile
├── alembic/                 # Migrações de banco
│   └── versions/            # 3 migrações
├── Dockerfile               # Multi-estágio (dev + prod)
├── docker-compose.yml       # API + DB + Redis + MLLP + Frontend
├── Makefile                 # 25+ comandos
├── pyproject.toml           # Build + tool config
└── docs/                    # Documentação
    ├── api/overview.md
    ├── product/
    ├── architecture/adr/
    ├── data/
    └── implementation-plan.md
```

---

## 🏥 Integração Hospitalar (MLLP)

O Intensicare inclui um **MLLP Listener** que recebe mensagens HL7 v2 ORU-R01 diretamente de monitores e sistemas hospitalares.

### Como funciona

1. O Listener escuta na porta TCP **2575** (padrão MLLP)
2. Recebe mensagens com framing MLLP (`<VT>...<FS><CR>`)
3. Parseia segmentos MSH, PID, OBR, OBX via `hl7apy`
4. Mapeia códigos LOINC → campos de sinais vitais
5. Encaminha como JSON para `POST /api/v1/vitals` com `X-Idempotency-Key: MSH-10`
6. Retorna ACK HL7 (`AA` = sucesso, `AE` = erro, `AR` = rejeição)

### Iniciar o MLLP Listener

```bash
# Via Docker Compose (já incluso)
docker compose up -d mllp-listener

# Ou manualmente:
python -m intensicare.mllp_listener --host 0.0.0.0 --port 2575 --api-url http://localhost:8000/api/v1
```

### LOINC Codes Suportados

| LOINC | Campo |
|-------|-------|
| 8867-4 | heart_rate |
| 8480-6 | systolic_bp |
| 8462-4 | diastolic_bp |
| 8310-5 | temperature |
| 2708-6, 59408-5 | spo2 |
| 9279-1 | respiratory_rate |
| 11488-4 | avpu |

Codes alternativos (não-LOINC) como `PULSE`, `HR`, `SBP`, `TEMP`, `SPO2`, `RR`, `AVPU` também são suportados.

---

## 🔐 Autenticação

A API usa **JWT Bearer tokens** para autenticação:

```bash
# Registrar usuário (admin-only)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin:admin" \
  -d '{
    "username": "medico01",
    "email": "medico@hospital.com",
    "password": "senha-segura-123",
    "display_name": "Dr. Silva"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "medico01", "password": "senha-segura-123"}'

# Usar token nos endpoints protegidos
curl http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer <access_token>"
```

---

## ⚙️ Configuração (Thresholds)

Os thresholds de alerta são configuráveis por tenant e unidade (admin-only):

```bash
# Criar threshold para MEWS
curl -X POST http://localhost:8000/api/v1/thresholds \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin:admin" \
  -d '{
    "tenant_id": "hospital-austa",
    "unit": "UTI-A",
    "score_type": "MEWS",
    "watch_threshold": 3,
    "urgent_threshold": 5,
    "critical_threshold": 7,
    "rate_limit_per_hour": 10,
    "cooldown_minutes": 15
  }'
```

---

## 🔒 Segurança e Compliance

### Status Regulatório

| Dimensão | Status |
|----------|--------|
| **ANVISA SaMD** | Classe II — análise preliminar; consultoria pendente |
| **LGPD** | Conformidade por design; RIPD pendente |
| **SBIS** | Plano de certificação elaborado |
| **CFM** | Conformidade com Resolução 1.821/07 (prontuário eletrônico) |

> Detalhes: [`docs/review-queue.md`](docs/review-queue.md) e [`docs/implementation-plan.md`](docs/implementation-plan.md#5-compliance-baseline)

### Práticas de Segurança Implementadas

- **Senhas**: hash bcrypt (via passlib)
- **JWT**: tokens com expiração (30 min access, 7 dias refresh)
- **Token Blacklist**: Redis para revogação de tokens
- **CORS**: configurável via `cors_origins`
- **Rate Limiting**: Redis-based no alert engine
- **Idempotência**: `X-Idempotency-Key` (MSH-10) na ingestão de vitais
- **Secrets**: `SecretStr` do Pydantic para senhas e chaves

---

## 🤝 Contribuindo

### Setup de desenvolvimento

```bash
# Setup inicial
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Pre-commit hooks
pre-commit install --hook-type pre-commit --hook-type commit-msg

# Lint + testes
ruff check src tests
mypy src/intensicare
pytest tests/ -v
```

### Antes de commitar

```bash
make check   # lint + test
```

---

## 📞 Suporte

Para questões técnicas, abra uma issue no repositório.
Para questões clínicas/regulatórias, consulte [`docs/review-queue.md`](docs/review-queue.md).

---

## 📜 Licença

Proprietária. Todos os direitos reservados.

---

<div align="center">

**Desenvolvido pela equipe Intensicare — tecnologia que salva vidas na UTI**

</div>
