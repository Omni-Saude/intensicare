'use client';

import { getApiToken } from './api';

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────

/** All event types the server can emit over the realtime channel */
export type RealtimeEventType =
  | 'alert.raised'
  | 'alert.updated'
  | 'bed_grid.updated'
  | 'presence.updated'
  | 'vitals.updated';

/** Payload carried by a realtime event */
export interface RealtimeEvent<T = unknown> {
  type: RealtimeEventType;
  payload: T;
  timestamp: string;
}

/** Connection status for UI indicators */
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

/** Callback invoked when an event arrives on a subscribed channel */
export type ChannelCallback<T = unknown> = (event: RealtimeEvent<T>) => void;

// ─────────────────────────────────────────────────────────────
// WebSocket URL resolution
// ─────────────────────────────────────────────────────────────

function getWsBaseUrl(): string {
  if (typeof window === 'undefined') return 'ws://localhost:8000';

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  if (process.env.NEXT_PUBLIC_WS_URL) return process.env.NEXT_PUBLIC_WS_URL;

  // In development, use the configured backend (default localhost:8000)
  return `${protocol}//${window.location.hostname}:8000`;
}

const WS_ENDPOINT = '/api/v1/ws';
const SSE_ENDPOINT = '/api/v1/events/stream';

// ─────────────────────────────────────────────────────────────
// Singleton connection manager
// ─────────────────────────────────────────────────────────────

type ListenerEntry = {
  type: RealtimeEventType;
  callback: ChannelCallback;
};

class RealtimeConnection {
  private static instance: RealtimeConnection | null = null;

  private ws: WebSocket | null = null;
  private eventSource: EventSource | null = null;
  private listeners: ListenerEntry[] = [];
  private statusListeners: Array<(s: ConnectionStatus) => void> = [];
  private _status: ConnectionStatus = 'disconnected';
  private reconnectAttempt = 0;
  private maxReconnectDelay = 32000; // 32s max
  private baseDelay = 1000; // 1s start
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private intentionalClose = false;
  private useSseFallback = false;

  private constructor() {
    // Private — singleton
  }

  static getInstance(): RealtimeConnection {
    if (!RealtimeConnection.instance) {
      RealtimeConnection.instance = new RealtimeConnection();
    }
    return RealtimeConnection.instance;
  }

  // ── Public API ─────────────────────────────────────────────

  get status(): ConnectionStatus {
    return this._status;
  }

  /** Subscribe to connection status changes (for UI indicators) */
  onStatusChange(cb: (s: ConnectionStatus) => void): () => void {
    this.statusListeners.push(cb);
    // Immediately notify of current status
    cb(this._status);
    return () => {
      this.statusListeners = this.statusListeners.filter((l) => l !== cb);
    };
  }

  /** Subscribe to a specific event type */
  subscribe<T = unknown>(
    type: RealtimeEventType,
    callback: ChannelCallback<T>,
  ): () => void {
    const entry: ListenerEntry = { type, callback: callback as ChannelCallback };
    this.listeners.push(entry);

    // Ensure connection is active
    if (this._status === 'disconnected' || this._status === 'error') {
      this.connect();
    }

    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter((l) => l !== entry);
    };
  }

  /** Force a reconnection (e.g. after token refresh) */
  reconnect(): void {
    this.disconnect();
    this.reconnectAttempt = 0;
    this.connect();
  }

  /** Gracefully close the connection */
  disconnect(): void {
    this.intentionalClose = true;
    this.clearReconnectTimer();
    this.closeTransport();
    this.setStatus('disconnected');
  }

  // ── Connection lifecycle ───────────────────────────────────

  private connect(): void {
    if (this._status === 'connecting' || this._status === 'connected') return;

    this.intentionalClose = false;
    this.setStatus('connecting');

    if (this.useSseFallback) {
      this.connectSse();
    } else {
      this.connectWs();
    }
  }

  private connectWs(): void {
    const token = getApiToken();
    const url = `${getWsBaseUrl()}${WS_ENDPOINT}`;
    // Append token as query param (common auth pattern for WS)
    const finalUrl = token ? `${url}?token=${encodeURIComponent(token)}` : url;

    try {
      this.ws = new WebSocket(finalUrl);

      this.ws.onopen = () => {
        this.reconnectAttempt = 0;
        this.setStatus('connected');
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const data: RealtimeEvent = JSON.parse(event.data as string);
          if (data.type) {
            this.dispatch(data.type, data);
          }
        } catch {
          // Ignore malformed messages
        }
      };

      this.ws.onerror = () => {
        // If WebSocket fails, try SSE fallback
        if (this.useSseFallback === false) {
          this.useSseFallback = true;
          this.closeTransport();
          this.connectSse();
        } else {
          this.setStatus('error');
          this.scheduleReconnect();
        }
      };

      this.ws.onclose = () => {
        if (!this.intentionalClose) {
          this.setStatus('disconnected');
          this.scheduleReconnect();
        }
      };
    } catch {
      // WebSocket constructor can throw in some environments
      this.useSseFallback = true;
      this.connectSse();
    }
  }

  private connectSse(): void {
    const token = getApiToken();
    const baseUrl = typeof window !== 'undefined'
      ? `${window.location.protocol}//${window.location.hostname}:8000`
      : 'http://localhost:8000';
    const url = `${baseUrl}${SSE_ENDPOINT}`;
    const finalUrl = token ? `${url}?token=${encodeURIComponent(token)}` : url;

    try {
      this.eventSource = new EventSource(finalUrl);

      this.eventSource.onopen = () => {
        this.reconnectAttempt = 0;
        this.setStatus('connected');
      };

      // SSE: listen for generic "message" and also named events
      const handleSseMessage = (event: MessageEvent) => {
        try {
          const data: RealtimeEvent = JSON.parse(event.data);
          if (data.type) {
            this.dispatch(data.type, data);
          }
        } catch {
          // Ignore
        }
      };

      this.eventSource.onmessage = handleSseMessage;

      // Also listen for specific event types sent as SSE named events
      const eventTypes: RealtimeEventType[] = [
        'alert.raised',
        'alert.updated',
        'bed_grid.updated',
        'presence.updated',
        'vitals.updated',
      ];
      for (const et of eventTypes) {
        this.eventSource.addEventListener(et, handleSseMessage as EventListener);
      }

      this.eventSource.onerror = () => {
        this.setStatus('error');
        this.closeTransport();
        this.scheduleReconnect();
      };
    } catch {
      this.setStatus('error');
      this.scheduleReconnect();
    }
  }

  private closeTransport(): void {
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect trigger
      this.ws.close();
      this.ws = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  // ── Reconnect with exponential backoff ─────────────────────

  private scheduleReconnect(): void {
    if (this.intentionalClose) return;

    const delay = Math.min(
      this.baseDelay * Math.pow(2, this.reconnectAttempt),
      this.maxReconnectDelay,
    );
    this.reconnectAttempt++;

    this.clearReconnectTimer();
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  // ── Status management ──────────────────────────────────────

  private setStatus(s: ConnectionStatus): void {
    if (this._status === s) return;
    this._status = s;
    for (const cb of this.statusListeners) {
      try {
        cb(s);
      } catch {
        // Don't let listener errors break the connection
      }
    }
  }

  // ── Dispatch to listeners ─────────────────────────────────

  private dispatch(type: RealtimeEventType, event: RealtimeEvent): void {
    for (const entry of this.listeners) {
      if (entry.type === type) {
        try {
          entry.callback(event);
        } catch {
          // Don't let listener errors break the dispatch loop
        }
      }
    }
  }
}

// ─────────────────────────────────────────────────────────────
// React hook
// ─────────────────────────────────────────────────────────────

import { useEffect, useState, useRef } from 'react';

/**
 * Subscribe to a realtime event channel.
 *
 * @example
 * ```tsx
 * const { data, status } = useRealtimeChannel<DashboardData>('bed_grid.updated', (event) => {
 *   // optional: side effects when event arrives
 * });
 * ```
 */
export function useRealtimeChannel<T = unknown>(
  eventType: RealtimeEventType,
  onEvent?: (payload: T) => void,
) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastEvent, setLastEvent] = useState<RealtimeEvent<T> | null>(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    const conn = RealtimeConnection.getInstance();

    // Subscribe to status changes
    const unsubStatus = conn.onStatusChange((s) => {
      setStatus(s);
    });

    // Subscribe to the specific event type
    const unsubChannel = conn.subscribe<T>(eventType, (event) => {
      setLastEvent(event);
      onEventRef.current?.(event.payload);
    });

    return () => {
      unsubStatus();
      unsubChannel();
    };
  }, [eventType]);

  return { status, lastEvent };
}

/**
 * Low-level hook: get the raw connection status only (for status indicators).
 */
export function useConnectionStatus(): ConnectionStatus {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');

  useEffect(() => {
    const conn = RealtimeConnection.getInstance();
    const unsub = conn.onStatusChange(setStatus);
    return unsub;
  }, []);

  return status;
}

// Re-export the singleton for imperative use
export { RealtimeConnection };
