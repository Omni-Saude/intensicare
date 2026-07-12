'use client';

import type { SeverityLevel } from '@/lib/api';
import { cn } from '@/lib/utils';

const SEVERITY_VAR: Record<SeverityLevel, string> = {
  normal: 'var(--severity-normal)',
  watch: 'var(--severity-watch)',
  urgent: 'var(--severity-urgent)',
  critical: 'var(--severity-critical)',
};

const SEVERITY_LABEL: Record<SeverityLevel, string> = {
  normal: 'Normal',
  watch: 'Observação',
  urgent: 'Urgente',
  critical: 'Crítico',
};

interface SeverityDotProps {
  // Defensive: accepts null/undefined even though the domain type is
  // non-nullable, since the backend has been observed sending an absent
  // severity (audit Dim B/D). Falls back to 'normal' rather than
  // rendering an undefined color / "Severidade null" label.
  severity: SeverityLevel | null | undefined;
}

export function SeverityDot({ severity }: SeverityDotProps) {
  const sev = severity ?? 'normal';
  const isCritical = sev === 'critical';

  return (
    <span
      role="status"
      aria-label={`Severidade ${SEVERITY_LABEL[sev]}`}
      className={cn(
        'inline-block size-2.5 shrink-0 rounded-full',
        isCritical && 'severity-critical-pulse',
      )}
      style={{ backgroundColor: SEVERITY_VAR[sev] }}
    />
  );
}
