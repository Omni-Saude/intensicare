'use client';

import type { PathwayState, StateTransition } from '@/lib/api';
import { cn } from '@/lib/utils';
import { Check, Lock, Circle } from 'lucide-react';

// ---------------------------------------------------------------------------
// Helper: map state order to transition-timing status
// ---------------------------------------------------------------------------

type StateStatus = 'past' | 'current' | 'future';

function getStateStatus(
  state: PathwayState,
  currentStateId: string,
  history: StateTransition[],
): StateStatus {
  if (state.id === currentStateId) return 'current';

  // Determine past/future by checking if this state has been visited in history
  const visitedIds = new Set<string>();
  for (const t of history) {
    if (t.from_state) visitedIds.add(t.from_state);
    visitedIds.add(t.to_state);
  }

  if (visitedIds.has(state.id)) return 'past';
  return 'future';
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface StateFlowProps {
  states: PathwayState[];
  currentStateId: string;
  history: StateTransition[];
}

// ---------------------------------------------------------------------------
// Visual constants
// ---------------------------------------------------------------------------

const STATUS_STYLES: Record<StateStatus, {
  pill: string;
  icon: string;
  connector: string;
}> = {
  past: {
    pill: 'bg-[var(--severity-normal)]/15 border-[var(--severity-normal)] text-[var(--severity-normal)]',
    icon: 'text-[var(--severity-normal)]',
    connector: 'bg-[var(--severity-normal)]',
  },
  current: {
    pill: 'bg-[var(--severity-watch)]/20 border-[var(--severity-watch)] text-[var(--text-primary)] shadow-[0_0_8px_2px_var(--severity-watch-wash)]',
    icon: 'text-[var(--severity-watch)]',
    connector: 'bg-[var(--border-default)]',
  },
  future: {
    pill: 'bg-transparent border-[var(--border-default)] text-[var(--text-secondary)]',
    icon: 'text-[var(--text-secondary)]',
    connector: 'bg-[var(--border-default)]',
  },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function StateFlow({ states, currentStateId, history }: StateFlowProps) {
  if (!states || states.length === 0) {
    return (
      <div
        className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] p-4 text-center text-sm text-[var(--text-secondary)]"
        aria-label="Fluxo de estados"
      >
        Nenhum estado definido para esta trilha.
      </div>
    );
  }

  // Sort by order
  const sorted = [...states].sort((a, b) => a.order - b.order);

  return (
    <nav
      aria-label="Progresso dos estados da trilha"
      className="rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)] px-4 py-4"
    >
      {/* Scrollable container for mobile */}
      <div className="overflow-x-auto -mx-1 px-1 scrollbar-thin">
        <div className="flex items-center min-w-max gap-0">
          {sorted.map((state, idx) => {
            const status = getStateStatus(state, currentStateId, history);
            const styles = STATUS_STYLES[status];
            const isLast = idx === sorted.length - 1;
            const isTerminal = state.is_terminal;

            return (
              <div key={state.id} className="flex items-center">
                {/* Pill */}
                <div
                  className={cn(
                    'flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium whitespace-nowrap transition-all',
                    styles.pill,
                  )}
                  aria-current={status === 'current' ? 'step' : undefined}
                >
                  {/* Icon */}
                  {status === 'past' ? (
                    <Check className="h-3.5 w-3.5" aria-hidden="true" />
                  ) : status === 'future' && isTerminal ? (
                    <Lock className="h-3.5 w-3.5" aria-hidden="true" />
                  ) : (
                    <Circle
                      className={cn('h-3.5 w-3.5', status === 'current' && 'fill-current')}
                      aria-hidden="true"
                    />
                  )}

                  {/* Label */}
                  <span>{state.name}</span>

                  {/* Terminal badge */}
                  {isTerminal && (
                    <span className="text-[10px] opacity-70" aria-label="Estado terminal">
                      (final)
                    </span>
                  )}
                </div>

                {/* Connector line */}
                {!isLast && (
                  <div
                    className={cn('h-0.5 w-4 sm:w-6 shrink-0', styles.connector)}
                    aria-hidden="true"
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
