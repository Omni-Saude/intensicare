# DIM C — Auditoria Backend Clínico (Fórmulas + Engenharia)

**Escopo:** motor de trilhas (`_work/alerts/pathways/*.yaml` + `services/trilhas_*`), scores clínicos (MEWS/NEWS2/qSOFA/SOFA), APIs REST (contrato + comportamento real), dados de seed.
**Modo:** somente leitura — nenhum código de produto foi alterado. Todos os achados foram verificados por execução real (curl contra `localhost:8000`, `psql` contra o Postgres do docker-compose, leitura de código-fonte com `file:line`).
**Data:** 2026-07-12.

---

## 1. Definições YAML das Trilhas

### 1.1 Parsing

Todos os **12 arquivos parseiam com sucesso** (`yaml.safe_load`, sem exceções):

```
antimicrobiano.yaml delirium.yaml desmame.yaml equilibrio.yaml estabilidade.yaml
nutricao.yaml profilaxia.yaml renal.yaml respiratorio.yaml sedacao.yaml sepse.yaml ventilacao.yaml
```

Todos têm as seções top-level `pathway`, `evaluation`, `criteria`, `states`, `suppression`, `evidence`.

### 1.2 Tabela-resumo

| Arquivo | id | Nome | #Critérios | Tipos de predicate | #Estados | Guideline citado | Problema de banda | content_hash |
|---|---|---|---|---|---|---|---|---|
| ventilacao.yaml | 1 | Ventilação Mecânica | 2 (1 graded, 1 **threshold**) | graded, threshold | 2 (mínimo do corpus) | ARDSNet 2000 + PROSEVA 2013 | não | fake (`abc123def...`) |
| sepse.yaml | 2 | Sepse | 7 (5 graded, 2 boolean) | graded, boolean | 5 | SSC-2021 (DOI real) | não | fake (`...0002`) |
| desmame.yaml | 3 | Desmame | 6 (3 graded, 3 boolean) | graded, boolean | 4 | ACCP/SCCM/AARC/ATS 2001 + "BURN Trial 2016" (não verificável) | não (bandas em ordem descendente, mas contíguas) | fake (`...0003`) |
| nutricao.yaml | 4 | Nutrição Enteral | 6 (graded) | graded | 4 | ESPEN 2019 + ASPEN/SCCM 2016 (DOI real) | não | fake (`...0004`) |
| estabilidade.yaml | 5 | Estabilidade Hemodinâmica | 4 (graded) | graded | 4 | SSC-2021 + ESICM Consensus 2014 (DOI real) | não | fake (`...0005`) |
| sedacao.yaml | 6 | Sedação | 3 (graded) | graded | 4 | PADIS 2018 (DOI real) | **SIM — crit-sed-rass e crit-sed-bps** | fake (`...0006`) |
| profilaxia.yaml | 7 | Profilaxia | 4 (3 boolean, 1 graded) | boolean, graded | 3 | bundle genérico (SCCM/ACCM+IHI+SSC+WHO) — impreciso | não | fake (`...0007`) |
| antimicrobiano.yaml | 8 | Antimicrobiano | 4 (2 graded, 2 boolean) | graded, boolean | 4 | IDSA/SHEA 2016 + SSC-2021 (DOI real) | não | fake (`...0008`) |
| equilibrio.yaml | 9 | Equilíbrio Hidroeletrolítico | 4 (graded) | graded | 4 | "ESICM" vago + UpToDate (fonte secundária) | não | fake (`...0009`) |
| renal.yaml | 10 | Função Renal/AKI | 3 (graded) | graded | 5 | KDIGO 2012 + ADQI 2020 (DOI real, textbook-correto) | não | fake (`...000a`) |
| delirium.yaml | 11 | Delirium | 3 (1 boolean, 2 graded) | boolean, graded | 4 | PADIS 2018 (DOI real) | **SIM — crit-del-agitacao** | fake (`...000b`) |
| respiratorio.yaml | 12 | Insuf. Respiratória | 4 (graded) | graded | 5 | ARDSNet + ATS/ERS + BTS O2 2017 | não (FiO2 inicia em 21, correto fisiologicamente) | fake (`...000c`) |

**Tally de predicate types (50 critérios no total):** `graded`=38, `boolean`=11, `threshold`=1 (único em ventilacao.yaml).

### 1.3 Contiguidade de bandas

Nenhuma banda com **gap, overlap ou range invertido** foi encontrada nos 38 critérios `graded`. Porém 3 critérios em 2 arquivos violam a convenção "última banda deve ser aberta (`null`)":

- `delirium.yaml`, `crit-del-agitacao` (RASS): última banda `[3,5]` em vez de `[3,null]`.
- `sedacao.yaml`, `crit-sed-rass`: última banda `[1,5]` em vez de `[1,null]`.
- `sedacao.yaml`, `crit-sed-bps`: última banda `[8,13]` em vez de `[8,null]` (e 13 nem é o teto real da escala BPS, que é 12).

**Consequência confirmada no motor (seção 2):** essas 3 bandas falham a validação de compilação e são descartadas silenciosamente — os critérios nunca avaliam. Ver achado CRITICAL-2.

### 1.4 Guidelines citados

9 dos 12 arquivos citam guideline real, identificável, e com DOI correspondente ao documento certo (sepse→SSC-2021, renal→KDIGO 2012, delirium/sedação→PADIS 2018, nutrição→ESPEN/ASPEN, estabilidade→SSC-2021+ESICM 2014, antimicrobiano→IDSA/SHEA 2016, respiratorio/ventilacao→ARDSNet/PROSEVA/BTS). 3 arquivos têm citação fraca: `desmame.yaml` cita um "BURN Trial (2016)" não identificável na literatura de desmame; `equilibrio.yaml` cita uma "ESICM guideline" sem título verificável mais UpToDate (fonte terciária, não guideline primário); `profilaxia.yaml` cita um bundle genérico sem nomear a diretriz específica de profilaxia de TVP/úlcera de estresse (ex.: CHEST/ACCP).

### 1.5 content_hash — TODOS fake

Hash real de `sepse.yaml` calculado (`sha256sum`): `90355a798f0348fbb36f6bec29606e91b29ea93b8b56887d95673dea38ec5dad...`. Valor declarado no YAML: `sha256:0000...0002`. **Confirmado: os 12 arquivos usam um padrão sequencial trivial (`...0002` a `...000c`, espelhando `pathway.id`), exceto `ventilacao.yaml` que usa um padrão fake diferente (`abc123def...` repetido).** Nenhum é um SHA-256 real do conteúdo — impossível reproduzir a partir de 12 arquivos com conteúdo substancialmente diferente.

### 1.6 Incompletude — ventilacao.yaml é um stub

`ventilacao.yaml` (1570 bytes vs 4.2–7.0 KB nos outros 11) está materialmente incompleto: falta `pathway.description`, falta `pathway.active`, falta `evidence.recommendations`, os 2 critérios e ambos os estados não têm `description`, e usa um tipo de predicate (`threshold`) e um campo extra (`rationale`) não usados em nenhum outro arquivo. Só 2 estados (`initial`,`alta`) — o menor state-machine do corpus.

### 1.7 Inputs declarados e nunca usados

5 dos 12 arquivos declaram um input em `evaluation.inputs[]` que nenhum critério consome, mas que aparece na narrativa clínica do próprio pathway — sugerindo lógica planejada e não implementada:

| Arquivo | Input órfão | Evidência de que deveria ser usado |
|---|---|---|
| delirium.yaml | `dexmedetomidina_dose` | `evidence.recommendations` menciona dexmedetomidina, mas nenhum critério pontua a dose |
| equilibrio.yaml | `fosforo` | `pathway.description` cita fósforo explicitamente como monitorado |
| renal.yaml | `trs_status` | `states[]` discute indicação de TRS (diálise), nunca avaliada como critério |
| respiratorio.yaml | `gaso_ph` | `states[]` cita "pH < 7.35" como parte da definição de IRpA, nunca avaliado |
| sedacao.yaml | `interrupcao_diaria` | um dos 4 estados é literalmente "Interrupção Diária" (SAT), input nunca avaliado |

Nenhuma referência pendurada (`criteria[].predicate.input` sem `evaluation.inputs[]` correspondente) foi encontrada — o problema é sempre na direção oposta (input declarado, não consumido).

---

## 2. Motor de Avaliação

### 2.1 Carregamento

`services/trilhas_engine.py:226-232`: `yaml_files = sorted(full_path.glob("*.yaml")) + sorted(full_path.glob("*.yml"))`, carregado a partir de `_work/alerts/pathways`. **Confirma-se que os 12 arquivos carregam** (não é uma lista hardcoded parcial) — instanciação real do `TrilhasEngine` durante a auditoria confirmou os 12 slugs presentes.

Existe um **segundo loader paralelo e duplicado**, `services/trilhas_definitions.py:493-566` (`_load_pathways_from_yaml`), usado por um caminho de catálogo legado — duas fontes de verdade independentes para a mesma definição de pathway (risco de manutenção/consistência, não um bug de avaliação em si).

### 2.2 Trace manual: sepse, PAM=58 mmHg, lactato=3.2 mmol/L

Casamento de banda em `trilhas_compiler.py:91-97`:
```python
def contains(self, value: float) -> bool:
    """Check if value falls within this band: lower ≤ value < upper."""
    if value < self.lower:
        return False
    if self.upper is not None and value >= self.upper:
        return False
    return True
```
Intervalo semiaberto `[lower, upper)` — implementado corretamente com `<` e `>=`.

- **crit-sep-pam** (`sepse.yaml:117-129`): bandas `[0,65]→critical/3`, `[65,null]→normal/0`. PAM=58 → `0≤58<65` → **critical, score 3**. Fronteira PAM=65 exata cai em `[65,null)` → normal/0 (comportamento clinicamente correto: "PAM≥65=adequada").
- **crit-sep-lactato** (`sepse.yaml:74-87`): bandas `[0,2.0)→normal/0`, `[2.0,4.0)→watch/1`, `[4.0,null)→critical/3`. Lactato=3.2 → **watch, score 1**.
- Os demais 5 critérios de sepse (qsofa_score, pct, culturas_status, atb_status, fluid_volume) não têm valor no `patient_data` do trace — `trilhas_evaluator.py:382-389` captura `KeyError` e faz `continue`, sem erro. Resultado agregado: `overall_severity="critical"` (máximo), `total_score=4`.

**Nenhum bug off-by-one encontrado na lógica de bandas** — o intervalo semiaberto é implementado de forma consistente e a validação de compilação (contiguidade obrigatória) previne ambiguidade de fronteira.

### 2.3 Suppression — real, não aspiracional (com uma exceção)

`SuppressionTracker` (`trilhas_evaluator.py:85-283`) é uma implementação real, com backend Redis (`EXISTS`/`TTL`/`SETEX` para cooldown, `INCR`+`EXPIRE` para rate-limit) e fallback em memória thread-safe. É chamado de fato no fluxo de avaliação (`trilhas_evaluator.py:409-424`), lendo `cooldown_minutes`/`rate_limit_per_hour` diretamente do bloco `suppression` de cada YAML.

**Exceção: `dedup_key`** (ex.: `["mpi_id","criteria_id"]` em `sepse.yaml:207`) é parseado mas **nunca lido em nenhum outro ponto do código** (grep em `services/` não retorna uso) — campo morto/aspiracional.

### 2.4 Persistência — CONFIRMADO ainda em memória (C3 do audit anterior permanece válido)

`trilhas_state.py:110-112`: `self._patient_pathway_store: dict[str, dict[int, PatientPathwayDict]] = {}` — dict Python puro, único destino de escrita para enrolamento/critérios/transições de estado. Nenhuma chamada `session.add`/`db.commit` em `trilhas_state.py`, `domain_trilhas_engine.py` ou `api/v1/pathways.py`. Os modelos SQLAlchemy `Pathway`/`PatientPathway`/`PathwayCriteria`/`PathwayStateTransition` (`models/pathway.py`) **nunca são instanciados** no caminho de serviço — scaffolding ORM morto. O próprio módulo se autodocumenta como depreciado, com "Migration deadline: 2026-09-01" (`trilhas_state.py:7-19`) — ainda não vencido, mas confirma que o débito técnico é conhecido e não resolvido.

Isso foi corroborado diretamente no banco: `select count(*) from patient_pathways` → **0**; `select count(*) from pathway_criteria` → **0**; `select count(*) from pathways` → **0**. As tabelas Postgres existem no schema mas estão completamente vazias — a API de pathways não lê nem escreve nelas, servindo tudo a partir do YAML+dict em memória.

### 2.5 `encounter_id` — CORRIGIDO desde 2026-07-09 (C4 do audit anterior não é mais válido)

`models/pathway.py:47-68`, `PatientPathway.encounter_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="Admission identifier from AMH Gold")` — coluna presente, obrigatória, indexada. Confirmado via `psql \d patient_pathways`. **Ressalva:** como a tabela nunca é escrita (seção 2.4), esse fix está em um modelo ORM não utilizado — a correção do schema é real, mas inerte.

### 2.6 content_hash no motor — fake é propagado, não verificado (C5 permanece válido)

`trilhas_engine.py:274`: `content_hash: str = pathway_meta.get("content_hash", "") or compute_content_hash(raw)` — **prioriza** o valor (fake) do YAML quando presente; a função `compute_content_hash` (implementação SHA-256 real e correta, `trilhas_compiler.py:46-66`) só é usada como fallback se o campo estiver ausente. Nenhum ponto do código compara o hash declarado com um hash recalculado para detectar drift — o hash fake é estampado em cada `AlertFiring`/`CriterionFiring` como se fosse rastreabilidade real.

### 2.7 Validação do compilador — real, mas com falha silenciosa ativa

`trilhas_compiler.py:_compile_graded` (linhas 292-364) valida corretamente: 2 elementos por range, `lower<upper`, contiguidade estrita entre bandas adjacentes, e exige que a última banda seja aberta (`upper is None`). **Porém**, falhas de compilação por critério são capturadas e apenas logadas (`trilhas_engine.py:283-297`, `logger.warning`), sem propagar exceção — o pathway inteiro continua carregando, só o critério problemático é descartado.

**Prova ao vivo:** instanciar o `TrilhasEngine` produz exatamente 3 warnings — `crit-del-agitacao`, `crit-sed-rass`, `crit-sed-bps` — todos por "Last band must have null upper bound". **Consequência clínica real:** os critérios de agitação (RASS) em `delirium.yaml` e de profundidade de sedação/dor (RASS/BPS) em `sedacao.yaml` **nunca disparam alerta**, hoje, em produção — e essa falha só é visível em log de aplicação, não em métrica, health-check ou alerta operacional. Ver CRITICAL-2 na tabela de achados.

Também não há validação de schema JSON no nível top-level do YAML (`_work/alerts/schema/pathway.schema.json` existe em disco mas só é referenciado em docstrings — grep por uso da lib `jsonschema` no código-fonte não retorna nada). Campos obrigatórios ausentes (`name`, `slug`, `version`) resultariam em strings vazias silenciosas, não em rejeição.

### 2.8 Outros bugs de correção

- Predicate `boolean` ignora completamente `operator`/`value` do YAML — `_evaluate_boolean` (`trilhas_compiler.py:499-515`) faz só `met = bool(actual_value)`. Hoje é dormente (todos os 11 usos em produção são `operator:"==", value:true`), mas é uma lacuna de fidelidade ao contrato declarado, e um valor booleano vindo como string `"false"` upstream resultaria em `bool("false")==True` (bug de coerção latente).

---

## 3. Fórmulas e Thresholds

### 3.1 MEWS (Subbe et al. 2001) — `services/mews.py` — **DIVERGÊNCIA MAJOR (CRITICAL)**

| Parâmetro | Implementado | Literatura | Veredito |
|---|---|---|---|
| FC | `mews.py:68-79`: ≤40→2; ≤50→1; ≤100→0; ≤110→1; ≤129→2; senão→3 | <40→2; 40–50→1; 51–100→0; 101–110→1; 111–129→2; ≥130→3 | **Divergência em FC=40**: código usa `<=40` (inclusivo) → score 2; literatura coloca FC=40 na banda 40–50 → score deveria ser **1**. Off-by-one de 1 valor. |
| PAS | `mews.py:94-103` | idêntico | MATCH |
| FR | `mews.py:118-127` | idêntico (`<9`≡`≤8` para inteiros) | MATCH |
| **Temp** | `mews.py:145-154`: ≤35.0→2; ≤36.0→1; ≤38.0→0; ≤38.5→1; senão→2 (escala de **5 bandas**) | <35→2; 35–38.4→0; ≥38.5→2 (escala de **3 bandas**) | **DIVERGÊNCIA MAJOR.** O código usa uma estrutura de bandas totalmente diferente da tabela literária fornecida. Temp=35.0: lit=0, código=2 (superestima). Temp=35.5–36.0 e 38.1–38.4: lit=0, código=1. **Mais grave clinicamente: Temp=38.5° exata → literatura=2 (limiar de febre), código=1** (`mews.py:151`, `<=` inclusivo no limite errado) — **subestima febre exatamente no ponto de escalada**, na direção perigosa (mascara gravidade). |
| AVPU | `mews.py:158-172` | idêntico | MATCH — mas valor não reconhecido (typo/vazio) faz fallback silencioso para "Alert"=0 (`mews.py:171`), podendo mascarar rebaixamento de consciência real se o dado vier malformado. |

Testes unitários (`tests/test_mews.py:33,127`) **certificam o comportamento divergente atual como correto** — regressão futura que corrija os limiares não seria pega pelos testes existentes sem também atualizá-los. Há rationale registrada em migração Alembic (`0007_seed_mews_v1_0_1.py`, `RAT-MEWS-SUBBE-2001`) alegando alinhamento com Subbe 2001 original — plausivelmente reflete uma versão publicada diferente da escala, mas diverge da tabela de referência desta auditoria e precisa de sign-off clínico explícito, não de aceitação silenciosa.

### 3.2 NEWS2 (RCP 2017) — `services/news2.py` — **CORRETO**

Todos os 7 parâmetros (FR, SpO2 escala 1, PAS, FC, Temp, consciência, O2 suplementar) batem exatamente com a tabela de referência, fronteira a fronteira, confirmado por `tests/test_news2.py:349-374`. Único ponto de atenção não-clínico: a descrição da migração Alembic que ativou este algoritmo (`0008_seed_news2_v2_0_0.py:12`, `0021_activate_news2_v3_0_0.py:9`) afirma "O2 suplementar ativa automaticamente Scale 2", mas o código real (`news2.py:110-114,267-272`) corretamente restringe Scale 2 a pacientes hipercápnicos confirmados (comportamento clinicamente correto per RCP 2017) — **drift entre documentação/audit-trail e comportamento real de runtime**, achado de governança, não de cálculo.

### 3.3 qSOFA (Sepsis-3) — `services/qsofa.py` — **CORRETO**

FR≥22→1 (`qsofa.py:81`), PAS≤100→1 (`qsofa.py:98`), Glasgow<15→1 (`qsofa.py:115`) — os 3 critérios batem exatamente com a literatura.

### 3.4 SOFA — `services/sofa.py` — **CORRETO**

Os 6 sistemas orgânicos (respiração PaO2/FiO2, coagulação/plaquetas, fígado/bilirrubina, cardiovascular/PAM+vasopressores, neurológico/Glasgow, renal/creatinina+diurese) batem exatamente com a tabela de referência em todas as fronteiras, consistente com o próprio audit-trail do arquivo ("CLINICALMENTE RATIFICADO per RAT-CLINICAL-SCORING-01/02/03").

### 3.5 Resumo

| Score | Veredito |
|---|---|
| MEWS | **DIVERGÊNCIA (CRITICAL)** — estrutura de bandas de temperatura e limiar de 38.5°C subestimam febre na direção perigosa; FC=40 é off-by-one menor |
| NEWS2 | CORRETO — só drift documental (migração vs. código) |
| qSOFA | CORRETO |
| SOFA | CORRETO |

---

## 4. APIs e Contratos

### 4.1 Autenticação e autorização

- `POST /api/v1/auth/login` funciona (form-urlencoded), retorna JWT com `sub, user_id, is_admin, role, name, email, exp, type, jti`.
- Endpoints protegidos testados sem token — **todos retornam 401** `{"detail":"Not authenticated"}` corretamente: `/dashboard`, `/patients/{mpi_id}`, `/admin/users`, `/pathways`.
- Rate limiting **existe e funciona**: login com senha errada em loop rápido → `401,401,401,401,429,429,...` (lockout após ~4 tentativas: `"Account temporarily locked due to too many failed attempts... try again in 15 minutes"`). Endpoints GET normais expõem header `x-ratelimit-limit: 100`.
- Erros 404/422 retornam JSON limpo, sem stack trace: `{"detail":"Patient not found: X"}` (404), `{"detail":[{"type":"int_parsing",...}]}` (422 do FastAPI/Pydantic nativo). Testado com payloads adversariais (mpi_id de 5000 caracteres, tentativa de SQLi no path) — nenhum 500, nenhum vazamento.

### 4.2 RBAC — incoerência confirmada e caracterizada (CRITICAL/MAJOR)

JWT do admin: `role:"readonly"` + `is_admin:true` simultâneos. Estado real no banco (`select id,username,role,is_admin from users`):

```
 id | username     | role     | is_admin
  2 | admin        | readonly | t
  3 | medico1      | readonly | f
  4 | test_user_99 | readonly | t
  6 | wstest       | admin    | t
```

- `models/user.py:21-27`: `role` e `is_admin` são colunas totalmente independentes, sem CHECK constraint nem validador de coerência.
- `auth/dependencies.py:92-101` (`require_admin`) checa **apenas `is_admin`** — `role` nunca é consultado nos gates reais.
- `auth/dependencies.py:119-123` (`_has_role`): `if user.is_admin: return True` — **is_admin sobrepõe role incondicionalmente** mesmo nos helpers de role granular (`require_medico`, `require_enfermeiro` etc.), que além disso **não têm nenhum call-site** em `api/` — RBAC clínico granular definido (migração `0035_add_user_role.py`) e nunca ligado a rota alguma.
- `UserCreate`/`UserUpdate` (`admin.py:66-97`) **não expõem `role`** — impossível defini-lo via API; todo usuário criado herda o default `"readonly"` do banco independentemente de `is_admin`. Isso contradiz a própria docstring do módulo ("PUT /admin/users/{id} — update user role/status").
- `admin.py:182,213,294` chamam `require_abac(role_str="admin", ...)` com **literal hardcoded**, não `current_admin.role` — o enforcement ABAC é decorativo, não avalia o papel real de quem chama.
- **Consequência prática:** `role="readonly"` é hoje um rótulo sem efeito de controle de acesso — quem tem `is_admin=True` tem acesso total, independentemente de `role`. Não é uma escalação de privilégio explorável por um atacante externo, mas é um risco sério de auditoria/compliance em sistema clínico: `GET /admin/users` mostra 2 usuários "readonly" que na prática têm acesso administrativo total.

### 4.3 Contrato vs. comportamento real — vazamento de repr interno

`GET /api/v1/pathways/1` (ventilacao): campo `criteria[].description` retorna `"graded(pf_ratio [0, 100)=critical(3) [100, 200)=urgent(2) [200, 300)=watch(1) [300, +∞)=normal(0) unit=mmHg)"` — uma string de fórmula interna, não a prosa clínica que `docs/contracts/pathways-openapi.yaml` especifica (exemplo no contrato: `"Relação entre pressão parcial de oxigênio arterial e fração inspirada de oxigênio"`).

**Causa raiz:** `api/v1/pathways.py:94` — `"description": c.get("description", pred.get("rationale", ""))` — faz fallback para o campo interno `rationale` do predicate quando o critério não tem `description` próprio. `ventilacao.yaml` é o único dos 12 arquivos sem `description` em nenhum critério/estado/pathway (é o stub — seção 1.6), então é o único afetado hoje; os outros 11 têm 100% de cobertura de `description` e não disparam o fallback. **Bug real e contract-breaking, mas de escopo estreito atualmente** (1/12 pathways) — risco latente para qualquer YAML futuro sem `description`.

`created_at`/`updated_at` são **sempre `null`** em `GET /pathways` e `GET /pathways/{id}`, para os 12 pathways, incondicionalmente — nem o caminho YAML (`_pathway_def_to_flat_dict`, `pathways.py:112-121`) nem o catálogo legado (`trilhas_definitions.PATHWAY_SEEDS`) carregam essas chaves. É um achado distinto do "tabela `pathways` vazia" (seção 2.4) — mesmo se a tabela tivesse linhas, o endpoint de leitura não a consulta.

### 4.4 Shapes testados

| Endpoint | HTTP | Shape |
|---|---|---|
| `GET /api/v1/health` | 200 | OK, sem auth, expõe staleness por unidade/score |
| `POST /api/v1/auth/login` | 200 / 401 (senha errada) / 429 (lockout) | OK |
| `GET /api/v1/dashboard` | 200 | `{patients:[7], total, critical_count:2, unit_counts}` — todos os 7 pacientes com `active_pathways:[]` |
| `GET /api/v1/patients/{mpi_id}` | 200 (existe) / 404 (não existe) | `vitals:[]`, `scores:[]` sempre vazios — ver §5.3 |
| `GET /api/v1/patients/{mpi_id}/pathways` | 200 | `{items:[],total:0}` para os 7 pacientes — nenhum enrolamento ativo hoje |
| `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress` | 404 (pp_id inexistente) | mensagem clara, sem stack trace |
| `GET /api/v1/pathways` | 200 | lista os 12 pathways (fonte: YAML, não DB) |
| `GET /api/v1/pathways/{id}` | 200 / 404 / 422 (id não-numérico) | OK, mas ver bug de `description` (§4.3) |
| `GET /api/v1/alerts` | 200 | 2 alertas ativos (`mews`, `aki`), `pathway_name:null` em ambos |
| `GET /api/v1/admin/users` | 200 | 4 usuários, RBAC incoerente (§4.2) |

---

## 5. Dados

### 5.1 Volume do seed

Via `psql` direto no Postgres (`intensicare` DB): `patient_cache`=7, `vital_sign`=19, `clinical_score`=72, `alert`=9, `users`=4, `beds`=0, `admission_episodes`=0. **`pathways`=0, `patient_pathways`=0, `pathway_criteria`=0** — as tabelas de pathway existem no schema mas estão completamente vazias (a API de pathways é servida por YAML+memória, nunca por essas tabelas — seção 2.4).

7 pacientes: LEITO-01 a LEITO-06 (UTI-ADULTO×5 + UTI-CORONARIANA×1) + MPI-001 (paciente de teste, sem vitals). MEWS/NEWS2 variam de 0/0 (LEITO-01, saudável) a 13/19 (LEITO-06, crítico) — faixa de gravidade plausível para demonstração, mas volume pequeno (7 pacientes, 19 vitals, 72 scores) para validar estatisticamente qualquer coisa além de "os cálculos rodam".

### 5.2 Pathways ativos com progress/critérios populados — NENHUM (achado MAJOR)

Contrário ao apontado por auditoria anterior ("enrolments existem: LEITO-01 em ventilação/desmame/nutrição"), **hoje nenhum dos 7 pacientes tem pathway ativo** — `GET /patients/{mpi_id}/pathways` retorna `{items:[],total:0}` para todos, e a tabela `patient_pathways` está vazia no banco. **O motor de trilhas não pôde ser validado end-to-end com um paciente real neste momento da auditoria** — a validação da seção 2.2 foi feita via trace manual de código com dados sintéticos, não observando um enrolamento real em produção. Isso é consistente com a arquitetura em memória (seção 2.4): qualquer enrolamento anterior foi perdido em um restart do processo desde a auditoria de 2026-07-09.

### 5.3 Staleness — impacto direto e mensurável na auditoria

`GET /api/v1/health` reporta `minutes_stale ≈ 23000` (~16 dias) para MEWS/NEWS2/SOFA/qSOFA nas unidades UTI-ADULTO/UTI-CORONARIANA — o último vital real é de `2026-06-26`. Isso tem **consequência funcional direta e verificada em código**: `services/dashboard.py:368` usa um cutoff hardcoded de 24h (`datetime.now(utc) - timedelta(hours=24)`) para filtrar vitals e scores em `GET /patients/{mpi_id}`. Com dados de 16 dias atrás, **esse endpoint retorna `vitals:[]` e `scores:[]` sempre**, para todos os pacientes, hoje — não é um bug de lógica, mas o efeito direto e 100% reprodutível da combinação staleness+cutoff. O dashboard summary (`GET /dashboard`) não usa esse cutoff e por isso ainda mostra os últimos valores conhecidos — mas o endpoint de detalhe do paciente está, na prática, inutilizável com o dataset atual.

---

## 6. Scoring

**Nota final: 46/100.**

### Tabela de achados

| # | Severidade | Achado | Evidência |
|---|---|---|---|
| 1 | **CRITICAL** | MEWS: estrutura de bandas de Temperatura diverge da literatura; Temp=38.5°C exatas subestima febre (score 1 em vez de 2), na direção clinicamente perigosa; FC=40 off-by-one menor | `services/mews.py:145-154`, `68-79`; `tests/test_mews.py:33,127` certificam o comportamento divergente |
| 2 | **CRITICAL** | 3 critérios clínicos (RASS em delirium, RASS+BPS em sedação) falham na compilação (banda final não-`null`) e são descartados silenciosamente — nunca disparam alerta em produção; único sinal é um `logger.warning` | `_work/alerts/pathways/delirium.yaml` (crit-del-agitacao), `sedacao.yaml` (crit-sed-rass, crit-sed-bps); `services/trilhas_engine.py:283-297` |
| 3 | MAJOR | Motor não validável end-to-end: 0 pathways ativos em todos os 7 pacientes; tabelas `pathways`/`patient_pathways`/`pathway_criteria` vazias no Postgres | `psql`: `select count(*) from patient_pathways` → 0; `GET /patients/{mpi_id}/pathways` → `{items:[],total:0}` ×7 |
| 4 | MAJOR | Estado de pathway (enrolamento/critérios/transições) só em memória (`dict` Python), não persistido — perdido em restart; modelos ORM existem mas nunca são instanciados | `services/trilhas_state.py:7-19,110-112`; deadline de migração 2026-09-01 ainda não vencido/resolvido |
| 5 | MAJOR | `content_hash` fake/placeholder nos 12 pathways, propagado como se fosse rastreabilidade real em cada `AlertFiring`, nunca verificado contra o conteúdo real | `trilhas_engine.py:274`; hash real de `sepse.yaml` ≠ `sha256:0000...0002` declarado |
| 6 | MAJOR | `GET /patients/{mpi_id}` sempre retorna `vitals:[]`,`scores:[]` hoje — cutoff hardcoded de 24h colide com staleness de 16 dias dos dados de seed | `services/dashboard.py:368-371,398-403` |
| 7 | MAJOR | RBAC incoerente: `role` é inerte em todo enforcement real (`is_admin` sobrepõe incondicionalmente); `UserCreate`/`UserUpdate` nem expõem `role`; admin rotulado "readonly" com acesso total | `models/user.py:21-27`; `auth/dependencies.py:92-101,119-123`; `admin.py:66-97,182` |
| 8 | MAJOR | `ventilacao.yaml` (pathway id 1) é um stub incompleto: sem descriptions, sem `evidence.recommendations`, só 2 estados, tipo de predicate único (`threshold`) | `_work/alerts/pathways/ventilacao.yaml` (1570 bytes vs 4.2–7.0KB nos outros) |
| 9 | MAJOR | Falhas de compilação de predicate são só logadas (`logger.warning`), nunca propagadas/alertadas — mecanismo que permitiu o achado #2 passar despercebido operacionalmente | `services/trilhas_engine.py:283-297` |
| 10 | MAJOR | 5 de 12 pathways declaram inputs (`dexmedetomidina_dose`, `fosforo`, `trs_status`, `gaso_ph`, `interrupcao_diaria`) citados na narrativa clínica mas nunca avaliados por nenhum critério | seção 1.7 |
| 11 | MAJOR | Citações de guideline fracas/não verificáveis em 3 arquivos: "BURN Trial 2016" (desmame), ESICM vago+UpToDate (equilibrio), bundle genérico (profilaxia) | seção 1.4 |
| 12 | MINOR | `criteria[].description` vaza repr interno do predicate (`rationale`) quando ausente — contract-breaking, hoje restrito a ventilacao.yaml (1/12) | `api/v1/pathways.py:94` |
| 13 | MINOR | `created_at`/`updated_at` sempre `null` em `GET /pathways` e `/pathways/{id}`, para os 12 pathways, incondicionalmente | `api/v1/pathways.py:112-121` |
| 14 | MINOR | `dedup_key` do bloco `suppression` é parseado mas nunca aplicado — campo morto | grep em `services/`, sem uso além do parse |
| 15 | MINOR | Predicate `boolean` ignora `operator`/`value` do YAML, só faz `bool(actual_value)` — risco latente de coerção (`bool("false")==True`) | `trilhas_compiler.py:499-515` |
| 16 | MINOR | Nenhuma validação de JSON Schema no nível top do YAML — campos obrigatórios ausentes resultam em default silencioso (`""`) | `trilhas_engine.py:265`; `_work/alerts/schema/pathway.schema.json` não é usado em código |
| 17 | MINOR | Dois loaders de YAML duplicados e independentes (`trilhas_engine.py` vs `trilhas_definitions.py`) — duas fontes de verdade | seção 2.1 |
| 18 | MINOR | Descrição da migração Alembic do NEWS2 contradiz o comportamento real (correto) do código quanto à ativação da Scale 2 | `alembic/versions/0008_seed_news2_v2_0_0.py:12`, `0021...py:9` vs `news2.py:110-114,267-272` |
| 19 | MINOR | `require_abac` chamado com `role_str="admin"` hardcoded em vez do papel real do usuário — enforcement decorativo | `admin.py:182,213,294` |

**Total: 2 CRITICAL, 9 MAJOR, 8 MINOR = 19 achados.**

### Pontos fortes confirmados (créditos, não deduzidos)

- SOFA, qSOFA e NEWS2 batem **exatamente** com a literatura de referência em todas as fronteiras testadas, com testes unitários corretos e citação explícita da fonte no código.
- Lógica de casamento de banda do motor (`[lower,upper)`) é implementada corretamente e sem off-by-one, com validação de contiguidade obrigatória em tempo de compilação.
- Suppression (cooldown + rate-limit) é uma implementação real, com Redis e fallback em memória, de fato ligada ao fluxo de avaliação.
- 9 dos 12 pathways citam guidelines reais e verificáveis com DOI correspondente correto.
- Autenticação, RBAC binário (autenticado/não), tratamento de erro (404/422 limpos, sem stack trace) e rate limiting de login funcionam corretamente e foram verificados ao vivo.
- `encounter_id` foi de fato corrigido desde a auditoria forense de 2026-07-09 (ainda que em um modelo hoje não utilizado).

### Justificativa da nota

O motor de trilhas tem uma base de engenharia genuinamente sólida — parsing, validação de contiguidade de bandas, semântica de intervalo correta, suppression real — e 3 dos 4 scores clínicos centrais (SOFA/qSOFA/NEWS2) estão perfeitamente alinhados à literatura. Isso evita uma nota muito baixa. Porém, o sistema tem gaps que comprometem a confiabilidade clínica **hoje**: (a) MEWS diverge da literatura de forma clinicamente perigosa em um limiar de febre; (b) dois pathways inteiros (delirium, sedação) têm critérios centrais que nunca disparam devido a uma falha de autoria em YAML combinada com engolimento silencioso de erro no compilador — um problema de patient-safety silencioso; (c) o motor não pôde ser observado processando um paciente real durante a auditoria porque não há nenhum enrolamento ativo e o armazenamento é volátil (em memória); (d) o mecanismo de content-addressing que o sistema alega prover (ADR-020/021) é hoje inteiramente fake em todos os 12 pathways; (e) o RBAC tem uma inconsistência de design que torna o campo `role` funcionalmente sem sentido para controle de acesso em um sistema clínico. A combinação desses fatores — especialmente (b) e (c), que tocam diretamente a confiabilidade do "motor de decisão clínica" que é a proposta central do produto — justifica uma nota na faixa 40–50, não uma nota de reprovação total (a fundação é sólida) nem uma nota de produção-pronta (os gaps são reais e ativos, não apenas teóricos).
