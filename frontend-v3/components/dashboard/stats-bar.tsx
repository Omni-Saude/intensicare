'use client';

import { Users, AlertTriangle } from 'lucide-react';

interface StatsBarProps {
  total: number;
  criticalCount: number;
  unit?: string;
}

export function StatsBar({ total, criticalCount, unit }: StatsBarProps) {
  const segments: string[] = [`${total} pacientes`];

  if (criticalCount > 0) {
    segments.push(`${criticalCount} críticos`);
  }

  if (unit) {
    segments.push(unit);
  }

  return (
    <div
      className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 rounded-[var(--radius-md)]"
      style={{
        backgroundColor: 'var(--surface-raised)',
        borderColor: 'var(--border-default)',
        borderWidth: '1px',
        borderStyle: 'solid',
      }}
    >
      <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
        <Users className="size-4" />
        <span className="text-sm font-medium">{segments.join(' • ')}</span>
      </div>

      {criticalCount > 0 && (
        <div
          className="flex items-center gap-1.5 text-sm font-semibold"
          style={{ color: 'var(--severity-critical)' }}
        >
          <AlertTriangle className="size-4" />
          <span>{criticalCount} crítico{criticalCount !== 1 ? 's' : ''}</span>
        </div>
      )}
    </div>
  );
}
