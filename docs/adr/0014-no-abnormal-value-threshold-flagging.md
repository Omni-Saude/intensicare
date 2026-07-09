# 0014. No threshold or reference-range flagging of abnormal clinical values

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's core clinical screens surface a large volume of numeric patient data —
vital signs, ICU labs, 24h fluid summaries, and a validated organ-failure severity score
— to clinicians who must triage deterioration quickly. None of this data carries any
value-driven visual encoding today: a normal reading and a critical one occupy the same
row, color, and weight. The new platform must decide, deliberately, how to encode
clinical severity directly on values, rather than silently inheriting this absence. This
matters most for a platform positioned as AI-agent-led, where an agent's own
severity/risk assessment needs a visual home consistent with how clinicians already read
abnormal values.

## The Legacy Decision

- **Vital signs** (HR, RR, systolic/diastolic BP, temperature, SpO2, HGT, ventilation
  mode, O2 flow, FiO2, consciousness level, pain scale — 15 fields) all render through
  the same generic `ListItem` row with no conditional styling by value — a SpO2 of 99%
  and 60% render identically.
  `trilhas-frontend:src/components/BalancoHidricoItens/ItemSinaisVitais/ItemSinaisVitais.tsx:29-127`
- **Assistive labs** (RASS, Glasgow, delirium, 24h diuresis/fluid balance, temperature,
  leukocytes, platelets, CRP, lactate, pH, bicarbonate, pO2, pCO2, P/F ratio, creatinine,
  urea, bilirubin — several classic sepsis/deterioration markers) go through the same
  neutral `ListItem`, no color/icon/bolding by reference range.
  `trilhas-frontend:src/components/InformacaoesAssistenciais/InformacoesAssistenciais.tsx:1-171`
- **24h summary indicators** follow the identical unencoded pattern.
  `trilhas-frontend:src/components/ItemIndicadores24h/ItemIndicadores24h.tsx:1-63`
- **Fluid-balance grid**: every non-zero intake/output cell gets a fixed green pill
  (`background: #42e26f`) purely to signal "a value exists" — a large intake and an
  extreme output render identically; no positive/negative split, no out-of-range flag.
  `trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx:81-96`,
  `.../GridView.less:38-44`
- **SOFA score** — a validated ICU organ-failure/mortality-risk score — is always
  rendered inside a static `<Tag color="warning">Escore sofa: {escore_sofa}</Tag>`,
  whether the value is 0 or 20+.
  `trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:85-94`
- **`RenderTagTable`** — a component taking an explicit `color` prop and rendering a
  colored left-border title or bordered `Tag`, structurally exactly what per-cell
  severity coloring needs — is called with the literal `"var(--primary-color)"` at all
  8 of its call sites, all non-clinical admin tables (setores, leitos, usuários,
  estabelecimentos, grupos, gestão de pacientes, inconsistências, relatório de evolução).
  `trilhas-frontend:src/components/RenderTagTable/RenderTagTable.tsx:1-39`
  The two clinically relevant fluid-balance column sets don't use it at all.
  `trilhas-frontend:src/components/ColumnsBalancoHidrico/ColumnsEntrada/ColumnsEntrada.tsx:1-98`,
  `.../ColumnsSaida/ColumnsSaida.tsx:1-112`
- The **only** numeric-to-color mapping anywhere is the bed-occupancy gauge (`>70%` red,
  `>50%` amber, else green) — an operational-capacity metric, not a clinical value.
  `trilhas-frontend:src/components/ListDashboard/DashboardCard/DashboardCard.tsx:291-307`
- Where "critical" treatment does exist it is presence-based, not value-based: an
  invasive-procedures badge shown only when a list is non-empty
  (`trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:423-454`)
  and a sepsis first-hour-delay icon shown only when an item is overdue
  (`trilhas-frontend:src/components/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx:42-50`).

## Evident Rationale

*(Inferred — no rationale is stated anywhere in the codebase.)* This reads as an
unaddressed gap, not a deliberate choice. `RenderTagTable` — a per-cell color primitive
structurally suited to exactly this problem, built, and then only ever wired to the
static brand color — is the strongest evidence someone anticipated value-driven cell
coloring and never finished connecting it to threshold logic. No comment, flag, or
clinical sign-off explaining the absence was found in the audited tree.

## Assessment

**Weaknesses (the dominant finding):**

- Every clinically load-bearing numeric surface — vitals, labs, 24h indicators, fluid
  balance, SOFA — uses identical non-differentiating rendering, so clinicians get zero
  passive severity signal and must read and interpret every value manually.
- The SOFA tag is actively misleading: a fixed `"warning"` color over-communicates
  severity at 0 and under-communicates it at 20+ — wrong at both ends of the scale.
- The fluid-balance grid's fixed-green pill obscures exactly the signal (magnitude,
  direction of imbalance) clinicians need from that view.
- `RenderTagTable` shows the right primitive (color-in, colored-cell-out) already exists
  and sits unused for its apparent purpose — the gap is wiring, not missing concept.

**Strengths worth preserving:**

- The one existing threshold (occupancy gauge) proves clean band logic
  (`>70/>50/else`) is within the team's practice — it simply never propagated to
  clinical values.
- The existing `statusTrilha` severity-color system (5 states × 6 shades, → ADR 0013)
  is a working precedent for a shared severity-shade palette to reuse.

## Considered Options

1. **Lift and shift** — keep neutral `ListItem` rendering everywhere. Rejected: this is
   the audit's top-ranked clinical UX gap; porting it forward would not be a considered
   baseline, only a repeated oversight.
2. **Per-screen, ad hoc thresholds** — each vitals/labs/SOFA screen writes its own
   inline "if abnormal, turn red" logic. Rejected: this is exactly how the legacy app's
   other severity systems ended up reinvented 6-plus times with divergent literals
   (inventory §5.1); it would reproduce the same drift one layer later.
3. **Centralized reference-range service + shared abnormal-value token scale.** One
   source of truth mapping each vital/lab code to a reference range (age/context-adjusted
   where necessary, e.g. pediatric HR bands, ventilated FiO2 targets), classifying values
   into a small severity scale (normal/mild/moderate/critical), consumed uniformly by
   vitals cards, lab panels, the fluid-balance grid, and composite scores like SOFA via
   published severity bands. Extends `RenderTagTable`'s color-prop shape (or a typed
   successor) to finally get wired for its apparent purpose.
4. **Option 3, plus agent-generated severity annotations** — additionally let the AI
   agent layer attach its own derived risk signal (trend-aware/multi-value, not just
   single-value thresholds) through the same token scale, visually equal in weight to
   static flags but distinguishable in source (e.g. an "agent-derived" marker).

## Decision Outcome

Recommend **Option 4**: build the centralized reference-range/threshold service and
shared abnormal-value token scale from Option 3, designed from the outset to accept both
static reference-range classifications and agent-derived severity signals through one
interface. This directly closes the audit's top clinical UX gap, avoids repeating the
legacy pattern of independently reinvented severity encodings, reuses the shape of the
one primitive (`RenderTagTable`) clearly intended for this, and gives an AI-agent-led
product a visual channel for agent risk assessment consistent with how clinicians already
read values. **This is a recommendation pending clinical and product-team ratification**
of the specific reference ranges, age/context adjustments, and severity-band count
(e.g. 3-tier vs. 4-tier) before implementation.

### Consequences

**Good:**

- Clinicians gain passive, at-a-glance severity signal across vitals, labs, fluid
  balance, and SOFA instead of reading and interpreting every value manually.
- One shared token scale and reference-range service prevents the "reinvented N times
  with drifting literals" failure documented elsewhere in the legacy audit (→ ADR 0013)
  from recurring here.
- Gives the AI-agent layer a pre-built, clinically-legible channel for its own risk
  assessments instead of requiring a bespoke UI later.

**Bad:**

- Defining and maintaining correct, age/context-adjusted reference ranges is clinical
  content work requiring sign-off, not pure engineering, and is an ongoing maintenance
  surface as guidelines evolve.
- A severity scale spanning single-value thresholds, composite scores, and
  agent-derived signals must be carefully specified so the three don't visually collide
  or get conflated as equal in confidence.
- This is new build, not lift-and-shift — there is no working legacy mechanism to adapt,
  only the unused shape of `RenderTagTable` to draw on.
