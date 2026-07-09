# 0003. Light mode as a client-only, cookie-gated, full-reload CSS overlay

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform ships a single, permanently dark, compact Ant Design build: `next.config.js` calls `getThemeVariables({ dark: true, compact: true })` and layers 15 custom brand variables on top, producing one compiled CSS bundle for every user regardless of preference or tenant (trilhas-frontend:next.config.js:1-38). Light mode is not a second build — it is bolted on entirely in the browser. The question this ADR answers: how should the new IntensiCare platform implement a light/dark mode switch, given that the legacy mechanism is expensive to maintain, fragile at runtime, and forces a full page reload on every toggle?

## The Legacy Decision

Light mode in `trilhas-frontend` is assembled from four independently-authored layers that happen to visually cohere only through manual tuning:

1. **Cookie-gated preference, full reload on toggle.** `useLightTheme()` reads/writes a `theme.light` cookie via `nookies`; the toggle handler calls `window.location.reload()` — there is no live/reactive theme switch (trilhas-frontend:src/hooks/useLightTheme.ts:1-23).
2. **A stylesheet-injecting component, not a themed variable set.** When `isLight` is true, `_app.tsx` dynamically imports (`next/dynamic`, `ssr:false`) a `LightTheme` component whose entire body is `require("./LightTheme.less")` (trilhas-frontend:src/pages/_app.tsx:18-51).
3. **A full re-import of stock, un-customized `antd/dist/antd.css`.** `LightTheme.less` opens with `@import url("~antd/dist/antd.css")` — the default light AntD theme, standard density, default blue primary — layered on top of the dark/compact/orange bundle purely via later-wins CSS cascade order, plus roughly 30 hand-written patch rules fixing what breaks (card backgrounds forced `#fff !important`, drawer padding resets, upload-dragger dimensions, tab paddings, skeleton widths) (trilhas-frontend:src/themes/LightTheme.less:1-115).
4. **Per-component literal-color overrides, threaded via a prop.** 23 of 153 `.less` files hand-roll their own `&.light { ... }` block with hardcoded hex pairs; the `isLight` boolean is threaded down as a React prop through many component trees to conditionally apply the `"light"` class name, e.g. `ItemDefault.tsx:27-31` (trilhas-frontend:src/components/ItemDefault/ItemDefault.tsx:27-31). One of these 23 files breaks the naming convention outright: `ProtocoloSepseContent.less` uses `&.is-light` where the other 22 use `&.light` (trilhas-frontend:src/components/ProtocoloSepseContent/ProtocoloSepseContent.less:18).

## Evident Rationale

*(Inferred — not stated in code or commit history.)* This reads as a pragmatic "make it work" patch added after the dark, compact, branded build had already shipped as the default. Recompiling a second full AntD Less bundle (light + compact + branded) would have required either a second webpack output or a runtime Less recompilation pass; importing the stock light stylesheet and patching the visible breakage was the fastest way to offer *a* light mode without touching the established build pipeline. The full-reload toggle is a natural consequence of choosing `require()`-time stylesheet injection over a live-swappable token set — there is no mechanism in this design that could apply new colors without re-evaluating the page.

## Assessment

**Strengths:** the approach shipped a working light mode with a small, contained code footprint (one `.less` file plus ~23 component-level blocks) and did not require the team to build or maintain two parallel AntD compilations at build time.

**Weaknesses (this is the single most fragile part of the legacy design system and must not be carried forward):**
- **Cascade-order dependent, no compile-time guarantee.** Whether the light override "wins" for any given selector depends entirely on stylesheet load order and specificity, not on an explicit theme contract (trilhas-frontend:src/themes/LightTheme.less:1-115).
- **No shared semantic tokens.** Neither the dark base nor the light overlay is expressed as a token map; each of the 23 `.light`-block files re-derives its own literal hex pair per mode, so light/dark parity is a matter of per-component author discipline, not a system property (trilhas-frontend:src/components/ItemDefault/ItemDefault.tsx:27-31).
- **A `.is-light` naming outlier** shows the convention itself was never enforced by tooling — only 1 of 23 files drifted, but nothing prevented it (trilhas-frontend:src/components/ProtocoloSepseContent/ProtocoloSepseContent.less:18).
- **Forces a full reload.** `window.location.reload()` on every toggle discards client state (open drawers, in-progress form input, scroll position) purely to re-run the stylesheet-injection dance (trilhas-frontend:src/hooks/useLightTheme.ts:12-18).
- **Every new component must remember to author its own light variant** — there is no default, no fallback, and no lint rule catching a component that ships dark-only.

## Considered Options

1. **CSS custom properties (design tokens) with `data-theme` attribute switching.** Define one token set (`--color-surface`, `--color-text`, `--color-border`, etc.) with light and dark value maps selected by a `data-theme="light|dark"` attribute on `<html>`; components consume `var(--color-*)` and never branch on a boolean.
2. **Ant Design v5 `ConfigProvider` algorithm switching.** Adopt AntD v5's `theme.token`/`theme.algorithm` (`theme.darkAlgorithm` / `theme.defaultAlgorithm`) to generate both themes from one token source at runtime, with app-level tokens layered as CSS variables for non-AntD surfaces.
3. **Dual build-time bundles (one per theme), selected by hostname/cookie at request time.** Compile two fully separate CSS bundles (as the legacy dark bundle already is) and serve the correct one server-side based on stored preference.
4. **Keep a single dark-only theme; drop light mode entirely** for the initial platform release, revisiting only if a validated user need emerges.

## Decision Outcome

**Recommended: Option 1 combined with Option 2** — a token-driven theme, implemented as CSS custom properties for design tokens and (if AntD is retained) AntD v5's `ConfigProvider` algorithm switching for library-internal component styling, both driven by symmetric, compile-verified light/dark token maps and switched via a `data-theme` attribute with no page reload. This recommendation is **pending ratification by the engineering and design team** before implementation begins.

Rationale: this is the only option among those considered that structurally prevents the four failure modes observed in the legacy system — cascade-order dependence, missing semantic tokens, silent per-component omission, and forced reloads — while still letting the platform preserve the "ICU-appropriate, dark-first" default documented in ADR 0002 as an explicit, symmetric variant rather than the sole baked-in build. Option 3 (dual bundles) was rejected as unnecessary complexity once tokens exist; Option 4 (drop light mode) was rejected because light mode is a real, currently-used feature for non-bedside/administrative contexts and removing it is a product regression, not a technical fix.

### Consequences

**Good:**
- Theme switching becomes instant (no reload), preserving in-flight form state and open overlays.
- New components inherit correct light/dark behavior automatically by consuming tokens — there is no per-component `.light` block to remember or forget.
- Both themes are produced from one source of truth, so light and dark can be visually verified in CI/Storybook without manual cross-checking.
- Removes an entire class of "forgot to author a light variant" and cascade-order bugs by construction.

**Bad / trade-offs:**
- Requires an up-front investment to define the full token set (surface, text, border, elevation) before any component work can proceed — a real, but one-time, cost.
- If AntD is retained, v5's token/algorithm model is a breaking change from the legacy's Less-`modifyVars` approach (already a v4→v5 major-version jump the platform must make regardless, per the broader design-system rebuild).
- Existing visual nuances tuned by the legacy's ~30 manual patch rules (e.g. specific drawer padding, skeleton widths under stock AntD light CSS) will need to be re-derived and re-verified against the new token set rather than inherited for free.
