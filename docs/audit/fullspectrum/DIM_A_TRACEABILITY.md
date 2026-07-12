# Dimensão A — Rastreabilidade Produto → Especificação → Implementação

**Auditor:** Claude (Fable 5), agente especialista em rastreabilidade — auditoria somente leitura
**Data:** 2026-07-12
**Escopo:** `/Users/familia/intensicare/` — todo o histórico de docs de produto, ADRs, contratos OpenAPI e o código atual
**Método:** leitura direta de arquivos-fonte + 4 sub-agentes de pesquisa paralelos (ADRs/gates, gaps forenses, contratos vs API viva, trace ponta-a-ponta da sepse) + verificação cruzada manual (git log, `gh pr view`)

---

## 1. Problema original

### 1.1 Onde está documentado

O problema do intensivista está documentado desde o primeiro commit de produto do repositório:

- **`docs/product/vision.md`** (commit `c405eb5`, 2026-06-26, "docs: análise técnica completa, PRD, ADR-001, plano de implementação e fundação DevOps") — §1 "Propósito" (linhas 9-11): *"O Intensicare é uma plataforma de suporte à decisão clínica para Unidades de Terapia Intensiva (UTI)... ingerindo sinais vitais, resultados laboratoriais e dados de prontuário eletrônico para gerar alertas inteligentes e recomendações baseadas em evidência."*
- **`docs/plan/product/product-spec.md`** (v2 build plan, mesclado 2026-07-06, PR #2) — §1 formaliza 4 personas com *jobs-to-be-done* explícitos, com a dor central do Dr. Carlos citada literalmente (linha 33-34): *"Today he receives ~200 alerts/day with ~80% false positives"* e da Enf. Ana (linha 51): *"manually calculates and charts MEWS (~20 min/shift per patient)"*.
- O README.md não contém uma seção de "problema" isolada — a dor do usuário só aparece nos docs de produto acima, não no README (achado MINOR, doc-hygiene).

**Conclusão:** o problema está bem documentado e é rastreável desde a origem do projeto — não é uma lacuna.

### 1.2 Métricas de sucesso

Sim, definidas em dois níveis, com boa granularidade:

- **`docs/product/vision.md` §7** — métricas clínicas (§7.1: sensibilidade sepse 45%→≥80%, PPV 35%→≥60%, tempo até ação 42min→≤15min, alarm fatigue 25%→≤10%, mortalidade −10%) e técnicas (§7.2: latência p95 <30s, disponibilidade 99,9%, throughput >500 alertas/min, retenção 7 anos, versionamento 100% auditável).
- **`docs/plan/product/product-spec.md` §3** — refina essas métricas em **12 critérios de persona (PER-\*-NN)**, cada um com instrumento de medição nomeado (evento/dado de auditoria específico) — ex.: `PER-CARLOS-01`: *"Score disponível em <30s após coleta de vitals"* → instrumento: *"Timestamp pair per score: vitals `recorded_at` → `clinical_score.calculated_at`; OTel span + p95 gauge"* (linha 435).

Este nível de rigor (métrica → instrumento de telemetria nomeado) é incomum e é um ponto forte real da documentação — não um achado de gap.

---

## 2. Tradução para especificação

### 2.1 Rastro do problema até requisitos técnicos

A cadeia documental é bidirecional e mecanicamente gerada em grande parte:

- `docs/plan/product/product-spec.md` §2 traduz cada JTBD em **User Stories (US-01..US-30)** com MoSCoW, critérios de aceite e ids de persona.
- §5 do mesmo arquivo é uma **tabela de rastreabilidade explícita** Story → Persona-criteria → Métricas (30 linhas, cobertura declarada de "todos os 12 critérios de persona aparecem em ≥1 story").
- `docs/plan/clinical/domains/*.md` (9 specs) traduzem os domínios clínicos do `vision.md` §3 em regras com thresholds, evidência (ex.: `docs/plan/clinical/domains/sepsis.md` cita Bone 1992, Seymour 2016 JAMA, SSC 2021 com valores corrigidos face à literatura legada).
- `docs/plan/traceability-matrix.md` é **gerado mecanicamente** (`docs/plan/_work/scripts/build_matrix.py`) a partir de `_work/dispositions/` e cobre **960 regras legadas** com disposição (ADOPT/ADAPT/SUPERSEDE/RETIRE/RATIFY) e link para o artefato técnico que as herda.

Isso é uma infraestrutura de rastreabilidade textual **muito acima da média** — a lacuna real não é a existência de rastro documental, é a fidelidade desse rastro ao que roda em produção (ver §2.2 e §4).

### 2.2 Amostragem bidirecional: sepse (problema → spec → implementação)

Trace completo executado ponta-a-ponta (vision.md → domínio clínico → YAML de trilha → contrato → engine → endpoint → tela → teste):

| Elo | Artefato | Status |
|---|---|---|
| 1. Problema | `docs/product/vision.md:40-56` §3.1 "Infecção e Detecção de Sepse" — sepse é #1 causa de morte em UTIs brasileiras, SSC 2021, Seymour 2016 | ✅ EXISTE |
| 2. Spec clínica | `docs/plan/clinical/domains/sepsis.md` — SIRS ≥2/4, qSOFA≥2 + infecção presumida, choque séptico (lactato≥4 OU PAM<65+vasopressor), timers de bundle 1h/3h, 6 alertas nomeados `ALERT-SEPSIS-SCREEN-01`..`06` | ✅ EXISTE, evidência completa |
| 3. YAML de trilha (catálogo atual) | `_work/alerts/pathways/sepse.yaml` (v3.0.0) — critérios graduados (qSOFA, lactato, PAM, PCT, culturas, ATB), 5 estados (`initial→confirmacao→tratamento→estabilizacao→alta`) | ⚠️ PARCIAL — thresholds de lactato/PAM/qSOFA batem com sepsis.md, **mas não tem critério SIRS, não tem gate de infecção presumida, não tem split PCT-subida/desescalada, não tem lógica de timer de bundle** |
| 4. Contrato OpenAPI | `docs/contracts/pathways-openapi.yaml` — endpoints genéricos parametrizados por `pathway_id`/`slug`, nenhuma menção literal a "sepse" | ✅ EXISTE (genérico, por design) |
| 5. Engine backend fiel à spec | `src/intensicare/services/domain_sepsis.py` (1022 linhas) — implementa fielmente as 6 funções `_eval_*` de sepsis.md, carrega definições de `docs/plan/_work/alerts/sepsis.yaml` via `compile_alert_registry()` | ⚠️ **CÓDIGO MORTO** — nenhum router de `api/v1/*.py` importa ou chama este serviço |
| 6. Endpoint API real | `src/intensicare/api/v1/pathways.py` — `GET /api/v1/pathways/{id}`, `.../pathways/{id}/progress` — wired ao **`TrilhasEngine`**, que carrega `_work/alerts/pathways/` (o YAML do elo 3, mais simples) | ✅ EXISTE, mas aponta para a implementação mais pobre |
| 7. Tela frontend | `frontend-v3/app/patient/[mpi_id]/pathway/[pp_id]/page.tsx` — consome `fetchPathwayProgress()`, renderiza componentes genéricos (`StateFlow`, `CriteriaList`, `RecommendationsPanel`) | ✅ EXISTE, 100% data-driven, mas mostra o critério empobrecido do elo 3/6 |
| 8. Testes | `tests/test_domain_sepsis.py` (722 linhas) — 31 vetores validando o `domain_sepsis.py` do elo 5 | ⚠️ **testa o código morto**, não o caminho que a API/tela realmente serve |

**Achado central desta amostra:** existem **duas implementações paralelas e não integradas de sepse** no backend. A implementação fiel à especificação clínica ratificada (`domain_sepsis.py`, com SIRS, gate de infecção, estratificação PCT, timers de bundle SSC-2021, testada com 31 vetores) é código morto — nenhum endpoint HTTP a alcança. A implementação que efetivamente serve a tela do intensivista (`sepse.yaml` via `TrilhasEngine`) é uma reescrita independente e mais simples, sem SIRS, sem estewardship de PCT e sem timers de bundle. **A trilha de maior prioridade clínica do produto (P1 em `vision.md` §5.1) e o benchmark declarado do MVP (ADR-0031) é exatamente onde a rastreabilidade spec→runtime quebra.**

---

## 3. Decisões arquiteturais

### 3.1 ADRs 0030–0034: justificativa clínica ou puramente técnica?

Todas as 5 ADRs são **autoria exclusiva de "Niemeyer (System Architect)"** — nenhuma tem coautoria ou revisão de um médico/intensivista registrada no próprio documento.

| ADR | Natureza da justificativa | Trecho citado |
|---|---|---|
| **ADR-0030** (arquitetura de trilhas no frontend) | Técnica/UX, com linguagem clínica decorativa | linha 12: *"O intensivista precisa navegar entre múltiplas páginas para entender o estado de um único paciente — o oposto de um centro de comando clínico."* Sem estudo, sem dado de outcome citado. |
| **ADR-0031** (sepse como MVP) | Engenharia pura — sepse escolhida por ser "teste de estresse" para os componentes genéricos | linha 35: *"É o teste de stress ideal para os componentes genéricos."* Guidelines (SSC-2021, KDIGO, CAM-ICU) aparecem só como metadado em tabela comparativa, não como argumento. |
| **ADR-0032** (rebuild do zero) | Diretriz de product owner, não evidência clínica | linha 16: *"Frontend do zero, 100% novo, sem reutilizações... UX precede design."* (citação do product owner) |
| **ADR-0033** (pathway view genérico) | Princípio de engenharia (DRY) | linha 77: *"Rejeitada porque: Viola o princípio DRY e repete o erro do v2."* |
| **ADR-0034** (WebSocket/realtime) | Técnica, com um requisito de latência clínica **afirmado sem fonte** | linha 89: *"UTI requer latência < 5s para alertas críticos"* — sem citar guideline ou estudo. |

**Conclusão:** a arquitetura pathway-centric foi uma **decisão de produto/engenharia** (reduzir 33 páginas fragmentadas do frontend v2 para uma jornada de 7 rotas), não uma decisão clinicamente fundamentada em evidência de outcome. Isso por si só não é um defeito — mas a documentação não afirma isso explicitamente, criando uma leitura enganosa de que a arquitetura "resolve o problema clínico" quando na verdade resolve um problema de navegação de UI.

### 3.2 Evidência de validação por médico/intensivista

**Não há nenhuma evidência de validação clínica real em todo o repositório.** Evidência coletada:

1. **Gate G1 nunca executado com médico.** `docs/audit/handoff-product-designer/HANDOFF.yaml:200-206` define explicitamente:
   ```
   - id: "G1"
     after: "M3"
     reviewer: "Arquiteto + Médico intensivista"
     criteria: [...]
   ```
   Mas o mesmo arquivo, na milestone M3 (linhas 101-106), só registra `gatekeeper_scores`: `ds_governance: 92%`, `a11y: 88/100`, `ux: 6.3/10` — **não existe campo de score clínico**. O `meta.status` do documento (linha 11) é `"all_milestones_completed"`, isto é, o projeto foi declarado concluído apesar de o gate G1 nunca ter produzido um artefato de revisão médica.

2. **Os "revisores clínicos" do plano v2 são personas de IA, não médicos.** `docs/plan/_work/panels/*/score-clinical-safety-officer-*.yaml` e `docs/plan/_work/scripts/panel_decide.py:46` confirmam que `clinical-safety-officer` é uma chave de `scorer` processada por um script de ponderação automática (`WEIGHTS = {"safety": 0.30, ...}`). `docs/plan/_work/panels/home-surface/decision.yaml:48-51` tem `scorers: [clinical-safety-officer, clinical-ux-researcher]` seguido de `signoffs: []` — **lista de assinaturas explicitamente vazia**, confirmado pelo próprio schema da ferramenta.

3. **A ratificação de todo o plano v2 (269 decisões, incluindo thresholds clínicos) foi feita por delegação, não por médico.** `docs/plan/_work/ratification-decisions.yaml:2-3`:
   ```
   authority: 'repository owner delegation (session directive: "use deep think to decide on the
     RATIFICATION items and close PR #3 and BUILD-ADR-001")'
   ```
   O mesmo arquivo (linhas 6-9) documenta explicitamente que a ratificação **não substitui** validação clínica:
   ```
   residual_professional_gates:
   - 'clinical pilot sign-off gates in delivery/roadmap.md remain (SaMD posture: ratification-for-build
     != deployment clearance)'
   ```
   PR #3 (`gh pr view 3`, merged) confirma: *"Produced by an orchestrated multi-agent effort (~200 specialist runs, 5 gated phases)"* — nenhum médico entre os "specialist runs".

**Conclusão:** existem *dois* gates formais de validação clínica definidos na documentação (G1 no handoff do frontend v3, e os "residual_professional_gates" da ratificação do plano v2) — e **nenhum dos dois foi executado por um profissional de saúde real**. Isso é crítico para uma plataforma classificada como SaMD Classe II (RDC 657/2022, citado em `vision.md:397`).

---

## 4. Gaps de especificação

### 4.1 Funcionalidades prometidas em docs, ausentes/incompletas no código atual

Reverificação em 2026-07-12 dos 7 gaps CRITICAL do `audit-results/CONSOLIDATED_FORENSIC_AUDIT.md` (2026-07-09):

| Gap original (forense 07-09) | Estado atual verificado | Evidência |
|---|---|---|
| C1 — Sem consumer CDC para ADT | **Ainda ausente** | `grep -rn "kafka\|MSK" src/` só acha referências em comentários/docstrings (`src/intensicare/services/altb_trigger.py:12,86,273`); `mllp_listener.py` só trata HL7 ORU-R01 (vitais), não ADT |
| C2 — 3 de 5 tabelas ADT faltando | **Corrigido** | `src/intensicare/models/movimentacao.py:111,155,215` define `AdmissionEpisode`, `PatientLocationCurrent`, `DischargeSummary`; migração `35c5eebda2c7` (2026-07-09) | 
| C3 — Storage em memória em 3 domínios | **Parcialmente corrigido** | Prescricao migrado para PostgreSQL (`domain_prescricao.py:16`); **Trilhas ainda em dict** (`trilhas_state.py:95-119`, `_patient_pathway_store`) apesar de existir tabela `patient_pathways` órfã (zero imports em `services/`/`api/`); **Formularios ainda em lista em memória** (`domain_formularios.py:250`: `_submissions: list[dict] = []`) |
| C4 — `encounter_id` faltando em PatientPathway | **Corrigido no schema** | migração `0034_add_encounter_id_to_patient_pathway.py`; população em runtime não verificável dado C3 |
| C5 — Sem hash de definição content-addressed | **Corrigido no schema** | migração `0036_add_definition_hash_to_pathways.py`; cálculo do hash no momento da escrita não verificado |
| C6 — ECS Task Definitions ausentes | **Literalmente ainda ausente, possivelmente obsoleto** | nenhum arquivo ECS encontrado, mas `k8s/base/*.yaml` e `helm/intensicare/` existem — sugere pivô de arquitetura ECS→K8s não refletido no relatório forense original |
| C7 — RBAC binário | **Parcialmente corrigido** | ABAC granular existe (`src/intensicare/auth/abac.py:33-43`, 7 `ClinicalRole`s) mas **só é chamado em `api/v1/admin.py`**; endpoints clínicos (vitals, labs, medicamentos, dashboard) ainda usam `current_user.is_admin` binário (`auth/dependencies.py:96,121`) |

**5 dos 7 CRITICAL do forense anterior seguem total ou parcialmente abertos** — a remediação (`HANDOFF.yaml` raiz, status `WAVE_1_RUNNING`, pendência `t3_cleanup` explícita) está em andamento, não concluída.

### 4.2 Funcionalidades no código sem rastro em documento de spec

- `domain_sepsis.py` — código morto, fiel à spec, mas nunca exposto (ver §2.2) — o inverso do gap típico: aqui a implementação existe e é *melhor* que a spec exposta, mas está desconectada.
- Endpoints implementados sem contrato: roteadores inteiros sem qualquer OpenAPI (ver §4.3) — `admin`, `alerts`, `alert_routing`, `auth` duplicado, `dashboard`, `events`, `health`, `patients` (rotas base), `thresholds`, `vitals`.

### 4.3 Cobertura dos 15 contratos OpenAPI vs. API viva

Comparação `docs/contracts/*.yaml` (15 arquivos, 50 operações) vs. `curl http://localhost:8000/openapi.json` (81 operações, 62 paths) vs. registro de routers em `src/intensicare/main.py:126-154` (28 `include_router`):

| Métrica | Valor |
|---|---|
| Operações definidas nos 15 contratos | 50 |
| Operações vivas na API (openapi.json) | 81 (62 paths) |
| Operações do contrato implementadas | 45/50 (90%) |
| Operações do contrato **não implementadas** (spec-only) | 5: `GET /units/{unit_id}/indicators`; `POST /drug-interactions/check-pair` e `/check`; `GET`+`POST /registry/setores`; `POST /registry/estabelecimentos` |
| Operações vivas **sem contrato** (não documentadas) | ~31/81 (≈38%) — roteadores inteiros: admin, alerts, alert_routing, auth (duplicado, com e sem prefixo `/api/v1`), dashboard, events, health, patients (base), thresholds, vitals |
| Sobreposição contrato ∩ implementação / total vivo | 45/81 ≈ 56% |

**Conclusão:** os contratos cobrem quase tudo que prometem (90%), mas cobrem **menos da metade da API real** — para 38% dos endpoints vivos não existe nenhum contrato formal, incluindo superfícies sensíveis como `auth`, `admin` e `alert_routing`.

### 4.4 Discrepância "9 vs. 12 trilhas" (investigada)

Confirmado: `_work/alerts/pathways/` tem **12 arquivos YAML** hoje. A origem do "9" é rastreável e consistente — **não é um erro isolado do prompt do orquestrador, é uma decisão de escopo documentada em vários artefatos que nunca foi atualizada**:

- `docs/adr/ADR-0031-mvp-pathway-sepsis.md:13,16,21,39` e `ADR-0033-pathway-view-generic-pattern.md:16,82,92` — ambas datadas 2026-07-09 (commit 2606acc, 2026-07-10) — falam em "9 trilhas clínicas atuais", com uma lista nomeada de 9: Sepse, Renal, Respiratório, Ventilação, Equilíbrio, Nutrição, Profilaxia, Sedação, Delirium.
- `docs/audit/handoff-product-designer/HANDOFF.yaml:212` (gate **G2**, critério de aceite final do projeto): *"Todas as 9 trilhas funcionais"*.
- **O mesmo `HANDOFF.yaml`, na milestone M7 (linhas 156-167), diz o oposto**: *"Trilhas Restantes (12)"*, *"12 pathways analisados ✅ (11 fully compatible, 1 needs attention)"*.

Isto é uma **inconsistência interna não resolvida dentro do próprio documento de handoff**: o critério de aceite do gate final (G2) nunca foi atualizado de 9→12 mesmo depois de M7 (executado antes de M8/G2) ter descoberto e processado as 12 trilhas reais. Os 3 pathways ausentes da lista original de "9" são: `antimicrobiano`, `desmame`, `estabilidade`.

---

## 5. Scoring

### 5.1 Tabela de achados (severidade → evidência)

| # | Severidade | Achado | Evidência |
|---|---|---|---|
| 1 | 🔴 CRITICAL | Zero validação clínica real em toda a plataforma, apesar de dois gates formais exigirem médico | `HANDOFF.yaml:200-206` (G1, sem score clínico registrado); `panels/*/decision.yaml:48-51` (`signoffs: []`); `ratification-decisions.yaml:2-9` (ratificado por delegação, gates profissionais residuais nunca fechados) |
| 2 | 🔴 CRITICAL | Trilha de sepse (P1, benchmark do MVP) tem duas implementações paralelas não integradas; a fiel à spec (`domain_sepsis.py`, testada, 31 vetores) é código morto; a que roda de fato (`sepse.yaml`/TrilhasEngine) carece de SIRS, PCT stewardship e timers de bundle SSC-2021 | `src/intensicare/services/domain_sepsis.py` (não importado por nenhum router); `src/intensicare/api/v1/pathways.py` (wired a TrilhasEngine); `_work/alerts/pathways/sepse.yaml` vs. `docs/plan/clinical/domains/sepsis.md` |
| 3 | 🔴 CRITICAL | RBAC ainda binário (`is_admin`) na maioria dos endpoints clínicos; ABAC granular (7 papéis clínicos) só aplicado em `admin.py` | `src/intensicare/auth/abac.py:33-43,89-275`; `src/intensicare/auth/dependencies.py:96,121` |
| 4 | 🔴 CRITICAL | Storage não-persistente (dict em memória) ainda ativo em Trilhas e Formulários — dados clínicos voláteis a reinícios; tabela `patient_pathways` existe mas está órfã | `trilhas_state.py:95-119`; `domain_formularios.py:250,381,416` |
| 5 | 🔴 CRITICAL | Sem consumer de CDC/ADT — tabelas ADT existem mas não são populadas; domínio de movimentação sem pipeline de ingestão viva | `grep -rn "kafka\|MSK" src/` só docstrings; `domain_movimentacao.py:267` |
| 6 | 🟠 MAJOR | Inconsistência interna não resolvida "9 vs. 12 trilhas" no próprio HANDOFF.yaml (M7 diz 12, gate G2 diz 9) — critério de aceite final desatualizado | `HANDOFF.yaml:156-167` vs. `HANDOFF.yaml:212`; `ADR-0031:13,16`; `ADR-0033:16,82` |
| 7 | 🟠 MAJOR | 38% (31/81) dos endpoints vivos da API não têm nenhum contrato OpenAPI — roteadores inteiros (admin, auth, alerts, alert_routing, dashboard, events, health, patients-base, thresholds, vitals) sem spec | comparação `docs/contracts/*.yaml` vs. `openapi.json` ao vivo |
| 8 | 🟠 MAJOR | 5 operações prometidas em contrato nunca implementadas (drug-interactions check x2, units/indicators, registry/setores x2) | `docs/contracts/prescricao-openapi.yaml`, `indicadores-openapi.yaml`, `cadastros-ui-openapi.yaml` vs. `openapi.json` |
| 9 | 🟠 MAJOR | ADRs 0030-0034 (decisão arquitetural central do produto) sem coautoria ou justificativa clínica — autoria exclusiva de arquiteto de sistema; requisito de latência clínica (ADR-0034) afirmado sem fonte | `docs/adr/ADR-0030..0034` (linhas citadas em §3.1) |
| 10 | 🟠 MAJOR | `encounter_id` e `definition_hash` corrigidos só no schema; não verificável em runtime pois o domínio Trilhas ainda roda no store legado em memória | `alembic/versions/0034_*.py`, `0036_*.py` vs. achado #4 |
| 11 | 🟡 MINOR | Gap C6 (ECS Task Definitions) do audit forense está provavelmente obsoleto — repo pivotou para K8s/Helm (`k8s/base/`, `helm/intensicare/`) sem que o relatório anterior fosse atualizado | `find infra infrastructure k8s helm` |
| 12 | 🟡 MINOR | Dados de vitals/scores com >13-16 dias de atraso, limitando a verificabilidade end-to-end via API viva durante esta auditoria | `docs/audit/handoff-parreira/WIRING_GAPS.md:59` |
| 13 | 🟡 MINOR | Protocolo de WebSocket diverge entre frontend (`{type:"auth"}`) e backend (`{action:"subscribe"}`), adiado para M8 | `WIRING_GAPS.md:22,55` |
| 14 | 🟡 MINOR | `docs/audit/FORENSICS_SYNTHESIS.md`, citado em `AUDIT_PROMPT.md`, não existe no repositório | verificação direta — arquivo ausente |
| 15 | 🟡 MINOR | README.md não contém seção de "problema do usuário" — dor do intensivista só é citada em docs/product/, exigindo navegação para achá-la | `README.md` (nenhuma ocorrência de "problema"/"dor") |

**Contagem:** 5 CRITICAL · 5 MAJOR · 5 MINOR = 15 achados.

### 5.2 Score final: **58 / 100**

Justificativa da nota:

- **Pontos fortes reais (não penalizados):** existe um PRD claro desde o commit inicial (`vision.md`); métricas de sucesso são específicas e instrumentadas (12 critérios de persona com evento/telemetria nomeados); há uma matriz de rastreabilidade gerada mecanicamente cobrindo 960 regras legadas; a amostra de sepse mostra que a **camada de documentação** (problema → spec clínica → YAML → contrato) está bem conectada. Isso por si só valeria uma nota alta (~85-90) se o critério fosse só "existe rastro documental".
- **Deduções severas:** a auditoria reduz a nota porque **rastreabilidade não é só existência de documento — é fidelidade ponta a ponta**, e a amostra mais crítica do produto (sepse, P1, benchmark do MVP) mostra que o código que de fato roda diverge da spec ratificada, enquanto o código fiel à spec é morto e não instrumentado no runtime (achado #2, −12 pontos). A ausência total de validação clínica real, apesar de dois gates formais a exigirem (achado #1), é uma falha estrutural para software classificado como SaMD Classe II (−15 pontos). RBAC binário e storage em memória em domínios clínicos, herdados de um audit forense de 3 dias atrás e apenas parcialmente corrigidos, comprometem a confiabilidade dos dados que alimentam a cadeia de rastreabilidade (achados #3-#5, −8 pontos). Gaps de contrato (38% da API sem spec) e a inconsistência interna "9 vs 12" no próprio handoff mostram que a documentação não é mantida em sincronia com o código à medida que este evolui (achados #6-#10, −7 pontos).

| Componente do score | Peso implícito | Nota parcial |
|---|---|---|
| Problema documentado + métricas de sucesso | — | 90/100 |
| Tradução problema→spec técnica (estrutura documental) | — | 85/100 |
| Fidelidade spec→implementação (amostra sepse) | — | 35/100 |
| Decisões arquiteturais com base clínica | — | 30/100 |
| Validação por profissional de saúde | — | 0/100 |
| Cobertura contrato↔API viva | — | 60/100 |
| **Score consolidado ponderado** | | **58/100** |

---

## Apêndice — Fontes consultadas

- `docs/product/vision.md`, `docs/plan/product/product-spec.md`, `docs/plan/traceability-matrix.md`, `docs/plan/README.md`
- `docs/adr/ADR-001-amh-data-platform-consumer.md`, `docs/adr/ADR-0030..0034-*.md`
- `docs/audit/handoff-product-designer/{HANDOFF.yaml,PROMPT.md,RUNBOOK.md,FRONTEND_REBUILD_PLAN.md,PLANS.md,HANDOFF.md}`
- `docs/audit/handoff-parreira/WIRING_GAPS.md`
- `docs/plan/_work/ratification-decisions.yaml`, `docs/plan/_work/panels/**`, `docs/plan/_work/scripts/panel_decide.py`
- `docs/plan/clinical/domains/sepsis.md`, `_work/alerts/pathways/sepse.yaml`, `docs/plan/_work/alerts/sepsis.yaml`
- `docs/contracts/*.yaml` (15 arquivos) vs. `curl http://localhost:8000/openapi.json` (ao vivo)
- `src/intensicare/services/domain_sepsis.py`, `src/intensicare/services/trilhas_state.py`, `src/intensicare/services/trilhas_engine.py`, `src/intensicare/api/v1/pathways.py`, `src/intensicare/auth/abac.py`, `src/intensicare/auth/dependencies.py`, `src/intensicare/models/movimentacao.py`, `src/intensicare/models/pathway.py`
- `frontend-v3/app/patient/[mpi_id]/pathway/[pp_id]/page.tsx`
- `tests/test_domain_sepsis.py`
- `audit-results/CONSOLIDATED_FORENSIC_AUDIT.md`
- `HANDOFF.yaml` (raiz do repo), `alembic/versions/{35c5eebda2c7,0034_*,0035_*,0036_*}.py`
- `git log`, `gh pr view 3` (PR #3, "Ratification: IntensiCare v2 build plan", MERGED)
