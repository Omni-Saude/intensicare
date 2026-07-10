'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ChevronDown, ChevronRight, Clock, User, GitBranch } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AlertInfo } from '@/lib/api';
import { SeverityBadge } from './severity-badge';
import { QuickActions } from './quick-actions';
import { AlertTrace } from './alert-trace';

interface AlertRowProps {
  alert: AlertInfo;
  onAlertUpdate: (updated: AlertInfo) => void;
  onError: (message: string) => void;
}

export function AlertRow({ alert, onAlertUpdate, onError }: AlertRowProps) {
  const [expanded, setExpanded] = useState(false);

  const createdAt = new Date(alert.created_at).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const isResolved = !!alert.resolved_at;
  const isAcknowledged = !!alert.acknowledged_at;

  return (
    <div
      className={cn(
        'rounded-lg border transition-colors',
        isResolved
          ? 'border-[var(--severity-normal)]/30 bg-[var(--severity-normal-wash)]'
          : 'border-[var(--border-default)] bg-[var(--surface-raised)]',
      )}
      role="listitem"
    >
      {/* Summary row */}
      <div
        className="flex cursor-pointer flex-wrap items-center gap-3 px-4 py-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[var(--severity-watch)]"
        onClick={() => setExpanded(!expanded)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setExpanded(!expanded);
          }
        }}
        tabIndex={0}
        role="button"
        aria-expanded={expanded}
        aria-label={`Alerta ${alert.id}: ${alert.title} — ${expanded ? 'Recolher' : 'Expandir'} detalhes`}
      >
        {/* Expand icon */}
        <span className="text-[var(--text-secondary)]" aria-hidden="true">
          {expanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </span>

        {/* Severity */}
        <SeverityBadge severity={alert.severity} />

        {/* Patient link */}
        {alert.mpi_id ? (
          <Link
            href={`/patient/${alert.mpi_id}`}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-sm font-medium text-[var(--text-primary)] hover:underline"
            aria-label={`Paciente: ${alert.patient_name || alert.mpi_id}`}
          >
            <User className="h-3.5 w-3.5 text-[var(--text-secondary)]" aria-hidden="true" />
            {alert.patient_name || alert.mpi_id}
          </Link>
        ) : (
          <span className="text-sm text-[var(--text-secondary)]">—</span>
        )}

        {/* Pathway link */}
        {alert.pathway_name ? (
          <Link
            href={`/pathways`}
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:underline"
            aria-label={`Trilha: ${alert.pathway_name}`}
          >
            <GitBranch className="h-3.5 w-3.5" aria-hidden="true" />
            {alert.pathway_name}
          </Link>
        ) : (
          <span className="text-sm text-[var(--text-secondary)]">—</span>
        )}

        {/* Message */}
        <span className="flex-1 truncate text-sm text-[var(--text-primary)] min-w-0">
          {alert.message}
        </span>

        {/* Date */}
        <span className="flex items-center gap-1 text-xs text-[var(--text-secondary)] whitespace-nowrap">
          <Clock className="h-3 w-3" aria-hidden="true" />
          {createdAt}
        </span>

        {/* Status indicators */}
        <span className="flex items-center gap-2">
          {isAcknowledged && (
            <span
              className="rounded-full bg-[var(--severity-watch-wash)] px-2 py-0.5 text-xs text-[var(--severity-watch)]"
              aria-label="Reconhecido"
            >
              ✓
            </span>
          )}
          {isResolved && (
            <span
              className="rounded-full bg-[var(--severity-normal-wash)] px-2 py-0.5 text-xs font-medium text-[var(--severity-normal)]"
              aria-label="Resolvido"
            >
              Resolvido
            </span>
          )}
        </span>

        {/* Quick actions — stop propagation so click doesn't toggle expand */}
        <div onClick={(e) => e.stopPropagation()} onKeyDown={(e) => e.stopPropagation()}>
          <QuickActions alert={alert} onAction={onAlertUpdate} onError={onError} />
        </div>
      </div>

      {/* Expanded detail */}
      {expanded && (
        <div
          className="border-t border-[var(--border-default)] px-4 py-3"
          role="region"
          aria-label="Detalhes do alerta"
        >
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <span className="text-xs text-[var(--text-secondary)]">Tipo</span>
              <p className="text-sm text-[var(--text-primary)]">{alert.type}</p>
            </div>
            <div>
              <span className="text-xs text-[var(--text-secondary)]">Título</span>
              <p className="text-sm text-[var(--text-primary)]">{alert.title}</p>
            </div>
            {alert.acknowledged_at && (
              <div>
                <span className="text-xs text-[var(--text-secondary)]">Reconhecido em</span>
                <p className="text-sm text-[var(--text-primary)]">
                  {new Date(alert.acknowledged_at).toLocaleString('pt-BR')}
                </p>
              </div>
            )}
            {alert.resolved_at && (
              <div>
                <span className="text-xs text-[var(--text-secondary)]">Resolvido em</span>
                <p className="text-sm text-[var(--text-primary)]">
                  {new Date(alert.resolved_at).toLocaleString('pt-BR')}
                </p>
                {alert.resolution && (
                  <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                    Motivo: {alert.resolution}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Traceability */}
          <AlertTrace alert={alert} />
        </div>
      )}
    </div>
  );
}
