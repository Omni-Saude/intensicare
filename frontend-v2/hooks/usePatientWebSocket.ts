'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Simple WebSocket hook for patient realtime updates.
 *
 * Subscribes to patient-specific channel and triggers a refetch callback
 * when new data is available. Respects the "one channel" architecture
 * (ADR-0017-01) — this is the single realtime entry point for the patient page.
 */

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UsePatientWebSocketOptions {
  mpiId: string;
  onUpdate: () => void;
  enabled?: boolean;
}

interface UsePatientWebSocketReturn {
  connectionState: ConnectionState;
  reconnect: () => void;
}

export function usePatientWebSocket({
  mpiId,
  onUpdate,
  enabled = true,
}: UsePatientWebSocketOptions): UsePatientWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stateRef = useRef<ConnectionState>('disconnected');
  const [, setRenderState] = useState(0);

  const forceRender = useCallback(() => {
    setRenderState((n) => n + 1);
  }, []);

  const setState = useCallback(
    (state: ConnectionState) => {
      if (stateRef.current !== state) {
        stateRef.current = state;
        forceRender();
      }
    },
    [forceRender],
  );

  const connect = useCallback(() => {
    if (!enabled || !mpiId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/patient/${encodeURIComponent(mpiId)}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      setState('connecting');

      ws.onopen = () => {
        setState('connected');
      };

      ws.onmessage = (_event) => {
        onUpdate();
      };

      ws.onclose = () => {
        setState('disconnected');
        wsRef.current = null;
        if (enabled) {
          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      ws.onerror = () => {
        setState('error');
        ws.close();
      };
    } catch {
      setState('error');
      if (enabled) {
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, 5000);
      }
    }
  }, [mpiId, onUpdate, enabled, setState]);

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    connect();
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return {
    connectionState: stateRef.current,
    reconnect,
  };
}
