# 0005. Design-token source of truth and governance

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy `trilhas-frontend` codebase has almost no formal design-token
surface: exactly 15 Less variables, all declared in one file, are the
entirety of it (`trilhas-frontend:src/styles/variables.less:1-15`).
Everything else — 188 hex-literal occurrences across 153 `.less` files (77
distinct values), plus 119 more inline in `.tsx`/`.ts` — bypasses these
variables entirely, roughly a 7:1 ratio of literal color usages to
named-variable usages (inventory §2.1, §2.3). Within that already-thin
surface, the mechanism meant to carry those 15 values into the build is
itself broken, and the set contains dead entries plus a live undefined-variable
defect. This ADR addresses that specific governance defect, not the broader
literal-vs-token sprawl (covered elsewhere in the inventory).

## The Legacy Decision

The 15 Less variables are declared once in
`trilhas-frontend:src/styles/variables.less:1-15` (e.g. `@primary-color: #fe6d01;`,
`@success-color: #258a10;`, `@warning-color: #d6a400;`). The identical 15
key/value pairs are duplicated, value-for-value, as a plain JS object in
`trilhas-frontend:next.config.js:5-21` (e.g. `"@primary-color": "#fe6d01"`),
passed into `next-plugin-antd-less`'s `modifyVars` at build time. A
repo-wide grep for `@import.*variables` over `src` returns no
results — `variables.less` is never `@import`-ed, so `next.config.js` is the
sole live input and `variables.less` is an inert second copy.

Five of the fifteen tokens have zero references anywhere outside their own
declaration line: `@skeleton-text` (`#eee3`), `@degree` (`120deg`),
`@grad-perc` (`-100%`), `@header-opacity` (`0.8`), `@border-width` (`3px`)
(`trilhas-frontend:src/styles/variables.less:11-15`).

Separately, `trilhas-frontend:src/components/Display/Display.tsx:38-44`
reads `var(--warning-color)` for the warning-tag text color, but no code
sets a `--warning-color` custom property anywhere — not via JS (the only
runtime-set properties are `--primary-color`/`--primary-shadow-color`) and
not via a `:root` fallback. The property is permanently undefined, so the
warning treatment silently no-ops.

## Evident Rationale

*(Inferred.)* `next-plugin-antd-less`'s `modifyVars` requires a plain JS
object at config-evaluation time and cannot `@import` a `.less` file, so the
values were hand-copied into `next.config.js` to satisfy that constraint.
`variables.less` was likely kept as a human-readable reference (IDE/Less
tooling, documentation of "the tokens") without anyone noticing, or later
forgetting, it was disconnected from the build. The dead tokens
(`@degree`/`@grad-perc` especially) read as remnants of a removed
conic/radial-gradient feature pulled without pruning its variables. The
`--warning-color` gap plausibly copy-pasted the working `--primary-color`
pattern in `Display.tsx` without wiring up a setter.

## Assessment

**Strengths:** the token values themselves (brand orange, semantic
success/info/danger/warning) are reasonable, and the intent — one small,
named palette — is the right instinct for a system this thin.

**Weaknesses, all cited:**

- **Single-source-of-truth defect.** Two independently maintained copies of
  the same 15 values exist; only one is wired into the build, with nothing
  preventing further drift.
- **Dead-token debris.** A third of the declared set (5 of 15) has no
  consumer anywhere, indistinguishable from "not yet wired up" without
  manual audit.
- **Live undefined-variable defect.** `var(--warning-color)` silently
  no-ops because nothing ever sets it — a real bug in a clinical UI's
  warning indicator today.
- **No enforcement mechanism.** No lint, type check, or test would have
  caught either the drift risk or the undefined-variable bug; both surfaced
  only via manual audit.

## Considered Options

1. **Keep two hand-synced files**, cross-referenced by comment. Rejected —
   treats the symptom, still permits silent drift and the undefined-variable
   bug class.
2. **Single JS/TS module as source of truth** (e.g. `tokens.ts`), imported
   directly by the build config; generate a `:root` CSS-variables block from
   the same object. Simple in a Next/React stack, but ties the canonical
   definition to one language's syntax.
3. **Single tokens JSON/YAML file**, consumed by a small generator emitting
   (a) the build-time theme config and (b) a CSS custom-properties
   stylesheet (and TS constants if needed). One extra generation step, but
   language-agnostic and toolable (schema validation, docs, design-tool sync).
4. **Third-party design-token pipeline** (e.g. Style Dictionary) to own the
   JSON/YAML-in, multi-format-out step. Same shape as option 3, outsources
   the generator; adds a dependency but reduces bespoke tooling.

## Decision Outcome

**Recommended: Option 3 (tokens JSON/YAML as single source, generating both
build config and CSS variables), preferably implemented via Option 4 (Style
Dictionary or equivalent) rather than a hand-rolled generator.** This is a
recommendation pending team ratification.

Justification: the legacy failure was specifically "two copies of the same
values, only one real, nothing forcing agreement." A single declarative
file plus generation structurally prevents that — there is no second copy
to drift, because the derived artifacts are generated, not hand-maintained.
It also creates a natural place for automated governance: a test that (a)
fails the build if any `var(--x)` in source lacks a matching generated
definition, and (b) flags a declared token with zero consumers after a
grace period — catching both failure modes here before they ship. Do not
port the 5 dead legacy tokens without a concrete reintroduced use case.
This choice is framework-independent: any React/Next-style (or equivalent)
build can consume a generated config object and a generated CSS file alike.

### Consequences

**Good:**

- Exactly one place to edit a token value; build config and CSS variables
  are both generated, not hand-kept copies.
- A lint/test asserting every `var(--x)` has a matching definition would
  have caught the `--warning-color` bug at commit time, not audit time.
- Dead tokens become visible (zero-consumer reports) instead of silently
  accumulating.
- Sets up the token layer needed by later ADRs (severity-color governance,
  spacing/radius/elevation scales, per-tenant brand-color theming).

**Bad:**

- Adds a build-time generation step (and possibly a dependency) where the
  legacy had none — modest added build complexity.
- Requires a one-time migration of the 10 live legacy values into the new
  format and consumer updates.
- If the generator or its lint rule is skipped or misconfigured, the same
  drift risk can reappear in a new form — the governance test itself
  becomes load-bearing and must stay enforced in CI.
