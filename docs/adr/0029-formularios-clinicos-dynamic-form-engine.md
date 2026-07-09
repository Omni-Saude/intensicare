# ADR-029: Formulários Clínicos — Dynamic Form Engine Strategy

- Status: accepted
- **Date:** 2026-07-07

## Context and Problem Statement

IntensiCare needs a rendering engine for clinical assessment forms (RASS, CAM-ICU, BPS/NRS, Glasgow, SOFA) used at the bedside in the ICU. The project already has a working `lib/form-engine/` in `frontend-v2/` with basic field renderers (StringField, SelectField, NumberField, DateField, CheckboxField, BooleanField, MaskedField) and JSON-based form definitions. The engine currently handles three forms (RASS, CAM-ICU, BPS/NRS) via client-side TypeScript configs.

However, the system must scale to 49 legacy clinical rules — many of which involve structured data collection — and address several cross-cutting concerns that the current approach does not yet handle:

1. **Form versioning** — Clinical forms evolve over time (e.g., a new RASS guideline, an updated Glasgow coma scale threshold). The system must support concurrent versions of the same form and track which version was used for each submission.
2. **Offline capability** — Bedside assessments often happen in areas with intermittent network connectivity. Clinicians must be able to fill forms and have them sync when connectivity is restored.
3. **Validation consistency** — Validation logic must agree between client (react-hook-form + Zod) and server (Pydantic/FastAPI). A discrepancy could allow invalid data to reach the database or cause confusing UX errors.
4. **Dynamic field visibility** — Some forms need conditional logic: fields that appear, disappear, or change based on previous answers (e.g., CAM-ICU feature 3 depends on RASS score ≠ 0; BPS vs. NRS selection changes the pain scale).
5. **Audit trail** — Every form submission must be immutable, traceable to the clinician who filled it, the patient, the timestamp, and the exact form version used.

The question is: **what is the right architectural split between client and server for form definition, rendering, and validation?**

## Considered Options

### Option A — Client-Side Rendering with Static TypeScript/JSON Form Definitions (Current Approach)

Form schemas live as JSON files in the frontend codebase (`config/forms/*.json`). The `FormEngine` component loads them at build time, validates with Zod on the client, and posts raw data to the backend.

**Pros:**
- Already implemented and working for 3 forms.
- Fast — no network round-trip to fetch form definition; instant rendering.
- Naturally supports offline — forms are bundled in the SPA, so they render without a server connection.
- Simple mental model — form authoring is just editing a JSON file.

**Cons:**
- **No form versioning.** The JSON file is a single source of truth per form ID. Changing it changes every instance of that form, retroactively breaking audit trail.
- **Validation duplication.** Zod schemas are generated client-side from `FormConfig`; the backend has no access to the same schema. Adding server-side validation requires a separate Pydantic model that must be manually kept in sync.
- **No dynamic field visibility.** The current `FormConfig` schema has no concept of conditional logic (`showIf`, `hideWhen`, `dependsOn`). Extending it to support this would require a DSL and interpreter in the client, with no server awareness.
- **Tight coupling to frontend deploy.** Adding a new clinical form or updating an existing one requires a frontend release. Clinical teams cannot iterate on forms independently.
- **Glasgow/SOFA would require new JSON configs and new rules engine logic duplicated in the client.**

### Option B — Server-Driven Forms: JSON Schema from API

The backend owns all form definitions (stored in the database with versioning). The frontend calls `GET /api/clinical-forms/{formId}/schema?version=X` to fetch the form definition as a JSON Schema document. The `FormEngine` renders from the fetched schema. Validation is performed server-side, and the client shows server-returned errors.

**Pros:**
- **Built-in form versioning.** The database is the source of truth; each submission references the exact form version used.
- **Single validation source.** The backend defines the schema once (e.g., Pydantic models stored as JSON Schema). The client renders it; the server validates against the same artifact.
- **Dynamic updates without frontend deploys.** Clinical teams can create/update forms via an admin interface or API; the frontend picks up changes on next fetch.
- **Audit trail is natural.** Submissions are linked to a form version record in the database.
- **Dynamic field visibility can be part of the schema** (e.g., JSON Schema `if/then/else` or a `visibilityRules` extension), interpreted by both client and server.

**Cons:**
- **No offline support out of the box.** The form schema must be fetched. Without a caching/service-worker layer, a clinician with no network cannot open the form.
- **Slower first render.** Every form open requires a network round-trip. Acceptable on a good LAN, but adds latency.
- **More complex backend.** Requires a form schema management system: CRUD for form definitions, version history, migration of existing JSON configs into the database.
- **Client rendering logic becomes generic.** The `FormEngine` must become a fully general JSON Schema renderer, which is harder to optimize for clinical-specific UX (e.g., RASS slider, pain scale visualization).

### Option C — Hybrid: Client-Side Rendering with Server-Side Validation and Schema Sync

Form definitions live in the frontend as JSON configs (Option A pattern) but are also stored and versioned in the backend database. The client renders from its bundled config, submits data to the backend, and the backend validates against its own copy of the schema (derived from the same source, kept in sync via a build-time or CI step). On submission, the backend also checks that the client's form version matches the latest or a compatible version.

**Pros:**
- **Offline-first.** Forms are bundled in the SPA and render instantly without network.
- **Versioning via backend.** The database record ties each submission to the form version known to the backend. The client bundles a specific version; the server rejects submissions with stale or unknown versions.
- **Single source of truth for validation.** The JSON config is the authoring format. A build step generates both the Zod schema (client) and Pydantic models (server), ensuring consistency.
- **Incremental migration.** The current JSON configs can be migrated into the database without rewriting the rendering engine.
- **Dynamic field visibility can be added to `FormConfig`** (e.g., a `visibility` property with `dependsOn` + `condition`) and interpreted by the client. The server can optionally validate that visibility rules were honored (e.g., required fields hidden by logic should not be enforced server-side if the condition was not met).

**Cons:**
- **Dual maintenance risk.** If the build-step synchronization breaks, client and server schemas drift. Requires discipline and CI checks.
- **Version negotiation complexity.** The client must know its bundled version and the server must decide whether to accept it or redirect to a newer version.
- **Still requires a backend schema store.** The database must hold form definitions, versions, and a sync mechanism.
- **Offline submissions need a local queue.** Submissions made offline must be stored locally (e.g., IndexedDB) and replayed when connectivity returns, with conflict resolution if the form version changed in the meantime.

## Decision Outcome

**Chosen: [C] Hybrid — Client-Side Rendering + Server-Side Validation with Schema Sync**

The hybrid approach (Option C) is chosen because it satisfies all five forces without sacrificing the working client-side rendering engine:

| Force | How Option C Addresses It |
|---|---|
| **Form versioning** | Form definitions versioned in DB; each submission references the exact version. Bundled client configs carry a version marker. |
| **Offline capability** | Forms bundled in SPA → render without network. Offline submissions queued in IndexedDB, synced on reconnect. |
| **Validation consistency** | Single JSON config source → build step generates Zod (client) + Pydantic (server). CI enforces parity. |
| **Dynamic field visibility** | Extend `FormConfig` with a `visibility` DSL (`dependsOn`, `condition`, `action: show/hide`). Client evaluates; server validates that hidden required fields are not enforced. |
| **Audit trail** | Immutable `form_submissions` table with `form_version_id`, `clinician_id`, `patient_id`, `submitted_at`, `data` (JSONB). |

### Implementation Plan

1. **Extend `FormConfig` types** to include:
   - `version: string` (semver) on the form config root.
   - `visibility?: VisibilityRule[]` on fields: `{ dependsOn: string; condition: 'eq' | 'neq' | 'gt' | 'lt' | 'in'; value: any; action: 'show' | 'hide' }`.
2. **Create a backend `form_definitions` table** with columns: `id`, `form_id`, `version`, `schema_json`, `created_at`, `deprecated_at`.
3. **Build a sync script** (or pre-commit hook) that:
   - Reads JSON configs from `config/forms/`.
   - Inserts/updates records in the `form_definitions` table.
   - Generates Pydantic validation models from the same config.
4. **Enhance the `POST /api/clinical-forms` endpoint** to:
   - Accept a `form_version` field alongside `form_type` and `data`.
   - Look up the form definition by `form_type` + `form_version`.
   - Validate `data` against the server-side Pydantic model before accepting.
   - Return `409 Conflict` if the client version is stale, with a hint to reload.
5. **Add offline queue** to the frontend:
   - Use a service worker or IndexedDB wrapper to cache form configs and queue submissions.
   - On reconnect, replay queued submissions, handling version conflicts with user prompts.
6. **Add audit table** `form_submissions`:
   - Columns: `id`, `form_definition_id` (FK), `clinician_id`, `patient_id`, `submitted_at`, `data` (JSONB), `client_version`, `offline_submission` (boolean).

### Consequences

**Positive:**
- Clinicians can fill forms at the bedside regardless of network status.
- The backend becomes the authoritative record for what was submitted, with which form version, by whom, and when.
- Clinical forms can evolve without breaking historical audit data.
- Validation consistency is enforced by CI, not by developer discipline alone.
- The existing `FormEngine` and JSON configs are preserved and extended, not replaced.

**Negative:**
- Increased architectural complexity: form versioning, sync pipeline, and offline queue are new subsystems.
- The build-step sync is a potential point of failure; it must be monitored.
- Dynamic field visibility adds client-side evaluation logic that must be carefully tested.
- Offline conflict resolution (stale version) requires UX design: prompt to reload vs. submit anyway.

**Risks:**
- If the sync pipeline is not run before deploy, client and server schemas will diverge.
- Offline queue could accumulate large submissions on devices with limited storage.
- Glasgow and SOFA forms may have scoring logic (not just data collection) that requires server-side computation beyond simple validation.

## References

- `src/intensicare/api/clinical_forms.py` — current FastAPI endpoint for form submission.
- `frontend-v2/lib/form-engine/` — client-side rendering engine (FormEngine.tsx, types.ts, renderers/).
- `frontend-v2/config/forms/{rass,cam-icu,bps-nrs}.json` — existing JSON form definitions.
- `intensicare/docs/rules/` — 49 legacy clinical rules, many requiring structured data capture.
- MADR template: https://adr.github.io/madr/
