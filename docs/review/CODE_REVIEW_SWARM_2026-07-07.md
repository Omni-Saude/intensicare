# IntensiCare — Revisão de Código (Swarm Review)

**Data:** 2026-07-07  
**Escopo:** Novos arquivos do backend (antimicrobial, prophylaxis, alert-routing, events)  
**Revisores:** 5 especialistas (Segurança, Performance, Estilo, Arquitetura, API Design)  
**Idioma do relatório:** PT-BR

---

## Sumário Executivo

Foram revisados 12 arquivos novos e 6 modificados, totalizando ~3.200 linhas de código. O código está **funcionalmente sólido** para o estágio de desenvolvimento, mas foram encontrados **2 problemas bloqueantes (blocking)**, **5 warnings** e **8 sugestões** de melhoria. As issues bloqueantes dizem respeito a: (1) ausência de autenticação no endpoint POST de alert-routing, e (2) código morto (dead code) no serviço de avaliação antimicrobiana que quebra o caminho de `inputs`.

---

## 🔴 BLOCKING (2 issues)

### B1. `POST /alert-routing` — Sem autenticação

- **Arquivo:** `src/intensicare/api/v1/alert_routing.py:79`
- **Severidade:** 🔴 BLOCKING
- **Revisor:** Segurança

O endpoint de criação de regras de roteamento (`create_alert_routing_rule`) **não tem dependência de autenticação**. Comparando com os endpoints equivalentes:

```python
# antimicrobial.py:129 — CORRETO
async def create_assessment(
    body: CreateAntimicrobialAssessmentSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ✅
) -> AntimicrobialAssessmentResponse:

# prophylaxis.py:197 — CORRETO
async def update_prophylaxis_bundle(
    ...
    current_user: User = Depends(get_current_user),  # ✅
) -> ProphylaxisBundleResponse:

# alert_routing.py:79 — VULNERÁVEL
async def create_alert_routing_rule(
    body: AlertRoutingRuleCreate,
    db: AsyncSession = Depends(get_db),
    # ❌ sem current_user!
) -> AlertRoutingRuleResponse:
```

**Impacto:** Qualquer pessoa sem autenticação pode criar, alterar (PUT) e deletar (DELETE) regras de roteamento de alertas.

**Solução:**
```python
from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User

async def create_alert_routing_rule(
    body: AlertRoutingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # adicionar
) -> AlertRoutingRuleResponse:
```
Aplicar a mesma correção nos endpoints `update_alert_routing_rule` (linha 122) e `delete_alert_routing_rule` (linha 152).

---

### B2. Dead code em `evaluate_assessment` — caminho `inputs` nunca executado

- **Arquivo:** `src/intensicare/services/domain_antimicrobiano.py:210-220`
- **Severidade:** 🔴 BLOCKING
- **Revisor:** Arquitetura

A variável `is_met` é computada mas **nunca utilizada**. A linha 220 ignora completamente o resultado e repete a condição original:

```python
# Linha 210-213 — computa is_met considerando inputs
is_met = crit_def["id"] in criteria_met_set or (
    inputs is not None
    and evaluate_criterion(crit_def, inputs.get(crit_def["id"])) is not None
)

# Linha 214-222 — IGNORA is_met, usa apenas criteria_met_set
criteria_results.append(
    AntimicrobialCriterionResult(
        ...
        met=crit_def["id"] in criteria_met_set,  # ❌ is_met descartado!
    )
)
```

Além disso, `evaluate_criterion` **sempre retorna** um objeto `AntimicrobialCriterionResult` (nunca `None`), então a condição `evaluate_criterion(...) is not None` é sempre `True`. O parâmetro `inputs` e toda a lógica de rule-engine são efetivamente **código morto**.

**Impacto:** O contrato da API espera que `inputs` possa ser usado para avaliação automática futura (milestones posteriores), mas atualmente nada acontece quando `inputs` é passado. Testes que passam `inputs` sem `criteria_met` vão reportar score 0 incorretamente.

**Solução:**
```python
# Opção A (correção imediata): usar is_met
met=is_met,

# Opção B (melhor): separar claramente os dois caminhos
if inputs is not None:
    criterion_result = evaluate_criterion(crit_def, inputs.get(crit_def["id"]))
    met = criterion_result.met
else:
    met = crit_def["id"] in criteria_met_set
```

---

## 🟡 WARNING (5 issues)

### W1. Race condition no registry SSE com listeners concorrentes

- **Arquivo:** `src/intensicare/api/v1/events.py:42-131`
- **Severidade:** 🟡 WARNING
- **Revisor:** Performance / Segurança

O registry global `_sse_listeners` é uma lista Python manipulada sem `asyncio.Lock`. Embora asyncio seja single-threaded, operações de append/remove durante iteração do `publish()` (no WS manager) podem causar `RuntimeError: list changed during iteration`.

**Sugestão:** Usar `asyncio.Queue` como registry ou proteger com `asyncio.Lock` compartilhado entre `events.py` e o `WSConnectionManager`.

---

### W2. Índice faltante em `antimicrobial_assessment.severity`

- **Arquivo:** `src/intensicare/models/antimicrobial.py:34-38`
- **Severidade:** 🟡 WARNING
- **Revisor:** Performance

A coluna `severity` é usada como filtro no endpoint `list_assessments` (query param `status`), mas **não possui índice**. Em produção com milhares de avaliações, o filtro por severity fará scan sequencial.

```python
severity: Mapped[str] = mapped_column(
    String(16),
    nullable=False,
    # ❌ falta index=True
)
```

**Solução:** Adicionar `index=True` ou um índice composto `Index("ix_am_severity_mpi", "mpi_id", "severity")`.

---

### W3. Inconsistência de idioma nos docstrings e comentários

- **Arquivos:** `models/alert_routing.py`, `schemas/alert_routing.py`, `api/v1/alert_routing.py`
- **Severidade:** 🟡 WARNING
- **Revisor:** Estilo

Os domínios `antimicrobial` e `prophylaxis` usam **inglês** em docstrings, comentários e nomes de campo. Já o domínio `alert_routing` usa **português (PT-BR)**. O projeto não tem um padrão definido, mas a maioria do código legado (`domain_aki.py`, `domain_sepsis.py`, `main.py`) usa português para docstrings/ comentários e inglês para símbolos (nomes de classe, função, variável).

**Sugestão:** Unificar para o padrão do resto do projeto: **inglês para símbolos, PT-BR para documentação**. Converter docstrings de `antimicrobial.py` e `prophylaxis.py` para PT-BR, ou manter inglês consistente em tudo.

---

### W4. `GET /prophylaxis/bundles` reavalia todos os bundles a cada request

- **Arquivo:** `src/intensicare/api/v1/prophylaxis.py:95-139`
- **Severidade:** 🟡 WARNING
- **Revisor:** Performance

O endpoint `list_prophylaxis_bundles` chama `evaluate_all_bundles()` **sempre**, mesmo quando o paciente já tem todas as avaliações persistidas no banco. Para 5 bundles isso é insignificante, mas o padrão de recomputar o domínio a cada GET é frágil — se um bundle futuramente tiver 50 critérios complexos, o custo escala linearmente com o número de requests.

**Sugestão:** Retornar os dados persistidos diretamente quando `status` e `score` já estão no banco. Recomputar apenas no PUT. Ou adicionar cache de curta duração (30s) por `(mpi_id, bundle_id)`.

---

### W5. `AntimicrobialAssessment.criteria` com type-hint `list[dict] | None` mas model usa `JSONB`

- **Arquivo:** `src/intensicare/models/antimicrobial.py:26-29`
- **Severidade:** 🟡 WARNING
- **Revisor:** Arquitetura

O type hint em Python declara `Mapped[list[dict] | None]`, mas em runtime o SQLAlchemy + JSONB retorna `list` (Python). O mesmo problema existe em `ProphylaxisAssessment.criteria` com `Mapped[dict[str, Any] | None]`. Isso força `# type: ignore[assignment]` nos endpoints (ex: `prophylaxis.py:120` e `:180`).

```python
# Model declara:
criteria: Mapped[dict[str, Any] | None] = mapped_column(JSONB, ...)

# API precisa de:
bundle_inputs[bundle_id] = row.criteria  # type: ignore[assignment]
```

**Sugestão:** Alinhar o type-hint com a realidade: `Mapped[Any]` ou criar um `TypeDecorator` que serialize/desserialize para `list[dict]` corretamente, eliminando os `type: ignore`.

---

## 🔵 SUGGESTION (8 issues)

### S1. Ausência de `Cache-Control` nos endpoints de catálogo

- **Arquivos:** `api/v1/antimicrobial.py:210`, `api/v1/prophylaxis.py:266`
- **Revisor:** API Design

Os endpoints de catálogo (`/antimicrobial/criteria`, `/prophylaxis/bundles/{id}/criteria`) são explicitamente marcados como "cacheable" nos docstrings, mas não retornam headers HTTP de cache. O frontend e proxies reversos não conseguem aplicar cache sem esses headers.

**Sugestão:**
```python
from fastapi import Response

@router.get("/antimicrobial/criteria", ...)
async def get_criteria_catalog_endpoint(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    ...
```

---

### S2. Nomenclatura inconsistente em list responses (`items` vs `rules`)

- **Arquivos:** `schemas/antimicrobial.py:75`, `schemas/alert_routing.py:84`
- **Revisor:** API Design

O padrão AUDIT-007 estabelece `{items, total}` para respostas de lista:

```python
# antimicrobial — segue AUDIT-007 ✅
class AntimicrobialAssessmentListResponse(BaseModel):
    items: list[...]
    total: int

# alert_routing — DESVIA ❌
class AlertRoutingRulesListResponse(BaseModel):
    rules: list[...]  # deveria ser "items"
    total: int
```

**Sugestão:** Renomear `rules` → `items` para consistência com o resto da API.

---

### S3. `evaluate_criterion` sempre retorna `met=False` — placeholder sem indicador claro

- **Arquivo:** `src/intensicare/services/domain_antimicrobiano.py:153-184`
- **Revisor:** Arquitetura

A docstring diz "This function is a placeholder for the rule engine", mas a função aceita `inputs` e parece funcional. Não há warning/log/todo visível em runtime. Um desenvolvedor novo poderia assumir que a avaliação funciona.

**Sugestão:** Adicionar `warnings.warn("evaluate_criterion is a placeholder — always returns met=False")` ou lançar `NotImplementedError` até que o rule engine seja implementado.

---

### S4. `BundleCriterionUpdate` definido após `ProphylaxisBundleUpdateRequest`

- **Arquivo:** `src/intensicare/schemas/prophylaxis.py:48-59`
- **Revisor:** Estilo

```python
class ProphylaxisBundleUpdateRequest(BaseModel):
    criteria: list[BundleCriterionUpdate] = ...  # forward reference

class BundleCriterionUpdate(BaseModel):  # definida DEPOIS
    id: str
    met: bool
```

Funciona com `from __future__ import annotations`, mas é frágil — se o `__future__` for removido, quebra. Inverte a ordem ou usa `"BundleCriterionUpdate"` (string) para forward reference explícita.

---

### S5. `patients.py` — query parameter `score_type` e `enrich` marcados como deprecated mas ainda no contrato

- **Arquivo:** `src/intensicare/api/patients.py:40-50`
- **Revisor:** API Design

Os parâmetros `score_type` e `enrich` têm `deprecated=True` e são explicitamente ignorados, mas continuam no schema OpenAPI. Isso polui a documentação e pode confundir integradores.

**Sugestão:** Remover completamente ou adicionar header `Deprecation: true` também nestes parâmetros (atualmente só o endpoint tem o header). Alternativa: versão explícita da API (`/api/v2/...`).

---

### S6. `clinical_forms.py` — `validation_alias` vs `alias`

- **Arquivo:** `src/intensicare/schemas/clinical_forms.py:18,24`
- **Revisor:** Estilo

Uso de `validation_alias` é correto para Pydantic v2 (aceita camelCase do frontend na entrada), mas a resposta da API vai retornar `form_type`/`patient_mpi_id` (snake_case). Se o frontend espera camelCase na resposta também, precisa de `serialization_alias`:

```python
form_type: str = Field(
    ...,
    validation_alias="formId",
    serialization_alias="formId",  # se necessário para round-trip
)
```

Verificar com o time de frontend se a resposta em snake_case é aceita.

---

### S7. `AlertRoutingRuleUpdate` — partial update sem validação de condições

- **Arquivo:** `src/intensicare/schemas/alert_routing.py:53-61`
- **Revisor:** Segurança / Arquitetura

O schema de update aceita `conditions` e `actions` como `list[dict[str, Any]]` sem validação estrutural. Uma regra com condição malformada (`{"field": 123}`) será persistida silenciosamente. O schema `AlertRoutingRuleCreate` tem o mesmo problema.

**Sugestão:** Adicionar um `field_validator` que cheque cada `ConditionItem` (já definido mas não usado nos schemas de request):

```python
@field_validator("conditions")
@classmethod
def validate_conditions(cls, v):
    for cond in v:
        ConditionItem(**cond)  # valida cada uma
    return v
```

---

### S8. SSE endpoint — heartbeat fixo de 30s pode ser curto para alguns proxies

- **Arquivo:** `src/intensicare/api/v1/events.py:101`
- **Revisor:** Performance

O timeout do `asyncio.wait_for` é 30s, mesmo valor do heartbeat. Proxies como AWS ALB têm idle timeout de 60s por padrão. 30s é seguro, mas seria mais robusto tornar configurável (`settings.sse_heartbeat_seconds`).

---

## 📊 Tabela de Consistência por Domínio

| Critério                | Antimicrobial          | Prophylaxis           | Alert Routing         | Events (SSE)          |
|-------------------------|------------------------|-----------------------|-----------------------|-----------------------|
| **Autenticação**        | ✅ POST                | ✅ PUT                | ❌ POST/PUT/DELETE    | ✅ Query token        |
| **Paginação**           | ✅ limit/offset        | N/A (fixo 5 bundles)  | ✅ limit/offset       | N/A                   |
| **Padrão AUDIT-007**    | ✅ `{items, total}`    | N/A                   | ❌ `{rules, total}`   | N/A                   |
| **Idioma docstrings**   | 🇬🇧 Inglês             | 🇬🇧 Inglês             | 🇧🇷 PT-BR              | 🇧🇷 PT-BR              |
| **Domínio separado**    | ✅ Service layer       | ✅ Service layer       | ❌ Lógica no router   | ✅ Service broadcast  |
| **Índices otimizados**  | ⚠️ Falta severity      | ✅ UK constraint       | ⚠️ Falta composite    | N/A                   |
| **Cache headers**       | ❌ Faltando            | ❌ Faltando            | N/A                   | ✅ no-cache           |
| **Tratamento 404**      | ✅                     | ✅                     | ✅                     | ❌ Retorna 401        |

---

## ✅ Pontos Positivos (Destaques)

1. **Separação de domínio limpa** — `domain_antimicrobiano.py` e `domain_profilaxia.py` seguem o mesmo padrão de dataclasses + funções puras dos outros serviços (`domain_aki.py`, `domain_sepsis.py`), sem acoplamento com SQLAlchemy ou FastAPI.
2. **Uso correto de SQLAlchemy 2.0** — `Mapped[]`, `mapped_column()`, `select()` sem `query()`, async session. Models bem tipados.
3. **Pydantic v2 correto** — `model_config`, `from_attributes`, `validation_alias`, `Field(default_factory=list)`. Sem uso de funcionalidades deprecadas da v1.
4. **Upsert idiomático** — `prophylaxis.py` usa `scalar_one_or_none()` + branch create/update, padrão consistente com SQLAlchemy async.
5. **SSE com heartbeat e cleanup** — `events.py` tem tratamento correto de `CancelledError`, `finally` para remover do registry, e heartbeat para keepalive.
6. **UniqueConstraint** em `prophylaxis_assessment` — garante integridade `(mpi_id, bundle_id)` no banco, prevenindo duplicatas mesmo sob concorrência.

---

## 📋 Checklist de Ações

| ID  | Ação                                                          | Prioridade | Responsável |
|-----|---------------------------------------------------------------|-----------|-------------|
| B1  | Adicionar `get_current_user` nos endpoints alert-routing      | 🔴 CRÍTICO | Backend     |
| B2  | Corrigir dead code em `evaluate_assessment` (usar `is_met`)   | 🔴 CRÍTICO | Backend     |
| W1  | Adicionar lock no registry SSE ou migrar para `asyncio.Queue` | 🟡 ALTA    | Backend     |
| W2  | Adicionar índice em `severity` + `mpi_id`                     | 🟡 ALTA    | Backend/DBA |
| W3  | Unificar idioma dos docstrings (PT-BR ou inglês consistente)  | 🟡 MÉDIA   | Tech Lead   |
| W4  | Cache ou evitar recomputação em GET `/prophylaxis/bundles`    | 🟡 MÉDIA   | Backend     |
| W5  | Corrigir type-hints JSONB nos models para eliminar `type: ignore` | 🟡 MÉDIA | Backend    |
| S1  | Adicionar `Cache-Control` nos endpoints de catálogo           | 🔵 BAIXA   | Backend     |
| S2  | Renomear `rules` → `items` em `AlertRoutingRulesListResponse` | 🔵 BAIXA   | Backend     |
| S3  | Adicionar warning visível no placeholder `evaluate_criterion` | 🔵 BAIXA   | Backend     |
| S4  | Reordenar classes em `schemas/prophylaxis.py`                 | 🔵 BAIXA   | Backend     |
| S5  | Remover query params deprecated do `/patients/{mpi_id}/status`| 🔵 BAIXA   | Backend     |
| S6  | Verificar necessidade de `serialization_alias` com frontend   | 🔵 BAIXA   | Full-stack  |
| S7  | Adicionar validação estrutural de conditions/actions          | 🔵 BAIXA   | Backend     |
| S8  | Tornar heartbeat SSE configurável via settings                | 🔵 BAIXA   | Backend     |

---

*Relatório gerado por Swarm Code Review — 5 revisores especializados em paralelo.*
