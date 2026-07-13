'use client';

import type { PatientBedSummary, SeverityLevel } from '@/lib/api';
import { SeverityDot } from './severity-dot';
import { ScorePair } from './score-pair';
import { PathwayBadges } from './pathway-badges';
import { VitalsInline } from './vitals-inline';
import { cn } from '@/lib/utils';
import { computeStaleness } from '@/lib/vitals-staleness';

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

  // Defensive fallback: the domain type declares `severity` non-nullable,
  // but the backend has been observed sending it absent (audit Dim B/D).
  // Without this guard, an unexpected value silently produces `undefined`
  // border colour (no visible severity indicator on the card).
  const borderColor = SEVERITY_BORDER[severity ?? 'normal'];
  const staleness = last_vital_at ? computeStaleness(last_vital_at) : null;

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
        // NOTE: the border-* shorthand properties must come before the
        // borderLeft* longhand overrides below. React assigns each style
        // object key to the DOM's CSSStyleDeclaration in insertion order,
        // and the `border-color`/`border-width` shorthands reset *all four*
        // sides (including left) when applied — so setting them after
        // borderLeftColor/borderLeftWidth silently clobbered the severity
        // accent, leaving every card with a plain 1px neutral border and no
        // visible severity indicator (found while verifying this task).
        borderColor: 'var(--border-default)',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderLeftWidth: '4px',
        borderLeftStyle: 'solid',
        borderLeftColor: borderColor,
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
            aria-label={`Último vital registrado ${staleness.shortLabel}`}
          >
            {staleness.shortLabel}
          </span>
        </div>
      )}
    </div>
  );
}
