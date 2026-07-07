# STACK_DECISION — IntensiCare Frontend-v2

**Date:** 2026-07-07  
**Status:** Ratified  
**Decision maker:** Administrador / Tech Lead  
**Applies to:** `frontend-v2/`

---

## Decision

**Option 2 — Radix UI + Tailwind CSS v4** has been selected as the frontend foundation for the IntensiCare rebuild (`frontend-v2/`), **overriding ADR 0001's original recommendation** of Next.js + Ant Design v5 (Option 1).

### What the stack looks like

| Layer | Choice | Version |
|---|---|---|
| Framework | Next.js (app router) | ^15.0.0 |
| React | React | ^19.0.0 |
| Headless primitives | Radix UI | @radix-ui/react-dialog, -tooltip, -dropdown-menu, -popover, -select, -tabs, -toast |
| Styling | Tailwind CSS | ^4.0.0 (via @tailwindcss/postcss) |
| Icons | Lucide React | ^0.400.0 |
| Charts | Recharts | ^3.9.2 |
| Design-token pipeline | Style Dictionary | ^5.5.0 |
| Component catalog | Storybook | ^8.6.14 (Next.js + React 19) |
| Type system | TypeScript | ^5.5.0 |

**What is NOT present:** `antd`, `less`, `next-plugin-antd-less`, `babel-plugin-import`, `moment`, `dynamic-antd-theme` — none of the legacy theming stack.

### Evidence (from the working codebase)

- `frontend-v2/package.json`: zero AntD dependency; Radix primitives + Tailwind + Lucide
- `frontend-v2/app/globals.css`: `@import "tailwindcss"` + manual `:root` / `[data-theme="light"]` CSS custom properties (no Less, no AntD token generator)
- `frontend-v2/app/layout.tsx:15`: `<html data-theme="dark">` — dark-first runtime switch via a data attribute, no `ConfigProvider`
- `frontend-v2/components/`: SeverityBadge, AlertCard, Layout, BedCard, VitalsChart, ScoreTimeline, FluidBalanceSummary — all built on Radix primitives + Tailwind utilities

---

## Justification

### 1. Full token control
CSS custom properties (`--semantic-surface-canvas`, `--clinical-severity-*`, etc.) declared directly in `globals.css` and mapped into Tailwind's `@theme` block. No dependency on a third-party library's opinionated token shape (e.g., AntD `theme.token`). Design tokens are authored once in a Style Dictionary pipeline (`design-tokens/`) and consumed as CSS vars — the theme is owned by the product, not by the component library.

### 2. Smaller bundle
No AntD (~500 KB+ minified) shipped to every user. Radix primitives are individually tree-shakeable (e.g., `@radix-ui/react-dialog` ≈ 12 KB). Tailwind CSS v4's JIT-on-demand produces only the utilities actually used. This matters for bedside dashboards and mobile monitoring views where bandwidth is constrained.

### 3. Dark-first, natively
The dark theme is the `:root` / `[data-theme="dark"]` default in `globals.css`. Light is an opt-in override via `[data-theme="light"]`. No AntD `ConfigProvider theme.algorithm` wrapper, no `dynamic-antd-theme` runtime recompilation, no `window.location.reload()` to toggle theme. A single `<html data-theme="…">` attribute switch is sufficient — and is already wired.

### 4. No opinionated library lock-in
AntD v5 dictates component shape, spacing, typography rhythm, and interaction patterns. Radix provides unstyled, accessible primitives — the visual language belongs entirely to IntensiCare's design system. This means:
- Neumorphic elevation (ADR 0007) is implemented as Tailwind `box-shadow` utilities, not mapped through AntD's shadow token schema
- The drawer-in-drawer pattern (ADR 0010) uses `@radix-ui/react-dialog` directly, not AntD `Drawer` with its built-in header/footer/close conventions
- The clinical form engine (ADR 0015) renders through custom field renderers styled with Tailwind, not AntD `Form.Item`

### 5. Why Option 1 (AntD v5) was NOT chosen
Option 1 was recommended as a "preserve the component vocabulary" migration from AntD v4 to v5. However:
- The legacy app's 281 `.tsx` files and 153 `.less` files represent accumulated technical debt, not reusable IP (except the clinical form engine, which is framework-agnostic config data)
- AntD v4→v5 is a genuine breaking-change migration — component APIs, theme token shapes, and Less→CSS-in-JS all change — so "upgrade in place" is nearly as expensive as a rewrite
- Staying on AntD inherits its visual idiom and bundle-size profile indefinitely; a full rebuild is the only window to escape this
- The admin explicitly chose Option 2, and the team has already implemented it

---

## Impact on Dependent ADRs

### ADR 0002 — Dark-first, compact base theme

**Original assumption:** AntD's dark algorithm (`getThemeVariables({dark: true, compact: true})`) baked at build time.  
**What changes with Radix/Tailwind:** No AntD dark algorithm exists. Dark-first is instead authored directly as `:root` CSS custom properties — the dark palette is the default, and light is the `[data-theme="light"]` override. Compact density is achieved through Tailwind spacing/padding utilities (e.g., `p-2` instead of `p-4`), not AntD's `compact: true` compilation pass.

**Reinterpretation:** ADR 0002's core recommendation — dark+compact as the explicit, documented default — remains valid and is already implemented. The *mechanism* changes from "AntD Less-variable generator" to "CSS custom properties + Tailwind density tokens." The symmetry goal (dark+compact default, light+comfortable available) is preserved; runtime switching is now a `data-theme` attribute toggle rather than a `ConfigProvider algorithm` swap.

**Actionable note:** Update ADR 0002 to reference CSS custom properties as the implementation vehicle for dark-first theming, and Tailwind spacing scale as the density mechanism. Remove references to `getThemeVariables` and AntD `compact` parameter.

---

### ADR 0007 — Neumorphic dual-shadow elevation

**Original assumption:** AntD's `box-shadow` tokens (or the absence thereof — the legacy had no shadow tokens).  
**What changes with Radix/Tailwind:** Elevation is expressed as Tailwind `shadow-*` utilities (e.g., `shadow-[5px_5px_10px_#0b0b0b,-5px_-5px_10px_#1d1d1d]` or, better, as named `@theme` shadow tokens). No AntD shadow token API exists to map through.

**Reinterpretation:** ADR 0007's core recommendation — preserve neumorphic dual-shadow elevation as a governed token scale (`sm`/`md`/`lg`) — remains fully applicable. The *implementation* changes from "AntD shadow tokens" to "Tailwind shadow utilities anchored in CSS custom properties or `@theme` shadow values." The accessibility fallback (`prefers-contrast`) is equally implementable.

**Actionable note:** Define an explicit Tailwind shadow scale: `--shadow-elevated-sm`, `--shadow-elevated-md`, `--shadow-elevated-lg`, each with a dark variant and a light variant (two values per token: one for `[data-theme="dark"]`, one for `[data-theme="light"]`). Wire `prefers-contrast: more` to substitute a flat single shadow. The sm/md/lg values from the ADR can be adapted directly — they're hex + offset literals, not AntD-specific.

---

### ADR 0010 — Drawer-in-drawer secondary view pattern

**Original assumption:** AntD `Drawer` component, wrapped in `DrawerBuilder`.  
**What changes with Radix/Tailwind:** `@radix-ui/react-dialog` replaces AntD `Drawer`. Radix Dialog is an unstyled, accessible overlay primitive with built-in focus trapping, Escape-to-close, and body scroll locking — the exact primitives the overlay-stack manager needs. `DrawerBuilder`'s visual conventions (width, footer, close affordance, `destroyOnClose`) are reimplemented as a Radix `Dialog` wrapper styled with Tailwind.

**Reinterpretation:** ADR 0010's core recommendation — keep the drawer-over-page visual pattern, add a generic overlay/stack manager — is fully compatible and arguably easier with Radix. Radix Dialog already provides focus trapping and Escape handling per-dialog; the overlay-stack manager only needs to own depth (which dialog is topmost) and back-button coordination. `DrawerBuilder` becomes a styled Radix `Dialog.Content` with Tailwind positioning/sizing.

**Actionable note:** Implement `OverlayStack` as a React context provider that maintains an ordered stack of dialog IDs. On Escape, close only the topmost. `DrawerBuilder` wraps `<Dialog.Root>` + `<Dialog.Portal>` + `<Dialog.Content>` with the existing width/close/footer conventions expressed as Tailwind classes. The 16 legacy call sites migrate to registering with the stack rather than hand-wiring boolean visibility state.

---

### ADR 0015 — Config-driven dynamic clinical form engine

**Original assumption:** AntD `Form`, `Form.Item`, `Collapse.Panel`, `Select`, `Checkbox`, `DatePicker` etc. as the rendered field vocabulary.  
**What changes with Radix/Tailwind:** No AntD form primitives exist. The config-driven engine renders through custom field renderers — one per `campo.type` — built from Radix primitives (e.g., `@radix-ui/react-select` for `select` type, `@radix-ui/react-checkbox` for `boolean`/`checkbox` types) or native HTML inputs styled with Tailwind. The field-type dispatch (`SelectCampoType`) remains structurally identical — only the rendered components change from AntD `Form.Item` + `Input`/`Select` to Radix + Tailwind equivalents.

**Reinterpretation:** ADR 0015's core recommendation — preserve and modernize the config/schema-driven engine — is **unchanged and fully compatible**. The engine's config shape (`Models.DadosFormDinamico[]`, `campo.type`, `grupo`/`subGroup`/`campos` hierarchy) is framework-agnostic data. The modernization goals (strongly-typed schema, unified visibility/nullability rule engine) are independent of the rendering layer. A Radix/Tailwind implementation is arguably simpler: each `SubForm*` renderer is a self-contained Radix primitive + Tailwind styles, with no dependency on AntD's form context, validation wiring, or `Form.Item` layout conventions.

**Actionable note:** The 10 `SubForm*` renderers from the legacy engine are reimplemented as:
- `string`, `masked` → `<input>` + Tailwind form classes
- `select` → `@radix-ui/react-select`
- `boolean`, `checkbox` → `@radix-ui/react-checkbox`
- `number` → `<input type="number">` + Tailwind
- `interval` → two `<input>` fields, range validation
- `data` → `@radix-ui/react-popover` + date grid or native `<input type="date">`
- `list` → dynamic field array renderer
- `multicheck` → `@radix-ui/react-checkbox` group

The config schema (Zod/JSON Schema) is shared with the backend regardless of rendering library.

---

## ADR Status Summary

| ADR | Title | Original Status | Final Status | Notes |
|---|---|---|---|---|
| 0001 | Frontend stack and UI library | `proposed` | **`accepted`** | Updated 2026-07-07: decision ratified as Option 2 (Radix + Tailwind), overriding original Option 1 recommendation |
| 0002 | Dark-first, compact base theme | `proposed` | `proposed` (no change) | Core recommendation unchanged; implementation vehicle shifts from AntD Less generator → CSS custom properties + Tailwind density. Add reinterpretation note to ADR body. |
| 0007 | Neumorphic dual-shadow elevation | `proposed` | `proposed` (no change) | Core recommendation unchanged; implementation vehicle shifts from AntD shadow tokens → Tailwind `@theme` shadow scale. Add reinterpretation note. |
| 0010 | Drawer-in-drawer secondary view pattern | `proposed` | `proposed` (no change) | Core recommendation unchanged; `DrawerBuilder` reimplemented as styled Radix `Dialog.Content` wrapper. Add reinterpretation note. |
| 0015 | Config-driven clinical form engine | `proposed` | `proposed` (no change) | Core recommendation unchanged and framework-agnostic; `SubForm*` renderers reimplemented with Radix primitives + Tailwind. Add reinterpretation note. |

---

## References

- `frontend-v2/package.json` — production dependencies (Radix, Tailwind, Lucide, Recharts; no AntD)
- `frontend-v2/app/globals.css` — CSS custom properties dark/light theme, Tailwind `@theme` mapping
- `frontend-v2/app/layout.tsx` — `<html data-theme="dark">` root
- `frontend-v2/components/` — 7 components, all Radix + Tailwind
- `docs/adr/0001-frontend-stack-and-ui-library.md` — updated to `Status: accepted`, Option 2

---

*This document captures the ratified stack decision and serves as the reference for all dependent ADRs and implementation work in `frontend-v2/`.*
