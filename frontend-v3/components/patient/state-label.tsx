'use client';

import type { SeverityLevel } from '@/lib/api';
import { severityColor } from './severity-glow';
import { cn } from '@/lib/utils';

interface StateLabelProps {
  label: string;
  severity: SeverityLevel;
  className?: string;
}

export function StateLabel({ label, severity, className }: StateLabelProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        className,
      )}
      style={{
        backgroundColor: `${severityColor(severity)}1A`,
        color: severityColor(severity),
        border: `1px solid ${severityColor(severity)}33`,
      }}
    >
      <span
        className="inline-block h-2 w-2 rounded-full"
        style={{ backgroundColor: severityColor(severity) }}
        aria-hidden="true"
      />
      {label}
    </span>
  );
}
