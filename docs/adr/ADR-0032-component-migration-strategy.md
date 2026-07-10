# ADR-0032: Construção do Zero — UX-First, Especificação do Backend como Única Fonte

**Status:** proposed  
**Data:** 2026-07-09  
**Decisão por:** Niemeyer (System Architect)  
**Supersedes:** ADR-0032 v1 (component migration strategy)  

---

## Contexto

O frontend v2 foi construído com o modelo mental errado — 1 domínio clínico = 1 página independente. A raiz do problema não foi técnica: foi de UX. Páginas visualmente bem construídas, mas desconexas da jornada real do intensivista, que precisa entender múltiplos aspectos clínicos de um paciente simultaneamente.

A abordagem inicial (ADR-0032 v1) propunha "reaproveitar" componentes do v2 — tokens, API client, componentes atômicos. Isso foi rejeitado pelo product owner com uma diretriz clara:

> "Frontend do zero, 100% novo, sem reutilizações, completamente baseado no backend e nas especificações originais. UX precede design."

A razão é profunda e correta: **reaproveitar componentes do v2 carregaria o modelo mental errado para o novo frontend.** O SeverityBadge do v2 foi desenhado para uma página standalone de sepse. O AlertCard foi desenhado para um fluxo de alertas isolado. Copiá-los seria como construir uma casa nova com as mesmas paredes tortas.

## Decisão

**O frontend v3 será construído 100% do zero. Nenhum código, componente, token ou arquivo de configuração do v2 será copiado ou reaproveitado.**

Toda construção parte de três fontes apenas:

1. **A jornada do intensivista** — as 7 perguntas que o médico faz durante o cuidado (Seção 1 do FRONTEND_REBUILD_PLAN.md). Cada componente só existe se responder a uma dessas perguntas.

2. **Os schemas OpenAPI do backend** — `docs/contracts/pathways-openapi.yaml` e demais contratos. Os tipos TypeScript são derivados diretamente desses schemas, não de código existente.

3. **As definições YAML das trilhas** — `_work/alerts/pathways/*.yaml`. A estrutura de dados que chega ao frontend determina o que é renderizado, não o contrário.

### O que isso significa na prática

| Artefato | v1 (rejeitado) | v2 (correto) |
|----------|---------------|--------------|
| Design tokens | Copiar 24 arquivos JSON do v2 | Derivar do sistema de severidade definido nos YAMLs (normal/watch/urgent/critical) |
| API client (`lib/api.ts`) | Copiar 1029 linhas e expandir | Escrever do zero a partir dos schemas OpenAPI — apenas os tipos e funções que o frontend realmente consome |
| Componentes de severidade | Copiar `SeverityBadge`, `ClinicalTooltip` | Projetar novos componentes que respondem à pergunta da jornada, usando severidade como atributo visual, não como componente isolado |
| Middleware de auth | Copiar `middleware.ts` | Escrever middleware novo baseado na spec de autenticação do backend (JWT, claims, refresh) |
| Layout/Sidebar | Refatorar `Layout.tsx` | Projetar `AppShell` do zero com navegação hierárquica que espelha a jornada (Dashboard → Pacientes → Alertas → Trilhas → Admin) |

## Alternativas Consideradas

### Alternativa A: Reaproveitar componentes atômicos (ADR-0032 v1 — REJEITADA)
- **Prós:** Menor esforço inicial, componentes já testados
- **Contras:** Carrega o modelo mental errado. Componentes foram desenhados para páginas standalone, não para uma jornada integrada. O SeverityBadge do v2 funciona isolado, mas no contexto do Pathway View ele precisa mostrar não só a severidade, mas também o critério, o threshold, a tendência — informação que o v2 não tem.
- **Rejeitada pelo product owner:** "Frontend do zero, sem reutilizações."

### Alternativa B: Construir do zero, mas sem design system
- **Prós:** Velocidade inicial
- **Contras:** Inconsistência visual entre componentes, retrabalho, problemas de acessibilidade
- **Rejeitada porque:** O design system é parte da construção do zero. Ele é derivado do sistema de severidade do backend, não copiado de lugar nenhum.

### Alternativa C: Usar biblioteca de componentes pronta (ex: Tremor, Mantine)
- **Prós:** Velocidade, acessibilidade built-in
- **Contras:** Estilo genérico, difícil de customizar para o contexto clínico (severidade pulsante, modo escuro de UTI, densidade de informação)
- **Rejeitada porque:** shadcn/ui oferece o equilíbrio certo: componentes headless e acessíveis que podem ser estilizados para o domínio clínico.

## Consequências

### Positivas
- **Modelo mental limpo.** Nenhum componente carrega assumptions do v2.
- **Design orientado à jornada.** Cada componente nasce de uma pergunta do intensivista.
- **Tipos TypeScript fiéis ao backend.** Derivados diretamente dos schemas OpenAPI, não de código legado.
- **Design system coeso.** Construído do zero em torno do sistema de severidade clínica.
- **Código mais enxuto.** Sem 1029 linhas de API client que cobriam endpoints que o v3 nem usa.

### Negativas
- **Maior esforço inicial.** Escrever API client, tokens, middleware do zero leva mais tempo que copiar.
- **Risco de perder funcionalidades periféricas.** O v2 tinha features que podem ser esquecidas (ex: tela de registro, recuperação de senha).
- **Sem rede de segurança.** Não há "fallback para o componente antigo" durante a construção.

### Riscos e Mitigações
- **Risco:** Perder feature crítica do v2 → **Mitigação:** Auditar o v2 antes de descartar. Listar todas as features. Mapear cada uma para uma página do v3 ou documentar que foi intencionalmente removida.
- **Risco:** API client escrito do zero tem bugs → **Mitigação:** Testar cada função contra o backend real durante o M0, antes de qualquer componente usá-la.
- **Risco:** Design system inconsistente entre componentes → **Mitigação:** Definir tokens CSS no M0 ANTES de qualquer componente visual. Usar CSS custom properties para tudo.

---

## Referências

- FRONTEND_REBUILD_PLAN.md v2.0 § 0 (Princípios Fundamentais)
- FRONTEND_REBUILD_PLAN.md v2.0 § 1 (Jornada do Intensivista)
- `docs/contracts/pathways-openapi.yaml` (schemas canônicos)
- `_work/alerts/pathways/sepse.yaml` (sistema de severidade)
- ADR-0030 (pathway-centric architecture)
- ADR-0033 (generic pathway view pattern)
