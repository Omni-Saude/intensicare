'use client';

import { useState, useCallback, useMemo } from 'react';
import useSWR from 'swr';
import { Bell } from 'lucide-react';
import {
  fetchAlerts,
  type AlertInfo,
  type AlertFilters,
  type SeverityLevel,
} from '@/lib/api';
import { useRealtimeChannel } from '@/lib/websocket';
import { FilterBar, type AlertFilterValues } from '@/components/alerts/filter-bar';
import { AlertTable } from '@/components/alerts/alert-table';

const INITIAL_FILTERS: AlertFilterValues = {
  severity: '',
  status: 'active',
  unit: '',
  pathway: '',
  period: 'all',
};

export default function AlertsPage() {
  const [filters, setFilters] = useState<AlertFilterValues>(INITIAL_FILTERS);
  const [optimisticUpdates, setOptimisticUpdates] = useState<
    Map<number, AlertInfo>
  >(new Map());

  // Build API params from filters. AlertFilterValues.status mirrors the
  // backend's AlertStatusFilter contract 1:1 (active/acknowledged/
  // escalated/resolved/all), so it passes straight through — including
  // 'all', which is what lets the user review already-processed alerts
  // that the default 'active' view would otherwise hide.
  const apiParams: AlertFilters = useMemo(() => {
    const params: AlertFilters = { limit: 50, status: filters.status };

    if (filters.severity) {
      params.severity = filters.severity as SeverityLevel;
    }

    return params;
  }, [filters]);

  const {
    data,
    error,
    isLoading,
    mutate,
  } = useSWR(
    ['alerts', apiParams],
    () => fetchAlerts(apiParams),
    {
      // WebSocket (below) is primary; interval is defense-in-depth
      refreshInterval: 30_000,
      revalidateOnFocus: true,
    },
  );

  // Realtime: WebSocket + polling fallback (ADR-0034)
  useRealtimeChannel('alert.raised', () => mutate(), { fallbackInterval: 30_000 });
  useRealtimeChannel('alert.updated', () => mutate(), { fallbackInterval: 30_000 });

  // Client-side filtering for unit/pathway (not yet supported by API)
  const alerts = useMemo(() => {
    if (!data?.items) return [];

    let items = data.items;

    // Apply optimistic updates
    for (const [id, updated] of optimisticUpdates) {
      items = items.map((a) => (a.id === id ? { ...a, ...updated } : a));
    }

    // Client-side filters not yet in API
    if (filters.unit) {
      const unitLower = filters.unit.toLowerCase();
      items = items.filter(
        (a) =>
          // AlertInfo doesn't have unit; match on patient_name as proxy
          (a.patient_name?.toLowerCase().includes(unitLower) ?? false),
      );
    }

    if (filters.pathway) {
      const pwLower = filters.pathway.toLowerCase();
      items = items.filter(
        (a) =>
          a.pathway_name?.toLowerCase().includes(pwLower) ??
          false,
      );
    }

    return items;
  }, [data, optimisticUpdates, filters.unit, filters.pathway]);

  const handleAlertUpdate = useCallback(
    (updated: AlertInfo) => {
      // Optimistic update
      setOptimisticUpdates((prev) => {
        const next = new Map(prev);
        next.set(updated.id, updated);
        return next;
      });

      // Revalidate in background
      mutate();
    },
    [mutate],
  );

  const [globalError, setGlobalError] = useState<string | null>(null);
  const handleError = useCallback((message: string) => {
    setGlobalError(message);
    setTimeout(() => setGlobalError(null), 5000);
  }, []);

  return (
    <div className="flex flex-col gap-4">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Alertas
          </h1>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Triagem e acompanhamento de alertas clínicos
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-[var(--surface-raised)] border border-[var(--border-default)] px-3 py-2">
          <Bell className="h-4 w-4 text-[var(--text-secondary)]" aria-hidden="true" />
          <span className="text-sm text-[var(--text-primary)]">
            <strong>{data?.total ?? '—'}</strong>{' '}
            <span className="text-[var(--text-secondary)]">alertas</span>
          </span>
        </div>
      </div>

      {/* Global error toast */}
      {globalError && (
        <div
          className="flex items-center gap-2 rounded-lg border border-[var(--severity-critical)]/40 bg-[var(--severity-critical-wash)] px-4 py-2.5 text-sm text-[var(--severity-critical)]"
          role="alert"
        >
          <Bell className="h-4 w-4" aria-hidden="true" />
          {globalError}
        </div>
      )}

      {/* Filters */}
      <FilterBar filters={filters} onChange={setFilters} />

      {/* Alert list */}
      <AlertTable
        alerts={alerts}
        isLoading={isLoading}
        isEmpty={!isLoading && !error && alerts.length === 0}
        error={error ? (error instanceof Error ? error.message : 'Erro desconhecido') : null}
        onAlertUpdate={handleAlertUpdate}
        onError={handleError}
      />
    </div>
  );
}
