# FASE 5b — UX Review: Nielsen Norman em 4 Domínios Core

**Projeto:** IntensiCare  
**Data:** 2026-07-07  
**Escopo:** Trilhas-Engine, Ventilação, Estabilidade, Piora-Clinica  
**Metodologia:** 10 Heurísticas de Nielsen Norman (1994)  
**Classificação SOUL.md:** FACTUAL (bug) | HEURÍSTICO (issue) | SUBJETIVO (sugestão)

---

## Tabela Priorizada de Achados

| # | Domínio | Heurística | Classificação | Severidade | Problema | Recomendação |
|---|---------|-----------|---------------|------------|----------|--------------|
| **1** | Estabilidade | H1: Visibility of System Status | FACTUAL | **Crítica** | A recomendação clínica (`RecommendationCard`) renderiza com `opacity: 0.12` (linha 404-405 de `stability/page.tsx`), tornando o texto praticamente invisível. O cartão é ilegível em qualquer tema. | Remover `opacity: 0.12` ou usar valor ≥ 0.9. A `backgroundColor` com `washColor` já provê distinção visual suficiente sem reduzir opacidade. |
| **2** | Estabilidade | H4: Consistency and Standards | FACTUAL | **Alta** | Filtros por categoria aparecem DUAS vezes na mesma tela: nos botões `role="tablist"` do page component (linhas 780-818) e dentro do `StabilityHeatmap` (linhas 312-349). Os dois conjuntos de filtros operam com estados independentes e não sincronizados — o heatmap mantém `activeFilter` local enquanto a página controla `categoryFilter`. | Remover os filtros duplicados de UM dos componentes. Recomendação: manter no page component e remover do `StabilityHeatmap`, passando `categoryFilter` como prop controlada. |
| **3** | Estabilidade | H1: Visibility of System Status | FACTUAL | **Alta** | O skeleton de loading nunca renderiza porque a condição `if (isLoading && !status)` (linha 689) nunca é verdadeira — `status` é inicializado como `MOCK_STATUS` (sempre truthy, linha 650). A troca de paciente dispara `setIsLoading(true)` com timeout de 600ms, mas o estado `status` não é resetado. O usuário nunca vê feedback visual de carregamento. | Alterar condição para `if (isLoading)` apenas, ou resetar `status` para `null` antes do timeout: `setStatus(null); setIsLoading(true); setTimeout(() => { setStatus(MOCK_STATUS); setIsLoading(false); }, 600);` |
| **4** | Trilhas | H1: Visibility of System Status | FACTUAL | **Alta** | Os estados `isLoading` e `error` são declarados com `useState(false)` e `useState(null)` (linhas 209-210 de `care-pathways/page.tsx`) mas nunca atualizados via `setIsLoading`/`setError`. Os componentes `SplitScreenSkeleton` e o bloco de erro NUNCA renderizam — estados mortos. | Implementar chamadas reais de API com transições de estado ou, se mock, simular via botão "Simular carregamento" como feito em Ventilação. |
| **5** | Ventilação | H1: Visibility of System Status | FACTUAL | **Alta** | Botões de demonstração ("Loading", "Error", "Empty", "Restaurar") estão expostos na UI de produção (linhas 501-557). São artefatos de desenvolvimento que poluem a interface clínica e podem ser acionados acidentalmente. | Remover botões de demo do build de produção. Usar feature flag, variável de ambiente (`NODE_ENV`), ou Storybook para testes de estado. |
| **6** | Piora-Clinica | H4: Consistency and Standards | FACTUAL | **Média** | O `alert_id` badge no `DomainCard` usa classes Tailwind hardcoded (`bg-amber-50 text-amber-700`, linha 510) em vez de CSS custom properties como todo o restante do design system. Isso quebra o theming (dark mode não funcionará) e a consistência visual. | Substituir por tokens do design system: `backgroundColor: 'var(--clinical-severity-watch-wash)'`, `color: 'var(--clinical-severity-watch-on-surface)'` ou criar token específico como `var(--feedback-warning-bg)`. |
| **7** | Estabilidade | H8: Aesthetic and Minimalist Design | HEURÍSTICO | **Alta** | As células do heatmap usam `opacity: 0.16` (linha 427 de `StabilityHeatmap.tsx`) sobre a `washColor` de fundo. Combinado com o ícone `SignalDot`, a distinção entre estados "normal" (verde), "atenção" (amarelo) e "crítico" (vermelho) fica muito sutil, especialmente para usuários com daltonismo ou em monitores de baixo contraste. | Aumentar opacidade para ≥ 0.25 e adicionar borda colorida (`borderColor: signalColor, borderWidth: '1px'`). Garantir contraste mínimo WCAG AA (4.5:1 para texto, 3:1 para elementos gráficos). |
| **8** | Trilhas | H2: Match System/Real World | HEURÍSTICO | **Média** | O mapeamento de severidade no `SeverityBadge` (PathwayBoard.tsx, linha 317) colapsa `'watch'` e `'urgent'` no mesmo valor `'urgent'`: `severity={severity === 'watch' ? 'urgent' : severity === 'urgent' ? 'urgent' : ...}`. Clinicamente, "watch" (observar) e "urgent" (urgente) são níveis distintos com ações clínicas diferentes. | Mapear `'watch'` para o valor `'watch'` no `SeverityBadge` (se disponível). Se o componente não suportar 'watch', estender o componente ou usar tradução semântica correta (ex.: "Em observação" vs "Urgente"). |
| **9** | Trilhas | H4: Consistency and Standards | HEURÍSTICO | **Média** | A página de Trilhas usa `FullScreenLayout` (sem sidebar fixa), enquanto Ventilação, Estabilidade e Piora-Clinica usam `Layout` (com sidebar fixa de 256px). Isso cria uma quebra de paradigma de navegação — o usuário perde a barra lateral de navegação ao entrar em Trilhas e precisa usar a top-bar minimalista para navegar. | Padronizar: todas as páginas clínicas devem usar o mesmo layout. Se Trilhas requer tela cheia, adicionar botão "Voltar" proeminente ou breadcrumb. Alternativa: usar `FullScreenLayout` com sidebar colapsável. |
| **10** | Piora-Clinica | H10: Help and Documentation | HEURÍSTICO | **Média** | As categorias de score de deterioração ("1-", "1", "2", "3+", "3-") não são terminologia clínica padrão (ex.: MEWS, NEWS2, qSOFA). Não há tooltip, legenda ou documentação contextual explicando o significado clínico de cada faixa. O usuário precisa inferir o significado. | Adicionar tooltip no gauge com descrição clínica: ex.: "1- = Baixo risco, reavaliar em 12h", "3+ = Risco iminente, acionar Time de Resposta Rápida". Incluir legenda abaixo do gauge ou botão (?) com explicação completa. |
| **11** | Ventilação | H9: Help Recover from Errors | HEURÍSTICO | **Média** | A mensagem de erro simulada é genérica: "Erro ao carregar dados de ventilação. Verifique a conexão com o ventilador e tente novamente." Não oferece: código de erro, timestamp, sugestão de ação alternativa (ex.: "Usar últimos dados disponíveis do cache"), ou contato do suporte técnico. | Enriquecer mensagem de erro com: (1) código/timestamp para debugging, (2) opção "Usar dados offline" se disponível, (3) link/telefone do suporte, (4) distinção entre erro de rede vs erro de dados inválidos. |
| **12** | Estabilidade | H6: Recognition Rather than Recall | HEURÍSTICO | **Média** | O heatmap não exibe os nomes dos critérios nas células — apenas ícones coloridos. O usuário precisa passar o mouse (hover) em cada célula para ler o nome do critério no tooltip, forçando memorização da posição ou exploração lenta. Em dispositivo touch, o tooltip não é acessível. | Adicionar texto abreviado do critério dentro da célula (ex.: "PAM", "FC", "Lactato") ou abaixo do grid como lista de referência. Alternativa: exibir tooltip também em `onFocus`/`onClick` para suporte touch. |
| **13** | Trilhas | H6: Recognition Rather than Recall | HEURÍSTICO | **Média** | Na lista de estados do pathway (PathwayBoard.tsx, linhas 473-557), estados futuros são indicados apenas por um círculo cinza (`w-2.5 h-2.5 rounded-full` com `backgroundColor: 'var(--semantic-surface-overlay)'`). Não há indicador visual de quantos estados faltam ou qual a distância temporal estimada. | Adicionar numeração (1, 2, 3...) ou barra de progresso com marcadores. Exibir estimativa de tempo para próximos estados se disponível (ex.: "Próximo estado estimado em 48h"). |
| **14** | Ventilação | H5: Error Prevention | HEURÍSTICO | **Média** | A tabela de histórico marca valores anormais de SpO₂ e Driving Pressure apenas com cor (verde/vermelho), sem ícone de alerta ou indicador redundante. Usuários daltônicos ou em displays monocromáticos podem não perceber valores críticos. | Adicionar ícone `AlertTriangle` ao lado de valores fora do threshold. Usar padrão redundante: cor + ícone + texto (ex.: "SpO₂: 88% ⚠️ Abaixo do alvo"). Seguir WCAG SC 1.4.1 (não usar cor como único meio de transmitir informação). |
| **15** | Trilhas | H7: Flexibility and Efficiency | HEURÍSTICO | **Baixa** | A lista de pacientes (sidebar de 280px) não possui campo de busca, filtro por gravidade, ou ordenação. Em UTIs com 20+ leitos, encontrar um paciente específico requer scroll manual. | Adicionar campo de busca com autocomplete por nome/leito, filtros rápidos por severidade (crítico/atenção/normal), ou atalhos de teclado (ex.: `/` para focar busca como no restante do sistema). |
| **16** | Ventilação | H4: Consistency and Standards | HEURÍSTICO | **Baixa** | O grid de parameter cards usa 4 colunas (`lg:grid-cols-4`) para 6 cards, resultando em fileira final com apenas 2 cards desalinhados. O layout visual fica assimétrico. | Ajustar para 3 colunas (`lg:grid-cols-3`) com 2 fileiras de 3 cards, ou 6 colunas (`lg:grid-cols-6`) para tela larga. Alternativa: usar `auto-fill` com `minmax` para grid responsivo. |
| **17** | Piora-Clinica | H4: Consistency and Standards | HEURÍSTICO | **Baixa** | A página exporta um wrapper `ClinicalDeteriorationPageWithBoundary` que duplica o `ErrorBoundary` e renderiza `<Layout>` repetidamente nos estados de loading/erro/empty, enquanto a página principal (`ClinicalDeteriorationPage`) também usa `<Layout>`. Os estados de loading/erro/empty repetem o cabeçalho "Deterioração Clínica" hardcoded em vez de usar um componente compartilhado. | Refatorar para padrão consistente com as outras páginas: único `<Layout>` + `<ErrorBoundary>` no export default, e os estados internos serem apenas o conteúdo (sem repetir Layout). Extrair o cabeçalho para um componente `PageHeader`. |
| **18** | Trilhas | H3: User Control and Freedom | SUBJETIVO | **Baixa** | No modo mobile, ao selecionar um paciente no modo "lista" (`viewMode === 'list'`), a interface automaticamente troca para o modo "board" (`handleSelectPatient`, linha 243-245). Isso pode desorientar o usuário que queria apenas visualizar informações resumidas e não o board completo. | Oferecer transição opcional: manter o modo atual e exibir um botão "Ver pathway board" após selecionar paciente, em vez de forçar a troca automática. |
| **19** | Ventilação | H7: Flexibility and Efficiency | SUBJETIVO | **Baixa** | O gráfico de tendência mostra apenas um parâmetro por vez. Para análise clínica cruzada (ex.: correlacionar FiO₂ com SpO₂), o usuário precisa alternar entre abas e comparar mentalmente. | Adicionar opção "Multi-parâmetro" que plota 2-3 séries sobrepostas no mesmo gráfico com eixos duplos (esquerdo/direito) para parâmetros com unidades diferentes. Ou mini-gráficos sparkline nos cards de parâmetro. |
| **20** | Ventilação | H2: Match System/Real World | SUBJETIVO | **Baixa** | Os parâmetros são apresentados em português (modo, FiO₂, PEEP) mas o toggle de período usa "24 horas" em vez do formato clínico comum "24h". Detalhe cosmético. | Padronizar abreviações conforme prontuário: "24h", "48h", "72h" em vez de "24 horas". Avaliar com equipe clínica o formato preferido. |
| **21** | Trilhas | H8: Aesthetic and Minimalist Design | SUBJETIVO | **Baixa** | A sidebar de pacientes tem 280px fixos. Em telas menores (1280px), o board pathway fica com ~1000px restantes, o que é adequado. Porém, o padding interno do board (p-6 = 24px cada lado) consome 48px adicionais desnecessários em modo split-screen. | Reduzir padding do board para `p-4` (16px) em telas < 1440px via media query ou container query, otimizando o espaço horizontal para dados clínicos. |
| **22** | Estabilidade | H7: Flexibility and Efficiency | SUBJETIVO | **Baixa** | O heatmap de 27 critérios em grid fixo por categoria não permite reordenação ou agrupamento por severidade. Um clínico pode preferir ver todos os critérios "críticos" agrupados no topo, independentemente da categoria. | Adicionar opção de ordenação: "Por categoria" (default) vs "Por gravidade" (críticos primeiro). Ou permitir clique no cabeçalho da coluna para reordenar. |
| **23** | Piora-Clinica | H8: Aesthetic and Minimalist Design | SUBJETIVO | **Baixa** | O label de score no centro do gauge (y+55) pode sobrepor visualmente a agulha em scores intermediários (ex.: score "2"). A geometria atual usa y+55 a partir do centro cy=150, posicionando o texto a 205px de altura — próximo da trajetória da agulha em ~180°-225°. | Ajustar posição Y do label para y+65 ou y+70, ou mover para abaixo do gauge (fora do SVG) como texto separado. Testar visualmente com todos os 5 scores. |
| **24** | Todos | H7: Flexibility and Efficiency | SUBJETIVO | **Baixa** | Nenhum dos 4 domínios oferece atalho de teclado para voltar ao dashboard ou navegar entre domínios relacionados. O `FullScreenLayout` tem atalho `?` para ajuda, mas o `Layout` padrão já provê sidebar. | Adicionar atalhos consistentes: `Ctrl+1` a `Ctrl+4` para os 4 domínios core, `Esc` para voltar ao dashboard. Documentar nos help drawers respectivos. |

---

## Resumo Estatístico

| Classificação | Quantidade | % |
|--------------|-----------|-----|
| **FACTUAL** (bugs) | 6 | 25% |
| **HEURÍSTICO** (issues) | 11 | 46% |
| **SUBJETIVO** (sugestões) | 7 | 29% |
| **TOTAL** | 24 | 100% |

### Por Domínio

| Domínio | FACTUAL | HEURÍSTICO | SUBJETIVO | Total |
|---------|---------|------------|-----------|-------|
| Trilhas-Engine | 1 | 4 | 2 | 7 |
| Ventilação | 1 | 3 | 3 | 7 |
| Estabilidade | 3 | 2 | 1 | 6 |
| Piora-Clinica | 1 | 2 | 1 | 4 |

### Por Severidade

| Severidade | Quantidade |
|-----------|-----------|
| **Crítica** | 1 |
| **Alta** | 4 |
| **Média** | 8 |
| **Baixa** | 11 |

---

## Top 5 Ações Imediatas (Quick Wins)

1. **Corrigir `opacity: 0.12` na RecommendationCard de Estabilidade** — ilegível, risco clínico (1 linha de código)
2. **Remover filtros duplicados no StabilityHeatmap** — confusão de UI (remover ~30 linhas)
3. **Corrigir condição de loading na página de Estabilidade** — nunca mostra skeleton (1 linha)
4. **Remover botões de demo da página de Ventilação em produção** — poluição visual (excluir bloco de ~55 linhas atrás de env flag)
5. **Substituir classes Tailwind hardcoded por tokens no DomainCard de Piora-Clinica** — quebra theming (2 linhas)

---

## Metodologia

**Heurísticas aplicadas (Nielsen Norman, 1994):**

1. Visibility of system status
2. Match between system and the real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, and recover from errors
10. Help and documentation

**Classificação SOUL.md:**
- **FACTUAL:** Viola regra objetiva do código ou especificação → bug que precisa ser corrigido
- **HEURÍSTICO:** Viola boa prática de usabilidade → issue que deve ser endereçado
- **SUBJETIVO:** Preferência de design discutível → sugestão para consideração da equipe

**Arquivos analisados:**
- `frontend-v2/app/care-pathways/page.tsx`
- `frontend-v2/app/ventilation/page.tsx`
- `frontend-v2/app/stability/page.tsx`
- `frontend-v2/app/clinical-deterioration/page.tsx`
- `frontend-v2/components/PathwayBoard.tsx`
- `frontend-v2/components/VentilationTrendChart.tsx`
- `frontend-v2/components/StabilityHeatmap.tsx`
- `frontend-v2/components/ClinicalTimeline.tsx`
- `frontend-v2/components/CriteriaChecklist.tsx`
- `frontend-v2/components/Layout.tsx`
