# ADR-029: Estratégia do Motor de Formulários Clínicos Dinâmicos — 49 regras

**Status:** Proposed
**Data:** 2026-07-07
**Area:** Frontend / Documentação Clínica / Arquitetura
**Referência:** Catálogo `docs/rules/extraction/phase2/catalog/formularios-clinicos.yaml` (49 regras);
ADR-0015 (config-driven dynamic clinical form engine); `lib/form-engine/` (implementação atual)

## Contexto

Formulários clínicos estruturados — RASS (sedação), CAM-ICU (delirium), BPS/NRS (dor), Glasgow
(coma), SOFA (disfunção orgânica), LPP (lesão por pressão/NPUAP) — são instrumentos de avaliação
padronizados aplicados repetidamente na rotina da UTI. Diferente das evoluções clínicas (que são
narrativas com seções estruturadas — ADR-028), esses formulários são **instrumentos de scoring
determinístico**: cada campo tem um significado clínico preciso, intervalos de referência validados,
e o escore agregado tem implicações prognósticas e de conduta.

O catálogo de regras legadas (`formularios-clinicos.yaml`) contém **49 regras** cobrindo:

- **RASS (Richmond Agitation-Sedation Scale):** escala ordinal de -5 a +4 para nível de sedação/
  agitação. A auditoria encontrou **discrepância de tipo** entre modelos (`number` vs `string` —
  RULE-EVOLUCOES-003, cross-referenciada no catálogo de formulários como RULE-FORMULARIOS-CLINICOS-006).
- **CAM-ICU (Confusion Assessment Method for ICU):** avaliação binária de delirium baseada em 4
  features (alteração aguda/flutuante, inatenção, pensamento desorganizado, nível de consciência
  alterado). Regras OK mas sem validação de coerência (ex.: RASS = -5 invalida CAM-ICU).
- **BPS/NRS (Behavioral Pain Scale / Numeric Rating Scale):** avaliação de dor em pacientes sob
  ventilação mecânica (BPS: expressão facial, movimentos de membros, adaptação ao ventilador) e
  conscientes (NRS: 0-10).
- **Glasgow (Glasgow Coma Scale):** abertura ocular (1-4), resposta verbal (1-5), resposta motora
  (1-6), total 3-15. Regras OK; sem validação de sub-escore individual no legado.
- **SOFA (Sequential Organ Failure Assessment):** 6 sistemas orgânicos (respiratório, coagulação,
  hepático, cardiovascular, SNC, renal), cada um 0-4, total 0-24. O legado exibe SOFA como badge
  "warning" estático independente do valor — o score não é computado client-side
  (RULE-EVOLUCOES-001/002). A computação é server-side.
- **LPP/NPUAP (Lesão por Pressão):** estadiamento NPUAP I-IV + suspeita de lesão profunda + não
  graduável + avaliação de ferida (tipo de tecido, secreção, exsudato, pele perilesional, edema
  com borda de 4 cm). Duplicação de formulário entre enfermagem e nutrição
  (RULE-FORMULARIOS-CLINICOS-002).
- **Avaliação global de admissão:** 24 campos de avaliação inicial (pele, mucosa, dispositivos,
  risco de queda — Morse/Braden —, alergias, condições prévias).

O projeto já possui um motor de formulários dinâmico (`lib/form-engine/`) com:
- **Tipos de campo:** `string`, `select`, `number`, `boolean`, `checkbox`, `date`, `masked`,
  `multicheck` (8 tipos — `FormField.type`).
- **Configuração declarativa:** `FormConfig` com `groups[]` → `fields[]`, cada campo com `name`,
  `label` (PT-BR), `type`, `required`, `options`, `min`/`max`, `mask`, `hint`.
- **Validação Zod dinâmica:** `buildZodSchema()` gera um schema Zod a partir do `FormConfig`
  em runtime, com validação de tipo, required, min/max para numbers.
- **Renderers desacoplados:** cada tipo de campo tem um componente React dedicado (`StringField`,
  `SelectField`, `NumberField`, `BooleanField`, `CheckboxField`, `DateField`, `MaskedField`).
- **Agrupamento colapsável:** grupos de campos com `collapsible`/`defaultOpen` (herança do
  `CollapsedFields` do legado).
- **Validação customizada:** `FormValidation.atLeastOne` para grupos onde pelo menos um campo deve
  ser preenchido.

O que **falta** no motor atual (gap analysis contra as 49 regras):

1. **Validação cross-field:** regras que envolvem múltiplos campos não são expressáveis no schema
   atual (ex.: "se RASS = -5, CAM-ICU não se aplica"; "se Glasgow verbal = 1 (intubado), campo deve
   aceitar 'NT' como valor especial"; "SOFA cardiovascular: se MAP < 70 mesmo com vasopressor,
   score = 3 ou 4 dependendo da dose").
2. **Visibilidade condicional de campos:** mostrar/esconder campos com base em respostas anteriores
   (ex.: "exsudato" só aparece se tipo de secreção ≠ "ausente"; "estágio LPP" só aparece se
   tipo_lpp = "nova_lesao").
3. **_Scoring_ automático server-side:** SOFA, Glasgow, RASS e CAM-ICU são computados server-side
   (o cliente envia os componentes, o servidor retorna o score). O motor atual não tem contrato
   para essa computação — o form engine é puramente client-side.
4. **Versionamento de formulário:** formulários clínicos evoluem (ex.: SOFA teve ajustes em 1996,
   2001, 2016; CAM-ICU tem variações CAM-ICU-7 para severidade). O motor atual não versiona o
   `FormConfig` — uma mudança no schema invalida formulários históricos.
5. **Validação server-side congruente:** a validação Zod client-side e a validação server-side
   (Python/Pydantic/FHIR) precisam ser congruentes — um formulário validado no cliente deve ser
   aceito pelo servidor sem surpresas. O motor atual é 100% client-side; não há schema compartilhado.
6. **Offline capability:** em UTIs, conectividade pode ser intermitente (cobertura WiFi instável,
   áreas blindadas). O motor atual assume conexão sempre disponível.
7. **Submissão parcial / save draft:** formulários clínicos podem ser longos (ex.: avaliação de
   admissão com 24+ campos). O profissional pode precisar salvar rascunho e completar depois.
8. **Duplicação de formulários entre papéis:** o legado tem `dataFormEnfermagem` e
   `dataFormNutricionista` com o mesmo formulário de LPP duplicado verbatim
   (RULE-FORMULARIOS-CLINICOS-002). O novo motor deve suportar **composição de formulários** —
   um formulário base compartilhado entre papéis, com extensões específicas.

### Decision Drivers

- **Versionamento de formulários clínicos:** escalas clínicas evoluem (ex.: SOFA, Glasgow). O
  sistema deve preservar a integridade de formulários históricos enquanto permite a evolução do
  schema. Um formulário submetido com `SOFA v1996` deve permanecer legível e auditável mesmo
  quando o schema atual é `SOFA v2016`.
- **Offline capability:** a UTI é um ambiente de missão crítica onde conectividade não é garantida.
  O profissional deve poder preencher e submeter formulários offline, com sincronização quando a
  conectividade for restaurada.
- **Validação cliente-servidor congruente:** um formulário validado pelo Zod no cliente deve ser
  aceito pelo Pydantic/FHIR no servidor. Divergência de validação gera erros de submissão que
  degradam a confiança do profissional no sistema.
- **Visibilidade condicional dinâmica:** campos que dependem de respostas anteriores (show/hide,
  enable/disable, required/optional condicional) são comuns em formulários clínicos. O legado
  implementava isso com três mecanismos independentes e inconsistentes (ADR-0015 §Assessment).
- **Composição e reuso:** o mesmo formulário clínico (ex.: LPP/NPUAP) é usado por múltiplos papéis
  (enfermagem, nutrição). O sistema deve suportar composição — um formulário base + extensões —
  para eliminar a duplicação de schema que o legado exibia.
- **Latência de renderização:** formulários clínicos são usados à beira-leito, frequentemente em
  tablets com hardware limitado. A renderização do motor deve ser rápida (<200ms FCP para um
  formulário típico de 15-20 campos).
- **Auditabilidade do form config:** toda alteração de `FormConfig` deve ser versionada e
  rastreável — consistente com INV-3 (cada alerta/evento carimba `definition_version` do schema
  que o gerou).

Três abordagens foram consideradas:

### Opção 1: Client-side rendering com definições TypeScript (arquitetura atual)

O `FormConfig` é definido como objetos TypeScript no código-fonte do frontend (`lib/form-engine/types.ts`).
O motor renderiza os formulários 100% no cliente. A validação é Zod, gerada dinamicamente a partir
do config. O servidor recebe os dados submetidos e valida novamente com Pydantic — com schemas
mantidos manualmente sincronizados (ou duplicados).

**Prós:**
- Simplicidade: o motor já existe e funciona (`lib/form-engine/`). As 49 regras podem ser
  implementadas estendendo os tipos existentes.
- Performance: renderização puramente client-side, sem fetch de schema — <50ms FCP.
- Offline com Service Worker: o formulário é renderizado a partir do bundle JS local; offline
  capability pode ser adicionada com cache de `FormConfig` + Service Worker para submissão diferida.
- Independência: o time de frontend pode iterar rapidamente em formulários sem deploy do backend.

**Contras:**
- **Validação duplicada e divergente:** Zod (TS) e Pydantic (Python) são mantidos manualmente —
  risco alto de divergência (ex.: o cliente aceita `rass: number`, o servidor espera `rass: string`
  — exatamente o bug RULE-EVOLUCOES-003).
- **Versionamento frágil:** o `FormConfig` é código TypeScript versionado no Git — mas a
  `definition_version` não é parte do schema, é um processo manual. Nada impede que uma alteração
  de schema quebre formulários históricos.
- **Composição limitada:** reuso de formulários entre papéis exige duplicação de config (como o
  legado fazia com `dataFormEnfermagem` e `dataFormNutricionista`) ou patterns frágeis de
  herança de objetos JS.
- **Scoring server-side requer contrato explícito:** o motor client-side não sabe que SOFA é
  computado server-side — o cliente envia os componentes e espera o score na resposta. Esse
  contrato é implícito e frágil (mudar um campo no `FormConfig` pode quebrar a computação
  server-side silenciosamente).
- **Validação cross-field não suportada:** o `buildZodSchema()` opera campo a campo — regras como
  "se RASS = -5, CAM-ICU não se aplica" exigiriam `.refine()` ou `.superRefine()` manual fora do
  motor, quebrando a geração dinâmica.

### Opção 2: Server-driven forms com JSON Schema via API

O backend é o source of truth do `FormConfig`. Uma API (`GET /api/v1/clinical-forms/{form_type}/schema`)
retorna o schema como JSON Schema (ou OpenAPI). O frontend é um **renderizador genérico** que
consome JSON Schema e renderiza campos dinamicamente — sem conhecimento prévio de formulários
específicos. A validação é server-side (Pydantic → JSON Schema); o cliente valida contra o mesmo
schema (ex.: AJV para JSON Schema no browser).

**Prós:**
- **Single source of truth:** o schema vive no backend e é servido ao cliente sob demanda. Não há
  duplicação — a validação cliente e servidor consomem o mesmo JSON Schema.
- **Versionamento nativo:** cada formulário tem um `definition_version` no backend; a API serve o
  schema correto para cada versão. Formulários históricos são renderizados com o schema da época.
- **Composição server-side:** formulários base + extensões são resolvidos no backend (ex.:
  `GET .../lpp/schema?roles=enfermagem,nutricao` retorna o schema unificado). Sem duplicação
  client-side.
- **Scoring integrado:** o schema inclui metadados de scoring (ex.: `"x-scoring": "sofa"`); o
  cliente sabe que os campos compõem um score server-side e pode exibir o resultado na resposta.
- **Hot-reload de formulários:** alterações de schema no backend são refletidas imediatamente no
  cliente, sem deploy de frontend — útil para correções rápidas de formulários clínicos.
- **Validação cross-field:** JSON Schema suporta `if/then/else`, `allOf`, `anyOf`, `not` —
  expressividade nativa para regras condicionais.

**Contras:**
- **Dependência de rede para renderização:** o formulário não renderiza sem fetch do schema —
  quebra offline capability (mitigável com cache de schema, mas adiciona complexidade de
  invalidação de cache e resolução de conflitos).
- **Latência de first paint:** fetch do schema (~50-200ms) + parse JSON Schema + renderização
  — FCP pode ser 2-5× maior que a Opção 1 para formulários complexos.
- **Complexidade do JSON Schema para formulários ricos:** expressar máscaras (`mask`), hints,
  placeholders PT-BR, e opções de select com labels i18n em JSON Schema puro é verboso e requer
  vocabulário de extensão (propriedades `x-*` customizadas).
- **Casal de dependência backend:** o time de frontend não pode iterar em formulários sem deploy
  ou mock do backend. Para um time integrado (clinical-engineering team), isso pode ser um gargalo.
- **O legado era 100% client-side em seus 14 configs:** migrar para server-driven exigiria
  reescrever todos os schemas no backend — um esforço de migração significativo.

### Opção 3: Híbrido — client-side rendering + server-side validation com schema compartilhado (recomendado)

O `FormConfig` é definido como TypeScript no frontend (preservando a agilidade de iteração), mas
é **compilado/exportado** para um schema canônico (JSON Schema ou Zod schema compartilhado) que o
backend consome para validação. O fluxo é:

1. **Authoring:** o `FormConfig` é escrito em TypeScript no monorepo (como hoje).
2. **Build-time:** um script de compilação gera um JSON Schema + um schema Pydantic a partir do
   `FormConfig` TypeScript (usando `zod-to-json-schema` + `datamodel-code-generator` ou similar).
   Ambos são commitados e versionados.
3. **Runtime client-side:** o motor renderiza a partir do `FormConfig` TypeScript (zero fetch,
   performance máxima, offline-ready). Validação: Zod (gerado pelo `buildZodSchema()`).
4. **Runtime server-side:** o endpoint de submissão valida com o schema Pydantic gerado no build.
   Se a validação passar, o servidor computa scores (SOFA, Glasgow, etc.) e retorna o resultado.
5. **Versionamento:** cada `FormConfig` tem um `definition_version` (ex.: `"sofa-v2016.1"`). O
   build gera artefatos versionados. Formulários históricos referenciam a versão do schema com
   que foram submetidos; o servidor armazena schemas históricos para validação de integridade e
   renderização de visualização histórica.
6. **Offline:** o `FormConfig` TypeScript é parte do bundle JS (cacheável por Service Worker).
   Submissões offline são enfileiradas no IndexedDB e sincronizadas quando online — com validação
   server-side no momento da sincronização (rejeitando submissões inválidas com feedback ao
   profissional).

**Prós:**
- **Performance client-side preservada:** renderização é instantânea (TypeScript no bundle), sem
  fetch de schema. FCP <50ms para formulários típicos.
- **Validação congruente por construção:** o schema Pydantic server-side é gerado do mesmo
  `FormConfig` TypeScript — divergência é impossível (quebraria o build, não o runtime).
- **Versionamento estruturado:** `definition_version` como cidadão de primeira classe no schema;
  schemas históricos são preservados e referenciáveis. Consistente com INV-3.
- **Offline-first:** o formulário carrega do bundle local; submissão é enfileirada e validada
  server-side na sincronização. O profissional nunca vê "sem conexão — formulário indisponível".
- **Agilidade de iteração:** o time de frontend edita TypeScript (como hoje); o backend recebe
  o schema Pydantic gerado automaticamente. Sem dependência circular.
- **Composição resolvida no build:** formulários base + extensões são resolvidos no build
  (TypeScript `spread`/`merge`), gerando um `FormConfig` composto que é compilado para ambos
  os lados. Sem duplicação de schema.
- **Validação cross-field:** o `buildZodSchema()` pode ser estendido para gerar `.refine()` a
  partir de uma DSL declarativa no `FormConfig` (ex.: `crossFieldRules: [{ when: { field: 'rass', op: 'eq', value: -5 }, then: { hide: ['cam_icu_field_1'] } }]`).
- **Scoring server-side explícito:** o `FormConfig` inclui metadados de scoring
  (`scoring: { type: 'sofa', version: '2016' }`); o cliente sabe quais campos compõem o score
  e exibe o resultado retornado pelo servidor — contrato explícito e verificável.

**Contras:**
- **Build pipeline adicional:** o script de compilação TypeScript → JSON Schema + Pydantic é
  infraestrutura customizada que precisa ser construída e mantida.
- **Complexidade de setup:** o desenvolvedor frontend precisa rodar o build de schema para que o
  backend receba a versão atualizada — adiciona um passo ao workflow (mitigável com pre-commit
  hook e CI).
- **Sincronização offline com conflito:** se o profissional submeter offline com uma versão
  antiga do schema (ex.: o formulário foi atualizado enquanto ele estava offline), o servidor
  rejeita e solicita re-preenchimento — UX de conflito que precisa ser tratada.
- **A DSL de validação cross-field é um mini-language:** adicionar `.refine()` condicional ao
  `buildZodSchema()` requer uma DSL declarativa no `FormConfig` — design não trivial e com
  risco de sub-especificação (não cobrir todos os casos clínicos).
- **Manutenção de schemas históricos:** armazenar e versionar schemas históricos no backend
  adiciona complexidade de storage e migração.

## Decisão

**Opção 3 — Híbrido: client-side rendering com schema compartilhado build-time e validação
server-side congruente**, com as seguintes características:

1. **`FormConfig` TypeScript como source of truth de authoring.** O time clínico-frontend define
   formulários como objetos `FormConfig` no monorepo (`frontend-v2/lib/form-engine/configs/` —
   ex.: `rass.config.ts`, `cam-icu.config.ts`, `sofa.config.ts`). O motor renderiza diretamente
   desses objetos (zero fetch, performance máxima, offline-ready).

2. **Build-time: geração de schema canônico.** Um script `generate-form-schemas` (executado no
   `pre-commit` e no CI) compila cada `FormConfig` TypeScript para:
   - **JSON Schema** (`frontend-v2/lib/form-engine/generated/{form_type}-v{version}.schema.json`) —
     para documentação, validação cross-platform e consumo por ferramentas externas.
   - **Pydantic model** (`src/intensicare/schemas/clinical_forms/{form_type}_v{version}.py`) —
     para validação server-side nos endpoints de submissão (`POST /api/v1/patients/{mpi_id}/clinical-forms`).
   
   Ambos os artefatos são commitados e versionados. O build quebra se a geração falhar (ex.:
   tipo TypeScript não mapeável para Pydantic) — a congruência é garantida por construção.

3. **`definition_version` como cidadão de primeira classe.** Todo `FormConfig` carrega uma
   `definition_version` semântica (ex.: `"rass-v1.0"`, `"sofa-v2016.2"`, `"cam-icu-v1.1"`).
   Esta versão é:
   - Embutida no `FormConfig` TypeScript.
   - Propagada para os artefatos gerados (JSON Schema e Pydantic).
   - Enviada pelo cliente no momento da submissão.
   - Armazenada junto ao registro do formulário no banco.
   - Usada pelo servidor para selecionar o schema de validação correto (schemas históricos são
     preservados; submissões com versão desconhecida são rejeitadas).
   
   Consistente com INV-3 (todo alerta/evento carimba `definition_version`).

4. **Validação congruente cliente-servidor.** O Zod schema client-side e o Pydantic model
   server-side são gerados da mesma fonte (`FormConfig` TypeScript). É **impossível** que o
   cliente aceite um valor que o servidor rejeite (ou vice-versa) por divergência de schema —
   qualquer incompatibilidade de tipo quebraria o build.

5. **Extensão do motor com validação cross-field.** O `FormConfig` é estendido com uma DSL
   declarativa para regras condicionais:
   
   ```typescript
   interface CrossFieldRule {
     when: { field: string; op: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in'; value: any };
     then: {
       hide?: string[];        // campos a esconder
       show?: string[];        // campos a mostrar
       require?: string[];     // campos a tornar obrigatórios
       optional?: string[];    // campos a tornar opcionais
       setValue?: { field: string; value: any }[];  // auto-preencher
     };
   }
   ```
   
   O `buildZodSchema()` é estendido para gerar `.refine()` e `.superRefine()` a partir dessas
   regras. Os renderers de campo consomem o estado das regras para show/hide/enable/disable.
   Isso substitui os três mecanismos independentes do legado (nullify switch, `checavel`
   display-toggle, permission-driven disabling) por um único rule engine declarativo,
   consistente com a recomendação do ADR-0015.

6. **Offline-first com sincronização diferida.**
   - O `FormConfig` TypeScript é parte do bundle JS, cacheado por Service Worker.
   - O formulário renderiza e valida 100% offline (Zod client-side).
   - A submissão é enfileirada em IndexedDB (`offline-submissions` store).
   - Quando a conectividade é restaurada, o Service Worker sincroniza as submissões via
     Background Sync API.
   - O servidor valida cada submissão com o Pydantic model correspondente à `definition_version`
     enviada.
   - Se a validação passar: submissão aceita, confirmação enviada ao cliente.
   - Se a validação falhar (ex.: schema version mismatch — o formulário foi atualizado enquanto
     offline): o servidor rejeita com o schema atual; o cliente renderiza o formulário atualizado
     com os dados preenchidos preservados (via `draftState` no IndexedDB) para o profissional
     revisar e re-submeter.

7. **Composição de formulários (reuso entre papéis).** Um formulário base pode ser composto com
   extensões específicas de papel:
   
   ```typescript
   // lib/form-engine/configs/lpp.base.config.ts
   export const lppBaseConfig: FormConfig = { ... };
   
   // lib/form-engine/configs/lpp.enfermagem.config.ts
   export const lppEnfermagemConfig: FormConfig = composeForms(lppBaseConfig, {
     groups: [/* campos específicos da enfermagem */]
   });
   ```
   
   A função `composeForms()` faz deep merge de `FormConfig`, resolvendo conflitos com
   estratégia declarada (`override`, `merge`, `append`). O build gera schemas separados
   para cada composição. Elimina a duplicação de schema entre papéis (ex.: `dataFormEnfermagem`
   e `dataFormNutricionista` com LPP duplicado verbatim — RULE-FORMULARIOS-CLINICOS-002).

8. **Metadados de scoring explícitos no `FormConfig`.**
   
   ```typescript
   interface FormConfig {
     // ... existing fields
     scoring?: {
       type: 'sofa' | 'glasgow' | 'rass' | 'cam_icu' | 'bps' | 'nrs';
       version: string;
       components: string[];  // field names que compõem o score
       serverComputed: boolean;  // true = score é computado server-side
     };
   }
   ```
   
   Quando `scoring.serverComputed === true`, o motor client-side:
   - Exibe os campos componentes normalmente.
   - Após submissão, exibe o score retornado pelo servidor (não calcula client-side).
   - Se offline, submete os componentes e exibe "Score pendente — será calculado na sincronização".
   
   Isso resolve a ambiguidade SOFA (RULE-EVOLUCOES-001/002): o motor sabe que SOFA é
   server-side, exibe o score retornado, e não tenta calcular client-side.

9. **Validação de formulários de scoring com invariantes clínicos.** Além da validação de schema,
   o Pydantic model inclui validadores de domínio para invariantes clínicos:
   - RASS: -5 a +4 (inteiro). Se RASS = -5 (inarousable), CAM-ICU é automaticamente "não
     aplicável" (não deve ser submetido).
   - Glasgow: 3-15 (soma). Sub-escores: ocular 1-4, verbal 1-5, motora 1-6. Se verbal = 1
     (intubado), aceitar valor especial `NT` (não testável) — mas o total é registrado como
     `3-15` ou `NT` com os sub-escores individuais para audit trail.
   - SOFA: cada componente 0-4, total 0-24. Cardiovascular: MAP < 70 mmHg → mínimo score 1;
     se em vasopressor → score ≥ 3 dependendo da dose em mcg/kg/min (convertida pelo serviço
     de conversão de unidades — ADR-0022 §CANON_PINS).
   - CAM-ICU: Feature 1 (alteração aguda/flutuante) e Feature 2 (inatenção) devem ambos ser
     positivos para CAM-ICU positivo — regra de scoring, não apenas validação de tipo.
   
   Essas invariantes são implementadas como `@validator` ou `@root_validator` no Pydantic model
   gerado, com mensagens de erro em PT-BR.

**Gatilho de reavaliação:** Se o build pipeline de geração de schema (TypeScript → JSON Schema +
Pydantic) se mostrar frágil ou de alta manutenção (>5 horas/mês de engenharia para manter),
reavaliar a Opção 2 (server-driven forms com JSON Schema como single source of truth no backend,
abolindo a geração build-time). Inversamente, se a necessidade de iteração rápida em formulários
pelo time de frontend for alta (>2 alterações de schema por semana), manter a Opção 3 com
investimento em tooling de build.

## Consequencias

**Positivas:**

- **Validação congruente por construção:** Zod (cliente) e Pydantic (servidor) gerados da mesma
  fonte (`FormConfig` TypeScript). O bug RULE-EVOLUCOES-003 (RASS `number` vs `string`) é
  estruturalmente impossível no novo sistema — o tipo é definido uma vez e propagado para ambos
  os lados.
- **Performance client-side preservada:** renderização instantânea a partir do bundle TypeScript,
  sem fetch de schema. FCP <50ms para formulários típicos de 15-20 campos — adequado para
  tablets de beira-leito.
- **Offline-first:** o formulário está sempre disponível (parte do bundle JS). Submissão diferida
  via Service Worker + IndexedDB. O profissional nunca vê "sem conexão".
- **Versionamento estruturado (INV-3):** `definition_version` no `FormConfig`, propagado para
  artefatos, armazenado com cada submissão. Schemas históricos preservados — auditoria e
  visualização de formulários antigos são nativas.
- **Regras condicionais unificadas:** a DSL `CrossFieldRule` substitui os três mecanismos
  independentes do legado (nullify switch, `checavel` toggle, permission-driven disabling) —
  consistente com a recomendação do ADR-0015.
- **Composição elimina duplicação:** o mesmo formulário base (ex.: LPP/NPUAP) é composto com
  extensões específicas de papel, eliminando a duplicação verbatim de schema que o legado exibia
  (RULE-FORMULARIOS-CLINICOS-002).
- **Scoring server-side com contrato explícito:** metadados de scoring no `FormConfig` informam
  o cliente que o score é computado server-side — sem ambiguidade.
- **Invariantes clínicos server-side:** validação de domínio (RASS + CAM-ICU coerência, Glasgow
  sub-escores, SOFA cardiovascular) protege contra submissões clinicamente inconsistentes.
- **Agilidade de iteração:** o time de frontend edita TypeScript; o backend recebe Pydantic
  gerado automaticamente. Sem dependência circular ou gargalo de deploy.

**Negativas (aceitas):**

- **Build pipeline adicional:** o script `generate-form-schemas` (TypeScript → JSON Schema +
  Pydantic) é infraestrutura customizada com custo inicial de implementação e manutenção contínua.
- **Complexidade de tooling:** o desenvolvedor frontend precisa entender o pipeline de build
  (`pre-commit` hook, CI check) — onboarding mais longo.
- **A DSL de validação cross-field é um mini-language:** o design da DSL (`CrossFieldRule`) precisa
  cobrir os casos clínicos das 49 regras sem se tornar Turing-completo — equilíbrio entre
  expressividade e simplicidade que requer iteração com o time clínico.
- **Conflito de versão offline:** se o profissional submeter offline com schema desatualizado, o
  servidor rejeita e solicita re-preenchimento — UX de conflito que precisa de tratamento cuidadoso
  (preservação de draft, notificação clara).
- **Manutenção de schemas históricos:** armazenar Pydantic models históricos no backend requer
  disciplina de versionamento e storage — complexidade adicional vs um sistema que só aceita a
  versão atual.
- **Gap de migração:** as 49 regras legadas estão espalhadas entre backend Django (`models/choices`)
  e frontend React (`dataForm*` configs). Migrar para o `FormConfig` TypeScript + Pydantic exige
  re-authoring de ~15 formulários — esforço de migração significativo (ainda que mecânico).

## Supersedes

— (implementa a recomendação do ADR-0015 — "modernize the engine with a strongly-typed config
schema and a unified visibility/nullability rule engine". O ADR-0015 recomendava a modernização;
este ADR decide o **como**: schema compartilhado build-time, DSL `CrossFieldRule`, composição
de formulários, e offline-first com sincronização diferida. Referencia ADR-0022 para o serviço
de conversão de unidades usado nas invariantes SOFA cardiovascular. Referencia ADR-0028 — o
form engine cobre formulários de scoring (RASS, CAM-ICU, Glasgow, SOFA); o ADR-028 estende o
motor com o renderer `rich-text` para evoluções narrativas.)
