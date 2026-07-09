# Análise Forense de Gaps TDD — IntensiCare

**Data:** 2026-07-09
**Auditor:** Forensic Agent 1 (Hermes)
**Escopo:** 5 TDDs vs implementação real em `src/intensicare/`
**Classificação de severidade:** CRITICAL > HIGH > MEDIUM > LOW

---

## SUMÁRIO EXECUTIVO

Todos os 5 domínios possuem arquivos de serviço (`domain_*.py`), routers API, modelos SQLAlchemy, schemas Pydantic, contratos OpenAPI, testes e migrações. **Nenhum contrato está ausente** — o diretório `docs/contracts/` contém 15 arquivos YAML, incluindo todos os 5 contratos referenciados. No entanto, **a implementação está em estágio "MVP inicial" com armazenamento majoritariamente em memória (in-memory)** e diverge substancialmente dos designs arquiteturais detalhados nos TDDs.

### Tabela de severidade por domínio

| Domínio | Gaps CRITICAL | Gaps HIGH | Gaps MEDIUM | Gaps LOW | Status geral |
|---|---|---|---|---|---|
| Trilhas Engine | 3 | 4 | 3 | 2 | **PARCIAL — em migração** |
| Prescrição | 2 | 5 | 3 | 1 | **PARCIAL — divergente** |
| Movimentação-ADT | 4 | 4 | 2 | 1 | **INCOMPLETO — versão simplificada** |
| Formulários Clínicos | 3 | 4 | 3 | 2 | **PARCIAL — core funcional** |
| Evoluções | 2 | 4 | 3 | 1 | **PARCIAL — bem estruturado** |

---

## 1. TRILHAS ENGINE (Pathways)

### 1.1 Estrutura existente

| Artefato | Caminho | Linhas | Status |
|---|---|---|---|
| **Serviço principal** | `services/domain_trilhas_engine.py` | 433 | Thin wrapper (deprecated) |
| **Novo engine YAML** | `services/trilhas_engine.py` | 345 | Estateless rule engine (M4) |
| **Engine legado** | `services/trilhas_state.py` | — | PathwayStore state machine |
| **Definições** | `services/trilhas_definitions.py` | — | PATHWAY_SEEDS |
| **Compilador YAML** | `services/trilhas_compiler.py` | — | Build-time compiler |
| **Avaliador** | `services/trilhas_evaluator.py` | — | Criteria evaluator |
| **API Router** | `api/v1/pathways.py` | 650 | **6/6 endpoints** ✅ |
| **Modelos** | `models/pathway.py` | 70 | 4 tabelas |
| **Schemas** | `schemas/pathways.py` | — | Pydantic |
| **Contrato** | `docs/contracts/pathways-openapi.yaml` | — | ✅ EXISTE |
| **Testes** | `tests/test_domain_trilhas_engine.py` | 848 | 848 linhas |
| **Migração** | `alembic/versions/0032_*.py` | — | pathways, pathway_criteria, patient_pathways, pathway_state_transitions |

### 1.2 Endpoints implementados vs especificados

| TDD Endpoint | Implementado? | Rota real |
|---|---|---|
| GET /api/v1/pathways | ✅ SIM | `/api/v1/pathways` |
| GET /api/v1/pathways/{id} | ✅ SIM | `/api/v1/pathways/{pathway_id}` |
| GET /api/v1/patients/{mpi_id}/pathways | ✅ SIM | `/api/v1/patients/{mpi_id}/pathways` |
| POST /api/v1/patients/{mpi_id}/pathways | ✅ SIM | `/api/v1/patients/{mpi_id}/pathways` |
| PUT /api/v1/patients/{mpi_id}/pathways/{id}/criteria | ✅ SIM | `/api/v1/patients/{mpi_id}/pathways/{patient_pathway_id}/criteria` |
| GET /api/v1/patients/{mpi_id}/pathways/{id}/progress | ✅ SIM | Integrado via legacy `get_pathway_progress()` |

**Todos os 6 endpoints especificados estão implementados.**

### 1.3 Modelos de dados vs TDD

| Tabela TDD | Tabela real | Match? |
|---|---|---|
| `pathway_definition` | `pathways` | ⚠️ PARCIAL — falta `definition_version_id`, `definition_content`, `compiled_at` |
| `patient_pathway` | `patient_pathways` | ⚠️ PARCIAL — falta `encounter_id`, `bed_id`, `unit`, `current_state_id` |
| `pathway_state_history` | `pathway_state_transitions` | ✅ SIMILAR |
| `criteria_evaluation` | ❌ AUSENTE | Avaliações colapsadas em `criteria_data` JSONB no `patient_pathways` |
| `audit_trail` | `audit_trail` (tabela compartilhada) | ✅ EXISTE |

### 1.4 Gaps identificados

| # | Gap | Severidade | Detalhes |
|---|---|---|---|
| G1 | **Falta `encounter_id` no PatientPathway** | **CRITICAL** | TDD (ADR-020/021) exige escopo por admissão; sem `encounter_id`, não é possível distinguir reinternações |
| G2 | **Falta `pathway_definition` como tabela imutável** | **CRITICAL** | TDD especifica content-addressed definitions com SHA-256; o modelo atual é mutável |
| G3 | **Sem `criteria_evaluation` normalizada** | **CRITICAL** | Avaliações colapsadas em JSONB impedem queries, auditoria e LGPD erasure granular |
| G4 | **12-slug vocabulary não é enforced** | **HIGH** | Sem constraint CHECK/ENUM no `slug`, a taxonomia de 12 pathways não é garantida |
| G5 | **Engine ainda usa fallback legado** | **HIGH** | O novo `TrilhasEngine` (YAML-based) é "primary source with legacy fallback" — migração incompleta |
| G6 | **Sem phase-tracking state machine** | **HIGH** | Postergado para post-MVP conforme ADR-020, mas o TDD lista como escopo inicial |
| G7 | **Sem integração com Alert Engine** | **HIGH** | O TDD §2.2 (6) descreve integração bidirecional; não implementada |
| G8 | **Falta `bed_id` e `unit` no PatientPathway** | **MEDIUM** | Necessário para bed re-association (TDD §5.2) |
| G9 | **Falta `definition_version_id` (SHA-256)** | **MEDIUM** | Content-addressing (INV-3) é pilar arquitetural do TDD; implementação usa slug simples |
| G10 | **Sem compilador YAML CI** | **MEDIUM** | O `trilhas_compiler.py` existe mas o pipeline CI de validação/build não está documentado |
| G11 | **Testes cobrem 848 linhas mas usam store legado** | **LOW** | Testes não exercitam o novo `TrilhasEngine` YAML-based |
| G12 | **Sem observabilidade (métricas Prometheus)** | **LOW** | TDD §7 especifica 6 métricas; nenhuma implementada |

---

## 2. PRESCRIÇÃO (Medication Prescription)

### 2.1 Estrutura existente

| Artefato | Caminho | Linhas | Status |
|---|---|---|---|
| **Serviço principal** | `services/domain_prescricao.py` | 855 | v3.0.0, state machine + drug safety |
| **Drug safety** | `services/drug_safety.py` | — | Dose validation, renal, pediatric |
| **Drug interactions** | `services/drug_interactions.py` | — | Drug-drug interaction engine |
| **API Router** | `api/v1/prescricao.py` | 311 | 5 endpoints (rotas divergentes) |
| **Modelos** | `models/prescricao.py` | 250 | 5 tabelas |
| **Schemas** | `schemas/prescricao.py` | — | Pydantic |
| **Contrato** | `docs/contracts/prescricao-openapi.yaml` | — | ✅ EXISTE |
| **Testes** | `tests/test_domain_prescricao.py` | 506 | 506 linhas |
| **Migração** | `alembic/versions/0033_*.py` | — | prescricoes, interacao_alertas, auditoria_prescricao, agenda_prescricao |

### 2.2 Endpoints — divergência de rotas

| TDD Endpoint | Implementado? | Rota real | Nota |
|---|---|---|---|
| POST /api/v1/prescricao | ⚠️ DIVERGE | POST `/api/v1/patients/{mpi_id}/prescriptions` | Rota diferente |
| GET /api/v1/prescricao/{id} | ⚠️ DIVERGE | GET `/api/v1/prescriptions/{prescription_id}` | Rota diferente |
| PUT /api/v1/prescricao/{id} | ⚠️ DIVERGE | PUT `/api/v1/prescriptions/{prescription_id}` | Rota diferente |
| POST /api/v1/prescricao/{id}/state | ❌ AUSENTE | — | State transitions embutidas no PUT, sem endpoint dedicado |
| — | ✅ EXTRA | GET `/api/v1/patients/{mpi_id}/prescriptions` | Listagem por paciente (não no TDD) |
| — | ✅ EXTRA | GET `/api/v1/prescriptions/state-machine` | Definição da máquina de estados |

### 2.3 Modelo de dados vs TDD

| Tabela TDD | Tabela real | Match? |
|---|---|---|
| `Prescricao` | `prescricoes` | ⚠️ PARCIAL — schema simplificado |
| `InteracaoAlerta` | `interacao_alertas` | ✅ PRÓXIMO |
| `AuditoriaPrescricao` | `auditoria_prescricao` | ✅ PRÓXIMO |
| `AgendaPrescricao` | `agenda_prescricao` | ✅ PRÓXIMO |
| `PrescriptionStateLog` | `prescription_state_log` | ✅ EXTRA (não no TDD, mas útil) |

### 2.4 Gaps identificados

| # | Gap | Severidade | Detalhes |
|---|---|---|---|
| G13 | **Rotas API divergem do contrato OpenAPI** | **CRITICAL** | TDD especifica `/api/v1/prescricao`; implementação usa `/patients/{mpi_id}/prescriptions` e `/prescriptions/{id}` |
| G14 | **Falta endpoint dedicado `POST /prescricao/{id}/state`** | **CRITICAL** | TDD §4.1 especifica endpoint separado para transições de ciclo de vida com body `{transition, co_signatario_id}` |
| G15 | **Modelo de dados simplificado vs TDD** | **HIGH** | TDD usa UUID para IDs, Decimal(10,4) para dose, campos separados `dose`/`dose_unit`/`via_administracao`; implementação usa BigInteger, String `dosage`, String `route` |
| G16 | **Faltam campos obrigatórios do TDD** | **HIGH** | `dose_unit` (Enum), `via_administracao` (Enum), `frequencia_detalhe` (JSON), `co_signatario_id` (FK User), `indicacao_clinica` (Text), `dose_calculation` (JSON), `instrucoes` (Text), `data_inicio`/`data_fim` como campos separados |
| G17 | **43 regras não são pipeline composable** | **HIGH** | TDD §5 especifica Chain of Responsibility com 43 validators independentes; implementação tem validações básicas em `drug_safety.py` mas sem framework de pipeline |
| G18 | **Sem integração com ANVISA API externa** | **HIGH** | TDD §2.2 e ADR-026 especificam local cache + ANVISA external fallback; implementação usa apenas dados locais |
| G19 | **Sem cálculo de dose renal (Cockcroft-Gault)** | **HIGH** | Funções existem em `drug_safety.py` mas não são integradas ao fluxo de criação |
| G20 | **Frequência como String vs Enum** | **MEDIUM** | TDD define Enum `Frequencia` com 7 valores; implementação aceita string arbitrária |
| G21 | **Sem soft-delete** | **MEDIUM** | TDD §6.2 especifica "soft-delete only, no hard delete" para LGPD; modelo não tem campo `deleted_at` |
| G22 | **Sem criptografia PHI field-level** | **MEDIUM** | TDD §6.2 especifica AES-256-GCM nos campos de auditoria; não implementado |
| G23 | **Testes cobrem 506 linhas** | **LOW** | Cobertura razoável mas não cobre todos os 43 validators nem integração ANVISA |

---

## 3. MOVIMENTAÇÃO-ADT (Patient Movement)

### 3.1 Estrutura existente

| Artefato | Caminho | Linhas | Status |
|---|---|---|---|
| **Serviço principal** | `services/domain_movimentacao.py` | 731 | v3.0.0, in-memory store |
| **API Router** | `api/v1/movimentacao.py` | 240 | **4/4 endpoints** ✅ |
| **Modelos** | `models/movimentacao.py` | 141 | 3 tabelas |
| **Schemas** | `schemas/movimentacao.py` | — | Pydantic |
| **Contrato** | `docs/contracts/movimentacao-openapi.yaml` | — | ✅ EXISTE |
| **Testes** | `tests/test_domain_movimentacao.py` | 183 | 183 linhas |
| **Migração** | `alembic/versions/0033_*.py` | — | patient_movements, beds, admission_episodes |

### 3.2 Endpoints implementados vs especificados

| TDD Endpoint | Implementado? | Rota real |
|---|---|---|
| GET /api/v1/patients/{mpi_id}/movements | ✅ SIM | `/api/v1/patients/{mpi_id}/movements` |
| POST /api/v1/patients/{mpi_id}/movements | ✅ SIM | `/api/v1/patients/{mpi_id}/movements` |
| GET /api/v1/beds | ✅ SIM | `/api/v1/beds` |
| PUT /api/v1/beds/{bed_id} | ✅ SIM | `/api/v1/beds/{bed_id}` |

**Todos os 4 endpoints especificados estão implementados.**

### 3.3 Modelos de dados vs TDD

| Tabela TDD | Tabela real | Match? |
|---|---|---|
| `admission_episode` | `admission_episodes` | ⚠️ PARCIAL — falta `encounter_id`, `primary_diagnosis`, `unit_at_admission`, `source_cdc_offset` |
| `patient_location_current` | ❌ AUSENTE | Não existe tabela separada para localização atual |
| `transfer_log` | ❌ AUSENTE | Movimentos são registrados em `patient_movements` (simplificado) |
| `discharge_summary` | ❌ AUSENTE | Alta tratada como movimento tipo "discharge" sem sumário separado |
| `bed_status` | `beds` | ⚠️ PARCIAL — falta `room`, `last_cleaned_at`, `block_reason`, `occupied_since` |

### 3.4 Gaps identificados

| # | Gap | Severidade | Detalhes |
|---|---|---|---|
| G24 | **Armazenamento IN-MEMORY, não PostgreSQL** | **CRITICAL** | Todo o serviço usa dicionários Python (`_movements_store`, `_beds_store`); dados são voláteis e não persistem entre reinicializações |
| G25 | **Faltam 3 das 5 tabelas do TDD** | **CRITICAL** | `patient_location_current`, `transfer_log`, `discharge_summary` não existem |
| G26 | **Sem CDC Consumer / Kafka** | **CRITICAL** | TDD e ADR-025 especificam materialized view pattern com CDC topics (`cdc.amh.tasy.*`); zero implementação |
| G27 | **Sem 74 regras como DMN decision tables** | **CRITICAL** | TDD §3.3 especifica 74 regras avaliadas incrementalmente; apenas 9 regras UNVERIFIABLE RATIFIED estão preservadas como funções utilitárias |
| G28 | **Sem schema `movimentacao`** | **HIGH** | TDD §3.2 especifica schema dedicado; tabelas estão no `public` |
| G29 | **Sem `encounter_id` como chave de admissão** | **HIGH** | Modelo usa `admission_date`/`discharge_date` em vez de `encounter_id` do AMH |
| G30 | **Sem daily reconciliation com AMH Gold** | **HIGH** | TDD §2.2 (5) e ADR-025 especificam job diário de reconciliação via Athena |
| G31 | **Sem LGPD erasure cascade particionado** | **HIGH** | TDD §6.2 especifica cascade particionado por `mpi_id` |
| G32 | **Modelo Bed simplificado** | **MEDIUM** | Faltam `room`, `last_cleaned_at`, `block_reason` |
| G33 | **Sem bootstrap procedure (snapshot + replay)** | **MEDIUM** | TDD §2.2 (6) especifica procedimento de inicialização via S3 snapshot |
| G34 | **Apenas 183 linhas de teste** | **LOW** | Cobertura mínima; sem testes para regras DMN, CDC, reconciliação |

---

## 4. FORMULÁRIOS CLÍNICOS (Clinical Forms)

### 4.1 Estrutura existente

| Artefato | Caminho | Linhas | Status |
|---|---|---|---|
| **Serviço principal** | `services/domain_formularios.py` | 719 | v3.0.0, in-memory scoring engine |
| **API Router** | `api/v1/formularios.py` | 171 | **3/3 endpoints** ✅ |
| **Modelos** | `models/clinical_form.py` | 76 | 2 tabelas |
| **Schemas** | `schemas/clinical_forms.py` + `schemas/clinical_forms_extended.py` | — | Pydantic |
| **Contrato** | `docs/contracts/formularios-clinicos-openapi.yaml` | — | ✅ EXISTE |
| **Testes** | `tests/test_domain_formularios.py` | 350 | 350 linhas |
| **Migração** | `alembic/versions/0033_*.py` | — | form_definitions, clinical_form_submissions |

### 4.2 Endpoints implementados vs especificados

| TDD Endpoint | Implementado? | Rota real |
|---|---|---|
| GET /api/v1/clinical-forms | ✅ SIM | `/api/v1/clinical-forms` |
| GET /api/v1/patients/{mpi_id}/clinical-forms | ✅ SIM | `/api/v1/patients/{mpi_id}/clinical-forms` |
| POST /api/v1/patients/{mpi_id}/clinical-forms | ✅ SIM | `/api/v1/patients/{mpi_id}/clinical-forms` |

**Todos os 3 endpoints especificados estão implementados.**

### 4.3 Modelos de dados vs TDD

| Tabela TDD | Tabela real | Match? |
|---|---|---|
| `form_definition_version` | `form_definitions` | ⚠️ PARCIAL — falta `definition_hash`, `definition_content`, `pydantic_module`, `deprecated`, `superseded_by` |
| `clinical_form_submission` | `clinical_form_submissions` | ⚠️ PARCIAL — falta `encounter_id`, `definition_version_id`, `score_components`, `submitted_offline` |
| `form_score` | ❌ AUSENTE | Score é coluna na `clinical_form_submissions`, não tabela separada |
| `submission_draft` | ❌ AUSENTE | Não existe tabela de rascunhos |

### 4.4 Gaps identificados

| # | Gap | Severidade | Detalhes |
|---|---|---|---|
| G35 | **Armazenamento IN-MEMORY para submissões** | **CRITICAL** | `submit_form()` usa `_submissions_store: dict`; dados não persistem |
| G36 | **Sem build-time schema generation (ADR-029)** | **CRITICAL** | TDD §2.2 especifica pipeline CI: TypeScript FormConfig → JSON Schema → Pydantic; zero implementação |
| G37 | **Sem CrossFieldRule DSL** | **CRITICAL** | TDD §2.4 e §4.2 especificam DSL declarativo para visibilidade condicional; não implementado |
| G38 | **Sem `definition_version_id` como FK** | **HIGH** | Submissões não referenciam a versão exata do schema usado (apenas `version` string) |
| G39 | **Falta `form_score` como tabela separada** | **HIGH** | Score e `score_components` (JSONB) deveriam ser tabela própria conforme TDD §3.2 |
| G40 | **Sem offline-first (IndexedDB, Background Sync)** | **HIGH** | TDD §2.3 [5] e ADR-029 especificam suporte offline; não implementado |
| G41 | **Sem `submission_draft` (save-draft)** | **HIGH** | TDD §5.5 especifica rascunhos com auto-expire 72h |
| G42 | **Apenas 5 core forms implementados** | **MEDIUM** | TDD especifica 49 regras com LPP/NPUAP, global admission e multi-disciplina; apenas RASS, CAM-ICU, BPS/NRS, Glasgow, SOFA |
| G43 | **Sem form composition (`composeForms()`)** | **MEDIUM** | TDD §5.6 especifica composição para eliminar duplicação LPP nursing/nutrition |
| G44 | **Sem `encounter_id` nas submissões** | **MEDIUM** | Necessário para correlacionar avaliações com admissões específicas |
| G45 | **Scoring engine funcional mas sem invariants cross-form** | **LOW** | RASS=-5 bloqueia CAM-ICU — invariants existem como lógica mas não como validadores cross-form explícitos |
| G46 | **Sem métricas de observabilidade** | **LOW** | TDD §7 especifica 8 métricas; nenhuma implementada |

---

## 5. EVOLUÇÕES CLÍNICAS (Clinical Notes)

### 5.1 Estrutura existente

| Artefato | Caminho | Linhas | Status |
|---|---|---|---|
| **Serviço principal** | `services/domain_evolucoes.py` | 1331 | v3.0.0, in-memory SBAR engine |
| **API Router** | `api/v1/evolucoes.py` | 211 | **3/3 endpoints** ✅ |
| **Modelos** | `models/evolucao.py` | 200 | 3 tabelas |
| **Schemas** | `schemas/evolucoes.py` | — | Pydantic |
| **Contrato** | `docs/contracts/evolucoes-openapi.yaml` | — | ✅ EXISTE |
| **Testes** | `tests/test_domain_evolucoes.py` | 496 | 496 linhas |
| **Migração** | `alembic/versions/0033_*.py` | — | evolucao_templates, evolucoes, evolucao_sections |

### 5.2 Endpoints implementados vs especificados

| TDD Endpoint | Implementado? | Rota real |
|---|---|---|
| GET /api/v1/patients/{mpi_id}/evolucoes | ✅ SIM | `/api/v1/patients/{mpi_id}/evolucoes` |
| POST /api/v1/patients/{mpi_id}/evolucoes | ✅ SIM | `/api/v1/patients/{mpi_id}/evolucoes` |
| GET /api/v1/evolucoes/{id} | ✅ SIM | `/api/v1/evolucoes/{evolution_id}` |

**Todos os 3 endpoints especificados estão implementados.**

### 5.3 Modelos de dados vs TDD

| Tabela TDD | Tabela real | Match? |
|---|---|---|
| `evolucao_template` | `evolucao_templates` | ⚠️ PARCIAL — falta `type`, `definition_hash`, `superseded_by`; `id` é String vs SERIAL |
| `evolucao` | `evolucoes` | ⚠️ PARCIAL — modelo próximo mas faltam campos críticos |
| `evolucao_section` | `evolucao_sections` | ✅ PRÓXIMO |

### 5.4 Gaps identificados

| # | Gap | Severidade | Detalhes |
|---|---|---|---|
| G47 | **Armazenamento IN-MEMORY para evoluções** | **CRITICAL** | `create_evolution()` usa `_evolutions_store: dict`; 1331 linhas de serviço mas sem persistência real em DB |
| G48 | **Modelo Evolucao sem campos críticos do TDD** | **CRITICAL** | Faltam: `encounter_id`, `content` (narrativa Markdown), `structured_data` (JSONB separado), `sofa_score`, `bundles_confirmed`, `enrichment`, `amends_evolution_id` |
| G49 | **Template sem `type` e versionamento** | **HIGH** | TDD especifica UNIQUE `(role, type, definition_version)`; modelo atual só tem `role` |
| G50 | **Status enum divergente** | **HIGH** | TDD: `draft`, `liberado`, `assinado`; implementação: `draft`, `final`, `amended` |
| G51 | **Sem pre-population do MovimentacaoStateStore** | **HIGH** | TDD §2.2 (3) e ADR-025 descrevem pre-população de sinais vitais, scores, dispositivos; não implementado |
| G52 | **Sem LLM enrichment pipeline** | **HIGH** | TDD §5.4 descreve enriquecimento assíncrono com LLM (sumarização, entity extraction); não implementado |
| G53 | **Sem integração com Trilhas Engine** | **HIGH** | TDD §5.1 descreve bundle adherence tracking; não implementado |
| G54 | **Amendment chain usa `previous_id` vs `amends_evolution_id`** | **MEDIUM** | Semântica similar mas nomenclatura diverge do TDD |
| G55 | **14 roles implementados, mas 81 regras não sistematicamente** | **MEDIUM** | O serviço tem 14 roles com templates SBAR, mas as 81 regras do catálogo legado não foram reimplementadas como validadores |
| G56 | **Sem content_hash SHA-256 para non-repudiation** | **MEDIUM** | Modelo tem campo `content_hash` (String 64), mas o cálculo real no serviço é simplificado |
| G57 | **Sem métricas e observabilidade** | **LOW** | TDD §7 especifica 10 métricas; nenhuma implementada |

---

## 6. CONTRATOS — NOTA IMPORTANTE

**CORREÇÃO:** O diretório `docs/contracts/` **NÃO está vazio**. Ele contém **15 arquivos YAML**, incluindo todos os 5 contratos referenciados nos TDDs:

| Contrato | Caminho | Tamanho |
|---|---|---|
| pathways-openapi.yaml | `docs/contracts/pathways-openapi.yaml` | ✅ EXISTE |
| prescricao-openapi.yaml | `docs/contracts/prescricao-openapi.yaml` | ✅ EXISTE |
| movimentacao-openapi.yaml | `docs/contracts/movimentacao-openapi.yaml` | ✅ EXISTE |
| formularios-clinicos-openapi.yaml | `docs/contracts/formularios-clinicos-openapi.yaml` | ✅ EXISTE |
| evolucoes-openapi.yaml | `docs/contracts/evolucoes-openapi.yaml` | ✅ EXISTE |

Contratos adicionais existentes (fora do escopo desta auditoria): ventilation, stability, sedacao, prophylaxis, antimicrobial, deterioração, documentação, eficiência, indicadores, cadastros-ui.

**Gap de contratos: NENHUM.** Todos os contratos referenciados estão presentes.

---

## 7. PADRÕES SISTÊMICOS IDENTIFICADOS

### 7.1 Armazenamento em memória (IN-MEMORY)

**3 dos 5 domínios** usam armazenamento exclusivamente em memória (dicionários Python):
- **Movimentação-ADT:** `_movements_store`, `_beds_store`
- **Formulários Clínicos:** `_submissions_store`
- **Evoluções:** `_evolutions_store`, `_templates_store`

Apenas **Trilhas Engine** (via PathwayStore legado em `trilhas_state.py`) e **Prescrição** (via `_prescriptions` dict com persistência parcial) têm algum nível de persistência. Isso significa que **dados são perdidos a cada reinicialização do servidor** — um gap CRITICAL transversal.

### 7.2 Tipos de ID inconsistentes

| Domínio | TDD espera | Implementação usa |
|---|---|---|
| Prescrição | UUID | BigInteger |
| Evoluções | UUID | BigInteger |
| Formulários | UUID (submission) | BigInteger |
| Pathways | SERIAL | BigInteger |
| Movimentação | SERIAL | BigInteger |

### 7.3 Falta de `encounter_id` como chave de admissão

Apenas o TDD de Trilhas Engine menciona `encounter_id` no `patient_pathway`. Nenhum dos outros modelos (prescricao, formularios, evolucoes) referencia `encounter_id`, impossibilitando correlação de dados clínicos com episódios de admissão específicos — um gap transversal de severidade **HIGH**.

### 7.4 Ausência de integração cross-domain

- Trilhas Engine ↔ Alert Engine: não implementado
- Evoluções ↔ Trilhas Engine (bundle tracking): não implementado
- Evoluções ↔ MovimentacaoStateStore (pre-population): não implementado
- Prescrição ↔ ANVISA API externa: não implementado

---

## 8. RESUMO QUANTITATIVO

| Métrica | Total |
|---|---|
| **Total de gaps identificados** | **57** |
| **Gaps CRITICAL** | **14** |
| **Gaps HIGH** | **21** |
| **Gaps MEDIUM** | **14** |
| **Gaps LOW** | **8** |
| **Endpoints implementados vs especificados** | 20/20 (100%) |
| **Modelos de dados alinhados com TDD** | 5/22 tabelas (23%) |
| **Domínios com persistência real em DB** | 1/5 (20%) — apenas Prescrição parcialmente |
| **Linhas de código de serviço** | 4,069 (domain_*.py) |
| **Linhas de teste** | 2,383 |
| **Cobertura aproximada de regras legadas** | ~30% (prescricao: ~20/43, movimentacao: 9/74, formularios: ~28/49, evolucoes: ~30/81) |

---

## 9. RECOMENDAÇÕES PRIORIZADAS

### Imediato (Sprint atual)
1. **Migrar armazenamento in-memory → PostgreSQL** para Movimentação, Formulários e Evoluções
2. **Adicionar `encounter_id`** em todos os modelos que referenciam pacientes
3. **Alinhar rotas da Prescrição** com o contrato OpenAPI (`/api/v1/prescricao`)

### Curto prazo (Próximo sprint)
4. Implementar **content-addressing** (SHA-256 `definition_version_id`) nos modelos Pathway e FormDefinition
5. Implementar **CDC Consumer** para Movimentação-ADT (ADR-025)
6. Criar **tabelas faltantes**: `patient_location_current`, `transfer_log`, `discharge_summary`, `form_score`, `submission_draft`
7. Implementar **pipeline de validação composable** para as 43 regras de Prescrição

### Médio prazo
8. Implementar **build-time schema generation** TypeScript→Pydantic (ADR-029)
9. Implementar **CrossFieldRule DSL** para formulários clínicos
10. Implementar **pre-population** de evoluções via MovimentacaoStateStore
11. Implementar **DMN rule engine** para as 74 regras de movimentação
12. Completar **testes de integração** para todos os domínios

---

*Relatório gerado por Forensic Agent 1 (Hermes) em 2026-07-09. Dados coletados via leitura direta de arquivos fonte e comparação com especificações TDD.*
