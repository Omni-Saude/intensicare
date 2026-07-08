# PLANS.md — Product-Design-Orchestrator Execution Plan

> **Projeto:** IntensiCare v2 — Sprint 1-2 Quick Wins
> **Handoff de:** Niemeyer (System Architect)
> **Data:** 2026-07-07
> **Formato:** Milestones de ≤3 arquivos, rollback por milestone, gatekeepers por fase

---

## Milestone Map

```
M0: RECON (1 agente)           → RECON_DESIGN_SYSTEM.md
M1: TOKENS (1 agente)          → tokens em tokens-generated.css
M2: COMPONENTS BASE (1 agente) → 4 componentes em components/
    ├─ CriteriaChecklist
    ├─ ClinicalTimeline
    ├─ BundleCard
    └─ StewardshipScoreBadge
M3: SEPSE PAGE (1 agente)      → app/sepse-dashboard/page.tsx
M4: ANTIMICROBIANO PAGE (1 agente) → app/antimicrobial-stewardship/page.tsx
M5: PROFILAXIA PAGE (1 agente) → app/prophylaxis-bundles/page.tsx
M6: INTEGRATION (1 agente)     → Layout update + build check + GATE final
```

---

## Detalhamento por Milestone

### M0 — RECON Design System
| Campo | Valor |
|-------|-------|
| Arquivos | 0 novos (read-only) |
| Agente | `figma-intake-agent-loop` |
| Output | `docs/audit/handoff-product-designer/RECON_DESIGN_SYSTEM.md` |
| Rollback | N/A (read-only) |
| Gatekeeper | Niemeyer (via cross-check de tokens/componentes listados) |

### M1 — Design Tokens
| Campo | Valor |
|-------|-------|
| Arquivos | `app/tokens-generated.css` (append) |
| Agente | `design-token-management-loop` |
| Tokens novos | `--clinical-sepsis-*`, `--clinical-antimicrobial-*`, `--clinical-prophylaxis-*` |
| Rollback | `git checkout app/tokens-generated.css` |
| Gatekeeper | `design-system-governance-loop` |

### M2 — Componentes Base
| Campo | Valor |
|-------|-------|
| Arquivos | `components/CriteriaChecklist.tsx` + `.stories.tsx`, `components/ClinicalTimeline.tsx` + `.stories.tsx`, `components/BundleCard.tsx` + `.stories.tsx`, `components/StewardshipScoreBadge.tsx` + `.stories.tsx` |
| Agente | `component-mapping-loop` → `design-to-code-agent-loop` |
| Rollback | `rm components/CriteriaChecklist.tsx components/CriteriaChecklist.stories.tsx ...` |
| Gatekeeper | `ux-review-agent-loop` + `accessibility-review-agent-loop` |

### M3 — Sepse Dashboard
| Campo | Valor |
|-------|-------|
| Arquivos | `app/sepse-dashboard/page.tsx`, `app/sepse-dashboard/layout.tsx` |
| Agente | `design-to-code-agent-loop` |
| Dependências | M1 (tokens), M2 (CriteriaChecklist, ClinicalTimeline) |
| Rollback | `rm -r app/sepse-dashboard/` |
| Gatekeeper | `ux-review-agent-loop` |

### M4 — Antimicrobiano Stewardship
| Campo | Valor |
|-------|-------|
| Arquivos | `app/antimicrobial-stewardship/page.tsx`, `lib/antimicrobial-types.ts` |
| Agente | `design-to-code-agent-loop` |
| Dependências | M1 (tokens), M2 (CriteriaChecklist, StewardshipScoreBadge) |
| Rollback | `rm -r app/antimicrobial-stewardship/ lib/antimicrobial-types.ts` |
| Gatekeeper | `ux-review-agent-loop` |

### M5 — Profilaxia Bundles
| Campo | Valor |
|-------|-------|
| Arquivos | `app/prophylaxis-bundles/page.tsx`, `lib/prophylaxis-types.ts` |
| Agente | `design-to-code-agent-loop` |
| Dependências | M1 (tokens), M2 (BundleCard) |
| Rollback | `rm -r app/prophylaxis-bundles/ lib/prophylaxis-types.ts` |
| Gatekeeper | `ux-review-agent-loop` |

### M6 — Integração + GATE Final
| Campo | Valor |
|-------|-------|
| Arquivos | Layout update (sidebar links), `COMPLETION_REPORT.md` |
| Agente | `storybook-sync-agent-loop` + `visual-regression-agent-loop` |
| Dependências | M3, M4, M5 |
| Rollback | `git checkout components/Layout.tsx` |
| Gatekeeper | `visual-regression-agent-loop` (zero regressões) + `accessibility-review-agent-loop` final |

---

## Paralelismo

```
M0
 │
 ├── M1 (tokens) ──┐
 └── M2 (comps)  ──┤  (M1 e M2 PARALELO — não compartilham arquivos)
                    │
                    ▼
              ┌─────┼─────┐
              M3    M4    M5   (PARALELO — domínios independentes)
              └─────┼─────┘
                    ▼
                    M6
```

---

## Verificação por Milestone

| Milestone | Comando de Verificação |
|-----------|----------------------|
| M2 | `npx tsc --noEmit` nos novos componentes |
| M3 | `npx tsc --noEmit && npm run build` (verifica integração com API existente) |
| M4 | `npx tsc --noEmit && npm run build` |
| M5 | `npx tsc --noEmit && npm run build` |
| M6 | `npm run build && git diff --stat` (confirma escopo de mudanças) |
