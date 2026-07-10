// =============================================================================
// IntensiCare Frontend v3 — WebSocket + Polling Fallback (ADR-0034)
// =============================================================================
// Single WebSocket connection with channel multiplexing.
// Automatic fallback to polling when WS fails (CSP, firewall, timeout).
// JWT handshake: challenge → token → subscribe.
//
// Usage:
//   useRealtimeChannel('bed_grid.updated', () => mutateDashboard());
//   useRealtimeChannel('vitals.updated', (p) => { if (p.mpi_id === id) mutate(); });
//   const { status } = useConnectionStatus(); // WiFi/WifiOff indicator
// =============================================================================

'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { getToken } from './api';

// ── Types ──

export type RealtimeChannel =
  | 'bed_grid.updated'
  | 'alert.raised'
  | 'alert.updated'
  | 'vitals.updated'
  | 'pathway.updated'
  | 'pathway.state_changed';

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'fallback';

interface WSMessage {
  type: 'auth_required' | 'auth' | 'subscribed' | 'event' | 'error' | 'ping' | 'pong';
  channel?: RealtimeChannel;
  challenge?: string;
  token?: string;
  payload?: Record<string, unknown>;
}

interface ChannelSubscription {
  channel: RealtimeChannel;
  onMessage: (payload: unknown) => void;
  filter?: (payload: unknown) => boolean;
  fallbackInterval: number;
  pollTimer: ReturnType<typeof setInterval> | null;
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

const WS_URL = typeof window !== 'undefined'
  ? (process.env.NEXT_PUBLIC_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`)
  : '';

const WS_TIMEOUT = 5000;

// ── Heartbeat
let pingTimer: ReturnType<typeof setInterval> | null = null;
let pongTimeout: ReturnType<typeof setTimeout> | null = null;
const PING_INTERVAL = 30_000;
const PONG_TIMEOUT = 5_000;

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

// ── Heartbeat engine

function startHeartbeat(): void {
  if (pingTimer) return;
  pingTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
      pongTimeout = setTimeout(() => {
        // No pong received — connection is dead
        if (ws) {
          ws.close();
          ws = null;
        }
      }, PONG_TIMEOUT);
    }
  }, PING_INTERVAL);
}

function stopHeartbeat(): void {
  if (pingTimer) { clearInterval(pingTimer); pingTimer = null; }
  if (pongTimeout) { clearTimeout(pongTimeout); pongTimeout = null; }
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
        stopHeartbeat();
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

// ── WebSocket engine (singleton) ──

function connectWS(): void {
  if (typeof window === 'undefined') return;
  setupVisibilityListeners();
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

  // Don't attempt reconnect if no valid token
  const token = getToken();
  if (!token) {
    setStatus('disconnected');
    return;
  }

  setStatus('connecting');

  try {
    ws = new WebSocket(WS_URL);
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

  ws.onopen = () => clearTimeout(timeoutId);

  ws.onmessage = (event: MessageEvent) => {
    try {
      const msg: WSMessage = JSON.parse(event.data);

      if (msg.type === 'auth_required') {
        const token = getToken();
        if (!token) {
          ws?.close();
          ws = null;
          setStatus('disconnected');
          return;
        }
        ws?.send(JSON.stringify({ type: 'auth', token, challenge: msg.challenge || '' }));
        return;
      }

      if (msg.type === 'subscribed') {
        clearTimeout(timeoutId);
        reconnectAttempt = 0;
        setStatus('connected');
        stopAllPolling();
        startHeartbeat();
        return;
      }

      if (msg.type === 'pong') {
        if (pongTimeout) { clearTimeout(pongTimeout); pongTimeout = null; }
        return;
      }

      if (msg.type === 'event' && msg.channel && msg.payload !== undefined) {
        const subs = subscriptions.get(msg.channel);
        if (subs) {
          subs.forEach((sub) => {
            if (!sub.filter || sub.filter(msg.payload)) sub.onMessage(msg.payload);
          });
        }
        lastEvent = new Date();
        lastEventListeners.forEach((fn) => fn(lastEvent));
      }
    } catch {
      if (process.env.NODE_ENV === 'development') {
        console.warn('[WS] Malformed message:', typeof event.data === 'string' ? event.data.slice(0, 100) : '(non-string data)');
      }
    }
  };

  ws.onclose = () => {
    ws = null;
    stopHeartbeat();
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
  stopHeartbeat();
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

  return () => {
    const current = subscriptions.get(sub.channel) || [];
    subscriptions.set(sub.channel, current.filter((s) => s !== sub));
    stopPolling(sub);
    if (subscriptions.get(sub.channel)?.length === 0) subscriptions.delete(sub.channel);
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
  const [status, setStatusState] = useState<ConnectionStatus>(_connectionStatus);
  const [lastEventState, setLastEventState] = useState<Date | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    const handler = (s: ConnectionStatus) => setStatusState(s);
    statusListeners.add(handler);
    return () => { statusListeners.delete(handler); };
  }, []);

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
  const [status, setStatusState] = useState<ConnectionStatus>(_connectionStatus);

  useEffect(() => {
    const handler = (s: ConnectionStatus) => setStatusState(s);
    statusListeners.add(handler);
    setStatusState(_connectionStatus);
    return () => { statusListeners.delete(handler); };
  }, []);

  const reconnect = useCallback(() => {
    intentionallyDisconnected = false;
    reconnectAttempt = 0;
    disconnectWS();
    connectWS();
  }, []);

  return { status, since: statusSince, reconnect };
}
