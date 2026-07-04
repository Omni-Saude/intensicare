# Screen Spec — Admin: Threshold Configuration & Alert Governance

**Owner:** alerting-ux-specialist · **Status:** draft for reconciliation barriers **B** (threshold_config schema) and **C2** (governance UX) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This spec defines the tenant/unit/bed threshold-configuration surface with change audit (extending `threshold_config`), and the alert enable/disable governance workflow whose central guardrail is: **safety-critical alerts cannot be silently disabled**. It renders the machinery in `architecture/alert-engine.md §6` (threshold resolution), `architecture/data-model.md §4.1/§6` (versioned definitions + audit trail), and the governed-change story US-25. No clinical cutoffs are invented — fixed cutoffs live versioned in the alert definitions; this screen governs the tunable *score→band* thresholds and the enable/disable state.

Every claim cites a source: a ledger constraint (`CON-*`), a brief fact (`DM-*`, `VIS-*`, `ADR-*`, `PER-*`), a user story (`US-*`), or an invariant (`INV-*`).

---

## 0. Design-system frame

- Reached from the **permission-filtered settings tiles** off the unit/tenant context (`ADR-0009` IA; legacy `useMenuByPermissions`, `DES-4-02`). **Deny-by-default, server-enforced** route permission (`CON-0038`/`CON-0056`/`DES-C-08`); the API independently authorizes every write (`CON-0047`). Editing thresholds is a role-gated capability (Dra. Fernanda coordinator + Dr. Carlos clinical reviewer, US-25).
- Config forms use the **schema-driven clinical form engine** (react-hook-form + zod, `ADR-0015`) with typed configs validated at build time — no `as any` (`CON-0043`/`ADR-C-10`). This is the modernized `FormDadosProntuario` IP (`DES-C-07`).
- Values are shown through the same **abnormal-value flagging** and **triple-encoded severity** tokens as the rest of the app (`CON-SEED-11`), so a band preview reads identically to how it will render clinically. Clinical `clinical.*` tokens are **structurally separate from tenant `brand.*`** — a tenant admin editing branding can never alter what a severity band *means* (`CON-0041`/`CON-0049`/`DES-C-01`).

---

## 1. Scope model — tenant → unit → bed (most-specific-wins)

`threshold_config` maps a **score type** (`MEWS`, `NEWS2`, `SOFA`, `qSOFA`) to its `watch/urgent/critical` bands per scope (`DM-T-05`). Phase-1 carries `tenant_id` + `unit` (NULL = tenant-wide, `DM-C-11`/`CON-0029`). This screen adds the **`bed_id`** scope (nullable; `patient_cache` already carries `bed_id` + `unit`, `DM-T-01`; alert-engine §6):

- **Resolution = most-specific-wins.** For a patient in `(tenant, unit, bed)`: use the row matching `bed_id`; else the `unit` row; else the tenant default (`unit` NULL, `bed_id` NULL). Precedence **bed ≻ unit ≻ tenant**.
- The editor shows the **effective resolved value** at each scope and whether it is inherited or overridden, so an admin always sees *why* a bed has the thresholds it has. Editing at a broader scope shows how many narrower overrides currently shadow it.
- **`threshold_config` stays operational-only** — no Gold persistence (`DM-C-11`/`CON-0029`/`CON-0003`). Multi-tenancy via indexed `tenant_id` (`DM-C-15`).
- **Scope note:** `threshold_config` governs **score→severity band** mapping only (MEWS/NEWS2/SOFA/qSOFA). **Fixed clinical cutoffs** (e.g. K⁺ > 6.5 mmol/L, Na⁺ < 120 mmol/L) live **versioned in the alert definition** (`alert_definition_version`, data-model §4.1), not here — they are not free-text-editable in this screen; changing one mints a new immutable definition version (§4).

### 1.1 Editable fields per scope row

| Field | Type | Meaning | Source |
|---|---|---|---|
| `score_type` | enum | MEWS / NEWS2 / SOFA / qSOFA | `DM-T-05` |
| `watch_threshold` | int | score ≥ → watch band | `DM-T-05` |
| `urgent_threshold` | int | score ≥ → urgent band | `DM-T-05` |
| `critical_threshold` | int | score ≥ → critical band | `DM-T-05` |
| `rate_limit_per_hour` | int | max alerts/patient/hour (suppression) | `DM-T-05`, alert-engine §5 |
| `cooldown_minutes` | int | min time between same-type alerts | `DM-T-05`, alert-engine §5 |
| `bed_id` | nullable | narrowest scope (NEW) | alert-engine §6 |

**Monotonic-band validation (build/submit-time):** the engine rejects `watch ≤ urgent ≤ critical` violations so a band ordering can never invert — analogous to the monotonic-scale rule (`CON-0036`) and enforced by the typed schema (`CON-0043`).

---

## 2. Change audit — every write is an immutable audit row (INV-1)

Extends `threshold_config` with full change audit per `alert-engine.md §6` and `data-model.md §6`:

- **Every `INSERT / UPDATE / DELETE`** on `threshold_config` writes an append-only `audit_trail` row (`action='threshold.update'`) with `updated_by`, `updated_at`, and **before/after state** (`INV-1`/`CON-0066`/`IMP-C-01`). The `audit_trail` table is append-only with an anti-mutation trigger (`data-model §6`); a threshold edit can never be silently rewritten. Legal basis: LGPD + CFM 1.821/07.
- **Versioned, never hard-deleted while referenced** (`data-model §8`, `threshold_config` retention = indefinite/versioned): superseded rows are retained so any historical alert traces to the exact threshold that produced it (`US-25 AC3`/`VIS-7.2-05`/`VIS-C-13`). A "delete" is a supersession, not a physical removal, while any fired alert references the version.
- The change-history view renders the audit chain per scope row: who changed what, when, from→to, with the justification (§3).

---

## 3. Governed change workflow (US-25) — propose → review → activate

Threshold tuning is **not a direct edit**; it is a governed, role-gated, audited workflow (`US-25 AC2`):

1. **Propose.** A coordinator (Dra. Fernanda) proposes a change, **required to cite a justification** — evidence or analytics, e.g. a US-23 governance-queue item or a US-26 retrospective preview (`US-25 AC4`). The proposal captures the target scope, the before/after values, and the citation.
2. **Review / approve.** Role-gated approval by the clinical reviewer (Dr. Carlos) (`US-25 AC2`). Approval is a distinct audited step (separation of proposer/approver).
3. **Activate with effective-from timestamp.** On approval the new `threshold_config` version becomes active from a recorded `effective_from`; the prior version is superseded (retained, §2). Fired alerts stamp the active version so the alarm-fatigue analytics can place a before/after marker on it (US-23 AC3).

**Retrospective preview (US-26, COULD/Fase 2c):** before activation, replay the stored last-N-days data against the proposed threshold to estimate alert-volume delta and which historical alerts would/would not have fired (`US-26 AC1`). The preview attaches to the proposal record (`US-26 AC2`) and is **decision support only** — activation still requires the approval path (`US-26 AC3`).

---

## 4. Alert enable/disable with governance guardrails

An alert type's enabled/disabled state is itself a governed, audited config — **not** a hidden toggle. The load-bearing guardrail:

### 4.1 Safety-critical alerts cannot be silently disabled

- **The `safety_critical` list is authoritative** and lives in `ppv-ledger-draft.yaml` (every `critical`-band alert + the delta-Na safety leg `ELY-003c`, `CON-0061`). A `safety_critical: true` alert type **cannot be disabled** through the normal toggle. Attempting it does not present a simple switch — it requires a **RATIFY-level escalation** (`US-25 AC5`: regulatory/guideline-mandated critical thresholds are non-relaxable below their published values without a RATIFY-level escalation; per rule-disposition policy `CON-SEED-08`/`SYS-C-03`, P0/safety items are RATIFY-only, never silently changed).
- **A "não procede" disposition never disables an alert type** (`US-22 AC3`) — the disposition UI (alert-triage §2.4) only feeds analytics and the governance queue. There is **no path** from clicking "não procede" on a live alert to muting that alert type; muting is only reachable through this governed screen, and for `safety_critical` types only through RATIFY escalation.
- **Non-relaxable safety floor on thresholds** (`US-25 AC5`): even for enabled alerts, a threshold cannot be relaxed *below* the published guideline value (the fixed cutoffs of §1 scope note) without RATIFY escalation. The delta-Na correction limit (≤ 8–10 mmol/L/24h, `CON-0061`/`CAT-C-01`) is a hard example: it is displayed as a locked, annotated floor.

### 4.2 What disable *can* do (non-safety-critical, still audited)

- A non-`safety_critical` alert type (e.g. an advisory `normal`-band or a low-PPV `watch` type) can be **disabled/enabled per scope** (tenant/unit/bed) by the governed workflow of §3 — propose → review → activate, with a required justification, all audited (`INV-1`). Disabling is a supersession event, reversible, with full history.
- Even a disabled alert is **still evaluated and recorded/audited** where relevant (mirrors the alert-engine §5 maintenance-window carve-out: alerts under maintenance are recorded but not delivered) — disabling changes *delivery*, not the audit trail, so a governance review can always see what *would* have fired.

### 4.3 Enable/disable affordance summary

| Alert class | Toggle in this screen | Path to disable | Audited |
|---|---|---|---|
| `safety_critical: true` (critical band + `ELY-003c`) | **shown locked** | RATIFY-level escalation only (`US-25 AC5`, `CON-SEED-08`) | ✅ (escalation + any change) |
| non-safety `watch`/`urgent` | enable/disable per scope | governed propose→review→activate (§3) | ✅ (INV-1) |
| `normal` advisory (Tier 4) | enable/disable per scope | governed, lighter review | ✅ (INV-1) |
| tunable threshold (score→band) | edit per scope | governed, monotonic + floor validated | ✅ (INV-1) |

---

## 5. Constraints this screen owns or discharges

| Constraint / story | Barrier | Where addressed |
|---|---|---|
| `DM-C-11`/`CON-0029` threshold_config operational + tenant/unit | B | §1 |
| `CON-0033`/`DM-C-15` multi-tenancy indexed `tenant_id` | B | §1 |
| alert-engine §6 `bed_id` scope addition (→ data-architect) | C2 | §1 |
| `INV-1`/`CON-0066`/`IMP-C-01` every threshold change audited | B | §2 |
| `US-25` governed propose→review→activate; `US-25 AC3` version traceability | C2 | §3 |
| `US-26` retrospective preview | Fase 2c | §3 |
| `US-25 AC5`/`CON-0061`/`CAT-C-01` non-relaxable safety floor; safety-critical not silently disabled | C2/C3 | §4.1 |
| `US-22 AC3` "não procede" never disables an alert type | Fase 2a | §4.1 |
| `CON-SEED-08`/`SYS-C-03` RATIFY-only discipline for P0/safety items | B | §4.1 |
| `CON-0038`/`CON-0047`/`DES-C-08` deny-by-default, server-enforced permission | B | §0 |
| `CON-0043`/`ADR-C-10` typed schema-validated config (no `as any`) | C2 | §0, §1.1 |
| `CON-0041`/`CON-0049`/`DES-C-01` clinical vs brand color decoupled | C2 | §0 |

**Open reconciliations (→ B / data-architect):** add nullable `bed_id` to `threshold_config` (extends `DM-T-05`); add `effective_from` + a version/supersession key so a config row is immutably versioned rather than updated-in-place; confirm the enable/disable state persistence (per-scope `enabled` flag on the alert-definition scope join, or a dedicated `alert_enablement` table) — flagged for the data model.

---

## 6. Accessibility gate (required by `accessibility-standard.md §8`)

Per `accessibility-standard.md §1`, admin threshold/governance forms are **incidental chrome scoped to WCAG 2.2 AA**, not the AAA critical-value ceiling — the sole AAA-scoped surface here is the `critical`-band **preview** chip, which renders through the same C2-validated `clinical.*` tokens as clinical screens.

- [x] **A11Y-GATE-01** — Every form label, value, and change-history text meets `SC 1.4.3` (4.5:1 / large 3:1) in both themes; the one AAA-scoped element — the `critical`-band threshold **preview** chip — renders through the C2-validated `clinical.*` tokens that clear 7:1 (`A11Y-REQ-01`; §0, §1.1).
- [x] **A11Y-GATE-02** — Band-preview chips, form-field borders, the `safety_critical` lock glyph, and focus rings meet `SC 1.4.11` (≥3:1 non-text) against adjacent colors in both themes (same `signal-*` roles as the app).
- [x] **A11Y-GATE-03** — Enable/disable state, the `safety_critical` **shown-locked** state, and band previews carry a distinct icon **and** shape/text (a lock glyph + *"bloqueado — escalar RATIFY"* on a locked toggle, §4.3), never color alone (`A11Y-REQ-02`).
- [x] **A11Y-GATE-04** — **N/A** — this screen introduces **no new severity hex**; band previews consume the C2-validated `clinical.*` set already run through the §2.2 CVD/ΔE method (`design-tokens.md §6`).
- [x] **A11Y-GATE-05** — No severity animation on this screen; save/validation transitions honor `prefers-reduced-motion` (collapse to instant) and nothing flashes >3 Hz (`A11Y-REQ-13/14`).
- [x] **A11Y-GATE-06** — The `watch`/`urgent`/`critical` band-preview chips stay icon+shape-distinct at the smallest preview size, protecting the deuteranopia `watch↔critical` LOW-RISK pair (`A11Y-GATE-06`/§2.3 of the standard).
- [x] **A11Y-GATE-07** — Band previews and every severity rendering derive from the live threshold→band computation via `clinical.*` tokens — no hardcoded literal severity anywhere in the spec (`A11Y-REQ`, §0).
- [x] **A11Y-GATE-08** — The propose→review→activate workflow, change-history view, and US-26 retrospective preview open on the managed overlay stack: `Escape` closes only the topmost, back matches Esc, `role="dialog"` (`alertdialog` for the destructive disable / RATIFY-escalation confirm, initial focus on the **safe** default), `aria-modal` + focus trap, exact focus-restore, depth ≤2 (`A11Y-REQ-07..11`, `accessibility-standard §3`).
- [x] **A11Y-GATE-09** — The only live surfaces are the save/validation result and async retrospective-preview completion → `aria-live="polite"` (non-critical status, no forced focus change, `A11Y-REQ-16`); no `critical`-tier alert renders on this admin surface.
- [x] **A11Y-GATE-10** — Where a scope row or governance-queue item names an alert type, its accessible name states severity band → score/parameter → scope (tenant/unit/bed), never band or scope alone (`A11Y-REQ-18`).
- [x] **A11Y-GATE-11** — Every toggle, scope-row edit, and the `Propor`/`Aprovar`/`Ativar` controls meet the 24×24 floor; the primary governed-change actions meet 44×44 (`A11Y-REQ-20/21`).
- [x] **A11Y-GATE-12** — No pure `#FFFFFF`/`#000000` large surface (`A11Y-REQ-23`); embossed form cards carrying values pass the both-theme contrast check (`CON-0037`) and have a `prefers-contrast: more` flat fallback (`A11Y-REQ-24`).
- [x] **A11Y-GATE-13** — **N/A** — no drag interactions on this screen (state: none); scope selection and toggles are tap/click.
- [x] **A11Y-GATE-14** — **N/A** — the safety-critical disable path is a **RATIFY-level governance escalation** (§4.1), an audited approval workflow, **not** a login/e-signature/PIN step, so `SC 3.3.8` has no cognitive-function-test gate here; if institutional policy later requires a signing step on activation it inherits `A11Y-REQ-25` from the shared signing redesign.
- [x] **A11Y-GATE-15** — The scope-row editor, enable/disable toggle, locked-floor annotation, and change-history timeline each expose an accessible name/role/state (`SC 4.1.2`) — no bare `<div onClick>`.
- [x] **A11Y-GATE-16** — Config forms use the schema-driven clinical form engine (§0); a governed change never re-asks a value already captured earlier in the same propose→review flow (`SC 3.3.7`; binds `form-engine-designer`).
