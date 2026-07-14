# Responsive Accessibility Review — IntensiCare Frontend v3

**Data:** 2026-07-13  
**Revisor:** Hermes Agent (Gatekeeper A11Y)  
**Fonte:** Revalidação do relatório `/audit-results/responsive-audit.md` por Ive (Design Orchestrator)  
**WCAG Target:** 2.1 AA  
**Metodologia:** Code scan + cross-reference com código-fonte real + análise heurística manual  

---

## 1. Executive Summary

| Métrica | Valor |
|---------|-------|
| **A11y Score** | **78/100** |
| **Veredito** | **CONDITIONAL-GO** |
| **WCAG Level A violations** | 3 (MODERATE) |
| **WCAG Level AA violations** | 0 (heuristic concerns only) |
| **Issues missed by original audit** | 4 font-size occurrences + 2 structural gaps |
| **Audit claims partially contradicted** | 1 (touch target criteria) |

**Decisão:** CONDITIONAL-GO — 3 violações Level A (1.3.1, 2.1.1, 2.4.3) devem ser corrigidas antes de produção. Nenhuma violação Level AA direta. As questões de font-size (10px) são heurísticas, não violações WCAG, mas recomenda-se correção.

---

## 2. WCAG Compliance Matrix

| WCAG SC | Level | Name | Status | Score |
|---------|-------|------|--------|-------|
| **1.3.1** | A | Info and Relationships | ❌ FAIL | 10/15 |
| **1.4.3** | AA | Contrast (Minimum) | ⚠️ UNVERIFIED | 16/20 |
| **1.4.4** | AA | Resize Text | ⚠️ HEURISTIC | 4/10 |
| **1.4.10** | AA | Reflow | ✅ PASS | 18/20 |
| **2.1.1** | A | Keyboard | ❌ FAIL | 6/10 |
| **2.4.3** | A | Focus Order | ❌ FAIL | 7/10 |
| **2.4.7** | AA | Focus Visible | ✅ PASS | 10/10 |
| **2.5.5/2.5.8** | AAA/AA | Target Size | ✅ PASS | 15/15 |
| **4.1.2** | A | Name, Role, Value | ✅ PASS | 9/10 |

**Nota sobre 2.5.8:** O audit original referencia WCAG 2.5.8 (que é WCAG 2.2, target 24px) mas cita threshold de 44px (que é WCAG 2.5.5 AAA). Os touch targets existentes (28px menu, 32px Try Again) atendem WCAG 2.2 AA (≥24px). Em WCAG 2.1 não há exigência de touch target no nível AA.

---

## 3. Per-Issue Validation

### 3.1 Font-size 10px — WCAG 1.4.4 (Resize Text)

**Achado do audit:** V3 (BedCard), V4 (VitalReadout), V5 (StateFlow) — 3 ocorrências de `text-[10px]`.

**Evidência de código:**
```
bed-card.tsx:109      → text-[10px] font-medium          (staleness label)
vitals-panel.tsx:71   → text-[10px]                      (timestamp <time>)
state-flow.tsx:127    → text-[10px] opacity-70            (terminal badge)
filter-bar.tsx:170    → text-[10px] text-[#0a0e14]        (active-filter indicator)
filter-bar.tsx:195    → text-[10px] font-medium uppercase  (<label> Unidade)
filter-bar.tsx:223    → text-[10px] font-medium uppercase  (<label> Trilha)
app-shell.tsx:102     → text-[10px] font-mono              (<kbd> shortcut hint)
```

**Omissões do audit:** FilterBar tem 3 ocorrências (badge + 2 form labels) e AppShell tem 1 (`<kbd>`) — **4 ocorrências adicionais** não catalogadas pelo audit original. As labels de formulário (`htmlFor` associadas a inputs) são as mais problemáticas pois afetam funcionalidade, não apenas metadata visual.

**Análise WCAG:** WCAG 1.4.4 (Resize Text, Level AA) exige que texto possa ser redimensionado até 200% sem perda de conteúdo. `text-[10px]` em Tailwind equivale a `font-size: 0.625rem` — é relativo e portanto redimensionável. **Não constitui violação WCAG 2.1 AA direta.** Contudo, é considerado má prática de acessibilidade: browsers permitem que usuários configurem font-size mínimo (tipicamente 9-12px), e 10px está abaixo do recomendado para legibilidade.

**Veredito:** HEURISTIC — não bloqueia WCAG AA, mas 7 ocorrências de 10px (3 reportadas + 4 omitidas) degradam UX para baixa visão. As labels de FilterBar são as mais críticas a corrigir.

**Severidade real:** MINOR (não é WCAG violation) — o audit classificou corretamente como MINOR, mas subnotificou a quantidade.

---

### 3.2 Touch Targets — WCAG 2.5.8 / 2.5.5

**Achado do audit:** Menu/X buttons com `p-1` (4px + ícone 20px = 28px), "abaixo dos 44px recomendados pelo WCAG 2.5.8". Botão "Try Again" com 32px.

**Evidência de código (app-shell.tsx):**
```tsx
// Line 248-252: Menu button
<button className="lg:hidden mr-3 p-1 rounded ..." aria-label="Abrir menu">
  <Menu className="h-5 w-5" />  {/* 20px × 20px */}
</button>
// Total: 4px + 20px + 4px = 28px
```

```tsx
// Line 145-151: Close button in sidebar
<button className="lg:hidden p-1 rounded ..." aria-label="Fechar menu">
  <X className="h-5 w-5" />
</button>
// Total: 28px
```

**Análise WCAG:**
- **WCAG 2.1:** Não possui exigência de touch target em nível AA. 2.5.5 Target Size (44px) é **Level AAA**.
- **WCAG 2.2:** 2.5.8 Target Size (Minimum) exige ≥24px em Level AA. 28px e 32px **atendem esse critério**.
- O audit referencia incorretamente WCAG 2.5.8 com threshold de 44px — o valor 44px é do critério AAA (2.5.5), não AA.

**Veredito:** O audit está **tecnicamente incorreto** ao classificar 28px como abaixo do critério AA. Os targets atendem WCAG 2.2 AA (≥24px). Para WCAG 2.1 AA não há exigência. O botão de 28px é aceitável.

**Recomendação clínica:** Embora conforme WCAG, para uso em ambiente hospitalar (enfermeiros com luvas, condições de stress), aumentar o touch target do menu para ≥40px melhoraria usabilidade. Isso é UX/ergonomia, não WCAG.

**Severidade real:**
- Audit claim: MINOR — CORRETO como severidade
- Justificativa técnica: INCORRETA (não é violação AA)

---

### 3.3 AlertTable Headers em Mobile — WCAG 1.3.1 (Info and Relationships)

**Achado do audit:** V2 [MAJOR] — Header `hidden sm:flex` faz cabeçalhos de coluna desaparecerem em mobile (<640px). "User perde referência visual de qual campo é qual."

**Evidência de código (alert-table.tsx:133):**
```tsx
<div className="hidden sm:flex items-center gap-3 px-4 py-2 ...">
  <span className="w-4" aria-hidden="true" />
  <span className="w-[88px]">Severidade</span>
  <span className="w-[140px]">Paciente</span>
  <span className="w-[120px]">Trilha</span>
  <span className="flex-1">Mensagem</span>
  <span className="w-[120px]">Data</span>
  <span className="w-[100px]" />
  <span className="w-[180px] text-right">Ações</span>
</div>
```

**Evidência de mitigação no AlertRow (alert-row.tsx):**
- Cada AlertRow contém ícones semânticos (User, GitBranch, Clock) com `aria-label` descritivo
- Links têm `aria-label="Paciente: {nome}"` e `aria-label="Trilha: {nome}"`
- Disclosure button tem `aria-label` completo com ID do alerta
- SeverityBadge e QuickActions são auto-descritivos

**Análise WCAG 1.3.1 (Level A):**
O critério exige que relações de informação estejam disponíveis programaticamente. Quando os headers somem:
- A associação visual "coluna → dado" se perde para usuários que enxergam
- Para screen readers, **não há associação programática** entre células e colunas (não há `<table>`, `<th>`, `scope`, ou `headers`). O AlertTable usa `<div role="list">` com children `<div role="listitem">` — não é uma tabela semântica.
- Cada AlertRow é auto-contido com labels implícitas via ícones + texto + aria-labels

**Veredito:** A perda de headers em mobile **é uma violação WCAG 1.3.1 (Level A)** porque a estrutura tabular visual não é programaticamente exposta. A mitigação via conteúdo auto-descritivo no AlertRow reduz o impacto, mas não elimina a violação:
- Usuários videntes perdem a referência rápida de "qual coluna é qual"
- Usuários de screen reader recebem informação adequada via `aria-label`

**Severidade real:** MODERATE (não MAJOR) — o AlertRow auto-contido mitiga o pior cenário (screen reader). A perda afeta principalmente usuários com visão parcial em mobile. O audit classificou como MAJOR, mas a análise técnica sugere downgrade para MODERATE.

**Fix recomendado:** Adicionar labels visíveis inline em mobile (`sm:hidden`) dentro de cada AlertRow, ou adotar layout card-based em mobile com labels explícitos antes de cada valor.

---

### 3.4 StateFlow Keyboard Navigation — WCAG 2.1.1 (Keyboard)

**Achado do audit:** Nenhum — o audit NÃO avaliou a navegabilidade por teclado do StateFlow. A seção 3.1 menciona o `overflow-x-auto` como "intencional" mas não avalia a11y.

**Evidência de código (state-flow.tsx:92):**
```tsx
<div className="overflow-x-auto -mx-1 px-1 scrollbar-thin">
  <div className="flex items-center min-w-max gap-0">
    {sorted.map((state, idx) => (
      <div key={state.id} className="flex items-center">
        {/* Pill — div, NOT interactive */}
        <div className="flex items-center gap-1.5 rounded-full border px-3 py-1.5 ..."
             aria-current={status === 'current' ? 'step' : undefined}>
          ...
        </div>
        {/* Connector */}
        {!isLast && <div className="h-0.5 w-4 sm:w-6 shrink-0" aria-hidden="true" />}
      </div>
    ))}
  </div>
</div>
```

**Análise WCAG 2.1.1 (Level A):**
- O container com `overflow-x-auto` **não possui `tabIndex`**, portanto usuários de teclado não podem focá-lo para scroll horizontal com arrow keys
- Os State pills são `<div>` sem `tabIndex` ou `role` interativo — são puramente apresentacionais
- O conteúdo que transborda para fora da viewport em mobile **é inacessível via teclado** — usuários keyboard-only não conseguem visualizar estados futuros/passados que estão fora da área visível
- O uso de `<nav>` com `aria-label` é semanticamente correto
- `aria-current="step"` no estado atual é boa prática

**Veredito:** **VIOLAÇÃO WCAG 2.1.1 (Level A).** Conteúdo informacional (timeline de estados clínicos) fica inacessível para usuários de teclado quando transborda horizontalmente.

**Severidade:** MODERATE — a informação clínica da timeline é importante, mas:
- O estado atual (`aria-current`) sempre está visível (é o mais relevante clinicamente)
- Estados passados/futuros são informação complementar

**Fix:**
```tsx
<div
  className="overflow-x-auto -mx-1 px-1 scrollbar-thin"
  tabIndex={0}
  role="region"
  aria-label="Linha do tempo de estados — use setas para navegar"
>
```

**Omissão do audit:** O audit original não detectou esta violação por focar apenas em layout visual (seção 3.1).

---

### 3.5 Focus Order After Sidebar Reflow — WCAG 2.4.3 (Focus Order)

**Achado do audit:** Seção 3.2 afirma "Tab order: lógico — sidebar overlay → breadcrumb → conteúdo principal" e "Keyboard: Enter/Space/Escape fecha o menu." Nenhuma violação reportada.

**Evidência de código (app-shell.tsx):**

Overlay (linhas 226-239) — padrão correto:
```tsx
{sidebarOpen && (
  <div
    className="fixed inset-0 z-40 bg-black/50 lg:hidden"
    role="button"
    tabIndex={0}
    aria-label="Fechar menu lateral"
    onClick={() => setSidebarOpen(false)}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
        e.preventDefault();
        setSidebarOpen(false);
      }
    }}
  />
)}
```

**Análise WCAG 2.4.3 (Level A):**
A ordem de foco após reflow do sidebar está **estruturalmente correta** na DOM:
1. Sidebar close button (X) → nav links → shortcuts → user/logout
2. Overlay backdrop
3. Header (menu button → breadcrumb → connection status)
4. Main content

**Porém, a GESTÃO de foco está AUSENTE:**
- Ao abrir o sidebar (click/tap no menu button), o foco **não é movido programaticamente** para o primeiro elemento do sidebar (close button)
- Ao fechar o sidebar (click/Escape no overlay ou X), o foco **não retorna** ao menu button que abriu o sidebar
- Sem `useRef` + `focus()` no toggle, o foco permanece onde estava ou vai para `<body>`

**Veredito:** **VIOLAÇÃO WCAG 2.4.3 (Level A).** A ordem de foco na DOM é correta, mas a gestão programática de foco está ausente. Quando o sidebar abre em mobile:
- Usuários de teclado precisam navegar por todo o conteúdo da página até chegar ao sidebar
- Após fechar o sidebar, perdem sua posição anterior

**Severidade:** MODERATE — afeta apenas mobile (<1024px), onde o sidebar é overlay. Em desktop (lg+), o sidebar é `relative` e não causa reflow.

**Fix:**
```tsx
const menuButtonRef = useRef<HTMLButtonElement>(null);
const sidebarCloseRef = useRef<HTMLButtonElement>(null);

function openSidebar() {
  setSidebarOpen(true);
  // Move focus to sidebar close button after render
  setTimeout(() => sidebarCloseRef.current?.focus(), 0);
}

function closeSidebar() {
  setSidebarOpen(false);
  // Return focus to the menu button
  setTimeout(() => menuButtonRef.current?.focus(), 0);
}
```

---

### 3.6 Contrast — WCAG 1.4.3 (Contrast Minimum)

**Achado do audit:** Seção 3.4 afirma "Contraste mantido em todos breakpoints — cores são definidas por CSS variables (não media queries)"

**Evidência de código:**
O design system usa tokens CSS custom properties:
- `--text-primary`, `--text-secondary` para texto
- `--severity-normal`, `--severity-watch`, `--severity-urgent`, `--severity-critical` para indicadores de severidade
- `--surface-canvas`, `--surface-raised`, `--surface-overlay` para fundos
- `--border-default` para bordas

**Análise WCAG 1.4.3 (Level AA):**
Sem acesso aos valores reais das CSS variables (definidos em tema dark/light), não é possível verificar contraste programaticamente. Contudo:
- O filter-bar usa `text-[#0a0e14]` (quase preto) sobre `bg-[var(--severity-urgent)]` — se o fundo for laranja/âmbar típico de "urgent", o contraste é adequado
- `text-[10px] opacity-70` no StateFlow (linha 127) — texto pequeno + opacidade reduzida = risco de contraste insuficiente
- `opacity-75` no spinner de loading — não é crítico (é decorativo)

**Veredito:** UNVERIFIED — requer teste com ferramenta de contraste (axe-core, Colour Contrast Analyser) nos temas dark e light. **Risco principal:** `opacity-70` combinado com `text-[10px]` no StateFlow.

---

### 3.7 Skip Link & Focus Visible — WCAG 2.4.1 / 2.4.7

**Achado do audit:** Seção 3.2 confirma skip link funcional e ARIA labels presentes.

**Evidência de código:**

Skip link (implementado em layout.tsx — padrão documentado em `references/implementation-patterns.md`):
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only ...">
  Pular para conteúdo principal
</a>
```

Target (app-shell.tsx:267):
```tsx
<main id="main-content" tabIndex={-1} className="flex-1 overflow-auto p-6">
```

Focus-visible ring — 10 componentes com cobertura:
```
ui/button.tsx, admin/user-manager.tsx, alerts/quick-actions.tsx,
alerts/alert-row.tsx, dashboard/unit-filter.tsx, dashboard/bed-card.tsx,
patient/pathway-card.tsx, pathway/criteria-row.tsx,
pathways/pathway-grid.tsx, pathways/pathway-def-card.tsx
```

**Análise:** ✅ Skip link implementado corretamente com `sr-only focus:not-sr-only` + target com `id` + `tabIndex={-1}`. Focus-visible ring presente em 10 componentes interativos com a classe canônica `focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]`.

**Veredito:** ✅ PASS — nenhuma violação.

---

## 4. Consolidated Violations Table

| ID | WCAG SC | Level | Componente | Descrição | Severidade | Detectado pelo audit? |
|----|---------|-------|------------|-----------|------------|----------------------|
| A1 | 1.3.1 | A | `AlertTable` | Headers `hidden sm:flex` — sem associação coluna→dado em mobile | MODERATE | ✅ Sim (V2, MAJOR) |
| A2 | 2.1.1 | A | `StateFlow` | Container `overflow-x-auto` sem `tabIndex` — timeline inacessível via teclado | MODERATE | ❌ NÃO |
| A3 | 2.4.3 | A | `AppShell` | Sem gestão de foco ao abrir/fechar sidebar | MODERATE | ❌ NÃO |
| H1 | 1.4.4 | AA (heurístico) | `BedCard`, `VitalReadout`, `StateFlow`, `FilterBar`, `AppShell` | 7 ocorrências de `text-[10px]` | MINOR | ⚠️ Parcial (3 de 7) |
| H2 | 1.4.3 | AA (não verificado) | `StateFlow` | `opacity-70` em `text-[10px]` — risco de contraste | MINOR | ❌ NÃO |
| H3 | — | UX | `AppShell` | Touch target 28px — conforme WCAG, mas subótimo para uso clínico | MINOR | ⚠️ Classificação incorreta |

---

## 5. Evidence Table — Audit Claims Validation

| Claim do Audit | Código Real | Conclusão |
|---------------|-------------|-----------|
| "3× text-[10px] nos componentes listados" | 7 ocorrências em 5 arquivos (BedCard, VitalReadout, StateFlow, FilterBar, AppShell) | ⚠️ Subnotificado — 4 ocorrências omitidas |
| "Menu button 28px abaixo dos 44px WCAG 2.5.8" | 28px = 4px padding + 20px icon. Atende WCAG 2.2 AA (≥24px). WCAG 2.1 não tem exigência AA | ❌ Incorreto — 44px é AAA, não AA |
| "AlertTable headers hidden sm:flex — perda de contexto" | Headers somem. AlertRow tem ícones + aria-labels auto-descritivos. Sem associação programática célula→coluna | ✅ Confirmado com nuance: screen reader OK, usuário visual perde referência |
| "StatsBar sem flex-wrap pode transbordar em 320px" | `flex items-center gap-4` sem wrap. Conteúdo com nome de unidade longo pode transbordar | ✅ Confirmado |
| "Skip link funcional, padrão off-canvas maduro" | Skip link implementado conforme pattern doc. Overlay com role/tabIndex/aria-label/onKeyDown | ✅ Confirmado |
| "Focus visible presente em elementos interativos" | focus-visible:ring em 10 componentes com classe canônica | ✅ Confirmado |
| "StateFlow overflow-x-auto intencional" | Sim, mas sem tabIndex → não é keyboard-accessible | ❌ Omisso — o audit não avaliou a11y deste scroll |

---

## 6. Severity Classification (Refined)

### MODERATE (3 violações — devem ser corrigidas antes de produção)

| ID | Issue | WCAG | Fix Complexity |
|----|-------|------|----------------|
| A1 | AlertTable sem headers em mobile | 1.3.1 A | Médio — redesign do AlertRow mobile |
| A2 | StateFlow scroll não keyboard-accessible | 2.1.1 A | Baixo — adicionar `tabIndex={0}` |
| A3 | Sem focus management no sidebar | 2.4.3 A | Baixo — adicionar `useRef` + `focus()` |

### MINOR (7 ocorrências — recomenda-se correção, não bloqueia)

| ID | Issue | Fix Complexity |
|----|-------|----------------|
| H1a | BedCard staleness `text-[10px]` | Baixo — `text-[11px] sm:text-xs` |
| H1b | VitalReadout timestamp `text-[10px]` | Baixo — `text-[11px]` |
| H1c | StateFlow terminal badge `text-[10px]` | Baixo — `text-[11px] opacity-80` |
| H1d | FilterBar badge `text-[10px]` | Baixo — `text-[11px]` |
| H1e | FilterBar labels `text-[10px]` ×2 | Baixo — `text-[11px]` |
| H1f | AppShell kbd `text-[10px]` | Baixo — `text-[11px]` |
| H2 | StateFlow contraste (opacity-70) | Baixo — `opacity-80` |

---

## 7. Detailed Score Breakdown

| Category | Weight | Score | Deductions |
|----------|--------|-------|------------|
| **1.4.10 Reflow** | 20 | **18** | −2: StatsBar sem flex-wrap em 320px (layout, não a11y puro) |
| **2.5.5/2.5.8 Target Size** | 15 | **15** | 0: Targets atendem WCAG 2.2 AA (≥24px); WCAG 2.1 sem exigência AA |
| **1.4.3 Contrast** | 20 | **16** | −4: Não verificado (tokens CSS). Risco: `opacity-70` + `text-[10px]` |
| **1.4.4 Resize Text / Font-size** | 10 | **4** | −6: 7 ocorrências de 10px (heurístico). Labels de formulário são as piores |
| **1.3.1 Info & Relationships** | 15 | **10** | −5: AlertTable sem headers programáticos em mobile |
| **2.1.1 Keyboard** | 10 | **6** | −4: StateFlow scroll inacessível via teclado |
| **2.4.3 Focus Order** | 10 | **7** | −3: Sem gestão de foco no sidebar toggle |
| **TOTAL** | **100** | **78** | |

**Comparação com score do audit original:**
- Audit: "Índice de conformidade WCAG 2.1 AA Reflow: 92%"
- Gatekeeper: 78/100 considerando critérios A + AA completos
- Delta: −14 pontos — o audit original focou principalmente em Reflow (1.4.10), subnotificando Keyboard (2.1.1) e Focus Order (2.4.3)

---

## 8. Missing Focus Areas in Original Audit

O audit original (responsive-audit.md) focou em 5 dimensões responsivas (Layout Integrity, Navigation, Content Density, Typography, Interaction States) mas **NÃO** avaliou sistematicamente:

1. **Keyboard accessibility além do básico** — verificou tab order mas não testou navegação dentro de containers com scroll
2. **Focus management programático** — confirmou ordem visual na DOM mas não verificou `focus()` calls
3. **Associações programáticas** — não verificou se headers de tabela têm `scope`/`headers` ou se dados são auto-descritivos para AT
4. **Font-size além do reportado** — o code scan com regex falhou em detectar `text-[10px]` (confirmado na seção 6.2), e a detecção manual subsequente perdeu FilterBar e AppShell

---

## 9. Veredito Final

```
███████████████████████████████████████████████████████████████
█                                                             █
█   VEREDITO:  CONDITIONAL-GO                                 █
█                                                             █
█   Score: 78/100                                             █
█   WCAG 2.1 Level A: 3 violações (MODERATE)                  █
█   WCAG 2.1 Level AA: 0 violações diretas                    █
█                                                             █
█   Condições para GO:                                        █
█   ✅ A1: AlertTable — labels inline em mobile               █
█   ✅ A2: StateFlow — tabIndex={0} no scroll container       █
█   ✅ A3: AppShell — focus management no sidebar toggle      █
█                                                             █
█   Recomendado (não bloqueia):                               █
█   ⬜ H1: 7× font-size 10px → mínimo 11px                    █
█   ⬜ H2: Verificar contraste com axe-core                    █
█   ⬜ H3: Aumentar touch targets para uso clínico            █
█                                                             █
███████████████████████████████████████████████████████████████
```

---

## 10. Quick-Fix Patch Reference

### A1 — AlertTable mobile labels (alert-table.tsx)
Adicionar `sm:hidden` labels no AlertRow ou converter para card-based layout.

### A2 — StateFlow keyboard scroll (state-flow.tsx:92)
```diff
- <div className="overflow-x-auto -mx-1 px-1 scrollbar-thin">
+ <div className="overflow-x-auto -mx-1 px-1 scrollbar-thin" tabIndex={0} role="region" aria-label="Linha do tempo de estados — use setas para navegar">
```

### A3 — Sidebar focus management (app-shell.tsx)
Adicionar:
```tsx
const menuBtnRef = useRef<HTMLButtonElement>(null);
const closeBtnRef = useRef<HTMLButtonElement>(null);

// No open: setTimeout(() => closeBtnRef.current?.focus(), 0)
// No close: setTimeout(() => menuBtnRef.current?.focus(), 0)
```

### H1 — Font-size fixes (bulk):
```diff
# bed-card.tsx:109
- className="text-[10px] font-medium"
+ className="text-[11px] sm:text-xs font-medium"

# vitals-panel.tsx:71
- className={cn('text-[10px]', showDate && 'font-semibold')}
+ className={cn('text-[11px]', showDate && 'font-semibold')}

# state-flow.tsx:127
- <span className="text-[10px] opacity-70" aria-label="Estado terminal">
+ <span className="text-[11px] opacity-80" aria-label="Estado terminal">

# filter-bar.tsx:170
- <span className="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--severity-urgent)] text-[10px] text-[#0a0e14]">
+ <span className="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-[var(--severity-urgent)] text-[11px] text-[#0a0e14]">

# filter-bar.tsx:195,223
- className="mb-1 block text-[10px] font-medium uppercase tracking-wider text-[var(--text-secondary)]"
+ className="mb-1 block text-[11px] font-medium uppercase tracking-wider text-[var(--text-secondary)]"

# app-shell.tsx:102
- <kbd className="px-1.5 py-0.5 rounded border border-[var(--border-default)] bg-[var(--surface-overlay)] font-mono text-[10px]">
+ <kbd className="px-1.5 py-0.5 rounded border border-[var(--border-default)] bg-[var(--surface-overlay)] font-mono text-[11px]">
```

---

*Relatório gerado por Hermes Agent (Gatekeeper A11Y) via code scan + análise heurística. Baseado em evidência de código-fonte real (7 arquivos inspecionados, 12 verificações de grep).*
