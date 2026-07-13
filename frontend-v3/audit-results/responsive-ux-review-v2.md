# UX Review v2: Responsive + Alert-Consolidation Re-Audit — IntensiCare Frontend v3

**Data:** 2026-07-13
**Revisor:** Re-auditor UX (flywheel, rodada v2) — Chromium real (Playwright headless), stack viva `:3000`/`:8000`
**Heurísticas:** Nielsen 10 + carga cognitiva + affordance + hierarquia visual + feedback + alarm fatigue (clínica)
**Baseline:** `/audit-results/responsive-ux-review.md` (v1, score 8.0/10, CONDITIONAL-GO, 4 MAJOR + 4 MINOR + 2 NICE-TO-HAVE)
**Mudanças testadas ao vivo:** drawer com focus trap (`app-shell.tsx`), grid críticos-primeiro (RF-007, `bed-grid.tsx`), visão agrupada default + títulos humanizados + badge "Escalando" (ADR-0039, `alert-table.tsx`/`alert-group-row.tsx`), cap `max-w-md` no BedCard (RF-019), `cooldown_minutes` 0→15 no seed
**Método:** navegação real via Playwright/Chromium (login UI, não injeção de cookie), viewports 320×690 e 512×800, screenshots + inspeção de DOM/computed-style + chamadas diretas à API para quantificar ruído de alertas. Artefatos: `/private/tmp/claude-501/-Users-familia-intensicare/2ddd8939-1ffb-4de3-9d7a-7a418c3d7b1a/scratchpad/reaudit-ux/artifacts/` (screenshots numerados + `report.json`/`report2.json`)

---

## UX Score — Nielsen v1 → v2 (por heurística, com delta)

| Dimensão | Peso | v1 | v2 | Δ | Justificativa da mudança |
|---|:--:|:--:|:--:|:--:|---|
| Visibility of system status | 1.5 | 8.5 | 9.3 | **+0.8** | U4 (StatsBar `flex-wrap`) confirmado ao vivo (screenshot 08, sem overflow em 320/512). U6 (SeverityDot) ganhou pista não-cromática (anel + tamanho crescente, ver `severity-dot.tsx:20-34`) — daltônico agora distingue watch/urgent sem depender só de cor. Header do `/alerts` agora expõe `N grupos · M alertas` — visibilidade nova do ruído bruto vs. consolidado. |
| Match between system and real world | 1.0 | 9.0 | 9.3 | **+0.3** | Títulos de alerta humanizados confirmados ao vivo: `"NEWS2 crítico — 19"` em vez do score_type cru (ADR-0039 §6). Mensagens 3 partes (o que aconteceu/por que importa/o que verificar) citam referência clínica (Royal College of Physicians NEWS2 2017) — mais próximo do vocabulário clínico real. |
| User control and freedom | 1.0 | 8.0 | 8.7 | **+0.7** | U7 (scroll perdido no filtro) corrigido (RF-020). Drawer ganhou Escape real + retorno de foco ao botão que abriu (confirmado ao vivo). "Reconhecer grupo" tem passo de confirmação explícito (Confirmar/Cancelar) antes de executar N acks — boa contenção, mas ainda sem "desfazer" pós-execução (mesma lacuna do v1, agora com blast radius maior — ver Trade-offs). |
| Consistency and standards | 1.0 | 9.0 | 9.3 | **+0.3** | U8 (`text-[10px]`) migrado para `text-2xs` (bed-card.tsx:116, confirmado). Padrão de labels inline `sm:hidden` do AlertRow foi replicado 1:1 no AlertGroupRow — mesmo idioma visual nas duas visões. |
| Error prevention | 1.5 | 8.5 | 8.8 | **+0.3** | Ack de grupo tem gate de confirmação com contagem explícita ("Reconhecer 9 alertas de ... — Crítico?") — prevenção de erro mais forte que o ack individual de 1 clique que já existia. Falhas parciais no ack de grupo são reportadas por ID (`Falhas: #123 (mensagem)`), não silenciadas. |
| Recognition rather than recall | 1.5 | 7.0 | 8.7 | **+1.7** | U1 (headers ausentes) mitigado por dois ângulos simultâneos: labels inline `sm:hidden` em TODO campo (paciente/sinal/ocorrências/janela) E a visão agrupada default reduz a quantidade de itens a reconhecer (25 grupos vs. 88 alertas soltos no dataset de teste). U3 (ícones sem texto) eliminado — `QuickActions` não tem mais `hidden sm:inline`; texto sempre visível (confirmado no código, sem classe condicional). U10 (StateFlow sem indicador de overflow) corrigido de forma mais sofisticada que um `sm:hidden` estático: `ResizeObserver` mede overflow real e só aplica o fade quando há conteúdo escondido (RF-021) — evita o problema oposto (fade decorativo sem função). |
| Flexibility and efficiency of use | 1.5 | 7.0 | 9.2 | **+2.2** | Maior ganho do ciclo. U2 (sem sort por severidade) resolvido — confirmado ao vivo: dashboard 320px abre com "12 pacientes • 11 críticos" e os 5 primeiros cards visíveis são TODOS críticos (border-left `rgb(255,112,119)`), sem precisar de scroll para localizar o primeiro crítico. "Reconhecer grupo" reduz N cliques a 1+confirmação (medido: grupo de 9 ocorrências → 1 clique de expand + 1 de reconhecer, vs. 9 acks individuais no fluxo antigo). |
| Aesthetic and minimalist design | 1.0 | 8.0 | 8.8 | **+0.8** | U5 duplo-corrigido: `<main>` mudou de `p-6` fixo para `p-4 sm:p-6` (16px em 320px vs. 24px antes — reclama espaço horizontal clínico); BedCard ganhou `max-w-md` (confirmado por medição ao vivo: `boundingBox.width === 448px` exatos em viewport 512px, não mais ~488-512px esticado). |
| Help users recover from errors | 1.0 | 9.0 | 9.2 | **+0.2** | Ack de grupo com falha parcial soma um caso de erro novo e bem tratado (contagem de sucesso/falha + IDs). Resto inalterado do v1 (já era forte). |
| Help and documentation | 0.5 | 8.0 | 8.0 | 0 | Sem mudança observada nesta rodada (fora do escopo dos commits revisados). |
| Carga cognitiva | 1.5 | 7.5 | 8.8 | **+1.3** | Ver §4 abaixo — critical-first elimina a busca linear que era o maior redutor de nota em v1; view agrupada elimina reconhecimento repetido de severidade quando o mesmo sinal dispara várias vezes seguidas. |
| Affordance | 1.0 | 8.5 | 8.7 | **+0.2** | QuickActions com texto visível reforça affordance dos botões (antes dependia só do ícone). Resto inalterado. |
| Hierarquia visual | 1.0 | 8.0 | 8.5 | **+0.5** | Card de grupo colapsado já expõe, em ordem: severidade (badge pulsante) → paciente → sinal → contagem em negrito → janela temporal → ação — hierarquia mais informativa por item do que uma linha de AlertRow crua. |
| Feedback (loading/empty/error) | 1.0 | 9.5 | 9.6 | **+0.1** | Ack de grupo tem feedback de progresso ("Reconhecendo 3/9…") — novo. Gap do v1 permanece: ações individuais (ack/escalate/resolve) ainda não têm toast de sucesso, só atualização otimista silenciosa da linha. |

**Score bruto (v2, não ponderado):** 8.92 / 10 (v1: 7.96)
**Score ponderado (v2):** 8.96 / 10 (v1: 8.20)
**Arredondado:** **9.0 / 10** (v1: 8.0) — **Δ +1.0**

---

## 1. Jornada do Intensivista — 320px Noturno (re-testada ao vivo)

### 1.1 Dashboard

Confirmado por screenshot (`01-320-dashboard.png`) e inspeção DOM: viewport 320×690, login real via UI, dashboard carrega com banner `"12 pacientes • 11 críticos"` (StatsBar com `flex-wrap`, sem overflow) e os **5 primeiros cards renderizados são todos severidade crítica** (`border-left-color: rgb(255,112,119)`), incluindo pacientes com MEWS/NEWS2 díspares (5, 11, 12, 12) — confirma que a ordenação é por `SEVERITY_RANK` (crítico→urgente→observação→normal) e não por score numérico, exatamente como implementado em `bed-grid.tsx:19-31` (RF-007).

**Veredito U2 (v1 MAJOR):** **RESOLVIDO.** O intensivista não precisa mais fazer scroll manual para localizar o primeiro paciente crítico — ele já está no topo. Isto elimina o pior item da carga cognitiva do v1 ("Rapidez para encontrar TODOS os críticos: 4/10").

### 1.2 Drawer mobile — focus trap (não testado no v1)

Testado ao vivo: abrir o menu hambúrguer (`aria-label="Abrir menu"`) muda o `<aside>` para `role="dialog"` + `aria-modal="true"` e move o foco para o botão "Fechar menu" automaticamente. Uma sequência de 8 `Tab` consecutivos foi rastreada e **todos os 8 elementos focados permaneceram dentro de `#app-sidebar`** (nav links → shortcuts hint → logout → logo → close button, em loop) — o trap segura corretamente, sem vazar foco para o conteúdo por trás do overlay. `Escape` fecha o drawer e devolve o foco exatamente ao botão hambúrguer que o abriu (confirmado: `document.activeElement.getAttribute('aria-label') === "Abrir menu"` após o Escape).

**Veredito:** **Implementação correta e completa** do padrão WAI-ARIA APG para dialog modal — Tab-trap, Escape, retorno de foco. Sem achados neste componente.

### 1.3 Patient Detail → Pathway View

Navegação real a partir do primeiro card crítico (`DEMO Sepse Crítica`) chega em `/patient/MPI-DEMO-001`; a partir daí, um card de trilha ativa (`role="button"`, não `<a href>` — usa `router.push`) leva a `/patient/MPI-DEMO-001/pathway/40` (screenshot `202-320-pathway-view.png`). O layout em 320px permanece robusto (empilhamento vertical, `Critérios (15)` legível).

**Achado novo (fora do escopo dos fixes revisados, honestidade):** o breadcrumb no topo da Pathway View ("Início › Paciente › DEMO Sepse Crítica › Trilha › Sepse") **quebra em 3 linhas** em 320px (medido: `boundingBox.height = 60px` para o `<nav aria-label="Breadcrumb">`), competindo por espaço vertical com o botão hambúrguer no header de 64px de altura. Não estava no escopo dos 10 achados do v1 (que só testou breadcrumbs de 1-2 níveis) e não bloqueia leitura, mas é uma regressão de densidade em rotas profundas (3 segmentos) que vale registrar para o próximo ciclo.

**Limitação da verificação:** a trilha alcançada só tinha 1 estado (`Triagem Inicial`), então o fix RF-021 do `StateFlow` (fade condicional via `ResizeObserver`) não pôde ser観servado em overflow real neste dataset — confirmado apenas por leitura de código (`state-flow.tsx`, commit `fdafbbb`), não por captura visual do fade ativo.

---

## 2. Densidade de Informação — Split-Screen (~512px)

Medido ao vivo (viewport 512×800, screenshot `08-512-dashboard.png`):

- **BedCard `max-w-md`:** `boundingBox.width === 448px` exatos (28rem, o passo de escala Tailwind citado na recomendação do v1) — confirmado por medição de elemento real, não inferência de código. O grid track (`gridTemplateColumns: "480px"`, 1 coluna) deixa ~32px de respiro visível à direita do card no screenshot, em vez do card esticar até a borda como em v1.
- **AlertGroupTable headers em ~512px:** medido `display: none` / `offsetParent: null` no elemento `.hidden.sm\:flex` — ou seja, os headers de coluna **continuam ocultos em 512px**, pois o breakpoint `sm` do Tailwind é 640px por padrão e este projeto não o customiza.

  **Correção ao v1:** a tabela da seção 2 do relatório original afirma "`hidden sm:flex` headers **VISÍVEIS** (>640px)" com ✅ para o cenário de 512px — isso é **inconsistente com a própria condição citada** (512 < 640) e a medição ao vivo desta rodada confirma que os headers estão de fato ocultos em 512px, não visíveis. Não é uma regressão introduzida pelos fixes — é uma imprecisão do relatório v1 que esta rodada corrige. Na prática o impacto é nulo: tanto o `AlertRow` quanto o novo `AlertGroupRow` já carregam labels inline `sm:hidden` que cobrem exatamente essa lacuna abaixo de 640px.

**Veredito:** densidade **adequada e mensuravelmente melhorada** — a recomendação de curto-prazo #5 do v1 ("adicionar `max-w-md`") foi implementada exatamente como sugerido.

---

## 3. AlertTable → AlertGroupTable — a consolidação ajuda ou atrapalha a percepção de gravidade?

Esta é a mudança mais estrutural desde o v1 (não era um dos 10 achados originais — é uma feature nova, ADR-0039/FASE 2B.1) e foi avaliada como pedido: **como UX evaluator, não como changelog.**

### O que mudou, medido ao vivo

Com `status=all` (para expor o dataset histórico completo e não só a fila ativa, que no momento do teste tinha apenas 1 alerta ativo): **88 alertas brutos → 25 grupos** (razão de ruído 3,52×; 22 dos 25 grupos têm `count > 1`). O header da página de Alertas exibe isso diretamente: `"25 grupos · 88 alertas"` — o intensivista vê o fator de compressão sem precisar calcular nada.

Card de grupo **colapsado** (sem nenhum clique de expandir), capturado ao vivo:
```
[Crítico ●]  Paciente: Paciente Teste MPI-001
Sinal: NEWS2
Ocorrências: 9 ocorrências
Janela: há 3.2h · janela de 16 min
[Reconhecer grupo]
```

### Avaliação — ajuda

1. **Tempo-para-identificar-crítico melhora, não piora.** A severidade do grupo é `max_severity` — o pior caso dentre os membros — exibida no mesmo badge pulsante `severity-critical-pulse` que já existia no AlertRow individual. Nada foi perdido na "força" do sinal visual; o que mudou é que agora **1 badge representa 9 eventos** em vez do intensivista ter que escanear 9 badges idênticos em sequência (ruído de repetição, não de informação).
2. **Contagem + janela temporal são, por si só, um dado clínico que o AlertTable v1 não comunicava.** "9 ocorrências em 16 minutos" é um sinal de deterioração aguda que 9 linhas soltas — cada uma competindo por atenção igual — obscurecem. Isso é diretamente relevante a fadiga de alarme: agrupar não é só "menos scroll", é uma leitura clínica que só emerge da agregação (frequência de disparo).
3. **Ação em lote reduz fricção sem reduzir segurança.** "Reconhecer grupo" exige confirmação explícita com contagem ("Reconhecer 9 alertas de Paciente Teste MPI-001 — NEWS2 Crítico?") antes de disparar — 9 chamadas sequenciais e auditadas individualmente no backend (ADR-0039 §4: "o backend NÃO ganha estado de grupo"), não um estado-fantasma. Cada acknowledge continua sendo uma transição de estado individual rastreável.

### Avaliação — trade-offs reais (honestidade pedida, não é torcida)

1. **Um clique a mais para ver membros individuais é real.** Para ver o `title` humanizado de cada uma das 9 ocorrências (`"NEWS2 crítico — 11"`, `"NEWS2 crítico — 19"` etc., cada uma com timestamp e mensagem própria), é necessário expandir o grupo — confirmado ao vivo (clique + 470-481ms de render). No fluxo antigo (flat), essas 9 linhas já estavam todas visíveis (com scroll). Se o intensivista precisa da timeline exata de escalonamento minuto-a-minuto (não só "houve uma janela de 16 min"), a visão agrupada exige esse clique extra — o toggle "Lista completa" continua existindo exatamente para esse caso, o que é a mitigação correta, mas ainda é uma decisão que o usuário precisa saber tomar.
2. **`escalating` não pôde ser observado ao vivo neste dataset** — de 25 grupos ativos+históricos, **zero** têm `escalating: true` no momento do teste. O badge "Escalando" (com fix de contraste AA documentado no commit `4d5b6ea`, contraste calculado 7.217:1 vs. 4.483:1 da versão anterior) existe e está implementado corretamente por leitura de código, mas esta rodada não pôde capturar sua aparência real em tela — é uma lacuna de cobertura do teste, não uma dúvida sobre a implementação.
3. **Risco de "grupo aparentemente resolvido, mas com membro novo por trás":** por design (ADR-0039 §4), uma nova ocorrência após o ack do grupo inteiro reabre o grupo na visão default — comportamento correto e documentado — mas depende de o intensivista confiar que o sistema vai "reaparecer" o grupo, em vez de assumir "já resolvi isso, não preciso olhar de novo". Isso é uma mudança de modelo mental (de "cada linha é um evento" para "cada card é uma situação em andamento") que não é automaticamente intuitiva para um usuário eventual/plantonista — o mesmo público que o v1 já sinalizava como vulnerável ao problema de headers ausentes (U1).
4. **A visão "Lista completa" (flat) não desapareceu** — é 1 clique de distância via toggle "Por paciente/sinal" / "Lista completa" no topo da página, testado e confirmado funcional. Isso preserva a flexibilidade para quem prefere o modelo antigo.

### Veredito da seção 3

**A consolidação melhora a percepção de gravidade agregada e a eficiência de resposta, sem enfraquecer o sinal individual de severidade — mas desloca o custo de "ver tudo" de scroll passivo para 1 clique ativo por grupo.** Para o cenário que motivou a mudança (burst de 53-88 alertas do mesmo sinal por falha de cooldown), o ganho é claramente positivo. Para o cenário raro de precisar da timeline fina de um grupo específico, o custo é real mas pequeno e tem rota de escape (toggle de lista completa). Não identifiquei um caso onde a consolidação **esconde** um alerta crítico — `max_severity` sempre soma o pior membro, e a arquitetura de leitura (ADR-0039 §1: "a fonte de verdade nunca é fundida") garante que nenhum evento é perdido, só reapresentado.

---

## 4. Carga Cognitiva — Identificação de Leitos Críticos em 320px (re-medida)

| Tarefa | v1 | v2 | Evidência da mudança |
|---|:--:|:--:|---|
| Identificar paciente crítico no dashboard | 9/10 | 9/10 | Inalterado — tripla redundância (dot pulsante + borda + scores coloridos) já era forte. |
| Encontrar TODOS os críticos (320px) | 4/10 | **9/10** | Critical-first sort confirmado ao vivo: não há mais busca linear. Os críticos ocupam o topo determinístico da lista. |
| Distinção critical vs urgent (daltonismo) | 7/10 | **8.5/10** | `SeverityDot` ganhou anel + tamanho crescente por nível (código, `severity-dot.tsx:20-34`) — não depende só de matiz de cor. Não testado com simulador de daltonismo real nesta rodada (limitação). |
| Reconhecer gravidade agregada de um sinal recorrente | N/A (não existia) | **8.5/10** | Novo em v2: "9 ocorrências em 16 min" comunica em 1 linha o que antes exigia ler 9 linhas separadas e inferir a frequência mentalmente. |
| Agir sobre um alerta (acknowledge) — mobile | 6/10 | **8/10** | U3 resolvido (texto sempre visível nos botões, sem precisar decorar ícone). |
| Agir sobre um grupo inteiro (ack em lote) | N/A | **8/10** | 1 clique de expandir intenção + 1 de confirmar substitui N acks manuais; contagem explícita na confirmação evita erro por escala ("reconhecer 9 alertas" é dito antes de acontecer). |

**Carga cognitiva geral v2: 8.8/10** (v1: 7.5/10, **Δ +1.3**) — o maior fator de melhora é a eliminação da busca linear (U2) combinada com a redução do número bruto de itens a escanear via agrupamento. O trade-off documentado na seção 3 (1 clique extra para detalhe por membro) é pequeno frente ao ganho de não precisar mais escanear 9 linhas quase-idênticas para perceber que são "o mesmo sinal, 9 vezes".

---

## Alarm Fatigue — avaliação sob a ótica clínica

Contexto medido ao vivo via API (`GET /api/v1/alerts` vs `GET /api/v1/alerts?group_by=signal`, ambos `status=all`, mesmo dataset):

- **88 alertas brutos → 25 episódios/grupos clínicos** (razão de ruído 3,52× no dataset de teste atual — a razão 7,57× citada no ADR-0039, baseada em 53 alertas/7 episódios, referia-se a um snapshot anterior do seed, antes do fix de `cooldown_minutes` 0→15 já ter sido aplicado repetidamente; ambos os números descrevem a mesma dinâmica de burst por cooldown ausente).
- Com o filtro **default** da página (`status=active`), o dataset no momento do teste tinha apenas **1 alerta ativo / 1 grupo** — ou seja, o cooldown de 15 min já está evitando burst em tempo real na fila que o intensivista vê primeiro; o ruído histórico (88/25) só aparece quando se troca o filtro para "Todos status".

**Avaliação clínica (alarm fatigue):**
1. **Redução de volume por-tela é real e mensurável** (3,52× no pior caso observável neste dataset) — isso é diretamente a literatura de alarm fatigue (ECRI Institute, Joint Commission Sentinel Event Alert #50): reduzir o número de alarmes distintos que exigem decisão humana, sem suprimir o evento subjacente, é a intervenção recomendada, e é exatamente o que a arquitetura de leitura (agregação sem perda, ADR-0039 §1) faz.
2. **O cooldown (0→15min) ataca a causa raiz** (o motivo dos 53-88 alertas nunca foi 53-88 deteriorações distintas, foi o motor de alertas reavaliando o mesmo evento em cada ciclo sem gate) — é a correção mais importante do ciclo do ponto de vista de segurança do paciente, mais que a UI de agrupamento em si, porque reduz o volume na origem, não só na apresentação.
3. **Risco residual, honesto:** cooldown por severidade+sinal+paciente (`alert_cooldown:{mpi_id}:{score_type}:{severity}`) significa que uma **transição** de severidade (watch→urgent→critical) ainda gera um novo alerta imediatamente (chave de cooldown diferente) — o que é correto clinicamente (você não quer suprimir uma escalada real), mas também significa que o cooldown não é uma garantia geral contra burst se um paciente oscilar rapidamente entre níveis de severidade. Isso está fora do escopo desta re-auditoria de frontend, mas é um ponto de atenção para quem for avaliar o `alert_engine.py` isoladamente.
4. **A UI de agrupamento não substitui o cooldown — os dois são complementares e ambos foram entregues neste ciclo**, o que é a combinação correta (mitigar na origem E na apresentação).

**Veredito alarm fatigue: melhora significativa, bem fundamentada clinicamente**, com uma ressalva de escopo (cooldown por transição de severidade não foi re-verificado nesta rodada, que era focada em frontend).

---

## Trade-offs identificados (honestidade, não é torcida)

| # | Trade-off | Quem paga o custo | Mitigação existente |
|---|---|---|---|
| T1 | 1 clique extra para ver título/timestamp individual de cada ocorrência num grupo | Intensivista que precisa da timeline fina | Toggle "Lista completa" continua disponível |
| T2 | Ação em lote ("Reconhecer grupo") aumenta o "blast radius" de um clique — 1 confirmação agora resolve até 9+ alertas de uma vez | Segurança/reversibilidade | Passo de confirmação explícito com contagem; sem "desfazer" pós-confirmação (mesma lacuna do v1, agora com escala maior) |
| T3 | Modelo mental muda de "cada linha = 1 evento" para "cada card = 1 situação em andamento" | Usuário eventual/plantonista (mesmo público vulnerável identificado em U1 no v1) | Nenhuma explícita — sem onboarding/tour (gap também citado no v1, #10 Help and documentation, inalterado) |
| T4 | Breadcrumb quebra em 3 linhas em rotas de 3 níveis a 320px | Espaço vertical na Pathway View | Nenhuma — achado novo desta rodada, fora do escopo dos fixes revisados |
| T5 | `Escalando` não verificável ao vivo no dataset atual | Confiança da verificação (não do produto) | Confirmado por leitura de código + math de contraste documentado no commit, não por captura visual |

---

## Veredito por Jornada

| Jornada | v1 | v2 | Veredito |
|---|:--:|:--:|---|
| §1 Intensivista 320px (dashboard→paciente→trilha) | Funcional com U2 pendente | **Resolvida** | Critical-first elimina a busca linear; drawer com focus trap é implementação de referência (WAI-ARIA APG completo, testado com Tab-trace real) |
| §2 Split-screen ~512px | Card sem cap, "esticado" | **Resolvida** | `max-w-md` medido em 448px exatos; correção documental ao v1 sobre headers do AlertTable em 512px (permanecem ocultos, não visíveis) |
| §3 AlertTable → percepção de gravidade | Sem headers, mitigado por labels inline | **Melhorada estruturalmente** | Agrupamento ajuda mais do que atrapalha — trade-off real é 1 clique a mais por grupo para detalhe fino, não perda de sinal de gravidade |
| §4 Carga cognitiva 320px | 7.5/10, gargalo = busca linear | **8.8/10** | Maior heurística individual de ganho do ciclo (+1.3); combinação de sort + agrupamento ataca o mesmo gargalo por dois ângulos |

---

## Conclusão

O ciclo de correção entre v1 e v2 endereçou **9 dos 10 achados originais** (U1–U8, U10; apenas U9 "swipe gestures", classificado como NICE-TO-HAVE, permanece em backlog) e entregou uma feature estrutural nova (agrupamento de alertas, ADR-0039) que não estava no escopo do v1 mas que esta rodada avaliou como pedido: **a consolidação melhora, não atrapalha, a percepção de gravidade** — o sinal de severidade nunca é suprimido (sempre reflete o pior membro do grupo), e o ganho de reduzir ruído repetitivo (3,52× no dataset testado) supera o custo real, mas pequeno, de 1 clique extra para inspeção de membro individual.

**Score final v2: 9.0/10** (v1: 8.0/10, **Δ +1.0**) — **GO** (upgrade de CONDITIONAL-GO para GO): nenhuma das 4 violações MAJOR do v1 permanece aberta, e a lacuna residual identificada nesta rodada (T2 — sem "desfazer" pós-confirmação em ack de grupo) é uma observação para o próximo ciclo, não um bloqueador — o passo de confirmação explícito com contagem já é uma mitigação real, só não é uma garantia de reversibilidade.

**Relatório:** `/Users/familia/intensicare/frontend-v3/audit-results/responsive-ux-review-v2.md`
**Artefatos ao vivo (screenshots + JSON):** `/private/tmp/claude-501/-Users-familia-intensicare/2ddd8939-1ffb-4de3-9d7a-7a418c3d7b1a/scratchpad/reaudit-ux/artifacts/`
