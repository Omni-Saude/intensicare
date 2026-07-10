'use client';

import type { PatientPathway } from '@/lib/api';
import { PathwayCard } from './pathway-card';
import { GitBranchPlus } from 'lucide-react';

interface ActivePathwaysProps {
  pathways: PatientPathway[];
  isLoading?: boolean;
  error?: string | null;
}

export function ActivePathways({ pathways, isLoading, error }: ActivePathwaysProps) {
  return (
    <section aria-label="Trilhas ativas" className="space-y-3">
      <div className="flex items-center gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
          Trilhas Ativas
        </h2>
        {!isLoading && !error && pathways.length > 0 && (
          <span className="inline-flex items-center justify-center rounded-full bg-[var(--surface-overlay)] px-2 py-0.5 text-xs text-[var(--text-secondary)]">
            {pathways.length}
          </span>
        )}
      </div>

      {isLoading && (
        <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-[140px] animate-pulse rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]"
              aria-hidden="true"
            />
          ))}
        </div>
      )}

      {error && (
        <div
          className="rounded-lg border border-[var(--severity-critical)] bg-[var(--severity-critical-wash)] p-4 text-sm text-[var(--severity-critical)]"
          role="alert"
        >
          Erro ao carregar trilhas ativas: {error}
        </div>
      )}

      {!isLoading && !error && pathways.length === 0 && (
        <div className="rounded-lg border border-dashed border-[var(--border-default)] bg-[var(--surface-raised)] p-8 text-center">
          <GitBranchPlus className="mx-auto h-8 w-8 text-[var(--text-secondary)] mb-2" aria-hidden="true" />
          <p className="text-sm text-[var(--text-secondary)]">
            Nenhuma trilha ativa para este paciente.
          </p>
          <p className="text-xs text-[var(--text-secondary)] mt-1">
            As trilhas são ativadas automaticamente quando os critérios clínicos são atendidos.
          </p>
        </div>
      )}

      {!isLoading && !error && pathways.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {pathways.map((pp) => (
            <PathwayCard key={pp.id} pathway={pp} />
          ))}
        </div>
      )}
    </section>
  );
}
