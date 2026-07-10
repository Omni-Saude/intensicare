'use client';

import { cn } from '@/lib/utils';
import { FileText, ScrollText, Lightbulb } from 'lucide-react';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface RecommendationsPanelProps {
  recommendations?: string[];
  isLoading?: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function RecommendationsPanel({
  recommendations,
  isLoading,
}: RecommendationsPanelProps) {
  // ---------- Loading ----------
  if (isLoading) {
    return (
      <section
        aria-label="Recomendações"
        className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]"
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-default)] bg-[var(--surface-canvas)]">
          <div className="h-4 w-4 rounded bg-[var(--surface-overlay)] animate-pulse" />
          <div className="h-4 w-36 rounded bg-[var(--surface-overlay)] animate-pulse" />
        </div>
        {[1, 2].map((i) => (
          <div key={i} className="px-4 py-3 space-y-2 border-b border-[var(--border-default)] last:border-b-0">
            <div className="h-3 w-full rounded bg-[var(--surface-overlay)] animate-pulse" />
            <div className="h-3 w-3/4 rounded bg-[var(--surface-overlay)] animate-pulse" />
          </div>
        ))}
      </section>
    );
  }

  // ---------- Empty ----------
  if (!recommendations || recommendations.length === 0) {
    return (
      <section
        aria-label="Recomendações"
        className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-5 text-center"
      >
        <Lightbulb className="h-8 w-8 text-[var(--text-secondary)] mx-auto mb-2" aria-hidden="true" />
        <p className="text-sm font-medium text-[var(--text-primary)]">
          Nenhuma recomendação disponível
        </p>
        <p className="text-xs text-[var(--text-secondary)] mt-1">
          As recomendações clínicas aparecerão aqui quando disponíveis.
        </p>
      </section>
    );
  }

  return (
    <section
      aria-label="Recomendações"
      className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-default)] bg-[var(--surface-canvas)]">
        <ScrollText className="h-4 w-4 text-[var(--text-secondary)]" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">
          Recomendações ({recommendations.length})
        </h3>
      </div>

      {/* Cards */}
      <div className="divide-y divide-[var(--border-default)]">
        {recommendations.map((rec, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 px-4 py-3 hover:bg-[var(--surface-overlay)] transition-colors"
          >
            <FileText className="h-4 w-4 text-[var(--severity-watch)] mt-0.5 shrink-0" aria-hidden="true" />
            <p className="text-sm text-[var(--text-primary)] leading-relaxed">{rec}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
