// =============================================================================
// IntensiCare Frontend v3 — WebSocket + Polling Fallback (ADR-0034)
// =============================================================================
// Single WebSocket connection with channel multiplexing.
// Automatic fallback to polling when WS fails (CSP, firewall, timeout).
//
// Real backend protocol (see src/intensicare/api/v1/ws.py — that file is the
// spec, not this comment):
//   Endpoint:  ws(s)://<backend-host>/api/v1/ws?token=<JWT>
//              A missing/invalid token closes the socket with code 1008.
//   Client -> Server (JSON), every message re-includes the JWT (per-message
//   auth, M7/F-09 — tokens are re-validated on every frame, not just at
//   connect time):
//     {"action":"subscribe",   "channel":"<event_type>", "token":"<JWT>"}
//     {"action":"unsubscribe", "channel":"<event_type>", "token":"<JWT>"}
//     {"action":"pong",        "token":"<JWT>"}
//   Server -> Client (JSON):
//     {"type":"ping"}                                          (every 30s)
//     {"type":"<channel>","data":...,"payload":...,"timestamp":...}
//     {"type":"error","message":"..."}
//   There is no handshake/challenge and no "subscribed" ack — the server
//   just starts forwarding events for channels the client has subscribed to.
//
// Usage:
//   useRealtimeChannel('bed_grid.updated', () => mutateDashboard());
//   useRealtimeChannel('vitals.updated', (p) => { if (p.mpi_id === id) mutate(); });
//   const { status } = useConnectionStatus(); // WiFi/WifiOff indicator
// =============================================================================

'use client';

import { useEffect, useRef, useCallback, useState, useSyncExternalStore } from 'react';
import { getToken, onTokenAvailable } from './api';

// ── Types ──

export type RealtimeChannel =
  | 'bed_grid.updated'
  | 'alert.raised'
  | 'alert.updated'
  | 'vitals.updated'
  | 'pathway.updated'
  | 'pathway.state_changed';

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'fallback';

// Server -> client envelope. `type` is either a channel name (event), the
// literal 'ping' (heartbeat), or 'error'. Events carry both `data` and
// `payload` (same value, `data` kept for backward-compat consumers) plus a
// `timestamp`. Errors carry `message` instead.
interface WSMessage {
  type: string;
  data?: unknown;
  payload?: unknown;
  timestamp?: string;
  message?: string;
}

interface ChannelSubscription {
  channel: RealtimeChannel;
  onMessage: (payload: unknown) => void;
  filter?: (payload: unknown) => boolean;
  fallbackInterval: number;
  pollTimer: ReturnType<typeof setInterval> | null;
}

// ── Channel aliasing ──
// The backend does NOT publish a `pathway.state_changed` channel — pathway
// transitions are published by PathwayEnrollmentService (Sprint 1) as
// `pathway.updated` only (see services/pathway_enrollment.py
// _publish_pathway_updated). Pages in this app still subscribe to
// `pathway.state_changed` and cannot be edited here, so we alias it
// transparently: we subscribe to the real backend channel on the wire, and
// route incoming `pathway.updated` events back out to any local
// `pathway.state_changed` subscribers too. The payload shape published by
// the enrollment service (mpi_id, patient_pathway_id, pathway_id,
// pathway_slug, from_state, to_state, status, severity) is a superset of
// what a `state_changed` consumer would expect, so this is payload-compatible.
function toBackendChannel(channel: RealtimeChannel): string {
  return channel === 'pathway.state_changed' ? 'pathway.updated' : channel;
}

function localChannelsForBackendChannel(backendChannel: string): RealtimeChannel[] {
  const result: RealtimeChannel[] = [];
  subscriptions.forEach((_subs, ch) => {
    if (toBackendChannel(ch) === backendChannel) result.push(ch);
  });
  return result;
}

// ── Global state (module-level singleton, client-only) ──

let ws: WebSocket | null = null;
let _connectionStatus: ConnectionStatus = 'disconnected';
let statusSince: Date | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
const statusListeners = new Set<(status: ConnectionStatus) => void>();
const subscriptions = new Map<RealtimeChannel, ChannelSubscription[]>();

let lastEvent: Date | null = null;
const lastEventListeners = new Set<(date: Date | null) => void>();

// Resolve the WebSocket base URL. lib/api.ts talks to the backend through a
// relative '/api/v1' path proxied by next.config.ts's rewrites() — but
// Next.js rewrites cannot reliably proxy a WebSocket upgrade, so the client
// must connect to the backend directly. We read the same *kind* of explicit,
// env-driven config lib/api.ts's proxy relies on (NEXT_PUBLIC_WS_URL, see
// frontend-v3/.env.local — defaults to the dev backend at :8000) rather than
// trusting window.location.host blindly. Only when that env var is absent do
// we fall back to same-origin, and even then with the real backend path.
function resolveWsBaseUrl(): string {
  if (typeof window === 'undefined') return '';
  const configured = process.env.NEXT_PUBLIC_WS_URL;
  if (configured) return configured;
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/api/v1/ws`;
}

const WS_TIMEOUT = 5000;

// ── Heartbeat watchdog ──
// The SERVER pings every 30s and disconnects a client that hasn't answered
// within HEARTBEAT_INTERVAL + PONG_TIMEOUT (40s, see ws.py). The client's
// job is just to answer each ping with a pong (see onmessage below); this
// watchdog is the client-side mirror — if no server ping (or any message)
// arrives for a while, treat the connection as dead and let the existing
// reconnect/fallback machinery in ws.onclose take over.
let watchdogTimer: ReturnType<typeof setTimeout> | null = null;
const WATCHDOG_TIMEOUT = 45_000; // server heartbeat window (40s) + latency buffer

function resetWatchdog(): void {
  if (watchdogTimer) clearTimeout(watchdogTimer);
  watchdogTimer = setTimeout(() => {
    if (ws) { ws.close(); ws = null; }
  }, WATCHDOG_TIMEOUT);
}

function stopWatchdog(): void {
  if (watchdogTimer) { clearTimeout(watchdogTimer); watchdogTimer = null; }
}

// ── Reconnect backoff
let reconnectAttempt = 0;

function getReconnectDelay(): number {
  const n = reconnectAttempt;
  reconnectAttempt++;
  return Math.min(1000 * Math.pow(2, n) + Math.random() * 1000, 30_000);
}

// ── Visibility / online
let visibilityListenerSetup = false;
let intentionallyDisconnected = false;

function setStatus(status: ConnectionStatus) {
  if (_connectionStatus !== status) {
    _connectionStatus = status;
    statusSince = new Date();
    statusListeners.forEach((fn) => fn(status));
  }
}

// External-store bindings for React's useSyncExternalStore (avoids the
// render/commit race a plain useState+useEffect subscription can miss).
function subscribeStatus(callback: () => void): () => void {
  const handler = () => callback();
  statusListeners.add(handler);
  return () => { statusListeners.delete(handler); };
}

function getStatusSnapshot(): ConnectionStatus {
  return _connectionStatus;
}

// ── Polling engine (per-channel) ──

function startPolling(sub: ChannelSubscription) {
  if (sub.pollTimer) return;
  sub.pollTimer = setInterval(() => {
    // Pass null so consumers' `!p` guards trigger mutation for scoped channels.
    // Example: `if (!p || p.mpi_id === mpiId) mutate()` — null passes the guard.
    sub.onMessage(null);
  }, sub.fallbackInterval);
}

function stopPolling(sub: ChannelSubscription) {
  if (sub.pollTimer) {
    clearInterval(sub.pollTimer);
    sub.pollTimer = null;
  }
}

function startAllPolling() {
  subscriptions.forEach((subs) => subs.forEach(startPolling));
}

function stopAllPolling() {
  subscriptions.forEach((subs) => subs.forEach(stopPolling));
}

// ── Visibility / online listeners

function setupVisibilityListeners(): void {
  if (visibilityListenerSetup) return;
  if (typeof window === 'undefined') return;
  visibilityListenerSetup = true;

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      if (_connectionStatus === 'connected' && (!ws || ws.readyState !== WebSocket.OPEN)) {
        // Tab became visible but WS is dead — reconnect
        reconnectAttempt = 0;
        stopWatchdog();
        if (ws) { ws.close(); ws = null; }
        connectWS();
      }
    }
  });

  window.addEventListener('online', () => {
    if (_connectionStatus === 'disconnected' && !intentionallyDisconnected) {
      reconnectAttempt = 0;
      connectWS();
    }
  });
}

// ── Token-available listener (BUG-F7-05) ──
// connectWS() checks getToken() exactly once per attempt and gives up with
// 'disconnected' if it's null. On a fresh reload/deep-link, the page's
// useRealtimeChannel mount (and thus the first connectWS() call) typically
// fires before lib/api.ts's async session bootstrap (ensureSession(), which
// recovers the in-memory token from the HttpOnly refresh_token cookie) has
// resolved — so that first attempt always sees no token and, without this,
// nothing ever retries. Register once for the module's lifetime: when a
// token later shows up (bootstrap resolves, or an explicit login()), retry
// iff something is still actively waiting to connect. Mirrors the 'online'
// listener's guards above: skip if there's no pending subscription (e.g. on
// /login, which never mounts a useRealtimeChannel — see components/app-shell.tsx)
// and skip if the disconnect was intentional (logout), to avoid ever looping
// on the login screen or after a deliberate sign-out.
let tokenListenerSetup = false;

function setupTokenListener(): void {
  if (tokenListenerSetup) return;
  tokenListenerSetup = true;

  onTokenAvailable(() => {
    if (_connectionStatus === 'disconnected' && !intentionallyDisconnected && subscriptions.size > 0) {
      reconnectAttempt = 0;
      connectWS();
    }
  });
}

// ── Channel (un)subscribe wire messages ──
// Every client message must re-include a valid token (per-message auth).

function sendChannelAction(action: 'subscribe' | 'unsubscribe', backendChannel: string): void {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  const token = getToken();
  if (!token) return;
  ws.send(JSON.stringify({ action, channel: backendChannel, token }));
}

// ── WebSocket engine (singleton) ──

function connectWS(): void {
  if (typeof window === 'undefined') return;
  setupVisibilityListeners();
  setupTokenListener();
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

  // Don't attempt reconnect if no valid token (yet — see setupTokenListener
  // above, which retries this call once the session bootstrap resolves one)
  const token = getToken();
  if (!token) {
    setStatus('disconnected');
    return;
  }

  const base = resolveWsBaseUrl();
  if (!base) {
    setStatus('disconnected');
    return;
  }

  setStatus('connecting');

  const sep = base.includes('?') ? '&' : '?';
  const url = `${base}${sep}token=${encodeURIComponent(token)}`;

  try {
    ws = new WebSocket(url);
  } catch {
    setStatus('fallback');
    startAllPolling();
    return;
  }

  const timeoutId = setTimeout(() => {
    if (ws && ws.readyState !== WebSocket.OPEN) {
      ws.close();
      ws = null;
    }
    setStatus('fallback');
    startAllPolling();
  }, WS_TIMEOUT);

  ws.onopen = () => {
    clearTimeout(timeoutId);
    reconnectAttempt = 0;

    // No handshake/ack in the real protocol — subscribe immediately for
    // every channel a consumer has already registered, then declare the
    // connection live.
    const backendChannels = new Set<string>();
    subscriptions.forEach((_subs, ch) => backendChannels.add(toBackendChannel(ch)));
    backendChannels.forEach((bc) => sendChannelAction('subscribe', bc));

    setStatus('connected');
    stopAllPolling();
    resetWatchdog();
  };

  ws.onmessage = (event: MessageEvent) => {
    try {
      const msg: WSMessage = JSON.parse(event.data);
      resetWatchdog();

      if (msg.type === 'ping') {
        // Server heartbeat — answer with a pong (re-including the token,
        // per-message auth) so the server doesn't drop us as stale.
        const token = getToken();
        if (token && ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ action: 'pong', token }));
        }
        return;
      }

      if (msg.type === 'error') {
        if (process.env.NODE_ENV === 'development') {
          console.warn('[WS] Server error:', msg.message);
        }
        return;
      }

      // Otherwise `type` is the channel name the event was published on.
      const localChannels = localChannelsForBackendChannel(msg.type);
      if (localChannels.length === 0) return;

      const eventPayload = msg.payload !== undefined ? msg.payload : msg.data;
      localChannels.forEach((ch) => {
        const subs = subscriptions.get(ch);
        subs?.forEach((sub) => {
          if (!sub.filter || sub.filter(eventPayload)) sub.onMessage(eventPayload);
        });
      });
      lastEvent = new Date();
      lastEventListeners.forEach((fn) => fn(lastEvent));
    } catch {
      if (process.env.NODE_ENV === 'development') {
        console.warn('[WS] Malformed message:', typeof event.data === 'string' ? event.data.slice(0, 100) : '(non-string data)');
      }
    }
  };

  ws.onclose = () => {
    // BUG-F7-02 fix: cancel *this attempt's* WS_TIMEOUT watchdog. Without
    // this, a fast-failing attempt (closes/errors well before its own 5s
    // WS_TIMEOUT elapses — the common case) leaves that timer armed and
    // uncancelled. If a subsequent reconnect then succeeds within that
    // stale timer's remaining window (typical: reconnect delay + connect
    // time « 5s), the orphaned timeout callback still fires later, reads
    // the *global* `ws` (by then reassigned to the new, live, open socket),
    // and — because it unconditionally calls setStatus('fallback') once its
    // "not yet open" branch is skipped — forces the UI into "polling" even
    // though the current socket is open and actively exchanging real
    // ping/pong. This is exactly the measured symptom: status stuck on
    // fallback while a live connection keeps working underneath it.
    clearTimeout(timeoutId);
    ws = null;
    stopWatchdog();
    if (_connectionStatus === 'connected' || _connectionStatus === 'connecting') {
      setStatus('fallback');
      startAllPolling();
      const delay = getReconnectDelay();
      reconnectTimer = setTimeout(() => connectWS(), delay);
    } else if (_connectionStatus !== 'fallback') {
      setStatus('disconnected');
    }
  };

  ws.onerror = () => {
    if (process.env.NODE_ENV === 'development') {
      console.warn('[WS] Connection error');
    }
  };
}

function disconnectWS(): void {
  stopWatchdog();
  reconnectAttempt = 0;
  intentionallyDisconnected = true;
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
  if (ws) { ws.close(); ws = null; }
  stopAllPolling();
  setStatus('disconnected');
}

function subscribe(sub: ChannelSubscription): () => void {
  const existing = subscriptions.get(sub.channel) || [];
  subscriptions.set(sub.channel, [...existing, sub]);

  if (_connectionStatus === 'disconnected') connectWS();
  if (_connectionStatus === 'fallback') startPolling(sub);
  if (_connectionStatus === 'connected') sendChannelAction('subscribe', toBackendChannel(sub.channel));

  return () => {
    const current = subscriptions.get(sub.channel) || [];
    subscriptions.set(sub.channel, current.filter((s) => s !== sub));
    stopPolling(sub);
    if (subscriptions.get(sub.channel)?.length === 0) subscriptions.delete(sub.channel);

    // Only unsubscribe on the wire once no local channel (including aliases)
    // still needs this backend channel.
    const backendChannel = toBackendChannel(sub.channel);
    const stillNeeded = Array.from(subscriptions.keys()).some(
      (ch) => toBackendChannel(ch) === backendChannel,
    );
    if (!stillNeeded) sendChannelAction('unsubscribe', backendChannel);

    if (subscriptions.size === 0) disconnectWS();
  };
}

// ── Public hooks ──

export function useRealtimeChannel(
  channel: RealtimeChannel,
  onMessage: (payload: unknown) => void,
  options?: {
    fallbackInterval?: number;
    filter?: (payload: unknown) => boolean;
    enabled?: boolean;
  },
): { status: ConnectionStatus; lastEvent: Date | null } {
  const status = useSyncExternalStore(subscribeStatus, getStatusSnapshot, getStatusSnapshot);
  const [lastEventState, setLastEventState] = useState<Date | null>(null);
  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  });

  useEffect(() => {
    const handler = (d: Date | null) => setLastEventState(d);
    lastEventListeners.add(handler);
    return () => { lastEventListeners.delete(handler); };
  }, []);

  useEffect(() => {
    if (options?.enabled === false) return;

    const sub: ChannelSubscription = {
      channel,
      onMessage: (payload) => onMessageRef.current(payload),
      filter: options?.filter,
      fallbackInterval: options?.fallbackInterval ?? 30_000,
      pollTimer: null,
    };

    const unsubscribe = subscribe(sub);
    return unsubscribe;
  }, [channel, options?.fallbackInterval, options?.enabled]);

  return { status, lastEvent: lastEventState };
}

export function useConnectionStatus(): {
  status: ConnectionStatus;
  since: Date | null;
  reconnect: () => void;
} {
  const status = useSyncExternalStore(subscribeStatus, getStatusSnapshot, getStatusSnapshot);

  const reconnect = useCallback(() => {
    intentionallyDisconnected = false;
    reconnectAttempt = 0;
    disconnectWS();
    connectWS();
  }, []);

  return { status, since: statusSince, reconnect };
}
