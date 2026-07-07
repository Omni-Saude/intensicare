# PLANS.md — IntensiCare Frontend-v2 Audit Remediation

**Based on:** `audit-results/FIXES_PROMPT.md`
**Created:** 2026-07-07
**Branch:** main (working from HEAD: f25170f)
**Stack:** Next.js 15 + React 19 + Radix UI + Tailwind CSS v4 (ratified)

---

## 1. Objective

Execute ALL corrections identified in the frontend-v2 canonical audit:
- 18 ADRs compliance
- 61 hardcoded color violations
- 14 WCAG FAILs
- 6 state coverage bugs
- Design system maturity gaps

## 2. Milestones

| ID | Milestone | Agents | Status | Files | Verification | Risk |
|----|-----------|--------|--------|-------|-------------|------|
| **M0** | Stack Ratification | 1 agent | ✅ COMPLETE | ADR 0001, STACK_DECISION.md, ADR 0019 | Human sign-off (Rodrigo) | L1 |
| **M1a** | Token Pipeline (base) | 1.2 | ✅ DONE | radius.json, elevation.json, z-index.json | `npm run build-tokens` | L1 |
| **M1b** | Token Integration + Colors | 1.1 + 1.3 | 🔄 RUNNING | globals.css @theme + 10 page/component files | `npm run build-tokens && npm run build` | L2 |
| **M2a** | Dedup + Dead Code | 2.1 | ⏳ PENDING | lib/clinical-severity.ts, del BedCard/VitalsChart/FluidBalanceSummary | `npm run build` | L2 |
| **M2b** | Radix Dialog + State Fixes | 2.2 + 2.3 | ⏳ PENDING | DrawerBuilder, useOverlayStack, 6 bugs | `npm run build && lint` | L2 |
| **M3** | Clinical Safety (all 3) | 3.1, 3.2, 3.3 | ⏳ PENDING | FormEngine, useThreshold, contrast | `npm run build`, zero contrast FAILs | L2 |
| **M4** | Accessibility (both) | 4.1, 4.2 | ⏳ PENDING | WCAG fixes, UX keyboard/tooltips | Playwright + axe scan | L2 |
| **M5** | DS Maturity (both) | 5.1, 5.2 | ⏳ PENDING | Storybook, CI, docs, eslint-plugin | CI green, Storybook deploy | L2 |
| **M6** | Final Verification | 1 agent | ⏳ PENDING | VERIFICATION_REPORT.md, all checks | All gates PASS | L2 |

### Discovery (2026-07-07): design-tokens/ already exists
The forensic remediation (HANDOFF.yaml: "design-tokens: 24 files + build/") already created the full Style Dictionary infrastructure. M1a was re-scoped from "create" to "align existing tokens with FIXES_PROMPT spec."

## 3. Dependencies

```
M0 (human gate)
 └─→ M1a (1.1: token infrastructure)
      └─→ M1b (1.2: scales ∥ 1.3: hardcoded colors)
           └─→ M2a (2.1: dedup/dead code)
                └─→ M2b (2.2: Radix dialog ∥ 2.3: state fixes)
                     └─→ M3 (3.1: form engine → 3.2: thresholds ∥ 3.3: contrast)
                          └─→ M4 (4.1: WCAG ∥ 4.2: UX)
                               └─→ M5 (5.1: Storybook ∥ 5.2: Docs/CI)
                                    └─→ M6 (verification)
```

## 4. Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| design-tokens/ doesn't exist, build-tokens script broken | HIGH (confirmed) | Blocks FASE 1 | Fix script path to frontend-v2/design-tokens/ |
| Agent 1.2 (scales) conflicts with Agent 1.1 (base) on tokens.json | MEDIUM | Merge conflict | Serialize: 1.1 first, then 1.2 |
| FormEngine rebuild is complex (10 field renderers + 3 config JSONs) | HIGH | Blocks FASE 3 | Break into sub-milestones if needed |
| API endpoints missing (thresholds, clinical-forms) | MEDIUM | Partial delivery | Fallback to hardcoded defaults (per prompt) |
| npm install of @tanstack/react-table, react-hook-form, zod | LOW | Package conflicts | Test install before dispatch |

## 5. Rollback Plan

- Each milestone has independent `git commit` — revert by `git revert <commit>`
- FASE 1: `git checkout -- app/globals.css` restores original tokens
- FASE 2: `git checkout -- components/ lib/` restores components
- FASE 3-5: Same pattern — per-directory rollback

## 6. Gatekeepers Required

| Milestone | Gatekeeper | Type |
|-----------|-----------|------|
| M0 | Human (Rodrigo) | Stack decision |
| M1b | DS Guardian | Token compliance |
| M2b | UX Reviewer | Component quality |
| M3 | A11y Reviewer | Contrast + threshold |
| M4 | A11y + UX | WCAG pass |
| M5 | DS Guardian | Doc + CI |
| M6 | production-validator + security-manager | Final sign-off |

## 7. Delegation Order

1. M0: STACK_DECISION.md agent (deleg_2b213c0b — RUNNING)
2. M1a: Token Pipeline agent (serial first)
3. M1b: Token Scales agent ∥ Hardcoded Colors agent (parallel after M1a)
4. M2a: Dedup/Dead Code agent (after M1b)
5. M2b: Radix Dialog agent ∥ State Fixes agent (after M2a)
6. M3.1 → M3.2, M3.3
7. M4.1 ∥ M4.2
8. M5.1 ∥ M5.2
9. M6: Final verification agent

## 8. Effort Estimate

**XL** — 14+ agents across 6 phases, 61+ files, 3 new libraries to install.
