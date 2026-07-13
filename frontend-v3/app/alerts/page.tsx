'use client';

import { useState, useCallback, useMemo } from 'react';
import useSWR from 'swr';
import { Bell } from 'lucide-react';
import {
  fetchAlerts,
  fetchAlertGroups,
  type AlertInfo,
  type AlertFilters,
  type AlertListResponse,
  type AlertGroupListResponse,
  type SeverityLevel,
} from '@/lib/api';
import { useRealtimeChannel } from '@/lib/websocket';
import { cn } from '@/lib/utils';
import { FilterBar, type AlertFilterValues } from '@/components/alerts/filter-bar';
import { AlertTable, AlertGroupTable } from '@/components/alerts/alert-table';

const INITIAL_FILTERS: AlertFilterValues = {
  severity: '',
  status: 'active',
  unit: '',
  pathway: '',
  period: 'all',
};

type AlertsView = 'grouped' | 'flat';

function isGroupResponse(
  data: AlertListResponse | AlertGroupListResponse | undefined,
): data is AlertGroupListResponse {
  return !!data && 'groups' in data;
}

// Folds one or more just-confirmed alert updates (ack/resolve/escalate
// responses, already authoritative — the request already round-tripped)
// directly into a *copy* of the current SWR cache value. Used as the
// updater passed to `mutate(key, updater, { revalidate: false })` from an
// action handler below, so a member's new state lands in the single source
// of truth (the SWR cache) synchronously, with no separate "optimistic"
// state and no follow-up GET that could race a concurrently-triggered
// WebSocket revalidation and overwrite it with an in-flight, older
// snapshot (GK-RESP achado C).
//
// Deliberately does NOT drop a member that no longer matches the active
// status filter (e.g. an just-acknowledged alert while filters.status ===
// 'active') or recompute group aggregates (count/max_severity/escalating)
// — those stay exactly as the server last computed them, same as before
// this fix, until the next real revalidation (WS event / focus / 30s
// interval) reconciles them. Recomputing aggregates client-side would risk
// exactly the "backend-computed aggregate stays truthful" invariant the
// existing grouped-view filtering comment below already protects.
function applyAlertUpdates(
  current: AlertListResponse | AlertGroupListResponse | undefined,
  updates: AlertInfo[],
): AlertListResponse | AlertGroupListResponse | undefined {
  if (!current || updates.length === 0) return current;
  const byId = new Map(updates.map((u) => [u.id, u]));

  if (isGroupResponse(current)) {
    return {
      ...current,
      groups: current.groups.map((g) => ({
        ...g,
        members: g.members.map((m) => {
          const patch = byId.get(m.id);
          return patch ? { ...m, ...patch } : m;
        }),
      })),
    };
  }

  return {
    ...current,
    items: current.items.map((a) => {
      const patch = byId.get(a.id);
      return patch ? { ...a, ...patch } : a;
    }),
  };
}

export default function AlertsPage() {
  const [filters, setFilters] = useState<AlertFilterValues>(INITIAL_FILTERS);

  // Default view is "Por paciente/sinal" (grouped) — ADR-0039/FASE 2B.1:
  // grouping is the alerts page's default; the flat list is the fallback,
  // reachable via the toggle below. Persistence is plain useState (survives
  // filter changes/re-renders within the session, resets on reload) —
  // cross-session persistence via localStorage was evaluated but dropped:
  // the app has zero existing localStorage precedent for UI prefs (the JWT
  // is deliberately in-memory-only, see lib/api.ts), and this repo's
  // react-hooks/purity + set-state-in-effect lint rules reject the naive
  // "read in a mount effect" approach — the only compliant pattern already
  // in the codebase (useSyncExternalStore, lib/websocket.ts) needs a full
  // module-level pub-sub to be visible within the same tab (localStorage's
  // native 'storage' event doesn't fire in the tab that wrote it), which is
  // not the "trivial" persistence this phase asked for.
  const [view, setView] = useState<AlertsView>('grouped');

  const handleViewChange = useCallback((next: AlertsView) => {
    setView(next);
  }, []);

  // Build API params from filters. AlertFilterValues.status mirrors the
  // backend's AlertStatusFilter contract 1:1 (active/acknowledged/
  // escalated/resolved/all), so it passes straight through — including
  // 'all', which is what lets the user review already-processed alerts
  // that the default 'active' view would otherwise hide. Reused as-is for
  // both fetchAlerts and fetchAlertGroups (ADR-0039 §2: "Filtros existentes
  // aplicam-se aos membros").
  const apiParams: AlertFilters = useMemo(() => {
    const params: AlertFilters = { limit: 50, status: filters.status };

    if (filters.severity) {
      params.severity = filters.severity as SeverityLevel;
    }

    return params;
  }, [filters]);

  // Single SWR entry keyed on [view, apiParams] — this is deliberate so the
  // WebSocket revalidation below (`mutate()`) always targets whichever
  // query (grouped or flat) is currently mounted, rather than two
  // independent caches that could drift (FASE 2B.1 requirement 6: "a visão
  // agrupada usa a MESMA chave SWR/mutate").
  const {
    data,
    error,
    isLoading,
    mutate,
  } = useSWR<AlertListResponse | AlertGroupListResponse>(
    ['alerts', view, apiParams],
    () => (view === 'grouped' ? fetchAlertGroups(apiParams) : fetchAlerts(apiParams)),
    {
      // WebSocket (below) is primary; interval is defense-in-depth
      refreshInterval: 30_000,
      revalidateOnFocus: true,
    },
  );

  // Realtime: WebSocket + polling fallback (ADR-0034). Bound to the single
  // `mutate` above, so a new/reactivated group appears in the grouped view
  // without a reload, exactly as it already does for the flat view. This is
  // a real GET revalidation (unlike the action handlers below) — that's
  // correct here, since a raised/updated alert this client didn't cause
  // itself is genuinely unknown data that only the server can supply.
  useRealtimeChannel('alert.raised', () => mutate(), { fallbackInterval: 30_000 });
  useRealtimeChannel('alert.updated', () => mutate(), { fallbackInterval: 30_000 });

  // Client-side filtering for unit/pathway (not yet supported by the API)
  // — flat view.
  const alerts = useMemo(() => {
    if (view !== 'flat' || !data || isGroupResponse(data)) return [];

    let items = data.items;

    if (filters.unit) {
      const unitLower = filters.unit.toLowerCase();
      items = items.filter(
        (a) => a.patient_name?.toLowerCase().includes(unitLower) ?? false,
      );
    }

    if (filters.pathway) {
      const pwLower = filters.pathway.toLowerCase();
      items = items.filter(
        (a) => a.pathway_name?.toLowerCase().includes(pwLower) ?? false,
      );
    }

    return items;
  }, [data, view, filters.unit, filters.pathway]);

  // Same client-side filters, applied at group granularity — grouped view.
  // A group is kept if it (or one of its members, for the pathway filter)
  // matches; member arrays are never pruned by these FE-only filters, so a
  // rendered group's count/severity badge always matches its expanded
  // member list (the backend-computed aggregate stays truthful). Per-member
  // ack/resolve/escalate patches are no longer applied here — `data` itself
  // already carries them, written straight into the SWR cache by the action
  // handlers below via `applyAlertUpdates`.
  const groups = useMemo(() => {
    if (view !== 'grouped' || !data || !isGroupResponse(data)) return [];

    let gs = data.groups;

    if (filters.unit) {
      const unitLower = filters.unit.toLowerCase();
      gs = gs.filter((g) => g.patient_name?.toLowerCase().includes(unitLower) ?? false);
    }

    if (filters.pathway) {
      const pwLower = filters.pathway.toLowerCase();
      gs = gs.filter((g) =>
        g.members.some((m) => m.pathway_name?.toLowerCase().includes(pwLower) ?? false),
      );
    }

    return gs;
  }, [data, view, filters.unit, filters.pathway]);

  // Single-alert actions (ack/resolve/escalate, both views). The API call
  // already happened and already succeeded by the time this fires (see
  // QuickActions) — `updated` is the server's own authoritative response,
  // not a guess — so this writes it straight into the SWR cache
  // (`populateCache: true`) and explicitly skips the automatic follow-up
  // GET (`revalidate: false`). That follow-up GET was the actual race (GK-
  // RESP achado C): a concurrent WebSocket-triggered revalidation (e.g.
  // another patient's `alert.raised`) could be in flight and get deduped
  // with this call's own revalidation, so this call could "win" the mutate
  // but silently receive that OTHER, older in-flight response instead of a
  // fresh one — overwriting the just-applied update with stale data. There
  // is no longer a second network round-trip for this call to race against.
  const handleAlertUpdate = useCallback(
    (updated: AlertInfo) => {
      mutate((current) => applyAlertUpdates(current, [updated]), {
        revalidate: false,
        populateCache: true,
        rollbackOnError: true,
      });
    },
    [mutate],
  );

  // Group acknowledge (ADR-0039 §4): AlertGroupRow runs its N sequential
  // acknowledges itself and hands back every one that actually succeeded
  // (partial failures are reported separately via onError) — folded into
  // the cache in one `mutate` call, same non-racing pattern as above.
  const handleGroupAcknowledged = useCallback(
    (succeeded: AlertInfo[]) => {
      mutate((current) => applyAlertUpdates(current, succeeded), {
        revalidate: false,
        populateCache: true,
        rollbackOnError: true,
      });
    },
    [mutate],
  );

  const [globalError, setGlobalError] = useState<string | null>(null);
  const handleError = useCallback((message: string) => {
    setGlobalError(message);
    setTimeout(() => setGlobalError(null), 5000);
  }, []);

  const totalAlerts = data ? (isGroupResponse(data) ? data.total_alerts : data.total) : undefined;

  return (
    <div className="flex flex-col gap-4">
      {/* Page header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Alertas
          </h1>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Triagem e acompanhamento de alertas clínicos
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* View toggle — grouped ("Por paciente/sinal") is the default;
              flat ("Lista completa") is the pre-existing view, unchanged. */}
          <div
            className="inline-flex items-center rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-0.5"
            role="group"
            aria-label="Modo de visualização dos alertas"
          >
            <button
              type="button"
              onClick={() => handleViewChange('grouped')}
              aria-pressed={view === 'grouped'}
              className={cn(
                'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                view === 'grouped'
                  ? 'bg-[var(--severity-watch-wash)] text-[var(--severity-watch)]'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
              )}
            >
              Por paciente/sinal
            </button>
            <button
              type="button"
              onClick={() => handleViewChange('flat')}
              aria-pressed={view === 'flat'}
              className={cn(
                'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                view === 'flat'
                  ? 'bg-[var(--severity-watch-wash)] text-[var(--severity-watch)]'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
              )}
            >
              Lista completa
            </button>
          </div>

          <div className="flex items-center gap-2 rounded-lg bg-[var(--surface-raised)] border border-[var(--border-default)] px-3 py-2">
            <Bell className="h-4 w-4 text-[var(--text-secondary)]" aria-hidden="true" />
            <span className="text-sm text-[var(--text-primary)]">
              {view === 'grouped' && isGroupResponse(data) ? (
                <>
                  <strong>{data.total_groups}</strong>{' '}
                  <span className="text-[var(--text-secondary)]">grupos</span>
                  <span className="text-[var(--text-secondary)]"> · </span>
                  <strong>{data.total_alerts}</strong>{' '}
                  <span className="text-[var(--text-secondary)]">alertas</span>
                </>
              ) : (
                <>
                  <strong>{totalAlerts ?? '—'}</strong>{' '}
                  <span className="text-[var(--text-secondary)]">alertas</span>
                </>
              )}
            </span>
          </div>
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
      {view === 'grouped' ? (
        <AlertGroupTable
          groups={groups}
          isLoading={isLoading}
          isEmpty={!isLoading && !error && groups.length === 0}
          error={error ? (error instanceof Error ? error.message : 'Erro desconhecido') : null}
          onAlertUpdate={handleAlertUpdate}
          onError={handleError}
          onGroupAcknowledged={handleGroupAcknowledged}
        />
      ) : (
        <AlertTable
          alerts={alerts}
          isLoading={isLoading}
          isEmpty={!isLoading && !error && alerts.length === 0}
          error={error ? (error instanceof Error ? error.message : 'Erro desconhecido') : null}
          onAlertUpdate={handleAlertUpdate}
          onError={handleError}
        />
      )}
    </div>
  );
}
