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
  const detailsId = `alert-${alert.id}-details`;

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
      {/*
        Summary row — the container itself is intentionally NOT interactive
        (no role="button"/tabIndex/onKeyDown). It contains focusable children
        (patient link, pathway link, quick-action buttons), so making the
        whole row a nested control would trap those children inside another
        control (axe: nested-interactive). Instead we follow the WAI-ARIA APG
        "disclosure" pattern: a single dedicated <button> below owns the
        expand/collapse semantics (aria-expanded/aria-controls) and is a
        SIBLING of the links/actions, not their ancestor. The onClick here is
        kept as a mouse-only progressive-enhancement convenience (click
        anywhere on the row to expand); it is not reachable via keyboard
        because the div has no tabIndex, so it never competes with the
        disclosure button or the nested controls for focus.
      */}
      <div
        className="flex cursor-pointer flex-wrap items-center gap-3 px-4 py-3"
        onClick={() => setExpanded(!expanded)}
      >
        {/* Disclosure control — the sole keyboard/AT-accessible trigger */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setExpanded(!expanded);
          }}
          aria-expanded={expanded}
          aria-controls={detailsId}
          aria-label={`Alerta ${alert.id}: ${alert.title} — ${expanded ? 'Recolher' : 'Expandir'} detalhes`}
          className="flex-shrink-0 rounded text-[var(--text-secondary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
        >
          {expanded ? (
            <ChevronDown className="h-4 w-4" aria-hidden="true" />
          ) : (
            <ChevronRight className="h-4 w-4" aria-hidden="true" />
          )}
        </button>

        {/* Severity */}
        <SeverityBadge severity={alert.severity} />

        {/* Patient link */}
        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
          Paciente
        </span>
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
        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
          Trilha
        </span>
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

        {/* Title — short label per ADR-0039 §6; the full 3-part explanation
            (alert.message) lives in the expanded region below, not here. */}
        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
          Mensagem
        </span>
        <span className="flex-1 truncate text-sm text-[var(--text-primary)] min-w-0">
          {alert.title}
        </span>

        {/* Date */}
        <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
          Criado em
        </span>
        <span className="flex items-center gap-1 text-xs text-[var(--text-secondary)] whitespace-nowrap">
          <Clock className="h-3 w-3" aria-hidden="true" />
          {createdAt}
        </span>

        {/* Status indicators */}
        {(isAcknowledged || isResolved) && (
          <span className="basis-full text-xs text-[var(--text-secondary)] sm:hidden">
            Status
          </span>
        )}
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

      {/*
        Expanded detail — kept mounted at all times (visibility toggled via
        the `hidden` attribute) rather than conditionally rendered, so
        aria-controls={detailsId} on the disclosure button above always
        resolves to a real node in the accessibility tree. AlertTrace is a
        pure presentational computation from props (no fetch/side effects),
        so always-mounting it is inexpensive.
      */}
      <div
        id={detailsId}
        hidden={!expanded}
        className="border-t border-[var(--border-default)] px-4 py-3"
        role="region"
        aria-label="Detalhes do alerta"
      >
        {/* Full clinical explanation — ADR-0039 §6: the short title lives in
            the compact row above; this 3-part body (o que aconteceu / por
            que importa / o que verificar, one sentence per line — see
            alert_copy.py) is the primary content of the expanded detail.
            whitespace-pre-line preserves the \n-separated parts. */}
        <p className="mb-3 whitespace-pre-line text-sm text-[var(--text-primary)]">
          {alert.message}
        </p>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <span className="text-xs text-[var(--text-secondary)]">Tipo</span>
            <p className="text-sm text-[var(--text-primary)]">{alert.type}</p>
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
    </div>
  );
}
