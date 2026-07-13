# Dimensão E — Inovação e Estado da Arte em CDS de UTI

**Auditor:** Claude (Fable 5), agente especialista em produto clínico/CDS — auditoria somente leitura
**Data:** 2026-07-12
**Escopo:** `/Users/familia/intensicare/` (12 trilhas YAML, motor de regras, ADR-0030..0034, frontend-v3) comparado ao estado da arte comercial e acadêmico em CDS de UTI
**Método:** leitura direta de código/YAML/docs (via sub-agente de pesquisa dedicado, `file:line` verificado) + 6 buscas web sobre concorrentes (Epic Deterioration Index, Philips IntelliVue Guardian/eICU, Etiometry, CLEW Medical) e padrões técnicos (Arden Syntax, CQL, CDS Hooks) + regulação (FDA AI/ML SaMD, CDS exemption)

---

## Sumário executivo

O IntensiCare é uma plataforma de **trilhas clínicas declarativas multi-domínio** (12 YAMLs) avaliadas por um motor de regras determinístico e renderizadas por um único componente de frontend genérico (ADR-0033). Isso é uma arquitetura de produto **genuinamente diferente** da maioria dos concorrentes de CDS de UTI pesquisados, que giram em torno de um **único índice/score de deterioração** (Epic Deterioration Index, MEWS/NEWS2 do Philips IntelliVue Guardian) ou um punhado de índices fisiológicos FDA-cleared isolados (Etiometry IDO2/IVCO2, CLEW hemodynamic-instability model) — nenhum deles organiza terapia intensiva como um conjunto de *pathways* de guideline completos (sepse, renal, ventilação, desmame, delirium, sedação, nutrição, antimicrobiano, eletrólitos, estabilidade hemodinâmica, profilaxia) sob uma única state-machine genérica.

Essa diferenciação, porém, tem contrapartidas reais: (1) nenhuma trilha tem tempo-de-ação estruturado e acionável — só texto livre; (2) o motor de regras é um DSL proprietário, não um padrão interoperável (Arden/CQL); (3) o produto é **puramente reativo** — zero capacidade preditiva/lead-time, o que o coloca estruturalmente atrás de concorrentes com AUC/lead-time publicados (CLEW: 8h de antecedência; Epic EDI: mediana de 24h); (4) a trilha-bandeira do produto (sepse, escolhida como MVP em ADR-0031) tem uma implementação-espelho mais completa (`domain_sepsis.py`, com SIRS/PCT/timers de bundle) que é **código morto** — o que a API realmente serve é a versão mais pobre (achado cruzado com Dimensão A, `docs/audit/fullspectrum/DIM_A_TRACEABILITY.md:56-61`); (5) há inconsistência documental sobre quantos domínios o produto cobre (27, 9, 12 e 7 aparecem em documentos diferentes, não reconciliados).

**Nota: 58/100.** Diferencial genuíno de arquitetura de produto, mas com déficit real de capacidade preditiva/analítica frente ao estado da arte comercial, e lacunas de rigor (tempo-de-ação não estruturado, contagens de domínio não reconciliadas, trilha-bandeira com implementação dupla).

---

## 1. Diferenciador arquitetural

### 1.1 Pathway-centric vs single risk score

A maioria dos sistemas de CDS de UTI pesquisados converge para um **score único agregado**:

- **Epic Deterioration Index (EDI)**: modelo proprietário de regressão/ML que combina ~30 mil pontos de dado do prontuário Epic em um único índice numérico de risco de deterioração/sepse; em validação no Cedars-Sinai, threshold de 68,8 associado a 87% de probabilidade de deterioração, sensibilidade 39%, lead time mediano de 24h ([IntechOpen](https://www.intechopen.com/chapters/87019)).
- **Philips IntelliVue Guardian**: calcula um Early Warning Score (EWS/MEWS/PEWS) único e configurável a partir de sinais vitais automatizados, com foco em detectar deterioração em enfermaria geral/emergência antes da transferência para UTI ([Philips](https://www.usa.philips.com/healthcare/product/HCNOCTN60)).
- **Etiometry**: agrega dados fisiológicos contínuos em um dashboard, mas sua inovação certificada pela FDA são **índices fisiológicos pontuais** (IDO2 — inadequate oxygen delivery; IVCO2 — inadequate CO2 ventilation), não trilhas de guideline completas ([Etiometry](https://www.etiometry.com/resources/how-clinical-intelligence-software-supports-icu-decision-making/)).
- **CLEW Medical (CLEWICU)**: primeiro dispositivo FDA-cleared para prever probabilidade de deterioração hemodinâmica até 8h de antecedência — também um **modelo único** de instabilidade, não um conjunto de trilhas de domínio ([PR Newswire](https://www.prnewswire.com/news-releases/clew-medical-receives-fda-clearance-for-ai-based-predictive-analytics-technology-to-support-adult-icu-patient-assessment-301221173.html)).

O IntensiCare não compete nesse eixo (score único de deterioração geral) — não tem nenhum score agregado equivalente ao NEWS2/MEWS/EDI. Em vez disso, decompõe a UTI em **12 trilhas de domínio independentes**, cada uma com seus próprios critérios graduados/booleanos, bandas de severidade e estados (`_work/alerts/pathways/*.yaml`, schema em `_work/alerts/schema/pathway.schema.json`). Isso é estruturalmente mais próximo de como um bundle de guidelines funciona na prática clínica (SSC-2021 para sepse, KDIGO para renal, PADIS para sedação/delirium) do que de um índice único.

**O que nenhum concorrente pesquisado faz**: renderizar **qualquer uma dessas trilhas** através de **um único componente de frontend genérico** dirigido inteiramente por dados (`frontend-v3/app/patient/[mpi_id]/pathway/[pp_id]/page.tsx` + `frontend-v3/components/pathway/*`). A ADR-0033 (`docs/adr/ADR-0033-pathway-view-generic-pattern.md:68`) declara explicitamente: *"O componente NUNCA recebe props específicas da trilha"* — rejeitando deliberadamente tanto componentes por trilha (`SepsisPathwayView`, `RenalPathwayView` — chamado de "repete o erro do v2", linha 13) quanto uma variante de "slots" de configuração por ser overengineering. Uma busca por nomes de trilha (`sepse|sepsis|renal|ventilacao`) dentro de `frontend-v3/app` e `frontend-v3/components` retorna **zero ocorrências** — toda trilha nova, em tese, é "zero código frontend" (`ADR-0033:92-93`). Os produtos comerciais pesquisados (Epic, Philips, Etiometry, CLEW) não publicam nenhuma arquitetura equivalente — eles têm, quando muito, um dashboard configurável por variável (EWS), não uma engine que renderiza N trilhas de guideline completas genericamente. **Isto é o diferencial genuíno mais defensável do produto.**

### 1.2 YAML declarativo → motor: inovação ou prática comum?

**Prática comum, com uma implementação específica cuidadosa.** Sistemas de regras declarativas para CDS existem desde 1989 (Arden Syntax, mantido pela HL7) e evoluíram para CQL (Clinical Quality Language) e CDS Hooks como padrões modernos e interoperáveis — ambos desenhados especificamente para representar lógica de guideline de forma executável e portátil entre EHRs ([PMC comparação Arden vs CQL](https://pmc.ncbi.nlm.nih.gov/articles/PMC8245210/); [PMC padrões FHIR/CDS](https://pmc.ncbi.nlm.nih.gov/articles/PMC8324242/)). Motores de regras genéricos (Drools, JSONLogic) e frameworks como PROforma seguem a mesma filosofia "declare a regra, o motor avalia."

O motor do IntensiCare (`src/intensicare/services/trilhas_compiler.py:1-3`, `trilhas_evaluator.py`) é um **AST interpreter proprietário e não Turing-completo**, com 4 tipos de nó (`threshold`, `graded`, `boolean`, `composite`), justificado por segurança (*"NO eval()/exec(). Uses Python operator module + safe dict lookup"*, `trilhas_compiler.py:1-3`) — decisão documentada em `docs/adr/0020-trilhas-engine-architecture.md`, que avaliou e rejeitou um motor de workflow formal (BPMN/Camunda/Temporal, linhas 73-86) em favor da opção declarativa (linhas 57-71, 101-133). Essa é uma engenharia sólida e defensável, mas **não é inovação de CDS** — é uma reimplementação, sem uso de FHIR como modelo de dados nem de CQL/Arden como sintaxe, do mesmo padrão arquitetural que a indústria já formalizou há décadas. A consequência prática de não adotar um padrão interoperável: a lógica clínica do IntensiCare não é portável para outro EHR/CDS via CDS Hooks, nem reutilizável como biblioteca CQL — ao contrário do ArdenSuite, que implementa CDS Hooks sobre Arden Syntax em produção no Hospital Universitário de Viena ([ResearchGate](https://www.researchgate.net/publication/328250782_Implementing_CDS_Hooks_Communication_in_an_Arden-Syntax-Based_Clinical_Decision_Support_Platform)).

**Conclusão da seção**: o diferencial real está na **camada de produto** (multi-pathway genérico ponta-a-ponta, frontend a engine), não na camada de linguagem de regras (que é prática de mercado bem estabelecida, implementada de forma mais fechada/menos interoperável que os padrões HL7 existentes).

---

## 2. Valor clínico

### 2.1 Responde perguntas reais do intensivista?

Sim, de forma documentada e rastreável. `docs/audit/handoff-product-designer/FRONTEND_REBUILD_PLAN.md` §1 "A Jornada do Intensivista" (linhas 40-71) ancora a arquitetura de 6 páginas em 7 perguntas clínicas concretas de plantão: ronda matinal ("Quantos pacientes... algum crítico?", linhas 43-49), drill-down de trilha ("A trilha de sepse está em qual estado? Quais critérios violados? Qual a recomendação baseada em evidência?", linhas 51-55, citando SSC-2021), plantão noturno (linhas 57-63), e rastreabilidade reversa em código-azul ("De onde veio o alerta? Qual critério disparou?", linhas 65-68). O princípio de design declarado (linha 71): *"Cada página... responde a uma dessas perguntas. Se não responder, não existe."* Esse nível de ancoragem em jornada real é incomum e um ponto forte genuíno — mas é importante notar que a jornada documentada é validada contra a **v2 (33 páginas fragmentadas)**, não contra os concorrentes comerciais pesquisados nesta seção.

### 2.2 As 12 trilhas cobrem os principais riscos de UTI?

Cobertura razoável dos domínios centrais (infecção/sepse, renal, respiratório, neuro/delirium, sedação, ventilação/desmame, nutrição, profilaxia de complicações, antimicrobianos, eletrólitos, hemodinâmica), mas com gaps concretos verificados por grep exaustivo nos 12 YAMLs:

| Domínio esperado em CDS de UTI abrangente | Presente? | Evidência |
|---|---|---|
| TEV (tromboprofilaxia) | Parcial | `profilaxia.yaml:9,18,34,93,116` — checagem booleana "foi feito", **sem** escore de risco (Padua/IMPROVE) |
| Úlcera de estresse/sangramento GI | Parcial | `profilaxia.yaml:9,22,45,47` — mesma limitação, checagem booleana sem fatores de risco específicos |
| PAV (pneumonia associada à ventilação) | Muito parcial | apenas cabeceira elevada (`profilaxia.yaml:68,69,119`); nenhum outro elemento do bundle PAV (higiene oral, pressão de cuff) e nenhuma trilha de vigilância dedicada |
| Dor | Órfão | `sedacao.yaml:22,62,70,114,139` — BPS mencionado dentro da trilha de sedação; CPOT citado apenas em texto livre (linha 139), **nunca implementado como input/critério** |
| **Glicemia/controle glicêmico** | **Ausente** | Zero ocorrência em qualquer um dos 12 YAMLs |
| **Transfusão** | **Ausente** | Zero ocorrência em qualquer um dos 12 YAMLs |
| Mobilização precoce | Presente | `profilaxia.yaml` — checagem booleana |

Controle glicêmico e gatilhos de transfusão são elementos-padrão de bundles de cuidado intensivo geral (ex.: protocolo de insulina, gatilho transfusional restritivo) e sua ausência total é uma lacuna de cobertura real, não cosmética.

### 2.3 Severidade acionável — tempo-de-ação estruturado?

**Não.** O schema compartilhado (`_work/alerts/schema/pathway.schema.json`) define bandas de severidade (`normal/watch/urgent/critical`) mas **não tem nenhum campo de SLA/tempo-de-ação/deadline** por critério ou banda — o único conceito de temporização é `states[].auto_advance.timer_minutes` (schema.json:245), que **nenhuma das 12 trilhas popula**. Grep exaustivo por `time_window|prazo|sla|reavaliar em|iniciar em|timer_minutes` nos 12 arquivos YAML retorna **zero ocorrências estruturadas**. Toda referência temporal ("1 hora", "3 horas", "72h", "a cada 1-4h") existe apenas como substring dentro de texto narrativo em `evidence.recommendations` (ex.: `sepse.yaml:213-216`, `estabilidade.yaml:170`, `nutricao.yaml:208-210`) — não é um dado que o motor possa usar para disparar um lembrete, escalar um alerta não resolvido, ou alimentar um dashboard de SLA. Isso é uma lacuna concreta frente à pergunta de auditoria "cada nível tem ação e janela de tempo?" — a resposta é: tem ação (texto), **não tem janela de tempo estruturada**.

### 2.4 Recomendações baseadas em guideline real — amostra de 4 trilhas

| Trilha | Guideline citado | DOI | Observação |
|---|---|---|---|
| `sepse.yaml` | SSC-2021 (linhas 2, 9, 114, 210) | `10.1007/s00134-021-06506-y` | Predicados graduados (lactato, 67-87) + booleano (status ATB, 140-149) |
| `renal.yaml` | KDIGO 2012 + ADQI 2020 (linhas 2, 36, 62, 148) | `10.1038/kisup.2012.1` | Todos os 3 critérios graduados |
| `delirium.yaml` | PADIS 2018 (linhas 2, 9, 122) | `10.1097/CCM.0000000000003299` | Booleano (CAM-ICU, 33-42) + graduado (RASS, 44-68) |
| `ventilacao.yaml` | ARDSNet + PROSEVA 2013 (linha 69) | `10.1056/NEJM200005043421801` | Único arquivo com predicado tipo `threshold` puro; **sem** `evidence.recommendations`, sem `description`/`label` — arquivo minimalista comparado aos demais |

As citações são reais, verificáveis (DOI válidos apontando para os papers-fonte corretos: Surviving Sepsis Campaign 2021, KDIGO AKI 2012, PADIS 2018, PROSEVA 2013) — não são genéricas. **Ressalva importante cruzada com a Dimensão A** (`DIM_A_TRACEABILITY.md:56-61`): existe uma segunda implementação de sepse, `src/intensicare/services/domain_sepsis.py` (1022 linhas), fiel à especificação clínica completa (SIRS, gate de infecção presumida, estratificação de PCT, timers de bundle SSC-2021 1h/3h) e testada com 31 vetores (`tests/test_domain_sepsis.py`) — mas essa implementação é **código morto**: nenhum router de API a chama. O que a API/tela efetivamente serve é `sepse.yaml` via `TrilhasEngine`, uma reescrita mais simples sem SIRS, sem PCT e sem timers de bundle. Ou seja: **a trilha-bandeira do produto (escolhida como MVP/benchmark em `docs/adr/ADR-0031-mvp-pathway-sepsis.md`) é, na prática servida ao usuário, a versão menos completa das duas que existem no repositório.** Isso não invalida a citação de guideline (SSC-2021 está de fato referenciado no YAML servido), mas reduz a fidelidade clínica real da trilha mais visível do produto.

---

## 3. Completude vs concorrentes

### 3.1 A confusão dos "27 domínios"

A auditoria verificou a origem do número "27" citado no prompt original. **Não é uma medida da cobertura clínica do produto atual.** Sua origem real: `docs/rules/README.md:1066` e `docs/rules/AUDIT-REPORT.md:46` descrevem a Fase 2 de um **exercício de auditoria de código legado**, que agrupou 1.018 regras extraídas do código antigo em "27 clusters de domínio" — uma mistura de categorias clínicas e puramente técnicas (`sepse`, `evolucoes`, `movimentacao-adt`, `auth-usuarios`, `balanco-hidrico`, `operacional-infra`, `tenancy-organizacao`, `cadastros-ui`, `auditoria-logs`, etc.). O próprio `docs/plan/_work/briefs/audit-report.json:28` nota que esses 27 clusters são "distintos da taxonomia de 10 categorias" usada em outra parte do mesmo relatório.

Mais grave: os documentos do produto têm **quatro contagens não reconciliadas** de "quantos domínios/trilhas" o produto cobre:
- **27** — clusters de regra legada (`docs/rules/README.md:1066`)
- **9** — trilhas declaradas no MVP (`docs/adr/ADR-0031-mvp-pathway-sepsis.md:13`, `FRONTEND_REBUILD_PLAN.md:16`)
- **12** — arquivos YAML realmente presentes em `_work/alerts/pathways/`
- **7** — "domínios clínicos" citados em `docs/product/vision.md:38`

Essa dispersão de números é, em si, um achado de rigor documental — dificulta qualquer comparação séria de completude com concorrentes, e é sintoma de que a contagem de cobertura nunca foi consolidada como uma fonte única de verdade após as diversas fases de planejamento.

### 3.2 12 trilhas é suficiente para UTI geral vs sistemas comerciais?

Comercialmente, os sistemas pesquisados não competem no eixo "número de trilhas" — eles competem em **abrangência de sinal + capacidade preditiva** dentro de um score menor de dimensões (tipicamente 1 a poucos índices, mas computados continuamente a partir de fluxo contínuo de monitor). O IntensiCare cobre mais **domínios de guideline discretos** (12) do que qualquer um desses concorrentes expõe como produto (Etiometry declara 2 índices FDA-cleared centrais; CLEW, 1 modelo hemodinâmico + 1 respiratório em EUA de 2020). Nesse sentido, **12 trilhas é uma cobertura de domínio mais ampla em largura**, mas cada trilha individual é rasa em profundidade de risco (checagens booleanas simples nos bundles de profilaxia, sem escore de risco) comparado à profundidade estatística validada clinicamente dos índices dos concorrentes (ex.: Etiometry publica validação em dados adultos reais; CLEW tem clearance FDA com estudo de não-inferioridade). Ou seja: **largura sim, profundidade validada não** — o IntensiCare não publica (nem parece ter) estudo de validação de desempenho (sensibilidade/especificidade/PPV) para as 12 trilhas equivalente ao que os concorrentes publicam para seus índices.

---

## 4. Inovação técnica

### 4.1 Motor declarativo: inovador ou padrão?

Padrão conhecido, como discutido em §1.2 — precedido por Arden Syntax (1989), CQL, CDS Hooks, Drools, PROforma. A escolha de reimplementar em vez de adotar um padrão HL7 é defensável por controle/segurança (AST não Turing-completo, `trilhas_compiler.py:1-3`), mas tem custo de interoperabilidade.

### 4.2 Frontend data-driven genérico: inovador?

Sim, dentro do nicho de produtos CDS de UTI pesquisados — nenhum concorrente documenta uma arquitetura de UI equivalente (um único componente que renderiza N trilhas de guideline completas sem código específico por trilha). Verificado com evidência de código real, não apenas declaração de ADR: `criteria-list.tsx:138-145` é um `.map()` genérico sobre `PathwayCriteria[]`; `state-flow.tsx:13-29,84` computa estado passado/atual/futuro puramente a partir de dados; os tipos TypeScript derivam 1:1 do contrato OpenAPI (`lib/api.ts:1-3` ↔ `docs/contracts/pathways-openapi.yaml:430`). Esta é a inovação de produto mais forte e mais bem verificada da auditoria.

### 4.3 Ausência de ML: limitação ou escolha deliberada?

**Escolha deliberada, documentada com rigor real — o achado mais forte da seção de justificativa regulatória.** `docs/adr/0023-estabilidade-scoring-model.md` (aceito 2026-07-07) argumenta explicitamente: (a) segurança do paciente — *"a clinical safety context... means any model that cannot explain why it fired is a patient-safety risk"* (linha 19); (b) explicabilidade pós-hoc é insuficiente — *"Post-hoc explainability (SHAP/LIME) provides feature-importance approximations, not the deterministic... per this guideline that Gate C requires"* (linha 64); (c) fundamento regulatório nomeado — Resolução CFM 2.147/2016 e RDC ANVISA 657/2022 exigem racional clínico rastreável (linha 25), e CDS baseado em ML seria classificado como SaMD Classe III/IV pela ANVISA, exigindo estudo clínico de validação e 12-18 meses de trâmite regulatório vs semanas para um motor de threshold (linha 65); (d) desproporcionalidade de estágio — um sistema ML-primário exigiria *"a multi-year, multi-million-real regulatory program — disproportionate to IntensiCare's current stage"* (linha 100).

**Essa é uma escolha defensável e alinhada ao que a regulação real está sinalizando em 2025-2026**: a pesquisa web confirma que a isenção de CDS como dispositivo médico sob a seção 520(o)(1)(E) do FDCA depende de o profissional de saúde poder **revisar independentemente a base da recomendação** — exatamente o que um motor threshold determinístico satisfaz e um modelo ML de regressão opaco (como o Epic EDI, cuja lógica interna não é publicada) não satisfaz da mesma forma ([guidance FDA revisada em janeiro de 2026](https://intuitionlabs.ai/articles/fda-ai-ml-samd-guidance-compliance)). A regra ONC HTI-1 também caminha para exigir que ferramentas de suporte à decisão algorítmica exponham inputs, lógica e desempenho por subgrupo — algo trivialmente satisfeito por um motor de threshold auditável e não por um índice proprietário de regressão. Isso é um argumento comercial genuíno de diferenciação regulatória que o produto **não está explorando publicamente** (não há material de produto/marketing citando essa vantagem — apenas uma ADR técnica interna).

**Nuance**: a decisão de ADR-0023 não é "nunca ML" — é um híbrido (Opção 3): threshold primário no MVP, ML adiado para pós-MVP como camada de enriquecimento consultivo, nunca o único gatilho, condicionado a dados, clearance ANVISA e validação clínica (linhas 104-137). Confirmado por `docs/plan/delivery/regulatory-plan.md:7` — invariante de design: o sistema *"nunca emite diagnóstico autônomo... o momento em que o software passaria a auto-diagnosticar ou auto-tratar, ele sai da Classe II"*.

---

## 5. Gaps de inovação

Comparado ao que CDS moderno de ponta oferece hoje (2026), o IntensiCare **não tem nenhuma das seguintes capacidades**, verificado por busca exaustiva de código (`sklearn|torch|tensorflow|model.predict|risk_score` — zero hits reais em `src/`, `tests/`, `scripts/`):

| Capacidade de CDS moderno | Presente no IntensiCare? | Concorrente que tem |
|---|---|---|
| Predictive analytics / lead-time de deterioração | Não | Epic EDI (mediana 24h), CLEW (até 8h) |
| ML risk scoring | Não (ausência confirmada, deliberada — ver §4.3) | Epic EDI, Etiometry IDO2/IVCO2, CLEW |
| NLP em evoluções/notas clínicas | Não | discutido e **rejeitado** como dependência de caminho crítico em `docs/adr/0026-*.md`/`0028-*.md` (nunca planejado como feature agendada) |
| Integração EHR/FHIR (ingestão) | **Sim, implementado** | `src/intensicare/fhir/client.py` (631 linhas) — cliente FHIR R4 real, `FHIRPatientData.from_fhir_bundle()` (228-373); `src/intensicare/mllp_listener.py` — listener HL7v2/MLLP com `hl7apy`, parsing ORU-R01 (linha 242) |
| Exposição como serviço CDS Hooks para EHR de terceiros | Não | ArdenSuite/CQL fazem isso nativamente |
| Feedback loop de outcomes | Parcial — existe mecanismo de resolução de alerta para medir PPV (`docs/plan/delivery/validation-plan.md:70,179,184`), mas não há recalibração automática de threshold nem estudo de validação publicado equivalente aos concorrentes | Etiometry/CLEW publicam validação clínica formal |

### Gaps conscientes vs omissões

A maior parte dos gaps de capacidade preditiva é **consciente e documentada em roadmap**, não omissão silenciosa:
- `docs/plan/delivery/roadmap.md:35` — "2d = Correlation Engine + ML-preditivo, Meses 10-12"; linhas 89-93 descrevem uma "Fase 4 — ML horizon, Semanas 21+" para modelagem preditiva de sepse (MIMIC-IV + dados locais, inferência via Bedrock/SageMaker, validação clínica formal, possível re-registro ANVISA Classe III) — mas o próprio roadmap nota que essa fase **"não tem critério de saída ainda porque não tem gate de entrada aberto"** (paráfrase do achado do agente de pesquisa), ou seja, é aspiracional sem compromisso de cronograma firme.
- `docs/plan/product/product-spec.md:471-491` lista explicitamente como **fora de escopo (WON'T-HAVE)**: modelo ML preditivo de sepse como entregável do MVP, runtime de ML dentro do caminho determinístico de alerta, apps SMART-on-FHIR, app mobile nativo, diagnóstico/tratamento autônomo (quebraria a classificação SaMD Classe II), operação de pipeline de ingestão próprio ou servidor FHIR próprio.

Os gaps de **cobertura clínica** (glicemia, transfusão, PAV completo, CPOT/dor, risco estratificado em profilaxia) **não têm o mesmo nível de reconhecimento explícito** — não há uma seção de docs que diga "sabemos que faltam glicemia e transfusão, decisão consciente de não incluir no MVP." Isso os torna mais próximos de **omissão não documentada** do que de gap conscientemente aceito, ao contrário do gap de ML.

---

## 6. Scoring

### 6.1 Nota final: **58/100**

Pontuação por dedução a partir de 100, cada item com achado correspondente:

| # | Achado | Pontos perdidos |
|---|---|---|
| 1 | Nenhuma trilha tem tempo-de-ação/SLA estruturado e acionável pelo motor — apenas texto livre embutido em `evidence.recommendations`; campo de schema (`timer_minutes`) existe mas não é populado por nenhuma das 12 trilhas (`_work/alerts/schema/pathway.schema.json:245`) | -10 |
| 2 | Zero capacidade preditiva/analítica — motor é puramente reativo a threshold do instante presente, sem trending nem lead-time, ao contrário de todos os 4 concorrentes pesquisados (Epic EDI: lead-time mediano 24h; CLEW: até 8h) | -8 |
| 3 | Trilha-bandeira (sepse, MVP/benchmark declarado em ADR-0031) servida ao usuário é a implementação **menos completa** das duas existentes no repo — `domain_sepsis.py` (SIRS, PCT, timers de bundle SSC-2021) é código morto não roteado por nenhum endpoint (achado cruzado com Dimensão A) | -7 |
| 4 | Gaps de cobertura clínica não documentados como decisão consciente: ausência total de glicemia e transfusão; PAV cobre só 1 elemento de bundle; profilaxia de TEV/UGE são checagens booleanas sem estratificação de risco (sem Padua/IMPROVE) | -6 |
| 5 | Quatro contagens de domínio/trilha não reconciliadas em docs distintos (27 clusters legados, 9 no ADR-0031, 12 arquivos reais, 7 em vision.md) — mina a confiabilidade da narrativa de completude | -4 |
| 6 | Motor de regras é DSL proprietário não interoperável — sem uso de Arden Syntax/CQL/CDS Hooks, lógica clínica não portável para EHR de terceiros nem exposta como serviço CDS Hooks | -4 |
| 7 | Sem validação clínica publicada (sensibilidade/PPV/AUC) das 12 trilhas equivalente à que concorrentes (Etiometry, CLEW) publicam para seus índices; feedback loop de PPV existe mas não gera recalibração automática documentada | -3 |
| **Total perdido** | | **-42** |
| **Nota final** | | **58/100** |

**O que sustenta a nota acima de 50**: arquitetura pathway-centric genuinamente diferenciada e verificada em código real (não apenas declarada em ADR); recomendações citando guidelines reais com DOI válidos em amostra de 4+ trilhas; justificativa "sem ML" excepcionalmente bem fundamentada e alinhada à direção regulatória real de 2025-2026 (FDA CDS exemption, ONC HTI-1); integração FHIR/HL7 real e funcional, não apenas planejada; jornada do intensivista documentada e rastreável a decisões de UI.

### 6.2 Matriz comparativa

| Critério | **IntensiCare** | Epic Deterioration Index | Philips IntelliVue Guardian / eICU | Etiometry | CLEW Medical |
|---|---|---|---|---|---|
| **Abordagem** | Multi-trilha declarativa (12 guidelines), motor de regras threshold/graduado | Índice único de regressão/ML sobre ~30k pontos de dado EHR | EWS/MEWS único configurável por parâmetro, tele-ICU hub-and-spoke | Dashboard multiparamétrico + 2 índices fisiológicos proprietários FDA-cleared (IDO2, IVCO2) | Modelo único de instabilidade hemodinâmica/respiratória, preditivo |
| **Cobertura clínica** | Larga (12 domínios de guideline), rasa em profundidade de risco em alguns (profilaxia sem escore) | Estreita (1 índice geral de deterioração/sepse) | Estreita (1 EWS geral) | Estreita-média (2 índices fisiológicos + dashboard) | Estreita (1-2 modelos: hemodinâmico + respiratório) |
| **Explicabilidade/auditabilidade** | Alta — threshold determinístico, racional 100% rastreável a critério/guideline, decisão documentada em ADR-0023 com fundamento CFM/ANVISA | Baixa — modelo proprietário de regressão, lógica interna não publicada | Média — EWS é soma de pontos por parâmetro, interpretável, mas não guideline-specific | Média-alta — índices publicados com base fisiológica conhecida, mas "advanced algorithms" não totalmente abertos | Baixa — modelo preditivo FDA-cleared, mas lógica interna não pública |
| **Tempo-real / capacidade preditiva** | Reativo apenas (threshold do instante); zero lead-time | Preditivo, lead-time mediano ~24h | Reativo (EWS calculado a cada leitura, sem lead-time preditivo divulgado) | Tempo real contínuo, orientado a risco instantâneo (não divulga lead-time como CLEW) | Preditivo, lead-time até 8h, FDA-cleared para esse claim |
| **Extensibilidade (nova trilha/parâmetro)** | Alta — nova trilha = novo YAML, zero código frontend (ADR-0033, verificado em código) | Baixa — modelo fechado, mudança requer retrain/revalidação Epic | Média — reconfiguração de pesos do EWS é suportada, mas não adiciona novos domínios de guideline | Baixa-média — requer trabalho de engenharia proprietário (embora ADK 2.0 vise permitir algoritmos customizados) | Baixa — modelo fechado, regulado |
| **Interoperabilidade de conhecimento clínico (portabilidade para outro EHR)** | Baixa — DSL proprietário, não Arden/CQL/CDS Hooks | N/A (embutido no Epic) | N/A (embutido no ecossistema Philips) | N/A (plataforma própria) | N/A (modelo embutido) |

### 6.3 Recomendações para aumentar diferenciação

1. **Estruturar tempo-de-ação como dado, não texto.** Adicionar campo `time_to_action` (ex.: minutos) por banda de severidade no schema (`pathway.schema.json`), popular nas 12 trilhas a partir do texto já existente em `evidence.recommendations`, e conectar ao motor para gerar escalonamento automático de alerta não resolvido. Isso fecha a lacuna #1 do scoring e transforma "recomendação lida" em "SLA clínico executável" — algo que nenhum dos concorrentes pesquisados expõe de forma tão granular por trilha.

2. **Resolver a duplicidade de sepse e tratar isso como gate de CI.** Decidir entre aposentar `domain_sepsis.py` ou roteá-lo como a implementação servida; adicionar um teste de integração que verifique que a trilha realmente exposta pela API contém os elementos clínicos documentados na especificação ratificada (SIRS, PCT, timers de bundle). A trilha-bandeira do MVP não pode ser a versão mais pobre das duas.

3. **Publicar a justificativa "sem ML" como diferencial comercial, não só ADR interna.** O argumento de ADR-0023 (explicabilidade determinística, CFM 2.147/2016, RDC ANVISA 657/2022, alinhamento com a isenção de CDS da FDCA §520(o)(1)(E) e a direção do ONC HTI-1) é mais forte e mais atual do que a maioria dos concorrentes pode alegar sobre seus próprios modelos de regressão/ML fechados. Isso deveria aparecer em material de produto voltado a compradores/reguladores, emparelhado com um roadmap público (não apenas interno) da camada de ML pós-MVP como consultiva/nunca-autônoma.

4. **Fechar gaps de cobertura documentados como decisão, não como silêncio.** Adicionar ao `product-spec.md` uma seção explícita "fora do MVP, e por quê" cobrindo glicemia, transfusão e vigilância completa de PAV — ou, alternativamente, priorizar glicemia (alto volume, protocolo bem padronizado, fácil de graduar como as trilhas já existentes) como 13ª trilha. Adicionar estratificação de risco (Padua/IMPROVE) aos booleanos de TEV/UGE em `profilaxia.yaml`.

5. **Reconciliar a narrativa de cobertura em uma fonte única de verdade.** Publicar um documento canônico (`docs/product/coverage.md` ou similar) que declare definitivamente "N trilhas ativas, cobrindo M domínios clínicos," mapeando explicitamente por que os 27 clusters legados, os 9 do MVP original e os 12 YAMLs atuais não são a mesma contagem — encerrando a ambiguidade que hoje mina qualquer alegação de completude frente a concorrentes.

---

## Apêndice — Fontes externas consultadas

- [Developing and Deploying a Sepsis Deterioration Machine Learning Algorithm — IntechOpen](https://www.intechopen.com/chapters/87019)
- [Philips IntelliVue Guardian Solution](https://www.usa.philips.com/healthcare/product/HCNOCTN60)
- [Philips eICU — ICU predictive analytics](https://intuitionlabs.ai/software/intensive-care-critical-care/icu-predictive-analytics/philips-eicu)
- [CLEW Medical Receives FDA Clearance for AI-Based Predictive Analytics Technology](https://www.prnewswire.com/news-releases/clew-medical-receives-fda-clearance-for-ai-based-predictive-analytics-technology-to-support-adult-icu-patient-assessment-301221173.html)
- [How Clinical Intelligence Software Supports ICU Decision-Making — Etiometry](https://www.etiometry.com/resources/how-clinical-intelligence-software-supports-icu-decision-making/)
- [A Comparison of Arden Syntax and Clinical Quality Language as Knowledge Representation Formalisms for CDS — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8245210/)
- [Implementing CDS Hooks Communication in an Arden-Syntax-Based CDS Platform — ResearchGate](https://www.researchgate.net/publication/328250782_Implementing_CDS_Hooks_Communication_in_an_Arden-Syntax-Based_Clinical_Decision_Support_Platform)
- [Contemporary CDS standards using HL7 FHIR — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8324242/)
- [FDA AI/ML SaMD Guidance: 2026 Compliance Guide — IntuitionLabs](https://intuitionlabs.ai/articles/fda-ai-ml-samd-guidance-compliance)
