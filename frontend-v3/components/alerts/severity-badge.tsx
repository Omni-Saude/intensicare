'use client';

import { cn } from '@/lib/utils';
import type { SeverityLevel } from '@/lib/api';

const SEVERITY_CONFIG: Record<
  SeverityLevel,
  { label: string; colorVar: string; washVar: string }
> = {
  normal: {
    label: 'Normal',
    colorVar: 'var(--severity-normal)',
    washVar: 'var(--severity-normal-wash)',
  },
  watch: {
    label: 'Observação',
    colorVar: 'var(--severity-watch)',
    washVar: 'var(--severity-watch-wash)',
  },
  urgent: {
    label: 'Urgente',
    colorVar: 'var(--severity-urgent)',
    washVar: 'var(--severity-urgent-wash)',
  },
  critical: {
    label: 'Crítico',
    colorVar: 'var(--severity-critical)',
    washVar: 'var(--severity-critical-wash)',
  },
};

interface SeverityBadgeProps {
  severity: SeverityLevel;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.normal;

  return (
    <span
      role="status"
      aria-label={`Severidade: ${config.label}`}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium whitespace-nowrap',
        severity === 'critical' && 'severity-critical-pulse',
        className,
      )}
      style={{
        backgroundColor: config.washVar,
        color: config.colorVar,
        border: `1px solid ${config.colorVar}`,
      }}
    >
      <span
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: config.colorVar }}
        aria-hidden="true"
      />
      {config.label}
    </span>
  );
}
