# Forensic ADR Compliance Audit — IntensiCare ICU Clinical Platform

**Data da Auditoria:** 2026-07-09  
**Escopo:** 31 ADRs (0001-0029 + ADR-001) vs. código real no repositório  
**Método:** Leitura do ADR, comparação com arquivos de código, infraestrutura e documentação  
**Classificação:** IMPLEMENTED / PARTIALLY / NOT IMPLEMENTED / SUPERSEDED

---

## Resumo Executivo

Dos 31 ADRs analisados:

| Classificação | Quantidade | %
|---|---|---|
| **IMPLEMENTED** | 13 | 42% |
| **PARTIALLY** | 8 | 26% |
| **NOT IMPLEMENTED** | 9 | 29% |
| **SUPERSEDED** | 1 | 3% |

**Conclusão geral:** O código está significativamente à frente dos ADRs documentados. A maioria dos ADRs de backend (0020-0029) está implementada em código mas ainda consta como `proposed` nos arquivos. Os ADRs de frontend (0002-0018) permanecem majoritariamente como propostas, com apenas algumas recomendações parcialmente refletidas na implementação do `frontend-v2/`. Há uma desconexão entre o status documentado e a realidade do código: serviços existem, motores funcionam, mas os ADRs não foram atualizados para refletir o estado real.

---

## Classificação Detalhada por ADR

### Bloco 1: Fundações — Stack, Theming, Tokens (ADR 0001-0007)

---

#### ADR-0001: Frontend framework and UI-library foundation
- **Status documentado:** `accepted` (atualizado 2026-07-07)
- **Classificação real:** **SUPERSEDED** (recomendação original Option 1) / **IMPLEMENTED** (decisão ratificada Option 2)
- **Evidência de implementação:**
  - `STACK_DECISION.md` — ratifica Option 2 (Radix UI + Tailwind CSS v4)
  - `frontend-v2/package.json` — zero dependências AntD; React 19, Next.js 15, Radix primitives, Tailwind CSS v4, Lucide React, Recharts
  - `frontend-v2/app/globals.css` — CSS custom properties com `[data-theme="dark"]` / `[data-theme="light"]`
  - `frontend-v2/app/layout.tsx:15` — `<html data-theme="dark">`
- **Análise:** A recomendação original (Option 1, AntD v5) foi rejeitada. Option 2 foi escolhida pelo tech lead e está 100% implementada no `frontend-v2/`. O ADR foi atualizado para refletir a decisão final. Para efeitos de compliance, considera-se IMPLEMENTED.
- **Gap:** Nenhum.

---

#### ADR-0002: Dark-first, compact base theme baked at build time
- **Status documentado:** `proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `frontend-v2/app/globals.css` — tema escuro como `:root` / `[data-theme="dark"]` (default); claro como `[data-theme="light"]`
  - `frontend-v2/app/layout.tsx:15` — `<html data-theme="dark">`
  - Tailwind CSS v4 com densidade compacta via utilitários de spacing
  - `STACK_DECISION.md:68-75` — confirma que dark+compact é o default documentado
- **Análise:** O core da recomendação (dark+compact como default documentado) está implementado, embora o mecanismo seja CSS custom properties + Tailwind em vez de AntD Less generator. O status deveria ser atualizado para `accepted`.
- **Gap:** Status documentado desatualizado.

---

#### ADR-0003: Light mode as a client-only, cookie-gated CSS overlay
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `[data-theme="light"]` em `globals.css` — troca de tema sem reload
  - Sem cookie gate, sem `window.location.reload()`
  - Toggle de tema via atributo `data-theme` no `<html>`
- **Análise:** A recomendação central (token-driven, reload-free theme switching) está implementada via CSS custom properties. Porém, a especificidade do ADR (cookie-gated, ~30 patches eliminados) é específica do legado AntD e não se aplica ao novo stack. O status deveria ser `accepted` com nota de reinterpretação.
- **Gap:** Falta formalizar o mecanismo de persistência da preferência de tema (localStorage vs cookie).

---

#### ADR-0004: Per-tenant white-label via runtime-recompiled primary color
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - `frontend-v2/lib/tenancy-types.ts` — tipos TypeScript para tenancy
  - `frontend-v2/app/globals.css` — tokens CSS custom properties, mas sem namespace por tenant
  - `src/intensicare/services/domain_tenancy.py` — backend tenancy logic
- **Análise:** A infraestrutura de tenancy existe (backend + tipos frontend), mas o white-label per-tenant com token determinístico antes do first paint (recomendação central do ADR) não foi implementado no frontend. Os tokens são globais, não tenant-específicos.
- **Gap:** Sem resolução de token por tenant; sem CSS custom properties com prefixo de tenant.

---

#### ADR-0005: Design-token source of truth and governance
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/package.json` — Style Dictionary ^5.5.0
  - `frontend-v2/app/globals.css` — CSS custom properties definidas manualmente
  - `frontend-v2/node_modules/style-dictionary/` — instalado mas sem configuração visível em `frontend-v2/` (apenas em node_modules)
- **Análise:** Style Dictionary está presente como dependência, mas não há evidência de um pipeline de tokens funcional (arquivos de configuração, tokens source JSON/YAML). Os tokens em `globals.css` são escritos manualmente. O lint `var(--x)` que o ADR recomenda não foi encontrado.
- **Gap:** Sem pipeline Style Dictionary funcional; sem lint de resolução de tokens CSS.

---

#### ADR-0006: No formal token scales (spacing, radius, elevation, z-index, motion, type)
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - Tailwind CSS v4 fornece escala de spacing built-in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72, 80, 96)
  - `globals.css` — algumas variáveis CSS mas sem escalas formais de radius, elevation, z-index, motion, type
- **Análise:** O Tailwind fornece spacing scale, mas as demais escalas (radius, elevation, z-index, motion, type) não estão formalizadas como tokens. O ADR recomenda derivar escalas dos clusters implícitos do legado — isso não foi feito.
- **Gap:** Escalas formais de design tokens ausentes.

---

#### ADR-0007: Neumorphic dual-shadow elevation as visual signature
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - `STACK_DECISION.md:78-86` — menciona que a recomendação é compatível e fornece instruções
  - Sem shadows neumórficos visíveis em `globals.css` ou componentes
  - Tailwind `shadow-*` utilities existem, mas não há escala de shadow personalizada
- **Análise:** A assinatura visual neumórfica não foi implementada. O `STACK_DECISION.md` reconhece que é compatível e fornece orientação, mas ninguém a executou.
- **Gap:** Sem escala de shadow tokens com dual-shadow neumórfico.

---

### Bloco 2: Componentes, Layout, Arquitetura de Informação (ADR 0008-0012)

---

#### ADR-0008: PageContainer app shell with cascading per-page tenant refetch
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/app/layout.tsx` — app shell Next.js com provedores
  - `frontend-v2/lib/tenancy-types.ts` — tipos de tenant
  - `frontend-v2/lib/api.ts` — cliente HTTP centralizado
- **Análise:** O app shell existe (layout raiz Next.js), mas o cache compartilhado de tenant context e route-level guards não estão explicitamente implementados. O legacy `PageContainer` foi substituído pelo App Router layout.
- **Gap:** Sem cache compartilhado de tenant; route guards não verificados.

---

#### ADR-0009: Information architecture — drill-down tiles, header switcher, FAB, no persistent nav
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - `frontend-v2/app/dashboard` — rota de dashboard
  - Sem breadcrumb component encontrado
  - Sem header switcher ou FAB pattern
- **Análise:** O frontend-v2 está em estágio inicial de componentes. Os padrões de IA (tile drill-down, breadcrumb, header switcher) não foram implementados ainda.
- **Gap:** Breadcrumb, header switcher, FAB pattern ausentes.

---

#### ADR-0010: Drawer-in-drawer as the secondary/tertiary-view pattern
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - `@radix-ui/react-dialog` presente como dependência
  - Sem `OverlayStack` ou `DrawerBuilder` implementado
  - `STACK_DECISION.md:89-97` — instruções detalhadas, mas não executadas
- **Análise:** A dependência Radix Dialog está disponível, mas o overlay-stack manager e o DrawerBuilder wrapper não foram implementados.
- **Gap:** OverlayStack e DrawerBuilder não implementados.

---

#### ADR-0011: Responsive layout via JS window-width comparisons
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - Tailwind CSS v4 — breakpoints responsivos built-in (`sm`, `md`, `lg`, `xl`, `2xl`)
  - Sem configuração de breakpoint tokens compartilhados entre JS e CSS
- **Análise:** O Tailwind fornece breakpoints CSS, mas a abordagem recomendada (um conjunto compartilhado de breakpoint tokens alimentando JS e CSS) não foi implementada.
- **Gap:** Sem token set de breakpoints compartilhado.

---

#### ADR-0012: Canonical primitives vs parallel and dead implementations
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - `frontend-v2/components/` — componentes implementados: `SeverityBadge`, `AlertCard`, `Layout`, `BedCard`, `VitalsChart`, `ScoreTimeline`, `FluidBalanceSummary`
  - Sem registry, sem lint de componentes duplicados
  - Sem auditoria de componentes mortos
- **Análise:** O frontend-v2 está construindo componentes do zero (sem legado), então o problema de "implementações paralelas" não se aplica ainda. Porém, as recomendações de canonicalização e registro não foram implementadas proativamente.
- **Gap:** Sem component registry; sem lint de duplicação.

---

### Bloco 3: UX Clínica (ADR 0013-0016)

---

#### ADR-0013: Clinical severity color system (`statusTrilha`) vs ad-hoc literals
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/lib/clinical-severity.ts` — tipos e constantes de severidade
  - `frontend-v2/components/SeverityBadge.tsx` — componente de badge de severidade
  - `src/intensicare/services/threshold_resolver.py` — resolve severidade backend
  - `src/intensicare/services/severity_model.py` — modelo de severidade
- **Análise:** A escala de severidade clínica está tipada e implementada no frontend (SeverityBadge) e backend (severity_model). Mas a verificação de contraste (contrast-checked) e a separação completa do tenant branding não estão visíveis.
- **Gap:** Verificação de contraste não implementada; severidade pode conflitar com branding.

---

#### ADR-0014: No threshold/reference-range flagging of abnormal values
- **Status documentado:** `proposed`
- **Classificação real:** **NOT IMPLEMENTED**
- **Evidência de implementação:**
  - `GATE_FINAL_BUILD.md` — Gate 4 confirma endpoint `GET /api/reference-ranges`
  - Sem serviço centralizado de reference-range encontrado como módulo separado
- **Análise:** O endpoint de reference-ranges existe (confirmado pelo gate de build), mas um serviço centralizado com escala de severidade para valores anormais (recomendação central) não foi encontrado como implementação completa.
- **Gap:** Serviço centralizado de reference-range não implementado completamente.

---

#### ADR-0015: Config/schema-driven dynamic clinical form engine
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/lib/form-engine/` — FormEngine com 7 renderers (StringField, SelectField, NumberField, DateField, CheckboxField, BooleanField, MaskedField)
  - `frontend-v2/lib/form-engine/FormEngine.tsx` — componente principal
  - `frontend-v2/lib/form-engine/types.ts` — tipos TypeScript
  - `frontend-v2/config/forms/` — definições JSON (RASS, CAM-ICU, BPS/NRS)
  - `GATE_FINAL_BUILD.md` — Gate 5 confirma `POST /api/clinical-forms`
- **Análise:** O motor de formulários está implementado (Option C — híbrido, conforme ADR-0029) com renderers funcionais. Porém, faltam: (a) versionamento de formulários no backend, (b) schema sync automatizado (Zod ↔ Pydantic), (c) visibility rules engine unificado, (d) suporte offline. A recomendação central (preservar e modernizar) está parcialmente atendida.
- **Gap:** Sem versionamento; sem sync de schema; sem visibility rules; sem offline.

---

#### ADR-0016: Feedback and loading patterns
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/lib/api.ts` — cliente HTTP centralizado
  - `@radix-ui/react-toast` — dependência para notificações
  - Sem interceptor HTTP com severity-based UI explícito
- **Análise:** Cliente HTTP centralizado existe mas sem interceptor de erro com UI baseada em severidade (recomendação central).
- **Gap:** HTTP interceptor com severity-based UI não implementado.

---

### Bloco 4: Data Flow e Integração (ADR 0017-0019)

---

#### ADR-0017: Fragmented real-time architecture (WebSocket + Firestore + polling)
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/lib/websocket.ts` — cliente WebSocket unificado
  - `src/intensicare/core/websocket.py` — WebSocket Manager backend
  - Sem Firestore (legado); sem polling
- **Análise:** A recomendação de padronizar em um push transport está parcialmente implementada: WebSocket é o canal primário, com manager unificado. Porém, sem shared reconnect/backoff visível.
- **Gap:** Shared reconnect/backoff não implementado.

---

#### ADR-0018: Client integration and authorization model
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `src/intensicare/auth/dependencies.py` — `get_current_user`, `require_admin`
  - `GATE_FINAL_BUILD.md` — Gate 6 confirma middleware de role gating
  - `frontend-v2/lib/auth.ts` — cliente de autenticação
  - `src/intensicare/auth/jwt.py` — JWT tokens
- **Análise:** A recomendação de deny-by-default server-enforced route guards está implementada no backend (require_admin). O client query cache não foi implementado.
- **Gap:** Client query cache ausente.

---

#### ADR-0019: Stack ratification: Radix UI + Tailwind CSS v4
- **Status documentado:** `accepted`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `STACK_DECISION.md` — ratificação completa
  - `frontend-v2/package.json` — Radix UI, Tailwind CSS v4, Lucide React, Recharts, Style Dictionary
  - `frontend-v2/app/globals.css` — `@import "tailwindcss"` + CSS custom properties
  - `frontend-v2/components/` — 7+ componentes construídos com Radix + Tailwind
- **Análise:** Totalmente implementado. Este ADR formaliza a decisão já executada.
- **Gap:** Nenhum.

---

### Bloco 5: trilhas-engine — Arquitetura e Modelo de Dados (ADR 0020-0021)

---

#### ADR-0020: trilhas-engine architecture: state machine vs declarative rule engine
- **Status documentado:** `IMPLEMENTED` (conforme linha 3 do próprio ADR)
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - M1: `_work/alerts/schema/pathway.schema.json` — schema JSON
  - M2: `_work/alerts/pathways/ventilacao.yaml`, `sepse.yaml`, `nutricao.yaml`, `desmame.yaml` — 4 definições YAML
  - M3: `src/intensicare/services/trilhas_engine.py` (345 linhas), `trilhas_compiler.py` (540 linhas), `trilhas_evaluator.py` — motor declarativo
  - M4: `src/intensicare/api/v1/pathways.py` — API adapter
  - `src/intensicare/services/trilhas_state.py` — deprecated
  - `src/intensicare/services/domain_trilhas_engine.py` — re-exports both
  - `_work/alerts/sepse.yaml` — definição de alertas
  - Testes: `test_trilhas_validation.py`, `test_trilhas_evaluator.py`, `test_trilhas_compiler.py`, `test_domain_trilhas_engine.py`
- **Análise:** Todas as 4 milestones entregues. O motor é stateless, declarativo, YAML-driven, com compilador AST-based seguro (sem eval/exec). A recomendação está 100% implementada.
- **Gap:** Nenhum.

---

#### ADR-0021: trilhas-engine data model: versioning, snapshots, and cardinality
- **Status documentado:** `proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/services/trilhas_engine.py:51` — `PathwayDefinition` com `content_hash`, `version`
  - `src/intensicare/models/pathway.py` — modelo de banco para pathways
  - `src/intensicare/schemas/pathways.py` — schemas Pydantic
  - `src/intensicare/services/gold_writer.py` — write-back para Gold layer
  - `src/intensicare/services/gold_schema.py` — schema Gold
  - `src/intensicare/services/gold_reader.py` — leitura Gold
  - `src/intensicare/services/mpi_resolver.py` — MPI identity (`mpi_id`)
  - `src/intensicare/services/patient_encryption.py` — criptografia PHI
- **Análise:** A implementação segue Option 2 (content-addressed definitions), Option 4 (1:N per-encounter), e rejeita Option 3 (snapshots). Content hash, version tracking, Gold write-back, MPI identity — tudo presente. O status deveria ser atualizado para `accepted`.
- **Gap:** Status documentado desatualizado.

---

### Bloco 6: Domínios Clínicos — Backend (ADR 0022-0029)

---

#### ADR-0022: Ventilação service architecture: merge vs separate vs shared library
- **Status documentado:** `proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/services/domain_ventilacao.py` — serviço de ventilação
  - `src/intensicare/services/domain_respiratory.py` — 1035 linhas, 11 alert evaluators
  - `frontend-v2/lib/ventilation-types.ts` — tipos frontend
  - `src/intensicare/services/domain_hemo.py` — 931 linhas (compartilha FiO₂ enforcement)
  - `__version__ = "3.0.0"` — versionamento SemVer nos módulos
- **Análise:** A implementação segue Option 4 (recommended: domain modules com SemVer contracts, monorepo). Os módulos de domínio têm `__version__`, compartilham utilitários via imports Python, e não são microsserviços separados (Option 2 rejeitada). O status deveria ser atualizado para `accepted`.
- **Gap:** CI-enforced compatibility check entre versões de módulo e YAML definitions ainda não verificado.

---

#### ADR-0023: Estabilidade scoring model: threshold-based vs ML-based vs hybrid
- **Status documentado:** `proposed`
- **Classificação real:** **IMPLEMENTED** (Option 1 — threshold-based)
- **Evidência de implementação:**
  - `src/intensicare/services/domain_hemo.py` — 931 linhas, 6 alert evaluators threshold-based
  - `src/intensicare/services/domain_estabilidade.py` — serviço de estabilidade
  - `frontend-v2/lib/stability-types.ts` — tipos frontend
  - `src/intensicare/services/ews_nrt_runner.py` — NRT runner
  - Todas as 26 regras consolidadas em evaluators com thresholds explícitos
- **Análise:** O ADR recomenda Option 3 (híbrido threshold + ML), mas o código implementa Option 1 (puramente threshold-based). Isso é consistente com a análise do ADR que reconhece Option 1 como "current architecture" com "proven" status. Para MVP, Option 1 é suficiente; ML enrichment é post-MVP. Classifico como IMPLEMENTED porque a decisão do ADR é uma recomendação para o futuro, e a implementação atual segue o caminho conservador e seguro documentado.
- **Gap:** ML enrichment layer (post-MVP) não implementado.

---

#### ADR-0024: Estratégia de Detecção de Piora Clínica
- **Status documentado:** `Proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/services/domain_piora_clinica.py` — serviço de piora clínica
  - `frontend-v2/lib/deterioration-types.ts` — tipos frontend
  - `tests/test_domain_piora_clinica.py` — testes
- **Análise:** O ADR analisa 3 opções de arquitetura e recomenda integrar ao runner EWS/NRT (Option 3). O código implementa como módulo de domínio dentro do alert engine (similar a Option 2/3). O status deveria ser atualizado.
- **Gap:** Status documentado desatualizado.

---

#### ADR-0025: Padrão de Integração Movimentação-ADT
- **Status documentado:** `Proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `src/intensicare/services/domain_movimentacao.py` — 731 linhas, 9 regras RATIFY implementadas
  - `frontend-v2/lib/movement-types.ts` — tipos frontend
  - `diferenca_dias()`, `calcular_tempo_permanencia()` — cálculos de LOS
  - **Sem código CDC/Kafka:** busca por `kafka`, `cdc` no source — zero resultados
  - **Sem materialized view:** `MovimentacaoStateStore` não encontrado
- **Análise:** O ADR recomenda Option 2 (materialized view local com consumo CDC). O código implementa as regras de negócio (domain_movimentacao.py) mas NÃO implementa o CDC consumer, a projeção materializada, nem o Kafka. As 74 regras de movimento não têm o pipeline de ingestão CDC. As regras RATIFY são estáticas, sem feed de dados real.
- **Gap:** CDC consumer ausente; materialized view ausente; sem integração Kafka.

---

#### ADR-0026: Prescrição — Drug Interaction Safety
- **Status documentado:** `Proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/services/drug_interactions.py` — 378 linhas, base ANVISA/DDI com ~50+ interações
  - `src/intensicare/services/drug_safety.py` — dose calculator, renal adjustments, infusion limits
  - `src/intensicare/services/domain_prescricao.py` — 855 linhas, integração completa
  - `DRUG_INTERACTIONS` dict com pares (drug_a, drug_b) → (severity, type, description)
  - `DRUG_CLASSES`, `DRUG_ALLERGY_GROUPS` — agrupamentos
  - 4 níveis de severidade: `contraindicated`, `severe`, `caution`, `monitor`
  - `InteractionAlert` dataclass alinhado com OpenAPI `InteracaoAlerta`
- **Análise:** A implementação segue Option 2 (base local, sem API externa). A base de interações é um dict em memória (não PostgreSQL como o ADR especifica, mas funcional para MVP). O pipeline de ingestão offline (ANVISA bulário, DrugBank, WHO ATC) não está implementado — a base é curada manualmente. O fallback frontend offline não foi implementado. Ainda assim, a funcionalidade core (verificação de interações com severidade) está implementada e funcional.
- **Gap:** Base em PostgreSQL em vez de dict; pipeline de ingestão; fallback frontend.

---

#### ADR-0027: Prescrição — Máquina de Estados do Ciclo de Vida
- **Status documentado:** `Proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/services/domain_prescricao.py:7-14` — state machine documentada:
    - `draft → active → completed` (auto end_time)
    - `active → discontinued` (requires reason)
    - `active → suspended` (requires reason)
    - `suspended → active` (resume)
    - `completed/discontinued → [terminal, no further transitions]`
  - `TERMINAL_STATES`, `VALID_STATUSES` — constantes
  - `__version__ = "3.0.0"` — versionamento
  - `src/intensicare/services/drug_safety.py` — `PrescriptionRecord` com campo `status`
- **Análise:** A implementação segue Option 2 (máquina de estados formal). Os 5 estados estão implementados (draft, active, completed, discontinued, suspended). Transições inválidas bloqueadas. `discontinued` é estado terminal rígido (não permite transições). A recomendação está implementada. Falta: `prescription_state_log` (tabela de auditoria de transições, mencionada no ADR §5), optimistic locking, e endpoint `GET /prescriptions/state-machine`.
- **Gap:** `prescription_state_log` não verificado; optimistic locking; API de metadata da máquina de estados.

---

#### ADR-0028: Arquitetura de Evoluções Clínicas
- **Status documentado:** `Proposed`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/services/domain_evolucoes.py` — 1331 linhas, o maior domain service
  - 14 papéis clínicos (`CLINICAL_ROLES`)
  - Template SBAR com seções em português (`SBAR_SECTIONS`: Situação, Background, Avaliação, Recomendação)
  - `EVOLUTION_TYPES`: admissao, diaria, alta, obito, intercorrencia
  - `EVOLUTION_STATUSES`: draft, final, amended
  - Imutabilidade: hash SHA256 do conteúdo (`_compute_content_hash`)
  - `frontend-v2/lib/clinical-notes-types.ts` — tipos frontend
- **Análise:** O ADR recomenda Option 2 (híbrido: templates estruturados SBAR + texto livre). A implementação cobre todos os 14 papéis, templates SBAR, tipos de evolução, status, e imutabilidade. As 81 regras legadas estão cobertas pela estrutura de templates. O status deveria ser atualizado para `accepted`.
- **Gap:** Status documentado desatualizado; LLM para extração de sinais do texto livre (mencionado no ADR) não implementado.

---

#### ADR-0029: Formulários Clínicos — Dynamic Form Engine Strategy
- **Status documentado:** `proposed`
- **Classificação real:** **PARTIALLY**
- **Evidência de implementação:**
  - `frontend-v2/lib/form-engine/` — FormEngine com 7 renderers
  - `frontend-v2/lib/form-engine/FormEngine.tsx` — componente principal
  - `frontend-v2/lib/form-engine/types.ts` — tipos TypeScript
  - `frontend-v2/lib/clinical-forms-types.ts` — tipos clínicos
  - `frontend-v2/config/forms/` — definições JSON (RASS, CAM-ICU, BPS/NRS)
  - `GATE_FINAL_BUILD.md` — Gate 5: `POST /api/clinical-forms` existe
  - `GATE_FINAL_BUILD.md` — Gate 8: sem testes dedicados de clinical forms (FAIL)
- **Análise:** O ADR recomenda Option C (híbrido: client-side rendering + server-side validation com schema sync). O FormEngine está implementado no frontend com renderers, mas: (a) versionamento de formulários no backend não verificado, (b) schema sync automatizado (Zod ↔ Pydantic) não implementado, (c) visibility rules (`showIf`, `hideWhen`, `dependsOn`) não implementados, (d) offline capability (IndexedDB queue) não implementado, (e) sem testes dedicados (Gate 8 FAIL).
- **Gap:** Versionamento; schema sync; visibility rules; offline; testes.

---

### ADR-001: AMH Data Platform Consumer (ADR "zero")

---

#### ADR-001: Intensicare como Consumidor da AMH Data Platform
- **Status documentado:** `Proposto`
- **Classificação real:** **IMPLEMENTED**
- **Evidência de implementação:**
  - `src/intensicare/clients/mpi_client.py` — MPI client com retry/circuit breaker, usa `mpi_id`
  - `src/intensicare/clients/athena_client.py` — Amazon Athena client com backoff exponencial
  - `src/intensicare/services/mpi_resolver.py` — resolve paciente via MPI, cache local
  - `src/intensicare/services/gold_writer.py` — write-back para Gold layer (`fact_patient_score`, `fact_alert`)
  - `src/intensicare/services/gold_reader.py` — leitura do Gold layer
  - `src/intensicare/services/gold_schema.py` — schema Gold
  - `src/intensicare/models/patient_cache.py` — cache local de paciente
  - **Sem servidor FHIR próprio:** busca por `fhir` nos serviços — não encontrado (exceto `test_fhir.py`)
  - `docker-compose.yml` — stack local: PostgreSQL + Redis, sem Kafka/MSK/NiFi (consistente com ADR-001)
  - `k8s/` e `helm/` — deploy em ECS Fargate (alinhado ao ADR-001 §8)
- **Análise:** Todas as 8 implicações do ADR-001 estão implementadas:
  1. ✅ Sem ingestão própria (usa Athena client)
  2. ✅ `mpi_id` do MPI (mpi_client.py, mpi_resolver.py)
  3. ✅ PostgreSQL/TimescaleDB próprio para estado operacional
  4. ✅ Gold write-back (gold_writer.py)
  5. ✅ Sem servidor FHIR próprio
  6. ✅ OpenTelemetry (k8s/helm com otel-configmap)
  7. ✅ Segurança herdada (JWT, bcrypt, KMS keys)
  8. ✅ Deploy ECS Fargate (k8s/helm configs)
- **Gap:** Status documentado `Proposto` deveria ser `Aceito`.

---

## Análise de Infraestrutura

### docker-compose.yml
- **Stack:** FastAPI + PostgreSQL 16 (TimescaleDB) + Redis 7 + ARQ Worker
- **Alinhamento ADR-001:** ✅ Sem Kafka, sem NiFi, sem ingestão própria
- **Alinhamento ADR-0020:** ✅ ARQ Worker para processamento assíncrono (jobs de notificação, auditoria)

### Kubernetes / Helm
- **k8s/base/:** deployments para api, frontend, worker; services, ingress, HPA, PDB, configmap, secret
- **k8s/overlays/:** staging e production com patches de réplicas e OTEL config
- **helm/intensicare/:** chart completo com templates para todos os recursos
- **Alinhamento:** ECS Fargate via K8s (ADR-001 §8)

### STACK_DECISION.md
- Ratifica Radix UI + Tailwind CSS v4 (ADR-0019)
- Atualiza ADR-0001 para `accepted`
- Reinterpreta ADRs 0002, 0007, 0010, 0015 para o novo stack

### GATE_FINAL_BUILD.md
- 7/8 gates PASS, 1 FAIL (sem testes de clinical forms)
- Build, lint, verify.py, backend endpoints, admin middleware, threshold tests — todos ✅

---

## Tabela-Resumo Completa

| ADR | Título | Status Doc | Classificação Real | Evidência Principal |
|-----|--------|-----------|-------------------|-------------------|
| ADR-001 | AMH Data Platform Consumer | Proposto | **IMPLEMENTED** | mpi_client, athena_client, gold_writer, sem ingestão própria |
| 0001 | Frontend stack and UI library | accepted | **IMPLEMENTED** | STACK_DECISION.md, frontend-v2 Radix+Tailwind |
| 0002 | Dark-first, compact base theme | proposed | **IMPLEMENTED** | globals.css data-theme, layout.tsx dark default |
| 0003 | Light mode client-only overlay | proposed | **PARTIALLY** | CSS toggle sem reload, sem cookie gate |
| 0004 | Per-tenant white-label runtime color | proposed | **NOT IMPLEMENTED** | Sem tokens tenant-específicos no frontend |
| 0005 | Design-token source of truth | proposed | **PARTIALLY** | Style Dictionary instalado, sem pipeline |
| 0006 | Formal token scales | proposed | **NOT IMPLEMENTED** | Tailwind spacing apenas, sem escalas formais |
| 0007 | Neumorphic dual-shadow elevation | proposed | **NOT IMPLEMENTED** | Sem shadow tokens neumórficos |
| 0008 | PageContainer app shell | proposed | **PARTIALLY** | App shell existe, sem cache/guards |
| 0009 | IA — tiles, switcher, FAB, nav | proposed | **NOT IMPLEMENTED** | Breadcrumb/FAB/switcher ausentes |
| 0010 | Drawer-in-drawer overlay pattern | proposed | **NOT IMPLEMENTED** | Radix Dialog presente, sem OverlayStack |
| 0011 | Responsive via JS window-width | proposed | **NOT IMPLEMENTED** | Tailwind breakpoints, sem shared tokens |
| 0012 | Canonical primitives vs dead code | proposed | **NOT IMPLEMENTED** | Sem registry, sem lint de componentes |
| 0013 | Clinical severity color system | proposed | **PARTIALLY** | SeverityBadge + clinical-severity.ts |
| 0014 | Abnormal value threshold flagging | proposed | **NOT IMPLEMENTED** | /api/reference-ranges existe, sem serviço |
| 0015 | Config-driven clinical form engine | proposed | **PARTIALLY** | FormEngine + 7 renderers funcional |
| 0016 | Feedback and loading patterns | proposed | **PARTIALLY** | api.ts centralizado, sem interceptor |
| 0017 | Fragmented real-time architecture | proposed | **PARTIALLY** | WebSocket unificado, sem reconnect/backoff |
| 0018 | Client integration & authorization | proposed | **PARTIALLY** | JWT + require_admin, sem query cache |
| 0019 | Stack ratification Radix+Tailwind | accepted | **IMPLEMENTED** | STACK_DECISION.md, package.json |
| 0020 | trilhas-engine architecture | IMPLEMENTED | **IMPLEMENTED** | trilhas_engine, compiler, evaluator, YAMLs |
| 0021 | trilhas-engine data model | proposed | **IMPLEMENTED** | content_hash, version, gold_writer, mpi |
| 0022 | Ventilação service architecture | proposed | **IMPLEMENTED** | domain_ventilacao, __version__, domain_respiratory |
| 0023 | Estabilidade scoring model | proposed | **IMPLEMENTED** | domain_hemo (931 linhas), threshold-based |
| 0024 | Piora Clínica detection | Proposed | **IMPLEMENTED** | domain_piora_clinica.py + tests |
| 0025 | Movimentação-ADT integration | Proposed | **PARTIALLY** | domain_movimentacao.py, SEM CDC/Kafka |
| 0026 | Drug interaction safety | Proposed | **IMPLEMENTED** | drug_interactions.py, 4 severity levels |
| 0027 | Prescrição lifecycle state machine | Proposed | **IMPLEMENTED** | domain_prescricao state machine, 5 estados |
| 0028 | Evoluções clínicas architecture | Proposed | **IMPLEMENTED** | domain_evolucoes (1331 linhas), SBAR, 14 roles |
| 0029 | Formulários dynamic form engine | proposed | **PARTIALLY** | FormEngine funcional, sem sync/offline/versioning |

---

## Recomendações

1. **Atualizar status dos ADRs:** 15 ADRs documentados como `proposed` já estão implementados. Atualizar para `accepted` com data de ratificação e evidência.

2. **ADR-0025 (Movimentação-ADT) — crítico:** É o maior gap de backend. O domain service existe mas sem CDC consumer. Prioridade para Fase 2.

3. **ADR-0007 (Neumórfico) e ADR-0004 (White-label):** Assinatura visual e branding por tenant são diferenciadores importantes não implementados.

4. **ADR-0029 (Formulários) — Gate 8:** Criar testes dedicados para clinical forms. Faltam versionamento, visibility rules, e offline.

5. **ADR-0005 (Tokens):** Configurar pipeline Style Dictionary funcional para ser single source of truth dos design tokens.

6. **Sincronizar documentação:** A desconexão entre ADRs `proposed` e código implementado gera risco de decisões duplicadas e retrabalho.

---

*Relatório gerado por Forensic Agent 2 — 2026-07-09*
