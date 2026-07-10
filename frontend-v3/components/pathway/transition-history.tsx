'use client';

import type { StateTransition } from '@/lib/api';
import { cn } from '@/lib/utils';
import { GitCommitHorizontal, ArrowRight, History } from 'lucide-react';

// ---------------------------------------------------------------------------
// Helper: format date
// ---------------------------------------------------------------------------

function formatTransitionDate(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface TransitionHistoryProps {
  history?: StateTransition[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function TransitionHistory({ history }: TransitionHistoryProps) {
  // ---------- Empty ----------
  if (!history || history.length === 0) {
    return (
      <section
        aria-label="Histórico de transições"
        className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-5 text-center"
      >
        <History className="h-8 w-8 text-[var(--text-secondary)] mx-auto mb-2" aria-hidden="true" />
        <p className="text-sm font-medium text-[var(--text-primary)]">
          Nenhuma transição registrada
        </p>
        <p className="text-xs text-[var(--text-secondary)] mt-1">
          O histórico de mudanças de estado aparecerá aqui.
        </p>
      </section>
    );
  }

  return (
    <section
      aria-label="Histórico de transições"
      className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-default)] bg-[var(--surface-canvas)]">
        <History className="h-4 w-4 text-[var(--text-secondary)]" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-[var(--text-primary)]">
          Histórico de Transições ({history.length})
        </h3>
      </div>

      {/* Timeline */}
      <ol className="relative ml-6 border-l border-[var(--border-default)] py-3 space-y-0">
        {history.map((transition, idx) => {
          const isFirst = idx === 0;
          const isLast = idx === history.length - 1;

          return (
            <li
              key={`${transition.from_state ?? 'start'}-${transition.to_state}-${transition.changed_at}`}
              className={cn(
                'relative pl-8 pb-5 last:pb-3',
              )}
            >
              {/* Timeline dot */}
              <span
                className={cn(
                  'absolute -left-[11px] flex items-center justify-center w-[21px] h-[21px] rounded-full border-2',
                  isFirst
                    ? 'bg-[var(--severity-watch-wash)] border-[var(--severity-watch)] text-[var(--severity-watch)]'
                    : 'bg-[var(--surface-raised)] border-[var(--border-default)] text-[var(--text-secondary)]',
                )}
                aria-hidden="true"
              >
                <GitCommitHorizontal className="h-3 w-3" />
              </span>

              {/* Content */}
              <div className="space-y-1">
                {/* Date */}
                <time
                  dateTime={transition.changed_at}
                  className="block text-xs text-[var(--text-secondary)]"
                >
                  {formatTransitionDate(transition.changed_at)}
                </time>

                {/* Transition description */}
                <p className="text-sm text-[var(--text-primary)] flex items-center gap-1.5 flex-wrap">
                  {transition.from_state ? (
                    <>
                      <span className="text-[var(--text-secondary)]">{transition.from_state}</span>
                      <ArrowRight className="h-3.5 w-3.5 text-[var(--text-secondary)]" aria-hidden="true" />
                      <span className="font-medium">{transition.to_state}</span>
                    </>
                  ) : (
                    <>
                      <span className="font-medium">{transition.to_state}</span>
                      <span className="text-xs text-[var(--text-secondary)]">(início)</span>
                    </>
                  )}
                </p>

                {/* Reason */}
                {transition.reason && (
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    {transition.reason}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
