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
import { fetchDashboard, type DashboardResponse, type PatientBedSummary } from '@/lib/api';
import { useRealtimeChannel, useConnectionStatus, type RealtimeEvent } from '@/lib/websocket';

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

  const getSeverityClass = (severity: string | null) => {
    if (!severity) return 'border-slate-200 bg-white';
    switch (severity) {
      case 'critical':
        return 'border-red-300 bg-red-50/50';
      case 'warning':
        return 'border-yellow-300 bg-yellow-50/50';
      default:
        return 'border-blue-200 bg-blue-50/50';
    }
  };

  const getSeverityFromAlert = (severity: string | null): 'normal' | 'watch' | 'urgent' | 'critical' | 'info' => {
    if (!severity) return 'normal';
    switch (severity) {
      case 'critical': return 'critical';
      case 'warning': return 'watch';
      case 'info': return 'info';
      default: return 'normal';
    }
  };

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Clinical Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">
            {data ? `${data.total} patients · ${data.active_alerts_total} active alerts` : 'Loading...'}
            {/* WS status indicator */}
            <span className="inline-flex items-center gap-1 ml-3">
              {wsStatus === 'connected' ? (
                <Wifi className="w-3 h-3 text-green-500" />
              ) : (
                <WifiOff className="w-3 h-3 text-slate-400" />
              )}
              <span className="text-[10px] text-slate-400">
                {wsStatus === 'connected' ? 'Live' : wsStatus === 'connecting' ? '...' : 'Offline'}
              </span>
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white rounded-lg border border-slate-200 px-3 py-2">
            <Activity className="w-4 h-4 text-slate-400" />
            <select
              value={selectedUnit || ''}
              onChange={(e) => setSelectedUnit(e.target.value || null)}
              className="text-sm bg-transparent border-none outline-none text-slate-700"
            >
              <option value="">All Units</option>
              <option value="ICU-1">ICU-1</option>
              <option value="ICU-2">ICU-2</option>
              <option value="ER">ER</option>
            </select>
          </div>
          <button
            onClick={loadDashboard}
            disabled={loading}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Stats cards */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 text-xs uppercase font-semibold mb-2">
              <Users className="w-4 h-4" /> Patients
            </div>
            <div className="text-2xl font-bold text-slate-800">{data.total}</div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-red-400 text-xs uppercase font-semibold mb-2">
              <Bell className="w-4 h-4" /> Active Alerts
            </div>
            <div className="text-2xl font-bold text-red-600">{data.active_alerts_total}</div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 text-xs uppercase font-semibold mb-2">
              <Activity className="w-4 h-4" /> Critical
            </div>
            <div className="text-2xl font-bold text-slate-800">
              {data.patients.filter((p) => p.highest_alert_severity === 'critical').length}
            </div>
          </div>
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 text-xs uppercase font-semibold mb-2">
              <TrendingUp className="w-4 h-4" /> MEWS ≥ 5
            </div>
            <div className="text-2xl font-bold text-slate-800">
              {data.patients.filter((p) => (p.latest_mews || 0) >= 5).length}
            </div>
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading && !data && (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3 text-slate-400">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Loading dashboard...</span>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 mb-6">
          <p className="font-medium">Failed to load dashboard</p>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={loadDashboard}
            className="mt-2 text-sm text-red-600 underline hover:no-underline"
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
              className={`text-left rounded-xl border-2 p-4 hover:shadow-md transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 ${getSeverityClass(
                patient.highest_alert_severity
              )}`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${
                        patient.highest_alert_severity === 'critical'
                          ? 'bg-red-500 animate-pulse'
                          : patient.active_alerts_count > 0
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                    />
                    <span className="font-semibold text-slate-800 text-sm truncate">
                      {patient.display_name}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    {patient.bed_id ? `Bed ${patient.bed_id}` : 'No bed'}
                    {patient.unit && ` · ${patient.unit}`}
                  </div>
                </div>
                {patient.active_alerts_count > 0 && (
                  <span className="flex-shrink-0 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
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
                <div className="text-[10px] text-slate-400 mt-3">
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
          <Activity className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 text-lg font-medium">No patients found</p>
          <p className="text-slate-400 text-sm mt-1">
            {selectedUnit ? `No patients in unit "${selectedUnit}"` : 'No patients are currently admitted'}
          </p>
        </div>
      )}
    </Layout>
  );
}
