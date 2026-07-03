# D-01 — Design Token Inventory: `trilhas-frontend` (legacy)

**Repo:** trilhas-frontend @ `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
**Scope:** color palette, typography, spacing/sizing, borders/radii/shadows, breakpoints, z-index, light/dark theme mechanics, Ant Design customization approach, token-sprawl quantification.
**Method:** every claim below is derived from reading actual source (`.less`, `.tsx`, `.ts`, `package.json`, `next.config.js`, `.babelrc`) in the pinned commit — not from file/variable names alone. All citations use `trilhas-frontend:path:line-range @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

Scale of the legacy stylesheet surface: 153 `.less` files, 4,888 total `.less` lines, 463 `.ts`/`.tsx` files (`trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`, file-count/line-count derived via `find`/`wc`).

---

## 1. Color palette

### 1.1 Declared Less variables (the *entire* formal token set)

There are exactly **15 Less variables** declared in the codebase, all in one file, plus **1 unrelated breakpoint variable** in a page file. This is the complete formal "design token" surface — nothing else is named/tokenized.

| Variable | Value | Purpose (inferred from usage) |
|---|---|---|
| `@primary-color` | `#fe6d01` (orange) | Brand/action color; AntD primary |
| `@secondary-color` | `#606060` (gray) | Secondary text/accents |
| `@primary-color-shade` | `darken(@primary-color, 47%)` → derived dark brown | Header/footer chrome background (`SelectEmpresaAtual`) |
| `@background-color` | `#333` | Base surface color (dark baseline) |
| `@success-color` | `#258a10` (green) | Success/positive semantic |
| `@info-color` | `#1a3bb7` (blue) | Info semantic |
| `@default-color` | `#bbbbbb` (gray) | Neutral/default semantic |
| `@danger-color` | `#ff1633` (red) | Danger semantic |
| `@error-color` | `@danger-color` (alias) | Error semantic (= danger) |
| `@warning-color` | `#d6a400` (amber) | Warning semantic |
| `@skeleton-text` | `#eee3` (4-digit hex, translucent gray) | *(declared, unused — see §7)* |
| `@degree` | `120deg` | *(declared, unused — see §7)* |
| `@grad-perc` | `-100%` | *(declared, unused — see §7)* |
| `@header-opacity` | `0.8` | *(declared, unused — see §7)* |
| `@border-width` | `3px` | *(declared, unused — see §7)* |

Source: `trilhas-frontend:src/styles/variables.less:1-15 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

**This exact same list is duplicated, value-for-value, as a plain JS object inside `next.config.js`** (see §6) — `styles/variables.less` is never `@import`-ed by any other `.less` file in the repo (verified: `grep -rn "@import.*variables" src` returns nothing), so it functions purely as a second, independently-maintained copy of the same 15 constants, not as the source feeding the build.
Source: `trilhas-frontend:next.config.js:5-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

Only 1 additional Less variable exists anywhere else in the tree: `@collapse-rule: 1260px;`, a breakpoint local to one page file (see §5).
Source: `trilhas-frontend:src/pages/Index.less:1 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

### 1.2 Color-literal sprawl vs. variable usage (quantified)

Counted via `grep -rEoh` over all 153 `.less` files:

| Metric | Count |
|---|---|
| Total hex-color literal **occurrences** in `.less` (`#rgb`/`#rgba`/`#rrggbb`/`#rrggbbaa`) | **188** |
| Distinct hex-color literal **values** in `.less` | **77** |
| `rgb()`/`rgba()`/`hsl()` literal occurrences | **18** (11 distinct) |
| CSS named-color keyword occurrences (`white/black/red/blue/...`) | **15** |
| **Total raw color-literal occurrences in `.less`** | **≈221** |
| Occurrences of the 15 declared `@color` variables *by name*, across all `.less` (any file) | **31** (`@primary-color` alone = 14; the other 8 semantic vars = 10 combined; the 5 dead vars = 0 real usages beyond their own declaration) |
| **Ratio of literal color usages to variable usages in `.less`** | **≈7:1** |

Additional sprawl outside `.less`: **119** inline hex-literal color occurrences inside `.tsx`/`.ts` files (style props / JS objects), headed by `"#fff"` (17×), `"#141414"` (14×), `"#000"` (8×), `"#a6a6a6"` (7×), and the brand orange re-typed 3 separate ways: `"#fe6d01"` (3×), `"#ff6d00"` (1×), `"#ff5900"` (1×) — three near-identical oranges that are not the same literal string as `@primary-color` and therefore cannot be grep-verified to match it.
Source: `grep -rEoh '"#[0-9a-fA-F]{3,8}"' src --include="*.tsx" --include="*.ts"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

Counting `.less` + `.tsx`/`.ts` together: **≈340 raw color-literal occurrences vs. 15 declared tokens** — token sprawl is severe and total-brand-color consistency cannot be verified by inspection (e.g. no shared constant guarantees `"#fe6d01"` in a `.tsx` file equals `@primary-color` in a `.less` file besides manual discipline).

Top repeated hex literals in `.less` (frequency ≥ 5), none of which map to a declared variable:

| Literal | Count | Likely role |
|---|---|---|
| `#212433` | 13 | dark-mode elevated surface |
| `#141414` | 12 | dark-mode base surface / text-on-light |
| `#f1f1f1` | 11 | light-mode striped-row / divider |
| `#fff` | 10 | light-mode surface |
| `#2a2a2a` | 8 | dark-mode surface variant |
| `#fafafa` | 7 | light-mode surface variant |
| `#323739` | 7 | dark-mode surface variant |
| `#f1f4fb` | 6 | light-mode chip background |
| `#434343` | 6 | dark-mode border/shadow |

Source: `grep -rEoh '#[0-9a-fA-F]{3,8}\b' src --include="*.less" | sort | uniq -c | sort -rn` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

**Interpretation:** there is no light/dark surface-color *scale* (no `@surface-1`, `@surface-2`, `@bg-elevated`, etc.). Every component that needs a "dark card" vs. "light card" background re-declares its own literal pair (see §4, the `.light` class pattern), and the specific grays chosen drift slightly component to component (`#141414` vs `#1c1c1c` vs `#191b25` vs `#2a2a2a` all used as "dark surface" in different files).

### 1.3 Clinical/status-severity colors bypass the semantic tokens

Despite `@success-color`, `@warning-color`, `@danger-color`/`@error-color`, `@info-color`, `@default-color` being declared, safety-relevant status indicators in the clinical UI define their **own** ad hoc literal colors instead of using them:

- Medication-administration status chip (`HorarioCheck`, used in the prescriptions/MAR flow): suspended → `#CCCCCC`/AntD preset `"grey"`; administered → `#389e0c`/preset `"green"`; not-administered-with-reason → `#d4b105`/preset `"yellow"`; default/pending → `#25979c`/preset `"cyan"`. None of these match `@success-color` (`#258a10`), `@warning-color` (`#d6a400`), or `@danger-color` (`#ff1633`).
  Source: `trilhas-frontend:src/components/Prescricao/HorarioCheck/HorarioCheck.tsx:124-134 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
- The login-screen illustration gradient uses yet another orange pair, `#f84a32 → #fcc153`, distinct from `@primary-color` (`#fe6d01`).
  Source: `trilhas-frontend:src/pages/Index.less:17 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

This is the single highest-priority finding for the new platform: **clinical severity semantics (medication given/missed/suspended, presumably vitals thresholds elsewhere) are encoded as scattered literals/AntD preset names, not as a governed severity token scale** — a real risk for consistency and for accessible color contrast in an ICU monitoring product.

### 1.4 Runtime CSS custom properties (a second, parallel color-token system)

Separate from the Less variables, the app defines and consumes exactly **2 CSS custom properties** at runtime: `--primary-color` and `--primary-shadow-color`. These are set imperatively via `document.documentElement.style.setProperty(...)` (not declared in any `:root` block as a static fallback) and then consumed via `var(--primary-color)` in **≥60 call sites** across `.less` files, inline `style={}` objects, and icon `color` props.
Source (setter): `trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
Source (representative consumers): `trilhas-frontend:src/styles/globals.css:30,50,76,94,117-118 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; `trilhas-frontend:src/hooks/useEvolucaoMenu.tsx:67-352 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (8 occurrences); `trilhas-frontend:src/components/PageContainer/PageContainer.less:77 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

`var(--warning-color)` is referenced once (`Display.tsx`) but **`--warning-color` is never set anywhere** (no JS setter, no `:root` fallback) — this is a live defect: the property is undefined at runtime, so the `color`/style consuming it silently falls back to the CSS initial value rather than an intentional warning color.
Source: `trilhas-frontend:src/components/Display/Display.tsx:40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (sole reference; confirmed absent elsewhere via repo-wide grep).

### 1.5 Per-tenant white-label branding (the real reason `--primary-color` exists)

The brand color is **not fixed** — it is a per-company (multi-tenant) setting fetched from the backend and applied client-side. Each tenant ("empresa") configures its own primary color via a native `<Input type="color">` under a "Identidade Visual" (Visual Identity) form section, alongside a `whitelabel` identifier field:
Source: `trilhas-frontend:src/components/FormEmpresa/FormEmpresa.tsx:92-101 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

The stored value (`cor_primaria`, hex without `#`) is applied on every page load in two places:
1. `_app.tsx` unconditionally applies the **hardcoded default** `#fe6d01` on mount, before any tenant data is available (flash-of-default-brand-color).
   Source: `trilhas-frontend:src/pages/_app.tsx:36-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
2. `PageContainer` re-applies the color a second time once the tenant record loads, via `changeColorTheme(`#${data.cor_primaria}`)`.
   Source: `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:112-133 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

`changeColorTheme` does two things simultaneously: (a) calls `changeAntdTheme(color)` from the third-party `dynamic-antd-theme` package (runtime AntD Less-variable recompilation), and (b) sets the two CSS custom properties in §1.4.
Source: `trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

This means the true color-theming model is **3 disconnected layers** (build-time Less vars → runtime AntD recompilation via 3rd-party lib → manual CSS custom properties + ~150 literal-color call sites that never got wired to any of the above). See §6 for the full theming-stack narrative.

### 1.6 Disconnected brand-color surfaces

- PWA manifest colors are static and unrelated to any of the above: `theme_color: "#000000"`, `background_color: "#FFFFFF"` — will not reflect a tenant's brand color in the OS task-switcher/splash screen.
  Source: `trilhas-frontend:public/manifest.json @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (no line numbers; JSON file, keys `theme_color`/`background_color`).
- The manifest's product name is `"teleUTI"`, not "trilhas" or "IntensiCare" — a naming remnant from an earlier product identity, worth noting for brand-asset provenance in the new platform.
  Source: `trilhas-frontend:public/manifest.json @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

---

## 2. Typography

### 2.1 Font family

Single font family, Poppins, loaded **twice, in two different and partially conflicting ways**:

1. Correctly via a Google Fonts stylesheet `<link>` in `_document.tsx`, requesting weights 400/500/600 (roman) + 400 (italic):
   `https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,500;0,600;1,400&display=swap`
   Source: `trilhas-frontend:src/pages/_document.tsx:16-27 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
2. A second, **malformed** `@font-face` declaration in `globals.css` that points `src: url(...)` at the *Google Fonts CSS API endpoint itself* (a stylesheet, not a font binary) rather than an actual `.woff2` file — this declaration cannot function as intended (browsers require `src` to reference an actual font resource, not a CSS document) and is effectively dead/no-op code, redundant with (1):
   ```css
   @font-face {
     font-family: "Poppins";
     src: url('https://fonts.googleapis.com/css2?family=Poppins:ital@1&display=swap');
     font-weight: 400;
     font-style: italic;
   }
   ```
   Source: `trilhas-frontend:src/styles/globals.css:33-38 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

Global reset applies the family + a default size/weight to literally every element:
```
* { margin: 0; border: 0; box-sizing: border-box; font: 400 1rem "Poppins", sans-serif; ... }
```
Source: `trilhas-frontend:src/styles/globals.css:24-31 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

No fallback stack beyond `sans-serif`; no monospace family anywhere in the codebase.

### 2.2 Root font-size (fluid rem base) — a 3-step, non-monotonic responsive scale

`globals.css` resizes the **root** `html` font-size at breakpoints, which rescales every `rem` value app-wide. The declaration order is non-monotonic (smaller breakpoint resets *larger* than the mid breakpoint), which is a real quirk to note:

| Media condition | `html { font-size }` |
|---|---|
| `max-width: 1590px` | `93.75%` |
| `max-width: 1480px` | `85.5%` |
| `max-width: 1260px` | `100%` (back to full size — narrower than 1480px but *larger* font than the 1480px rule) |

Source: `trilhas-frontend:src/styles/globals.css:1-17 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

Because CSS cascade applies all matching rules in source order, at viewport widths ≤1260px **all three** rules match and the last one (`100%`) wins — meaning the `85.5%` shrink only actually applies in the narrow band `1261px–1480px`. This is very likely an unintended interaction rather than a deliberate design, and should not be ported as-is.

### 2.3 Font sizes in use (no defined scale — literal values only)

No `@font-size-*` Less variables exist. Observed literal `font-size` values across `.less` (occurrence counts):

| Value | Count | | Value | Count |
|---|---|---|---|---|
| `12px` | 14 | | `2rem` | 3 |
| `14px` | 6 | | `0px` | 3 |
| `0.75rem` | 5 | | `18px` | 2 |
| `16px` | 4 | | `10px` | 2 |
| `8px` | 3 | | `0.9rem` | 2 |
| `9px` | 1 | | `90%` | 1 |
| `3.75rem` | 1 | | `13px` | 1 |
| `1.3rem` | 1 | | `1.15rem` | 1 |
| `0.78rem` | 1 | | `0.625rem` | 1 |
| `0.5625rem` | 1 | | `1rem` | 2 |

Source: `grep -rhoE "font-size:\s*[0-9.]+(px|rem|em|%|vh|vw)" src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Additionally, 45 inline `fontSize:` occurrences exist in `.tsx` files (`0` ×15, `18` ×7, `14` ×5, `12` ×4, `16` ×2, plus singles), independent of the `.less` values above.

This is a **20+-value, unscaled typography ramp** — px and rem are freely mixed within the same responsive root-font-size system described in §2.2, meaning `px` values do not scale with the root-font zoom while `rem` values do; the two families of literal sizes will visually drift apart from each other at different viewport widths.

### 2.4 Font weights

Only 4 distinct weight declarations exist in `.less`: `bold` (9×, keyword rather than numeric), `700` (1×), `400` (1×), `300` (1×). No use of the 500/600 weights that are explicitly loaded from Google Fonts (§2.1) was found in `.less` — they may only be reached via AntD's own internal styles/typography components, not by this codebase's custom CSS.
Source: `grep -rhoE "font-weight:\s*[0-9a-zA-Z]+" src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

### 2.5 Line-height

Essentially undeclared: a single explicit `line-height: 3.9` was found repo-wide in `.less`; all other line-height behavior is left to AntD defaults / browser defaults. There is no line-height scale.
Source: `grep -rhoE "line-height:\s*[0-9.]+(px|rem|em|%)?" src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

---

## 3. Spacing / sizing

No `@spacing-*` Less variables exist anywhere. Spacing is 100% literal, in a loose mix of `px` and `rem` with an *implicit* (never codified) 4/8-multiple bias:

**Padding**, top values by frequency: `8px` (11), `1rem` (11), `0.5rem` (6), `16px` (5), `12px` (5), `0px` (5), `0.625rem` (5, always as `padding-bottom`), `8px 16px` (4), `2px 6px` (4), `10px` (4). Full long-tail includes `1rem 8rem`, `2rem 1rem`, `16px 0px 0px 16px`, etc. — one-off compound shorthand values with no shared vocabulary.

**Margin**, top values by frequency: `margin-top: 0.5rem` (13), `margin: 8px` (12), `margin-left: 4px` (11), `margin: 16px` (9), `margin: 1rem` (8), `margin-left: 0.5rem` (8), `margin: 0.5rem` (7), `margin-right: 8px` (7), `margin-right: 0.5rem` (7) — plus dozens more singles.

Source: `grep -rhoE "padding(-[a-z]+)?:..." / "margin(-[a-z]+)?:..." src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

**Assessment:** an approximate 4px/8px (and 0.25rem/0.5rem/1rem) rhythm *does* exist informally (most values are multiples of 4px or 0.25rem), but it was never extracted into a spacing scale — every component re-derives its own numbers, so the "rhythm" is a coincidence of habit, not an enforced system. This is a straightforward, low-risk win to formalize in the new platform (an 8-point spacing scale would fit almost all observed values with minimal visual change).

---

## 4. Borders / radii / shadows

### 4.1 Border radius

No `@radius-*` variable exists. 13 distinct literal values observed, dominated by 3 clusters that look like an implicit small/medium/large scale:

| Value | Count | Role |
|---|---|---|
| `8px` | 20 | small controls |
| `50%` | 17 | circular avatars/icons |
| `16px` | 11 | cards |
| `0.625rem` | 10 | cards (rem-equivalent to 10px) |
| `0.75rem` | 9 | cards (rem-equivalent to 12px) |
| `6px` | 6 | small controls |
| `10px` | 6 | small controls |
| `0.5rem` | 5 | small controls |
| `1rem` | 4 | cards |
| `20px`, `12px`, `5px`, `32px`, `3.125rem` | 1–2 each | one-offs (the `3.125rem`/50px case is the login form panel) |

Source: `grep -rhoE "border-radius:..." src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

Note the **unit inconsistency between literally equal values**: `8px`/`0.5rem`, `10px`/`0.625rem`, and `12px`/`0.75rem` are each the same physical radius expressed two different ways in different files — direct evidence the "scale" was never centralized.

### 4.2 Border width

`@border-width: 3px` is declared but dead (§7) — actual border widths in use are unrelated literals: `1px`, `3px` (as `border-left: 3px solid ...`), `4px` (as `border-left: 4px solid ...`, `MessageBallon`), `5px` (`ChatSenderFooter`). None of these consistently reference the declared token.

### 4.3 Shadows — two distinct visual languages coexisting

23 `box-shadow` declarations found, falling into two clearly different design languages that were never reconciled:

- **Flat drop-shadows** (single-offset, translucent black), e.g. `0px 0px 10px 0px rgba(0,0,0,0.75)`, `7px 7px 25px rgba(0,0,0,0.15)`, `0px 1px 3px rgba(0,0,0,0.2)` — conventional Material-style elevation.
- **Neumorphic dual-shadow pairs** (light+dark opposing offsets forming a "soft UI" embossed look), always declared as a *pair* per component for dark vs. light theme, e.g.:
  - dark: `5px 5px 10px #0b0b0b, -5px -5px 10px #1d1d1d` (`ItemDefault`)
  - light: `0px 0px 10px #d1d1d1` (`ItemDefault`, `.light` variant — asymmetric with its dark counterpart, i.e. the light variant drops the neumorphic double-shadow entirely and uses a flat shadow instead)
  - dark: `5px 5px 10px #171717, -5px -5px 10px #292929`
  - light: `8px 8px 20px #cccccc, -8px -8px 20px #f4f4f4` (this one *does* keep the dual-shadow neumorphic treatment in light mode)

Source: `grep -rhoE "box-shadow:[^;]+;" src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; representative components `trilhas-frontend:src/components/ItemDefault/ItemDefault.less:8-9,18 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

**Assessment:** the neumorphic language is a genuine, distinctive visual signature of this product (worth evaluating for reuse), but it is applied inconsistently — some components keep the dual-shadow treatment in both themes, others silently swap to a flat shadow in light mode. There is no shared elevation-token set (`@shadow-sm/md/lg`) driving any of this; each shadow pair is copy-pasted per component.

---

## 5. Breakpoints

Two entirely separate, non-integrated breakpoint systems are in play:

### 5.1 CSS `@media` breakpoints — 33 distinct widths, effectively unscaled

Distinct `max-width`/`min-width` values found range from `324px` to `1590px`; **most values appear exactly once**, indicating breakpoints are picked ad hoc per component rather than drawn from a shared scale. The only repeated values with meaningful frequency: `768px` (12×, clearly a semi-convention), `1260px` (4×, ties to `collapseRule`, see 5.2), `700px` (3×), `800px`/`1220px`/`345px` (2× each). Everything else (`334px`, `328px`, `355px`, `362px`, `815px`, `762px`, `756px`, `600px`, `576px`, `450px`, `400px`, `390px`, `375px`, `368px`, `360px`, `350px`, `340px`, `324px`, `1223px`, `1000px`, `720px` min-width, `1024px` min-width, etc.) is a one-off.
Source: `grep -rhoE "@media[^{]+" src --include="*.less" --include="*.css"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

Two responsive root-font-size breakpoints exist separately in `globals.css` (`1590px`, `1480px`, `1260px`) — see §2.2.

### 5.2 JS-driven layout breakpoints (the dominant pattern for structural responsiveness)

The *actual* primary mechanism for "mobile vs. desktop" layout switching is not CSS media queries but a **JS width-tracking hook** compared against two exported numeric constants, then branched via conditional JSX/class-name, in **40+ components and pages**:

```ts
export const collapseRule = 1260;
export const collapseRuleMobile = 800;
```
Source: `trilhas-frontend:src/utils/constants.ts:5-6 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

Usage pattern repeated verbatim across the tree:
```ts
const [width] = useWindowSize();
const collapsed = useMemo(() => width < collapseRule, [width]);
```
Representative sources (of ~40 total call sites): `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:106 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`, `trilhas-frontend:src/components/TrilhaInterativa/TrilhaInterativa.tsx:39 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`, `trilhas-frontend:src/hooks/useEvolucaoMenu.tsx:50 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (uses `collapseRuleMobile` instead).

The one Less breakpoint variable that does exist, `@collapse-rule: 1260px` in `Index.less`, duplicates `collapseRule` from `constants.ts` as a **separate, independently maintained literal** — the two are not derived from a shared source and could silently drift.
Source: `trilhas-frontend:src/pages/Index.less:1 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

**Assessment:** the JS-comparison approach means "responsive" behavior in this app is really "container-query-by-hand" via `window.resize` + React state, not CSS breakpoints — this has real performance and SSR-hydration implications (`useWindowSize` needs a client mount before it knows real width) that the new platform should deliberately decide to keep or replace (e.g., with CSS container queries / matchMedia hooks / Tailwind breakpoints).

---

## 6. Z-index layers

No `@z-*` variables exist. 11 distinct literal values in use, with no visible layering documentation:

| Value | Count | Likely role |
|---|---|---|
| `1` | 10 | base stacking context lift |
| `2` | 4 | — |
| `99999` | 2 | full-screen loading overlay (`FadeLoading`) |
| `999` | 2 | — |
| `3` | 2 | — |
| `1031` | 2 | nprogress bar/spinner (matches the library's own convention) |
| `10` | 2 | — |
| `9999` | 1 | — |
| `5`, `4`, `0` | 1 each | — |

Source: `grep -rhoE "z-index:\s*[0-9]+" src --include="*.less" --include="*.css" --include="*.tsx"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. There is no coherent z-index scale (e.g., 10/20/30/40 conventions) — values appear to have been picked to "just be higher than whatever was previously highest nearby," a classic z-index arms race.

---

## 7. Light/Dark theme mechanics and Ant Design customization

### 7.1 The base build is permanently dark + compact — "light" is a client-only patch, not a real second theme

`next.config.js` wires `next-plugin-antd-less` with AntD's official Less-variable generator, requesting the **dark** algorithm and **compact** density, then layers the 15 custom brand variables from §1.1 on top:

```js
modifyVars: {
  ...getThemeVariables({ dark: true, compact: true }),
  ...variables,   // the @primary-color etc. object, identical to variables.less
}
```
Source: `trilhas-frontend:next.config.js:1-38 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

This produces **one single compiled CSS bundle**, shipped to every user regardless of theme preference or tenant — dark background, compact AntD control sizing, orange primary. This is the only theme actually baked into the production build; there is no equivalent "light + compact" or "dark + comfortable" build variant.

### 7.2 "Light mode" is a client-side runtime bolt-on, gated by a cookie, requiring a full reload

- Preference is stored as a plain cookie (`theme.light`) via `nookies`, read/written by `useLightTheme()`. Toggling calls `window.location.reload()` — there is no live/reactive theme switch; every toggle is a full page reload.
  Source: `trilhas-frontend:src/hooks/useLightTheme.ts:1-23 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
- The toggle UI is `SwitchThemeButton`, an AntD `Switch` with sun/moon `MaterialIcon`s, rendered in `PageContainer` (2 places) and on the login page.
  Source: `trilhas-frontend:src/components/SwitchThemeButton/SwitchThemeButton.tsx:1-25 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`
- When `isLight` is true, `_app.tsx` dynamically (`next/dynamic`, `ssr:false`) mounts a `LightTheme` component whose entire body is `require("./LightTheme.less")` — i.e., a React component that renders nothing and exists purely as a vehicle to conditionally inject a stylesheet client-side.
  Source: `trilhas-frontend:src/pages/_app.tsx:18-20,42-44 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; `trilhas-frontend:src/themes/LightTheme.tsx:1-9 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

- **What `LightTheme.less` actually contains is not a themed variable set — it's (a) a full re-import of the *stock, uncustomized* `antd/dist/antd.css`** (`@import url("~antd/dist/antd.css");`, i.e. the default light AntD theme, standard density, default blue primary, layered *on top of* the dark/compact/orange bundle from §7.1 purely via later-wins CSS cascade order) **plus (b) ~30 hand-written override rules** patching specific components that don't look right once light AntD is layered over dark-compiled base (card backgrounds forced to `#fff !important`, drawer padding resets, upload-dragger dimensions, tab paddings, skeleton widths, etc.).
  Source: `trilhas-frontend:src/themes/LightTheme.less:1-115 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

- **Per-component "light" visual variants are then hand-implemented a third time**, independently of both of the above: 23 of the 153 `.less` files implement their own `&.light { ... }` (or, once, `&.is-light` — a naming inconsistency, see below) selector block with hardcoded literal colors for that specific component's light-mode look (e.g. `ItemDefault.less`, `InfoPacienteHeader.less`, `DisplayCard.less`, `BalancoHidricoContent.less`). The `isLight` boolean is threaded down as a React prop from `useLightTheme()` through many component trees to conditionally apply the `"light"` class name.
  Source (count): `grep -rl "&\.light\|\.light {" src --include="*.less"` → 23 files, over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Representative: `trilhas-frontend:src/components/ItemDefault/ItemDefault.less:11-14 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.
  Naming inconsistency: `ProtocoloSepseContent.less` uses `&.is-light` instead of the `.light` convention used everywhere else (43 total `.light` occurrences vs. this 1 lone `.is-light`).
  Source: `trilhas-frontend:src/components/ProtocoloSepseContent/ProtocoloSepseContent.less:18 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`

**Net picture:** "theme switching" in this codebase is not one mechanism but **four stacked, independently-authored mechanisms** that happen to visually cohere today through careful manual tuning: (1) a single build-time dark/compact/branded AntD compile, (2) an entire second stock AntD stylesheet loaded client-side and cascade-layered over it, (3) ~30 manual patch rules fixing what (2) breaks, and (4) ~23 components each hand-rolling their own light/dark literal-color pair via a `.light` class. This is expensive to maintain (a new component must remember to add its own `.light` block) and fragile (cascade-order dependent; no compile-time guarantee light-mode CSS "wins" for any given selector specificity).

### 7.3 Per-tenant runtime recoloring is a fifth, orthogonal mechanism

Layered independently on top of all of the above: the `dynamic-antd-theme` npm package (`changeAntdTheme`) recompiles AntD's colors **in the browser at runtime** to the tenant's configured brand color, and simultaneously sets the 2 CSS custom properties described in §1.4/§1.5. This is wired into `_app.tsx` (mount-time, hardcoded default) and `PageContainer.tsx` (re-applied once real tenant data loads) — see §1.5 for the double-application / flash-of-default-color detail.

### 7.4 Ant Design customization approach — summary

| Aspect | Value / mechanism |
|---|---|
| AntD version | `^4.21.7` (pre-v5; Less-variable theming, no CSS-in-JS design tokens) |
| Less compilation plugin | `next-plugin-antd-less` `^1.8.0`, via `.babelrc`'s `babel-plugin-import` (`libraryName: "antd", style: true`) for per-component style imports, and `next.config.js`'s `withAntdLess(...)` wrapper for the actual Less→CSS compile with `modifyVars` |
| Base theme algorithm | `getThemeVariables({ dark: true, compact: true })` from `antd/dist/theme` — **baked at build time**, not switchable at runtime |
| Brand variable overrides | The 15 variables in §1.1, merged into the same `modifyVars` object, duplicated verbatim in `styles/variables.less` (unused by the build) |
| Runtime re-theming | `dynamic-antd-theme` package (`^0.8.7`) — recompiles AntD colors client-side per tenant; parallel to (not derived from) the build-time Less vars |
| Locale | `ConfigProvider locale={ptBR}` (Brazilian Portuguese) + `moment/locale/pt-br` — app is PT-BR only, no i18n scaffolding observed |
| Light theme | Not a build variant — a client-only stock-AntD-CSS overlay + manual patches + cookie flag (§7.2), requiring full reload to toggle |
| PWA | `next-pwa` wraps the AntD-Less config; manifest colors (§1.6) are disconnected from the theme system entirely |

Source: `trilhas-frontend:package.json:8-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; `trilhas-frontend:.babelrc:1-13 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; `trilhas-frontend:next.config.js:1-38 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; `trilhas-frontend:src/pages/_app.tsx:1-54 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

---

## 8. Dead / unused tokens

Confirmed by exhaustive repo-wide grep (each variable name searched across every `.less` file; the only hit found is the declaration line itself):

| Token | Declared value | Evidence of non-use |
|---|---|---|
| `@skeleton-text` | `#eee3` | 0 other references in any `.less` file |
| `@degree` | `120deg` | 0 other references; no `conic-gradient`/`gradient` usage found anywhere that takes an angle variable |
| `@grad-perc` | `-100%` | 0 other references |
| `@header-opacity` | `0.8` | 0 other references |
| `@border-width` | `3px` | 0 other references (actual borders use unrelated literals `1px`/`3px`/`4px`/`5px`) |

Source: `grep -rn "@skeleton-text\|@degree\|@grad-perc\|@header-opacity\|@border-width" src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` returns only the declaration line in `styles/variables.less:11-15`. These 5 tokens (a third of the declared token set) are entirely dead weight — most plausibly remnants of a removed circular/conic-gradient feature (`@degree`/`@grad-perc` strongly suggest a `conic-gradient(from @degree, ...)` or radial progress ring that was later reimplemented or removed) and an unshipped header-opacity/border treatment.

By contrast `@primary-color-shade` (`darken(@primary-color, 47%)`), while used only once, *is* genuinely consumed: `trilhas-frontend:src/components/SelectEmpresaAtual/SelectEmpresaAtual.less:4 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

---

## 9. Motion (bonus — not explicitly requested but material to "visually strong" claim)

No motion/duration tokens exist. Observed literal `transition`/`animation` durations: `0.2s`/`0.3s`/`0.4s`/`0.6s`/`1s`/`150ms` eases, plus two named keyframe animations (`slide-in-top`/`slide-out-top`, both `0.25s` with distinct cubic-béziers) and a `fadeIn` keyframe (`0.5s both`) applied globally to `.page`. All ad hoc, all one-off per component, no shared easing/duration scale.
Source: `trilhas-frontend:src/styles/globals.less:55-68 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`; `grep -rhoE "transition:[^;]+;|animation:[^;]+;" src --include="*.less"` over `trilhas-frontend:src @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

---

## Candidate ADR decisions

Each entry: **what the legacy did**, **evident rationale**, **assessment for the new platform**.

1. **Single build-time AntD theme (dark + compact + custom brand vars), no build-time light variant.**
   *Legacy:* `next.config.js` bakes `getThemeVariables({dark:true, compact:true})` + 15 brand vars into the one shipped bundle (§7.1, §7.4).
   *Rationale (evident):* dark mode was likely the primary/preferred mode for ICU night-shift/low-light clinical environments; compact density maximizes data-table information density for bedside/dashboard views.
   *Assessment:* the "ICU-appropriate dark-first, dense-by-default" instinct is sound and worth preserving as an explicit decision — but it should be a first-class, documented choice (e.g., an ADR stating "dark, compact is default because X"), not an implicit side-effect of a config object nobody revisited.

2. **Light mode implemented as a client-only, cookie-gated, full-reload CSS overlay rather than a true second theme.**
   *Legacy:* stock un-customized `antd/dist/antd.css` is loaded on top of the dark/compact/branded bundle via cascade order, patched with ~30 manual override rules, plus 23 components each hand-rolling their own `.light` literal-color block (§7.2).
   *Rationale (evident):* pragmatic "make it work" patch added after the fact, without revisiting the base theme; avoiding a second full build likely kept the build pipeline simpler at the time.
   *Assessment:* this is the single most fragile part of the legacy design system and should **not** be carried forward as-is. Recommend a real token-driven theme (CSS custom properties or AntD v5 `ConfigProvider` `theme.token`/algorithm switching) with light and dark as symmetric, compile-verified variants, switchable without reload.

3. **Multi-tenant white-label branding via a single runtime-overridable primary-color token (`cor_primaria`), applied via 3rd-party AntD Less recompilation + 2 CSS custom properties.**
   *Legacy:* each tenant picks a brand color via a native color `<input>`; `dynamic-antd-theme` recompiles AntD colors client-side and `--primary-color`/`--primary-shadow-color` propagate to ~60 call sites (§1.5).
   *Rationale (evident):* IntensiCare/teleUTI serves multiple hospital/company clients ("empresas") who want their brand color reflected in the product — a real, valid product requirement.
   *Assessment:* keep the *capability* (per-tenant brand color is clearly a validated need), but replace the mechanism — a single runtime CSS-variable-driven token (feeding AntD v5's `theme.token.colorPrimary` or a CSS-variable-based design-token system) is far simpler and more reliable than live Less recompilation via a small, unmaintained-looking third-party package, and removes the double-application/flash-of-default-color bug (§1.5).

4. **Semantic status colors (`@success/@warning/@danger/@info/@default`) declared but bypassed for actual clinical status indicators.**
   *Legacy:* medication-administration state colors and other status chips use independent literals/AntD preset names instead of the declared semantic tokens (§1.3).
   *Rationale (evident):* likely organic growth — each feature author picked "a green" and "a yellow" without checking for an existing token, and AntD's own preset `Tag` colors (`"green"`/`"yellow"`/`"cyan"`/`"grey"`) were convenient defaults.
   *Assessment:* highest-priority ADR for the new platform. A clinical product needs one governed, accessible, contrast-checked severity scale (e.g., normal/caution/critical/inactive) used *everywhere* severity is shown — vitals, medication status, sepsis protocol steps, occupancy alerts — not per-component reinvention.

5. **No spacing, radius, shadow, motion, or z-index scale — 100% literal values throughout `.less`.**
   *Legacy:* every dimension examined (padding/margin, border-radius, box-shadow, transition duration, z-index) is a literal, freely mixing `px` and `rem`, with dozens of near-duplicate values doing the same visual job (§3, §4, §6, §9).
   *Rationale (evident):* no design-system tooling existed at project start; the codebase grew by component-level copy/paste rather than shared primitives.
   *Assessment:* straightforward, low-risk modernization opportunity — the *values in use* already cluster around implicit 4/8px and small/medium/large radius groupings, so a formal scale (spacing, radius, elevation, z-index, motion-duration tokens) can be introduced with minimal visual regression, and should be an early ADR for the new platform's token architecture.

6. **Neumorphic ("soft UI") dual-shadow visual language used for cards/list items, inconsistently paired between dark and light variants.**
   *Legacy:* many components use light+dark opposing-offset shadow pairs for an embossed look in dark mode, but the light-mode counterpart sometimes drops to a flat single shadow and sometimes keeps the dual-shadow treatment (§4.3).
   *Rationale (evident):* a deliberate, distinctive visual identity choice (this is genuinely one of the "visually strong" aspects of the legacy app worth reusing), executed inconsistently due to lack of a shared elevation-token abstraction.
   *Assessment:* worth explicitly preserving as a brand signature in the new platform, but implemented as a proper elevation-token pair (e.g., `--shadow-elevated-dark` / `--shadow-elevated-light`) applied uniformly, rather than copy-pasted per component.

7. **Responsive layout driven primarily by JS `window.width` comparisons against two magic numbers (`collapseRule=1260`, `collapseRuleMobile=800`), not CSS breakpoints, duplicated as a separate Less literal in one file.**
   *Legacy:* ~40 components independently call `useWindowSize()` + `useMemo(() => width < collapseRule, ...)`; a parallel, unlinked `@collapse-rule: 1260px` Less variable exists in one page file (§5.2).
   *Rationale (evident):* enables conditional component-tree switching (not just CSS reflow) for genuinely different mobile/desktop layouts (e.g., different nav patterns), which pure CSS media queries can't do without duplicating markup.
   *Assessment:* the underlying need (structural, not just cosmetic, responsive behavior) is legitimate and likely needs to be preserved, but the new platform should formalize the breakpoints as a single named constant/token (shared between JS and CSS, e.g. via a CSS custom property read in JS, or a design-tokens JSON consumed by both), and choose a single deliberate breakpoint set rather than the 33 ad hoc `@media` widths found in `.less` (§5.1).

8. **`styles/variables.less` duplicates `next.config.js`'s `modifyVars` object verbatim and is never imported by any `.less` file.**
   *Legacy:* the 15 declared color/scalar tokens exist as two independently maintained copies — one is the actual build input, the other is inert (§1.1).
   *Rationale (evident):* likely intended as "the" canonical token file for IDE/Less-language-server support or documentation purposes, with the developer forgetting (or not realizing) it isn't wired into the webpack build.
   *Assessment:* an unambiguous single-source-of-truth bug. In the new platform, tokens must be declared exactly once and consumed by both the design-time reference and the build pipeline (e.g., a tokens JSON/YAML that generates both TypeScript constants and CSS variables / Less vars).

9. **Five of fifteen declared Less tokens (`@skeleton-text`, `@degree`, `@grad-perc`, `@header-opacity`, `@border-width`) are entirely dead.**
   *Legacy:* declared, duplicated into `next.config.js`, never consumed (§8).
   *Rationale (evident):* remnants of removed or unshipped features (most likely a conic-gradient/radial element, given `@degree`+`@grad-perc`).
   *Assessment:* do not port these tokens forward without a concrete reintroduced use case; treat as historical debris.

10. **Poppins loaded twice via two different, partially conflicting mechanisms; one is broken.**
    *Legacy:* a correct Google Fonts `<link>` in `_document.tsx` plus a malformed `@font-face` in `globals.css` whose `src` points at a CSS-API URL instead of a font file (§2.1).
    *Rationale (evident):* an attempt to guarantee the italic weight loads (possibly added because the italic style seemed to be missing at some point), added without removing/fixing the pre-existing correct mechanism.
    *Assessment:* trivial cleanup for the new platform — declare the font once, correctly (e.g., self-hosted `next/font` or a single verified Google Fonts link), and drop the dead `@font-face` block.

11. **Root `html` font-size is rescaled at 3 viewport breakpoints with a non-monotonic, likely-unintended cascade interaction.**
    *Legacy:* `93.75%` at ≤1590px, `85.5%` at ≤1480px, `100%` at ≤1260px — the last rule wins at ≤1260px, silently negating the 85.5% shrink except in a narrow 1261–1480px band (§2.2).
    *Rationale (evident):* likely added incrementally (one rule per "this feels too big at this width" bug report) without testing the combined cascade.
    *Assessment:* replace with a single, deliberately-designed fluid-type or clamp()-based scale in the new platform; do not port the specific percentages forward without re-deriving them against real content.

12. **`.light` class-naming convention used 43 times across 23 files, with one inconsistent `.is-light` outlier.**
    *Legacy:* `ProtocoloSepseContent.less` alone uses `&.is-light` where every other component uses `&.light` (§7.2).
    *Rationale (evident):* simple author inconsistency / lack of a shared component-authoring convention or lint rule.
    *Assessment:* minor, but indicative of the broader "no shared design-system contract enforced by tooling" theme running through this inventory — the new platform should enforce token/class naming via lint rules or a component-generation template, not tribal knowledge.

13. **PWA manifest brand colors (`theme_color: #000000`, `background_color: #FFFFFF`) are static and disconnected from both the AntD theme and the per-tenant brand color.**
    *Legacy:* manifest colors never reflect `@primary-color` or a tenant's `cor_primaria` (§1.6).
    *Rationale (evident):* manifest.json is a static asset generated once at project setup and not revisited as theming evolved.
    *Assessment:* if per-tenant PWA installability/branding matters for the new platform, manifest generation should be dynamic (server-rendered per tenant) or explicitly scoped out as a known limitation; don't silently inherit the mismatch.
