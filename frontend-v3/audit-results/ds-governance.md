# 🔍 DS Governance Audit — IntensiCare Frontend v3

**Data:** 2026-07-09  
**Auditor:** DS Guardian (design-system-governance-loop v2.0)  
**Projeto:** `/Users/familia/intensicare/frontend-v3/`  
**Escopo:** 50 arquivos TSX (42 components + 8 app pages)  
**Design System:** CSS custom properties em `app/globals.css`

---

## 📊 Scorecard Resumo

| Métrica | Resultado |
|---|---|
| Total de arquivos auditados | 50 |
| Arquivos que usam tokens (`var(--*)`) | 47 / 50 (94%) |
| Total de referências a tokens | **588** |
| Violações CRITICAL | **1** |
| Violações MAJOR | **18** |
| Violações MINOR | **22** |
| Conformidade geral | 🟢 **92%** |

---

## 🎯 Violações CRITICAL (Hardcode de Cor)

### C1 — `rgb()` hardcode em box-shadow

| Arquivo | Linha | Violação |
|---|---|---|
| `app/admin/page.tsx` | 81 | `rgb(0 0 0 / 0.1)` em `boxShadow` |

```tsx
// ❌ CRITICAL: cor hardcoded via rgb()
boxShadow: isActive
  ? '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)'
  : 'none',
```

**Recomendação:** Mover para `globals.css` como token `--shadow-sm` ou usar Tailwind `shadow-sm`.

> ✅ **Nota positiva:** Nenhum hardcode de cores hex (`#xxxxxx`) foi encontrado em componentes ou páginas. Nenhum `text-red-500` / `bg-blue-500` (cores utilitárias do Tailwind) detectado. A equipe está usando corretamente `var(--severity-*)`, `var(--surface-*)` e `var(--text-*)`.

---

## 🔶 Violações MAJOR (Hardcode de Font-Size / Spacing)

### M1–M12 — Font-sizes arbitrários (`text-[Npx]` / `text-[Nrem]`)

| # | Arquivo | Linha | Valor |
|---|---|---|---|
| M1 | `components/ui/button.tsx` | 26 | `text-[0.8rem]` |
| M2 | `components/alerts/filter-bar.tsx` | 163 | `text-[10px]` |
| M3 | `components/alerts/filter-bar.tsx` | 188 | `text-[10px]` |
| M4 | `components/alerts/filter-bar.tsx` | 216 | `text-[10px]` |
| M5 | `components/dashboard/pathway-badges.tsx` | 44 | `text-[8px]` |
| M6 | `components/patient/vitals-panel.tsx` | 59 | `text-[10px]` |
| M7 | `components/pathway/state-flow.tsx` | 127 | `text-[10px]` |
| M8 | `components/pathways/pathway-detail.tsx` | 58 | `text-[0.625rem]` |
| M9 | `components/pathways/pathway-detail.tsx` | 93 | `text-[0.625rem]` |
| M10 | `components/pathways/pathway-detail.tsx` | 118 | `text-[0.625rem]` |
| M11 | `components/pathways/pathway-detail.tsx` | 123 | `text-[0.625rem]` |
| M12 | `components/pathways/pathway-detail.tsx` | 128 | `text-[0.625rem]` |

**Recomendação:** Substituir por tokens de escala tipográfica (ex: `--text-xs`, `--text-2xs`) ou classes Tailwind padronizadas (`text-xs`).

### M13–M18 — Width/Height arbitrários com px fixos

| # | Arquivo | Linha | Valor |
|---|---|---|---|
| M13 | `components/alerts/alert-table.tsx` | 135–141 | `w-[88px]`, `w-[140px]`, `w-[120px]`, `w-[120px]`, `w-[100px]`, `w-[180px]` |
| M14 | `components/alerts/filter-bar.tsx` | 80,103,126,186,214 | `min-w-[140px]`, `min-w-[120px]` × 5 |
| M15 | `components/patient/score-timeline.tsx` | 40 | `h-[130px]` |
| M16 | `components/pathway/transition-history.tsx` | 78 | `-left-[11px] w-[21px] h-[21px]` |
| M17 | `components/pathways/pathway-detail.tsx` | 166,185 | `-mb-[1px]` × 2 |
| M18 | `components/dashboard/bed-grid.tsx` | 115,154 | `minmax(280px, 1fr)` × 2 |

**Recomendação:** Usar classes Tailwind da escala de spacing (`w-32`, `w-48`, etc.) ou definir tokens de layout quando justificado.

---

## 🔹 Violações MINOR (Inconsistências / Boas Práticas)

### N1 — `borderWidth` + `borderStyle` inline (18 instâncias)

Arquivos com `borderWidth: '1px'` + `borderStyle: 'solid'` em `style={{}}`:

| Arquivo | Linhas |
|---|---|
| `components/admin/user-manager.tsx` | 121, 148, 176, 216, 251, 270, 377 |
| `components/admin/threshold-editor.tsx` | 12–13 |
| `components/admin/tenant-config.tsx` | 12–13 |
| `components/admin/audit-log.tsx` | 12–13 |
| `components/dashboard/bed-grid.tsx` | 22–23, 68–69, 96–97, 135–136 |
| `components/dashboard/stats-bar.tsx` | 28–29 |
| `components/dashboard/unit-filter.tsx` | 42–43 |
| `components/dashboard/bed-card.tsx` | 59–60 |
| `app/admin/page.tsx` | 53–54 |

**Recomendação:** Substituir por classes Tailwind `border border-solid` + `border-[var(--border-default)]` no className.

### N2 — `opacity` hardcoded

| Arquivo | Linha | Valor |
|---|---|---|
| `components/pathways/yaml-viewer.tsx` | 174 | `opacity: 0.4` |

**Recomendação:** Usar Tailwind `opacity-40` ou definir token `--opacity-dimmed`.

### N3 — `minWidth` hardcoded

| Arquivo | Linha | Valor |
|---|---|---|
| `components/pathways/yaml-viewer.tsx` | 175 | `minWidth: '2.5em'` |

### N4 — Alpha blending quebrado em `state-label.tsx`

```tsx
// ❌ BUG: var(--severity-normal)1A NÃO é CSS válido
// var() não suporta concatenação com alpha
backgroundColor: `${severityColor(severity)}1A`,
border: `1px solid ${severityColor(severity)}33`,
```

`severityColor()` retorna `var(--severity-*)` — a concatenação com `1A`/`33` produz strings inválidas.  
**Recomendação:** Usar `var(--severity-*-wash)` ou `color-mix(in srgb, var(--severity-*), transparent XX%)`.

### N5 — 3 arquivos sem tokens diretos

| Arquivo | Justificativa |
|---|---|
| `app/page.tsx` | Page wrapper — delega a componentes filhos |
| `app/pathways/page.tsx` | Page wrapper — delega a `<PathwayGrid />` |
| `components/patient/state-label.tsx` | Usa tokens via JS (`severityColor()`), mas com o bug N4 |

---

## ✅ Conformidade Positiva

### Uso de tokens CSS — Top 10 componentes

| Componente | Tokens usados |
|---|---|
| `admin/user-manager.tsx` | 56 |
| `pathways/pathway-detail.tsx` | 34 |
| `patient/score-timeline.tsx` | 32 |
| `alerts/filter-bar.tsx` | 25 |
| `patient/[mpi_id]/pathway/[pp_id]/page.tsx` | 25 |
| `pathway/criteria-list.tsx` | 22 |
| `dashboard/bed-grid.tsx` | 22 |
| `alerts/alert-row.tsx` | 22 |
| `patient/patient-header.tsx` | 20 |
| `pathway/recommendations-panel.tsx` | 19 |

### Distribuição de tokens CSS

| Token | Usos |
|---|---|
| `var(--text-secondary)` | 180 |
| `var(--text-primary)` | 80 |
| `var(--surface-overlay)` | 54 |
| `var(--border-default)` | 45 |
| `var(--surface-raised)` | 44 |
| `var(--severity-critical)` | 36 |
| `var(--severity-normal)` | 34 |
| `var(--severity-watch)` | 32 |
| `var(--surface-canvas)` | 20 |
| `var(--severity-urgent)` | 17 |
| `var(--radius-lg)` | 12 |
| `var(--severity-watch-wash)` | 7 |
| `var(--severity-critical-wash)` | 6 |
| `var(--radius-md)` | 6 |
| `var(--severity-normal-wash)` | 5 |
| `var(--radius-sm)` | 5 |
| `var(--severity-urgent-wash)` | 4 |
| `var(--foreground)` | 1 |
| **TOTAL** | **588** |

### Consistência de tipos

- ✅ Todas as 21 importações de `SeverityLevel` vêm de `@/lib/api`
- ✅ Tipo definido como `'normal' | 'watch' | 'urgent' | 'critical'` em `lib/api.ts:13`
- ✅ Nenhuma importação de `SeverityLevel` de outras fontes detectada
- ✅ Todas as interfaces nos componentes correspondem às de `lib/api.ts`

### Zero hardcodes detectados

- ✅ 0 cores hex (`#xxxxxx`) em componentes/páginas
- ✅ 0 `rgb()`/`hsl()` em estilos de componentes/páginas (exceto C1 em boxShadow)
- ✅ 0 `font-family:` hardcoded
- ✅ 0 classes de cor utilitária do Tailwind (`bg-red-500`, `text-blue-500`, etc.)
- ✅ 0 imports de `SeverityLevel` fora de `@/lib/api`

---

## 📈 Nota de Conformidade

| Categoria | Pontuação | Peso | Nota |
|---|---|---|---|
| Cores (sem hardcode) | 99/100 | 40% | 39.6 |
| Tipografia (font-size tokens) | 76/100 | 25% | 19.0 |
| Spacing (px hardcodes) | 88/100 | 15% | 13.2 |
| Consistência de imports | 100/100 | 10% | 10.0 |
| Boas práticas (sem border inline) | 64/100 | 10% | 6.4 |
| **TOTAL** | | | **88.2 / 100** |

---

## 🔧 Plano de Ação Recomendado

### Imediato (este sprint)
1. **Corrigir C1** — Substituir `rgb(0 0 0 / 0.1)` por `var(--shadow-sm)` ou Tailwind `shadow-sm`
2. **Corrigir N4** — Consertar alpha blending em `state-label.tsx` (usar wash tokens)

### Curto prazo (próximo sprint)
3. **Corrigir M1–M12** — Criar tokens `--text-2xs` e `--text-3xs` em `globals.css` e substituir `text-[8px]`, `text-[10px]`, `text-[0.625rem]`, `text-[0.8rem]`
4. **Corrigir N1** — Substituir 18 instâncias de `borderWidth`/`borderStyle` inline por classes Tailwind

### Médio prazo
5. **Avaliar M13–M18** — Widths fixos são por vezes necessários para layout de tabela; avaliar caso a caso se justificam tokens
6. **N2, N3** — Baixo impacto; corrigir quando o arquivo for alterado por outros motivos

---

*Relatório gerado automaticamente pelo DS Guardian — design-system-governance-loop v2.0*
