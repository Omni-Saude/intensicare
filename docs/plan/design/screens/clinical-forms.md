# IntensiCare v2 — Schema-Driven Clinical Form Engine

Deliverable of the **form-engine-designer**. Specifies the v2 clinical documentation engine that
replaces the legacy `FormDadosProntuario` config engine: a **single zod schema source** shared
backend↔frontend, **one unified visibility/nullability rule engine**, **auditable annulment** (a
voided answer is retained, never deleted), **offline-safe drafts**, and **form versioning**. It
carries every per-discipline PT-BR vocabulary forward **verbatim** (accents included) and corrects
**only** the audit-flagged copy-paste drift, each citing its disposition.

**Modernizes** audit `ADR-0015` (config-driven dynamic clinical form engine), whose design-authority
disposition is **ADAPT** — *"preserve the config-driven intent... while correcting the as-any typing
and the three uncoordinated conditional-field mechanisms per constraint ADR-C-10"* (`design-adrs.yaml`
adr `0015`).

**Inputs read in full:**
`docs/plan/_work/dispositions/formularios-clinicos-p1.yaml` (RULE-001…023),
`docs/plan/_work/dispositions/formularios-clinicos-p2.yaml` (RULE-024…045),
`docs/plan/_work/dispositions/evolucoes-p1.yaml` (RULE-001…039),
`docs/plan/_work/dispositions/evolucoes-p2.yaml` (RULE-040…077),
`docs/plan/_work/briefs/clusters/formularios-clinicos.json`,
`docs/plan/_work/briefs/clusters/evolucoes.json`,
`docs/plan/_work/dispositions/design-adrs.yaml` (adr `0015`),
`docs/adr/0015-config-driven-dynamic-clinical-form-engine.md`,
`docs/plan/_work/constraints/ledger.yaml` (`CON-0043`/`ADR-C-10`).

**Traceability.** Every load-bearing decision cites a `RULE-<CLUSTER>-NNN` disposition, a `CON-xxxx`/
`ADR-C-xx` constraint, or `ADR-0015`. RULE ids without a cluster prefix belong to `evolucoes`;
`FC-NNN` abbreviates `RULE-FORMULARIOS-CLINICOS-NNN`; `EV-NNN` abbreviates `RULE-EVOLUCOES-NNN`.
Calls this document makes beyond a settled disposition are flagged **[DECISION]**. Items whose
clinical semantics a disposition sent to committee are flagged **[RATIFY]** and are *not* decided
here — they are surfaced with their `RAT-*` id in §12.

---

## 1. Goals and non-negotiables

| # | Goal | Source |
|---|---|---|
| G1 | One config/schema-driven engine serves all ~14 discipline forms; adding a field is a schema edit, not a new component. | `ADR-0015` (Option 3), `DES-C-07` |
| G2 | Field configs are validated against a **strongly-typed schema (zod), not `as any`** — a malformed config fails at build/compile time, not runtime. | `CON-0043` / `ADR-C-10` |
| G3 | **One** declarative visibility/nullability rule engine replaces the legacy's three uncoordinated mechanisms (nullify switch, `checavel` display-toggle, RBAC disabling). | `ADR-0015` weakness §1; EV-021, EV-049, EV-050, EV-064, EV-065 |
| G4 | A voided/annulled answer is **auditable, not deleted** — the prior value and its who/when survive in an immutable trail. | EV-074 **[RATIFY]**, EV-049; `ADR-0015` weakness (nullify "loses the reason why") |
| G5 | The zod schema is the **single source of truth shared backend↔frontend** (and the FHIR-mapping layer), so config and API payload shapes cannot drift. | `ADR-0015` Decision Outcome; `CON-0043` |
| G6 | Per-discipline PT-BR vocabularies are carried **verbatim, accents included**; the audit-flagged copy-paste drift is the **only** thing corrected. | Mission; FC-001…045, EV-031…041, EV-076 |
| G7 | Drafts (`salvo`) are offline-safe and author-private; the 3-state lifecycle and its integrity invariants are preserved. | EV-042, EV-007, EV-051, EV-052 |
| G8 | Every form schema is **versioned**; a record renders against the schema version it was authored under. | `ADR-0015` migration cost; ledger `clinical_scores.algorithm_version`, Gold-schema-versioning constraints |

---

## 2. Single source of truth — the zod `Campo` schema

The legacy engine's core contract is the `Campo`/`CampoType` shape — *"required/min/max/regex/mask/
conditions/formList/disabledOnEdit... the declarative engine contract that the v2 clinical-forms
schema should adopt as its baseline field-definition shape"* (**EV-072**, ADOPT). v2 re-expresses that
contract as a **zod schema**, authored once and consumed by both tiers.

```ts
// packages/clinical-schema/src/campo.ts — the ONE source of truth (G2, G5, CON-0043)
import { z } from "zod";

/** 11 field types — the FULL declared vocabulary, all dispatched (fixes EV-023). */
export const CampoType = z.enum([
  "string", "select", "interval", "number", "boolean",
  "checkbox", "data", "list", "masked", "multicheck",
  "time",                       // ← 11th type: declared in legacy union but never dispatched
]);                             //   (EV-023, ESC-P3-160 ADOPT-CORRECTED). Backs the optional
                                //   HH:MM exit-time field duplicated across 9 forms (FC-041).

export const CondOp = z.enum(["eq", "in", "truthy", "gte", "lte"]);   // §3

export type Campo = z.infer<typeof Campo>;
export const Campo: z.ZodType<Campo> = z.lazy(() =>
  z.object({
    name:        z.string(),
    label:       z.string(),                 // PT-BR display label, accents verbatim (§10)
    type:        CampoType,
    required:    z.boolean().default(false), // required-if gate (EV-071)
    min:         z.number().optional(),      // inclusive bound / min selections / list floor
    max:         z.number().optional(),      // inclusive bound / max selections / list cap
    regex:       z.string().optional(),      // masked-field pattern (EV-069, FC-041)
    mask:        z.string().optional(),
    options:     z.array(z.object({ value: z.string(), label: z.string() })).optional(),
    conditions:  z.array(RuleClause).optional(),   // unified rule engine (§3) — replaces EV-021/049/050
    anulavel:    z.boolean().default(false),       // group is annullable (§4, EV-074)
    formList:    z.object({ item: z.lazy(() => z.array(Campo)) }).optional(), // repeatable (EV-070)
    subGroup:    z.array(z.lazy(() => Campo)).optional(),
    disabledOnEdit: z.boolean().default(false),    // immutable-after-create (EV-059, EV-064)
  }),
);

export const FormSchema = z.object({
  formId:        z.string(),                 // e.g. "evolucao.medico"
  schemaVersion: z.string(),                 // semver, pinned into every record (§7)
  discipline:    ProfessionalRole,           // §10.1 (EV-062 corrected enum)
  sections:      z.array(Campo),
});
```

**Sharing contract (G5).** `packages/clinical-schema` is imported by the Next.js app **and** by the
API service. The API validates inbound payloads with the same `FormSchema.parse`; the FHIR-mapping
layer derives `Observation`/`QuestionnaireResponse` shapes from the same field definitions. There is
no second, hand-maintained config type — the `as any` gap the audit flagged (`ADR-0015` weakness,
`CON-0043`) is closed structurally: a malformed config does not type-check.

**Runtime stack.** On the client the zod schema drives form state via **react-hook-form** with a zod
resolver, the stack the design-authority disposition names — *"react-hook-form + zod powering a
schema-driven clinical form engine"* (`design-adrs.yaml` adr `0015`, ADAPT). The same schema is the
resolver's validation contract and the API's `parse` contract, so field-level rules (§5) are declared
once. The concrete library-version/packaging choices are owned by the peer stack-choice ADR draft
(`form-engine-stack.md`, Option 3 — zod TS-native schema), referenced, not re-decided here.

**Field-type coverage (EV-023, ADOPT-CORRECTED, ESC-P3-160).** The legacy `CampoType` union declared
11 types but `SelectCampoType` dispatched only 10, silently dropping `time`. v2 dispatches **all 11**;
`time` renders the optional `00:00` 24h-or-empty masked input that FC-041 found duplicated verbatim
across nine discipline forms (`^([01]\d|2[0-3]):[0-5]\d$|^$`).

---

## 3. The one unified visibility / nullability rule engine (G3)

The legacy had **three independent, unshared** conditional mechanisms with divergent semantics
(`ADR-0015` weakness; also EV-021/022/049/050/064/065): (1) a group **nullify switch** (nulls the
submitted value only, fields stay mounted and interactive — the data-integrity gap), (2) a sub-group
`checavel` switch (`display:none`, still mounted), and (3) RBAC/tenant-type field disabling. v2
collapses all three into **one declarative rule set** evaluated by a single interpreter.

### 3.1 Declarative clause shape

`campo.conditions` is a list of clauses; a clause names a governing field, an operator, a match value,
and the **effect** on the target field. This generalizes the legacy `conditions` map keyed by a
governing field's value (**EV-073**, ADOPT — *"the correctly-specified conditional/dependent field
visibility mechanism"*; **EV-021**, ADAPT — the `select/boolean/checkbox/multicheck` reveal pattern).

```ts
export const Effect = z.enum(["show", "require", "disable", "nullify"]);
export const RuleClause = z.object({
  when:   z.string(),        // governing field name
  op:     CondOp,            // eq | in | truthy | gte | lte
  value:  z.unknown().optional(),
  effect: Effect,
});
```

| Effect | Semantics | Replaces legacy mechanism | Disposition |
|---|---|---|---|
| `show` | Field is mounted+visible **iff** clause matches; hidden fields are unmounted (not `display:none`). | `checavel` display-toggle; `SubGroup` reveal | EV-050 (ADAPT), EV-073 (ADOPT) |
| `require` | Field becomes `required` only when clause matches (required-if). | ad hoc per-form logic | EV-021, EV-071 (ADOPT) |
| `disable` | Field is read-only when clause matches; composes with the baseline disable rule (§3.3). | RBAC/tenant `FormLeito` disabling; `disabledOnEdit` | EV-064 (ADOPT) |
| `nullify` | On submit, an out-of-scope field's value is **nulled AND its prior value routed to the annulment trail** (§4), never silently dropped. | group nullify switch | EV-049 (ADAPT), EV-074 |

**One evaluator, one order.** The interpreter resolves clauses deterministically: `show` first
(unmounted fields never validate and never submit a value), then `require`, then `disable`, then — at
submit — `nullify`. This is the single rule engine `ADR-0015` Option 3(b) mandated.

### 3.2 Nullify is non-destructive by default (G3→G4 bridge)

Legacy `nullifyFields` recursively replaced an annulled group's value with `{}` or `[]` per its
declared type (**EV-049**, ADAPT — *"a sound, well-specified implementation of the soft-void concept...
the concrete submit-time behavior should carry forward"*), and the sub-group toggle set the subgroup
value to `null` when disabled, defaulting ON only when data already exists (**EV-050**, ADAPT). v2
keeps that submit-time shape (empty container per declared type) **but** never discards the prior
content: whenever `nullify` fires on a field that previously held a value, the old value is captured
into the annulment trail (§4). This closes the `ADR-0015` weakness where a user *"can fill in a
section, flip the switch, and lose the reason why without an explicit warning."*

### 3.3 Field disable semantics (baseline)

Baseline read-only state is `disableAll = disabledOnEdit || mode === "view" || isNullified`
(**EV-064**, ADOPT — the reference semantics). The legacy `SubFormString` **inverted** `isAnnulled`
(disabling when a group was *not* annulled, the opposite of every sibling) and could throw when the
nullifier was missing; v2 aligns every field type to the single `disableAll` expression above
(**EV-065**, ADOPT-CORRECTED, ESC-P3-163).

### 3.4 Retired dead conditional paths

- **EV-022** (RETIRE, ESC-AMBIGUOUS-327): the legacy `SubFormCheckbox` keyed conditions off
  `e.target.value` on an antd `Checkbox`, which only ever carries `e.target.checked`, so the lookup was
  always `undefined` and **no conditional field ever rendered through this path**. There is no working
  behavior to preserve; the correct pattern is the unified engine above (EV-021/073).

---

## 4. Annulment — auditable, not deleted (G4)

The legacy type shapes (`anulavel`, `nullifiers`) *"strongly suggest a medical-legal audit-trail
pattern (void rather than delete)"* but **no code in the audited partition actually set `isAnnulled`
or read `anulavel`** — so the *semantics* are escalated, not decided here: **EV-074 → RATIFY,
`RAT-EVOLUCOES-01` (ESC-AMBIGUOUS-329)**. This section specifies the engine's mechanism so that,
**once ratified**, it is a config flag rather than a redesign; it does not pre-empt the committee's
call on whether/where annulment applies clinically.

**Design [DECISION], contingent on `RAT-EVOLUCOES-01`.** A group with `anulavel: true` renders an
annul control. Annulling does **not** delete: it

1. writes an **annulment event** to an append-only trail —
   `{ recordId, formId, schemaVersion, fieldPath, priorValue, annulledBy, annulledAt, reason }`;
2. sets the active record's field to the empty container for its declared type (EV-049 shape); and
3. is itself immutable and never physically removed.

This satisfies G4 and is consistent with the cluster's medical-legal recordkeeping invariants:
`inativo` records are immutable (**EV-051**, ADOPT, CFM NGS-2 / VIS-C-07) and edits are author-only
(**EV-052**, ADOPT) — annulment is the *field-level* analogue of the *document-level* `inativo`
void. A `reason` is required at annul time (this is the "explicit warning" the audit said was
missing). The trail is the source for any later "this section was voided by X on Y" display.

> The document-level void/inactivation guards (EV-030/EV-055 — `destroy()` must call
> `validar_inativacao` so a `liberado` record cannot be silently inactivated) and the true
> signature-timestamp fix (EV-025 — record the signing service's timestamp, not `dt_registro`) are
> **security/authorization-layer** concerns (`architecture/security-lgpd.md`); they are cited here as
> the invariants annulment composes with, and are owned there, not in this form-engine spec.

---

## 5. Field-level validation (all ADOPT, carried as-is)

The dynamic-form engine's field constraints are correctly specified in the legacy and adopt unchanged
into the zod layer:

| Behavior | Rule | Disposition |
|---|---|---|
| Inclusive `[min, max]` numeric bound + required-when-flagged | EV-066 | ADOPT |
| `interval` via slider clamped to `min..max`, disabled input in read-only | EV-067 | ADOPT |
| `multicheck` selection **count** validated as array length in `[min, max]`; conditional sub-fields flattened across checked values | EV-068 | ADOPT |
| `masked` field applies `mask` + validates against `regex`; required from `campo.required` | EV-069 | ADOPT |
| `list` (repeatable groups) capped at `campo.max` (unbounded if undefined); add control hidden at cap or read-only | EV-070 | ADOPT |
| Standard required rule gated strictly on `campo.required` across text/date/select/boolean/checkbox/extra; `extra` inherits parent required | EV-071 | ADOPT |
| Sub-form update **requires an `id`** per campo; campos with falsy `valor` skipped | EV-058 | ADAPT (schema-validated, not bare `KeyError`) |
| Nutritionist form **uniquely requires** `avaliacao_global`, `terapia_nutricional`, `avaliacao_abdominal` (siblings mark these `required=false`) | EV-056 | ADOPT (deliberate discipline rule) |

**Numeric-bound corrections (input-validation only, not clinical thresholds).** Two legacy bounds are
physiologically implausible and are the **only** numeric edits:
- O2 flow `0–1000 L/min` → capped at a clinically plausible high-flow ceiling (**FC-012**, ADAPT,
  `#numeric-field-bounds-o2-flow`).
- Vomit/gastric-residue `0–10000 ml` is kept as an input-validation bound, not a clinical threshold
  (**FC-006**, ADOPT).

---

## 6. Conditional section rendering (PDF/read view)

Legacy PDF rendering flagged a section "present" whenever any single non-metadata field was non-`None`
— but a lone `False`/empty-string field also counted as "filled" (**EV-013**, ADAPT). v2 renders a
section iff it has **type-aware non-empty** content (a `false` boolean, `0`, or `""` counts as empty
for presence, not as data), reusing the same emptiness predicate the `show` effect uses (§3). Intent
preserved, mechanism corrected.

---

## 7. Form versioning (G8)

Each `FormSchema` carries `schemaVersion` (semver). **[DECISION]:**

- Every submitted record **pins** the `schemaVersion` it was authored under.
- Historical records **render against their pinned version** (labels, options, order preserved as
  captured); new records use the latest version.
- Schema evolution is **additive by contract**: adding an optional field or an enum option is a minor
  bump; renaming/removing a field or narrowing an enum is a **major** bump that must ship a migration
  mapping. This mirrors the platform rule that *Gold-schema changes are versioned breaking changes*
  (ledger) and the `clinical_scores.algorithm_version` pinning pattern.
- Because vocabularies are carried **verbatim** (§10), a version bump is *not* required to "fix"
  historical spelling — corrected codes (§11) ship as a new major version with an old→new value map so
  historical records still resolve their original stored code.

This directly answers the `ADR-0015` migration concern (*"all 14 config shapes need to be
re-authored... a one-time migration cost"*): re-authoring is a versioned, mapped migration, not a
lossy rewrite.

---

## 8. Offline-safe drafts (G7)

The lifecycle is the canonical `salvo → liberado → inativo` tri-state, **reconciled BE/FE with no
divergence** (**EV-042**, ADOPT, CLU-EVOLUCOES-C-01). Only `salvo` drafts are offline-mutable.

**[DECISION] offline posture:**

- A `salvo` draft is persisted locally (IndexedDB) with its pinned `schemaVersion`; edits queue
  optimistically and reconcile on reconnect (aligns with the frontend offline/degraded posture in
  `component-library.md`).
- Drafts are **author-private**: a same-type form is visible only to its author unless status is
  `liberado` (**EV-007**, ADOPT → `security-lgpd.md#draft-document-visibility`; the "previous form"
  lookup must apply the same filter — **EV-029**, ADOPT-CORRECTED, ESC-P3-117).
- A form is **never auto-released offline**. `liberar` requires a registered **CPF** (**EV-053**,
  ADOPT); digital signing requires **CPF + PIN** (**EV-054**, ADOPT) — both need connectivity, so the
  offline path can only produce/refresh a `salvo` draft.
- Conflict handling leans on immutability invariants: `dt_registro` is immutable server-side
  (**EV-059**, ADAPT — enforce server-side, not just a disabled UI control) and edits are author-only
  (**EV-052**, ADOPT), so a reconciling draft cannot silently rewrite another author's record or its
  registration time.
- `inativo` records are read-only and reject any update (**EV-051**, ADOPT) — never draftable offline.

**Save vs. save-and-release UX** (**EV-045**, ADAPT): a confirmation offers a distinct *"save as
draft"* vs *"save and release/sign"* choice; **EV-044** (ADAPT) sets `status=liberado` + `assinar`.
Lifecycle visual treatment (icon/color/success message per state) is redesigned in the v2 design
system, **not** ported from the legacy `mdi` icons and hardcoded hex (`#258a10/#1890ff/#ff1633`)
(**EV-043**, ADAPT).

**Prefill / carry-forward** (**EV-046/047**, ADAPT): a new evolution prefills from the patient's last
saved form and resets the registration timestamp to now. Inherited ids must be **deep-stripped
recursively** before POST so a new record does not overwrite the prefilled one — the legacy stripper
only went one level deep and left array-element ids (**EV-063**, ADAPT).

---

## 9. Retired form-engine plumbing (no clinical loss)

These carry **no** clinical vocabulary forward and are retired with the platform change; the
underlying vocabulary, where any, is preserved via the vocabulary rules in §10–§11, not this plumbing:

- Tasy `tipo→integration-code` map and release gating (EV-009, EV-010, EV-011, EV-012, EV-016, EV-028)
  — legacy Tasy/AMH-Docs ETL, retired per ADR-001.
- `Leito`/tenancy/URL-routing view logic (EV-006, EV-018, EV-020, EV-048) — retired per ADR-001.
- Ad hoc client type-coercion (`peso/altura/imc` unary-plus; moment↔string date adapters) obsolete
  under natively-typed FHIR `valueQuantity`/date fields (EV-060, EV-061).
- DRF serializer defect: a required field absent from every `Meta.fields` variant (EV-057, RETIRE,
  ESC-P3-161) — the `dispositivos_invasivos` vocabulary survives via §11 rules, not this bug.
- Duplicate/dead UI assets: byte-identical `Terapeuta.jsx`/`Psicologo.jsx` SVGs (FC-038); the bare
  `Intercorrencia` icon with zero logic (FC-017); two DRF routes on one basename/viewset (FC-040).

---

## 10. Adopted per-discipline PT-BR vocabularies (VERBATIM)

All values below are carried **exactly as stored, accents included**. Corrections are confined to
§11; anything not listed there is unchanged.

### 10.1 Professional-role enum & form composition (evolucoes)

Role key enum — the pharmacist key is corrected from feminine `formulario_farmaceutica` to masculine
`formulario_farmaceutico` to match its own gating permission and every sibling (**EV-062**,
ADOPT-CORRECTED, ESC-P3-162):

`medico, enfermagem, tecnico_enfermagem, fisioterapeuta, farmaceutico, fonoaudiologo,
musicoterapeuta, nutricionista, psicologo, terapeuta, intercorrencia`

| Discipline | Content-block sections (verbatim) | Rule |
|---|---|---|
| Médico | `impressao_geral, impressao_medica, plano_terapeutico, conduta_medica` | EV-031 |
| Enfermagem | `impressao_geral` | EV-032 |
| Técnico de Enfermagem | `impressao_geral` | EV-033 |
| Fisioterapeuta | `impressao_geral, meta_terapeutica` | EV-034 |
| Farmacêutico | `impressao_geral, conciliacao_medicamentosa, conduta_farmaceutica, profilaxias, meta_terapeutica` | EV-035 |
| Fonoaudiólogo | `impressao_geral, avaliacao_fonoaudiologica, conduta_fonoaudiologica, meta_terapeutica` | EV-036 |
| Musicoterapeuta | `impressao_geral, conduta_realizada, meta_terapeutica` | EV-037 |
| Nutricionista | `impressao_geral, avaliacao_diaria_nutricionista, meta_terapeutica, objetivos_diarios_pendencias` (+ required `avaliacao_global, terapia_nutricional, avaliacao_abdominal`, EV-056) | EV-038 |
| Psicólogo | `impressao_geral, avaliacao_psicologica, conduta_psicologica, meta_terapeutica` | EV-039 |
| Terapeuta | `impressao_geral` (base only) | EV-040 |
| Intercorrência | `impressao_geral, descricao, intervencao, desfecho, relato_gastos` | EV-041 |

### 10.2 Cross-cutting clinical enums

| Vocabulary | Values (verbatim) | Rule / disposition |
|---|---|---|
| Lifecycle status | `salvo, liberado, inativo` | EV-042 (ADOPT) |
| Gender/sex | `M`=Masculino, `F`=Feminino, `O`=Outro, `N`=Nao informado | EV-076 (ADOPT) — see §12 `RAT-FC-02` |
| LPP staging (NPUAP/EPUAP, BE source of truth) | `suspeita_de_lesao, estagio_i, estagio_ii, estagio_iii, estagio_iv, nao_graduavel` | FC-001 (ADOPT, VERIFIED) |
| Exudate amount (canonical 5-option) | `nada, escasso, pequeno, moderado, grande` | FC-004 (ADOPT-CORRECTED) — see §11 |
| Abertura ocular (GCS-label enum) | `espontanea, ao_comando, a_dor, nenhuma` | FC-031 (ADOPT) |
| Grau de urgência (home-care triage) | `normal, urgencia, sem_urgencia, emergencia` | FC-007 (ADOPT) |
| Diurese route multicheck | `ausente, presente, svd, sva, fralda` (`fralda`→`nr_trocas_24h` conditional) | FC-030/FC-013 (ADOPT) |
| Locomotion (TecEnfermagem) | `acamado, deambula, deambula_auxilio, cadeirante` | FC-036 (ADOPT) |
| Edema MMII ordinal | `MMII1, MMII2, MMII3, anasarca` | FC-011 (ADOPT) |
| Respiratory equipment multicheck | `concentrador_oxigenio, cilindro_o2, bipap, cpap, coughassist, aspirador, ventilador_mecanico` | FC-024 (ADOPT) |

### 10.3 Discipline-specific assessment vocabularies (all ADOPT verbatim)

Speech therapy global + orofacial/language (FC-025, FC-026); music therapy global + instrument-
relations multicheck (FC-027, FC-028); nursing abdominal/genitourinary/neuro exams (FC-029, FC-030,
FC-031); physiotherapy neuro/cardio/respiratory + motor-function (FC-032, FC-033); psychology global +
psychological-assessment (FC-034, FC-035); TecEnfermagem global assessment (FC-036); pharmacist &
tech-nursing neuro/cardio slices reusing the shared vocabulary (FC-044, FC-045); nursing global-
assessment + assistance-risk multicheck (FC-011); TecEnfermagem diet block (FC-006); home-care
Intercorrência triage/intervention/disposition vocabularies (FC-007, FC-009, FC-015); physiotherapy
respiratory & motor technique multichecks (FC-016); physio mobilization-eligibility (FC-008);
non-pressure lesion assessment (FC-019); device/dressing field catalog + invasive-device dressing
schedule (FC-022, FC-043); optional HH:MM exit-time mask (FC-041, backed by the `time` type §2).

> Label-only accent fix (stored value already correct, presentation layer only): the speech-therapy
> `Ausênte` **label** is corrected to **Ausente**; the stored value `ausente` is unchanged (**FC-026**).

---

## 11. Audit-flagged copy-paste drift — the ONLY corrections

Nothing outside this table is altered. Each row cites the disposition that authorizes it.

| Concern | Legacy (drifted) | Canonical / corrected | Disposition |
|---|---|---|---|
| **Peri-wound edema top tier** (headline drift) | Nursing/dietitian FE store `crepitacao_edema_com_sulco_maior_4cm` | **Canonical value: `crepitacao_maior_4cm`** (BE + TecEnfermagem). Nursing/dietitian FE realigned to it. | **FC-002** (ADOPT-CORRECTED, ESC-P2-060), **FC-003** (ESC-P2-061), **FC-004** (ESC-P2-075); BWAT-anchored |
| **Peri-wound exudate set** | Nursing/dietitian FE drop the `pequeno` option (4-option set) | Restore the canonical **5-option** set `nada, escasso, pequeno, moderado, grande` | FC-002 / FC-004 |
| **LPP origin field** | `nova_lesao`/`lesao_previa` (`tipo_lpp`) submittable empty (`allow_null=True` + `allow_blank=True`) | `tipo_lpp` made **required**, no blank/null option | FC-018 (ADOPT-CORRECTED) |
| **Anatomical-site spelling** | `toronozelo_lateral`, `toronozelo_medial`; `inframaria_d`, `inframaria_e`; duplicate `sacro_coccix` region | `tornozelo_lateral`, `tornozelo_medial`; `inframamaria_d`, `inframamaria_e`; duplicate region removed (44 concepts kept) | FC-020 (ADOPT-CORRECTED) |
| **Invasive-device codes** | `traquestomia`, `jejunostopia` | `traqueostomia`, `jejunostomia` (other 6 unchanged) | FC-023 (ADOPT-CORRECTED) |
| **Chronic-diagnosis catalog** | BE dict-index **no default** → `KeyError` on any unlisted code; FE trailing-comma sparse-array hole | Add safe **default/fallback label** (fix KeyError) + remove trailing comma. **Stored codes/labels — including verbatim typos `corononariana`, `diabettes_mellitus_tipo2`, `doença_de_alzheimer` — preserved** (load-bearing) | FC-021 (ADOPT-CORRECTED, ESC-P3-165) |
| **Field-type dispatch gap** | `time` declared in `CampoType`, not dispatched | Dispatch all 11 types incl. `time` (§2) | EV-023 (ADOPT-CORRECTED, ESC-P3-160) |
| **Pharmacist role key** | `formulario_farmaceutica` (feminine, absent from type-union) | `formulario_farmaceutico` (masculine, matches gating perm + siblings) | EV-062 (ADOPT-CORRECTED, ESC-P3-162) |
| **Annulment disable inversion** | `SubFormString` inverts `isAnnulled`, can throw on missing nullifier | Align to single `disableAll`/`nullCampo` semantics (§3.3) | EV-065 (ADOPT-CORRECTED, ESC-P3-163) |
| **Previous-form visibility leak** | `anterior_indicadores` skips the author/status filter → another user's draft leaks | Apply the same visibility parity as EV-007 | EV-029 (ADOPT-CORRECTED, ESC-P3-117) |
| **Id-strip depth** | inherited ids stripped one level only, array-element ids left | deep-strip ids recursively before POST | EV-063 (ADAPT) |

> **Not corrected here (owned by other domains, cited for completeness):** capillary-refile-time alert
> `>5s → >3s` and the `tec_5s` label rename (**FC-005**, **FC-010** → `hemodynamics.md`); RASS
> integer-canonical `-5..+4` (**EV-003** → `neuro-sedation.md`); canonical single-typed encounter
> identifier (**EV-075** → `architecture/data-model.md`); signature-timestamp integrity (**EV-025** →
> `security-lgpd.md`).

---

## 12. Open ratifications — surfaced, not decided [RATIFY]

These dispositions sent a clinical/semantic question to committee; this spec provides the mechanism so
each resolves to a config flag, not a redesign, but does **not** pre-empt the decision.

| Id | Question | Rule |
|---|---|---|
| `RAT-EVOLUCOES-01` | Confirm the **annulment / void-not-delete** semantics (§4): is group-level annulment adopted, and where does it apply clinically? (Legacy declared `anulavel`/`nullifiers` types but no code exercised them.) | EV-074 (ESC-AMBIGUOUS-329) |
| `RAT-EVOLUCOES-01` | **SOFA** field shape parity: does v2's own SOFA (Vincent 1996) need 1:1 legacy component-field parity, or may it be redesigned? | EV-001 (ESC-UNVERIFIABLE-262), EV-002 |
| `RAT-FC-01` | High-cost drug/antibiotic **route+body-site** capture vocabulary — reuse as-is or restructure for the v2 eMAR? Plus the 10-discipline care-team role set (icon-derived, not confirmed exhaustive). | FC-014 (ESC-UNVERIFIABLE-284), FC-037 (ESC-AMBIGUOUS-301) |
| `RAT-FC-02` | **Gender/sex** vocabulary: confirm the adopted 4-value `M/F/O/N` enum (§10.2, EV-076) is the intended set and is **not** restricted to a binary (legacy shipped `Masculino/Feminino`-only iconography) — LGPD-inclusivity weight. | FC-039 (ESC-AMBIGUOUS-330) |
| `RAT-FC-03` | **Vasoactive/sedative infusion units**: dobutamina `0–30`, noradrenalina `0–200`, sedativos `0–30` captured with **no unit**; plausible bases differ per drug. Confirm the unit model before designing dosing capture. | FC-042 (ESC-UNVERIFIABLE-285) |
| `RAT-EVOLUCOES-05` | Vitals-creation bundled with an auto-created daily `BalancoHidrico` via a possibly-nonexistent `.get_pk` — confirm the intended vitals/fluid-balance workflow. | EV-017 (ESC-AMBIGUOUS-299) |

---

## 13. RULE coverage map

**formularios-clinicos (45):** ADOPT verbatim — 001, 006, 007, 008, 009, 011, 013, 015, 016, 019,
022, 024, 025, 027, 028, 029, 030, 031, 032, 033, 034, 035, 036, 043, 044, 045; ADOPT-CORRECTED /
ADAPT (§11) — 002, 003, 004, 010, 012, 018, 020, 021, 023, 026; RETIRE (§9) — 017, 038, 040;
RATIFY (§12) — 014, 037, 039, 042; routed to other domains — 005 (hemodynamics).

**evolucoes (77):** field engine & validation ADOPT — 042, 049, 050, 051, 052, 053, 054, 056, 058,
059, 064, 066, 067, 068, 069, 070, 071, 072, 073, 076; per-discipline composition ADOPT — 031–041;
lifecycle/prefill ADAPT — 013, 021, 043, 044, 045, 046, 047, 063; ADOPT-CORRECTED (§11) — 023, 029,
062, 065; RETIRE (§9) — 006, 009–012, 016, 018, 020, 022, 028, 048, 057, 060, 061; RATIFY (§12) —
001, 002, 004, 005, 017, 074; routed to other domains — 003 (neuro-sedation), 007/008/019/025/026/
027/029(sec)/030/051/055/059 (security-lgpd), 014/015/024 (correlation-engine, sepsis), 075
(data-model), 077 (reports).

---

*End — form-engine-designer deliverable. Peer stack-choice ADR draft (`form-engine-stack.md`) and the
security-layer document lifecycle/signature rules are owned elsewhere and referenced above.*
