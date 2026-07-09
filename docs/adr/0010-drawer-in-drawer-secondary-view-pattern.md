# 0010. Drawer-in-drawer as the standard secondary/tertiary-view pattern

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's core screen is the ICU bed board (`ListOcupacoes`), a single page from
which staff reach many short-lived secondary tasks — filter beds, view a bed's clinical
recommendations, add a movement, admit/discharge a patient — without losing sight of the
board. The legacy platform solved this entirely with nested AntD `Drawer`s rather than
routed pages or a modal-stack manager, without any shared abstraction for tracking which
drawers are open, how deep they nest, or how they respond to Escape/back navigation. Any
rebuild must decide whether to keep drawers-over-navigation as the secondary-view
pattern, and if so, how to fix the missing stack/nesting/focus-management layer, because
the current implementation already shows per-page drift (inventory §4.4; D-02 §2.2).

## The Legacy Decision

- No client-side modal-routing or nested-route pattern exists for secondary views; all
  such views are AntD `Drawer`s wrapped by one shared primitive, `DrawerBuilder`.
  `trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99`
- `DrawerBuilder` standardizes: a forced-off native close X (`closable={false}`) replaced
  by a custom link-button X; width `"95vw"` below `collapseRule` (1260px) else `"50vw"`;
  a footer with `Salvar`/`Fechar` (`Button shape="round"`) driven by
  `hideOk`/`hideClose`/`hidefooter`/`disableOkButton`/`extraButton` props; and
  `destroyOnClose`. Used at **16 call sites** outside its own folder.
  `trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99` (inventory §3.2)
- Nesting goes **two levels deep** from a single page: `OcupacoesPage` renders a chat
  `DrawerBuilder`, and *inside* its children conditionally renders a second
  `DrawerBuilder` for `TabRecomendacoes` — the inner drawer's JSX is literally nested
  inside the outer drawer's children.
  `trilhas-frontend:src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor].tsx:228-290`
- `ListOcupacoes` independently stacks **4** separate `DrawerBuilder`s off one list —
  filter-leito, recomendações, add-movimentação, add/remove-paciente — each with its own
  boolean `visible*` state (`visibleDrawerFiltroLeito`, `visibleDrawerRecomendacoes`,
  `visibleDrawerAddMov`, `visibleDrawerAddPaciente`, `visibleDrawerRemovePaciente`) and
  its own inline `onClose` handler that manually resets related state (e.g.
  `setDrawerContent(undefined)`, `formAddMovimentacao.resetFields()`).
  `trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:489-690`
- No generic overlay-stack manager exists anywhere: no shared concept of nesting depth,
  no centralized Escape/back-button handling, no shared focus-trap logic — each
  page/component hand-wires its own booleans and close callbacks (inventory §4.4; D-02
  §2.2).

## Evident Rationale

*(Inferred — not stated in the codebase.)* Keeping the board or chat mounted and visible
behind a drawer plausibly matters for a clinical monitoring tool: staff opening a
movement form or recommendations panel likely want peripheral awareness of the ward,
which a full page navigation would remove. Drawers also avoid the cost of a route
transition (remount, refetch, lost scroll position) for short, frequent interactions.
`DrawerBuilder` itself is well-factored — one primitive, consistently sized and footed,
reused at 16 sites — suggesting the *shell* was a deliberate decision even though the
*stacking* of shells was not.

## Assessment

**Strengths:**

- `DrawerBuilder` is a genuinely well-factored, consistently-adopted primitive owning
  width, close affordance, and footer conventions for essentially every create/edit/
  detail panel in the app (16 call sites).
  `trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99`
- The pattern correctly preserves page context behind the overlay, which routed
  full-page navigation would not.
- Two-level nesting works today (`OcupacoesPage`'s chat drawer containing a
  recommendations drawer), showing the primitive can support depth.
  `trilhas-frontend:src/pages/.../setor/[id_setor].tsx:228-290`

**Weaknesses:**

- **No shared stack abstraction.** `ListOcupacoes`'s 4 independent drawers each get a
  separate boolean and a separate inline `onClose`, with no shared registry of what's
  open or how deep. `trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:489-690`
- **No Esc/back-navigation handling.** Nothing wires the browser back button or a shared
  Escape handler to close the topmost drawer first; the setor page's outer chat-drawer
  close handler does not coordinate with the inner tabs-drawer's own visibility state.
  `trilhas-frontend:src/pages/.../setor/[id_setor].tsx:228-290`
- **No focus-trap handling** beyond AntD v4's default — with two drawers open, focus
  behavior across the boundary is never deliberately managed.
- **Manual, error-prone state cleanup.** Each `onClose` resets related state by hand
  (`setDrawerContent(undefined)`, `formAddMovimentacao.resetFields()`,
  `setNomeLeitoState("")`), re-derived at every one of the 16 call sites rather than
  centralized once. `trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:489-690`

## Considered Options

1. **Lift and shift**: keep `DrawerBuilder` and per-page hand-wired booleans as-is.
   Rejected — every new nested drawer repeats the same hand-rolled stack/back/focus bugs.
2. **Routed pages / parallel routes** (e.g. intercepting routes, or an equivalent
   modal-via-URL pattern). Gives free back-button semantics and deep-linkability, but
   changes the "board stays visible" interaction model and reintroduces route-transition
   cost.
3. **Keep drawers as the visual pattern; add a generic overlay/stack manager.** A single
   stack-aware provider owns an ordered list of open overlays, assigns depth, closes only
   the topmost on Escape/back, and traps focus per level, while `DrawerBuilder`'s
   width/footer/close conventions remain the visual shell rendered by each stack entry.
4. **Third-party overlay-manager library** supplying the stack/focus-trap primitives,
   with `DrawerBuilder`'s conventions reimplemented as a themed variant on top.

## Decision Outcome

Recommend **Option 3**: keep the drawer-over-page visual pattern — well-suited to a
monitoring tool where peripheral context matters, and `DrawerBuilder`'s conventions are
worth preserving largely as-is — but replace per-page hand-wired booleans with a single
overlay-stack manager that every drawer call site registers with. It should own nesting
depth, Escape/back handling (closing only the topmost overlay), and per-level focus
trapping, centralizing logic today reimplemented ad hoc at 16 call sites and
inconsistently at nesting points like the setor page's chat-then-tabs drawer and
`ListOcupacoes`'s four-drawer stack. This is a recommendation pending team ratification,
including the concrete implementation (custom hook vs. adopting a library) and whether
any specific flow (e.g. sepsis protocol detail) warrants a full routed page instead.

### Consequences

**Good:**

- New nested-drawer flows get Esc/back/focus-trap behavior for free instead of each
  author re-deriving it.
- `DrawerBuilder`'s proven visual conventions are preserved, minimizing behavior change
  and reuse work.
- Centralized close-time state cleanup replaces today's manual, easy-to-forget per-site
  reset logic.

**Bad:**

- New infrastructure work with no legacy equivalent to port — the team designs the stack
  API (depth, registration, focus-trap ownership) from scratch.
- Promoting specific flows to routed pages for deep-linkability is out of scope here and
  needs its own per-flow review.
- Migrating 16 existing call sites to a new registration API is a real, if mechanical,
  migration cost to sequence rather than rewrite in one pass.
