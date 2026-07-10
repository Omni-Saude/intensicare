'use client';

import type { SeverityLevel } from '@/lib/api';
import { cn } from '@/lib/utils';

const SEVERITY_VAR: Record<SeverityLevel, string> = {
  normal: 'var(--severity-normal)',
  watch: 'var(--severity-watch)',
  urgent: 'var(--severity-urgent)',
  critical: 'var(--severity-critical)',
};

interface SeverityDotProps {
  severity: SeverityLevel;
}

export function SeverityDot({ severity }: SeverityDotProps) {
  const isCritical = severity === 'critical';

  return (
    <span
      role="status"
      aria-label={`Severidade ${severity}`}
      className={cn(
        'inline-block size-2.5 shrink-0 rounded-full',
        isCritical && 'severity-critical-pulse',
      )}
      style={{ backgroundColor: SEVERITY_VAR[severity] }}
    />
  );
}
