'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  RefreshCw,
  Heart,
  Thermometer,
  Activity,
  Brain,
  TrendingUp,
  TrendingDown,
  Bell,
  AlertTriangle,
  Wifi,
  WifiOff,
} from 'lucide-react';
import Layout from '@/components/Layout';
import SeverityBadge from '@/components/SeverityBadge';
import AlertCard from '@/components/AlertCard';
import { fetchPatientDetail, type PatientDetailResponse, type ScoreHistoryPoint, type VitalsHistoryPoint } from '@/lib/api';
import { useRealtimeChannel, useConnectionStatus, type RealtimeEvent } from '@/lib/websocket';

export default function PatientTimelinePage() {
  const params = useParams();
  const router = useRouter();
  const mpiId = params.id as string;

  const [data, setData] = useState<PatientDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection status
  const wsStatus = useConnectionStatus();

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchPatientDetail(mpiId);
      setData(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load patient data');
    } finally {
      setLoading(false);
    }
  }, [mpiId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Subscribe to realtime vitals updates via WebSocket (replaces polling)
  useRealtimeChannel('vitals.updated', useCallback((payload: unknown) => {
    const event = payload as RealtimeEvent<{ mpi_id: string }>;
    // Only refresh if the update is for this patient
    if (event?.payload?.mpi_id === mpiId) {
      loadData();
    }
  }, [loadData, mpiId]));

  // Also refresh when new alerts are raised for this patient
  useRealtimeChannel('alert.raised', useCallback(() => {
    loadData();
  }, [loadData]));

  useRealtimeChannel('alert.updated', useCallback(() => {
    loadData();
  }, [loadData]));

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getScoreColor = (type: string, value: number) => {
    if (type === 'mews') {
      if (value >= 5) return 'var(--clinical-severity-critical-on-surface)';
      if (value >= 3) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';
    }
    if (type === 'news2') {
      if (value >= 7) return 'var(--clinical-severity-critical-on-surface)';
      if (value >= 5) return 'var(--clinical-severity-watch-on-surface)';
      return 'var(--clinical-severity-normal-on-surface)';
    }
    return 'var(--semantic-text-secondary)';
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-20">
          <RefreshCw className="w-6 h-6 text-slate-400 animate-spin" />
        </div>
      </Layout>
    );
  }

  if (error || !data) {
    return (
      <Layout>
        <div
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-wash)',
          }}
          className="border rounded-xl p-6"
        >
          <h2 style={{ color: 'var(--clinical-severity-critical-on-surface)' }} className="font-semibold">Error</h2>
          <p style={{ color: 'var(--clinical-severity-critical-on-surface)' }} className="text-sm mt-1">{error || 'Patient not found'}</p>
          <button
            onClick={() => router.back()}
            style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
            className="mt-3 text-sm underline"
          >
            Go back
          </button>
        </div>
      </Layout>
    );
  }

  const latestVitals = data.vitals_history[data.vitals_history.length - 1];

  return (
    <Layout>
      {/* Header with back button */}
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-3 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">{data.display_name}</h1>
            <p className="text-slate-500 text-sm mt-1">
              MPI: {data.mpi_id}
              {data.bed_id && ` · Bed ${data.bed_id}`}
              {data.unit && ` · ${data.unit}`}
              {/* WS indicator */}
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
          <div className="flex items-center gap-2">
            {data.active_alerts.length > 0 && (
              <span
                style={{
                  backgroundColor: 'var(--clinical-severity-critical-wash)',
                  color: 'var(--clinical-severity-critical-on-surface)',
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium"
              >
                <Bell className="w-4 h-4" />
                {data.active_alerts.length} active alert{data.active_alerts.length !== 1 ? 's' : ''}
              </span>
            )}
            <button
              onClick={loadData}
              disabled={loading}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="p-2 rounded-lg border bg-white hover:bg-slate-50"
            >
              <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Latest vitals card */}
      {latestVitals && (
        <div
          style={{ borderColor: 'var(--semantic-border-default)' }}
          className="bg-white rounded-xl border p-6 shadow-sm mb-6"
        >
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
            Latest Vitals
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <VitalItem
              icon={<Heart className="w-4 h-4" />}
              label="Heart Rate"
              value={latestVitals.heart_rate}
              unit="bpm"
              warnHigh={100}
              warnLow={60}
            />
            <VitalItem
              icon={<Activity className="w-4 h-4" />}
              label="Blood Pressure"
              value={latestVitals.systolic_bp}
              suffix={latestVitals.diastolic_bp ? ` / ${latestVitals.diastolic_bp}` : ''}
              unit="mmHg"
            />
            <VitalItem
              icon={<Thermometer className="w-4 h-4" />}
              label="Temperature"
              value={latestVitals.temperature}
              unit="°C"
              warnHigh={38}
            />
            <VitalItem
              icon={<Activity className="w-4 h-4" />}
              label="SpO₂"
              value={latestVitals.spo2}
              unit="%"
              warnLow={92}
            />
            <VitalItem
              icon={<Brain className="w-4 h-4" />}
              label="Respiratory Rate"
              value={latestVitals.respiratory_rate}
              unit="/min"
              warnHigh={20}
              warnLow={12}
            />
            <VitalItem
              icon={<Brain className="w-4 h-4" />}
              label="AVPU"
              value={latestVitals.avpu}
              isText
            />
            <VitalItem
              icon={<Activity className="w-4 h-4" />}
              label="Supp. O₂"
              value={latestVitals.supplemental_o2 ? 'Yes' : 'No'}
              isText
            />
          </div>
          <div className="text-xs text-slate-400 mt-4">
            Recorded: {formatDate(latestVitals.recorded_at)}
          </div>
        </div>
      )}

      {/* Score timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* MEWS History */}
        <div
          style={{ borderColor: 'var(--semantic-border-default)' }}
          className="bg-white rounded-xl border p-6 shadow-sm"
        >
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
            MEWS History
          </h3>
          {data.mews_history.length === 0 ? (
            <p className="text-sm text-slate-400">No MEWS data available</p>
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {data.mews_history.map((point, idx) => (
                <ScoreTimelineRow
                  key={idx}
                  point={point}
                  getScoreColor={getScoreColor}
                  formatDate={formatDate}
                />
              ))}
            </div>
          )}
        </div>

        {/* NEWS2 History */}
        <div
          style={{ borderColor: 'var(--semantic-border-default)' }}
          className="bg-white rounded-xl border p-6 shadow-sm"
        >
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
            NEWS2 History
          </h3>
          {data.news2_history.length === 0 ? (
            <p className="text-sm text-slate-400">No NEWS2 data available</p>
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {data.news2_history.map((point, idx) => (
                <ScoreTimelineRow
                  key={idx}
                  point={point}
                  getScoreColor={getScoreColor}
                  formatDate={formatDate}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Active Alerts */}
      {data.active_alerts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
            Active Alerts
          </h3>
          <div className="space-y-4">
            {data.active_alerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} onUpdate={loadData} />
            ))}
          </div>
        </div>
      )}

      {/* Vitals Timeline */}
      {data.vitals_history.length > 0 && (
        <div
          style={{ borderColor: 'var(--semantic-border-default)' }}
          className="bg-white rounded-xl border p-6 shadow-sm"
        >
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
            Vitals Timeline (24h)
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.vitals_history.map((point, idx) => (
              <div
                key={idx}
                className="flex items-center gap-4 py-2 border-b border-slate-100 last:border-0"
              >
                <span className="text-xs text-slate-400 w-20 flex-shrink-0">
                  {formatDate(point.recorded_at)}
                </span>
                <div className="flex gap-3 text-xs">
                  {point.heart_rate !== null && (
                    <span className="text-slate-600">HR: {point.heart_rate}</span>
                  )}
                  {point.systolic_bp !== null && (
                    <span className="text-slate-600">
                      BP: {point.systolic_bp}/{point.diastolic_bp || '--'}
                    </span>
                  )}
                  {point.spo2 !== null && (
                    <span
                      style={{
                        color: (point.spo2 || 100) < 92 ? 'var(--clinical-severity-critical-on-surface)' : undefined,
                        fontWeight: (point.spo2 || 100) < 92 ? 'bold' : undefined,
                      }}
                    >
                      SpO₂: {point.spo2}%
                    </span>
                  )}
                  {point.temperature !== null && (
                    <span
                      style={{
                        color: (point.temperature || 0) > 38 ? 'var(--clinical-severity-critical-on-surface)' : undefined,
                        fontWeight: (point.temperature || 0) > 38 ? 'bold' : undefined,
                      }}
                    >
                      Temp: {point.temperature}°C
                    </span>
                  )}
                  {point.respiratory_rate !== null && (
                    <span className="text-slate-600">RR: {point.respiratory_rate}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}

// Sub-components

function VitalItem({
  icon,
  label,
  value,
  unit,
  suffix,
  warnHigh,
  warnLow,
  isText,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string | null;
  unit?: string;
  suffix?: string;
  warnHigh?: number;
  warnLow?: number;
  isText?: boolean;
}) {
  const isWarn =
    !isText &&
    typeof value === 'number' &&
    ((warnHigh !== undefined && value >= warnHigh) ||
      (warnLow !== undefined && value <= warnLow));

  return (
    <div
      style={{
        backgroundColor: isWarn
          ? 'var(--clinical-severity-critical-wash)'
          : 'var(--semantic-surface-canvas)',
      }}
      className="p-3 rounded-lg"
    >
      <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
        {icon}
        {label}
      </div>
      <div
        style={{
          color: isWarn
            ? 'var(--clinical-severity-critical-on-surface)'
            : 'var(--semantic-text-primary)',
        }}
        className="text-lg font-bold"
      >
        {value !== null && value !== undefined ? (
          <>
            {value}
            {suffix && <span className="text-sm font-normal">{suffix}</span>}
            {unit && <span className="text-sm font-normal text-slate-400 ml-0.5">{unit}</span>}
          </>
        ) : (
          <span className="text-slate-300">--</span>
        )}
      </div>
    </div>
  );
}

function ScoreTimelineRow({
  point,
  getScoreColor,
  formatDate,
}: {
  point: ScoreHistoryPoint;
  getScoreColor: (type: string, value: number) => string;
  formatDate: (iso: string) => string;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
      <span className="text-xs text-slate-400">{formatDate(point.calculated_at)}</span>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold" style={{ color: getScoreColor(point.score_type, point.score_value) }}>
          {point.score_value}
        </span>
        {point.trend === 'increasing' && <TrendingUp className="w-3.5 h-3.5 text-red-500" />}
        {point.trend === 'decreasing' && <TrendingDown className="w-3.5 h-3.5 text-green-500" />}
        {point.trend === 'stable' && <span className="text-xs text-slate-400">→</span>}
      </div>
    </div>
  );
}
