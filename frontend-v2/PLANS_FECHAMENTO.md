# PLANS.md — Fechamento de Qualidade Frontend

> Data: 2026-07-08 | Handoff: PROMPT_FECHAMENTO_FRONTEND.md

## Finding Inventory

| ID | Fase | Arquivo | Linha | Problema | Severidade |
|----|------|---------|-------|----------|------------|
| A.1 | CRITICAL | prescription/page.tsx | 674 | Drug interaction OR→AND | 🔴 |
| A.2 | CRITICAL | clinical-forms/page.tsx | 101,114 | LPP mapped as BPS/NRS | 🔴 |
| B.1a | HIGH | prescription/page.tsx | 724 | Simular Erro button | 🟠 |
| B.1b | HIGH | documentation/page.tsx | 708 | Simular Erro button | 🟠 |
| B.1c | HIGH | efficiency/page.tsx | 1015 | Simular Erro button | 🟠 |
| B.1d | HIGH | antimicrobial-stewardship/page.tsx | 431 | Simular Erro button | 🟠 |
| B.1e | HIGH | nutrition/page.tsx | 748 | Simular Erro button | 🟠 |
| B.2a | HIGH | patient-movement/page.tsx | 557 | Dead loading states | 🟠 |
| B.2b | HIGH | admin/registry/page.tsx | 173 | Dead loading states | 🟠 |
| B.3 | HIGH | indicators/page.tsx | 471 | Math.random() | 🟠 |
| D.1 | A11Y | tokens-generated.css | — | 6 contrast violations | 🔴 |

## Milestones (parallel where possible)

### M1: CRITICAL + A11Y (3 agents paralelos)
- Agent A: A.1 (drug interaction fix)
- Agent B: A.2 (LPP mapping fix)
- Agent C: D.1 (contrast token fix)

### M2: HIGH — Limpeza + Estados (3 agents paralelos)
- Agent D: B.1 (remove all Simular Erro buttons in 5 files)
- Agent E: B.2 (connect loading states in 3 domains)
- Agent F: B.3 (Math.random → deterministic)

### M3: Cross-Validation
- tsc + build + build-tokens + storybook + path check + HANDOFF
