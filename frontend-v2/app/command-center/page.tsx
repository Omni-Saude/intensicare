'use client';

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Activity, AlertTriangle, Bell, ShieldAlert, Search, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { FullScreenLayout } from '@/components/Layout';
import SeverityBadge from '@/components/SeverityBadge';
import ClinicalTooltip from '@/components/ClinicalTooltip';
import { fetchDashboard, type DashboardResponse } from '@/lib/api';
import { useRealtimeChannel, useConnectionStatus, type RealtimeEvent } from '@/lib/websocket';
import { getMEWSSeverity, getSeverityStyle, getSeverityFromAlert } from '@/lib/clinical-severity';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

export default function CommandCenterPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string | null>(null);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // WebSocket connection status for indicator
  const wsStatus = useConnectionStatus();

  // Keyboard shortcuts: 1-4 → filter by severity, / → focus search, Escape → clear filters
  useKeyboardShortcuts([
    {
      key: '1',
      handler: () => setSeverityFilter(severityFilter === 'critical' ? null : 'critical'),
    },
    {
      key: '2',
      handler: () => setSeverityFilter(severityFilter === 'warning' ? null : 'warning'),
    },
    {
      key: '3',
      handler: () => setSeverityFilter(severityFilter === 'normal' ? null : 'normal'),
    },
    {
      key: '4',
      handler: () => setSeverityFilter(severityFilter === 'alert' ? null : 'alert'),
    },
    {
      key: '/',
      handler: () => {
        if (searchInputRef.current) {
          searchInputRef.current.focus();
        }
      },
    },
    {
      key: 'Escape',
      handler: () => {
        setSearch('');
        setSeverityFilter(null);
      },
    },
    {
      key: 'j',
      handler: () => moveFocus(1),
    },
    {
      key: 'k',
      handler: () => moveFocus(-1),
    },
    {
      key: 'ArrowDown',
      handler: () => moveFocus(1),
    },
    {
      key: 'ArrowUp',
      handler: () => moveFocus(-1),
    },
  ]);

  // Initial data load (REST)
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchDashboard();
      setData(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Subscribe to realtime bed_grid updates via WebSocket
  useRealtimeChannel('bed_grid.updated', useCallback((payload: unknown) => {
    // When the bed grid updates, reload the full dashboard to keep state consistent
    const event = payload as RealtimeEvent<DashboardResponse>;
    if (event?.payload) {
      // Direct payload update (optimistic)
      setData(event.payload as DashboardResponse);
      setLoading(false);
    } else {
      // Fallback: re-fetch
      loadData();
    }
  }, [loadData]));

  const filteredPatients = data?.patients.filter((p) => {
    const matchesSearch =
      !search ||
      p.display_name.toLowerCase().includes(search.toLowerCase()) ||
      p.mpi_id.toLowerCase().includes(search.toLowerCase()) ||
      (p.bed_id && p.bed_id.toLowerCase().includes(search.toLowerCase()));

    const matchesSeverity =
      !severityFilter ||
      (severityFilter === 'critical' &&
        p.highest_alert_severity === 'critical') ||
      (severityFilter === 'warning' &&
        p.highest_alert_severity === 'warning') ||
      (severityFilter === 'normal' && !p.highest_alert_severity) ||
      (severityFilter === 'alert' && p.active_alerts_count > 0);

    return matchesSearch && matchesSeverity;
  });

  // Reset focusedIndex when filters change
  useEffect(() => {
    setFocusedIndex(-1);
  }, [search, severityFilter]);

  // Navigate patient list with j/k/↑/↓ — wraps at boundaries
  const moveFocus = useCallback(
    (direction: number) => {
      if (!filteredPatients || filteredPatients.length === 0) return;
      setFocusedIndex((prev) => {
        const next = prev + direction;
        if (next < 0) return filteredPatients.length - 1;
        if (next >= filteredPatients.length) return 0;
        return next;
      });
    },
    [filteredPatients],
  );

  if (loading && !data) {
    return (
      <FullScreenLayout>
        <div className="flex items-center justify-center py-20">
          <div
            className="flex items-center gap-3"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            <RefreshCw className="w-5 h-5 animate-spin" aria-hidden="true" />
            <span>Carregando painel de leitos...</span>
          </div>
        </div>
      </FullScreenLayout>
    );
  }

  if (error) {
    return (
      <FullScreenLayout>
        <div
          className="border rounded-xl p-6"
          style={{
            color: 'var(--clinical-severity-critical-on-surface)',
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
          }}
          role="alert"
          aria-live="assertive"
        >
          <h2 className="font-semibold">Erro ao carregar painel de leitos</h2>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={loadData}
            className="mt-3 text-sm underline"
            aria-label="Tentar novamente"
          >
            Tentar novamente
          </button>
        </div>
      </FullScreenLayout>
    );
  }

  const criticalCount =
    data?.patients.filter(
      (p) => p.highest_alert_severity === 'critical',
    ).length || 0;
  const warningCount =
    data?.patients.filter(
      (p) =>
        p.active_alerts_count > 0 &&
        p.highest_alert_severity !== 'critical',
    ).length || 0;
  const normalCount =
    data?.patients.filter((p) => p.active_alerts_count === 0).length || 0;

  return (
    <FullScreenLayout>
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1
              className="text-2xl font-bold"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              Central de Comando
            </h1>
            <p
              className="text-sm mt-1"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Painel de leitos com visão de gravidade
              {/* WS connection indicator */}
              <span className="inline-flex items-center gap-1 ml-3">
                {wsStatus === 'connected' ? (
                  <Wifi className="w-3 h-3" style={{ color: 'var(--clinical-severity-normal-signal)' }} aria-hidden="true" />
                ) : (
                  <WifiOff className="w-3 h-3" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
                )}
                <span className="text-[10px]">
                  {wsStatus === 'connected' ? 'Ao vivo' : wsStatus === 'connecting' ? 'Conectando...' : 'Offline'}
                </span>
              </span>
            </p>
          </div>
          <button
            onClick={loadData}
            disabled={loading}
            aria-label="Refresh bed board"
            className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm disabled:opacity-50"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
            Atualizar
          </button>
        </div>
      </div>

      {/* Severity summary cards */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {/* Critical */}
        <button
          onClick={() =>
            setSeverityFilter(
              severityFilter === 'critical' ? null : 'critical',
            )
          }
          aria-label={`Critical: ${criticalCount} patients`}
          aria-pressed={severityFilter === 'critical'}
          className="p-4 rounded-xl border-2 transition-all bg-white border-slate-200"
          style={
            severityFilter === 'critical'
              ? {
                  borderColor: 'var(--clinical-severity-critical-signal)',
                  backgroundColor: 'var(--clinical-severity-critical-wash)',
                }
              : {}
          }
        >
          <h3 className="sr-only">Critical Patients</h3>
          <div className="flex items-center gap-2 mb-1">
            <ShieldAlert
              className="w-5 h-5"
              style={{ color: 'var(--clinical-severity-critical-signal)' }}
              aria-hidden="true"
            />
            <span
              className="text-xs font-semibold uppercase"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Crítico
            </span>
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
          >
            {criticalCount}
          </div>
        </button>

        {/* Warning */}
        <button
          onClick={() =>
            setSeverityFilter(
              severityFilter === 'warning' ? null : 'warning',
            )
          }
          aria-label={`Warning: ${warningCount} patients`}
          aria-pressed={severityFilter === 'warning'}
          className="p-4 rounded-xl border-2 transition-all bg-white border-slate-200"
          style={
            severityFilter === 'warning'
              ? {
                  borderColor: 'var(--clinical-severity-watch-signal)',
                  backgroundColor: 'var(--clinical-severity-watch-wash)',
                }
              : {}
          }
        >
          <h3 className="sr-only">Warning Patients</h3>
          <div className="flex items-center gap-2 mb-1">
            <Bell
              className="w-5 h-5"
              style={{ color: 'var(--clinical-severity-watch-signal)' }}
              aria-hidden="true"
            />
            <span
              className="text-xs font-semibold uppercase"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Atenção
            </span>
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: 'var(--clinical-severity-watch-on-surface)' }}
          >
            {warningCount}
          </div>
        </button>

        {/* Stable */}
        <button
          onClick={() =>
            setSeverityFilter(severityFilter === 'normal' ? null : 'normal')
          }
          aria-label={`Stable: ${normalCount} patients`}
          aria-pressed={severityFilter === 'normal'}
          className="p-4 rounded-xl border-2 transition-all bg-white border-slate-200"
          style={
            severityFilter === 'normal'
              ? {
                  borderColor: 'var(--clinical-severity-normal-signal)',
                  backgroundColor: 'var(--clinical-severity-normal-wash)',
                }
              : {}
          }
        >
          <h3 className="sr-only">Stable Patients</h3>
          <div className="flex items-center gap-2 mb-1">
            <Activity
              className="w-5 h-5"
              style={{ color: 'var(--clinical-severity-normal-signal)' }}
              aria-hidden="true"
            />
            <span
              className="text-xs font-semibold uppercase"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Estável
            </span>
          </div>
          <div
            className="text-2xl font-bold"
            style={{ color: 'var(--clinical-severity-normal-on-surface)' }}
          >
            {normalCount}
          </div>
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
          style={{ color: 'var(--semantic-text-secondary)' }}
          aria-hidden="true"
        />
        <input
          type="text"
          ref={searchInputRef}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por nome, MPI ID ou leito..."
          aria-label="Buscar pacientes"
          className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Bed grid */}
      {filteredPatients && filteredPatients.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {filteredPatients.map((patient, index) => (
            <button
              key={patient.mpi_id}
              onClick={() => router.push(`/patient/${patient.mpi_id}`)}
              aria-label={`Patient ${patient.display_name}${patient.bed_id ? `, bed ${patient.bed_id}` : ''}`}
              className={`text-left rounded-r-xl border border-slate-200 p-4 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 border-l-4 ${focusedIndex === index ? 'ring-2 ring-blue-500' : ''}`}
              style={getSeverityStyle(patient.highest_alert_severity, 'left-accent')}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="min-w-0">
                  <div
                    className="font-semibold text-sm truncate"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {patient.display_name}
                  </div>
                  <div
                    className="text-xs mt-0.5"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    {patient.bed_id || 'Sem leito'}
                    {patient.unit && ` · ${patient.unit}`}
                  </div>
                </div>
                {patient.highest_alert_severity && (
                  <SeverityBadge
                    severity={getSeverityFromAlert(patient.highest_alert_severity)}
                    showLabel={false}
                  />
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex gap-4">
                  <div className="text-center">
                    <div
                      className="text-[10px] uppercase"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      <ClinicalTooltip term="MEWS">MEWS</ClinicalTooltip>
                    </div>
                    <div
                      className="text-sm font-bold"
                      style={{ color: getMEWSSeverity(patient.latest_mews).colorVar }}
                    >
                      {patient.latest_mews !== null
                        ? patient.latest_mews
                        : '--'}
                    </div>
                  </div>
                  <div className="text-center">
                    <div
                      className="text-[10px] uppercase"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      <ClinicalTooltip term="NEWS2">NEWS2</ClinicalTooltip>
                    </div>
                    <div
                      className="text-sm font-bold"
                      style={{
                        color:
                          patient.news2_risk === 'high'
                            ? 'var(--clinical-severity-critical-on-surface)'
                            : patient.news2_risk === 'medium'
                            ? 'var(--clinical-severity-watch-on-surface)'
                            : 'var(--semantic-text-primary)',
                      }}
                    >
                      {patient.latest_news2 !== null
                        ? patient.latest_news2
                        : '--'}
                    </div>
                  </div>
                </div>
                {patient.active_alerts_count > 0 && (
                  <span
                    className="text-white text-xs font-bold px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor:
                        patient.highest_alert_severity === 'critical'
                          ? 'var(--clinical-severity-critical-fill)'
                          : 'var(--clinical-severity-watch-fill)',
                    }}
                    aria-label={`${patient.active_alerts_count} active alert${patient.active_alerts_count !== 1 ? 's' : ''}`}
                  >
                    {patient.active_alerts_count}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      ) : (
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
            Nenhum paciente corresponde aos filtros
          </p>
          <button
            onClick={() => {
              setSearch('');
              setSeverityFilter(null);
            }}
            className="mt-2 text-sm underline"
            style={{ color: 'var(--clinical-status-attended-color)' }}
            aria-label="Limpar todos os filtros"
          >
            Limpar filtros
          </button>
        </div>
      )}
    </FullScreenLayout>
  );
}
