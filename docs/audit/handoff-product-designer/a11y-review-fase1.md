# GATE FASE 1 — Accessibility Review WCAG 2.2 A/AA

**Data:** 2026-07-07
**Escopo:** 4 componentes base (M2) — CriteriaChecklist, ClinicalTimeline, BundleCard, StewardshipScoreBadge
**Método:** Revisão estática de código-fonte + verificação de tokens de design (`tokens-generated.css` + `globals.css`)
**Tema verificado:** Dark (default) — tokens `:root, [data-theme="dark"]`

---

## Executive Summary

Os componentes demonstram **boa base de acessibilidade estrutural** (roles ARIA, labels, keyboard navigation, focus indicators), mas apresentam **falhas significativas de contraste de cor** nos tokens de severidade do design system. As violações concentram-se nos critérios **1.4.3 (Contrast Minimum)** e **1.4.11 (Non-text Contrast)**, com impacto cross-component nos badges e indicadores de status.

| Componente | Score WCAG AA | Status |
|---|---|---|
| CriteriaChecklist | 93% (13/14 checks) | ⚠️ Approvado condicional |
| ClinicalTimeline | 100% (11/11 checks) | ✅ Aprovado |
| BundleCard | 88% (14/16 checks) | ⚠️ Approvado condicional |
| StewardshipScoreBadge | 63% (5/8 checks) | ❌ Reprovado |
| **Geral** | **88% (43/49 checks)** | ❌ Abaixo de 95% |

---

## Score WCAG AA: **88%** — ❌ REPROVADO (meta: ≥ 95%)

O score geral fica abaixo de 95% devido a **6 violações de contraste** concentradas em tokens do design system. Corrigindo os tokens, o score sobe para **96%+**.

---

## Tabela de Violações

| # | Critério WCAG | Severidade | Componente | Localização | Descrição |
|---|---|---|---|---|---|
| V1 | 1.4.3 Contrast Min (AA) | **BLOCKER** | StewardshipScoreBadge | L:149,165,178 — `tokens.onSurface` sobre `tokens.wash` | Texto de score/severidade/recomendação em todos os 3 níveis de severidade falha 4.5:1 (pior caso: AMARELO 2.97:1) |
| V2 | 1.4.3 Contrast Min (AA) | **BLOCKER** | BundleCard | L:218 — `tokens.onFill` sobre `tokens.fill` (status N/A) | Badge "N/A": `#9CA3AF` sobre `#374151` = 3.99:1 (< 4.5:1) |
| V3 | 1.4.11 Non-text Contrast (AA) | **MAJOR** | StewardshipScoreBadge | L:124 — `tokens.signal` (border) sobre `tokens.wash` (bg) | Borda do badge vs fundo: VERMELHO 1.72:1, AMARELO 2.12:1, NEUTRO 1.9:1 (mínimo 3:1) |
| V4 | 1.4.3 Contrast Min (AA) | **MAJOR** | CriteriaChecklist | L:244-248 — `tokens.notMetOnSurface` valor numérico | Valor "não atendido": `#6B7280` sobre canvas `#0E1014` = 4.09:1 (< 4.5:1 para texto 13px semibold) |
| V5 | 1.4.11 Non-text Contrast (AA) | **MINOR** | BundleCard | L:252-255 — progress bar fill (`tokens.signal`) sobre track | Barra "pending": `#6B7280` sobre `#1F232C` = 3.27:1 (passa 3:1 por margem estreita) |
| V6 | 2.5.8 Target Size (AA) | **MINOR** | BundleCard | L:304 — checkbox `w-4 h-4` (16×16px) | Checkbox visual é 16×16px, abaixo do mínimo AA de 24×24px. Label wrapping mitiga mas target visual é pequeno |

---

## Análise Detalhada por Componente

---

### 1. CriteriaChecklist (`CriteriaChecklist.tsx`)

**Score: 93% (13/14 checks)** — ⚠️ Aprovado condicional

#### ✅ Passes

| Critério | Evidência |
|---|---|
| 1.1.1 Non-text Content | Todos ícones com `aria-hidden="true"`: AlertTriangle (L144), HelpCircle (L159), CheckCircle/XCircle (L193, L264) |
| 1.3.1 Info and Relationships | `<ul role="list">` (L167), `<li>` por critério (L180), `<label htmlFor>` associado a `<input>` |
| 2.1.1 Keyboard | `<input type="checkbox">` nativo — totalmente operável por teclado |
| 2.4.7 Focus Visible | `focus-visible:ring-2 focus-visible:ring-offset-1` nos checkboxes (L213-214) |
| 3.3.1 Error Identification | Estado de erro com `role="alert"` + `aria-live="assertive"` (L133-135) |
| 3.3.2 Labels or Instructions | `<label htmlFor={criterionId}>` + `aria-label` + `aria-describedby` com `sr-only` (L182, L225-226, L285-289) |
| 4.1.2 Name, Role, Value | Roles: `list`, `listitem`, `alert`, `status`. Inputs nativos expõem name/role/value |
| 4.1.3 Status Messages | `aria-live="assertive"` no erro (L135), `role="status"` no loading/empty |

#### ⚠️ Violações

| # | Critério | Severidade | Linha | Descrição |
|---|---|---|---|---|
| V4 | 1.4.3 | MAJOR | 244-248 | Valor "não atendido": `#6B7280` sobre `#0E1014` (canvas) = **4.09:1** (< 4.5:1 para texto 13px semibold) |
| — | 2.5.8 | MINOR | 213 | Checkbox `w-5 h-5` (20×20px). Label wrapping (L182-188 com `py-2.5`) provê target efetivo adequado, mas elemento visual é < 24px |

#### 🔧 Suggested Fix (V4)

```css
/* tokens-generated.css — Adjust not-met on-surface for dark theme */
--clinical-sepsis-criteria-not-met-on-surface-dark: #9CA3AF; /* era #6B7280 */
/* #9CA3AF on #0E1014 ≈ 6.3:1 ✅ */
```

---

### 2. ClinicalTimeline (`ClinicalTimeline.tsx`)

**Score: 100% (11/11 checks)** — ✅ Aprovado

#### ✅ Passes

| Critério | Evidência |
|---|---|
| 1.1.1 Non-text Content | Todos ícones/nodos decorativos com `aria-hidden="true"`: AlertTriangle (L195), History (L210), timeline nodes (L266, L273, L302), Clock (L331), status dot (L353) |
| 1.3.1 Info and Relationships | `role="list"` + `role="listitem"` (L221, L239), `<h4>` para labels (L311), `<p>` para descrições (L318) |
| 1.4.3 Contrast Minimum | Texto primário `#E9ECF1` sobre canvas `#0E1014` = ~18:1 ✅. Texto secundário `#A6ADBB` = ~8:1 ✅. Status badge usa `tokens.onFill` (#FFF) sobre fills sólidos ≥ 6:1 |
| 1.4.11 Non-text Contrast | Timeline nodes: bordas `tokens.signal` sobre canvas com alto contraste (ex: `#22C55E` sobre `#0E1014` ≈ 8:1) |
| 2.1.1 Keyboard | `tabIndex={0}` no container (L223) e em cada evento (L238). Navegação ArrowUp/ArrowDown customizada (L128-158) |
| 2.4.7 Focus Visible | `focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500` (L237) |
| 2.5.8 Target Size | Eventos com `pb-6` (24px) + padding do layout — amplamente acima de 24px |
| 3.3.1 Error Identification | `role="alert"` + mensagem descritiva (L184-196) |
| 4.1.2 Name, Role, Value | `aria-label` rico em cada listitem (L240-242): inclui label + status + timestamp + descrição |
| 4.1.3 Status Messages | `aria-live="assertive"` no erro, `role="status"` no loading/empty |

#### Observações (não-violacões)

- **Heading hierarchy**: Uso de `<h4>` (L311) como heading do evento. Depende do contexto da página (se `<h3>` existe no parent). Como componente folha, não há violação garantida — apenas requer atenção no consumo.
- **Loader2 spinner** no estado "in-progress" (L285-288): fica dentro de div com `aria-hidden="true"` (L266), herdando corretamente. A informação de status "in progress" está no `aria-label` do listitem (L240). ✅

---

### 3. BundleCard (`BundleCard.tsx`)

**Score: 88% (14/16 checks)** — ⚠️ Aprovado condicional

#### ✅ Passes

| Critério | Evidência |
|---|---|
| 1.1.1 Non-text Content | Ícones com `aria-hidden="true"`: AlertTriangle (L180), StatusIcon (L221), Ban/CheckCircle/XCircle (L278, L285-296), HelpCircle (L345) |
| 1.3.1 Info and Relationships | `<h3>` para nome do bundle (L205), `<ul role="list">` + `<li>` para critérios (L264) |
| 2.1.1 Keyboard | `<input type="checkbox">` nativos com `<label htmlFor>` (L270, L299) |
| 2.4.7 Focus Visible | `focus-visible:ring-2 focus-visible:ring-offset-1` (L304) |
| 3.3.1 Error Identification | `role="alert"` + mensagem descritiva (L169-181) |
| 3.3.2 Labels or Instructions | `aria-label={criterion.label}` nos checkboxes (L309) |
| 4.1.2 Name, Role, Value | `role="region"` + `aria-label` no card (L188-189), `role="progressbar"` com `aria-valuenow/min/max` + `aria-label` (L245-249) — **Excelente!** |
| 4.1.3 Status Messages | `aria-live="assertive"` no erro, `role="status"` no loading |

#### ⚠️ Violações

| # | Critério | Severidade | Linha | Descrição |
|---|---|---|---|---|
| V2 | 1.4.3 | **BLOCKER** | 218 | Status badge N/A: `#9CA3AF` texto sobre `#374151` fundo = **3.99:1** (< 4.5:1) |
| V5 | 1.4.11 | MINOR | 252-255 | Progress bar "pending": fill `#6B7280` sobre track `#1F232C` = **3.27:1** (passa 3:1, mas com margem estreita) |
| V6 | 2.5.8 | MINOR | 304 | Checkbox `w-4 h-4` (16×16px) — abaixo de 24px. Label wrapping (`py-1`) expande área clicável, mas alvo visual é pequeno |

#### 🔧 Suggested Fix

**V2 — N/A badge contrast:**
```css
/* tokens-generated.css — Aumentar contraste do texto N/A */
--clinical-prophylaxis-na-on-fill: #D1D5DB; /* era #9CA3AF */
/* #D1D5DB sobre #374151 ≈ 5.3:1 ✅ */

/* OU alternativamente, escurecer o fundo */
--clinical-prophylaxis-na-fill: #1F2937; /* era #374151 */
/* #9CA3AF sobre #1F2937 ≈ 4.7:1 ✅ */
```

**V6 — Checkbox size:**
```tsx
// BundleCard.tsx L304 — aumentar checkbox de w-4 h-4 para w-5 h-5
<input
  id={criterionId}
  type="checkbox"
  // ...
  className="flex-shrink-0 w-5 h-5 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
  style={{
    accentColor: tokens.signal,
    borderColor: tokens.signal,
    minWidth: '20px',
    minHeight: '20px',
  }}
/>
```

---

### 4. StewardshipScoreBadge (`StewardshipScoreBadge.tsx`)

**Score: 63% (5/8 checks)** — ❌ **REPROVADO**

Este componente concentra as falhas mais graves, todas originadas nos tokens de severidade do design system.

#### ✅ Passes

| Critério | Evidência |
|---|---|
| 1.1.1 Non-text Content | Loader2 (L103), Icon (L142), TrendingUp (L184) — todos com `aria-hidden="true"` |
| 1.3.1 Info and Relationships | Badge display-only — estrutura semântica adequada ao propósito |
| 2.1.1 Keyboard | N/A — sem elementos interativos |
| 4.1.2 Name, Role, Value | `role="status"` + `aria-label` compreensivo (L119-121): score, total, severidade, recomendação |
| 4.1.3 Status Messages | `aria-live="polite"` (L120) — atualizações de score anunciadas a leitores de tela |

#### ⚠️ Violações

| # | Critério | Severidade | Linha | Descrição |
|---|---|---|---|---|
| V1 | 1.4.3 | **BLOCKER** | 149,165,178 | Texto `tokens.onSurface` sobre `tokens.wash`: **VERMELHO 3.42:1, AMARELO 2.97:1, NEUTRO 2.95:1** (mínimo 4.5:1) |
| V3 | 1.4.11 | **MAJOR** | 124 | Borda `tokens.signal` sobre fundo `tokens.wash`: **VERMELHO 1.72:1, AMARELO 2.12:1, NEUTRO 1.9:1** (mínimo 3:1) |

#### Detalhe dos contrastes (dark theme)

| Severidade | Texto (onSurface) | Fundo (wash) | Contraste texto | Meta 4.5:1? | Borda (signal) | Contraste borda | Meta 3:1? |
|---|---|---|---|---|---|---|---|
| VERMELHO | `#FCA5A5` | `#B91C1C` | **3.42:1** | ❌ | `#EF4444` | **1.72:1** | ❌ |
| AMARELO | `#FBBF24` | `#B45309` | **2.97:1** | ❌ | `#F59E0B` | **2.12:1** | ❌ |
| NEUTRO | `#4ADE80` | `#15803D` | **2.95:1** | ❌ | `#22C55E` | **1.90:1** | ❌ |

#### 🔧 Suggested Fix (V1 + V3)

O problema é estrutural: `onSurface` (texto) e `signal` (borda) são tons claros destinados a superfícies escuras (canvas `#0E1014`), mas estão sendo aplicados sobre `wash`/`fill` que são tons médio-escuros. Solução: criar tokens específicos para texto/borda **sobre fundos coloridos**.

```css
/* tokens-generated.css — Novos tokens para contraste sobre fills/washes */

/* VERMELHO */
--clinical-antimicrobial-stewardship-intervention-on-surface-dark: #FCA5A5; /* mantido para uso sobre canvas */
--clinical-antimicrobial-stewardship-intervention-on-fill-text: #FFFFFF;     /* NOVO: texto sobre fill/wash */
--clinical-antimicrobial-stewardship-intervention-signal-dark: #EF4444;      /* mantido */
--clinical-antimicrobial-stewardship-intervention-border-on-wash: #FCA5A5;   /* NOVO: borda com contraste ≥ 3:1 sobre wash */

/* AMARELO */
--clinical-antimicrobial-stewardship-review-on-fill-text: #FFFFFF;
--clinical-antimicrobial-stewardship-review-border-on-wash: #FDE68A;

/* NEUTRO */
--clinical-antimicrobial-stewardship-optimal-on-fill-text: #FFFFFF;
--clinical-antimicrobial-stewardship-optimal-border-on-wash: #BBF7D0;
```

**Alternativa mais simples (se preferir não criar tokens novos):** Alterar os valores de `onSurface` e `signal` para versões mais escuras com contraste garantido sobre `wash`/`fill`, e usar a versão clara apenas sobre canvas.

```css
/* Abordagem: tornar onSurface e signal com contraste garantido sobre fill/wash */
/* VERMELHO */
--clinical-antimicrobial-stewardship-intervention-on-surface-dark: #FFFFFF;  /* era #FCA5A5 */
--clinical-antimicrobial-stewardship-intervention-signal-dark: #FCA5A5;      /* era #EF4444 */

/* AMARELO */
--clinical-antimicrobial-stewardship-review-on-surface-dark: #FFFFFF;        /* era #FBBF24 */
--clinical-antimicrobial-stewardship-review-signal-dark: #FDE68A;            /* era #F59E0B */

/* NEUTRO */
--clinical-antimicrobial-stewardship-optimal-on-surface-dark: #FFFFFF;       /* era #4ADE80 */
--clinical-antimicrobial-stewardship-optimal-signal-dark: #BBF7D0;           /* era #22C55E */
```

**Verificação pós-fix (abordagem alternativa):**

| Severidade | Texto | Fundo | Contraste | Meta |
|---|---|---|---|---|
| VERMELHO | `#FFFFFF` | `#B91C1C` | **6.48:1** | ✅ |
| AMARELO | `#FFFFFF` | `#B45309` | **6.10:1** | ✅ |
| NEUTRO | `#FFFFFF` | `#15803D` | **5.08:1** | ✅ |

| Severidade | Borda | Fundo | Contraste | Meta |
|---|---|---|---|---|
| VERMELHO | `#FCA5A5` | `#B91C1C` | **3.42:1** | ✅ |
| AMARELO | `#FDE68A` | `#B45309` | **3.76:1** | ✅ |
| NEUTRO | `#BBF7D0` | `#15803D` | **3.08:1** | ✅ |

---

## Verificações Específicas Solicitadas

### Cor + ícone + texto (nunca só cor) — ✅ TODOS PASSAM

| Componente | Cor | Ícone | Texto |
|---|---|---|---|
| CriteriaChecklist | Verde/Vermelho/Cinza | CheckCircle / XCircle | "Atendido" / "Não atendido" |
| ClinicalTimeline | Verde/Amarelo/Cinza/Vermelho | Checkmark SVG / Loader2 / Circle / Pulse | "completed" / "in progress" / "pending" / "overdue" |
| BundleCard | Verde/Amarelo/Cinza | CheckCircle / Clock / Circle / Ban | "Completo" / "Parcial" / "Pendente" / "N/A" |
| StewardshipScoreBadge | Verde/Amarelo/Vermelho | ShieldCheck / AlertTriangle / AlertOctagon | "NEUTRO" / "AMARELO" / "VERMELHO" + recomendação |

### aria-label em todos elementos interativos — ✅

- CriteriaChecklist: `aria-label={item.label}` nos checkboxes (L226)
- ClinicalTimeline: `aria-label` rico em cada listitem (L240-242)
- BundleCard: `aria-label={criterion.label}` nos checkboxes (L309), `aria-label` no card (L190) e progressbar (L249)
- StewardshipScoreBadge: Sem elementos interativos; `aria-label` no badge (L121)

### aria-describedby em inputs com descrição — ✅

- CriteriaChecklist: `aria-describedby={descriptionId}` (L225) → aponta para `<div id={descriptionId} className="sr-only">` (L285-289)

### role apropriado — ✅

| Role | Componente | Linha |
|---|---|---|
| `list` | CriteriaChecklist, ClinicalTimeline, BundleCard | L170, L221, L264 |
| `listitem` | ClinicalTimeline | L239 |
| `alert` | Todos (erro) | L134, L185, L170 |
| `status` | Todos (loading/empty) | L118, L157, L74, L207, L103, L156, L100, L119 |
| `region` | BundleCard | L188 |
| `progressbar` | BundleCard | L245 |

### aria-live para conteúdo dinâmico — ✅

| aria-live | Componente | Uso |
|---|---|---|
| `assertive` | CriteriaChecklist, ClinicalTimeline, BundleCard | Estados de erro |
| `polite` | StewardshipScoreBadge | Atualização do score |
| Implícito (`role="status"`) | Todos | Loading e empty states |

### TabIndex e keyboard handlers — ✅

- ClinicalTimeline: `tabIndex={0}` + ArrowUp/ArrowDown (L128-158, L223, L238)
- Demais: controles nativos (`<input>`, `<label>`) com comportamento de teclado padrão

### Focus Visible — ✅ TODOS

- CriteriaChecklist: `focus-visible:ring-2 focus-visible:ring-offset-1` (L213-214)
- ClinicalTimeline: `focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500` (L237)
- BundleCard: `focus-visible:ring-2 focus-visible:ring-offset-1` (L304)
- StewardshipScoreBadge: N/A (sem elementos interativos)

---

## Plano de Correção (Ordem de Prioridade)

### Blocker (corrigir antes do deploy)

1. **V1 — StewardshipScoreBadge: texto sobre fundo colorido**
   - Arquivo: `tokens-generated.css`
   - Alterar tokens `on-surface-dark` de antimicrobial stewardship para `#FFFFFF` nas 3 severidades
   - Impacto: 3 tokens, zero alterações em código TSX

2. **V2 — BundleCard: badge N/A**
   - Arquivo: `tokens-generated.css`
   - Alterar `--clinical-prophylaxis-na-on-fill` para `#D1D5DB` ou `--clinical-prophylaxis-na-fill` para `#1F2937`
   - Impacto: 1 token

### Major (corrigir no próximo sprint)

3. **V3 — StewardshipScoreBadge: borda sobre fundo colorido**
   - Arquivo: `tokens-generated.css`
   - Alterar tokens `signal-dark` de antimicrobial stewardship para tons com contraste ≥ 3:1 sobre `wash`/`fill`
   - Impacto: 3 tokens

4. **V4 — CriteriaChecklist: valor "não atendido"**
   - Arquivo: `tokens-generated.css`
   - Alterar `--clinical-sepsis-criteria-not-met-on-surface-dark` para `#9CA3AF`
   - Impacto: 1 token

### Minor (backlog)

5. **V5 — BundleCard: progress bar pending**
   - Arquivo: `tokens-generated.css`
   - Aumentar `--clinical-prophylaxis-pending-signal-dark` para `#9CA3AF`
   - Impacto: 1 token

6. **V6 — BundleCard: checkbox 16px → 20px**
   - Arquivo: `BundleCard.tsx` L304
   - Alterar classes Tailwind de `w-4 h-4` para `w-5 h-5`
   - Impacto: 1 linha

---

## Notas sobre Light Theme

Esta auditoria verificou apenas o **dark theme** (default do sistema). Os tokens light theme existem em `tokens-generated.css` com valores diferentes. **Recomenda-se auditoria separada do light theme** pois os pares de contraste serão diferentes:

- Canvas light: `#F5F6F8`
- Texto secundário light: `#565D6D` sobre `#F5F6F8` → verificar se atinge 4.5:1
- Tokens de severidade light usam cores mais escuras (ex: `#166534` para sepsis confirmed) — provavelmente têm contraste adequado, mas requer verificação

---

## Conclusão

Os componentes têm **excelente qualidade de acessibilidade estrutural** —Roles ARIA, keyboard navigation, focus indicators, labels, e live regions estão implementados corretamente em todos os 4 componentes. O ClinicalTimeline é exemplar e atinge 100% de conformidade.

O gap está nos **tokens de cor do design system**: os valores `onSurface` e `signal` foram projetados para uso sobre canvas escuro (`#0E1014`), mas são reutilizados sobre fundos coloridos (`wash`/`fill`) sem contraste suficiente. A correção é trivial (alterar valores de tokens CSS, sem alterar lógica dos componentes) e elevará o score para **≥ 96%**.
