'use client';

import type { PatientBedSummary, SeverityLevel } from '@/lib/api';
import { SeverityDot } from './severity-dot';
import { ScorePair } from './score-pair';
import { PathwayBadges } from './pathway-badges';
import { VitalsInline } from './vitals-inline';
import { cn } from '@/lib/utils';

const SEVERITY_BORDER: Record<SeverityLevel, string> = {
  normal: 'var(--severity-normal)',
  watch: 'var(--severity-watch)',
  urgent: 'var(--severity-urgent)',
  critical: 'var(--severity-critical)',
};

interface BedCardProps {
  patient: PatientBedSummary;
  onClick: () => void;
}

function formatStaleness(lastVitalAt: string): { label: string; color: string } | null {
  const diffMs = Date.now() - new Date(lastVitalAt).getTime();
  const diffMin = Math.floor(diffMs / 60_000);

  if (diffMin < 0) return null;

  let color: string;
  if (diffMin < 30) {
    color = 'var(--severity-normal)';
  } else if (diffMin < 60) {
    color = 'var(--severity-watch)';
  } else {
    color = 'var(--severity-critical)';
  }

  const label = diffMin < 60
    ? `há ${diffMin} min`
    : `há ${(diffMin / 60).toFixed(1)}h`;

  return { label, color };
}

export function BedCard({ patient, onClick }: BedCardProps) {
  const {
    patient_name,
    bed,
    unit,
    severity,
    mews,
    news2,
    active_pathways,
    vitals,
    last_vital_at,
  } = patient;

  const borderColor = SEVERITY_BORDER[severity];
  const staleness = last_vital_at ? formatStaleness(last_vital_at) : null;

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Paciente ${patient_name}, Leito ${bed}, ${unit}${mews != null ? `, MEWS ${mews}` : ''}`}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      className={cn(
        'flex flex-col gap-3 p-4 rounded-[var(--radius-lg)] cursor-pointer',
        'transition-colors hover:border-opacity-80',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
      )}
      style={{
        backgroundColor: 'var(--surface-raised)',
        borderLeftWidth: '4px',
        borderLeftStyle: 'solid',
        borderLeftColor: borderColor,
        borderColor: 'var(--border-default)',
        borderWidth: '1px',
        borderStyle: 'solid',
      }}
    >
      {/* Top row: severity dot + name + bed/unit */}
      <div className="flex items-center gap-2 min-w-0">
        <SeverityDot severity={severity} />
        <span
          className="font-semibold text-sm truncate"
          style={{ color: 'var(--text-primary)' }}
        >
          {patient_name}
        </span>
        <span
          className="text-xs shrink-0 ml-auto"
          style={{ color: 'var(--text-secondary)' }}
        >
          {bed}
          {unit ? ` • ${unit}` : ''}
        </span>
      </div>

      {/* Scores */}
      <ScorePair mews={mews ?? null} news2={news2 ?? null} />

      {/* Bottom row: pathways + vitals */}
      <div className="flex items-center gap-3">
        <PathwayBadges pathways={active_pathways ?? []} />
        <VitalsInline vitals={vitals} />
      </div>

      {/* Staleness indicator */}
      {staleness && (
        <div className="flex justify-end">
          <span
            className="text-[10px] font-medium"
            style={{ color: staleness.color }}
            aria-label={`Último vital registrado ${staleness.label}`}
          >
            {staleness.label}
          </span>
        </div>
      )}
    </div>
  );
}
