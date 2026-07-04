# 0012. Canonical component primitives versus parallel and dead implementations

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy component library has 117 top-level directories under `src/components` (281
`.tsx` files, 126 co-located `.less` files), one folder per component, with no enforced
component-authoring contract (D-02 §3, inventory §3). Within that surface, a handful of
primitives were built once and adopted consistently, while several UI concerns — tabs,
icons, "unread count" badges — independently acquired two competing implementations each,
and three fully-built components were never wired up at all. Any rebuild must decide which
of the legacy primitives to carry forward as the canonical implementation, and how to stop
this kind of ungoverned duplication from recurring.

## The Legacy Decision

- **`DrawerBuilder`** is the single shared drawer scaffold (width, close-button, Salvar/
  Fechar footer conventions), used at 16 call sites outside its own folder.
  `trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99`
- **`AlertDelete`** is a uniform two-step destructive-confirm: an `Alert type="warning"`
  banner plus a `Popconfirm` guarding a `danger` "Excluir" button, applied consistently to
  destructive flows app-wide. `trilhas-frontend:src/components/AlertDelete/AlertDelete.tsx:1-49`
- **`Ball`** is a small two-tone SVG status dot reused identically on bed cards, dashboard
  cards, chat headers, and the video-call online roster. `trilhas-frontend:src/icons/Ball.jsx:1-34`
- **`MaterialIcon`** wraps `@mdi/js` path data, forcing `size="1em"` and an `anticon` class
  so MDI glyphs sit flush in AntD icon slots; adopted in the overwhelming majority of
  component files. `trilhas-frontend:src/components/MaterialIcon/MaterialIcon.tsx:1-19`
- Alongside those, a **second, bespoke, untyped (`.jsx`) SVG icon system** exists for
  clinical-role, gender, and config-menu glyphs, each hardcoding its own `viewBox` and
  `size`/`color` props with no shared sizing contract against `MaterialIcon`.
  `trilhas-frontend:src/icons/configs/EstabelecimentoIcon.jsx:1-37`
- **Two tab implementations coexist**: AntD `Tabs` (used for `TabRecomendacoes`, the
  add-movement drawer's date-history tabs, and elsewhere) and a bespoke `CustomTabs`
  (absolutely-positioned sliding underline, manual `activeKey` state), adopted in only 2
  files (`DrawerReacoes`, the inconsistências page).
  `trilhas-frontend:src/components/CustomTabs/CustomTabs.tsx:1-98`
- **Two "unread count" badge treatments coexist**: AntD `Badge count={n}` on the
  notification bell versus a hand-rolled circular `div` on `DashboardCard` capped at
  `"+99"`, colored from `@secondary-color` rather than the alert palette — two different
  visual treatments for the same affordance.
  `trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:140-156`,
  `trilhas-frontend:src/components/ListDashboard/DashboardCard/DashboardCard.tsx:250-259`
- **Three components are fully built but never imported anywhere in `src`**:
  `Breadcrumbs` (a real AntD `Breadcrumb` with UUID-aware path parsing, abandoned in favor
  of a bespoke header `Tag` trail), `MobileCardWrapper`, and `SideFixedButton` (D-02 §7;
  inventory §3.6, §7).

## Evident Rationale

*(Inferred — not stated in the codebase.)* The well-factored primitives show intentional
componentization for the shapes repeated most often across the app — every drawer needs
the same chrome, every destructive action needs the same confirm ritual, every bed/roster
needs the same status dot, every icon slot needs to sit flush in AntD's layout. The
duplications and dead code plausibly reflect organic drift rather than deliberate
redesign: a later feature (the reactions drawer, the inconsistências page) likely needed a
visual effect (sliding underline) the in-use AntD version made awkward, so a parallel
`CustomTabs` was written instead of extending the existing tab usage; the dashboard badge
was hand-rolled separately from the notification bell's AntD `Badge` at a different point
in time; and `Breadcrumbs`/`MobileCardWrapper`/`SideFixedButton` were plausibly built ahead
of a UI direction later abandoned in favor of the header `Tag` trail (inventory §3.6), with
nothing subsequently removing them.

## Assessment

**Strengths, cited:** `DrawerBuilder`, `AlertDelete`, `Ball`, and `MaterialIcon` are each a
single, consistently-adopted implementation of a frequently-repeated shape — no competing
version of any of these four exists anywhere in the 281-file component tree.

**Weaknesses, cited:**

- Two icon systems, no shared sizing contract: `MaterialIcon` standardizes on `size="1em"`,
  while the bespoke SVGs (`EstabelecimentoIcon` and siblings) each hardcode their own
  `viewBox` and accept ad hoc `size`/`color` props — swapping families requires per-icon
  visual tuning.
- Two tab implementations for the same UI purpose, `CustomTabs` adopted in only 2 of the
  files where tabbed navigation appears, so most engineers must know both APIs.
- Two badge treatments for "unread count," differing in both component (`Badge` vs. a
  hand-rolled `div`) and color source (AntD default vs. `@secondary-color`, unrelated to
  the clinical alert palette).
- Three fully-implemented, non-trivial components (`Breadcrumbs`'s UUID-aware path
  parsing; `MobileCardWrapper`'s light/dark-aware card) carry ongoing maintenance/typing
  cost with zero usages and no in-repo signal that they are deprecated rather than merely
  undiscovered.

## Considered Options

1. **Lift and shift**: port every legacy component, duplicates and dead code included.
   Rejected — repeats the undiscoverability problem in a fresh codebase, two APIs per
   concern from day one.
2. **Cherry-pick the good primitives, re-derive the rest ad hoc** as new tab/icon/badge
   needs arise, same as legacy did. Rejected — this is the exact process that produced the
   original duplication; without governance it recurs.
3. **Canonical primitive set, enforced by tooling.** Designate one dialog/drawer shell, one
   destructive-confirm pattern, one status-dot atom, and one icon component (explicit typed
   sizing contract) as the only sanctioned implementations; consolidate on a single tab
   primitive and a single badge/count treatment; retire the three dead components; add a
   lint rule / dependency-cruiser-style check that fails CI on a second competing
   implementation of a registered primitive.
4. **Adopt a third-party headless component library** (e.g. Radix/shadcn-style primitives)
   for generic concerns (tabs, badge, dialog), reserving custom components for
   clinically-specific atoms (status dot, destructive-confirm flow). Less from-scratch
   design work, but a new dependency and theming layer the legacy app didn't have.

## Decision Outcome

Recommend **Option 3**, optionally informed by Option 4 for generic (non-clinical)
primitives if the chosen stack has a strong headless-component ecosystem. Carry forward
`DrawerBuilder`, `AlertDelete`, the `Ball` status-dot, and `MaterialIcon` as the conceptual
core of the new primitive set — proven, well-adopted shapes with no design defect found,
only an absence of enforcement elsewhere. Consolidate the two tab implementations into one
themed component (sliding-underline as a variant, not a parallel implementation), unify the
two badge treatments into one "count" primitive on a single color source, and retire
`Breadcrumbs`, `MobileCardWrapper`, and `SideFixedButton` rather than porting them
speculatively. This is a governance decision, not a per-component styling note: register
canonical primitives in one place (a component registry/Storybook) and add an automated
check blocking a second implementation of a registered concern from merging. Recommendation
pending team ratification, including the specific enforcement tooling and whether a
headless library is adopted.

### Consequences

**Good:**

- One API per UI concern (tabs, icon, badge, drawer, destructive-confirm), reducing
  onboarding cost and inconsistent visual treatment.
- Proven primitives transfer with minimal redesign risk, preserving what already works.
- Automated enforcement turns future duplication into a caught CI failure instead of a
  silent, years-long drift discovered only by audit.
- Removing three dead components cuts maintenance/typing surface with zero user impact.

**Bad:**

- Consolidating tabs and badges needs an explicit migration pass (which variant wins, how
  existing call sites update) rather than a mechanical lift.
- A component registry and CI enforcement rule is new tooling investment with no legacy
  equivalent to copy from.
- Adopting a headless third-party library adds a dependency and integration layer the
  legacy app never had.
