# 0001. Frontend framework and UI-library foundation

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's legacy frontend (`trilhas-frontend`) is a 2021-era Next.js/Ant Design
application: 463 `.ts`/`.tsx` files, 153 `.less` files (4,888 lines), 117 component
directories, 27 routed pages (`trilhas-frontend:src`, inventory 1.1). Rebuilding the
platform requires deciding whether to keep, upgrade, or replace this foundation, because
that choice determines whether design tokens, theming, and i18n can be first-class or
require workarounds. The legacy theming stack (5 stacked, independently-authored
mechanisms) is analyzed separately (→ ADR 0002–0004); this ADR addresses the
framework/UI-library foundation those layers were built on.

## The Legacy Decision

The legacy frontend is **Next.js `^12.2.2` (pages router) + React `^17.0.2` + Ant Design
`^4.21.7`**, themed via **LESS** through `next-plugin-antd-less ^1.8.0`
(`trilhas-frontend:package.json:1-45`; `trilhas-frontend:next.config.js:1-38`). AntD's own
Less-variable generator is invoked directly in `next.config.js`:

```js
modifyVars: {
  ...getThemeVariables({ dark: true, compact: true }),
  ...variables,   // 15 @primary-color etc. constants
}
```
(`trilhas-frontend:next.config.js:22-28`)

Per-component AntD style imports are wired through `babel-plugin-import`
(`libraryName: "antd", style: true`, `trilhas-frontend:.babelrc:1-13`). Supporting stack:
Firebase `^8.7.1` (Firestore only), `agora-rtc-react ^1.1.1` (video), a raw `websocket`
(`w3cwebsocket`) client for notifications, `moment ^2.29.4` + `moment/locale/pt-br`,
`nookies ^2.5.2` (cookie-based SSR auth), `next-pwa ^5.5.4`
(`trilhas-frontend:package.json:18-40`). The app is locale-locked to Brazilian Portuguese —
`ConfigProvider locale={ptBR}` plus the moment PT-BR locale — with **no i18n scaffolding
observed anywhere in the tree** (inventory 1.1, 1.4; D-01 §7.4).

AntD v4 means Less-variable theming only: no `ConfigProvider` `theme.token`/
`theme.algorithm` API (that arrived in v5) and no CSS-in-JS tokens. This is the documented
root cause of the 5-layer theming stack (build-time dark+compact compile → stock-AntD
light overlay → ~30 manual patches → 23 per-component `.light` hex blocks → runtime
per-tenant Less recompilation) detailed in ADR 0002–0004 (inventory 1.4, 2.7; D-01 §7.4).

## Evident Rationale

*(Inferred — not stated in any commit or doc found in the audit.)* In 2021 a Next.js
pages-router app on Ant Design 4 was a standard, low-risk choice for a B2B
data-density product: AntD shipped ready-made enterprise components (tables, forms,
drawers) suited to a clinical CRUD-and-dashboard app, and the pages router was the only
router Next.js offered then (app router shipped in Next 13, 2022). PT-BR-only is
consistent with a single-market Brazilian hospital product with no near-term
international rollout planned; `moment`/`nookies` were the conventional date/cookie
libraries for that Next.js generation.

## Assessment

**Strengths observed:**

- Internally coherent for its era — `next-plugin-antd-less` + `babel-plugin-import` is the
  documented way to theme AntD v4 with Less, and it works (inventory 1.4; D-01 §7.4).
- AntD's component surface let the team build 117 component directories without
  hand-rolling tables, drawers, form controls.
- The schema-driven clinical form engine (`FormDadosProntuario`, 14 role-specific forms)
  is strong, framework-agnostic reusable IP worth preserving regardless of this decision
  (inventory 3.3, §8).

**Weaknesses, cited:**

- **AntD v4 forecloses first-class token theming.** `modifyVars` is Less-only and
  build-time (or third-party-recompiled); there is no live theme switch — toggling
  light/dark requires `window.location.reload()`
  (`trilhas-frontend:src/hooks/useLightTheme.ts:1-23`; inventory 2.7). This single version
  choice cascades into the entire 5-layer theming stack.
- **Two independently-maintained copies of the same 15 tokens.** The Less mechanism
  required duplicating `next.config.js`'s `variables` object, value-for-value, into
  `src/styles/variables.less:1-15` — a file **never `@import`-ed by any `.less` file**, so
  it is a dead second copy (inventory 2.1, 2.7; D-01 §1.1) — a direct consequence of
  `modifyVars` needing a JS object at config time rather than an importable `.less` file.
- **PT-BR-only is an unexamined scope decision, not a stated one.** `ConfigProvider
  locale={ptBR}` and `moment/locale/pt-br` are hardcoded with no i18n library or
  locale-switch mechanism anywhere (inventory 1.1, 1.4). If multi-market expansion is on
  the roadmap this must be reversed deliberately now — retrofitting i18n onto 463 files
  later costs far more than deciding up front.
- **Runtime per-tenant re-theming** depends on a small third-party package
  (`dynamic-antd-theme ^0.8.7`) recompiling AntD Less in the browser, applied twice
  (`_app.tsx` then `PageContainer`), producing a visible flash-of-default-color bug
  (inventory 1.3; → ADR 0004) — a symptom of the version/theming limitation, not an
  isolated bug.
- **Pages router + React 17** are both superseded (app router since Next 13; React 18
  concurrent features), so the legacy app cannot use either without a major upgrade
  regardless of the UI-library decision.

## Considered Options

1. **Upgrade in place: Next.js (app router) + React 18/19 + Ant Design v5.** Keeps the
   component vocabulary and the clinical-form engine's patterns while gaining AntD v5's
   `ConfigProvider` `theme.token`/`theme.algorithm` — first-class light/dark and
   per-tenant theming without Less recompilation.
2. **Next.js (app router) + a headless component layer** (Radix/shadcn-style) + Tailwind
   or CSS-variable tokens. Maximum control over tokens/accessibility/bundle size; no
   inherited AntD debt; highest migration cost since almost no legacy component reuses
   directly.
3. **Next.js (app router) + a different enterprise design system** (Chakra, Mantine)
   already token-based. Middle ground — modern theming out of the box, but discards
   AntD's clinical-table/form density the product depends on and adds a new library to
   learn.
4. **Keep pages router + AntD v4, patch only the theming mechanism.** Lowest short-term
   cost; rejected — does not address the root cause (AntD v4 has no token API) and would
   re-author the same 5-layer stack under a new name.

## Decision Outcome

**Recommended: Option 1 — Next.js (app router) + React 18+ + Ant Design v5**, adopting
AntD v5's `ConfigProvider` `theme.token`/`theme.algorithm` as the single source of truth
for both light/dark and per-tenant brand theming, replacing Less `modifyVars` and
`dynamic-antd-theme` entirely. Locale moves to `ConfigProvider locale` plus a real i18n
library (e.g. `next-intl`) with PT-BR as the sole shipped locale initially — turning
"PT-BR-only" from an implicit constraint into an explicit, revisitable scope decision.
`moment` should be replaced with a maintained, tree-shakeable date library (e.g. `dayjs`,
which AntD v5 itself uses internally). Firebase, Agora, and the raw WebSocket client are
out of scope here and addressed in the real-time/data-flow ADR set (→ ADR 0017).

This is a **recommendation pending team ratification** — it assumes the team accepts an
AntD v4→v5 breaking-change migration rather than a full rewrite, on the premise that the
component vocabulary and clinical-form patterns are worth preserving and that a
from-scratch system (Option 2/3) isn't justified: the audit points to a
*theming-mechanism* defect, not a *component-library* defect.

### Consequences

**Good:**

- AntD v5 tokens make per-tenant white-labeling (a validated real requirement, inventory
  1.3) first-class instead of fragile runtime recompilation, resolving both the
  flash-of-default-color bug and the duplicate-token-copy defect.
- App router unlocks server components/streaming for the cascading data-loads currently
  done client-side inside `PageContainer` (inventory 4.1) — addressed further in the
  layout ADR.
- Explicit i18n scaffolding removes a silent scope assumption and de-risks future
  multi-market expansion.
- The clinical form engine's design transfers with moderate, not full-rewrite, effort.

**Bad:**

- AntD v4→v5 is a genuine breaking-change migration (new theming API, component
  prop/behavior changes) across 281 `.tsx` files — nontrivial cost, not a drop-in upgrade.
- Pages-router-to-app-router migration touches all 27 routed pages and the SSR auth
  pattern (`nookies`/`validateRoute`), which must be redesigned for app-router data
  fetching.
- Staying on AntD still inherits its visual idiom and bundle-size profile; a fully bespoke
  design language would require revisiting this decision later at higher cost than
  choosing Option 2/3 now.
