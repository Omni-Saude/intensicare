'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Activity,
  Bell,
  Users,
  TrendingUp,
  RefreshCw,
  Wifi,
  WifiOff,
} from 'lucide-react';
import Layout from '@/components/Layout';
import SeverityBadge, { ScoreDisplay, TrendBadge } from '@/components/SeverityBadge';
import ClinicalTooltip from '@/components/ClinicalTooltip';
import { fetchDashboard, type DashboardResponse, type PatientBedSummary } from '@/lib/api';
import { useRealtimeChannel, useConnectionStatus, type RealtimeEvent } from '@/lib/websocket';
import { getSeverityStyle, getSeverityFromAlert } from '@/lib/clinical-severity';

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUnit, setSelectedUnit] = useState<string | null>(null);

  // WebSocket connection status
  const wsStatus = useConnectionStatus();

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchDashboard(selectedUnit || undefined);
      setData(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, [selectedUnit]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  // Subscribe to realtime bed_grid updates via WebSocket (replaces polling)
  useRealtimeChannel('bed_grid.updated', useCallback((payload: unknown) => {
    const event = payload as RealtimeEvent<DashboardResponse>;
    if (event?.payload) {
      setData(event.payload as DashboardResponse);
      setLoading(false);
    } else {
      loadDashboard();
    }
  }, [loadDashboard]));

  // Also refresh when alerts change (may affect severity coloring)
  useRealtimeChannel('alert.raised', useCallback(() => {
    loadDashboard();
  }, [loadDashboard]));

  useRealtimeChannel('alert.updated', useCallback(() => {
    loadDashboard();
  }, [loadDashboard]));

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 style={{ color: 'var(--semantic-text-primary)' }} className="text-2xl font-bold">Painel Clínico</h1>
          <p style={{ color: 'var(--semantic-text-secondary)' }} className="text-sm mt-1">
            {data ? `${data.total} pacientes · ${data.active_alerts_total} alertas ativos` : 'Carregando...'}
            {/* WS status indicator */}
            <span className="inline-flex items-center gap-1 ml-3">
              {wsStatus === 'connected' ? (
                <Wifi className="w-3 h-3" style={{ color: 'var(--clinical-severity-normal-on-surface)' }} aria-hidden="true" />
              ) : (
                <WifiOff className="w-3 h-3" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
              )}
              <span className="text-[10px]" style={{ color: 'var(--semantic-text-secondary)' }}>
                {wsStatus === 'connected' ? 'Ao vivo' : wsStatus === 'connecting' ? '...' : 'Offline'}
              </span>
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div style={{ borderColor: 'var(--semantic-border-default)' }} className="flex items-center gap-2 bg-white rounded-lg border px-3 py-2">
            <Activity className="w-4 h-4" style={{ color: 'var(--semantic-text-secondary)' }} aria-hidden="true" />
            <select
              value={selectedUnit || ''}
              onChange={(e) => setSelectedUnit(e.target.value || null)}
              style={{ color: 'var(--semantic-text-primary)' }}
              className="text-sm bg-transparent border-none outline-none"
            >
              <option value="">Todas as Unidades</option>
              <option value="ICU-1">ICU-1</option>
              <option value="ICU-2">ICU-2</option>
              <option value="ER">ER</option>
            </select>
          </div>
          <button
            onClick={loadDashboard}
            disabled={loading}
            style={{ borderColor: 'var(--semantic-border-default)' }}
            className="p-2 rounded-lg border bg-white hover:bg-slate-50 disabled:opacity-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw style={{ color: 'var(--semantic-text-secondary)' }} className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Stats cards */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div style={{ borderColor: 'var(--semantic-border-default)' }} className="bg-white rounded-xl border p-4 shadow-sm">
            <div style={{ color: 'var(--semantic-text-secondary)' }} className="flex items-center gap-2 text-xs uppercase font-semibold mb-2">
              <Users className="w-4 h-4" aria-hidden="true" /> Pacientes
            </div>
            <div style={{ color: 'var(--semantic-text-primary)' }} className="text-2xl font-bold">{data.total}</div>
          </div>
          <div style={{ borderColor: 'var(--semantic-border-default)' }} className="bg-white rounded-xl border p-4 shadow-sm">
            <div style={{ color: 'var(--clinical-severity-critical-on-surface)' }} className="flex items-center gap-2 text-xs uppercase font-semibold mb-2">
              <Bell className="w-4 h-4" aria-hidden="true" /> Alertas Ativos
            </div>
            <div style={{ color: 'var(--clinical-severity-critical-on-surface)' }} className="text-2xl font-bold">{data.active_alerts_total}</div>
          </div>
          <div style={{ borderColor: 'var(--semantic-border-default)' }} className="bg-white rounded-xl border p-4 shadow-sm">
            <div style={{ color: 'var(--semantic-text-secondary)' }} className="flex items-center gap-2 text-xs uppercase font-semibold mb-2">
              <Activity className="w-4 h-4" aria-hidden="true" /> Críticos
            </div>
            <div style={{ color: 'var(--semantic-text-primary)' }} className="text-2xl font-bold">
              {data.patients.filter((p) => p.highest_alert_severity === 'critical').length}
            </div>
          </div>
          <div style={{ borderColor: 'var(--semantic-border-default)' }} className="bg-white rounded-xl border p-4 shadow-sm">
            <div style={{ color: 'var(--semantic-text-secondary)' }} className="flex items-center gap-2 text-xs uppercase font-semibold mb-2">
              <TrendingUp className="w-4 h-4" aria-hidden="true" /> MEWS ≥ 5
            </div>
            <div style={{ color: 'var(--semantic-text-primary)' }} className="text-2xl font-bold">
              {data.patients.filter((p) => (p.latest_mews ?? null) !== null && (p.latest_mews ?? 0) >= 5).length}
            </div>
          </div>
        </div>
      )}

      {/* Loading state — skeleton grid */}
      {loading && !data && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="rounded-xl border-2 p-4 animate-pulse"
              style={{ borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                    <div className="h-4 rounded w-24" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                  </div>
                  <div className="h-3 rounded w-16" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                </div>
                <div className="h-5 rounded-full w-8" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <div className="h-3 rounded w-10" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                  <div className="h-6 rounded w-8" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                </div>
                <div className="space-y-1">
                  <div className="h-3 rounded w-10" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                  <div className="h-6 rounded w-8" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          className="border rounded-xl p-4 mb-6"
        >
          <p className="font-medium">Failed to load dashboard</p>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={loadDashboard}
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
            className="mt-2 text-sm underline hover:no-underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Bed grid */}
      {data && data.patients.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {data.patients.map((patient: PatientBedSummary) => (
            <button
              key={patient.mpi_id}
              onClick={() => router.push(`/patient/${patient.mpi_id}`)}
              aria-label={`Patient ${patient.display_name}${patient.bed_id ? `, Bed ${patient.bed_id}` : ''}${patient.unit ? `, ${patient.unit}` : ''}`}
              style={getSeverityStyle(patient.highest_alert_severity)}
              className={`text-left rounded-xl border-2 p-4 hover:shadow-md transition-all focus:outline-none focus:ring-2 focus:ring-blue-500`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${
                        patient.highest_alert_severity === 'critical'
                          ? 'animate-pulse'
                          : ''
                      }`}
                      style={{
                        backgroundColor:
                          patient.highest_alert_severity === 'critical'
                            ? 'var(--clinical-severity-critical-signal)'
                            : patient.active_alerts_count > 0
                            ? 'var(--clinical-severity-watch-signal)'
                            : 'var(--clinical-severity-normal-signal)',
                      }}
                    />
                    <span style={{ color: 'var(--semantic-text-primary)' }} className="font-semibold text-sm truncate">
                      {patient.display_name}
                    </span>
                  </div>
                  <div style={{ color: 'var(--semantic-text-secondary)' }} className="text-xs mt-0.5">
                    {patient.bed_id ? `Bed ${patient.bed_id}` : 'No bed'}
                    {patient.unit && ` · ${patient.unit}`}
                  </div>
                </div>
                {patient.active_alerts_count > 0 && (
                  <span className="flex-shrink-0 bg-[var(--clinical-severity-critical-fill)] text-white text-xs font-bold px-2 py-0.5 rounded-full">
                    {patient.active_alerts_count}
                  </span>
                )}
              </div>

              {/* Scores */}
              <div className="grid grid-cols-2 gap-2">
                <ScoreDisplay
                  label="MEWS"
                  score={patient.latest_mews}
                  trend={patient.mews_trend}
                />
                <ScoreDisplay
                  label="NEWS2"
                  score={patient.latest_news2}
                  risk={patient.news2_risk}
                  trend={patient.news2_trend}
                />
              </div>

              {/* Last updated */}
              {patient.last_updated && (
                <div style={{ color: 'var(--semantic-text-secondary)' }} className="text-[10px] mt-3">
                  Updated: {new Date(patient.last_updated).toLocaleString()}
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Empty state */}
      {data && data.patients.length === 0 && (
        <div className="text-center py-20">
          <Activity className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--semantic-text-secondary)', opacity: 0.4 }} aria-hidden="true" />
          <p style={{ color: 'var(--semantic-text-secondary)' }} className="text-lg font-medium">No patients found</p>
          <p style={{ color: 'var(--semantic-text-secondary)' }} className="text-sm mt-1">
            {selectedUnit ? `No patients in unit "${selectedUnit}"` : 'No patients are currently admitted'}
          </p>
        </div>
      )}
    </Layout>
  );
}
