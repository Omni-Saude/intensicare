'use client';

import type { PatientPathway } from '@/lib/api';
import { severityGlow } from './severity-glow';
import { StateLabel } from './state-label';
import { MiniProgress } from './mini-progress';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';
import { GitBranch, ChevronRight } from 'lucide-react';

interface PathwayCardProps {
  pathway: PatientPathway;
}

export function PathwayCard({ pathway }: PathwayCardProps) {
  const router = useRouter();
  const sev = pathway.severity ?? 'normal';

  // Count criteria met
  const criteria = pathway.criteria ?? [];
  const met = criteria.filter((c) => c.met).length;
  const total = criteria.length;

  const handleClick = () => {
    router.push(`/patient/${pathway.mpi_id}/pathway/${pathway.id}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Trilha ${pathway.pathway.name}, estado ${pathway.current_state.name}, severidade ${sev}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={cn(
        'group cursor-pointer rounded-lg border bg-[var(--surface-raised)] p-4 transition-all',
        'border-[var(--border-default)]',
        'hover:border-[var(--text-secondary)] hover:shadow-lg',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
        sev === 'critical' && 'severity-critical-pulse',
      )}
      style={{
        borderLeftColor: sev !== 'normal' ? `var(--severity-${sev})` : 'var(--border-default)',
        borderLeftWidth: '3px',
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0 space-y-2">
          {/* Title + severity label */}
          <div className="flex items-center gap-2 flex-wrap">
            <GitBranch className="h-4 w-4 text-[var(--text-secondary)] shrink-0" aria-hidden="true" />
            <h3 className="text-sm font-semibold text-[var(--text-primary)] truncate">
              {pathway.pathway.name}
            </h3>
            <StateLabel label={pathway.current_state.name} severity={sev} />
          </div>

          {/* Progress */}
          {total > 0 && (
            <MiniProgress met={met} total={total} />
          )}

          {/* Enrollment date */}
          <p className="text-xs text-[var(--text-secondary)]">
            Iniciado em {new Date(pathway.enrolled_at).toLocaleDateString('pt-BR')}
          </p>
        </div>

        <ChevronRight
          className="h-5 w-5 text-[var(--text-secondary)] shrink-0 transition-transform group-hover:translate-x-0.5 mt-1"
          aria-hidden="true"
        />
      </div>
    </div>
  );
}
