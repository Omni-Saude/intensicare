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
import ClinicalTooltip from '@/components/ClinicalTooltip';
import SeverityBadge from '@/components/SeverityBadge';
import AlertCard from '@/components/AlertCard';
import { fetchPatientDetail, type PatientDetailResponse, type ScoreHistoryPoint, type VitalsHistoryPoint } from '@/lib/api';
import { useRealtimeChannel, useConnectionStatus, type RealtimeEvent } from '@/lib/websocket';
import { getScoreColor } from '@/lib/clinical-severity';
import { useThreshold, severityToColorVar, severityToWashVar } from '@/lib/thresholds/useThreshold';
import type { ThresholdSeverity } from '@/lib/thresholds/types';

export default function PatientTimelinePage() {
  const params = useParams();
  const router = useRouter();
  const mpiId = params.id as string;

  const [data, setData] = useState<PatientDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection status
  const wsStatus = useConnectionStatus();

  // Threshold service — fetches reference ranges with 5‑min cache + fallback
  const { getVitalSeverity, getScoreBand } = useThreshold();

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

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6 animate-pulse">
          {/* Header skeleton */}
          <div className="mb-6">
            <div className="h-4 rounded w-16 mb-3" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
            <div className="space-y-2">
              <div className="h-8 rounded w-48" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
              <div className="h-4 rounded w-72" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
            </div>
          </div>
          {/* Vitals card skeleton */}
          <div className="rounded-xl border p-6" style={{ borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' }}>
            <div className="h-4 rounded w-28 mb-4" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {Array.from({ length: 7 }).map((_, i) => (
                <div key={i} className="p-3 rounded-lg" style={{ backgroundColor: 'var(--semantic-surface-canvas)' }}>
                  <div className="h-3 rounded w-16 mb-2" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                  <div className="h-6 rounded w-12" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                </div>
              ))}
            </div>
          </div>
          {/* Score history skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {Array.from({ length: 2 }).map((_, i) => (
              <div key={i} className="rounded-xl border p-6" style={{ borderColor: 'var(--semantic-border-default)', backgroundColor: 'var(--semantic-surface-raised)' }}>
                <div className="h-4 rounded w-28 mb-4" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                <div className="space-y-3">
                  {Array.from({ length: 4 }).map((_, j) => (
                    <div key={j} className="flex items-center justify-between py-2">
                      <div className="h-3 rounded w-24" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                      <div className="h-6 rounded w-8" style={{ backgroundColor: 'var(--semantic-border-default)' }} />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
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
          <h2 style={{ color: 'var(--clinical-severity-critical-on-surface)' }} className="font-semibold">Erro</h2>
          <p style={{ color: 'var(--clinical-severity-critical-on-surface)' }} className="text-sm mt-1">{error || 'Paciente não encontrado'}</p>
          <div className="flex items-center gap-3 mt-3">
            <button
              onClick={loadData}
              style={{
                color: 'var(--semantic-text-primary)',
                backgroundColor: 'var(--semantic-surface-raised)',
                borderColor: 'var(--semantic-border-default)',
              }}
              className="px-4 py-2 rounded-lg border text-sm font-medium hover:bg-white transition-colors"
            >
              Tentar novamente
            </button>
            <button
              onClick={() => router.back()}
              style={{ color: 'var(--clinical-severity-critical-on-surface)' }}
              className="text-sm underline"
            >
              Voltar
            </button>
          </div>
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
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          Voltar
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
                  <Wifi className="w-3 h-3" style={{ color: 'var(--clinical-severity-normal-on-surface)' }} aria-hidden="true" />
                ) : (
                  <WifiOff className="w-3 h-3 text-slate-400" aria-hidden="true" />
                )}
                <span className="text-[10px] text-slate-400">
                  {wsStatus === 'connected' ? 'Ao vivo' : wsStatus === 'connecting' ? '...' : 'Offline'}
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
                <Bell className="w-4 h-4" aria-hidden="true" />
                {data.active_alerts.length} alerta{data.active_alerts.length !== 1 ? 's' : ''} ativo{data.active_alerts.length !== 1 ? 's' : ''}
              </span>
            )}
            <button
              onClick={loadData}
              disabled={loading}
              style={{ borderColor: 'var(--semantic-border-default)' }}
              className="p-2 rounded-lg border bg-white hover:bg-slate-50"
            >
              <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
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
            Sinais Vitais
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <VitalItem
              icon={<Heart className="w-4 h-4" aria-hidden="true" />}
              label="Frequência Cardíaca"
              value={latestVitals.heart_rate}
              unit="bpm"
              vitalName="heart_rate"
              getVitalSeverity={getVitalSeverity}
            />
            <VitalItem
              icon={<Activity className="w-4 h-4" aria-hidden="true" />}
              label="Pressão Arterial"
              value={latestVitals.systolic_bp}
              suffix={latestVitals.diastolic_bp ? ` / ${latestVitals.diastolic_bp}` : ''}
              unit="mmHg"
              vitalName="systolic_bp"
              getVitalSeverity={getVitalSeverity}
            />
            <VitalItem
              icon={<Thermometer className="w-4 h-4" aria-hidden="true" />}
              label="Temperatura"
              value={latestVitals.temperature}
              unit="°C"
              vitalName="temperature"
              getVitalSeverity={getVitalSeverity}
            />
            <VitalItem
              icon={<Activity className="w-4 h-4" aria-hidden="true" />}
              label="SpO₂"
              value={latestVitals.spo2}
              unit="%"
              vitalName="spo2"
              getVitalSeverity={getVitalSeverity}
            />
            <VitalItem
              icon={<Brain className="w-4 h-4" aria-hidden="true" />}
              label="Frequência Respiratória"
              value={latestVitals.respiratory_rate}
              unit="/min"
              vitalName="respiratory_rate"
              getVitalSeverity={getVitalSeverity}
            />
            <VitalItem
              icon={<Brain className="w-4 h-4" aria-hidden="true" />}
              label="AVPU"
              value={latestVitals.avpu}
              isText
            />
            <VitalItem
              icon={<Activity className="w-4 h-4" aria-hidden="true" />}
              label="Supp. O₂"
              value={latestVitals.supplemental_o2 ? 'Sim' : 'Não'}
              isText
            />
          </div>
          <div className="text-xs text-slate-400 mt-4">
            Registrado: {formatDate(latestVitals.recorded_at)}
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
            <ClinicalTooltip term="MEWS">MEWS</ClinicalTooltip> Histórico
          </h3>
          {data.mews_history.length === 0 ? (
            <p className="text-sm text-slate-400">Nenhum dado MEWS disponível</p>
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
            <ClinicalTooltip term="NEWS2">NEWS2</ClinicalTooltip> Histórico
          </h3>
          {data.news2_history.length === 0 ? (
            <p className="text-sm text-slate-400">Nenhum dado NEWS2 disponível</p>
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
            Alertas Ativos
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
            Linha do Tempo de Sinais Vitais (24h)
          </h3>
          {/* Screen-reader accessible data table */}
          <div className="sr-only" role="region" aria-label="Tabela de dados vitais">
            <table>
              <caption>Histórico de Sinais Vitais (24h)</caption>
              <thead>
                <tr>
                  <th scope="col">Horário</th>
                  <th scope="col">Frequência Cardíaca (bpm)</th>
                  <th scope="col">Pressão Arterial (mmHg)</th>
                  <th scope="col">SpO₂ (%)</th>
                  <th scope="col">Temperatura (°C)</th>
                  <th scope="col">Frequência Respiratória (/min)</th>
                </tr>
              </thead>
              <tbody>
                {data.vitals_history.map((point, idx) => (
                  <tr key={idx}>
                    <td>{formatDate(point.recorded_at)}</td>
                    <td>{point.heart_rate ?? '--'}</td>
                    <td>{point.systolic_bp ?? '--'}/{point.diastolic_bp ?? '--'}</td>
                    <td>{point.spo2 ?? '--'}</td>
                    <td>{point.temperature ?? '--'}</td>
                    <td>{point.respiratory_rate ?? '--'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
                    <span
                      style={{
                        color: severityToColorVar(getVitalSeverity(point.heart_rate, 'heart_rate')),
                        fontWeight: getVitalSeverity(point.heart_rate, 'heart_rate') !== 'normal' ? 'bold' : undefined,
                      }}
                    >
                      HR: {point.heart_rate}
                    </span>
                  )}
                  {point.systolic_bp !== null && (
                    <span
                      style={{
                        color: severityToColorVar(getVitalSeverity(point.systolic_bp, 'systolic_bp')),
                        fontWeight: getVitalSeverity(point.systolic_bp, 'systolic_bp') !== 'normal' ? 'bold' : undefined,
                      }}
                    >
                      BP: {point.systolic_bp}/{point.diastolic_bp || '--'}
                    </span>
                  )}
                  {point.spo2 !== null && (
                    <span
                      style={{
                        color: severityToColorVar(getVitalSeverity(point.spo2, 'spo2')),
                        fontWeight: getVitalSeverity(point.spo2, 'spo2') !== 'normal' ? 'bold' : undefined,
                      }}
                    >
                      SpO₂: {point.spo2}%
                    </span>
                  )}
                  {point.temperature !== null && (
                    <span
                      style={{
                        color: severityToColorVar(getVitalSeverity(point.temperature, 'temperature')),
                        fontWeight: getVitalSeverity(point.temperature, 'temperature') !== 'normal' ? 'bold' : undefined,
                      }}
                    >
                      Temp: {point.temperature}°C
                    </span>
                  )}
                  {point.respiratory_rate !== null && (
                    <span
                      style={{
                        color: severityToColorVar(getVitalSeverity(point.respiratory_rate, 'respiratory_rate')),
                        fontWeight: getVitalSeverity(point.respiratory_rate, 'respiratory_rate') !== 'normal' ? 'bold' : undefined,
                      }}
                    >
                      RR: {point.respiratory_rate}
                    </span>
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
  vitalName,
  getVitalSeverity,
  isText,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string | null;
  unit?: string;
  suffix?: string;
  vitalName?: string;
  getVitalSeverity?: (value: number, vitalName: string) => ThresholdSeverity;
  isText?: boolean;
}) {
  const severity: ThresholdSeverity =
    !isText && typeof value === 'number' && vitalName && getVitalSeverity
      ? getVitalSeverity(value, vitalName)
      : 'normal';

  const isAbnormal = severity !== 'normal';

  return (
    <div
      style={{
        backgroundColor: isAbnormal
          ? severityToWashVar(severity)
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
          color: isAbnormal
            ? severityToColorVar(severity)
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
  getScoreColor: (type: 'mews' | 'news2' | 'sofa', value: number) => string;
  formatDate: (iso: string) => string;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
      <span className="text-xs text-slate-400">{formatDate(point.calculated_at)}</span>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold" style={{ color: getScoreColor(point.score_type as 'mews' | 'news2' | 'sofa', point.score_value) }}>
          {point.score_value}
        </span>
        {point.trend === 'increasing' && <TrendingUp className="w-3.5 h-3.5 text-[var(--clinical-severity-critical-on-surface)]" aria-hidden="true" />}
        {point.trend === 'decreasing' && <TrendingDown className="w-3.5 h-3.5 text-[var(--clinical-severity-normal-on-surface)]" aria-hidden="true" />}
        {point.trend === 'stable' && <span className="text-xs text-slate-400">→</span>}
      </div>
    </div>
  );
}
