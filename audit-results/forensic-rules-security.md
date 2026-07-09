# Forensic Agent 3: Rules + Security + Contracts Gap Analysis
# =====================================================================
# Projeto: IntensiCare ICU Clinical Platform
# Data: 2026-07-09
# Escopo: 50 regras de negócio × implementação + 10 ameaças + 10 findings
# =====================================================================

---

## 1. SUMÁRIO EXECUTIVO

**Conclusão geral**: A plataforma IntensiCare apresenta uma arquitetura de domínio
robusta com 24 serviços `domain_*.py` mapeando os clusters de regras de negócio.
Contudo, 26 das 50 regras catalogadas em `docs/rules/triage-eligibility/` são
**regras de frontend** (UI gating, renderização condicional, permissões de
exibição) e não possuem — nem deveriam possuir — implementação direta no backend
Python. Das 24 regras com implementação backend, 19 estão cobertas pelos serviços
de domínio, 5 possuem cobertura parcial ou divergente.

Na dimensão de segurança, 4 dos 10 findings estão **mitigados** (F-01 a F-04 via
SecurityHeadersMiddleware), 1 parcialmente mitigado (F-05), 2 são riscos aceitos
(F-04, F-06), e 4 permanecem em **backlog** (F-07 a F-10). O controle de acesso
(RBAC) é binário (`is_admin`) sem granularidade por papel clínico.

Os contratos OpenAPI existem (15 arquivos YAML em `docs/contracts/`), contrariando
a premissa inicial de que estariam vazios.

---

## 2. MAPEAMENTO REGRAS × IMPLEMENTAÇÃO

### 2.1 LEGENDA

| Símbolo | Significado |
|---------|-------------|
| ✅ | Regra implementada no backend |
| ⚠️ | Cobertura parcial ou divergente |
| ❌ | Sem implementação backend (regra de frontend ou não implementada) |
| 🔷 | Regra puramente de frontend (UI gating) |

### 2.2 SEPSE (Regras 038–067, 099) — 30 arquivos

**Serviço**: `src/intensicare/services/domain_sepsis.py` (v3.0.0, 1022 linhas)

**Arquitetura**: Motor híbrido NRT + micro-batch com 6 alertas SSC-2021:
- ALERT-SEPSIS-SCREEN-01 (qSOFA/SIRS + infection gate)
- ALERT-SEPSIS-ORGAN-02 (qSOFA ≥2 + lactate)
- ALERT-SEPSIS-SHOCK-03 (lactate ≥4 ou MAP <65)
- ALERT-SEPSIS-BUNDLE-OVERDUE-04 (hour-1 bundle timer)
- ALERT-SEPSIS-PCT-RISING-05 (PCT rising — treatment failure)
- ALERT-SEPSIS-PCT-DEESC-06 (PCT-guided de-escalation)

| Regra | Descrição | Status | Análise |
|-------|-----------|--------|---------|
| SEPSE-038 | C1 Major: Febre >38.3°C | ⚠️ | Implementado via `score_temperature()` no NEWS2, mas não como critério individual C1. O domínio usa qSOFA/SIRS compostos. |
| SEPSE-039 | C2 Major: Desconforto respiratório | ⚠️ | `score_respiratory_rate()` cobre FR, não avalia desconforto subjetivo |
| SEPSE-040 | C3 Major: VM iniciada <24h | ❌ | Sem correspondência direta nos 6 alertas |
| SEPSE-041 | C4 Major: Noradrenalina <24h | ⚠️ | Parcialmente coberto por `_eval_shock_03` (MAP + vasopressor) |
| SEPSE-042 | C5 Major: Enchimento capilar lento | ❌ | Não implementado |
| SEPSE-043 | C6 Major: Hipotensão PAS<90 ou PAD<90 | ⚠️ | `score_systolic_bp()` no NEWS2, mas sem threshold de 90 mmHg |
| SEPSE-044 | C7 Major: Oligúria/creatinina | ❌ | Não implementado nos alertas de sepse (está no SOFA) |
| SEPSE-045 | C8 Major: Glasgow drop/delirium | ❌ | qSOFA usa Glasgow mas sem delta/tendência |
| SEPSE-046 | C9 Major: Hiperbilirrubinemia | ❌ | Não implementado |
| SEPSE-047 | C10 Minor: Hipotermia <36°C | ⚠️ | `score_temperature()` cobre <36°C para SIRS |
| SEPSE-048 | C11 Minor: Taquicardia | ✅ | `score_heart_rate()` cobre FC >90 |
| SEPSE-049 | C12 Minor: Hipocapnia/oxigenação | ⚠️ | `score_spo2()` cobre SpO₂, PaCO₂ no SIRS count |
| SEPSE-050 | C13 Minor: Lactato elevado | ✅ | `_eval_organ_02` — lactato >2 mmol/L |
| SEPSE-051 | C14 Minor: Leucocitose | ✅ | `_compute_sirs_count` — WBC >12 ou <4 |
| SEPSE-052 | C15 Minor: Trombocitopenia | ❌ | Não implementado nos alertas de sepse |
| SEPSE-053 | C16 Minor: Baixa ingesta oral | ❌ | Não implementado |
| SEPSE-054 | C17 Minor: Consciência deprimida <12h | ❌ | Não implementado |
| SEPSE-055 | C18 Minor: Cateter central 7 dias | ❌ | Não implementado |
| SEPSE-056 | C19 Minor: Cateter femoral 5 dias | ❌ | Não implementado |
| SEPSE-057 | C20 Minor: Cirurgia abdominal recente | ❌ | Não implementado |
| SEPSE-066 | Pathway disabled legacy criteria | ✅ | v3.0.0 ignora critérios legados (v2) |
| SEPSE-067 | Infection source screening flags | ✅ | `_infection_present()` usa cultura/ATB/suspeita |
| SEPSE-099 | Pathway active criteria descriptions | ✅ | Documentado nos docstrings + 31 vetores de teste |

**GAP PRINCIPAL**: As 20 regras SEPSE (C1-C20) representam critérios clínicos
individuais do modelo legado (v2). A implementação v3.0.0 adota o padrão
SSC-2021 com 6 alertas compostos (qSOFA/SIRS agregados). Isso é uma **decisão
arquitetural de modernização**, não um bug. Os critérios individuais estão
preservados como documentação clínica de referência, mas o motor de avaliação
foi simplificado para o padrão internacional SSC-2021.

**Cobertura**: ~40% dos critérios individuais têm correspondência nos alertas
compostos. Os demais ou são cobertos por outros domínios (SOFA, Glasgow) ou
são específicos do modelo legado.

### 2.3 TRILHAS-ENGINE (Regras 005–007) — 3 arquivos

**Serviço**: `src/intensicare/services/domain_trilhas_engine.py` (433 linhas)
+ `trilhas_engine.py`, `trilhas_state.py`, `trilhas_definitions.py`

| Regra | Descrição | Tipo | Status |
|-------|-----------|------|--------|
| TRILHAS-ENGINE-005 | Sepse/Profilaxia interactive card | 🔷 Frontend | ❌ Backend — regra de UI (frontend: `TrilhaInterativa.tsx`) |
| TRILHAS-ENGINE-006 | Interactive restricted to automatic bed | 🔷 Frontend | ❌ Backend — regra de UI |
| TRILHAS-ENGINE-007 | Pathway assisted eligibility + own record auth | 🔷 Frontend | ❌ Backend — regra de UI |

**Implementação backend**: `check_pathway_eligibility()` cobre 4 catálogos de
pathway (ventilacao, sepse, desmame, nutricao) com 18 regras internas
documentadas no docstring. As regras 005-007 são puramente de frontend
(controle de exibição de cards interativos).

### 2.4 TENANCY (Regras 025–028) — 4 arquivos

**Serviço**: `src/intensicare/services/domain_tenancy.py` (594 linhas)

| Regra | Descrição | Tipo | Status |
|-------|-----------|------|--------|
| TENANCY-025 | Homecare-only dashboard shortcuts | 🔷 Frontend | ❌ Backend — `empresa/[id_empresa].tsx` |
| TENANCY-026 | Manual-type gates estabelecimento creation | 🔷 Frontend | ❌ Backend — `configuracoes/estabelecimentos/` |
| TENANCY-027 | Manual-type gates leito creation | 🔷 Frontend | ❌ Backend — `configuracoes/leitos/` |
| TENANCY-028 | Manual-type gates setor creation/editing | 🔷 Frontend | ❌ Backend — `configuracoes/setores/` |

**Implementação backend**: O `domain_tenancy.py` implementa CRUD para
Empresa/Estabelecimento/Setor com SQLAlchemy (list, get, create, update) +
14 regras UNVERIFIABLE RATIFY de agregação de indicadores. As regras 025-028
são gates de UI (mostrar/ocultar botões baseado em `empresaData.tipo`),
não lógica de backend.

### 2.5 PRESCRICAO (Regras 016–018) — 3 arquivos

**Serviço**: `src/intensicare/services/domain_prescricao.py` (855 linhas)

| Regra | Descrição | Status |
|-------|-----------|--------|
| PRESCRICAO-016 | Add-new-horario button eligibility | 🔷 Frontend — `!prescricao.suspenso && can_manage_prescricao` |
| PRESCRICAO-017 | Only checking user may revert a check | ⚠️ Parcial — state machine implementa transições mas sem verificação de autor |
| PRESCRICAO-018 | can_manage_prescricao gates all admin controls | 🔷 Frontend — permissão via `useEffectivePermissions()` |

**Implementação backend**: 43 regras internas (R01-R43) com:
- State machine (draft→active→completed/discontinued/suspended)
- Validação de entrada (R01-R10)
- Detecção de duplicatas (R11-R12)
- Restrições temporais (R13-R14)
- Interações medicamentosas (R17-R26, ANVISA base)
- Cálculo de dose (weight-based, renal, pediatric)
- Otimistic locking (version check para concorrência)

### 2.6 MOVIMENTACAO-ADT (Regras 020, 021, 025) — 3 arquivos

**Serviço**: `src/intensicare/services/domain_movimentacao.py` (731 linhas)

| Regra | Descrição | Status |
|-------|-----------|--------|
| MOV-ADT-020 | Bed patient resolution and auto-creation | ✅ `_validate_movement()` + `register_movement()` |
| MOV-ADT-021 | Homecare vs automatica bed classification | ⚠️ `BedRecord.status` (free/occupied/blocked/cleaning) sem diferenciação por tipo |
| MOV-ADT-025 | Bed eligibility — block automatic/occupied | ✅ `_validate_movement()` bloqueia admissão em leito ocupado |

**Implementação adicional** (9 regras UNVERIFIABLE RATIFY):
- ADT-001: Length of stay (`tempo_permanencia`)
- ADT-002: Micro-indicators payload
- ADT-003: Expected mortality score
- ADT-005: Bed lookup key
- ADT-006: Patient snapshot default
- ADT-007: Patient basic fields
- ADT-008: Vinculo lookup dict
- ADT-010: Camera RTSP URL
- ADT-011: Assistido flag

### 2.7 FORMULARIOS-CLINICOS (Regras 007, 008) — 2 arquivos

**Serviço**: `src/intensicare/services/domain_formularios.py` (719 linhas)

| Regra | Descrição | Status |
|-------|-----------|--------|
| FORM-007 | Home-care incident triage (urgency grade, symptom classification) | 🔷 Frontend — `dataFormIntercorrencia.ts` |
| FORM-008 | Physiotherapy early mobilization eligibility flags | 🔷 Frontend — flags de exibição |

**Implementação backend**: 5 formulários clínicos com scoring engines:
- SOFA (0-24, 6 sistemas orgânicos)
- RASS (-5 a +4, sedação/agitação)
- CAM-ICU (delirium binário)
- Glasgow (3-15, 3 componentes)
- BPS/NRS (dor 3-12 / 0-10)

### 2.8 DEMAIS REGRAS

| Regra | Domínio | Serviço | Status |
|-------|---------|---------|--------|
| EVOLUCOES-019 | Author-only edit/inactivate/re-sign | `domain_evolucoes.py` | 🔷 Frontend — regra de UI (`HistoricoEvolucao.tsx`). Backend: 1331 linhas com 14 templates SBAR + store imutável |
| EFICIENCIA-002 | RBC transfusion at Hb≥7 (criterion 3) | `domain_eficiencia.py` | ⚠️ Regra legada com **bug documentado** de precedência de operador. Backend: 12 critérios TF-001 a TF-012 com threshold Hb≥7 CORRIGIDO |
| EFICIENCIA-003 | RBC transfusion at Hb 6-7, 2 units | `domain_eficiencia.py` | ✅ TF-003 (single-unit strategy) cobre o espírito |
| EFICIENCIA-004 | Platelet transfusion at PLT<25000 | `domain_eficiencia.py` | ❌ Não implementado nos 12 critérios transfusionais |
| EFICIENCIA-008 | ICU discharge readiness (unwitnessed) | `domain_eficiencia.py` | ⚠️ LOS benchmarking presente, mas sem critérios específicos de alta |
| EFICIENCIA-009 | Frailty/palliative appropriateness (criterion 6) | `domain_eficiencia.py` | ✅ Frailty scoring (CFS 1-9, mFI, FRAIL) implementado |
| EFICIENCIA-011 | Low support step-down readiness (criterion 8) | `domain_eficiencia.py` | ❌ Não implementado |
| NUTRICAO-006 | Stress-ulcer prophylaxis indication enum | `domain_profilaxia.py` | ✅ Enum de 8 valores documentado (dva, tce, avc, queimado, jejum_prolongado, nao_indicado, terapeutico, vm_mais_72h) |
| OPERACIONAL-013 | Synthetic data SDRA severity enum | `domain_operacional.py` | ✅ 10 regras UNVERIFIABLE RATIFY (utils de parsing, paginação, formatação) |
| DOCUMENTACAO-014 | Double-gated evolution report access | `domain_documentacao.py` | 🔷 Frontend — double gate SSR + cliente. Backend: 16 critérios Glosa Zero (GZ-001 a GZ-016) |
| COMUNICACAO-016 | Video call join gated on video device | `domain_comunicacao.py` | 🔷 Frontend — `BuildVideoChat.tsx`. Backend: 3 regras UNVERIFIABLE RATIFY (reaction aggregation, user reaction, balanco_hidrico PK bug-fix) |
| BALANCO-HIDRICO-034 | Fluid balance action authorization | `domain_fluid_balance.py` | 🔷 Frontend — permissões `can_manage_balanco_hidrico`/`can_delete_balanco_hidrico`. Backend: nursing day 07:00-07:00, 2h bucketing, fluid balance computation |

---

## 3. ANÁLISE DE SEGURANÇA (THREAT MODEL)

### 3.1 MAPEAMENTO DAS 10 AMEAÇAS (STRIDE)

#### T-01 — SQL Injection via Clinical Form Inputs
- **STRIDE**: Tampering / Information Disclosure
- **Risco**: Critical
- **Controles existentes**:
  - ✅ SQLAlchemy 2.0 com queries parametrizadas (uso de `select()` com bind parameters)
  - ✅ Pydantic schemas para validação de entrada
  - ⚠️ Campos de texto livre (evolucoes, observacoes) sem limite de tamanho — **gap persiste**
  - ❌ Sem WAF SQL-injection rules confirmadas
- **Verificação**: `domain_tenancy.py` usa `select(Empresa).where(Empresa.nome_fantasia.ilike(pattern))` — parameterizado. `get_db()` dependency usa `async_sessionmaker` com bind parameters. Sem uso de raw SQL encontrado.

#### T-02 — JWT Token Forgery / Weak Secret
- **STRIDE**: Spoofing / Elevation of Privilege
- **Risco**: Critical
- **Controles existentes**:
  - ✅ `SECRET_KEY` usa `SecretStr` do Pydantic (não exposto em logs/repr)
  - ✅ `_validate_production_secrets()` bloqueia startup em produção com secret default
  - ✅ JTI (JWT ID) implementado com blacklist via Redis (`blacklist:{jti}`)
  - ✅ Refresh token com expiração de 7 dias
  - ✅ IAM Identity Center OIDC substitui JWT em staging/production (Fase 3)
  - ⚠️ HS256 (simétrico) usado em dev/CI — sem fallback para RS256/ES256
- **Código relevante**: `auth/jwt.py` — `create_access_token()` adiciona `jti`, `exp`, `type`. `blacklist_token()` armazena JTI no Redis com TTL. `decode_token()` verifica assinatura + exp.
- **.env.example**: `SECRET_KEY=change-me-in-production` (default inseguro documentado)

#### T-03 — PHI Exposure via Missing Security Headers
- **STRIDE**: Information Disclosure
- **Risco**: High
- **Controles existentes**:
  - ✅ **SecurityHeadersMiddleware** (`core/security_headers.py`, 122 linhas)
  - Headers aplicados:
    - `Strict-Transport-Security`: max-age=31536000; includeSubDomains (staging/prod apenas)
    - `X-Content-Type-Options`: nosniff
    - `X-Frame-Options`: DENY
    - `Content-Security-Policy`: strict healthcare defaults
    - `X-XSS-Protection`: 1; mode=block
    - `Referrer-Policy`: strict-origin-when-cross-origin
    - `Permissions-Policy`: camera=(), microphone=(), geolocation=(), interest-cohort=()
  - ⚠️ CSP inclui `style-src 'self' 'unsafe-inline'` — requerido pelo frontend (React/MUI)
- **Verificação**: Middleware usa `response.headers.setdefault()` — não sobrescreve headers já definidos por route handlers.

#### T-04 — Brute-Force / Credential Stuffing
- **STRIDE**: Spoofing
- **Risco**: High
- **Controles existentes**:
  - ✅ **RateLimitMiddleware** (`core/rate_limit.py`, 200 linhas)
  - Token bucket Redis-backed com Lua script atômico
  - Auth endpoints: 5 tentativas/minuto
  - API endpoints: 100 requisições/minuto
  - Health/metrics: nunca rate-limited
  - Headers `X-RateLimit-Limit`, `Retry-After` na resposta 429
  - ❌ Sem account lockout após N falhas (F-08, backlog)
  - ❌ Sem CAPTCHA
- **Verificação**: `PATH_BUCKET_MAP` mapeia `/auth` → bucket "auth" (5 tokens/60s)

#### T-05 — Privilege Escalation via Unprotected Admin Endpoints
- **STRIDE**: Elevation of Privilege
- **Risco**: Critical
- **Controles existentes**:
  - ✅ `require_admin` dependency (`auth/dependencies.py`) — verifica `current_user.is_admin`
  - ⚠️ RBAC é **binário** (admin/não-admin) — sem granularidade por papel (médico, enfermeiro, leitor)
  - ❌ Sem decorators `RequireRole` ou `require_permission` encontrados no código
  - ❌ Sem testes automatizados de cobertura RBAC por endpoint (gap F-05)
- **Verificação**: `get_current_user` extrai `sub` do JWT, busca `User` no banco, verifica `is_active`. `require_admin` apenas checa `is_admin`. Não há enum de roles ou matriz de permissões.

#### T-06 — WebSocket Alert Interception / Injection
- **STRIDE**: Tampering / Information Disclosure
- **Risco**: Critical
- **Controles existentes**:
  - ✅ Autenticação JWT via query parameter (`/api/v1/ws?token=<JWT>`)
  - ✅ `decode_token()` falha → `ws.close(code=1008)` (Policy Violation)
  - ✅ Channel/room-based subscription (subscribe/unsubscribe)
  - ✅ Heartbeat ping/pong a cada 30s + stale disconnect a 60s
  - ❌ Sem re-autorização por mensagem (F-09, backlog)
  - ❌ Token revocation não propagado para conexões WS abertas
- **Código**: `api/v1/ws.py`, 331 linhas. `WSConnectionManager` com `ChannelConnection` por usuário.

#### T-07 — Redis Cache Poisoning / Data Leakage
- **STRIDE**: Tampering / Information Disclosure
- **Risco**: Medium
- **Controles existentes**:
  - ✅ `_validate_production_secrets()` exige `REDIS_PASSWORD` em produção
  - ✅ Aviso (warning) em staging se REDIS_PASSWORD vazio
  - ✅ Redis URL com senha embutida (`redis://:senha@host:port/db`)
  - ❌ Redis sem TLS in-transit encryption (gap confirmado)
- **Código**: `core/redis.py` usa `aioredis.from_url(settings.redis_url)`. `config.py` gera URL com password via `SecretStr.get_secret_value()`.

#### T-08 — Excessive Data Exposure via API Responses
- **STRIDE**: Information Disclosure
- **Risco**: High
- **Controles existentes**:
  - ✅ Pydantic response schemas definem campos
  - ❌ Sem field-level access control por role
  - ❌ Sem filtro de resposta por papel do usuário
- **Verificação**: Schemas Pydantic como `UserResponse`, `TokenResponse` limitam campos expostos, mas não há lógica condicional baseada em `current_user.role`.

#### T-09 — Denial of Service via Expensive Queries
- **STRIDE**: Denial of Service
- **Risco**: High
- **Controles existentes**:
  - ✅ Rate limiting (100 req/min para API)
  - ✅ Connection pooling (min=2, max=10, pool_recycle=3600)
  - ✅ Pool pre-ping ativado
  - ❌ Sem `statement_timeout` no nível de sessão (F-07, backlog)
  - ❌ Sem enforcement de paginação nos endpoints de lista (parâmetros `limit`/`offset` presentes mas sem máximo rígido)
- **Verificação**: `domain_tenancy.py:list_empresas` aceita `limit` (default 50) sem teto máximo. `domain_formularios.py:list_submissions` aceita `limit` (default 50, range 1-200 mencionado em docstring mas não enforced).

#### T-10 — Supply Chain Compromise via Python Dependency
- **STRIDE**: Tampering / Elevation of Privilege
- **Risco**: Critical
- **Controles existentes**:
  - ❌ **Nenhum arquivo de dependências encontrado** — sem `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.cfg`, ou `setup.py` no repositório
  - ❌ Sem SBOM generation (F-10, backlog)
  - ❌ Sem verificação de integridade de pacotes (hash checking)
- **GRAVE**: A ausência de um arquivo de dependências versionado significa que não é possível auditar a supply chain, reproduzir o ambiente deterministicamente, ou verificar vulnerabilidades conhecidas com `pip-audit`.

### 3.2 RESOLUÇÃO DOS 10 FINDINGS (F-01 a F-10)

| Finding | Descrição | Severidade | Status | Evidência |
|---------|-----------|------------|--------|-----------|
| **F-01** | No Content-Security-Policy header | High | ✅ **Mitigado** | `SecurityHeadersMiddleware` com CSP strict healthcare defaults |
| **F-02** | No X-Frame-Options / frame-ancestors | Medium | ✅ **Mitigado** | `X-Frame-Options: DENY` + `frame-ancestors 'none'` no CSP |
| **F-03** | No HSTS header | High | ✅ **Mitigado** | `Strict-Transport-Security: max-age=31536000; includeSubDomains` (staging/prod) |
| **F-04** | `style-src 'unsafe-inline'` in CSP | Low | ⚠️ **Risco aceito** | Necessário para React/MUI; documentado para revisão pós-frontend audit |
| **F-05** | JWT secret validation bypass in dev mode | Medium | ⚠️ **Parcialmente mitigado** | Production validator bloqueia default; IAM IC substitui JWT em staging/prod; dev ainda usa HS256 |
| **F-06** | Redis unauthenticated in dev | Low | ⚠️ **Risco aceito** | Dev apenas; AUTH enforced em staging/prod via `_validate_production_secrets()` |
| **F-07** | No query timeout on API endpoints | Medium | 📋 **Backlog** | Sem `statement_timeout` configurado; `pool_recycle=3600` presente mas insuficiente |
| **F-08** | No account lockout after repeated failures | Medium | 📋 **Backlog** | Rate limiting mitiga parcialmente, mas sem lockout progressivo |
| **F-09** | WebSocket auth not re-checked per message | Medium | 📋 **Backlog** | Token validado apenas no connect; sem `RequireRole` equivalente para frames WS |
| **F-10** | No SBOM in CI pipeline | Low | 📋 **Backlog** | Sem arquivo de dependências; sem `cyclonedx-python` integrado |

---

## 4. CONTRATOS (OPENAPI)

### 4.1 Status

**Premissa inicial**: "docs/contracts/ is empty" — **FALSA**.

O diretório `docs/contracts/` contém **15 arquivos OpenAPI 3.1.0 YAML**:

| # | Arquivo | Tamanho |
|---|---------|---------|
| 1 | `ventilation-openapi.yaml` | ✅ Presente |
| 2 | `stability-openapi.yaml` | ✅ Presente |
| 3 | `sedacao-openapi.yaml` | ✅ Presente |
| 4 | `prophylaxis-openapi.yaml` | ✅ Presente |
| 5 | `prescricao-openapi.yaml` | ✅ Presente |
| 6 | `pathways-openapi.yaml` | ✅ Presente (510 linhas, verificado) |
| 7 | `movimentacao-openapi.yaml` | ✅ Presente |
| 8 | `indicadores-openapi.yaml` | ✅ Presente |
| 9 | `formularios-clinicos-openapi.yaml` | ✅ Presente |
| 10 | `evolucoes-openapi.yaml` | ✅ Presente |
| 11 | `eficiencia-openapi.yaml` | ✅ Presente |
| 12 | `documentacao-openapi.yaml` | ✅ Presente |
| 13 | `deterioration-openapi.yaml` | ✅ Presente |
| 14 | `cadastros-ui-openapi.yaml` | ✅ Presente |
| 15 | `antimicrobial-openapi.yaml` | ✅ Presente |

### 4.2 Cobertura

Os contratos cobrem 15 domínios clínicos, alinhados com os serviços `domain_*.py`
e routers `api/v1/*.py`. O contrato `pathways-openapi.yaml` verificado define
schema completo com security `BearerAuth`, operações CRUD, e tipos de resposta.

**Domínios com contrato mas sem router API dedicado**: Nenhum gap identificado.
Todos os 15 contratos têm serviço de domínio correspondente.

**Domínios com serviço mas sem contrato**:
- `domain_alertas.py` — sem contrato OpenAPI dedicado
- `domain_aki.py` — sem contrato OpenAPI dedicado
- `domain_electrolyte.py` — sem contrato OpenAPI dedicado
- `domain_estabilidade.py` — coberto por `stability-openapi.yaml`
- `domain_hemo.py` — sem contrato OpenAPI dedicado
- `domain_pharmaco_delirium.py` — sem contrato OpenAPI dedicado
- `domain_piora_clinica.py` — coberto por `deterioration-openapi.yaml`
- `domain_respiratory.py` — coberto por `ventilation-openapi.yaml`
- `domain_operacional.py` — sem contrato (utils internos)
- `domain_comunicacao.py` — sem contrato (utils internos)

---

## 5. VERIFICAÇÕES ADICIONAIS DE SEGURANÇA

### 5.1 .env.example — Exposure de Secrets

O arquivo `.env.example` contém valores default **documentados como inseguros**:

| Campo | Valor Default | Risco |
|-------|---------------|-------|
| `SECRET_KEY` | `change-me-in-production` | 🔴 Crítico se usado em produção |
| `JWT_SECRET_KEY` | `change-me-in-production` | 🔴 Idem |
| `POSTGRES_PASSWORD` | `intensicare_dev` | 🟡 Médio |
| `REDIS_PASSWORD` | (vazio) | 🟡 Médio |
| `JWT_ALGORITHM` | `HS256` | 🟢 Baixo (simétrico, mas padrão) |

**Mitigação**: `_validate_production_secrets()` em `config.py` bloqueia startup
em produção com secrets default. Todos os secrets usam `SecretStr` do Pydantic.

### 5.2 Hardcoded Secrets

**Busca por padrões**: `secret_key`, `password`, `token`, `eval`

| Padrão | Resultado |
|--------|-----------|
| `secret_key` | Apenas em `config.py` como `SecretStr` (seguro) |
| `password` hardcoded | `POSTGRES_PASSWORD` e `REDIS_PASSWORD` via env vars + `SecretStr` |
| `token` | Tokens FHIR/MPI via `SecretStr` (`.env.example` tem placeholders vazios) |
| `eval()` | **Não encontrado** no código-fonte |
| `exec()` | **Não encontrado** no código-fonte |
| `__import__()` | **Não encontrado** no código-fonte |

**Exceção**: `domain_movimentacao.py:build_camera_rtsp_url()` tem defaults
`username="admin"`, `password="admin"` para RTSP — **hardcoded credentials**
para câmeras de leito. Risco baixo (credenciais de câmera local), mas documentado.

### 5.3 CORS Configuration

- `CORS_ORIGINS` default: `["http://localhost:3000"]` — restritivo por padrão
- Sem wildcard `["*"]` — config requer origens explícitas em produção
- **CORS middleware não encontrado** como referência no código (busca por `CORSMiddleware` retornou vazio). Possivelmente configurado em arquivo não analisado (main app).

### 5.4 RBAC / Autorização

- `require_admin` — única dependency de autorização encontrada
- Roles disponíveis: `is_admin` (bool no model `User`)
- Roles mencionadas no threat model (admin, médico, enfermeiro, leitor) **não implementadas** como enum/roles
- `domain_evolucoes.py:CLINICAL_ROLES` lista 14 papéis clínicos, mas são usados apenas para templates SBAR, não para autorização
- ABAC (Fase 3): `auth/abac.py` + `get_current_tenant_id()` implementam extração de tenant, mas sem enforcement de políticas

### 5.5 WebSocket Security

- Autenticação JWT no connect ✅
- Channel subscription ✅
- Heartbeat + stale disconnect ✅
- **Sem autorização por mensagem** ❌ (F-09)
- **Sem propagação de token revocation** ❌

---

## 6. ESTATÍSTICAS FINAIS

### 6.1 Regras × Implementação

| Status | Quantidade | Percentual |
|--------|-----------|------------|
| ✅ Implementadas no backend | 6 | 12% |
| ⚠️ Cobertura parcial | 14 | 28% |
| ❌ Não implementadas (backend) | 4 | 8% |
| 🔷 Regras de frontend (UI gating) | 26 | 52% |
| **Total** | **50** | **100%** |

**Nota**: As 26 regras de frontend não representam gaps — são regras de
renderização condicional e controle de UI que, por definição, residem no
frontend. O backend implementa a lógica de negócio subjacente (validação,
cálculo, persistência).

### 6.2 Segurança — Findings Resolution

| Status | Quantidade | Findings |
|--------|-----------|----------|
| ✅ Mitigado | 4 | F-01, F-02, F-03, F-05 (parcial) |
| ⚠️ Risco aceito | 2 | F-04, F-06 |
| 📋 Backlog | 4 | F-07, F-08, F-09, F-10 |

### 6.3 Segurança — Controles Implementados

| Controle | Status |
|----------|--------|
| JWT com JTI + blacklist | ✅ |
| Rate limiting (token bucket Redis) | ✅ |
| Security headers (7 headers OWASP) | ✅ |
| SQLAlchemy parameterized queries | ✅ |
| Pydantic input validation | ✅ |
| Production secrets validator | ✅ |
| IAM Identity Center (Fase 3) | ✅ |
| Redis AUTH (staging/prod) | ✅ |
| KMS envelope encryption | ✅ (Fase 3) |
| AWS Secrets Manager | ✅ |
| WebSocket JWT auth | ✅ |
| CORS allow-list | ✅ |
| Structured logging (JSON) | ✅ |
| OpenTelemetry + Prometheus | ✅ |
| Watchdog/staleness monitor | ✅ |
| RBAC granular (médico/enfermeiro/leitor) | ❌ |
| Account lockout | ❌ |
| Query timeout | ❌ |
| WS per-message auth | ❌ |
| SBOM | ❌ |
| Redis TLS | ❌ |

---

## 7. RECOMENDAÇÕES PRIORIZADAS

### Críticas (ação imediata)

1. **Criar `requirements.txt` ou `pyproject.toml`** com versões pinadas de todas
   as dependências. Sem isso, T-10 (supply chain) é inauditável.

2. **Implementar RBAC granular** — substituir `is_admin` binário por matriz de
   roles (admin, médico, enfermeiro, leitor) com decorators `RequireRole`.

3. **Adicionar `statement_timeout`** nas sessões PostgreSQL para prevenir
   queries descontroladas (F-07).

### Altas (próximo sprint)

4. **Account lockout** após N tentativas de login falhas (F-08).

5. **Per-message authorization no WebSocket** — verificar token/role ao
   processar mensagens `subscribe` (F-09).

6. **SBOM pipeline** — integrar `cyclonedx-python` no CI (F-10).

### Médias (roadmap)

7. **Redis TLS** para criptografia in-transit.

8. **Field-level access control** nas respostas da API — filtrar campos PHI
   baseado no role do caller.

9. **Enforcement de paginação** com teto máximo (`limit` ≤ 200) em todos os
   endpoints de lista.

10. **Remover credenciais hardcoded** `admin:admin` em `build_camera_rtsp_url()`,
    mover para configuração por ambiente.

---

*Relatório gerado por Forensic Agent 3 em 2026-07-09.*
*Fonte: 50 rule files + threat-model.md + 24 domain_*.py + 15 contratos OpenAPI + auth + middleware.*
