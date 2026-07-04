# 0011. Responsive layout via JS window-width comparisons with competing sub-strategies

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform's structural responsiveness — mobile vs. desktop layout switching, not just cosmetic reflow — is computed in JavaScript from `window.innerWidth` rather than driven by CSS media or container queries. A single width-tracking hook (`useWindowSize`) feeds `useMemo` comparisons against two exported numeric constants, and this pattern recurs across roughly 42 files (49 files import `useWindowSize`, 42 reference `collapseRule`) (`trilhas-frontend:src/utils/constants.ts:5-6`; D-01 §5.2; D-02 §5.1; inventory §2.6). Separately, and never integrated with the JS constants, 33 distinct one-off `@media` widths exist across `.less` files, most appearing exactly once (D-01 §5.1; inventory §2.6). At least three different sub-strategies have grown up independently around the shared constants, producing drift and at least one live bug on very large ICU-monitor displays (D-02 §5.1; D-03 §4.1-4.2). As the new platform is rebuilt (framework choice out of scope for this ADR), the underlying need — genuinely different component structure at different breakpoints, not just CSS reflow — is real and must be preserved deliberately rather than reinvented ad hoc per screen.

## The Legacy Decision

- Two "magic" breakpoint constants are exported from a single utils file and consumed everywhere: `export const collapseRule = 1260;` and `export const collapseRuleMobile = 800;` (`trilhas-frontend:src/utils/constants.ts:5-6`).
- The dominant usage pattern, repeated near-verbatim across the tree: `const [width] = useWindowSize(); const collapsed = useMemo(() => width < collapseRule, [width]);` (D-01 §5.2; inventory §2.6).
- **Sub-strategy (A) — single-tree class-toggling (dominant, ~42 files):** `collapsed` toggles a CSS class and/or branches small pieces of JSX/inline style within one component tree (`PageContainer`, `DrawerBuilder`, `TabRecomendacoes`, `CollapseCard`, etc.) (inventory §4.4).
- **Sub-strategy (B) — fully forked component trees (1 confirmed instance):** `BalancoHidricoVisaoGeral` selects between two entirely separate files, `<GridView>` (hour×patient CSS grid) and `<MobileView>` (stacked cards), based on the same `collapsed` boolean derived from `collapseRule` — verified at `trilhas-frontend:src/components/BalancoHidricoVisaoGeral/BalancoHidricoVisaoGeral.tsx:1-55` (import of `collapseRule`, `useWindowSize`, and the `{data && !collapsed ? <GridView/> : <MobileView/>}` branch).
- **Sub-strategy (C) — ad-hoc per-page `Col span` if-chains over raw `window.innerWidth`, independent of both (A) and (B) and of AntD's `xs/sm/md/lg/xl` grid props:**
  - `ListOcupacoes` computes an AntD `Col span` via a 5-bucket chain: `width > 2800 → 4`; `1800 < width < 2400 → 6`; `1260 < width < 1800 → 8`; `800 < width < 1260 → 12`; `width < 800 → 24` (`trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:420-437`, verified directly against the pinned commit). **The band `(2400, 2800]` matches none of the five conditions, so `span` is `undefined` and AntD falls back to full-width cards** on very large monitors — a real dead-band bug (inventory §4.4; D-03 §4.1).
  - `ListDashboard` reimplements a *different*, non-identical bucket set one level up the navigation hierarchy: `width > 1800 → 6`; `1260 < width < 1800 → 8`; `800 < width < 1260 → 12`; `width < 800 → 24` (`trilhas-frontend:src/components/ListDashboard/ListDashboard.tsx:26-39`, verified). This set has no `>2800` tier and no dead band, but neither grid imports `collapseRule`/`collapseRuleMobile`, nor references the other's bucket set — two structurally identical "responsive card grid" behaviors, hand-duplicated with drift (D-03 §4.2).
- Separately, one lone Less breakpoint variable, `@collapse-rule: 1260px` in `Index.less`, duplicates the JS constant's value as an independently-maintained literal that could silently drift from it (D-01 §5.2; inventory §2.6).
- 33 distinct `@media` widths exist in `.less`, ranging `324px`–`1590px`; only `768px` (12×), `1260px` (4×), and `700px` (3×) repeat meaningfully — everything else is a one-off, ungoverned by any shared breakpoint token (D-01 §5.1; inventory §2.6, §4.4).
- Table density (`size="small"` vs. `"large"`, `scroll.y = calc(100vh - 350px)`) is likewise chosen ad hoc per screen rather than from a density token, independent of the breakpoint question but part of the same "no shared responsive contract" pattern (inventory §4.4; D-03 §4.3).

## Evident Rationale

*(Inferred — not stated anywhere in the legacy codebase or commit history reviewed.)* JS-computed branching lets a component render a genuinely different tree per breakpoint — not just reflowed CSS — which is exactly what sub-strategy (B) does for `BalancoHidricoVisaoGeral`: the hour×patient grid and the stacked-card mobile view are different information architectures, not the same markup restyled, and pure media queries cannot switch markup structure without duplicating it anyway (D-01 §5.2; D-03 §9 item 4/6 discussion; inventory §2.6). Given that legitimate need, and no design-token tooling in place at project start (per the token-governance pattern documented across the rest of this audit), it is plausible that once `collapseRule`/`collapseRuleMobile` existed as ordinary exported constants, individual feature authors reached for `window.innerWidth` directly for one-off cases (sub-strategy C) rather than importing the shared constants or reusing AntD's native responsive grid props, because nothing enforced a single responsive contract.

## Assessment

**Strengths:**
- The core need this pattern serves — structurally different component trees, not just visual reflow, at different breakpoints — is real and legitimate; sub-strategy (B) is a deliberate, reasonable use of JS branching for that purpose (D-01 §5.2 "Assessment"; inventory §4.4).
- `collapseRule`/`collapseRuleMobile` are at least centrally *declared*, and are correctly reused by several well-factored primitives (`DrawerBuilder`'s width auto-sizing, `PageContainer`'s mobile drawer gate, `TabRecomendacoes`, `Prescricao`, `ProtocoloSepseContent`) — proof the shared-constant approach works when actually followed (D-03 §8).

**Weaknesses, with specific inconsistencies:**
- **SSR/hydration cost:** `useWindowSize` cannot know the real viewport width until after client mount, so every one of the ~42 consuming components either renders a default-width guess on first paint or defers correct layout until hydration completes — a structural cost inherent to computing layout in JS rather than CSS (D-01 §5.2; inventory §2.6).
- **Dead-band bug on large ICU monitors:** `ListOcupacoes`'s span chain has no rule covering `(2400, 2800]`, so `span` is `undefined` and AntD renders full-width cards in that band — directly counter to the presumed intent of a 5-tier density scale, and specifically affecting the kind of large bedside/central-station monitor an ICU product should handle well (`trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:420-437`; D-03 §4.1).
- **Drift between hand-duplicated grids:** `ListDashboard`'s bucket set is structurally the same pattern as `ListOcupacoes`'s but numerically different and independently maintained, with neither referencing `collapseRule`/`collapseRuleMobile` nor each other (`trilhas-frontend:src/components/ListDashboard/ListDashboard.tsx:26-39`; D-03 §4.2).
- **33 ungoverned `.less` media widths**, almost all one-off, with no shared breakpoint token feeding them, plus a separately-drifting duplicate Less literal (`@collapse-rule: 1260px`) for the one breakpoint that *is* shared with JS (D-01 §5.1-5.2).
- **Three sub-strategies with no documented boundary for when to use which** — a new component's author has no rule for choosing (A) class-toggle vs. (B) fork vs. (C) ad hoc bucket, which is exactly how (C) proliferated in the first place.

## Considered Options

1. **Do nothing / continue the status quo.** Rejected — perpetuates the dead-band bug, the `ListOcupacoes`/`ListDashboard` drift, and gives a rebuilding team (especially AI agents generating new screens) no single contract to follow.
2. **Pure CSS solution — replace all JS width branching with CSS media queries / native CSS container queries**, eliminating the JS hook entirely. Would fix SSR/hydration cost and unify the breakpoint source, but cannot express sub-strategy (B)'s genuinely-different-markup-per-breakpoint need without duplicating DOM structure in both branches and hiding one with `display:none` — wasteful for a heavy grid like `GridView`/`MobileView` and loses the "don't even mount the unused tree" benefit the legacy fork provides.
3. **Single shared breakpoint token set, consumed by both a `matchMedia`-based hook and CSS (e.g. a design-tokens file feeding both TypeScript constants and CSS custom properties/media-query values), keeping the forked-tree escape hatch only where information density genuinely differs; retire ad-hoc per-page bucket chains in favor of the shared tokens or native responsive grid props.** Fixes the single-source-of-truth problem, fixes the dead-band bug by construction (a shared, tested bucket function replaces two independent if-chains), and preserves the one legitimate use of JS-driven forking.
4. **Adopt CSS container queries as the primary mechanism** (scoping "collapsed" state to a container rather than the viewport), reserving JS width detection only for the rare fork-tree case. More modern and arguably more correct for components nested inside variable-width containers (e.g. a drawer), but a bigger behavioral change from the legacy model and needs validation against real component nesting in the new platform before being assumed as the default.

## Decision Outcome

**Recommend Option 3** — a single named breakpoint set, defined once and consumed by both JS and CSS, with the JS-fork escape hatch (sub-strategy B) retained deliberately and narrowly, and the ad-hoc bucket chains (sub-strategy C) replaced by a shared, tested density function or native grid responsive props — pending team ratification. Concretely:

- Define breakpoints once (e.g. a tokens file or shared constants module) and generate both the JS comparison values and the CSS media-query / container-query values from it, closing the `constants.ts` vs. `Index.less @collapse-rule` drift risk at the root.
- Consider `matchMedia`-based hooks or CSS container queries in place of raw `resize`-listener + `useMemo` where only visual reflow (not structural forking) is needed — this removes the SSR/hydration gap for the majority (sub-strategy A) of cases, since container/media queries are resolved by the browser without a client-only width read.
- Keep the forked-component-tree pattern (sub-strategy B) only for cases where density/information-architecture genuinely differs per breakpoint (as `BalancoHidricoVisaoGeral` correctly does) — document this as the explicit bar for justifying a fork, so it is not reached for by default.
- Replace both `ListOcupacoes`'s and `ListDashboard`'s independent span-bucket if-chains with one shared, unit-tested density function (or AntD/equivalent `xs/sm/md/lg/xl`-style responsive props), explicitly covering the full width domain so the `(2400, 2800]` dead band cannot recur structurally.
- Retire the 33 one-off `.less`/CSS media widths in favor of the same shared breakpoint set; where a truly one-off value is needed, require it to be justified against the shared scale rather than hand-typed.

This is actionable regardless of final framework choice (React/Next or otherwise): the deliverable is a single breakpoint/token contract plus a documented rule for when component-forking is justified, both of which an AI-agent-led build process needs as an explicit, machine-readable contract rather than tribal precedent inferred from 42 divergent call sites.

### Consequences

**Good:**
- Eliminates the `ListOcupacoes` dead-band bug by construction, since bucket logic is defined and tested once rather than duplicated by hand.
- Removes the `ListOcupacoes`/`ListDashboard` drift and the `constants.ts`/`Index.less` duplicate-literal risk by giving both JS and CSS one source of truth.
- Preserves the one legitimate reason the legacy app used JS branching at all (structurally different trees in `BalancoHidricoVisaoGeral`), rather than discarding a sound instinct along with the ungoverned parts.
- Reduces SSR/hydration cost for the majority of components that only need reflow, not tree-forking, by shifting them to media/container queries.

**Bad:**
- Requires an upfront pass to decide the definitive breakpoint values and which of the ~42 current call sites qualify for the fork exception vs. simple CSS reflow — real, if bounded, migration effort.
- A shared density function/token set must be validated against the full range of real screen sizes actually used in ICU settings (including the >2800px monitors the legacy code silently mishandled) rather than assumed correct by inspection.
- Moving to container queries where nesting is deep (e.g. inside `DrawerBuilder`'s stacked drawers) needs verification that container context is correctly established at each nesting level; this is a genuine unknown until the new platform's component tree exists.
