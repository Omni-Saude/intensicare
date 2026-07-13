# ALERT_CONSOLIDATION_ANALYSIS.md — Workstream B (2B.0), FASE 2B

**Agente:** ALERT-ANALYSIS (somente análise — nenhum código alterado)
**Branch:** `feat/responsive-alerts-uplift` — repo `/Users/familia/intensicare`
**Ambiente:** backend `:8000` (tenant `austa`, admin/admin), frontend `:3000`, Postgres dev `intensicare` (5432)
**Momento da coleta:** 2026-07-13 ~18:39–18:55 UTC (dados via API real + 1 verificação em browser Chromium/Playwright)
**Entregável único deste agente:** este arquivo.

---

## 1. BASELINE DE FADIGA (dado real via API)

### 1.1 Totais globais

`GET /api/v1/alerts?status=all&limit=200` → `total=62`, 62 items retornados (sem paginação adicional necessária).
`GET /api/v1/alerts` (default, sem query params) → `status` default é `active` (contrato: `docs/contracts/alerts-openapi.yaml:38`, implementação: `src/intensicare/api/v1/alerts.py:140` `Query("active", alias="status")`) → **`total=55`**, mas só **50 items** vêm na página 1 (`limit` default = 50, `src/intensicare/api/v1/alerts.py:148`).

Breakdown por status (queries dedicadas, autoritativo — bate 55+2+4+1=62):

| status | total |
|---|---|
| active (default) | 55 |
| escalated | 2 (LEITO-01 SpO2<88%; LEITO-04 MEWS CRITICAL: 9) |
| acknowledged | 4 |
| resolved | 1 |
| **all** | **62** |

Breakdown por severidade (all, N=62): `critical=37, watch=22, urgent=3`.
Breakdown por `type` (all, N=62): `clinical=57`, e 5 outliers com `type` específico (`mews`, `lactate`, `spo2`, `news2`, `aki` — 1 cada; resíduo do LEITO-01/02/03, seed mais antigo, tipos ainda não normalizados para `clinical`).

### 1.2 Duas camadas de seed coexistindo (achado operacional, não é o foco mas explica o dataset)

- **Camada A — burst de hoje** (`created_at` = 2026-07-13T18:39:18–19, uma janela de **~920 ms**): 53 alertas, 4 pacientes (`MPI-DEMO-001`=18, `MPI-DEMO-002`=5, `MPI-DEMO-003`=10, `MPI-DEMO-005`=20; `MPI-DEMO-004`=**0**, confirmado — paciente "normal" de referência sem alertas, correto).
- **Camada B — seed antigo** (`created_at` = 2026-06-26 e 2026-07-10): 9 alertas, pacientes `LEITO-01..06` (nomenclatura de leito, não MPI-DEMO — outro dataset/cenário), todos singletons (sem repetição) exceto o pareamento NEWS2+MEWS por paciente (ver Taxonomia (c)).
- 53 + 9 = 62. Confirma a hipótese do prompt: **o dataset seed já produz ~53 alertas para 5 pacientes** (na verdade 53 para 4 dos 5 pacientes DEMO — DEMO-004 tem 0).

### 1.3 Agrupamento (mpi_id, família-de-sinal) — camada A (burst de hoje), min/max timestamp

Regex de normalização: título sem o valor numérico final (`"NEWS2 CRITICAL: 17"` → `"NEWS2 CRITICAL"`). 8 grupos com >1 alerta, todos dentro da janela de 920 ms:

| paciente | família (título+banda) | N | score min→max | created_at min | created_at max | Δt |
|---|---|---|---|---|---|---|
| MPI-DEMO-005 | NEWS2 CRITICAL | 10 | 11→17 | 18:39:19.357597 | 18:39:19.477798 | 120 ms |
| MPI-DEMO-005 | MEWS CRITICAL | 10 | 8→11 | 18:39:19.355223 | 18:39:19.475618 | 120 ms |
| MPI-DEMO-003 | MEWS WATCH | 10 | 3→3 (constante) | 18:39:19.106098 | 18:39:19.214139 | 108 ms |
| MPI-DEMO-001 | NEWS2 CRITICAL | 7 | 8→13 | 18:39:18.900274 | 18:39:18.976896 | 77 ms |
| MPI-DEMO-002 | MEWS WATCH | 4 | (watch band) | 18:39:19.052827 | 18:39:19.094186 | 41 ms |
| MPI-DEMO-001 | MEWS CRITICAL | 4 | 7→9 | 18:39:18.937026 | 18:39:18.974724 | 38 ms |
| MPI-DEMO-001 | MEWS WATCH | 4 | 4→4 (constante) | 18:39:18.884914 | 18:39:18.924700 | 40 ms |
| MPI-DEMO-001 | NEWS2 WATCH | 2 | 4→5 | 18:39:18.561532 | 18:39:18.860847 | 299 ms |

Mais 3 singletons na camada A (`MPI-DEMO-002 NEWS2 WATCH`=1, `MPI-DEMO-001 NEWS2 URGENT`=1) e a camada B (9 singletons/pares, patients LEITO-*).

**Interpretação do padrão temporal**: intervalos de 10–20 ms entre alertas sucessivos do mesmo paciente/score — impossível ser reingestão clínica real (vitais não chegam a cada 15 ms). É o script de seed reproduzindo uma série histórica de leituras (ver `SCORES` no painel do paciente: timestamps de vitais espalhados entre 09:39 e 15:34 do mesmo dia) processada em loop apertado no backend, sem respeitar o passo de tempo real — **e sem nenhuma barreira de deduplicação/cooldown a impedir a criação de uma linha por leitura** (causa raiz na seção 2).

### 1.4 Trilhas de escalação cruzando banda de severidade (evidência-chave para a Taxonomia §3(b))

`MPI-DEMO-001 / NEWS2`, cronológico, todas as severidades:
```
18:39:18.561  NEWS2 WATCH: 4     watch
18:39:18.860  NEWS2 WATCH: 5     watch
18:39:18.887  NEWS2 URGENT: 7    urgent
18:39:18.900  NEWS2 CRITICAL: 8  critical
18:39:18.914  NEWS2 CRITICAL: 8  critical   (dup exato)
18:39:18.927  NEWS2 CRITICAL: 9  critical
18:39:18.939  NEWS2 CRITICAL: 10 critical
18:39:18.952  NEWS2 CRITICAL: 13 critical
18:39:18.964  NEWS2 CRITICAL: 13 critical   (dup exato)
18:39:18.976  NEWS2 CRITICAL: 13 critical   (dup exato)
```
`MPI-DEMO-001 / MEWS`, cronológico:
```
18:39:18.884  MEWS WATCH: 4      watch
18:39:18.896  MEWS WATCH: 4      watch      (dup exato)
18:39:18.911  MEWS WATCH: 4      watch      (dup exato)
18:39:18.924  MEWS WATCH: 4      watch      (dup exato)
18:39:18.937  MEWS CRITICAL: 7   critical   (pula a banda urgent: threshold urgent=5, critical=7 — valor não amostrado entre 5 e 7)
18:39:18.949  MEWS CRITICAL: 9   critical
18:39:18.962  MEWS CRITICAL: 9   critical   (dup exato)
18:39:18.974  MEWS CRITICAL: 9   critical   (dup exato)
```
Estas 2 trilhas (18 alertas) contêm tanto transições reais de banda (watch→urgent→critical; watch→critical) quanto repetições exatas intra-banda — o caso didático que prova por que um dedup ingênuo por texto de título é perigoso (colapsaria a trilha inteira e esconderia a escalação) e por que um dedup por (paciente, score_type) sem checar banda também é perigoso (mesma razão).

### 1.5 Métrica-headline de fadiga (camada A, 4 pacientes com alerta)

53 linhas de alerta cru → **7 episódios clinicamente distintos** quando agrupados por (paciente, score_type, trilha contígua de banda):
1. MPI-DEMO-001 / NEWS2 — 1 trilha (10 alertas, 3 bandas: watch→urgent→critical)
2. MPI-DEMO-001 / MEWS — 1 trilha (8 alertas, 2 bandas: watch→critical)
3. MPI-DEMO-005 / NEWS2 — 1 trilha (10 alertas, 1 banda: critical, score sobe 11→17)
4. MPI-DEMO-005 / MEWS — 1 trilha (10 alertas, 1 banda: critical, score sobe 8→11)
5. MPI-DEMO-003 / MEWS — 1 trilha (10 alertas, 1 banda: watch, score constante=3, **duplicata exata pura**)
6. MPI-DEMO-002 / MEWS — 1 trilha (4 alertas, 1 banda: watch)
7. MPI-DEMO-002 / NEWS2 — singleton (1 alerta, watch)

**53 → 7 = razão de ruído 7.57×.** Este é o número a citar como baseline "itens crus vs. sinais clínicos reais" para a fadiga do intensivista.

### 1.6 Itens visíveis na UI (verificado via API + 1 passada em browser Chromium real)

- **`/alerts` default** (view do intensivista de plantão, sem filtro manual): header renderiza **"55 alertas"** (bate com `total` da API); página 1 renderiza **50 linhas** (`limit` default=50, paginação para as 5 restantes). Evidência: `frontend-v3/audit-results` não relevante aqui — capturado ao vivo via harness (`/private/tmp/.../scratchpad/e2e-live/artifacts/alert-fatigue-baseline/alerts-page-body.txt`), texto cru confirmado: título da página "Alertas", contador "55 alertas", linhas com texto literal `"Patient MPI-DEMO-005 — NEWS2 score: 17\nThreshold: 8\nTenant: austa, Unit: UTI-DEMO"` repetido variando só o score.
- **`/patient/MPI-DEMO-001`** (painel do paciente): API `GET /alerts?mpi_id=MPI-DEMO-001&status=all` → `total=18` (também `total=18` com `status=all` vs. default — todos os 18 estão em status `active`, nenhum ack/resolved para este paciente). `components/patient/alerts-panel.tsx:83-95` faz `alerts.map(...)` sem slice/limit — renderiza os 18 recebidos. Captura de browser (`patient-page-body.txt`) confirma os 18 títulos crus em sequência (`NEWS2 CRITICAL: 13`, `MEWS CRITICAL: 9`, repetido ~9×). Uma contagem heurística por botão "Confirmar" no texto capturado achou 15/18 — tratado como **artefato de captura** (regex de linha, não bug de produto: o componente não pagina/trunca no código), não deve ser usado como métrica; a métrica autoritativa é a API (18).
- Sem consolidação: **um intensivista abrindo o paciente mais crítico do plantão (DEMO-001, sepse crítica) vê 18 cartões de alerta para 2 sinais clínicos reais** (NEWS2 e MEWS, cada um com sua trilha de escalação).

---

## 2. INVENTÁRIO DO CÓDIGO

### 2.1 Ponto de criação — confirmado único NO CAMINHO VIVO, mas com um segundo local órfão

`src/intensicare/services/alert_engine.py:19-123` — `check_score_against_thresholds()`. Fluxo: resolve `ThresholdConfig` (tenant+unit ou tenant global) → calcula severidade por `>=` contra `watch/urgent/critical_threshold` → rate-limit Redis (`alert_rate:{mpi_id}:{score_type}`, `config.rate_limit_per_hour or 10`) → **cooldown Redis condicional** (`if config.cooldown_minutes:` linha 77 — **skip total se `cooldown_minutes` for `0` ou `None`**) → `Alert(...)` + `db.add()` + `flush()` (linhas 92-102) → publica WS (linha 121). Comentário no próprio código (linhas 115-118) afirma ser "the single convergence point for live alert creation... the only place that constructs Alert() on the request path" — **essa afirmação está desatualizada/imprecisa**: `grep "Alert("` em todo `src/` encontra um segundo site:

- `src/intensicare/services/ews_nrt_runner.py:656` — função `_build_alert()` (chamada a partir de `process_ews_after_vital_insert()`, linha ~672) também constrói `Alert(mpi_id=..., score_id=..., severity=..., status="active", title=..., body=..., created_at=...)`, **sem nenhum gate de rate-limit/cooldown Redis**. Confirmado **não importado/chamado por nenhuma rota ou pipeline viva** (`vitals.py` só chama `process_clinical_score` de `alert_engine.py`) — hoje é código morto, exercitado só por `tests/test_ews_nrt.py`/`test_ews_nrt_runner.py`. **Risco identificado**: se alguém ligar este runner no futuro sem replicar a disciplina de rate-limit/cooldown do `alert_engine.py`, reintroduz o mesmo bug de fadiga por um segundo caminho.

Confirmação de que `check_score_against_thresholds` é hoje o único caminho vivo: `src/intensicare/api/v1/vitals.py` chama `process_clinical_score()` (linhas 167-184 do próprio `alert_engine.py`, wrapper fino), que chama `check_score_against_thresholds`. Nenhuma outra rota/serviço em `src/` constrói `Alert()`.

### 2.2 `dedup_key` — a PROVA de "parseado mas nunca aplicado" (achado C#14)

`dedup_key` aparece em **3 contextos desconectados**, nenhum deles alcançando a criação de `Alert`:

1. **Configs de pathway/trilhas** (`_work/alerts/pathways/*.yaml` — 11 arquivos: `sepse.yaml:418`, `equilibrio.yaml:176`, `renal.yaml:143`, `respiratorio.yaml:181`, `sedacao.yaml:130`, `profilaxia.yaml:110`, `nutricao.yaml:201`, `estabilidade.yaml:161`, `delirium.yaml:119`, `desmame.yaml:168`, `ventilacao.yaml:66`) declaram um bloco `suppression: {cooldown_minutes, rate_limit_per_hour, dedup_key: ["mpi_id","criteria_id"]}`. `src/intensicare/services/alert_compiler.py:84` (`AlertDefinition.suppression: dict`) e `:361` (`suppression=raw.get("suppression") or {}`) **carregam o dict inteiro** (incluindo `dedup_key`) para dentro do objeto `AlertDefinition` compilado em memória — isso é o "parseado". Mas: `grep -rn '\.suppression\[' e '\["dedup_key"\]\|\.dedup_key'` em todo `src/` → **zero resultados**. `src/intensicare/schemas/thresholds.py:18-19,37-38` (schema Pydantic usado pelo `trilhas_evaluator`) só declara `rate_limit_per_hour` e `cooldown_minutes` — **`dedup_key` é o único campo do trio que não atravessa a fronteira para o schema tipado**. `src/intensicare/services/trilhas_evaluator.py:133-166` (função de suppression Redis-backed, chave `mpi_id+pathway_id+criterion_id`) recebe `cooldown_minutes: int, rate_limit_per_hour: int` como parâmetros — **sem parâmetro `dedup_key`**. Ou seja: existe uma suppression funcional (cooldown+rate-limit) para trilhas, mas o terceiro campo do mesmo bloco YAML — `dedup_key` — é ignorado silenciosamente na fronteira de parsing. Isso é literal e comprovadamente "parseado mas nunca aplicado".
2. **`notification_worker.py`** (`src/intensicare/services/notification_worker.py:108-125,133-173`) — dedup Redis `SETNX`-based **funcional e correto** para a camada de ENTREGA de notificação (não de criação de Alert), chave = string fornecida pelo chamador. `grep "send_alert_notification("` em `src/` → só a própria `def` (linha 133) e o registro em `WorkerSettings.functions` (linha 237). **Nenhum call-site em `src/` enfileira este job** — é um mecanismo real, testado (`tests/test_notification_worker.py`), mas órfão (nunca invocado em produção).
3. **Contrato/design v2 (aspiracional, não implementado)**: `docs/plan/architecture/api/openapi.yaml:506-509,1351` descreve um endpoint POST idempotente por `dedup_key` (`"repeat raise with same dedup_key returns 200 with recurrence_count incremented"`) e `docs/plan/_work/alerts/correlation-engine.yaml` usa `dedup_key: "patient_id+alert_id"` dentro de blocos `suppression` das correlações cross-domain. Isso é **plano/documento**, não código executando — ver §2.3.

**Conclusão C#14 confirmada com prova de código**: não existe coluna `dedup_key` no modelo `Alert` (nenhuma migration Alembic a adiciona), não existe lógica em `check_score_against_thresholds` que compute ou consulte um `dedup_key`, e nas 2 outras trilhas onde o campo aparece (pathways YAML, notification_worker) ele é parseado/aceito mas nunca chega a afetar se um `Alert` é criado.

### 2.3 `correlation-engine.yaml` + `correlation_engine.py` — motor completo e testado, porém DESCONECTADO

Dois arquivos `correlation-engine.yaml`: `docs/plan/_work/alerts/correlation-engine.yaml` (296 linhas — catálogo de 4 correlações cross-domain: `ALERT-CORR-SEPSIS-AKI-01`, `ALERT-CORR-RESP-HEMO-02`, `ALERT-CORR-QTC-ELEC-03`, `ALERT-CORR-EXAM-REDUND-04`, mais um `cross_domain_grouping: GROUP-CORR-DETERIORATION-CLUSTER-01`) e `docs/plan/_work/domain-interfaces/correlation-engine.yaml` (67 linhas, contrato de interface). **Nenhum dos dois é carregado em runtime**: `grep "yaml.safe_load\|yaml.load"` referenciando este arquivo em `src/` → zero. `src/intensicare/services/correlation_engine.py` (870 linhas, docstring linha 1-23 cita o YAML como fonte) **reimplementa as constantes à mão em Python** (`JOIN_WINDOWS`, `PPV_BUDGET`, `CORRELATION_SEVERITY` — linhas 41-102) — o YAML é documentação-fonte que o Python foi escrito para espelhar, não um config parseado.

Mais grave: `grep "correlation_engine\|CorrelationEngine"` em todo `src/` → **só o próprio arquivo aparece**. Nenhum caller em `alert_engine.py`, `vitals.py`, nenhuma rota de API. O motor de correlação — que implementa exatamente o mecanismo de fold/supressão/amplificação que o Workstream B precisa (`member_suppressed`, cooldown por correlação, break-through de severidade) — está **totalmente implementado e testado em isolamento** (`tests/test_correlation_engine.py` exercita `CorrelationEngine.evaluate_single()` com os 8 vetores TV-1..TV-8 por correlação) mas **nunca é invocado a partir do caminho de criação de Alert real**. As 4 correlações que ele calcula (Sepsis+AKI, Resp+Hemo, QTc+Eletrólito, Exame redundante) também **não são o mesmo problema** observado no baseline — o baseline é sobre repetição do MESMO score de domínio único (NEWS2/MEWS re-disparado), não sobre correlação cross-domain. Achar isso é importante para não confundir a solução: ligar `correlation_engine.py` não resolveria a fadiga observada em §1.

`tests/rules/test_alert_vectors.py` (único arquivo em `tests/rules/`) faz `glob *.yaml` em `docs/plan/_work/alerts/` e valida **só a forma estrutural** dos `test_vectors:` (campos obrigatórios, enums válidos) — é um linter de schema do corpus YAML, **não executa a lógica de correlação** contra os vetores (não há `import` de `CorrelationEngine` neste arquivo). Os "vetores TV-*" citados no prompt não são arquivos `TV-*` separados — são entradas inline dentro do YAML (`test_vectors: [{id: TV-1, ...}]`).

`alert_compiler.py`'s `AlertCompiler`/`compile_alert_registry()` (glob de `docs/plan/_work/alerts/*.yaml`) **é** chamado em runtime, mas só a partir de `SepsisDomainService._ensure_loaded()` (`domain_sepsis.py:504-506`), e `SepsisDomainService` por sua vez não tem caller vivo fora de `domain_piora_clinica.py` (também sem caller vivo) e testes — outra camada de infraestrutura pronta mas não conectada à criação real de `Alert`.

### 2.4 Modelo `Alert` — colunas existentes vs. o que faltaria para agrupar

`src/intensicare/models/alert.py:12-61`, tabela `alert` (TimescaleDB hypertable em `created_at`):

Colunas existentes: `id, mpi_id, score_id, severity, status, definition_version_id, correlation_event_id, title, body, created_at, acknowledged_at, acknowledged_by, resolved_at, resolution`.

- **`correlation_event_id`** (FK para `correlation_event`, linha 41-45) — **já existe como stub de schema** para linkar um alerta a um evento de correlação, mas `check_score_against_thresholds` (§2.1) nunca a popula. É o único "gancho" de agrupamento já presente no schema hoje, e está vazio para 100% dos 62 alertas do baseline.
- **Confirmado ausente**: `occurrence_count`, `last_seen_at`, `group_id`/`dedup_key`. Qualquer desenho de "atualizar alerta aberto em vez de criar N" (§4, opção i) exige migração Alembic para adicionar pelo menos `occurrence_count` (int, default 1) e `last_seen_at` (timestamptz).
- **Confirmado no contrato mas NÃO no modelo** (hardcoded no endpoint): `resolved_by` — `src/intensicare/api/v1/alerts.py:132` retorna sempre `None` com comentário `# Not tracked on Alert model yet`; `pathway_name` — linha 128, mesmo padrão (`# Not available on Alert model yet`). Débito pré-existente, não introduzido por este ciclo, mas relevante se o desenho de consolidação usar `pathway_name` como chave de agrupamento por apresentação.

### 2.5 Contrato `docs/contracts/alerts-openapi.yaml` — superfície atual (394 linhas)

`GET /alerts` (linhas 11-100): params `status` (enum `active|acknowledged|escalated|resolved|all`, default `active`), `severity`, `unit`, `mpi_id`, `limit` (max 200, default 50), `offset`. **Sem `groupBy`.** `AlertResponse` (linhas 267-333): `id, type, severity, title, message, mpi_id, patient_name, pathway_name, created_at, acknowledged_at, resolved_at, resolved_by, resolution` — **sem `occurrence_count`, `last_seen_at`, `group_id`, `dedup_key`**. Implementação bate 1:1 com o contrato (`src/intensicare/api/v1/alerts.py:137-192`, query simples com `WHERE`s, `ORDER BY created_at DESC`, sem `GROUP BY`). Qualquer desenho que exponha agregação por paciente precisa estender este contrato (novo campo/endpoint) + regenerar do `app.openapi()` + `scripts/ci/check_openapi_drift.py` verde (regra de ouro §19 do prompt-mãe).

### 2.6 Publisher WS `alert.raised`

Único publish-site: `src/intensicare/services/alert_engine.py:131-164` (`_publish_alert_raised`), chamado 1× por `Alert` criado (linha 121, dentro de `check_score_against_thresholds`). Payload: `{alert_id, mpi_id, severity}` — mínimo. Consumidores frontend (`app/page.tsx:23`, `app/alerts/page.tsx:61`, `app/patient/[mpi_id]/page.tsx:82`) **todos ignoram o payload** e só chamam `mutate()`/`mutateAlerts()` (revalidação SWR) — ou seja, a cardinalidade do evento WS não é hoje observável pelo usuário além de disparar um re-fetch. **Implicação para o desenho**: mudar a cardinalidade de criação de `Alert` (write-side dedup) muda 1:1 a cardinalidade de eventos WS, mas como o consumidor só re-busca a lista, o impacto real na UI é 100% determinado pelo que `GET /alerts` retorna — não pelo número de eventos WS em si. Isso reduz o risco de uma mudança write-side quebrar o WS (nenhum acúmulo client-side de eventos a corrigir).

### 2.7 UI — como renderiza hoje

- **`components/alerts/alert-table.tsx`** (156 linhas): lista plana `role="list"`, um `AlertRow` por item de `alerts` — **sem agrupamento**.
- **`components/alerts/alert-row.tsx`** (203 linhas): **já implementa o padrão disclosure APG** — `<button aria-expanded={expanded} aria-controls={detailsId}>` (linhas ~62-78) alterna uma região de detalhe `<div role="region" hidden={!expanded}>` (linhas ~158-199), documentado explicitamente em comentário como "WAI-ARIA APG disclosure pattern" (linhas ~43-56). Isso é reusável diretamente para renderizar um grupo (resumo = paciente+contagem+severidade máx; expandido = membros).
- **`components/alerts/filter-bar.tsx`** (252 linhas): filtros severidade/status/período/unidade/pathway — sem controle `groupBy`.
- **`components/alerts/quick-actions.tsx`** (228 linhas): Reconhecer/Escalar/Não procede/Resolver, uma ação por `alert.id` — precisaria de variante "ação em grupo" se ack/resolve de grupo for adjudicado (§6).
- **`components/patient/alerts-panel.tsx`** (99 linhas) delega para **`components/patient/alert-item.tsx`** (129 linhas): cartão plano, **sem disclosure** (`AlertItem` não tem `aria-expanded`), `alerts.map(...)` direto sem slice/agrupamento (confirmado §1.6).

---

## 3. TAXONOMIA DOS DUPLICADOS (com contagens, camada A — 53 alertas)

| categoria | definição | grupos | alertas envolvidos | exemplo |
|---|---|---|---|---|
| **(a) mesmo sinal, mesma banda, candidato a rollup** | repetição do mesmo score_type+severidade, sem cruzar limiar de banda | 4 trilhas puras de 1 banda | MPI-DEMO-005/NEWS2 (10, critical, 11→17), MPI-DEMO-005/MEWS (10, critical, 8→11), MPI-DEMO-003/MEWS (10, watch, constante 3), MPI-DEMO-002/MEWS (4, watch) | ver §1.3 |
| **(b) mesmo sinal, escalação de severidade — NUNCA consolidar silenciosamente** | mesma trilha (paciente+score_type) cruza banda(s) dentro da janela do burst | 2 trilhas | MPI-DEMO-001/NEWS2 (10 alertas, watch→urgent→critical), MPI-DEMO-001/MEWS (8 alertas, watch→critical, pulando urgent) | ver §1.4 |
| **(c) sinais distintos do mesmo paciente — agrupável só por apresentação** | NEWS2 e MEWS (ou outros scores) do MESMO paciente, calculados a partir de vitais sobrepostos mas com thresholds/semânticas próprias — não são "o mesmo alerta" | qualquer paciente com >1 score_type ativo (todos os 4 pacientes DEMO da camada A; LEITO-04 e LEITO-06 na camada B) | LEITO-06: NEWS2 CRITICAL + MEWS CRITICAL disparados a 3.5 ms de distância (16:25:58.210667 e .214157) — pares análogos em LEITO-04 | — |
| **(d) duplicata exata — bug/seed** | mesmo título, mesma severidade, **mesmo valor de score**, timestamps a poucos ms | sub-runs dentro de (a)/(b) | MPI-DEMO-003/MEWS WATCH: **10/10 alertas com score=3 idêntico** (o caso mais puro); dentro de MPI-DEMO-005/MEWS CRITICAL: score=8 repetido 6× idêntico; dentro de MPI-DEMO-001/MEWS WATCH: score=4 repetido 4× idêntico; dentro de MPI-DEMO-001/NEWS2 CRITICAL: score=8 2× e score=13 3× idênticos | ver §1.4 |

**Observação de desenho crítica**: (a) e (d) não são mutuamente exclusivos — todo grupo (d) está contido dentro de um grupo (a) ou (b) maior (a duplicata exata é o caso extremo de "mesma banda"). (b) e (c) nunca devem ser colapsados sem preservar a trilha/o par visível. Um motor de rollup correto precisa detectar (b) (mudança de banda) para **nunca** aplicá-lo silenciosamente, e tratar (c) como agrupamento apenas de apresentação (cartão "paciente" com 2 sub-linhas, não uma fusão).

**Achado colateral de tendência sub-banda**: mesmo dentro de grupos (a) puros (MPI-DEMO-005), o score sobe monotonicamente (NEWS2: 11→17, +55%; MEWS: 8→11, +37%) sem trocar de banda-rótulo. Um rollup que mostre só "critical ×10" sem a tendência esconde uma deterioração real dentro da mesma banda. Recomenda-se que o grupo carregue min/max/tendência do valor, não só a contagem.

---

## 4. DESENHOS DE CONSOLIDAÇÃO (2–3, com trade-offs) — PARA ADJUDICAÇÃO, NÃO IMPLEMENTAR

### Opção (i) — Dedup na ESCRITA (upsert no ponto único de criação)

`check_score_against_thresholds` (`alert_engine.py:92-102`), antes de `Alert(...)`, consulta se já existe um `Alert` **aberto** (`status='active'`) para `(mpi_id, score_type, severidade IGUAL)` dentro de uma janela/cooldown; se sim, faz `UPDATE` (incrementa `occurrence_count`, atualiza `last_seen_at`, mantém `created_at` original) em vez de `INSERT`; se a severidade mudou (banda diferente), sempre insere uma linha NOVA (nunca funde uma escalação).

- **Risco clínico**: baixo-médio SE a regra "banda diferente sempre insere novo" for implementada corretamente (a trilha (b) fica preservada) — mas é a opção com maior superfície de lógica nova a testar unitariamente (é fácil errar a fronteira "mesma banda" vs "escalou").
- **Contrato/drift**: exige migração Alembic (`occurrence_count`, `last_seen_at` — colunas confirmadas ausentes §2.4) + estender `AlertResponse`/`alerts-openapi.yaml` com esses 2 campos + drift check.
- **WS**: reduz cardinalidade de `alert.raised` 1:1 com as linhas suprimidas (bom para fadiga), mas evento de "occurrence_count incrementado" num alerta já existente precisa de um payload/tipo de evento diferente (ou o mesmo evento com `alert_id` repetido) — os 3 consumidores frontend já ignoram o payload e só reagem revalidando (§2.6), então baixo risco de quebra, mas exige decidir a semântica do evento.
- **Complexidade de teste**: média-alta (upsert concorrente sob a mesma corrida de ingestão, janela de cooldown, fronteira de banda) — precisa de testes de integração com Postgres real, não só unitário.
- **Semântica ack/resolve**: ack de um alerta com `occurrence_count>1` = ack de "todas as ocorrências dedupadas até agora"? E se uma nova ocorrência chegar depois do ack (reabre? cria novo?) — **decisão explícita necessária (ver §6)**.

### Opção (ii) — Agregação na LEITURA (endpoint/param `groupBy=patient`, zero mudança de escrita)

`GET /alerts` ganha `groupBy=patient` (ou `patient+score_type`); a query SQL agrega em memória/SQL (`GROUP BY mpi_id, score_type` + `MAX(severity ordinal)`, `MIN/MAX(created_at)`, `COUNT(*)`) e retorna uma resposta com grupos + membros crus (todo alerta original continua na lista de membros, nada é escrito/alterado no banco). UI: `alert-row.tsx` (já tem o padrão disclosure APG, §2.7) renderiza o resumo do grupo; expandir mostra os N membros individuais com suas próprias ações de ack/resolve.

- **Risco clínico**: **mais baixo** de todas as opções — nenhuma alteração na criação/persistência de `Alert`, zero risco de perder ou fundir incorretamente um evento clínico (a fonte de verdade nunca muda). A escalação (b) é trivialmente preservada porque cada linha original continua existindo; a UI só precisa decidir como apresentar a tendência dentro do grupo.
- **Contrato/drift**: menor mudança de contrato — 1 novo query param + 1 novo shape de resposta (`AlertGroupResponse` opcional, aditivo — não quebra consumidores existentes que não passam `groupBy`). Nenhuma migração de banco.
- **WS**: zero impacto — `alert.raised` continua 1:1 por `Alert` criado; o cliente decide se refaz o agrupamento ao revalidar.
- **Complexidade de teste**: **menor** — é uma transformação pura de leitura, testável com fixtures estáticas, sem necessidade de simular concorrência de escrita.
- **Semântica ack/resolve de grupo**: mesma pergunta da opção (i) permanece (ack do grupo = ack de todos os membros visíveis no momento?), mas o "custo de errar" é menor porque nada foi fundido na fonte — reverter uma decisão de UX de agrupamento é um deploy de frontend, não uma migração de dados.
- **Limitação**: não resolve o crescimento ilimitado da tabela `alert` (o burst de 53 linhas continua existindo fisicamente; só não é tudo mostrado de uma vez) — para o cooldown/rate-limit já existente (§2.1) isso é aceitável hoje (`cooldown_minutes=0` no tenant `austa` é uma escolha de config, não um limite físico), mas em produção real (não-seed) o INSERT sem controle de banda continua sendo uma fonte de crescimento de tabela que a opção (ii) não trata.

### Opção (iii) — Híbrida: rollup NA LEITURA agora + fechar o `cooldown_minutes` misconfigurado como pré-requisito

Implementar (ii) primeiro (menor risco, ship rápido) E, em paralelo, **corrigir a causa raiz operacional já comprovada em §1.3**: o tenant `austa` tem `cooldown_minutes=0` (confirmado via `GET /api/v1/thresholds`) para MEWS/NEWS2 — isso desliga completamente o único gate de repetição que `check_score_against_thresholds` já possui (linha 77: `if config.cooldown_minutes:` é `False` quando `0`). Ajustar esse valor de config (não é mudança de código, é dado de seed/admin) já reduziria drasticamente o burst futuro sem tocar em `alert_engine.py`. Depois, se a adjudicação decidir que a leitura agregada não é suficiente a longo prazo (ex.: performance da tabela, necessidade de `occurrence_count` visível fora do agrupamento), evoluir para (i) como incremento sobre a base de (ii) — o contrato de leitura agregada não precisa mudar quando a escrita passar a ser upsert (o `GROUP BY` na leitura vira redundante mas inofensivo).

- **Trade-off**: entrega valor imediato de baixo risco (ii) + resolve a causa raiz mais barata (config de cooldown) sem esperar a opção mais arriscada (i); mas adia a pergunta "a tabela `alert` deveria parar de crescer 1:1 por leitura" para um ciclo futuro.

### Recomendação

**Opção (ii) — agregação na leitura — como entrega deste ciclo**, com a correção de `cooldown_minutes` (parte da opção iii) registrada como achado de config a corrigir separadamente (não é mudança de contrato/código, é dado). Justificativa em 5 linhas:
1. Menor risco clínico: fonte de verdade (`Alert` rows) nunca é alterada/fundida, cada evento original permanece 100% auditável e alcançável — atende ao requisito inviolável "zero perda de informação" sem esforço extra de design.
2. `alert-row.tsx` já implementa o padrão disclosure APG necessário para grupo→membros — reuso direto, sem novo padrão de acessibilidade a inventar/testar.
3. Menor mudança de contrato (aditiva, 1 param + 1 schema novo) e zero migração de banco — mais fácil manter o drift-check verde e o ciclo dentro do prazo.
4. WS não muda de forma alguma — elimina uma classe inteira de risco de regressão no pipeline de tempo real.
5. Não fecha a porta para a opção (i) depois — se a adjudicação decidir que o crescimento físico da tabela e `occurrence_count` persistente são necessários no futuro, a opção (i) pode ser construída por cima sem quebrar o contrato de leitura agregada já entregue.

---

## 5. HUMANIZAÇÃO (subsídio)

### 5.1 Formato cru atual — de onde vem

Título e corpo são montados **inline** em `alert_engine.py:85-90`, dentro de `check_score_against_thresholds`, sem nenhuma camada de template:

```python
title = f"{clinical_score.score_type} {severity.upper()}: {score_value}"
body = (
    f"Patient {clinical_score.mpi_id} — {clinical_score.score_type} score: {score_value}\n"
    f"Threshold: {getattr(config, severity + '_threshold')}\n"
    f"Tenant: {tenant_id}, Unit: {unit or 'N/A'}"
)
```

Exemplos reais capturados no baseline (§1): `"NEWS2 CRITICAL: 17"` / `"Patient MPI-DEMO-005 — NEWS2 score: 17\nThreshold: 8\nTenant: austa, Unit: UTI-DEMO"`; `"MEWS WATCH: 3"` / `"Patient MPI-DEMO-003 — MEWS score: 3\nThreshold: 3\nTenant: austa, Unit: UTI-DEMO"`. Não há interpretação clínica, tendência, nem próxima ação — é uma serialização direta de variáveis internas (`score_type`, `severity`, `score_value`, `threshold`, `tenant_id`, `unit`), voltada para debug, não para leitura por um clínico sob pressão.

### 5.2 Onde os templates centralizados deveriam viver

Junto do ponto único de criação (`alert_engine.py`, ao lado de `check_score_against_thresholds`, ou um módulo novo `alert_copy.py`/`alert_templates.py` no mesmo pacote `services/`), parametrizado por `(score_type, severity, score_value, threshold, trend?)` — nunca string solta espalhada pela UI. Um mapa por `score_type × severidade` (NEWS2/MEWS × watch/urgent/critical, mínimo 6-8 combinações reais observadas no baseline) é suficiente para cobrir o dataset atual; a estrutura deveria já prever cabimento para os `score_type` que ainda faltam entrar no pipeline vivo (SOFA/qSOFA — citados no comentário de `alert_engine.py:118` como já suportados por `process_clinical_score`, mas não vistos no baseline atual porque o seed só gerou MEWS/NEWS2).

### 5.3 Referência de tom já validada no código — `pathway_enrollment.py` / `cds_hooks.py`

`src/intensicare/services/pathway_enrollment.py`, função `_build_recommendation()` (linhas ~819-1019), já implementa exatamente o padrão de 3 partes pedido pelo prompt-mãe (o que aconteceu / por que importa / o que verificar), em PT-BR clínico, por severidade, com prefixo consistente:

```python
# severity == "critical" (pathway Sepse, linhas ~820-828)
f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
f"{eval_str}; critério em faixa crítica. ACIONAR PROTOCOLO DE SEPSE IMEDIATAMENTE. "
"Verificar: antibiótico administrado? Culturas coletadas? Ressuscitação volêmica "
"iniciada? Lactato >4 mmol/L requer reavaliação em 2-4h. Considerar acesso central e "
"droga vasoativa."

# severity == "urgent"
f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
f"{eval_str}; critério em faixa urgente. Completar bundle da 1ª hora: "
"coletar culturas, administrar antibiótico, iniciar cristaloide 30 mL/kg. "
"Reavaliar lactato em 2-4h."
```

Padrão genérico (fallback para pathways sem caso especial, linhas ~996-1019): prefixo por severidade `⚠️ ALERTA CRÍTICO` / `⚠️ ATENÇÃO` / `Acompanhar` / `✓ Dentro das metas`, seguido de em-dash, nome do pathway+estado, uma cláusula de transparência (`"N de M critérios avaliados"`), e uma frase de ação objetiva com janela de reavaliação (`"reavaliar em 6-12h"`). `src/intensicare/api/v1/cds_hooks.py:74-79` mapeia a mesma severidade de 4 níveis para o indicador CDS Hooks de 3 níveis (`{"normal":"info","watch":"info","urgent":"warning","critical":"critical"}`) e `_build_detail()` (linhas 211-276) monta um corpo estruturado (critérios atendidos/não atendidos + recomendação) — é o padrão de referência mais próximo e já em produção para replicar no template de alerta humanizado.

### 5.4 UI — onde o corpo explicativo deveria renderizar

`alert-row.tsx` já tem a região expandida (disclosure APG, §2.7) — o corpo explicativo (o que aconteceu/por que importa/o que verificar) cabe ali sem inflar a linha compacta (que mantém só título curto + badge de severidade), amarrando com QW-4/QW-5 da FASE 1 (densidade mobile). `alert-item.tsx` (painel do paciente) não tem disclosure hoje — se a humanização for renderizada lá também, precisa decidir entre (a) adicionar o mesmo padrão disclosure ou (b) mostrar sempre o corpo curto e mover o detalhe completo para a trilha/trace já existente (`alert-trace.tsx`).

---

## 6. DECISÕES QUE EXIGEM ADJUDICAÇÃO DO ORQUESTRADOR

1. **Confirmar a opção de desenho** (§4): (ii) agregação-na-leitura como recomendado, ou preferência por (i)/(iii)?
2. **Semântica de ack/resolve de grupo** (invariante clínico do prompt-mãe, item 2B.1): ack do grupo = ack de todos os membros exibidos no momento? E se um membro novo (potencialmente escalado) chegar depois do ack do grupo — o grupo "reabre"? Precisa de um ADR curto antes de qualquer implementação, conforme já antecipado no prompt-mãe.
3. **Config `cooldown_minutes=0`** no tenant `austa` (raiz operacional do burst, §4 opção iii) — é intencional (para demo/teste) ou deveria ser corrigido junto com o ciclo de consolidação? Se corrigido, isso sozinho já reduz o burst futuro sem qualquer mudança de código.
4. **Escopo de `groupBy`**: agrupar só por `(mpi_id, score_type)` (mais conservador, preserva a distinção de sinais §3(c)) ou por `mpi_id` puro com sub-agrupamento por score_type dentro do cartão do paciente (mais compacto, mas exige decidir a ordem de exibição de múltiplos score_types por paciente)?
5. **Alcance da humanização neste ciclo**: cobrir só NEWS2/MEWS (os únicos `score_type` observados no baseline vivo) ou já preparar o template para SOFA/qSOFA (citados no código como suportados mas não exercitados pelo seed atual)?
6. **`ews_nrt_runner.py:656`** (segundo site de criação de `Alert`, hoje morto): arquivar/remover formalmente, ou deixar como está com um comentário de aviso? Risco de alguém religar sem a disciplina de rate-limit no futuro.

---

## Arquivo entregue

`docs/audit/ALERT_CONSOLIDATION_ANALYSIS.md` (este arquivo) — único artefato escrito por este agente. Evidência de apoio (JSON bruto da API, capturas de tela/texto do browser) em `/private/tmp/claude-501/-Users-familia-intensicare/2ddd8939-1ffb-4de3-9d7a-7a418c3d7b1a/scratchpad/` (`alerts_all_200.json`, `alerts_default_200.json`, `pat_MPI-DEMO-*.json`, `e2e-live/artifacts/alert-fatigue-baseline/`).
