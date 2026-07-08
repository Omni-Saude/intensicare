# PLANS.md — Sprint 5-8 Core Critical UI

> **Orquestrador:** Ive (Product Design Orchestrator)
> **Data:** 2026-07-07
> **RECON:** Completo ✅

---

## RECON Summary

| Artefato | Status | Notas |
|----------|--------|-------|
| ADR 0020 (trilhas-engine architecture) | ✅ | Option 2: Declarative rule engine (stateless evaluation) |
| ADR 0021 (trilhas-engine data model) | ✅ | Immutable content-addressed definitions (YAML artifacts) |
| ADR 0022 (ventilacao architecture) | ✅ | Service architecture |
| ADR 0024 (piora-clinica strategy) | ✅ | Multi-domain deterioration detection |
| pathways-openapi.yaml | ✅ 510L | 6 endpoints, 7 schemas (Pathway, PathwayState, PathwayCriteria, PatientPathway, PathwayProgress, etc.) |
| ventilation-openapi.yaml | ✅ 292L | 2 endpoints, 3 schemas (VentilationParameters 12 fields, VentilationTrend, ParameterTrend) |
| stability-openapi.yaml | ✅ 168L | 2 endpoints, 4 schemas (27 StabilityCriteria, StabilityStatus, StabilityTrend) |
| deterioration-openapi.yaml | ✅ 157L | 2 endpoints, 2 schemas (DeteriorationScore categorical 0/1+/1-/3+/3-, DeteriorationCriteria) |
| Backend domain_respiratory.py | ✅ 33,262L | Covers ventilation |
| Backend domain_hemo.py | ✅ 32,933L | Covers hemodynamics/stability |
| Backend domain_aki.py | ✅ 12,755L | Covers renal domain |
| Frontend components reusáveis | ✅ | CriteriaChecklist, ClinicalTimeline, SeverityBadge, Layout, ErrorBoundary, DrawerBuilder |

---

## Milestones

### ⚠️ FASE 0 — Token Expansion (PRÉ-REQUISITO)
**Arquivo:** `app/tokens-generated.css`
**Tokens novos:**
- `--clinical-pathway-*` (5 variants: active, completed, screening, discontinued, overdue)
- `--clinical-ventilation-*` (3 variants: normal, attention, critical)
- `--clinical-stability-*` (3 variants: estavel, atencao, critico)
- `--clinical-deterioration-*` (5 variants: score-0, score-1-plus, score-1-minus, score-3-plus, score-3-minus)

### FASE 1 — Trilhas-Engine `/care-pathways` ⭐⭐⭐⭐⭐
**Complexidade:** Máxima. Split-screen layout com patient list + pathway board.
**Backend:** ❌ (mock — parreira constrói em paralelo)
**Arquivos (3):**
1. `lib/pathway-types.ts` — tipos do contrato pathways-openapi.yaml + mock data
2. `components/PathwayBoard.tsx` — board principal com estados, progresso, critérios
3. `app/care-pathways/page.tsx` — split-screen: patient list (esq) + pathway board (dir)
**Reusar:** CriteriaChecklist (criteria panel), ClinicalTimeline (state history), SeverityBadge, Layout, ErrorBoundary
**Estados:** patient list (com indicador de pathway), pathway board (estados, progresso, critérios), loading, empty, error

### FASE 2 — Ventilacao `/ventilation`
**Complexidade:** Alta. 12 parâmetros + gráfico de tendência.
**Backend:** domain_respiratory.py ✅ (existe)
**Arquivos (3):**
1. `lib/ventilation-types.ts` — tipos VentilationParameters + VentilationTrend + mock
2. `components/VentilationTrendChart.tsx` — Recharts multi-linha para tendência 24h
3. `app/ventilation/page.tsx` — parâmetros atuais + gráfico + histórico
**Reusar:** Layout, ErrorBoundary, SeverityBadge
**Estados:** current params, 24h trend, loading, error, empty

### FASE 3 — Estabilidade `/stability`
**Complexidade:** Alta. 27 critérios. Mapa de calor.
**Backend:** domain_hemo.py ✅ (existe)
**Arquivos (3):**
1. `lib/stability-types.ts` — 27 StabilityCriteria + StabilityStatus + mock
2. `components/StabilityHeatmap.tsx` — grid colorido 27 critérios por status
3. `app/stability/page.tsx` — score + heatmap + trend + filtros por categoria
**Reusar:** Layout, ErrorBoundary, SeverityBadge, CriteriaChecklist
**Estados:** heatmap view, category filter, 7d trend, loading, error, empty

### FASE 4 — Piora-Clinica `/clinical-deterioration`
**Complexidade:** Média. Score categórico (0/1+/1-/3+/3-) + multi-domínio.
**Backend:** domain_respiratory.py + domain_sepsis.py + domain_hemo.py ✅ (existem)
**Arquivos (2):**
1. `lib/deterioration-types.ts` — DeteriorationScore categórico + criteria por domínio + mock
2. `app/clinical-deterioration/page.tsx` — score gauge + criteria timeline + domain breakdown
**Reusar:** Layout, ErrorBoundary, ClinicalTimeline, SeverityBadge
**Estados:** current score, history, loading, error, empty

### FASE 5 — Stories + Gatekeeping
**Agentes (3 em paralelo):**
- Storybook Keeper: stories para PathwayBoard, VentilationTrendChart, StabilityHeatmap
- A11y Reviewer: WCAG 2.2 scan estático em 4 novas páginas
- UX Reviewer: Nielsen Norman em 4 domínios

### FASE 6 — Cross-Validation
- `npx tsc --noEmit`
- `npm run build`
- `npm run build-tokens`
- Nav update no Layout (+4 itens)
- HANDOFF.yaml atualizado

---

## Paralelização

```
FASE 0 (Tokens) ──┬── FASE 1 (Trilhas-Engine)
                  ├── FASE 2 (Ventilacao)        }── TODAS em paralelo
                  ├── FASE 3 (Estabilidade)       }   (sem dependências
                  └── FASE 4 (Piora-Clinica)      }    entre si)
                           │
                    FASE 5 (Gatekeeping) ── 3 agentes paralelos
                           │
                    FASE 6 (Cross-Validation)
```

## Estimativa

| Fase | Tamanho | Arquivos | Complexidade |
|------|---------|----------|-------------|
| FASE 0 | S | 1 | Baixa |
| FASE 1 (Trilhas) | XL | 3 | ⭐⭐⭐⭐⭐ Split-screen layout |
| FASE 2 (Ventilacao) | L | 3 | ⭐⭐⭐⭐ Recharts multi-linha |
| FASE 3 (Estabilidade) | L | 3 | ⭐⭐⭐⭐ Heatmap 27 critérios |
| FASE 4 (Piora) | M | 2 | ⭐⭐⭐ Score gauge |
| FASE 5 | M | 3 agentes | Gatekeeping |
| FASE 6 | S | — | Verificação |

## Rollback Plan

| Fase | Rollback |
|------|----------|
| FASE 0 | `git checkout HEAD -- app/tokens-generated.css` |
| FASE 1-4 | `git checkout HEAD -- app/{care-pathways,ventilation,stability,clinical-deterioration}/ lib/{pathway,ventilation,stability,deterioration}-types.ts components/{PathwayBoard,VentilationTrendChart,StabilityHeatmap}.tsx` |

## Scope Boundary

- ✅ DENTRO: 4 novas páginas, 3 novos componentes, tokens, types, mock data
- ✅ DENTRO: Reutilizar CriteriaChecklist, ClinicalTimeline, SeverityBadge, Layout, ErrorBoundary, DrawerBuilder
- ❌ FORA: Backend (parreira), contratos (Niemeyer), ADRs (Niemeyer)
