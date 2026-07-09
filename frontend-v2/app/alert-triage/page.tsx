'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Filter, RefreshCw, AlertTriangle, Search, Wifi, WifiOff } from 'lucide-react';
import Layout from '@/components/Layout';
import AlertCard from '@/components/AlertCard';
import { fetchAlerts, type AlertInfo, type AlertListResponse } from '@/lib/api';
import { useRealtimeChannel, useConnectionStatus, type RealtimeEvent } from '@/lib/websocket';

// Status filter colors — using CSS custom properties (design-tokens.md)
const STATUS_FILTERS = [
  {
    value: 'active',
    label: 'Active',
    bgVar: 'var(--clinical-severity-critical-wash)',
    textVar: 'var(--clinical-severity-critical-on-surface)',
  },
  {
    value: 'acknowledged',
    label: 'Acknowledged',
    bgVar: 'var(--clinical-status-attended-color)',
    textVar: 'var(--clinical-status-attended-on-color)',
  },
  {
    value: 'escalated',
    label: 'Escalated',
    bgVar: 'var(--clinical-severity-urgent-wash)',
    textVar: 'var(--clinical-severity-urgent-on-surface)',
  },
  {
    value: 'resolved',
    label: 'Resolved',
    bgVar: 'var(--clinical-severity-normal-wash)',
    textVar: 'var(--clinical-severity-normal-on-surface)',
  },
];

export default function AlertTriagePage() {
  const [alerts, setAlerts] = useState<AlertInfo[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('active');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 20;

  // WebSocket connection status
  const wsStatus = useConnectionStatus();

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result: AlertListResponse = await fetchAlerts({
        status: statusFilter,
        limit: pageSize,
        offset: page * pageSize,
      });
      setAlerts(result.alerts);
      setTotal(result.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, page]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // Subscribe to realtime alert events via WebSocket (replaces polling)
  useRealtimeChannel('alert.raised', useCallback(() => {
    // New alert raised — refresh the current page
    loadAlerts();
  }, [loadAlerts]));

  useRealtimeChannel('alert.updated', useCallback(() => {
    // Alert status changed — refresh
    loadAlerts();
  }, [loadAlerts]));

  const totalPages = Math.ceil(total / pageSize);

  // Client-side search filter
  const filteredAlerts = search
    ? alerts.filter(
        (a) =>
          a.title.toLowerCase().includes(search.toLowerCase()) ||
          (a.body && a.body.toLowerCase().includes(search.toLowerCase())) ||
          a.mpi_id.toLowerCase().includes(search.toLowerCase()),
      )
    : alerts;

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1
              className="text-2xl font-bold"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              Triagem de Alertas
            </h1>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              {total} alert{total !== 1 ? 's' : ''} · {statusFilter}
              {/* WS indicator */}
              <span className="inline-flex items-center gap-1 ml-3">
                {wsStatus === 'connected' ? (
                   <Wifi className="w-3 h-3" style={{ color: 'var(--clinical-severity-normal-signal)' }} aria-hidden="true" />
                ) : (
                   <WifiOff className="w-3 h-3" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
                )}
                <span className="text-[10px]">
                  {wsStatus === 'connected' ? 'Ao vivo' : wsStatus === 'connecting' ? '...' : 'Offline'}
                </span>
              </span>
            </p>
          </div>
          <button
            onClick={loadAlerts}
            disabled={loading}
            aria-label="Refresh alerts"
            className="flex items-center gap-2 px-3 py-2 bg-[var(--semantic-surface-raised)] border border-[var(--semantic-border-default)] rounded-lg text-sm disabled:opacity-50"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
            Atualizar
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex flex-wrap gap-2">
          {STATUS_FILTERS.map((f) => {
            const isSelected = statusFilter === f.value;
            return (
              <button
                key={f.value}
                onClick={() => {
                  setStatusFilter(f.value);
                  setPage(0);
                }}
                aria-label={`Filter by ${f.label} alerts`}
                aria-pressed={isSelected}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                style={
                  isSelected
                    ? {
                        backgroundColor: f.bgVar,
                        color: f.textVar,
                        boxShadow: `0 0 0 2px var(--semantic-surface-canvas), 0 0 0 4px currentColor`,
                      }
                    : {
                        backgroundColor: 'var(--semantic-surface-raised)',
                        color: 'var(--semantic-text-secondary)',
                      }
                }
              >
                {f.label}
              </button>
            );
          })}
        </div>

        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--semantic-text-secondary)]" aria-hidden="true" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar alertas..."
            aria-label="Search alerts"
            className="w-full pl-9 pr-3 py-2 bg-[var(--semantic-surface-raised)] border border-[var(--semantic-border-default)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Error — uses critical severity tokens */}
      {error && (
        <div
          className="border rounded-xl p-4 mb-6"
          style={{
            color: 'var(--clinical-severity-critical-on-surface)',
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
          }}
          role="alert"
          aria-live="assertive"
        >
          <p className="font-medium">Falha ao carregar alertas</p>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={loadAlerts}
            className="mt-2 text-sm underline"
            aria-label="Retry loading alerts"
          >
            Tentar novamente
          </button>
        </div>
      )}

      {/* Loading — skeleton list */}
      {loading && (
        <div className="space-y-4 animate-pulse">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="rounded-xl border p-5"
              style={{ borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="space-y-2 flex-1">
                  <div className="h-5 rounded w-48" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                  <div className="h-3 rounded w-32" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                </div>
                <div className="h-6 rounded-full w-20" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
              </div>
              <div className="h-4 rounded w-3/4" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
            </div>
          ))}
        </div>
      )}

      {/* Alert list */}
      {!loading && filteredAlerts.length > 0 && (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} onUpdate={loadAlerts} />
          ))}
        </div>
      )}

      {/* Empty */}
      {!loading && alerts.length === 0 && (
        <div className="text-center py-20">
          <AlertTriangle
            className="w-12 h-12 mx-auto mb-4"
            style={{ color: 'var(--semantic-text-secondary)', opacity: 0.5 }}
            aria-hidden="true"
          />
          <p
            className="font-medium"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Nenhum alerta {statusFilter}
          </p>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Tudo limpo!
          </p>
        </div>
      )}

      {/* No search results */}
      {!loading && alerts.length > 0 && filteredAlerts.length === 0 && (
        <div className="text-center py-12">
          <p style={{ color: 'var(--semantic-text-secondary)' }}>
            Nenhum alerta corresponde à sua busca
          </p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            aria-label="Previous page"
            className="px-3 py-1.5 bg-[var(--semantic-surface-raised)] border border-[var(--semantic-border-default)] rounded-lg text-sm disabled:opacity-50"
          >
            Anterior
          </button>
          <span
            className="text-sm"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Página {page + 1} de {totalPages}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            aria-label="Next page"
            className="px-3 py-1.5 bg-[var(--semantic-surface-raised)] border border-[var(--semantic-border-default)] rounded-lg text-sm disabled:opacity-50"
          >
            Próximo
          </button>
        </div>
      )}
    </Layout>
  );
}
