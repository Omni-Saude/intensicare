# 0016. Error-feedback and loading-state patterns

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform has no differentiated way to surface failure to a user, and no documented rule for how a screen should indicate "something is happening." Every REST error — a field validation issue, a permission denial, a 500 — reaches the user through one function, `handleApiError`, which always opens the same AntD `Modal.error` (`trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103`). Separately, screens pick between two unrelated loading affordances — generic skeleton rows or a full-screen blocking spinner — with no written guidance on when to use which (inventory §5.4). For a clinical tool where staff triage multiple patients and may need to keep working while a request is in flight, both gaps matter: severity-blind errors train users to modal-dismiss everything without reading it, and blocking spinners stop all interaction for even minor mutations. The question this ADR resolves: what should the new platform's error-surface and loading-state model be, given what the legacy system actually did and where it fell short?

## The Legacy Decision

**Error surface.** `handleApiError` is a single exported function, not a client interceptor, called individually inside REST `catch` blocks — confirmed at 86 call sites across 39 files (`grep` over `trilhas-frontend:src`). It takes an `Utils.ApiError` (`{ errors: Utils.ApiError.Errors }`, `trilhas-frontend:src/@types/models/Utils.d.ts:21-27`) plus optional `title`/`content`/`meanings`, and always renders an AntD `Modal.error` (`trilhas-frontend:src/utils/feedback/handleApiError.tsx:29-102`). When `error.errors` is non-empty it additionally renders a field-by-field list: each field name uppercased, each issue — flat string, array of strings, or nested `{ field: string[] }` objects — rendered as a `Tag color="warning"` with a fixed `mdiAlertDecagram` icon (`trilhas-frontend:src/utils/feedback/handleApiError.tsx:37-96`). Every issue gets the identical amber warning tag regardless of whether it is a required-field validation, a permission denial, or a server-side fault; there is no `severity`/`type` parameter and no branching on HTTP status code anywhere in the function.

**Loading affordances.** `SkeletonList` renders `rows` (default 4) generic `Skeleton.Button` rows of fixed `itemHeight` (default 40px) inside a `Form`, or an `Empty` state if `errorMessage` is passed — the shape is not adapted to the content being loaded (`trilhas-frontend:src/components/SkeletonList/SkeletonList.tsx:1-40`). `FadeLoading` renders a `<section>` fixed to the full viewport (`position: fixed; top:0; left:0; width:100%; height:100%`) with a translucent background and a centered spinning icon (`trilhas-frontend:src/components/FadeLoading/FadeLoading.tsx:1-23`; `trilhas-frontend:src/components/FadeLoading/FadeLoading.less:1-16`) — it blocks the entire screen, not just the affected region. Inventory §5.4 records the split as "chosen per-screen with no documented rule": `SkeletonList` for initial list/page loads, `FadeLoading` for most mutations.

## Evident Rationale

*(Inferred — not stated anywhere in code or comments.)* One shared error function called from every `catch` block gave the team app-wide visual consistency for failure states with minimal per-screen boilerplate — a developer only had to remember one import, not design a dialog each time. Assuming a DRF-shaped `errors` object was a reasonable simplification when the backend is a single Django REST Framework service always returning that shape. The skeleton/spinner split plausibly mapped to a simple mental model — "loading a page" vs. "doing a thing" — without anyone formalizing when a mutation is small enough to not need a full block.

## Assessment

**Strengths:**
- A single error utility meant every failure in the app looked the same, which is better than 39 files independently inventing error UI (`trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103`, 86 call sites).
- The nested-issue rendering (string | string[] | `{field: string[]}[]`) shows real effort to cope with DRF's variably-shaped validation payloads without crashing the UI.
- `SkeletonList`'s `errorMessage` fallback to `Empty` is a reasonable, if minor, extra affordance beyond a bare loading state.

**Weaknesses:**
- No severity differentiation: a missing-required-field validation, a 403 permission denial, and a 500 server fault all produce the identical `Modal.error` with the identical amber `Tag` list — the visual weight never matches the actual stakes, and staff have no way to tell "fix this field" from "you're not allowed" from "the server is down" without reading prose (`trilhas-frontend:src/utils/feedback/handleApiError.tsx:29-96`).
- Coupled to a specific backend shape: the function assumes `Utils.ApiError.errors` is always DRF-shaped (`trilhas-frontend:src/@types/models/Utils.d.ts:21-27`), so any non-DRF failure (network timeout, a gateway error with a different body) either renders the generic fallback `content` string or breaks the field-list rendering.
- Not centralized: because it is invoked individually in 86 `catch` blocks rather than once in an axios interceptor, every REST call site is a place a developer could forget to call it (silent failure) or call it inconsistently (different `title`/`meanings`), and there is no single point to add retry, telemetry, or offline handling later.
- Always a blocking modal: `Modal.error` requires an explicit dismissal for even a minor validation issue, which is heavier interaction cost than the failure often warrants.
- The loading-state split has no written rule (inventory §5.4), so the choice of skeleton vs. full-screen block is inconsistent by convention rather than by design intent — a developer adding a new screen has nothing to consult.
- `FadeLoading` blocks the entire viewport for "most mutations" (inventory §5.4), including presumably small ones — in a clinical tool where a nurse may need to glance at a different bed's card or dismiss a notification while a save is in flight, a full-screen block is disproportionate friction for anything short of a destructive, app-wide operation.
- `SkeletonList`'s fixed generic rows (`Skeleton.Button`, uniform `itemHeight`) do not reflect the shape of what is loading (a card grid, a table, a form), so the loading state gives no visual continuity into the loaded content.

## Considered Options

1. **Port both mechanisms as-is** (single `Modal.error` utility, unshaped skeleton, full-screen spinner). Fastest, but reproduces the severity-blindness, DRF coupling, and heavy-handed blocking documented above.
2. **Centralize error handling in the HTTP client with a severity parameter and UI decoupled from DRF shape.** Move error interception into an axios (or fetch wrapper) interceptor so no call site can forget it; classify failures by HTTP status / an explicit `severity` (`validation` | `permission` | `server`) independent of any one backend's error-body shape; map severity to visual weight (e.g. inline field errors or a non-blocking toast for `validation`, a dismissible banner for `permission`, a modal reserved for `server`/unrecoverable faults). Keep the "one surface, many call sites" simplicity legacy got right, drop the one-size-fits-all rendering.
3. **Adopt a general-purpose toast/notification library end-to-end** (e.g. all failures as toasts, no modals at all), for maximum non-blocking-ness. Simpler to build than option 2, but risks under-representing genuinely blocking failures (e.g. "you have been logged out") that legitimately need acknowledgment before the user proceeds.
4. **Formalize the loading rule explicitly**, independent of which error option is chosen: list/page-level loads render content-shaped skeletons (matching the eventual layout, not generic bars); discrete mutations render a small, localized inline spinner (on the triggering button/row/section) rather than a full-screen overlay; a full-screen block is reserved for operations that are both destructive and app-wide (e.g. session-ending actions), and even then should be the exception, not the default.

## Decision Outcome

Recommended (pending team ratification): **Option 2 for errors, combined with Option 4 for loading.** Keep the legacy's one genuinely good idea — a single, centrally-invoked error-handling surface — but fix its two structural flaws: move invocation from 86 scattered `catch` blocks into an HTTP-client interceptor so it cannot be skipped or invoked inconsistently, and add an explicit severity/type classification (validation vs. permission vs. server) so the UI (inline message, toast, or modal) is chosen by actual stakes rather than uniformly defaulting to `Modal.error`. The severity classification must not assume any particular backend error-body shape (unlike the legacy's DRF-specific `errors` object) so the new platform is not locked to one backend framework's conventions. For loading, adopt Option 4 as a documented rule in the component library: list/page loads get content-shaped skeletons; discrete mutations default to localized, non-blocking inline spinners; a full-screen block is reserved for the rare destructive/app-wide case and requires explicit justification, reversing the legacy default of blocking on "most mutations." This matters more in a clinical, AI-agent-assisted context than a typical CRUD app: staff routinely have several concurrent tasks in view (a bed card, a chat, a form), and an AI agent proposing an action on the user's behalf needs the UI to distinguish "this needs your attention now" from "this is still processing" without stopping everything else on screen.

### Consequences

**Good:**
- Centralizing in the HTTP client removes an entire class of "someone forgot to call handleApiError" silent failures and gives one place to later add retry/telemetry/offline handling.
- Severity-differentiated UI lets staff triage their own attention — a minor validation Tag no longer looks as alarming as a permission or server fault, and vice versa.
- Backend-shape independence means the error-handling layer survives a backend migration or a second backend (e.g. a FHIR service alongside a core API) without a rewrite.
- Defaulting mutations to non-blocking inline feedback matches how clinical staff actually work — multiple patients, frequent interruption — better than the legacy's blanket full-screen spinner.

**Bad:**
- Building severity classification and multiple UI treatments (inline/toast/modal) is more design and engineering work up front than reusing one `Modal.error` call for everything.
- An interceptor-based model requires discipline to keep call-site-specific context (which field, which action) flowing through to the centralized handler, something the legacy's per-call-site `meanings`/`title` props did trivially by being invoked locally.
- Reserving full-screen blocking for a rare, explicitly justified case means every new destructive/app-wide flow needs a deliberate design decision instead of defaulting to the safe-feeling (if heavy-handed) legacy spinner.
