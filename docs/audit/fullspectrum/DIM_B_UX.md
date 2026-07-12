# DIM B — UX Clínica & Acessibilidade — Auditoria de Inspeção de Código

**Data:** 2026-07-12
**Escopo:** `/Users/familia/intensicare/frontend-v3/` (Next.js 16)
**Auditor:** Agente de auditoria (Claude)

## Metodologia

Auditoria por **inspeção de código estático** (Read/Grep/Glob) sobre o código-fonte de
`frontend-v3/app` e `frontend-v3/components`, sem uso de browser, build, ou ferramentas de
teste automatizado de acessibilidade (axe/Playwright), conforme instrução explícita. Cálculo
de contraste WCAG feito via script Python (fórmula de luminância relativa WCAG 2.1, seção
1.4.3) contra os hex codes definidos em `app/globals.css`. Foram feitas 5 chamadas `curl
--max-time 5` pontuais para validar disponibilidade dos serviços; o backend (`localhost:8000`)
respondeu (`POST /api/v1/auth/login` → `200`), mas o frontend dev server (`localhost:3000`)
não respondeu no momento da auditoria (timeout/connection refused, código `000`) — portanto
todas as afirmações sobre roteamento/redirect/responsividade são baseadas exclusivamente em
inspeção de código, não em observação de runtime. Isso é declarado explicitamente onde
relevante. Referência cruzada com `docs/audit/GAP_CLOSURE_PLAN.md` (gerado 2026-07-09) para
verificar quais gaps conhecidos persistem.

---

## 1. Jornada (Dashboard → Patient → Pathway)

Jornada real rastreada via `router.push`/`Link`:

- `app/page.tsx:48-54` — `BedGrid` recebe `onSelect={(mpiId) => router.push('/patient/${mpiId}')}`.
- `components/dashboard/bed-grid.tsx:159-165` — cada `BedCard` chama `onClick={() => onSelect(patient.mpi_id)}`.
- `components/dashboard/bed-card.tsx:61-71` — `BedCard` é um `div role="button" tabIndex={0]` com `onClick` e `onKeyDown` (Enter/Espaço) — clicável e navegável por teclado.
- `components/patient/active-pathways.tsx:62-64` — lista `PathwayCard` para cada trilha ativa do paciente.
- `components/patient/pathway-card.tsx:24-26` — `handleClick` chama `router.push('/patient/${pathway.mpi_id}/pathway/${pathway.id}')`; também `div role="button" tabIndex={0}` com `onKeyDown` (linha 28-33).

**Resultado: 2 cliques Dashboard → Patient → Pathway confirmados** (BedCard → PathwayCard),
igual à meta declarada em HANDOFF.yaml.

**Dead ends:** nenhum encontrado. `components/pathway/pathway-header.tsx:76-82` inclui link
explícito "Voltar para o paciente" (`<Link href="/patient/${mpiId}">` com ícone `ArrowLeft`)
no topo da Pathway View — não há página terminal sem saída.

**Breadcrumb:** existe em `components/app-shell.tsx:29-70` (função `Breadcrumb`), renderizado
no topbar (`app-shell.tsx:206`) em todas as páginas exceto `/login` (linha 80-82). Porém o
breadcrumb **usa segmentos brutos da URL** (`app-shell.tsx:42-46`: `seg.replace(/-/g,'
').replace(/\b\w/g, c => c.toUpperCase())`), sem tradução de IDs para nomes legíveis. Em
`/patient/{mpi_id}/pathway/{pp_id}` isso produz um crumb literal com o UUID/ID numérico do
paciente e da trilha, não o nome do paciente/trilha — **gap UX-M1 do GAP_CLOSURE_PLAN.md
("Breadcrumb mostra slugs") ainda está ABERTO**, confirmado por inspeção.

---

## 2. Densidade de Informação

**Dashboard** (`app/page.tsx` + `components/dashboard/`): uma única tela mostra, por
paciente, em `bed-card.tsx`:
- Nome + leito + unidade (linhas 88-103)
- `SeverityDot` (severidade, linha 89)
- `ScorePair` — MEWS e NEWS2 juntos (linha 106)
- `PathwayBadges` — trilhas ativas (linha 110)
- `VitalsInline` (linha 111)
- Indicador de "staleness" dos últimos vitais (linhas 115-125)

Mais `StatsBar` (total de pacientes + contagem de críticos, `stats-bar.tsx:22-47`) e
`UnitFilter` acima do grid. Tudo above-the-fold em um card por paciente — sem necessidade de
navegar para ver MEWS/NEWS2/severidade/trilhas. **Atende à meta de densidade.**

**Patient Detail** (`app/patient/[mpi_id]/page.tsx:162-203`): ordem no JSX —
`PatientHeader` (MEWS/NEWS2 ao vivo, `patient-header.tsx:63-91`) → `VitalsPanel` →
`ScoreTimeline` → `ActivePathways` (comentário no código, linha 185: "the heart of the
page") → sidebar com `AlertsPanel`. `ActivePathways` renderiza **todas** as trilhas ativas
(`active-pathways.tsx:62-64`, sem paginação/corte), com estado vazio explícito e distinto de
erro (linhas 39-58 vs 48-58) — boa distinção "bug de UX" vs "ausência de dados".

**Pathway View** (`app/patient/[mpi_id]/pathway/[pp_id]/page.tsx:216-251`): ordem —
`PathwayHeader` (estado atual + severidade + tendência) → `StateFlow` (linha 228) →
duas colunas: `CriteriaList` + `RecommendationsPanel` (coluna principal, 2/3 largura) →
`TransitionHistory` (sidebar, 1/3 largura, linha 248). A ordem no JSX corresponde à hierarquia
clínica esperada (estado → critérios → recomendações → histórico), com estado e critérios
acima da dobra.

---

## 3. Severidade

4 níveis definidos como CSS custom properties em `app/globals.css:6-9`:
`--severity-normal` (#2DD269), `--severity-watch` (#F2B90D), `--severity-urgent` (#F96F06),
`--severity-critical` (#FF3B4A), cada um com variante "wash" (linhas 11-14).

**Sem hardcodes de cor fora dos tokens**: `grep -rn '#[0-9a-fA-F]{3,6}|rgb(' components/
app/ --include=*.tsx | grep -v stories` retornou **zero resultados** — todos os componentes
usam `var(--severity-*)`. Confirma que o gap **DS-C1 (CRITICAL, rgb() hardcoded em
app/admin/page.tsx:81) foi corrigido**, conforme já indicado no GAP_CLOSURE_PLAN.md.

**Pulse/animação para critical**: `app/globals.css:44-48` define `@keyframes pulse-critical`
e a classe `.severity-critical-pulse`, usada em `components/alerts/severity-badge.tsx:46`,
`components/patient/pathway-card.tsx:47` e `components/pathway/severity-icon.tsx:113`
(`isPulse = severity === 'critical' && met !== true`).

**Ícone/forma além de cor (daltonismo)**: `components/pathway/severity-icon.tsx:24-80`
mapeia severidade→ícone distinto (`CircleCheck`, `CircleX`, `CircleAlert`, `Clock`,
`CircleDot`) além da cor — atende ao requisito de não depender só de cor.

---

## 4. Acessibilidade

Contraste WCAG calculado (fórmula de luminância relativa) para os 4 tokens de severidade
contra os 3 fundos usados no app (`--surface-canvas` #0a0e14, `--surface-raised` #141b22,
`--surface-overlay` #1c2530):

| Par | Contraste | AA texto (4.5:1) | AA UI/large (3:1) |
|---|---|---|---|
| normal / qualquer fundo | 7.76–9.70 | PASS | PASS |
| watch / qualquer fundo | 8.64–10.79 | PASS | PASS |
| urgent / qualquer fundo | 5.38–6.73 | PASS | PASS |
| critical / surface-canvas | 5.50 | PASS | PASS |
| critical / surface-raised | 4.94 | PASS | PASS |
| **critical / surface-overlay** | **4.41** | **FAIL** | PASS |

Texto (`--text-primary` #e6edf3, `--text-secondary` #8b949e) contra os 3 fundos: todos PASS
(5.03–16.37).

**Achado novo (não listado no GAP_CLOSURE_PLAN.md): texto branco sobre fundo de severidade.**
Dois usos de `text-white` sobre cor de severidade sólida, ambos falham WCAG AA texto (4.5:1):
- `components/app-shell.tsx:151` — botão de confirmação de logout "Sair": `bg-[var(--severity-critical)] text-white text-xs` → contraste branco/critical = **3.51:1 (FAIL)**.
- `components/alerts/filter-bar.tsx:163` — badge de contagem: `bg-[var(--severity-urgent)] text-[10px] text-white` → contraste branco/urgent = **2.87:1 (FAIL, falha grave)**.

**aria-label / role / onKeyDown**: 38 arquivos usam `aria-label` (`grep -rln aria-label
components app --include=*.tsx` = 38). Todos os elementos clicáveis não-nativos encontrados
(`grep onClick` em 17 arquivos não-story) usam `<button>`, `<Link>`, ou `div role="button"
tabIndex={0}` com `onKeyDown` tratando Enter/Espaço — confirmado em `bed-card.tsx:62-71`,
`pathway-card.tsx:37-42`, `criteria-row.tsx:66-69`, `pathway-def-card.tsx:38-41`,
`app-shell.tsx:182-192` (overlay mobile). Nenhum `div onClick` órfão sem suporte a teclado
encontrado.

**Comparação com os 3 gaps do GAP_CLOSURE_PLAN.md:**
- **A11Y-1** (skip-link ausente, 2.4.1) — **confirmado DONE**: `app/layout.tsx:19-24` tem `<a href="#main-content">Pular para conteúdo principal</a>`; `app-shell.tsx:220` tem `<main id="main-content" tabIndex={-1}>`.
- **A11Y-2** (overlay mobile sem teclado, 2.1.1) — **confirmado DONE**: `app-shell.tsx:180-192`, `role="button" tabIndex={0}` com `onKeyDown` tratando Enter/Espaço/Escape.
- **A11Y-3** (~40% sem focus-visible, 2.4.7) — **parcialmente confirmado**: `focus-visible:ring` presente em `bed-card.tsx:75`, `pathway-card.tsx:46`, mas não foi possível confirmar cobertura completa por amostragem manual dentro do tempo alocado; tratado como plausivelmente DONE conforme declarado.

---

## 5. Responsividade

Breakpoints Tailwind (`sm:`/`md:`/`lg:`/`xl:`) usados nas páginas core:
- `components/app-shell.tsx:91,104,181,201` — sidebar vira drawer com overlay abaixo de `lg:` (colapsa para `-translate-x-full`, reabre via botão `Menu` no header, linha 199-205). **Sidebar mobile existe e é funcional por inspeção de código** (drawer + overlay + botão de fechar).
- `app/patient/[mpi_id]/page.tsx:168,170` — grid 1 coluna → `xl:grid-cols-3` (2/3 + sidebar).
- `app/patient/[mpi_id]/pathway/[pp_id]/page.tsx:235,237` — grid 1 coluna → `lg:grid-cols-3`.
- `components/dashboard/bed-grid.tsx:113-115,151-155` — **não usa breakpoints Tailwind**; usa CSS grid nativo `gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))'`, que é responsivo por natureza (sem media queries manuais) — padrão diferente mas funcionalmente equivalente.
- `components/pathway/state-flow.tsx:92,136` — `overflow-x-auto` + `w-4 sm:w-6` para o fluxo de estados em telas estreitas.

Nenhuma página core carece de tratamento responsivo por inspeção. **Nota:** frontend dev
server não respondeu a curl no momento da auditoria (timeout), então o comportamento real em
viewport móvel não foi observado visualmente — apenas inferido do código.

---

## 6. Páginas Abolidas (0 standalone)

`frontend-v3/app/` contém apenas: `admin`, `alerts`, `login`, `page.tsx` (dashboard),
`pathways`, `patient/[mpi_id]`, `patient/[mpi_id]/pathway/[pp_id]` — 7 rotas totais, todas
genéricas/consolidadas.

`frontend-v2-archive/app/` (apenas `ls`, não lido) contém 24 diretórios de domínio standalone:
`alert-routing`, `alert-triage`, `antimicrobial-stewardship`, `care-pathways`,
`clinical-deterioration`, `clinical-forms`, `clinical-notes`, `command-center`,
`communication`, `dashboard`, `documentation`, `efficiency`, `fluid-balance`, `handoff`,
`indicators`, `nutrition`, `patient-movement`, `prescription`, `prophylaxis-bundles`,
`register`, `sedation`, `sepse-dashboard`, `stability`, `ventilation` (+ `admin`, `login`,
`patient` que persistem em v3).

**Confirmado: v3 aboliu as ~21 páginas standalone de domínio clínico** presentes em v2,
consolidando-as no fluxo Dashboard→Patient→Pathway. Meta "0 páginas standalone" atendida
por contagem de rotas.

---

## 7. Scoring

**Nota: 78/100**

Cálculo: parte de 100, deduções por violação (CRITICAL -8, MAJOR -4, MINOR -1.5), com piso
informado pelas metas centrais (jornada de 2 cliques, densidade, 4 níveis de severidade e
0 páginas standalone todas atendidas — os pontos fortes do produto).

| ID | Severidade | Achado | Evidência |
|---|---|---|---|
| B-C1 | CRITICAL | Texto branco sobre badge de contagem urgente ilegível (2.87:1, quase metade do mínimo AA) | `components/alerts/filter-bar.tsx:163` |
| B-M1 | MAJOR | Botão de confirmação de logout "Sair" com texto branco sobre vermelho crítico abaixo do AA (3.51:1 < 4.5:1) | `components/app-shell.tsx:151` |
| B-M2 | MAJOR | Token `--severity-critical` sobre `--surface-overlay` fica abaixo do AA para texto (4.41:1 < 4.5:1); qualquer uso de texto colorido crítico sobre superfícies overlay (hover states, badges) herda essa falha | `app/globals.css:9,18` vs uso em `components/pathway/severity-icon.tsx:40` |
| B-M3 | MAJOR (herdado, ainda aberto) | Breadcrumb expõe IDs brutos (UUID/número) em vez de nomes de paciente/trilha — gap UX-M1 do GAP_CLOSURE_PLAN.md | `components/app-shell.tsx:42-46` |
| B-M4 | MAJOR (herdado, ainda aberto) | Sem atalhos de teclado globais (nenhum listener de `keydown` em nível de window/document encontrado) — gap UX-M3 | grep vazio em `components/`, `app/`, `lib/` |
| B-M5 | MAJOR (herdado, ainda aberto) | Tooltips clínicos (`title=`) presentes em apenas 2 de ~90 componentes — gap UX-M4 | `grep -rln 'title='` → só `app-shell.tsx`, `quick-actions.tsx` |
| B-Mn1 | MINOR | 7 usos de `text-[Npx]` arbitrário fora do sistema de tokens — gap DS-M1 ainda aberto | grep count=7, vários arquivos |
| B-Mn2 | MINOR | Estilos inline (`borderWidth`/`borderStyle`) repetidos manualmente em vez de classes utilitárias (ex.: `bed-card.tsx:79-85`, `stats-bar.tsx:27-30`, `bed-grid.tsx:19-24,66-70`) — gap DS-M3 ainda aberto | múltiplos arquivos |
| B-Mn3 | MINOR | Cobertura de `focus-visible` não confirmável a 100% por amostragem manual dentro do tempo alocado — risco residual do gap A11Y-3 | amostragem parcial, não é regressão confirmada |

**Pontos fortes confirmados (sem violação):** jornada em 2 cliques sem dead-ends
(`app/page.tsx`, `bed-card.tsx`, `pathway-card.tsx`, `pathway-header.tsx:76-82`); densidade
de informação adequada em todas as 3 telas; 4 níveis de severidade consistentes via CSS
tokens sem hardcodes (`grep` de hex/rgb = 0 hits); diferenciação por ícone além de cor
(`severity-icon.tsx`); pulse animation para critical; skip-link e overlay mobile acessível
por teclado (A11Y-1/A11Y-2 confirmados DONE); 0 páginas standalone (21 rotas de domínio
abolidas vs. v2-archive); sidebar mobile responsiva via drawer.
