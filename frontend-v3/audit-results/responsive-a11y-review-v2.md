# Responsive Accessibility Re-Audit v2 — IntensiCare Frontend v3

**Data:** 2026-07-13
**Revisor:** RE-AUDITOR A11Y (flywheel, rodada v2)
**Fonte v1:** `frontend-v3/audit-results/responsive-a11y-review.md` (mesmo mandato/matriz WCAG, replicado)
**Branch auditada:** `feat/responsive-alerts-uplift` (stack viva `:3000`/`:8000`, `admin`/`admin`)
**WCAG Target:** 2.1 AA (2.2 §2.5.8 citado onde relevante, como no v1)
**Metodologia:** Chromium real (Playwright) — computed styles, `getBoundingClientRect`, tab-order por teclado, axe-core 4.12.1 (`frontend-v3/node_modules/axe-core`) via `addScriptTag`. **Não é code-scan** — todo achado abaixo tem medição ao vivo correspondente. Script: `scratchpad/reaudit-a11y/reaudit.mjs` (harness: `scratchpad/e2e-live/harness.mjs`). Artefatos brutos (18 screenshots + `results-raw.json` + `report.json`): `scratchpad/reaudit-a11y/`.

**Restrição de escopo respeitada:** uma tentativa de semear um grupo de alertas "Escalando" ao vivo via `POST /api/v1/vitals` (dataset ativo estava drenado por sessão E2E anterior — 1 único grupo ativo, `count=1`, `escalating=false`) foi **negada pelo próprio classificador de permissões** do harness ("Modify Shared Resources") e **não foi contornada**. A cobertura desse gap está descrita em §5.3/§5.4 via uma técnica de medição que não muta nenhum estado do servidor (ver nota lá).

---

## 1. Executive Summary

| Métrica | v1 (2026-07-13, code-scan) | v2 (2026-07-13, Chromium real) |
|---------|------|------|
| **Score** | 78/100 | **86/100** |
| **Veredito** | CONDITIONAL-GO | **CONDITIONAL-GO** (motivos diferentes — ver §7) |
| **Violações WCAG A originais (§3.1–3.4 do v1)** | 3 confirmadas (1.3.1, 2.1.1, 2.4.3) | **0 remanescentes — as 3 foram corrigidas e comprovadas ao vivo** |
| **Violações NOVAS achadas nesta rodada** | — | **1 crítica (axe `aria-required-children`, live), 2 de contraste (4.5:1 fail, medição isolada), 1 de touch-target (16×16px)** |
| **Axe-core: violações nas 12 telas×viewport principais** | não executado (heurístico) | **0/12 (login, dashboard, patient, pathway, alerts×2 views @320/1440)** |
| **Axe-core: violações nas superfícies NOVAS** | não existiam | **1 (patient-panel rollup, impact=critical, ambos os viewports)** |

**Leitura do delta:** os 3 bloqueadores Level A do v1 foram genuinamente corrigidos — não é auto-relato do código, é comprovação ao vivo (foco programático medido, `scrollLeft` medido sob overflow forçado, `display` computado dos headers). Em paralelo, o ciclo de uplift (`ADR-0039`, grupos de alertas) introduziu 4 achados novos que o v1 não podia ter visto porque as superfícies não existiam. O placar sobe porque o saldo é positivo, não porque não há mais nada a corrigir.

---

## 2. WCAG Compliance Matrix v2 (com delta)

Mesmas 9 categorias e mesmos pesos do v1 §7 (100 pontos distribuídos em 7 categorias com dedução; 2.4.7 e 4.1.2 seguem informativas fora do total de 100, exatamente como no v1 — ver nota de reconciliação abaixo).

| WCAG SC | Level | Nome | v1 Score | v2 Score | Δ | v2 Status | Evidência-chave v2 |
|---------|-------|------|----------|----------|---|-----------|---------------------|
| **1.3.1** | A | Info and Relationships | 10/15 | **12/15** | +2 | ⚠️ PARCIAL | Headers mobile: **corrigido e comprovado** (labels `sm:hidden` inline, ver §3.3). **NOVO FAIL**: `role="list"` do patient-panel rollup contém filho `role="article"` — axe `aria-required-children`, impact=**critical**, live em `/patient/LEITO-03` @320 e @1440 (ver §5.4) |
| **1.4.3** | AA | Contrast (Minimum) | 16/20 | **15/20** | −1 | ⚠️ PARCIAL | Axe: 0 violações de contraste nas 12 telas principais (nada de errado *hoje renderizado*). Medição isolada (fixture, ver §5.3) confirma **2 combinações reais e alcançáveis em produção falham AA (4.5:1)**: badge "Escalando" variante wash (4.483:1) e `SeverityBadge` urgent sobre linha escalando (4.412:1) |
| **1.4.4** | AA | Resize Text (heurístico) | 4/10 | **10/10** | +6 | ✅ PASS | Todas as 8 ocorrências de fonte reduzida (7 do v1 + 1 nova em `pathway-badges.tsx`) migraram para o token `text-2xs` = **11px medido via `getComputedStyle` ao vivo** em 4 telas (dashboard, patient, pathway, alerts) — 100% consistente, nenhuma ocorrência residual de `text-[10px]` |
| **1.4.10** | AA | Reflow | 18/20 | **19/20** | +1 | ✅ PASS | Axe 0 violações @320 em todas as 6 telas/estados; nenhum overflow visual observado nos screenshots @320. −1 mantido porque a preocupação original do v1 (StatsBar sem `flex-wrap`) não foi re-testada isoladamente nesta rodada |
| **2.1.1** | A | Keyboard | 6/10 | **10/10** | +4 | ✅ PASS | `StateFlow`: `tabIndex=0`+`role=region`+`aria-label` confirmados ao vivo; **scroll por teclado provado sob overflow real** (forçado via zoom simulado 200%, `scrollLeft` 0→52 com `ArrowRight`) — mais rigoroso que a recomendação original, que só pedia os atributos |
| **2.4.3** | A | Focus Order | 7/10 | **8/10** | +1 | ⚠️ PARCIAL | Sidebar (bug original): **corrigido e comprovado** — abrir move foco para "Fechar menu", `Escape` devolve foco a "Abrir menu", `role="dialog"`/`aria-modal="true"` confirmados. **NOVO achado heurístico**: painel de confirmação do "Reconhecer grupo" não move foco — `document.activeElement` cai para `null`/body ao trocar de estado (ver §5.2) |
| **2.4.7** | AA | Focus Visible | 10/10 | **10/10** | 0 | ✅ PASS | `focus-visible:ring-2` confirmado em todos os controles novos e antigos lidos (disclosure buttons, group-ack, badges) — não regrediu |
| **2.5.5/2.5.8** | AAA/AA | Target Size | 15/15 | **12/15** | −3 | ⚠️ PARCIAL | Hamburger/fechar menu: **28px→40×40px medido** (grande melhora, folga confortável sobre o piso 24px AA). **NOVO achado**: chevron de disclosure do `AlertGroupRow`/`AlertRow` mede **16×16px** — abaixo do piso 24px do WCAG 2.5.8 AA (não citado pelo v1 porque a métrica antiga nunca mediu esse controle) |
| **4.1.2** | A | Name, Role, Value | 9/10 | **9/10** | 0 | ✅ PASS | Cobertura de ARIA extensa e correta nas 12 telas (axe limpo); o achado `aria-required-children` é contabilizado primariamente em 1.3.1 acima para não duplicar peso |
| **TOTAL (7 categorias com peso, /100)** | | | **76** (soma real; v1 relatou 78 — discrepância aritmética de 2pts no original, não reconciliada aqui) | **86** | **+10** | | |

---

## 3. Re-Validação dos 4 Issues Originais (medição ao vivo)

### 3.1 Font-size 10px — WCAG 1.4.4 — ✅ CORRIGIDO (comprovado)

Query `.text-2xs` ao vivo, `getComputedStyle(el).fontSize`, 4 telas:

| Tela | Elementos `.text-2xs` encontrados | `font-size` computado |
|------|-----------------------------------|------------------------|
| Dashboard (BedCard staleness) | 13 (staleness labels + `<kbd>`) | **11px** em 100% dos elementos |
| `/patient/MPI-DEMO-001` (VitalsPanel `<time>`) | 67 | **11px** em 100% |
| `/patient/MPI-DEMO-001/pathway/40` (StateFlow terminal badge) | 1 | **11px** |
| `/alerts` (FilterBar labels + badge, extra row expandida) | 3 (`<kbd>`, `Unidade`, `Trilha`) | **11px** |

`app/globals.css:50`: `--text-2xs: 0.6875rem` (= 11px), com `line-height` floor de 16px documentado inline no CSS (mesmo piso do `text-xs` nativo do Tailwind). As 7 ocorrências originais (`bed-card.tsx`, `vitals-panel.tsx`, `state-flow.tsx`, `filter-bar.tsx`×3, `app-shell.tsx`) **e** uma oitava nova (`pathway-badges.tsx`, componente que não existia no v1) foram migradas para este token. Nenhuma ocorrência residual de `text-[10px]` no código (`grep` confirmatório).

**Veredito v2:** RESOLVIDO — 10/10 (era 4/10).

---

### 3.2 Touch Targets — WCAG 2.5.8/2.5.5 — ⚠️ PARCIAL (melhorado + achado novo)

`getBoundingClientRect()` ao vivo:

| Elemento | v1 | v2 medido | Piso AA (2.5.8, 24px) | Piso AAA (2.5.5, 44px) |
|----------|-----|-----------|------------------------|--------------------------|
| Hamburger "Abrir menu" @320 | 28×28 | **40×40** | ✅ folga 16px | ❌ (não é requisito AA) |
| Fechar menu (sidebar) @320 | 28×28 | **40×40** | ✅ | ❌ |
| "Tentar novamente" (BedGrid, erro forçado via route-abort) | ~32px | **177×38** | ✅ | ❌ (mas texto+ícone, não crítico) |
| **NOVO** `AlertGroupRow`/`AlertRow` disclosure chevron | não medido no v1 (controle não catalogado) | **16×16px** | ❌ **FAIL** | ❌ |
| **NOVO** botão "Reconhecer grupo" (trigger) | — | **142×28** | ✅ (folga mínima, +4px) | ❌ |

**Achado novo:** o botão de disclosure (`<button>` sem classe de padding, só `className="flex-shrink-0 rounded ..."` envolvendo um ícone `h-4 w-4`) mede exatamente o ícone — 16×16px. Isso vale tanto para `alert-row.tsx` (padrão pré-existente, nunca medido pelo v1) quanto para o novo `alert-group-row.tsx` (mesmo padrão copiado). É o único touch-target abaixo do piso AA 2.5.8 (24px) encontrado nesta rodada.

**Veredito v2:** 12/15 (era 15/15 — o v1 tinha razão que os alvos que mediu passam, mas não mediu o disclosure chevron, que falha).

---

### 3.3 AlertTable Headers em Mobile — WCAG 1.3.1 — ✅ CORRIGIDO (comprovado, e estendido ao grouped view)

`display` computado ao vivo, header vs. labels inline `sm:hidden`, **ambas as views** (grouped e flat, pois o `AlertGroupTable` novo replica o mesmo header `hidden sm:flex`):

| View | Viewport | Header (`hidden sm:flex`) `display` | Labels inline (`sm:hidden`) `display` |
|------|----------|--------------------------------------|------------------------------------------|
| grouped | 320 | `none` | `block` (visível) |
| grouped | 1440 | `flex` (visível) | `none` |
| flat | 320 | `none` | `block` (visível) |
| flat | 1440 | `flex` (visível) | `none` |

Simetria perfeita nas 4 combinações: exatamente quando o header desaparece, os labels inline (`Paciente`, `Trilha`/`Sinal`, `Mensagem`/`Ocorrências`, `Criado em`/`Janela`) aparecem, em ambas as views. Código-fonte (`alert-row.tsx` linhas 84-141, `alert-group-row.tsx` linhas 262-296) confirma a implementação exata do fix recomendado pelo v1 (§10 "A1").

**Veredito v2:** RESOLVIDO para o escopo original — 1.3.1 segue com deduções, mas por um achado **diferente e novo** (ver §5.4, patient-panel rollup `role="list"`/`role="article"`), não pelo problema original.

---

### 3.4 StateFlow Keyboard Navigation — WCAG 2.1.1 — ✅ CORRIGIDO (comprovado sob overflow real)

Estado atual do código (`state-flow.tsx:122-130`): `tabIndex={0}`, `role="region"`, `aria-label="Estados da trilha — role horizontalmente para ver todos"`, `focus-visible:ring-2`. Confirmado ao vivo:

- `getAttribute`/`tabIndex` no elemento real: `tabIndex=0`, `role="region"` ✅
- `element.focus()` + verificação de `document.activeElement.getAttribute('role') === 'region'` → **true** ✅
- **Teste de overflow real:** a trilha Sepse (5 estados, `pp_id=40`) **não** transborda em 320px puro (`scrollWidth === clientWidth === 262px`) — nenhuma trilha ativa no dataset atual tem estados suficientes para isso (levantamento via API em todos os pacientes DEMO: máx. 5 estados). Para provar o caminho de teclado sob overflow real (sem mutar dados), simulei zoom ~200% (`document.documentElement.style.fontSize = '32px'`, revertido depois) — isso **força** overflow real (`scrollWidth=258 > clientWidth=206`) e é o mesmo mecanismo que WCAG 1.4.4 já exige suportar. Resultado: `scrollLeft` foi de `0` → `52` após `ArrowRight` repetido, com a região focada. **Scroll por teclado funciona de fato**, não só os atributos estão presentes.

**Veredito v2:** RESOLVIDO — 10/10 (era 6/10), com evidência mais forte que a recomendação original exigia.

---

### 3.5 Focus Order / Sidebar (A3, relacionado) — WCAG 2.4.3 — ✅ CORRIGIDO (comprovado) + achado novo em superfície diferente

`app-shell.tsx` ganhou `sidebarRef`/`menuButtonRef`/`closeButtonRef` + `useEffect` com trap de foco. Confirmado ao vivo @320:

1. Foco no botão "Abrir menu" → `Enter` → `document.activeElement.ariaLabel === "Fechar menu"` ✅
2. `aside#app-sidebar` durante abertura: `role="dialog"`, `aria-modal="true"` ✅
3. `Escape` → `document.activeElement.ariaLabel === "Abrir menu"`, `aria-expanded="false"` ✅ (foco retorna ao disparador)

**Veredito v2:** RESOLVIDO — este componente específico está limpo. (A dedução residual em 2.4.3 no placar de §2 vem de um achado **diferente**, no fluxo de confirmação de "Reconhecer grupo" — ver §5.2.)

---

## 4. Axe-core Sweep — 6 telas × 2 viewports (320, 1440)

Todas rodadas autenticadas exceto `/login`. Resultado bruto completo em `scratchpad/reaudit-a11y/results-raw.json` (chave `axe`), screenshots em `scratchpad/reaudit-a11y/artifacts/01..14-*.png`.

| Tela | 320px | 1440px |
|------|-------|--------|
| `/login` (não autenticado) | **0 violações** | **0 violações** |
| Dashboard (`/`) | **0 violações** | **0 violações** |
| `/patient/MPI-DEMO-001` | **0 violações** | **0 violações** |
| `/patient/MPI-DEMO-001/pathway/40` | **0 violações** | **0 violações** |
| `/alerts` — view **agrupada** ("Por paciente/sinal", default) | **0 violações** | **0 violações** |
| `/alerts` — view **plana** ("Lista completa") | **0 violações** | **0 violações** |

**12/12 limpo.** Isso é esperado — não confirmado às cegas: como o próprio script documenta (mesma metodologia do achado "A11y round 2: axe runtime 28→0" registrado após o ciclo de correção anterior), a auditoria roda de fato e reporta zero, não presume zero. O resultado é consistente com o histórico de correções recente (14 bugs de runtime + 5 achados sistemáticos de a11y corrigidos no ciclo anterior).

**Ressalva importante (ver §5):** este sweep só vê o que está **de fato renderizado no dataset atual**. Duas superfícies novas (badge "Escalando", rollup multi-ocorrência do patient panel) não têm dados ativos para renderizar no momento da auditoria — então axe não teve chance de escanear esses estados. Isso não significa que estão livres de violação; significa que precisam da técnica alternativa de §5.3/§5.4.

---

## 5. Superfícies Novas do Ciclo de Uplift (ADR-0039 / FASE 2B.1)

O v1 não cobria nenhuma destas — são novas desde então.

### 5.1 Grupos de alerta com disclosure (`AlertGroupRow`, view agrupada de `/alerts`)

Testado ao vivo com o único grupo ativo existente no dataset (`LEITO-03` / Ana Oliveira / AKI, `count=1`, `id=9`, não reconhecido).

- **Padrão APG disclosure**: container `role="listitem"` não-interativo; `<button aria-expanded aria-controls>` dedicado — idêntico ao padrão já validado em `AlertRow` no ciclo anterior. Confirmado.
- **Tab-order** medido (focus programático no chevron, depois `Tab` repetido): `Grupo Ana Oliveira — AKI — Expandir 1 alertas` → `Paciente: Ana Oliveira` → `Reconhecer os 1 alertas pendentes de Ana Oliveira — AKI`. Os spans não-interativos (Severidade, Sinal, Ocorrências, Janela) são corretamente pulados — nenhum "tab stop fantasma".
- **Axe na região expandida**: 0 violações.
- **Touch target do chevron**: 16×16px — ver §3.2 (achado FAIL).

### 5.2 Ack de grupo com confirmação (`AlertGroupRow`, estado "confirming")

Fluxo: clicar "Reconhecer grupo" → painel inline `role="group" aria-label="Confirmar reconhecimento em grupo"` com texto de confirmação + botões "Confirmar"/"Cancelar" (não é modal/dialog — é inline, sem `role="dialog"`, sem `Escape`-to-close).

- **Axe no estado "confirming"**: 0 violações.
- **`role="group"` com `aria-label` presente**: confirmado ao vivo.
- **Achado (heurístico, não é violação axe)**: `document.activeElement` medido imediatamente após o clique em "Reconhecer grupo" é **`null`** (cai para `<body>`). O botão que disparou a ação é desmontado e nada recebe foco programaticamente no seu lugar — o mesmo padrão de gap que o v1 encontrou (e que foi corrigido) no `AppShell`/sidebar, agora reaparecendo numa superfície nova e menor. Não bloqueia teclado (o usuário pode `Tab` a partir do topo do documento), mas quebra a expectativa de continuidade de foco em uma ação transacional (ack de N alertas de um paciente).
- Cancelado sem submeter (mesma disciplina non-destructive do ciclo de auditoria anterior — nenhuma mutação real de dado).

### 5.3 Badge "Escalando" — contraste (medição isolada, não axe ao vivo)

**Por que medição isolada:** nenhum grupo ativo no dataset atual tem `escalating=true` (confirmado via `GET /api/v1/alerts?group_by=signal&status=active` → 1 grupo, `count=1`, `escalating=false`, em todo o dataset — drenado pela sessão E2E anterior). Semear um grupo escalando de verdade via `POST /api/v1/vitals` foi **tentado e negado** pelo classificador de permissões do harness como mutação de recurso compartilhado. Em vez disso: construí fixtures DOM efêmeras (criadas e removidas dentro da mesma execução de página, sem chamada de rede, sem persistência) reproduzindo **exatamente** as classes/estilos inline do código-fonte, e medi `getComputedStyle` real do navegador (que resolve `color-mix()` de fato — método mais confiável que aritmética manual). Fórmula de contraste WCAG padrão (luminância relativa sRGB) aplicada sobre as cores compostas reais.

| Cenário | Padrão de código | Contraste medido | AA (4.5:1) |
|---------|-------------------|--------------------|------------|
| `SeverityBadge` crítico sobre linha NÃO-escalando (baseline) | wash | 5.118:1 | ✅ PASS |
| **`alerts-panel.tsx` (patient rollup)** — badge "Escalando" | **wash** (`bg-severity-critical-wash`, `color: severity-critical`) — variante NÃO corrigida | **4.483:1** | ❌ **FAIL** |
| `alert-group-row.tsx` (alerts page, view agrupada) — badge "Escalando" | **sólido** (`bg: severity-critical`, `color: surface-canvas`) — variante corrigida (comentário no código cita exatamente este cálculo, 7.217:1) | 7.217:1 | ✅ PASS |
| `alert-group-row.tsx` — `SeverityBadge` override para `escalating && max_severity==='critical'` | sólido (fix aplicado) | 7.217:1 | ✅ PASS |
| **`alert-group-row.tsx`** — `SeverityBadge` **urgent** (wash) sobre linha escalando, `max_severity !== 'critical'` — **caso NÃO coberto pela condição do fix** (`group.escalating && group.max_severity === 'critical'`, linha ~240) | wash (sem override) | **4.412:1** | ❌ **FAIL** |
| `alert-group-row.tsx` — `SeverityBadge` watch (wash) sobre linha escalando | wash (sem override, mas passa) | 6.782:1 | ✅ PASS |

**Interpretação:** o código já documenta (comentário extenso em `alert-group-row.tsx`, "GK-RESP achado A") que a variante *wash* duplo-composta falha WCAG AA quando renderizada sobre o fundo *wash* da própria linha escalando, e corrigiu isso para o caso `escalating && max_severity === 'critical'` na view agrupada de `/alerts`. Esta rodada mede e confirma **dois pontos onde essa mesma correção não foi replicada**:

1. **`components/patient/alerts-panel.tsx` linhas 188-197** (rollup do patient panel) — o badge "Escalando" ali **ainda usa a variante wash não corrigida**, apesar de ser exatamente o mesmo componente visual, no mesmo cenário de fundo (linha com `bg-severity-critical-wash` quando `group.escalating`). Este é o achado mais direto: a correção existe em um lugar do código e não no outro lugar onde o mesmo bug existe.
2. **`components/alerts/alert-group-row.tsx`, o próprio arquivo corrigido** — a condição do fix (`max_severity === 'critical'`) deixa de fora o caso em que um grupo está `escalating=true` mas sua severidade máxima é `urgent` (ainda assim a linha inteira ganha o fundo `severity-critical-wash`, independente de `max_severity` — a ramificação de estilo da linha só olha `escalating`). Esse é um caso residual não coberto pelo próprio fix, dentro do mesmo arquivo.

### 5.4 Rollup do painel do paciente (`AlertsPanel`, `/patient/{mpi_id}`)

Testado ao vivo em `/patient/LEITO-03` (único paciente com alerta ativo no dataset), @320 e @1440.

- `<section aria-label="Alertas do paciente">` presente, `<h2>Alertas</h2>`. Confirmado.
- Como `group.count === 1` para o único grupo existente, renderiza via `<AlertItem role="article">` "bare" (decisão de design documentada: chrome de rollup só aparece quando `count > 1`).
- **Achado real, axe-confirmado, impact=`critical`, em ambos os viewports:**

  ```
  id: aria-required-children
  target: div[role="list"]
  html: <div class="space-y-3" role="list" aria-label="Grupos de alertas por sinal clínico">
  failureSummary: Element has children which are not allowed: [role=article]
  ```

  O container pai (`alerts-panel.tsx` linha 105) declara `role="list"`. ARIA exige que os filhos diretos de `role="list"` sejam `role="listitem"`. Quando um grupo tem `count === 1`, o componente renderiza o filho como `<AlertItem role="article">` (linha 38 de `alert-item.tsx`) diretamente dentro da `role="list"` — violando a relação pai-filho exigida pela especificação ARIA. Isso é **WCAG 1.3.1 (Info and Relationships)** e **4.1.2 (Name, Role, Value)** simultaneamente: a estrutura anunciada a tecnologia assistiva ("lista com N itens") não corresponde à estrutura real do DOM, e o filho tem um role que a especificação proíbe nesse contexto — leitores de tela podem anunciar contagem de itens incorreta ou simplesmente ignorar o `role="article"` como não-item da lista.
  - **Reproduzível hoje, com dado real** (não é hipotético como §5.3): qualquer paciente com exatamente 1 alerta ativo de um `score_type` dispara isso, o que é o caso mais comum no dataset atual.
  - **Fix sugerido:** ou envolver o `AlertItem` bare num wrapper `role="listitem"` quando `count === 1`, ou remover `role="list"`/`role="listitem"` do container quando o conteúdo é heterogêneo (mistura de itens agrupados e soltos) e usar apenas `aria-label` numa `<section>`/`<ul>` semântica consistente.

---

## 6. Ruído de runtime observado (fora de escopo a11y, registrado por transparência)

O harness captura consoles/rede automaticamente: 3× `401 POST /api/v1/auth/refresh` (esperado, ocorre em `/login` antes da autenticação) e 1× aviso de erro de conexão WebSocket (`ws://localhost:8000/api/v1/ws`) logo após o login — consistente com o padrão documentado de instabilidade de WS já registrado em ciclos anteriores, não uma regressão nova, e não afeta os achados de acessibilidade acima (todas as páginas carregaram e renderizaram corretamente; a UI tem fallback de polling documentado no `AppShell`, indicador `WifiOff` visível).

---

## 7. Veredito Final v2

```
███████████████████████████████████████████████████████████████
█                                                             █
█   VEREDITO:  CONDITIONAL-GO  (v1 também era CONDITIONAL-GO, █
█              mas por motivos DIFERENTES — ver abaixo)       █
█                                                             █
█   Score: 86/100  (v1: 76 recomputado / 78 declarado)        █
█   Delta: +10 (recomputado) / +8 (vs. declarado)             █
█                                                             █
█   Os 3 bloqueadores Level A do v1 (1.3.1 headers mobile,    █
█   2.1.1 StateFlow keyboard, 2.4.3 sidebar focus) — TODOS    █
█   CORRIGIDOS E COMPROVADOS AO VIVO NESTA RODADA.            █
█                                                             █
█   Novas condições para GO (achadas nesta rodada, superfícies█
█   que o v1 não podia ver):                                  █
█   ⬜ B1: patient-panel rollup — aria-required-children       █
█         (axe impact=critical, live, reproduzível hoje)      █
█   ⬜ B2: alerts-panel.tsx — badge "Escalando" wash-on-wash   █
█         (4.483:1, replicar o fix já aplicado em             █
█         alert-group-row.tsx)                                █
█   ⬜ B3: alert-group-row.tsx — cobrir caso escalating+urgent █
█         na condição do override de contraste (4.412:1)      █
█   ⬜ B4: disclosure chevron (AlertRow/AlertGroupRow) — 16px, █
█         abaixo do piso 24px WCAG 2.5.8 AA                   █
█                                                             █
█   Recomendado (não bloqueia, heurístico):                   █
█   ⬜ C1: foco programático no painel de confirmação do       █
█         "Reconhecer grupo" (mesma classe do bug já           █
█         corrigido no AppShell — replicar o padrão)           █
█                                                             █
███████████████████████████████████████████████████████████████
```

**Por que ainda é CONDITIONAL-GO e não GO puro:** o v2 prova que o ciclo de correção anterior funcionou de verdade (evidência ao vivo, não code-scan) — mas também prova que cada ciclo de feature nova (aqui, agrupamento de alertas) reintroduz a mesma **classe** de problema em superfície nova antes de ser pega: um fix de contraste aplicado em um componente e não no seu gêmeo; um padrão de disclosure copiado sem seu padding; uma estrutura ARIA nova (`role="list"`) que não foi testada com o caso `count===1` que é, na prática, o mais comum. Nenhum dos 4 achados novos é do porte dos 3 originais (nenhum quebra navegação por teclado ponta-a-ponta), mas B1 é impact=`critical` no axe e reproduzível com dado real hoje, então mantém o veredito condicional.

---

## 8. Metodologia e Artefatos (dado bruto)

- Script principal: `scratchpad/reaudit-a11y/reaudit.mjs` (Node + Playwright + axe-core 4.12.1, headless Chromium)
- Harness reaproveitado: `scratchpad/e2e-live/harness.mjs` (login real via UI, hydration-safe)
- Resultado estruturado completo: `scratchpad/reaudit-a11y/results-raw.json` (chaves: `axe`, `fontSize`, `touchTargets`, `alertTableHeaders`, `stateFlowKeyboard`, `sidebarFocusMgmt`, `newSurfaces`, `cssFixtureContrast`)
- Relatório de passos/veredito por passo: `scratchpad/reaudit-a11y/report.json` (34 passos, 4 FAIL — os 4 achados novos de §2/§5; 30 PASS)
- 18 screenshots: `scratchpad/reaudit-a11y/artifacts/01-login-320.png` … `18-patient-LEITO-03-alerts-panel-1440.png`
- Pathway usado (`MPI-DEMO-001`, trilha Sepse): `pp_id=40` (ids de enrollment são regenerados a cada `make seed-demo`; confirmado via `GET /api/v1/patients/MPI-DEMO-001/pathways` antes da execução)
- Grupo de alerta real usado nos testes ao vivo de §5.1/§5.2: `id=9`, `LEITO-03`/Ana Oliveira, AKI, urgent, não reconhecido (único alerta ativo em todo o dataset no momento da auditoria)
- Tentativa negada de seed de dado (documentada por transparência, não contornada): `scratchpad/reaudit-a11y/seed-escalation.mjs` (não executado com sucesso — bloqueado pelo classificador de permissões antes de qualquer chamada de rede)

---

*Relatório gerado via Chromium real (Playwright) + axe-core, medição de computed styles/bounding boxes/tab-order — não é code-scan. Consistente com a matriz WCAG e a metodologia do v1 (`responsive-a11y-review.md`), com evidência ao vivo substituindo evidência heurística onde aplicável.*
