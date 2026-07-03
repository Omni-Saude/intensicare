# 0009. Information architecture: drill-down tiles, header switcher, and FAB with no persistent nav

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

IntensiCare's data model is a strictly nested hierarchy — `empresa` (hospital group) → `estabelecimento` (facility) → `setor` (ward) → `leito` (bed) → `ocupacao` (occupancy/stay) — and every one of the legacy platform's 27 routed pages lives at some depth of that tree. `trilhas-frontend:src/pages/**/*.tsx` (route map, inventory §4.3). Clinicians and administrators need to move both *down* the hierarchy (drill into a specific bed) and *across* it (jump from one ward to a sibling ward without walking back up), and they need to always know where they are. Any rebuild has to decide, deliberately, how users find their way through that depth — the legacy platform never made this decision explicitly; it accreted five different partial mechanisms.

## The Legacy Decision

There is **no persistent left/side navigation and no AntD `Menu`** driving primary navigation anywhere in the app. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:106-485` (inventory §4.1, §4.2). Wayfinding is instead composed of five independent mechanisms:

1. **Drill-down tile grids.** `DisplayCard`/`ListDashboard` (empresa → estabelecimento) and `ItemDefault`/`ListItem` (settings tiles) each wire `onClick` directly to `router.push` — one tile, one hop down the tree. `trilhas-frontend:src/components/DisplayCard/DisplayCard.tsx:1-27`; `trilhas-frontend:src/components/ItemDefault/ItemDefault.tsx:1-48`.
2. **Header context switcher.** `SelectEmpresaAtual` and `ItensMenuMobile` (three swap cards for Empresa/Estabelecimento/Setor, each calling `onSwicth(destiny)`) let a user jump sideways between siblings without re-drilling from the top. `trilhas-frontend:src/components/ItensMenuMobile/ItensMenuMobile.tsx:1-72`.
3. **`CircularMenu` FAB.** A floating-action-button that expands a `translate3d`-animated stack of `Tooltip`-labeled actions (Filtrar/Expandir/Mensagens/Relatórios/Dashboard) on the bed-board page only. `trilhas-frontend:src/components/CircularMenu/CircularMenu.tsx:1-65`.
4. **A hand-built, clickable `Tag` trail** in the header showing estabelecimento/setor names, each tag an `onClick` that calls `navigate(...)` — functioning as a breadcrumb but implemented ad hoc inside `PageContainer` rather than as a reusable component. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:330-357`.
5. **Permission-filtered settings tiles.** `useMenuByPermissions` builds the `/configuracoes` tile list purely from boolean flags (`can_manage_empresa`, `can_manage_grupo_acesso`, `can_manage_usuario`), each producing a `{route, nome, image}` tuple. `trilhas-frontend:src/hooks/useMenuByPermissions.tsx:1-111`.

Separately, a fully-built, AntD `Breadcrumb`-based `Breadcrumbs` component exists — it parses `router.asPath`, skips 36-character (UUID-length) segments, and capitalizes the rest — but it is imported nowhere in the codebase. `trilhas-frontend:src/components/Breadcrumbs/Breadcrumbs.tsx:1-58` (confirmed zero call sites outside its own folder by repo-wide grep).

## Evident Rationale

*(Inferred — not stated in the codebase.)* The hierarchy is deep (5 levels) and strictly nested with no cross-cutting or many-to-many relationships, so tile-per-level drill-down maps naturally onto it and requires no navigation component more sophisticated than a click handler per card. The header switcher plausibly exists because pure drill-down would otherwise force a user managing multiple wards to walk back up to `empresa` and back down every time they change context — a real usability gap the switcher patches directly. The `CircularMenu` FAB is scoped to the one screen (the bed board) with a distinct set of page-level actions that don't fit the tile or breadcrumb metaphor, so it was solved locally rather than folded into a global nav.

## Assessment

**Strengths:**
- Drill-down tiles are a reasonable, low-effort fit for a hierarchy this strictly nested — no page needs to reach a sibling subtree it isn't inside.
- The header switcher correctly identifies and patches the one real gap in pure drill-down (lateral movement between siblings) rather than over-building a full nav for it.

**Weaknesses:**
- **No persistent wayfinding beyond the bespoke `Tag` trail.** The only always-visible "where am I" affordance is two clickable tags built inline inside `PageContainer`, not a dedicated, reusable breadcrumb component — despite one having been fully built. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:330-357` vs. `trilhas-frontend:src/components/Breadcrumbs/Breadcrumbs.tsx:1-58`.
- **Built-then-abandoned duplication.** The dead `Breadcrumbs` component is a real AntD `Breadcrumb` with UUID-aware path parsing — someone solved this problem generically once, and the header trail solves a narrower version of the same problem again, by hand, in a different file. This is the same governance pattern the inventory flags elsewhere (duplicated token files, two tab implementations, two icon systems): a component gets built, a second ad hoc version ships anyway, and the first is never wired in or deleted.
- **The `Tag` trail is depth-limited and hand-maintained.** It only ever shows estabelecimento and setor (`trilhas-frontend:src/components/PageContainer/PageContainer.tsx:330-357`) — it does not extend to leito/ocupação, so the deepest pages (bed video, fluid balance, prescription, sepsis protocol) have no breadcrumb trail at all, only the back-button + page-title row also rendered by `PageContainer`.
- **Wayfinding logic is scattered across five uncoordinated mechanisms** (tiles, switcher, FAB, tag trail, permission-filtered tiles) with no single component owning "where the user is and where they can go," making it hard to reason about or extend consistently as new sections are added.

## Considered Options

1. **Lift and shift**: keep tile-drill-down + header switcher + FAB + hand-built tag trail as-is. Rejected — perpetuates the exact duplication (dead `Breadcrumbs` vs. live ad hoc trail) and depth-limited breadcrumb this ADR exists to fix, and gives a new engineer no single place to add wayfinding for a new nesting level.
2. **Tile-drill-down + one persistent, reusable breadcrumb component**, used on every authenticated page rather than only in `PageContainer`'s header, extended to cover the full path down to leito/ocupação, with the header switcher retained for lateral movement between siblings. Closest to the legacy shape, but resolves the duplication and depth gap directly.
3. **Persistent collapsible sidebar** listing the current empresa/estabelecimento's children (setores, or leitos), replacing tile grids as the primary drill mechanism, with a breadcrumb for depth beyond what the sidebar shows. Gives always-visible lateral + hierarchical context in one surface, at the cost of persistent screen real estate on data-dense clinical screens (bed board, dashboards) where every pixel is contested.
4. **Command/search-first navigation** (a global "jump to ward/bed" search or command palette) layered on top of either option 2 or 3, aimed at an AI-agent-led platform where an agent or power user may want to jump directly to a deep node without walking the tree. New capability, not a lift-and-shift of anything legacy had.

## Decision Outcome

Recommend **Option 2**: keep drill-down tiles as the primary "explore" mechanism (it fits the strict hierarchy and requires no new IA concept), keep a header context switcher for lateral movement, but replace the ad hoc `Tag` trail with **one** persistent, reusable breadcrumb component — built once, mounted in the shared app shell on every authenticated page, and extended to represent the full path (empresa → estabelecimento → setor → leito → ocupação) rather than stopping at setor. This is the smallest change that removes both defects the audit found (duplicated component, depth-limited trail) without asserting a sidebar is needed for a hierarchy this well-suited to drill-down. Option 4's search/command affordance is worth layering in later, especially for an AI-agent-led platform where an agent may need to address a deep node directly, but it is additive scope and should be proposed separately once the core IA (option 2) is in place. This is a recommendation pending team ratification — the option 3 sidebar tradeoff (persistent orientation vs. screen real estate on the bed board) should be validated with clinical users before being ruled out permanently.

### Consequences

**Good:**
- One breadcrumb component, one place to fix bugs or extend depth, eliminating the built-twice pattern the audit found.
- Full-depth breadcrumb coverage means the deepest clinical screens (bed video, fluid balance, prescription, sepsis protocol) finally get a "where am I" affordance they never had.
- Preserves what worked: tile-drill-down still matches the hierarchy's shape, and the header switcher still handles the lateral-movement gap tiles alone can't.
- Low migration cost relative to option 3 — no new persistent chrome to design, test, and keep responsive across breakpoints.

**Bad:**
- Does not solve orientation for users managing many wards/facilities as well as a persistent sidebar listing siblings would — breadcrumbs show the path already taken, not the paths available from here, so discoverability of siblings still depends on the header switcher being used correctly.
- If the new platform later adds cross-cutting views that don't fit the strict tree (e.g. an agent-facing "all critical beds across facilities" view), pure drill-down + breadcrumb will strain, and option 3 or 4 will need revisiting sooner rather than later.
- Requires discipline the legacy team didn't maintain (they built `Breadcrumbs` once and still duplicated it) — needs an explicit lint/review rule ("no ad hoc breadcrumb-like trails outside the shared component") to actually stick.
