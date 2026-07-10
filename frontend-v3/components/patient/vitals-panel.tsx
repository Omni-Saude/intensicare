'use client';

import type { VitalRecord, SeverityLevel } from '@/lib/api';
import { severityColor } from './severity-glow';
import { cn } from '@/lib/utils';
import { Heart, Activity, Thermometer, Wind, Droplets } from 'lucide-react';

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
        className="text-[10px] text-[var(--text-secondary)]"
        dateTime={vital.measured_at}
      >
        {new Date(vital.measured_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
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

export function VitalsPanel({ vitals, isLoading, error }: VitalsPanelProps) {
  return (
    <section aria-label="Sinais vitais" className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        Sinais Vitais
      </h2>

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
