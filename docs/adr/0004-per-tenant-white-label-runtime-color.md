# 0004. Per-tenant white-label branding via a single runtime-recompiled primary color

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare is multi-tenant: each customer ("empresa") is a distinct hospital/ICU group. The legacy platform lets every tenant configure one brand color and re-skins the AntD UI to match it at runtime, on every page load, for every user of that tenant. Any rebuild of the platform has to decide how — or whether — to keep this per-tenant re-skinning, because the legacy mechanism is both load-bearing (it is the *only* tenant customization surfaced anywhere) and visibly broken (it renders the wrong color first, every time).

## The Legacy Decision

- Each tenant stores a single hex color, `cor_primaria` (stored without a leading `#`), set via a native `<Input type="color">` inside an "Identidade Visual" section of the company-settings form, next to a `whitelabel` identifier field. `trilhas-frontend:src/components/FormEmpresa/FormEmpresa.tsx:92-101`
- Applying the color is done by `useChangeColorTheme`'s `changeColorTheme(color)`, which does two things on every call: (a) calls `changeAntdTheme(color)` from the third-party `dynamic-antd-theme` package to recompile AntD's Less variables in the browser, and (b) sets two CSS custom properties, `--primary-color` and `--primary-shadow-color` (computed as `${color}2e`, i.e. the same hex with fixed alpha). `trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19`
- It is invoked twice per page load, in sequence, with different colors:
  1. `_app.tsx` unconditionally applies the hardcoded default `#fe6d01` on mount, but only when `isLight` is true, before any tenant data has loaded. `trilhas-frontend:src/pages/_app.tsx:36-40`
  2. `PageContainer` re-applies the real tenant color, `` `#${data.cor_primaria}` ``, once the `empresa` record is fetched. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:112-133`
- `--primary-color` is consumed at 60+ call sites across `.less` files, inline `style={}` props, and icon `color` props (inventory §1.3).
- `cor_primaria` is the only per-tenant customization surfaced anywhere in the product — there is no per-tenant typography, spacing, or logo layout (inventory §1.3).

## Evident Rationale

*(Inferred — not stated in the codebase.)* Per-tenant branding is plausibly a real, sales-driven requirement: white-labeling the bed-board UI to match each hospital group's own visual identity is a common enterprise-SaaS ask, and a single "primary color" swap is the cheapest way to satisfy it without building a full theming system. `dynamic-antd-theme` was likely chosen because the app already used AntD v4's Less-variable theming for its build-time dark/compact base (inventory §1.2), so a runtime Less recompiler looked like the path of least resistance to extend that same mechanism per tenant, rather than introducing a second theming model. The `_app.tsx` mount-time default-color call is plausibly a hedge against an unstyled flash before any data exists at all, but it was applied without accounting for the fact that `PageContainer` would immediately override it with the real value.

## Assessment

**Strengths (worth preserving as a capability):**
- Validates a real product need: tenants can carry their own brand identity into a shared clinical UI. Inventory explicitly flags this as "a real, validated need" worth keeping (inventory §1.3, Summary #8).
- The consuming surface (CSS custom properties) is itself a reasonable pattern — the problem is upstream of it, in how the value is produced and when it is applied.

**Weaknesses (do not port as-is):**
- **Flash of the wrong brand color on every load**, by construction: `_app.tsx` always sets `#fe6d01` first (gated only on `isLight`), then `PageContainer` overwrites it once tenant data arrives — two sequential, uncoordinated writers to the same state. `trilhas-frontend:src/pages/_app.tsx:36-40`; `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:112-133`
- **Fragile dependency:** `changeAntdTheme` recompiles Less in the browser via a small, unmaintained-looking third-party package (`dynamic-antd-theme`) rather than a first-party theming primitive — a maintenance and supply-chain risk for a mechanism that runs on every authenticated page. `trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19`
- **Dual write-paths for one value:** the same color is expressed twice per call (AntD Less recompile *and* two CSS variables), so any new consumer must know which of the two to read, and the two can drift if one path fails silently.
- **No validation or contrast guard** on the tenant-supplied hex: a native color `<input>` lets an admin pick any color, including one with poor contrast against text/icons that assume `--primary-color` is a mid-tone — nothing in `FormEmpresa.tsx:92-101` constrains this.
- **Scope is already maximally narrow** — one color, no logo, no secondary palette — so there is no existing per-tenant "system" to lift forward, only the single value and the flash-of-default bug to fix.

## Considered Options

1. **Lift and shift**: keep `dynamic-antd-theme` and the double-apply pattern, just reorder so `PageContainer`'s value wins. Rejected — retains a fragile third-party runtime-recompilation dependency and does not address root cause (two independent call sites writing the same state).
2. **Single CSS-variable token, resolved before first paint, feeding AntD v5's `theme.token.colorPrimary`.** Fetch (or read from an SSR/edge-cached tenant record, or a signed cookie/JWT claim set at login) the tenant's primary color *before* the app shell renders, set it once as the AntD v5 `ConfigProvider` theme token and as a single `--primary-color` CSS variable, and never re-apply it client-side after mount. No runtime Less recompilation.
3. **Build-time per-tenant bundles.** Statically generate a themed bundle per tenant at deploy time. Rejected for this ADR's scope — needlessly heavyweight for a single-color token, multiplies build/deploy artifacts, and doesn't fit a platform serving many tenants from one deployment.
4. **Expanded theming system (logo, secondary color, typography, default mode) via a tenant "brand" object.** Real option for a later iteration, but it is new scope, not a lift-and-shift of the legacy capability — noted here as a future direction, not the immediate recommendation.

## Decision Outcome

Recommend **Option 2**: a single, deterministic primary-color token resolved before first paint and fed into the framework's native theming primitive (e.g. AntD v5 `theme.token.colorPrimary`, or the equivalent design-token entry point for whatever component library is chosen), applied exactly once with no client-side re-application step. Concretely: resolve the tenant's color server-side (SSR prop, edge config, or a claim already present at auth time) so the first HTML/CSS the client paints already reflects the tenant's brand — eliminating the two-writer race that causes the flash-of-default-orange. Drop `dynamic-antd-theme` and any runtime Less recompilation entirely; a CSS-custom-property-driven or CSS-in-JS token system does not need it. Treat deeper per-tenant branding (logo, secondary color, default light/dark mode) as new scope to be proposed separately if there is product demand, not assumed as part of this rebuild.

This is a recommendation pending team ratification; the concrete data-fetch mechanism (SSR prop vs. edge cache vs. auth claim) should be settled against whatever framework and auth architecture the team ultimately adopts.

### Consequences

**Good:**
- Removes the flash-of-default-brand-color defect by construction — there is only one writer, and it runs before paint.
- Drops a fragile, unmaintained-looking third-party runtime-Less dependency, reducing supply-chain and upgrade risk.
- A single token value is simpler to test, cache, and reason about than two parallel mechanisms (Less recompile + CSS vars) doing the same job.

**Bad:**
- Requires the tenant's color to be available at (or before) first render, which may mean adding it to the auth/session payload or an edge-cacheable endpoint — a small architectural dependency that legacy did not need (legacy fetched it lazily after mount).
- Still inherits the legacy product limitation that only one color is customizable per tenant; if the business needs richer white-labeling (logo, secondary palette), that is a separate, larger effort not covered by this ADR.
- Contrast/validation of tenant-supplied colors is still an open gap and should be scoped explicitly (e.g. a min-contrast check on the `FormEmpresa`-equivalent input) rather than silently inherited.
