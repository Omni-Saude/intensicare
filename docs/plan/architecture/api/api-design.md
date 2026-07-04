# IntensiCare v2 — API Design

**Owner:** api-designer · **Companions:** `openapi.yaml` (REST), `asyncapi.yaml` (WebSocket + SSE) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This document is the *why* behind the two machine specs. It states the principles, the
versioning and breaking-change policy, pagination, idempotency, rate limiting, and the error
envelope — each with a worked example — so that every future endpoint added to `openapi.yaml`
or event added to `asyncapi.yaml` inherits one consistent contract instead of re-deriving it.
Nothing here overrides the machine specs; where a description disagrees, the YAML wins
(mirroring the discipline in `docs/plan/clinical/units-registry.md` §"machine registry wins").

Every rule below cites a source: a brief fact id (`VIS-*`, `ADR001-*`, `IMP-*`, `DM-*`,
`PER-*`), a ledger constraint (`CON-*`), or a companion design doc
(`alert-engine.md`, `severity-model.yaml`, `units-registry.md`).

---

## 1. Principles

1. **IntensiCare is a consumer, not a data platform (ADR-001).** This API fronts
   IntensiCare's own operational PostgreSQL/TimescaleDB store — computed scores, active
   alerts, threshold configs (`ADR001-C-03`/`CON-0003`) — never the AMH analytical lakehouse
   directly. No endpoint here performs ad-hoc Athena queries on demand; the alert-engine's
   micro-batch/NRT runners are the only Athena callers (`alert-engine.md` §1). Clients never
   see a raw AMH Gold table shape — every resource is IntensiCare's own operational
   representation, insulating clients from Gold schema changes (`ADR001-C-09`/`CON-0009`).

2. **Advisory, never automated.** No endpoint issues a diagnosis or a binding clinical order.
   `acknowledge` / `act` / `resolve` / `escalate` are audited records of a *human* decision
   (`VIS-C-01`, `VIS-C-08`). The API's job is to make the evidence for that decision
   legible — every alert exposes which parameter triggered it, with value, unit, and trend
   (`CON-0090`/`PER-C-04`) — not to make the decision.

3. **One severity scale, everywhere.** `normal | watch | urgent | critical`
   (`#/components/schemas/Severity` in both specs) is used identically for a patient's score
   band and an alert's severity, on every REST resource and every realtime event. It is never
   re-derived per-endpoint and never conflated with a tenant's `brand.*` color
   (`CON-0041`/`ADR-C-08`). See `alert-engine.md` §3 for the full mapping from the legacy
   `CRIT/URG/WARN/INFO` catalog scale and from the current `alert.severity` DB enum.

4. **The realtime channel is derived state, not a second source of truth.** Every WebSocket/SSE
   event is either a full snapshot of a REST resource or a thin patch reconcilable against it
   (`CON-0045`/`ADR-C-12`). A client that misses events (reconnect, buffer overflow) always has
   a REST endpoint to reconcile against (`GET /alerts`, `GET /dashboard/bed-grid`) — see §8.

5. **Nothing invented, everything cited.** Every enum value, SLA number, and unit in the specs
   traces to a brief fact or ledger constraint. Where the source is silent (e.g. an exact HTTP
   status choice), this document states the design decision explicitly rather than leaving it
   implicit, so a reviewer can tell "traced" from "designed."

---

## 2. Versioning policy

- **URL versioning, major only:** `/api/v1/...`. The version segment changes **only** for a
  breaking change (§2.1). Additive/backward-compatible evolution (new optional field, new
  endpoint, new enum value behind an opt-in header) ships within `v1` — clients do not need a
  new URL to get new capability.
- **Header echo for traceability:** every response carries `X-API-Version: 1.0.0` (semantic
  minor.patch within the major URL version) so support/observability can correlate a bug
  report to an exact contract revision without guessing from the `Sunset` history.
- **One prior major version supported concurrently.** When `v2` ships, `v1` is not deleted the
  same day — see the deprecation window in §2.2. Given IntensiCare's ICU-safety posture, a
  version bump is treated with the same gravity as an AMH Gold schema change
  (`ADR001-C-09`/`CON-0009`): planned, dated, and communicated ahead of time, never silent.

### 2.1 What counts as breaking

A change is breaking — and therefore requires a new major version, never a silent `v1` mutation —
if it would make an existing, spec-conforming client either **crash** or **silently
misinterpret clinical data**. The second clause is the one that matters most here: this API
carries severity bands and clinical values, so "the client still parses the response" is not a
sufficient bar.

| Change | Breaking? | Rationale |
|---|---|---|
| Add a new optional response field | No | Existing clients ignore unknown fields (`additionalProperties` not `false` anywhere in `openapi.yaml`/`asyncapi.yaml` response schemas). |
| Add a new optional request field with a safe default | No | — |
| Add a new endpoint or a new event type | No | Additive. |
| Add a new enum value to `Severity`, `AlertStatus`, `ScoreType`, or `Resolution` | **Yes** | An enum consumer that `switch`es exhaustively (a clinician-facing severity color map, for instance) will silently mis-render an unrecognized value — exactly the class of "renders but lies" defect this platform was built to eliminate (`CON-0041`/`CON-0182`, the P0-10 downgrade-defect class). New enum values are additive **only** behind a version bump, or introduced first as a documented, opt-in `x-status: planned` value (as `/auth/sso/*` are today) with a migration window before default-on. |
| Remove or rename a field, or change a field's type/unit | **Yes** | Especially units: silently changing a field's unit is exactly the SYS-01/02/03 defect class (`units-registry.md`) — never done without a major version, ever, regardless of how "small" the field. |
| Change a field's semantics without changing its name/type (e.g. redefine what `data_as_of` means) | **Yes** | The dangerous, easy-to-miss case — flag any such PR for `api-designer` + `alert-engine-architect` sign-off explicitly; CI cannot catch a meaning change. |
| Tighten a request validation rule | **Yes**, unless the tightened rule already matches 100% of observed traffic for ≥30 days | A previously-accepted request must not start failing without notice. |
| Change a default value | **Yes** | A default is part of the contract for any client that omits the field. |
| Change HTTP status code for an existing error condition | **Yes** | Clients branch on status codes; §7's registry is the frozen mapping. |

### 2.2 Deprecation window

1. Announce: `Deprecation: true` + `Sunset: <RFC 7231 date>` response headers on the endpoint
   or field being retired, plus a changelog entry, **at least 90 days** before removal (aligned
   to the platform's slower-moving compliance cadence — ANVISA/LGPD artifacts are also produced
   on a quarterly rhythm, `IMP-C-08/09`). Critical-path clinical endpoints (alert lifecycle,
   `/health`) get a **180-day** minimum window.
2. During the window, the deprecated shape and its replacement are both live and both fully
   supported — this is how `/auth/login` survives the ADR-001 SSO cutover (§9) without a flag
   day.
3. Removal only after the Sunset date **and** telemetry shows zero production traffic on the
   deprecated shape for 14 consecutive days, or an explicit, dated exception signed off by
   `platform-reliability-engineer`.

---

## 3. Multi-tenancy and scope resolution

Every list/read endpoint is implicitly scoped to the caller's JWT `tenant_id` claim (`§9`).
`unit` and `bed_id` narrow further and are **required, not optional**, on endpoints whose
result set would otherwise be unbounded across a hospital network (`GET /dashboard/bed-grid`,
`GET /dashboard/metrics`) — an accidental "all beds, all tenants" query is exactly the kind of
request a rate-limit-and-forget design would let through; requiring `unit` makes the request
shape itself bound the blast radius. A `platform-admin` role may pass `tenant_id` explicitly to
cross tenants; every such cross-tenant read is audited the same way a threshold write is
(`AuditEntry`, INV-1) even though it is a read, because "which platform admin looked at which
hospital's data" is itself an LGPD-relevant fact.

---

## 4. Pagination

**Cursor-based, not offset-based**, on every list endpoint (`GET /patients`, `/alerts`,
`/thresholds`, vitals/scores sub-lists). Rationale: these are TimescaleDB hypertables
(`DM-C-03/04/05`) receiving continuous inserts; an offset computed against a moving result set
skips or duplicates rows under concurrent writes, which is unacceptable for an audit-adjacent
alert list. A cursor is an opaque, server-signed token encoding `(sort_key, tiebreaker_id)` —
clients must never parse or construct one.

- `limit` — default `50`, max `200`. A request for `limit=500` is **not** an error; it is
  clamped to `200` and the response's `meta.limit` reports the clamped value, so a naive client
  gets a working (if smaller-than-asked) page rather than a `400`.
- `meta.next_cursor` — `null` when there is no further page; pass verbatim as `?cursor=` to
  continue.
- `meta.has_more` — always present, cheap to compute (fetch `limit + 1`, trim). Prefer this over
  `total_count_estimate` for "is there more" UI logic.
- `meta.total_count_estimate` — nullable, approximate, **never exact-counted on every page**
  (a `COUNT(*)` on a hypertable per page load is a latency and Athena-adjacent-cost hazard we
  do not want to normalize). Use only for an approximate "~1,240 alerts" label, never for
  pagination math.
- **Default sort** is always the resource's natural time axis descending (`created_at` for
  alerts, `recorded_at` for vitals, `calculated_at` for scores) — "newest first" matches how a
  clinician actually scans a list, and matches the hypertable's physical chunk order for
  cheap cursoring.

---

## 5. Idempotency

Every state-changing endpoint accepts an `Idempotency-Key` request header (client-generated
UUIDv4). This is layered on top of — not a replacement for — the alert engine's own semantic
dedup key (`alert-engine.md` §4.2: `dedup_key = mpi_id + alert_definition_id (+ window_bucket)`
for alert creation, natural keys for ingestion). The two serve different failure modes:

- **`dedup_key` (semantic, engine-owned):** answers "is this the *same clinical event* as one
  already raised?" — e.g. two evaluation runs both detect the same qSOFA breach in the same
  window. This is a clinical dedup decision and lives in the alert-definition, not the
  transport.
- **`Idempotency-Key` (transport, API-owned):** answers "did the client's HTTP request get
  processed already?" — the same acknowledge click retried after a timed-out response, a mobile
  client's automatic retry on a flaky ward Wi-Fi connection. The server caches
  `(endpoint, Idempotency-Key) → response` for **24 hours** and replays the cached response
  byte-for-byte on a repeat, **without re-executing the state transition** — so a retried
  `POST /alerts/{id}/resolve` never double-writes `resolved_at` or double-counts a PPV outcome.
- **Conflict rule:** if the same `Idempotency-Key` arrives with a **different** request body
  than the first use, the server returns `409 CONFLICT` with `code: IDEMPOTENCY_KEY_REUSE` —
  reusing a key for a different logical request is a client bug, surfaced loudly rather than
  silently executing the second body.
- **Required** on `POST /alerts` (the engine-role alert-raise endpoint — replay safety here is
  load-bearing for INV-2/§4.1 of `alert-engine.md`); **recommended** on every other mutating
  call; **not applicable** to `GET`/`DELETE` (delete is naturally idempotent; a repeat delete on
  an already-deleted resource returns `404`, not `409`).

**Worked example.** A clinician taps "Acknowledge" on a critical alert; the ward Wi-Fi drops the
response but the request landed. The mobile client retries the same `POST
/alerts/88231/acknowledge` with the same `Idempotency-Key: 6f2c...`. The server recognizes the
key, does **not** re-run the `raised → acknowledged` transition (which would otherwise fail with
`409 STATUS_CONFLICT` since the alert is now already `acknowledged`), and instead replays the
original `200` response. The clinician's UI shows success on the retry instead of a confusing
conflict error for an action that, from their perspective, already worked.

---

## 6. Rate limits

Two independent limiters, both surfaced via standard headers
(`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) and a `429` +
`Retry-After` on exhaustion:

1. **Per-user, per-endpoint-class limiter** — protects the API from a runaway client (a buggy
   polling loop, a misconfigured integration): e.g. 300 req/min for read endpoints, 60 req/min
   for mutating endpoints, per authenticated `user_id`.
2. **Per-tenant global limiter** — protects one hospital's traffic spike (a mass-casualty event
   generating a burst of vitals/alerts) from starving another tenant on shared infrastructure —
   multi-tenant fairness, sized generously above normal peak (per-tenant limits are an order of
   magnitude above the busiest observed unit).

**Patient-safety carve-outs — never rate-limited:**
- `POST /alerts` for `severity: critical` (mirrors the alert-engine's own suppression carve-out:
  "critical is NEVER rate-limited/suppressed", `severity-model.yaml` line 60, `CON-SEED-11`).
- `POST /alerts/{id}/acknowledge`, `/act`, `/resolve`, `/escalate` on any alert currently
  `critical` — a clinician's action on a life-threatening alert must never be throttled.
- `GET /health` — the external dead-man's-switch watchdog (INV-5) is unauthenticated and
  unthrottled by design; it is the one endpoint that must never itself become the reason the
  platform "looks down."
- The realtime channel's heartbeat frames (`asyncapi.yaml`) — throttling a heartbeat would
  manufacture the exact silent-staleness failure the channel exists to prevent.

Everything else, including `watch`/`normal`-severity alert actions and all read traffic, is
rate-limited normally; a burst there degrades gracefully (`429` + client backoff) rather than
risking an unbounded query against the operational store.

---

## 7. Error envelope

One shape, everywhere, on every non-2xx response (`#/components/schemas/ErrorEnvelope` in
`openapi.yaml`):

```json
{
  "error": {
    "code": "STATUS_CONFLICT",
    "message": "Alert 88231 is in status 'resolved'; acknowledge is only valid from 'raised' or 'escalated'.",
    "details": [
      {"field": "status", "issue": "current=resolved, required one of [raised, escalated]"}
    ],
    "trace_id": "4f2b6e6c9d3a4e1caa7e2f7b6c9d0a11",
    "timestamp": "2026-07-04T13:05:22Z",
    "documentation_url": "https://docs.intensicare.internal/api/errors#status_conflict"
  }
}
```

- **`code`** is the stable, machine-branchable identifier — clients should switch on `code`,
  never on `message` (message text may be localized/reworded without a version bump; `code`
  changing is a breaking change per §2.1).
- **`trace_id`** correlates to the OpenTelemetry trace emitted to the AMP/Grafana stack
  (`CON-0006`) — every support ticket should carry this value so on-call can jump straight to
  the trace instead of grepping logs by timestamp.
- **`details`** is present only for multi-field validation failures; omitted otherwise (not an
  empty array — absence, not emptiness, signals "nothing more to say").

### 7.1 Code registry (frozen mapping to HTTP status)

| HTTP | `code` | Meaning | Example endpoint |
|---|---|---|---|
| 400 | `BAD_REQUEST` | Malformed request (unparseable JSON, wrong content-type) | any |
| 401 | `UNAUTHORIZED` | Missing/expired/invalid JWT | any |
| 403 | `FORBIDDEN` | Authenticated but wrong role/tenant scope | `POST /thresholds`, cross-tenant read |
| 403 | `FORBIDDEN_TENANT_OVERRIDE` | Non-`platform-admin` supplied `tenant_id` query param | any list endpoint |
| 404 | `NOT_FOUND` | Resource absent or outside caller's tenant scope (never distinguished from "absent" — see §3 note below) | `GET /patients/{mpiId}` |
| 409 | `STATUS_CONFLICT` | Alert lifecycle transition invalid from current status | `POST /alerts/{id}/acknowledge` |
| 409 | `IDEMPOTENCY_KEY_REUSE` | Same `Idempotency-Key`, different request body | any mutating endpoint |
| 409 | `SCOPE_ALREADY_EXISTS` | `threshold_config` row already exists at this exact scope | `POST /thresholds` |
| 409 | `TENANT_DEFAULT_UNDELETABLE` | Attempted delete of a tenant-default threshold row | `DELETE /thresholds/{id}` |
| 422 | `VALIDATION_ERROR` | Schema-valid but business-rule-invalid (e.g. `watch_threshold >= urgent_threshold`) | `POST /thresholds` |
| 422 | `UNIT_MISMATCH` | A supplied unit is not the parameter's canonical unit or a declared alias (`units-registry.md` §1.4) | `POST /alerts` |
| 429 | `RATE_LIMITED` | Limiter exhausted (see §6 for carve-outs) | any (except carve-outs) |
| 503 | `UPSTREAM_DEGRADED` | A required upstream (Athena, HAPI FHIR, Redis) is down — mirrors `HealthStatus.status=down` | any endpoint depending on that upstream |
| 500 | `INTERNAL` | Unhandled server error | any |

**Deliberate non-leak note (`404` vs `403`):** a request for a patient/alert/threshold outside
the caller's tenant returns `404`, never `403` — `403` would confirm the resource *exists*
somewhere, leaking cross-tenant existence information. The one exception is
`FORBIDDEN_TENANT_OVERRIDE`, which is about the *query parameter itself* being disallowed, not
about a specific resource's existence.

---

## 8. Realtime reconnect / backoff (summary — normative text lives in `asyncapi.yaml` `x-reconnect-backoff-policy`)

A client's realtime lifecycle has four states: **connecting → subscribed → degraded (missed
heartbeat) → reconnecting**, with an explicit **stale-data UI state** entered whenever the
client cannot prove its view is current.

### 8.1 State diagram

```
        connect                  subscribe_ack received
  ┌────────────┐  ──────────▶  ┌────────────┐
  │  DISCONNECTED  │            │  SUBSCRIBED   │◀────────────────┐
  └────────────┘  ◀──────────  └────────────┘                  │
        ▲              max retries /            │ heartbeat_ping        │ resume ok
        │              RESUME_WINDOW_EXPIRED     │ every 25s              │ (subscribe_ack,
        │              (surface stale banner)    ▼                        │  seq > last seq)
        │                                  ┌────────────┐                 │
        └───────────────────────────────── │  DEGRADED  │ ────────────────┘
           reconnect w/ backoff            │ (missed pong│
           + resume_from_seq / Last-Event-ID│  or ping)  │
                                            └────────────┘
```

### 8.2 Backoff schedule
Exponential with full jitter: `delay = random(0, min(30_000ms, 1_000ms * 2^attempt))`. The
attempt counter resets after 60 continuous seconds `SUBSCRIBED`. This is the standard AWS-style
jittered backoff, chosen specifically to avoid a thundering-herd reconnect storm across an
entire unit's bed-board displays after a shared network blip — every ADR-001 v2 client shares
the same VPC path to the ECS service (`ADR001-C-08`), so a synchronized reconnect burst is a
real, not theoretical, risk.

### 8.3 Resume and the stale-data banner
On reconnect, the client resubscribes with the last processed `seq`
(`resume_from_seq` on WS, `Last-Event-ID` on SSE). The server holds a 5-minute rolling replay
buffer per tenant. If the gap is inside the buffer, missed events replay before live resumes —
invisible to the user. If the gap exceeds 5 minutes (extended outage, laptop sleep), the server
returns `RESUME_WINDOW_EXPIRED`; the client **must**:
1. Show a visible "reconnecting — data may be stale" banner (never silently keep displaying
   the last-known state as if current — this is the realtime-channel analogue of the
   alert-engine's staleness watchdog, `alert-engine.md` §7.2).
2. Perform one REST reconciliation pass (`GET /dashboard/bed-grid`, `GET /alerts`) to
   re-baseline.
3. Resubscribe fresh (no `resume_from_seq`) and clear the banner once `subscribe_ack` arrives.

### 8.4 WebSocket auth ticket
Because some client runtimes (browser `WebSocket`, embedded webviews) cannot set an
`Authorization` header on the upgrade request, the WS channel accepts a short-lived
(≤60s), single-use upgrade ticket via `?access_token=`. This is **not** the long-lived JWT
access token — clients call a ticket-minting REST call before each fresh WebSocket connect
(not on reconnects that carry `resume_from_seq`, which reuse the still-valid prior session
where possible). Never log or cache this query-param value beyond the connection attempt.

---

## 9. Auth today, SSO tomorrow — ADR-001 §7 migration

**Today:** `POST /auth/login` issues an IntensiCare-signed JWT
(`iss: intensicare-auth`, 15-minute access token, 7-day rotating refresh token), claims
`{sub, tenant_id, roles[], iat, exp, iss, aud}`. This is what every `bearerAuth` security
requirement in `openapi.yaml` checks today.

**Tomorrow (mandatory, `ADR001-C-07`/`CON-0007`):** IntensiCare inherits the AMH Data
Platform's security model — **AWS IAM Identity Center for SSO**, per-tenant KMS for
encryption, Lake Formation ABAC for data access. IntensiCare does not reimplement any of these;
it consumes them. For the API surface specifically, this means an OIDC authorization-code flow
replaces password-grant login.

**Why the migration is additive, not a breaking change (§2.1) for resource servers:**

| Aspect | Today | After SSO migration | Changed? |
|---|---|---|---|
| Transport | `Authorization: Bearer <jwt>` | `Authorization: Bearer <jwt>` | No |
| Claim names checked by every endpoint (`tenant_id`, `roles[]`) | present | present (mapped from IAM Identity Center group/attribute assignment) | No |
| `iss` claim value | `intensicare-auth` | IAM Identity Center issuer URL | **Yes**, but resource servers validate `iss ∈ {accepted issuers}`, not a single hardcoded string, from day one — this is the one piece of forward design cost paid now to make the cutover additive later |
| Token acquisition | `POST /auth/login` (password grant) | `GET /auth/sso/authorize` → redirect → `GET /auth/sso/callback` (OIDC authorization code) | **Yes** — but `/auth/login` is deprecated per §2.2, not deleted, during the migration window |
| New claims available | — | `idc_user_id`, `idc_group_ids` (for ABAC cross-reference with Lake Formation, `ADR001-C-07`) | Additive |
| `UserProfile.auth_source` | `password` | `sso` | Additive field, already modeled in `openapi.yaml` today so clients don't need a schema change to distinguish the two mid-migration |

**Cutover plan (both issuers accepted concurrently during the window):** once
`/auth/sso/authorize`/`/auth/sso/callback` are implemented, the resource-server JWT validator
accepts tokens from **either** issuer for the full 180-day deprecation window (§2.2, critical-path
minimum), long enough for every internal client (bed-board web app, RRT mobile app, any
service-account integration) to migrate its login flow. `role: engine` service-account tokens
(used by the alert engine to call `POST /alerts`) migrate on the same clock but are lower risk —
they are provisioned by platform engineering, not by individual clinicians re-logging-in.

**Ownership.** `amh-integration-architect` owns the IAM Identity Center integration itself
(standing constraint, `CON-0007`); `api-designer` (this document) owns keeping the API contract
stable across that integration landing.

---

## 10. Traceability

| Design decision | Source |
|---|---|
| URL versioning `/api/v1` | mission directive |
| Severity `normal\|watch\|urgent\|critical` everywhere | `CON-SEED-11`, `severity-model.yaml`, `alert-engine.md` §3 |
| Alert triggering-parameter + evidence + rule-id + staleness shape | `CON-0090`/`PER-C-04`, `CONTRACTS.md` Alert entry schema, `units-registry.md` |
| Alert lifecycle raise/ack/act/resolve(/escalate) | `alert-engine.md` §9, `DM-VOCAB-04/05` |
| Thresholds tenant→unit→bed, most-specific-wins | `alert-engine.md` §6, `DM-T-05`, `DM-C-11`/`CON-0029` |
| JWT now, IAM Identity Center SSO later | `ADR-001` §Implicação 7, `ADR001-C-07`/`CON-0007` |
| Single realtime channel, REST is not a bed-board polling path | `CON-0046`/`CON-0053`/`DES-C-05`, `alert-engine.md` §7.1 |
| Realtime payloads never a second source of truth | `CON-0045`/`ADR-C-12` |
| Critical severity never rate-limited/suppressed | `severity-model.yaml` (`rate_limited: false`), `CON-SEED-11` |
| Cursor pagination over hypertables | `DM-C-03/04/05` (TimescaleDB hypertables) |
| Idempotency-Key layered over engine `dedup_key` | `alert-engine.md` §4.2, `CON-0067`/`IMP-C-02` |
| `/health` unauthenticated, unthrottled | `IMP-C-05`/`CON-0070`, `alert-engine.md` §7.2 (INV-5) |
| Every write audited (INV-1) | `CON-0066`/`IMP-C-01` |
| No manual vitals-entry endpoint | `PER-ANA-01` structural criterion (`product-spec.md` line 438) |

**Open reconciliations this spec surfaces but does not resolve (per zero-silent-resolution,
`CON-0011`/`CON-0012`):**
- `AlertStatus` includes `acting`/`escalated`, extending the current `alert.status` DB enum
  (`active/acknowledged/resolved/expired`, `DM-VOCAB-04`) — flagged in `alert-engine.md` §9 for
  data-architect reconciliation at barrier C2.
- `Severity` includes `normal`, which has no corresponding row in the current `alert.severity`
  DB enum (`watch/urgent/critical` only, `DM-VOCAB-03`) — `severity-model.yaml` recommends
  adding a delivery-only `info`/`normal` value; this API is written against the target
  four-band scale and depends on that reconciliation landing by barrier C2.
- `ThresholdConfig.bed_id` extends `DM-T-05`, which today has no `bed_id` column — flagged in
  `alert-engine.md` §6 for the same barrier.
