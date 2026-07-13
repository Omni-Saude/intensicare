# Responsive Audit Prompt — IntensiCare Frontend v3

**Objetivo:** Auditar a adaptabilidade responsiva do frontend-v3 em 5 breakpoints críticos, identificando regressões de layout, navegação e legibilidade. O foco é garantir que a jornada do intensivista (Dashboard → Patient Detail → Pathway View) permaneça funcional e navegável em qualquer viewport, incluindo uso em split-screen durante o round multidisciplinar.

## Escopo

- **Repositório:** `/Users/familia/intensicare/frontend-v3/`
- **Stack:** Next.js 16 + Tailwind CSS 4 (utility-first, breakpoint prefixes: `sm:`, `md:`, `lg:`, `xl:`)
- **Componentes auditados:** 42 componentes + 8 páginas
- **WCAG target:** 2.1 AA (inclui critério 1.4.10 Reflow — conteúdo adapta-se sem scroll horizontal em 320px)

## Breakpoints de Teste

| Breakpoint | Largura | Dispositivo/Cenário |
|-----------|---------|---------------------|
| **XS** | 320px | Smartphone pequeno (plantão noturno) |
| **SM** | 480px | Smartphone médio |
| **MD** | 768px | Tablet portrait (round à beira do leito) |
| **LG** | 1024px | Tablet landscape / split-screen 50% |
| **XL** | 1440px | Desktop (round multidisciplinar, monitor grande) |

## Critérios de Auditoria (5 dimensões)

### 1. Layout Integrity (integridade visual)
- [ ] Zero scroll horizontal em qualquer breakpoint (WCAG 1.4.10)
- [ ] Nenhum componente transborda seu container
- [ ] Grids colapsam corretamente (ex: 3-col → 2-col → 1-col)
- [ ] Texto não é truncado sem indicador de overflow
- [ ] Imagens/SVGs mantêm aspect ratio (`max-w-full h-auto`)

**Comandos de verificação:**
```bash
# Detectar scroll horizontal (indicador de layout quebrado)
rg "overflow-x-auto|overflow-x-scroll" components/ app/ --include='*.tsx'

# Verificar ausência de max-w-full em imagens
rg "<img" components/ app/ --include='*.tsx' | grep -v "max-w-full\|className"

# Verificar grid breakpoints definidos
rg "grid-cols-\d|grid-cols-\[" components/ app/ --include='*.tsx'
```

### 2. Navigation Accessibility (navegabilidade)
- [ ] Sidebar colapsa em drawer/hamburger abaixo de `lg:` (1024px)
- [ ] Breadcrumb permanece visível em todos breakpoints
- [ ] Touch targets ≥ 44×44px em viewports ≤ 768px (WCAG 2.5.8)
- [ ] Links de navegação não se sobrepõem em split-screen (1024px/2 = 512px)
- [ ] Tab order permanece lógico após reflow

**Comandos de verificação:**
```bash
# Elementos sem tamanho mínimo de touch target
rg "className=\"[^\"]*w-\d[^\"]*h-\d" components/ --include='*.tsx' | grep -E "w-[123]?[0-9]\b"

# Sidebar responsivo
rg "lg:relative|lg:translate-x-0|-translate-x-full" components/app-shell.tsx
```

### 3. Content Density (densidade de informação clínica)
- [ ] StatsBar: valores não quebram em múltiplas linhas abaixo de 480px
- [ ] BedGrid: 1 col (XS-SM) → 2 cols (MD) → 3-4 cols (LG-XL)
- [ ] BedCard: ScorePair + PathwayBadges + VitalsInline visíveis sem scroll interno
- [ ] Patient Detail: layout 2-colunas colapsa para 1-coluna em MD
- [ ] Pathway View: StateFlow com scroll horizontal funcional em mobile
- [ ] AlertTable: colunas não-essenciais ocultas abaixo de MD (`hidden md:table-cell`)

**Comandos de verificação:**
```bash
# Colunas responsivas na tabela de alertas
rg "hidden|table-cell" components/alerts/ --include='*.tsx' | grep -E "sm:|md:|lg:"

# Grid de leitos responsivo
rg "grid-cols" components/dashboard/bed-grid.tsx
```

### 4. Typography & Legibility (legibilidade)
- [ ] Font-size mínimo de 12px em qualquer breakpoint (recomendado: 14px para dados clínicos)
- [ ] Contraste mantido em todos breakpoints (cores não mudam com viewport)
- [ ] Line-height não colapsa em textos clínicos (mín 1.4)
- [ ] Valores numéricos (MEWS, SpO₂) mantêm `tabular-nums` para alinhamento

**Comandos de verificação:**
```bash
# Font-size abaixo de 12px
rg "text-\[?1[01]px\]?|text-xs" components/ app/ --include='*.tsx'

# Ausência de tabular-nums em scores
rg "score\|MEWS\|NEWS2\|value" components/ --include='*.tsx' -l | xargs rg "tabular-nums" 2>/dev/null
```

### 5. Interaction States (estados interativos)
- [ ] Loading skeletons mantêm dimensões do componente em todos breakpoints
- [ ] Empty states centralizados e legíveis em viewports estreitos
- [ ] Error messages com botão "Tentar novamente" acessível (touch target)
- [ ] Modals/dialogs não excedem 90vw em mobile
- [ ] Dropdowns e selects não são cortados na borda da tela

**Comandos de verificação:**
```bash
# Modal sem max-w responsivo
rg "max-w-\[|max-w-screen" components/ --include='*.tsx'

# Skeleton sem dimensão responsiva
rg "animate-pulse.*w-\[" components/ --include='*.tsx' | grep -v "w-full"
```

## Metodologia de Teste

1. **Automated:** Playwright viewport tests nos 5 breakpoints
2. **Manual:** Chrome DevTools Device Toolbar nos 5 breakpoints
3. **Split-screen:** Redimensionar janela para 50% da largura (simula round com 2 monitores)

## Critérios de Severidade

| Nível | Definição | Exemplo |
|-------|-----------|---------|
| **BLOCKER** | Jornada do intensivista impossível no breakpoint | Sidebar inacessível, navegação quebrada |
| **CRITICAL** | Dado clínico ilegível ou oculto | Score MEWS truncado, botão de ação fora da tela |
| **MAJOR** | Degradação significativa de UX | Scroll horizontal, texto sobreposto |
| **MINOR** | Desconforto visual sem perda funcional | Espaçamento inconsistente, fonte ligeiramente pequena |

## Output Esperado

Relatório em `/Users/familia/intensicare/frontend-v3/audit-results/responsive-audit.md` com:

1. **Matriz de conformidade:** 5 breakpoints × 5 dimensões × severidade
2. **Screenshots comparativos:** mesmo componente em 320px vs 1440px
3. **Violações classificadas:** BLOCKER → CRITICAL → MAJOR → MINOR
4. **Heatmap de componentes problemáticos:** quais componentes falham em quais breakpoints
5. **Recomendações acionáveis:** por componente, com diff de código sugerido

## Referências

- WCAG 2.1 AA: [1.4.10 Reflow](https://www.w3.org/WAI/WCAG21/Understanding/reflow.html), [2.5.8 Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- Tailwind CSS 4: [Responsive Design](https://tailwindcss.com/docs/responsive-design)
- DESIGN_BRIEF.yaml § responsive breakpoints
- FRONTEND_REBUILD_PLAN.md § 1: jornada do intensivista em mobile (plantão noturno)
