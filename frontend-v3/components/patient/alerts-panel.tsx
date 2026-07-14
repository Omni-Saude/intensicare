'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Layers, TrendingUp, BellOff } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AlertGroup } from '@/lib/api';
import { SeverityBadge } from '@/components/alerts/severity-badge';
import { AlertItem } from './alert-item';

interface AlertsPanelProps {
  /**
   * Read-side aggregation (ADR-0039 §1/§2). For a single-patient panel the
   * group key (mpi_id, score_type) collapses to just `score_type` — each
   * group here *is* a clinical signal for this patient, so the header
   * reads as "signal + rollup" rather than repeating the patient's name.
   */
  groups: AlertGroup[];
  isLoading?: boolean;
  error?: string | null;
  onAcknowledge?: (id: number) => Promise<void>;
  onEscalate?: (id: number) => Promise<void>;
}

export function AlertsPanel({ groups, isLoading, error, onAcknowledge, onEscalate }: AlertsPanelProps) {
  const [actingIds, setActingIds] = useState<Set<number>>(new Set());
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(new Set());

  const handleAcknowledge = async (id: number) => {
    if (!onAcknowledge) return;
    setActingIds((prev) => new Set(prev).add(id));
    try {
      await onAcknowledge(id);
    } finally {
      setActingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const handleEscalate = async (id: number) => {
    if (!onEscalate) return;
    setActingIds((prev) => new Set(prev).add(id));
    try {
      await onEscalate(id);
    } finally {
      setActingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const toggleExpanded = (scoreType: string) => {
    setExpandedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(scoreType)) {
        next.delete(scoreType);
      } else {
        next.add(scoreType);
      }
      return next;
    });
  };

  return (
    <section aria-label="Alertas do paciente" className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
        Alertas
      </h2>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-[120px] animate-pulse rounded-lg border border-[var(--border-default)] bg-[var(--surface-raised)]"
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
          Erro ao carregar alertas: {error}
        </div>
      )}

      {!isLoading && !error && groups.length === 0 && (
        <div className="rounded-lg border border-dashed border-[var(--border-default)] bg-[var(--surface-raised)] p-6 text-center">
          <BellOff className="mx-auto h-8 w-8 text-[var(--text-secondary)] mb-2" aria-hidden="true" />
          <p className="text-sm text-[var(--text-secondary)]">
            Nenhum alerta ativo para este paciente.
          </p>
        </div>
      )}

      {!isLoading && !error && groups.length > 0 && (
        <div className="space-y-3" role="list" aria-label="Grupos de alertas por sinal clínico">
          {groups.map((group) => {
            // A group of one is a single occurrence — the group chrome
            // (disclosure, count, "N ocorrências") would just repeat what
            // the AlertItem itself already says. Render it bare, same as
            // any other alert, and reserve the rollup header for groups
            // that actually roll something up (count > 1).
            if (group.count === 1) {
              const only = group.members[0];
              return (
                <AlertItem
                  key={only.id}
                  alert={only}
                  onAcknowledge={onAcknowledge ? handleAcknowledge : undefined}
                  onEscalate={onEscalate ? handleEscalate : undefined}
                  disabled={actingIds.has(only.id)}
                />
              );
            }

            const expanded = expandedTypes.has(group.score_type);
            const detailsId = `patient-alert-group-${group.score_type}-details`;
            const groupLabel = `${group.score_type} (${group.count} ocorrências)`;

            return (
              <div
                key={group.score_type}
                className={cn(
                  'rounded-lg border transition-colors',
                  group.escalating
                    ? 'border-[var(--severity-critical)]/50 bg-[var(--severity-critical-wash)]'
                    : 'border-[var(--border-default)] bg-[var(--surface-raised)]',
                )}
                role="listitem"
              >
                {/*
                  Summary row — same APG disclosure pattern as
                  components/alerts/alert-group-row.tsx: the row itself is a
                  mouse-only convenience (no tabIndex), a sibling <button>
                  owns aria-expanded/aria-controls.
                */}
                <div
                  className="flex cursor-pointer flex-wrap items-center gap-2 px-3 py-2.5"
                  onClick={() => toggleExpanded(group.score_type)}
                >
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleExpanded(group.score_type);
                    }}
                    aria-expanded={expanded}
                    aria-controls={detailsId}
                    aria-label={`Grupo ${groupLabel} — ${expanded ? 'Recolher' : 'Expandir'}`}
                    className="flex-shrink-0 rounded text-[var(--text-secondary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
                  >
                    {expanded ? (
                      <ChevronDown className="h-4 w-4" aria-hidden="true" />
                    ) : (
                      <ChevronRight className="h-4 w-4" aria-hidden="true" />
                    )}
                  </button>

                  <SeverityBadge severity={group.max_severity} />

                  <span
                    className="inline-flex items-center gap-1 rounded-full border border-[var(--border-default)] bg-[var(--surface-overlay)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]"
                    aria-label={`Tipo de sinal: ${group.score_type}`}
                  >
                    <Layers className="h-3 w-3" aria-hidden="true" />
                    {group.score_type}
                  </span>

                  <span className="text-sm text-[var(--text-primary)]">
                    {group.count} {group.count === 1 ? 'ocorrência' : 'ocorrências'}
                  </span>

                  {/*
                    Escalation badge — ADR-0039 §3: never suppressed, always
                    rendered in the collapsed summary. Same tokens as
                    alert-group-row.tsx (critical color/wash pair +
                    severity-critical-pulse).
                  */}
                  {group.escalating && (
                    <span
                      className="severity-critical-pulse inline-flex items-center gap-1 rounded-full border border-[var(--severity-critical)] bg-[var(--severity-critical-wash)] px-2 py-0.5 text-xs font-semibold text-[var(--severity-critical)]"
                      role="status"
                      aria-label="Em escalação: a severidade subiu desde o alerta ativo mais antigo deste grupo"
                    >
                      <TrendingUp className="h-3 w-3" aria-hidden="true" />
                      Escalando
                    </span>
                  )}
                </div>

                {/*
                  Expanded members — kept mounted (visibility via `hidden`)
                  so aria-controls always resolves. Each member renders via
                  the existing AlertItem, unmodified — title/preview and
                  individual ack/escalate stay per-alert.
                */}
                <div
                  id={detailsId}
                  hidden={!expanded}
                  className="space-y-2 border-t border-[var(--border-default)] px-3 py-2.5"
                >
                  {group.members.map((member) => (
                    <AlertItem
                      key={member.id}
                      alert={member}
                      onAcknowledge={onAcknowledge ? handleAcknowledge : undefined}
                      onEscalate={onEscalate ? handleEscalate : undefined}
                      disabled={actingIds.has(member.id)}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
