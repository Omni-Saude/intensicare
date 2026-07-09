# 0006. No formal design-token scales for spacing, radius, elevation, z-index, motion, or type

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform has exactly 15 declared Less variables in total, all colour, and none of them cover spacing, radius, elevation, z-index, motion, or type (`trilhas-frontend:src/styles/variables.less:1-15`). Every other dimension of the visual language — padding/margin, border-radius, box-shadow, transition duration, z-index, and the entire type ramp — is written as a raw literal at each call site. Colour-literal sprawl alone is quantified at ≈340 raw occurrences against 15 declared tokens, a ≈7:1 ratio in `.less` files (design-system-inventory.md §2.3; D-01 §1.2). The non-colour dimensions have no tokens at all, so no ratio can even be computed — there is nothing to be a ratio *against*. As the new platform is rebuilt (React/Next or equivalent, framework TBD elsewhere), this absence of scales is the single largest "pave the cowpaths" opportunity: the legacy values already cluster, they were just never named.

## The Legacy Decision

- **Spacing:** no `@spacing-*` variable exists. Padding/margin are 100% literal, freely mixing `px` and `rem` (e.g. padding `8px` ×11, `1rem` ×11, `0.5rem` ×6; `margin-top: 0.5rem` ×13, `margin: 8px` ×12), with an implicit, never-codified 4/8-multiple bias (D-01 §3; inventory §2.5).
- **Border-radius:** no variable. 13 distinct literals fall into 3 implicit clusters — small (`8px`/`0.5rem`/`6px`/`10px`), card (`16px`/`0.625rem`/`0.75rem`/`1rem`), circular (`50%` ×17) — and the *same* radius is expressed two ways in different files: `8px`≡`0.5rem`, `10px`≡`0.625rem`, `12px`≡`0.75rem` (D-01 §4.1; inventory §2.5).
- **Elevation (box-shadow):** 23 declarations split between flat drop-shadows and neumorphic dual-shadow pairs, applied inconsistently (some components keep the dual-shadow in light mode, others silently swap to a flat shadow), with no shared elevation token (`trilhas-frontend:src/components/ItemDefault/ItemDefault.less:8-9,18`; inventory §2.5).
- **Z-index:** no variable. 11 distinct literals (`1` ×10, `2` ×4, `99999` ×2, `1031` ×2, `9999`, `999`, …) with no documented layering — a "be higher than whatever was highest nearby" pattern (D-01 §6; inventory §2.5).
- **Motion:** no duration/easing tokens. Ad-hoc `0.2s`/`0.3s`/`0.4s`/`0.6s`/`1s`/`150ms` durations plus one-off keyframes `slide-in-top`/`slide-out-top` (`0.25s`) and `fadeIn` (`0.5s`) applied to `.page` (`trilhas-frontend:src/styles/globals.less:55-68`).
- **Type:** single family (Poppins), no `@font-size-*` variables; a 20+-value unscaled px/rem ramp (`12px` ×14, `14px` ×6, `0.75rem` ×5, `16px` ×4, … down to `0.5625rem`), plus 45 inline `fontSize:` occurrences in `.tsx` (D-01 §2.3; inventory §2.4). Only 4 weights appear in `.less` (`bold` keyword ×9, `700`/`400`/`300` ×1 each) despite 500/600 being loaded from Google Fonts (D-01 §2.4). Line-height is essentially undeclared — one repo-wide `line-height: 3.9` and otherwise no scale (D-01 §2.5). The responsive root font-size is non-monotonic: `93.75%` at ≤1590px, `85.5%` at ≤1480px, `100%` at ≤1260px; because CSS cascade applies matching rules in source order, at ≤1260px all three rules match and `100%` wins, so the `85.5%` shrink only actually applies in the narrow 1261–1480px band (`trilhas-frontend:src/styles/globals.css:1-17`). No monospace family exists anywhere in the codebase (D-01 §2.1).

## Evident Rationale

*(Inferred — not stated anywhere in the legacy codebase or commit history reviewed.)* No design-system tooling existed at project start, and the codebase grew by component-level copy/paste rather than shared primitives (inventory §4; D-01 "Candidate ADR decisions" #5). Each feature author picked "a plausible 8px" or "a shadow that looks right" locally rather than checking for an existing convention, because no convention was ever named or enforced by lint/tooling. The px/rem mixing likely reflects multiple authors independently choosing whichever unit felt natural for a given rule, without an editorial pass reconciling them against the responsive root-font mechanism in `globals.css`.

## Assessment

**Strengths (surprisingly, given the lack of formalization):** the observed values are not random — they already cluster around an implicit 4/8px spacing rhythm and three de facto radius tiers (small/card/circular), so a named scale can be introduced with minimal visual regression (D-01 §3, §4.1). This is a low-risk, high-leverage rebuild opportunity, not a from-scratch design exercise.

**Weaknesses, with specific inconsistencies:**
- Unit inconsistency between literally-equal values (`8px`/`0.5rem`, `10px`/`0.625rem`, `12px`/`0.75rem`) is direct evidence the "scale" was never centralized — the same design decision was made twice, in two units, in two files (D-01 §4.1).
- Because px does not rescale with the responsive root-font-size zoom while rem does, the type ramp's px and rem families visually drift apart from each other at different viewport widths — a defect baked into the mixing, not just an aesthetic inconsistency (inventory §2.4).
- The non-monotonic root-font cascade (§2.2 above) is very likely an unintended interaction between three incrementally-added rules, not a deliberate design — it should be treated as a bug, not a baseline to reproduce (D-01 §2.2).
- Z-index and motion show pure "arms race" and "one-off" patterns respectively, with no coherent layering or timing story documented anywhere (D-01 §6, §9).
- No monospace family exists, which will matter for the new platform's tabular clinical values (vitals, labs, SOFA scores) where digit alignment aids fast scanning.

## Considered Options

1. **Do nothing / continue ad hoc literals.** Rejected — perpetuates the exact 7:1-literal-to-token sprawl documented above and blocks any future dark/light or density-variant work.
2. **Full formal token scales for all six dimensions** (spacing, radius, elevation, z-index, motion-duration, type), expressed as a single source of truth (e.g., a tokens JSON/YAML) generating both CSS custom properties and TypeScript constants, with an explicit px-vs-rem policy decided per dimension rather than mixed ad hoc.
3. **Partial adoption** — formalize only spacing and radius (the clearest, lowest-risk wins per the audit) now, deferring elevation/z-index/motion/type scales to later ADRs once component inventory work is further along.
4. **Adopt an existing off-the-shelf scale wholesale** (e.g., Tailwind's default spacing/radius/shadow/z-index scale) instead of deriving one from the legacy's implicit clusters.

## Decision Outcome

**Recommend Option 2** (full formal scales, single source of truth), informed by the legacy's implicit clusters rather than an unrelated off-the-shelf scale — pending team ratification. Concretely:

- Adopt an 8-point spacing scale (with a 4px half-step where the legacy data shows real half-step usage), expressed once and consumed everywhere.
- Adopt a 3-tier radius scale (small/card/circular) derived from the legacy's own clusters, resolving each `px`≡`rem` duplicate pair to a single representation.
- Formalize the neumorphic dual-shadow language as a proper elevation-token pair (e.g. `--shadow-elevated-dark` / `--shadow-elevated-light`) applied uniformly — this is a genuine, distinctive visual signature worth preserving (inventory §2.5, §8), just not worth re-copy-pasting per component.
- Adopt a small, named z-index scale (e.g., base/dropdown/overlay/modal/toast) sized to cover the legacy's observed range (up to `99999` for full-screen loading) without arbitrary gaps.
- Adopt a small set of named motion durations/easings (e.g., fast/base/slow) covering the legacy's `150ms`–`1s` range, replacing one-off keyframes with shared, reusable ones.
- Adopt a type scale with a bounded number of steps (not 20+), a defined weight set matching the fonts actually loaded (400/500/600), an explicit line-height scale, and — critically — **do not port the non-monotonic root-font-size percentages forward**; re-derive responsive type against real content using a monotonic `clamp()`-based or step-based approach. Add a monospace family for tabular clinical values (vitals, labs, SOFA/severity scores), which the legacy never had.
- Decide px-vs-rem deliberately per token dimension (not per component) and document the decision, since mixing them drifts silently under any responsive root-font zoom mechanism the new platform retains.

This favors a modern rebuild with an AI-agent-led workforce: agents generating or modifying UI code need an unambiguous, machine-readable token contract (JSON/YAML feeding both CSS and TypeScript) rather than tribal conventions an agent cannot infer from 20+ unscaled literals.

### Consequences

**Good:**
- Eliminates the literal-sprawl pattern (≈340:15 for colour; unbounded:0 for every other dimension) at its root, for both humans and AI agents generating new components.
- Preserves the legacy's genuinely good visual instincts (neumorphic elevation, implicit 4/8 rhythm) while making them uniform and governed instead of copy-pasted.
- Removes two concrete legacy defects outright: the non-monotonic root-font cascade and the unit-duplicated radius/spacing values.
- A single tokens source of truth prevents the "declared but never imported" governance failure seen with `variables.less` vs. `next.config.js` (inventory §2.1, §7).

**Bad:**
- Requires an upfront design pass to pick final scale values, which is real (if bounded) effort before any component work can proceed cleanly.
- Any component ported from the legacy will need every literal remapped to a token — a mechanical but non-zero migration cost across 126 co-located `.less` files' worth of precedent.
- Re-deriving responsive type against real content (rather than porting legacy percentages) means the new platform's type scale cannot simply copy the old one; it must be validated fresh, which risks a visual mismatch investigation phase.
