# ADR-DRAFT: Clinical form-engine stack

Status: **draft, pending ratification**
Date: 2026-07-04
Author: frontend-architect (v2 design phase)

## Context and Problem Statement

`ADR-0015` (legacy audit) identifies `FormDadosProntuario` — a config-driven engine that dispatches a
typed field-config array (`DadosFormDinamico[]`) across 10 field-type renderers (string, select,
interval, number, boolean, checkbox, data, list, masked, multicheck) — as "the strongest, most
valuable IP in the legacy frontend," backing 14 role-specific clinical documentation forms (nursing,
physiotherapy, speech therapy, physician, pharmacy, music therapy, nutrition, psychology, tech-
nursing, admission, movement, patient removal, intercurrence, fluid balance). The audit also found
concrete defects to fix, not port: configs are loosely/`as any`-typed despite a declared type
(`ADR-C-10`/`CON-0043`); conditional-field visibility/nullability is implemented via three separate,
unshared mechanisms (a group-level nullify switch that nulls the *submitted* value while leaving the
field mounted — a data-integrity gap; a sub-group `checavel` switch using `display:none` while still
mounted; and permission/tenant-type disabling); there is no `Steps` wizard anywhere, with multi-step
flows simulated inconsistently via accordion, tabs, or sequential drawers.

v2 must decide the concrete schema technology and runtime-validation stack for re-authoring these 14+
configs, and settle the conditional-field/visibility model as one governed mechanism instead of three.

## Decision Drivers

- `ADR-C-10`/`CON-0043`: form field configs MUST be validated against a strongly-typed schema so a
  malformed config is caught at compile/build time, not at runtime.
- `DES-C-07`: preserve the config/schema-driven pattern as reusable IP — do not re-hardcode per-role
  forms as bespoke markup.
- The audit's data-integrity finding on `nullifyFields`: a mechanism that nulls a *value* while
  leaving the *field* mounted and interactable is a live bug shape (a user can still see/edit a field
  whose value will be silently discarded on submit) that v2 must not reproduce.
- Clinical forms feed data that must ultimately reconcile with the FHIR-based data model used
  elsewhere in the platform (`vision.json` §4 AMH Data Platform, FHIR R4) — the schema technology
  should be able to express a validation contract that a backend/FHIR-mapping layer can also consume
  or at least cross-check against, per the brief's instruction that the config schema be "shared
  w/ backend/FHIR layer" (`ADR-0015` Recommend clause).
- `open_questions` in `design-adrs.json`: "config-schema technology choice; whether a Steps-wizard is
  wanted" is explicitly left open by the audit for the rebuild to decide.

## Considered Options

1. **Keep configs as plain TypeScript object literals with hand-written interfaces (status quo
   pattern, typed "for real" this time).** Rejected as insufficient on its own: a hand-written
   interface only catches *shape* errors that TypeScript's structural typing happens to catch, not
   *value*-level invariants (e.g., "an `interval` field's `min` must be less than its `max`", "a
   `masked` field's mask pattern must be a valid regex") — exactly the class of error that let the
   legacy's `as any` typing slip through undetected.
2. **JSON Schema + a generic form-renderer library** (e.g., `react-jsonschema-form` or a hand-rolled
   equivalent). Rejected: JSON Schema's validation vocabulary is a weaker fit for TypeScript-native
   authoring (config authors are frontend engineers, not a separate JSON-authoring audience per the
   legacy's own pattern of 14 TS config files), and round-tripping JSON Schema into TS types adds a
   codegen step for no clear benefit over option 3.
3. **TypeScript-native schema with `zod`, config objects authored as `z.infer`-typed TS, validated at
   both build time (type-check) and runtime (config-loading + form-submission boundaries).** Chosen.
   `zod` schemas double as the runtime validator at the exact two points that matter: (a) when a
   config is loaded (catching a malformed config before it ever renders, closing `ADR-C-10`'s "compile
   or build time, not runtime" requirement — a `zod`-validated config that fails validation fails the
   build/CI, not a clinician's screen), and (b) when a form submits (catching a value that violates a
   field's declared constraint before it reaches the API). `zod`'s TS-native authoring keeps the
   14-config-file pattern the legacy already had, so re-authoring cost is about redefining
   field-level constraints, not learning a new configuration language.
4. **A dedicated forms DSL/compiler (custom).** Rejected: unscoped, unbounded engineering investment
   for a problem `zod` + typed React already solves; no evidence in the audit that the legacy's
   TS-object-array pattern itself was the problem (it is explicitly praised) — only its typing
   rigor and conditional-visibility mechanism were flagged.

## Decision Outcome

Adopt **Option 3**: a `zod`-schema-backed, TypeScript-native config engine.

- **Schema layer:** each of the 10 field types (string, select, interval, number, boolean, checkbox,
  date, list, masked, multicheck — carried forward from the legacy's proven type set) has a `zod`
  schema describing both its config shape (e.g., an `interval` field's config requires `min < max`)
  and, where applicable, its submitted-value shape. A config file is a typed array validated against
  a discriminated-union `zod` schema at load time; CI runs this validation against every one of the
  14+ role configs on every change — a malformed config fails CI, never reaches a clinician.
- **One conditional-visibility/nullability mechanism**, replacing the legacy's three: a declarative
  `visibleWhen` / `nullableWhen` predicate per field or group, evaluated from current form state by
  one shared rule-engine hook (`useFieldVisibility`). A field that is not visible is **unmounted**,
  not merely `display:none`'d — closing the legacy's `checavel`-switch gap where a hidden field
  remained interactable. A field whose value will be nulled on submit is visually indicated as such
  (disabled + a "não será salvo" affordance) rather than silently discarding input after the fact —
  closing the `nullifyFields` data-integrity gap directly.
- **Steps wizard:** deferred, per `ADR-0015`'s own recommendation ("defer Steps-wizard pending
  workflow validation") — v2 ships the same accordion/tabs/sequential-drawer *presentation* options
  the legacy used (now backed by the single `OverlayStack` manager, `component-library.md` §5.9,
  instead of uncoordinated drawer stacking), leaving a true multi-step wizard as a future option once
  clinical workflow validation calls for it.
- **FHIR alignment:** field-level `zod` schemas are authored with an explicit mapping annotation
  (`fhirPath` or equivalent) where a field corresponds to a FHIR Observation/Condition/
  MedicationAdministration element, so the schema can be cross-checked against the backend/FHIR layer
  without requiring the two to share a single generated artifact on day 1 — a lighter-weight version
  of the "shared w/ backend/FHIR layer" recommendation, appropriate to how far the backend data model
  is currently specified.

### Consequences

**Good:**
- Directly closes `ADR-C-10`/`CON-0043`: malformed configs fail CI, not runtime.
- Directly closes both named legacy conditional-field defects (nullify-while-mounted,
  `checavel`-hidden-but-interactable) with one governed mechanism instead of three unshared ones.
- Re-authoring cost is bounded and estimable: 14+ existing configs map field-by-field onto the new
  typed schema; no new authoring paradigm for the team to learn.
- `zod`'s TS inference means the same schema drives both compile-time types and runtime validation —
  no risk of the two drifting apart the way the legacy's declared-but-unenforced `as any` type did.

**Bad:**
- Re-authoring 14+ configs against stricter schemas is real, non-trivial migration work (the audit's
  own estimate: "14 configs need re-authoring, real migration cost") — this ADR does not reduce that
  cost, only makes the result more robust.
- A discriminated-union schema across 10 field types plus group/sub-group nesting is a nontrivial
  `zod` schema to design well; getting the ergonomics wrong (verbose config authoring) could tempt
  future authors back toward loosely-typed shortcuts if not paired with good authoring tooling
  (editor autocomplete via inferred types, a config-authoring lint).
- Deferring the Steps wizard means multi-step flows remain visually non-linear (accordion/tabs/
  drawers) for v2's initial ship — acceptable per the audit's own recommendation, but a known UX gap
  to revisit.

## Open questions for ratification

1. Whether `fhirPath` annotations should be a required field on every clinically-mapped schema entry
   from day 1, or added incrementally — depends on how far `amh-integration-architect`'s FHIR mapping
   work has progressed when form re-authoring begins.
2. Whether a Steps wizard should be revisited for any specific high-friction config (e.g., admission)
   ahead of the general "defer" posture — a workflow-validation question, not resolved here.
3. Config-authoring developer-experience tooling (schema-to-form-builder GUI vs. hand-authored TS) is
   out of scope for this ADR — flagged for a future tooling-investment decision if the 14-config
   re-authoring proves to be a bottleneck.
