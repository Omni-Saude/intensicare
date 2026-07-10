'use client';

import type { PathwayCriteria } from '@/lib/api';
import { CriteriaRow } from './criteria-row';
import { cn } from '@/lib/utils';
import { useState, useCallback } from 'react';
import {
  Loader2,
  AlertCircle,
  ClipboardList,
  CircleCheck,
  CircleX,
  CircleDot,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface CriteriaListProps {
  criteria?: PathwayCriteria[];
  summary: {
    total: number;
    met: number;
    not_met: number;
    pending: number;
  };
  isLoading?: boolean;
  error?: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function CriteriaList({
  criteria,
  summary,
  isLoading,
  error,
}: CriteriaListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleToggle = useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  // ---------- Loading skeleton ----------
  if (isLoading) {
    return (
      <section
        aria-label="Critérios da trilha"
        className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]"
      >
        {/* Skeleton summary */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-default)]">
          <Loader2 className="h-4 w-4 animate-spin text-[var(--text-secondary)]" aria-hidden="true" />
          <div className="h-4 w-48 rounded bg-[var(--surface-overlay)] animate-pulse" />
        </div>
        {/* Skeleton rows */}
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-default)] last:border-b-0">
            <div className="h-5 w-5 rounded-full bg-[var(--surface-overlay)] animate-pulse shrink-0" />
            <div className="flex-1 space-y-1.5">
              <div className="h-4 w-36 rounded bg-[var(--surface-overlay)] animate-pulse" />
              <div className="h-3 w-24 rounded bg-[var(--surface-overlay)] animate-pulse" />
            </div>
          </div>
        ))}
      </section>
    );
  }

  // ---------- Error ----------
  if (error) {
    return (
      <section
        aria-label="Critérios da trilha"
        className="rounded-lg border border-[var(--severity-critical)] bg-[var(--surface-raised)] p-6 text-center"
      >
        <AlertCircle className="h-8 w-8 text-[var(--severity-critical)] mx-auto mb-2" aria-hidden="true" />
        <p className="text-sm text-[var(--severity-critical)] font-medium mb-1">Erro ao carregar critérios</p>
        <p className="text-xs text-[var(--text-secondary)]">{error}</p>
      </section>
    );
  }

  // ---------- Empty ----------
  if (!criteria || criteria.length === 0) {
    return (
      <section
        aria-label="Critérios da trilha"
        className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-6 text-center"
      >
        <ClipboardList className="h-8 w-8 text-[var(--text-secondary)] mx-auto mb-2" aria-hidden="true" />
        <p className="text-sm font-medium text-[var(--text-primary)] mb-1">
          Nenhum critério disponível
        </p>
        <p className="text-xs text-[var(--text-secondary)]">
          Esta trilha não possui critérios configurados.
        </p>
      </section>
    );
  }

  // ---------- Data ----------
  const { total, met, not_met, pending } = summary;

  return (
    <section
      aria-label="Critérios da trilha"
      className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] overflow-hidden"
    >
      {/* Summary header */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-4 px-4 py-3 border-b border-[var(--border-default)] bg-[var(--surface-canvas)]">
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">
          Critérios ({total})
        </h3>

        <div className="flex flex-wrap items-center gap-3 text-xs">
          <span className="inline-flex items-center gap-1 text-[var(--severity-normal)]">
            <CircleCheck className="h-3.5 w-3.5" aria-hidden="true" />
            {met} atendidos
          </span>
          <span className="inline-flex items-center gap-1 text-[var(--severity-critical)]">
            <CircleX className="h-3.5 w-3.5" aria-hidden="true" />
            {not_met} não atendidos
          </span>
          <span className="inline-flex items-center gap-1 text-[var(--text-secondary)]">
            <CircleDot className="h-3.5 w-3.5" aria-hidden="true" />
            {pending} pendentes
          </span>
        </div>
      </div>

      {/* Criteria rows */}
      <div role="list" aria-label="Lista de critérios">
        {criteria.map((criterion) => (
          <CriteriaRow
            key={criterion.id}
            criterion={criterion}
            isExpanded={expandedId === criterion.id}
            onToggle={() => handleToggle(criterion.id)}
          />
        ))}
      </div>
    </section>
  );
}
