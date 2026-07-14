# Matriz Consolidada de Violações Responsivas — FASE 0

**Gerado por:** Agente MATRIX (FASE 0, Workstream A, item 1-3)
**Data:** 2026-07-13
**Branch:** `feat/responsive-alerts-uplift`
**Insumos (exatamente estes 4, demais relatórios do diretório ignorados):**
`frontend-v3/audit-results/responsive-audit.md` (Ive), `responsive-ds-governance.md` (Hermes/DS Guardian), `responsive-a11y-review.md` (Hermes/A11y Gatekeeper), `responsive-ux-review.md` (Ive/UX Gatekeeper).
**Metodologia:** cada achado foi re-localizado no código atual (grep + leitura integral dos arquivos citados, branch `feat/responsive-alerts-uplift`, mesmo estado que os 4 relatórios auditaram — datados 2026-07-13, pós-PR #45/#47). Nenhuma correção foi aplicada; este documento é só diagnóstico + adjudicação.

---

## 0. Achado-chave da FASE 0

Todas as 22 violações PENDING abaixo foram confirmadas **linha a linha idênticas** às citadas pelos 4 relatórios — os 4 relatórios já foram gerados contra o código pós-PR #45/#47, então nenhuma ficou obsoleta por deriva de código. A única discrepância encontrada foi um **achado refutado** (RF-023, ver §3) onde o `responsive-ux-review.md` descreve um componente que, na leitura direta do código, já implementa o comportamento que o relatório diz faltar.

Um achado **CRITICAL não nomeado pelo owner** foi descoberto por adjudicação de um item que os 4 relatórios tratam como "fora de escopo": `state-label.tsx` concatena um sufixo de alpha-hex (`1A`, `33`) diretamente a uma string `var(--severity-*)`, produzindo CSS inválido (`"var(--severity-critical)1A"` não é uma cor válida). O `background-color` e a `border` do componente `StateLabel` silenciosamente falham em qualquer viewport — quebra o canal de cor da comunicação de severidade em um dos poucos lugares do app que não tem redundância textual visível. Ver RF-001.

---

## 1. Matriz de Violações

| RF-ID | Arquivo:linha ATUAL | Viewport(s) | Regra (WCAG/DS/Nielsen) | Severidade adjudicada | Fontes | Prescrição técnica | Status |
|---|---|---|---|---|---|---|---|
| RF-001 | `components/patient/state-label.tsx:20-23` | Todos (não é bug responsivo — afeta todos os breakpoints igualmente) | DS Governance N4 (CSS inválido) + risco indireto WCAG 1.4.1 Use of Color | **CRITICAL** | ds-governance §6.2/§8 (C4, marcado "bloqueante") | `severityColor()` retorna `var(--severity-critical)` (string); `` `${severityColor(severity)}1A` `` concatena sufixo hex-alpha a um `var()`, produzindo `background-color`/`border` com valor CSS inválido (ignorado pelo browser). Trocar por `color-mix(in srgb, ${severityColor(severity)} 10%, transparent)` para o fundo e `color-mix(in srgb, ${severityColor(severity)} 20%, transparent)` para a borda — mesmo mecanismo já usado em `--severity-*-wash` no `globals.css:11-14`. | PENDING |
| RF-002 | `components/dashboard/stats-bar.tsx:24` | 320px (XS), risco até ~400px | WCAG 1.4.10 Reflow (AA) + Nielsen #1 Visibility | **MAJOR** | responsive-audit.md (V1), responsive-ux-review.md (U4) | `className="flex items-center gap-4 ..."` → `"flex flex-wrap items-center gap-x-4 gap-y-1 ..."`. Confirmado: sem `flex-wrap`, ainda hoje. **= QW-1**. | PENDING |
| RF-003 | `components/alerts/alert-table.tsx:133` (header `hidden sm:flex`) + `components/alerts/alert-row.tsx` (nenhum label `sm:hidden` inline nos campos) | <640px (SM/XS) | WCAG 1.3.1 Info and Relationships (A) + Nielsen #6 Recognition | **MAJOR** | responsive-audit.md (V2), responsive-a11y-review.md (A1, nuance: downgrade técnico para MODERATE mas confirma violação), responsive-ux-review.md (U1) | Confirmado: `alert-row.tsx` já foi reestruturado (padrão disclosure APG, PR #45/47 — comentário explícito no código) mas **não** ganhou labels de campo para mobile. Adicionar `<span className="sm:hidden text-[length:var(--text-2xs)] uppercase text-[var(--text-secondary)]">Paciente</span>` (etc.) antes de cada valor (Severidade/Paciente/Trilha/Data), preservando `role="list"/"listitem"` e o header desktop existente. **= QW-5**. | PENDING |
| RF-004 | `components/pathway/state-flow.tsx:92` | 320-768px (onde o conteúdo transborda horizontalmente) | WCAG 2.1.1 Keyboard (A) | **MAJOR** | responsive-a11y-review.md (A2) — não detectado pelo audit original | Lido o componente por completo: é **somente-leitura** — os "pills" de estado são `<div>` sem `onClick`/`role`/`tabIndex` (nenhum estado é clicável, `aria-current="step"` no atual). A prescrição correta é semântica de **região rolável focável**, não `tabIndex={0}` nos pills: adicionar `tabIndex={0} role="region" aria-label="Linha do tempo de estados — use setas para navegar"` no `<div className="overflow-x-auto ...">` de linha 92 (o container, não os filhos). **= QW-2**. | PENDING |
| RF-005 | `components/app-shell.tsx` (abrir: linha 247 `onClick={() => setSidebarOpen(true)}`; fechar: linha 146 e overlay 226-239) | <1024px (sidebar é overlay, não `relative`) | WCAG 2.4.3 Focus Order (A) | **MAJOR** | responsive-a11y-review.md (A3) — não detectado pelo audit original | Confirmado: nenhum `useRef`/`.focus()` no componente inteiro; `Tab` não é interceptado dentro do `<aside>` (só Enter/Space/Escape no overlay fecham, não há trap cíclico). Adicionar `useRef` para o botão "Fechar" e o botão "Menu"; mover foco ao abrir (`closeBtnRef.current?.focus()`) e restaurar ao fechar (`menuBtnRef.current?.focus()`); Tab cíclico dentro do `<aside>` enquanto `sidebarOpen`, reusando o padrão de trap já existente em outro dialog do app (atalhos/CreateUserDialog). **= QW-3**. | PENDING |
| RF-006 | `components/alerts/quick-actions.tsx:118,139,160,178` | <640px (SM/XS) | Nielsen #6 Recognition (não é falha WCAG — `aria-label`+`title` já presentes em cada botão) | **MAJOR** | responsive-audit.md (addendum §6c, U3), responsive-ux-review.md (U3) | Confirmado: 4 botões (Reconhecer/Escalar/Não procede/Resolver) com `<span className="hidden sm:inline">`. Remover `hidden sm:inline` OU decidir por densidade medida no browser (FASE 1) — nunca manter ícone-só sem alternativa visível equivalente. **= QW-4**. | PENDING |
| RF-007 | `components/dashboard/bed-grid.tsx` + `app/page.tsx:16-18` (chave SWR `['dashboard', unit]`, sem sort) | 320px principalmente (scroll manual por 14 leitos) | Nielsen #7 Flexibility and Efficiency | **MAJOR** | responsive-audit.md (addendum §6c, U2), responsive-ux-review.md (U2) | Confirmado por grep: nenhuma lógica de `sort`/ordenação por severidade em `bed-grid.tsx`. Adicionar ordenação padrão `critical→urgent→watch→normal` em `data.patients` antes de renderizar (em `app/page.tsx` ou dentro de `BedGrid`), ou toggle "Críticos primeiro". Não bloqueia uso clínico imediato (severidade já é visível por leito) — degrada eficiência. | PENDING |
| RF-008 | `components/dashboard/bed-card.tsx:109` | 320-480px (legibilidade) | WCAG 1.4.4 Resize Text (AA, heurístico — unidade `px`, não relativa) + DS token ausente | MINOR | responsive-audit.md (V3), ds-governance (V3, "violação factual"), a11y-review (H1a) | `text-[10px]` → token DS (ver §2, criar `--text-2xs`). | PENDING |
| RF-009 | `components/patient/vitals-panel.tsx:71` | 320-480px | idem RF-008 | MINOR | responsive-audit.md (V4), ds-governance (V4), a11y-review (H1b) | idem RF-008. | PENDING |
| RF-010 | `components/pathway/state-flow.tsx:127` | 320-480px | idem RF-008 + WCAG 1.4.3 Contrast (AA, não verificado — `opacity-70` empilhado sobre fonte já pequena) | MINOR | responsive-audit.md (V5), ds-governance (V5), a11y-review (H1c + H2) | `text-[10px] opacity-70` → token DS + subir opacidade para `opacity-80` (ou remover dependência de opacidade — verificar contraste real em FASE 3 com axe). Mesmo arquivo de RF-004 (QW-2) — ver colisão §4. | PENDING |
| RF-011 | `components/alerts/filter-bar.tsx:170` (badge "!") | 320-480px | idem RF-008 | MINOR | ds-governance (A1 em §6.1), a11y-review (H1d) — **não capturado pelo audit original** | idem RF-008. | PENDING |
| RF-012 | `components/alerts/filter-bar.tsx:195` (`<label>` "Unidade") | 320-480px | idem RF-008 — label de formulário, mais sensível (`htmlFor` associado a input) | MINOR | ds-governance (A2 em §6.1), a11y-review (H1e) — **não capturado pelo audit original** | idem RF-008. | PENDING |
| RF-013 | `components/alerts/filter-bar.tsx:223` (`<label>` "Trilha") | 320-480px | idem RF-012 | MINOR | ds-governance (A3 em §6.1), a11y-review (H1e) — **não capturado pelo audit original** | idem RF-008. | PENDING |
| RF-014 | `components/app-shell.tsx:102` (`<kbd>` atalho "?") | 320-480px | idem RF-008 | MINOR | ds-governance (A4 em §6.1), a11y-review (H1f) — **não capturado pelo audit original** | idem RF-008. Mesmo arquivo de RF-005 (QW-3), RF-016, RF-017 — ver colisão §4. | PENDING |
| RF-015 | `components/dashboard/pathway-badges.tsx:44` (`text-[8px]`, badge "+N") | 320-480px | idem RF-008 — pior instância, 8px | MINOR | ds-governance (A5 em §6.1) — **não capturado por nenhum outro relatório** | `text-[8px]` → token DS `--text-3xs` (ver §2). | PENDING |
| RF-016 | `components/app-shell.tsx:267` (`<main className="... p-6">`) | 320px (48px = 15% do viewport) | Nielsen #8 Aesthetic + WCAG 1.4.10 Reflow (adjacente, não SC direto) | MINOR | responsive-audit.md (V6), responsive-ux-review.md (U5) — ds-governance rebaixa para "recomendação heurística, não violação de token" | `p-6` → `p-4 sm:p-6`. Mesmo arquivo de RF-005/014/017 — ver colisão §4. | PENDING |
| RF-017 | `components/app-shell.tsx:147` (botão fechar) e `:248` (botão menu) | <1024px | WCAG 2.5.8 Target Size Minimum (AA, 24px) — **atende**; não é violação WCAG | MINOR | responsive-audit.md (citou incorretamente WCAG 2.5.8=44px), a11y-review (H3, corrige a citação) | Medido no código: `p-1` (4px cada lado) + ícone `h-5 w-5` (20px) = **28×28px renderizado** — acima do mínimo AA (24px), abaixo do AAA (44px). Audit original errou a base normativa (44px é WCAG 2.5.5 AAA, não 2.5.8 AA). Não é bloqueante; recomendação ergonômica para uso clínico com luvas: `p-1`→`p-2` (28px→36px). Mesmo arquivo de RF-005/014/016 — ver colisão §4. | PENDING |
| RF-018 | `components/dashboard/severity-dot.tsx` (todo o componente) + uso em `bed-card.tsx:80` | Todos, mais crítico em 320px (menor espaço para redundância visual) | WCAG 1.4.1 Use of Color (A) — mitigado para AT via `aria-label`, não para usuários daltônicos videntes | MINOR | responsive-audit.md (addendum §6c, U6), responsive-ux-review.md (U6) | Confirmado: `SeverityDot` diferencia severidade só por `backgroundColor` (+ pulse só para `critical`); `BedCard` não expõe rótulo textual visível de severidade (só via `aria-label`, invisível). Adicionar diferenciador não-cromático (ícone/padrão) ao `SeverityDot` para `urgent`/`watch`, ou rótulo textual curto visível no `BedCard`. | PENDING |
| RF-019 | `components/dashboard/bed-card.tsx` (elemento raiz, linha 55-59 — sem `max-w-*`) | ~488-512px (split-screen clínico) | Nielsen #8 Aesthetic (largura de linha excessiva) | MINOR | responsive-ux-review.md (§2 "Densidade de Informação — Split-Screen", recomendação #5) — fonte única | Confirmado: `BedGrid` usa `repeat(auto-fill, minmax(280px, 1fr))` (linhas 115,154) sem teto — em ~512px produz 1 coluna de ~488px. Adicionar `max-w-md` (~448px) ao card. Mesmo arquivo de RF-008 e RF-018 (severity-dot é separado, mas ambos tocam `bed-card.tsx`) — ver colisão §4. | PENDING |
| RF-020 | `app/page.tsx:16-18` (`useSWR(['dashboard', unit], ...)`) | 320px principalmente | Nielsen #3 User Control and Freedom | MINOR | responsive-ux-review.md (U7) — fonte única | Confirmado: a chave SWR muda com `unit`, disparando novo fetch/loading a cada troca de filtro sem preservação de scroll. Usar `keepPreviousData` do SWR (evita re-render vazio intermediário) e/ou capturar `window.scrollY` antes de `setUnit`, restaurando via `useLayoutEffect` pós-fetch. | PENDING |
| RF-021 | `components/pathway/state-flow.tsx:92-144` | 320-768px (onde há overflow horizontal) | Nielsen #6 Recognition (NICE-TO-HAVE na fonte) | MINOR | responsive-audit.md (addendum §6c, U10), responsive-ux-review.md (U10) | Confirmado: nenhum indicador visual de overflow (sem gradiente fade, sem dots). Adicionar fade gradient nas bordas do container `overflow-x-auto` via `mask-image` ou pseudo-elemento. Mesmo arquivo de RF-004 e RF-010 (QW-2) — ver colisão §4. | PENDING |
| RF-022 | `components/alerts/alert-row.tsx` (linha 57-148, summary row) | Mobile, uso com 1 mão | Nielsen #7 Flexibility (NICE-TO-HAVE na fonte) | MINOR | responsive-ux-review.md (U9) — fonte única | Sem gesto de swipe para acknowledge/dismiss (2 taps hoje). Recomenda-se **adiar para o próximo ciclo**: mesmo arquivo de RF-003 (QW-5); baixo valor clínico imediato. | PENDING |
| RF-023 | `components/patient/active-pathways.tsx:48-58` | N/A — achado refutado | N/A | N/A | responsive-ux-review.md (§5, "Única fragilidade": *"grid de ActivePathways simplesmente não renderiza nada"*) | **Achado refutado pela leitura do código atual.** `ActivePathways` já implementa um empty-state dedicado e completo: `{!isLoading && !error && pathways.length === 0 && (<div className="rounded-lg border border-dashed ..."><GitBranchPlus .../><p>Nenhuma trilha ativa para este paciente.</p>...)}` (linhas 48-58). Nenhuma ação necessária. | **OBSOLETO** (achado não se sustenta no código — refutado com evidência) |

---

## 2. Onde criar o token de tipografia (G-TYPO)

O DS não define nenhum token de tipografia hoje (`app/globals.css` tem apenas cor/superfície/raio/marca — confirmado por leitura integral do arquivo, 54 linhas, sem `--text-size-*`/`--font-*`). Prescrição única para as 8 ocorrências RF-008…RF-015:

1. Em `app/globals.css`, dentro do bloco `:root[data-theme='dark'] { ... }` (após a linha 24, `--radius-lg`), adicionar:
   ```css
   --text-3xs: 0.5rem;    /* 8px — substitui pathway-badges.tsx:44 */
   --text-2xs: 0.6875rem; /* 11px — substitui as 7 instâncias de text-[10px] (resolve em 1 tacada o achado heurístico de legibilidade H1 do a11y-review, sem introduzir novo hardcode) */
   ```
2. Mapear no bloco `@theme inline` (linha 35-42) para gerar utilitários Tailwind v4 nativos:
   ```css
   --font-size-3xs: var(--text-3xs);
   --font-size-2xs: var(--text-2xs);
   ```
3. Consumidores trocam `text-[10px]`/`text-[8px]` por `text-2xs`/`text-3xs` (utilitário gerado, não mais arbitrary value) — unidade `rem`, portanto redimensionável por preferência de fonte mínima do usuário e por zoom, resolvendo a preocupação WCAG 1.4.4 levantada nos 4 relatórios.
4. **Nota lateral (fora da matriz):** `components/pathways/pathway-detail.tsx` já usa `text-[0.625rem]` (5 ocorrências, linhas 58,93,118,123,128) — já é rem-based mas ainda é arbitrary value, não token. Não incluído como RF (nenhum dos 4 relatórios o cita), mas o agente G-TYPO deve migrar essas 5 ocorrências para o mesmo `--text-2xs`/token equivalente já que está mexendo no mesmo mecanismo — **oportunidade, não obrigação desta matriz**.

---

## 3. Achados citados nos relatórios mas fora do escopo desta matriz

- **ds-governance.md §6.2** cita débitos pré-existentes de auditorias DS v1/v2 (não incluídas nos 4 insumos mandatados): N1 (19 instâncias de border inline), M1–M16 (16 font-sizes arbitrários adicionais), M17–M44 (28 width/height fixos). **Não enumerados com arquivo:linha em nenhum dos 4 relatórios-insumo** — portanto não viram RF-ID (instrução: usar exatamente os 4 relatórios). O plano de agrupamento (§4) da FASE 2 do prompt cita "M13–M18" como exemplo de `G-DS` — esse ID não existe nos meus 4 insumos; sinalizo abaixo como item a resolver pelo orquestrador, não pela matriz.
- **Toast/feedback de sucesso pós-ack/escalate/resolve** (responsive-ux-review.md, heurística #9 + recomendação #7 do backlog): citado em prosa, sem severidade atribuída na lista formal U1-U10 da fonte. Não recebeu RF-ID para não inventar severidade não declarada pela fonte.

---

## 4. Contagem total declarada

**N = 23 violações extraídas** → **1 CRITICAL / 6 MAJOR / 15 MINOR / 1 OBSOLETO**

(RF-001 CRITICAL · RF-002 a RF-007 MAJOR [6] · RF-008 a RF-022 MINOR [15] · RF-023 OBSOLETO)

---

## 5. Plano de Agrupamento por Mecanismo (FASE 2) — com colisões de arquivo mapeadas

**Pré-requisito (bloqueia G-TYPO inteiro):** 1 agente, 1 arquivo (`app/globals.css`) — criar `--text-3xs`/`--text-2xs` + mapeamento `@theme inline` (§2). Sem isso nenhum consumidor de G-TYPO pode rodar.

**Prioridade fora dos grupos nomeados pelo owner:** RF-001 (CRITICAL) não está entre QW-1..5. Recomendo tratá-lo como **QW-0** — mesmo padrão de execução da FASE 1 (1 arquivo, `state-label.tsx`, ~3 linhas, zero dependência de outro grupo) — rodando em paralelo à FASE 1, não esperando a FASE 2.

### Colisões de arquivo identificadas e resolução

| Arquivo | RF-IDs que o tocam | Grupos envolvidos | Resolução proposta |
|---|---|---|---|
| `components/app-shell.tsx` | RF-005 (QW-3), RF-014 (G-TYPO), RF-016 (G-LAYOUT), RF-017 (G-TOUCH) | Fase 1 (QW-3) × 3 grupos Fase 2 | **Fundir** RF-014+RF-016+RF-017 em 1 agente único `G-APPSHELL`, sequenciado **depois** de QW-3 (mesmo arquivo, mesmo estado pós-merge) — evita 3 agentes editando o mesmo arquivo em paralelo. |
| `components/pathway/state-flow.tsx` | RF-004 (QW-2), RF-010 (G-TYPO), RF-021 (G-UX-320) | Fase 1 (QW-2) × 2 grupos Fase 2 | **Fundir** RF-010+RF-021 no próprio agente de QW-2 (arquivo já aberto, mudanças são linhas adjacentes — 127 e 92-144) — mais simples que sequenciar 2 agentes extras num arquivo de 147 linhas. |
| `components/alerts/alert-row.tsx` | RF-003 (QW-5), RF-022 (backlog) | Fase 1 (QW-5) × backlog | RF-022 é NICE-TO-HAVE na fonte — **adiar para o próximo ciclo**, não escalar agente nesta rodada. |
| `components/dashboard/bed-card.tsx` | RF-008 (G-TYPO), RF-019 (G-LAYOUT/UX) | 2 grupos Fase 2 | **Fundir** em 1 agente `G-BEDCARD` cobrindo `bed-card.tsx` (RF-008+RF-019) + `severity-dot.tsx` (RF-018) — 2 arquivos, dentro do limite de 3. |
| `components/alerts/filter-bar.tsx` | RF-011, RF-012, RF-013 | G-TYPO apenas | Sem colisão entre grupos — mesmo grupo, 1 agente, 3 linhas no mesmo arquivo. |
| `app/page.tsx` + `components/dashboard/bed-grid.tsx` | RF-007, RF-020 | G-UX-320 apenas | Sem colisão entre grupos — mesmo grupo, 1 agente, 2 arquivos. |

### Grupos finais para despacho em paralelo (sem colisão entre si)

| Grupo | RF-IDs | Arquivo(s) | Depende de |
|---|---|---|---|
| **QW-0** (fora da nomenclatura do owner, prioridade CRITICAL) | RF-001 | `state-label.tsx` | — |
| **G-TYPO-token** (prerequisito) | — | `app/globals.css` | — |
| **G-TYPO-filterbar** | RF-011, RF-012, RF-013 | `filter-bar.tsx` | G-TYPO-token |
| **G-TYPO-vitals** | RF-009 | `vitals-panel.tsx` | G-TYPO-token |
| **G-TYPO-badges** | RF-015 | `pathway-badges.tsx` | G-TYPO-token |
| **G-BEDCARD** | RF-008, RF-018, RF-019 | `bed-card.tsx`, `severity-dot.tsx` | G-TYPO-token |
| **G-UX-320** | RF-007, RF-020 | `app/page.tsx`, `bed-grid.tsx` | — |
| **G-APPSHELL** (pós-QW-3) | RF-014, RF-016, RF-017 | `app-shell.tsx` | QW-3 mergeado + G-TYPO-token |
| **QW-2-estendido** (fusão recomendada) | RF-004, RF-010, RF-021 | `state-flow.tsx` | G-TYPO-token (para RF-010) |
| **Backlog (não despachar nesta rodada)** | RF-022 | `alert-row.tsx` | Roda depois de QW-5, próximo ciclo |

Todos os grupos acima ficam dentro do limite de ≤3 arquivos/agente do prompt. Nenhum par de grupos toca o mesmo arquivo simultaneamente após as fusões/sequenciamentos propostos.

---

## 6. Quick-Wins da FASE 1 — mapeamento QW-1..5 (+ QW-0)

| QW | RF-ID | Arquivo | Observação para o agente de quick-wins |
|---|---|---|---|
| **QW-0** (adicional, CRITICAL, recomendado rodar junto) | RF-001 | `components/patient/state-label.tsx` | Não nomeado pelo owner; incluir por severidade. Único arquivo, isolado — sem risco de colisão com QW-1..5. |
| **QW-1** | RF-002 | `components/dashboard/stats-bar.tsx` | Sem dependências; não colide com nenhum outro grupo. |
| **QW-2** | RF-004 (+ RF-010, RF-021 se o orquestrador optar por estender) | `components/pathway/state-flow.tsx` | Confirmado read-only — NÃO usar `tabIndex` nos pills, só no container de scroll. Se estender para RF-010, depende de G-TYPO-token estar mergeado antes (ou usar valor provisório e trocar depois). |
| **QW-3** | RF-005 (+ RF-014/016/017 via G-APPSHELL sequenciado depois) | `components/app-shell.tsx` | Reusar padrão de trap já existente no app (dialog de atalhos). G-APPSHELL (Fase 2) só pode rodar depois deste merge. |
| **QW-4** | RF-006 | `components/alerts/quick-actions.tsx` | Isolado, sem colisão. |
| **QW-5** | RF-003 | `components/alerts/alert-table.tsx`, `components/alerts/alert-row.tsx` | RF-022 (backlog) toca o mesmo `alert-row.tsx` — não despachar RF-022 na mesma rodada para evitar conflito de merge. |

Nenhum RF-ID mapeado para QW-1..5 (ou QW-0) deve ser re-despachado nos grupos da FASE 2 sem a fusão/sequenciamento indicada em §5 — isso é o que impede colisão entre o agente de quick-wins e os agentes de FASE 2.

---

*Matriz produzida pelo agente MATRIX. Nenhuma correção de código foi aplicada nesta fase — apenas leitura, grep e adjudicação técnica contra o estado atual do branch `feat/responsive-alerts-uplift`.*
