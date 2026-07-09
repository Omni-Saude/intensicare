# 0008. PageContainer app shell with cascading per-page tenant refetch and client-side gating

Status: superseded by ADR-0019
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

Every authenticated screen in the legacy platform is nested inside `empresa/estabelecimento/setor` route params, and every one of those screens needs the same three things: tenant chrome (header, tenant color, breadcrumb-style trail, mobile nav), a guarantee that the viewer is authenticated and the relevant tenant record has loaded, and the actual `empresa`/`estabelecimento`/`setor` records themselves to render names and drive navigation. The legacy platform solved all three with one component, `PageContainer`, mounted by essentially every authenticated page (25 usages outside its own folder). `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:106-485` (inventory §4.1). Any rebuild has to decide whether to keep a single app-shell component doing all of this, and — separately — how tenant context is fetched/cached and where auth/tenant gating actually lives, since the legacy answers to those two sub-questions are the parts worth reconsidering.

## The Legacy Decision

- `PageContainer` receives `idEmpresaAtual`/`idEstabelecimentoAtual`/`idSetorAtual` as props (populated from Next.js route params by the calling page) and independently REST-fetches `empresa → estabelecimento → setor` on every mount, storing each in local `useState` and surfacing it via `onLoadEmpresa`/`onLoadEstabelecimento`/`onLoadSetor` callbacks — not read from any shared cache. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:114-179,198-212`
- The empresa fetch (`_getEmpresaAtual`) runs in a `useEffect` keyed on `idEmpresaAtual`; the estabelecimento/setor fetches run once via `useMountEffect`. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:198-212`
- On successful empresa load, it applies the tenant brand color by calling `changeColorTheme(`#${data.cor_primaria}`)` (ADR 0004). `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:120`
- It renders the mobile hamburger `Drawer` (`width="70vw"`, holding `ItensMenuMobile`) when `width < collapseRule` (1260px), plus the full desktop header: auto-reload `Switch`, `SwitchThemeButton`, `SelectEmpresaAtual`, a hand-built `Tag` breadcrumb trail, the WebSocket-driven notification bell, user tag, and config/profile/logout icon buttons. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227-323,324-432`
- It renders a back-button + `Typography.Title` row (setting `setBacking(true)` and delaying 200ms before `router.back()`) and a static "iTech Ltda" copyright footer with prod/homolog text keyed off `baseURL`. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:441-472,475-481`
- **Render is blocked entirely** behind `<LoadingAuth/>` until `token && empresaAtual.id && !loading` — i.e. the component's own JSX conditional is the auth/tenant gate. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227,483-485`
- The only server-side check is that each page's `getServerSideProps` calls `validateRoute(ctx)`, which reads the `trilhas.token`/`trilhas.permissions` cookies and redirects to `/` if no token is present; permission enforcement itself is opt-in via an `ignorePermission` parameter that **defaults to `true`** (off), and no page in the audited surface overrides it. `trilhas-frontend:src/hocs/validateRoute.ts:1-38` (inventory §4.3 → ADR 0018)

## Evident Rationale

*(Inferred — not stated in the codebase.)* A single shell component keeps every page thin: authors get header chrome, tenant color, mobile nav, and a loading gate for free just by mounting `PageContainer` with route-derived IDs, rather than re-implementing them per page. Fetching the empresa/estabelecimento/setor chain from props rather than a shared store is the simplest thing that works when there is no query-caching library in the stack (`AuthContext` itself has no cache, ADR 0018) — each page "just asks for what it needs" via props, which is a reasonable local decision in isolation but ignores that the same chain was very likely already fetched one navigation ago. Gating in the JSX conditional (rather than via redirect) is plausibly a hedge against an SSR/client auth-state mismatch: since SSR only confirms a cookie exists (`validateRoute`), the client still needs to independently verify the token and load tenant data before it is safe to render tenant-scoped chrome — a legitimate problem, solved by the easiest available mechanism (block the render) rather than by design.

## Assessment

**Strengths:**
- Centralizing chrome, tenant theming, and the loading gate in one component is a real win for consistency: 25 call sites get identical header/footer/drawer behavior with no copy-paste. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227-482`
- The breadcrumb-style `Tag` trail and mobile drawer are functionally adequate substitutes for a persistent nav, and are consumed uniformly (inventory §4.2).

**Weaknesses:**
- **Redundant refetch on every navigation, with no caching layer to absorb it.** Moving from the bed board to a settings page and back re-fetches empresa, estabelecimento, and setor from scratch each time, even though the IDs (and very likely the data) haven't changed. This is compounded by `AuthContext` having no query cache at all (ADR 0018), so there is no cross-component de-dup anywhere in the data layer — `PageContainer`'s local `useState` is the norm, not an outlier. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:114-179,198-212`
- **The three fetches use two different effect mechanisms** (`useEffect` keyed on `idEmpresaAtual` for empresa; `useMountEffect`, i.e. run-once-on-mount, for estabelecimento/setor) for what is conceptually one cascading load — an inconsistency that makes the actual refetch behavior on ID changes not obviously predictable by inspection. `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:114-133,137-179,198-212`
- **Client-side gating means SSR provides no real protection.** `validateRoute` only checks that a token cookie is present; the actual "is this user allowed to see this tenant" gate is `token && empresaAtual.id && !loading` inside `PageContainer`, evaluated after a REST round-trip on the client. A user with a stale/invalid token but a present cookie gets real markup streamed to them and only sees `<LoadingAuth/>` (or an error) once the client-side fetch fails — not a server redirect. `trilhas-frontend:src/hocs/validateRoute.ts:1-38`; `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227,483-485`
- **Route-level permission enforcement is off by default** (`ignorePermission = true`) and nothing overrides it, so the only real access control most routes get is this same client-side layer, layered on top of button/menu-level `useEffectivePermissions` checks — not a hard boundary. `trilhas-frontend:src/hocs/validateRoute.ts:9,28`

## Considered Options

1. **Lift and shift**: keep one shell component, keep per-mount REST fetch of the tenant chain, keep JSX-conditional gating. Rejected — carries forward both the redundant-refetch cost and the false sense of security from client-only gating with no changes.
2. **Single app-shell layout, tenant context backed by a shared cache (e.g. a query-cache library or framework data loader), auth/tenant check moved to a server boundary (middleware/loader) ahead of the shell.** Keep the "one shell owns chrome" idea, but the empresa/estabelecimento/setor chain is fetched once per unique ID set and served from cache to every consumer, and the gate that decides "may this request render this tenant" runs server-side (or at minimum, before the shell subscribes to data) rather than being encoded as a JSX ternary inside the layout.
3. **Split the shell**: a thin, cache-only "chrome" component (header/footer/drawer/theming) that reads context from a shared provider, plus a separate route-level guard/loader responsible for auth and tenant resolution. Decouples "what renders the chrome" from "what decides if the user may be here," at the cost of one more moving part per route tree.
4. **No shared shell — per-page composition of chrome primitives.** Rejected outright: it would reintroduce exactly the copy-paste inconsistency `PageContainer` was built to avoid, with no offsetting benefit; nothing in the audit suggests the "one shell" concept itself is the problem.

## Decision Outcome

Recommend **Option 2**, evolving toward Option 3 as the tenant hierarchy's read/write surface grows: retain a single app-shell concept for chrome consistency, but back the empresa/estabelecimento/setor context with a shared cache (a query-cache library, or the chosen framework's loader/route-data mechanism) keyed on the route IDs, so that navigating between pages under the same tenant does not re-issue the same three REST calls — the cache should serve already-fetched records and only refetch on ID change or explicit invalidation. Separately, move the authoritative auth/tenant gate out of the shell's render conditional and into a route-level guard that runs ahead of (or alongside) data fetching — ideally as close to the server boundary as the chosen framework allows — so that failing the gate prevents the protected UI from being sent to the client at all, rather than being masked by a loading state after the fact. Also make permission enforcement default to *on*, inverting the legacy default. This is a recommendation pending team ratification; the concrete caching primitive and the exact seam for the server-side gate should be settled once the framework and auth architecture for the new platform are chosen.

### Consequences

**Good:**
- Eliminates redundant empresa/estabelecimento/setor round-trips on in-tenant navigation, reducing latency and backend load on every page transition.
- Removes the inconsistency between the two current fetch-timing mechanisms (`useEffect` vs. `useMountEffect`) by centralizing fetch/cache logic in one place instead of duplicating it per shell instance.
- A server-side (or pre-render) gate closes the gap where protected markup can currently be produced before the client confirms access, and flipping the permission-enforcement default to "on" removes a standing security-posture risk.

**Bad:**
- Introduces a new dependency (a query-cache library or framework-specific loader convention) and a cache-invalidation surface that legacy did not have to reason about — e.g., what invalidates a tenant record after an edit in `FormEmpresa`.
- Moving the gate server-side requires the auth/permission check to be evaluated somewhere with access to the token before the shell renders, which may require restructuring how session state is threaded into routing — a larger change than the legacy's single-component approach, and one that needs to be co-designed with whatever auth architecture (ADR-level decision) the new platform adopts.
