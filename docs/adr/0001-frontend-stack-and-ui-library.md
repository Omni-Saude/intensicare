# 0001. Frontend framework and UI-library foundation

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's legacy frontend (`trilhas-frontend`) is a 2021-era Next.js/Ant Design
application: 463 `.ts`/`.tsx` files, 153 `.less` files (4,888 lines), 117 component
directories, 27 routed pages (`trilhas-frontend:src`, inventory 1.1). As the platform is
rebuilt, we must decide whether to keep, upgrade, or replace the framework and UI-library
foundation, because that choice determines whether design tokens, theming, and
accessibility can be first-class citizens or require workarounds. The legacy stack's
theming approach is already the root cause of a 5-layer theming hack analyzed separately
(→ ADR 0002–0004); this ADR addresses the foundation those layers are built on.

## The Legacy Decision

The legacy frontend is **Next.js `^12.2.2` (pages router) + React `^17.0.2` + Ant Design
`^4.21.7`**, themed via **LESS** through `next-plugin-antd-less ^1.8.0`
(`trilhas-frontend:package.json:1-45`; `trilhas-frontend:next.config.js:1-38`). AntD's own
Less-variable theme generator is invoked directly in `next.config.js`:

```js
modifyVars: {
  ...getThemeVariables({ dark: true, compact: true }),
  ...variables,   // 15 @primary-color etc. constants
}
```
(`trilhas-frontend:next.config.js:22-28`)

Per-component AntD style imports are wired through `babel-plugin-import`
(`libraryName: "antd", style: true`) declared in `.babelrc:1-13`. Supporting stack:
Firebase `^8.7.1` (Firestore only, no other Firebase products), `agora-rtc-react ^1.1.1`
(video), a raw `websocket` (`w3cwebsocket`) client for notifications, `moment ^2.29.4` +
`moment/locale/pt-br`, `nookies ^2.5.2` (cookie-based SSR auth), and `next-pwa ^5.5.4`
(`trilhas-frontend:package.json:18-40`). The app is locale-locked to Brazilian Portuguese
— `ConfigProvider locale={ptBR}` plus the moment PT-BR locale — with **no i18n scaffolding
observed anywhere in the tree** (inventory 1.1, 1.4; D-01 §7.4).

AntD v4 means Less-variable theming only: there is no `ConfigProvider` `theme.token`/
`theme.algorithm` API (that arrived in AntD v5) and no CSS-in-JS design tokens. This one
fact is the documented root cause of the legacy platform's 5-stacked-mechanism theming
system (build-time dark+compact compile → stock-AntD light overlay → ~30 manual patch
rules → 23 per-component `.light` hex blocks → runtime per-tenant Less recompilation),
covered in full in ADR 0002–0004 (inventory 1.4, 2.7; D-01 §7.4).

## Evident Rationale

*(Inferred — not stated in any commit message or doc found in the audit.)* In 2021, a
Next.js pages-router app paired with Ant Design 4 was a standard, low-risk choice for a
B2B/enterprise data-density product: AntD shipped a large batch of ready-made
enterprise-grade components (tables, forms, drawers) suited to a clinical
CRUD-and-dashboard product, and the pages router was the only router Next.js offered at
the time (the app router did not exist until Next.js 13, 2022). PT-BR-only locale is
consistent with a single-market (Brazil) hospital product where no near-term
international rollout was planned, and moment + nookies were the conventional date/cookie
libraries for that Next.js generation.

## Assessment

**Strengths, as observed in the audit:**
- The stack was internally coherent for its era: `next-plugin-antd-less` +
  `babel-plugin-import` is the standard, documented way to theme AntD v4 with Less, and it
  works (inventory 1.4; D-01 §7.4).
- AntD's component surface let the team build a large, clinically-specific app (117
  component directories) without hand-rolling primitives like tables, drawers, and form
  controls.
- The config/schema-driven clinical form engine (`FormDadosProntuario`, 14 role-specific
  forms) is genuinely strong reusable IP that is framework-agnostic in design and worth
  preserving regardless of what the UI library decision is (inventory 3.3, §8).

**Weaknesses, specific and cited:**
- **AntD v4 forecloses first-class token theming.** Because `modifyVars` is a Less-only,
  build-time (or third-party-runtime-recompiled) mechanism, there is no
  `ConfigProvider`-driven live theme switch; toggling light/dark requires
  `window.location.reload()` (`trilhas-frontend:src/hooks/useLightTheme.ts:1-23`,
  inventory 2.7). This single version choice cascades into the 5-layer theming stack
  audited separately.
- **Two independently-maintained copies of the same 15 tokens.** The Less-only theming
  mechanism required duplicating `next.config.js`'s `variables` object, value-for-value,
  into `src/styles/variables.less:1-15` — a file **never `@import`-ed by any `.less`
  file**, so it is a dead second copy (inventory 2.1, 2.7; D-01 §1.1). This is a direct
  consequence of `modifyVars` requiring a plain JS object at Next.js config time rather
  than being able to `@import` a `.less` file.
- **PT-BR-only is an unexamined scope decision, not a stated one.** `ConfigProvider
  locale={ptBR}` and `moment/locale/pt-br` are hardcoded; no i18n library, no
  string-extraction convention, and no locale-switch mechanism exist anywhere in the tree
  (inventory 1.1, 1.4). If multi-market expansion is on the roadmap, this must be reversed
  deliberately now — retrofitting i18n onto 463 files later is far more expensive than
  deciding up front.
- **Runtime per-tenant re-theming depends on a small third-party package
  (`dynamic-antd-theme ^0.8.7`)** recompiling AntD Less variables in the browser, applied
  twice (`_app.tsx` then `PageContainer`), producing a visible flash-of-default-brand-color
  bug (inventory 1.3; → ADR 0004) — a symptom of the underlying version/theming
  limitation, not an isolated bug.
- **Pages router + React 17** are both superseded (Next.js app router since v13; React 18
  concurrent features) with no server-components option, so the legacy app cannot take
  advantage of either without a major upgrade regardless of the UI-library decision.

## Considered Options

1. **Upgrade in place: Next.js (latest, app router) + React 18/19 + Ant Design v5.**
   Keeps the team's existing component vocabulary and the valuable
   `FormDadosProntuario` engine's patterns, while gaining AntD v5's `ConfigProvider`
   `theme.token`/`theme.algorithm` API — first-class light/dark and per-tenant theming
   without Less recompilation.
2. **Next.js (app router) + a headless/unstyled component layer (e.g. Radix
   Primitives/shadcn-style) + Tailwind or CSS-variable design tokens.** Maximum control
   over tokens, accessibility, and bundle size; no inherited AntD visual/behavioral debt;
   highest migration/rebuild cost since almost no legacy component can be reused directly.
3. **Next.js (app router) + a different enterprise design system** (e.g. Chakra, Mantine)
   already built around a CSS-in-JS or CSS-variable token model. Middle ground: modern
   theming primitives out of the box, but discards AntD's clinical-table/form density that
   the legacy product depends on, and introduces a new library the team must learn.
4. **Keep Next.js pages router + AntD v4, patch only the theming mechanism.** Lowest
   short-term cost; explicitly rejected because it does not address the root cause
   identified in this audit (AntD v4 has no token API) and would simply re-author the same
   5-layer theming stack under a new name.

## Decision Outcome

**Recommended: Option 1 — Next.js (app router) + React 18+ + Ant Design v5**, adopting
AntD v5's `ConfigProvider` `theme.token`/`theme.algorithm` as the single source of truth
for both light/dark and per-tenant brand theming, replacing Less `modifyVars` and
`dynamic-antd-theme` entirely. Locale should move to `ConfigProvider` `locale` plus a real
i18n library (e.g. `next-intl`) with PT-BR as the sole shipped locale initially — this
reverses "PT-BR-only" from an implicit constraint into an explicit, revisitable scope
decision. `moment` should be replaced with a maintained, tree-shakeable date library (e.g.
`dayjs`, which AntD v5 itself uses internally) rather than carried forward. Firebase
(Firestore-only), Agora, and the raw WebSocket client are out of scope for this ADR and
are addressed in the real-time/data-flow ADR set (→ ADR 0017).

This is a **recommendation pending team ratification** — it assumes the team is willing to
absorb an AntD v4→v5 breaking-change migration (component API changes, CSS reset
differences) rather than a full rewrite, on the premise that the component vocabulary and
clinical-form patterns are worth preserving and that a from-scratch design system (Option
2/3) is not justified by the audit's findings, which point to a *theming-mechanism* defect,
not a *component-library* defect.

### Consequences

**Good:**
- AntD v5 tokens make per-tenant white-labeling (a validated, real requirement, inventory
  1.3) a supported first-class feature instead of a fragile third-party runtime
  recompilation, directly resolving the flash-of-default-color bug and the two
  independently-maintained token-copy defect.
- App router unlocks server components/streaming for the cascading data-loads that
  currently happen client-side inside `PageContainer` (inventory 4.1), a likely
  performance and correctness win addressed further in the layout ADR.
- Explicit i18n scaffolding removes a silent scope assumption and de-risks any future
  multi-market expansion.
- Most existing component knowledge, and all of the schema-driven clinical form engine's
  design, transfers with moderate (not full-rewrite) migration effort.

**Bad:**
- AntD v4→v5 is a genuine breaking-change migration (new theming API, some component
  prop/behavior changes) across 281 `.tsx` component files; this is nontrivial migration
  cost, not a drop-in upgrade.
- Pages-router-to-app-router migration touches all 27 routed pages and the SSR auth
  pattern (`nookies`/`validateRoute`), which must be redesigned for the app router's
  data-fetching model.
- Committing to AntD v5 (rather than a from-scratch system) still inherits AntD's overall
  visual idiom and bundle-size profile; teams wanting a fully bespoke design language
  would need to revisit this decision later at higher cost than choosing Option 2/3 now.
