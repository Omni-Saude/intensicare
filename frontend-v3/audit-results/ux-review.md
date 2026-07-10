# UX Review — IntensiCare Frontend v3

**Data**: 09/07/2026 | **Revisor**: UX Reviewer (subagente)  
**Framework**: Heurísticas de Nielsen (10 princípios)  
**Stack**: Next.js 16 + React 19 + Tailwind CSS 4 | Tema dark  
**Páginas avaliadas**: 6 (Dashboard, Patient Detail, Pathway View, Alert Triage, Pathway Catalog, Admin)

---

## 1. Resumo por Página

### 1.1 Dashboard (`app/page.tsx`)
**Jornada**: "Quantos pacientes? Algum crítico?"

- **StatsBar**: total + contagem de críticos com cor de severidade
- **UnitFilter**: dropdown de unidades (renderizado condicionalmente)
- **BedGrid**: cards de leito com borda esquerda colorida por severidade
- **BedCard**: dot de severidade + nome + leito/unidade + scores MEWS/NEWS2 + badges de trilhas + vitals inline
- **Estados**: loading (6 skeletons), erro (com retry), vazio ("Nenhum paciente internado")
- **Navegação**: 1 clique → Patient Detail

### 1.2 Patient Detail (`app/patient/[mpi_id]/page.tsx`)
**Jornada**: "Quais riscos este paciente apresenta?"

- **PatientHeader**: nome + MPI ID + leito + unidade + scores MEWS/NEWS2 com código de cores
- **Layout 2 colunas** (xl: 3-col): main (vitals, score timeline, active pathways) + sidebar (alerts)
- **VitalsPanel**: grid de sinais vitais com cor de severidade e animação pulse para críticos
- **ScoreTimeline**: sparkline SVG + tabela de dados + indicadores de tendência (↑↓→)
- **ActivePathways**: cards clicáveis com state label + mini progress bar
- **AlertsPanel**: itens de alerta com ações acknowledge/escalate
- **Estados**: loading, erro, not-found, sem mpiId — todos cobertos

### 1.3 Pathway View (`app/patient/[mpi_id]/pathway/[pp_id]/page.tsx`)
**Jornada**: "Qual estado? Quais critérios? O que fazer?"

- **PathwayHeader**: link "Voltar para o paciente" + nome da trilha + trend + severity badge
- **StateFlow**: stepper horizontal com estados passados (✓ verde), atual (glow amarelo), futuros (cadeado cinza)
- **Layout 2 colunas** (lg: 3-col): criteria + recommendations / transition history
- **CriteriaList**: header com resumo (atendidos/não atendidos/pendentes) + linhas expansíveis
- **RecommendationsPanel**: lista de recomendações clínicas acionáveis
- **TransitionHistory**: timeline vertical com dots e motivos de transição
- **Estados**: loading (skeleton fiel ao layout real), erro (com retry), not-found, parâmetros inválidos

### 1.4 Alert Triage (`app/alerts/page.tsx`)
**Jornada**: "Quais alertas ativos?"

- **Header**: contagem total de alertas
- **FilterBar**: dropdowns (severidade/status/período) + filtros expansíveis (unidade/trilha) + botão limpar
- **AlertTable**: header + linhas expansíveis com severity badge, link paciente, link trilha, quick actions
- **QuickActions**: reconhecer/escalar/resolver com input inline de resolução
- **Otimizações**: optimistic updates, auto-refresh 30s, filtragem client-side para unidade/trilha
- **Estados**: loading, erro, vazio, toast de erro global (auto-dismiss 5s)

### 1.5 Pathway Catalog (`app/pathways/page.tsx` → `PathwayGrid`)
**Jornada**: "Quais trilhas existem?"

- **Toolbar**: título + contagem + toggle ativas/todas
- **Grid** de `PathwayDefCard` com expand/collapse → `PathwayDetail`
- **Estados**: loading, erro (com retry), vazio (com sugestão contextual: "Experimente mostrar todas")

### 1.6 Admin (`app/admin/page.tsx`)
**Jornada**: Funcionalidades administrativas

- **Tabbed interface**: Usuários, Thresholds, Tenant, Auditoria
- **ARIA roles**: tablist/tabpanel corretos
- **Estados**: loading/erro delegados aos componentes internos (UserManager, ThresholdEditor, etc.)

---

## 2. Avaliação contra Heurísticas de Nielsen

### H1 — Visibility of System Status ⭐⭐⭐⭐ (BOM)

**Pontos fortes**:
- Todos os componentes tratam loading (skeletons/spinners), erro (alertas coloridos), e vazio
- Pathway View tem skeleton fiel ao layout real (melhor prática)
- BedGrid usa skeleton cards que antecipam a estrutura final
- Alert Table mostra "Carregando alertas…" com spinner animado
- QuickActions mostra Loader2 durante operações assíncronas
- Estados resolved/acknowledged exibem badges visuais (✓, "Resolvido")

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H1-01 | MINOR | Dashboard esconde StatsBar durante loading (`{data && (<StatsBar.../>)}`). Usuário perde referência do cabeçalho de estatísticas durante carregamento inicial |
| H1-02 | MINOR | Nenhum indicador de "última atualização" (timestamp) visível no Dashboard ou Patient Detail. Em ambiente clínico, é crítico saber se os dados são de 30s ou 5min atrás |
| H1-03 | NICE-TO-HAVE | Sem indicadores de conexão WebSocket/live — usuário não sabe se dados estão sendo recebidos em tempo real |

---

### H2 — Match between System and Real World ⭐⭐⭐⭐ (BOM)

**Pontos fortes**:
- PT-BR em todos os labels: "Paciente", "Leito", "Unidade", "Sinais Vitais", "Trilhas Ativas"
- Terminologia clínica correta: MEWS, NEWS2, SpO₂, critérios
- Metáfora de "leito" no Dashboard alinhada ao modelo mental de UTI
- Severidade mapeada para urgência clínica: normal → observação → urgente → crítico
- Ícones clinicamente relevantes: coração para FC, termômetro para temperatura

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H2-01 | MINOR | Aba "Thresholds" no Admin usa termo em inglês. Deveria ser "Limiares" ou "Limites" para consistência com "Usuários" e "Auditoria" |
| H2-02 | MINOR | "Tenant" é um termo técnico de SaaS — equipe clínica pode não entender. Sugestão: "Instituição" ou "Configuração" |
| H2-03 | NICE-TO-HAVE | "MPI ID" sem tooltip — novos residentes podem não conhecer "Master Patient Index" |

---

### H3 — User Control and Freedom ⭐⭐⭐ (REGULAR)

**Pontos fortes**:
- Breadcrumb no header do AppShell com link Home
- "Voltar para o paciente" no PathwayHeader (link explícito de retorno)
- Sidebar persistente com todos os atalhos de navegação
- FilterBar com botão "Limpar" quando filtros ativos
- Navegação hierárquica clara: Dashboard → Patient → Pathway
- AlertRow colapsável (expande/recolhe com clique)

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H3-01 | **MAJOR** | Breadcrumb mostra slugs técnicos em vez de nomes legíveis. Ex: `Patient / [mpi Id] / Pathway / [pp Id]`. O algoritmo `seg.replace(/-/g, ' ')` não resolve placeholders dinâmicos. Intensivista não sabe onde está na hierarquia |
| H3-02 | MINOR | Ações acknowledge/escalate em alertas não têm undo. Uma vez clicado, o estado é commitado sem confirmação |
| H3-03 | MINOR | Alert Triage page não tem link rápido "Voltar ao Dashboard" no header da página — só sidebar |

---

### H4 — Consistency and Standards ⭐⭐⭐ (REGULAR)

**Pontos fortes**:
- Design tokens via CSS custom properties consistentes: `--severity-*`, `--surface-*`, `--text-*`, `--border-*`
- Padrão de seção consistente: `<section>` + `<h2>` uppercase tracking-wider + border padrão
- Loading: skeleton boxes com `animate-pulse` em todos os componentes
- Erro: borda `--severity-critical` + fundo `--severity-critical-wash` em todos os componentes
- Vazio: ícone centralizado + mensagem + texto de ajuda contextual
- ARIA labels em todos os elementos interativos

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H4-01 | **MAJOR** | Mistura inconsistente de `className` e `style` inline para cores. Admin page usa `style={{ color: 'var(--text-primary)' }}` enquanto outros componentes usam `className="text-[var(--text-primary)]"`. Mesmo componente (Admin) mistura ambos |
| H4-02 | MINOR | Padding inconsistente entre seções: `p-4` vs `p-5` vs `p-6` sem critério claro |
| H4-03 | MINOR | Botões com estilização inconsistente — alguns via className, outros via style objects |
| H4-04 | MINOR | Mix de idiomas: "Thresholds" (EN) vs "Usuários/Auditoria" (PT) em abas Admin |

---

### H5 — Error Prevention ⭐⭐ (FRACO)

**Pontos fortes**:
- Alert actions têm estado `disabled` durante operações assíncronas (actingIds Set / isBusy)
- Login tem validação client-side (`required` nos campos)
- FilterBar usa tipos TypeScript para prevenir combinações inválidas de filtro
- Resolve alert exige input de resolução antes de confirmar
- Escape key fecha input de resolução

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H5-01 | **CRITICAL** | Botão "Sair" (logout) no AppShell não tem confirmação. Um clique acidental no meio de um plantão de 24h encerra a sessão sem aviso. Em ambiente de UTI com luzes baixas e fadiga, o risco é alto |
| H5-02 | **MAJOR** | Botão "Escalar" em AlertItem não tem confirmação. Escalar um alerta pode ter consequências clínicas (notificar outros profissionais), e não há diálogo de confirmação |
| H5-03 | MINOR | Login form só tem validação HTML `required`. Sem validação de formato, sem feedback de campo específico |
| H5-04 | MINOR | Componentes Admin (UserManager, ThresholdEditor) — ações de delete/save não foram revisadas mas provavelmente precisam de confirmação |

---

### H6 — Recognition rather than Recall ⭐⭐⭐⭐ (BOM)

**Pontos fortes**:
- Cores de severidade são o atributo visual primário — consistentes em todo o app:
  - Verde = normal, Amarelo = observação, Laranja = urgente, Vermelho = crítico
- StateFlow mostra estados com ícones intuitivos: ✓ check (passado), ⊙ glow (atual), 🔒 lock (futuro)
- Mini progress bars com código de cores (≥80% verde, ≥50% amarelo, <50% laranja)
- MEWS/NEWS2 com cores por faixa de valor (≥7 crítico, ≥5 urgente, ≥3 observação)
- Severity dots + badges + bordas laterais — três canais visuais redundantes para a mesma informação
- Tabela de scores mostra tendência com ícones ↑↓→

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H6-01 | MINOR | AlertRow no estado colapsado mostra informação mínima — usuário precisa expandir para ver detalhes, mas ao recolher perde o contexto (força memorização de qual alerta expandiu) |
| H6-02 | MINOR | PathwayDefCard no catálogo não mostra contagem de critérios ou estados no estado colapsado — requer expandir |
| H6-03 | NICE-TO-HAVE | Sem "recentes" ou "favoritos" para acesso rápido entre trocas de plantão |

---

### H7 — Flexibility and Efficiency of Use ⭐⭐ (FRACO)

**Pontos fortes**:
- Um clique do Dashboard ao Patient Detail
- AlertRow com expand inline para acesso rápido
- Auto-refresh de alertas a cada 30s
- FilterBar preserva estado dos filtros
- Resolve alert com input inline (sem modal)
- Toggle ativas/todas no catálogo de trilhas

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H7-01 | **MAJOR** | Zero atalhos de teclado para power users. Intensivistas experientes não têm: tecla para próximo paciente crítico, atalho para acknowledge all, tecla para voltar ao dashboard |
| H7-02 | MINOR | Dashboard sem busca/filtro textual de pacientes. Intensivista precisa escanear visualmente todos os leitos para encontrar um paciente específico |
| H7-03 | MINOR | Sem operações em lote nos alertas (acknowledge all visíveis, resolve all filtrados) |
| H7-04 | NICE-TO-HAVE | Sem toggle de tema claro/escuro. Embora dark seja apropriado para UTI noturna, plantão diurno pode preferir light mode |
| H7-05 | NICE-TO-HAVE | Sem personalização de dashboard (ordenar leitos, esconder/mostrar colunas) |

---

### H8 — Aesthetic and Minimalist Design ⭐⭐⭐⭐⭐ (EXCELENTE)

**Pontos fortes**:
- Tema dark otimizado para UTI com luzes baixas: `#0a0e14` canvas, `#141b22` raised, `#1c2530` overlay
- Densidade de informação alta sem poluição visual — cada card de leito tem 6+ dados mas mantém clareza
- Severidade como diferenciador visual primário: borda colorida + dot + badge (três canais)
- Hierarquia visual clara: scores grandes e coloridos → detalhes menores e secundários
- Animações sutis: pulse em críticos (atenção médica), transições hover, chevron rotate no expand
- Consistência de border-radius (`--radius-sm/md/lg`) e espaçamento
- Uso excelente de whitespace entre seções (`space-y-6`)

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H8-01 | MINOR | StatsBar mostra contagem de críticos duas vezes: no resumo geral (`"X críticos"`) e em destaque separado com AlertTriangle. Redundância leve |
| H8-02 | MINOR | FilterBar ocupa espaço vertical significativo (~100px) antes da lista de alertas |
| H8-03 | NICE-TO-HAVE | Scores MEWS/NEWS2 no PatientHeader poderiam ser mais proeminentes (são a informação mais crítica da página) |
| H8-04 | NICE-TO-HAVE | Poderia usar micro-interações (ex: número anima ao atualizar) para reforçar que dados são live |

---

### H9 — Help Users Recognize, Diagnose, and Recover from Errors ⭐⭐⭐ (REGULAR)

**Pontos fortes**:
- Mensagens de erro incluem o texto real do erro (não apenas "Algo deu errado")
- BedGrid erro tem botão "Tentar novamente" com RefreshCw icon
- Pathway View erro tem botão "Tentar novamente"
- Alert page tem toast de erro global com auto-dismiss (5s)
- Estados vazios frequentemente incluem texto de ajuda contextual:
  - "As trilhas são ativadas automaticamente quando os critérios clínicos são atendidos"
  - "As recomendações clínicas aparecerão aqui quando disponíveis"

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H9-01 | MINOR | Mensagens de erro mostram apenas `Error.message` cru — sem sugestão de próximo passo (ex: "Verifique sua conexão", "Contate o administrador", "Tente novamente em alguns minutos") |
| H9-02 | MINOR | Sem detecção de offline/network error — usuário vê erro genérico quando API está inacessível, sem saber se é rede, servidor, ou auth |
| H9-03 | NICE-TO-HAVE | Sem log/histórico de erros visível para o usuário reportar ao suporte |

---

### H10 — Help and Documentation ⭐⭐ (FRACO)

**Pontos fortes**:
- Textos de ajuda em estados vazios (contextual help)
- ARIA labels descritivos em elementos interativos
- Labels e placeholders claros nos formulários

**Problemas**:

| ID | Severidade | Descrição |
|----|-----------|-----------|
| H10-01 | **MAJOR** | Zero tooltips em abreviações clínicas (MEWS, NEWS2, SpO₂). Novos residentes ou profissionais em treinamento podem não conhecer todos os acrônimos |
| H10-02 | MINOR | Sem onboarding/tutorial para primeiro acesso |
| H10-03 | MINOR | Sem link de ajuda ou documentação em lugar nenhum da aplicação |
| H10-04 | NICE-TO-HAVE | Sem ajuda contextual em conceitos complexos como "estados de trilha" ou "avaliação de critérios" |
| H10-05 | NICE-TO-HAVE | Sem indicador visual do que cada cor de severidade significa (legenda) |

---

## 3. Análise de Carga Cognitiva

### 3.1 Decisões por Tela

| Página | Decisões/Tela | Complexidade | Nota |
|--------|---------------|-------------|------|
| Dashboard | ~1 (qual paciente precisa de atenção?) | Baixa | ✅ |
| Patient Detail | ~2-3 (qual severidade? trilhas ativas? alertas?) | Média | ✅ |
| Pathway View | ~2 (qual estado? critérios atendidos? o que fazer?) | Média | ✅ |
| Alert Triage | ~2 (qual alerta agir? como filtrar?) | Média | ✅ |
| Pathway Catalog | ~1 (qual trilha explorar?) | Baixa | ✅ |
| Admin | ~1 (qual aba?) | Baixa | ✅ |

**Conclusão**: Carga de decisão bem distribuída. Nenhuma tela sobrecarrega com escolhas excessivas.

### 3.2 Hierarquia Visual

**O que funciona:**
- Dashboard: severidade → nome do paciente → scores → leito/unidade → trilhas
- Patient Detail: scores MEWS/NEWS2 (grandes, coloridos) → sinais vitais → trilhas → alertas
- Pathway View: estado atual (glow) → critérios → recomendações → histórico
- Alert Triage: severidade → paciente → mensagem → data → ações

**O que poderia melhorar:**
- Scores MEWS/NEWS2 no PatientHeader: estão à direita, tamanho `text-2xl`. Para a pergunta "quais riscos?", esses números são a resposta primária e poderiam ser `text-3xl` ou `text-4xl` com mais destaque
- No Dashboard, a informação de unidade/leito compete visualmente com scores — a hierarquia poderia ser mais explícita (scores primeiro)

### 3.3 Affordance (Elementos clicáveis parecem clicáveis?)

| Elemento | Affordance | Nota |
|----------|-----------|------|
| BedCard | ✅ cursor-pointer + hover + focus-visible ring + role="button" + tabIndex | Excelente |
| PathwayCard | ✅ cursor-pointer + hover shadow/border + focus ring + role="button" + ChevronRight animado | Excelente |
| CriteriaRow | ✅ hover bg + cursor + chevron animado + focus ring | Excelente |
| AlertRow (colapsável) | ✅ cursor-pointer + expand chevron + focus ring + role="button" + aria-expanded | Excelente |
| Botões de ação | ✅ estilos de botão claros, disabled state | Bom |
| Sidebar links | ✅ hover + active state + ícones | Bom |
| Admin tabs | ✅ active/inactive states + role="tab" + aria-selected | Bom |

**Conclusão**: Affordance está **muito bem implementada** em todos os componentes interativos. Uso consistente de cursor-pointer, hover states, focus-visible rings, e roles ARIA apropriados.

---

## 4. Resumo de Classificação

### 🔴 CRITICAL (1)
| ID | Página | Descrição |
|----|--------|-----------|
| H5-01 | AppShell | Logout sem confirmação — risco de perda de sessão em ambiente de UTI |

### 🟠 MAJOR (5)
| ID | Página | Descrição |
|----|--------|-----------|
| H3-01 | AppShell | Breadcrumb mostra slugs brutos (`[mpi Id]`) em vez de nomes reais |
| H4-01 | Várias | Mistura inconsistente de className e style inline para cores |
| H5-02 | Patient/Alerts | Escalar alerta sem confirmação (consequências clínicas) |
| H7-01 | Global | Zero atalhos de teclado para power users |
| H10-01 | Global | Zero tooltips em abreviações clínicas (MEWS, NEWS2, SpO₂) |

### 🟡 MINOR (16)
| ID | Página | Descrição |
|----|--------|-----------|
| H1-01 | Dashboard | StatsBar desaparece durante loading |
| H1-02 | Dashboard/Patient | Sem indicador de "última atualização" |
| H2-01 | Admin | "Thresholds" em inglês vs "Usuários/Auditoria" em português |
| H2-02 | Admin | "Tenant" é jargão técnico |
| H3-02 | Patient/Alerts | Ações acknowledge/escalate sem undo |
| H3-03 | Alerts | Sem link rápido "Voltar ao Dashboard" |
| H4-02 | Várias | Padding inconsistente entre seções (p-4/p-5/p-6) |
| H4-03 | Várias | Estilização de botões inconsistente |
| H4-04 | Admin | Mix de idiomas nas abas |
| H5-03 | Login | Sem validação além de HTML required |
| H5-04 | Admin | Possível falta de confirmação em ações admin |
| H6-01 | Alerts | AlertRow colapsado perde contexto |
| H6-02 | Pathways | PathwayDefCard não mostra critérios/estados colapsado |
| H7-02 | Dashboard | Sem busca textual de pacientes |
| H7-03 | Alerts | Sem operações em lote |
| H8-01 | Dashboard | StatsBar mostra contagem de críticos redundantemente |
| H8-02 | Alerts | FilterBar ocupa espaço vertical significativo |
| H9-01 | Várias | Mensagens de erro sem sugestão de próximo passo |
| H9-02 | Várias | Sem detecção de offline |
| H10-02 | Global | Sem onboarding/tutorial |
| H10-03 | Global | Sem link de ajuda/documentação |

### 🔵 NICE-TO-HAVE (10)
| ID | Página | Descrição |
|----|--------|-----------|
| H1-03 | Global | Sem indicadores de live update/WebSocket |
| H2-03 | Patient | "MPI ID" sem tooltip |
| H6-03 | Global | Sem "recentes/favoritos" |
| H7-04 | Global | Sem toggle light/dark mode |
| H7-05 | Dashboard | Sem personalização de layout |
| H8-03 | Patient | Scores MEWS/NEWS2 poderiam ser maiores |
| H8-04 | Global | Micro-interações em dados live |
| H9-03 | Global | Sem log de erros visível |
| H10-04 | Pathway | Sem ajuda contextual em conceitos complexos |
| H10-05 | Global | Sem legenda de cores de severidade |

---

## 5. Nota Geral

| Dimensão | Nota | Peso |
|----------|------|------|
| Visibility of system status (H1) | 8/10 | 15% |
| Match system ↔ real world (H2) | 8/10 | 10% |
| User control and freedom (H3) | 6/10 | 10% |
| Consistency and standards (H4) | 6/10 | 10% |
| Error prevention (H5) | 4/10 | 15% |
| Recognition rather than recall (H6) | 8/10 | 10% |
| Flexibility and efficiency (H7) | 4/10 | 10% |
| Aesthetic and minimalist (H8) | 9/10 | 10% |
| Help users recover from errors (H9) | 6/10 | 5% |
| Help and documentation (H10) | 4/10 | 5% |

### **Nota final ponderada: 6.3 / 10**

---

## 6. Destaques Positivos

1. **Sistema de severidade visual excepcional**: 4 cores + 3 canais redundantes (dot, borda, badge). Implementação consistente em todos os componentes com animação pulse para casos críticos. Isso salva vidas em UTI.

2. **Tratamento completo de estados**: Todo componente tem loading (skeleton), erro (com ação), e vazio (com ajuda contextual). Pathway View inclusive tem skeleton que replica fielmente o layout real — padrão de excelência.

3. **Affordance impecável**: Todo elemento interativo tem cursor-pointer, hover state, focus-visible ring, role ARIA e keyboard navigation. Acessibilidade bem implementada.

4. **Design visual coeso**: Design tokens via CSS custom properties, tema dark otimizado para UTI, hierarquia visual clara. A densidade de informação é alta sem sacrificar clareza.

5. **Jornada do intensivista respeitada**: Dashboard → Patient → Pathway em ≤2 cliques. Informação crítica visível sem scroll. Severidade como atributo visual primário.

---

## 7. Recomendações Prioritárias

### Sprint Imediato (corrigir antes do go-live)
1. **H5-01**: Adicionar diálogo de confirmação no logout
2. **H5-02**: Adicionar confirmação na ação "Escalar" alerta
3. **H3-01**: Corrigir breadcrumb para mostrar nomes reais (PatientDetail → "Fulano de Tal", Pathway → "SEPSE - Triagem")

### Sprint Seguinte
4. **H10-01**: Adicionar tooltips em MEWS, NEWS2, SpO₂ e outros acrônimos
5. **H7-01**: Implementar atalhos de teclado básicos (Ctrl+1 Dashboard, Ctrl+2 Alertas, setas para navegar pacientes)
6. **H4-01**: Padronizar estilização — escolher className ou style objetos e aplicar consistentemente

### Backlog
7. **H7-02**: Adicionar busca textual no Dashboard
8. **H9-01**: Melhorar mensagens de erro com sugestões de ação
9. **H10-02**: Criar onboarding simples para primeiro acesso
10. **H2-01**: Renomear "Thresholds" → "Limiares", "Tenant" → "Instituição"

---

*Relatório gerado por subagente UX Reviewer. Baseado em análise estática do código-fonte das 6 páginas core e 30+ componentes do IntensiCare Frontend v3.*
