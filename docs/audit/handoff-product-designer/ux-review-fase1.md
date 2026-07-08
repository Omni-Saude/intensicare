# UX Review — Fase 1: Componentes Base

**Data:** 2026-07-07  
**Revisor:** Hermes Agent (automatizado)  
**Escopo:** 4 componentes do módulo M2  
**Classificação:** Factual (bug) / Heurístico (issue) / Subjetivo (sugestão)

---

## Sumário Executivo

| Componente | Achados Factuais | Achados Heurísticos | Achados Subjetivos | Score |
|---|---|---|---|---|
| CriteriaChecklist | 0 | 1 | 2 | ✅ Aprovado |
| ClinicalTimeline | 2 | 2 | 2 | ⚠️ Aprovado com Ressalvas |
| BundleCard | 2 | 1 | 2 | ⚠️ Aprovado com Ressalvas |
| StewardshipScoreBadge | 3 | 2 | 1 | ❌ Rejeitado |
| **Global** | **7** | **6** | **7** | **⚠️ Aprovado com Ressalvas** |

---

## 1. CriteriaChecklist

### 1.1 Estados Cobertos
| Estado | Coberto? | Observações |
|---|---|---|
| Loading | ✅ | 5 skeleton rows com `animate-pulse`, `role="status"` |
| Empty | ✅ | "Nenhum critério configurado" com HelpCircle |
| Error | ✅ | AlertTriangle + mensagem, `role="alert"`, `aria-live="assertive"` |
| Normal (interativo) | ✅ | Checkboxes com toggle, valores/limiares |
| ReadOnly | ✅ | Ícones CheckCircle/XCircle no lugar dos checkboxes |
| Disabled individual | ❌ | Não há suporte a critério desabilitado individualmente |

### 1.2 Achados

| # | Severidade | Classificação | Descrição | Recomendação |
|---|---|---|---|---|
| C1 | minor | Heurístico | **Sem ação de retry no estado de erro.** O componente exibe a mensagem mas não oferece botão "Tentar novamente". Viola heurística #9 (error recovery). | Adicionar `onRetry?: () => void` como prop opcional e renderizar botão "Tentar novamente" no estado de erro. |
| C2 | suggestion | Subjetivo | **Skeleton rows em número fixo (5).** Poderia ser configurável ou proporcional ao número esperado de critérios para evitar layout shift. | Aceitar `skeletonCount?: number` (default 5) ou inferir do `items.length` quando disponível. |
| C3 | suggestion | Subjetivo | **Status text (Atendido/Não atendido) visível apenas no hover** em modo interativo (`opacity-0 group-hover:opacity-100`). Em touch devices, nunca aparece. | Considerar exibir permanentemente em mobile (media query) ou usar `focus-within` para mostrar quando o checkbox recebe foco. |

### 1.3 Verificações

| Critério | Status | Notas |
|---|---|---|
| Feedback visual claro | ✅ | Checkbox preenche com cor do token; valor/threshold colorido conforme status |
| Hierarquia de informação | ✅ | Label principal → valor/threshold → status indicator |
| Labels PT-BR | ✅ | "Atendido", "Não atendido", "Nenhum critério configurado" |
| Consistência design system | ✅ | CSS variables do sistema; tokens por domínio (sepsis/antimicrobial) |
| Acessibilidade | ✅ | `aria-label`, `aria-describedby`, `role="list"`, `role="status"`, `role="alert"` |

---

## 2. ClinicalTimeline

### 2.1 Estados Cobertos
| Estado | Coberto? | Observações |
|---|---|---|
| Loading | ✅ | 3 skeleton events com `animate-pulse` |
| Empty | ✅ | "Nenhum evento registrado" com History icon |
| Error | ✅ | AlertTriangle + mensagem |
| Normal | ✅ | Timeline vertical com nós, conectores, timestamps |
| Overdue | ✅ | Animação `animate-pulse-critical`, tokens vermelhos |
| Single event | ✅ | Sem linha conectora (`isLast`) |
| General domain | ✅ | Story separada para `domain="general"` |

### 2.2 Achados

| # | Severidade | Classificação | Descrição | Recomendação |
|---|---|---|---|---|
| C4 | **blocker** | Factual | **Status badges exibem labels em INGLÊS.** `statusLabels` (linhas 63-68) mapeia para "completed", "in progress", "pending", "overdue". Viola requisito de PT-BR. | Traduzir `statusLabels` para: `completed: 'Concluído'`, `in-progress: 'Em andamento'`, `pending: 'Pendente'`, `overdue: 'Atrasado'`. |
| C5 | major | Factual | **`itemRefs` (Map) é populado mas nunca lido.** O `useEffect` de keyboard navigation usa `querySelectorAll` em vez dos refs. Código morto (`setItemRef` chamado no `ref` callback de cada item, mas `itemRefs.current` nunca é acessado). | Remover `itemRefs` e `setItemRef`, ou refatorar keyboard navigation para usar os refs em vez de querySelectorAll. |
| C6 | minor | Heurístico | **Sem ação de retry no erro.** Mesmo padrão do CriteriaChecklist. | Adicionar `onRetry?: () => void`. |
| C7 | minor | Heurístico | **Prop `domain` não influencia tokens visuais.** O domínio só altera `aria-label`. Para `domain="general"`, os tokens de status ainda referenciam `--clinical-sepsis-*`. Isso pode gerar inconsistência visual se os tokens do domínio general diferirem. | Mapear tokens por domínio quando necessário, ou documentar que `domain` é apenas semântico para acessibilidade. |
| C8 | suggestion | Subjetivo | **Keyboard navigation não suporta Home/End.** Apenas ArrowUp/ArrowDown. | Adicionar handlers para Home (primeiro evento) e End (último evento). |
| C9 | suggestion | Subjetivo | **Campo `icon` definido na interface `TimelineEvent` mas nunca utilizado.** API surface não implementada. | Remover ou implementar renderização condicional do ícone no nó da timeline. |

### 2.3 Verificações

| Critério | Status | Notas |
|---|---|---|
| Feedback visual claro | ✅ | Nós coloridos por status, badge de status, animação overdue |
| Hierarquia de informação | ✅ | Nó → Label → Descrição → Timestamp → Status badge |
| Labels PT-BR | ❌ | Status badges em inglês (C4). Labels de eventos estão em PT-BR nos stories. |
| Consistência design system | ⚠️ | Domain="general" usa tokens de sepse (C7) |
| Acessibilidade | ✅ | `aria-label` detalhado, keyboard nav, `tabIndex`, `focus-visible` |

---

## 3. BundleCard

### 3.1 Estados Cobertos
| Estado | Coberto? | Observações |
|---|---|---|
| Loading | ✅ | Skeleton card com header, barra, 3 critérios |
| Error | ✅ | AlertTriangle + mensagem |
| Complete (100%) | ✅ | Barra verde cheia, CheckCircle badge |
| Partial | ✅ | Barra parcial, Clock badge |
| Pending (0%) | ✅ | Barra vazia, Circle badge |
| N/A | ✅ | Sem barra de progresso, Ban badge, critérios riscados |
| ReadOnly | ✅ | Ícones no lugar de checkboxes |
| Empty criteria | ✅ | Estado interno: "Nenhum critério definido" |

### 3.2 Achados

| # | Severidade | Classificação | Descrição | Recomendação |
|---|---|---|---|---|
| C10 | **major** | Factual | **Critérios N/A inflam `metCount` e `progressPercent`.** O cálculo `bundle.criteria.filter((c) => c.met).length` inclui critérios com `na: true` que tenham `met: true`. Para bundles com status diferente de 'na' mas com critérios N/A individuais, a barra de progresso exibe valor incorreto. | Filtrar critérios N/A: `bundle.criteria.filter((c) => c.met && !c.na).length` e `totalCount` deve excluir N/A também. |
| C11 | minor | Factual | **Condicional CSS morto na linha 316.** `!criterion.met && !criterion.na ? '' : ''` — ambos os branches produzem string vazia. Código sem efeito. | Remover a expressão condicional inútil. |
| C12 | minor | Heurístico | **Sem ação de retry no erro.** Padrão consistente com os demais. | Adicionar `onRetry?: () => void`. |
| C13 | suggestion | Subjetivo | **Score explícito vs. calculado: comportamento ambíguo.** `bundle.score` tem precedência sobre `progressPercent` (via `??`). Se o backend enviar score divergente do cálculo local, a UI mostra o score do backend mas a barra pode parecer inconsistente com os checkboxes. | Documentar a precedência ou exibir indicador visual quando o score é externo vs. calculado. |
| C14 | suggestion | Subjetivo | **Rótulo de progresso não inclui percentual.** "3 de 5 critérios atendidos" — o percentual só aparece no número à direita. Poderia ser integrado: "3 de 5 (60%)". | Unificar label e percentual em uma string ou tooltip. |

### 3.3 Verificações

| Critério | Status | Notas |
|---|---|---|
| Feedback visual claro | ✅ | Barra de progresso animada, badge de status, checkbox colorido |
| Hierarquia de informação | ✅ | Nome → Status badge → Progresso → Critérios |
| Labels PT-BR | ✅ | "Completo", "Parcial", "Pendente", "N/A", "Nenhum critério definido" |
| Consistência design system | ✅ | Tokens de prophylaxis reutilizados; CSS variables padrão |
| Acessibilidade | ✅ | `role="progressbar"` com `aria-valuenow/min/max`, `aria-label` no card |

---

## 4. StewardshipScoreBadge

### 4.1 Estados Cobertos
| Estado | Coberto? | Observações |
|---|---|---|
| Loading | ✅ | Skeleton inline com Loader2 animado |
| Error | ❌ | **Não implementado.** Sem prop `error`. |
| Empty / Zero | ❌ | Sem tratamento para `totalCriteria = 0`. |
| NEUTRO (verde) | ✅ | ShieldCheck, tokens de "optimal" |
| AMARELO (amber) | ✅ | AlertTriangle, tokens de "review" |
| VERMELHO (red) | ✅ | AlertOctagon, tokens de "intervention" |
| Sem recomendação | ✅ | Bloco de recomendação condicional |
| Comparação lado a lado | ✅ | Story Comparison com os 3 níveis |

### 4.2 Achados

| # | Severidade | Classificação | Descrição | Recomendação |
|---|---|---|---|---|
| C15 | **blocker** | Factual | **Badge exibe valor RAW do enum `severity` em vez do label PT-BR.** Linha 165 renderiza `{severity}` que produz "VERMELHO", "AMARELO", ou "NEUTRO". O `severityLabels` existe (linhas 59-63) com labels amigáveis ("Intervenção Imediata", "Revisão Recomendada", "Prescrição Adequada") mas é usado apenas no `aria-label` (linha 85-89), não na renderização visual. | Substituir `{severity}` por `{label}` (ou `{severityLabels[severity]}`) no JSX da linha 165. |
| C16 | **blocker** | Factual | **Sem estado de erro.** O componente não aceita prop `error` e não renderiza estado de falha. Se o cálculo do score falhar, o componente não tem como comunicar isso ao usuário. Todos os outros 3 componentes suportam erro. | Adicionar `error?: string \| null` à interface e renderizar estado de erro com AlertTriangle, consistente com os demais componentes. |
| C17 | major | Factual | **Sem validação de bounds.** Se `totalCriteria = 0`, o badge exibe "score / 0". Se `score > totalCriteria`, exibe valor inconsistente (ex: "15 / 12"). | Adicionar validação: `totalCriteria <= 0` → estado vazio/indisponível. `score > totalCriteria` → cap em `totalCriteria` ou exibir warning visual. |
| C18 | minor | Heurístico | **Sem ação de retry no loading.** O estado de loading não oferece cancelamento ou timeout visual — se o carregamento travar, o usuário fica sem feedback. | Adicionar timeout + transição para estado de erro com botão retry. |
| C19 | minor | Heurístico | **`role="status"` + `aria-live="polite"` anuncia mudanças de score.** Isso é bom para updates em tempo real, mas se o score for estático, pode causar anúncios desnecessários em alguns screen readers. | Avaliar se `aria-live` deve ser condicional (apenas quando o score é dinâmico). |
| C20 | suggestion | Subjetivo | **Sem indicador visual de tendência.** Um ícone `TrendingUp`/`TrendingDown` poderia indicar se o score melhorou ou piorou desde a última avaliação (útil para contexto clínico). | Adicionar prop opcional `trend?: 'up' \| 'down' \| 'stable'` com ícone correspondente. |

### 4.3 Verificações

| Critério | Status | Notas |
|---|---|---|
| Feedback visual claro | ⚠️ | Ícone + cor fortes, mas label exibe enum RAW (C15) |
| Hierarquia de informação | ✅ | Ícone circular → Score → Severidade → Recomendação |
| Labels PT-BR | ❌ | Severidade exibe "VERMELHO"/"AMARELO"/"NEUTRO" (C15); recomendação está em PT-BR nos stories |
| Consistência design system | ✅ | CSS variables do sistema; tokens stewardship |
| Acessibilidade | ✅ | `aria-label` com score + severidade + recomendação; `role="status"` |

---

## 5. Verificações Transversais

### 5.1 Consistência entre Componentes

| Aspecto | CriteriaChecklist | ClinicalTimeline | BundleCard | StewardshipScoreBadge |
|---|---|---|---|---|
| Loading pattern | Skeleton rows | Skeleton timeline | Skeleton card | Skeleton inline |
| Error pattern | AlertTriangle + msg | AlertTriangle + msg | AlertTriangle + msg | ❌ Ausente |
| Retry no erro | ❌ | ❌ | ❌ | ❌ |
| Labels PT-BR | ✅ | ❌ (C4) | ✅ | ❌ (C15) |
| CSS variables | ✅ | ✅ | ✅ | ✅ |
| `role` attributes | ✅ | ✅ | ✅ | ✅ |
| `use client` | ✅ | ✅ | ✅ | ✅ |

### 5.2 Heurísticas Nielsen Norman — Avaliação Global

| Heurística | Avaliação | Notas |
|---|---|---|
| #1 Visibility of system status | ✅ | Loading/error/empty cobertos (exceto StewardshipScoreBadge sem erro) |
| #2 Match between system and real world | ⚠️ | ClinicalTimeline usa labels em inglês; StewardshipScoreBadge mostra enum raw |
| #3 User control and freedom | ❌ | Nenhum componente oferece "retry" ou "cancel" no erro/loading |
| #4 Consistency and standards | ⚠️ | StewardshipScoreBadge quebra padrão de erro; ClinicalTimeline usa inglês |
| #5 Error prevention | ⚠️ | BundleCard não trata N/A no cálculo; StewardshipScoreBadge sem validação de bounds |
| #6 Recognition rather than recall | ✅ | Ícones + cores + labels; status visuais claros |
| #7 Flexibility and efficiency of use | ✅ | Keyboard nav na timeline; readOnly em Checklist e BundleCard |
| #8 Aesthetic and minimalist design | ✅ | Design limpo, sem elementos desnecessários |
| #9 Help users recognize, diagnose, recover from errors | ❌ | Mensagens de erro sem ação de recuperação |
| #10 Help and documentation | ⚠️ | Stories cobrem variações mas ClinicalTooltip dependency não documentada no CriteriaChecklist |

---

## 6. Matriz de Severidade por Componente

### CriteriaChecklist: ✅ Aprovado
- 0 bloqueadores
- 0 major
- 1 minor (sem retry)
- 2 sugestões

### ClinicalTimeline: ⚠️ Aprovado com Ressalvas
- 1 bloqueador (labels em inglês)
- 1 major (itemRefs não utilizado)
- 2 minor (sem retry, domain não afeta tokens)
- 2 sugestões

### BundleCard: ⚠️ Aprovado com Ressalvas
- 0 bloqueadores
- 1 major (N/A infla metCount)
- 1 minor (sem retry, CSS morto)
- 2 sugestões

### StewardshipScoreBadge: ❌ Rejeitado
- 2 bloqueadores (enum raw no display, sem estado de erro)
- 1 major (sem validação de bounds)
- 2 minor
- 1 sugestão

---

## 7. Plano de Ação Recomendado

### Bloqueadores (corrigir antes do merge)
1. **C4 — ClinicalTimeline:** Traduzir `statusLabels` para PT-BR
2. **C15 — StewardshipScoreBadge:** Usar `severityLabels` no display visual
3. **C16 — StewardshipScoreBadge:** Implementar estado de erro

### Major (corrigir na mesma sprint)
4. **C5 — ClinicalTimeline:** Remover código morto (`itemRefs`)
5. **C10 — BundleCard:** Corrigir cálculo de progresso excluindo critérios N/A
6. **C17 — StewardshipScoreBadge:** Adicionar validação de bounds

### Minor (próxima sprint)
7. **C1, C6, C12 — Todos:** Adicionar `onRetry` nos estados de erro
8. **C7 — ClinicalTimeline:** Documentar ou implementar tokens por domínio
9. **C11 — BundleCard:** Remover condicional CSS morta
10. **C18, C19 — StewardshipScoreBadge:** Timeout no loading; revisar aria-live

### Sugestões (backlog)
11. C2, C3, C8, C9, C13, C14, C20

---

## 8. Conclusão

**Score global: ⚠️ APROVADO COM RESSALVAS**

Dois componentes (CriteriaChecklist, BundleCard) estão em bom estado e próximos do padrão de qualidade. ClinicalTimeline tem um bloqueador simples de resolver (tradução de labels). StewardshipScoreBadge é o componente mais frágil, com 2 bloqueadores que precisam de atenção imediata — notadamente a ausência total de estado de erro e a exibição de enum RAW em vez de labels amigáveis.

O padrão transversal mais preocupante é a **falta de ação de recuperação em estados de erro** (presente em 3 dos 4 componentes), o que viola a heurística #9 de Nielsen Norman e pode degradar a experiência em cenários reais de falha de rede.
