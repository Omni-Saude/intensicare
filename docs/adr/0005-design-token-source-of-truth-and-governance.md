# 0005. Design-token source of truth and governance

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy `trilhas-frontend` codebase has almost no formal design-token
surface: exactly 15 Less variables, all declared in one file, are the
entirety of it (`trilhas-frontend:src/styles/variables.less:1-15`). Everything
else — 188 hex-literal occurrences across 153 `.less` files (77 distinct
values), plus 119 more inline in `.tsx`/`.ts` — bypasses these variables
entirely, a roughly 7:1 ratio of literal color usages to named-variable usages
(inventory §2.1, §2.3; d01-tokens.md §1.2).

Within that already-thin token surface, the mechanism that is supposed to
carry those 15 values into the build is itself broken: the values exist as
two independently maintained copies, only one of which is real, and the set
still contains dead entries and at least one live undefined-variable defect.
This ADR addresses that specific defect — token *source of truth and
governance* — not the broader literal-vs-token sprawl (covered elsewhere in
the inventory).

## The Legacy Decision

The 15 Less variables are declared once in
`trilhas-frontend:src/styles/variables.less:1-15` (e.g. `@primary-color:
#fe6d01;`, `@success-color: #258a10;`, `@warning-color: #d6a400;`). The
identical 15 key/value pairs are duplicated, value-for-value, as a plain JS
object in `trilhas-frontend:next.config.js:5-21` (e.g. `"@primary-color":
"#fe6d01"`), which is passed into `next-plugin-antd-less`'s `modifyVars` at
build time. A repo-wide grep for `@import.*variables` over `src` returns no
results — `variables.less` is never `@import`-ed by any `.less` file, so
`next.config.js` is the sole live input to the compiled CSS and
`variables.less` is an inert second copy.

Five of the fifteen tokens have zero references anywhere outside their own
declaration line: `@skeleton-text` (`#eee3`), `@degree` (`120deg`),
`@grad-perc` (`-100%`), `@header-opacity` (`0.8`), and `@border-width`
(`3px`) (confirmed by exhaustive grep of every `.less` file;
`trilhas-frontend:src/styles/variables.less:11-15`).

Separately, `trilhas-frontend:src/components/Display/Display.tsx:38-44`
reads `var(--warning-color)` for the warning-tag text color, but no code
anywhere sets a `--warning-color` CSS custom property — not via JS (the only
runtime-set custom properties are `--primary-color` and
`--primary-shadow-color`, per `useChangeColorTheme.ts`) and not via any
`:root` fallback rule. The property is permanently undefined at runtime, so
the warning treatment silently falls back to the CSS initial value.

## Evident Rationale

*(Inferred.)* `next-plugin-antd-less`'s `modifyVars` option requires a plain
JS object available at webpack-config evaluation time; it has no mechanism
to `@import` a `.less` file. The values were therefore hand-copied into
`next.config.js` to satisfy that constraint. `variables.less` was most
likely retained as a human-readable reference — for IDE Less-language-server
support, or as documentation of "the tokens" — without the author realizing,
or later forgetting, that it was disconnected from the actual build. The 5
dead tokens (`@degree`, `@grad-perc` in particular) read as remnants of a
removed conic/radial-gradient feature that was pulled without also pruning
its variables. The `--warning-color` gap is plausibly a copy/paste of the
working `--primary-color` pattern in `Display.tsx` that was never wired up
on the setter side.

## Assessment

**Strengths:** the token *values themselves* (brand orange, semantic
success/info/danger/warning) are reasonable and the intent — one small,
named palette — is the right instinct for a design system this thin.

**Weaknesses, all cited:**
- **Single-source-of-truth defect.** Two independently maintained copies of
  the same 15 values exist (`variables.less` vs. `next.config.js`); only one
  is wired into the build, and nothing prevents them from drifting further
  apart than they already implicitly could.
- **Dead-token debris.** A third of the declared set (5 of 15) has no
  consumer anywhere in the codebase, adding noise with no way to
  distinguish "unused because removed" from "unused because not yet wired
  up" without manual investigation.
- **Live undefined-variable defect.** `var(--warning-color)` in
  `Display.tsx` silently no-ops because nothing ever sets the custom
  property — a real, currently-shipping bug in a clinical UI's warning
  indicator.
- **No enforcement mechanism.** Nothing in the build (lint, type check, or
  test) would have caught either the drift risk or the undefined-variable
  bug; both were only found by manual/audit-level inspection.

## Considered Options

1. **Keep two hand-synced files**, add a comment in each pointing at the
   other. Rejected — treats the symptom, not the cause; still permits
   silent drift and does nothing about the undefined-variable class of bug.
2. **Single JS/TS module as source of truth** (e.g. `tokens.ts` exporting a
   plain object), imported directly by the build config; generate a `:root`
   CSS-variables block from the same object at build or via a small script.
   Straightforward in a Next.js/React stack, no new file format, but ties
   the canonical definition to one language's syntax.
3. **Single tokens JSON/YAML file as source of truth**, consumed by a small
   generator that emits (a) the build-time theme config object and (b) a
   CSS custom-properties stylesheet (and, if a component library needs it,
   TypeScript constants). Adds one generation step but keeps the token
   definition language-agnostic and toolable (schema validation, docs
   generation, design-tool sync).
4. **Adopt a third-party design-token pipeline** (e.g. Style Dictionary) to
   own the JSON/YAML-in, multi-format-out step instead of a bespoke script.
   Same shape as option 3 but outsources the generator; adds a dependency
   but reduces bespoke tooling to maintain.

## Decision Outcome

**Recommended: Option 3 (tokens JSON/YAML as single source, generating both
build config and CSS variables), with Option 4 (Style Dictionary or
equivalent) as the preferred implementation rather than a hand-rolled
generator.** This is a recommendation pending team ratification.

Justification: the legacy failure mode was specifically "two copies of the
same values, only one of which is real, with no mechanism forcing them to
agree." A single declarative file plus a generation step structurally
prevents that failure — there is no second copy to fall out of sync,
because the second artifact is derived, not hand-maintained. It also gives
the new platform a natural place to add automated governance: a test or
lint rule that (a) fails the build if any `var(--x)` in source references a
token name absent from the generated CSS-variable set, and (b) fails if a
declared token has zero consumers after a grace period, catching both
failure modes this ADR documents before they ship. Do not port the 5 dead
legacy tokens (`@skeleton-text`, `@degree`, `@grad-perc`, `@header-opacity`,
`@border-width`) into the new token set without a concrete reintroduced use
case.

This choice is independent of framework: any React/Next-style (or
equivalent) build can consume a generated JS/TS config object and a
generated CSS file equally well.

### Consequences

**Good:**
- Exactly one place to edit a token value; the build config and the CSS
  custom properties are both generated artifacts, not hand-kept copies.
- A lint/test can assert every `var(--x)` reference has a matching
  generated definition, which would have caught the `--warning-color` bug
  at commit time rather than at audit time.
- Dead tokens become visible (zero consumers reported by the same tooling)
  instead of silently accumulating.
- Sets up the token layer needed by later ADRs (severity-color governance,
  spacing/radius/elevation scales, per-tenant brand-color theming) without
  further plumbing changes.

**Bad:**
- Adds a build-time generation step (and a dependency, if Style Dictionary
  or similar is adopted) where the legacy had none — a small increase in
  build complexity and one more thing to keep working in CI.
- Requires an initial migration effort to move the 10 live legacy values
  (and any newly needed tokens) into the new format and update all
  consumers, though this is a one-time cost.
- If the generator or its lint rule is skipped/misconfigured, the same
  drift risk reappears in a new form — the governance test itself becomes
  load-bearing and must be kept in CI, not just in local tooling.
