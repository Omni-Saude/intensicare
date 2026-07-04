# ADR-DRAFT: Realtime channel consolidation (client architecture)

Status: **draft, pending ratification**
Date: 2026-07-04
Author: frontend-architect (v2 design phase)
Supersedes-context: `docs/adr/0017-fragmented-real-time-architecture.md` (legacy audit ADR, status
"proposed" — this draft is the client-side implementation decision that ADR-0017 deferred pending
"team ratification" and "the specific transport... settled alongside the backend framework and
hosting decisions").

## Context and Problem Statement

`ADR-0017` documented that the legacy `trilhas-frontend` used three unrelated realtime mechanisms
(raw bidirectional WebSocket for notifications with two connections per user; Firestore `onSnapshot`
for chat presence; `setInterval` REST polling for the bed board — the single most safety-critical
view) with no shared reconnect/backoff, and recommended consolidating onto one push transport with a
shared client, topic multiplexing, and a strict system-of-record discipline. It left the concrete
transport choice open pending the backend framework/hosting decision.

The backend architecture is now settled (`docs/plan/architecture/system-architecture.md`): the API
container is FastAPI, "REST + WebSocket" (line 80/100), backed by Redis 7 for pub/sub (line 87). This
ADR makes the client-side consolidation decision building on that backend commitment, and states the
fallback posture the orchestrating brief requires ("WebSocket+SSE fallback per audit ADR-0017").

## Decision Drivers

- `ADR-C-12`/`CON-0045`: the realtime transport MUST NOT become a second source of truth.
- `ADR-C-13`/`CON-0046`: notification alerts and bed-board/dashboard state MUST be delivered via the
  same push channel/latency class.
- `DES-C-05`/`CON-0053`: the bed board MUST NOT rely on REST polling.
- Real-world ICU hospital networks include restrictive corporate proxies/firewalls that can block or
  degrade WebSocket upgrade handshakes — a condition the legacy never had to design for because the
  bed board never attempted push at all.
- `PER-C-01`/`PER-C-06`: score-availability and mobile-notification latency SLOs (<30s, <5s) depend
  on the realtime path not silently failing closed.

## Considered Options

1. **WebSocket-only**, no fallback. Simplest, matches the backend container exactly. Rejected as the
   sole mechanism: any client behind a proxy that blocks WS upgrade falls back to nothing, silently
   regressing to the legacy's "least live" bed board for exactly the population most likely to be on
   a locked-down hospital network.
2. **SSE-only.** Simpler reconnect semantics (native browser retry), one-way only. Rejected as the
   sole mechanism: the notification "mark as read" and any future client-initiated realtime signal
   need a return channel; SSE would require a second REST call for every ack, reintroducing a
   split-channel problem at a smaller scale.
3. **WebSocket primary, SSE fallback, one shared client module, automatic transport selection.**
   Chosen. The client attempts a WebSocket connection first; on repeated upgrade failure (proxy
   rejection, corporate network policy) or a configured feature flag, it falls back to an SSE
   `EventSource` subscription for inbound topics, with acks/mutations sent over a plain authenticated
   REST call in fallback mode (the transport-degradation path already implies mutations are rarer and
   REST latency is acceptable there). Both transports are hidden behind the same
   `subscribe(topic, handler)` / `publish(topic, payload)` interface so no consumer code branches on
   which transport is active.
4. **Managed pub/sub product** (e.g., Ably, Pusher, or a broader Firestore/Firebase usage) as the
   transport, per ADR-0017 Option 3. Left open as an acceptable substitute for the *transport*
   implementation detail if the team prefers not to operate a WebSocket/SSE gateway directly, provided
   the same client-side interface (`subscribe`/`publish`, shared reconnect/backoff, topic
   multiplexing across all three use cases) is preserved and the vendor's connection semantics can
   express an SSE-equivalent fallback. **Not decided here — a hosting/vendor cost decision.**

## Decision Outcome

Adopt **Option 3**: one `lib/realtime` client module, WebSocket primary transport (matching the
FastAPI `REST + WebSocket` backend container), automatic SSE fallback for networks that cannot
sustain a WebSocket upgrade, shared exponential-backoff-with-jitter reconnect logic used by both
transports, and topic-based multiplexing so a single connection (of either transport) serves
notifications, bed-board/vitals/occupancy updates, and chat/presence-refresh signals alike.

**System-of-record discipline (carried forward from ADR-0017, restated as binding):** every message
on the wire is either a "something changed, refetch" signal (triggers a TanStack Query
`invalidateQueries` call) or a thin, versioned, idempotent patch reconciled against the query cache —
never treated as the record of truth itself. REST/the database remains authoritative for all clinical
data, exactly as the legacy's Firestore boundary did for chat, generalized to every topic.

**Same-channel guarantee:** the bed-board grid and the notification bell subscribe to the same
`bed.<bedId>.alert` topic family, closing the specific life-safety gap ADR-0017 named (bell instant,
grid delayed).

**Connection-state visibility:** the client exposes a state machine (`connected | reconnecting |
degraded(fallback-active) | offline`) consumed by `ConnectionStatusIndicator` and `StalenessBanner`
(see `docs/plan/design/component-library.md` §5.7/§5.13) — new surface area; the legacy had none.

### Consequences

**Good:**
- Closes the bell/grid-disagreement life-safety defect structurally (one topic family, one channel
  class) rather than by convention.
- One reconnect/backoff implementation, covering both transports, replaces zero implementations
  today.
- Degraded-network clients (locked-down hospital Wi-Fi) still get near-real-time updates via SSE
  instead of falling all the way back to the legacy's REST-polling-or-nothing outcome.
- Gives the frontend one place to add connection-quality telemetry, informing future SLA/latency
  tuning.

**Bad:**
- Two transport code paths (even behind one interface) is more surface area to test than a single
  transport; CI must exercise both (§6 of the component-library doc, interaction/connection tests).
- SSE fallback mode's mutation-over-REST path has different latency characteristics than WebSocket's
  in-band ack — acceptable as a degraded-mode compromise, but must be monitored so "degraded" doesn't
  quietly become the steady state for a meaningful fraction of clients.
- A bug in the shared client now affects all three use cases simultaneously (the same blast-radius
  tradeoff ADR-0017 already accepted for Option 2).

## Open questions for ratification

1. Self-hosted WebSocket/SSE gateway vs. a managed pub/sub product (Option 4) — a hosting/cost
   decision for the team, not resolved here; the client interface is designed to be transport-
   agnostic either way.
2. Exact backoff curve parameters (base delay, max delay, jitter bounds) and the reconnect-attempt
   threshold that triggers the SSE fallback — an engineering tuning pass, not a product decision.
3. Whether chat/presence signaling stays conceptually separate from the clinical alert topics at the
   authorization layer (different sensitivity, potentially different retention) even though they
   share one transport — needs input from `auth-security-architect`.
