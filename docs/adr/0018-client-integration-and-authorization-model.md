# 0018. Client-side authorization model and backend integration boundaries

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform's permission model is fine-grained (booleans like `can_manage_prescricao`, `can_assist_ocupacao`, `can_add_movimentacao`, `can_manage_camera`) and varies per company (`empresa`), across a strictly nested route hierarchy (`empresa/estabelecimento/setor/leito/ocupacao`). Every route needs an answer to "is this request allowed to see this page," every client component needs tenant/permission state to drive its own visibility logic, and several features (file attachments, the ICU bed camera) need to move binary/media data across the REST boundary to services that aren't the main Django-REST-Framework-shaped API. `trilhas-frontend:src/hocs/validateRoute.ts:1-38`; `trilhas-frontend:src/contexts/AuthContext/AuthContext.tsx:1-193`; `trilhas-frontend:src/components/DisplayVideoUti/DisplayVideoUti.tsx:1-71`. The question this ADR resolves is where real authorization is enforced, how client-side identity/permission/tenant state is cached and shared, and how binary/media integrations should cross the app-server boundary in the rebuild.

## The Legacy Decision

- Every page exports `getServerSideProps` calling `validateRoute(ctx)`, which reads the `trilhas.token`/`trilhas.permissions`/`theme.light` cookies via `nookies` and redirects to `/` only if no token is present. `trilhas-frontend:src/hocs/validateRoute.ts:1-38`
- `validateRoute` accepts an `ignorePermission` flag that **defaults to `true`** (permission enforcement off); no page in the repo was found passing `ignorePermission=false`, so SSR route enforcement is uniformly "logged in or not," never "authorized for this specific page." `trilhas-frontend:src/hocs/validateRoute.ts:1-38` (inventory §4.3)
- Real feature-level gating happens entirely client-side, via `useEffectivePermissions()` flags that control button/menu visibility (e.g. `can_assist_ocupacao`, `can_manage_prescricao`, `can_add_movimentacao`). `trilhas-frontend:src/hooks/useEffectivePermissions.tsx:1-28`
- Auth/tenant state (`user`, `permissions`, `empresaData`) lives in a single global React Context (`AuthProvider`): it re-verifies the token against `/verify-token/` on every mount, pulls all permissions, `logout()`s on refresh failure, and `signIn()` posts `/login/`, sets a 30-day `trilhas.token` cookie, and routes to `/empresa/{id}` (or the picker). There is **no query cache** — no react-query/SWR anywhere in `package.json` — so every consumer re-renders on any context change and there is no request de-duplication or staleness model. `trilhas-frontend:src/contexts/AuthContext/AuthContext.tsx:1-193`; `trilhas-frontend:package.json:18-40`
- 19 resource hook files (`hooks/networking/*`) each wrap one shared axios instance in `useCallback`-memoized `useGetX/usePostX/…` calls, and nearly every call site independently wraps the call in `try/catch`, funneling failures to a shared `handleApiError()` that assumes a DRF-shaped error body. `trilhas-frontend:src/hooks/networking/setor.ts:1-181`; `trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103`
- File uploads (`FileB64Convert`, `ImagePicker`, `FilePicker`) base64-encode file contents client-side, then `POST` the encoded payload to the REST API — not a signed direct-to-object-storage upload. (D-02 §6.2/§3.7; inventory §6.1)
- The ICU bed camera (`DisplayVideoUti`) is a bare `<iframe src={cameraURL}>` pointing at a separate camera microservice (`NEXT_PUBLIC_CAMERA_URL`, `/api/v2/...`), with a client-side CSS `blur(20px)` "privacy" toggle that is a **visual mask only** — the underlying stream keeps running, it is not stopped. `trilhas-frontend:src/components/DisplayVideoUti/DisplayVideoUti.tsx:1-71` (blur mechanics at lines 17-68). This is architecturally distinct from the Agora RTC telemedicine call path (`BuildVideoChat`/`VideoCall`). `trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:1-155`

## Evident Rationale

*(Inferred — not stated in the codebase.)* Permissions are numerous, fine-grained, and vary per company, so enforcing all of them at every nested SSR route was likely judged as heavy boilerplate given `validateRoute`'s per-page, opt-in (`ignorePermission`) design — leaving it off by default and doing the real check once, client-side, via a single hook (`useEffectivePermissions`) is the path of least resistance. A single global auth context with no cache is the simplest thing that works when no query-caching library is in the dependency tree at all — it wasn't a deliberate rejection of caching so much as caching never being introduced. Base64 upload and the camera iframe were plausibly the fastest way to integrate with, respectively, the existing REST backend (no separate signed-URL/storage auth needed client-side) and a separate camera vendor/microservice whose streaming protocol the frontend team likely didn't want to own.

## Assessment

**Strengths:**
- The pattern is at least *consistent* — one permission hook, one shared axios instance, one error-rendering path (`handleApiError`), one camera boundary — so a new engineer can learn the shape once and apply it everywhere. `trilhas-frontend:src/hooks/useEffectivePermissions.tsx:1-28`; `trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103`
- Separating passive ICU camera monitoring (iframe) from active telemedicine (Agora RTC) is a reasonable and clear split by use case, not an accidental duplication. `trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:1-155`
- Base64 upload and the iframe camera are both defensible *integration* choices in isolation: neither requires the frontend to own a second auth scheme (signed storage URLs, a camera-vendor SDK).

**Weaknesses:**
- Defaulting `ignorePermission` to `true`, with zero call sites overriding it, means SSR provides **no authorization defense-in-depth beyond "is logged in."** The design implicitly relies on the REST API enforcing real authorization independently, but nothing in the audited frontend confirms or exercises that boundary — a bug or bypass in `useEffectivePermissions` has no server-adjacent backstop at this layer. `trilhas-frontend:src/hocs/validateRoute.ts:1-38`
- The cacheless global `AuthContext` causes redundant refetching on every navigation with no request de-dup (compounding the per-page tenant refetch pattern addressed in ADR 0008). `trilhas-frontend:src/contexts/AuthContext/AuthContext.tsx:1-193`
- Base64 upload inflates payload size by roughly a third and routes binary data through the application server rather than a storage-optimized path — tolerable for small clinical attachments, costly for larger media. (D-02 §6.2)
- The camera iframe has no shared chrome, reconnect, or error-state handling of its own — it inherits whatever the embedded microservice happens to render.
- **Inconsistency worth flagging explicitly:** the camera's "privacy" blur is purely a client-side visual mask — the feed itself is never paused or stopped — a gap between the feature's apparent guarantee (patient privacy) and its actual behavior that a rebuild should not silently repeat. `trilhas-frontend:src/components/DisplayVideoUti/DisplayVideoUti.tsx:17-68`

## Considered Options

1. **Lift and shift**: keep `ignorePermission` defaulting to off, one global uncached auth context, base64 uploads, and the bare camera iframe. Rejected — carries forward the authorization gap, the redundant-refetch cost, and the unmanaged binary/media boundaries with no offsetting benefit.
2. **Deny-by-default route guard + query cache + revisit heavy binary/media boundaries.** Route guards require an explicit, typed permission declaration per route (no opt-out default); identity/permission/tenant state moves into a query-cache layer (e.g. react-query/SWR or framework loader cache) with de-dup and staleness control; base64 upload is kept for small clinical attachments but a signed direct-to-storage path is added for large media (video, imaging); the camera stays a separable backend service but is wrapped in a first-party player shell (consistent chrome, the existing blur-for-privacy toggle made to actually gate the feed, reconnect/error states) instead of a bare iframe.
3. **Fully server-driven authorization with no client permission hints** (server decides what markup exists at all; client renders no disabled/hidden branches). Rejected — closes the defense-in-depth gap but removes the ability to gracefully show disabled controls with explanatory UI, and still requires *some* client-side permission awareness to avoid a jarring all-or-nothing render.
4. **Rebuild the camera path as a native embedded player with a direct media protocol integration** (bypassing iframe entirely, owning the streaming client). Deferred — a larger scope change entangled with the camera microservice's own protocol/vendor choice, not solely a frontend-authorization decision; Option 2's player-shell approach captures most of the benefit without that dependency.

## Decision Outcome

Recommend **Option 2**: a deny-by-default route guard requiring explicit permission declarations per route (inverting the legacy default), backed by a client query-cache library replacing the single uncached global context, with base64 upload retained only for small attachments while signed direct-to-storage upload is evaluated for large media, and the ICU camera kept as a separable backend service but rendered through a first-party player shell rather than a bare iframe. This closes the authorization-default gap without pretending the frontend can replace server-side enforcement — the REST API must independently enforce authorization on every request regardless of what the client guard decides; the client-side guard is a UX/defense-in-depth layer, not the source of truth. This is a recommendation pending team ratification, in particular on which query-cache library and which storage-signing approach the platform's backend team adopts.

### Consequences

**Good:**
- Removes the standing security-posture risk of SSR route permission checks being off by default with no exceptions.
- A shared query cache eliminates redundant identity/permission/tenant refetching and gives components a consistent staleness model (complements ADR 0008's caching recommendation for tenant chrome data).
- A signed direct-to-storage path for large media removes the ~33% base64 overhead and stops routing large binaries through the app server for the cases that need it.
- A first-party camera player shell gives consistent error/reconnect handling and makes the privacy toggle behave as users likely already assume it does.

**Bad:**
- Requires coordination with whoever owns the REST API to confirm/verify server-side authorization actually exists per endpoint — this ADR can only fix client-side assumptions, not prove the backend enforces access control correctly.
- Introduces new infrastructure (a query-cache dependency, a route-guard convention, signed-URL issuance) that legacy did not need to build or maintain.
- A first-party camera player shell adds ongoing maintenance surface (reconnect/backoff logic, error states) that the iframe previously offloaded entirely to the camera microservice's own UI.
