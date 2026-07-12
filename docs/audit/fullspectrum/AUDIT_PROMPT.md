# PROMPT — Auditoria Full-Spectrum da Plataforma IntensiCare
## Do Problema do Usuário à Inovação Entregue

**De:** Niemeyer (System Architect)  
**Para:** Orquestrador de Auditoria (agente especializado)  
**Data:** 2026-07-10  
**Tipo:** Auditoria completa de plataforma — NÃO EXECUTAR CÓDIGO, NÃO CORRIGIR BUGS  
**Objetivo:** Produzir um veredito independente e baseado em evidência sobre se a plataforma IntensiCare resolve o problema para o qual foi concebida e se é genuinamente inovadora.

---

## ═══════ ENVELOPE ═══════

| Campo | Valor |
|-------|-------|
| **Goal** | Auditar a plataforma IntensiCare em 5 dimensões — rastreabilidade produto→spec, UX/jornada, backend/correção, integração frontend↔backend, e inovação — e produzir um veredito unificado com scoring quantitativo e recomendações acionáveis. |
| **Context** | IntensiCare: plataforma de alertas proativos para UTIs. Backend: 9 trilhas clínicas YAML, motor de avaliação, 54 serviços de domínio. Frontend: rebuild completo (v3) com 6 páginas core orientadas a trilhas (pathway-centric). Stack: FastAPI + Next.js 16 + PostgreSQL + Redis. Projeto em `/Users/familia/intensicare/`. |
| **Constraints** | NÃO modificar código. NÃO corrigir bugs. NÃO fazer deploy. Auditoria somente — ler, analisar, testar, reportar. Backend em localhost:8000, frontend em localhost:3000. |
| **Done When** | Relatório de auditoria com 5 seções (uma por dimensão), scoring de 0-100 por dimensão, matriz de achados com severidade, e veredito final: GO / GO-WITH-ISSUES / NO-GO. |
| **Risk Level** | L1 — leitura, análise, teste de endpoints. Sem alterações em produção. |
| **Scope** | Plataforma IntensiCare completa: `/Users/familia/intensicare/`. Excluído: infraestrutura cloud, CI/CD pipelines, custos AWS. |

---

## ═══════ REGRAS DE OURO (Agentic Loop) ═══════

1. **RECON antes de agir.** Para cada dimensão, ler a documentação relevante ANTES de despachar agentes.
2. **`delegate_task` com skills.** Cada dimensão da auditoria é executada por um agente especializado COM skill específica carregada via `skill_view()`. Nenhum agente genérico.
3. **Evidência sobre opinião.** Todo achado DEVE citar arquivo, linha, endpoint, ou output de teste. "Parece bom" não é evidência.
4. **Gatekeeper ≠ Auditor.** Você orquestra. Os agentes auditam. A síntese final é SUA — cross-validando achados entre agentes.
5. **Estado no filesystem.** Produzir relatórios em `docs/audit/fullspectrum/`. Atualizar `AUDIT_HANDOFF.yaml` após cada fase.
6. **Max 3 agentes concorrentes.** Paralelize onde as dimensões forem independentes.
7. **Flywheel.** Após a auditoria: quais gaps são recorrentes? Atualizar skills.

---

## ═══════ FASES DA AUDITORIA ═══════

### FASE 0 — RECON (você, 20 min)

Antes de despachar qualquer agente, leia e sintetize:

1. `docs/audit/FORENSICS_SYNTHESIS.md` — auditoria anterior (v2)
2. `docs/audit/handoff-product-designer/FRONTEND_REBUILD_PLAN.md` — arquitetura do rebuild v3
3. `docs/adr/ADR-0030` a `ADR-0034` — 5 decisões arquiteturais core
4. `docs/contracts/pathways-openapi.yaml` — contrato canônico das trilhas
5. `_work/alerts/pathways/sepse.yaml` — trilha benchmark
6. `docs/audit/handoff-parreira/WIRING_GAPS.md` — gaps de integração conhecidos
7. `docs/audit/handoff-product-designer/HANDOFF.yaml` — estado atual dos milestones

**Output:** `docs/audit/fullspectrum/AUDIT_PLAN.md` com:
- Mapa do que será auditado em cada dimensão
- Lista de fontes de verdade para cada dimensão
- Ordem de execução (paralelismo)

---

### FASE 1 — Dimensão A: Rastreabilidade Produto→Spec (1 agente, 45 min)

**Pergunta central:** *O que foi construído corresponde ao problema que o usuário tinha?*

```
delegate_task(
  goal="Auditar a rastreabilidade completa da plataforma IntensiCare: do problema do usuário à especificação implementada",
  context="""
Repositório: /Users/familia/intensicare/

PERGUNTAS A RESPONDER (com evidência de arquivo):

1. PROBLEMA ORIGINAL:
   - Qual era o problema do intensivista que a plataforma se propôs a resolver?
   - Onde isso está documentado? (PRD, docs/plan/, ADRs iniciais?)
   - Havia métricas de sucesso definidas? Quais?

2. TRADUÇÃO PARA ESPECIFICAÇÃO:
   - O problema foi traduzido em requisitos técnicos? Onde? (docs/contracts/, docs/adr/, docs/tdd/?)
   - Cada requisito de usuário tem um artefato técnico correspondente?
   - Há rastro bidirecional: problema → spec → implementação?

3. DECISÕES ARQUITETURAIS:
   - As 5 ADRs (0030-0034) têm justificativa clínica ou são puramente técnicas?
   - A arquitetura de trilhas (pathway-centric) foi uma decisão de produto ou de engenharia?
   - Há evidência de que um médico/intensivista validou o modelo de trilhas?

4. GAPS DE ESPECIFICAÇÃO:
   - Há funcionalidades prometidas nos docs iniciais que NÃO existem no código?
   - Há funcionalidades no código que NÃO têm rastro em nenhum documento de especificação?
   - Os 15 contratos OpenAPI cobrem todos os endpoints? Ou há endpoints sem contrato?

5. SCORING:
   - Nota 0-100 para rastreabilidade produto→spec
   - Tabela de gaps com severidade (CRITICAL/MAJOR/MINOR)

Output: docs/audit/fullspectrum/DIM_A_TRACEABILITY.md
""",
  toolsets=["terminal", "file", "web", "skills"]
)
```

---

### FASE 2 — Dimensão B: UX e Jornada do Usuário (1 agente, 60 min)

**Pergunta central:** *Um intensivista consegue usar esta plataforma para tomar decisões clínicas em <2 cliques?*

```
delegate_task(
  goal="Auditar a experiência do usuário e a completude da jornada do intensivista na plataforma IntensiCare",
  context="""
Frontend: /Users/familia/intensicare/frontend-v3/ (Next.js 16, 8 rotas)
Backend: localhost:8000

PERGUNTAS A RESPONDER (com evidência de navegação real e inspeção de código):

1. JORNADA COMPLETA:
   - A jornada prometida (Dashboard → Patient → Pathway → Ação) funciona em ≤2 cliques?
   - Testar navegando NO BROWSER ou via curl em cada rota.
   - Há dead ends? Páginas que não têm link de volta? Breadcrumbs quebrados?

2. DENSIDADE DE INFORMAÇÃO:
   - O Dashboard mostra, em UMA tela: pacientes, scores (MEWS/NEWS2), severidade, e trilhas ativas?
   - O Patient Detail mostra TODAS as trilhas ativas do paciente em UMA tela?
   - O Pathway View mostra estado, critérios, recomendações, e histórico em UMA tela?
   - Há scroll excessivo? Informação clínica crítica está below the fold?

3. SISTEMA DE SEVERIDADE:
   - As 4 cores (verde/âmbar/laranja/vermelho) são usadas consistentemente em TODOS os componentes?
   - A severidade é codificada por cor E posição E movimento (pulsante para critical)?
   - Um daltônico conseguiria distinguir severidades? (verificar se há ícones ou formas além de cor)

4. ACESSIBILIDADE:
   - Verificar WCAG 2.1 AA: contraste, navegação por teclado, aria-labels
   - Todo elemento interativo tem aria-label?
   - A navegação funciona sem mouse? (Tab, Enter, Escape)
   - Testar com axe-core ou similar se disponível

5. RESPONSIVIDADE:
   - A interface funciona em viewport de tablet (768px)?
   - A interface funciona em viewport de desktop (1440px)?
   - Elementos críticos (scores, alertas, trilhas) são visíveis em ambas?

6. PÁGINAS ABOLIDAS:
   - As 17 páginas standalone de domínio do v2 foram REALMENTE removidas?
   - Listar todas as rotas do v3 e confirmar que nenhuma é standalone de domínio.
   - As 6 páginas core cobrem 100% da funcionalidade clínica?

7. SCORING:
   - Nota 0-100 para UX e jornada
   - Tabela de violações com severidade
   - Screenshots ou evidência de teste para cada ponto

Output: docs/audit/fullspectrum/DIM_B_UX.md
""",
  toolsets=["terminal", "file", "web", "browser", "skills"]
)
```

---

### FASE 3 — Dimensão C: Backend — Correção e Completude (1 agente, 60 min)

**Pergunta central:** *As fórmulas, thresholds e critérios clínicos estão corretos e completos?*

```
delegate_task(
  goal="Auditar a correção clínica e completude do backend IntensiCare: fórmulas, thresholds, motor de trilhas, e APIs",
  context="""
Backend: /Users/familia/intensicare/ (FastAPI, Python)
Trilhas YAML: /Users/familia/intensicare/_work/alerts/pathways/*.yaml
API contracts: /Users/familia/intensicare/docs/contracts/*.yaml

PERGUNTAS A RESPONDER (com evidência de código e teste de endpoint):

1. DEFINIÇÕES YAML DAS TRILHAS:
   - As 9+ trilhas YAML são sintaticamente válidas? (parse cada uma)
   - Cada trilha tem: id, name, states[], criteria[] com predicates, evidence?
   - Os predicates cobrem os tipos necessários? (graded com bands, boolean, thresholds)
   - Há referências a guidelines clínicas reais? (SSC-2021, KDIGO, CAM-ICU?)
   - Há trilhas com campos faltando ou incompletos?

2. MOTOR DE AVALIAÇÃO (trilhas_engine.py):
   - O motor carrega e compila TODAS as definições YAML?
   - A avaliação de critérios produz scores corretos para casos de teste conhecidos?
   - Testar: para a trilha de sepse, com valores conhecidos (ex: PAM=58, lactato=3.2), o score e severidade estão corretos?
   - O suppression (cooldown, rate_limit, dedup) funciona?

3. FÓRMULAS E THRESHOLDS:
   - MEWS, NEWS2, SOFA, qSOFA — as fórmulas conferem com a literatura médica?
   - Os thresholds de severidade (normal/watch/urgent/critical) são clinicamente apropriados?
   - Há documentação ou referência médica para cada threshold?

4. APIs E CONTRATOS:
   - Os 14+ endpoints consumidos pelo frontend retornam os shapes esperados?
   - Bater em cada endpoint com curl e comparar resposta com o schema OpenAPI
   - Endpoints que retornam 500/404/422?
   - Autenticação funciona em todos os endpoints protegidos?
   - Rate limiting? Tratamento de erros adequado (não vaza stack trace)?

5. DADOS:
   - Os dados de seed (pacientes, vitals, scores, pathways) são realistas?
   - A staleness dos dados (13+ dias) é um problema para uma auditoria de correção?
   - Há pacientes com pathways ativos? Se não, o motor de trilhas não pode ser validado.

6. SCORING:
   - Nota 0-100 para correção e completude do backend
   - Tabela de erros com severidade (CRITICAL: fórmula errada, MAJOR: threshold questionável, MINOR: campo faltando)

Output: docs/audit/fullspectrum/DIM_C_BACKEND.md
""",
  toolsets=["terminal", "file", "web", "skills"]
)
```

---

### FASE 4 — Dimensão D: Integração Frontend↔Backend (1 agente, 45 min)

**Pergunta central:** *O frontend e o backend estão realmente conectados ou há contratos quebrados?*

```
delegate_task(
  goal="Auditar a integração entre frontend-v3 e backend: shapes de API, fluxo de autenticação, WebSocket, e consistência de dados",
  context="""
Frontend API client: /Users/familia/intensicare/frontend-v3/lib/api.ts (403 linhas, 14 funções)
Backend APIs: localhost:8000/api/v1/*
Wiring gaps: /Users/familia/intensicare/docs/audit/handoff-parreira/WIRING_GAPS.md

PERGUNTAS A RESPONDER (com evidência de teste real):

1. SHAPE MATCHING (14 endpoints):
   Para CADA função em lib/api.ts:
   - Bater no endpoint real com curl
   - Comparar response JSON campo-a-campo com o tipo TypeScript esperado
   - Classificar: FULL_MATCH / PARTIAL (campos opcionais faltando) / MISMATCH (tipo errado) / BROKEN (500/404)

2. FLUXO DE AUTENTICAÇÃO:
   - Login (form-urlencoded) retorna { access_token, token_type, user }?
   - O token JWT contém claims: sub, is_admin, role, exp?
   - O middleware do frontend lê o cookie 'token' e redireciona corretamente?
   - Token expirado → 401 → redirect /login funciona?
   - Admin guard funciona? (usuário não-admin acessa /admin → redirecionado?)

3. WEBSOCKET:
   - Conexão ws://localhost:8000/api/v1/ws estabelece?
   - O protocolo de mensagens é compatível entre frontend e backend?
   - Se não, o fallback de polling (SWR 30s) está funcional?

4. CONSISTÊNCIA DE DADOS:
   - O Dashboard mostra os mesmos pacientes que o backend retorna?
   - As trilhas ativas no Patient Detail batem com GET /patients/{mpi_id}/pathways?
   - Os alertas no Alert Triage batem com GET /api/v1/alerts?
   - Ou há dissonância (ex: frontend mostra 0 pathways mas backend retorna dados)?

5. TRATAMENTO DE ERROS:
   - O frontend lida graciosamente com 401, 404, 500?
   - Mensagens de erro são informativas para o usuário?
   - Ou o frontend quebra silenciosamente (tela branca, spinner eterno)?

6. SCORING:
   - Nota 0-100 para integração
   - Matriz de endpoints com status e shape match

Output: docs/audit/fullspectrum/DIM_D_INTEGRATION.md
""",
  toolsets=["terminal", "file", "web", "skills"]
)
```

---

### FASE 5 — Dimensão E: Inovação e Diferenciação (1 agente, 45 min)

**Pergunta central:** *A plataforma IntensiCare é genuinamente inovadora ou é apenas um dashboard clínico genérico?*

```
delegate_task(
  goal="Auditar a inovação e diferenciação da plataforma IntensiCare em relação ao estado da arte em CDS (Clinical Decision Support) para UTI",
  context="""
Plataforma: /Users/familia/intensicare/
Documentação de produto: docs/plan/, docs/adr/, docs/audit/

PERGUNTAS A RESPONDER (com evidência comparativa):

1. DIFERENCIADOR ARQUITETURAL:
   - O modelo de trilhas (pathway-centric) é diferente de como outros CDS de UTI funcionam?
   - Sistemas concorrentes (Epic Deterioration Index, Philips IntelliVue, Hillrom) usam abordagem similar?
   - O que o IntensiCare faz que NENHUM concorrente faz?
   - A abordagem declarativa (YAML → motor de avaliação) é uma inovação técnica?

2. VALOR CLÍNICO:
   - A plataforma responde perguntas que o intensivista REALMENTE faz?
   - As 9 trilhas cobrem os principais riscos de UTI? (sepse, IRA, insuficiência respiratória, delirium...)
   - O sistema de severidade (normal/watch/urgent/critical) é acionável? (cada nível tem ação e tempo associados)
   - As recomendações são baseadas em guidelines (SSC-2021, KDIGO, CAM-ICU) ou são genéricas?

3. COMPLETUDE vs CONCORRENTES:
   - Quantos domínios clínicos a plataforma cobre? (27 reportados)
   - Isso é mais ou menos que sistemas comerciais?
   - A cobertura de trilhas (9) é suficiente para uma UTI geral?

4. INOVAÇÃO TÉCNICA:
   - O motor de regras declarativo (YAML → AST → avaliação) é tecnicamente inovador?
   - A abordagem data-driven do frontend (componentes genéricos que renderizam qualquer trilha) é inovadora?
   - Há uso de IA/ML ou é puramente baseado em regras? Isso é uma limitação ou uma escolha deliberada?

5. GAPS DE INOVAÇÃO:
   - O que a plataforma NÃO faz que seria esperado de um CDS moderno?
   - Ex: predictive analytics, ML-based risk scoring, NLP em evoluções clínicas, integração com EHR?
   - Esses gaps são conscientes (MVP) ou omissões?

6. SCORING:
   - Nota 0-100 para inovação
   - Matriz comparativa com concorrentes (mesmo que estimada)
   - Recomendações para aumentar diferenciação

Output: docs/audit/fullspectrum/DIM_E_INNOVATION.md
""",
  toolsets=["terminal", "file", "web", "skills"]
)
```

---

### FASE 6 — Síntese e Veredito (você, 45 min)

Após TODOS os 5 agentes retornarem, produza a síntese final.

**Output:** `docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md` com:

1. **Scoring Summary** (tabela):
   | Dimensão | Nota | Peso | Nota Ponderada |
   |----------|------|------|-----------------|
   | A — Rastreabilidade | ?/100 | 15% | — |
   | B — UX e Jornada | ?/100 | 30% | — |
   | C — Backend | ?/100 | 25% | — |
   | D — Integração | ?/100 | 20% | — |
   | E — Inovação | ?/100 | 10% | — |
   | **TOTAL** | | | **?/100** |

2. **Veredito:**
   - ≥85: **GO** — Plataforma inovadora, pronta para produção
   - 70-84: **GO-WITH-ISSUES** — Funcional, mas com gaps documentados
   - <70: **NO-GO** — Requer correções estruturais antes da produção

3. **Top 10 Achados** (CRITICAL primeiro)

4. **Cross-Validation:** Onde os achados de diferentes dimensões convergem? (ex: agente B diz "pathways vazios", agente C confirma "seed data ausente", agente D mostra "endpoint retorna 0")

5. **Recomendações Acionáveis:** Para cada achado CRITICAL e MAJOR, o que fazer, quem faz, e em qual milestone (M7/M8/M9)

6. **Inovação Real vs Percebida:** A plataforma é genuinamente inovadora ou é "mais um dashboard"? Resposta em 1 parágrafo com evidência.

---

## ═══════ ORDEM DE EXECUÇÃO ═══════

```
FASE 0: RECON (20 min)
  └── AUDIT_PLAN.md

FASE 1-5: 5 agentes em 2 batches paralelos

  BATCH 1 (independentes entre si):
  ├── FASE 1: Dimensão A — Rastreabilidade (45 min)
  ├── FASE 3: Dimensão C — Backend (60 min)
  └── FASE 5: Dimensão E — Inovação (45 min)

  BATCH 2 (dependem de backend rodando, podem rodar com Batch 1):
  ├── FASE 2: Dimensão B — UX (60 min)
  └── FASE 4: Dimensão D — Integração (45 min)

FASE 6: Síntese (45 min)
  └── FULLSPECTRUM_VERDICT.md
```

**Tempo total:** ~3.5 horas (2h de agentes paralelos + 1.5h de síntese)

---

## ═══════ ANTI-PATTERNS ═══════

- ❌ **Agente genérico sem skill.** Cada agente DEVE ter a skill relevante carregada. Auditoria sem skill = análise superficial.
- ❌ **Achado sem evidência.** "Parece incompleto" não é achado. "DIM_C_BACKEND.md §3.2: fórmula MEWS não confere com a literatura — threshold de FC usa 100 em vez de 110" é achado.
- ❌ **Corrigir bugs durante a auditoria.** Se encontrar um bug, REPORTE. Não corrija. O objetivo é medir, não consertar.
- ❌ **Síntese sem cross-validation.** Se dois agentes reportam o mesmo gap, isso é MAIS grave do que um gap isolado. A síntese deve identificar convergências.
- ❌ **Veredito baseado em intuição.** O scoring DEVE ser derivado dos achados. Cada ponto perdido deve ter um achado correspondente.
- ❌ **Ignorar o problema original.** A pergunta final não é "o código está bom?" — é "o intensivista está melhor com esta plataforma do que sem ela?"

---

## ═══════ OUTPUTS ESPERADOS ═══════

| Arquivo | Conteúdo |
|---------|----------|
| `docs/audit/fullspectrum/AUDIT_PLAN.md` | Plano de auditoria, fontes de verdade, ordem de execução |
| `docs/audit/fullspectrum/DIM_A_TRACEABILITY.md` | Rastreabilidade produto→spec (0-100) |
| `docs/audit/fullspectrum/DIM_B_UX.md` | UX e jornada do intensivista (0-100) |
| `docs/audit/fullspectrum/DIM_C_BACKEND.md` | Correção do backend (0-100) |
| `docs/audit/fullspectrum/DIM_D_INTEGRATION.md` | Integração frontend↔backend (0-100) |
| `docs/audit/fullspectrum/DIM_E_INNOVATION.md` | Inovação e diferenciação (0-100) |
| `docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md` | Síntese, scoring ponderado, veredito, recomendações |
| `docs/audit/fullspectrum/AUDIT_HANDOFF.yaml` | Estado da auditoria (máquina de estados) |

---

## ═══════ REFERÊNCIAS ═══════

- `/Users/familia/intensicare/docs/audit/FORENSICS_SYNTHESIS.md` — auditoria anterior
- `/Users/familia/intensicare/docs/audit/handoff-product-designer/FRONTEND_REBUILD_PLAN.md` — arquitetura v3
- `/Users/familia/intensicare/docs/adr/ADR-0030` a `ADR-0034` — decisões arquiteturais
- `/Users/familia/intensicare/docs/contracts/pathways-openapi.yaml` — contrato canônico
- `/Users/familia/intensicare/_work/alerts/pathways/*.yaml` — definições das trilhas
- `/Users/familia/intensicare/frontend-v3/lib/api.ts` — contrato frontend (403 linhas)
- `/Users/familia/intensicare/docs/audit/handoff-parreira/WIRING_GAPS.md` — gaps conhecidos
