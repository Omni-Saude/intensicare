'use client';

import { cn } from '@/lib/utils';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface CriteriaValueProps {
  /** Current measured value (e.g. "58"). */
  value?: string | null;
  /** Unit of measurement (e.g. "mmHg"). */
  unit?: string;
  /** Alert threshold (e.g. "≥65 mmHg"). */
  threshold?: string;
  /** Normal reference range (e.g. "≥65"). */
  normalRange?: string;
  /** Additional class names. */
  className?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CriteriaValue({
  value,
  unit,
  threshold,
  normalRange,
  className,
}: CriteriaValueProps) {
  const hasValue = value !== null && value !== undefined;
  const displayValue = hasValue ? `${value} ${unit ?? ''}`.trim() : '—';

  return (
    <span
      className={cn(
        'inline-flex flex-wrap items-baseline gap-1.5 text-sm',
        className,
      )}
    >
      {/* Current value */}
      <span
        className={cn(
          'font-semibold tabular-nums',
          hasValue ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]',
        )}
      >
        {displayValue}
      </span>

      {/* Threshold */}
      {threshold && (
        <span className="text-[var(--text-secondary)] text-xs">
          <span className="mx-1" aria-hidden="true">—</span>
          limiar: {threshold}
        </span>
      )}

      {/* Normal range (only if different from threshold) */}
      {normalRange && normalRange !== threshold && (
        <span className="text-[var(--text-secondary)] text-xs">
          (normal: {normalRange})
        </span>
      )}
    </span>
  );
}
