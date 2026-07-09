# 0002. Dark-first, compact Ant Design base theme baked at build time

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's legacy frontend (`trilhas-frontend`) is an ICU bed-management and clinical-documentation tool used at bedside dashboards and in dim, night-shift-staffed rooms. Its visual theme is not expressed as a design decision anywhere in the codebase — it is an emergent property of a single build configuration object. `next.config.js` wires `next-plugin-antd-less` to Ant Design's official Less-variable generator and compiles exactly one CSS bundle for the entire application, shipped to every user regardless of individual preference, device, ambient lighting, or tenant (`trilhas-frontend:next.config.js:1-38`). There is no build-time "light" or "comfortable density" counterpart — only one theme exists as a first-class, compiled artifact (`trilhas-frontend:next.config.js:31-37`; inventory §1.2, §1.4). The new platform needs to decide, deliberately, what the default look and density should be — rather than inheriting this as an unexamined side effect.

## The Legacy Decision

`next.config.js` merges Ant Design's dark-theme algorithm and compact-density algorithm with the app's 15 custom brand variables into one `modifyVars` object, which is the sole input to the Less→CSS compile:

```js
modifyVars: {
  ...getThemeVariables({ dark: true, compact: true }),
  ...variables,   // the 15 @primary-color, @success-color, etc. constants
}
```
`trilhas-frontend:next.config.js:31-37` (full config: `trilhas-frontend:next.config.js:1-38`).

This produces one compiled bundle: Ant Design's dark palette, compact control sizing/spacing, and the orange (`#fe6d01`) brand primary baked in together, with no runtime or build-time toggle to change the base algorithm (D-01 §7.1, §7.4). Everything users perceive as "light mode" is a separate, unrelated client-side overlay mechanism layered on top of this bundle after the fact (inventory §2.7) — it is not a build-time sibling of this decision and is out of scope here (→ ADR 0003).

## Evident Rationale

*(Inferred — not stated anywhere in the codebase or commit history.)* Dark mode plausibly suits dim ICU rooms during night shifts, where a bright white UI would cause glare and disrupt patient care in low-light clinical environments. Compact density plausibly maximizes information density for data-heavy views — bed-occupancy grids, vitals tables, dashboards — where fitting more patients/values on screen at once has real clinical value (D-01 §7.1 candidate-decision #1; inventory §1.2). Both instincts are reasonable defaults for this product category. However, no comment, commit message, ticket reference, or design note in the audited source substantiates this reasoning — it is reconstructed entirely from the shape of the config and the product's domain.

## Assessment

**Strengths (worth preserving as explicit choices):**
- Dark-first and compact-by-default are both defensible, domain-appropriate instincts for a 24/7 ICU monitoring tool (inventory §1.2, §8 "Preserve").
- Bundling the base algorithm with brand variables in one config keeps the build simple and avoids theme-init sequencing at runtime.

**Weaknesses (specific and cited):**
- **Undocumented, not decided.** The choice lives entirely inside a `modifyVars` object; nothing marks it as intentional versus incidental. No ADR, comment, or doc backs it (inventory §1.2).
- **No symmetric light or comfortable-density build.** There is exactly one compiled variant; anyone who wants light mode or comfortable density gets a patched-on overlay, not a real alternative (`trilhas-frontend:next.config.js:31-37`; inventory §2.7, item 1 in the theming-mechanism list — "one bundle for everyone").
- **Coupled to a fragile theming stack.** This build-time bundle is the base layer of a 5-mechanism theming stack (build-time compile → stock-AntD light overlay → ~30 manual patch rules → ~23 per-component `.light` blocks → runtime per-tenant recolor) that the inventory rates "Critical — do not port" as a whole (inventory Summary #1, §2.7). The dark/compact choice itself is sound, but its implementation as an unexamined config side-effect is what let the other four layers accrete without anyone revisiting the foundation.
- **AntD v4 Less-variable theming is inherently single-shot.** `getThemeVariables({dark, compact})` bakes the algorithm at compile time; there is no API for switching it without a full separate build or the runtime-recompilation hack the legacy app uses elsewhere for brand color (D-01 §7.4).

## Considered Options

1. **Port forward as-is:** keep a single dark+compact build-time default, still undocumented. Rejected — repeats the exact governance gap this ADR exists to close.
2. **Make dark+compact the explicit, documented default, with light and comfortable density as equally first-class, independently selectable, build- or runtime-switchable variants** (e.g., via CSS custom properties / a token system with a light-algorithm counterpart, or, if staying on Ant Design, AntD v5's `ConfigProvider` `theme.algorithm`/`theme.token` API rather than Less-variable compilation). Symmetric with ADR 0003 (light path).
3. **Make light+comfortable the default, dark+compact opt-in.** Rejected — inverts a rationale (glare reduction, information density) that is well-suited to this clinical domain without evidence the assumption is wrong; would only be justified by new user research.
4. **No default; force explicit choice at first login (no theme until user/tenant picks one).** Rejected — adds onboarding friction for a clinical tool where staff need a working screen immediately; a sensible default plus override is standard practice.

## Decision Outcome

**Recommended: Option 2** — adopt dark, compact as the explicit, documented default theme for the new platform, justified by ICU night-shift glare reduction and bedside information density, and implement it as one of two symmetric, equally-supported variants (dark+compact default, light+comfortable available) driven by a runtime-switchable design-token mechanism rather than a single hardcoded build. This makes explicit what the legacy config only implied, and removes the structural reason a second, patched-on light theme (ADR 0003) was ever needed as an afterthought. This recommendation is pending ratification by the design and engineering leads; it does not assume a specific frontend framework, only that whatever theming mechanism is chosen supports declaring both variants as first-class citizens.

### Consequences

**Good:**
- The rationale (glare, density) is now a recorded decision that can be validated with real ICU users, not an implicit artifact future engineers must reverse-engineer from a config object.
- Establishes the point of symmetry that ADR 0003 (light-mode mechanism) and ADR 0004 (per-tenant brand color) depend on — both can now assume "two real variants," not "one real bundle plus a patch."
- Opens the door to a single token-driven theming mechanism (feeding both variants) instead of the legacy's five stacked, independently-authored mechanisms (inventory §2.7).

**Bad / risks:**
- Requires committing to a token architecture (spacing/density scale, dark+light color pairs) up front rather than deferring it — more initial design work than "just compile AntD's dark theme and move on."
- If density and color-scheme are made independently toggleable (dark/light × compact/comfortable = 4 combinations), QA and visual-regression surface area grows relative to the legacy's single bundle.
- Any accessibility/contrast validation done for the legacy dark+compact+orange combination does not automatically carry over and must be redone for each newly-supported combination.
