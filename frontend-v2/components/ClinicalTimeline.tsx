'use client';

import React, { useRef, useEffect } from 'react';
import { AlertTriangle, Loader2, Clock, History } from 'lucide-react';

// ─── Types ──────────────────────────────────────────────────────────────────

export type TimelineStatus =
  | 'completed'
  | 'in-progress'
  | 'pending'
  | 'overdue';

export interface TimelineEvent {
  id: string;
  status: TimelineStatus;
  label: string;
  description?: string;
  timestamp?: string;
  icon?: string;
}

export type TimelineDomainType = 'sepsis' | 'general';

interface ClinicalTimelineProps {
  events: TimelineEvent[];
  domain: TimelineDomainType;
  isLoading?: boolean;
  error?: string | null;
}

// ─── Status → Token mapping ─────────────────────────────────────────────────

interface StatusTokenSet {
  signal: string;
  onSurface: string;
  fill: string;
}

const statusTokens: Record<TimelineStatus, StatusTokenSet> = {
  completed: {
    signal: 'var(--clinical-sepsis-confirmed-signal)',
    onSurface: 'var(--clinical-sepsis-confirmed-on-surface)',
    fill: 'var(--clinical-sepsis-confirmed-fill)',
  },
  'in-progress': {
    signal: 'var(--clinical-sepsis-suspected-signal)',
    onSurface: 'var(--clinical-sepsis-suspected-on-surface)',
    fill: 'var(--clinical-sepsis-suspected-fill)',
  },
  pending: {
    signal: 'var(--semantic-text-secondary)',
    onSurface: 'var(--semantic-text-secondary)',
    fill: 'var(--semantic-surface-overlay)',
  },
  overdue: {
    signal: 'var(--clinical-sepsis-bundle-overdue-signal)',
    onSurface: 'var(--clinical-sepsis-bundle-overdue-on-surface)',
    fill: 'var(--clinical-sepsis-bundle-overdue-fill)',
  },
};

const statusLabels: Record<TimelineStatus, string> = {
  completed: 'Concluído',
  'in-progress': 'Em andamento',
  pending: 'Pendente',
  overdue: 'Atrasado',
};

// ─── Skeleton ────────────────────────────────────────────────────────────────

function TimelineSkeleton(): React.ReactElement {
  return (
    <div className="space-y-4 py-2" role="status" aria-label="Loading timeline">
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex gap-4 animate-pulse">
          <div className="flex flex-col items-center">
            <div
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            {i < 2 && (
              <div
                className="w-0.5 flex-1 mt-1"
                style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
              />
            )}
          </div>
          <div className="flex-1 space-y-1.5 pb-4">
            <div
              className="h-3.5 rounded w-1/3"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
            <div
              className="h-2.5 rounded w-2/3"
              style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function ClinicalTimeline({
  events,
  domain,
  isLoading = false,
  error = null,
}: ClinicalTimelineProps): React.ReactElement {
  const listRef = useRef<HTMLDivElement>(null);

  // Keyboard navigation: arrow up/down
  useEffect(() => {
    const el = listRef.current;
    if (!el) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;

      const items = Array.from(
        el.querySelectorAll<HTMLElement>('[data-timeline-event]'),
      );
      if (items.length === 0) return;

      const currentIdx = items.indexOf(document.activeElement as HTMLElement);
      let nextIdx: number;

      if (currentIdx === -1) {
        nextIdx = e.key === 'ArrowDown' ? 0 : items.length - 1;
      } else {
        e.preventDefault();
        nextIdx =
          e.key === 'ArrowDown'
            ? Math.min(currentIdx + 1, items.length - 1)
            : Math.max(currentIdx - 1, 0);
      }

      items[nextIdx]?.focus();
    };

    el.addEventListener('keydown', handleKeyDown);
    return () => el.removeEventListener('keydown', handleKeyDown);
  }, []);

  const formatTimestamp = (iso?: string): string => {
    if (!iso) return '';
    try {
      const date = new Date(iso);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return iso;
    }
  };

  // ─── Loading state ────────────────────────────────────────────────────────
  if (isLoading) {
    return <TimelineSkeleton />;
  }

  // ─── Error state ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className="flex items-center gap-2 px-3 py-3 rounded-lg text-sm"
        style={{
          backgroundColor: 'var(--feedback-error-bg-dark)',
          color: 'var(--feedback-error-text-dark)',
          borderColor: 'var(--feedback-error-border-dark)',
          borderWidth: '1px',
        }}
      >
        <AlertTriangle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // ─── Empty state ──────────────────────────────────────────────────────────
  if (events.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center gap-2 py-8 text-sm"
        style={{ color: 'var(--semantic-text-secondary)' }}
        role="status"
        aria-label="No events recorded"
      >
        <History className="w-10 h-10 opacity-30" aria-hidden="true" />
        <p>Nenhum evento registrado</p>
      </div>
    );
  }

  // ─── Timeline ─────────────────────────────────────────────────────────────
  return (
    <div
      ref={listRef}
      className="relative pl-1"
      role="list"
      aria-label={`${domain === 'sepsis' ? 'Sepse' : 'Clínica'} timeline`}
      tabIndex={0}
    >
      {events.map((event, index) => {
        const tokens = statusTokens[event.status];
        const isLast = index === events.length - 1;
        const isOverdue = event.status === 'overdue';
        const isCompleted = event.status === 'completed';
        const isInProgress = event.status === 'in-progress';

        return (
          <div
            key={event.id}
            data-timeline-event={event.id}
            className="flex gap-4 group outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500 rounded-lg px-1"
            tabIndex={0}
            role="listitem"
            aria-label={`${event.label}: ${statusLabels[event.status]}${
              event.timestamp ? ` às ${formatTimestamp(event.timestamp)}` : ''
            }${event.description ? `. ${event.description}` : ''}`}
          >
            {/* Timeline node + connector */}
            <div className="flex flex-col items-center">
              {/* Node */}
              <div
                className={`relative flex items-center justify-center rounded-full transition-all ${
                  isOverdue ? 'animate-pulse-critical' : ''
                }`}
                style={{
                  width: isInProgress ? '20px' : '16px',
                  height: isInProgress ? '20px' : '16px',
                  backgroundColor: isCompleted
                    ? tokens.fill
                    : isInProgress
                    ? tokens.signal
                    : 'transparent',
                  borderColor: tokens.signal,
                  borderWidth: isInProgress || isCompleted ? '0px' : '2px',
                  borderStyle: 'solid',
                  minWidth: '16px',
                  minHeight: '16px',
                  marginTop: '2px',
                }}
                aria-hidden="true"
              >
                {isCompleted && (
                  <svg
                    className="w-2.5 h-2.5"
                    viewBox="0 0 10 10"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M2 5l2 2 4-4"
                      stroke="var(--clinical-sepsis-confirmed-on-fill, white)"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
                {isInProgress && (
                  <Loader2
                    className="w-3 h-3 animate-spin"
                    style={{ color: tokens.onSurface }}
                  />
                )}
              </div>

              {/* Connector line */}
              {!isLast && (
                <div
                  className="w-0.5 flex-1 mt-1"
                  style={{
                    backgroundColor: isCompleted
                      ? tokens.signal
                      : 'var(--semantic-surface-overlay)',
                    minHeight: '24px',
                  }}
                  aria-hidden="true"
                />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 pb-6">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h4
                    className="text-sm font-semibold truncate"
                    style={{ color: 'var(--semantic-text-primary)' }}
                  >
                    {event.label}
                  </h4>
                  {event.description && (
                    <p
                      className="text-xs mt-0.5"
                      style={{ color: 'var(--semantic-text-secondary)' }}
                    >
                      {event.description}
                    </p>
                  )}
                </div>
                {event.timestamp && (
                  <span
                    className="text-xs whitespace-nowrap tabular-nums flex items-center gap-1 flex-shrink-0"
                    style={{ color: 'var(--semantic-text-secondary)' }}
                  >
                    <Clock className="w-3 h-3" aria-hidden="true" />
                    {formatTimestamp(event.timestamp)}
                  </span>
                )}
              </div>

              {/* Status badge */}
              <div className="flex items-center gap-1 mt-1.5">
                <span
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider"
                  style={{
                    backgroundColor: tokens.fill,
                    color: tokens.onSurface,
                    borderWidth: '1px',
                    borderColor: tokens.signal,
                    borderStyle: 'solid',
                    opacity: event.status === 'pending' ? 0.7 : 1,
                  }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: tokens.signal }}
                    aria-hidden="true"
                  />
                  {statusLabels[event.status]}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
