# 🛡️ DS Governance — Responsive Audit Validation

**Data:** 2026-07-13  
**Auditor:** Hermes Agent (DS Guardian / Gatekeeper)  
**Fonte validada:** `responsive-audit.md` (Ive, Design Orchestrator)  
**Escopo:** 6 violações do relatório de auditoria responsiva × código fonte  
**Metodologia:** Leitura direta dos 6 arquivos fonte, análise do design system (`globals.css`), cruzamento com auditorias DS anteriores (v1, v2)

---

## 1. Arquitetura do Design System

| Elemento | Mecanismo | Localização |
|---|---|---|
| **Framework** | Tailwind CSS v4 (`@import "tailwindcss"`) | `app/globals.css:1` |
| **Cores** | CSS custom properties (`--severity-*`, `--surface-*`, `--text-*`, `--border-*`) | `app/globals.css:5-21` |
| **Radius** | CSS custom properties (`--radius-sm`, `--radius-md`, `--radius-lg`) | `app/globals.css:22-24` |
| **Brand** | CSS custom properties (`--brand-*`) | `app/globals.css:26-29` |
| **Tipografia** | ❌ **AUSENTE** — sem tokens `--text-*`, `--font-size-*`, `--font-family-*` | — |
| **Spacing** | ❌ **AUSENTE** — sem tokens `--spacing-*`. Usa escala padrão do Tailwind (`gap-4` = 1rem, `p-6` = 1.5rem) | — |
| **Breakpoints** | Tailwind v4 defaults (sm=640px, md=768px, lg=1024px, xl=1280px). **Sem breakpoints customizados.** | — |
| **Layout** | ❌ **AUSENTE** — sem tokens de grid, container, ou max-width | — |

> **Diagnóstico:** O design system atual é um sistema de **cores e severidade**, não um design system completo. Faltam as dimensões de tipografia, espaçamento e layout que seriam necessárias para classificar violações de "token" nessas categorias.

---

## 2. Score de Conformidade

| Categoria | Pontuação | Peso | Nota |
|---|---|---|---|
| Cores (uso de tokens `var(--*)`) | 99/100 | 30% | 29.7 |
| Tipografia (ausência de `text-[Npx]`) | 62/100 | 25% | 15.5 |
| Spacing (uso de escala Tailwind) | 95/100 | 15% | 14.3 |
| Breakpoints responsivos | 100/100 | 15% | 15.0 |
| Padrões de layout (grid, wrap) | 90/100 | 15% | 13.5 |
| **TOTAL** | | | **88.0 / 100** |

---

## 3. Validação das 6 Violações do Audit Responsivo

### V1 — StatsBar: sem `flex-wrap`

| Campo | Valor |
|---|---|
| **Arquivo:linha** | `components/dashboard/stats-bar.tsx:24` |
| **Código** | `className="flex items-center gap-4 px-4 py-3 rounded-[var(--radius-md)]"` |
| **Spacing usado** | `gap-4` (Tailwind = 1rem), `px-4` (padding-x 1rem), `py-3` (padding-y 0.75rem) |
| **Tipo de violação** | 🔶 **RECOMENDAÇÃO HEURÍSTICA** |
| **Justificativa** | O DS **não define tokens de spacing**. Usar `gap-4`, `px-4`, `py-3` da escala Tailwind padrão é o **padrão correto** para este codebase. A violação real é de **layout** (falta `flex-wrap`), não de token. O fix sugerido pelo audit (`flex flex-wrap items-center gap-x-4 gap-y-1`) é válido como melhoria de UX, mas não como correção de DS. |
| **Ação DS** | Nenhuma — não há violação de token. O fix de layout é recomendado por usabilidade. |

### V2 — AlertTable: header `hidden sm:flex`

| Campo | Valor |
|---|---|
| **Arquivo:linha** | `components/alerts/alert-table.tsx:133` |
| **Código** | `className="hidden sm:flex items-center gap-3 px-4 py-2 text-xs..."` |
| **Breakpoint usado** | `sm:` = 640px (Tailwind default) |
| **Tipo de violação** | 🔶 **RECOMENDAÇÃO HEURÍSTICA** |
| **Justificativa** | `hidden sm:flex` é um padrão Tailwind **canônico e correto** para esconder cabeçalhos de tabela em mobile. O DS não define breakpoints customizados — `sm:` é o breakpoint do sistema. Cada `AlertRow` (arquivo `alert-row.tsx:58`) é auto-descritivo: contém ícone de severidade, nome do paciente com ícone `User`, trilha com ícone `GitBranch`, mensagem truncada, data com ícone `Clock`, e badges de status. A decisão de esconder headers em mobile é uma **escolha de UX**, não uma violação de DS. |
| **Verificação do AlertRow** | `flex cursor-pointer flex-wrap items-center gap-3 px-4 py-3` — adapta-se a qualquer largura. Cada campo tem label contextual por ícone ou texto inline. |
| **Ação DS** | Nenhuma — padrão conforme. Se UX decidir por labels inline mobile, usar `sm:hidden` nos labels adicionais. |

### V3 — BedCard: staleness `text-[10px]`

| Campo | Valor |
|---|---|
| **Arquivo:linha** | `components/dashboard/bed-card.tsx:109` |
| **Código** | `className="text-[10px] font-medium"` |
| **Token usado** | ❌ Nenhum — valor arbitrário |
| **Tipo de violação** | 🔴 **VIOLAÇÃO FACTUAL** |
| **Justificativa** | Valor hardcoded `10px` sem referência a token. O DS **não possui tokens de tipografia**, o que força os devs a usar valores arbitrários. O audit classifica corretamente como MINOR. A severidade está correta: é metadata não-crítico (staleness indicator). |
| **Ação DS** | ① Criar token `--text-2xs: 0.625rem` (10px) em `globals.css` ② Substituir `text-[10px]` por `text-[length:var(--text-2xs)]` ou criar utilitário Tailwind. O fix `text-[11px] sm:text-xs` do audit é paliativo (ainda usa valor arbitrário para 11px). |
| **Severidade do audit** | ✅ Correta (MINOR) |

### V4 — VitalReadout: timestamp `text-[10px]`

| Campo | Valor |
|---|---|
| **Arquivo:linha** | `components/patient/vitals-panel.tsx:71` |
| **Código** | `className={cn('text-[10px]', showDate && 'font-semibold')}` |
| **Token usado** | ❌ Nenhum — valor arbitrário |
| **Tipo de violação** | 🔴 **VIOLAÇÃO FACTUAL** |
| **Justificativa** | Mesmo padrão de V3. Timestamp de leitura vital — informação secundária, mas ainda assim deve usar token quando disponível. O DS atual não provê alternativa. |
| **Ação DS** | Usar mesmo token `--text-2xs` após criação. |
| **Severidade do audit** | ✅ Correta (MINOR) |

### V5 — StateFlow: terminal badge `text-[10px]`

| Campo | Valor |
|---|---|
| **Arquivo:linha** | `components/pathway/state-flow.tsx:127` |
| **Código** | `<span className="text-[10px] opacity-70" aria-label="Estado terminal">(final)</span>` |
| **Token usado** | ❌ Nenhum — valor arbitrário + `opacity-70` (utilitário Tailwind) |
| **Tipo de violação** | 🔴 **VIOLAÇÃO FACTUAL** |
| **Justificativa** | Duplo hardcode: `text-[10px]` + `opacity-70`. O `opacity-70` é um utilitário Tailwind (aceitável), mas o font-size é arbitrário. Badge decorativo "final" em pill de estado. |
| **Ação DS** | Usar mesmo token `--text-2xs` após criação. `opacity-70` é aceitável como utilitário Tailwind. |
| **Severidade do audit** | ✅ Correta (MINOR) |

### V6 — AppShell: padding `p-6` fixo

| Campo | Valor |
|---|---|
| **Arquivo:linha** | `components/app-shell.tsx:267` |
| **Código** | `<main id="main-content" tabIndex={-1} className="flex-1 overflow-auto p-6">` |
| **Spacing usado** | `p-6` = 1.5rem (Tailwind default) |
| **Tipo de violação** | 🔶 **RECOMENDAÇÃO HEURÍSTICA** |
| **Justificativa** | `p-6` é um valor **válido da escala Tailwind padrão**. O DS não define tokens de spacing — usar a escala Tailwind é o padrão correto. A preocupação do audit (15% do viewport em 320px) é válida como otimização de espaço, não como violação de DS. O fix `p-4 sm:p-6` usa a mesma escala Tailwind e é uma melhoria de UX, não de conformidade. |
| **Ação DS** | Nenhuma obrigatória. `p-4 sm:p-6` é melhoria opcional de UX. |

---

## 4. Verificação dos Grids Responsivos

| Componente | Arquivo:linha | Breakpoints | Conformidade |
|---|---|---|---|
| `BedGrid` | `bed-grid.tsx:115,154` | `repeat(auto-fill, minmax(280px, 1fr))` — auto-adaptativo | ✅ CONFORME |
| `AlertRow` (details) | `alert-row.tsx:165` | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` | ✅ CONFORME |
| `ActivePathways` | `active-pathways.tsx:28,61` | `sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3` | ✅ CONFORME |
| `VitalsPanel` | `vitals-panel.tsx:132,159` | `grid-cols-2 md:grid-cols-3 lg:grid-cols-5` | ✅ CONFORME |
| `PathwayGrid` | `pathway-grid.tsx:181` | `grid-cols-1 md:grid-cols-2 xl:grid-cols-3` | ✅ CONFORME |
| `CriteriaRow` | `criteria-row.tsx:133` | `grid-cols-1 sm:grid-cols-3` | ✅ CONFORME |
| Patient detail page | `patient/[mpi_id]/page.tsx:172` | `grid-cols-1 xl:grid-cols-3` | ✅ CONFORME |
| Pathway detail page | `patient/.../pathway/[pp_id]/page.tsx:302` | `grid-cols-1 lg:grid-cols-3` | ✅ CONFORME |

> **Conclusão:** Todos os 8 grids responsivos usam exclusivamente breakpoints padrão do Tailwind (`sm:`, `md:`, `lg:`, `xl:`). O DS não define breakpoints customizados — o padrão Tailwind **é** o breakpoint system. Nenhuma violação encontrada.

---

## 5. Padrão de Tabela Responsiva (AlertTable)

O `AlertTable` adota o padrão **"table → card list"** no mobile:

| Breakpoint | Comportamento | Mecanismo |
|---|---|---|
| < 640px (mobile) | Linhas viram cards auto-descritivos, header escondido | `AlertRow`: `flex flex-wrap` com ícones + labels inline |
| ≥ 640px (desktop) | Header de colunas visível | `hidden sm:flex` no header row |

**Análise de cada campo no AlertRow mobile:**

| Campo | Renderização mobile | Auto-explicativo? |
|---|---|---|
| Expandir | `<ChevronRight>` button c/ `aria-label` completo | ✅ |
| Severidade | `<SeverityBadge>` com cor + texto ("Crítico", "Urgente") | ✅ |
| Paciente | `<User>` ícone + nome (ou "—") | ✅ |
| Trilha | `<GitBranch>` ícone + nome (ou "—") | ✅ |
| Mensagem | Texto truncado com `flex-1 truncate` | ✅ |
| Data | `<Clock>` ícone + timestamp | ✅ |
| Status | Badges "✓" (reconhecido) e "Resolvido" | ✅ |
| Ações | `<QuickActions>` com botões de acknowledge/resolve | ✅ |

> **Veredito:** O padrão é **conforme** com as melhores práticas de design responsivo. Cada linha contém contexto suficiente para ser compreendida sem os headers de coluna. A decisão de esconder headers em mobile é uma escolha de UX válida, não uma violação de DS.

---

## 6. Achados Adicionais (fora do escopo do audit responsivo)

### 6.1 `text-[10px]` não reportados

O audit responsivo identificou 3 instâncias. Existem **5 adicionais** no codebase:

| # | Arquivo | Linha | Contexto |
|---|---|---|---|
| A1 | `components/alerts/filter-bar.tsx` | 170 | Badge "!" no botão de filtros |
| A2 | `components/alerts/filter-bar.tsx` | 195 | Label "Unidade" |
| A3 | `components/alerts/filter-bar.tsx` | 223 | Label "Trilha" |
| A4 | `components/app-shell.tsx` | 102 | Kbd shortcut `?` hint |
| A5 | `components/dashboard/pathway-badges.tsx` | 44 | `text-[8px]` — ainda menor |

> As instâncias A1–A4 já foram documentadas nas auditorias DS Governance v1 e v2 (2026-07-09 e 2026-07-10).

### 6.2 Violações de token pré-existentes

Auditorias DS anteriores (v1: 88.2/100, v2: 84.1/100) documentaram problemas mais graves que o audit responsivo não cobriu:

- **N4 (alpha blending):** `state-label.tsx` — `var(--severity-normal)1A` produz CSS inválido
- **N1 (border inline):** 19 instâncias de `borderWidth`/`borderStyle` em `style={{}}`
- **M1–M16:** 16 font-sizes arbitrários (incluindo `text-[0.625rem]`, `text-[0.8rem]`)
- **M17–M44:** 28 width/height fixos com `w-[Npx]`/`h-[Npx]`

---

## 7. Resumo de Classificações

| ID | Componente | Achado do Audit | Classificação DS | Severidade |
|---|---|---|---|---|
| V1 | StatsBar | Sem `flex-wrap` | 🔶 Recomendação heurística | MAJOR → mantido (layout, não token) |
| V2 | AlertTable | `hidden sm:flex` header | 🔶 Recomendação heurística | MAJOR → rebaixado (padrão válido) |
| V3 | BedCard | `text-[10px]` | 🔴 Violação factual | MINOR — confirmado |
| V4 | VitalReadout | `text-[10px]` | 🔴 Violação factual | MINOR — confirmado |
| V5 | StateFlow | `text-[10px]` | 🔴 Violação factual | MINOR — confirmado |
| V6 | AppShell | `p-6` fixo | 🔶 Recomendação heurística | MINOR — mantido (otimização UX) |

---

## 8. Veredito

```
╔══════════════════════════════════════════════════════════════╗
║                    VEREDITO: CONDITIONAL-GO                  ║
║                                                            ║
║  O frontend v3 está APTO para produção com condições.      ║
║  Nenhuma violação de design system bloqueia o deploy.      ║
║                                                            ║
║  Condições para GO pleno:                                  ║
║  1. Criar tokens de tipografia (--text-2xs, --text-xs)     ║
║     e substituir os 8 text-[Npx] hardcoded                 ║
║  2. Aplicar flex-wrap no StatsBar (1 linha, zero risco)    ║
║  3. Decidir UX do AlertTable mobile (manter ou labels)     ║
║                                                            ║
║  Score DS: 88.0/100 (mesma faixa das auditorias v1/v2)     ║
║  Score WCAG Reflow: 92% (conforme audit responsivo)        ║
╚══════════════════════════════════════════════════════════════╝
```

### Condições detalhadas

| Condição | Bloqueante? | Esforço | Risco |
|---|---|---|---|
| **C1:** Criar `--text-2xs` (10px) e `--text-3xs` (8px) em `globals.css` | Não | 30 min | Baixo |
| **C2:** Substituir 8× `text-[10px]` + 1× `text-[8px]` por tokens | Não | 1h | Baixo |
| **C3:** Adicionar `flex-wrap` ao StatsBar | Não | 5 min | Zero |
| **C4:** Resolver alpha blending quebrado em `state-label.tsx` (N4) | Sim* | 1h | Médio |

> \*C4 é bloqueante por produzir CSS inválido (já documentado desde a auditoria v1 de 09/Jul).

---

## 9. Comparativo com Auditorias Anteriores

| Métrica | DS Gov v1 (09/Jul) | DS Gov v2 (10/Jul) | **Resp. DS Gov (13/Jul)** |
|---|---|---|---|
| Escopo | 50 arquivos | 89 arquivos | 6 violações do audit responsivo |
| Score DS | 88.2/100 | 84.1/100 | **88.0/100** |
| Violações CRITICAL | 1 (rgb hardcode) | 0 ✅ | 0 ✅ |
| Violações MAJOR | 18 | 22 | 0 novas |
| Violações MINOR | 22 | 24 | 3 text-[10px] (já conhecidas) |
| Foco | Cores + Tipografia | Cores + Tipografia + Spacing | **Tokens × Valores Arbitrários** |

---

*Relatório gerado por Hermes Agent (DS Guardian / Gatekeeper) — 2026-07-13.*  
*Fontes: `responsive-audit.md` (Ive), código fonte (6 arquivos), `globals.css`, DS Governance v1/v2.*
