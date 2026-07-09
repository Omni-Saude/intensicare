# 0015. Config/schema-driven dynamic clinical form engine

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's clinical documentation spans roughly 14 distinct roles/screens — nursing,
physiotherapy, pharmacy, nutrition, psychology, music/speech therapy, physician notes,
patient admission/discharge, movement/transfer, intercurrence, and fluid balance — each
needing overlapping-but-distinct structured fields, nested sections, and conditionally
relevant sub-sections. The legacy platform answered this with a single generic form
*engine* driven by data configs rather than one hand-built form per role. Any rebuild
must decide whether to keep a config/schema-driven engine as the foundation for clinical
documentation, and if so, how to fix the typing, conditional-field, and multi-step gaps
the audit found (inventory §3.3, §5.3; D-02 §3.3; D-03 §6).

## The Legacy Decision

- `FormDadosProntuario` is the entry point: it takes a `Models.DadosFormDinamico[]`
  **config array** (not markup) plus `initialValues`, and renders a single AntD `Form`
  wrapping a recursive `CollapsedFields` tree. It also owns a `nullStatus`/`nullifyFields`
  mechanism that walks the submitted values and nulls out whole sub-objects/arrays when a
  group's "annul" switch is off, and unconditionally renders a static SOFA-score `Tag`
  (`color="warning"` regardless of score). `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:1-111`
- `CollapsedFields` renders each config group as an AntD `Collapse.Panel`, recursing into
  either nested `subGroup`s, a flat `campos` array, or a fully custom injected `Fieldset`
  component reference carried directly in the config data.
  `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:1-111` (D-02 §3.3)
- `SelectCampoType` is the field-type dispatcher: `campo.type` ∈ `{string, select,
  interval, number, boolean, checkbox, data, list, masked, multicheck}`, each mapped to
  one of **10 typed `SubForm*` renderers**.
  `trilhas-frontend:src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx:1-177`
- **14 config files** instantiate the engine for the different clinical roles/screens:
  `dataFormEnfermagem`, `dataFormFisioterapeuta`, `dataFormFonoaudiologo`,
  `dataFormFormularioMedico`, `dataFormFarmaceutico`, `dataFormMusicoterapia`,
  `dataFormNutricionista`, `dataFormPsicologo`, `dataFormTecEnfermagem`,
  `dataFormPaciente`, `dataFormMovimentacao`, `dataFormRemovePaciente`,
  `dataFormIntercorrencia`, `dataFormBalancoHidrico`. `trilhas-frontend:src/utils/dataForms`
  (D-02 §3.3, 14 configs)
- No AntD `Steps` wizard component exists anywhere in the codebase. "Multi-step" is
  simulated by three uncoordinated mechanisms: accordion sections (`CollapsedFields`,
  each `grupo` a `Collapse.Panel`), tabs inside a drawer for movement history vs.
  new-entry, and sequential drawers per action (choose evolução type → drawer opens the
  specific form). `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:1-111`
  (D-03 §6.1, §6.2)
- Conditional fields are handled by **three separate, unshared mechanisms**: (1) a
  group-level "nullify" `Switch` that only nulls the *submitted value* via
  `nullifyFields`, leaving fields mounted and interactive; (2) a sub-group `checavel`
  `Switch` in `SubGroupHandle` that toggles a sub-group's fields via inline
  `display: none`/`"block"`, keeping them mounted in the AntD form tree; (3)
  permission/tenant-type-driven field disabling elsewhere in the form catalog (e.g.
  `FormLeito` disables fields unless the tenant is of a given type).
  `trilhas-frontend:src/components/FormDadosProntuario/SubGroupHandle/SubGroupHandle.tsx:32-91`
  (D-03 §6.3)

## Evident Rationale

*(Inferred — not stated in the codebase.)* With roughly 14 clinical roles needing
overlapping-but-distinct structured documentation — nested groups, nullable sections, ten
different field types — a config-driven engine avoids writing and maintaining one
hardcoded form per role; new fields are added by editing a `dataForm*.ts` object rather
than writing new JSX. The `nullifiers`/`checavel` conditional mechanisms plausibly grew
independently because they were solving different problems (an entire clinical section
not applying to a patient, vs. a sub-group's relevance depending on another answer, vs.
tenant/permission-driven visibility) with no one stepping back to unify them. The absence
of a `Steps` wizard is consistent with the engine's group-oriented structure: accordion
panels were the natural container for named field groups, and true linear workflows
(movement history vs. new entry) were solved with tabs instead of extending the engine.

## Assessment

**Strengths:**

- This is the strongest, most valuable IP in the legacy frontend: one rendering
  architecture serves 14 clinical roles/screens, and extending clinical documentation
  means editing config data, not writing new components.
  `trilhas-frontend:src/utils/dataForms`
- The field-type dispatch is centralized and typed by `campo.type`, giving a single,
  auditable place (`SelectCampoType`) to see every supported input shape.
  `trilhas-frontend:src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx:1-177`
- The engine already supports arbitrary escape hatches (`Fieldset` injection) for cases
  the generic renderers can't express, avoiding a rigid all-or-nothing schema.

**Weaknesses:**

- **No shared conditional-field abstraction.** The nullify-switch, the `checavel`
  display-toggle, and RBAC/tenant-driven disabling are three independently hand-rolled
  mechanisms with different semantics (null-on-submit vs. hide-but-mount vs.
  disable-or-omit) and no common rule engine.
  `trilhas-frontend:src/components/FormDadosProntuario/SubGroupHandle/SubGroupHandle.tsx:32-91`
- **Configs are weakly typed.** The engine's `dadosFormProntuario` configs are typed as
  `Models.DadosFormDinamico[]` but individual field/config authoring in practice relies on
  loose/`as any`-shaped objects (inventory §3.3), so a malformed 15th config would not be
  reliably caught at compile time.
- **The "nullify" switch only nulls the submitted value**, not the field's mounted state —
  the fields stay interactive in the UI while flagged for nulling, which is a subtle
  UX/data-integrity gap (a user can fill in a section, flip the switch, and lose the
  reason why without an explicit warning).
  `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:1-111`
- **No wizard/stepper semantics.** Multi-step is simulated via accordion + tabs +
  sequential drawers with no shared step-progression, validation-per-step, or
  save-and-resume model; each mechanism was reached for ad hoc rather than as a
  considered workflow decision. (D-03 §6.2)
- **The SOFA score display is a static `"warning"` tag regardless of the actual score**,
  demonstrating that even inside this well-factored engine, per-value severity was never
  wired through generically. `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:85-94`

## Considered Options

1. **Lift and shift**: port the engine's shape (config array → group/field dispatch)
   as-is, keeping loose typing and the three conditional mechanisms. Rejected — carries
   forward the exact typing and conditional-logic fragmentation the audit flags as the
   main risk.
2. **Re-hardcode per role**: abandon the config-driven approach and hand-build ~14
   separate forms in the new stack. Rejected — discards the platform's strongest reusable
   IP and reintroduces the N-hardcoded-forms maintenance burden the legacy engine was
   built to avoid.
3. **Modernize the engine**: keep the config/schema-driven architecture, but (a) define a
   strongly-typed config schema (e.g. a shared TypeScript/Zod or JSON-Schema definition,
   ideally shareable with the backend/FHIR-mapping layer so clinical field configs and API
   payload shapes can't drift), and (b) unify the three conditional-field mechanisms
   (nullify switch, sub-group visibility toggle, permission-driven disabling) into a
   single visibility/nullability rule engine driven by declarative conditions in the
   config itself.
4. **Modernize the engine and adopt true wizard/stepper semantics** for the currently
   accordion/tab/drawer-simulated multi-step flows, in addition to (3).

## Decision Outcome

Recommend **Option 3**, with Option 4 deferred pending clinical-workflow validation. The
config/schema-driven engine is this codebase's most valuable pattern and should be
preserved and modernized, not re-hardcoded: build a strongly-typed config schema (shared
with the backend/FHIR-mapping layer where possible) and a single visibility/nullability
rule engine that replaces the nullify-switch, `checavel` display-toggle, and permission
gating with one declarative mechanism. Whether the new platform also needs true
`Steps`-wizard semantics, versus continuing to organize clinical documentation into
collapsible groups, is a workflow question that should be validated directly with
clinical users rather than assumed — the legacy accordion-based structure is not
inherently wrong, only its multi-step *simulation* (three uncoordinated mechanisms) is.
This is a recommendation pending team ratification, including the concrete schema
technology choice and whether a wizard is actually wanted.

### Consequences

**Good:**

- Fourteen-plus clinical roles/screens continue to share one engine and one field-type
  catalog, keeping the addition of new fields/roles a config change, not a new-component
  change.
- A strongly-typed, shareable config schema catches malformed configs at compile/build
  time and gives the backend/FHIR-mapping layer a single source of truth for field shape,
  closing the "as-any configs" gap the audit flags.
- A unified visibility/nullability rule engine removes an entire class of bugs where a
  field's "doesn't apply" state is expressed inconsistently (nulled-on-submit vs.
  hidden-but-mounted vs. disabled), and makes new conditional logic declarative instead of
  hand-rolled per form.

**Bad:**

- Designing and migrating to a new config schema and a unified rule engine is real,
  non-trivial upfront work with no drop-in equivalent to port from the legacy code.
- All 14 existing config shapes need to be re-authored (or auto-migrated) against the new
  schema, which is a sizeable, if mechanical, one-time migration cost.
- Deferring the wizard/stepper question means the new platform may temporarily inherit
  the same accordion/tabs/drawers "simulated multi-step" feel until clinical workflow
  validation lands, rather than resolving it in this decision.
