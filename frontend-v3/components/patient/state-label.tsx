'use client';

import type { SeverityLevel } from '@/lib/api';
import { severityColor, severityWash, severityRing } from './severity-glow';
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
        backgroundColor: severityWash(severity),
        color: severityColor(severity),
        border: `1px solid ${severityRing(severity)}`,
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
