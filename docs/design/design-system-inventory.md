# IntensiCare Design-System Inventory — legacy `trilhas-frontend`

**Source repo:** `trilhas-frontend` · **Pinned commit:** `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
**Status:** reference document for designers/engineers rebuilding the platform. The legacy frontend is visually strong and a candidate for revamp/reuse; this inventory records *what exists*, *why it probably exists*, and *what is broken or inconsistent*, so the new platform can make each decision deliberately.

---

## How to read this document

- **Everything here is derived from reading actual source** (`.tsx`/`.less`/`.ts`/`.json`/config) in the pinned commit, not from filenames. This is a consolidation of three independent auditor inventories (tokens `D-01`, components & IA `D-02`, clinical UX `D-03`), de-duplicated into one reference.
- **Citations.** Every material claim carries a citation of the form `trilhas-frontend:<path>:<lines>`. **All citations are against the single pinned commit `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`**; the `@ <commit>` suffix is omitted inline for readability but applies to every citation below.
- **"Legacy did X" ≠ "do X".** A finding being documented here is not an endorsement. Each section separates *observed behavior* from *assessment*. Decisions worth an Architecture Decision Record are cross-referenced as **→ ADR NNNN** (see the companion ADR set in `docs/adr/`); one-off styling quirks are recorded here in the inventory only.
- **Two colour systems, remember which is which.** The product has a *brand* colour system (tenant-overridable, `--primary-color`) and a *clinical severity* colour system (`statusTrilha`, static). They are unrelated by design. When you read "primary/orange," that is brand chrome; when you read "VERMELHO/AMARELO/severity," that is patient-safety colour. Conflating them is the single easiest way to reintroduce a bug.
- **Scale of the surface being described:** 463 `.ts`/`.tsx` files; 153 `.less` files totalling 4,888 lines; 117 top-level component directories (281 `.tsx`, 126 co-located `.less`); 27 routed pages. (`trilhas-frontend:src`, counts via `find`/`wc`.)

---

## Summary — the biggest findings

| # | Finding | Severity for rebuild | Where |
|---|---|---|---|
| 1 | **"Theming" is 5 stacked, independently-authored mechanisms** (build-time dark+compact AntD compile → stock-AntD light stylesheet layered over it → ~30 manual patch rules → ~23 per-component `.light` hex blocks → runtime per-tenant AntD recompile). Coheres today only through manual tuning; light-mode toggle requires a full page reload. | **Critical — do not port** | §1, §2.7 |
| 2 | **Clinical severity colour is the real design system, and it is untyped and reinvented 6–7 times.** `statusTrilha` (5 states × 6 shades) is the true semantic palette, decoupled from the declared AntD tokens; the same "green/amber/red" is re-encoded with divergent literals in ≥6 other places, plus two live severity bugs. | **Critical — patient safety** | §2.2, §5.1 |
| 3 | **No threshold/reference-range flagging of abnormal clinical values.** Vitals, labs, SOFA score, and fluid balance all render through a neutral label/value row with zero conditional styling. A SpO₂ of 99% and 60% look identical. Only one gauge (bed occupancy %) maps a number to colour. | **Critical — biggest clinical UX gap** | §5.2 |
| 4 | **No formal token scales.** Spacing, radius, elevation, z-index, motion, and type are 100% literal, freely mixing px/rem; ~340 raw colour-literal occurrences vs. 15 declared tokens (≈7:1 in `.less` alone). | High | §2 |
| 5 | **Fragmented real-time: the mission-critical bed board is the *least* live view.** Three unrelated channels — `setInterval` REST polling (bed board/dashboard), raw bidirectional WebSocket (notifications), Firestore `onSnapshot` (chat/presence) — with no shared reconnect/backoff. A red alert can appear in the bell instantly but take up to `tempo_atualizacao` seconds to appear on the grid. | **Critical — correctness/life-safety** | §6 |
| 6 | **Responsive behavior is JS-computed from `window.innerWidth`, not CSS.** Two "magic" breakpoints (`collapseRule=1260`, `collapseRuleMobile=800`) drive ~42 files; 33 distinct ad-hoc `@media` widths exist besides; three competing responsive strategies coexist, one with a dead-band bug on very large monitors. | High | §2.6, §4.4 |
| 7 | **The config-driven dynamic clinical form engine is the strongest reusable IP.** `FormDadosProntuario` renders 14 role-specific clinical forms from `dataForm*` config arrays via 10 typed field renderers. Worth preserving and modernizing. | Positive — preserve | §3.3 |
| 8 | **Per-tenant white-label branding is a real, validated need** implemented via a fragile mechanism (runtime Less recompilation by a third-party package + 2 CSS custom properties), with a flash-of-default-orange bug. | Medium — keep capability, replace mechanism | §1.3 |
| 9 | **Neumorphic ("soft UI") dual-shadow elevation is a genuine, distinctive visual signature** — applied inconsistently (dark/light asymmetry, copy-pasted per component, no elevation token). | Positive — preserve, formalize | §2.5 |
| 10 | **Governance debris throughout:** token file duplicated by hand and never imported, 5 of 15 tokens dead, `--warning-color` referenced but never defined, 3 dead components fully built, `.is-light` vs `.light` naming outlier, PWA manifest still named "teleUTI," route-level permission enforcement defaults *off*. | Medium | §7 |

---

## 1. Stack & theming foundation

### 1.1 Stack facts (verified)
Next.js 12 (pages router) + React 17 + Ant Design `^4.21.7` (pre-v5; Less-variable theming, no CSS-in-JS design tokens) + LESS via `next-plugin-antd-less` `^1.8.0`. Firebase 8 (Firestore only), `agora-rtc-react` (video), raw `websocket` (`w3cwebsocket`) client (notifications), `moment` + `moment/locale/pt-br`, `nookies` (cookie-based SSR auth), `next-pwa`. Locale is **PT-BR only** (`ConfigProvider locale={ptBR}`); no i18n scaffolding observed.
`trilhas-frontend:package.json:1-45`; `trilhas-frontend:.babelrc:1-13`; `trilhas-frontend:next.config.js:1-38`. **→ ADR 0001**

### 1.2 Base theme is permanently dark + compact, baked at build time
`next.config.js` wires the AntD official Less generator with the **dark** algorithm and **compact** density, then layers the 15 custom brand variables on top, producing **one compiled CSS bundle** shipped to every user regardless of preference or tenant:
```js
modifyVars: {
  ...getThemeVariables({ dark: true, compact: true }),
  ...variables,   // the 15 @primary-color etc. constants
}
```
`trilhas-frontend:next.config.js:1-38`. There is no build-time "light" or "comfortable" variant. The evident rationale (dark-first for dim ICU rooms, compact for data density) is sound but implicit — a config object nobody revisited. **→ ADR 0002**

### 1.3 Per-tenant white-label branding (why `--primary-color` exists)
The brand colour is **not fixed** — it is a per-company (`empresa`) setting. Each tenant configures its own primary colour via a native `<input type="color">` under an "Identidade Visual" form section, alongside a `whitelabel` field. `trilhas-frontend:src/components/FormEmpresa/FormEmpresa.tsx:92-101`. The stored value (`cor_primaria`, hex without `#`) is applied client-side by `changeColorTheme`, which does two things at once: (a) calls `changeAntdTheme(color)` from the third-party `dynamic-antd-theme` package (runtime AntD Less-variable **recompilation in the browser**), and (b) sets two CSS custom properties, `--primary-color` and `--primary-shadow-color` (`${color}2e`). `trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19`.

It is applied twice, causing a flash of the wrong brand colour: `_app.tsx` unconditionally applies the hardcoded default `#fe6d01` on mount (only when `isLight`), before any tenant data exists (`trilhas-frontend:src/pages/_app.tsx:36-40`); `PageContainer` then re-applies `#${data.cor_primaria}` once the tenant record loads (`trilhas-frontend:src/components/PageContainer/PageContainer.tsx:112-133`). `--primary-color` is consumed at **≥60 call sites** across `.less`, inline `style={}`, and icon `color` props. The only per-tenant customization surfaced anywhere is this single hex — no per-tenant typography, spacing, or logo-layout. **→ ADR 0004**

### 1.4 Theme mechanics summary
| Aspect | Mechanism |
|---|---|
| AntD version | `^4.21.7` (Less-variable theming) |
| Compile | `next-plugin-antd-less` `withAntdLess({ modifyVars })` + `.babelrc` `babel-plugin-import` per-component style imports |
| Base algorithm | `getThemeVariables({ dark: true, compact: true })` — baked at build time, not runtime-switchable |
| Brand overrides | 15 vars, merged into the same `modifyVars` object, **duplicated verbatim** in `styles/variables.less` (which the build never imports) |
| Runtime re-theming | `dynamic-antd-theme` `^0.8.7` — recompiles AntD colours client-side per tenant |
| Light theme | Not a build variant — a client-only stock-AntD-CSS overlay + manual patches + cookie flag (§2.7), full-reload to toggle |

*Full theming-stack detail (5 stacked mechanisms) is in §2.7 with the token analysis, since it is fundamentally a token-governance problem.*

---

## 2. Design tokens

### 2.1 Colour palette — the entire formal token set is 15 Less variables

There are exactly **15 Less variables** in the codebase, all in `variables.less`, plus 1 unrelated breakpoint variable in a page file. This is the complete formal token surface.

| Variable | Value | Role (inferred) | Live? |
|---|---|---|---|
| `@primary-color` | `#fe6d01` (orange) | Brand/action; AntD primary | ✅ (14 `.less` uses; also the runtime `--primary-color`) |
| `@secondary-color` | `#606060` | Secondary text/accents; unread-badge bg | ✅ |
| `@primary-color-shade` | `darken(@primary-color, 47%)` | Header/footer chrome (`SelectEmpresaAtual`) | ✅ (1 use) |
| `@background-color` | `#333` | Base surface (dark baseline) | ⚠️ not wired to any component read |
| `@success-color` | `#258a10` (green) | Success semantic | ⚠️ never referenced by name |
| `@info-color` | `#1a3bb7` (blue) | Info semantic | ⚠️ never referenced |
| `@default-color` | `#bbbbbb` | Neutral semantic | ⚠️ never referenced |
| `@danger-color` / `@error-color` | `#ff1633` (red, aliased) | Danger/error semantic | ⚠️ never referenced *by name* (literal recurs hardcoded) |
| `@warning-color` | `#d6a400` (amber) | Warning semantic | ⚠️ never referenced by name; `var(--warning-color)` expected at runtime but never set |
| `@skeleton-text` | `#eee3` | — | ❌ dead |
| `@degree` | `120deg` | (gradient util) | ❌ dead |
| `@grad-perc` | `-100%` | (gradient util) | ❌ dead |
| `@header-opacity` | `0.8` | — | ❌ dead |
| `@border-width` | `3px` | — | ❌ dead (real borders use unrelated literals) |

`trilhas-frontend:src/styles/variables.less:1-15`. The 5 dead tokens (`@skeleton-text`, `@degree`, `@grad-perc`, `@header-opacity`, `@border-width`) are confirmed by repo-wide grep — the only hit is the declaration line — and are most plausibly remnants of a removed conic/radial-gradient feature (`@degree`+`@grad-perc`). **→ ADR 0005**

**Two independently-maintained copies.** This exact 15-value set is duplicated value-for-value as a plain JS object inside `next.config.js` (`trilhas-frontend:next.config.js:5-21`), which is the *actual* build input; `variables.less` is **never `@import`-ed** by any `.less` file (verified), so it functions purely as an inert second copy. `next-plugin-antd-less`'s `modifyVars` needs a JS object at config time and cannot `@import` a `.less` file, which is why the values were copy-pasted — a genuine single-source-of-truth defect. **→ ADR 0005**

### 2.2 Two live colour systems (and the semantic tokens are *not* one of them)

Despite the declared `@success/@warning/@danger/@info/@default` tokens, the product's real colour semantics live in two other places:

**(a) Brand chrome — `--primary-color`** (tenant-overridable, §1.3): the only genuinely live, working colour token.

**(b) Clinical severity — `statusTrilha.ts`** (static JS literals, **the actual clinical design system**). Five named severity states, each with 6 pre-computed shades so consumers never compute contrast — they pick a shade key per context (border vs. fill vs. light-mode fill vs. dot). `trilhas-frontend:src/utils/statusTrilha.ts:1-45`:

| Key | `color` | `background` (dark) | `backgroundLight` | `ballColor` | `ballBackground` | `backgroundShade` |
|---|---|---|---|---|---|---|
| `NEUTRO` (calm) | `#5BCE85` | `#16302A` | `#E1FCE0` | `#00DC50` | `#08712E` | `#08712E1A` |
| `VERMELHO` (critical) | `#C54C5C` | `#412125` | `#FCE4DD` | `#FF1633` | `#740614` | `#7406141A` |
| `AMARELO` (caution) | `#cebc5a` | `#443f23` | `#fffadb` | `#ffd900` | `#726208` | `#7262081A` |
| `LARANJA` (caution-high) | `#F9A65A` | `#4A2B1F` | `#FFEDDD` | `#ff5900` | `#712B08` | `#7137081A` |
| `ASSISTIDO` (being handled) | `#4FBFE1` | `#04314A` | `#DCFDFB` | `#00B0FF` | `#0060A0` | `#0060A01A` |

`NEUTRO/VERMELHO/AMARELO/LARANJA` map to a clinical alert severity returned by the API (`ocupacao.alerta`, `trilha.alerta`, `mensagem.alerta`, `criterio.alerta`); `ASSISTIDO` is a manually-acknowledged state that **always overrides** the raw alert colour when `assistido === true`. Imported directly (not via any theme provider), typed `as any`, by 7 components: `InfoPacienteHeader`, `CollapseCard`, `DashboardCard`, `MessageBallon`, `FeedBallon`, `TabRecomendacoes`, `ItemNotificacao`. Consumed as inline `style={{ backgroundColor: statusTrilha[...] }}` rather than CSS classes. It is entirely independent of `--primary-color`: rebranding a tenant has **zero effect** on severity colours — which is arguably correct (patient-safety colours should not be brand-customizable) but is incidental, never documented or enforced. **→ ADR 0013**

### 2.3 Colour-literal sprawl (quantified)
Counted across all 153 `.less` files: **188** hex-literal occurrences (77 distinct values), plus 18 `rgb()/rgba()/hsl()` and 15 CSS named-colour keywords ≈ **221 raw colour literals in `.less`** vs. **31** uses of the 15 declared variables by name (`@primary-color` alone = 14) — a **≈7:1 literal-to-token ratio**. Add **119** inline hex literals in `.tsx`/`.ts` (headed by `"#fff"` 17×, `"#141414"` 14×, `"#000"` 8×) and the brand orange re-typed three ways (`"#fe6d01"` 3×, `"#ff6d00"` 1×, `"#ff5900"` 1×) — three near-identical oranges that cannot be grep-verified equal to `@primary-color`. **Total ≈340 raw colour literals vs. 15 tokens.**

There is **no light/dark surface-colour scale** (no `@surface-1/2`, `@bg-elevated`): every component re-declares its own literal pair, and the grays drift (`#141414` / `#1c1c1c` / `#191b25` / `#2a2a2a` all used as "dark surface" in different files). Top repeated `.less` literals, none mapped to a variable: `#212433` (13, dark elevated), `#141414` (12, dark base), `#f1f1f1` (11, light stripe/divider), `#fff` (10), `#2a2a2a` (8), `#fafafa` (7), `#323739` (7), `#f1f4fb` (6, light chip), `#434343` (6). Sources: `grep` over `trilhas-frontend:src` `.less`/`.tsx`/`.ts`. **→ ADR 0005, 0006**

### 2.4 Typography
- **Family:** single family, **Poppins**, loaded twice — correctly via a Google Fonts `<link>` in `_document.tsx` (weights 400/500/600 + italic 400) (`trilhas-frontend:src/pages/_document.tsx:16-27`), and again via a **malformed** `@font-face` in `globals.css` whose `src` points at the Google Fonts *CSS API endpoint* (a stylesheet, not a font binary) — dead/no-op code (`trilhas-frontend:src/styles/globals.css:33-38`). Global reset applies `font: 400 1rem "Poppins", sans-serif` to every element (`trilhas-frontend:src/styles/globals.css:24-31`). No fallback beyond `sans-serif`; **no monospace family anywhere** (relevant for tabular clinical values). *(Double-load is cleanup trivia → inventory only.)*
- **Root font-size (fluid rem base), a 3-step non-monotonic scale:** `html { font-size }` = `93.75%` at ≤1590px, `85.5%` at ≤1480px, `100%` at ≤1260px (`trilhas-frontend:src/styles/globals.css:1-17`). Because the cascade applies matching rules in source order, at ≤1260px **all three match and `100%` wins** — so the `85.5%` shrink only applies in the narrow 1261–1480px band. Very likely unintended; do not port as-is. **→ ADR 0006**
- **Font sizes:** no `@font-size-*` variables. A **20+-value unscaled ramp** in `.less` (`12px` ×14, `14px` ×6, `0.75rem` ×5, `16px` ×4, … down to `0.5625rem`) freely mixing px and rem, plus 45 inline `fontSize:` occurrences in `.tsx`. Because px does not scale with the responsive root-font zoom while rem does, the two families drift apart at different widths. `grep` over `trilhas-frontend:src`.
- **Weights:** only 4 in `.less` (`bold` ×9 as a keyword, `700`/`400`/`300` ×1 each); the loaded 500/600 weights appear only via AntD's own styles.
- **Line-height:** essentially undeclared (a single `line-height: 3.9` repo-wide); no scale. **→ ADR 0006**

### 2.5 Spacing, radii, borders, shadows, z-index, motion
- **Spacing:** no `@spacing-*` variables; 100% literal, mixing px/rem with an *implicit, never-codified* 4/8-multiple bias (e.g. padding `8px` ×11, `1rem` ×11, `0.5rem` ×6; margin-top `0.5rem` ×13, `margin 8px` ×12). An 8-point scale would fit almost all observed values with minimal visual change — a low-risk win.
- **Border-radius:** no variable; 13 distinct literals in 3 implicit clusters (small `8px`/`0.5rem`/`6px`/`10px`; card `16px`/`0.625rem`/`0.75rem`/`1rem`; circular `50%` ×17). Note the **unit inconsistency between equal values** (`8px`≡`0.5rem`, `10px`≡`0.625rem`, `12px`≡`0.75rem`) — direct evidence the scale was never centralized.
- **Border-width:** `@border-width: 3px` is dead; real borders use unrelated `1px`/`3px`/`4px`/`5px`.
- **Shadows — two coexisting visual languages:** 23 `box-shadow` declarations split between conventional **flat drop-shadows** (Material-style, e.g. `0px 1px 3px rgba(0,0,0,0.2)`) and **neumorphic dual-shadow pairs** (light+dark opposing offsets for an embossed "soft UI" look, declared per-component per-theme, e.g. dark `5px 5px 10px #0b0b0b, -5px -5px 10px #1d1d1d`). Applied **inconsistently**: some components keep the dual-shadow in both themes, others silently swap to a flat shadow in light mode (`ItemDefault`). No shared elevation token; each pair copy-pasted. `trilhas-frontend:src/components/ItemDefault/ItemDefault.less:8-9,18`. The neumorphic language is a genuine brand signature worth preserving. **→ ADR 0007**
- **Z-index:** no variable; 11 distinct literals (`1` ×10, `2` ×4, `99999` ×2 full-screen loading, `1031` ×2 nprogress, `9999`, `999`, …) — a classic "just be higher than whatever was highest nearby" arms race, no coherent scale.
- **Motion:** no duration/easing tokens; ad-hoc `0.2s`/`0.3s`/`0.4s`/`0.6s`/`1s`/`150ms` durations, plus keyframes `slide-in-top`/`slide-out-top` (`0.25s`) and `fadeIn` (`0.5s`) applied to `.page`. All one-off. `trilhas-frontend:src/styles/globals.less:55-68`.

All of the above are literal-only, no scale. **→ ADR 0006**

### 2.6 Breakpoints — two non-integrated systems
- **CSS `@media`:** 33 distinct widths from `324px`–`1590px`, **most appearing exactly once** (ad-hoc per component). Only meaningfully-repeated values: `768px` (12×), `1260px` (4×), `700px` (3×). `grep` over `trilhas-frontend:src` `.less`/`.css`.
- **JS-driven layout breakpoints (the dominant mechanism):** structural "mobile vs. desktop" switching is done in JS, not CSS, via a width-tracking hook compared against two exported constants used across ~42 files:
  ```ts
  export const collapseRule = 1260;
  export const collapseRuleMobile = 800;
  ```
  `trilhas-frontend:src/utils/constants.ts:5-6`. Pattern: `const [width] = useWindowSize(); const collapsed = useMemo(() => width < collapseRule, [width]);` (49 files import `useWindowSize`, 42 reference `collapseRule`). One lone Less breakpoint (`@collapse-rule: 1260px` in `Index.less`) duplicates the JS constant as a separate, drift-prone literal. This is "container-query-by-hand" via `window.resize` + React state, with SSR-hydration implications (`useWindowSize` needs a client mount before it knows real width). Three competing sub-strategies documented in §4.4. **→ ADR 0011**

### 2.7 Theme mechanics — the 5 stacked mechanisms
"Theme switching" is not one mechanism but **five independently-authored layers** that cohere today only through manual tuning:

1. **Build-time** single dark/compact/branded AntD compile (§1.2). One bundle for everyone.
2. **Light-mode overlay:** preference is a plain cookie (`theme.light`) read/written by `useLightTheme()`; toggling calls `window.location.reload()` — **no live switch, every toggle is a full reload** (`trilhas-frontend:src/hooks/useLightTheme.ts:1-23`). When `isLight`, `_app.tsx` dynamically mounts (`ssr:false`) a `LightTheme` component whose entire body is `require("./LightTheme.less")` — a component that renders nothing, existing only to inject a stylesheet (`trilhas-frontend:src/pages/_app.tsx:18-51`; `trilhas-frontend:src/themes/LightTheme.tsx:1-9`).
3. **`LightTheme.less` content:** a full re-import of the **stock, un-customized** `antd/dist/antd.css` (default light theme, standard density, default blue) layered over the dark/compact/orange bundle purely via cascade order, **plus ~30 hand-written patch rules** fixing what breaks (`#fff !important` card backgrounds, drawer padding resets, upload-dragger dims, skeleton widths). `trilhas-frontend:src/themes/LightTheme.less:1-115`.
4. **Per-component `.light` blocks:** 23 of 153 `.less` files hand-roll their own `&.light { … }` selector with hardcoded literal colour pairs; the `isLight` boolean is threaded down as a React prop through many trees to apply the `"light"` class (~30+ components branch on it). `trilhas-frontend:src/components/ItemDefault/ItemDefault.tsx:27-31`; `trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx:15-19` (hardcodes `"#434343"`/`"#fff"`/`"#eeeeee"`/`"#373737"` inline). **Naming outlier:** `ProtocoloSepseContent.less` uses `&.is-light` where all 43 other occurrences use `&.light` (`trilhas-frontend:src/components/ProtocoloSepseContent/ProtocoloSepseContent.less:18`).
5. **Runtime per-tenant recolor** via `dynamic-antd-theme` + the 2 CSS custom properties (§1.3), applied twice with a flash-of-default-orange.

This is expensive (a new component must remember its own `.light` block) and fragile (cascade-order dependent; no compile-time guarantee light CSS wins). **→ ADR 0003** (light overlay), **ADR 0002** (dark base), **ADR 0004** (runtime tenant colour).

- **Disconnected brand surfaces:** the PWA manifest colours are static and unrelated to any of the above (`theme_color:"#000000"`, `background_color:"#FFFFFF"`) and will not reflect a tenant's brand. The manifest product name is still **`"teleUTI"`** — a remnant of an earlier product identity. `trilhas-frontend:public/manifest.json`.
- **`--warning-color` is a live defect:** `Display.tsx` reads `var(--warning-color)` but no code ever sets it and no `:root` declares it — the property is permanently unset, so the "warning" text treatment silently falls back to the inherited colour. `trilhas-frontend:src/components/Display/Display.tsx:38-44`. **→ ADR 0005**

---

## 3. Component library

**117 top-level directories under `src/components`** (281 `.tsx`, 126 co-located `.less`), each typically `ComponentName.tsx` + `.less` + `index.tsx` barrel.

### 3.1 Icons — two coexisting systems, no shared sizing contract
1. **Material Design Icons** via `@mdi/js` path data, always wrapped by `MaterialIcon` (forces `size="1em"` + `anticon` class so MDI glyphs sit flush in AntD icon slots). Used in the overwhelming majority of files. `trilhas-frontend:src/components/MaterialIcon/MaterialIcon.tsx:1-19`.
2. **Bespoke hand-drawn SVG components** (`.jsx`, untyped) for domain concepts MDI lacks: clinical roles (`Enfermagem`, `Farmaceutico`, `Fisioterapeuta`, `Medico`, `Nutricionista`, `Psicologo`, `TecEnfermagem`, …), gender (`Masculino`/`Feminino`), config-menu icons, and decorative assets (`Logo`, `Waves`, `Ball`, `PdfIcon`). Each hardcodes its own `viewBox` and takes `size`/`color` — **no shared icon-sizing contract** between the two systems. `trilhas-frontend:src/icons/configs/EstabelecimentoIcon.jsx:1-37`. **→ ADR 0012**

### 3.2 Layout & wrapper primitives
| Component | Purpose | Adoption / note |
|---|---|---|
| `PageContainer` | The app shell (see §4.1) | 25 usages — the layout root |
| `DrawerBuilder` | Shared drawer scaffold: wraps AntD `Drawer`, custom X (native `closable={false}`), auto width `95vw`<`collapseRule` else `50vw`, standardized Salvar/Fechar footer, `destroyOnClose` | 16 call sites — **well-factored, preserve** |
| `DefaultCardWrapper` | AntD `Card` with fixed classes | 4 usages |
| `MobileCardWrapper` | Light/dark-aware card | **0 usages — dead code** |
| `ItemDefault` | Generic clickable list row (icon+title+desc+children), `isLight`-aware | 10 usages |
| `ListItem` | Minimal label/value row | 5 usages; used for all vitals/labs (§5.2) |
| `Display` | Read-view field: `Tag` list if array else text; `<></>` if falsy | across read-only clinical views; hosts the `--warning-color` bug |
| `DisplayCard` | Big clickable menu-tile (icon+title) | empresa/estabelecimento pickers |
| `SkeletonList` | N `Skeleton.Button` rows, or `Empty` if `errorMessage` | primary loading placeholder |
| `FadeLoading` | Full-viewport blocking spinner overlay | mutation loading (§5.4) |
| `AlertDelete` | `Alert type="warning"` banner + `Popconfirm` `danger` "Excluir" | **consistent destructive-confirm pattern, preserve** |
| `Ball` | Two-tone SVG dot (colour + darker ring) | severity/presence dot everywhere — **preserve** |
| `RenderTagTable` | Table cell as coloured left-border title or pill `Tag`, colour passed in | used in 8 admin column defs — see §5.2 |
| `HeaderForm` | Title bar inside every form/drawer | ubiquitous |

`trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99`; `…/AlertDelete/AlertDelete.tsx:1-49`; `…/icons/Ball.jsx:1-34`; `…/SkeletonList/SkeletonList.tsx:1-40`; `…/FadeLoading/FadeLoading.tsx:1-23`. **→ ADR 0010, 0012**

### 3.3 The dynamic clinical-form engine (`FormDadosProntuario`) — the most valuable IP
The single most structurally significant subsystem. It renders **arbitrary, config-driven clinical documentation forms**, not one hardcoded form per role:
- Entry point takes a `Models.DadosFormDinamico[]` **config array** (not markup) + `initialValues`, and supports a `nullStatus`/`nullifyFields` mechanism that nulls out whole sub-objects on submit when a group's "annul" switch is off (represents "this section doesn't apply to this patient"). `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:1-111`.
- `CollapsedFields` renders each config group as a `Collapse.Panel` (optional per-group "annulável" `Switch`), recursing into nested `subGroup`s (`SubGroupHandle`), a flat `campos` array (`SelectCampoType`), or a fully custom injected `Fieldset` component reference carried in the config. `trilhas-frontend:src/components/FormDadosProntuario/CollapsedFields/CollapsedFields.tsx:1-139`.
- `SelectCampoType` dispatches on `campo.type` ∈ `{string, select, interval, number, boolean, checkbox, data, list, masked, multicheck}` to **10 typed field renderers**. `trilhas-frontend:src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx:1-177`.
- **14 config files** instantiate the engine per role/screen: `dataFormEnfermagem`, `dataFormFisioterapeuta`, `dataFormFonoaudiologo`, `dataFormFormularioMedico`, `dataFormFarmaceutico`, `dataFormMusicoterapia`, `dataFormNutricionista`, `dataFormPsicologo`, `dataFormTecEnfermagem`, `dataFormPaciente`, `dataFormMovimentacao`, `dataFormRemovePaciente`, `dataFormIntercorrencia`, `dataFormBalancoHidrico`. `trilhas-frontend:src/utils/dataForms`. It backs the per-role "Evolução" menu, the bedside add/remove/move drawers, and the read-only "último prontuário" tab. New fields are added by editing schema objects, not JSX. **→ ADR 0015**

### 3.4 Static forms, filters, tables
- **Static `Form*` components** (`FormLeito/Setor/Grupo/Usuario/Estabelecimento/Empresa/Login/Prontuario`) share one shape: receive an AntD `FormInstance` from the parent (parent owns submit + `DrawerBuilder` chrome), render `Form.Item`s with a shared `defaultFormRules`, a `HeaderForm`, and a `mode: "in_page" | "modal"` prop toggling field `disabled` (view vs. edit). `trilhas-frontend:src/components/FormEstabelecimento/FormEstabelecimento.tsx:1-40`.
- **10+ `Filter*` components** all follow: plain AntD `Form layout="vertical"` with `onFilter`/`onClear`, rendered as `DrawerBuilder` content opened from a header filter button. `trilhas-frontend:src/components/FilterGestaoPacientes/FilterGestaoPacientes.tsx:1-68`.
- **Tables:** each entity has a `Colum(n)s*Table.tsx` exporting a plain `ColumnType<T>[]` array (not a component) with `responsive: ["xs"|"sm"]` per column and renderers delegating to `RenderTagTable`. `FooterPaginator` (AntD `Pagination`) reads from `PaginationContext` and cannot be used outside a `PaginationProvider`. `trilhas-frontend:src/components/FooterPaginator/FooterPaginator.tsx:1-35`.

### 3.5 Clinical/domain widgets (no generic AntD equivalent)
| Component | Renders | Key mechanic |
|---|---|---|
| `CollapseCard` (bed card) | Patient name/age/gender-icon, occupied/empty state, `statusTrilha`-coloured border+glow, `MicroIndicadores` row, per-trilha chips, camera/files/evolução actions | All colouring is **inline `style` from `statusTrilha`**; collapsed `11rem` ↔ expanded `50rem` via CSS animation, toggled globally by `collapseAll` (all-or-nothing). `trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:1-690` |
| `MicroIndicadores` | Tooltipped icon row: noradrenaline, mech. ventilation, sedation, hemodialysis, length-of-stay, expected mortality % | presentational; `color` from caller's `statusTrilha`. `…/MicroIndicadores/MicroIndicadores.tsx:1-90` |
| `TabRecomendacoes` | Per-bed tabbed panel: "Critérios" (left-tab-bar of trilhas, `Collapse` of recommendations, "Assistido" checkbox gated by `can_assist_ocupacao`) + read-only "Último prontuário" | custom `renderTabBar` colours buttons via `statusTrilha`. `…/TabRecomendacoes/TabRecomendacoes.tsx:1-353` |
| `TrilhaInterativa` | Accept/Refuse workflow for a protocol (string check `trilha.nome === "Sepse" \|\| "Profilaxia"`) | domain logic (protocol-name match) lives in the component. `…/TrilhaInterativa/TrilhaInterativa.tsx:1-245` |
| `Prescricao`/`HorarioCheck` | Medication administration: one row per scheduled dose, each checkable/editable/deletable | severity colours (§5.1). `…/Prescricao/Prescricao.tsx:1-149` |
| `BalancoHidrico*` | Fluid-balance entry + hourly grid overview | forked responsive trees (§4.4) |
| `DisplayVideoUti` | ICU bed camera via `<iframe src={cameraURL}>` to a separate microservice, client-side `blur(20px)` privacy toggle | not a native player; stream not stopped by blur. `…/DisplayVideoUti/DisplayVideoUti.tsx:1-71` |
| `BuildVideoChat`/`VideoCall` | Agora RTC telemedicine, Firestore presence roster | §6.4 |
| `MessagesList`/`MessageBallon`/`ChatSenderFooter` | Sector chat: REST history + Firestore-signaled refresh | §6.3 |
| `DisplayNotificaoes`/`ItemNotificacao` | Bell + drawer of push notifications | raw WebSocket, §6.2 |

### 3.6 Navigation/chrome primitives & parallel implementations
- `CircularMenu`: floating-action-button expanding a `Tooltip`-labeled stack via `translate3d`; used for page actions on the bed board (Filtrar/Expandir/Mensagens/Relatórios/Dashboard). `…/CircularMenu/CircularMenu.tsx:1-65`.
- **Two tab implementations coexist:** AntD `Tabs` (used for `TabRecomendacoes`, movement-history) **and** a bespoke `CustomTabs` (absolutely-positioned sliding-underline, manual `activeKey`, used only in `DrawerReacoes` + the inconsistências page). `…/CustomTabs/CustomTabs.tsx:1-98`. **→ ADR 0012**
- **Dead components (fully built, 0 usages):** `Breadcrumbs` (a real AntD `Breadcrumb` with UUID-aware path parsing — abandoned in favour of a bespoke header `Tag` trail, §4.2), `MobileCardWrapper`, `SideFixedButton`. `BottomDrawer` has exactly 1 usage.

---

## 4. Layout & information architecture

### 4.1 `PageContainer` — the app shell
The single layout root used by essentially every authenticated page. Responsibilities: AntD `Layout` with fixed `Header`/`Content`/`Footer`; **cascading data loading** — given `idEmpresa/Estabelecimento/Setor` route params, it independently REST-fetches empresa → estabelecimento → setor and exposes them via callbacks, i.e. **breadcrumb context is refetched by every page that mounts `PageContainer`, not read from a shared cache**; applies the tenant colour on empresa load (§1.3); renders the mobile hamburger `Drawer` (`width="70vw"`, `ItensMenuMobile`) when `width < collapseRule`; renders header actions (auto-reload `Switch`, `SwitchThemeButton`, `SelectEmpresaAtual`, `Tag` breadcrumb trail, notification bell, user/config/logout); renders a back-button + `Typography.Title` row (`setBacking(true)` flag + 200ms delay before `router.back()`); renders a static "iTech Ltda" footer with prod/homolog detection. **Blocks render** (`<LoadingAuth/>`) until `token && empresaAtual.id && !loading` — auth/tenant gating happens **client-side inside the layout**, not via SSR redirect. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:106-485`. **→ ADR 0008**

### 4.2 Navigation model — no persistent menu
There is **no persistent left/side nav and no AntD `Menu`** driving primary navigation. Navigation is entirely:
1. **Drill-down tile grids** — `DisplayCard`/`ListDashboard` (empresa → estabelecimento), `ItemDefault`/`ListItem` (settings tiles), each `onClick` → `router.push`.
2. **Header context switcher** (`SelectEmpresaAtual`, `ItensMenuMobile`) to jump between empresa/estabelecimento/setor without re-drilling.
3. **`CircularMenu` FAB** for page-level actions on the bed board.
4. A hand-built **`Tag` breadcrumb trail** in the header (estabelecimento/setor, each clickable) — functions as a breadcrumb but is bespoke; the real `Breadcrumbs` component is dead code. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:330-357`.
5. **Permission-filtered settings tiles** via `useMenuByPermissions` (boolean flags `can_manage_empresa/grupo_acesso/usuario` → `{route, nome, image}` tuples). `trilhas-frontend:src/hooks/useMenuByPermissions.tsx:1-111`.
**→ ADR 0009**

### 4.3 Route map (27 routed pages, one strict nested hierarchy)
```
/                                                            Login (FormLogin)
/empresa                                                     Company picker
/empresa/[id_empresa]                                        Establishments dashboard (ListDashboard)
  /feed                                                      Home-care social feed
  /relatorio-evolucao                                        Progress-note report builder
  /configuracoes                                             Settings menu (permission-filtered)
    /empresa /estabelecimentos /setores /leitos              CRUD lists
    /grupos , /grupos/[id_grupo]                             Access-group CRUD + detail
    /profissionais , /profissionais/[id_profissional]        Users CRUD + detail
  /estabelecimento/[id_estabelecimento]                      Sectors list
    /chats , /chats/[id_setor]/[id_usuario]                  Chat directory + 1:1 video call (Agora)
    /setor/[id_setor]                                        ★ ICU bed board (ListOcupacoes) — core screen
      /auditoria , /auditoria/[id_ocupacao]                  Audit trail
      /cameras                                               Camera grid
      /dashboard                                             Sector KPI dashboard
      /inconsistencias                                       Data-quality report + signature sub-report
      /leito/[id_leito]/ocupacao/[id_ocupacao]               Bed camera/video (DisplayVideoUti)
        /balanco                                             Fluid balance
        /prescricao                                          Medication administration
        /sepse/[id_trilha]                                   Sepsis protocol detail
```
`trilhas-frontend:src/pages/**/*.tsx`. **Auth gating:** every page's `getServerSideProps` calls `validateRoute(ctx)`, which checks the `trilhas.token`/`permissions`/`theme.light` cookies and redirects to `/` if no token. **Route-level permission enforcement is opt-in via an `ignorePermission` flag that defaults to `true` (i.e. off)** and no page was found overriding it — all real gating is client-side via `useEffectivePermissions` (button/menu visibility). `trilhas-frontend:src/hocs/validateRoute.ts:1-38`; `trilhas-frontend:src/hooks/useEffectivePermissions.tsx:1-28`. **→ ADR 0018**

### 4.4 Secondary views & responsive strategy
- **Drawer-in-drawer** is the standard secondary/tertiary-view pattern (no modal-routing/nested-route). `DrawerBuilder`s nest up to **2 levels deep** from one page (e.g. `OcupacoesPage` opens a chat drawer that conditionally renders a `TabRecomendacoes` drawer inside it); `ListOcupacoes` stacks 4 independent `DrawerBuilder`s off one list. Each page hand-wires its own boolean `visible` states and close handlers — no generic overlay-stack manager (no shared Esc/back/focus-trap handling). `trilhas-frontend:src/pages/.../setor/[id_setor].tsx:228-290`; `…/ListOcupacoes/ListOcupacoes.tsx:489-690`. **→ ADR 0010**
- **Three competing responsive sub-strategies:**
  - **(A) Single-tree class-toggling (dominant, ~42 files):** `useWindowSize()` → `collapsed = width < collapseRule` → toggle a class and/or branch small JSX/inline style. `PageContainer`, `DrawerBuilder`, `TabRecomendacoes`, `CollapseCard`, etc.
  - **(B) Forked component trees (rare, 1 confirmed):** `BalancoHidricoVisaoGeral` renders either `<GridView>` (hour×patient CSS grid) or `<MobileView>` (stacked cards) — two separate files, selected by `collapsed`, because information density genuinely differs. `trilhas-frontend:src/components/BalancoHidricoVisaoGeral/BalancoHidricoVisaoGeral.tsx:1-55`.
  - **(C) Ad-hoc per-page span buckets (independent of both):** `ListOcupacoes` computes an AntD `Col span` via a **5-bucket `if` chain over raw `window.innerWidth`** (`>2800→4`, `1800–2400→6`, `1260–1800→8`, `800–1260→12`, `<800→24`) that does **not** reuse `collapseRule` and does **not** use AntD's `xs/sm/md/lg/xl` grid props. **Bug:** the band `(2400, 2800]` matches no rule → `span` is `undefined` → full-width cards on very large monitors. `ListDashboard` reimplements a *different* bucket set one level up (`>1800→6`, `1260–1800→8`, `800–1260→12`, `<800→24`) — two near-identical grids hand-duplicated with drift. `trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:420-437`; `…/ListDashboard/ListDashboard.tsx:26-39`.
  - **Table density** (`size="small"` vs `"large"`, `scroll.y = calc(100vh - 350px)`) is chosen ad-hoc per screen, not from a density token — the audit/inconsistency tables are the highest-density view; fluid-balance tables the lowest. **→ ADR 0011**

---

## 5. Clinical UX patterns

### 5.1 Status colour-coding semantics (and its 6–7 divergent reinventions)
The dominant clinical semantic is the `statusTrilha` alert severity (§2.2), applied **consistently** to: patient-header border+glow (`InfoPacienteHeader`), bed-card border+glow+ball+gender-icon+age-badge (`CollapseCard`), dashboard-card border+glow+ball (`DashboardCard`), chat-message header (`MessageBallon`, keyed off the *bed's* alert), notification list item (`ItemNotificacao`), and recommendation tab buttons (`TabRecomendacoes`, correctly reading each trilha's own `alerta`).

But the same "green/amber/red" concept is **reinvented with divergent literals** in at least six other places — none importing `statusTrilha`:

| System | File | green | red | amber |
|---|---|---|---|---|
| Clinical severity (canonical) | `statusTrilha.ts` | `#00DC50` | `#FF1633` | `#ffd900`/`#ff5900` |
| Evolução record status | `handleIconByStatus.ts` | `#258a10` | `#ff1633` | (blue `#1890ff` for "liberado") |
| Prescription check tag | `HorarioCheck.tsx` `colorCheck` | `#389e0c` | (grey for suspended) | `#d4b105` |
| Prescription popover icon | `HorarioCheck.tsx` wrapper | `#acff76` | `#ff5252` | — |
| Sepsis-item delay flag | `ItemProtocoloSepse.tsx` | — | `#e84748` | — |
| Bed-occupancy gauge | `DashboardCard.tsx` | `#00DC50` | `#FF1633` | `#FFAB00` |
| Notification toast icon | `DisplayNotificaoes.tsx` | — | — | `#FFAB00` |

`trilhas-frontend:src/utils/handleIconByStatus.ts:1-23`; `…/Prescricao/HorarioCheck/HorarioCheck.tsx:60-138`; `…/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx:42-50`. The `handleIconByStatus` green (`#258a10`) is `@success-color` re-typed as a literal — the *only* place that token's value is reused, and it is reused by copy, not by import.

**Two concrete severity bugs to fix, not port:**
- **Notification toast is severity-blind:** the `notification.open()` toast icon is hardcoded amber `#FFAB00` regardless of alert severity — a VERMELHO (red) and an AMARELO (yellow) bed alert produce an identical amber toast; only the in-drawer list item reflects severity. `trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:73-96`.
- **Criteria panel hard-codes `"VERMELHO"`:** immediately below the correctly-dynamic tab buttons, `TabRecomendacoes` styles the recommendation panel background with a literal `statusTrilha["VERMELHO"]` — every criteria panel, at every severity, renders red-tinted. Same feature, correct one component up, ignored one component down. `trilhas-frontend:src/components/TabRecomendacoes/TabRecomendacoes.tsx:213-231`.
- **Occupancy gauge near-miss:** `DashboardCard`'s occupancy % maps `>70%→red`, `>50%→amber`, else green; its red/green match `statusTrilha` exactly but its amber (`#FFAB00`) silently differs from `statusTrilha.AMARELO` (`#ffd900`) — the exact accidental drift a token system prevents. (The same card's alert-count stacked bars *do* import `statusTrilha` correctly.) `trilhas-frontend:src/components/ListDashboard/DashboardCard/DashboardCard.tsx:291-392`.
- **Sepsis completion uses shape-only encoding:** `concluida`→`mdiCheck`, `finalizado`→`mdiClose`, both in default/inherited colour — the one status in the app with no colour differentiation, inconsistent with everywhere else. `trilhas-frontend:src/components/ProtocoloSepseContent/ProtocoloSepseContent.tsx:68-90`.

Empty beds (`leito.ocupado === false`) get a flat neutral border (`#212433`) — visually a "calm" state, indistinguishable at a glance from a `NEUTRO` occupied bed except by content. **→ ADR 0013**

### 5.2 The biggest gap — no threshold/abnormal-value flagging
**There is essentially no threshold-based visual flagging of abnormal clinical values anywhere.**
- **Vitals** (`ItemSinaisVitais`): HR, RR, BP, temp, SpO₂, HGT, ventilation mode, O₂ flow, FiO₂, consciousness, pain — all 15 fields render through the same neutral `ListItem` with **no conditional styling**. A SpO₂ of 99% and 60% render identically. `trilhas-frontend:src/components/BalancoHidricoItens/ItemSinaisVitais/ItemSinaisVitais.tsx:29-127`.
- **Labs/assistive** (`InformacoesAssistenciais`): BP, RASS, Glasgow, delirium, diuresis, fluid balance, temp, leukocytes, platelets, CRP, **lactate**, pH, bicarbonate, pO₂, pCO₂, **P/F ratio**, creatinine, urea, bilirubin — every one (several classic sepsis/deterioration markers) shown via neutral `ListItem`, no colour/icon/bolding by range. `trilhas-frontend:src/components/InformacaoesAssistenciais/InformacoesAssistenciais.tsx:1-171`.
- **24h indicators** (`ItemIndicadores24h`): fluid balance, diuresis, HGT, temp max — plain `ListItem`, no thresholding.
- **Fluid-balance grid** (`GridView`): every non-zero cell gets a fixed green pill (`#42e26f`) purely to signal "a value exists here" — a large intake and an extreme output look identical; no positive/negative split, no out-of-range flag. `trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx:81-96`.
- **SOFA score** (a validated ICU mortality-risk score) always renders with AntD `"warning"` tag colour whether it is 0 or 20+. No band escalation. `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:85-94`.
- **The tell:** `RenderTagTable` is a per-cell colour-injection primitive that *looks* built for critical-value severity, but in all 8 call sites the `color` argument is the literal `"var(--primary-color)"`, and none of those 8 tables is clinical (they are admin listings). The two clinically relevant tables (`ColumnsEntrada`/`ColumnsSaida`) don't use it at all. Someone built the mechanism and never wired thresholds. `trilhas-frontend:src/components/RenderTagTable/RenderTagTable.tsx:1-39`.
- **Where "critical" flagging *does* exist:** presence-based only — invasive-procedures badge (amber `#d6a400` when `procedimentos_invasivos.length > 0`), sepsis first-hour delay (red `#e84748`), and the single numeric-to-colour gauge (bed occupancy %, §5.1). **→ ADR 0014**

### 5.3 Clinical form UX
- **Schema-driven engine** (§3.3) backs every clinical data-entry form.
- **"Multi-step" is simulated, never a wizard** — no AntD `Steps` anywhere (grep = 0). The multi-step feel comes from three uncoordinated mechanisms: accordion sections (`CollapsedFields`, groups as `Collapse.Panel`), tabs inside a drawer (movement history vs. new entry), and sequential drawers (choose evolução type → specific form). `trilhas-frontend:src/components/FormDadosProntuario/CollapsedFields/CollapsedFields.tsx:32-38`.
- **Conditional fields — three different mechanisms, no shared abstraction:** (1) group-level "nullify" `Switch` (fields stay mounted/interactive; only the *submitted* value is nulled via `nullifyFields`); (2) sub-group "checavel" `Switch` (`display:none/block`, fields stay mounted to preserve `Form` state); (3) permission/tenant-type field disabling (e.g. `FormLeito` disables name/code unless `empresaData.tipo === "manual"`, hides camera-IP unless `can_manage_camera`). `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:36-54`; `…/SubGroupHandle/SubGroupHandle.tsx:32-91`; `…/FormLeito/FormLeito.tsx:42-66`. **→ ADR 0015**

### 5.4 Feedback & loading
- **One universal error surface:** `handleApiError` always renders `Modal.error` (AntD red chrome) regardless of whether the failure is validation, permission, or server fault — **no warning/error/info differentiation by type/status code**. Field-level validation issues render as a flat list of `Tag color="warning"` with a fixed `mdiAlertDecagram`. It assumes a **Django-REST-Framework-shaped** error body (`error.errors: Record<string, string|string[]|NestedIssue[]>`) and is called individually from nearly every REST `catch` block (not centralized in the HTTP client). `trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103`. **→ ADR 0016**
- **Two loading affordances, chosen per-screen with no documented rule:** skeleton rows (`SkeletonList`, generic rounded bars not shaped to content — used for initial list/page loads) vs. a **full-screen blocking spinner** (`FadeLoading`, fixed translucent overlay blocking all interaction — used for most mutations). The full-screen block is heavy-handed for a clinical tool where staff may need to keep working elsewhere on screen. `trilhas-frontend:src/components/FadeLoading/FadeLoading.tsx:1-23`. **→ ADR 0016**

---

## 6. Data flow & real-time architecture

### 6.1 State & REST
- **Auth** is a single global React Context (`AuthProvider`): re-verifies the token against `/verify-token/` on every mount, pulls all permissions, `logout()`s on refresh failure; `signIn()` posts `/login/`, sets the `trilhas.token` cookie (30-day maxAge), and routes to `/empresa/{id}` if the user has exactly one company else the picker. Auth state (`user`, `permissions`, `empresaData`) is one global context — **no query cache, no react-query/SWR** — so every consumer re-renders on any change and there is no request de-dup/staleness model. `trilhas-frontend:src/contexts/AuthContext/AuthContext.tsx:1-193`; `trilhas-frontend:package.json:18-40`.
- **REST layer:** 19 resource files (`empresas`, `estabelecimentos`, `setor`, `leito`, `ocupacao`, `usuario`, `mensagens`, `prescricao`, `balancoHidrico`, `inconsistencias`, `feed`, `dashboard`, `arquivos`, `grupos`, `indicadores`, `evolucao`, `permission`, `trilhaInterativaSepse`), each exporting `useCallback`-memoized `useGetX/usePostX/…` wrappers around one shared axios instance, hitting paths built from empresa/estabelecimento/setor IDs. `trilhas-frontend:src/hooks/networking/setor.ts:1-181`.
- **Pagination:** `createPagination({cleanPage, defaultFilters})` is a **factory manufacturing a fresh Context+Provider pair per call site** (not one shared context); the provider owns `page`/`filters`/`paginator` and auto-fetches on mount. `trilhas-frontend:src/contexts/PaginationContext/PaginationContext.tsx:1-133`.
- **File uploads** go through a **base64-encode-then-POST** pipeline (`FileB64Convert`, `ImagePicker`, `FilePicker`), not direct-to-object-storage signed uploads — simplest single-backend integration, but inflates payload ~33% and routes binary through the app server. **→ ADR 0018**

### 6.2 Three independent real-time channels — no shared abstraction
1. **Raw WebSocket (notifications):** `DisplayNotificaoes` opens **two** `w3cwebsocket` connections to `${baseWsURL}notificacao/?token=…` — one for the list, one (`&popover=true`) purely to fire a `notification.open()` toast (debounced 2s). Marking-as-read sends `{evento:"visualizar", visto:true, id}` back over the same socket, i.e. **the socket is bidirectional and doubles as a mutation channel**. No reconnect/backoff; `ws.onerror` just logs. `trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:1-133`.
2. **Firestore (`onSnapshot`) — signaling/presence only, never system-of-record:** every Firestore access targets one doc shape, `chats/{setorId}/usuarios/{usuarioId}`. `MessagesList` reads it only to know *when to re-run the REST message fetch* and to zero an unread counter — **chat history itself is paginated REST**. The same doc carries `qtd_mensagens` (unread badge) and `online_call: boolean` (video-room presence, filtered `where("online_call","==",true)`). No other Firestore path exists. A deliberate, narrow "presence/signal" layer over a REST-of-record backend. `trilhas-frontend:src/hooks/Firestore/useCollection.tsx:1-77`; `…/MessagesList/MessagesList.tsx:332-348`. **→ ADR 0017**
3. **`setInterval` REST polling — the mission-critical bed board:** both the establishment dashboard and `ListOcupacoes` poll via `setInterval(applyFilters, tempo_atualizacao*1000)`, gated by an app-wide `AutoReloadContext.update` flag (header `Switch`), with the interval a **per-tenant business setting** (`empresa.tempo_atualizacao`). **Despite Firebase being a dependency, bed/vitals/alert state is never pushed** — it is REST-polled. So the primary ICU grid does **not** react to the alert WebSocket that drives the bell; a new red alert can take up to `tempo_atualizacao` seconds to reach the grid while showing near-instantly in the toast — the two live views of the same event can visibly disagree. `trilhas-frontend:src/contexts/AutoReloadContext/AutoReloadContext.tsx:1-22`; `…/ListOcupacoes/ListOcupacoes.tsx:112-141`. **→ ADR 0017**

### 6.3 Video (two distinct technologies, a reasonable separation)
- **Passive ICU monitoring:** `DisplayVideoUti` `<iframe>` embed of a separate camera microservice (`NEXT_PUBLIC_CAMERA_URL`), with a client-side `blur(20px)` privacy toggle (visual mask only — stream not stopped). `trilhas-frontend:src/components/DisplayVideoUti/DisplayVideoUti.tsx:17-68`.
- **Active telemedicine:** `BuildVideoChat`/`VideoCall` use Agora RTC (`agora-rtc-react`), gated by a `hasVideoDevice` check (falls back to an AntD `Result status="warning"` "Video Offline"), with Firestore presence and a `useSendIndicator("entrada_videochamada")` REST audit event on join. `trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:1-155`. **→ ADR 0018** (camera boundary).

---

## 7. Inconsistencies & dead code (consolidated)

| Finding | Evidence | Class |
|---|---|---|
| Token file duplicated verbatim (`variables.less` vs. `next.config.js`), never imported by the build | `variables.less:1-15` vs `next.config.js:5-21` | governance |
| 5 of 15 tokens dead (`@skeleton-text`, `@degree`, `@grad-perc`, `@header-opacity`, `@border-width`) | grep = declaration line only | dead token |
| `--warning-color` referenced (`Display.tsx`) but never set anywhere | `Display.tsx:38-44` | live defect |
| `statusTrilha` (the real severity system) typed `as any`, never in the token file, consumed via inline styles | `statusTrilha.ts:1-45` | typing/governance |
| Severity "green/amber/red" reinvented as 6–7 divergent literal sets; 2 severity bugs (toast severity-blind; criteria panel hard-codes VERMELHO) | §5.1 | duplication + bug |
| Non-monotonic root font-size cascade (85.5% shrink negated ≤1260px) | `globals.css:1-17` | quirk |
| Poppins loaded twice; the `@font-face` `src` points at a CSS URL (dead) | `globals.css:33-38` | dead code |
| `.is-light` naming outlier (43× `.light` vs 1× `.is-light`) | `ProtocoloSepseContent.less:18` | naming |
| Two tab implementations (AntD `Tabs` + bespoke `CustomTabs`) | §3.6 | duplication |
| Two icon systems, no shared sizing contract (MDI wrapper + bespoke SVG) | §3.1 | duplication |
| Two "unread count" badge treatments (AntD `Badge` vs hand-rolled circular div) | `DashboardCard` §6.5-equiv | duplication |
| Dead components fully built: `Breadcrumbs`, `MobileCardWrapper`, `SideFixedButton` | grep = 0 usages | dead code |
| `ListOcupacoes` span dead-band `(2400,2800]` → `undefined` → full-width on huge monitors | `ListOcupacoes.tsx:420-437` | bug |
| Two near-identical responsive card grids hand-duplicated with drift (`ListOcupacoes` vs `ListDashboard`) | §4.4 | duplication |
| Three real-time channels, no shared reconnect/backoff | §6.2 | architecture risk |
| Route-level permission enforcement defaults `ignorePermission=true` (off); no page overrides | `validateRoute.ts:1-38` | security posture |
| PWA manifest still named `"teleUTI"`; manifest colours disconnected from theme/tenant | `public/manifest.json` | brand provenance |
| Theme toggle requires full `window.location.reload()` | `useLightTheme.ts:12-18` | UX |

---

## 8. Quick reference — preserve vs. replace

**Preserve (the genuinely good bones):**
- Dark-first, compact default (ICU-appropriate) — as an *explicit* decision, not a config side-effect. (§1.2 → ADR 0002)
- The **two-tier colour separation** (immutable clinical severity vs. tenant-overridable brand) — but make both governed, typed tokens. (§2.2 → ADR 0013)
- The **config/schema-driven dynamic clinical form engine** — the strongest reusable IP. (§3.3 → ADR 0015)
- **Neumorphic elevation** as a brand signature — via a proper elevation-token pair. (§2.5 → ADR 0007)
- Well-factored primitives: `DrawerBuilder`, `AlertDelete`, `Ball`, `MaterialIcon`. (§3.2 → ADR 0010, 0012)
- Per-tenant white-label *capability* (§1.3 → ADR 0004); Firestore-out-of-record *principle* (§6.2 → ADR 0017).

**Replace (do not port as-is):**
- The 5-layer theming stack + full-reload light mode (§2.7 → ADR 0003).
- Runtime Less recompilation via `dynamic-antd-theme` (§1.3 → ADR 0004).
- Literal-everywhere tokens; introduce spacing/radius/elevation/z/motion/type scales (§2 → ADR 0006).
- JS-`window.innerWidth` responsive strategy with 3 competing variants (§4.4 → ADR 0011).
- Polling the mission-critical bed board; unify real-time transport (§6.2 → ADR 0017).
- The "no abnormal-value flagging" baseline — this is a gap, not a considered choice (§5.2 → ADR 0014).

---

*End of inventory. Companion ADR set (foundations → components/layout → clinical UX → data-flow/real-time) lives in `docs/adr/`.*
