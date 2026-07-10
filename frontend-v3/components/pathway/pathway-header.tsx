'use client';

import type { SeverityLevel } from '@/lib/api';
import { cn } from '@/lib/utils';
import { SeverityBadge } from '@/components/alerts/severity-badge';
import {
  GitBranch,
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowLeft,
} from 'lucide-react';
import Link from 'next/link';

// ---------------------------------------------------------------------------
// Trend helpers
// ---------------------------------------------------------------------------

const TREND_CONFIG: Record<string, { Icon: typeof TrendingUp; label: string; colorVar: string }> = {
  improving: {
    Icon: TrendingUp,
    label: 'Melhorando',
    colorVar: 'var(--severity-normal)',
  },
  worsening: {
    Icon: TrendingDown,
    label: 'Piorando',
    colorVar: 'var(--severity-critical)',
  },
  stable: {
    Icon: Minus,
    label: 'Estável',
    colorVar: 'var(--severity-watch)',
  },
  none: {
    Icon: Minus,
    label: 'Sem tendência',
    colorVar: 'var(--text-secondary)',
  },
};

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface PathwayHeaderProps {
  pathwayName: string;
  patientName: string;
  mpiId: string;
  currentState: string;
  severity: SeverityLevel;
  trend: 'improving' | 'stable' | 'worsening' | 'none';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function PathwayHeader({
  pathwayName,
  patientName,
  mpiId,
  currentState,
  severity,
  trend,
}: PathwayHeaderProps) {
  const trendInfo = TREND_CONFIG[trend] ?? TREND_CONFIG.none;
  const TrendIcon = trendInfo.Icon;

  return (
    <header
      className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-4 sm:p-5"
      aria-label={`Trilha ${pathwayName} do paciente ${patientName}`}
    >
      {/* Back link */}
      <Link
        href={`/patient/${encodeURIComponent(mpiId)}`}
        className="inline-flex items-center gap-1.5 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors mb-3"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
        Voltar para o paciente
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        {/* Left: pathway name + patient */}
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <GitBranch className="h-5 w-5 text-[var(--text-secondary)] shrink-0" aria-hidden="true" />
            <h1 className="text-xl font-bold text-[var(--text-primary)] truncate">
              {pathwayName}
            </h1>
          </div>
          <p className="text-sm text-[var(--text-secondary)] mt-0.5">
            Paciente: <span className="font-medium text-[var(--text-primary)]">{patientName}</span>
            {' — '}
            <span className="font-medium text-[var(--text-primary)]">{currentState}</span>
          </p>
        </div>

        {/* Right: severity badge + trend */}
        <div className="flex items-center gap-3 shrink-0">
          {/* Trend arrow */}
          <span
            className="inline-flex items-center gap-1 text-xs font-medium"
            style={{ color: trendInfo.colorVar }}
            aria-label={`Tendência: ${trendInfo.label}`}
          >
            <TrendIcon className="h-4 w-4" aria-hidden="true" />
            {trendInfo.label}
          </span>

          {/* Severity badge (reuse existing component) */}
          <SeverityBadge severity={severity} />
        </div>
      </div>
    </header>
  );
}
