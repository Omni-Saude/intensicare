# ADR-028: Arquitetura de Evoluções Clínicas — 81 regras de documentação

Status: accepted
**Data:** 2026-07-07
**Area:** Documentação Clínica / Dados / Agentes
**Referência:** Catálogo `docs/rules/extraction/phase2/catalog/evolucoes.yaml` (81 regras); ADR-0015 (form engine); ADR-0008 (L0-hard — sistema nunca decide conduta)

## Contexto

As evoluções clínicas são o principal instrumento de documentação em UTIs brasileiras. Diferente de
formulários estruturados como RASS ou SOFA (que capturam uma medida pontual), a evolução é um
**registro narrativo longitudinal** produzido por múltiplos profissionais (médico, enfermeiro,
fisioterapeuta, nutricionista, farmacêutico, psicólogo, fonoaudiólogo) em turnos sucessivos,
descrevendo o estado do paciente, intercorrências, resposta à terapêutica e plano de cuidados.

O catálogo de regras legadas (`evolucoes.yaml`) contém **81 regras** — o segundo maior cluster do
projeto (atrás apenas de movimentação/ADT com 74 regras). As regras cobrem:

- **14 papéis clínicos** com formulários de evolução específicos (médico, enfermagem, fisioterapia,
  farmácia, nutrição, psicologia, fonoaudiologia, musicoterapia, técnico de enfermagem, admissão,
  alta/remoção, movimentação, intercorrência, balanço hídrico).
- **Campos estruturados** coexistindo com **texto livre**: sinais vitais, scores (SOFA, Glasgow,
  RASS), dados de ventilação mecânica, acesso venoso, dispositivos invasivos, medicações em uso,
  intercorrências e o texto narrativo da evolução propriamente dita.
- **SOFA pré-calculado** exibido como badge no topo do formulário (RULE-EVOLUCOES-001/002),
  demonstrando que mesmo o campo "narrativo" carrega dados estruturados computados server-side.
- **Inconsistências de tipo** entre modelos (ex.: RASS como `number` em Ocupação vs `string` em
  DadosProntuario — RULE-EVOLUCOES-003), sinalizando que a fronteira entre "estruturado" e
  "texto livre" nunca foi formalizada — os campos migraram de tipo conforme o contexto de uso.
- **Padrão SBAR implícito**: as seções dos formulários de evolução (identificação, situação atual,
  background/antecedentes, avaliação, recomendação/plano) seguem a estrutura do protocolo SBAR
  (Situation-Background-Assessment-Recommendation), padrão ouro em comunicação clínica para
  handoff seguro (The Joint Commission, 2017).

O problema arquitetural central é: **qual o grau de estruturação das evoluções clínicas?**
A resposta afeta três dimensões concorrentes: aceitação clínica (texto livre é preferido pelos
profissionais), capacidade analítica (dados estruturados habilitam ML e pesquisa), e conformidade
médico-legal (trilha de auditoria, imutabilidade, não-repúdio).

### Decision Drivers

- **Aceitação clínica:** profissionais de UTI rejeitam sistemas que substituem texto narrativo por
  checkboxes — a evolução é um ato clínico de raciocínio, não um formulário de coleta. Impor
  estruturação total gera boicote ou workaround (cola texto livre em campos "observações").
- **Analytics e ML:** dados estruturados permitem busca, agregação, análise de tendências e
  treinamento de modelos preditivos (ex.: deterioração clínica, tempo de permanência, readmissão).
  Texto livre exige NLP/LLM para extração — viável, mas com recall/precision abaixo de 100%.
- **Conformidade médico-legal (CFM/ANVISA):** o prontuário é documento legal. Cada entrada deve ser
  imutável (audit trail), atribuível a um profissional e timestamped. Resoluções CFM 1.638/2002 e
  1.821/2007 definem requisitos de completude e fidedignidade do prontuário.
- **SBAR como padrão de comunicação:** as seções do formulário de evolução já mapeiam naturalmente
  para SBAR — preservar essa estrutura facilita handoff e comunicação interdisciplinar.
- **Integração com o form engine (ADR-0015):** o motor de formulários dinâmico já cobre formulários
  estruturados (RASS, CAM-ICU, Glasgow, SOFA). As evoluções podem compartilhar ou estender esse
  motor, ou seguir um caminho arquitetural distinto.
- **81 regras legadas cobrem validações de negócio:** regras como "SOFA ≥ 2 com infecção suspeita
  → alerta de sepse", "paciente em ventilação mecânica > 21 dias → alerta de traqueostomia",
  "intercorrência grave sem evolução médica em 2h → alerta de qualidade". Essas regras consomem
  dados que só existem se estruturados.

Três abordagens foram consideradas:

### Opção 1: Texto livre puro (narrativa não estruturada)

A evolução é um único campo de texto rico (Rich Text Editor com suporte a formatação, templates
personalizáveis por profissional, reconhecimento de voz). Nenhum campo estruturado — o profissional
escreve o que julgar relevante. O sistema armazena o texto como documento versionado e imutável
(audit trail). Agentes de IA (Helena) consomem o texto via LLM para extrair sinais, sumarizar e
detectar padrões.

**Prós:**
- Máxima aceitação clínica — o profissional escreve exatamente como faria no papel.
- Flexibilidade total: nenhum protocolo clínico é "hardcoded" no formulário; a evolução se adapta
  organicamente a qualquer cenário clínico.
- Simplicidade de implementação: um editor de texto rico + storage de documentos versionados.
- O LLM como camada de extração é flexível e evolui sem alterar a UI.

**Contras:**
- NLP/LLM como dependência crítica para qualquer funcionalidade analítica — se o modelo falha ou
  degrada, perde-se a capacidade de busca, sumarização, detecção de padrões e disparo de alertas.
- Recall/precision da extração nunca é 100% — informações críticas (ex.: "noradrenalina 0.5" sem
  unidade) podem ser mal interpretadas ou perdidas.
- As 81 regras legadas que dependem de campos estruturados (SOFA, Glasgow, sinais vitais,
  dispositivos) não podem ser aplicadas deterministicamente — dependem da acurácia da extração.
- Custo de inferência: cada evolução precisa ser processada por LLM para extração, sumarização e
  detecção — custo computacional e financeiro por documento.
- Impossibilidade de validação em tempo real: o sistema não pode alertar o profissional no momento
  do preenchimento (ex.: "SOFA sugere sepse — deseja registrar o bundle de 1h?") porque não há
  estrutura para disparar a regra.
- Conformidade regulatória ambígua: um prontuário puramente narrativo sem campos estruturados
  pode não satisfazer requisitos mínimos de completude da CFM/ANVISA para UTIs.

### Opção 2: Templates estruturados com seções de texto livre (balanceado)

A evolução é um **template híbrido**: seções estruturadas (sinais vitais, scores, dispositivos,
medicações — campos tipados, com validação) convivem com seções de texto narrativo livre
(evolução propriamente dita, impressão clínica, plano). O template é específico por papel clínico
(médico, enfermagem, fisioterapeuta, etc.) e mapeia para a estrutura SBAR naturalmente:

- **S (Situation):** identificação do paciente, data/hora, profissional, tipo de evolução.
- **B (Background):** scores atuais (SOFA, Glasgow, RASS), sinais vitais, dispositivos, medicações
  em uso — campos estruturados, pré-preenchidos do estado atual do paciente.
- **A (Assessment):** evolução narrativa e impressão clínica — texto livre rico.
- **R (Recommendation):** plano terapêutico e conduta — texto livre com structured hints (checklist
  de bundles aplicáveis).

O motor de formulários dinâmico (ADR-0015/ADR-029) renderiza as seções estruturadas; um editor de
texto rico é embutido como campo `string` do tipo `rich-text` nas seções narrativas.

**Prós:**
- Balanceia aceitação clínica (texto livre onde o raciocínio importa) com analytics (campos
  estruturados onde a precisão importa).
- Campos estruturados são pré-preenchidos do estado atual do paciente (via `MovimentacaoStateStore`,
  ADR-0025, e EWS/NRT pipeline), reduzindo carga de documentação e risco de erro de transcrição.
- As 81 regras podem ser aplicadas deterministicamente sobre os campos estruturados (SOFA, sinais
  vitais, dispositivos) sem depender de NLP.
- O texto narrativo pode ser enriquecido com LLM (sumarização, extração de entidades, sugestão de
  bundles) sem que a funcionalidade crítica dependa do LLM.
- Validação em tempo real: o sistema pode alertar durante o preenchimento (ex.: "Paciente em VM por
  21 dias — considerar avaliação para traqueostomia").
- Conformidade regulatória: campos estruturados mínimos garantem completude documental exigida
  pela CFM/ANVISA.
- Reusa o form engine existente (ADR-0015/ADR-029) — as seções estruturadas são grupos no
  `FormConfig`; a seção narrativa é um field renderer especializado.

**Contras:**
- Complexidade de design dos templates: 14 papéis clínicos × seções específicas exigem design
  cuidadoso para não sobrecarregar o profissional com campos obrigatórios irrelevantes.
- Rigidez parcial: se um template não prevê um campo que o profissional julga relevante, ele
  precisa usar o texto livre — e esse dado fica invisível para as regras estruturadas.
- A fronteira entre "estruturado" e "narrativo" pode migrar com o tempo (ex.: um campo que hoje é
  texto livre pode se tornar estruturado em uma versão futura) — exige versionamento de template
  e migração de dados históricos.
- Custo de manutenção: 14 templates evoluem independentemente (cada papel clínico pode requisitar
  novos campos); requer governança de schema.

### Opção 3: Totalmente estruturado com campos codificados (analyzable, rígido)

Toda a evolução é composta por campos estruturados e codificados — cada observação clínica é
mapeada para um código de vocabulário controlado (SNOMED CT, LOINC) e registrada como um par
`{code, value, unit, timestamp}`. O texto narrativo é substituído por seleção de achados clínicos
pré-codificados. A evolução deixa de ser um documento e passa a ser um conjunto de observações
FHIR (`Observation` resources).

**Prós:**
- Analisabilidade máxima: todos os dados são estruturados, codificados e queryable. ML, pesquisa
  clínica e epidemiologia em tempo real são nativos.
- Interoperabilidade total: cada observação é um recurso FHIR com codificação SNOMED/LOINC,
  exportável e integrável com qualquer sistema consumidor.
- Validação completa: regras de negócio, bundles e alertas operam sobre o grafo completo de
  observações, sem zona cinzenta de texto não estruturado.
- Consistência semântica: vocabulários controlados eliminam ambiguidade (ex.: "dispneia" sempre
  mapeia para um código SNOMED específico, não para texto livre).

**Contras:**
- **Rejeição clínica praticamente certa.** Profissionais de UTI experienciam sistemas totalmente
  estruturados como "checklist medicine" — a evolução deixa de ser um ato de raciocínio clínico e
  passa a ser uma tarefa de data entry. A adoção seria baixíssima.
- Impossibilidade de capturar nuances clínicas: o raciocínio diagnóstico (ex.: "provável aspergilose
  pulmonar invasiva vs colonização — iniciar voriconazol empírico e solicitar galactomanana sérica")
  não é redutível a um conjunto de códigos SNOMED.
- Custo de vocabulário: manter o mapeamento SNOMED/LOINC para todos os achados clínicos de UTI é
  um esforço contínuo e especializado.
- A evolução é um documento médico-legal narrativo — um prontuário composto exclusivamente de
  observações codificadas pode não ser aceito como registro clínico válido em auditoria ou perícia.
- O legado tem 14 formulários com campos mistos (estruturados + texto) — migrar para 100%
  estruturado exigiria reescrever completamente o modelo de documentação, com altíssimo custo de
  transição e treinamento.

## Decisão

**Opção 2 — Templates estruturados com seções de texto livre (modelo híbrido SBAR)**, com as
seguintes características:

1. **Template híbrido por papel clínico, com estrutura SBAR canônica.** Cada papel clínico
   (médico, enfermagem, fisioterapeuta, farmácia, nutrição, psicologia, fonoaudiologia,
   musicoterapia, técnico de enfermagem, admissão, alta, movimentação, intercorrência, balanço
   hídrico) possui um template de evolução com quatro seções SBAR:

   - **S (Situation):** cabeçalho comum — identificação do paciente (pré-preenchido via MPI),
     data/hora, profissional, tipo de evolução, número de atendimento. Campos estruturados,
     todos obrigatórios.
   - **B (Background):** dados clínicos objetivos — sinais vitais (pré-preenchidos do pipeline
     EWS/NRT), scores (SOFA, Glasgow, RASS — pré-calculados pelo `PioraClinicaService` e
     serviços de scoring), dispositivos invasivos, medicações em uso, ventilação mecânica,
     acesso venoso. Campos estruturados com validação, pré-preenchidos do estado atual do
     paciente via `MovimentacaoStateStore` (ADR-0025) e serviços de domínio (ventilação,
     hemodinâmica). O profissional confere e ajusta, não digita do zero.
   - **A (Assessment):** evolução narrativa e impressão clínica — **texto livre rico** (Rich Text
     Editor com suporte a formatação, voice-to-text, snippets personalizados por profissional).
     Esta é a seção central onde o raciocínio clínico acontece — não é estruturável.
   - **R (Recommendation):** plano terapêutico, conduta e bundles — **texto livre com hints
     estruturados**. O sistema sugere bundles aplicáveis (ex.: "Bundle de PAV", "Bundle de CVC",
     "Bundle de sepse 1h") com base nos dados estruturados da seção B; o profissional confirma,
     ajusta ou ignora. As confirmações geram registros estruturados de adesão a bundles.

2. **O motor de formulários dinâmico (ADR-0015/ADR-029) renderiza as seções S e B.** As seções
   `Situation` e `Background` são `FormGroup`s no `FormConfig` do form engine, com campos tipados
   (`number`, `select`, `boolean`, `date`, `masked`) e validação Zod. O motor de formulários
   é estendido com um field renderer `rich-text` para as seções `Assessment` e `Recommendation`.

3. **Pré-preenchimento inteligente (reduce charting burden).** Os campos da seção B são
   pré-preenchidos com o último valor conhecido de cada parâmetro (do pipeline EWS/NRT,
   `MovimentacaoStateStore` e serviços de scoring). O profissional **confere e corrige**, não
   redigita. Isso reduz o tempo de documentação (um dos principais fatores de burnout em UTI) e
   elimina erros de transcrição. Valores alterados pelo profissional são sinalizados como
   "corrigidos manualmente" no audit trail.

4. **Regras de negócio (81 regras) aplicadas deterministicamente sobre campos estruturados.**
   As regras do catálogo `evolucoes.yaml` consomem os campos da seção B (SOFA, sinais vitais,
   dispositivos, medicações) e disparam alertas, bundles e notificações. O texto narrativo
   (seções A e R) é enriquecido por LLM (sumarização, extração de entidades, sugestão de bundles)
   mas **nenhuma regra crítica depende exclusivamente do LLM** — o caminho determinístico
   (campos estruturados → regras → alertas) é o primário.

5. **Imutabilidade e audit trail (medico-legal).** Cada evolução é armazenada como um documento
   versionado e imutável. O registro inclui: conteúdo completo (estruturado + texto), profissional,
   timestamp, `definition_version` do template utilizado, e hash do conteúdo para não-repúdio.
   Correções são feitas como **adendos** (novo documento que referencia o original), nunca como
   edição in-place. Consistente com ADR-0007 (audit trail) e resoluções CFM 1.638/2002 e 1.821/2007.

6. **Versionamento de templates.** Cada template de evolução (por papel clínico) é versionado
   (`definition_version`). Alterações no template (ex.: adicionar um novo campo estruturado na
   seção B, ou modificar opções de um select) geram uma nova versão. Evoluções criadas com a
   versão anterior permanecem íntegras e legíveis — o sistema renderiza o template histórico para
   visualização, mas novas evoluções usam a versão atual. O campo `definition_version` é registrado
   em cada documento para trilha de auditoria (INV-3).

7. **O LLM é assistente, não substituto.** O texto narrativo (seções A e R) pode ser processado
   por LLM para:
   - Sumarização automática (resumo da evolução para handoff).
   - Extração de entidades clínicas (medicações mencionadas, procedimentos, diagnósticos).
   - Sugestão de bundles aplicáveis com base no contexto narrativo.
   - Detecção de omissões (ex.: "Paciente em VM — evolução não menciona desmame ou traqueostomia").

   Nenhuma dessas funções bloqueia o fluxo clínico — são sugestões exibidas como cards laterais
   que o profissional pode aceitar, ignorar ou descartar. Consistente com ADR-0008 (L0-hard: o
   sistema nunca decide conduta) e ADR-0005 (decisão clínica é exclusiva do profissional).

8. **Integração com bundles e pathways.** As sugestões de bundles na seção R integram-se com o
   `trilhas-engine` (ADR-0020): quando o profissional confirma um bundle (ex.: "Bundle de PAV
   aplicado"), o sistema registra o evento de adesão e o motor de trilhas avalia se o paciente
   está aderente ao protocolo. Isso fecha o ciclo: documentação → adesão a bundles → métricas de
   qualidade → feedback para o time assistencial.

**Gatilho de reavaliação:** Se a extração por LLM do texto narrativo atingir recall/precision
> 98% sustentados em validação clínica prospectiva por ≥ 6 meses, reavaliar a redução de campos
estruturados na seção B (mantendo apenas os críticos para segurança) e a migração de regras para
consumo do texto enriquecido por LLM. Inversamente, se a aceitação clínica dos templates for baixa
(NPS < 30 ou taxa de abandono de campos estruturados > 30%), reavaliar a simplificação dos
templates (menos campos, mais texto livre) rumo à Opção 1.

## Consequencias

**Positivas:**

- Balanceia aceitação clínica com analytics: o profissional escreve a narrativa clínica como sempre
  fez (texto livre rico nas seções A e R), mas o sistema extrai valor dos campos estruturados
  (seção B) para alertas, bundles e pesquisa — sem depender de NLP para funcionalidade crítica.
- Redução da carga de documentação: o pré-preenchimento inteligente da seção B (via EWS/NRT,
  `MovimentacaoStateStore`, serviços de scoring) elimina redigitação de sinais vitais, scores e
  dispositivos — o profissional confere e ajusta, economizando 2-5 minutos por evolução.
- As 81 regras legadas operam deterministicamente sobre os campos estruturados (SOFA, Glasgow,
  sinais vitais, dispositivos, ventilação) — sem dependência de LLM para disparo de alertas.
- SBAR como estrutura canônica melhora a qualidade do handoff: todas as evoluções seguem o mesmo
  padrão de comunicação, facilitando a continuidade do cuidado entre turnos e entre profissionais.
- Imutabilidade e audit trail satisfazem requisitos médico-legais (CFM/ANVISA) — cada evolução é
  um documento versionado, atribuível e não-repudiável.
- O LLM atua como assistente de documentação (sumarização, sugestão de bundles, detecção de
  omissões) sem bloquear o fluxo clínico — consistente com ADR-0008 (L0-hard).
- Reuso do form engine (ADR-0015/ADR-029): as seções estruturadas são grupos no `FormConfig`;
  apenas o renderer `rich-text` é novo.
- Extensibilidade: novos papéis clínicos ou novos campos estruturados são adicionados como
  templates versionados, sem alterar a arquitetura.

**Negativas (aceitas):**

- Complexidade de design dos 14 templates: cada papel clínico exige um template SBAR específico
  com os campos relevantes para aquele profissional — o design inicial é trabalhoso e requer
  validação com cada especialidade.
- A fronteira "estruturado vs narrativo" vai evoluir: campos que hoje são texto livre podem migrar
  para estruturados (e vice-versa) conforme o uso clínico — exige versionamento de template e
  migração de dados históricos.
- O pré-preenchimento inteligente depende da disponibilidade dos serviços upstream (EWS/NRT,
  `MovimentacaoStateStore`, serviços de scoring) — se um serviço estiver indisponível, o campo
  aparece vazio e o profissional precisa preencher manualmente (modo degradado).
- As 81 regras legadas precisam ser revalidadas contra o novo modelo híbrido — regras que hoje
  dependem de campos que migrarão para texto livre precisam ser redesenhadas ou descontinuadas
  (com sign-off clínico).
- Custo de manutenção: 14 templates versionados + renderer `rich-text` + pipeline de
  pré-preenchimento + integração com bundles/trilhas — superfície de código maior que uma
  solução puramente narrativa (Opção 1) ou puramente estruturada (Opção 3).

## Supersedes

— (estende ADR-0015 — o form engine cobre formulários estruturados como RASS e SOFA; este ADR
estende o engine com o renderer `rich-text` e o conceito de template híbrido SBAR para evoluções.
Referencia ADR-0025 — o `MovimentacaoStateStore` provê o estado do paciente para pré-preenchimento.
Referencia ADR-0020 — o `trilhas-engine` consome os bundles confirmados na seção R para avaliação
de aderência a protocolos.)
