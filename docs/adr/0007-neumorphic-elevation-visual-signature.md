# 0007. Neumorphic dual-shadow elevation as the product's visual signature

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform has no shared elevation abstraction: 23 `box-shadow` declarations exist across the `.less` tree, split between two unreconciled visual languages — conventional flat, single-offset drop-shadows (Material-style) and neumorphic ("soft UI") dual-shadow pairs that emboss a surface using opposing light/dark offsets (`trilhas-frontend:src/components/FeedBallon/FeedBallon.less:8`, `trilhas-frontend:src/components/MessagesList/MessagesList.less:20` for the flat language; design-system-inventory.md §2.5, D-01 §4.3 for the count). Because there is no `@shadow-*` token of any kind (D-01 §4.1 confirms zero elevation variables exist), every component that wants the embossed look hand-types its own light/dark shadow-pair literals, and every component that wants the flat look hand-types a different literal shape. As the new platform is rebuilt, this ADR decides whether to keep the neumorphic language at all, and if so, how to stop it from being re-invented per component.

## The Legacy Decision

- `ItemDefault` (a widely-reused list-row primitive, per design-system-inventory.md §3.2) declares a dark-mode dual-shadow: `box-shadow: 5px 5px 10px #0b0b0b, -5px -5px 10px #1d1d1d;` (`trilhas-frontend:src/components/ItemDefault/ItemDefault.less:6`). Its `&.light` variant does **not** carry an equivalent dual-shadow — it drops to a flat single shadow, `box-shadow: 0px 0px 10px #d1d1d1;` (`trilhas-frontend:src/components/ItemDefault/ItemDefault.less:12-14`).
- `ItemNotificacao` resolves the same question the opposite way: dark mode uses `5px 5px 10px #171717, -5px -5px 10px #292929` (`trilhas-frontend:src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.less:5`), and its light mode **keeps** the dual-shadow treatment, `8px 8px 20px #cccccc, -8px -8px 20px #f4f4f4` (`trilhas-frontend:src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.less:13`).
- The exact dark-mode value from `ItemDefault` is copy-pasted verbatim into `MobileCardWrapper` (`trilhas-frontend:src/components/MobileCardWrapper/MobileCardWrapper.less:6`) — a component design-system-inventory.md §3.2 records as having **0 usages** (dead code), showing the propagation mechanism is literally copy/paste between files, not a shared mixin, even into code nobody ends up shipping.
- No `.less` file references a shared shadow variable; each of the 23 declarations is authored independently (design-system-inventory.md §2.5, §7; D-01 §4.3).

## Evident Rationale

*(Inferred — not documented anywhere in the codebase or commit history reviewed.)* Neumorphism was plausibly chosen as a deliberate brand-differentiation move away from generic flat Material-style cards, and it pairs naturally with the legacy's dark-first, compact base theme (→ ADR 0002): an embossed dark surface reads clearly against a dark background where the light/dark offset pair has good contrast to work with. This also plausibly explains the light-mode inconsistency: light mode was added later as a client-side overlay (→ ADR 0003), and getting a soft-UI emboss to read well against light backgrounds requires more careful, lighter offset tuning — some authors did that tuning (`ItemNotificacao`), others took the easier path of falling back to a flat shadow (`ItemDefault`) rather than solving the harder problem.

## Assessment

**Strengths:** the neumorphic language is genuinely distinctive and immediately recognizable — one of the few visually strong, intentional-feeling aspects of the legacy UI (design-system-inventory.md §8, "Preserve"). It is not accidental: it recurs across unrelated components (list rows, notification items) with consistent offset/blur proportions, suggesting a real if undocumented design intent.

**Weaknesses, specifically:**
- **No shared abstraction.** All 23 declarations, dual-shadow and flat alike, are hand-typed literals; there is no `@shadow-elevated` variable or mixin to update centrally (D-01 §4.1, §4.3).
- **The dark/light question is answered twice, oppositely, with no documented rule.** `ItemDefault` silently drops neumorphism in light mode; `ItemNotificacao` silently keeps it. Neither choice is wrong on its own, but the coexistence of both, unexplained, means the next component author has no precedent to follow and will likely add a third variant.
- **Copy-paste, not reuse, is the propagation mechanism** — evidenced by `MobileCardWrapper` duplicating `ItemDefault`'s exact literal values while being entirely unused, i.e. the pattern spreads even without a live consumer driving it.
- **Accessibility/contrast is unverified.** Embossed surfaces rely on subtle light/dark offset contrast against the surface colour; layering clinical content (text, icons, or `statusTrilha` severity colouring, → future severity-token ADR) on top of a soft-UI surface has not been checked against WCAG contrast minimums in either theme.

## Considered Options

1. **Drop neumorphism, standardize on flat/Material elevation only.** Simplest to implement and to keep accessible, but discards the one distinctive, already-validated visual signature the audit identifies as worth reusing.
2. **Preserve neumorphism in dark mode only, flat shadows in light mode, made explicit.** Codifies `ItemDefault`'s asymmetric resolution as a deliberate rule rather than an accident, but permanently limits the signature to one theme.
3. **Preserve neumorphism symmetrically in both themes, as a governed elevation-token pair with multiple levels (e.g., `sm`/`md`/`lg`).** Systematizes `ItemNotificacao`'s approach: a small set of tokens (e.g. `--shadow-elevated-dark`, `--shadow-elevated-light`, each with sm/md/lg variants) consumed everywhere via one shared utility/mixin instead of literals, with contrast verified for both themes at build time.
4. **Tokenize neumorphism but gate it behind a fallback for accessibility/contrast preference** (e.g., `prefers-contrast: more`), falling back to flat shadows for users/contexts that need it, on top of option 3's token structure.

## Decision Outcome

**Recommended: Option 3, with the accessibility fallback from Option 4** — pending team ratification. Preserve neumorphic dual-shadow elevation as an explicit brand signature, but implement it as a small, named elevation-token scale (e.g., `--shadow-elevated-{sm,md,lg}-dark` / `-light`) consumed through one shared component-level utility, not copy-pasted per file. Resolve the dark/light asymmetry deliberately by adopting `ItemNotificacao`'s symmetric pattern as the default (soft-UI in both themes) rather than `ItemDefault`'s silent drop, since a signature that disappears in one theme is not really a signature. Any surface that carries clinical text/status content on top of an embossed background must pass an explicit contrast check in both themes before shipping, and the token set should honor `prefers-contrast`/reduced-transparency user preferences by substituting a flat shadow. This favors an AI-agent-led build process: agents adding a new card or list-row component should reach for a named `elevation` token/prop, not re-derive offset values by eyeballing a neighboring file, which is how the legacy's `ItemDefault`/`MobileCardWrapper` duplication happened in the first place.

### Consequences

**Good:**
- Preserves a genuinely distinctive, already-validated visual identity instead of flattening the product into generic Material design.
- Eliminates the copy-paste propagation pattern (`ItemDefault` → `MobileCardWrapper`) by giving agents and engineers one token/utility to reach for.
- Forces a deliberate, documented answer to the dark/light question instead of the current unexplained 50/50 split.
- Bakes in accessibility/contrast verification that the legacy never had, closing a real risk for a clinical product.

**Bad:**
- Requires an upfront design pass to pick and contrast-verify sm/md/lg dark and light shadow values before any component work proceeds, which the legacy never invested in.
- Soft-UI shadows are relatively expensive to render at scale (e.g., a bed-board grid with many simultaneously-elevated cards); the sm/md/lg scale should be benchmarked for paint cost on the densest real screens before being applied broadly.
- Adds a fallback code path (contrast/reduced-transparency preference) that must be tested and kept in sync with the primary token set, a maintenance surface the legacy did not have.
