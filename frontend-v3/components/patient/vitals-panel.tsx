'use client';

import type { VitalRecord, SeverityLevel } from '@/lib/api';
import { severityColor } from './severity-glow';
import { cn } from '@/lib/utils';
import { computeStaleness, isSameDay } from '@/lib/vitals-staleness';
import { Heart, Activity, Thermometer, Wind, Droplets, AlertTriangle } from 'lucide-react';

interface VitalReadoutProps {
  vital: VitalRecord;
  className?: string;
}

const VITAL_META: Record<string, { label: string; icon: React.ComponentType<{ className?: string }> }> = {
  HR: { label: 'Freq. Cardíaca', icon: Heart },
  BP_SYS: { label: 'Pressão Sistólica', icon: Activity },
  BP_DIA: { label: 'Pressão Diastólica', icon: Activity },
  SpO2: { label: 'Saturação O₂', icon: Droplets },
  TEMP: { label: 'Temperatura', icon: Thermometer },
  RR: { label: 'Freq. Respiratória', icon: Wind },
};

const VITAL_UNIT_OVERRIDE: Record<string, string> = {
  TEMP: '°C',
  RR: 'rpm',
};

export function VitalReadout({ vital, className }: VitalReadoutProps) {
  const meta = VITAL_META[vital.name] ?? { label: vital.name, icon: Activity };
  const unit = VITAL_UNIT_OVERRIDE[vital.name] ?? vital.unit;
  const Icon = meta.icon;
  const sev = vital.severity ?? 'normal';
  const color = severityColor(sev);

  // BUG-F3-01: when the reading isn't from today (e.g. served by the
  // backend's "N most recent" fallback because the 24h window was empty),
  // an HH:MM-only timestamp is indistinguishable from a fresh reading. Add
  // the date and tint the timestamp so an old reading reads as old.
  const age = computeStaleness(vital.measured_at);
  const showDate = !isSameDay(vital.measured_at);
  const timeColor = age && age.tier !== 'fresh' ? age.color : 'var(--text-secondary)';
  const timeLabel = showDate
    ? `${new Date(vital.measured_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })} ${new Date(vital.measured_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
    : new Date(vital.measured_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

  return (
    <div
      className={cn(
        'flex flex-col gap-1 rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-4 transition-shadow',
        sev === 'critical' && 'severity-critical-pulse',
        className,
      )}
      style={{ borderLeftColor: color, borderLeftWidth: '3px' }}
      role="status"
      aria-label={`${meta.label}: ${vital.value} ${unit}`}
    >
      <div className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
        <Icon className="h-3.5 w-3.5" aria-hidden="true" />
        <span>{meta.label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span
          className="text-3xl font-bold tabular-nums leading-tight"
          style={{ color }}
        >
          {vital.value}
        </span>
        <span className="text-xs text-[var(--text-secondary)]">{unit}</span>
      </div>
      <time
        className={cn('text-[10px]', showDate && 'font-semibold')}
        style={{ color: timeColor }}
        dateTime={vital.measured_at}
      >
        {timeLabel}
      </time>
    </div>
  );
}

// ---------- Panel ----------

interface VitalsPanelProps {
  vitals: VitalRecord[];
  isLoading?: boolean;
  error?: string | null;
}

// BUG-F3-01: when the 24h window has no readings, the backend falls back to
// the N most recent vitals — which may be hours or days old. The tiles alone
// (HH:MM only) don't communicate that; find the freshest reading among the
// batch and, if even that is stale, surface a proeminent banner above the
// grid so an intensivist can't mistake old data for current.
function latestMeasuredAt(vitals: VitalRecord[]): string | null {
  if (vitals.length === 0) return null;
  return vitals.reduce(
    (latest, v) => (new Date(v.measured_at) > new Date(latest) ? v.measured_at : latest),
    vitals[0].measured_at,
  );
}

export function VitalsPanel({ vitals, isLoading, error }: VitalsPanelProps) {
  const latestAt = latestMeasuredAt(vitals);
  const panelStaleness = latestAt ? computeStaleness(latestAt) : null;
  const isStale = panelStaleness?.tier === 'stale';

  return (
    <section aria-label="Sinais vitais" className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        Sinais Vitais
      </h2>

      {isStale && panelStaleness && (
        <div
          role="alert"
          className="flex items-start gap-2 rounded-lg border p-3 text-sm font-semibold"
          style={{
            borderColor: panelStaleness.color,
            backgroundColor: panelStaleness.washColor,
            color: panelStaleness.color,
          }}
        >
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" aria-hidden="true" />
          <span>
            {panelStaleness.longLabel}. Estes não são os sinais vitais mais recentes das
            últimas 24h — confirme a data antes de decidir.
          </span>
        </div>
      )}

      {isLoading && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-[110px] animate-pulse rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]"
              aria-hidden="true"
            />
          ))}
        </div>
      )}

      {error && (
        <div
          className="rounded-lg border border-[var(--severity-critical)] bg-[var(--severity-critical-wash)] p-4 text-sm text-[var(--severity-critical)]"
          role="alert"
        >
          Erro ao carregar sinais vitais: {error}
        </div>
      )}

      {!isLoading && !error && vitals.length === 0 && (
        <div className="rounded-lg border border-dashed border-[var(--border-default)] bg-[var(--surface-raised)] p-6 text-center text-sm text-[var(--text-secondary)]">
          Nenhum sinal vital registrado para este paciente.
        </div>
      )}

      {!isLoading && !error && vitals.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {vitals.map((v, i) => (
            <VitalReadout key={`${v.name}-${v.measured_at}-${i}`} vital={v} />
          ))}
        </div>
      )}
    </section>
  );
}
